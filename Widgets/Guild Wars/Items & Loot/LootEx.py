from PyTrading import PyTrading
from Py4GWCoreLib import *
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import get_widget_handler
from ctypes import windll

from Sources.frenkey.SulfurousRunner import ui


MODULE_NAME = "LootEx"
 # Copy keys so we can delete from sys.modules safely
module_names = list(sys.modules.keys())

for name in module_names:    
    if MODULE_NAME not in name:
        continue

    module = sys.modules.get(name, None)
    if module is None:
        continue

    # Check persistence flag (proper bugfix)
    is_persistent = getattr(module, "PERSISTENT", False)

    if is_persistent:
        ConsoleLog(MODULE_NAME, f"Skipping reloading for persistent module: {name}", Console.MessageType.Info)
        continue

    try:
        del sys.modules[name]
        
    except Exception as e:
        ConsoleLog(MODULE_NAME, f"Error unloading {name}: {e}", Console.MessageType.Error)

from Sources.frenkey.LootEx.price_check import PriceCheckManager
from Sources.frenkey.LootEx.data import Data
from Sources.frenkey.LootEx.settings import Settings
from Sources.frenkey.LootEx.loot_handling import LootHandler
from Sources.frenkey.LootEx.inventory_handling import InventoryHandler
from Sources.frenkey.LootEx.data_collection import DataCollector
from Sources.frenkey.LootEx import messaging
from Sources.frenkey.LootEx.cache import Cached_Item
from Sources.frenkey.LootEx.utility import Util
from Sources.frenkey.LootEx.gui import UI

VK_LBUTTON = 0x01  # Virtual-Key code for left mouse button

