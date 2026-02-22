
from pathlib import Path
from typing import Optional
import re
import Py4GW
import PyImGui
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.HotkeyManager import HOTKEY_MANAGER
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.enums_src.IO_enums import Key, ModifierKey

from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.item_properties import DamageProperty
from Sources.frenkeyLib.ItemHandling.item_types.base_item import Axe, Bag, Salvage, Item, Scythe
from Sources.frenkeyLib.LootEx.data import Data
from Sources.frenkeyLib.LootEx.enum import ModType
from Sources.frenkeyLib.LootEx.models import Rune, WeaponMod

Utils.ClearSubModules("ItemHandling")
from Sources.frenkeyLib.ItemHandling.item_modifier_parser import ItemModifierParser


def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)

def run_test():
    data = Data()
    
    def compose_names_dict(mod: Rune) -> str:
        names_dict = {
            ServerLanguage.English: mod.names.get(ServerLanguage.English, None),
            ServerLanguage.Spanish: mod.names.get(ServerLanguage.Spanish, None),
            ServerLanguage.Italian: mod.names.get(ServerLanguage.Italian, None),
            ServerLanguage.German: mod.names.get(ServerLanguage.German, None),
            ServerLanguage.Korean: mod.names.get(ServerLanguage.Korean, None),
            ServerLanguage.French: mod.names.get(ServerLanguage.French, None),
            ServerLanguage.TraditionalChinese: mod.names.get(ServerLanguage.TraditionalChinese, None),
            ServerLanguage.Japanese: mod.names.get(ServerLanguage.Japanese, None),
            ServerLanguage.Polish: mod.names.get(ServerLanguage.Polish, None),
            ServerLanguage.Russian: mod.names.get(ServerLanguage.Russian, None),
            ServerLanguage.BorkBorkBork: mod.names.get(ServerLanguage.BorkBorkBork, None)
        }
        # keep only entries with a name
        names_dict = {k: v for k, v in names_dict.items() if v is not None}
        
        #format it nicely as python code        
        formatted = "\tnames = {\n"
        for lang, name in names_dict.items():
            
            #names can contain double quotes, escape them
            name = name.replace('"', '\\"')
            formatted += f"\t\tServerLanguage.{lang.name}: \"{name}\",\n"
        formatted += "\t}"
        
        return formatted
    
    runes : dict[str, Rune] = {r.identifier.lower(): r for r in data.Runes.values()}
    def get_rune_name(class_name : str) -> str:
        if runes.get(class_name.lower()):
            return runes[class_name.lower()].name
        
        Py4GW.Console.Log("ItemHandling", f"Warning: No rune found for class name {class_name}, using class name as fallback")
        return class_name

    # iterate over Sources\\frenkeyLib\\ItemHandling\\edit_input.py.py lines and add the names dict to each rune
    normalize_class_property_order("Sources\\frenkeyLib\\ItemHandling\\edit_input.py", "Sources\\frenkeyLib\\ItemHandling\\edit_output.py")
    import re
from pathlib import Path


