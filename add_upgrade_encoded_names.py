import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
UPGRADES_PATH = ROOT / "Sources" / "frenkeyLib" / "ItemHandling" / "Mods" / "upgrades.py"
STRINGS_PATH = ROOT / "Sources" / "frenkeyLib" / "ItemHandling" / "Items" / "collected_strings.json"

TARGET_BASES = {"WeaponUpgrade", "Inscription"}
ABSTRACT_CLASSES = {"Upgrade", "WeaponUpgrade", "WeaponPrefix", "WeaponSuffix", "Inscription"}
NAME_ALIASES = {
    "\"Knowing is Half the Battle\"": "\"Knowing is Half the Battle.\"",
    "\"Master of My Domain!\"": "\"Master of My Domain\"",
    "\"Not the Face!\"": "\"Not the face!\"",
}


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
    value = node.value
    if not isinstance(value, ast.Dict):
        return None

    for key, item in zip(value.keys, value.values):
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            continue
        if isinstance(key, ast.Attribute) and isinstance(key.value, ast.Name):
            if key.value.id == "ServerLanguage" and key.attr == "English":
                return item.value
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


def main() -> None:
    strings = load_strings()
    source = UPGRADES_PATH.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)

    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    bases_by_class = {node.name: [base for base in (get_base_name(item) for item in node.bases) if base] for node in classes}
    relevant_cache: dict[str, bool] = {}

    replacements: list[tuple[int, int, list[str]]] = []
    updated_classes: list[str] = []
    missing_strings: list[tuple[str, str]] = []

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


if __name__ == "__main__":
    main()
