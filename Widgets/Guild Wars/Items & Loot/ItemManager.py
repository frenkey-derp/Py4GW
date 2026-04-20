
import Py4GW

from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils

Utils.ClearSubModules("ItemHandling")
Utils.ClearSubModules("ItemManager")
Utils.ClearSubModules("frenkeyLib.Core")

from Sources.frenkeyLib.ItemManager.config import Config
from Sources.frenkeyLib.ItemManager.ui import UI

MODULE_NAME = "Item Manager"
MODULE_ICON = "Textures\\Module_Icons\\item_manager.png"

MODULE_CONFIG = Config()
MODULE_UI : UI | None = None

def tooltip():
    pass


def configure():    
    pass


def main():
    global MODULE_UI
    
    try:
        if not Routines.Checks.Map.MapValid():
            return
        
        if not MODULE_CONFIG._ensure_ini():
            return
        
        if MODULE_UI is None:
            Py4GW.Console.Log(MODULE_NAME, "Initializing UI...", Py4GW.Console.MessageType.Info)
            MODULE_UI = UI(MODULE_CONFIG)
            MODULE_UI.floating_button.load_visibility()
        
        MODULE_UI.floating_button.visible = True
        MODULE_UI.draw()
    
    except Exception as e:
        Py4GW.Console.Log(MODULE_NAME, f"Error: {e}", Py4GW.Console.MessageType.Error)
        raise

# These functions need to be available at module level
__all__ = ['main', 'configure', 'tooltip']