
import struct
from typing import Optional
import Py4GW
import PyImGui
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.HotkeyManager import HOTKEY_MANAGER
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.IO_enums import Key, ModifierKey

from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Py4GWCoreLib.native_src.internals.string_table import decode
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.ItemMod import ItemMod
from Sources.frenkeyLib.ItemHandling.types import ItemUpgrade, ItemUpgradeId

Utils.ClearSubModules("ItemHandling")


from Sources.frenkeyLib.ItemHandling.item_modifier_parser import ItemModifierParser

MODULE_NAME = "ItemModifier Tests"

def ParseHex(hex_string: str) -> int:
    return int(hex_string, 16)

def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)

def run_test():
    Py4GW.Console.Log(MODULE_NAME, f"Trying to decode ...")
    
    code_point_string = ""
    codepoints = [ParseHex(code_point) for code_point in code_point_string.strip().split()]

    encoded = struct.pack(f"<{len(codepoints)}H", *codepoints)
    
    Py4GW.Console.Log(MODULE_NAME, f"Encoded: {str(encoded)}")
    
    decoded = decode(encoded)
    
    Py4GW.Console.Log(MODULE_NAME, f"Decoded: {str(decoded)}")
    pass

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
        
        lang = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))
        ImGui.text(f"Hovered Item ID: {hovered_item_id} | Language: {lang.name}")
        
        if parser:
            properties = parser.properties
                        
            ImGui.text("Item", 18, "Bold")
            prefix, suffix, inscription = ItemMod.get_item_upgrades(hovered_item_id)  
                      
            if ImGui.begin_table("item properties", 2, PyImGui.TableFlags.Borders):
                PyImGui.table_next_row()
                PyImGui.table_next_column()
            
                ImGui.text("Prefix")
                PyImGui.table_next_column()
                ImGui.text(prefix.name if prefix else "None")
                is_zealous = prefix is not None and prefix.id == ItemUpgrade.Zealous
                is_zealous_scythe = prefix is not None and prefix.id == ItemUpgrade.Zealous and prefix.item_type == ItemType.Scythe
                
                #Optional different approach
                is_zealous_scythe_alt = prefix is not None and prefix.id == ItemUpgradeId.Zealous_Scythe

                ImGui.text(f"Is Zealous: {is_zealous}")
                ImGui.text(f"Is Zealous Scythe: {is_zealous_scythe}")
                ImGui.text(f"Is Zealous Scythe (alt): {is_zealous_scythe_alt}")
                PyImGui.table_next_column()
                
                ImGui.text("Inscription")
                PyImGui.table_next_column()
                ImGui.text(inscription.name if inscription else "None")
                PyImGui.table_next_column()
                
                
                ImGui.text("Suffix")
                PyImGui.table_next_column()
                ImGui.text(suffix.name if suffix else "None")
                PyImGui.table_next_column()
                    
                ImGui.end_table()
            
            if False and ImGui.begin_table("raw properties", 4, PyImGui.TableFlags.Borders):
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                
                for mod in parser.modifiers:
                    ImGui.text(f"{mod.identifier} ({mod.raw_identifier})")
                    PyImGui.table_next_column()      
                    
                    ImGui.text(f"{mod.arg1}")
                    PyImGui.table_next_column()
                    
                    ImGui.text(f"{mod.arg2}")
                    PyImGui.table_next_column()
                                      
                    ImGui.text(f"{mod.arg}")
                    PyImGui.table_next_column()
                    
                ImGui.end_table()
            
            ImGui.text("Parser", 18, "Bold")
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