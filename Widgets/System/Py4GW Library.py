MODULE_NAME = "Py4GW Library"

import os
import traceback
import Py4GW
import PyImGui
from Py4GWCoreLib import ImGui, IniManager, Player
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.ImGui_src.IconsFontAwesome5 import IconsFontAwesome5
from Py4GWCoreLib.ImGui_src.Style import Style
from Py4GWCoreLib.enums_src.Multiboxing_enums import SharedCommandType
from Py4GWCoreLib.py4gwcorelib_src.Color import Color, ColorPalette
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import Widget, get_widget_handler

Utils.ClearSubModules(MODULE_NAME.replace(" ", ""))
from Sources.frenkey.Py4GWLibrary.library import ModuleBrowser
from Sources.frenkey.Py4GWLibrary.module_cards import draw_widget_card


widget_filter = ""
widget_manager = get_widget_handler()
filtered_widgets : list[Widget] = []

INI_KEY = ""
INI_PATH = f"Widgets/{MODULE_NAME}"
INI_FILENAME = f"{MODULE_NAME}.ini"
ModuleBrowserInstance : ModuleBrowser | None = None

def on_enable():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} loaded successfully.")

def on_disable():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} unloaded successfully.")
    
def configure():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} configuration opened.")

def draw():    
    global widget_filter
    
    if not INI_KEY:
        return
            
    if INI_KEY:
        global ModuleBrowserInstance
        
        if ModuleBrowserInstance is None:
            ModuleBrowserInstance = ModuleBrowser(INI_KEY, MODULE_NAME, widget_manager)
            
        ModuleBrowserInstance.draw_window()
    
def update():
    pass

def main():
    global INI_KEY
    
    if not INI_KEY:
        if not os.path.exists(INI_PATH):
            os.makedirs(INI_PATH, exist_ok=True)

        INI_KEY = IniManager().ensure_global_key(
            INI_PATH,
            INI_FILENAME
        )
        
        if not INI_KEY: return
        
        # widget_manager.MANAGER_INI_KEY = INI_KEY
        
        # widget_manager.discover()
        # _add_config_vars()
        IniManager().load_once(INI_KEY)

        # FIX 1: Explicitly load the global manager state into the handler
        widget_manager.enable_all = bool(IniManager().get(key=INI_KEY, var_name="enable_all", default=False, section="Configuration"))
        widget_manager._apply_ini_configuration()
        
    
# These functions need to be available at module level
__all__ = ['on_enable', 'on_disable', 'configure', 'draw', 'update', 'main']

if __name__ == "__main__":
    main()
