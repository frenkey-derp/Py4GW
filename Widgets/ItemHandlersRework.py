import sys
        
from Py4GWCoreLib import UIManager
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Widgets.ItemHandlersRework.Helpers import IsWeaponType
from Widgets.ItemHandlersRework.Mods import RUNES, WEAPON_MODS

for mod in list(sys.modules.keys()):
    if "ItemHandlersRework" in mod:
        del sys.modules[mod]
                
from Widgets.ItemHandlersRework.ItemCache import ITEM_CACHE
from Widgets.ItemHandlersRework.DestroyHandler import DestroyHandler
from Widgets.ItemHandlersRework.MerchantHandler import MerchantHandler
from Widgets.ItemHandlersRework.XunlaiVaultHandler import XunlaiVaultHandler
from Widgets.ItemHandlersRework.SalvageHandler import SalvageHandler

MODULE_NAME = "Item Handlers Rework"

update_throttle = ThrottledTimer(50)

destroy_handler = DestroyHandler()
merchant_handler = MerchantHandler()
xunlai_vault_handler = XunlaiVaultHandler()
salvage_handler = SalvageHandler()


items_per_tick = 5
current_processor = None

ConsoleLog(MODULE_NAME, "Module loaded.")
ConsoleLog(MODULE_NAME, f"{len(RUNES)} Runes loaded.")
ConsoleLog(MODULE_NAME, f"{len(WEAPON_MODS)} Weapon Upgrades loaded.")


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