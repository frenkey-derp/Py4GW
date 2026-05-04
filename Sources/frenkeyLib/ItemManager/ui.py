"""
Item Manager UI.

This file is intentionally large because it owns the full editor surface for:
- top-level config navigation
- rule creation / editing
- buy config editing
- upgrade-specific editors

To keep it navigable, the class is organized in broad sections:
1. setup / static formatting helpers
2. shared data caches and selector helpers
3. upgrade editors
4. item / model / weapon / material rule editors
5. window layout and config rendering
6. rule dispatch and per-rule editors
"""

import json
import inspect
import os
import re
import time
from typing import Any, Callable, Generic, NamedTuple, Optional, TypeVar

import Py4GW
import PyImGui

from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.Item import Bag, Item
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.ImGui_src.IconsFontAwesome5 import IconsFontAwesome5
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.ImGui_src.types import Alignment
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, Profession, Range
from Py4GWCoreLib.enums_src.Item_enums import DAMAGE_RANGES as ITEM_DAMAGE_RANGES, INVENTORY_BAGS, ITEM_TYPE_META_TYPES, STORAGE_BAGS, Bags, ItemAction, ItemType
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.enums_src.Texture_enums import ProfessionTextureMap, get_texture_for_model
from Py4GWCoreLib.item_mods_src.item_mod import ItemMod
from Py4GWCoreLib.item_mods_src.types import ItemUpgradeType
from Py4GWCoreLib.item_mods_src.upgrades import (
    Inscription,
    Insignia,
    RangeInstruction,
    Rune,
    _INHERENT_UPGRADES,
    AppliesToRune,
    Upgrade,
    _UPGRADES,
    UpgradeRune,
    WeaponUpgrade,
)
from Py4GWCoreLib.native_src.internals import string_table
from Py4GWCoreLib.native_src.internals.encoded_strings import GWEncoded
from Py4GWCoreLib.py4gwcorelib_src.Color import Color, ColorPalette
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.BuyConfig import BuyConfig, BuyConfigEntry
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.InventoryConfig import InventoryConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import *
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Condition import (
    ArmorUpgradesCondition,
    Condition,
    DamageRange,
    DyeColorsCondition,
    EncodedNamesCondition,
    ExactItemTypeCondition,
    InherentFilter,
    InherentFiltersCondition,
    InscribableCondition,
    ItemTypesCondition,
    MaxWeaponUpgradesCondition,
    ModelFileIdsAndItemTypesCondition,
    ModelFileIdsCondition,
    ModelIdsAndItemTypesCondition,
    ModelIdsCondition,
    RaritiesCondition,
    SalvagesToMaterialsCondition,
    UnidentifiedCondition,
    UpgradeRangesCondition,
    WeaponRequirementCondition,
)
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig
from Sources.frenkeyLib.ItemHandling.InventoryBT import InventoryBT, InventoryPreviewEntry
from Sources.frenkeyLib.ItemHandling.Items.ItemData import ITEM_DATA, ItemData, SalvageInfoCollection
from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions
from Sources.frenkeyLib.ItemManager.btrees import TraderPriceCheckManager, TraderQuote
from Sources.frenkeyLib.ItemManager.config import Config


TConfig = TypeVar("TConfig", bound=Any)


