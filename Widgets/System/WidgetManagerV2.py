MODULE_NAME = "Py4GW Browser"

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
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import Widget, get_widget_handler


widget_filter = ""
widget_manager = get_widget_handler()
filtered_widgets : list[Widget] = []

INI_KEY = ""
INI_PATH = f"Widgets/{MODULE_NAME}"
INI_FILENAME = f"{MODULE_NAME}.ini"

def on_enable():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} loaded successfully.")

def on_disable():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} unloaded successfully.")
    
def configure():
    Py4GW.Console.Log(MODULE_NAME, f"{MODULE_NAME} configuration opened.")

def _push_card_style(style : Style, enabled : bool):
    CARD_BACKGROUND_COLOR = Color(200, 200, 200, 20)
    CARD_ENABLED_BACKGROUND_COLOR = Color(90, 255, 90, 30)
    style.ChildBg.push_color(CARD_ENABLED_BACKGROUND_COLOR.rgb_tuple if enabled else CARD_BACKGROUND_COLOR.rgb_tuple)
    style.ChildBorderSize.push_style_var(2.0 if enabled else 1.0) 
    style.ChildRounding.push_style_var(4.0)
    style.Border.push_color(CARD_ENABLED_BACKGROUND_COLOR.opacify(0.6).rgb_tuple if enabled else CARD_BACKGROUND_COLOR.opacify(0.6).rgb_tuple)
    pass

def _pop_card_style(style : Style):
    style.ChildBg.pop_color()
    style.ChildBorderSize.pop_style_var()
    style.ChildRounding.pop_style_var()
    style.Border.pop_color()
    pass

def _push_tag_style(style : Style, color : tuple):
    style.FramePadding.push_style_var(4, 4)
    style.Button.push_color(color)
    style.ButtonHovered.push_color(color)
    style.ButtonActive.push_color(color)
    ImGui.push_font("Regular", 12)

def _pop_tag_style(style : Style):
    style.FramePadding.pop_style_var()
    style.Button.pop_color()
    style.ButtonHovered.pop_color()
    style.ButtonActive.pop_color()
    ImGui.pop_font()
   

def draw_widget_card(widget : Widget, CARD_WIDTH : float):
    """
    Draws a single widget card.
    Must be called inside a grid / SameLine layout.
    """
    CARD_HEIGHT = 88
    IMAGE_SIZE = 40
    PADDING = 10
    TAG_HEIGHT = 18
    BUTTON_HEIGHT = 24
    ROUNDING = 6.0
    NAME_COLOR = Color(255, 255, 255, 255)
    NAME_ENABLED_COLOR = Color(150, 255, 150, 255)
    CATEGORY_COLOR = Color(150, 150, 150, 255)
    SYSTEM_COLOR = Color(255, 0, 0, 255)
    TAG_COLOR = Color(38, 51, 59, 255)

    style = ImGui.get_style()
    _push_card_style(style, widget.enabled)
    
    opened = PyImGui.begin_child(
        f"##widget_card_{widget.folder_script_name}",
        (CARD_WIDTH, CARD_HEIGHT),
        border=True,
        flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse
    )
    
    if opened and PyImGui.is_rect_visible(CARD_WIDTH, CARD_HEIGHT):
        available_width = PyImGui.get_content_region_avail()[0]
        
        # --- Top Row: Icon + Title ---
        PyImGui.begin_group()

        # Icon
        ImGui.image(widget.image, (IMAGE_SIZE, IMAGE_SIZE), border_color=CATEGORY_COLOR.rgb_tuple)

        PyImGui.same_line(0, 5)

        # Title + Category
        PyImGui.begin_group()
        ImGui.push_font("Regular", 15)
        name = ImGui.trim_text_to_width(text=widget.name, max_width=CARD_WIDTH - IMAGE_SIZE - BUTTON_HEIGHT - PADDING * 4)
        ImGui.text_colored(name, NAME_COLOR.color_tuple if not widget.enabled else NAME_ENABLED_COLOR.color_tuple, 15)
        ImGui.pop_font()
        
        PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 4)
        PyImGui.separator()

        PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 2)
        ImGui.text_colored(f"{widget.category}", CATEGORY_COLOR.color_tuple if widget.category != "System" else SYSTEM_COLOR.color_tuple, 12)

        PyImGui.end_group()
                
        if widget.has_configure_property:
            PyImGui.set_cursor_pos(available_width - 8, 2)
            ImGui.toggle_icon_button(IconsFontAwesome5.ICON_COG, widget.configuring, BUTTON_HEIGHT, BUTTON_HEIGHT)
        PyImGui.end_group()

        # --- Tags ---
        _push_tag_style(style, TAG_COLOR.rgb_tuple)
        PyImGui.begin_group()
        for i, tag in enumerate(widget.tags):
            if i > 0:
                PyImGui.same_line(0, 2)

            PyImGui.button(tag)
        PyImGui.end_group()
        _pop_tag_style(style)


    PyImGui.end_child()
    
    if PyImGui.is_item_clicked(0):
        widget.enable() if not widget.enabled else widget.disable()
        
    if PyImGui.is_item_hovered():
        if widget.has_tooltip_property:
            try:
                if widget.tooltip:
                    widget.tooltip()
            except Exception as e:
                Py4GW.Console.Log("WidgetHandler", f"Error during tooltip of widget {widget.folder_script_name}: {str(e)}", Py4GW.Console.MessageType.Error)
                Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
        else:
            PyImGui.show_tooltip(f"Enable/Disable {widget.name} widget")

    _pop_card_style(style)
    
