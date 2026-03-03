
import struct
from typing import Optional
import Py4GW
import PyImGui
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.HotkeyManager import HOTKEY_MANAGER
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.IO_enums import Key, ModifierKey

from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Py4GWCoreLib.native_src.internals.string_table import decode
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE
from Sources.frenkeyLib.ItemHandling.Items.ItemData import ITEM_DATA
from Sources.frenkeyLib.ItemHandling.Mods.ItemMod import ItemMod
from Sources.frenkeyLib.ItemHandling.Mods.types import ItemUpgrade, ItemUpgradeId
from Sources.frenkeyLib.ItemHandling.Mods.upgrades import OfEnchantingUpgrade, Upgrade
from Sources.frenkeyLib.ItemHandling.Rules.base_rule import ItemTypesRule, UpgradeRule, WeaponSkinRule
from Sources.frenkeyLib.ItemHandling.Rules.profile import RuleProfile
from Sources.frenkeyLib.ItemHandling.Rules.types import ItemAction
from Sources.frenkeyLib.LootEx import utility

Utils.ClearSubModules("ItemHandling")


from Sources.frenkeyLib.ItemHandling.Mods.item_modifier_parser import ItemModifierParser

MODULE_NAME = "ItemModifier Tests"

def ParseHex(hex_string: str) -> int:
    return int(hex_string, 16)

def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)

def run_test():
    global loaded_profile
    
    my_profile = RuleProfile("Test Profile")
    
    item_type_rule = ItemTypesRule("All Usables", item_types=[ItemType.Usable], action=ItemAction.Use)
    my_profile.add_rule(item_type_rule)
    
    weapon_skin_rule = WeaponSkinRule("Divine Staff", weapon_skins=["Divine Staff.png"], action=ItemAction.Hold)
    my_profile.add_rule(weapon_skin_rule)
    
    upgrade_rule = UpgradeRule("Upgrade Rule", upgrade=OfEnchantingUpgrade(), action=ItemAction.Salvage_Mods) 
    my_profile.add_rule(upgrade_rule)
    
    my_profile.save()
    
    loaded_profile = RuleProfile.load(my_profile.default_path)
    loaded_profile.save()
    total_rules = sum(len(group) for group in loaded_profile.rule_groups.values())
    Py4GW.Console.Log(MODULE_NAME, f"Loaded profile '{loaded_profile.name}' with {len(loaded_profile.rule_groups)} rule groups with a total of {total_rules} rules.", Py4GW.Console.MessageType.Info)
    
    pass

def check_item(item_id):
    runtime_modifiers = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(item_id)
    
    parser = ItemModifierParser(runtime_modifiers)        
    for prop in parser.get_properties():
        print(prop.describe())
   

HOTKEY_MANAGER.register_hotkey(key=Key.T, modifiers=ModifierKey.Ctrl, callback=run_test, identifier="test_item_modifier_parser", name="Test Item Modifier Parser")

hovered_item_id = Inventory.GetHoveredItemID()
parser : Optional[ItemModifierParser] = None
loaded_profile : Optional[RuleProfile] = None

def main():
    global hovered_item_id, parser
    start_bag : Bag = Bag.Backpack
    end_bag : Bag = Bag.Bag_2
    inventory_array, inventory_sizes = utility.Util.GetZeroFilledBags(start_bag, end_bag)
    ITEM_CACHE.items.clear()  # Clear the cache to ensure fresh snapshots for testing
    
    if loaded_profile:
        for i in range(10):
            for item_id in inventory_array:
                if item_id == 0:
                    continue
                
                rule = loaded_profile.get_matching_rule(item_id)
                action = rule.action if rule else ItemAction.NONE
                
                # if action != ItemAction.NONE and rule:
                #     Py4GW.Console.Log(MODULE_NAME, f"Item ID {item_id} matches {rule.name} with action: {action.name}", Py4GW.Console.MessageType.Info)
                # Py4GW.Console.Log(MODULE_NAME, f"[{format(item_id, "#06")}] - {snapshot.data.names.get(ServerLanguage.English) if snapshot.data else f'Unknown {snapshot.item_type.name} Item [{format(snapshot.model_id, "#06")}]'}", Py4GW.Console.MessageType.Info)
    
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
                is_zealous_scythe_alt = prefix is not None and prefix.upgrade_id == ItemUpgradeId.Zealous_Scythe

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