def normalize_class_property_order(source_path: str, target_path: str) -> None:
    content = Path(source_path).read_text(encoding="utf-8")
    lines = content.splitlines()

    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        class_match = re.match(r"class\s+(\w+)\(", stripped)

        if not class_match:
            new_lines.append(line)
            i += 1
            continue

        # ----------------------------------------------------------
        # Found class
        # ----------------------------------------------------------
        class_indent = re.match(r"(\s*)", line).group(1)
        body_indent = class_indent + "    "

        new_lines.append(line)
        i += 1

        # Collect class body
        body = []
        while i < len(lines):
            if re.match(rf"^{class_indent}class\s+", lines[i]):
                break
            body.append(lines[i])
            i += 1

        # ----------------------------------------------------------
        # Extract relevant sections
        # ----------------------------------------------------------
        id_line = None
        mod_type_line = None
        rarity_line = None
        property_block = []
        names_block = []
        others = []

        j = 0
        while j < len(body):
            current = body[j]
            stripped_current = current.strip()

            # id
            if stripped_current.startswith("id ="):
                id_line = current
                j += 1
                continue

            # mod_type
            if stripped_current.startswith("mod_type ="):
                mod_type_line = current
                j += 1
                continue

            # rarity
            if stripped_current.startswith("rarity ="):
                rarity_line = current
                j += 1
                continue

            # property_identifiers block
            if stripped_current.startswith("property_identifiers"):
                property_block.append(current)
                j += 1
                while j < len(body) and not body[j].strip().endswith("]"):
                    property_block.append(body[j])
                    j += 1
                if j < len(body):
                    property_block.append(body[j])
                    j += 1
                continue

            # names block
            if stripped_current.startswith("names ="):
                names_block.append(current)
                j += 1
                while j < len(body) and not body[j].strip().endswith("}"):
                    names_block.append(body[j])
                    j += 1
                if j < len(body):
                    names_block.append(body[j])
                    j += 1
                continue

            others.append(current)
            j += 1

        # ----------------------------------------------------------
        # Reassemble in required order
        # ----------------------------------------------------------
        ordered = []

        if id_line:
            ordered.append(id_line)
        if mod_type_line:
            ordered.append(mod_type_line)
        if rarity_line:
            ordered.append(rarity_line)

        if ordered:
            ordered.append("")  # blank line

        if property_block:
            ordered.extend(property_block)
            ordered.append("")

        if names_block:
            ordered.extend(names_block)
            ordered.append("")

        # Preserve other attributes at bottom
        if others:
            ordered.extend(others)

        # Clean trailing blank lines inside class
        while ordered and ordered[-1].strip() == "":
            ordered.pop()

        new_lines.extend(ordered)
        new_lines.append("")  # blank line after class

    # ----------------------------------------------------------
    # Final cleanup
    # ----------------------------------------------------------
    final = "\n".join(new_lines)
    final = re.sub(r"\n{3,}", "\n\n", final)
    final = final.strip() + "\n"

    Path(target_path).write_text(final, encoding="utf-8")
    
def inject_rune_names():
    data = Data()

    source_path = Path("Sources\\frenkeyLib\\ItemHandling\\edit_input.py")
    target_path = Path("Sources\\frenkeyLib\\ItemHandling\\edit_output.py")

    content = source_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    def normalize_class_name(name: str) -> str:
        name = name.replace(" ", "")
        name = name.replace("'", "")
        name = name.replace("-", "")
        name = name.replace(".", "")
        name = name.replace(",", "")
        
        #remove everyting in []
        name = re.sub(r"\[.*?\]", "", name)
        
        return name

    runes: dict[str, Rune] = {
        normalize_class_name(r.identifier.lower()): r for r in data.Runes.values()
    }

    def compose_names_dict(mod: Rune, indent: str) -> list[str]:
        names_dict = {
            lang: mod.names.get(lang, None)
            for lang in ServerLanguage
        }

        names_dict = {k: v for k, v in names_dict.items() if v}

        output = [f"{indent}names = {{"]

        for lang, name in names_dict.items():
            name = name.replace('"', '\\"')
            output.append(
                f"{indent}    ServerLanguage.{lang.name}: \"{name}\","
            )

        output.append(f"{indent}}}")
        return output

    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip().lower()

        class_match = re.match(r"class\s+(\w+)\(", stripped)

        if class_match:
            class_name = class_match.group(1)
            new_lines.append(line)

            # Determine indentation level
            indent = re.match(r"(\s*)", line).group(1) + "    "

            # Check if this class already has names
            j = i + 1
            has_names = False
            while j < len(lines) and not lines[j].strip().startswith("class "):
                if "names =" in lines[j]:
                    has_names = True
                    break
                j += 1

            if not has_names:
                rune = runes.get(class_name.lower())

                if rune:
                    name_block = compose_names_dict(rune, indent)

                    new_lines.append("")
                    new_lines.extend(name_block)
                else:
                    Py4GW.Console.Log("ItemHandling", f"Warning: No rune found for class {class_name}, skipping injection")

            i += 1
            continue

        new_lines.append(line)
        i += 1

    # Normalize blank lines between classes
    final_content = "\n".join(new_lines)
    final_content = re.sub(r"\n{3,}", "\n\n", final_content)
    final_content = final_content.strip() + "\n"

    target_path.write_text(final_content, encoding="utf-8")

    Py4GW.Console.Log("ItemHandling", "Rune names injection complete.")
    
