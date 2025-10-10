
# Reload imports
import importlib
from multiprocessing.dummy import Process
import os
import ctypes
import sys

from Py4GW import Console

from Py4GWCoreLib import ImGui, Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, ThrottledTimer

MODULE_NAME = "Multiboxing Manager"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

sharedMemoryManager = Py4GWSharedMemoryManager()
module_window = ImGui.WindowModule(MODULE_NAME, MODULE_NAME, (400, 800), (200, 100))
client_title = ""

def configure():
    pass

import subprocess
import sys

def try_set_title(hwnd, new_title):
    hwnd_str = hex(hwnd)

    try:
        script = "Addons\\set_title.py"
        _ = subprocess.run(
            ["python", script, hwnd_str, new_title],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=0.05,
        )
        
    except subprocess.TimeoutExpired:
        pass

def draw():
    global client_title
    
    if module_window.begin():
        pass

    client_title = ImGui.input_text("Client Title", client_title)

    if ImGui.button("Set Client Title") and client_title != "":
        try_set_title(Console.get_gw_window_handle(), client_title)
                
    if ImGui.button("Apply Geometry"):
        Console.set_window_geometry(100, 100, 1200, 800)

    module_window.end()


def main():    
    draw()
    
    if not Routines.Checks.Map.MapValid():
        return    
            
    if not GLOBAL_CACHE.Map.IsExplorable():
        return                    
        
        

__all__ = ['main', 'configure']
