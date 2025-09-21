
# Reload imports
import importlib
import math
import os

import PyImGui

from Py4GWCoreLib import ImGui, Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, ThrottledTimer
from Py4GWCoreLib.UIManager import UIManager
from Widgets.frenkey.Core.ui_manager_extensions import UIManagerExtensions


MODULE_NAME = "Distance"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

configure_window = ImGui.WindowModule(MODULE_NAME + "Config", MODULE_NAME + "#Config", (300, 100), (100, 100))

def configure():
    pass


def main():    
    if not Routines.Checks.Map.MapValid():
        return    
            
    
    frame_hash = 2044388929
    frame_id = UIManager.GetFrameIDByHash(frame_hash)

    if UIManagerExtensions.IsElementVisible(frame_id):
        target_id = GLOBAL_CACHE.Player.GetTargetID()
        player_id = GLOBAL_CACHE.Player.GetAgentID()
        if target_id:
            target_pos = GLOBAL_CACHE.Agent.GetXY(target_id)
            player_pos = GLOBAL_CACHE.Agent.GetXY(player_id)
            distance = math.ceil(((target_pos[0] - player_pos[0]) ** 2 + (target_pos[1] - player_pos[1]) ** 2) ** 0.5)
            
            left, top, right, bottom = UIManager.GetFrameCoords(
                frame_id)
            height = (bottom - top) / 4
            font_size = int(height)
            ImGui.push_font("Regular", font_size)
            
            PyImGui.set_next_window_pos(left, bottom - height * 2)
            PyImGui.set_next_window_size(right - left, font_size)
            if PyImGui.begin(MODULE_NAME, PyImGui.WindowFlags.NoTitleBar | PyImGui.WindowFlags.NoMouseInputs | PyImGui.WindowFlags.NoBackground | PyImGui.WindowFlags.NoScrollbar| PyImGui.WindowFlags.NoScrollWithMouse):
                PyImGui.text(f"{distance}")
            
            PyImGui.end()
            ImGui.pop_font()

__all__ = ['main', 'configure']
