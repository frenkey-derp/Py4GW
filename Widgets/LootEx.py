from Widgets.frenkey.LootEx import loot_handling, profile, settings, price_check, cache, inventory_handling, data_collector, data, utility, messaging, gui
from Py4GWCoreLib import *
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
    

inventory_frame_hash = 291586130
sharedMemoryManager = Py4GWSharedMemoryManager()
current_account : str = ""
current_character : str = ""
current_character_requested : bool = False
current_character_set : bool = False

# LootConfig().AddCondition(LootConfig.ConditionCategory.Custom, loot_handler.Should_Loot_Item, "LootEx - Should Loot Item")

def configure():
    pass

def Initialize_And_Load():
    settings.current.settings_file_path = os.path.join(
        script_directory, "Config", "LootEx", f"{Player.GetAccountEmail()}.json")
    settings.current.profiles_path = os.path.join(
        script_directory, "Config", "LootEx", "Profiles")
    settings.current.data_collection_path = os.path.join(script_directory, "Config", "DataCollection")    
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
    global inventory_frame_hash, current_account, current_character, current_character_requested
    
    if not Routines.Checks.Map.MapValid():
        loot_handler.reset()
        inventory_handler.reset()
        current_character = ""
        current_character_requested = False
        return           
    
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
        settings.current.automatic_inventory_handling = False  
        settings.current.save()
    
    if not settings.current.profile:
        settings.current.SetProfile(settings.current.character_profiles[current_character])
        return    
    
    if messaging.HandleMessages():
        return
        
    if settings.current.parent_frame_id is None or settings.current.parent_frame_id == 0:
        settings.current.parent_frame_id = UIManager.GetFrameIDByHash(inventory_frame_hash)
    
    
    ui.py_io = PyImGui.get_io()
    ui.draw_vault_controls()        
    ui.draw_inventory_controls()
    ui.draw_window()
    
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
    loot_handler.CheckExisingLoot()       
                      

__all__ = ['main', 'configure']