class LootEx:
    def __init__(self):
        self.throttle_timer = ThrottledTimer(250)
        self.hotkey_timer = ThrottledTimer(200)

        self.data = Data()
        self.data.Reload()

        self.data_collector = DataCollector()
        self.inventory_handler = InventoryHandler()
        self.loot_handler = LootHandler()
        self.price_check_mgr = PriceCheckManager()

        self.ui = UI()
        
        self.settings : Settings

        # Load settings
            
        self.key_handler_gen = None
        self.inventory_frame_hash = 291586130
        self.current_account : str = ""
        self.current_character : str = ""
        self.map_changed_reported : bool = False
        self.current_character_requested : bool = False
        self.current_character_set : bool = False
            
        self.widget_handler = get_widget_handler()

    def configure(self):
        pass

    def Initialize_And_Load(self):
        self.settings = Settings()   
        
        ConsoleLog(MODULE_NAME, f"Loading settings from {self.settings.settings_file_path}", Console.MessageType.Info)
        self.settings.load()    
        
        if self.settings.enable_loot_filters:
            self.loot_handler.Start()
        else:
            self.loot_handler.Stop()
            
        if self.settings.automatic_inventory_handling:
            self.inventory_handler.Start()
        else:
            self.inventory_handler.Stop()
        

    def CreateDirectories(self):
        settings = Settings()
        if not os.path.exists(settings.profiles_path):
            os.makedirs(settings.profiles_path)

        if not os.path.exists(settings.data_collection_path):
            os.makedirs(settings.data_collection_path)
            


    @staticmethod
    def is_left_mouse_down():
        return (windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0

    def handle_keys(self):
        if not LootEx.is_left_mouse_down() or not Console.is_window_active() or PyImGui.is_any_item_hovered() or self.ui.py_io.want_capture_mouse:
            return
        
        hovered_item = GLOBAL_CACHE.Inventory.GetHoveredItemID()
        
        while LootEx.is_left_mouse_down():
            yield
        
        new_hovered_item = GLOBAL_CACHE.Inventory.GetHoveredItemID()
        
        if not new_hovered_item and not hovered_item:
            return
        
        item = Cached_Item(hovered_item)  
        if self.ui.py_io.key_ctrl:        
            if new_hovered_item == hovered_item:            
                ## Deposit/Withdraw item
                if self.hotkey_timer.IsExpired():
                    self.hotkey_timer.Reset()
                    
                    trade_window_id = UIManager.GetFrameIDByHash(3198579276)
                    if UIManager.FrameExists(trade_window_id):
                        ConsoleLog(MODULE_NAME, f"Offering item '{item.name}' in trade window.", Console.MessageType.Info)
                        PyTrading.OfferItem(item_id=item.id, quantity=item.quantity)
                        return
                    
                    
                    if Map.IsExplorable():
                        if item.is_inventory_item:
                            ConsoleLog(MODULE_NAME, f"Dropping item '{item.name}' to floor.", Console.MessageType.Info)
                            self.inventory_handler.DropItem(item)
                            
                    elif item.is_inventory_item:
                        self.inventory_handler.DepositItem(item, False)
                        
                    elif item.is_storage_item:
                        self.inventory_handler.WithdrawItem(item)
                        
                
        elif not self.ui.py_io.key_ctrl and not self.ui.py_io.key_shift:     
            if not new_hovered_item and hovered_item > -1:
                yield
                            
                ## Confirm max amount dialog
                UIManager.ConfirmMaxAmountDialog()


    def main(self):
        if not Routines.Checks.Map.IsMapReady():
            self.data_collector.reset()
            self.ui.action_summary = None
            
            self.inventory_handler.reset()
            self.current_character = ""
            self.current_character_requested = False
            return
        
        
        if messaging.HandleMessages():
            return
        
        show_ui = not UIManager.IsWorldMapShowing() and not Map.IsMapLoading() and not Map.IsInCinematic() and not Map.Pregame.InCharacterSelectScreen()
        
        conflicting_widgets = ["InventoryPlus"]
        active_conflicting_inventory_widgets = [w for w in conflicting_widgets if self.widget_handler.is_widget_enabled(w)]

        if active_conflicting_inventory_widgets:
            if show_ui:
                self.ui.draw_disclaimer(active_conflicting_inventory_widgets)
            return
        
        if show_ui and self.data.is_loaded:      
            self.ui.draw_inventory_controls()        
            self.ui.draw_vault_controls()      
            self.ui.draw_window()
            self.ui.draw_data_collection()
        
        if not self.current_account:
            self.current_account = Player.GetAccountEmail()
            
            if self.current_account:      
                ConsoleLog(MODULE_NAME, f"Current Account: {self.current_account}", Console.MessageType.Info)      
                self.Initialize_And_Load()
        
        if not self.current_account:
            return
            
        if not self.current_character:
            self.current_character = Party.party_instance().GetPlayerNameByLoginNumber(GLOBAL_CACHE.ShMem.GetLoginNumber())        
                
        if self.current_character == "Timeout":
            ConsoleLog(MODULE_NAME, "Character name request timed out. Try again...", Console.MessageType.Error)
            self.current_character = ""
            self.current_character_requested = False
            return
        
        if not self.current_character:
            return
        
        language = Util.get_server_language()
        english_languages = [ServerLanguage.English, ServerLanguage.Japanese, ServerLanguage.Korean, ServerLanguage.TraditionalChinese, ServerLanguage.Russian]
        language = language if language not in english_languages else ServerLanguage.English

        if (language != self.settings.language):
            self.settings.language = language if language not in english_languages else ServerLanguage.English
            self.data.UpdateLanguage(language)
            self.settings.save()

        self.settings.current_character = self.current_character
        if not self.settings.character_profiles.get(self.current_character, False):        
            if self.settings.profiles:
                self.settings.character_profiles[self.current_character] = self.settings.profiles[0].name
            
            if not self.settings.character_profiles.get(self.current_character, False):
                return
                
            self.settings.SetProfile(self.settings.character_profiles[self.current_character])
            ConsoleLog(MODULE_NAME, f"First time using {MODULE_NAME} on '{self.current_character}'.{"\nDisabling inventory handling to prevent unwanted actions." if self.settings.automatic_inventory_handling else ""}\nSet Profile to '{self.settings.profile.name if self.settings.profile else "Unkown Profile"}'.", Console.MessageType.Warning)          
            self.inventory_handler.Stop()
        
        if not self.settings.profile:
            self.settings.SetProfile(self.settings.character_profiles[self.current_character])
            return    
            
        if self.settings.parent_frame_id is None or self.settings.parent_frame_id == 0:
            self.settings.parent_frame_id = UIManager.GetFrameIDByHash(self.inventory_frame_hash)
        
        
        self.ui.py_io = PyImGui.get_io()

        try:
            if self.key_handler_gen is None:
                self.key_handler_gen = self.handle_keys()
                
            next(self.key_handler_gen)
            
        except StopIteration:
            self.key_handler_gen = self.handle_keys()
                
        self.data_collector.Run()
        self.price_check_mgr.Run()    
        self.inventory_handler.Run()       

loot_ex : LootEx | None = None

def on_enable():
    global loot_ex
    loot_ex = LootEx()

def configure():
    global loot_ex

    if loot_ex is not None:
        loot_ex.configure()

def main():
    global loot_ex

    if loot_ex is not None:
        loot_ex.main()

__all__ = ['main', 'configure']
