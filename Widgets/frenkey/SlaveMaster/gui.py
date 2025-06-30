
import ctypes
from ctypes import wintypes
import math
import os
import Py4GW
import PyImGui
from Py4GWCoreLib import IconsFontAwesome5, ImGui, UIManager
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import HeroAIOptionStruct
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Widgets.frenkey.LootEx import utility
import Widgets.frenkey.SlaveMaster.commands
from Widgets.frenkey.SlaveMaster.ui_manager_extensions import UIManagerExtensions
import importlib


importlib.reload(Widgets.frenkey.SlaveMaster.commands)


class UI:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(UI, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.window = None
        self.commands = Widgets.frenkey.SlaveMaster.commands.Commands()
        self.commands_list = self.commands.commands
        self.account_mail = GLOBAL_CACHE.Player.GetAccountEmail()
        file_directory = os.path.dirname(os.path.abspath(__file__))
        self.icon_textures_path = os.path.join(file_directory, "textures")
        self.skill_textures_path = os.path.join(utility.Util.GetPy4GWPath(), "Textures", "Items")
        self.skill_textures_path = os.path.join(utility.Util.GetPy4GWPath(), "Textures", "Skill_Icons")
        self.options = HeroAIOptionStruct()

    def draw(self):
        """Draw the main UI components."""
        self.draw_window()
        self.draw_command_bar()

        # Add other UI components here as needed
        # self.draw_inventory_controls()
        # self.draw_vault_controls()

    def draw_window(self):
        """Draw the main window."""

        pass

    def draw_command_bar(self):
        """Draw the main window."""

        skill_bar_hash = 641635682
        self.frame_id = UIManager.GetFrameIDByHash(skill_bar_hash)

        if UIManagerExtensions.IsElementVisible(self.frame_id):
            self.left, self.top, self.right, self.bottom = UIManager.GetFrameCoords(
                self.frame_id)

            height = (self.bottom - self.top) * 2
            width = 300
            spacing = 10
            button_spacing = 2
            button_size = 38
            columns = math.floor(width // (button_size + button_spacing))
            PyImGui.set_next_window_pos(self.left - width - spacing, self.bottom - (height))
            PyImGui.set_next_window_size(width, height)
            
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, button_spacing * 2, button_spacing * 2)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, button_spacing, button_spacing)

            PyImGui.begin_with_close("Slave Master Command Bar", True, PyImGui.WindowFlags.NoMove |
                                     PyImGui.WindowFlags.NoResize | PyImGui.WindowFlags.NoCollapse | PyImGui.WindowFlags.NoTitleBar)
            if PyImGui.is_rect_visible(0, 20):
                PyImGui.begin_table("Commands Table", columns,
                                    PyImGui.TableFlags.NoFlag)

                self.options.Following = ImGui.toggle_button(IconsFontAwesome5.ICON_RUNNING + "##Following", self.options.Following,40,40)
                ImGui.show_tooltip("Following")
                PyImGui.table_next_column()
                self.options.Avoidance = ImGui.toggle_button(IconsFontAwesome5.ICON_PODCAST + "##Avoidance", self.options.Avoidance,40,40)
                ImGui.show_tooltip("Avoidance")
                PyImGui.table_next_column()
                self.options.Looting = ImGui.toggle_button(IconsFontAwesome5.ICON_COINS + "##Looting", self.options.Looting,40,40)
                ImGui.show_tooltip("Looting")
                PyImGui.table_next_column()
                self.options.Targeting = ImGui.toggle_button(IconsFontAwesome5.ICON_BULLSEYE + "##Targeting", self.options.Targeting,40,40)
                ImGui.show_tooltip("Targeting")
                PyImGui.table_next_column()
                self.options.Combat = ImGui.toggle_button(IconsFontAwesome5.ICON_SKULL_CROSSBONES + "##Combat", self.options.Combat,40,40)
                ImGui.show_tooltip("Combat")
                            
                if not self.account_mail or self.account_mail != GLOBAL_CACHE.Player.GetAccountEmail():
                    ConsoleLog("SlaveMaster", "No current account set, cannot handle messages.")
                    self.account_mail = GLOBAL_CACHE.Player.GetAccountEmail()  
                
                options = GLOBAL_CACHE.ShMem.GetHeroAIOptions(self.account_mail) if self.account_mail else None
                if options is not None:
                    options.Following = self.options.Following
                    options.Avoidance = self.options.Avoidance
                    options.Looting = self.options.Looting
                    options.Targeting = self.options.Targeting
                    options.Combat = self.options.Combat
                    # GLOBAL_CACHE.ShMem.SetHeroAIOptions(self.account_mail, options)
                    
                # PyImGui.table_next_column()
                # PyImGui.table_next_column()
                # if PyImGui.button(IconsFontAwesome5.ICON_SKULL_CROSSBONES + f"##MoveWindows", button_size, button_size):
                #     user32 = ctypes.WinDLL('user32', use_last_error=True)
                #     SetWindowTextW = user32.SetWindowTextW
                #     SetWindowTextW.restype = wintypes.BOOL
                #     SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
                                        
                #     MoveWindow = user32.MoveWindow
                #     MoveWindow.restype = wintypes.BOOL
                #     MoveWindow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.BOOL]

                    
                #     window_handle = Py4GW.Console.get_gw_window_handle() 
                
                #     ConsoleLog("SlaveMaster", f"Moving window: {window_handle}", Py4GW.Console.MessageType.Info)
                #     MoveWindow(
                #         window_handle, 
                #         0,  # x position #1273
                #         0,  # y position
                #         2574,  # width
                #         1399,  # height
                #         True  # repaint the window
                #     )       

                #     ConsoleLog("SlaveMaster", f"Moved window: {window_handle}", Py4GW.Console.MessageType.Info)
                #     ConsoleLog("SlaveMaster", f"Setting window title: {Player.GetName()} - Guild Wars", Py4GW.Console.MessageType.Info)
                #     ## Set window title 
                #     SetWindowTextW(
                #         window_handle, 
                #         "ASDASD ASD ASD ASD ASD "
                #     )
                
                #     pass
                
                PyImGui.table_next_column()
                
                if ImGui.ImageButton("##SpiritPrep", os.path.join(self.skill_textures_path, "[1240] - Soul Twisting.jpg"), button_size, button_size, 0):
                    self.commands.prep_spirits()
                    
                PyImGui.table_next_row()    
                                         
                for command in self.commands_list:
                    PyImGui.table_next_column()
                    if PyImGui.button(command.icon + f"##{command.name}", button_size, button_size):
                        command.execute()
                    
                    ImGui.show_tooltip(command.name)

                PyImGui.end_table()

            PyImGui.end()
            
            PyImGui.pop_style_var(2)

        pass
