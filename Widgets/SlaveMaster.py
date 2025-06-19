
# Reload imports
import importlib
import os
from Widgets.SlaveMasterLib import gui

from Py4GWCoreLib import Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.Py4GWcorelib import ThrottledTimer

importlib.reload(gui)

MODULE_NAME = "SlaveMaster"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))


inventory_frame_hash = 291586130
sharedMemoryManager = Py4GWSharedMemoryManager()
current_account = GLOBAL_CACHE.Player.GetAccountEmail()

ui = gui.UI()

def configure():
    pass


def main():
    global inventory_frame_hash
    
    if not Routines.Checks.Map.MapValid():
        return
        
    if GLOBAL_CACHE.Player.GetAgentID() != GLOBAL_CACHE.Party.GetPartyLeaderID():
        return                                    
                         
    ui.draw()
    
    # account_mail = GLOBAL_CACHE.Player.GetAccountEmail()
    # if GLOBAL_CACHE.Map.IsExplorable():
    #     if GLOBAL_CACHE.ShMem.FindAccount(account_mail) > -1:
    #         game_option = GLOBAL_CACHE.ShMem.GetHeroAIOptions(account_mail)
    #         if game_option is not None:      
    #             game_option.Following = False
    #             game_option.Avoidance = False
    #             game_option.Looting = False
    #             game_option.Targeting = False
    #             game_option.Combat = True
                
    #             GLOBAL_CACHE.ShMem.SetHeroAIOptions(account_mail, game_option)
    

__all__ = ['main', 'configure']
