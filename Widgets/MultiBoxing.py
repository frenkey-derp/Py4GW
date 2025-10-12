
import ctypes
from enum import IntEnum
import os
from typing import Optional

from Py4GW import Console
import PyImGui

from Py4GWCoreLib import ImGui, Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.ImGui_src.IconsFontAwesome5 import IconsFontAwesome5
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, ThrottledTimer
from Py4GWCoreLib.enums_src.IO_enums import Key
from Py4GWCoreLib.py4gwcorelib_src.Color import Color
from Py4GW_widget_manager import WidgetHandler

MODULE_NAME = "MultiBoxing"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

module_window = ImGui.WindowModule(MODULE_NAME, MODULE_NAME, (300, 600))
configure_window = ImGui.WindowModule(MODULE_NAME, MODULE_NAME + " Configure", (1400, 800), can_close=True)
accounts = []
ratio = 2574 / 1400  # Frenkeys main window size ratio

widget_handler = WidgetHandler()
module_info = None

class Settings:
    def __init__(self):
        screen_size = self.get_screen_size()
        screen_size = (2560, 1440)  # For testing, assume 1440p
        
        main_size = (2574, 1400) # This is just frenkeys main window size
        x,y = (screen_size[0] - main_size[0]) // 2, (screen_size[1] - main_size[1]) // 2
        scr = (x, y, main_size[0], main_size[1])
        
        self.main_region : tuple[int, int, int, int] = (scr)  # x, y, width, height
        self.sub_regions : dict[str, tuple[int, int, int, int]] = {}
        self.screen_size : tuple[int, int] = screen_size
        self.snap_to_edges : bool = True
        self.edge_snap_distance : int = 15
        
        self.columns : int = 1
        self.rows : int = 1
        self.layout_import_rows : str = "1 1 1"
        self.layout_import_columns : str = "1 1 1"
    pass

    def get_screen_size(self) -> tuple[int, int]:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        return screen_width, screen_height

settings = Settings()

