
from typing import Optional
import Py4GW
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.HotkeyManager import HOTKEY_MANAGER
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Item
from Py4GWCoreLib.enums_src.IO_enums import Key, ModifierKey

from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.LootEx.data import Data
from Sources.frenkeyLib.LootEx.enum import ModType

Utils.ClearSubModules("ItemHandling")
from Sources.ItemHandling.item_modifier_parser import ItemModifierParser
from Sources.ItemHandling.item_properties import _PROPERTY_REGISTRY, Damage


def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)


def run_test():
    # with file open to write values
    Py4GW.Console.Log("Test", f"{get_true_identifier_with_hex(10312)}")   

def write_insignias():
    with open("Sources\\ItemHandling\\generated_insignias.py", "w", encoding='utf-8') as f:
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
            for prop in parser.get_properties():
                ImGui.text(prop.describe())
        
    ImGui.end()
    pass