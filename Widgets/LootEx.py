from Py4GW_widget_manager import WidgetHandler
from Py4GWCoreLib import *
from ctypes import windll

MODULE_NAME = "LootEx"
for module_name in list(sys.modules.keys()):
    if module_name not in ("sys", "importlib", "cache_data"):
        try:            
            if f"{MODULE_NAME}." in module_name:
                del sys.modules[module_name]
                # importlib.reload(module_name)
                pass
        except Exception as e:
            Py4GW.Console.Log(MODULE_NAME, f"Error reloading module {module_name}: {e}")

from Widgets.frenkey.LootEx import loot_handling, profile, settings, price_check, cache, inventory_handling, data_collector, utility, messaging
from Widgets.frenkey.LootEx.data import Data
from Widgets.frenkey.LootEx.gui import UI

map_timer = Timer()
throttle_timer = ThrottledTimer(250)
loot_timer = ThrottledTimer(1000)
hotkey_timer = ThrottledTimer(200)
script_directory = os.path.dirname(os.path.abspath(__file__))

data = Data()
data.Load()

ui = UI()

inventory_handler = inventory_handling.InventoryHandler()
loot_handler = loot_handling.LootHandler()

# Load settings
    

inventory_frame_hash = 291586130
current_account : str = ""
current_character : str = ""
map_changed_reported : bool = False
current_character_requested : bool = False
current_character_set : bool = False

widget_handler = WidgetHandler()

def configure():
    pass

def Initialize_And_Load():
    settings.current.settings_file_path = os.path.join(
        script_directory, "Config", "LootEx", f"{Player.GetAccountEmail()}.json")
    settings.current.profiles_path = os.path.join(
        script_directory, "Config", "LootEx", "Profiles")
    settings.current.data_collection_path = os.path.join(script_directory, "Config", "DataCollection")    
    
    ConsoleLog(MODULE_NAME, f"Loading settings from {settings.current.settings_file_path}", Console.MessageType.Info)
    settings.current.load()
    

def CreateDirectories():
    if not os.path.exists(settings.current.profiles_path):
        os.makedirs(settings.current.profiles_path)  
        
    if not os.path.exists(settings.current.data_collection_path):
        os.makedirs(settings.current.data_collection_path)    
        
VK_LBUTTON = 0x01  # Virtual-Key code for left mouse button


@staticmethod
def is_left_mouse_down():
    return (windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0


def main():
    global inventory_frame_hash, current_account, current_character, current_character_requested, map_changed_reported
    
    show_ui = not UIManager.IsWorldMapShowing() and not GLOBAL_CACHE.Map.IsMapLoading() and not GLOBAL_CACHE.Map.IsInCinematic() and not Player.InCharacterSelectScreen()
    
    conflicting_widgets = ["InventoryPlus"]
    active_conflicting_inventory_widgets = [w for w in conflicting_widgets if widget_handler.is_widget_enabled(w)]

    if active_conflicting_inventory_widgets:
        if show_ui:
            ui.draw_disclaimer(active_conflicting_inventory_widgets)
        return
    
    if show_ui and data.is_loaded:      
        ui.draw_inventory_controls()        
        ui.draw_vault_controls()      
        ui.draw_window()
    
    if not Routines.Checks.Map.MapValid():
        map_timer.Reset()
        map_timer.Start()
        
        loot_handler.reset()
        inventory_handler.reset()
        current_character = ""
        current_character_requested = False
        return

    if not map_timer.IsStopped():
        if map_timer.GetElapsedTime() < 5000:
            if not map_changed_reported:
                ConsoleLog(MODULE_NAME, "Map changed. Waiting a bit ...", Console.MessageType.Warning)
                map_changed_reported = True
            return

        ConsoleLog(MODULE_NAME, "Waited for 5 seconds. Lets continue...", Console.MessageType.Warning)
        map_timer.Stop()

    if not current_account:
        current_account = GLOBAL_CACHE.Player.GetAccountEmail()
        
        if current_account:            
            Initialize_And_Load()
    
    if not current_account:
        return
        
    if not current_character:
        agent_id = Player.GetAgentID()
        
        if not current_character_requested:
            Agent.RequestName(agent_id)
            current_character_requested = True
            return
        
        if Agent.IsNameReady(agent_id):
            current_character = Agent.GetName(agent_id)        
            
    if current_character == "Timeout":
        ConsoleLog(MODULE_NAME, "Character name request timed out. Try again...", Console.MessageType.Error)
        current_character = ""
        current_character_requested = False
        return
    
    if not current_character:
        return
    
    language = utility.Util.get_server_language()
    english_languages = [ServerLanguage.English, ServerLanguage.Japanese, ServerLanguage.Korean, ServerLanguage.TraditionalChinese, ServerLanguage.Russian]
    language = language if language not in english_languages else ServerLanguage.English
    
    if (language != settings.current.language):
        settings.current.language = language if language not in english_languages else ServerLanguage.English
        data.UpdateLanguage(language)
        settings.current.save()
        
    settings.current.current_character = current_character
    if not settings.current.character_profiles.get(current_character, False):        
        if settings.current.profiles:
            settings.current.character_profiles[current_character] = settings.current.profiles[0].name
        
        if not settings.current.character_profiles.get(current_character, False):
            return
            
        settings.current.SetProfile(settings.current.character_profiles[current_character])
        ConsoleLog(MODULE_NAME, f"First time using {MODULE_NAME} on '{current_character}'.{"\nDisabling inventory handling to prevent unwanted actions." if settings.current.automatic_inventory_handling else ""}\nSet Profile to '{settings.current.profile.name if settings.current.profile else "Unkown Profile"}'.", Console.MessageType.Warning)          
        inventory_handler.Stop()
    
    if not settings.current.profile:
        settings.current.SetProfile(settings.current.character_profiles[current_character])
        return    
    
    if messaging.HandleMessages():
        return
        
    if settings.current.parent_frame_id is None or settings.current.parent_frame_id == 0:
        settings.current.parent_frame_id = UIManager.GetFrameIDByHash(inventory_frame_hash)
    
    
    ui.py_io = PyImGui.get_io()
            
    hovered_item = GLOBAL_CACHE.Inventory.GetHoveredItemID()
    if hovered_item > -1:
        py_io = PyImGui.get_io()
        if py_io.key_ctrl:                
            if is_left_mouse_down():
                item = cache.Cached_Item(hovered_item)  
                    
                if hotkey_timer.IsExpired():
                    hotkey_timer.Reset()
                    if py_io.key_shift:
                        if item.is_inventory_item:
                            inventory_handler.DropItem(item)
                            
                    elif item.is_inventory_item:
                        inventory_handler.DepositItem(item, False)
                        
                    elif item.is_storage_item:
                        inventory_handler.WithdrawItem(item)
            
    if not price_check.trader_queue.action_queue.is_empty():
        price_check.PriceCheck.process_trader_queue()
        return

    data_collector.instance.run_v2()  
    inventory_handler.Run()       

__all__ = ['main', 'configure']
