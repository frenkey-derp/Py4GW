import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
UPGRADES_PATH = ROOT / "Sources" / "frenkeyLib" / "ItemHandling" / "Mods" / "upgrades.py"
STRINGS_PATH = ROOT / "Sources" / "frenkeyLib" / "ItemHandling" / "Items" / "collected_strings.json"

TARGET_BASES = {"WeaponUpgrade", "Inscription", "Insignia", "Rune"}
ABSTRACT_CLASSES = {
    "Upgrade",
    "WeaponUpgrade",
    "WeaponPrefix",
    "WeaponSuffix",
    "Inscription",
    "Insignia",
    "Rune",
    "AttributeRune",
}
NAME_ALIASES = {
    "\"Knowing is Half the Battle\"": "\"Knowing is Half the Battle.\"",
    "\"Master of My Domain!\"": "\"Master of My Domain\"",
    "\"Not the Face!\"": "\"Not the face!\"",
}
DESCRIPTION_BOILERPLATE_PREFIXES = (
    "upgrade component",
    "attaches to:",
    "value:",
    "use to apply to another item.",
)


def load_strings() -> dict[str, str]:
    with STRINGS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def get_english_name(node: ast.Assign | ast.AnnAssign) -> str | None:
    return get_english_dict_value(node, "English")


def get_english_dict_value(node: ast.Assign | ast.AnnAssign, language: str) -> str | None:
    value = node.value
    if not isinstance(value, ast.Dict):
        return None

    for key, item in zip(value.keys, value.values):
        if isinstance(key, ast.Attribute) and isinstance(key.value, ast.Name):
            if key.value.id == "ServerLanguage" and key.attr == language:
                if isinstance(item, ast.Constant) and isinstance(item.value, str):
                    return item.value
                if isinstance(item, ast.JoinedStr):
                    parts: list[str] = []
                    for value_part in item.values:
                        if not isinstance(value_part, ast.Constant) or not isinstance(value_part.value, str):
                            return None
                        parts.append(value_part.value)
                    return "".join(parts)
    return None


