from LootEx import loot_handling, profile, settings, price_check, cache, inventory_handling, data_collector, data, utility, messaging
from LootEx.cache import Cached_Item
from Py4GWCoreLib import *
from LootEx import gui

import ctypes
from ctypes import windll

# Reload imports
import importlib

from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
importlib.reload(gui)
importlib.reload(cache)
importlib.reload(profile)
importlib.reload(settings)
importlib.reload(loot_handling)
importlib.reload(inventory_handling)
importlib.reload(data_collector)
importlib.reload(price_check)
importlib.reload(messaging)

MODULE_NAME = "LootEx"
throttle_timer = ThrottledTimer(250)
hotkey_timer = ThrottledTimer(200)
script_directory = os.path.dirname(os.path.abspath(__file__))

data.Load()
ui = gui.UI()

inventory_handler = inventory_handling.InventoryHandler()
loot_handler = loot_handling.LootHandler()

# Load settings
settings.current.settings_file_path = os.path.join(
    script_directory, "Config", "LootEx", "LootExSettings.json")
settings.current.profiles_path = os.path.join(
    script_directory, "Config", "LootEx", "Profiles")
settings.current.data_collection_path = os.path.join(
    script_directory, "Config", "LootEx", "DataCollection")
settings.current.load()

inventory_frame_hash = 291586130
sharedMemoryManager = Py4GWSharedMemoryManager()
current_account = Player.GetAccountEmail()

def configure():
    if not settings.current.window_visible is True:
        settings.current.window_visible = True
    pass

VK_LBUTTON = 0x01  # Virtual-Key code for left mouse button

LootConfig().AddCondition(LootConfig.ConditionCategory.Custom, loot_handler.Should_Loot_Item, "LootEx - Should Loot Item")
    
@staticmethod
def is_left_mouse_down():
    return (windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0


def main():
    global inventory_frame_hash
    
    if not Routines.Checks.Map.MapValid():
        inventory_handler.reset()
        return           

    if messaging.HandleMessages():
        return
        
    if settings.current.parent_frame_id is None or settings.current.parent_frame_id == 0:
        settings.current.parent_frame_id = UIManager.GetFrameIDByHash(inventory_frame_hash)
    
    language = utility.Util.get_server_language()
    if (language != settings.current.language):
        settings.current.language = language
        data.UpdateLanguage(language)
        settings.current.save()
        
    ui.draw_vault_controls()        
    ui.draw_inventory_controls()

    if settings.current.window_visible:
        ui.draw_window()

    settings.current.window_visible = False
    
    hovered_item = GLOBAL_CACHE.Inventory.GetHoveredItemID()
    if hovered_item > -1:
        py_io = PyImGui.get_io()
        if py_io.key_ctrl:                
            if is_left_mouse_down():
                item = Cached_Item(hovered_item)  
                    
                if hotkey_timer.IsExpired():
                    hotkey_timer.Reset()
                    if py_io.key_shift:
                        if item.is_inventory_item:
                            inventory_handler.DropItem(item)
                            
                    elif item.is_inventory_item:
                        inventory_handler.DepositItem(item, False)
                        
                    elif item.is_storage_item:
                        inventory_handler.WithdrawItem(item)
            
    # if (throttle_timer.IsExpired()):
    #     throttle_timer.Reset()
    # else:
    #     return
    if not price_check.trader_queue.action_queue.is_empty():
        price_check.PriceCheck.process_trader_queue()
        return


    data_collector.instance.run_v2()  
    inventory_handler.Run()                            
                             

# if __name__ == "__main__":
#     main()

__all__ = ['main', 'configure']
