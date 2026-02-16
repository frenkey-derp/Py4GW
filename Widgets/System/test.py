
from typing import Optional
import re
import Py4GW
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.HotkeyManager import HOTKEY_MANAGER
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Item
from Py4GWCoreLib.enums_src.GameData_enums import DamageType
from Py4GWCoreLib.enums_src.IO_enums import Key, ModifierKey

from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.item_modifiers import ItemProperty
from Sources.frenkeyLib.ItemHandling.item_properties import AppliesToRuneProperty, AttributeRequirement, BaneProperty, DamageCustomized, DamageProperty, DamageTypeProperty, InscriptionProperty, PrefixProperty, SuffixProperty, UpgradeRuneProperty
from Sources.frenkeyLib.ItemHandling.types import ItemModifierParam
from Sources.frenkeyLib.LootEx.data import Data
from Sources.frenkeyLib.LootEx.enum import ModType

Utils.ClearSubModules("ItemHandling")
from Sources.frenkeyLib.ItemHandling.item_modifier_parser import ItemModifierParser


def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)

import inspect
from dataclasses import dataclass


def run_test():
    def localized_dictionary_to_string(d: dict[ServerLanguage, str]) -> str:
        return "{\n\t" + ",\n\t\t".join(f"ServerLanguage.{lang.name}: \"{text.replace('\"', '\\\"')}\"" for lang, text in d.items()) + "}"
    with open("test_weapon_upgradesoutput.txt", "w", encoding="utf-8") as f:
        data = Data()
        data.Load()
        
        for key, mod in data.Weapon_Mods.items():
            txt = f"""{key.replace(" ", "").replace('"', '').replace("'", "").replace("-", "").replace(".", "").replace(",", "")} = Upgrade(
    names = {localized_dictionary_to_string(mod.names)},
    descriptions = {localized_dictionary_to_string(mod.descriptions)},
    upgrade_type = ItemUpgradeClassType.{mod.mod_type.name}
)\n\n"""
            
            f.write(txt)


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
        

HOTKEY_MANAGER.register_hotkey(key=Key.T, modifiers=ModifierKey.Ctrl, callback=run_test, identifier="test_item_modifier_parser", name="Test Item Modifier Parser")

hovered_item_id = Inventory.GetHoveredItemID()
parser : Optional[ItemModifierParser] = None

def sort_for_item_display(props: list[ItemProperty]) -> list[ItemProperty]:

    GROUP_ORDER = {
        DamageTypeProperty: 1,
        DamageProperty: 2,
        AttributeRequirement: 3,
        PrefixProperty: 4,
        SuffixProperty: 4,
        UpgradeRuneProperty: 4,
        InscriptionProperty: 5,
        DamageCustomized: 6,
    }

    def get_group(prop: ItemProperty) -> int:
        for cls, order in GROUP_ORDER.items():
            if isinstance(prop, cls):
                return order
        return 5

    def get_identifier(prop: ItemProperty) -> int:
        return getattr(prop.__class__, "identifier", 999999)

    return sorted(props, key=lambda p: (get_group(p), get_identifier(p)))

def main():
    global hovered_item_id, parser
    
    open = ImGui.begin("Item Modifier Parser Test")
    if open:
        if ImGui.button("Test Parser"):
            run_test()
            
        item_id = Inventory.GetHoveredItemID()
        if hovered_item_id != item_id and item_id != 0:
            hovered_item_id = item_id
            parser = ItemModifierParser(GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(hovered_item_id))
        
        if parser:
            for prop in sort_for_item_display(parser.get_properties()):
                if parser:
                    ImGui.text(prop.describe())
                
        
    ImGui.end()
    pass