UPGRADE_PATTERN = re.compile(
    r'ItemUpgrade\s+(\w+)\s*=\s*new\(\s*([^,]+)\s*,\s*"((?:\\.|[^"\\])*)"\s*,\s*ItemUpgradeType\.([A-Za-z_]+)\s*\);'
)


def normalize_class_name(name: str) -> str:
    name = name.replace(" ", "")
    name = name.replace("'", "")
    name = name.replace("-", "")
    name = name.replace(".", "")
    name = name.replace(",", "")
    return name


def write_upgrades():
    source_path = "Sources\\frenkeyLib\\ItemHandling\\upgrades.txt"
    target_path = "Sources\\frenkeyLib\\ItemHandling\\generated_upgrades.py"

    with open(source_path, "r", encoding="utf-8") as fsource:
        upgrade_lines = fsource.readlines()

    with open(target_path, "w", encoding="utf-8") as f:

        for line in upgrade_lines:
            line = line.strip()

            if not line or line.startswith("//"):
                continue

            match = UPGRADE_PATTERN.search(line)
            if not match:
                if len(line.strip()) > 0:
                    Py4GW.Console.Log("ItemHandling", f"Warning: Line did not match upgrade pattern: {line}")
                continue

            variable_name, upgrade_id_raw, display_name, upgrade_type = match.groups()

            class_name = normalize_class_name(variable_name)
            text = f"""{class_name} = ItemUpgrade(upgrade_id = {upgrade_id_raw},  name = "{display_name}", upgrade_type = ItemUpgradeType.{upgrade_type})\n"""

            f.write(text)


def write_insignias():
    with open("Sources\\frenkeyLib\\ItemHandling\\generated_insignias.py", "w", encoding='utf-8') as f:
        Py4GW.Console.Log("ItemHandling", "Generating insignia classes from runes.json data...")
        
        data = Data()
        data.Load()
        
        for rune in data.Runes.values():
            Py4GW.Console.Log("ItemHandling", f"Processing rune: {rune.identifier}...")
            
            if rune.mod_type == ModType.Prefix or "Absorption" in rune.name or "Vigor" in rune.name:
                class_name = f"{rune.identifier.split(' ')[0]}Insignia"
                class_name = class_name.replace("'", "").replace("-", "")
                
                text = f'''class {class_name}(Insignia):
    identifier = {rune.modifiers[0].arg}
    model_id = {rune.model_id}
    model_file_id = {rune.model_file_id}
    inventory_icon = "{rune.inventory_icon}"
    profession = Profession.{rune.profession.name}
    rarity = Rarity.{rune.rarity.name}
    names = {{
        ServerLanguage.English: "{rune.names.get(ServerLanguage.English, rune.name)}",
        ServerLanguage.Spanish: "{rune.names.get(ServerLanguage.Spanish, rune.name)}",
        ServerLanguage.Italian: "{rune.names.get(ServerLanguage.Italian, rune.name)}",
        ServerLanguage.German: "{rune.names.get(ServerLanguage.German, rune.name)}",
        ServerLanguage.Korean: "{rune.names.get(ServerLanguage.Korean, rune.name)}",
        ServerLanguage.French: "{rune.names.get(ServerLanguage.French, rune.name)}",
        ServerLanguage.TraditionalChinese: "{rune.names.get(ServerLanguage.TraditionalChinese, rune.name)}",
        ServerLanguage.Japanese: "{rune.names.get(ServerLanguage.Japanese, rune.name)}",
        ServerLanguage.Polish: "{rune.names.get(ServerLanguage.Polish, rune.name)}",
        ServerLanguage.Russian: "{rune.names.get(ServerLanguage.Russian, rune.name)}",
        ServerLanguage.BorkBorkBork: "{rune.names.get(ServerLanguage.BorkBorkBork, rune.name)}"
    }}
    def describe(self) -> str:
        return f"{rune.description.replace("\n", "\\n")}"
register_insignia({class_name})'''
                f.write(text)
                f.write("\n\n")

