
import math
import PyImGui
from Py4GWCoreLib import ImGui, UIManager
import Widgets.SlaveMasterLib.commands
from Widgets.SlaveMasterLib.ui_manager_extensions import UIManagerExtensions
import importlib


importlib.reload(Widgets.SlaveMasterLib.commands)


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
        self.commands = Widgets.SlaveMasterLib.commands.Commands().commands

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

            height = self.bottom - self.top
            width = 300
            spacing = 10
            button_spacing = 2
            button_size = 38
            columns = math.floor(width // (button_size + button_spacing))
            PyImGui.set_next_window_pos(self.left - width - spacing, self.top)
            PyImGui.set_next_window_size(width, height)
            
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, button_spacing * 2, button_spacing * 2)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, button_spacing, button_spacing)

            PyImGui.begin_with_close("Slave Master Command Bar", True, PyImGui.WindowFlags.NoMove |
                                     PyImGui.WindowFlags.NoResize | PyImGui.WindowFlags.NoCollapse | PyImGui.WindowFlags.NoTitleBar)
            if PyImGui.is_rect_visible(0, 20):
                PyImGui.begin_table("Commands Table", columns,
                                    PyImGui.TableFlags.NoFlag)

                for command in self.commands:
                    PyImGui.table_next_column()
                    if PyImGui.button(command.icon + f"##{command.name}", button_size, button_size):
                        command.action()
                    
                    ImGui.show_tooltip(command.name)

                PyImGui.end_table()

            PyImGui.end()
            
            PyImGui.pop_style_var(2)

        pass