class Region:
    class ResizeDirection(IntEnum):
        NONE = 0
        TOP = 1
        BOTTOM = 2
        LEFT = 4
        RIGHT = 8
        TOP_LEFT = TOP | LEFT
        TOP_RIGHT = TOP | RIGHT
        BOTTOM_LEFT = BOTTOM | LEFT
        BOTTOM_RIGHT = BOTTOM | RIGHT
        
    def __init__(self, x: int = 0, y: int = 0, w: int = 300, h: int = 200, name: str = "Region", account: str = "", color: Optional[Color] = None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.color = color if color else Color.random()
        
        self.selected = False
        self.dragging = False
        self.resizing = False
        self.resize_grab_size = 12
        self.resize_direction = Region.ResizeDirection.NONE
        
        self.name : str = name
        self.account : str = account

    def rect(self, scale: float = 1.0) -> tuple[float, float, float, float]:
        return (self.x * scale, self.y * scale, (self.x + self.w) * scale, (self.y + self.h) * scale)

    def contains(self, mx, my, scale: float = 1.0):
        x1, y1, x2, y2 = self.rect(scale)
        return x1 <= mx <= x2 and y1 <= my <= y2

    def on_resize_zone(self, mx, my, scale: float = 1.0) -> "Region.ResizeDirection":
        x1, y1, x2, y2 = self.rect(scale)
        grab = self.resize_grab_size

        if x1 <= mx <= x1 + grab and y1 <= my <= y1 + grab:
            return Region.ResizeDirection.TOP_LEFT
        
        if x2 - grab <= mx <= x2 and y1 <= my <= y1 + grab:
            return Region.ResizeDirection.TOP_RIGHT
        
        if x1 <= mx <= x1 + grab and y2 - grab <= my <= y2:
            return Region.ResizeDirection.BOTTOM_LEFT
        
        if x2 - grab <= mx <= x2 and y2 - grab <= my <= y2:
            return Region.ResizeDirection.BOTTOM_RIGHT
        
        if x1 <= mx <= x1 + grab: 
            return Region.ResizeDirection.LEFT
        
        elif x2 - grab <= mx <= x2: 
            return Region.ResizeDirection.RIGHT
        
        elif y1 <= my <= y1 + grab:
            return Region.ResizeDirection.TOP
        
        elif y2 - grab <= my <= y2:
            return Region.ResizeDirection.BOTTOM

        return Region.ResizeDirection.NONE

    def draw(self, origin_x: float, origin_y: float, scale: float = 1.0):
        text_display = f"{self.name if not self.account else self.account}"
        
        # Compute rectangle coordinates and size
        x1, y1, x2, y2 = self.rect(scale)
        width = x2 - x1
        height = y2 - y1

        # Apply origin offset
        x1 += origin_x
        y1 += origin_y
        x2 += origin_x
        y2 += origin_y

        # Background + border
        PyImGui.draw_list_add_rect_filled(
            x1, y1, x2, y2, self.color.opacify(0.15).color_int, 0, 0
        )
        PyImGui.draw_list_add_rect(
            x1, y1, x2, y2, self.color.color_int, 0, 0, 1
        )
        
        # Resize handles
        # Top-left
        PyImGui.draw_list_add_triangle_filled(
            x1, y1 + self.resize_grab_size,
            x1, y1,
            x1 + self.resize_grab_size, y1,
            self.color.opacify(0.5).color_int
        )
        
        # Top-right
        PyImGui.draw_list_add_triangle_filled(
            x2 - 1 - self.resize_grab_size, y1,
            x2 - 1, y1,
            x2 - 1, y1 + self.resize_grab_size,
            self.color.opacify(0.5).color_int
        )
        
        # Bottom-left
        PyImGui.draw_list_add_triangle_filled(
            x1, y2 - 1 - self.resize_grab_size,
            x1, y2 - 1,
            x1 + self.resize_grab_size, y2 - 1,
            self.color.opacify(0.5).color_int
        )
        
        # Bottom-right
        PyImGui.draw_list_add_triangle_filled(
            x2 - 1 - self.resize_grab_size, y2 - 1,
            x2 - 1 , y2 - 1,
            x2 - 1, y2 - 1 - self.resize_grab_size,
            self.color.opacify(0.5).color_int
        )

        # --- Improved font scaling ---
        # Base font size (e.g. 13–16 depending on current ImGui font)
        start_font_size = PyImGui.get_text_line_height()

        # Measure text at base font size
        base_text_size = PyImGui.calc_text_size(text_display)
        base_width, base_height = base_text_size

        # Determine scaling factors for width and height constraints
        # (How much we can grow before exceeding available box)
        # Add a 4px vertical padding margin
        available_width = width - 6
        available_height = height - 4

        # Avoid division by zero
        if base_width <= 0 or base_height <= 0:
            return

        scale_x = available_width / base_width
        scale_y = available_height / base_height

        # Choose smallest scale factor to fit both width & height
        scale_factor = min(scale_x, scale_y)

        # Compute new font size relative to start font size
        font_size = start_font_size * scale_factor

        # Clamp the final font size to a reasonable range
        font_size = max(10, min(32, font_size))

        # Apply and render text
        ImGui.push_font("Regular", int(font_size))
        text_size = PyImGui.calc_text_size(text_display)

        PyImGui.push_clip_rect(x1, y1, width, height, True)
        PyImGui.draw_list_add_text(
            x1 + ((width - text_size[0]) / 2),
            y1 + ((height - text_size[1]) / 2),
            self.color.opacify(1).color_int,
            text_display,
        )
        ImGui.pop_font()
        
        details_text = f"{self.w}x{self.h} @ {self.x},{self.y}"
        details_size = PyImGui.calc_text_size(details_text)
        PyImGui.draw_list_add_text(
            x1 + ((width - details_size[0]) / 2),
            y1 + height - details_size[1] - 2,
            self.color.opacify(1).color_int,
            details_text,
        )
        PyImGui.pop_clip_rect()


regions: list[Region] = []
active_region: Optional[Region] = None  
screen_size_changed : bool = False

def set_window_active(handle: int):
    try:
        ctypes.windll.user32.SetForegroundWindow(handle)
    except Exception as e:
        ConsoleLog(MODULE_NAME, f"Error setting window active: {e}", message_type=1)
    pass

def configure():
    global module_info
    
    if not module_info:
        module_info = widget_handler.get_widget_info(MODULE_NAME)
        
    try:
        draw_configure_window()
        
    except Exception as e:
        ConsoleLog(MODULE_NAME, f"Error in draw(): {e}", message_type=1)

def draw():
    global module_window, accounts
    if not module_window.open:
        return
    
    if module_window.begin():        
        i = 0
        for account in accounts:
            i += 1           
            btn_text = f"{i}: {account.AccountEmail} - {account.CharacterName}"
            btn_text = f"Account #{i}"
            
            if account.AccountEmail == GLOBAL_CACHE.Player.GetAccountEmail():
                continue
            
            if ImGui.button(btn_text):
                # ConsoleLog(MODULE_NAME, f"Switching to account: {account.AccountEmail} - {account.CharacterName}")
                set_window_active(account.WindowHandle)
                pass
        
        if ImGui.begin_tab_bar("##ConfigTabs"):
            if ImGui.begin_tab_item("Settings"):
                ImGui.text("Settings go here.")
                ImGui.end_tab_item()
            if ImGui.begin_tab_item("Help"):
                ImGui.text("Help information goes here.")
                ImGui.end_tab_item()
            ImGui.end_tab_bar()
        
        pass
    
    module_window.end()
    
def center_aligned_text(text: str, area_width: float):
    text_size = PyImGui.calc_text_size(text)
    text_width = text_size[0]
    if area_width > text_width:
        cursor_x = (area_width - text_width) / 2
        PyImGui.set_cursor_pos_x(cursor_x)
    ImGui.text(text)

def ensure_regions_within_bounds():
    for region in regions:
        region.x = max(0, min(region.x, settings.screen_size[0] - region.w))
        region.y = max(0, min(region.y, settings.screen_size[1] - region.h))
        region.w = min(region.w, settings.screen_size[0])
        region.h = min(region.h, settings.screen_size[1])

def add_region(region: Region):
    regions.append(region)

def draw_row_icon(width, height, rows : int = 4, even_color: Optional[Color] = None, odd_color: Optional[Color] = None):
    PyImGui.dummy(width, height)
    
    item_rect_min = PyImGui.get_item_rect_min()
    item_rect_max = PyImGui.get_item_rect_max()
    
    x, y = item_rect_min
    width = item_rect_max[0] - item_rect_min[0]
    height = item_rect_max[1] - item_rect_min[1]
    
    even_color = even_color if even_color else Color(200, 200, 200, 200)
    odd_color = odd_color if odd_color else Color(100, 100, 100, 100)
    
    style = ImGui.get_style()
    
    for i in range(rows):
        # draw every uneven row        
            PyImGui.draw_list_add_rect_filled(
                x, y + (i * (height / rows)),
                x + width, y + ((i + 1) * (height / rows)),
                (even_color if i % 2 == 0 else odd_color).color_int,
                style.FrameRounding.get_current().value1,
                PyImGui.DrawFlags.RoundCornersAll
            )

def draw_column_icon(width, height, columns : int = 4, even_color: Optional[Color] = None, odd_color: Optional[Color] = None):
    PyImGui.dummy(width, height)
    
    item_rect_min = PyImGui.get_item_rect_min()
    item_rect_max = PyImGui.get_item_rect_max()
    
    x, y = item_rect_min
    width = item_rect_max[0] - item_rect_min[0]
    height = item_rect_max[1] - item_rect_min[1]
    
    even_color = even_color if even_color else Color(200, 200, 200, 200)
    odd_color = odd_color if odd_color else Color(100, 100, 100, 100)
    
    style = ImGui.get_style()
    
    for i in range(columns):
        # draw every uneven row        
            PyImGui.draw_list_add_rect_filled(
                x + (i * (width / columns)), y,
                x + ((i + 1) * (width / columns)), y + height,
                (even_color if i % 2 == 0 else odd_color).color_int,
                style.FrameRounding.get_current().value1,
                PyImGui.DrawFlags.RoundCornersAll
            )
    

def draw_configure_window():
    global regions, active_region, screen_size_changed
    
    configure_window.open = module_info["configuring"] if module_info else False
    
    if configure_window.begin(None):  
        configure_window.window_flags = PyImGui.WindowFlags.NoFlag
        style = ImGui.get_style()
    
        style.CellPadding.push_style_var(5, 0)
        
        regions_width = 300
        header_height = 105
            
        if ImGui.begin_table("layout_table", 2, PyImGui.TableFlags.NoFlag, 0, 0):
            PyImGui.table_setup_column("left", PyImGui.TableColumnFlags.NoFlag, 0.5)
            PyImGui.table_setup_column("right", PyImGui.TableColumnFlags.WidthFixed, regions_width)
            
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            card_background = style.WindowBg.opacify(0.6).to_tuple()
            
            def draw_configs():
                global screen_size_changed
                
                style.ChildBg.push_color(card_background)
                if ImGui.begin_child("configs", (300, header_height), border=True, flags=PyImGui.WindowFlags.NoScrollbar):      
                    avail = PyImGui.get_content_region_avail()
                    center_aligned_text("Screen Size", avail[0])
                    ImGui.separator()
                            
                    style.ItemSpacing.push_style_var(0, 0)
                    style.CellPadding.push_style_var(0, 0)
                    
                    if ImGui.begin_table("screen_size_table", 3, PyImGui.TableFlags.NoFlag, avail[0] - 5, 25):
                        PyImGui.table_setup_column("Width", PyImGui.TableColumnFlags.NoFlag, 0.5)
                        PyImGui.table_setup_column("x", PyImGui.TableColumnFlags.WidthFixed, 30)
                        PyImGui.table_setup_column("Height", PyImGui.TableColumnFlags.NoFlag, 0.5)
                        
                        PyImGui.table_next_row()
                        PyImGui.table_next_column()
                        
                        PyImGui.push_item_width(PyImGui.get_content_region_avail()[0] - 15)
                        swidth = ImGui.input_int("##width", settings.screen_size[0], 800, 10, PyImGui.InputTextFlags.AutoSelectAll)
                        if swidth != settings.screen_size[0]:
                            settings.screen_size = (max(800, swidth), settings.screen_size[1])
                            screen_size_changed = True
                            
                        input_active = PyImGui.is_item_active()
                            
                        PyImGui.pop_item_width()
                            
                        PyImGui.table_next_column()
                        ImGui.text("x")
                        PyImGui.table_next_column()
                        
                        PyImGui.push_item_width(PyImGui.get_content_region_avail()[0])
                        sheight = ImGui.input_int("##height", settings.screen_size[1], 600, 10, PyImGui.InputTextFlags.AutoSelectAll)
                        if sheight != settings.screen_size[1]:
                            settings.screen_size = (settings.screen_size[0], max(600, sheight))  
                            screen_size_changed = True        
                        
                        input_active = input_active or PyImGui.is_item_active()                    
                        
                        if not input_active and screen_size_changed:
                            screen_size_changed = False
                            ensure_regions_within_bounds()      
                            
                        PyImGui.pop_item_width()
                        ImGui.end_table()
                        
                    style.CellPadding.pop_style_var()
                    style.ItemSpacing.pop_style_var()
                    
                    PyImGui.spacing()
                    settings.snap_to_edges = ImGui.checkbox("Snap to edges", settings.snap_to_edges)                  
                        
                style.ChildBg.pop_color()
                ImGui.end_child()  
            
            def draw_layout_presets():
                style.ChildBg.push_color(card_background)
                style.WindowPadding.push_style_var(0, 0)
                if ImGui.begin_child("layouts", (0, header_height), border=True, flags=PyImGui.WindowFlags.NoScrollbar): 
                    style.ChildBg.pop_color()
                    style.WindowPadding.pop_style_var()
                    
                    if ImGui.begin_child("layouts edit", (PyImGui.get_content_region_avail()[0] / 2, header_height), border=True, flags=PyImGui.WindowFlags.NoScrollbar): 
                        PyImGui.push_item_width(PyImGui.get_content_region_avail()[0] - 35) 
                             
                        draw_column_icon(30, 20, 5)      
                        PyImGui.same_line(0, 5)          
                        settings.layout_import_columns = ImGui.input_text("##Columns##layout_import_columns", settings.layout_import_columns, 0)  
                        ImGui.show_tooltip("Define the column structure using space, comma or semicolon separated integers.\nE.g. '1 2 1' for 3 columns where the middle one is twice as wide as the others.")
                        
                        draw_row_icon(30, 20)      
                        PyImGui.same_line(0, 5)  
                        settings.layout_import_rows = ImGui.input_text("##Rows##layout_import", settings.layout_import_rows, 0)
                        ImGui.show_tooltip("Define the row structure using space, comma or semicolon separated integers.\nE.g. '1 2 1' for 3 rows where the middle one is twice as high as the others.")
                        
                        PyImGui.pop_item_width()
                        
                        if ImGui.button("Create Layout", PyImGui.get_content_region_avail()[0] - 5):
                            try:
                                ## import from strings like "1,2,1", "1 2 1" "1;1;1;1"
                                cols = [int(x) for x in settings.layout_import_columns.replace(";", ",").replace(" ", ",").split(",") if x.strip().isdigit() and int(x.strip()) > 0] if settings.layout_import_columns.strip() else [1]
                                rows = [int(x) for x in settings.layout_import_rows.replace(";", ",").replace(" ", ",").split(",") if x.strip().isdigit() and int(x.strip()) > 0] if settings.layout_import_rows.strip() else [1]

                                if not cols or not rows:
                                    ConsoleLog(MODULE_NAME, "Invalid layout import format. Please provide comma-separated integers for columns and rows.", message_type=1)
                                    return

                                regions.clear()
                                cell_widths = [settings.screen_size[0] // sum(cols) * c for c in cols]
                                cell_heights = [settings.screen_size[1] // sum(rows) * r for r in rows]

                                y_offset = 0
                                for rh in cell_heights:
                                    x_offset = 0
                                    for cw in cell_widths:
                                        region = Region(x_offset, y_offset, cw, rh, name = f"Region {len(regions) + 1}")
                                        regions.append(region)
                                        x_offset += cw
                                    y_offset += rh

                                ConsoleLog(MODULE_NAME, f"Imported layout with {len(regions)} regions.")
                            except Exception as e:
                                ConsoleLog(MODULE_NAME, f"Error importing layout: {e}", message_type=1)
                                
                    ImGui.end_child()
                    
                    PyImGui.same_line(0, 0)
                    
                    if ImGui.begin_child("layouts load and save", (0, header_height), border=True, flags=PyImGui.WindowFlags.NoScrollbar):
                        layouts = []
                        layouts.insert(0, "None")
                        layout_index = layouts.index("None") if "None" in layouts else 0
                        new_layout_index = ImGui.combo("Selected Layout", layout_index, layouts)
                        if new_layout_index != layout_index:
                            pass
                        
                        layout_name = ImGui.input_text("Layout Name", "", 0)
                        
                        if ImGui.button("Save Layout", PyImGui.get_content_region_avail()[0] - 5):
                            pass
                    
                    ImGui.end_child()
                else:
                    style.WindowPadding.pop_style_var()                    
                    style.ChildBg.pop_color()
                    
                ImGui.end_child()
                            
            def draw_regions_edit():
                global active_region
                style.ChildBg.push_color(card_background)
                if ImGui.begin_child("regions", (0, 0), border=True, flags=PyImGui.WindowFlags.NoScrollbar):                                               
                    if ImGui.button("Add Region", PyImGui.get_content_region_avail()[0], 20):
                        new_region = Region(0, 0, 1920, 1080, name = f"Region {len(regions) + 1}")
                        #center the new region
                        new_region.x = (settings.screen_size[0] - new_region.w) // 2
                        new_region.y = (settings.screen_size[1] - new_region.h) // 2
                        
                        regions.append(new_region)
                        
                    PyImGui.spacing()
                    ImGui.separator()
                    PyImGui.spacing()
                    
                    new_active = active_region
                    
                    for region in regions:
                        if region == active_region:       
                            style.ChildBg.push_color(region.color.opacify(0.15).to_tuple())
                            style.Border.push_color(region.color.to_tuple())
                            if ImGui.begin_child("active_region_edit", (0, 260), border=True, flags=PyImGui.WindowFlags.NoScrollbar):
                                style.Border.pop_color()
                                style.ChildBg.pop_color()
                                center_aligned_text(region.name, PyImGui.get_content_region_avail()[0])
                                PyImGui.set_cursor_pos(250 - 2, 4)
                                if ImGui.icon_button(IconsFontAwesome5.ICON_TRASH, 25, 25):
                                    regions.remove(region)
                                    new_active = None
                                    if active_region == region:
                                        active_region = None
                                    ImGui.end_child()
                                    break
                                
                                ImGui.show_tooltip("Delete this region")
                                
                                ImGui.separator()
                                
                                region.name = ImGui.input_text("Name", region.name, 0)
                                account_names = [acc.AccountEmail for acc in accounts]
                                account_names = [f"frenkey+{i+1}@gmail.com" for i in range(8)]
                                account_names.insert(0, "None")
                                
                                account_index = account_names.index(region.account) if region.account in account_names else 0
                                new_account = ImGui.combo("Account", account_index, account_names)
                                if new_account != account_index:
                                    region.account = account_names[new_account]
                                    
                                region.x = ImGui.input_int("X", region.x, 10, 1, PyImGui.InputTextFlags.AutoSelectAll)
                                region.y = ImGui.input_int("Y", region.y, 10, 1, PyImGui.InputTextFlags.AutoSelectAll)
                                region.w = ImGui.input_int("Width", region.w, 10, 1, PyImGui.InputTextFlags.AutoSelectAll)
                                region.h = ImGui.input_int("Height", region.h, 10, 1, PyImGui.InputTextFlags.AutoSelectAll)           
                                color = PyImGui.color_edit4("Color", region.color.color_tuple)
                                if color != region.color.color_tuple:
                                    region.color = Color.from_tuple(color)                   
                            

                            else:
                                style.Border.pop_color()
                                style.ChildBg.pop_color()
                                
                            ImGui.end_child()
                            pass
                        else:
                            style.Button.push_color(region.color.rgb_tuple)
                            style.ButtonTextureBackground.push_color(region.color.rgb_tuple)
                            style.ButtonHovered.push_color(region.color.saturate(0.2).rgb_tuple)
                            style.ButtonTextureBackgroundHovered.push_color(region.color.saturate(0.2).rgb_tuple)
                            style.ButtonActive.push_color(region.color.saturate(0.4).rgb_tuple)
                            style.ButtonTextureBackgroundActive.push_color(region.color.saturate(0.4).rgb_tuple)
                            
                            if ImGui.button(f"{region.name} ({region.w}x{region.h} @ {region.x},{region.y})", PyImGui.get_content_region_avail()[0], 20):
                                new_active = region
                                    
                            style.Button.pop_color()
                            style.ButtonTextureBackground.pop_color()
                            style.ButtonHovered.pop_color()       
                            style.ButtonTextureBackgroundHovered.pop_color()                     
                            style.ButtonActive.pop_color()
                            style.ButtonTextureBackgroundActive.pop_color()
                    
                    if new_active != active_region:
                        active_region = new_active
                        for r in regions:
                            r.selected = (r == active_region)
                            
                style.ChildBg.pop_color()
                ImGui.end_child()
                                     
            draw_configs()
            PyImGui.same_line(0, 5)
            draw_layout_presets()
            if ImGui.begin_child("region_canvas_container", (0, 0), border=False, flags=PyImGui.WindowFlags.NoScrollbar):
                draw_region_canvas(style, PyImGui.get_content_region_avail(), PyImGui.get_cursor_pos_y())
            ImGui.end_child()
            
            PyImGui.table_next_column()
            draw_regions_edit()
            
            ImGui.end_table()
        style.CellPadding.pop_style_var()   
        
        
    configure_window.end()
    
def draw_configure_windowX():
    global regions, active_region, screen_size_changed
    
    configure_window.open = module_info["configuring"] if module_info else False
    
    if configure_window.begin(None):  
        configure_window.window_flags = PyImGui.WindowFlags.NoFlag
        style = ImGui.get_style()
    
        style.ItemSpacing.push_style_var(0, 0)
        style.CellPadding.push_style_var(5, 0)
        
        win_size = PyImGui.get_window_size()

        # Adjust for window padding
        win_size = (
            win_size[0] - (style.WindowPadding.get_current().value1 * 2),
            win_size[1] - ((style.WindowPadding.get_current().value2 or 0) * 2)
        )


        # Header control layout
        header_control_size = (300, 125)
        header_control_pos = ((win_size[0] - header_control_size[0]) / 2, 30)
        header_bottom = header_control_pos[1] + header_control_size[1]
        
        region_edit_size = (300, 125)
        if ImGui.begin_table("layout_table", 2, PyImGui.TableFlags.NoFlag, 0, 0):
            PyImGui.table_setup_column("left", PyImGui.TableColumnFlags.NoFlag, 0.5)
            PyImGui.table_setup_column("right", PyImGui.TableColumnFlags.WidthFixed, region_edit_size[0])
            
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            
            if ImGui.begin_child("header_controls", (0, header_control_size[1]), border=True, flags=PyImGui.WindowFlags.NoScrollbar):      
                ImGui.push_font("Regular", 20)
                center_aligned_text("Regions", header_control_size[0])
                ImGui.pop_font()
                
                ImGui.separator()
                center_aligned_text("Screen Size", header_control_size[0])
                        
                style.ItemSpacing.push_style_var(0, 0)
                style.CellPadding.push_style_var(0, 0)
                
                if ImGui.begin_table("screen_size_table", 3, PyImGui.TableFlags.NoFlag, header_control_size[0] - 5, 25):
                    PyImGui.table_setup_column("Width", PyImGui.TableColumnFlags.NoFlag, 0.5)
                    PyImGui.table_setup_column("x", PyImGui.TableColumnFlags.NoFlag, 0.05)
                    PyImGui.table_setup_column("Height", PyImGui.TableColumnFlags.NoFlag, 0.5)
                    
                    PyImGui.table_next_row()
                    PyImGui.table_next_column()
                    
                    PyImGui.push_item_width(PyImGui.get_content_region_avail()[0] - 15)
                    swidth = ImGui.input_int("##width", settings.screen_size[0], 800, 10, PyImGui.InputTextFlags.AutoSelectAll)
                    if swidth != settings.screen_size[0]:
                        settings.screen_size = (max(800, swidth), settings.screen_size[1])
                        screen_size_changed = True
                        
                    input_active = PyImGui.is_item_active()
                        
                    PyImGui.pop_item_width()
                        
                    PyImGui.table_next_column()
                    ImGui.text("x")
                    PyImGui.table_next_column()
                    
                    PyImGui.push_item_width(PyImGui.get_content_region_avail()[0] - 15)
                    sheight = ImGui.input_int("##height", settings.screen_size[1], 600, 10, PyImGui.InputTextFlags.AutoSelectAll)
                    if sheight != settings.screen_size[1]:
                        settings.screen_size = (settings.screen_size[0], max(600, sheight))  
                        screen_size_changed = True        
                    
                    input_active = input_active or PyImGui.is_item_active()                    
                    
                    if not input_active and screen_size_changed:
                        screen_size_changed = False
                        ensure_regions_within_bounds()      
                        
                    PyImGui.pop_item_width()
                    ImGui.end_table()
                    
                style.CellPadding.pop_style_var()
                style.ItemSpacing.pop_style_var()
                
            ImGui.end_child()
            
            draw_region_canvas(style, win_size, header_bottom)
            
            PyImGui.table_next_column()
                
                
            style.ChildBg.push_color(style.WindowBg.opacify(0.8).to_tuple())
            if ImGui.begin_child("Regions Edit", header_control_size, border=True, flags=PyImGui.WindowFlags.NoScrollbar):
                ImGui.push_font("Regular", 20)
                center_aligned_text("Regions", header_control_size[0])
                ImGui.pop_font()
                
                ImGui.separator()
                center_aligned_text("Screen Size", header_control_size[0])
                
                    
                PyImGui.set_cursor_pos(10, header_control_size[1] - 30)
                if ImGui.button("Add Region", PyImGui.get_content_region_avail()[0], 20):
                    new_region = Region(0, 0, 1920, 1080, name = f"Region {len(regions) + 1}")
                    #center the new region
                    new_region.x = (settings.screen_size[0] - new_region.w) // 2
                    new_region.y = (settings.screen_size[1] - new_region.h) // 2
                    
                    regions.append(new_region)
                pass
            style.ChildBg.pop_color()
                   
            
            ImGui.end_table()
        
        style.CellPadding.pop_style_var()
        style.ItemSpacing.pop_style_var()
            
        
        ImGui.end_child()
        
    if not configure_window.open:
        widget_handler.set_widget_configuring(MODULE_NAME, False)
        
    configure_window.end()

def draw_region_canvas(style, win_size, header_bottom):
    global regions, active_region
    
    screen_cursor_pos = PyImGui.get_cursor_screen_pos()
    
    ratio = settings.screen_size[0] / settings.screen_size[1]
        
        # Default drawing area size
    drawing_area_size = [win_size[0], win_size[0] / ratio]

        # Maintain minimum vertical gap below header
    desired_gap = 5
    available_height = win_size[1] - header_bottom - desired_gap

        # If the drawing area is too tall, shrink proportionally (keeping ratio)
    if drawing_area_size[1] > available_height:
        drawing_area_size[1] = available_height
        drawing_area_size[0] = drawing_area_size[1] * ratio

        # Recalculate horizontal centering (center within current window)
    drawing_area_pos_x = PyImGui.get_cursor_pos_x() + max(0, (win_size[0] - drawing_area_size[0]) / 2)

        # Default vertical position (centered vertically)
    drawing_area_pos_y = (win_size[1] - drawing_area_size[1]) / 2

        # Ensure it stays below the header (keep gap)
    drawing_area_pos_y = max(header_bottom + desired_gap, drawing_area_pos_y)

        # Prevent going off the bottom of the window
    bottom_space = win_size[1] - (drawing_area_pos_y + drawing_area_size[1])
    if bottom_space < 0:
        drawing_area_pos_y += bottom_space  # move up to fit fully

        # Prevent it from leaving the top of the window
    drawing_area_pos_y = max(0, drawing_area_pos_y)

    drawing_area_pos = (drawing_area_pos_x, drawing_area_pos_y)

    scale = drawing_area_size[0] / settings.screen_size[0]

    
            
        # --- Draw the area ---
    PyImGui.set_cursor_pos(drawing_area_pos[0], drawing_area_pos[1])
    drawing_area_screen_pos = PyImGui.get_cursor_screen_pos()

    if ImGui.is_mouse_in_rect((drawing_area_screen_pos[0], drawing_area_screen_pos[1], drawing_area_size[0], drawing_area_size[1])):
        configure_window.window_flags = PyImGui.WindowFlags.NoMove
                    
    if drawing_area_size[0] > 0 and drawing_area_size[1] > 0 and PyImGui.is_rect_visible(drawing_area_size[0], drawing_area_size[1]):
        style.WindowPadding.push_style_var(0, 0)
            
        if PyImGui.begin_child("region_canvas", (drawing_area_size[0], drawing_area_size[1]), False, PyImGui.WindowFlags.NoFlag):
            origin_x, origin_y = PyImGui.get_window_pos()

            io = PyImGui.get_io()
            mx, my = io.mouse_pos_x, io.mouse_pos_y

            canvas_hovered = PyImGui.is_window_hovered()
                    
            left_down = PyImGui.is_mouse_down(0)
            left_clicked = PyImGui.is_mouse_clicked(0)

            for region in regions:
                region.draw(origin_x, origin_y, scale)

                # --- interaction logic ---
            if canvas_hovered:
                hovered = None
                for region in reversed(regions):  # topmost first
                    if region.contains(mx - origin_x, my - origin_y, scale):
                        hovered = region
                        break

                    # click handling
                if left_clicked:                                
                    if hovered:
                            # select
                        active_region = hovered
                                
                        if io.key_ctrl:
                                #copy region
                            if not active_region.resizing:
                                new_region = Region(active_region.x + 20, active_region.y + 20, active_region.w, active_region.h, name = f"{active_region.name} Copy", account = active_region.account, color = active_region.color.copy())
                                regions.append(new_region)
                                active_region = new_region
                                for r in regions:
                                    r.selected = (r == new_region)
                                active_region.dragging = True
                                    
                        for r in regions:
                            r.selected = (r == hovered)
                            # begin drag/resize
                        hovered.resize_direction = hovered.on_resize_zone(mx - origin_x, my - origin_y, scale)
                        
                        if hovered.resize_direction != Region.ResizeDirection.NONE:
                            hovered.resizing = True
                        else:
                            hovered.dragging = True
                    else:
                            # deselect
                        active_region = None
                        for r in regions:
                            r.selected = False

                    # drag or resize
                if left_down and active_region:
                    dx, dy = PyImGui.get_mouse_drag_delta(0, 0)
                                                
                    if active_region.dragging:
                        active_region.x += int(dx * (1/scale))
                        active_region.y += int(dy * (1/scale))
                            
                        if settings.snap_to_edges:
                                # Snap to screen edges
                            if abs(active_region.x) <= settings.edge_snap_distance:
                                active_region.x = 0
                            if abs((active_region.x + active_region.w) - settings.screen_size[0]) <= settings.edge_snap_distance:
                                active_region.x = settings.screen_size[0] - active_region.w
                            if abs(active_region.y) <= settings.edge_snap_distance:
                                active_region.y = 0
                            if abs((active_region.y + active_region.h) - settings.screen_size[1]) <= settings.edge_snap_distance:
                                active_region.y = settings.screen_size[1] - active_region.h
                                
                                # Snap to other regions
                            for r in regions:
                                if r == active_region:
                                    continue
                                    
                                    # Snap X axis (left/right)
                                if abs((active_region.x + active_region.w) - r.x) <= settings.edge_snap_distance:
                                    active_region.x = r.x - active_region.w
                                if abs(active_region.x - (r.x + r.w)) <= settings.edge_snap_distance:
                                    active_region.x = r.x + r.w
                                    
                                    # Snap Y axis (top/bottom)
                                if abs((active_region.y + active_region.h) - r.y) <= settings.edge_snap_distance:
                                    active_region.y = r.y - active_region.h
                                if abs(active_region.y - (r.y + r.h)) <= settings.edge_snap_distance:
                                    active_region.y = r.y + r.h
                            

                    elif active_region.resizing:
                        # Get drag delta since last reset (not since drag start)
                        dx, dy = PyImGui.get_mouse_drag_delta(0, 0)
                        dx /= scale
                        dy /= scale

                        min_w = 64
                        min_h = 32

                        # Work on local vars first
                        x, y = active_region.x, active_region.y
                        w, h = active_region.w, active_region.h

                        match active_region.resize_direction:
                            case Region.ResizeDirection.TOP_LEFT:
                                # Move top-left corner
                                x += dx
                                y += dy
                                w -= dx
                                h -= dy

                            case Region.ResizeDirection.TOP_RIGHT:
                                # Move top edge, right stays fixed
                                y += dy
                                w += dx
                                h -= dy

                            case Region.ResizeDirection.BOTTOM_LEFT:
                                # Move left edge, bottom stays fixed
                                x += dx
                                w -= dx
                                h += dy

                            case Region.ResizeDirection.BOTTOM_RIGHT:
                                # Bottom-right only changes size
                                w += dx
                                h += dy

                        # Enforce min width/height and correct position if clamped
                        if w < min_w:
                            if active_region.resize_direction in [Region.ResizeDirection.TOP_LEFT, Region.ResizeDirection.BOTTOM_LEFT]:
                                x -= (min_w - w)
                            w = min_w

                        if h < min_h:
                            if active_region.resize_direction in [Region.ResizeDirection.TOP_LEFT, Region.ResizeDirection.TOP_RIGHT]:
                                y -= (min_h - h)
                            h = min_h

                        # Apply new values
                        active_region.x = int(x)
                        active_region.y = int(y)
                        active_region.w = int(w)
                        active_region.h = int(h)

                        # Reset delta so movement is relative frame-to-frame, not cumulative
                        PyImGui.reset_mouse_drag_delta(0)
                            
                        if settings.snap_to_edges:
                                # Snap to screen edges
                            if abs((active_region.x + active_region.w) - settings.screen_size[0]) <= settings.edge_snap_distance:
                                active_region.w = settings.screen_size[0] - active_region.x
                            if abs((active_region.y + active_region.h) - settings.screen_size[1]) <= settings.edge_snap_distance:
                                active_region.h = settings.screen_size[1] - active_region.y
                                
                                # Snap to other regions, if other region is touching, snap to same width/height           
                            for r in regions:
                                if r == active_region:
                                    continue
                                    
                                    # Snap width (right edge)
                                if abs((active_region.x + active_region.w) - r.x) <= settings.edge_snap_distance:
                                    if (active_region.y + active_region.h > r.y and active_region.y < r.y + r.h):
                                        active_region.w = r.x - active_region.x
                                    
                                    # Snap height (bottom edge)
                                if abs((active_region.y + active_region.h) - r.y) <= settings.edge_snap_distance:
                                    if (active_region.x + active_region.w > r.x and active_region.x < r.x + r.w):
                                        active_region.h = r.y - active_region.y
                                    
                                is_below_at_same_x = (active_region.x >= r.x and active_region.x <= r.x + r.w) or (active_region.x + active_region.w >= r.x and active_region.x + active_region.w <= r.x + r.w)
                                if is_below_at_same_x and abs((active_region.y) - (r.y + r.h)) <= settings.edge_snap_distance:
                                    if abs(active_region.h - r.h) <= settings.edge_snap_distance:
                                        active_region.h = r.h
                                        
                                    if abs(active_region.w - r.w) <= settings.edge_snap_distance:
                                        active_region.w = r.w
                                            
                            
                    PyImGui.reset_mouse_drag_delta(0)
                else:
                    for r in regions:
                        r.dragging = False
                        r.resizing = False

        ImGui.end_child()
            
        style.WindowPadding.pop_style_var()
            
        border = Color(168, 168, 168, 150)
        PyImGui.draw_list_add_rect_filled(drawing_area_screen_pos[0], drawing_area_screen_pos[1], drawing_area_screen_pos[0] + drawing_area_size[0], drawing_area_screen_pos[1] + drawing_area_size[1], border.color_int, 0, 0)
            
        border = Color(0, 0, 0, 150)
        border_thickness = 3
        PyImGui.draw_list_add_rect(drawing_area_screen_pos[0] - (border_thickness / 2), drawing_area_screen_pos[1] - (border_thickness / 2), drawing_area_screen_pos[0] + drawing_area_size[0] + (border_thickness / 2), drawing_area_screen_pos[1] + drawing_area_size[1] + (border_thickness / 2), border.color_int, 0, 0, border_thickness)
    

def on_enable():
    ConsoleLog(MODULE_NAME, "Module enabled.")
    
    player_name = GLOBAL_CACHE.Player.GetName()
    
    if player_name:
        title = f"{player_name} - Guild Wars"
        ConsoleLog(MODULE_NAME, "Set window title to: " + title)
        
        Console.set_window_title(title)
    else:
        ConsoleLog(MODULE_NAME, "Could not get player account name.", message_type=1)
        
    pass

def on_disable():
    ConsoleLog(MODULE_NAME, "Module disabled.")
    pass

def main():    
    global accounts, active_region
    
    if widget_handler is not None:
        widget_handler.set_widget_configuring(MODULE_NAME, True)
    
    if throttle_timer.IsExpired():
        throttle_timer.Reset()
        
        accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
        
    try:
        module_window.open = False
        if active_region and PyImGui.is_key_down(Key.Delete.value):
            regions.remove(active_region)
            active_region = None
            
        draw()
        
    except Exception as e:
        ConsoleLog(MODULE_NAME, f"Error in draw(): {e}", message_type=1)
    
    if not Routines.Checks.Map.MapValid():
        return                   

__all__ = ['main', 'configure']
