import os

import Py4GW
import PyImGui

from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.ImGui_src.types import Alignment
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig 
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import *
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.SalvageConfig import SalvageConfig 
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig
from Sources.frenkeyLib.ItemManager.config import Config


class ConfigInfo:
    def __init__(self, config: RuleConfig, name: str, description: str, folder_path: str):
        self.config = config
        self.name = name
        self.description = description
        self.folder_path = folder_path
    
    def save(self):
        self.config.Save(os.path.join(self.folder_path, f"{self.config.__class__.__name__.lower()}.json"))
        Py4GW.Console.Log("Item Manager", f"Saved config for {self.name} to {self.folder_path} with {len(self.config)} rules.", Py4GW.Console.MessageType.Info)
    
    def load(self):
        self.config.Load(os.path.join(self.folder_path, f"{self.config.__class__.__name__.lower()}.json"))
        Py4GW.Console.Log("Item Manager", f"Loaded config for {self.name} from {self.folder_path} with {len(self.config)} rules.", Py4GW.Console.MessageType.Info)

class UI:
    GRAY_COLOR = (0.35, 0.35, 0.35, 1.0)
    ITEM_TYPE_TEXTURES = {
        
    }
    
    def __init__(self, module_config: Config):
        self.module_config = module_config        
        self.floating_button = ImGui.FloatingIcon(
                icon_path=self.module_config.icon_path,
                window_id="##item_manager_floating_button",
                window_name="Item Manager##FloatingButton",
                tooltip_visible="Hide Item Manager",
                tooltip_hidden="Show Item Manager",
                toggle_ini_key=self.module_config.floating_ini_key,
                toggle_var_name="show_main_window",
                toggle_default=True,
                draw_callback=self.draw_main_window,
            )
        
        folder_path = os.path.join(Py4GW.Console.get_projects_path(), "Settings", "Global", "Item & Inventory", "Configs")
        
        self.configs : list[ConfigInfo] = [
            ConfigInfo(LootConfig(), "Looting", "Configure which items to pick up and which to ignore", folder_path),
            ConfigInfo(SalvageConfig(), "Salvaging", "Configure which items to salvage", folder_path),
        ]
        
        for config_info in self.configs:
            config_info.load()
        
        self.config = self.configs[0]
        self.rule = self.config.config[0] if len(self.config.config) > 0 else None
        
        self.context_menu_id : str | None = None
        self.context_menu_rule : Rule | None = None
        self.context_menu_config : ConfigInfo | None = None

    def draw_main_window(self) -> None:
        expanded, open_ = ImGui.BeginWithClose(
            ini_key=self.module_config.main_ini_key,
            name="Item Manager",
            p_open=self.floating_button.visible,
            flags=PyImGui.WindowFlags.NoCollapse,
        )
        self.floating_button.sync_begin_with_close(open_)

        if expanded:
            self.draw_explorer()

        ImGui.End(self.module_config.main_ini_key)
        
    def draw(self):
        self.floating_button.draw(self.module_config.floating_ini_key)
        
    def draw_explorer(self):
        style = ImGui.get_style()
        # style.TableBorderLight.push_color_direct((255,255,255,255))
        # style.TableBorderStrong.push_color_direct((255,255,255,255))
        style.CellPadding.push_style_var_direct(10, 10)
        if ImGui.begin_table("##item_manager_explorer", 2, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable):
            PyImGui.table_setup_column("Navigation", PyImGui.TableColumnFlags.WidthFixed, 200)
            PyImGui.table_setup_column("Content", PyImGui.TableColumnFlags.WidthStretch)
            
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            
            if ImGui.begin_child("##navigation", (0, 0), border=False):
                for _, config in enumerate(self.configs):
                    if ImGui.begin_selectable(f"##{config.name}", selected=self.config == config, size=(0, 35), border=True):
                        ImGui.text(config.name)
                        x, y = PyImGui.get_cursor_pos()
                        PyImGui.set_cursor_pos(x, y - 5)
                        ImGui.text_colored(config.config.__class__.__name__, UI.GRAY_COLOR, font_size=12)
                        
                    if ImGui.end_selectable():
                        self.config = config
                        self.rule = config.config[0]
                    
                    ImGui.show_tooltip(config.description)
                        
            ImGui.end_child()
            
            PyImGui.table_next_column()
            
            if ImGui.begin_child("##content", (0, 0), border=False):
                if self.config:                   
                    if ImGui.begin_table("##config_header", 3, PyImGui.TableFlags.NoBordersInBody, height=20):
                        PyImGui.table_setup_column("Title", PyImGui.TableColumnFlags.WidthStretch)
                        PyImGui.table_setup_column("Export", PyImGui.TableColumnFlags.WidthFixed, 100)
                        PyImGui.table_setup_column("Import", PyImGui.TableColumnFlags.WidthFixed, 100)
                        
                        PyImGui.table_next_row()
                        PyImGui.table_next_column()
                        
                        ImGui.text(f"{self.config.name} Rules", font_size=18)
                        PyImGui.table_next_column()
                        
                        if ImGui.button("Export##export_config", -1):
                            self.config.save()
                            
                        PyImGui.table_next_column()
                        if ImGui.button("Import##import_config", -1):
                            ImGui.show_tooltip(f"Import {self.config.name} config from {self.config.folder_path}")
                        ImGui.end_table()
                    
                    self.draw_config(self.config)
                    
            ImGui.end_child()
        
            ImGui.end_table()
            
        style.CellPadding.pop_style_var_direct()
        # style.TableBorderLight.pop_color_direct()
        # style.TableBorderStrong.pop_color_direct()
        
    
    def draw_context_menu(self, popup_id: str, config_info: ConfigInfo, rule: Rule) -> bool:
        if PyImGui.begin_popup(popup_id):
            ImGui.text(rule.name or popup_id)
            ImGui.separator()
            
            if ImGui.menu_item("Delete Rule"):
                config_info.config.remove(rule)
                config_info.save()
                self.rule = None
            
            ImGui.end_popup()
            return True
        
        return False
            
    def draw_config(self, config_info: ConfigInfo):
        style = ImGui.get_style()
        
        if ImGui.begin_table("##config_table", 2, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable):
            PyImGui.table_setup_column("Navigation", PyImGui.TableColumnFlags.WidthFixed, 200)
            PyImGui.table_setup_column("Content", PyImGui.TableColumnFlags.WidthStretch)
            
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            
            PyImGui.set_next_item_width(-1)
            if ImGui.begin_combo("##add_rule", "Add Rule", PyImGui.ImGuiComboFlags.NoFlag):
                for rule_type in Rule.__subclasses__():
                    if ImGui.selectable(rule_type.__name__, False):
                        new_rule = rule_type()
                        config_info.config.append(new_rule)
                        config_info.save()
                        self.rule = new_rule
                ImGui.end_combo()
            
            ImGui.separator()
            PyImGui.spacing()
            
            if ImGui.begin_child("##rules", (0, 0), border=False):
                width = PyImGui.get_content_region_avail()[0]
                
                for i, rule in enumerate(config_info.config):                    
                    if ImGui.begin_selectable(f"##rule_{i}", selected=self.rule == rule, size=(0, 35)):
                        ImGui.text(rule.name or f"{rule.__class__.__name__} #{i}")
                        x, y = PyImGui.get_cursor_pos()
                        PyImGui.set_cursor_pos(x, y - 5)
                        ImGui.text_colored(rule.__class__.__name__, UI.GRAY_COLOR, font_size=12)
                    
                    if ImGui.end_selectable():
                        self.rule = rule
                        
                    if PyImGui.is_item_hovered() and PyImGui.is_mouse_clicked(1):
                        self.context_menu_id = f"{rule.__class__.__name__} #{i}"
                        self.context_menu_rule = rule
                        self.context_menu_config = config_info                        
                        PyImGui.open_popup(self.context_menu_id)
                                                                        
                    ImGui.show_tooltip(rule.__class__.__name__)       
                    
            if self.context_menu_id and self.context_menu_rule and self.context_menu_config:
                if not self.draw_context_menu(self.context_menu_id, self.context_menu_config, self.context_menu_rule):
                    self.context_menu_id = None
                    self.context_menu_rule = None
                    self.context_menu_config = None
                
            ImGui.end_child()
            
            PyImGui.table_next_column()
            
            if ImGui.begin_child("##rule content", (0, 0), border=False):
                if self.rule:
                    self.draw_rule(self.rule)
                    pass
                    
            ImGui.end_child()
        
            ImGui.end_table()
        
    def draw_rule(self, rule: Rule):
        ImGui.text_aligned("Name", alignment=Alignment.MidLeft, height=25)
        PyImGui.same_line(0, 5)
        PyImGui.set_next_item_width(-1)
        name = ImGui.input_text("##rule_name", rule.name or "")
        
        if name != rule.name:
            rule.name = name
            self.config.save()
            
        ImGui.separator()
        PyImGui.spacing()
        
        match rule:
            case ModelIdsRule():
                ImGui.text_wrapped("This rule matches items based on their model IDs. You can specify one or more model IDs to match against the item.")
                
            case ItemTypesRule():
                ImGui.text_wrapped("This rule matches items based on their item types. You can specify one or more item types to match against the item.")
                
                if ImGui.begin_child("##item_types", (0, 0), border=False):
                    for item_type in ItemType:
                        is_selected = item_type in rule.item_types
                        selected = ImGui.checkbox(f"{item_type.name}", is_selected)
                        
                        if selected != is_selected:
                            if item_type in rule.item_types:
                                rule.item_types.remove(item_type)
                            else:
                                rule.item_types.append(item_type)
                            self.config.save()
                ImGui.end_child()
                
            case RaritiesRule():
                ImGui.text_wrapped("This rule matches items based on their rarity. You can specify one or more rarities to match against the item.")
                
                if ImGui.begin_child("##rarities", (0, 0), border=False):
                    for rarity in Rarity:
                        is_selected = rarity in rule.rarities
                        selected = ImGui.checkbox(f"{rarity.name}", is_selected)
                        
                        if selected != is_selected:
                            if rarity in rule.rarities:
                                rule.rarities.remove(rarity)
                            else:
                                rule.rarities.append(rarity)
                            self.config.save()
                ImGui.end_child()
            
            case RaritiesAndItemTypesRule():
                ImGui.text_wrapped("This rule matches items based on a combination of rarity and item type. You can specify pairs of rarities and item types to match against the item.")
            
                PyImGui.columns(2, "content_split", False)
                                                    
                if ImGui.begin_child("##rarities", (0, 0), border=False):
                    for rarity in Rarity:
                        is_selected = rarity in rule.rarities
                        selected = ImGui.checkbox(f"{rarity.name}", is_selected)
                        
                        if selected != is_selected:
                            if rarity in rule.rarities:
                                rule.rarities.remove(rarity)
                            else:
                                rule.rarities.append(rarity)
                            self.config.save()
                ImGui.end_child()
                
                PyImGui.next_column()
            
                if ImGui.begin_child("##item_types", (0, 0), border=False):
                    for item_type in ItemType:
                        is_selected = item_type in rule.item_types
                        selected = ImGui.checkbox(f"{item_type.name}", is_selected)
                        
                        if selected != is_selected:
                            if item_type in rule.item_types:
                                rule.item_types.remove(item_type)
                            else:
                                rule.item_types.append(item_type)
                            self.config.save()
                ImGui.end_child()
                
                PyImGui.end_columns()
                                                
            case DyesRule():
                ImGui.text_wrapped("This rule matches items based on their dye color. You can specify one or more dye colors to match against the item.")
                
                if ImGui.begin_child("##dye_colors", (0, 0), border=False):
                    sorted_dye_colors = sorted(DyeColor, key=lambda dc: dc.name)
                    for dye_color in sorted_dye_colors:
                        if dye_color == DyeColor.NoColor:
                            continue
                        
                        is_selected = dye_color in rule.dye_colors
                        selected = ImGui.checkbox(f"{dye_color.name}", is_selected)
                        
                        if selected != is_selected:
                            if dye_color in rule.dye_colors:
                                rule.dye_colors.remove(dye_color)
                            else:
                                rule.dye_colors.append(dye_color)
                            self.config.save()
                ImGui.end_child()
                
            case UpgradesRule():
                ImGui.text_wrapped("This rule matches items based on their upgrades. You can specify one or more upgrades to match against the item.")
            
            case _:
                ImGui.text("No editor available for this rule type.")