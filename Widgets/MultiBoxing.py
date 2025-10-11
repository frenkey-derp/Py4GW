
import ctypes
import os
from typing import Optional

from Py4GW import Console
import PyImGui

from Py4GWCoreLib import ImGui, Player, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, ThrottledTimer
from Py4GWCoreLib.py4gwcorelib_src.Color import Color
from Py4GW_widget_manager import WidgetHandler

MODULE_NAME = "MultiBoxing"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

module_window = ImGui.WindowModule(MODULE_NAME, MODULE_NAME, (300, 600))
configure_window = ImGui.WindowModule(MODULE_NAME, MODULE_NAME + " Configure", (1200, 800), can_close=True)
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
    pass

    def get_screen_size(self) -> tuple[int, int]:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        return screen_width, screen_height

settings = Settings()

class Region:
    def __init__(self, x: int = 0, y: int = 0, w: int = 300, h: int = 200, name: str = "Region", account: str = "", color: Optional[Color] = None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.color = color if color else Color.random()
        
        self.selected = False
        self.dragging = False
        self.resizing = False
        self.resize_grab_size = 12
        
        self.name : str = name
        self.account : str = account

    def rect(self, scale: float = 1.0) -> tuple[float, float, float, float]:
        return (self.x * scale, self.y * scale, (self.x + self.w) * scale, (self.y + self.h) * scale)

    def contains(self, mx, my, scale: float = 1.0):
        x1, y1, x2, y2 = self.rect(scale)
        return x1 <= mx <= x2 and y1 <= my <= y2

    def on_resize_zone(self, mx, my, scale: float = 1.0):
        # bottom-right corner for resize
        x1, y1, x2, y2 = self.rect(scale)
        
        return (x2 - self.resize_grab_size <= mx <= x2 and
                y2 - self.resize_grab_size <= my <= y2)

    def draw(self, origin_x: float, origin_y: float, scale: float = 1.0):
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
        
        # Resize handle
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
        base_text_size = PyImGui.calc_text_size(self.name)
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
        text_display = f"{self.name if not self.account else self.account}"
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

def draw_configure_window():
    global regions, active_region, screen_size_changed
    
    configure_window.open = module_info["configuring"] if module_info else False
    
    if configure_window.begin(None):  
        configure_window.window_flags = PyImGui.WindowFlags.NoFlag
        
        style = ImGui.get_style()
        win_size = PyImGui.get_window_size()

        # Adjust for window padding
        win_size = (
            win_size[0] - (style.WindowPadding.get_current().value1 * 2),
            win_size[1] - ((style.WindowPadding.get_current().value2 or 0) * 2)
        )

        ratio = settings.screen_size[0] / settings.screen_size[1]

        # Header control layout
        header_control_size = (300, 125)
        header_control_pos = ((win_size[0] - header_control_size[0]) / 2, 30)
        header_bottom = header_control_pos[1] + header_control_size[1]

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
            style.Border.push_color((255,0,0,255))
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
                            if hovered.on_resize_zone(mx - origin_x, my - origin_y, scale):
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
                            active_region.w = int(max(64, active_region.w + (dx * (1/scale))))
                            active_region.h = int(max(32, active_region.h + (dy * (1/scale))))
                            
                            
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
            
            style.Border.pop_color()
            style.WindowPadding.pop_style_var()
            
            border = Color(168, 168, 168, 150)
            PyImGui.draw_list_add_rect_filled(drawing_area_screen_pos[0], drawing_area_screen_pos[1], drawing_area_screen_pos[0] + drawing_area_size[0], drawing_area_screen_pos[1] + drawing_area_size[1], border.color_int, 0, 0)
            
            border = Color(0, 0, 0, 150)
            border_thickness = 3
            PyImGui.draw_list_add_rect(drawing_area_screen_pos[0] - (border_thickness / 2), drawing_area_screen_pos[1] - (border_thickness / 2), drawing_area_screen_pos[0] + drawing_area_size[0] + (border_thickness / 2), drawing_area_screen_pos[1] + drawing_area_size[1] + (border_thickness / 2), border.color_int, 0, 0, border_thickness)
                
        
        PyImGui.set_cursor_pos(header_control_pos[0], header_control_pos[1])
        
        ## Draw the header last to be on top of everything else    
        style.ChildBg.push_color(style.WindowBg.opacify(0.8).to_tuple())
        if ImGui.begin_child("header_controls", header_control_size, border=True, flags=PyImGui.WindowFlags.NoScrollbar):
            ImGui.push_font("Regular", 20)
            center_aligned_text("Layout", header_control_size[0])
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
                swidth = PyImGui.input_int("##width", settings.screen_size[0], 800, 10, PyImGui.InputTextFlags.AutoSelectAll)
                if swidth != settings.screen_size[0]:
                    settings.screen_size = (max(800, swidth), settings.screen_size[1])
                    screen_size_changed = True
                    
                input_active = PyImGui.is_item_active()
                    
                PyImGui.pop_item_width()
                    
                PyImGui.table_next_column()
                ImGui.text("x")
                PyImGui.table_next_column()
                
                PyImGui.push_item_width(PyImGui.get_content_region_avail()[0] - 15)
                sheight = PyImGui.input_int("##height", settings.screen_size[1], 600, 10, PyImGui.InputTextFlags.AutoSelectAll)
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
                
            PyImGui.set_cursor_pos(10, header_control_size[1] - 30)
            if ImGui.button("Add Region", PyImGui.get_content_region_avail()[0], 20):
                new_region = Region(0, 0, 1920, 1080, name = f"Region {len(regions) + 1}")
                #center the new region
                new_region.x = (settings.screen_size[0] - new_region.w) // 2
                new_region.y = (settings.screen_size[1] - new_region.h) // 2
                
                regions.append(new_region)
            pass
        style.ChildBg.pop_color()
        
        ImGui.end_child()
        
    if not configure_window.open:
        widget_handler.set_widget_configuring(MODULE_NAME, False)
        
    configure_window.end()
    

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
    global accounts
    
    if widget_handler is not None:
        widget_handler.set_widget_configuring(MODULE_NAME, True)
    
    if throttle_timer.IsExpired():
        throttle_timer.Reset()
        
        accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
        
    try:
        module_window.open = False
        draw()
        
    except Exception as e:
        ConsoleLog(MODULE_NAME, f"Error in draw(): {e}", message_type=1)
    
    if not Routines.Checks.Map.MapValid():
        return                   

__all__ = ['main', 'configure']
