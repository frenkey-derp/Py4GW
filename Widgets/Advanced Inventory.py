
# Reload imports
import json
import os


from Py4GWCoreLib import ImGui, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.Py4GWcorelib import ThrottledTimer
from Py4GWCoreLib.UIManager import UIManager


MODULE_NAME = "Advanced Inventory"
save_throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

configure_window = ImGui.WindowModule(MODULE_NAME + "Config", MODULE_NAME + "#Config", (300, 100), (100, 100))

class Settings:        
    def __init__(self):
        self.save_requested = False

        self.drop_move_fullstack : bool = False
        self.disable_gold_and_green_item_confirmation : bool = False
        self.trade_item_on_alt_click : bool = False

    def to_dict(self):
        return {
            "drop_move_fullstack": self.drop_move_fullstack,
            "disable_gold_and_green_item_confirmation": self.disable_gold_and_green_item_confirmation,
            "trade_item_on_alt_click": self.trade_item_on_alt_click
        }
    def request_save(self):
        self.save_requested = True
        
    def save(self):
        with open(os.path.join(script_directory, "Config", f"{MODULE_NAME}.json"), "w") as f:
            json.dump(self.to_dict(), f)
            self.save_requested = False
    
    def load(self):
        with open(os.path.join(script_directory, "Config", f"{MODULE_NAME}.json"), "r") as f:
            data = json.load(f)
            self.drop_move_fullstack = data["drop_move_fullstack"]
            self.disable_gold_and_green_item_confirmation = data["disable_gold_and_green_item_confirmation"]
            self.trade_item_on_alt_click = data["trade_item_on_alt_click"]

settings = Settings()
settings.load()

def configure():
    configure_window.open = True
    if configure_window.begin():
        drop_move_fullstack = ImGui.checkbox("Drop/Move full stack", settings.drop_move_fullstack)
        if drop_move_fullstack != settings.drop_move_fullstack:
            settings.drop_move_fullstack = drop_move_fullstack
            settings.request_save()
        
        disable_gold_and_green_item_confirmation = ImGui.checkbox("Disable gold item confirmation", settings.disable_gold_and_green_item_confirmation)
        if disable_gold_and_green_item_confirmation != settings.disable_gold_and_green_item_confirmation:
            settings.disable_gold_and_green_item_confirmation = disable_gold_and_green_item_confirmation
            settings.request_save()
            
        trade_item_on_alt_click = ImGui.checkbox("Trade item on ALT+Click", settings.trade_item_on_alt_click)
        if trade_item_on_alt_click != settings.trade_item_on_alt_click:
            settings.trade_item_on_alt_click = trade_item_on_alt_click
            settings.request_save()

    configure_window.end()
    pass

def OnItemAmountPopUp():
    if settings.drop_move_fullstack:
        max_frame_id = UIManager.GetFrameIDByHash(4008686776) # Max amount button
        drop_frame_id = UIManager.GetFrameIDByHash(4014954629) # Drop button

        if UIManager.FrameExists(max_frame_id) and UIManager.FrameExists(drop_frame_id):
            GLOBAL_CACHE._ActionQueueManager.AddAction("ACTION", UIManager.FrameClick, max_frame_id)
            GLOBAL_CACHE._ActionQueueManager.AddAction("ACTION", UIManager.FrameClick, drop_frame_id)

def OnItemConfirmationPopUp():
    if settings.disable_gold_and_green_item_confirmation:
        confirm_frame_id = UIManager.GetFrameIDByHash(3932446343) # Confirm button

        if UIManager.FrameExists(confirm_frame_id):
            GLOBAL_CACHE._ActionQueueManager.AddAction("ACTION", UIManager.FrameClick, confirm_frame_id)

def main():    
    global settings
    
    if not Routines.Checks.Map.MapValid():
        return    
                
    if save_throttle_timer.IsExpired():
        save_throttle_timer.Reset()
        
        if settings.save_requested:
            settings.save()
    
    configure_window.open = False

__all__ = ['main', 'configure']
