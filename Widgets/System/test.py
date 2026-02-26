
from typing import Optional
import Py4GW
import PyImGui
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.HotkeyManager import HOTKEY_MANAGER
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.IO_enums import Key, ModifierKey

from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.mod_parser_stream import ModifierParser

Utils.ClearSubModules("ItemHandling")

from Sources.frenkeyLib.ItemHandling.item_properties import Insignia, PrefixProperty, SuffixProperty
from Sources.frenkeyLib.ItemHandling.item_types.base_item import Item

from Sources.frenkeyLib.ItemHandling.item_modifier_parser import ItemModifierParser


def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)

def run_test():
    pass

def check_item(item_id):
    runtime_modifiers = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(item_id)
    
    parser = ItemModifierParser(runtime_modifiers)        
    for prop in parser.get_properties():
        print(prop.describe())
   

HOTKEY_MANAGER.register_hotkey(key=Key.T, modifiers=ModifierKey.Ctrl, callback=run_test, identifier="test_item_modifier_parser", name="Test Item Modifier Parser")

hovered_item_id = Inventory.GetHoveredItemID()
parser : Optional[ModifierParser] = None
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
            parser = ModifierParser(GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(hovered_item_id))
            parser.parse()
            
            item  = Item.from_item_id(hovered_item_id)
        
        lang = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))
        ImGui.text(f"Hovered Item ID: {hovered_item_id} | Language: {lang.name}")
        
        if parser:
            item_name = GLOBAL_CACHE.Item.GetName(hovered_item_id) or "Unknown Item"
            
            properties = parser.properties
            
            prefixes = [prefix for prefix in properties if isinstance(prefix, PrefixProperty)]
            #Sort first Insignia then Runes
            prefixes.sort(key=lambda p: 0 if p.upgrade and isinstance(p.upgrade, Insignia) else 1)
            
            suffixes = [suffix for suffix in properties if isinstance(suffix, SuffixProperty)]
            suffixes.sort(key=lambda p: 0 if p.upgrade and isinstance(p.upgrade, Insignia) else 1)
            
            for prefix in prefixes:
                if prefix.upgrade and hasattr(prefix.upgrade, "remove_from_item_name"):
                    item_name = prefix.upgrade.remove_from_item_name(item_name)
            
            for suffix in suffixes:
                if suffix.upgrade and hasattr(suffix.upgrade, "remove_from_item_name"):
                    item_name = suffix.upgrade.remove_from_item_name(item_name)
            
            ImGui.text(f"{item_name}")
            
            for prefix in prefixes:
                if prefix.upgrade and hasattr(prefix.upgrade, "apply_to_item_name"):
                    item_name = prefix.upgrade.apply_to_item_name(item_name)
            
            for suffix in suffixes:
                if suffix.upgrade and hasattr(suffix.upgrade, "apply_to_item_name"):
                    item_name = suffix.upgrade.apply_to_item_name(item_name)
            
            ImGui.text(f"{item_name}")
            
            if ImGui.begin_table("properties", 2, PyImGui.TableFlags.Borders):
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                
                for prop in properties:
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