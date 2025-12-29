import sys
        
from Py4GWCoreLib import UIManager
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Widgets.ItemHandlersRework.Rules import ByModelIdRule, BySkinRule, RuneRule, WeaponModRule

for mod in list(sys.modules.keys()):
    if "ItemHandlersRework" in mod:
        del sys.modules[mod]
                
from Widgets.ItemHandlersRework.Helpers import IsWeaponType
from Widgets.ItemHandlersRework.types import ItemAction
from Widgets.ItemHandlersRework.ItemData import ITEMS
from Widgets.ItemHandlersRework.Mods import RUNES, WEAPON_MODS
from Widgets.ItemHandlersRework.ItemCache import ITEM_CACHE
from Widgets.ItemHandlersRework.DestroyHandler import DestroyConfig, DestroyHandler
from Widgets.ItemHandlersRework.MerchantHandler import MerchantConfig, MerchantHandler
from Widgets.ItemHandlersRework.XunlaiVaultHandler import XunlaiVaultConfig, XunlaiVaultConfig, XunlaiVaultHandler
from Widgets.ItemHandlersRework.SalvageHandler import SalvageConfig, SalvageHandler

MODULE_NAME = "Item Handlers Rework"

update_throttle = ThrottledTimer(50)

destroy_handler = DestroyHandler()
destroy_config = DestroyConfig()
destroy_config.load_config()

merchant_handler = MerchantHandler()
merchant_config = MerchantConfig()
merchant_config.load_config()

xunlai_vault_handler = XunlaiVaultHandler()
xunlai_vault_config = XunlaiVaultConfig()
xunlai_vault_config.load_config()

salvage_handler = SalvageHandler()
salvage_config = SalvageConfig()
salvage_config.load_config()


items_per_tick = 5
current_processor = None

ConsoleLog(MODULE_NAME, "Module loaded.")
ConsoleLog(MODULE_NAME, f"{len(RUNES)} Runes loaded.")
ConsoleLog(MODULE_NAME, f"{len(WEAPON_MODS)} Weapon Upgrades loaded.")
ConsoleLog(MODULE_NAME, f"{len(ITEMS.All)} Items loaded.")

xunlai_vault_config.rules.clear()
xunlai_vault_config.add_rule(ByModelIdRule(name="ToT Bags", action=ItemAction.Stash, item_type=ItemType.Usable, model_id=ModelID.Trick_Or_Treat_Bag.value))
xunlai_vault_config.add_rule(RuneRule(name="Sup Vigor", action=ItemAction.Stash, rune_id="Rune of Superior Vigor"))
xunlai_vault_config.add_rule(WeaponModRule(name="of Necromancer", action=ItemAction.Stash, weapon_mod_id="of the Necromancer", item_types={ItemType.Staff : True, ItemType.Wand : True}))
xunlai_vault_config.add_rule(BySkinRule(name="Shadow Blades", action=ItemAction.Stash, skin_name="Shadow Blade.png"))

xunlai_vault_config.save_config()
xunlai_vault_config.load_config()

for rule in xunlai_vault_config.rules:
    ConsoleLog(MODULE_NAME, f"Xunlai Vault Rule: {rule.name} | Action: {rule.action.name} | Type: {type(rule).__name__}")


def configure():
    pass

def items_processor():    
    bag_list = GLOBAL_CACHE.ItemArray.CreateBagList(*range(Bag.Equipped_Items.value, Bag.Equipped_Items.value + 1))
    item_ids = GLOBAL_CACHE.ItemArray.GetItemArray(bag_list)
    
    count = 0
    for item_id in item_ids:
        item_view = ITEM_CACHE.GetItem(item_id)
        if item_view is None:
            continue
        
        if IsWeaponType(item_view.base.item_type) is False:
            continue
        
        ConsoleLog(MODULE_NAME, f"Processed item [{item_id:04}] | {item_view.base.item_type.name} | {item_view.base.model_id} | Runes {", ".join(str(rune.names.get(ServerLanguage.English, f"No Name Found ('{rune.identifier}').")) for rune in item_view.state.runes.values()) if item_view.state.runes else 'None'} | Weapon Upgrades {", ".join(str(upgrade.names.get(ServerLanguage.English, f"No Name Found ('{upgrade.identifier}').")) for upgrade in item_view.state.weapon_mods.values()) if item_view.state.weapon_mods else 'None'}")
        
        count += 1
        
        if count >= items_per_tick:
            # ConsoleLog(MODULE_NAME, f"Processed {items_per_tick} items, yielding ...")
            count = 0
            yield

def process_items():
    global current_processor
    
    if current_processor is None:
        current_processor = items_processor()
        ConsoleLog(MODULE_NAME, "Starting new items processor ...")
    
    try:
        next(current_processor)
    except StopIteration:
        current_processor = None
    

def main():            
    ITEM_CACHE.Update()
    
    if Routines.Checks.Map.IsLoading():
        return
      
    if not Routines.Checks.Map.IsMapReady():
        return
            
    if UIManager.IsWorldMapShowing():
        return
    
    if not update_throttle.IsExpired():
        return
    
    update_throttle.Reset()    
    process_items()
    
    
    # destroy_handler.Run()
    # merchant_handler.Run()
    # xunlai_vault_handler.Run()
    # salvage_handler.Run()
                    

__all__ = ["main", "configure"]