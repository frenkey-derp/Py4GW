import os
import struct
import time
from dataclasses import fields
from enum import Enum
from types import UnionType
from typing import Any, Optional, cast, get_args, get_origin

import Py4GW
import PyImGui

from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.ImGui_src.types import Alignment
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, AttributeNames, Profession
from Py4GWCoreLib.enums_src.Item_enums import ITEM_TYPE_META_TYPES, ItemType
from Py4GWCoreLib.enums_src.Texture_enums import ProfessionTextureMap
from Py4GWCoreLib.item_mods_src.item_mod import ItemMod
from Py4GWCoreLib.item_mods_src.properties import ItemProperty
from Py4GWCoreLib.item_mods_src.types import ItemUpgradeType, ModifierIdentifier
from Py4GWCoreLib.item_mods_src.upgrades import (
    EnumInstruction,
    FixedValueInstruction,
    Inscription,
    Insignia,
    OfTheProfessionUpgrade,
    RangeInstruction,
    Rune,
    SelectInstruction,
    _INHERENT_UPGRADES,
    AppliesToRune,
    Instruction,
    Upgrade,
    _UPGRADES,
    UpgradeRune,
)
from Py4GWCoreLib.native_src.internals import string_table
from Py4GWCoreLib.native_src.internals.encoded_strings import GWEncoded
from Py4GWCoreLib.py4gwcorelib_src.Color import Color, ColorPalette
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.BuyConfig import BuyConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.DepositConfig import DepositConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig 
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.ProtectedItemsConfig import ProtectedItemsConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import *
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.SalvageConfig import SalvageConfig 
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.SellConfig import SellConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.UpgradesConfig import UpgradesConfig
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions
from Sources.frenkeyLib.ItemManager.btrees import TraderPriceCheckManager, TraderQuote
from Sources.frenkeyLib.ItemManager.config import Config


_STRING_TABLE_BASE = 0x7F00
_STRING_TABLE_DIGIT_BASE = 0x0100
_STRING_TABLE_MORE = 0x8000


def _encode_string_table_number(value: int) -> bytes:
    if value < 0:
        raise ValueError("String-table numeric arguments must be non-negative.")

    if value == 0:
        return b""

    digits: list[int] = []
    current = value
    while current > 0:
        current, remainder = divmod(current, _STRING_TABLE_BASE)
        digits.append(remainder + _STRING_TABLE_DIGIT_BASE)

    digits.reverse()
    for i in range(len(digits) - 1):
        digits[i] |= _STRING_TABLE_MORE

    return struct.pack(f"<{len(digits)}H", *digits)


def _gold_amount_bytes(amount: int) -> bytes:
    return bytes([*GWEncoded.NUM1_GOLD, 0x1, 0x1]) + _encode_string_table_number(amount) + bytes([0x1, 0x0])


def _platinum_amount_bytes(amount: int) -> bytes:
    return bytes([*GWEncoded.NUM1_PLATINUM, 0x1, 0x1]) + _encode_string_table_number(amount) + bytes([0x1, 0x0])


