from LootEx import LootCheck, LootHandling, LootProfile, Settings
from LootEx import Settings
from Py4GWCoreLib import *
from LootEx import gui

# Reload imports
import importlib
importlib.reload(gui)
importlib.reload(LootProfile)
importlib.reload(Settings)
importlib.reload(LootHandling)

MODULE_NAME = "LootEx"
loot_handling_timer = ThrottledTimer(50)
throttle_timer = ThrottledTimer(50)
script_directory = os.path.dirname(os.path.abspath(__file__))

# Load settings
Settings.Current.Settings_file_path = os.path.join(script_directory, "Config", "LootEx", "LootExSettings.json")
Settings.Current.ProfilesPath = os.path.join(script_directory, "Config", "LootEx", "Profiles")
settings = Settings.Current.Load()

inventory_frame_hash = 291586130

def configure():    
    if not Settings.Current.WindowVisible:
        Settings.Current.WindowVisible = True
    
    pass

def main():        
    if(throttle_timer.IsExpired()):
        throttle_timer.Reset()

        if UIManager.IsWindowVisible(WindowID.WindowID_InventoryBags):
            Settings.Current.parent_frame_id = UIManager.GetFrameIDByHash(inventory_frame_hash)
            
            if Settings.Current.parent_frame_id != 0:
                Settings.Current.inventory_frame_exists = UIManager.FrameExists(Settings.Current.parent_frame_id)
            else:
                Settings.Current.inventory_frame_exists = False
        else:
            Settings.Current.parent_frame_id = 0
            Settings.Current.inventory_frame_exists = False
    
    if Settings.Current.inventory_frame_exists:
        Settings.Current.inventory_frame_coords = Settings.FrameCoords(Settings.Current.parent_frame_id)       
        gui.DrawInventoryControls()

    if Settings.Current.WindowVisible:
        gui.DrawWindow()

    Settings.Current.WindowVisible = False  

    if not LootCheck.trader_queue.action_queue.is_empty():
        LootCheck.LootCheck.ProcessTraderQueue()
        return

    if (Settings.Current.AutomaticInventoryHandling):
        if not loot_handling_timer.IsExpired():
            return
        
        loot_handling_timer.Reset()
        
        throttle_time = LootHandling.HandleInventoryLoot()

        if throttle_time > 0:
            loot_handling_timer.SetThrottleTime(throttle_time)
            return  
 

    
# if __name__ == "__main__":
#     main()

__all__ = ['main', 'configure']