class ConfigInfo(Generic[TConfig]):
    def __init__(
        self,
        config: TConfig,
        name: str,
        description: str,
        folder_path: str,
        storage_key: str | None = None,
        tabs: list["ConfigInfo[Any]"] | None = None,
    ):
        self.config = config
        self.name = name
        self.description = description
        self.folder_path = folder_path
        self.storage_key = storage_key or self.config.__class__.__name__.lower()
        self.tabs = tabs or []
        self.selected_tab_index = 0

    @property
    def file_path(self) -> str:
        return os.path.join(self.folder_path, f"{self.storage_key}.json")

    def save(self):
        if self.tabs:
            for tab in self.tabs:
                tab.save()
            return

        if isinstance(self.config, RuleConfig):
            self.config.Save(self.file_path)
            Py4GW.Console.Log("Item Manager", f"Saved config for {self.name} to {self.file_path} with {len(self.config)} rules.", Py4GW.Console.MessageType.Info)
            return

        if isinstance(self.config, BuyConfig):
            directory = os.path.dirname(self.file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

            json_data = self.config.to_dict()

            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)

            configured_entries = sum(1 for entry in self.config.get_entries() if entry.quantity > 0)
            Py4GW.Console.Log("Item Manager", f"Saved config for {self.name} to {self.file_path} with {configured_entries} configured consumables.", Py4GW.Console.MessageType.Info)
            return

        Py4GW.Console.Log("Item Manager", f"No save handler available for {self.name}.", Py4GW.Console.MessageType.Warning)

    def load(self):
        if self.tabs:
            for tab in self.tabs:
                tab.load()
            return

        if isinstance(self.config, RuleConfig):
            loaded_config = self.config.Load(self.file_path)
            Py4GW.Console.Log("Item Manager", f"Loaded config for {self.name} from {self.file_path} with {len(loaded_config)} rules.", Py4GW.Console.MessageType.Info)
            return

        if isinstance(self.config, BuyConfig):
            if not os.path.isfile(self.file_path):
                return

            with open(self.file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            if isinstance(json_data, dict):
                self.config.load_dict(json_data)

            configured_entries = sum(1 for entry in self.config.get_entries() if entry.quantity > 0)
            Py4GW.Console.Log("Item Manager", f"Loaded config for {self.name} from {self.file_path} with {configured_entries} configured consumables.", Py4GW.Console.MessageType.Info)
            return

        Py4GW.Console.Log("Item Manager", f"No load handler available for {self.name}.", Py4GW.Console.MessageType.Warning)

class UI:
    GRAY_COLOR : Color = Color.from_tuple((0.35, 0.35, 0.35, 1.0))
    LEADING_SEARCH_AMOUNT_RE = re.compile(r"(?<!\S)(?:[1-9]|[1-9]\d|1\d\d|2[0-4]\d|250)\s+")
    INVENTORY_PREVIEW_BAGS: list[Bags] = [
        Bags.Backpack,
        Bags.BeltPouch,
        Bags.Bag1,
        Bags.Bag2,
        Bags.EquipmentPack,
        Bags.Storage1,
        Bags.Storage2,
        Bags.Storage3,
        Bags.Storage4,
        Bags.Storage5,
        Bags.Storage6,
        Bags.Storage7,
        Bags.Storage8,
        Bags.Storage9,
        Bags.Storage10,
        Bags.Storage11,
        Bags.Storage12,
        Bags.Storage13,
        Bags.Storage14,
    ]
    ITEM_TYPE_ATTRIBUTES = {
        ItemType.Axe : Attribute.AxeMastery,
        ItemType.Bow : Attribute.Marksmanship,
        ItemType.Daggers : Attribute.DaggerMastery,
        ItemType.Hammer : Attribute.HammerMastery,
        ItemType.Sword : Attribute.Swordsmanship,
        ItemType.Scythe : Attribute.ScytheMastery,
        ItemType.Spear : Attribute.SpearMastery,
        ItemType.Offhand : Attribute.None_,
        ItemType.Shield : Attribute.None_,
        ItemType.Staff : Attribute.None_,
        ItemType.Wand : Attribute.None_,
    }
    
    ITEM_TYPE_REPRESENTATIVE_MODEL_IDS = {
        ItemType.Salvage : ModelID.Ancient_Armor_Remnant,
        ItemType.Axe : ModelID.Totem_Axe,        
        ItemType.Bag : ModelID.Bag,
        ItemType.Boots : ModelID.Battle_Commendation,
        ItemType.Bow : ModelID.Bow_Grip,
        ItemType.Bundle : ModelID.War_Supplies,
        ItemType.Chestpiece : ModelID.Battle_Commendation,
        ItemType.Rune_Mod : ModelID.Sword_Hilt,
        ItemType.Usable : ModelID.Creme_Brulee,
        ItemType.Dye : ModelID.Vial_Of_Dye,
        ItemType.Materials_Zcoins : ModelID.Iron_Ingot,
        ItemType.Offhand : ModelID.Focus_Core,
        ItemType.Gloves : ModelID.Battle_Commendation,
        ItemType.Hammer : ModelID.Hammer_Haft,
        ItemType.Headpiece : ModelID.Battle_Commendation,
        ItemType.CC_Shards : ModelID.Candy_Cane_Shard,
        ItemType.Key : ModelID.Obsidian_Key,
        ItemType.Leggings : ModelID.Battle_Commendation,
        ItemType.Gold_Coin : ModelID.Gold_Coins,
        ItemType.Quest_Item : ModelID.Encrypted_Charr_Battle_Plans,
        ItemType.Wand : ModelID.WandWrapping,
        ItemType.Shield : ModelID.Shield_Handle,
        ItemType.Staff : ModelID.Staff_Head,
        ItemType.Sword : ModelID.Sword_Hilt,
        ItemType.Kit : ModelID.Salvage_Kit,
        ItemType.Trophy : ModelID.Quetzal_Crest,
        ItemType.Scroll : ModelID.Passage_Scroll_Fow,
        ItemType.Daggers : ModelID.Dagger_Handle,
        ItemType.Present : ModelID.Birthday_Present,
        ItemType.Minipet : ModelID.Water_Djinn_Mini,
        ItemType.Scythe : ModelID.Scythe_Snathe,
        ItemType.Spear : ModelID.Spearhead,
        # ItemType.Weapon : ModelID.Weapon,
        # ItemType.MartialWeapon : ModelID.MartialWeapon,
        # ItemType.OffhandOrShield : ModelID.OffhandOrShield,
        # ItemType.EquippableItem : ModelID.EquippableItem,
        # ItemType.SpellcastingWeapon : ModelID.SpellcastingWeapon,
        # ItemType.Storybook : ModelID.Book,
        # ItemType.Costume : ModelID.Costume,
        # ItemType.Costume_Headpiece : ModelID.Costume_Headpiece,
        # ItemType.Unknown : ModelID.Unknown
    }
    
    UpgradeTexture = NamedTuple("UpgradeTextures", [("prefix", str), ("suffix", str)])

    # -------------------------------------------------------------------------
    # Construction / state
    # -------------------------------------------------------------------------
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
                toggle_default=False,
                draw_callback=self.draw_main_window,
            )

        self.show_preview_window: bool = False
        folder_path = os.path.join(Py4GW.Console.get_projects_path(), "Settings", "Global", "Item & Inventory", "Configs")

        self.configs : list[ConfigInfo] = [
            ConfigInfo(BuyConfig(), "Kits, Keys & Lockpicks", "Configure how many kits, keys and lockpicks to keep in stock", folder_path),
            ConfigInfo(LootConfig(), "Looting", "Configure which items to pick up and which to ignore", folder_path),
            ConfigInfo(InventoryConfig(), "Item Processing", "Configure how to process items (Stash, Salvage, Extract Upgrades, Sell, ...)", folder_path),
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
        self.max_weapon_upgrade_search: str = ""
        self.upgrade_range_search: str = ""
        self.model_id_search: str = ""
        self.model_file_id_search: str = ""
        self.encoded_name_search: str = ""
        self.material_search: str = ""
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

        self.dye_textures: dict[int, str] = {
            DyeColor.NoColor: os.path.join(self.texture_path, "Dyes", "Gray.png"),
            DyeColor.Blue: os.path.join(self.texture_path, "Dyes", "Blue.png"),
            DyeColor.Green: os.path.join(self.texture_path, "Dyes", "Green.png"),
            DyeColor.Purple: os.path.join(self.texture_path, "Dyes", "Purple.png"),
            DyeColor.Red: os.path.join(self.texture_path, "Dyes", "Red.png"),
            DyeColor.Yellow: os.path.join(self.texture_path, "Dyes", "Yellow.png"),
            DyeColor.Brown: os.path.join(self.texture_path, "Dyes", "Brown.png"),
            DyeColor.Orange: os.path.join(self.texture_path, "Dyes", "Orange.png"),
            DyeColor.Silver: os.path.join(self.texture_path, "Dyes", "Silver.png"),
            DyeColor.Black: os.path.join(self.texture_path, "Dyes", "Black.png"),
            DyeColor.Gray: os.path.join(self.texture_path, "Dyes", "Gray.png"),
            DyeColor.White: os.path.join(self.texture_path, "Dyes", "White.png"),
            DyeColor.Pink: os.path.join(self.texture_path, "Dyes", "Pink.png"),
        }

        self._all_item_data_cache: list[ItemData] = []
        self._item_by_model_file_id: dict[int, ItemData] = {}
        self._item_by_encoded_name: dict[bytes, ItemData] = {}
        self._unique_encoded_name_items: list[ItemData] = []
        self._unique_model_file_id_items: list[ItemData] = []
        self._salvage_material_options: list[ItemData] = []
        self.inherent_upgrade_search: str = ""
        self.inventory_preview_search: str = ""
        self.inventory_preview_show_no_action: bool = False
        self.inventory_preview_show_hold: bool = False
        self.inventory_preview_selected_bags: list[Bags] = [
            Bags.Backpack,
            Bags.BeltPouch,
            Bags.Bag1,
            Bags.Bag2,
        ]
        self.loot_preview_search: str = ""
        self.loot_preview_show_no_action: bool = False
        self.loot_preview_distance: int = int(Range.SafeCompass.value)
        self.buy_preview_search: str = ""
        self.buy_preview_show_satisfied: bool = True
        self._rebuild_item_ui_caches()

    # -------------------------------------------------------------------------
    # General formatting / discovery helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def format_currency(value: int) -> str:
        plat, gold = GWEncoded._formatted_currency_amount_bytes(value)

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
    def _get_rule_types() -> list[type[Rule]]:
        discovered_rule_types: list[type[Rule]] = []

        def visit(rule_type: type[Rule]) -> None:
            for child_rule_type in rule_type.__subclasses__():
                if child_rule_type not in discovered_rule_types:
                    discovered_rule_types.append(child_rule_type)
                visit(child_rule_type)

        visit(Rule)
        types = [
            rule_type
            for rule_type in discovered_rule_types
            if getattr(rule_type, "ui_selectable", True)
        ]
        return sorted(types, key=lambda t: t.__name__)

    @staticmethod
    def _get_condition_types() -> list[type[Condition]]:
        discovered_condition_types: list[type[Condition]] = []

        def visit(condition_type: type[Condition]) -> None:
            for child_condition_type in condition_type.__subclasses__():
                if child_condition_type not in discovered_condition_types:
                    discovered_condition_types.append(child_condition_type)
                visit(child_condition_type)

        visit(Condition)
        types = [
            condition_type
            for condition_type in discovered_condition_types
            if getattr(condition_type, "ui_selectable", True)
            and condition_type is not Condition
            and not inspect.isabstract(condition_type)
        ]
        return sorted(types, key=lambda t: t.__name__)

    @staticmethod
    def _humanize_name(value: str) -> str:
        return Utils.humanize_string(value.replace("NONE", "None").replace("None_", "None").replace("_None", "None")).replace("  ", " ").strip()

    @staticmethod
    def _normalize_search_query(value: str) -> str:
        return UI.LEADING_SEARCH_AMOUNT_RE.sub("", value.strip(), count=1).lower()

    @staticmethod
    def _normalize_searchable_text(value: str) -> str:
        return UI.LEADING_SEARCH_AMOUNT_RE.sub("", value.strip()).lower()

    @staticmethod
    def _singularize_search_query(value: str) -> str:
        return re.sub(r"\b([a-zA-Z]{4,})s\b", r"\1", value)

    @staticmethod
    def _search_text_matches(search_query: str, *values: Any) -> bool:
        if not search_query:
            return True

        raw_text = " ".join(str(value) for value in values if value is not None).lower()
        searchable_text = UI._normalize_searchable_text(raw_text)
        if search_query in raw_text or search_query in searchable_text:
            return True

        singular_query = UI._singularize_search_query(search_query)
        return singular_query != search_query and singular_query in searchable_text

    @staticmethod
    def _format_rule_type_tooltip(rule_type: type) -> str:
        title = UI._humanize_name(rule_type.__name__)
        doc = inspect.getdoc(rule_type) or ""
        doc = re.sub(r":class:`([^`]+)`", r"\1", doc)
        doc = doc.replace("**", "")
        doc = doc.replace("\n", "\n\n").strip()
        inversion_note = "Enable Inverted on a rule to apply it to items that do not match the configured criteria."
        return f"{title}\n\n{doc}\n\n{inversion_note}" if doc else f"{title}\n\n{inversion_note}"

    @staticmethod
    def _format_condition_type_tooltip(condition_type: type) -> str:
        title = UI._humanize_name(condition_type.__name__)
        doc = inspect.getdoc(condition_type) or ""
        doc = re.sub(r":class:`([^`]+)`", r"\1", doc)
        doc = doc.replace("**", "")
        doc = doc.replace("\n", "\n\n").strip()
        return f"{title}\n\n{doc}" if doc else title

    @staticmethod
    def _show_wrapped_tooltip(text: str, wrap_width: float = 420.0) -> None:
        if not PyImGui.is_item_hovered():
            return

        PyImGui.begin_tooltip()
        PyImGui.push_text_wrap_pos(PyImGui.get_cursor_pos_x() + wrap_width)
        PyImGui.text_wrapped(text)
        PyImGui.pop_text_wrap_pos()
        PyImGui.end_tooltip()

    def _format_upgrade_type_label(self, upgrade_type: type[Upgrade]) -> str:
        type_name = upgrade_type.__name__.replace("Upgrade", "")
        return self._humanize_name(type_name)

    def _format_upgrade_label(self, upgrade: Upgrade) -> str:
        name = upgrade.name_plain if getattr(upgrade, "name_plain", "") else ""
        return name or self._format_upgrade_type_label(type(upgrade))

    @staticmethod
    def _get_all_item_data() -> list[ItemData]:
        return [item for sublist in ITEM_DATA.data.values() for item in sublist.values()]

    @staticmethod
    def _get_item_display_name(item: Any) -> str:
        return item.name or f"Model {item.model_id}"

    @staticmethod
    def _get_item_encoded_name_string(item: Any) -> str:
        if getattr(item, "name_encoded", bytes()):
            return ", ".join(f"0x{byte:X}" for byte in item.name_encoded)
        return ""

    @staticmethod
    def _draw_item_texture(item: Optional[ItemData], size: tuple[float, float] = (32, 32)) -> None:
        # UI._draw_texture_from_model_file_id(getattr(item, "model_file_id", -1), size)
        texture = get_texture_for_model(item.model_id) if item and getattr(item, "model_id", -1) > 0 else None
        if texture and "0-File_Not_found.png" in texture:
            texture = None

        UI._draw_texture_or_dummy(texture, size)

    def _rebuild_item_ui_caches(self) -> None:
        all_items = self._get_all_item_data()
        self._all_item_data_cache = all_items

        self._item_by_model_file_id = {}
        self._item_by_encoded_name = {}
        encoded_name_items: dict[tuple[ItemType, str], ItemData] = {}
        model_file_id_items: dict[tuple[ItemType, int], ItemData] = {}
        salvage_materials: list[ItemData] = []
        for item in all_items:
            model_id = int(getattr(item, "model_id", -1))
            item_type = getattr(item, "item_type", ItemType.Unknown)
            model_file_id = int(getattr(item, "model_file_id", -1))
            encoded_name = self._get_item_encoded_name_string(item)

            if model_file_id > 0 and model_file_id not in self._item_by_model_file_id:
                self._item_by_model_file_id[model_file_id] = item

            if item.name_encoded and item.name_encoded not in self._item_by_encoded_name:
                self._item_by_encoded_name[item.name_encoded] = item

            if encoded_name:
                encoded_name_items.setdefault((item_type, encoded_name), item)

            if model_file_id > 0:
                model_file_id_items.setdefault((item_type, model_file_id), item)

            if item.category == "Material":
                salvage_materials.append(item)

        sort_key = lambda item: (self._get_item_display_name(item), self._humanize_name(item.item_type.name), int(getattr(item, "model_id", -1)))
        self._unique_encoded_name_items = sorted(encoded_name_items.values(), key=sort_key)
        self._unique_model_file_id_items = sorted(model_file_id_items.values(), key=sort_key)
        self._salvage_material_options = sorted(salvage_materials, key=lambda material: material.name)

    def _find_item_by_model_file_id(self, model_file_id: int) -> ItemData | None:
        return self._item_by_model_file_id.get(model_file_id)

    def _find_item_by_encoded_name(self, encoded_name: bytes) -> ItemData | None:
        return self._item_by_encoded_name.get(encoded_name)

    def _format_weapon_value_range(self, item_type: Optional[ItemType], requirement: int) -> str:
        value_range = self._get_default_weapon_value_range(item_type, requirement)
        if value_range is None:
            return ""

        min_value, max_value = value_range
        value = f"{min_value}-{max_value}" if min_value != max_value else f"{min_value}"
        if item_type == ItemType.Shield:
            return f"Armor: {value}"

        if item_type == ItemType.Offhand:
            return f"Energy: {value}"

        return f"Damage: {value}"

    @staticmethod
    def _get_default_weapon_value_range(item_type: Optional[ItemType], requirement: int) -> Optional[tuple[int, int]]:
        if item_type is None:
            return None

        return ITEM_DAMAGE_RANGES.get(item_type, {}).get(min(requirement, 9))

    @staticmethod
    def _draw_texture_from_model_file_id(model_file_id: int, size: tuple[float, float]) -> None:
        model_file_id = Item.GetTrueModelFileID(model_file_id)
        model_file_texture : Optional[str] = f"gwdat://{int(model_file_id)}" if int(model_file_id or 0) > 0 else None
        UI._draw_texture_or_dummy(model_file_texture, size)

    @staticmethod
    def _draw_texture_or_dummy(texture: Optional[str], size: tuple[float, float]) -> None:
        if texture is not None:
            ImGui.image(texture, size)
        else:
            ImGui.dummy(*size)

    @staticmethod
    def _get_rarity_color(rarity) -> Color:
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

    # -------------------------------------------------------------------------
    # Upgrade editor helpers
    # -------------------------------------------------------------------------
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

    def _get_range_instructions(self, upgrade: Upgrade) -> list[RangeInstruction]:
        return [instruction for instruction in type(upgrade).upgrade_info if isinstance(instruction, RangeInstruction)]

    def _get_range_instruction(self, upgrade: Upgrade, target: str) -> RangeInstruction | None:
        return next((instruction for instruction in self._get_range_instructions(upgrade) if instruction.target == target), None)

    def _get_range_upgrade_options(self) -> list[tuple[type[WeaponUpgrade | Inscription], RangeInstruction]]:
        options: list[tuple[type[WeaponUpgrade | Inscription], RangeInstruction]] = []
        for upgrade_type in self.available_upgrade_types:
            if not issubclass(upgrade_type, (WeaponUpgrade, Inscription)):
                continue

            range_instructions = [instruction for instruction in upgrade_type.upgrade_info if isinstance(instruction, RangeInstruction)]
            for instruction in range_instructions:
                options.append((upgrade_type, instruction))

        return sorted(
            options,
            key=lambda option: (
                self._format_upgrade_type_label(option[0]),
                self._humanize_name(option[1].target),
            ),
        )

    def _convert_str_to_encoded_bytes(self, text: str) -> bytes:
        try:
            return bytes(int(x, 16) for x in text.replace(",", " ").split())
        except ValueError:
            return text.encode("utf-8")
        
    def draw_main_window(self) -> None:
        expanded, open_ = ImGui.BeginWithClose(
            ini_key=self.module_config.main_ini_key,
            name="Item Manager",
            p_open=self.floating_button.visible,
            flags=PyImGui.WindowFlags.NoFlag,
        )
        self.floating_button.sync_begin_with_close(open_)

        if expanded:
            self.draw_explorer()
            
            if self.show_preview_window and self.config is not None:
                self.draw_preview_window(self.config)
                
        ImGui.End(self.module_config.main_ini_key)
        
    def draw(self):
        self.floating_button.draw(self.module_config.floating_ini_key)

    def _get_active_config_info(self, config_info: ConfigInfo | None = None) -> ConfigInfo | None:
        return config_info or self.config

    def _sync_selected_rule(self) -> None:
        active_config = self._get_active_config_info()
        if active_config is None or not isinstance(active_config.config, RuleConfig):
            self.rule = None
            return

        if self.rule not in active_config.config:
            self.rule = active_config.config[0] if len(active_config.config) > 0 else None

    def _save_active_config(self) -> None:
        active_config = self._get_active_config_info()
        if active_config is not None:
            active_config.save()

    def _load_active_config(self) -> None:
        active_config = self._get_active_config_info()
        if active_config is not None:
            active_config.load()
            self._sync_selected_rule()

    def switch_to_config(self, rule_config: ConfigInfo | None):
        self.config = rule_config or (self.configs[0] if len(self.configs) > 0 else None)
        self._sync_selected_rule()

    def draw_preview_window(self, config_info: ConfigInfo):          
        expanded, open_ = ImGui.BeginWithClose(
            ini_key=self.module_config.main_ini_key,
            name="Item Manager - Preview",
            p_open=self.show_preview_window,
            flags=PyImGui.WindowFlags.NoFlag,
        )
        
        match config_info.config:
            case InventoryConfig():
                self.draw_inventory_config_preview(config_info.config)
            
            case LootConfig():
                self.draw_loot_config_preview(config_info.config)
            
            case BuyConfig():
                self.draw_buy_config_preview(config_info.config)
                
        ImGui.End(self.module_config.main_ini_key)
        
        if not open_:
            self.show_preview_window = False
    
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
                        ImGui.text_colored(config.config.__class__.__name__, UI.GRAY_COLOR.color_tuple, font_size=12)

                    if ImGui.end_selectable():
                        self.switch_to_config(config)

                    ImGui.show_tooltip(config.description)

            ImGui.end_child()

            PyImGui.table_next_column()

            if ImGui.begin_child("##content", (0, 0), border=False):
                if self.config:
                    active_config = self._get_active_config_info(self.config)
                    active_config_name = active_config.name if active_config is not None and active_config is not self.config else None
                    title = self.config.name if active_config_name is None else f"{self.config.name} / {active_config_name}"

                    if ImGui.begin_table("##config_header", 4, PyImGui.TableFlags.NoBordersInBody, height=20):
                        PyImGui.table_setup_column("Title", PyImGui.TableColumnFlags.WidthStretch)
                        PyImGui.table_setup_column("Preview", PyImGui.TableColumnFlags.WidthFixed, 100)
                        PyImGui.table_setup_column("Export", PyImGui.TableColumnFlags.WidthFixed, 100)
                        PyImGui.table_setup_column("Import", PyImGui.TableColumnFlags.WidthFixed, 100)

                        PyImGui.table_next_row()
                        PyImGui.table_next_column()

                        ImGui.text(title, font_size=18)
                        PyImGui.table_next_column()
                        if ImGui.button("Preview##preview_config", -1):
                            self.show_preview_window = not self.show_preview_window
                        
                        PyImGui.table_next_column()
                        if ImGui.button("Export##export_config", -1):
                            self._save_active_config()

                        PyImGui.table_next_column()
                        if ImGui.button("Import##import_config", -1):
                            self._load_active_config()
                        if active_config is not None:
                            ImGui.show_tooltip(f"Import {active_config.name} config from {active_config.file_path}")
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

            if ImGui.menu_item("Move Up"):
                index = config_info.config.index(rule)
                if index > 0:
                    config_info.config.remove(rule)
                    config_info.config.insert(index - 1, rule)
                config_info.save()
                self.rule = None

            if ImGui.menu_item("Move Down"):
                index = config_info.config.index(rule)
                if index < len(config_info.config) - 1:
                    config_info.config.remove(rule)
                    config_info.config.insert(index + 1, rule)
                config_info.save()
                self.rule = None

            ImGui.separator()

            if ImGui.menu_item("Delete Rule"):
                config_info.config.remove(rule)
                config_info.save()
                self.rule = None

            ImGui.end_popup()
            return True

        return False

    def draw_config(self, config_info: ConfigInfo):
        if isinstance(config_info.config, RuleConfig):
            self.draw_rule_config(config_info)
            return

        if isinstance(config_info.config, BuyConfig):
            self.draw_buy_config(config_info)
            return

        ImGui.text("No editor available for this config.")

    def draw_buy_config(self, config_info: ConfigInfo[BuyConfig]) -> None:
        changed = False
        entries = config_info.config.get_entries()

        ImGui.text_wrapped("Configure how many common consumables should be kept in stock.")
        ImGui.separator()

        for index, entry in enumerate(entries):
            item_data = None
            if entry.model_id is not None and entry.item_type is not None:
                model_id_value = int(entry.model_id.value) if isinstance(entry.model_id, ModelID) else int(entry.model_id)
                item_data = ITEM_DATA.get_item_data(item_type=entry.item_type, model_id=model_id_value)

            unique_id = f"buy_config_{entry.key}_{index}"
            if ImGui.begin_child(f"##{unique_id}", (0, 64), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                PyImGui.columns(2, "##buy_config_columns", False)
                if item_data is not None:
                    self._draw_item_texture(item_data, (40, 40))
                else:
                    ImGui.dummy(40, 40)

                PyImGui.same_line(0, 10)
                PyImGui.begin_group()
                ImGui.text(entry.label)
                x, y = PyImGui.get_cursor_pos()
                PyImGui.set_cursor_pos(x, y - 4)
                helper_text = entry.description or "Target quantity to keep in inventory."
                ImGui.text_colored(helper_text, UI.GRAY_COLOR.color_tuple, font_size=12)
                PyImGui.end_group()

                PyImGui.next_column()
                PyImGui.set_next_item_width(-1)
                quantity = ImGui.slider_int(f"##Quantity{unique_id}", v=entry.quantity, v_min=0, v_max=500 if entry.model_id == ModelID.Lockpick else 50)
                if quantity != entry.quantity:
                    setattr(config_info.config, entry.key, max(0, int(quantity)))
                    changed = True
                PyImGui.end_columns()
            ImGui.end_child()

        if changed:
            config_info.save()

    def draw_rule_config(self, config_info: ConfigInfo[RuleConfig]):
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
                    if ImGui.selectable(UI._humanize_name(rule_type.__name__), False):
                        new_rule = rule_type()
                        config_info.config.AddRule(new_rule)
                        config_info.save()
                        self.rule = new_rule
                    self._show_wrapped_tooltip(self._format_rule_type_tooltip(rule_type))
                ImGui.end_combo()

            ImGui.separator()
            PyImGui.spacing()

            item_height = 50
            if ImGui.begin_child("##rules", (0, 0), border=False):
                for i, rule in enumerate(config_info.config):
                    if PyImGui.is_rect_visible(5, item_height):
                        if ImGui.begin_selectable(f"##rule_{i}", selected=self.rule is rule, size=(0, item_height)):
                            ImGui.text(rule.name or f"{rule.__class__.__name__} #{i}")
                            PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)
                            PyImGui.separator()
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 2)
                            ImGui.text(f"{UI._humanize_name(rule.action.name)}", font_size=13)
                            PyImGui.set_cursor_pos(x, PyImGui.get_cursor_pos_y() - 5)
                            ImGui.text_colored(f"{rule.__class__.__name__}", UI.GRAY_COLOR.color_tuple, font_size=11)

                        if ImGui.end_selectable():
                            self.rule = rule

                        if PyImGui.is_item_hovered() and PyImGui.is_mouse_clicked(1):
                            self.context_menu_id = f"{rule.__class__.__name__} #{i}"
                            self.context_menu_rule = rule
                            self.context_menu_config = config_info
                            PyImGui.open_popup(self.context_menu_id)

                        self._show_wrapped_tooltip(self._format_rule_type_tooltip(rule.__class__))
                    else:
                        PyImGui.dummy(0, item_height)

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
                
            ImGui.end_child()

            ImGui.end_table()

    def _set_inventory_preview_bags(self, bags: list[Bags]) -> None:
        self.inventory_preview_selected_bags = list(bags)

    @staticmethod
    def _get_first_matching_rule(config: RuleConfig, item_id: int) -> Rule | None:
        if item_id in config.blacklisted_items:
            return None

        for rule in config:
            if rule.applies(item_id):
                return rule

        return None

    @staticmethod
    def _is_valid_loot_agent(agent_id: int) -> bool:
        if not Agent.IsValid(agent_id):
            return False

        player_agent_id = Player.GetAgentID()
        owner_id = Agent.GetItemAgentOwnerID(agent_id)
        return owner_id in (0, player_agent_id)

    @staticmethod
    def _get_buy_entry_inventory_quantity(entry: BuyConfigEntry) -> int:
        inventory_snapshot = ItemSnapshot.get_bags_snapshot([Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2, Bags.EquipmentPack])
        total_quantity = 0

        for bag_items in inventory_snapshot.values():
            for item in bag_items.values():
                if item is None or not item.is_valid or not item.is_inventory_item:
                    continue

                if entry.model_id is not None:
                    model_id_value = int(entry.model_id.value) if isinstance(entry.model_id, ModelID) else int(entry.model_id)
                    if item.model_id != model_id_value:
                        continue
                elif entry.item_type is not None and item.item_type != entry.item_type:
                    continue

                if entry.key == "keys" and item.model_id == int(ModelID.Lockpick.value):
                    continue

                total_quantity += item.quantity if item.is_stackable else 1

        return total_quantity

    def draw_inventory_config_preview(self, config: InventoryConfig) -> None:
        try:
            ImGui.text("Preview", font_size=18)
            ImGui.text_wrapped("Preview how the current Item Processing config would classify items in the selected bags. This does not execute any actions. InventoryBT itself still only processes live inventory bags.")
        
            preview_entries = InventoryBT.Preview(config, bags=self.inventory_preview_selected_bags)
            action_counts: dict[ItemAction, int] = {}
            visible_entries : list[InventoryPreviewEntry] = []
        
            button_width = 110
            if ImGui.button("Inventory", button_width):
                self._set_inventory_preview_bags(INVENTORY_BAGS)
            PyImGui.same_line(0, 5)
            if ImGui.button("Storage", button_width):
                self._set_inventory_preview_bags(STORAGE_BAGS)
            PyImGui.same_line(0, 5)
            if ImGui.button("All", button_width):
                self._set_inventory_preview_bags(list(self.INVENTORY_PREVIEW_BAGS))
            PyImGui.same_line(0, 5)
            if ImGui.button("Clear", button_width):
                self._set_inventory_preview_bags([])

            self.inventory_preview_search = ImGui.input_text("Search##inventory_preview_search", self.inventory_preview_search)
            self.inventory_preview_show_no_action = ImGui.checkbox("Show No Action", self.inventory_preview_show_no_action)
            self.inventory_preview_show_hold = ImGui.checkbox("Show Hold", self.inventory_preview_show_hold)

            if ImGui.begin_child("##inventory_preview_bags", (0, 90), border=True):
                width = PyImGui.get_content_region_avail()[0]
                columns = max(1, int(width // 170))
                PyImGui.columns(columns, "inventory_preview_bag_columns", False)

                for bag in self.INVENTORY_PREVIEW_BAGS:
                    is_selected = bag in self.inventory_preview_selected_bags
                    selected = ImGui.checkbox(f"{self._humanize_name(bag.name)}", is_selected)
                    if selected != is_selected:
                        if selected:
                            self.inventory_preview_selected_bags.append(bag)
                        else:
                            self.inventory_preview_selected_bags = [selected_bag for selected_bag in self.inventory_preview_selected_bags if selected_bag != bag]
                    PyImGui.next_column()

                PyImGui.end_columns()
            ImGui.end_child()

            for entry in preview_entries:
                action = entry.action
                if action is None and not self.inventory_preview_show_no_action:
                    continue
                if action == ItemAction.Hold and not self.inventory_preview_show_hold:
                    continue

                search_blob = " ".join(
                    [
                        entry.item.names.plain or entry.item.name or "",
                        entry.rule.name if entry.rule and entry.rule.name else entry.rule.__class__.__name__ if entry.rule else "",
                        entry.note,
                        entry.item.bag.name,
                        action.name if action else "No Action",
                    ]
                )
                if not self._search_text_matches(self._normalize_search_query(self.inventory_preview_search), search_blob):
                    continue

                if action is not None:
                    action_counts[action] = action_counts.get(action, 0) + 1

                visible_entries.append(entry)

            summary_text = ", ".join(
                f"{self._humanize_name(action.name)}: {count}"
                for action, count in sorted(action_counts.items(), key=lambda item: item[0].name)
            )
            ImGui.text_wrapped(summary_text if summary_text else "No matching preview entries for the current filters.")

            if not self.inventory_preview_selected_bags:
                ImGui.text_wrapped("Select at least one bag to preview items.")
                return

            if not visible_entries:
                return

            if ImGui.begin_table("##inventory_preview_table", 6, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable | PyImGui.TableFlags.ScrollY, height=280):
                PyImGui.table_setup_column("Bag", PyImGui.TableColumnFlags.WidthFixed, 110)
                PyImGui.table_setup_column("Slot", PyImGui.TableColumnFlags.WidthFixed, 45)
                PyImGui.table_setup_column("Item", PyImGui.TableColumnFlags.WidthStretch)
                PyImGui.table_setup_column("Action", PyImGui.TableColumnFlags.WidthFixed, 120)
                PyImGui.table_setup_column("Rule", PyImGui.TableColumnFlags.WidthFixed, 160)
                PyImGui.table_setup_column("Notes", PyImGui.TableColumnFlags.WidthStretch)
                PyImGui.table_headers_row()

                for entry in visible_entries:
                    rule_name = entry.rule.name if entry.rule and entry.rule.name else entry.rule.__class__.__name__ if entry.rule else "-"
                    action_name = self._humanize_name(entry.action.name) if entry.action is not None else "No Action"
                    item_name = entry.item.complete_name or entry.item.singular_name or entry.item.name or f"Item {entry.item.id}"

                    PyImGui.table_next_row()
                    PyImGui.table_next_column()
                    ImGui.text(self._humanize_name(entry.item.bag.name))
                    PyImGui.table_next_column()
                    ImGui.text(str(entry.item.slot))
                    PyImGui.table_next_column()
                    ImGui.text(item_name, render_markdown=True)
                    PyImGui.table_next_column()
                    ImGui.text(action_name)
                    PyImGui.table_next_column()
                    ImGui.text(rule_name)
                    PyImGui.table_next_column()
                    ImGui.text_wrapped(entry.note if entry.note else ("Ready" if entry.executable else "-"))

                ImGui.end_table()
        except Exception as e:
            ImGui.text_wrapped(f"Error generating inventory preview: {str(e)}")

    def draw_loot_config_preview(self, config: LootConfig) -> None:
        ImGui.text("Preview", font_size=18)
        ImGui.text_wrapped("Preview how the current loot config would classify nearby ground items. This does not pick up anything.")

        self.loot_preview_search = ImGui.input_text("Search##loot_preview_search", self.loot_preview_search)
        self.loot_preview_show_no_action = ImGui.checkbox("Show No Action", self.loot_preview_show_no_action)
        self.loot_preview_distance = ImGui.slider_int(
            "Distance##loot_preview_distance",
            self.loot_preview_distance,
            0,
            int(Range.SafeCompass.value),
        )

        if not Player.GetAgentID():
            ImGui.text_wrapped("Loot preview is only available while the player is in-game.")
            return

        item_array = AgentArray.GetItemArray() or []
        item_array = AgentArray.Filter.ByDistance(item_array, Player.GetXY(), self.loot_preview_distance)
        item_array = AgentArray.Sort.ByDistance(item_array, Player.GetXY())

        visible_entries: list[tuple[ItemSnapshot, Rule | None, ItemAction | None, str, float]] = []
        action_counts: dict[str, int] = {}
        player_pos = Player.GetXY()

        for agent_id in item_array:
            if not self._is_valid_loot_agent(agent_id):
                continue

            item_agent = Agent.GetItemAgentByID(agent_id)
            if item_agent is None:
                continue

            item = ItemSnapshot.from_item_id(item_agent.item_id)
            if item is None or not item.is_valid:
                continue

            rule = self._get_first_matching_rule(config, item.id)
            action = rule.action if rule is not None else None
            note = ""

            if action in (ItemAction.NONE, ItemAction.Hold):
                note = "No loot action will be executed."
            elif action is None:
                note = "No matching rule."

            item_name = item.names.plain or item.name or f"Item {item.id}"
            distance = Utils.Distance(player_pos, Agent.GetXY(agent_id))
            action_name = self._humanize_name(action.name) if action is not None else "No Action"
            rule_name = rule.name if rule and rule.name else rule.__class__.__name__ if rule else ""
            search_blob = " ".join([item_name, action_name, rule_name, note])

            if not self.loot_preview_show_no_action and action is None:
                continue

            if not self._search_text_matches(self._normalize_search_query(self.loot_preview_search), search_blob):
                continue

            if action is not None:
                action_counts[action_name] = action_counts.get(action_name, 0) + 1

            visible_entries.append((item, rule, action, note, distance))

        summary_text = ", ".join(f"{action}: {count}" for action, count in sorted(action_counts.items()))
        ImGui.text_wrapped(summary_text if summary_text else "No matching preview entries for the current filters.")

        if not visible_entries:
            ImGui.text_wrapped("No nearby loot entries matched the current preview filters.")
            return

        if ImGui.begin_table("##loot_preview_table", 5, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable | PyImGui.TableFlags.ScrollY, height=320):
            PyImGui.table_setup_column("Distance", PyImGui.TableColumnFlags.WidthFixed, 70)
            PyImGui.table_setup_column("Item", PyImGui.TableColumnFlags.WidthStretch)
            PyImGui.table_setup_column("Action", PyImGui.TableColumnFlags.WidthFixed, 120)
            PyImGui.table_setup_column("Rule", PyImGui.TableColumnFlags.WidthFixed, 180)
            PyImGui.table_setup_column("Notes", PyImGui.TableColumnFlags.WidthStretch)
            PyImGui.table_headers_row()

            for item, rule, action, note, distance in visible_entries:
                item_name = item.names.plain or item.name or f"Item {item.id}"
                action_name = self._humanize_name(action.name) if action is not None else "No Action"
                rule_name = rule.name if rule and rule.name else rule.__class__.__name__ if rule else "-"

                PyImGui.table_next_row()
                PyImGui.table_next_column()
                ImGui.text(str(distance))
                PyImGui.table_next_column()
                ImGui.text(item_name)
                PyImGui.table_next_column()
                ImGui.text(action_name)
                PyImGui.table_next_column()
                ImGui.text(rule_name)
                PyImGui.table_next_column()
                ImGui.text_wrapped(note if note else "Ready")

            ImGui.end_table()
    
    def draw_buy_config_preview(self, config: BuyConfig) -> None:
        ImGui.text("Preview", font_size=18)
        ImGui.text_wrapped("Preview the current inventory stock against your configured target amounts. This does not buy anything.")

        self.buy_preview_search = ImGui.input_text("Search##buy_preview_search", self.buy_preview_search)
        self.buy_preview_show_satisfied = ImGui.checkbox("Show Satisfied", self.buy_preview_show_satisfied)

        entries = config.get_entries()
        if not entries:
            ImGui.text("No buy rules configured.")
            return

        visible_entries: list[tuple[BuyConfigEntry, int, int]] = []

        for entry in entries:
            current_quantity = self._get_buy_entry_inventory_quantity(entry)
            missing_quantity = max(0, entry.quantity - current_quantity)
            search_blob = " ".join([entry.label, entry.description, str(entry.quantity), str(current_quantity), str(missing_quantity)])

            if not self.buy_preview_show_satisfied and missing_quantity <= 0:
                continue

            if not self._search_text_matches(self._normalize_search_query(self.buy_preview_search), search_blob):
                continue

            visible_entries.append((entry, current_quantity, missing_quantity))

        configured_total = sum(1 for entry in entries if entry.quantity > 0)
        pending_total = sum(1 for _, _, missing_quantity in visible_entries if missing_quantity > 0)
        ImGui.text_wrapped(f"Configured entries: {configured_total}, still below target: {pending_total}")

        if not visible_entries:
            ImGui.text_wrapped("No buy entries matched the current preview filters.")
            return

        if ImGui.begin_table("##buy_preview_table", 5, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable | PyImGui.TableFlags.ScrollY, height=280):
            PyImGui.table_setup_column("Item", PyImGui.TableColumnFlags.WidthStretch)
            PyImGui.table_setup_column("Target", PyImGui.TableColumnFlags.WidthFixed, 70)
            PyImGui.table_setup_column("Current", PyImGui.TableColumnFlags.WidthFixed, 70)
            PyImGui.table_setup_column("Missing", PyImGui.TableColumnFlags.WidthFixed, 70)
            PyImGui.table_setup_column("Notes", PyImGui.TableColumnFlags.WidthStretch)
            PyImGui.table_headers_row()

            for entry, current_quantity, missing_quantity in visible_entries:
                note = "Ready" if missing_quantity <= 0 else f"Needs {missing_quantity} more."

                PyImGui.table_next_row()
                PyImGui.table_next_column()
                ImGui.text(entry.label)
                PyImGui.table_next_column()
                ImGui.text(str(entry.quantity))
                PyImGui.table_next_column()
                ImGui.text(str(current_quantity))
                PyImGui.table_next_column()
                ImGui.text(str(missing_quantity))
                PyImGui.table_next_column()
                ImGui.text_wrapped(note if entry.description == "" else f"{note} {entry.description}")

            ImGui.end_table()

    # -------------------------------------------------------------------------
    # Rule rendering / dispatch
    # -------------------------------------------------------------------------
    def _draw_rule_header(self, rule: Rule) -> None:
        ImGui.text_aligned("Name", alignment=Alignment.MidLeft, height=25)
        PyImGui.same_line(0, 5)

        width = PyImGui.get_content_region_avail()[0]
        PyImGui.set_next_item_width(width - 155 - 155)
        rule_name_input_id = f"##rule_name_{id(rule)}"
        name = ImGui.input_text(rule_name_input_id, rule.name or "")
        if name != rule.name:
            rule.name = name
            self._save_active_config()


        PyImGui.same_line(0, 5)
        PyImGui.set_next_item_width(150)

        style = ImGui.get_style()
        unset = rule.action == ItemAction.NONE
        if unset:
            style.FrameBg.push_color_direct((229, 62, 48, 200))
            style.FrameBgHovered.push_color_direct((231, 95, 81, 200))

        open = PyImGui.begin_combo(f"##rule_action_{id(rule)}", UI._humanize_name(rule.action.name)  if rule.action != ItemAction.NONE else "Select an action", PyImGui.ImGuiComboFlags.NoFlag)

        if unset:
            style.FrameBg.pop_color_direct()
            style.FrameBgHovered.pop_color_direct()

        if open:
            sorted_actions = sorted(ItemAction, key=lambda action: action.name)
            for action in sorted_actions:
                if ImGui.selectable(UI._humanize_name(action.name), selected=rule.action == action):
                    rule.action = action
                    self._save_active_config()
            ImGui.end_combo()
        ImGui.show_tooltip("The action to perform on items that match this rule.")

        PyImGui.same_line(0, 5)
        PyImGui.set_next_item_width(150)
        if PyImGui.begin_combo(
            f"##rule_result_interpretation_{id(rule)}",
            self._humanize_name(rule.result_interpretation.name),
            PyImGui.ImGuiComboFlags.NoFlag,
        ):
            interpretations = {
                ResultInterpretation.Match: "Handle items that match the specified conditions.",
                ResultInterpretation.NoMatch: "Handle items that do not match the specified conditions.",
            }

            for interpretation, description in interpretations.items():
                if ImGui.selectable(interpretation.name, selected=rule.result_interpretation == interpretation):
                    rule.result_interpretation = interpretation
                    self._save_active_config()
                ImGui.show_tooltip(description)

            ImGui.end_combo()
        ImGui.show_tooltip("Controls whether the rule handles matching items or non-matching items.")


        ImGui.separator()
        PyImGui.spacing()

    def _get_condition_requirement_item_types(self, rule: Rule) -> list[ItemType]:
        exact_type_condition = next((condition for condition in rule.conditions if isinstance(condition, ExactItemTypeCondition)), None)
        if exact_type_condition is not None and exact_type_condition.item_type is not None:
            return [exact_type_condition.item_type]

        item_types_condition = next((condition for condition in rule.conditions if isinstance(condition, ItemTypesCondition)), None)
        if item_types_condition is not None:
            return list(item_types_condition.item_types)

        model_file_ids_condition = next((condition for condition in rule.conditions if isinstance(condition, ModelFileIdsCondition)), None)
        if model_file_ids_condition is not None:
            item_types: list[ItemType] = []
            for model_file_id in model_file_ids_condition.model_file_ids:
                item = self._find_item_by_model_file_id(model_file_id)
                if item is not None and item.item_type.is_weapon_type() and item.item_type not in item_types:
                    item_types.append(item.item_type)
            return item_types

        return []

    class ConditionEditor:
        @staticmethod
        def BeginConditionContainer(ui : "UI", rule : Rule, condition : Condition, size: Optional[tuple[float, float]] = None) -> bool:
            is_custom_rule = isinstance(rule, CustomRule)
            single_condition = len(rule.conditions) == 1
            show_condition_wrapper = not single_condition or is_custom_rule
            size = size if size is not None else (0, 0)
            
            if ImGui.begin_child(f"##condition_container{id(condition)}", size, border=show_condition_wrapper):
                title = ui._humanize_name(type(condition).__name__)
                description = inspect.getdoc(type(condition)) or ""
                description = re.sub(r":class:`([^`]+)`", r"\1", description).replace("**", "").strip()
                style = ImGui.get_style()
                y = PyImGui.get_cursor_pos_y()
                width = PyImGui.get_content_region_avail()[0]
                
                if show_condition_wrapper:
                    ImGui.text_wrapped(title, font_size=16)
                    if description:
                        ImGui.show_tooltip(description)
                    
                    if is_custom_rule:      
                        PyImGui.set_cursor_pos_y(y - 4)
                        PyImGui.set_cursor_pos_x(width - 3)
                                    
                        style.FramePadding.push_style_var_direct(4, 1)
                        clicked = PyImGui.button("x", 16, 16)                
                        style.FramePadding.pop_style_var_direct()
                        
                        if clicked:
                            rule.conditions.remove(condition)
                            return False
                        
                    ImGui.separator()
                    
                return True
            
            return False
        
        @staticmethod
        def EndConditionContainer() -> None:
            ImGui.end_child()
            
        @staticmethod
        def ForModelIdsCondition(ui : "UI", rule : Rule, condition: ModelIdsCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            model_ids = [m for m in ModelID]
            popup_id = "##model_ids_rule_add_popup"
            selected_model_ids = {
                int(model_id.value) if isinstance(model_id, ModelID) else int(model_id)
                for model_id in condition.model_ids
            }
            
            style = ImGui.get_style()
            
            spacing = style.ItemSpacing.value2 or 0
            element_height = 48
            base_height = 50 + spacing
            available_height = PyImGui.get_content_region_avail()[1]
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * len(condition.model_ids), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Model ID", -1):
                    ui.model_id_search = ""
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((300, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Model ID")
                    ImGui.separator()

                    PyImGui.set_next_item_width(-1)
                    _, ui.model_id_search = ImGui.search_field("##model_id_enum_search", ui.model_id_search, "Search model ids or enter an integer...")
                    search_query = ui._normalize_search_query(ui.model_id_search)
                    matching_model_ids = [
                        model_id
                        for model_id in sorted(model_ids, key=lambda model_id: model_id.name)
                        if ui._search_text_matches(search_query, model_id.name, int(model_id.value))
                    ]

                    manual_value: int | None = None
                    if search_query:
                        try:
                            manual_value = int(search_query)
                        except ValueError:
                            manual_value = None

                    exact_enum_match = any(int(model_id.value) == manual_value for model_id in model_ids) if manual_value is not None else False

                    if manual_value is not None and not exact_enum_match and manual_value not in selected_model_ids:
                        if ImGui.begin_selectable(f"##manual_model_id_{manual_value}", False, (0, 34)):
                            ImGui.text(f"Manual Model ID: {manual_value}")

                        if ImGui.end_selectable():
                            condition.model_ids.append(manual_value)
                            changed = True
                            PyImGui.close_current_popup()

                        if PyImGui.is_item_hovered():
                            ImGui.show_tooltip("Add this raw integer model id even if it is not part of the ModelID enum yet.")

                    if ImGui.begin_child("##model_id_enum_candidates", (0, 320), border=True):
                        for model_id in matching_model_ids:
                            model_id_value = int(model_id.value)
                            already_selected = model_id_value in selected_model_ids
                            if ImGui.begin_selectable(f"##model_id_enum_{model_id.name}", False, (0, 34)):
                                ImGui.text(ui._humanize_name(model_id.name))
                                x, y = PyImGui.get_cursor_pos()
                                PyImGui.set_cursor_pos(x, y - 4)
                                ImGui.text_colored(f"{model_id_value}", UI.GRAY_COLOR.color_tuple, font_size=12)

                            if ImGui.end_selectable() and not already_selected:
                                condition.model_ids.append(model_id)
                                changed = True
                                PyImGui.close_current_popup()

                            if PyImGui.is_item_hovered():
                                tooltip = f"{ui._humanize_name(model_id.name)}\nModel ID: {model_id_value}"
                                ImGui.show_tooltip(tooltip)
                    ImGui.end_child()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()

                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_child("##added_model_id_candidates", (0, 0), border=False):
                    for index, model_id in enumerate(condition.model_ids):
                        model_id_value = int(model_id.value) if isinstance(model_id, ModelID) else int(model_id)
                        label = ui._humanize_name(model_id.name) if isinstance(model_id, ModelID) else f"Manual ID {model_id_value}"
                        unique_id = f"model_ids_rule_{id(condition)}_{model_id_value}_{index}"

                        if ImGui.begin_child(f"##{unique_id}", (0, element_height), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 30):
                                condition.model_ids.pop(index)
                                changed = True
                                ImGui.end_child()
                                break

                            PyImGui.same_line(0, 8)
                            PyImGui.begin_group()
                            ImGui.text(label)
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 4)
                            ImGui.text_colored(f"Model ID: {model_id_value}", UI.GRAY_COLOR.color_tuple, font_size=12)
                            PyImGui.end_group()
                        ImGui.end_child()
                ImGui.end_child()
                
            UI.ConditionEditor.EndConditionContainer()

            return changed
        
        @staticmethod
        def ForItemTypesCondition(ui : "UI", rule : Rule, condition: ItemTypesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            
            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 25
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            
            width = PyImGui.get_content_region_avail()[0]
            columns = max(1, int(width // 200))
            
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * (len(ItemType) / columns), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.begin_child(f"##item_types_{id(condition)}", (0, 0), border=False):
                    PyImGui.columns(columns, "item_type_columns", False)
                    sorted_item_types = sorted(ItemType, key=lambda it: it.name)
                    for item_type in sorted_item_types:
                        is_selected = item_type in condition.item_types
                        selected = ImGui.checkbox(f"{ui._humanize_name(item_type.name)}", is_selected)

                        if selected != is_selected:
                            if item_type in condition.item_types:
                                condition.item_types.remove(item_type)
                            else:
                                condition.item_types.append(item_type)
                            changed = True

                        PyImGui.next_column()
                    PyImGui.end_columns()
                ImGui.end_child()
                
            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForEncodedNamesCondition(ui: "UI", rule: Rule, condition: EncodedNamesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            items = ui._unique_encoded_name_items
            popup_id = f"##encoded_name_condition_add_popup_{id(condition)}"
            selected_encoded_names = set(condition.encoded_names)
            
            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 56
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * len(condition.encoded_names), available_height))
                        
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Encoded Name", -1):
                    ui.encoded_name_search = ""
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((500, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Encoded Name")
                    ImGui.separator()

                    PyImGui.set_next_item_width(-1)
                    _, ui.encoded_name_search = ImGui.search_field(f"##encoded_name_search_{id(condition)}", ui.encoded_name_search, "Search by item name or paste an encoded name...")
                    search_query = ui._normalize_search_query(ui.encoded_name_search)
                    matching_items = [
                        item
                        for item in items
                        if ui._search_text_matches(search_query, item.name, item.plural_name, ui._get_item_encoded_name_string(item))
                    ]

                    matching_items = [
                        matching_items[i]
                        for i in range(len(matching_items))
                        if ui._get_item_encoded_name_string(matching_items[i]) not in selected_encoded_names
                        or (i > 0 and ui._get_item_encoded_name_string(matching_items[i]) == ui._get_item_encoded_name_string(matching_items[i - 1]))
                    ]

                    if ui.encoded_name_search.strip() and ui.encoded_name_search.strip() not in selected_encoded_names:
                        manual_encoded_name = ui.encoded_name_search.strip()

                        if PyImGui.is_rect_visible(10, 40):
                            if ImGui.begin_selectable(f"##manual_encoded_name_{id(condition)}", False, (0, 40)):
                                ImGui.text("Use typed encoded name")
                                x, y = PyImGui.get_cursor_pos()
                                PyImGui.set_cursor_pos(x, y - 4)
                                ImGui.text_colored(manual_encoded_name, UI.GRAY_COLOR.color_tuple, font_size=12)

                            if ImGui.end_selectable():
                                condition.encoded_names.append(ui._convert_str_to_encoded_bytes(manual_encoded_name))
                                changed = True
                                PyImGui.close_current_popup()
                        else:
                            ImGui.dummy(0, 40)

                    if ImGui.begin_child(f"##encoded_name_candidates_{id(condition)}", (0, 320), border=True):
                        for item in matching_items:
                            encoded_name = ui._get_item_encoded_name_string(item)
                            already_selected = encoded_name in selected_encoded_names
                            item_name = ui._get_item_display_name(item)

                            if PyImGui.is_rect_visible(10, 40):
                                if ImGui.begin_selectable(f"##encoded_name_{id(condition)}_{item.item_type.name}_{item.model_id}", False, (0, 40)):
                                    ui._draw_item_texture(item)
                                    PyImGui.same_line(0, 8)
                                    PyImGui.begin_group()
                                    ImGui.text(item_name)
                                    x, y = PyImGui.get_cursor_pos()
                                    PyImGui.set_cursor_pos(x, y - 4)
                                    ImGui.text_colored(encoded_name, UI.GRAY_COLOR.color_tuple, font_size=12)
                                    PyImGui.end_group()

                                if ImGui.end_selectable() and not already_selected:
                                    condition.encoded_names.append(ui._convert_str_to_encoded_bytes(encoded_name))
                                    changed = True
                                    PyImGui.close_current_popup()

                                if PyImGui.is_item_hovered():
                                    tooltip = f"{item_name}\n{ui._humanize_name(item.item_type.name)}\nModel ID: {item.model_id}"
                                    ImGui.show_tooltip(tooltip)
                            else:
                                ImGui.dummy(0, 40)
                    ImGui.end_child()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()

                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_child(f"##added_encoded_name_candidates_{id(condition)}", (0, 0), border=False):
                    for index, encoded_name in enumerate(condition.encoded_names):
                        item = ui._find_item_by_encoded_name(encoded_name)
                        unique_id = f"encoded_name_condition_{id(condition)}_{index}"

                        if ImGui.begin_child(f"##{unique_id}", (0, 56), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 36):
                                condition.encoded_names.pop(index)
                                changed = True
                                ImGui.end_child()
                                break

                            PyImGui.same_line(0, 8)
                            ui._draw_item_texture(item)
                            PyImGui.same_line(0, 8)
                            PyImGui.begin_group()
                            ImGui.text(ui._get_item_display_name(item) if item is not None else "Custom Encoded Name")
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 4)
                            ImGui.text_colored(string_table.decode(encoded_name), UI.GRAY_COLOR.color_tuple, font_size=12)
                            PyImGui.end_group()
                        ImGui.end_child()
                ImGui.end_child()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForModelFileIdsCondition(ui: "UI", rule: Rule, condition: ModelFileIdsCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            items = ui._unique_model_file_id_items
            popup_id = f"##model_file_id_condition_add_popup_{id(condition)}"
            selected_model_file_ids = set(condition.model_file_ids)
                        
            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 56
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * len(condition.model_file_ids), available_height))

            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Model File ID", -1):
                    ui.model_file_id_search = ""
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((450, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Model File ID")
                    ImGui.separator()

                    PyImGui.set_next_item_width(-1)
                    _, ui.model_file_id_search = ImGui.search_field(f"##model_file_id_search_{id(condition)}", ui.model_file_id_search, "Search by item name or enter a model file id...")
                    search_query = ui._normalize_search_query(ui.model_file_id_search)

                    manual_value: int | None = None
                    if search_query:
                        try:
                            manual_value = int(search_query)
                        except ValueError:
                            manual_value = None

                    if manual_value is not None and manual_value not in selected_model_file_ids:
                        if ImGui.begin_selectable(f"##manual_model_file_id_{id(condition)}_{manual_value}", False, (0, 36)):
                            ImGui.text(f"Manual Model File ID: {manual_value}")

                        if ImGui.end_selectable():
                            condition.model_file_ids.append(manual_value)
                            changed = True
                            PyImGui.close_current_popup()

                    if ImGui.begin_child(f"##model_file_id_candidates_{id(condition)}", (0, 320), border=True):
                        for item in items:
                            model_file_id = int(item.model_file_id)
                            already_selected = model_file_id in selected_model_file_ids
                            item_name = ui._get_item_display_name(item)
                            if not ui._search_text_matches(search_query, item_name, item.plural_name, model_file_id):
                                continue

                            if ImGui.begin_selectable(f"##model_file_id_{id(condition)}_{item.item_type.name}_{item.model_id}", False, (0, 36)):
                                ui._draw_item_texture(item)
                                PyImGui.same_line(0, 8)
                                PyImGui.begin_group()
                                ImGui.text(item_name)
                                x, y = PyImGui.get_cursor_pos()
                                PyImGui.set_cursor_pos(x, y - 4)
                                ImGui.text_colored(f"Model File ID: {model_file_id}", UI.GRAY_COLOR.color_tuple, font_size=12)
                                PyImGui.end_group()

                            if ImGui.end_selectable() and not already_selected:
                                condition.model_file_ids.append(model_file_id)
                                changed = True
                                PyImGui.close_current_popup()

                            if PyImGui.is_item_hovered():
                                tooltip = f"{item_name}\nModel File ID: {model_file_id}"
                                ImGui.show_tooltip(tooltip)
                    ImGui.end_child()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()

                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_child(f"##added_model_file_id_candidates_{id(condition)}", (0, 0), border=False):
                    for index, model_file_id in enumerate(condition.model_file_ids):
                        item = ui._find_item_by_model_file_id(model_file_id)
                        unique_id = f"model_file_id_condition_{id(condition)}_{model_file_id}_{index}"

                        if ImGui.begin_child(f"##{unique_id}", (0, 56), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 36):
                                condition.model_file_ids.pop(index)
                                changed = True
                                ImGui.end_child()
                                break

                            PyImGui.same_line(0, 8)
                            ui._draw_item_texture(item)
                            PyImGui.same_line(0, 8)
                            PyImGui.begin_group()
                            ImGui.text(ui._get_item_display_name(item) if item is not None else f"Unknown Item ({model_file_id})")
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 4)
                            ImGui.text_colored(f"Model File ID: {model_file_id}", UI.GRAY_COLOR.color_tuple, font_size=12)
                            PyImGui.end_group()
                        ImGui.end_child()
                ImGui.end_child()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForModelFileIdsAndItemTypesCondition(ui: "UI", rule: Rule, condition: ModelFileIdsAndItemTypesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            items = ui._unique_model_file_id_items
            popup_id = f"##model_file_id_item_type_condition_add_popup_{id(condition)}"
            selected_entries = {(entry.model_file_id, entry.item_type) for entry in condition.model_file_ids_and_item_types}

            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 56
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * len(condition.model_file_ids_and_item_types), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Model File ID", -1):
                    ui.model_file_id_search = ""
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((450, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Item By Model File ID")
                    ImGui.separator()

                    PyImGui.set_next_item_width(-1)
                    _, ui.model_file_id_search = ImGui.search_field(f"##model_file_id_item_type_search_{id(condition)}", ui.model_file_id_search, "Search by item name or model file id...")
                    search_query = ui._normalize_search_query(ui.model_file_id_search)

                    if ImGui.begin_child(f"##model_file_id_item_type_candidates_{id(condition)}", (0, 320), border=True):
                        for item in items:
                            key = (int(item.model_file_id), item.item_type)
                            already_selected = key in selected_entries
                            item_name = ui._get_item_display_name(item)
                            if not ui._search_text_matches(search_query, item.name, item.plural_name, item.item_type.name, item.model_file_id):
                                continue

                            if ImGui.begin_selectable(f"##model_file_id_item_type_{id(condition)}_{item.item_type.name}_{item.model_id}", False, (0, 36)):
                                ui._draw_item_texture(item)
                                PyImGui.same_line(0, 8)
                                PyImGui.begin_group()
                                ImGui.text(item_name)
                                x, y = PyImGui.get_cursor_pos()
                                PyImGui.set_cursor_pos(x, y - 4)
                                ImGui.text_colored(
                                    f"{ui._humanize_name(item.item_type.name)} | Model File ID: {item.model_file_id}",
                                    UI.GRAY_COLOR.color_tuple,
                                    font_size=12,
                                )
                                PyImGui.end_group()

                            if ImGui.end_selectable() and not already_selected:
                                condition.model_file_ids_and_item_types.append(
                                    ModelFileIdAndItemType(
                                        model_file_id=int(item.model_file_id),
                                        item_type=item.item_type,
                                    )
                                )
                                changed = True
                                PyImGui.close_current_popup()

                            if PyImGui.is_item_hovered():
                                tooltip = f"{item_name}\n{ui._humanize_name(item.item_type.name)}\nModel File ID: {item.model_file_id}"
                                ImGui.show_tooltip(tooltip)
                    ImGui.end_child()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()

                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_child(f"##added_model_file_id_item_type_candidates_{id(condition)}", (0, 0), border=False):
                    for index, entry in enumerate(list(condition.model_file_ids_and_item_types)):
                        item = next(
                            (
                                candidate
                                for candidate in items
                                if int(candidate.model_file_id) == int(entry.model_file_id) and candidate.item_type == entry.item_type
                            ),
                            None,
                        )
                        unique_id = f"model_file_id_item_type_condition_{id(condition)}_{entry.model_file_id}_{entry.item_type.name}_{index}"

                        if ImGui.begin_child(f"##{unique_id}", (0, 56), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 36):
                                condition.model_file_ids_and_item_types.pop(index)
                                changed = True
                                ImGui.end_child()
                                break

                            PyImGui.same_line(0, 8)
                            ui._draw_item_texture(item)
                            PyImGui.same_line(0, 8)
                            PyImGui.begin_group()
                            ImGui.text(ui._get_item_display_name(item) if item is not None else f"Unknown Item ({entry.model_file_id})")
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 4)
                            ImGui.text_colored(
                                f"{ui._humanize_name(entry.item_type.name)} | Model File ID: {entry.model_file_id}",
                                UI.GRAY_COLOR.color_tuple,
                                font_size=12,
                            )
                            PyImGui.end_group()
                        ImGui.end_child()
                ImGui.end_child()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForModelIdsAndItemTypesCondition(ui: "UI", rule: Rule, condition: ModelIdsAndItemTypesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            items = [item for sublist in ITEM_DATA.data.values() for item in sublist.values()]
            sorted_items = sorted(items, key=lambda item: item.name)

            popup_id = f"##model_id_item_type_condition_add_popup_{id(condition)}"
            selected_models = [(model_id, item_type) for model_id, item_type in condition.modelids_and_itemtypes]

            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 56
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * len(condition.modelids_and_itemtypes), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Model ID", -1):
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((400, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Item By Model ID")
                    ImGui.separator()

                    PyImGui.set_next_item_width(-1)
                    search_changed, ui.model_id_search = ImGui.search_field(f"##model_id_search_{id(condition)}", ui.model_id_search, "Search by name or model id...")
                    search_query = ui._normalize_search_query(ui.model_id_search)

                    if ImGui.begin_child(f"##model_id_candidates_{id(condition)}", (0, 320), border=True):
                        if search_changed:
                            PyImGui.set_scroll_y(0)

                        for item in sorted_items:
                            modelid_item_type = int(item.model_id)
                            already_selected = any(modelid_item_type == (int(mid.value) if isinstance(mid, ModelID) else mid) for mid, _ in selected_models)

                            item_name = item.name or f"Model {item.model_id}"
                            if not ui._search_text_matches(search_query, item.name, item.plural_name, item.model_id):
                                continue

                            if already_selected:
                                continue

                            if PyImGui.is_rect_visible(10, 42):
                                if ImGui.begin_selectable(f"##model_id_candidate_{id(condition)}_{item.item_type.name}_{modelid_item_type}", False, (0, 36)):
                                    UI._draw_item_texture(item, (32, 32))
                                    PyImGui.same_line(0, 8)
                                    PyImGui.begin_group()
                                    x, _ = PyImGui.get_cursor_pos()
                                    ImGui.text(item_name)
                                    if len(item.attributes) == 1:
                                        PyImGui.same_line(0, 8)
                                        ImGui.text_colored(f"[{ui._humanize_name(item.attributes[0].name)}]", UI.GRAY_COLOR.color_tuple, font_size=12)

                                    _, y = PyImGui.get_cursor_pos()
                                    PyImGui.set_cursor_pos(x, y - 4)
                                    ImGui.text_colored(f"Model ID: {modelid_item_type}", UI.GRAY_COLOR.color_tuple, font_size=12)
                                    PyImGui.end_group()

                                if ImGui.end_selectable():
                                    try:
                                        condition.modelids_and_itemtypes.append(ModelIdAndItemType(ModelID(modelid_item_type), item.item_type))
                                    except ValueError:
                                        condition.modelids_and_itemtypes.append(ModelIdAndItemType(modelid_item_type, item.item_type))
                                    changed = True
                                    PyImGui.close_current_popup()

                                if PyImGui.is_item_hovered():
                                    if PyImGui.begin_tooltip():
                                        ImGui.text(item_name)
                                        if len(item.attributes) == 1:
                                            PyImGui.same_line(0, 8)
                                            ImGui.text_colored(f"[{ui._humanize_name(item.attributes[0].name)}]", UI.GRAY_COLOR.color_tuple, font_size=12)
                                        ImGui.separator()
                                        ImGui.text_colored(f"Model ID: {modelid_item_type}", UI.GRAY_COLOR.color_tuple, font_size=12)
                                        ImGui.text_colored(f"Item Type: {ui._humanize_name(item.item_type.name)}", UI.GRAY_COLOR.color_tuple, font_size=12)
                                    PyImGui.end_tooltip()
                            else:
                                ImGui.dummy(0, 36)
                    ImGui.end_child()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()

                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_child(f"##model_id_rule_list_{id(condition)}", (0, 0), border=False):
                    selected_items: list[tuple[ModelIdAndItemType, Any]] = []
                    for model_id, item_type in condition.modelids_and_itemtypes:
                        modelid_item_type = int(model_id.value) if isinstance(model_id, ModelID) else int(model_id)
                        item_data = next((item for item in sorted_items if item.model_id == modelid_item_type), None)
                        selected_items.append((ModelIdAndItemType(model_id, item_type), item_data))

                    for index, (modelid_item_type, item_data) in enumerate(selected_items):
                        unique_id = f"model_id_condition_{id(condition)}_{modelid_item_type}_{index}"
                        item_name = item_data.name if item_data is not None else f"Unknown Item ({modelid_item_type})"

                        if ImGui.begin_child(f"##{unique_id}", (0, 50), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 30):
                                original_entry = next(
                                    (
                                        existing_model_id
                                        for existing_model_id in condition.modelids_and_itemtypes
                                        if (int(existing_model_id.model_id.value) if isinstance(existing_model_id.model_id, ModelID) else int(existing_model_id.model_id)) == (int(modelid_item_type.model_id.value) if isinstance(modelid_item_type.model_id, ModelID) else int(modelid_item_type.model_id))
                                        and existing_model_id.item_type == modelid_item_type.item_type
                                    ),
                                    None,
                                )
                                if original_entry is not None:
                                    condition.modelids_and_itemtypes.remove(original_entry)
                                    changed = True
                                ImGui.end_child()
                                break

                            PyImGui.same_line(0, 8)
                            UI._draw_item_texture(item_data, (32, 32))
                            PyImGui.same_line(0, 8)
                            PyImGui.begin_group()
                            ImGui.text(item_name)
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 4)
                            item_type_name = ui._humanize_name(modelid_item_type.item_type.name)
                            ImGui.text_colored(
                                f"{item_type_name} | Model ID: {modelid_item_type.model_id}" + (f" | {item_data.attributes[0].name}" if item_data is not None and len(item_data.attributes) == 1 else ""),
                                UI.GRAY_COLOR.color_tuple,
                                font_size=12,
                            )
                            PyImGui.end_group()
                        ImGui.end_child()
                ImGui.end_child()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForExactItemTypeCondition(ui: "UI", rule: Rule, condition: ExactItemTypeCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            
            size = size if size is not None else (-1, 30)
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                selected_label = ui._humanize_name(condition.item_type.name) if condition.item_type is not None else "Select an item type"
                PyImGui.set_next_item_width(size[0] if size[0] > 0 else -1)
                if PyImGui.begin_combo(f"##exact_item_type_{id(condition)}", selected_label, PyImGui.ImGuiComboFlags.NoFlag):
                    for item_type in sorted(ItemType, key=lambda item_type: item_type.name):
                        if ImGui.selectable(ui._humanize_name(item_type.name), selected=condition.item_type == item_type):
                            condition.item_type = item_type
                            changed = True
                    ImGui.end_combo()
            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForRaritiesCondition(ui: "UI", rule: Rule, condition: RaritiesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            style = ImGui.get_style()
            
            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 25
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * len(Rarity), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.begin_child(f"##rarities_{id(condition)}", (0, 0), border=False):
                    for rarity in Rarity:
                        is_selected = rarity in condition.rarities
                        style.Text.push_color_direct(ui._get_rarity_color(rarity).rgb_tuple)
                        selected = ImGui.checkbox(f"{rarity.name}##{id(condition)}", is_selected)
                        style.Text.pop_color_direct()

                        if selected != is_selected:
                            if rarity in condition.rarities:
                                condition.rarities.remove(rarity)
                            else:
                                condition.rarities.append(rarity)
                            changed = True
                ImGui.end_child()
            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForDyeColorsCondition(ui: "UI", rule: Rule, condition: DyeColorsCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            
            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 25
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * (len(DyeColor) - 1), available_height))

            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.begin_child(f"##dye_colors_{id(condition)}", (0, 0), border=False):
                    sorted_dye_colors = sorted(DyeColor, key=lambda dc: dc.name)
                    for dye_color in sorted_dye_colors:
                        if dye_color == DyeColor.NoColor:
                            continue

                        is_selected = dye_color in condition.dye_colors
                        PyImGui.begin_group()
                        selected = ImGui.checkbox(f"##dye_{id(condition)}_{dye_color.name}", is_selected)
                        hovered = PyImGui.is_item_hovered()
                        PyImGui.same_line(0, 5)
                        ImGui.image(ui.dye_textures.get(dye_color, ""), (24, 24))
                        PyImGui.same_line(0, 5)
                        ImGui.text_aligned(dye_color.name, height=24, alignment=Alignment.MidLeft)
                        PyImGui.end_group()

                        if not hovered and PyImGui.is_item_clicked(0):
                            selected = not is_selected

                        if selected != is_selected:
                            if dye_color in condition.dye_colors:
                                condition.dye_colors.remove(dye_color)
                            else:
                                condition.dye_colors.append(dye_color)
                            changed = True
                ImGui.end_child()
            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForSalvagesToMaterialsCondition(ui: "UI", rule: Rule, condition: SalvagesToMaterialsCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            popup_id = f"##salvage_material_condition_add_popup_{id(condition)}"
            selected_materials = set(condition.materials)

            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 48
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * (len(condition.materials)), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Material", -1):
                    ui.material_search = ""
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((420, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Salvage Material")
                    ImGui.separator()

                    PyImGui.set_next_item_width(-1)
                    _, ui.material_search = ImGui.search_field(f"##salvage_material_search_{id(condition)}", ui.material_search, "Search material name or model id...")
                    search_query = ui._normalize_search_query(ui.material_search)
                    ImGui.show_tooltip("Search by material name or model id.")

                    if ImGui.begin_child(f"##salvage_material_candidates_{id(condition)}", (0, 320), border=True):
                        for material in ui._salvage_material_options:
                            already_selected = material in selected_materials
                            label = material.name
                            if not ui._search_text_matches(search_query, label, material.plural_name, int(material.model_id)):
                                continue

                            if ImGui.begin_selectable(f"##salvage_material_{id(condition)}_{material.name}", False, (0, 34)):
                                UI._draw_item_texture(material, (32, 32))
                                PyImGui.same_line(0, 8)
                                PyImGui.begin_group()
                                ImGui.text(label)
                                x, y = PyImGui.get_cursor_pos()
                                PyImGui.set_cursor_pos(x, y - 4)
                                ImGui.text_colored(f"Model ID: {int(material.model_id)}", UI.GRAY_COLOR.color_tuple, font_size=12)
                                PyImGui.end_group()

                            if ImGui.end_selectable() and not already_selected:
                                condition.materials.append(material.model_id)
                                changed = True
                                PyImGui.close_current_popup()

                            if PyImGui.is_item_hovered():
                                tooltip = f"{label}\nModel ID: {int(material.model_id)}"
                                ImGui.show_tooltip(tooltip)
                    ImGui.end_child()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()

                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_child(f"##added_material_candidates_{id(condition)}", (0, 0), border=False):
                    for index, mid in enumerate(condition.materials):
                        material = next((m for m in ui._salvage_material_options if int(m.model_id) == int(mid)), None)
                        unique_id = f"salvage_material_condition_{id(condition)}_{material.name}_{index}" if material is not None else f"salvage_material_condition_{id(condition)}_{mid}_{index}"
                        if ImGui.begin_child(f"##{unique_id}", (0, 48), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 30):
                                condition.materials.pop(index)
                                changed = True
                                ImGui.end_child()
                                break

                            PyImGui.same_line(0, 8)
                            UI._draw_item_texture(material, (32, 32)) if material is not None else ImGui.dummy(32, 32)
                            PyImGui.same_line(0, 8)
                            PyImGui.begin_group()
                            ImGui.text(ui._humanize_name(material.name if material is not None else f"Unknown Material ({mid})"))
                            x, y = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(x, y - 4)
                            ImGui.text_colored(f"Model ID: {int(material.model_id) if material is not None else int(mid)}", UI.GRAY_COLOR.color_tuple, font_size=12)
                            PyImGui.end_group()
                        ImGui.end_child()
                ImGui.end_child()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForWeaponRequirementCondition(ui: "UI", rule: Rule, condition: WeaponRequirementCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            item_types = [item_type for item_type in ui._get_condition_requirement_item_types(rule) if item_type.is_weapon_type()]
            item_types = sorted(set(item_types), key=lambda item_type: item_type.name)
            detail_item_type = item_types[0] if len(item_types) == 1 else None
            editor_id = str(id(condition))

            style = ImGui.get_style()
            spacing = style.ItemSpacing.value2 or 0
            element_height = 25
            base_height = 30 + element_height
            available_height = PyImGui.get_content_region_avail()[1]
            size = size if size is not None else (0, min(base_height + (element_height + spacing) * (14), available_height))
            
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.begin_child(f"##requirement_rows_{editor_id}", (0, 0), border=True):
                    for requirement in range(0, 14):
                        selected = requirement in condition.requirements
                        default_range = ui._get_default_weapon_value_range(detail_item_type, requirement) or (0, 0)
                        current_range = condition.requirements.get(requirement)
                        min_value = current_range.min_value if current_range is not None else default_range[0]
                        max_value = current_range.max_value if current_range is not None else default_range[1]
                        if current_range is not None and current_range.min_value == 0 and current_range.max_value == 0 and default_range != (0, 0):
                            min_value, max_value = default_range
                        value_text = ui._format_weapon_value_range(detail_item_type, requirement)

                        if ImGui.begin_selectable(f"##requirement_selectable_{editor_id}_{requirement}", selected=selected, size=(0, 40), border_color=UI.GRAY_COLOR.rgb_tuple):
                            ImGui.text(string_table.decode(GWEncoded._requires_attribute_level(attribute_level=requirement, attribute=UI.ITEM_TYPE_ATTRIBUTES.get(detail_item_type or ItemType.Unknown, Attribute.None_))))
                            ImGui.text_colored(value_text, UI.GRAY_COLOR.color_tuple, font_size=12)

                        if ImGui.end_selectable():
                            if not selected:
                                condition.requirements[requirement] = DamageRange(min_value, max_value)
                            else:
                                condition.requirements.pop(requirement, None)
                            changed = True
                ImGui.end_child()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForInherentFiltersCondition(ui: "UI", rule: Rule, condition: InherentFiltersCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            unique_id = str(id(condition))

            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                try:
                    selectable_size = (0, 45)
                    selected_selectable_size = (0, 90)
                    if ImGui.begin_child(f"##inherent_candidates_{unique_id}", (0, 0), border=True):
                        ImGui.text("Inherent Upgrades", font_size=16)
                        PyImGui.set_next_item_width(-1)
                        _, ui.inherent_upgrade_search = ImGui.search_field(f"##inherent_search_{unique_id}", ui.inherent_upgrade_search, "Search inherent upgrades...")
                        search_query = ui._normalize_search_query(ui.inherent_upgrade_search)

                        if ImGui.begin_child(f"##inherent_selectables_{unique_id}", (0, 0), border=False):
                            for index, inherent_type in enumerate(ui.available_inherent_upgrade_types):
                                inherent = inherent_type()
                                if not isinstance(inherent, Inherent):
                                    continue

                                label = inherent.name_plain or ui._humanize_name(inherent_type.__name__)
                                description = inherent.description_plain
                                already_selected = any(type(existing.inherent) is inherent_type for existing in condition.inherents)
                                if not ui._search_text_matches(search_query, label, description, inherent_type.__name__):
                                    continue

                                inherent_filter = next((existing for existing in condition.inherents if type(existing.inherent) is inherent_type), None)
                                if ImGui.begin_selectable(f"##inherent_candidate_{unique_id}_{inherent_type.__name__}", selected=already_selected, size=selected_selectable_size if already_selected else selectable_size):
                                    ImGui.text(label)
                                    x, y = PyImGui.get_cursor_pos()
                                    PyImGui.set_cursor_pos(x, y - 4)
                                    ImGui.text_colored(description, UI.GRAY_COLOR.color_tuple, font_size=12)

                                    if already_selected and inherent_filter is not None:
                                        range_instructions = ui._get_range_instructions(inherent)
                                        PyImGui.begin_group()
                                        if len(range_instructions) == 0:
                                            ImGui.text_colored("Fixed inherent upgrade.", UI.GRAY_COLOR.color_tuple, font_size=12)
                                        else:
                                            for instruction in range_instructions:
                                                current_range = inherent_filter.ranges.get(
                                                    instruction.target,
                                                    DamageRange(int(instruction.min_value), int(instruction.max_value)),
                                                )
                                                min_value = max(int(instruction.min_value), min(int(instruction.max_value), int(current_range.min_value)))
                                                max_value = max(min_value, min(int(instruction.max_value), int(current_range.max_value)))
                                                ImGui.text_colored(ui._humanize_name(instruction.target), UI.GRAY_COLOR.color_tuple, font_size=12)
                                                PyImGui.same_line(0, 8)
                                                PyImGui.set_next_item_width(80)
                                                new_min = ImGui.slider_int(
                                                    f"Min##inherent_min_{unique_id}_{index}_{instruction.target}",
                                                    min_value,
                                                    int(instruction.min_value),
                                                    int(instruction.max_value),
                                                )
                                                PyImGui.same_line(0, 6)
                                                PyImGui.set_next_item_width(80)
                                                new_max = ImGui.slider_int(
                                                    f"Max##inherent_max_{unique_id}_{index}_{instruction.target}",
                                                    max_value,
                                                    int(instruction.min_value),
                                                    int(instruction.max_value),
                                                )
                                                new_min = max(int(instruction.min_value), min(int(new_min), int(instruction.max_value)))
                                                new_max = max(int(instruction.min_value), min(int(new_max), int(instruction.max_value)))
                                                if new_min > new_max:
                                                    new_min, new_max = new_max, new_min
                                                if new_min != min_value or new_max != max_value:
                                                    inherent_filter.ranges[instruction.target] = DamageRange(new_min, new_max)
                                                    changed = True
                                        PyImGui.end_group()

                                if ImGui.end_selectable():
                                    if not already_selected:
                                        condition.inherents.append(InherentFilter.from_inherent(inherent, use_full_ranges=False))
                                    else:
                                        condition.inherents[:] = [existing for existing in condition.inherents if type(existing.inherent) is not inherent_type]
                                    changed = True

                                if PyImGui.is_item_hovered():
                                    text_size = PyImGui.calc_text_size(inherent.description_plain)
                                    PyImGui.set_next_window_size(((text_size[0] + 20) * (1 if inherent_filter is None else 2), 0), cond=PyImGui.ImGuiCond.Appearing)
                                    ImGui.begin_tooltip()
                                    ImGui.text(label, font_size=16)
                                    _, _, item_size = ImGui.get_item_rect()
                                    ImGui.separator()

                                    if inherent_filter is not None:
                                        width = max((text_size[0] + 20) * 2, item_size[0])
                                        if PyImGui.begin_child(f"##instruction_details_{unique_id}_{index}", (width, text_size[1] + 0), border=False):
                                            PyImGui.columns(2, "##inherent_tooltip_columns", False)
                                            for instruction in ui._get_range_instructions(inherent):
                                                setattr(inherent, instruction.target, inherent_filter.ranges[instruction.target].min_value)
                                                ImGui.text(inherent.description_plain)
                                                PyImGui.next_column()
                                                setattr(inherent, instruction.target, inherent_filter.ranges[instruction.target].max_value)
                                                ImGui.text(inherent.description_plain)
                                            PyImGui.end_columns()
                                        PyImGui.end_child()
                                    else:
                                        ImGui.text(description)
                                    ImGui.end_tooltip()
                        ImGui.end_child()
                    ImGui.end_child()
                except Exception as e:
                    Py4GW.Console.Log("Item Manager", f"Error in ConditionEditor.ForInherentFiltersCondition: {type(e).__name__}: {e!r}")
            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForInscribableCondition(ui: "UI", rule: Rule, condition: InscribableCondition, size: Optional[tuple[float, float]] = None) -> bool:
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                ImGui.text_wrapped("Requires the item to be inscribable.")
            UI.ConditionEditor.EndConditionContainer()
            return False

        @staticmethod
        def ForUnidentifiedCondition(ui: "UI", rule: Rule, condition: UnidentifiedCondition, size: Optional[tuple[float, float]] = None) -> bool:
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                ImGui.text_wrapped("Requires the item to be unidentified.")
            UI.ConditionEditor.EndConditionContainer()
            return False

        @staticmethod
        def ForArmorUpgradesCondition(ui: "UI", rule: Rule, condition: ArmorUpgradesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            popup_id = f"##armor_upgrade_price_popup_{id(condition)}"
            trader_open = UIManagerExtensions.MerchantWindow.IsOpen()
            kind = TraderPriceCheckManager.get_kind()

            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
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
                    new_threshold = ImGui.input_int("Minimum trader value", ui.armor_upgrade_price_threshold, min_value=0, step_fast=1)
                    if new_threshold != ui.armor_upgrade_price_threshold:
                        ui.armor_upgrade_price_threshold = max(0, new_threshold)

                    quote_count = len(ui._get_trader_armor_upgrade_quotes())
                    ImGui.text_colored(f"Available trader quotes: {quote_count}", UI.GRAY_COLOR.color_tuple, font_size=12)

                    if ImGui.button("Apply Threshold", -1):
                        quotes = ui._get_trader_armor_upgrade_quotes()
                        added_count = 0
                        for quote in quotes:
                            if quote.quoted_value < ui.armor_upgrade_price_threshold:
                                continue
                            for selected_upgrade in ui._extract_armor_upgrades_from_trader_quote(quote):
                                if any(ui._upgrade_equals(existing_upgrade, selected_upgrade) for existing_upgrade in condition.armor_upgrades):
                                    continue
                                condition.armor_upgrades.append(selected_upgrade)
                                changed = True
                                added_count += 1
                        if not changed:
                            Py4GW.Console.Log("Item Manager", "Trader-based selection found matches, but all of them were already selected.", Py4GW.Console.MessageType.Warning)
                        else:
                            Py4GW.Console.Log("Item Manager", f"Trader-based selection added {added_count} upgrades to the condition.", Py4GW.Console.MessageType.Success)
                        PyImGui.close_current_popup()

                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()
                    PyImGui.end_popup()

                ImGui.separator()

                if ImGui.begin_table(f"##armor_upgrade_condition_table_{id(condition)}", 2, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable):
                    PyImGui.table_setup_column("Profession", PyImGui.TableColumnFlags.WidthFixed, 150)
                    PyImGui.table_setup_column("Upgrades", PyImGui.TableColumnFlags.WidthStretch)
                    PyImGui.table_next_row()
                    PyImGui.table_next_column()

                    if ImGui.begin_child(f"##armor_upgrade_condition_profession_{id(condition)}", (0, 0), border=False):
                        for profession in Profession:
                            is_selected = profession == ui.profession
                            decoded_profession_name = string_table.decode(GWEncoded.PROFESSION.get(profession, bytes())) or ui._humanize_name(profession.name)
                            if ImGui.begin_selectable(f"##profession_{id(condition)}_{profession.value}", is_selected):
                                ImGui.image(os.path.join(ui.texture_path, "Profession_Icons", ProfessionTextureMap.get(profession.value, "")), (24, 24))
                                PyImGui.same_line(0, 5)
                                ImGui.text_aligned(decoded_profession_name, height=24, alignment=Alignment.MidLeft)
                            if ImGui.end_selectable():
                                ui.profession = profession
                    ImGui.end_child()

                    PyImGui.table_next_column()
                    if ImGui.begin_child(f"##armor_upgrade_condition_upgrades_{id(condition)}", (0, 0), border=False):
                        try:
                            upgrades = [
                                upgrade_type for upgrade_type in ui.available_upgrade_types
                                if issubclass(upgrade_type, ArmorUpgrade) and getattr(upgrade_type, "profession", None) == ui.profession
                            ]
                            sorted_upgrades = sorted(upgrades, key=lambda ut: (getattr(ut, "rarity", 0), ui._format_upgrade_type_label(ut)))
                            insignias = [upgrade_type for upgrade_type in sorted_upgrades if issubclass(upgrade_type, Insignia)]
                            runes = [upgrade_type for upgrade_type in sorted_upgrades if issubclass(upgrade_type, Rune)]

                            for upgrade_type in [*insignias, *runes]:
                                upgrade: ArmorUpgrade = upgrade_type()
                                upgrade_label = ui._format_upgrade_label(upgrade)
                                is_upgrade_selected = any(isinstance(existing_upgrade, upgrade_type) for existing_upgrade in condition.armor_upgrades)
                                if ImGui.begin_selectable(f"##armor_upgrade_{id(condition)}_{upgrade_type.__name__}", is_upgrade_selected, (0, 20)):
                                    rarity_color = UI._get_rarity_color(upgrade.rarity)
                                    ImGui.text_colored(upgrade_label, rarity_color.color_tuple, font_size=14)
                                if ImGui.end_selectable():
                                    if is_upgrade_selected:
                                        condition.armor_upgrades = [existing_upgrade for existing_upgrade in condition.armor_upgrades if not isinstance(existing_upgrade, upgrade_type)]
                                    else:
                                        condition.armor_upgrades.append(upgrade_type())
                                    changed = True

                                if PyImGui.is_item_hovered():
                                    PyImGui.set_next_window_size((400, 50), cond=PyImGui.ImGuiCond.Appearing)
                                    PyImGui.begin_tooltip()
                                    quote = ui._get_trader_quote_for_armor_upgrade(upgrade)
                                    PyImGui.text_wrapped(upgrade.description_plain)
                                    if quote is not None:
                                        ImGui.text_colored(f"Trader Value: {UI.format_currency(quote.quoted_value)}\n", UI._get_rarity_color(Rarity.Gold).color_tuple, font_size=13)
                                        PyImGui.separator()
                                        ImGui.text_colored(f"Updated: {UI.format_time_ago(quote.checked_at)}\n", UI.GRAY_COLOR.color_tuple, font_size=12)
                                    else:
                                        PyImGui.separator()
                                        ImGui.text_colored("No matching trader quote found for this upgrade.", UI.GRAY_COLOR.color_tuple, font_size=12)
                                    PyImGui.end_tooltip()
                        except Exception as e:
                            ImGui.text_colored(f"Error loading upgrades: {str(e)}", (255, 0, 0, 255), font_size=12)
                    ImGui.end_child()
                    ImGui.end_table()

            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForMaxWeaponUpgradesCondition(ui: "UI", rule: Rule, condition: MaxWeaponUpgradesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.begin_table(f"##weapon_upgrade_condition_table_{id(condition)}", 2, PyImGui.TableFlags.Borders | PyImGui.TableFlags.Resizable):
                    PyImGui.table_setup_column("Mod Type", PyImGui.TableColumnFlags.WidthFixed, 150)
                    PyImGui.table_setup_column("Upgrades", PyImGui.TableColumnFlags.WidthStretch)
                    PyImGui.table_next_row()
                    PyImGui.table_next_column()

                    if ImGui.begin_child(f"##mod_type_selection_{id(condition)}", (0, 0), border=False):
                        for mod_type in [ItemUpgradeType.Prefix, ItemUpgradeType.Suffix, ItemUpgradeType.Inscription]:
                            is_selected = mod_type == ui.mod_type
                            mod_type_name = ui._humanize_name(mod_type.name)
                            if ImGui.begin_selectable(f"##mod_type_{id(condition)}_{mod_type.value}", is_selected):
                                ImGui.text_aligned(mod_type_name, height=24, alignment=Alignment.MidLeft)
                            if ImGui.end_selectable():
                                if ui.mod_type != mod_type:
                                    ui.max_weapon_upgrade_search = ""
                                ui.mod_type = mod_type
                    ImGui.end_child()

                    PyImGui.table_next_column()
                    style = ImGui.get_style()
                    style.ToggleButtonEnabled.push_color(ui._get_rarity_color(Rarity.Gold).opacity(0.85).rgb_tuple)
                    style.ToggleButtonDisabled.push_color((0, 0, 0, 85))
                    PyImGui.set_next_item_width(-1)
                    _, ui.max_weapon_upgrade_search = ImGui.search_field(f"##upgrade_search_{id(condition)}", ui.max_weapon_upgrade_search, "Search Upgrades...")
                    search_query = ui._normalize_search_query(ui.max_weapon_upgrade_search)
                    ImGui.separator()

                    if ImGui.begin_child(f"##weapon_upgrade_condition_upgrades_{id(condition)}", (0, 0), border=False):
                        upgrades = [
                            upgrade_type for upgrade_type in ui.available_upgrade_types
                            if (issubclass(upgrade_type, WeaponUpgrade) or issubclass(upgrade_type, Inscription)) and getattr(upgrade_type, "mod_type", None) == ui.mod_type
                        ]
                        for upgrade_type in sorted(upgrades, key=lambda ut: ui._format_upgrade_type_label(ut)):
                            for variant in [upgrade_type]:
                                upgrade = variant()
                                upgrade_label = ui._format_upgrade_label(upgrade)
                                if not ui._search_text_matches(search_query, upgrade_label):
                                    continue

                                if isinstance(upgrade, WeaponUpgrade):
                                    item_types = ui._get_allowed_item_types(upgrade)
                                    rarity_color = UI._get_rarity_color(upgrade.rarity)
                                    hovered = False
                                    if PyImGui.is_rect_visible(10, 70):
                                        if ImGui.begin_child(f"##upgrade_item_types_{id(condition)}_{variant}", (0, 70), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                                            ImGui.text_colored(upgrade_label, rarity_color.color_tuple, font_size=14)
                                            ImGui.separator()
                                            for item_type in item_types:
                                                is_upgrade_selected = any(isinstance(existing_upgrade.upgrade, upgrade_type) and item_type in existing_upgrade.item_types for existing_upgrade in condition.weapon_upgrades)
                                                texture = ui.weapon_upgrade_textures.get(item_type)
                                                if texture:
                                                    ImGui.image_toggle_button(f"##{id(condition)}_{variant}_{item_type.name}", texture.prefix if ui.mod_type == ItemUpgradeType.Prefix else texture.suffix, is_upgrade_selected, 24, 24)
                                                    encoded = upgrade.create_upgrade_name(item_type)
                                                    if PyImGui.is_item_clicked(0):
                                                        io = PyImGui.get_io()
                                                        existing_entry = next((existing_upgrade for existing_upgrade in condition.weapon_upgrades if isinstance(existing_upgrade.upgrade, upgrade_type)), None)
                                                        if io.key_ctrl:
                                                            should_select_all = not is_upgrade_selected
                                                            if should_select_all:
                                                                if existing_entry:
                                                                    existing_entry.item_types.clear()
                                                                    existing_entry.item_types.extend(item_types)
                                                                else:
                                                                    condition.weapon_upgrades.append(UpgradeAndItemType(upgrade=upgrade, item_types=list(item_types)))
                                                            elif existing_entry:
                                                                condition.weapon_upgrades.remove(existing_entry)
                                                        else:
                                                            if existing_entry and item_type in existing_entry.item_types:
                                                                existing_entry.item_types.remove(item_type)
                                                                if not existing_entry.item_types:
                                                                    condition.weapon_upgrades.remove(existing_entry)
                                                            elif existing_entry:
                                                                existing_entry.item_types.append(item_type)
                                                            else:
                                                                condition.weapon_upgrades.append(UpgradeAndItemType(upgrade=upgrade, item_types=[item_type]))
                                                        changed = True
                                                    ImGui.show_tooltip(encoded.plain if encoded else ui._humanize_name(item_type.name))
                                                    hovered = hovered or PyImGui.is_item_hovered()
                                                    PyImGui.same_line(0, 5)
                                        ImGui.end_child()
                                        if not hovered:
                                            ImGui.show_tooltip(upgrade.description_plain)
                                    else:
                                        ImGui.dummy(0, 70)
                                else:
                                    is_upgrade_selected = any(isinstance(existing_upgrade.upgrade, upgrade_type) for existing_upgrade in condition.weapon_upgrades)
                                    if PyImGui.is_rect_visible(10, 25):
                                        if ImGui.begin_selectable(f"##weapon_upgrade_{id(condition)}_{upgrade_type.__name__}", is_upgrade_selected, (0, 25)):
                                            rarity_color = UI._get_rarity_color(upgrade.rarity)
                                            ImGui.text_colored(upgrade_label, rarity_color.color_tuple, font_size=14)
                                        if ImGui.end_selectable():
                                            if is_upgrade_selected:
                                                condition.weapon_upgrades = [existing_upgrade for existing_upgrade in condition.weapon_upgrades if not isinstance(existing_upgrade.upgrade, upgrade_type)]
                                            else:
                                                condition.weapon_upgrades.append(UpgradeAndItemType(upgrade=upgrade, item_types=[]))
                                            changed = True
                                        ImGui.show_tooltip(upgrade.description_plain)
                                    else:
                                        ImGui.dummy(0, 25)
                    ImGui.end_child()
                    style.ToggleButtonDisabled.pop_color()
                    style.ToggleButtonEnabled.pop_color()
                    ImGui.end_table()
            UI.ConditionEditor.EndConditionContainer()
            return changed

        @staticmethod
        def ForUpgradeRangesCondition(ui: "UI", rule: Rule, condition: UpgradeRangesCondition, size: Optional[tuple[float, float]] = None) -> bool:
            changed = False
            popup_id = f"##upgrade_range_add_popup_{id(condition)}"
            if UI.ConditionEditor.BeginConditionContainer(ui, rule, condition, size):
                if ImGui.button("Add Range Upgrade", -1):
                    ui.upgrade_range_search = ""
                    PyImGui.open_popup(popup_id)

                PyImGui.set_next_window_size((300, 0), cond=PyImGui.ImGuiCond.Appearing)
                if PyImGui.begin_popup(popup_id):
                    ImGui.text("Add Upgrade Range Rule")
                    ImGui.separator()
                    PyImGui.set_next_item_width(-1)
                    _, ui.upgrade_range_search = ImGui.search_field(f"##upgrade_range_search_{id(condition)}", ui.upgrade_range_search, "Search Upgrades...")
                    search_query = ui._normalize_search_query(ui.upgrade_range_search)

                    if ImGui.begin_child(f"##upgrade_range_candidates_{id(condition)}", (0, 300), border=True):
                        for upgrade_type, instruction in ui._get_range_upgrade_options():
                            upgrade = upgrade_type()
                            option_label = ui._format_upgrade_label(upgrade)
                            if not ui._search_text_matches(search_query, option_label, upgrade.description_plain):
                                continue
                            already_selected = any(isinstance(existing.upgrade, upgrade_type) and existing.target == instruction.target for existing in condition.upgrade_ranges)
                            if ImGui.begin_selectable(f"##upgrade_range_option_{id(condition)}_{upgrade_type.__name__}_{instruction.target}", False, (0, 36)):
                                rarity_color = UI._get_rarity_color(upgrade.rarity)
                                ImGui.text_colored(option_label, rarity_color.color_tuple, font_size=14)
                                x, y = PyImGui.get_cursor_pos()
                                PyImGui.set_cursor_pos(x, y - 4)
                                ImGui.text_colored(f"{instruction.target}: {instruction.min_value} - {instruction.max_value}" + ("%" if instruction.target == "chance" else ""), UI.GRAY_COLOR.color_tuple, font_size=12)
                            if ImGui.end_selectable() and not already_selected:
                                condition.upgrade_ranges.append(RangedUpgrade(upgrade=upgrade, target=instruction.target, min_value=float(instruction.min_value), max_value=float(instruction.max_value), item_types=[]))
                                changed = True
                                PyImGui.close_current_popup()
                            if PyImGui.is_item_hovered():
                                ImGui.show_tooltip(upgrade.description_plain)
                    ImGui.end_child()
                    if ImGui.button("Cancel", -1):
                        PyImGui.close_current_popup()
                    PyImGui.end_popup()

                ImGui.separator()
                style = ImGui.get_style()
                style.ToggleButtonEnabled.push_color(ui._get_rarity_color(Rarity.Gold).opacity(0.85).rgb_tuple)
                style.ToggleButtonDisabled.push_color((0, 0, 0, 85))
                for index, upgrade_range in enumerate(condition.upgrade_ranges):
                    unique_id = f"upgrade_range_condition_{id(condition)}_{index}"
                    instruction = ui._get_range_instruction(upgrade_range.upgrade, upgrade_range.target)
                    if instruction is None:
                        continue
                    if ImGui.begin_child(f"##{unique_id}", (0, 100), border=True):
                        style.CellPadding.push_style_var_direct(4, 4)
                        if ImGui.begin_table(f"##{unique_id}_table", 3, PyImGui.TableFlags.NoBordersInBody):
                            PyImGui.table_setup_column("Name", PyImGui.TableColumnFlags.WidthFixed, 200)
                            PyImGui.table_setup_column("ItemTypes", PyImGui.TableColumnFlags.WidthStretch)
                            PyImGui.table_setup_column("Delete", PyImGui.TableColumnFlags.WidthFixed, 50)
                            PyImGui.table_next_row()
                            PyImGui.table_next_column()
                            rarity_color = UI._get_rarity_color(upgrade_range.upgrade.rarity)
                            ImGui.text_colored(ui._format_upgrade_label(upgrade_range.upgrade), rarity_color.color_tuple, font_size=14)
                            PyImGui.table_next_column()
                            item_types = ui._get_allowed_item_types(upgrade_range.upgrade)
                            if item_types:
                                style.ChildBg.push_color_direct((0, 0, 0, 80))
                                style.WindowPadding.push_style_var_direct(4, 4)
                                if ImGui.begin_child(f"##{unique_id}_item_types", (0, 32), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
                                    for item_type in item_types:
                                        is_upgrade_selected = any(isinstance(existing_upgrade.upgrade, type(upgrade_range.upgrade)) and item_type in existing_upgrade.item_types for existing_upgrade in condition.upgrade_ranges)
                                        texture = ui.weapon_upgrade_textures.get(item_type)
                                        if texture:
                                            ImGui.image_toggle_button(f"##{id(condition)}_{index}_{item_type.name}", texture.prefix if upgrade_range.upgrade.mod_type == ItemUpgradeType.Prefix else texture.suffix, is_upgrade_selected, 24, 24)
                                            encoded = upgrade_range.upgrade.create_upgrade_name(item_type)
                                            if PyImGui.is_item_clicked(0):
                                                io = PyImGui.get_io()
                                                existing_entry = next((existing_upgrade for existing_upgrade in condition.upgrade_ranges if isinstance(existing_upgrade.upgrade, type(upgrade_range.upgrade))), None)
                                                if io.key_ctrl:
                                                    should_select_all = not is_upgrade_selected
                                                    if should_select_all:
                                                        if existing_entry:
                                                            existing_entry.item_types.clear()
                                                            existing_entry.item_types.extend(item_types)
                                                        else:
                                                            condition.upgrade_ranges.append(RangedUpgrade(upgrade=upgrade_range.upgrade, target=upgrade_range.target, min_value=upgrade_range.min_value, max_value=upgrade_range.max_value, item_types=list(item_types)))
                                                else:
                                                    if existing_entry and item_type in existing_entry.item_types:
                                                        existing_entry.item_types.remove(item_type)
                                                    elif existing_entry:
                                                        existing_entry.item_types.append(item_type)
                                                    else:
                                                        condition.upgrade_ranges.append(RangedUpgrade(upgrade=upgrade_range.upgrade, target=upgrade_range.target, min_value=upgrade_range.min_value, max_value=upgrade_range.max_value, item_types=[item_type]))
                                                changed = True
                                            ImGui.show_tooltip(encoded.plain if encoded else ui._humanize_name(item_type.name))
                                            PyImGui.same_line(0, 5)
                                ImGui.end_child()
                                style.WindowPadding.pop_style_var()
                                style.ChildBg.pop_color_direct()
                            PyImGui.table_next_column()
                            if ImGui.icon_button(f"{IconsFontAwesome5.ICON_TRASH}##{unique_id}", 40, 40):
                                condition.upgrade_ranges.pop(index)
                                changed = True
                            ImGui.end_table()
                        style.CellPadding.pop_style_var()

                        ImGui.separator()
                        value_is_int = isinstance(instruction.min_value, int) and isinstance(instruction.max_value, int)
                        current_min = int(upgrade_range.min_value) if value_is_int else upgrade_range.min_value
                        current_max = int(upgrade_range.max_value) if value_is_int else upgrade_range.max_value
                        width = PyImGui.get_content_region_avail()[0]
                        PyImGui.push_item_width(width / 2 - 10)
                        if value_is_int:
                            new_min = ImGui.slider_int(f"##Minimum##{unique_id}", int(current_min), int(instruction.min_value), int(instruction.max_value))
                            if PyImGui.is_item_hovered():
                                upgrade_range.upgrade.__setattr__(upgrade_range.target, new_min)
                                ImGui.show_tooltip(upgrade_range.upgrade.description_plain)
                            PyImGui.same_line(0, 8)
                            new_max = ImGui.slider_int(f"###Maximum##{unique_id}", int(current_max), int(instruction.min_value), int(instruction.max_value))
                            if PyImGui.is_item_hovered():
                                upgrade_range.upgrade.__setattr__(upgrade_range.target, new_max)
                                ImGui.show_tooltip(upgrade_range.upgrade.description_plain)
                        else:
                            new_min = ImGui.slider_float(f"###Minimum##{unique_id}", current_min, float(instruction.min_value), float(instruction.max_value))
                            PyImGui.same_line(0, 8)
                            new_max = ImGui.slider_float(f"##Maximum##{unique_id}", current_max, float(instruction.min_value), float(instruction.max_value))
                        PyImGui.pop_item_width()

                        new_min_value = min(new_min, new_max)
                        new_max_value = max(new_min, new_max)
                        if new_min_value != upgrade_range.min_value or new_max_value != upgrade_range.max_value:
                            condition.upgrade_ranges[index] = RangedUpgrade(upgrade=upgrade_range.upgrade, target=upgrade_range.target, min_value=float(new_min_value), max_value=float(new_max_value), item_types=upgrade_range.item_types)
                            changed = True
                    ImGui.end_child()
                style.ToggleButtonDisabled.pop_color()
                style.ToggleButtonEnabled.pop_color()
                
            UI.ConditionEditor.EndConditionContainer()
            return changed

    def _draw_condition_editor(self, rule: Rule, condition: Condition, size: Optional[tuple[float, float]] = None) -> bool:
        draw_size = size if size is not None else (0, 0)
        
        match condition:
            case ModelIdsCondition():
                return UI.ConditionEditor.ForModelIdsCondition(self, rule, condition, draw_size)
            
            case ItemTypesCondition():
                return UI.ConditionEditor.ForItemTypesCondition(self, rule, condition, draw_size)
            
            case EncodedNamesCondition():
                return UI.ConditionEditor.ForEncodedNamesCondition(self, rule, condition, draw_size)
            
            case ModelFileIdsCondition():
                return UI.ConditionEditor.ForModelFileIdsCondition(self, rule, condition, draw_size)
            
            case ModelFileIdsAndItemTypesCondition():
                return UI.ConditionEditor.ForModelFileIdsAndItemTypesCondition(self, rule, condition, draw_size)
            
            case ModelIdsAndItemTypesCondition():
                return UI.ConditionEditor.ForModelIdsAndItemTypesCondition(self, rule, condition, draw_size)
            
            case ExactItemTypeCondition():
                return UI.ConditionEditor.ForExactItemTypeCondition(self, rule, condition, draw_size)
            
            case RaritiesCondition():
                return UI.ConditionEditor.ForRaritiesCondition(self, rule, condition, draw_size)
            
            case DyeColorsCondition():
                return UI.ConditionEditor.ForDyeColorsCondition(self, rule, condition, draw_size)
            
            case SalvagesToMaterialsCondition():
                return UI.ConditionEditor.ForSalvagesToMaterialsCondition(self, rule, condition, draw_size)
            
            case WeaponRequirementCondition():
                return UI.ConditionEditor.ForWeaponRequirementCondition(self, rule, condition, draw_size)
            
            case InherentFiltersCondition():
                return UI.ConditionEditor.ForInherentFiltersCondition(self, rule, condition, draw_size)
            
            case InscribableCondition():
                return UI.ConditionEditor.ForInscribableCondition(self, rule, condition, draw_size)
            
            case UnidentifiedCondition():
                return UI.ConditionEditor.ForUnidentifiedCondition(self, rule, condition, draw_size)
            
            case ArmorUpgradesCondition():
                return UI.ConditionEditor.ForArmorUpgradesCondition(self, rule, condition, draw_size)
            
            case MaxWeaponUpgradesCondition():
                return UI.ConditionEditor.ForMaxWeaponUpgradesCondition(self, rule, condition, draw_size)
            
            case UpgradeRangesCondition():
                return UI.ConditionEditor.ForUpgradeRangesCondition(self, rule, condition, draw_size)
            
            case _:
                ImGui.text("No editor available for this condition.")
                return False

    def _supports_custom_condition_editor(self, condition_type: type[Condition]) -> bool:
        supported_types = (
            ModelIdsCondition,
            EncodedNamesCondition,
            ModelFileIdsCondition,
            ModelFileIdsAndItemTypesCondition,
            ModelIdsAndItemTypesCondition,
            ItemTypesCondition,
            ExactItemTypeCondition,
            RaritiesCondition,
            DyeColorsCondition,
            SalvagesToMaterialsCondition,
            WeaponRequirementCondition,
            InherentFiltersCondition,
            InscribableCondition,
            UnidentifiedCondition,
            ArmorUpgradesCondition,
            MaxWeaponUpgradesCondition,
            UpgradeRangesCondition,
        )
        return issubclass(condition_type, supported_types)

    def _draw_custom_rule(self, rule: CustomRule) -> bool:
        changed = False
        PyImGui.set_next_item_width(180)
        if PyImGui.begin_combo(f"##custom_rule_operator_{id(rule)}", self._humanize_name(rule.condition_operator.name), PyImGui.ImGuiComboFlags.NoFlag):
            for operator in ConditionOperator:
                if ImGui.selectable(self._humanize_name(operator.name), selected=rule.condition_operator == operator):
                    rule.condition_operator = operator
                    changed = True
            ImGui.end_combo()
        ImGui.show_tooltip("Choose whether all conditions must match or whether any single condition is enough.")

        PyImGui.same_line(0, 8)
        if PyImGui.begin_combo(f"##custom_rule_add_condition_{id(rule)}", "Add Condition", PyImGui.ImGuiComboFlags.NoFlag):
            existing_condition_types = {type(condition) for condition in rule.conditions}
            for condition_type in self._get_condition_types():
                if not self._supports_custom_condition_editor(condition_type):
                    continue
                if condition_type in existing_condition_types:
                    continue

                if ImGui.selectable(self._humanize_name(condition_type.__name__), False):
                    rule.conditions.append(condition_type())
                    changed = True
                self._show_wrapped_tooltip(self._format_condition_type_tooltip(condition_type))
            ImGui.end_combo()

        ImGui.separator()
        if not rule.conditions:
            ImGui.text_wrapped("Add one or more conditions to build a custom rule.")
            return changed

        for condition in rule.conditions:
            if self._draw_condition_editor(rule, condition, size=(0, 300)):
                changed = True
                
        return changed

    def _draw_rule_body(self, rule: Rule) -> bool:
        PyImGui.spacing()
        
        match rule:
            case CustomRule():
                ImGui.text_wrapped("Build this rule from reusable condition sections. Add any supported conditions, reorder the rule itself in the list, and choose whether all or any conditions must match.")
                return self._draw_custom_rule(rule)

            case ModelIdsRule():
                ImGui.text_wrapped("This rule matches items based on their model IDs. You can specify one or more model IDs to match against the item.")
                return UI.ConditionEditor.ForModelIdsCondition(self, rule, rule.condition)

            case EncodedNameRule():
                ImGui.text_wrapped("This rule matches items by their encoded item name. You can add values from the item database or paste a raw encoded name string.")
                return UI.ConditionEditor.ForEncodedNamesCondition(self, rule, rule.condition)

            case ModelFileIdRule():
                ImGui.text_wrapped("This rule matches items based on their model file ID. You can add values from known item data or enter raw ids manually.")
                return UI.ConditionEditor.ForModelFileIdsCondition(self, rule, rule.condition)

            case ModelFileIdAndItemTypeRule():
                ImGui.text_wrapped("This rule matches items using a combination of model file ID and item type.")
                return UI.ConditionEditor.ForModelFileIdsAndItemTypesCondition(self, rule, rule.condition)

            case UnidentifiedRule():
                ImGui.text_wrapped("This rule matches unidentified items.")
                return UI.ConditionEditor.ForUnidentifiedCondition(self, rule, rule.condition)
            
            case UnidentifiedAndRarityRule():
                ImGui.text_wrapped("This rule matches unidentified items of specific rarities.")
                changed = False
                
                changed = self._draw_condition_editor(rule, rule.conditions[0], size=(0, 60)) or changed
                changed = self._draw_condition_editor(rule, rule.conditions[1], size=(0, 0)) or changed

                return changed

            case WeaponSkinRule():
                ImGui.text_wrapped("This rule matches weapon skins by model file id, with configurable requirement damage ranges and optional inherent upgrade filters.")
                
                avail = PyImGui.get_content_region_avail()
                width = (avail[0] - 5) * 0.5
                height = avail[1]
                changed = False
                
                for condition in rule.conditions:
                    changed = self._draw_condition_editor(rule, condition, size=(width, height)) or changed
                    PyImGui.same_line(0, 5)

                return changed

            case WeaponTypeRule():
                ImGui.text_wrapped("This rule matches a weapon type, with configurable requirement damage ranges and optional inherent upgrade filters.")
                avail = PyImGui.get_content_region_avail()
                width = (avail[0] - 5) * 0.5
                height = avail[1]
                changed = False
                
                for condition in rule.conditions:
                    changed = self._draw_condition_editor(rule, condition, size=(width, height)) or changed
                    PyImGui.same_line(0, 5)

                return changed

            case SalvagesToMaterialRule():
                ImGui.text_wrapped("This rule matches items that can salvage into any of the selected materials. We rely on the scraped salvage data from the GW-Wiki which is stored in our ITEM_DATA.")
                return UI.ConditionEditor.ForSalvagesToMaterialsCondition(self, rule, rule.condition)

            case ModelIdsAndItemTypesRule():
                ImGui.text_wrapped("This rule matches items based on their model id and item type. You can specify one or more model id and item type pairs to match against the item.")
                return UI.ConditionEditor.ForModelIdsAndItemTypesCondition(self, rule, rule.condition)

            case ItemTypesRule():
                ImGui.text_wrapped("This rule matches items based on their item types. You can specify one or more item types to match against the item.")
                return UI.ConditionEditor.ForItemTypesCondition(self, rule, rule.condition)

            case RaritiesRule():
                ImGui.text_wrapped("This rule matches items based on their rarity. You can specify one or more rarities to match against the item.")
                return UI.ConditionEditor.ForRaritiesCondition(self, rule, rule.condition)

            case RaritiesAndItemTypesRule():
                ImGui.text_wrapped("This rule matches items based on a combination of rarity and item type. You can specify pairs of rarities and item types to match against the item.")
                
                avail = PyImGui.get_content_region_avail()
                rarity_width = min((avail[0] - 5) * 0.5, 200)
                item_type_width = avail[0] - rarity_width - 5
                height = avail[1]
                changed = False
                
                changed = UI.ConditionEditor.ForRaritiesCondition(self, rule, rule._rarity_condition(), size=(rarity_width, height)) or changed
                PyImGui.same_line(0, 5)
                changed = UI.ConditionEditor.ForItemTypesCondition(self, rule, rule._item_type_condition(), size=(item_type_width, height)) or changed

                return changed
            
            case DyesRule():
                ImGui.text_wrapped("This rule matches items based on their dye color. You can specify one or more dye colors to match against the item.")
                return UI.ConditionEditor.ForDyeColorsCondition(self, rule, rule.condition)

            case ArmorUpgradeRule():
                ImGui.text_wrapped("This rule matches items based on their armor upgrades. You can specify one or more armor upgrades to match against the item.")
                return UI.ConditionEditor.ForArmorUpgradesCondition(self, rule, rule.condition)

            case MaxWeaponUpgradeRule():
                ImGui.text_wrapped("This rule matches items based on their weapon upgrades. You can specify one or more weapon upgrades to match against the item.")
                return UI.ConditionEditor.ForMaxWeaponUpgradesCondition(self, rule, rule.condition)

            case UpgradeRangeRule():
                ImGui.text_wrapped("This rule matches items based on their upgrades that have a numeric value within a specified range.")
                return UI.ConditionEditor.ForUpgradeRangesCondition(self, rule, rule.condition)

            case _:
                ImGui.text("No editor available for this rule type.")
                return False

    def draw_rule(self, rule: Rule):
        self._draw_rule_header(rule)
        if self._draw_rule_body(rule):
            self._save_active_config()
