
# Reload imports
from enum import IntEnum
import importlib
import json
import math
import os

import PyImGui

from Py4GWCoreLib import ImGui, Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, ThrottledTimer
from Py4GWCoreLib.UIManager import UIManager
from Widgets.frenkey.Core.ui_manager_extensions import UIManagerExtensions


MODULE_NAME = "Health"
save_throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

configure_window = ImGui.WindowModule(MODULE_NAME + "Config", MODULE_NAME + "#Config", (300, 100), (100, 100))

class Settings:
    class Positioning(IntEnum):
        Custom = 0
        Center = 1
        Left = 2
        Right = 3
        
    def __init__(self):
        self.positioning : Settings.Positioning = Settings.Positioning.Center
        self.font_size = 12
        self.save_requested = False

    def to_dict(self):
        return {
            "positioning": self.positioning,
            "font_size": self.font_size
        }
    def request_save(self):
        self.save_requested = True
        
    def save(self):
        with open(os.path.join(script_directory, "Config", "health.json"), "w") as f:
            json.dump(self.to_dict(), f)
            self.save_requested = False
    
    def load(self):
        if not os.path.exists(os.path.join(script_directory, "Config")):
            os.makedirs(os.path.join(script_directory, "Config"))
            
        if not os.path.exists(os.path.join(script_directory, "Config", "health.json")):
            self.save()
            return
        
        with open(os.path.join(script_directory, "Config", "health.json"), "r") as f:
            data = json.load(f)
            self.positioning = Settings.Positioning(data["positioning"])
            self.font_size = data["font_size"]

positioning_names = [e.name for e in Settings.Positioning]
settings = Settings()
settings.load()

def configure():
    configure_window.open = True
    if configure_window.begin():
        positioning = ImGui.combo("Positioning", settings.positioning.value, positioning_names)
        if positioning != settings.positioning:
            settings.positioning = Settings.Positioning(positioning)
            settings.request_save()

        font_size = ImGui.slider_int("Font Size", settings.font_size, 8, 24)
        if font_size != settings.font_size:
            settings.font_size = font_size
            settings.request_save()

    configure_window.end()
    pass


def main():    
    global settings
    
    if not Routines.Checks.Map.MapValid():
        return    
    
    frame_hash = 2044388929
    frame_id = UIManager.GetFrameIDByHash(frame_hash)

    if UIManagerExtensions.IsElementVisible(frame_id):
        target_id = GLOBAL_CACHE.Player.GetTargetID()
        
        if target_id:
            if GLOBAL_CACHE.Agent.IsGadget(target_id):
                return

            left, top, right, bottom = UIManager.GetFrameCoords(
                frame_id)
            
            target_health = GLOBAL_CACHE.Agent.GetHealth(target_id)
            
            health = f"{round(target_health * 100, 2)} %"
            health_total = f"{round(GLOBAL_CACHE.Agent.GetMaxHealth(target_id) * target_health, 0)}"
            health_font = int((bottom - top) / 3)
            
            ImGui.push_font("Regular", health_font)
            health_size = PyImGui.calc_text_size(health)
            ImGui.pop_font()
            
            
            total_health_font = int(health_font * 0.8)
            ImGui.push_font("Regular", total_health_font)
            total_health_size = PyImGui.calc_text_size(health_total)
            ImGui.pop_font()

            position = (0, 0)
            size = (max(health_size[0], total_health_size[0]), health_font * 2)


            match(settings.positioning):
                case Settings.Positioning.Custom:
                    pass
                case Settings.Positioning.Center:
                    position = (left + (right - left) / 2 - size[0] / 2, top + (bottom - top) / 2 - size[1] / 2)
                    pass
                
                case Settings.Positioning.Left:
                    position = (left + 60, (top + (bottom - top) / 4))
                    pass
                
                case Settings.Positioning.Right:
                    position = (right - health_size[0] - 60, (top + (bottom - top) / 4))
                    pass
            
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)
            PyImGui.set_next_window_pos(*position)
            PyImGui.set_next_window_size(*size)
            
            if PyImGui.begin(MODULE_NAME, PyImGui.WindowFlags.NoTitleBar | PyImGui.WindowFlags.NoMouseInputs | PyImGui.WindowFlags.NoBackground | PyImGui.WindowFlags.NoScrollbar| PyImGui.WindowFlags.NoScrollWithMouse):
                ImGui.push_font("Regular", health_font)
                PyImGui.text(health)
                ImGui.pop_font()
                
                ImGui.push_font("Regular", total_health_font)
                PyImGui.text(f"{int(health_total)}")
                ImGui.pop_font()
            
            PyImGui.end()
            PyImGui.pop_style_var(1)

            
    if save_throttle_timer.IsExpired():
        save_throttle_timer.Reset()
        
        if settings.save_requested:
            settings.save()
    
    configure_window.open = False

__all__ = ['main', 'configure']
