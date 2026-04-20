import os
from dataclasses import fields
from enum import Enum
from types import UnionType
from typing import Any, Optional, cast, get_args, get_origin

import Py4GW
import PyImGui

from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.ImGui_src.types import Alignment
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, AttributeNames
from Py4GWCoreLib.enums_src.Item_enums import ITEM_TYPE_META_TYPES, ItemType
from Py4GWCoreLib.item_mods_src.properties import ItemProperty
from Py4GWCoreLib.item_mods_src.types import ModifierIdentifier
from Py4GWCoreLib.item_mods_src.upgrades import (
    EnumInstruction,
    FixedValueInstruction,
    RangeInstruction,
    SelectInstruction,
    _INHERENT_UPGRADES,
    AppliesToRune,
    Instruction,
    Upgrade,
    _UPGRADES,
    UpgradeRune,
)
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
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
        available_upgrade_types: list[type[Upgrade]] = list(_UPGRADES)
        
        #Remove all subclasses and class of UpgradeRune, AppliesToRune
        self.available_inherent_upgrade_types: list[type[Upgrade]] = list(_INHERENT_UPGRADES)
        self.available_upgrade_types = [
            upgrade_type for upgrade_type in available_upgrade_types
            if not issubclass(upgrade_type, (UpgradeRune, AppliesToRune)) and upgrade_type is not UpgradeRune and upgrade_type is not AppliesToRune
        ]
        
        self.selected_upgrade_type_index = 0
        
        self.context_menu_id : str | None = None
        self.context_menu_rule : Rule | None = None
        self.context_menu_config : ConfigInfo | None = None

    @staticmethod
    def _get_concrete_item_types() -> list[ItemType]:
        return [
            item_type
            for item_type in ItemType
            if item_type not in ITEM_TYPE_META_TYPES and item_type != ItemType.Unknown
        ]

    @staticmethod
    def _humanize_name(value: str) -> str:
        return Utils.humanize_string(value.replace("None_", "None").replace("_None", "None")).strip()

    def _format_upgrade_type_label(self, upgrade_type: type[Upgrade]) -> str:
        type_name = upgrade_type.__name__.replace("Upgrade", "")
        return self._humanize_name(type_name)

    def _format_upgrade_label(self, upgrade: Upgrade) -> str:
        name = upgrade.name_plain if getattr(upgrade, "name_plain", "") else ""
        return name or self._format_upgrade_type_label(type(upgrade))

    def _format_enum_member(self, value: Enum | None) -> str:
        if value is None:
            return "None"

        if isinstance(value, Attribute):
            return AttributeNames.get(value, self._humanize_name(value.name))

        return self._humanize_name(value.name)

    @staticmethod
    def _get_enum_type(annotation: Any, current_value: Any) -> tuple[type[Enum] | None, bool]:
        if isinstance(current_value, Enum):
            return type(current_value), False

        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin in (UnionType, Optional) or (origin is not None and type(None) in args):
            enum_type = next(
                (
                    arg
                    for arg in args
                    if isinstance(arg, type) and issubclass(arg, Enum)
                ),
                None,
            )
            return enum_type, True

        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return annotation, False

        return None, False

    def _find_upgrade_property(self, upgrade: Upgrade, identifier: ModifierIdentifier) -> ItemProperty | None:
        getter = getattr(upgrade, "_get_upgrade_property", None)
        if callable(getter):
            prop = getter(identifier)
            if prop is not None:
                return cast(ItemProperty, prop)

        return upgrade.properties.get(identifier)

    def _allowed_values_match_enum(self, enum_type: type[Enum], allowed_values: tuple[int, ...] | None) -> bool:
        if not allowed_values:
            return False

        enum_values = {
            int(member.value)
            for member in enum_type
            if isinstance(member.value, int)
        }
        return all(value in enum_values for value in allowed_values)

    def _expand_item_type(self, item_type: ItemType) -> list[ItemType]:
        expanded = ITEM_TYPE_META_TYPES.get(item_type)
        if expanded is None:
            return [item_type] if item_type != ItemType.Unknown else []

        concrete_item_types: list[ItemType] = []
        for nested_item_type in expanded:
            for concrete_item_type in self._expand_item_type(nested_item_type):
                if concrete_item_type not in concrete_item_types:
                    concrete_item_types.append(concrete_item_type)

        return concrete_item_types

    def _get_allowed_item_types(self, upgrade: Upgrade) -> list[ItemType]:
        allowed_item_types: list[ItemType] = []

        for item_type in type(upgrade).id.item_type_id_map.keys():
            for concrete_item_type in self._expand_item_type(item_type):
                if concrete_item_type not in allowed_item_types:
                    allowed_item_types.append(concrete_item_type)

        target_item_type = getattr(type(upgrade), "target_item_type", ItemType.Unknown)
        if isinstance(target_item_type, ItemType):
            for concrete_item_type in self._expand_item_type(target_item_type):
                if concrete_item_type not in allowed_item_types:
                    allowed_item_types.append(concrete_item_type)

        instance_item_type = upgrade.item_type
        if instance_item_type is not None:
            for concrete_item_type in self._expand_item_type(instance_item_type):
                if concrete_item_type not in allowed_item_types:
                    allowed_item_types.append(concrete_item_type)

        if len(allowed_item_types) == 0:
            return self._get_concrete_item_types()

        return allowed_item_types

    def _normalize_item_type_filters(self, selected_item_types: list[ItemType], allowed_item_types: list[ItemType]) -> list[ItemType]:
        return [item_type for item_type in selected_item_types if item_type in allowed_item_types]

    def _create_upgrade_entry(self, upgrade_type: type[Upgrade]) -> tuple[Upgrade, list[ItemType]]:
        upgrade = upgrade_type()
        return upgrade, []

    def _draw_upgrade_type_combo(self, label: str, upgrade: Upgrade) -> Upgrade | None:
        if not self.available_upgrade_types:
            return None

        current_type = type(upgrade)
        current_index = next(
            (index for index, upgrade_type in enumerate(self.available_upgrade_types) if upgrade_type is current_type),
            0,
        )
        current_upgrade_type = self.available_upgrade_types[current_index]

        replacement: Upgrade | None = None
        if ImGui.begin_combo(label, self._format_upgrade_type_label(current_upgrade_type), PyImGui.ImGuiComboFlags.NoFlag):
            for index, upgrade_type in enumerate(self.available_upgrade_types):
                upgrade_label = self._format_upgrade_type_label(upgrade_type)
                if ImGui.selectable(f"{upgrade_label}##{label}_{index}", index == current_index):
                    replacement = upgrade_type()
            ImGui.end_combo()

        return replacement

    def _draw_upgrade_item_type_filters(self, upgrade: Upgrade, item_types: list[ItemType], unique_id: str) -> bool:
        changed = False
        allowed_item_types = self._get_allowed_item_types(upgrade)
        normalized_item_types = self._normalize_item_type_filters(item_types, allowed_item_types)
        if normalized_item_types != item_types:
            item_types[:] = normalized_item_types
            changed = True

        summary = "Any allowed item type" if len(item_types) == 0 else ", ".join(self._humanize_name(item_type.name) for item_type in item_types)

        if PyImGui.collapsing_header(f"Item Types: {summary}##{unique_id}", int(PyImGui.TreeNodeFlags.DefaultOpen)):
            if ImGui.begin_child(f"##upgrade_item_types_{unique_id}", (0, 140), border=True):
                for item_type in allowed_item_types:
                    is_selected = item_type in item_types
                    selected = ImGui.checkbox(f"{self._humanize_name(item_type.name)}##{unique_id}_{item_type.name}", is_selected)
                    if selected != is_selected:
                        if selected:
                            item_types.append(item_type)
                        else:
                            item_types.remove(item_type)
                        changed = True
            ImGui.end_child()

        return changed

    def _set_upgrade_field_value(self, upgrade: Upgrade, field_name: str, value: Any) -> None:
        setattr(upgrade, field_name, value)

        if field_name == "attribute" and hasattr(upgrade, "profession") and isinstance(value, Attribute):
            profession = value.get_profession()
            if profession is not None:
                setattr(upgrade, "profession", profession)

    def _get_upgrade_field_info(self, upgrade: Upgrade, field_name: str) -> Any | None:
        return next((field_info for field_info in fields(upgrade) if field_info.init and field_info.name == field_name), None)

    def _get_upgrade_instruction_groups(self, upgrade: Upgrade) -> list[tuple[str, list[Instruction[Upgrade, Any]]]]:
        grouped: dict[str, list[Instruction[Upgrade, Any]]] = {}
        for instruction in type(upgrade).upgrade_info:
            if instruction.target == "None":
                continue
            grouped.setdefault(instruction.target, []).append(instruction)

        return [(target, instructions) for target, instructions in grouped.items() if self._get_upgrade_field_info(upgrade, target) is not None]

    def _format_instruction_constraint(self, upgrade: Upgrade, instruction: Instruction[Upgrade, Any]) -> str:
        if isinstance(instruction, RangeInstruction):
            return f"{instruction.min_value}-{instruction.max_value}"

        if isinstance(instruction, SelectInstruction):
            return ", ".join(str(option) for option in instruction.options_list)

        if isinstance(instruction, EnumInstruction):
            enum_options = ", ".join(self._format_enum_member(member) for member in instruction.enum_type)
            return enum_options

        if isinstance(instruction, FixedValueInstruction):
            fixed_value = instruction.fixed_value
            if isinstance(fixed_value, Enum):
                return self._format_enum_member(fixed_value)
            return str(fixed_value)

        current_value = getattr(upgrade, instruction.target, None)
        if isinstance(current_value, Enum):
            return self._format_enum_member(current_value)
        return str(current_value)

    def _draw_upgrade_instruction_editor(self, upgrade: Upgrade, field_info: Any, instructions: list[Instruction[Upgrade, Any]], unique_id: str) -> bool:
        field_name = field_info.name
        label = self._humanize_name(field_name)
        current_value = getattr(upgrade, field_name)

        editable_instruction = next(
            (
                instruction
                for instruction in instructions
                if not isinstance(instruction, FixedValueInstruction)
            ),
            None,
        )
        
        if editable_instruction is None:
            # display_value = self._format_enum_member(current_value) if isinstance(current_value, Enum) else str(current_value)
            # ImGui.text(f"{label}: {display_value}")
            return False

        constraint_text = "; ".join(
            f"{type(instruction).__name__.replace('Instruction', '')}: {self._format_instruction_constraint(upgrade, instruction)}"
            for instruction in instructions
        )
        ImGui.text_colored(f"Constraint: {label} ({constraint_text})", UI.GRAY_COLOR, font_size=12)


        if isinstance(editable_instruction, EnumInstruction):
            options = list(editable_instruction.enum_type)
            preview_value = self._format_enum_member(current_value if isinstance(current_value, Enum) else None)
            changed = False
            if ImGui.begin_combo(f"{label}##{unique_id}_{field_name}", preview_value, PyImGui.ImGuiComboFlags.NoFlag):
                for index, option in enumerate(options):
                    option_label = self._format_enum_member(option)
                    is_selected = option == current_value
                    if ImGui.selectable(f"{option_label}##{unique_id}_{field_name}_{index}", is_selected):
                        self._set_upgrade_field_value(upgrade, field_name, option)
                        changed = True
                ImGui.end_combo()
            return changed

        if isinstance(editable_instruction, SelectInstruction):
            options = list(editable_instruction.options_list)
            preview_value = self._format_enum_member(current_value) if isinstance(current_value, Enum) else str(current_value)
            changed = False
            if ImGui.begin_combo(f"{label}##{unique_id}_{field_name}", preview_value, PyImGui.ImGuiComboFlags.NoFlag):
                for index, option in enumerate(options):
                    option_label = self._format_enum_member(option) if isinstance(option, Enum) else str(option)
                    is_selected = option == current_value
                    if ImGui.selectable(f"{option_label}##{unique_id}_{field_name}_{index}", is_selected):
                        self._set_upgrade_field_value(upgrade, field_name, option)
                        changed = True
                ImGui.end_combo()
            return changed

        if isinstance(editable_instruction, RangeInstruction) and isinstance(current_value, int):
            new_value = ImGui.input_int(f"{label}##{unique_id}_{field_name}", v=current_value, min_value=1, step_fast=1)
            new_value = max(editable_instruction.min_value, min(editable_instruction.max_value, new_value))
            if new_value != current_value:
                self._set_upgrade_field_value(upgrade, field_name, new_value)
                return True
            return False

        if isinstance(editable_instruction, RangeInstruction) and isinstance(current_value, float):
            new_value = ImGui.input_float(f"{label}##{unique_id}_{field_name}", current_value)
            new_value = max(editable_instruction.min_value, min(editable_instruction.max_value, new_value))
            if new_value != current_value:
                self._set_upgrade_field_value(upgrade, field_name, new_value)
                return True
            return False

        return self._draw_upgrade_field_editor(upgrade, field_info, unique_id)

    def _draw_upgrade_field_editor(self, upgrade: Upgrade, field_info: Any, unique_id: str) -> bool:
        field_name = field_info.name
        label = self._humanize_name(field_name)
        current_value = getattr(upgrade, field_name)

        if isinstance(current_value, bool):
            new_value = ImGui.checkbox(f"{label}##{unique_id}_{field_name}", current_value)
            if new_value != current_value:
                self._set_upgrade_field_value(upgrade, field_name, new_value)
                return True
            return False

        enum_type, allow_none = self._get_enum_type(field_info.type, current_value)
        if enum_type is not None:
            options: list[Enum | None] = [None] if allow_none else []
            options.extend(list(enum_type))

            preview_value = self._format_enum_member(current_value if isinstance(current_value, Enum) else None)
            changed = False
            if ImGui.begin_combo(f"{label}##{unique_id}_{field_name}", preview_value, PyImGui.ImGuiComboFlags.NoFlag):
                for index, option in enumerate(options):
                    option_label = self._format_enum_member(option)
                    is_selected = option == current_value
                    if ImGui.selectable(f"{option_label}##{unique_id}_{field_name}_{index}", is_selected):
                        self._set_upgrade_field_value(upgrade, field_name, option)
                        changed = True
                ImGui.end_combo()

            return changed

        if isinstance(current_value, int):
            new_value = ImGui.input_int(f"{label}##{unique_id}_{field_name}", v=current_value, min_value=1, step_fast=1)
            if new_value != current_value:
                self._set_upgrade_field_value(upgrade, field_name, new_value)
                return True
            return False

        if isinstance(current_value, float):
            new_value = ImGui.input_float(f"{label}##{unique_id}_{field_name}", current_value)
            if new_value != current_value:
                self._set_upgrade_field_value(upgrade, field_name, new_value)
                return True
            return False

        if isinstance(current_value, str):
            new_value = ImGui.input_text(f"{label}##{unique_id}_{field_name}", current_value)
            if new_value != current_value:
                self._set_upgrade_field_value(upgrade, field_name, new_value)
                return True
            return False

        display_value = self._format_enum_member(current_value) if isinstance(current_value, Enum) else str(current_value)
        ImGui.text(f"{label}: {display_value}")
        return False

    def _draw_upgrade_entry(self, rule: UpgradesRule, index: int, upgrade: Upgrade, item_types: list[ItemType]) -> tuple[bool, bool]:
        changed = False
        removed = False
        unique_id = f"upgrade_rule_{id(rule)}_{index}"

        if ImGui.button(f"Remove##{unique_id}", 70):
            removed = True

        PyImGui.same_line(0, 8)
        is_open = PyImGui.collapsing_header(
            f"{self._format_upgrade_label(upgrade)}##{unique_id}",
            int(PyImGui.TreeNodeFlags.DefaultOpen),
        )

        if not is_open:
            return changed, removed

        replacement = self._draw_upgrade_type_combo(f"Upgrade Type##{unique_id}", upgrade)
        if replacement is not None:
            item_types = self._normalize_item_type_filters(item_types, self._get_allowed_item_types(replacement))
            rule.upgrades[index] = (replacement, item_types)
            upgrade = replacement
            changed = True

        description = upgrade.description_plain
        if description:
            ImGui.text_wrapped(description)

        instruction_groups = self._get_upgrade_instruction_groups(upgrade)
        if len(instruction_groups) > 0:
            for field_name, instructions in instruction_groups:
                field_info = self._get_upgrade_field_info(upgrade, field_name)
                if field_info is None:
                    continue

                if self._draw_upgrade_instruction_editor(upgrade, field_info, instructions, unique_id):
                    changed = True
        else:
            ImGui.text_colored("This upgrade has no editable upgrade instructions. Its values are fixed by the selected upgrade type.", UI.GRAY_COLOR, font_size=12)

        if self._draw_upgrade_item_type_filters(upgrade, item_types, unique_id):
            changed = True

        return changed, removed

    def _draw_upgrades_rule(self, rule: UpgradesRule) -> bool:
        changed = False

        if len(self.available_upgrade_types) > 0:
            selected_upgrade_type = self.available_upgrade_types[self.selected_upgrade_type_index]
            preview_label = self._format_upgrade_type_label(selected_upgrade_type)

            if ImGui.begin_combo("New Upgrade##upgrade_rule_add", preview_label, PyImGui.ImGuiComboFlags.NoFlag):
                for index, upgrade_type in enumerate(self.available_upgrade_types):
                    upgrade_label = self._format_upgrade_type_label(upgrade_type)
                    if ImGui.selectable(f"{upgrade_label}##new_upgrade_{index}", index == self.selected_upgrade_type_index):
                        self.selected_upgrade_type_index = index
                ImGui.end_combo()

            if ImGui.button("Add Upgrade##upgrade_rule_add_button", -1):
                rule.upgrades.append(self._create_upgrade_entry(self.available_upgrade_types[self.selected_upgrade_type_index]))
                changed = True

        ImGui.separator()

        if len(rule.upgrades) == 0:
            ImGui.text_colored("No upgrades configured yet.", UI.GRAY_COLOR, font_size=12)
            return changed

        remove_index = -1
        for index, (upgrade, item_types) in enumerate(rule.upgrades):
            entry_changed, removed = self._draw_upgrade_entry(rule, index, upgrade, item_types)
            if entry_changed:
                changed = True
            if removed:
                remove_index = index

        if remove_index >= 0:
            del rule.upgrades[remove_index]
            changed = True

        return changed

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
                if self._draw_upgrades_rule(rule):
                    self.config.save()
            
            case _:
                ImGui.text("No editor available for this rule type.")