def get_assignment_name(node: ast.stmt) -> str | None:
    if isinstance(node, ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return None


def parse_hex_bytes(value: str) -> str:
    parts = [part.rstrip(",") for part in value.split() if part]
    return f"bytes([{', '.join(parts)}])"


def is_relevant_class(class_name: str, bases_by_class: dict[str, list[str]], cache: dict[str, bool]) -> bool:
    if class_name in cache:
        return cache[class_name]
    if class_name in TARGET_BASES:
        cache[class_name] = True
        return True

    for base_name in bases_by_class.get(class_name, []):
        if base_name in TARGET_BASES:
            cache[class_name] = True
            return True
        if base_name in bases_by_class and is_relevant_class(base_name, bases_by_class, cache):
            cache[class_name] = True
            return True

    cache[class_name] = False
    return False


def inherits_from(class_name: str, target_base: str, bases_by_class: dict[str, list[str]], cache: dict[tuple[str, str], bool]) -> bool:
    cache_key = (class_name, target_base)
    if cache_key in cache:
        return cache[cache_key]

    if class_name == target_base:
        cache[cache_key] = True
        return True

    for base_name in bases_by_class.get(class_name, []):
        if base_name == target_base or inherits_from(base_name, target_base, bases_by_class, cache):
            cache[cache_key] = True
            return True

    cache[cache_key] = False
    return False


def normalize_description_text(value: str) -> str:
    value = value.replace("%%", "%")
    value = re.sub(r"</?c[^>]*>", "", value)
    value = value.lower()
    value = value.replace("[an] ", "")
    value = value.replace("on foes", "of foes")
    value = re.sub(r"\b(?:a|an)\b", "", value)
    value = value.replace("enchantment spells", "enchantment spell")
    value = value.replace("weapon spells", "weapon spell")
    value = value.replace("1 or more enchantment spell", "or more enchantment spell")
    value = re.sub(r"\s+", " ", value.strip())
    return value


def split_description_components(value: str) -> list[str]:
    components: list[str] = []
    stripped = normalize_description_text(value)
    if not stripped or stripped == ",":
        return components

    match = re.fullmatch(r"(.+?) \((.+)\)", stripped)
    if match:
        components.append(match.group(1).strip())
        components.extend(part.strip() for part in match.group(2).split(","))
        return [component for component in components if component]

    if stripped.startswith("(") and stripped.endswith(")"):
        return [part.strip() for part in stripped[1:-1].split(",") if part.strip()]

    return [stripped]


def description_key_components(key: str) -> list[str]:
    components: list[str] = []
    for line in key.splitlines():
        normalized_line = normalize_description_text(line)
        if not normalized_line or normalized_line == ",":
            continue
        if normalized_line.startswith(DESCRIPTION_BOILERPLATE_PREFIXES):
            continue
        components.extend(split_description_components(line))
    return components


def expected_description_components(description: str) -> list[str]:
    components: list[str] = []
    for line in description.splitlines():
        components.extend(split_description_components(line))
    return components


def find_insignia_description_match(description: str, strings: dict[str, str]) -> str | None:
    expected = expected_description_components(description)
    if not expected:
        return None

    best_match: str | None = None
    best_extra_components: int | None = None

    for key in strings:
        if "Upgrade component" not in key or "Attaches to: Armor" not in key or "Use to apply to another item." not in key:
            continue

        candidate_components = description_key_components(key)
        remaining = list(candidate_components)
        matched = True

        for component in expected:
            if component in remaining:
                remaining.remove(component)
                continue
            matched = False
            break

        if not matched:
            continue

        extra_components = len(remaining)
        if best_extra_components is None or extra_components < best_extra_components:
            best_match = key
            best_extra_components = extra_components

    return best_match


def main() -> None:
    strings = load_strings()
    source = UPGRADES_PATH.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)

    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    bases_by_class = {node.name: [base for base in (get_base_name(item) for item in node.bases) if base] for node in classes}
    relevant_cache: dict[str, bool] = {}
    inheritance_cache: dict[tuple[str, str], bool] = {}

    replacements: list[tuple[int, int, list[str]]] = []
    updated_classes: list[str] = []
    missing_strings: list[tuple[str, str]] = []
    missing_descriptions: list[tuple[str, str]] = []

    for class_node in classes:
        if class_node.name in ABSTRACT_CLASSES:
            continue
        if not is_relevant_class(class_node.name, bases_by_class, relevant_cache):
            continue

        names_node: ast.Assign | ast.AnnAssign | None = None
        encoded_node: ast.Assign | ast.AnnAssign | None = None

        for stmt in class_node.body:
            assignment_name = get_assignment_name(stmt)
            if assignment_name == "names":
                names_node = stmt
            elif assignment_name == "encoded_name":
                encoded_node = stmt

        if names_node is None:
            continue

        english_name = get_english_name(names_node)
        if english_name is None:
            continue

        encoded_value = strings.get(english_name)
        if encoded_value is None:
            encoded_value = strings.get(NAME_ALIASES.get(english_name, ""))
        if encoded_value is None:
            missing_strings.append((class_node.name, english_name))
            continue

        new_line = f"    encoded_name : bytes = {parse_hex_bytes(encoded_value)}"

        if encoded_node is not None:
            block = [new_line]
            next_line_index = encoded_node.end_lineno
            if next_line_index < len(lines):
                next_line = lines[next_line_index]
                if next_line and not next_line.startswith(" "):
                    block.append("")
            replacements.append((encoded_node.lineno - 1, encoded_node.end_lineno - 1, block))
            updated_classes.append(class_node.name)
            continue

        insert_at = names_node.end_lineno
        block = [new_line]
        if insert_at < len(lines):
            next_line = lines[insert_at]
            if next_line and not next_line.startswith(" "):
                block.append("")
        replacements.append((insert_at, insert_at - 1, block))
        updated_classes.append(class_node.name)

    for class_node in classes:
        if class_node.name in ABSTRACT_CLASSES:
            continue
        if not inherits_from(class_node.name, "Insignia", bases_by_class, inheritance_cache):
            continue

        descriptions_node: ast.Assign | ast.AnnAssign | None = None
        encoded_description_node: ast.Assign | ast.AnnAssign | None = None

        for stmt in class_node.body:
            assignment_name = get_assignment_name(stmt)
            if assignment_name == "descriptions":
                descriptions_node = stmt
            elif assignment_name == "encoded_description":
                encoded_description_node = stmt

        if descriptions_node is None:
            continue

        english_description = get_english_dict_value(descriptions_node, "English")
        if english_description is None:
            continue

        matched_key = find_insignia_description_match(english_description, strings)
        if matched_key is None:
            missing_descriptions.append((class_node.name, english_description))
            continue

        encoded_value = strings[matched_key]
        new_line = f"    encoded_description : bytes = {parse_hex_bytes(encoded_value)}"

        if encoded_description_node is not None:
            block = [new_line]
            next_line_index = encoded_description_node.end_lineno
            if next_line_index < len(lines):
                next_line = lines[next_line_index]
                if next_line and not next_line.startswith(" "):
                    block.append("")
            replacements.append((encoded_description_node.lineno - 1, encoded_description_node.end_lineno - 1, block))
            updated_classes.append(class_node.name)
            continue

        insert_at = descriptions_node.lineno - 1
        block = [new_line]
        replacements.append((insert_at, insert_at - 1, block))
        updated_classes.append(class_node.name)

    for start, end, new_block in sorted(replacements, key=lambda item: item[0], reverse=True):
        if start <= end:
            lines[start : end + 1] = new_block
        else:
            lines[start:start] = new_block

    new_source = "\n".join(lines) + "\n"
    if new_source != source:
        UPGRADES_PATH.write_text(new_source, encoding="utf-8")

    print(f"Updated {len(updated_classes)} classes in {UPGRADES_PATH}")
    if missing_strings:
        print("Missing encoded strings:")
        for class_name, english_name in missing_strings:
            print(f"  {class_name}: {english_name}")
    if missing_descriptions:
        print("Missing encoded descriptions:")
        for class_name, english_description in missing_descriptions:
            print(f"  {class_name}: {english_description}")


if __name__ == "__main__":
    main()
