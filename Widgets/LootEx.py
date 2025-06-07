from LootEx import settings, loot_check, loot_handling, loot_profile, data_collector, data, utility, messaging
from Py4GWCoreLib import *
from LootEx import gui

# Reload imports
import importlib

from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
importlib.reload(gui)
importlib.reload(loot_profile)
importlib.reload(settings)
importlib.reload(loot_handling)
importlib.reload(data_collector)
importlib.reload(loot_check)
importlib.reload(messaging)

MODULE_NAME = "LootEx"
loot_handling_timer = ThrottledTimer(50)
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

data.Load()
ui = gui.UI()

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


def main():
    global inventory_frame_hash
    
    if not Routines.Checks.Map.MapValid():
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

    # if (throttle_timer.IsExpired()):
    #     throttle_timer.Reset()
    # else:
    #     return
    if not loot_check.trader_queue.action_queue.is_empty():
        loot_check.LootCheck.process_trader_queue()
        return


    data_collector.instance.run_v2()                               
                             
    if (settings.current.automatic_inventory_handling):
        if not loot_handling_timer.IsExpired():
            return

        loot_handling_timer.Reset()
        loot_handling.Run()


# if __name__ == "__main__":
#     main()

__all__ = ['main', 'configure']