def _formatted_currency_amount_bytes(amount: int) -> tuple[bytes, bytes]:
    platinum_amount = amount // 1000
    gold_amount = amount % 1000

    return _platinum_amount_bytes(platinum_amount) if platinum_amount > 0 else b"", _gold_amount_bytes(gold_amount) if gold_amount > 0 else b""

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
    UpgradeTexture = NamedTuple("UpgradeTextures", [("prefix", str), ("suffix", str)])
    
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
            ConfigInfo(BuyConfig(), "Buying", "Configure which items to buy", folder_path),
            ConfigInfo(DepositConfig(), "Depositing", "Configure which items to deposit", folder_path),
            ConfigInfo(LootConfig(), "Looting", "Configure which items to pick up and which to ignore", folder_path),
            ConfigInfo(ProtectedItemsConfig(), "Protected Items", "Configure which items to protect from all other configurations", folder_path),
            ConfigInfo(SalvageConfig(), "Salvaging", "Configure which items to salvage", folder_path),
            ConfigInfo(SellConfig(), "Selling", "Configure which items to sell", folder_path),
            ConfigInfo(UpgradesConfig(), "Upgrades", "Configure upgrades to extract", folder_path),
        ]
        
        for config_info in self.configs:
            config_info.load()
        
        self.config : Optional[ConfigInfo] = None
        self.rule : Optional[Rule] = None
        
        self.switch_to_config(self.configs[0] if len(self.configs) > 0 else None)
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
        
        self.profession : Profession = Profession._None
        self.mod_type : ItemUpgradeType = ItemUpgradeType.Prefix
        self.armor_upgrade_price_threshold: int = 250
        self._armor_upgrade_quote_cache_generation: int | None = None
        self._armor_upgrade_quote_cache_profession: Profession | None = None
        self._armor_upgrade_quote_cache_processed_item_ids: set[int] = set()
        self._armor_upgrade_quote_cache: dict[Any, TraderQuote] = {}
        self.texture_path = os.path.join(Py4GW.Console.get_projects_path(), "Textures")
        
        self.weapon_upgrade_textures : dict[ItemType, UI.UpgradeTexture] = {
                ItemType.Axe : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "00893-Axe_Haft.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "00905-Axe_Grip.png"),
                ),
                ItemType.Bow : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "00894-Bow_String.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "00906-Bow_Grip.png"),
                ),
                ItemType.Daggers : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "06323-Dagger_Tang.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "06331-Dagger_Handle.png"),
                ),
                ItemType.Hammer : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "00895-Hammer_Haft.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "00907-Hammer_Grip.png"),
                ),
                ItemType.Offhand : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "missing_texture.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "15551-Focus_Core.png"),
                ),
                ItemType.Scythe : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "15543-Scythe_Snathe.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "15553-Scythe_Grip.png"),
                ),
                ItemType.Shield : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "missing_texture.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "15554-Shield_Handle.png"),
                ),
                ItemType.Spear : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "15544-Spearhead.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "15555-Spear_Grip.png"),
                ),
                ItemType.Staff : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "00896-Staff_Head.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "00908-Staff_Wrapping.png"),
                ),
                ItemType.Sword : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "Item Models", "00897-Sword_Hilt.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "00909-Sword_Pommel.png"),
                ),
                ItemType.Wand : UI.UpgradeTexture(
                    prefix=os.path.join(self.texture_path, "missing_texture.png"),
                    suffix=os.path.join(self.texture_path, "Item Models", "15552-Wand_Wrapping.png"),
                ),
            }
        
    @staticmethod
    def format_currency(value: int) -> str:
        plat, gold = _formatted_currency_amount_bytes(value)
        
        return (string_table.decode(plat) + " " if plat else "") + string_table.decode(gold)

    @staticmethod
    def format_time_ago(timestamp: float) -> str:
        elapsed = max(0, int(time.time() - timestamp))
        units = [
            ("year", 365 * 24 * 60 * 60),
            ("month", 30 * 24 * 60 * 60),
            ("day", 24 * 60 * 60),
            ("hour", 60 * 60),
            ("minute", 60),
            ("second", 1),
        ]

        parts: list[str] = []
        remaining = elapsed

        for label, unit_seconds in units:
            value, remaining = divmod(remaining, unit_seconds)
            if value <= 0:
                continue

            parts.append(f"{value} {label}{'' if value == 1 else 's'}")

        return f"{' '.join(parts) if parts else '0 seconds'} ago"
    
    @staticmethod
    def _get_concrete_item_types() -> list[ItemType]:
        return [
            item_type
            for item_type in ItemType
            if item_type not in ITEM_TYPE_META_TYPES and item_type != ItemType.Unknown
        ]

    @staticmethod
    def _get_rule_types() -> list[type[Rule]]:
        discovered_rule_types: list[type[Rule]] = []

        def visit(rule_type: type[Rule]) -> None:
            for child_rule_type in rule_type.__subclasses__():
                if child_rule_type not in discovered_rule_types:
                    discovered_rule_types.append(child_rule_type)
                visit(child_rule_type)

        visit(Rule)
        return [
            rule_type
            for rule_type in discovered_rule_types
            if getattr(rule_type, "ui_selectable", True)
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
    def GetRarityColor(rarity) -> Color:
        rarity_colors = {
            Rarity.White: Color(255, 255, 255, 255),
            Rarity.Blue: Color(153, 238, 255, 255),
            Rarity.Green: Color(0, 255, 0, 255),
            Rarity.Purple: Color(187, 136, 238, 255),
            Rarity.Gold: Color(255, 204, 85, 255),
        }

        if (rarity in rarity_colors):
            return rarity_colors[rarity]
        else:
            return ColorPalette.GetColor("white")
        
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

        if len(allowed_item_types) == 0:
            return []

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
        
        if not allowed_item_types:
            return False
        
        normalized_item_types = self._normalize_item_type_filters(item_types, allowed_item_types)
        if normalized_item_types != item_types:
            item_types[:] = normalized_item_types
            changed = True
            
        if len(allowed_item_types) <= 1:
            item_types[:] = allowed_item_types
            return changed

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

    @staticmethod
    def _normalize_upgrade_lookup_name(value: str) -> str:
        normalized = value.lower().strip()
        if "[" in normalized:
            normalized = normalized.split("[", 1)[0].strip()

        for profession in Profession:
            profession_name = profession.name.lower().strip("_")
            if profession_name:
                normalized = normalized.replace(profession_name, "")

        normalized = normalized.replace("'", "").replace("-", "").replace(" ", "")
        return "".join(ch for ch in normalized if ch.isalnum())

    def _get_upgrade_lookup_candidates(self, upgrade: ArmorUpgrade) -> set[str]:
        candidates = {
            self._normalize_upgrade_lookup_name(upgrade.name_plain),
            self._normalize_upgrade_lookup_name(self._format_upgrade_label(upgrade)),
            self._normalize_upgrade_lookup_name(type(upgrade).__name__),
        }

        return {candidate for candidate in candidates if candidate}

    def _get_trader_armor_upgrade_quotes(self) -> list[TraderQuote]:
        trader_output = TraderPriceCheckManager.get_output()
        quotes = [quote for quote in trader_output.quotes.values() if quote.is_rune_mod]

        if self.profession != Profession._None:
            quotes = [quote for quote in quotes if quote.profession in (self.profession, Profession._None)]

        return quotes

    @staticmethod
    def _upgrade_equals(left: ArmorUpgrade, right: ArmorUpgrade) -> bool:
        return left._comparison_data() == right._comparison_data()

    def _extract_armor_upgrades_from_trader_quote(self, quote: TraderQuote) -> list[ArmorUpgrade]:
        prefix, suffix, inscription, inherent = ItemMod.get_item_upgrades(quote.item_id)
        upgrades = [upgrade for upgrade in [prefix, suffix, inscription, *(inherent or [])] if isinstance(upgrade, ArmorUpgrade)]

        # Py4GW.Console.Log(
        #     "Item Manager",
        #     f"Parsed {len(upgrades)} armor upgrades from trader item {quote.item_id} ('{quote.name}') model={quote.model_id}.",
        #     Py4GW.Console.MessageType.Info,
        # )

        # for upgrade in upgrades:
        #     Py4GW.Console.Log(
        #         "Item Manager",
        #         f"Parsed trader upgrade '{upgrade.name_plain}' ({type(upgrade).__name__}) from item {quote.item_id}.",
        #         Py4GW.Console.MessageType.Info,
        #     )

        return upgrades

    def _get_armor_upgrade_quote_lookup(self) -> dict[Any, TraderQuote]:
        quotes = self._get_trader_armor_upgrade_quotes()
        generation = TraderPriceCheckManager.get_generation()

        if (
            self._armor_upgrade_quote_cache_generation != generation
            or self._armor_upgrade_quote_cache_profession != self.profession
        ):
            self._armor_upgrade_quote_cache_generation = generation
            self._armor_upgrade_quote_cache_profession = self.profession
            self._armor_upgrade_quote_cache_processed_item_ids.clear()
            self._armor_upgrade_quote_cache = {}

        current_quote_ids = {quote.item_id for quote in quotes}
        if not current_quote_ids.issuperset(self._armor_upgrade_quote_cache_processed_item_ids):
            self._armor_upgrade_quote_cache_processed_item_ids.clear()
            self._armor_upgrade_quote_cache = {}

        for quote in quotes:
            if quote.item_id in self._armor_upgrade_quote_cache_processed_item_ids:
                continue

            for parsed_upgrade in self._extract_armor_upgrades_from_trader_quote(quote):
                comparison_key = parsed_upgrade._comparison_data()
                current_quote = self._armor_upgrade_quote_cache.get(comparison_key)
                if current_quote is None or quote.quoted_value > current_quote.quoted_value:
                    self._armor_upgrade_quote_cache[comparison_key] = quote
            self._armor_upgrade_quote_cache_processed_item_ids.add(quote.item_id)

        return self._armor_upgrade_quote_cache

    def _get_trader_quote_for_armor_upgrade(self, upgrade: ArmorUpgrade) -> TraderQuote | None:
        return self._get_armor_upgrade_quote_lookup().get(upgrade._comparison_data())

    def _select_armor_upgrades_from_trader_prices(self, rule: ArmorUpgradeRule, minimum_value: int) -> bool:
        Py4GW.Console.Log("Item Manager", f"Selecting armor upgrades from trader prices with threshold {minimum_value} for profession {self.profession.name}.", Py4GW.Console.MessageType.Info)

        quotes = self._get_trader_armor_upgrade_quotes()
        if not quotes:
            Py4GW.Console.Log("Item Manager", "No trader rune / insignia quotes available for the selected profession.", Py4GW.Console.MessageType.Warning)
            return False

        eligible_quotes: list[TraderQuote] = []
        for quote in quotes:
            normalized_quote_name = self._normalize_upgrade_lookup_name(quote.name)
            Py4GW.Console.Log(
                "Item Manager",
                f"Trader quote: '{quote.name}' -> '{normalized_quote_name}', value={quote.quoted_value}, profession={quote.profession.name}",
                Py4GW.Console.MessageType.Info,
            )

            if quote.quoted_value < minimum_value:
                continue

            eligible_quotes.append(quote)

        if not eligible_quotes:
            Py4GW.Console.Log("Item Manager", f"No trader quotes met the threshold {minimum_value}.", Py4GW.Console.MessageType.Warning)
            return False

        selected_upgrades: list[ArmorUpgrade] = []
        for quote in eligible_quotes:
            parsed_upgrades = self._extract_armor_upgrades_from_trader_quote(quote)
            if not parsed_upgrades:
                Py4GW.Console.Log(
                    "Item Manager",
                    f"No armor upgrades could be parsed from trader item {quote.item_id} ('{quote.name}').",
                    Py4GW.Console.MessageType.Warning,
                )
                continue

            for parsed_upgrade in parsed_upgrades:
                if self.profession != Profession._None and parsed_upgrade.profession not in (self.profession, Profession._None):
                    Py4GW.Console.Log(
                        "Item Manager",
                        f"Skipping parsed upgrade '{parsed_upgrade.name_plain}' because its profession is {parsed_upgrade.profession.name}, expected {self.profession.name}.",
                        Py4GW.Console.MessageType.Info,
                    )
                    continue

                selected_upgrades.append(parsed_upgrade)
                Py4GW.Console.Log(
                    "Item Manager",
                    f"Selected parsed trader upgrade '{parsed_upgrade.name_plain}' ({type(parsed_upgrade).__name__}) from item {quote.item_id} with value {quote.quoted_value}.",
                    Py4GW.Console.MessageType.Success,
                )

        if not selected_upgrades:
            Py4GW.Console.Log("Item Manager", "No armor upgrades could be extracted from the trader quotes that met the threshold.", Py4GW.Console.MessageType.Warning)
            return False

        changed = False
        added_count = 0

        for selected_upgrade in selected_upgrades:
            if any(self._upgrade_equals(existing_upgrade, selected_upgrade) for existing_upgrade in rule.armor_upgrades):
                Py4GW.Console.Log(
                    "Item Manager",
                    f"Upgrade '{selected_upgrade.name_plain}' ({type(selected_upgrade).__name__}) is already present in the rule.",
                    Py4GW.Console.MessageType.Info,
                )
                continue

            rule.armor_upgrades.append(selected_upgrade)
            changed = True
            added_count += 1
            Py4GW.Console.Log(
                "Item Manager",
                f"Added upgrade '{selected_upgrade.name_plain}' ({type(selected_upgrade).__name__}) to the armor upgrade rule.",
                Py4GW.Console.MessageType.Success,
            )

        if not changed:
            Py4GW.Console.Log("Item Manager", "Trader-based selection found matches, but all of them were already selected.", Py4GW.Console.MessageType.Warning)
        else:
            Py4GW.Console.Log("Item Manager", f"Trader-based selection added {added_count} upgrades to the rule.", Py4GW.Console.MessageType.Success)

        return changed

    def _draw_armor_upgrade_price_popup(self, rule: ArmorUpgradeRule) -> bool:
        changed = False
        popup_id = "##armor_upgrade_price_popup"
        trader_open = UIManagerExtensions.IsMerchantWindowOpen()
        kind = TraderPriceCheckManager.get_kind()
        PyImGui.begin_disabled(not trader_open or kind != "runes")
        if ImGui.button("Select From Trader Prices", -1):
            PyImGui.open_popup(popup_id)
        PyImGui.end_disabled()

        if PyImGui.is_item_hovered():
            if not trader_open or kind != "runes":
                ImGui.show_tooltip("Open the rune trader window to enable this option.")
            else:
                ImGui.show_tooltip("Open a popup to select runes and insignias priced at or above a threshold.")

        if PyImGui.begin_popup(popup_id):
            ImGui.text("Select Upgrades By Price")
            ImGui.separator()

            new_threshold = ImGui.input_int("Minimum trader value", self.armor_upgrade_price_threshold, min_value=0, step_fast=1)
            if new_threshold != self.armor_upgrade_price_threshold:
                self.armor_upgrade_price_threshold = max(0, new_threshold)

            quote_count = len(self._get_trader_armor_upgrade_quotes())
            ImGui.text_colored(f"Available trader quotes: {quote_count}", UI.GRAY_COLOR, font_size=12)

            if ImGui.button("Apply Threshold", -1):
                changed = self._select_armor_upgrades_from_trader_prices(rule, self.armor_upgrade_price_threshold)
                PyImGui.close_current_popup()

            if ImGui.button("Cancel", -1):
                PyImGui.close_current_popup()

            PyImGui.end_popup()

        return changed

    def _draw_armor_upgrades_rule(self, rule: ArmorUpgradeRule) -> bool:
        changed = False

        if self._draw_armor_upgrade_price_popup(rule):
            changed = True
        
        ImGui.separator()
        
        if ImGui.begin_table("##armor_upgrade_rule_table", 2, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable):
            PyImGui.table_setup_column("Profession", PyImGui.TableColumnFlags.WidthFixed, 150)
            PyImGui.table_setup_column("Upgrades", PyImGui.TableColumnFlags.WidthStretch)
            
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            
            if ImGui.begin_child("##armor_upgrade_rule_profession", (0, 0), border=False):
                for profession in Profession:
                    is_selected = profession == self.profession
                    decoded_profession_name = string_table.decode(GWEncoded.PROFESSION.get(profession, bytes())) or self._humanize_name(profession.name)   
                     
                    if ImGui.begin_selectable(f"##profession_{profession.value}", is_selected):
                        ImGui.image(os.path.join(self.texture_path, "Profession_Icons", ProfessionTextureMap.get(profession.value, "")), (24, 24))
                        PyImGui.same_line(0, 5)
                        ImGui.text_aligned(decoded_profession_name, height=24, alignment=Alignment.MidLeft)
                        
                    if ImGui.end_selectable():
                        self.profession = profession
                    
            ImGui.end_child()
            
            PyImGui.table_next_column()
            
            if ImGui.begin_child("##armor_upgrade_rule_upgrades", (0, 0), border=False):
                try:
                    #get all subclasses of ArmorUpgrade which has the selected profession
                    upgrades = [
                        upgrade_type for upgrade_type in self.available_upgrade_types
                        if issubclass(upgrade_type, ArmorUpgrade) and getattr(upgrade_type, "profession", None) == self.profession
                    ]               
                    
                    #sort by rarity, then by name
                    sorted_upgrades = sorted(upgrades, key=lambda ut: (getattr(ut, "rarity", 0), self._format_upgrade_type_label(ut)))
                    
                    insignias = [
                        upgrade_type for upgrade_type in sorted_upgrades if issubclass(upgrade_type, Insignia)
                    ]
                    
                    runes = [
                        upgrade_type for upgrade_type in sorted_upgrades if issubclass(upgrade_type, Rune)
                    ]
                    
                    for upgrade_type in [*insignias, *runes]:
                        upgrade : ArmorUpgrade = upgrade_type()
                        upgrade_label = self._format_upgrade_label(upgrade)
                        is_upgrade_selected = any(isinstance(existing_upgrade, upgrade_type) for existing_upgrade in rule.armor_upgrades)
                        
                        if ImGui.begin_selectable(f"##armor_upgrade_{upgrade_type.__name__}", is_upgrade_selected, (0 , 20)):
                            rarity_color = UI.GetRarityColor(upgrade.rarity)
                            ImGui.text_colored(upgrade_label, rarity_color.color_tuple, font_size=14)
                        
                        if ImGui.end_selectable():
                            if is_upgrade_selected:
                                rule.armor_upgrades = [existing_upgrade for existing_upgrade in rule.armor_upgrades if not isinstance(existing_upgrade, upgrade_type)]
                            else:
                                rule.armor_upgrades.append(upgrade_type())
                            changed = True
                        
                        if PyImGui.is_item_hovered():
                            quote = self._get_trader_quote_for_armor_upgrade(upgrade)
                            tooltip_text = upgrade.description_plain
                            if quote is not None:
                                tooltip_text = (
                                    f"{tooltip_text}\n"
                                    f"Trader Quote: {UI.format_currency(quote.quoted_value)}\n"
                                    f"Last updated: {UI.format_time_ago(quote.checked_at)}"
                                )

                            ImGui.show_tooltip(tooltip_text)
                        
                except Exception as e:
                    ImGui.text_colored(f"Error loading upgrades: {str(e)}", (255, 0, 0, 255), font_size=12)
                        
            ImGui.end_child()
            ImGui.end_table()

        return changed

    def _draw_max_weapon_upgrades_rule(self, rule: MaxWeaponUpgradeRule) -> bool:
        changed = False
        
        if ImGui.begin_table("##weapon_upgrade_rule_table", 2, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable):
            PyImGui.table_setup_column("Mod Type", PyImGui.TableColumnFlags.WidthFixed, 150)
            PyImGui.table_setup_column("Upgrades", PyImGui.TableColumnFlags.WidthStretch)
            
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            
            if ImGui.begin_child("##mod_type_selection", (0, 0), border=False):
                for mod_type in [ItemUpgradeType.Prefix, ItemUpgradeType.Suffix, ItemUpgradeType.Inscription]:
                    is_selected = mod_type == self.mod_type
                    mod_type_name = self._humanize_name(mod_type.name)   
                     
                    if ImGui.begin_selectable(f"##mod_type_{mod_type.value}", is_selected):
                        ImGui.text_aligned(mod_type_name, height=24, alignment=Alignment.MidLeft)
                        
                    if ImGui.end_selectable():
                        self.mod_type = mod_type
                    
            ImGui.end_child()
            
            PyImGui.table_next_column()
            style = ImGui.get_style()
            style.ToggleButtonEnabled.push_color(self.GetRarityColor(Rarity.Gold).opacity(0.85).rgb_tuple)
            style.ToggleButtonDisabled.push_color((0, 0, 0, 85))
            
            if ImGui.begin_child("##armor_upgrade_rule_upgrades", (0, 0), border=False):
                #get all subclasses of ArmorUpgrade which has the selected profession
                upgrades = [
                    upgrade_type for upgrade_type in self.available_upgrade_types
                    if (issubclass(upgrade_type, WeaponUpgrade) or issubclass(upgrade_type, Inscription)) and getattr(upgrade_type, "mod_type", None) == self.mod_type
                ]                
                                
                for upgrade_type in sorted(upgrades, key=lambda ut: self._format_upgrade_type_label(ut)):
                    variants = [upgrade_type]
                    # if upgrade_type is OfTheProfessionUpgrade:
                    #     variants = [
                    #         lambda ut=upgrade_type, profession=profession: ut(profession=profession)
                    #         for profession in Profession
                    #     ]
                    
                    # if upgrade_type is OfAttributeUpgrade:
                    #     variants = [
                    #         lambda ut=upgrade_type, attribute=attribute: ut(attribute=attribute)
                    #         for attribute in Attribute
                    #     ]
                    
                    for variant in variants:
                        upgrade = variant()
                        upgrade_label = self._format_upgrade_label(upgrade)
                        item_types : list[ItemType] = []
                        
                        if isinstance(upgrade, WeaponUpgrade):
                            item_types = self._get_allowed_item_types(upgrade)
                            rarity_color = UI.GetRarityColor(upgrade.rarity)
                            hovered = False
                            if PyImGui.is_rect_visible(10, 70):  
                                if ImGui.begin_child(f"##upgrade_item_types_{variant}", (0, 70), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):                          
                                        ImGui.text_colored(upgrade_label, rarity_color.color_tuple, font_size=14)
                                        
                                        ImGui.separator()
                                        
                                        if item_types:
                                            for item_type in item_types:
                                                is_upgrade_selected = any(isinstance(existing_upgrade.upgrade, upgrade_type) and item_type in existing_upgrade.item_types for existing_upgrade in rule.weapon_upgrades)
                                                
                                                texture = self.weapon_upgrade_textures.get(item_type)
                                                if texture:
                                                    ImGui.image_toggle_button(f"##{variant}_{item_type.name}", texture.prefix if self.mod_type == ItemUpgradeType.Prefix else texture.suffix, is_upgrade_selected, 24, 24)
                                                    encoded = upgrade.create_upgrade_name(item_type)
                                                    if PyImGui.is_item_clicked(0):
                                                        if is_upgrade_selected:
                                                            rule.weapon_upgrades = [existing_upgrade for existing_upgrade in rule.weapon_upgrades if not (isinstance(existing_upgrade.upgrade, upgrade_type) and item_type in existing_upgrade.item_types)]
                                                        else:
                                                            existing_entry = next((existing_upgrade for existing_upgrade in rule.weapon_upgrades if isinstance(existing_upgrade.upgrade, upgrade_type)), None)
                                                            if existing_entry:
                                                                existing_entry.item_types.append(item_type)
                                                            else:
                                                                rule.weapon_upgrades.append(UpgradeAndItemType(upgrade=upgrade, item_types=[item_type]))
                                                        changed = True
                                                    
                                                    # ImGui.show_tooltip(string_table.decode(encoded).replace("%str2%", upgrade_label) if encoded else self._humanize_name(item_type.name))
                                                    ImGui.show_tooltip(encoded.plain if encoded else self._humanize_name(item_type.name))
                                                    # ImGui.show_tooltip(string_table.decode(upgrade.__encoded_name.encoded + encoded) if encoded else self._humanize_name(item_type.name))
                                                    
                                                    hovered = hovered or PyImGui.is_item_hovered()
                                                    
                                                    PyImGui.same_line(0, 5)
                                    
                                ImGui.end_child()
                            
                                if not hovered:
                                    ImGui.show_tooltip(upgrade.description_plain)
                            else:
                                ImGui.dummy(0, 70)
                            
                        else:             
                            is_upgrade_selected = any(isinstance(existing_upgrade.upgrade, upgrade_type) for existing_upgrade in rule.weapon_upgrades)
                            
                            if PyImGui.is_rect_visible(10, 25):     
                                if ImGui.begin_selectable(f"##armor_upgrade_{upgrade_type.__name__}", is_upgrade_selected, (0, 25)):
                                    rarity_color = UI.GetRarityColor(upgrade.rarity)
                                    ImGui.text_colored(upgrade_label, rarity_color.color_tuple, font_size=14)
                                    
                                if ImGui.end_selectable():
                                    if is_upgrade_selected:
                                        rule.weapon_upgrades = [existing_upgrade for existing_upgrade in rule.weapon_upgrades if not isinstance(existing_upgrade.upgrade, upgrade_type)]
                                    else:
                                        rule.weapon_upgrades.append(UpgradeAndItemType(upgrade=upgrade, item_types=[]))
                                    changed = True
                            
                                ImGui.show_tooltip(upgrade.description_plain)
                            else:
                                ImGui.dummy(0, 25)
                        
            ImGui.end_child()
            
            style.ToggleButtonDisabled.pop_color()
            style.ToggleButtonEnabled.pop_color()
            
            ImGui.end_table()

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
        
    def switch_to_config(self, rule_config: ConfigInfo | None):
        self.config = rule_config or (self.configs[0] if len(self.configs) > 0 else None)
        self.rule = self.config.config[0] if self.config and len(self.config.config) > 0 else None
        
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
                        self.switch_to_config(config)
                    
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
                allowed_rule_types = config_info.config.GetAllowedRuleTypes()
                for rule_type in self._get_rule_types():
                    if allowed_rule_types is not None and not issubclass(rule_type, allowed_rule_types):
                        continue
                    if ImGui.selectable(rule_type.__name__, False):
                        new_rule = rule_type()
                        config_info.config.AddRule(new_rule)
                        config_info.save()
                        self.rule = new_rule
                ImGui.end_combo()
            
            ImGui.separator()
            PyImGui.spacing()
            
            if ImGui.begin_child("##rules", (0, 0), border=False):
                width = PyImGui.get_content_region_avail()[0]
                
                for i, rule in enumerate(config_info.config):                    
                    if ImGui.begin_selectable(f"##rule_{i}", selected=self.rule is rule, size=(0, 35)):
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
        rule_name_input_id = f"##rule_name_{id(rule)}"
        name = ImGui.input_text(rule_name_input_id, rule.name or "")
        
        if name != rule.name:
            rule.name = name
            if self.config:
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
    
                            if self.config:
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

                            if self.config:
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
    
                            if self.config:
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
                            if self.config:
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
                            if self.config:
                                self.config.save()
                ImGui.end_child()
                
            case UpgradesRule():
                ImGui.text_wrapped("This rule matches items based on their upgrades. You can specify one or more upgrades to match against the item.")
                if self._draw_upgrades_rule(rule):
                    if self.config:
                        self.config.save()
            
            case ArmorUpgradeRule():
                ImGui.text_wrapped("This rule matches items based on their armor upgrades. You can specify one or more armor upgrades to match against the item.")
                if self._draw_armor_upgrades_rule(rule):
                    if self.config:
                        self.config.save()
            
            case MaxWeaponUpgradeRule():
                ImGui.text_wrapped("This rule matches items based on their weapon upgrades. You can specify one or more weapon upgrades to match against the item.")
                if self._draw_max_weapon_upgrades_rule(rule):
                    if self.config:
                        self.config.save()
            
            case _:
                ImGui.text("No editor available for this rule type.")