def draw_compact_widget_card(widget : Widget, CARD_WIDTH : float):
    """
    Draws a single widget card.
    Must be called inside a grid / SameLine layout.
    """
    CARD_HEIGHT = 30
    IMAGE_SIZE = 40
    PADDING = 10
    TAG_HEIGHT = 18
    BUTTON_HEIGHT = 24
    ROUNDING = 6.0
    NAME_COLOR = Color(255, 255, 255, 255)
    NAME_ENABLED_COLOR = Color(150, 255, 150, 255)
    CATEGORY_COLOR = Color(150, 150, 150, 255)
    SYSTEM_COLOR = Color(255, 0, 0, 255)
    TAG_COLOR = Color(38, 51, 59, 255)

    style = ImGui.get_style()
    _push_card_style(style, widget.enabled)
    
    opened = PyImGui.begin_child(
        f"##widget_card_{widget.folder_script_name}",
        (CARD_WIDTH, CARD_HEIGHT),
        border=True,
        flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse
    )
    
    if opened and PyImGui.is_rect_visible(CARD_WIDTH, CARD_HEIGHT):
        available_width = PyImGui.get_content_region_avail()[0]

        ImGui.push_font("Regular", 15)
        name = ImGui.trim_text_to_width(text=widget.name, max_width=available_width - 20)
        ImGui.text_colored(name, NAME_COLOR.color_tuple if not widget.enabled else NAME_ENABLED_COLOR.color_tuple, 15)
        ImGui.pop_font()
                        
        if widget.has_configure_property:
            PyImGui.set_cursor_pos(available_width - 10, 2)
            ImGui.toggle_icon_button(IconsFontAwesome5.ICON_COG, widget.configuring, BUTTON_HEIGHT, BUTTON_HEIGHT)

    PyImGui.end_child()
    
    if PyImGui.is_item_clicked(0):
        widget.enable() if not widget.enabled else widget.disable()
        
    if PyImGui.is_item_hovered():
        if widget.has_tooltip_property:
            try:
                if widget.tooltip:
                    widget.tooltip()
            except Exception as e:
                Py4GW.Console.Log("WidgetHandler", f"Error during tooltip of widget {widget.folder_script_name}: {str(e)}", Py4GW.Console.MessageType.Error)
                Py4GW.Console.Log("WidgetHandler", f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
        else:
            PyImGui.show_tooltip(f"Enable/Disable {widget.name} widget")

    _pop_card_style(style)
    
def draw_widget(widget: Widget, card_width: float):
    if ImGui.begin_child(f"widget_card_{widget.folder_script_name}", (card_width, 50), True):
        ImGui.text(f"{widget.name or widget.plain_name} ")
    
    ImGui.end_child()
    pass

def filter_widgets(filter_text: str):
    global filtered_widgets, widget_manager, tree
    
    filtered_widgets.clear()
    if not filter_text:
        return
    
    filtered_widgets = [w for w in widget_manager.widgets.values() if filter_text.lower() in w.plain_name.lower() or filter_text.lower() in w.folder.lower()]
    
def draw():    
    global widget_filter
    
    if not INI_KEY:
        return
            
    if INI_KEY:
        PyImGui.set_next_window_size((500, 300), PyImGui.ImGuiCond.Once)
        if ImGui.Begin(ini_key=INI_KEY, name=MODULE_NAME):            
            PyImGui.push_item_width(-1)
            changed, widget_filter = ImGui.search_field("##WidgetFilter", widget_filter)
            PyImGui.pop_item_width()
            if changed:
                filter_widgets(widget_filter)
                
            ImGui.separator()
            
            style = ImGui.get_style()
            style.DisabledAlpha.push_style_var(0.4)      
            
            min_card_width = 250
            available_width = PyImGui.get_content_region_avail()[0]
            num_columns = max(1, int(available_width // min_card_width))
            card_width = 0
            PyImGui.columns(num_columns, "widget_cards", False)
                 
            for widget in (filtered_widgets if widget_filter else widget_manager.widgets.values()):
                card_width = PyImGui.get_content_region_avail()[0]
                draw_widget_card(widget, card_width)
                PyImGui.next_column()
            
                
            style.DisabledAlpha.pop_style_var()
            PyImGui.end_columns()
                
        ImGui.End(INI_KEY)
    
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