def check_item(item_id):
    runtime_modifiers = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(item_id)
    
    parser = ItemModifierParser(runtime_modifiers)        
    for prop in parser.get_properties():
        print(prop.describe())
   


def refactor_upgrade_file(source_path: str, target_path: str) -> None:
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ----------------------------------------------------------
    # 1️⃣ Replace item_type_id_map blocks with id = ItemUpgradeId.X
    # ----------------------------------------------------------

    map_pattern = re.compile(
        r"item_type_id_map\s*=\s*\{\s*.*?ItemUpgradeId\.([A-Za-z0-9_]+).*?\}",
        re.DOTALL
    )

    def replace_map(match: re.Match) -> str:
        upgrade_name = match.group(1)
        return f"id = ItemUpgradeId.{upgrade_name}"

    content = map_pattern.sub(replace_map, content)

    # ----------------------------------------------------------
    # 2️⃣ Remove empty property_identifiers
    # ----------------------------------------------------------

    content = re.sub(
        r"\n\s*property_identifiers\s*=\s*\[\s*\]\s*",
        "\n",
        content
    )

    # ----------------------------------------------------------
    # 3️⃣ Ensure exactly ONE blank line between classes
    # ----------------------------------------------------------

    lines = content.splitlines()
    new_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # If this line starts a class and previous line isn't blank,
        # insert a blank line before it (except at file start)
        if stripped.startswith("class ") and new_lines:
            if new_lines[-1].strip() != "":
                new_lines.append("")

        new_lines.append(line.rstrip())

    content = "\n".join(new_lines)

    # Remove multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    content = content.strip() + "\n"

    # ----------------------------------------------------------
    # 4️⃣ Write result
    # ----------------------------------------------------------

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)


HOTKEY_MANAGER.register_hotkey(key=Key.T, modifiers=ModifierKey.Ctrl, callback=run_test, identifier="test_item_modifier_parser", name="Test Item Modifier Parser")

hovered_item_id = Inventory.GetHoveredItemID()
parser : Optional[ItemModifierParser] = None
item : Optional[Item] = None

def main():
    global hovered_item_id, parser, item
    
    open = ImGui.begin("Item Modifier Parser Test")
    if open:
        if ImGui.button("Test Parser"):
            run_test()
            
        item_id = Inventory.GetHoveredItemID()
        if hovered_item_id != item_id and item_id != 0:
            hovered_item_id = item_id
            parser = ItemModifierParser(GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(hovered_item_id))
            item  = Item.from_item_id(hovered_item_id)
            
        if parser:
            if ImGui.begin_table("properties", 2, PyImGui.TableFlags.Borders):
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                
                for prop in parser.get_properties():
                    if parser:
                        ImGui.text(f"{type(prop).__name__} ({prop.modifier.raw_identifier})")
                        PyImGui.table_next_column()
                        ImGui.text(f"{prop.describe()}")
                        PyImGui.table_next_column()
                ImGui.end_table()
        
        ImGui.separator()
        # if item:
        #     ImGui.text(f"Item: {item.name} | Type: {item.item_type.name}")
        
        #     ImGui.text(item.damage.describe() if hasattr(item, 'damage') and item.damage else "No damage")
        #     ImGui.text(item.damage_type.describe() if hasattr(item, 'damage_type') and item.damage_type else "No damage type")
        #     ImGui.text(item.prefix.describe() if hasattr(item, 'prefix') and item.prefix else "No prefix properties")
        #     ImGui.text(item.inherent.describe() if hasattr(item, 'inherent') and item.inherent else "No inherent properties")
        #     ImGui.text(item.suffix.describe() if hasattr(item, 'suffix') and item.suffix else "No suffix properties")
                
        
    ImGui.end()
    pass