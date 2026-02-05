import os
import Py4GW
import PyImGui

from Py4GWCoreLib import ImGui
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.ImGui_src.IconsFontAwesome5 import IconsFontAwesome5
from Py4GWCoreLib.ImGui_src.Style import Style
from Py4GWCoreLib.IniManager import IniManager
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.enums_src.Multiboxing_enums import SharedCommandType
from Py4GWCoreLib.py4gwcorelib_src.Color import Color
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import Widget, WidgetHandler
from Sources.frenkeyLib.Py4GWLibrary.enum import SortMode, LayoutMode, ViewMode
from Sources.frenkeyLib.Py4GWLibrary.module_cards import draw_compact_widget_card, draw_compact_widget_card, draw_widget_card

class ModuleBrowser:
    CATEGORY_COLUMN_MAX_WIDTH = 150
    
    def __init__(self, ini_key: str, module_name: str, widget_manager : WidgetHandler):
        self.ini_key = ini_key
        self.module_name = module_name
        self.widget_manager = widget_manager
        self.widget_filter = ""
        
        self.view_mode = ViewMode.All
        self.layout_mode = LayoutMode.Minimalistic
        self.sort_mode = SortMode.ByName
        
        self.widgets : list[Widget] = list(self.widget_manager.widgets.values())
        self.filtered_widgets : list[Widget] = []
        self.favorites : list[Widget] = []
                
        self.category : str = ""
        # get unique categories sorted alphabetically
        self.categories : list[str] = sorted(set(widget.category for widget in self.widgets if widget.category))
        
        self.tag : str = ""
        self.tags : list[str] = sorted(set(tag for widget in self.widgets for tag in widget.tags if widget.tags))
        
        self.win_size = (800, 600)
        self.ui_active = False
        self.focus_search = False
        self.popup_opened = False
        
        self.context_menu_widget = None
        self.context_menu_id = ""
        
        self.set_layout_mode(self.layout_mode)
        self.filter_widgets("")
        
    def set_layout_mode(self, mode : LayoutMode):
        self.layout_mode = mode
        match mode:
            case LayoutMode.Library:
                self.win_size = (800, 600)
            case LayoutMode.Compact:
                self.win_size = (300, 80)
            case LayoutMode.Minimalistic:
                self.win_size = (200, 45)
        pass

    def set_search_focus(self):
        match self.layout_mode:
            case LayoutMode.Library:
                self.focus_search = True
                
            case LayoutMode.Compact | LayoutMode.Minimalistic:
                self.set_layout_mode(LayoutMode.Compact)
                self.focus_search = True

    def draw_window(self): 
        match self.layout_mode:
            case LayoutMode.Library:
                self.draw_libary()
            case LayoutMode.Compact:
                self.compact_view()  
            case LayoutMode.Minimalistic:
                self.minimalistic_view()

    def filter_widgets(self, filter_text: str):        
        self.filtered_widgets.clear()     
        prefiltered = self.widgets.copy()
        
        keywords = [kw.strip().lower() for kw in filter_text.lower().strip().split(";")]
        
        preset_words = [
            "enabled", "active", "on",
            "disabled", "inactive", "off",
            "favorites", "favs", "fav",
            "system", "sys"]
        
        enabled_check = False
        disabled_check = False
        favorites_check = False
        system_check = False
        
        for kw in list(keywords):            
            enabled_check = enabled_check or kw == "enabled" or kw == "active" or kw == "on"
            disabled_check = disabled_check or kw == "disabled" or kw == "inactive" or kw == "off"
            favorites_check = favorites_check or kw == "favorites" or kw == "favs" or kw == "fav"
            system_check = system_check or kw == "system" or kw == "sys"
            
            prefiltered = [w for w in prefiltered if 
                            (not enabled_check or w.enabled) and
                            (not disabled_check or not w.enabled) and
                            (not favorites_check or w in self.favorites) and
                            (not system_check or w.category == "System")]
            
            if kw in preset_words:
                keywords.remove(kw)
            
        
        match self.layout_mode:
            case LayoutMode.Library:
                match self.view_mode:
                    case ViewMode.Favorites:
                        prefiltered = [w for w in prefiltered if w in self.favorites]
                        
                    case ViewMode.Actives:
                        prefiltered = [w for w in self.widgets if w.enabled]
                        
                    case ViewMode.Inactives:
                        prefiltered = [w for w in self.widgets if not w.enabled]
                
                self.filtered_widgets = [w for w in prefiltered if 
                                        (w.category == self.category or not self.category) and 
                                        (self.tag in w.tags or not self.tag) and 
                                        all(kw in w.plain_name.lower() or kw in w.folder.lower() for kw in keywords if keywords and kw)]
                
                match self.sort_mode:
                    case SortMode.ByName:
                        self.filtered_widgets.sort(key=lambda w: w.name.lower())
                    case SortMode.ByCategory:
                        self.filtered_widgets.sort(key=lambda w: (w.category.lower() if w.category else "", w.name.lower()))
                    case SortMode.ByStatus:
                        self.filtered_widgets.sort(key=lambda w: (not w.enabled, w.name.lower()))
            case LayoutMode.Compact:
                # check if all keywords are in name or folder
                self.filtered_widgets = [w for w in prefiltered if all(kw in w.plain_name.lower() or kw in w.folder.lower() for kw in keywords if keywords and kw)]

    def draw_toggle_view_mode_button(self):
        match self.layout_mode:
            case LayoutMode.Library:
                if ImGui.icon_button(IconsFontAwesome5.ICON_BARS, 28, 24):
                    self.set_layout_mode(LayoutMode.Compact)
                    
                ImGui.show_tooltip("Switch to Compact View")
                    
            case LayoutMode.Compact:
                if ImGui.icon_button(IconsFontAwesome5.ICON_TH_LIST, 28, 24):
                    self.set_layout_mode(LayoutMode.Library)
                    
                ImGui.show_tooltip("Switch to Library View")
    
    def draw_global_toggles(self, button_width : float, spacing : float):       
        if ImGui.icon_button(IconsFontAwesome5.ICON_RETWEET + "##Reload Widgets", button_width):
            Py4GW.Console.Log("Widget Manager", "Reloading Widgets...", Py4GW.Console.MessageType.Info)
            self.widget_initialized = False
            self.discovered = False
            self.widget_manager.discover()
            self.widget_initialized = True    
                
        ImGui.show_tooltip("Reload all widgets")
        PyImGui.same_line(0, spacing)
        
        e_all = bool(IniManager().get(key=self.ini_key, var_name="enable_all", default=True, section="Configuration"))
        new_enable_all = ImGui.toggle_icon_button(
            (IconsFontAwesome5.ICON_TOGGLE_ON if e_all else IconsFontAwesome5.ICON_TOGGLE_OFF) + "##widget_disable",
            e_all,
            button_width
        )

        if new_enable_all != e_all:
            IniManager().set(key= self.ini_key, var_name="enable_all", value=new_enable_all, section="Configuration")
            IniManager().save_vars(self.ini_key)

        self.enable_all = new_enable_all


        ImGui.show_tooltip(f"{("Run" if not self.enable_all else "Pause")} all widgets")
        
        PyImGui.same_line(0, spacing)
        show_widget_ui = ImGui.toggle_icon_button((IconsFontAwesome5.ICON_EYE if self.widget_manager.show_widget_ui else IconsFontAwesome5.ICON_EYE_SLASH) + "##Show Widget UIs", self.widget_manager.show_widget_ui, button_width)
        if show_widget_ui != self.widget_manager.show_widget_ui:
            self.widget_manager.set_widget_ui_visibility(show_widget_ui)
        ImGui.show_tooltip(f"{("Show" if not self.widget_manager.show_widget_ui else "Hide")} all widget UIs")
        
        PyImGui.same_line(0, spacing)
        pause_non_env = ImGui.toggle_icon_button((IconsFontAwesome5.ICON_PAUSE if self.widget_manager.pause_optional_widgets else IconsFontAwesome5.ICON_PLAY) + "##Pause Non-Env Widgets", not self.widget_manager.pause_optional_widgets, button_width)
        if pause_non_env != (not self.widget_manager.pause_optional_widgets):
            if not self.widget_manager.pause_optional_widgets:
                self.widget_manager.pause_widgets()
            else:
                self.widget_manager.resume_widgets()
                
            own_email = Player.GetAccountEmail()
            for acc in GLOBAL_CACHE.ShMem.GetAllAccountData():
                if acc.AccountEmail == own_email:
                    continue
                
                GLOBAL_CACHE.ShMem.SendMessage(own_email, acc.AccountEmail, SharedCommandType.PauseWidgets if self.widget_manager.pause_optional_widgets else SharedCommandType.ResumeWidgets)
            
        ImGui.show_tooltip(f"{("Pause" if not self.widget_manager.pause_optional_widgets else "Resume")} all optional widgets")
    
    def get_button_width(self, width, num_buttons, spacing) -> float:        
        button_width = (width - spacing * (num_buttons - 1)) / num_buttons
        return button_width
    
    def minimalistic_view(self):
        PyImGui.set_next_window_size(self.win_size, PyImGui.ImGuiCond.Always)
        
        if self.focus_search:
            PyImGui.set_next_window_focus()
            
        if ImGui.Begin(ini_key=self.ini_key, name=self.module_name, flags=PyImGui.WindowFlags(PyImGui.WindowFlags.NoResize|PyImGui.WindowFlags.NoTitleBar)):   
            win_size = PyImGui.get_window_size()
            self.win_size = (win_size[0], win_size[1])
            style = ImGui.get_style()
            
            spacing = 5
            width = win_size[0] - style.WindowPadding.value1 * 2
            button_width = self.get_button_width(width, 5, spacing)            
            if ImGui.button(IconsFontAwesome5.ICON_SEARCH + "##FocusSearch", button_width):
                self.set_layout_mode(LayoutMode.Compact)
            
            PyImGui.same_line(0, spacing)            
            self.draw_global_toggles(button_width, spacing)
                            
        ImGui.End(self.ini_key)
            
    def draw_presets_button(self) -> bool:
        if ImGui.icon_button(IconsFontAwesome5.ICON_FILTER, 28, 24):
            if not self.popup_opened:
                PyImGui.open_popup("PreSets##WidgetBrowser")
                self.popup_opened = True
                Py4GW.Console.Log("Widget Browser", "Opening presets popup", Py4GW.Console.MessageType.Info)
            
        self.popup_opened = PyImGui.begin_popup("PreSets##WidgetBrowser")
        if self.popup_opened:
            if ImGui.menu_item("Show Enabled"):
                self.widget_filter = "enabled; "
                self.focus_search = True
                self.filter_widgets(self.widget_filter)
            
            if ImGui.menu_item("Show Favorites"):
                self.widget_filter = "favorites; "
                self.focus_search = True
                self.filter_widgets(self.widget_filter)
                
            if ImGui.menu_item("Show System"):
                self.widget_filter = "system; "  
                self.focus_search = True
                self.filter_widgets(self.widget_filter)
            
            PyImGui.end_popup()   
                    
        return self.popup_opened
            
    def compact_view(self):
        PyImGui.set_next_window_size(self.win_size, PyImGui.ImGuiCond.Always)
        
        if self.focus_search:
            PyImGui.set_next_window_focus()
            
        if ImGui.Begin(ini_key=self.ini_key, name=self.module_name, flags=PyImGui.WindowFlags.NoResize | PyImGui.WindowFlags.NoTitleBar):   
            window_hovered = PyImGui.is_window_hovered() or PyImGui.is_window_focused()
            win_size = PyImGui.get_window_size()
            self.win_size = (win_size[0], win_size[1])
            style = ImGui.get_style()
            width = win_size[0] - style.WindowPadding.value1 * 2
            
            spacing = 5
            button_width = self.get_button_width(width, 4, spacing)     
            self.draw_global_toggles(button_width, spacing)
            ImGui.separator()
            self.draw_toggle_view_mode_button()   
            PyImGui.same_line(0, spacing)      
            
            search_width = PyImGui.get_content_region_avail()[0] - 30
            PyImGui.push_item_width(search_width)
            changed, self.widget_filter = ImGui.search_field("##WidgetFilter", self.widget_filter)
            if changed:
                self.filter_widgets(self.widget_filter)
            PyImGui.pop_item_width()
            search_active = PyImGui.is_item_active()
            
            if self.focus_search:
                PyImGui.set_keyboard_focus_here(-1)
                self.focus_search = False
            
            PyImGui.same_line(0, spacing)
            
            presets_opened = self.draw_presets_button()      
            window_hovered = PyImGui.is_window_hovered() or PyImGui.is_window_focused() or PyImGui.is_item_hovered() or window_hovered 
            
            
            if not self.draw_suggestions(win_size, style, search_active, window_hovered, presets_opened) and not search_active and not window_hovered and not presets_opened:
                Py4GW.Console.Log("Widget Browser", "Clearing search filter", Py4GW.Console.MessageType.Info)
                Py4GW.Console.Log("Widget Browser", f"presets_opened {presets_opened}", Py4GW.Console.MessageType.Info)
                self.widget_filter = ""
                self.filtered_widgets.clear()
                self.set_layout_mode(LayoutMode.Minimalistic)
                
                            
        ImGui.End(self.ini_key)

    def draw_suggestions(self, win_size, style : Style, search_active, window_hovered, presets_opened) -> bool:
        open = False
        
        if self.filtered_widgets and self.widget_filter:
            win_pos = PyImGui.get_window_pos()
                
            PyImGui.set_next_window_pos(
                    (win_pos[0], win_pos[1] + win_size[1] - style.WindowBorderSize.value1),
                    PyImGui.ImGuiCond.Always
                )

            height = min(200, len(self.filtered_widgets) * 30 + (style.ItemSpacing.value2 or 0) + (style.WindowPadding.value2 or 0) * 2)
            PyImGui.set_next_window_size((win_size[0], height),
                    PyImGui.ImGuiCond.Always
                )
                
            suggestion_hovered = False
            if PyImGui.begin(
                    "##WidgetsList",
                    False,
                    PyImGui.WindowFlags(PyImGui.WindowFlags.NoTitleBar
                    | PyImGui.WindowFlags.NoMove
                    | PyImGui.WindowFlags.NoResize
                    | PyImGui.WindowFlags.NoSavedSettings
                    | PyImGui.WindowFlags.NoFocusOnAppearing
                )):
                suggestion_hovered = PyImGui.is_window_hovered()
                card_width = PyImGui.get_content_region_avail()[0]
                open = True
                    
                for widget in self.filtered_widgets:
                    suggestion_hovered = draw_compact_widget_card(widget, card_width) or suggestion_hovered
                    if PyImGui.is_item_clicked(0):
                        self.filter_widgets(self.widget_filter)
                        self.focus_search = True
                        
                        # ---- RIGHT CLICK DETECTION ----
                    if PyImGui.is_item_hovered() and PyImGui.is_mouse_clicked(1):
                        self.context_menu_id = f"WidgetContext##{widget.folder_script_name}"
                        self.context_menu_widget = widget
                        PyImGui.open_popup(self.context_menu_id)
                        
                if self.context_menu_id and self.context_menu_widget:
                    self.card_context_menu(self.context_menu_id, self.context_menu_widget)
                            
                if suggestion_hovered and not self.context_menu_id and not search_active and not self.focus_search and not presets_opened:
                    Py4GW.Console.Log("Widget Browser", "set_window_focus to ##WidgetsList", Py4GW.Console.MessageType.Info)
                    PyImGui.set_window_focus("##WidgetsList")
                    
            if (
                    not PyImGui.is_window_focused()
                    and not search_active
                    and not window_hovered
                    and not suggestion_hovered
                    and not self.context_menu_id
                    and not PyImGui.is_any_item_active()
                ):
                open = False
                    
            ImGui.end()
            
        return open
    
    def card_context_menu(self, popup_id: str, widget : Widget):
        
        if PyImGui.begin_popup(popup_id):
            if PyImGui.menu_item("Add to Favorites" if widget not in self.favorites else "Remove from Favorites"):
                if widget not in self.favorites:
                    self.favorites.append(widget)
                else:
                    self.favorites.remove(widget)
                
            PyImGui.separator()
            
            if PyImGui.menu_item("Enable" if not widget.enabled else "Disable"):
                if not widget.enabled:
                    widget.enable()
                else:
                    widget.disable()
                    
            PyImGui.separator()

            if widget.has_configure_property:
                if PyImGui.menu_item("Configure"):
                    widget.set_configuring(True)

                PyImGui.separator()

            if PyImGui.menu_item("Open Widget Folder"):
                os.startfile(os.path.join(Py4GW.Console.get_projects_path(), "Widgets", widget.folder))

            if PyImGui.menu_item("Open Widget File"):
                os.startfile(os.path.join(Py4GW.Console.get_projects_path(), "Widgets", widget.folder_script_name))

            PyImGui.end_popup()
        else:
            self.context_menu_id = ""
            self.context_menu_widget = None
    
    def draw_sorting_button(self):
        if ImGui.icon_button(IconsFontAwesome5.ICON_SORT_AMOUNT_DOWN, 28, 24):
            PyImGui.open_popup("SortingPopup##WidgetBrowser")
    
        if PyImGui.begin_popup("SortingPopup##WidgetBrowser"):
            sort_mode = ImGui.radio_button("Sort by Name", self.sort_mode, SortMode.ByName)
            if self.sort_mode != sort_mode:
                self.sort_mode = SortMode.ByName
                self.filtered_widgets.sort(key=lambda w: w.name.lower())
                
            sort_mode = ImGui.radio_button("Sort by Category", self.sort_mode, SortMode.ByCategory)
            if self.sort_mode != sort_mode:
                self.sort_mode = SortMode.ByCategory
                self.filtered_widgets.sort(key=lambda w: (w.category.lower() if w.category else "", w.name.lower()))
                
            sort_mode = ImGui.radio_button("Sort by Status", self.sort_mode, SortMode.ByStatus)
            if self.sort_mode != sort_mode:
                self.sort_mode = SortMode.ByStatus
                self.filtered_widgets.sort(key=lambda w: (not w.enabled, w.name.lower()))
                
            PyImGui.end_popup()    
    
    def draw_libary(self):
        PyImGui.set_next_window_size(self.win_size, PyImGui.ImGuiCond.Always)
        if ImGui.Begin(ini_key=self.ini_key, name=self.module_name, flags=PyImGui.WindowFlags.NoFlag):    
            io = PyImGui.get_io()
            win_size = PyImGui.get_window_size()
            self.win_size = (win_size[0], win_size[1])
                   
            style = ImGui.get_style()
            
            self.draw_toggle_view_mode_button()   
            PyImGui.same_line(0, 5)    
            search_width = PyImGui.get_content_region_avail()[0] - 32
            PyImGui.push_item_width(search_width)
            changed, self.widget_filter = ImGui.search_field("##WidgetFilter", self.widget_filter)
            if self.focus_search:
                PyImGui.set_keyboard_focus_here(-1)
                self.focus_search = False
            PyImGui.pop_item_width()
            if changed:
                self.filter_widgets(self.widget_filter)
            
            PyImGui.same_line(0, 5)
            self.draw_sorting_button()    
            
            ImGui.separator()
            
            if ImGui.begin_table("navigation_view", 2, PyImGui.TableFlags.SizingStretchProp | PyImGui.TableFlags.BordersInnerV):
                max_width = PyImGui.get_content_region_avail()[0]
                                
                PyImGui.table_setup_column("##categories", PyImGui.TableColumnFlags.WidthFixed, min(self.CATEGORY_COLUMN_MAX_WIDTH, max_width * 0.5))
                PyImGui.table_setup_column("##widgets", PyImGui.TableColumnFlags.WidthStretch)
                PyImGui.table_next_row()
                
                PyImGui.table_set_column_index(0)
                if ImGui.begin_child("##category_list", (0, 0)):      
                    if ImGui.selectable("All", self.view_mode is ViewMode.All):
                        self.view_mode = ViewMode.All if not self.view_mode is ViewMode.All else ViewMode.All
                        self.filter_widgets(self.widget_filter)            
                        
                    if ImGui.selectable("Favorites", self.view_mode is ViewMode.Favorites):
                        self.view_mode = ViewMode.Favorites if not self.view_mode is ViewMode.Favorites else ViewMode.All
                        self.filter_widgets(self.widget_filter)
                        
                    if ImGui.selectable("Active", self.view_mode is ViewMode.Actives):
                        self.view_mode = ViewMode.Actives if not self.view_mode is ViewMode.Actives else ViewMode.All
                        self.filter_widgets(self.widget_filter)
                        
                    if ImGui.selectable("Inactive", self.view_mode is ViewMode.Inactives):
                        self.view_mode = ViewMode.Inactives if not self.view_mode is ViewMode.Inactives else ViewMode.All
                        self.filter_widgets(self.widget_filter)
                        
                    ImGui.separator()
                    
                    for category in self.categories:
                        if ImGui.selectable(category, category == self.category):                            
                            self.category = category if category != self.category else ""     
                              
                            if not io.key_ctrl:
                                self.tag = ""
                                                     
                            self.filter_widgets(self.widget_filter)
                    
                    ImGui.separator()
                    style.ScrollbarSize.push_style_var(5)
                    if ImGui.begin_child("##tags", (0, 0)):  
                        for tag in self.tags:
                            if ImGui.selectable(f"{tag}", tag == self.tag):
                                self.tag = tag if tag != self.tag else ""  
                                if not io.key_ctrl:
                                    self.category = ""
                                self.filter_widgets(self.widget_filter)
                                
                    PyImGui.end_child()
                    style.ScrollbarSize.pop_style_var()
                ImGui.end_child()
                
                PyImGui.table_set_column_index(1)
                
                if ImGui.begin_child("##widgets", (0, 0)):  
                    style.DisabledAlpha.push_style_var(0.4)
                    
                    min_card_width = 250
                    available_width = PyImGui.get_content_region_avail()[0] - (style.ScrollbarSize.value1 if PyImGui.get_scroll_y() == 0 else 0)
                    num_columns = max(1, int(available_width // min_card_width))
                    card_width = 0
                    PyImGui.columns(num_columns, "widget_cards", False)
                            
                    for widget in (self.filtered_widgets):
                        card_width = PyImGui.get_content_region_avail()[0]
                        draw_widget_card(widget, card_width, widget in self.favorites)
                        if PyImGui.is_item_clicked(0):
                            self.filter_widgets(self.widget_filter)
                                                                        
                        popup_id = f"WidgetContext##{widget.folder_script_name}"
                        # ---- RIGHT CLICK DETECTION ----
                        if PyImGui.is_item_hovered() and PyImGui.is_mouse_clicked(1):
                            PyImGui.open_popup(popup_id)

                        # ---- CONTEXT MENU ----
                        self.card_context_menu(popup_id, widget)
                        
                        PyImGui.next_column()
                                            
                        
                    style.DisabledAlpha.pop_style_var()
                    PyImGui.end_columns()
                    
                ImGui.end_child()
                ImGui.end_table()
                
        ImGui.End(self.ini_key)