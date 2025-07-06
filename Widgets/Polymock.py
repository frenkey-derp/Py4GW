
# Reload imports
import importlib
import os
from Widgets.frenkey.Polymock import gui

from Py4GWCoreLib import Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, ThrottledTimer

importlib.reload(gui)

MODULE_NAME = "Polymock"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))


sharedMemoryManager = Py4GWSharedMemoryManager()

ui = gui.UI()

def configure():
    pass


def main():    
    if not Routines.Checks.Map.MapValid():
        return                         
                         
    ui.draw()
        

__all__ = ['main', 'configure']
