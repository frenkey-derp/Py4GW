from argparse import Action
import re
import webbrowser

from Widgets.frenkey.LootEx import profile, settings, data, price_check, item_configuration, utility, enum, cache, ui_manager_extensions, inventory_handling, wiki_scraper, filter, models, messaging, data_collector,wiki_scraper
from Widgets.frenkey.LootEx.item_configuration import ItemConfiguration, ConfigurationCondition
from Widgets.frenkey.LootEx.filter import Filter
from Widgets.frenkey.LootEx.profile import Profile
from Widgets.frenkey.LootEx.ui_manager_extensions import UIManagerExtensions
from Py4GWCoreLib import *

import ctypes
from ctypes import windll

import importlib

from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
importlib.reload(settings)
importlib.reload(data)
importlib.reload(enum)
importlib.reload(models)
importlib.reload(price_check)
importlib.reload(profile)
importlib.reload(item_configuration)
importlib.reload(utility)
importlib.reload(cache)
importlib.reload(ui_manager_extensions)
importlib.reload(inventory_handling)
importlib.reload(wiki_scraper)
importlib.reload(filter)


class SelectableItem:
    """
    Represents an item that can be selected and hovered over in a GUI.
    Attributes:
        item_info (data.Item): The information about the item.
        is_selected (bool): Indicates whether the item is currently selected. Defaults to False.
        is_hovered (bool): Indicates whether the item is currently being hovered over. Defaults to False.
    Methods:
        __str__(): Returns a string representation of the SelectableItem instance.
        __repr__(): Returns a string representation of the SelectableItem instance (same as __str__).
    """

    def __init__(self, item: models.Item, is_selected: bool = False):
        self.item_info: models.Item = item
        self.is_selected: bool = is_selected
        self.is_hovered: bool = False
        self.is_clicked: bool = False
        self.time_stamp : datetime = datetime.min

    def __str__(self):
        return f"SelectableItem(item={self.item_info}, is_selected={self.is_selected})"

    def __repr__(self):
        return self.__str__()

class SelectableWrapper:
    """
    Represents a selectable wrapper for an object, allowing it to be selected and hovered over in a GUI.
    Attributes:
        object (object): The object to be wrapped.
        is_selected (bool): Indicates whether the object is currently selected. Defaults to False.
        is_hovered (bool): Indicates whether the object is currently being hovered over. Defaults to False.
    """

    def __init__(self, object, is_selected: bool = False):
        self.object = object
        self.is_selected: bool = is_selected
        self.is_hovered: bool = False

class ItemFilter:
    def __init__(self, name: str, lambda_function: Callable[[models.Item], bool]):
        self.name: str = name
        self.lambda_function: Callable[[models.Item], bool] = lambda_function
        pass
    
    def match(self, item: models.Item) -> bool:
        """
        Checks if the item matches the filter criteria.
        
        Args:
            item (models.Item): The item to check against the filter.
        
        Returns:
            bool: True if the item matches the filter, False otherwise.
        """
        
        return self.lambda_function(item)
    
class UI:
    _instance = None
    
    class COLORS(IntEnum):
        TEXT = Utils.RGBToColor(255, 255, 255, 255)
        RARE_WEAPONS_TEXT = Utils.RGBToColor(251, 62, 141, 255)
        RARE_WEAPONS_FRAME = Utils.RGBToColor(251, 62, 141, 75)
        RARE_WEAPONS_FRAME_HOVERED = Utils.RGBToColor(251, 62, 141, 125)
        LOW_REQ_WEAPONS_TEXT = Utils.RGBToColor(242, 136, 22, 255)
        LOW_REQ_WEAPONS_FRAME = Utils.RGBToColor(242, 136, 22, 75)
        LOW_REQ_WEAPONS_FRAME_HOVERED = Utils.RGBToColor(242, 136, 22, 125)
        INFO_ICON = Utils.RGBToColor(245,172,
                                     47, 255)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UI, cls).__new__(cls)
        
        return cls._instance
    
    def __init__(self):       
        # self.cached_item = cache.Cached_Item(1401) 
        file_directory = os.path.dirname(os.path.abspath(__file__))
        self.icon_textures_path = os.path.join(file_directory, "textures")
        self.item_textures_path = os.path.join(utility.Util.GetPy4GWPath(), "Textures", "Items")
        self.actions_timer = ThrottledTimer()
        self.action_summary: inventory_handling.InventoryHandler.ActionsSummary | None = None
        self.action_textures: dict[enum.ItemAction, str] = {   
            # enum.ItemAction.NONE: os.path.join(self.item_textures_path, "Data_Collector.png"),        
            enum.ItemAction.LOOT: os.path.join(self.item_textures_path, "Bag.png"),       
            enum.ItemAction.COLLECT_DATA: os.path.join(self.icon_textures_path, "wiki_logo.png"),      
            enum.ItemAction.IDENTIFY: os.path.join(self.item_textures_path, "Identification_Kit.png"),      
            enum.ItemAction.STASH: os.path.join(self.icon_textures_path, "xunlai_chest.png"),      
            enum.ItemAction.SALVAGE_MODS: os.path.join(self.item_textures_path, "Inscription_equippable_items.png"),
            enum.ItemAction.SALVAGE: os.path.join(self.item_textures_path, "Salvage_Kit.png"),
            enum.ItemAction.SALVAGE_SMART: os.path.join(self.icon_textures_path, "expert_or_common_salvage_kit.png"),
            enum.ItemAction.SALVAGE_RARE_MATERIALS: os.path.join(self.item_textures_path, "Steel_Ingot.png"),  
            enum.ItemAction.SALVAGE_COMMON_MATERIALS: os.path.join(self.item_textures_path, "Iron_Ingot.png"),
            enum.ItemAction.SELL_TO_MERCHANT: os.path.join(self.item_textures_path, "Gold.png"),
            enum.ItemAction.SELL_TO_TRADER: os.path.join(self.item_textures_path, "Gold.png"),
            enum.ItemAction.DESTROY: os.path.join(self.icon_textures_path, "destroy.png"),
            enum.ItemAction.DEPOSIT_MATERIAL: os.path.join(self.icon_textures_path, "xunlai_chest.png"),
        }
        self.py_io = PyImGui.get_io()
        self.selected_loot_items: list[SelectableItem] = []
        
        self.inventory_view: bool = True
        self.item_search: str = ""
        self.filtered_loot_items: list[SelectableItem] = []        
        self.filtered_blacklist_items: list[SelectableItem] = []       
        
        self.selected_condition: Optional[ConfigurationCondition] = None
        self.filter_name: str = ""
        self.condition_name: str = ""
        self.new_profile_name: str = ""
        self.mod_search: str = ""
        
        self.filtered_weapon_mods: list[SelectableWrapper] = []
        
        self.scroll_bar_visible: bool = False
        self.trader_type: str = ""
        
        self.entered_price_threshold: int = 1000
        self.mark_to_sell_runes: bool = False
        
        self.show_price_check_popup: bool = False
        self.show_add_filter_popup: bool = False
        self.show_add_profile_popup: bool = False
        self.show_delete_profile_popup: bool = False
        self.first_draw: bool = True
        self.window_flags: int = PyImGui.WindowFlags.NoFlag
        self.weapon_types = [
            ItemType.Axe,
            ItemType.Sword,
            ItemType.Spear,
            ItemType.Wand,
            ItemType.Daggers,
            ItemType.Hammer,
            ItemType.Scythe,
            ItemType.Bow,
            ItemType.Staff,
            ItemType.Offhand,
            ItemType.Shield,
        ]

        self.prefix_names = ["Any"]
        self.suffix_names = ["Any"]
        self.inherent_names = ["Any"]
        self.inventory_coords: Optional[settings.FrameCoords] = None
        
        self.mod_textures : dict[ItemType, dict[enum.ModType, str]] = {
            ItemType.Axe: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Axe_Haft.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Axe_Grip.png"),
            },
            ItemType.Bow: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Bow_String.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Bow_Grip.png"),
            },
            ItemType.Offhand: {
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Focus_Core.png"),
            },
            ItemType.Hammer: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Hammer_Haft.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Hammer_Grip.png"),
            },
            ItemType.Wand: {
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Wand_Wrapping.png"),
            },
            ItemType.Shield: {
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Shield_Handle.png"),                        
            },
            ItemType.Staff: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Staff_Head.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Staff_Wrapping.png"),
            },
            ItemType.Sword: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Sword_Hilt.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Sword_Pommel.png"),
            },
            ItemType.Daggers: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Dagger_Tang.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Dagger_Handle.png"),
            },
            ItemType.Spear: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Spearhead.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Spear_Grip.png"),
            },
            ItemType.Scythe: {
                enum.ModType.Prefix: os.path.join(self.item_textures_path, "Scythe_Snathe.png"),
                enum.ModType.Suffix: os.path.join(self.item_textures_path, "Scythe_Grip.png"),
            },                            
        }
        
        self.item_type_textures: dict[ItemType, str] = {
            ItemType.Salvage: os.path.join(self.item_textures_path, "Salvage_Heavy_Armor.png"),
            ItemType.Axe: os.path.join(self.item_textures_path, "Great_Axe.png"),
            ItemType.Bag: os.path.join(self.item_textures_path, "Bag.png"),
            # ItemType.Boots: os.path.join(self.item_textures_path, "Boots.png"),
            ItemType.Bow: os.path.join(self.item_textures_path, "Ivory_Bow.png"),
            # ItemType.Bundle: os.path.join(self.item_textures_path, "Bundle.png"),
            # ItemType.Chestpiece: os.path.join(self.item_textures_path, "Chestpiece.png"),
            ItemType.Rune_Mod: os.path.join(self.item_textures_path, "Inscription_martial_weapons.png"),
            ItemType.Usable: os.path.join(self.item_textures_path, "Cr%C3%A8me_Br%C3%BBl%C3%A9e.png"),
            ItemType.Dye: os.path.join(self.item_textures_path, "White_Dye.png"),
            ItemType.Materials_Zcoins: os.path.join(self.item_textures_path, "Wood_Plank.png"),
            ItemType.Offhand: os.path.join(self.item_textures_path, "Channeling_Focus.png"),
            # ItemType.Gloves: os.path.join(self.item_textures_path, "Gloves.png"),
            ItemType.Hammer: os.path.join(self.item_textures_path, "PvP_Hammer.png"),
            # ItemType.Headpiece: os.path.join(self.item_textures_path, "Headpiece.png"),
            ItemType.CC_Shards: os.path.join(self.item_textures_path, "Candy_Cane_Shard.png"),
            ItemType.Key: os.path.join(self.item_textures_path, "Zaishen_Key.png"),
            # ItemType.Leggings: os.path.join(self.item_textures_path, "Leggings.png"),
            ItemType.Gold_Coin: os.path.join(self.item_textures_path, "Gold.png"),
            ItemType.Quest_Item: os.path.join(self.item_textures_path, "Top_Right_Map_Piece.png"),
            ItemType.Wand: os.path.join(self.item_textures_path, "Shaunur%27s_Scepter.png"),
            ItemType.Shield: os.path.join(self.item_textures_path, "Crude_Shield.png"),
            ItemType.Staff : os.path.join(self.item_textures_path, "Holy_Staff.png"),
            ItemType.Sword: os.path.join(self.item_textures_path, "Short_Sword.png"),
            ItemType.Kit: os.path.join(self.item_textures_path, "Superior_Salvage_Kit.png"),
            ItemType.Trophy: os.path.join(self.item_textures_path, "Destroyer_Core.png"),
            ItemType.Scroll: os.path.join(self.item_textures_path, "Scroll_of_the_Lightbringer.png"),
            ItemType.Daggers: os.path.join(self.item_textures_path, "Kris_Daggers.png"),
            ItemType.Present: os.path.join(self.item_textures_path, "Birthday_Present.png"),
            ItemType.Minipet: os.path.join(self.item_textures_path, "Miniature_Celestial_Tiger.png"),
            ItemType.Scythe: os.path.join(self.item_textures_path, "Suntouched_Scythe.png"),
            ItemType.Spear: os.path.join(self.item_textures_path, "Suntouched_Spear.png"),
            ItemType.Weapon: os.path.join(self.item_textures_path, "Inscription_weapons.png"),
            ItemType.MartialWeapon: os.path.join(self.item_textures_path, "Inscription_martial_weapons.png"),
            ItemType.OffhandOrShield: os.path.join(self.item_textures_path, "Inscription_focus_items_or_shields.png"),
            ItemType.EquippableItem: os.path.join(self.item_textures_path, "Inscription_equippable_items.png"),
            ItemType.SpellcastingWeapon: os.path.join(self.item_textures_path, "Inscription_spellcasting_weapons.png"),
            # ItemType.Storybook: os.path.join(self.item_textures_path, "Young_Heroes_of_Tyria.png"),
            # ItemType.Costume: os.path.join(self.item_textures_path, "134px-Shining_Blade_costume.png"),
            # ItemType.Costume_Headpiece: os.path.join(self.item_textures_path, "Divine_Halo.png"),
            # ItemType.Unknown: os.path.join(self.item_textures_path, "Unknown_Item.png"),
        }
        
        self.bag_ranges : dict[str, tuple[Bag, Bag]] = {
            "Inventory": (Bag.Backpack, Bag.Bag_2),   
            "Equipped Items": (Bag.Equipped_Items, Bag.Equipped_Items),       
            "Equipment Pack": (Bag.Equipment_Pack, Bag.Equipment_Pack),       
        }
        for bag in Bag:
            if bag.value <= Bag.Bag_2.value:
                continue
            
            if bag == Bag.Max:
                continue
            
            key = utility.Util.reformat_string(bag.name)
            if key in self.bag_ranges:
                continue
            
            self.bag_ranges[key] = (bag, bag)

        self.bag_ranges["Merchant/Trader"] = (Bag.NoBag, Bag.NoBag)
        
        self.bag_names = [key for key in self.bag_ranges.keys()]
        self.bag_index = 0
        
        for mod in data.Weapon_Mods.values():
            if mod.mod_type == enum.ModType.Prefix:
                self.prefix_names.append(mod.name)

            elif mod.mod_type == enum.ModType.Suffix:
                self.suffix_names.append(mod.name)

            elif mod.mod_type == enum.ModType.Inherent:
                self.inherent_names.append(mod.name)

        self.filter_actions = [
            enum.ItemAction.LOOT,
            enum.ItemAction.STASH,
            enum.ItemAction.SALVAGE_SMART,
            enum.ItemAction.SALVAGE_COMMON_MATERIALS,
            enum.ItemAction.SALVAGE_RARE_MATERIALS,
            enum.ItemAction.SELL_TO_MERCHANT,
            enum.ItemAction.SELL_TO_TRADER,
            enum.ItemAction.DESTROY,
        ]
        
        self.filter_action_names = [
            "Loot (Pick Up)",
            "Stash",
            "Smart Salvage (Common or Rare Materials)",
            "Salvage for Common Materials",
            "Salvage for Rare Materials",
            "Sell to Merchant",
            "Sell to Trader (Scrolls, Dyes...)",
            "Destroy",
            ]
                
        self.item_actions = [
            enum.ItemAction.LOOT,
            enum.ItemAction.STASH,
            enum.ItemAction.SELL_TO_MERCHANT,
            enum.ItemAction.SALVAGE_SMART,
            enum.ItemAction.SALVAGE_COMMON_MATERIALS,
            enum.ItemAction.SALVAGE_RARE_MATERIALS,
            enum.ItemAction.DESTROY,
        ]
        self.item_action_names = [
            action.name for action in self.item_actions]
                
        
        self.os_low_req_itemtype_selectables: list[SelectableWrapper] = [
            SelectableWrapper(ItemType.Axe, False),
            SelectableWrapper(ItemType.Bow, False),
            SelectableWrapper(ItemType.Daggers, False),
            SelectableWrapper(ItemType.Hammer, False),
            SelectableWrapper(ItemType.Scythe, False),
            SelectableWrapper(ItemType.Spear, False),
            SelectableWrapper(ItemType.Sword, False),
            SelectableWrapper(ItemType.Staff, False),
            SelectableWrapper(ItemType.Wand, False),
            SelectableWrapper(ItemType.Offhand, False),
            SelectableWrapper(ItemType.Shield, False),
        ]
        
        self.mod_heights: dict[str, float] = {}
        self.sharedMemoryManager = Py4GWSharedMemoryManager()
        self.filter_popup = False

        self.action_heights: dict[enum.ItemAction, float] = {
                            enum.ItemAction.SALVAGE: 250,
                        }
        self.selected_filter: Optional[ItemFilter] = None
        self.filters : list[ItemFilter] = [
            ItemFilter("All Items", lambda item: True),
            ItemFilter("Weapons", lambda item: item.item_type in self.weapon_types),
            ItemFilter("Armor", lambda item: item.item_type in [
                ItemType.Chestpiece,
                ItemType.Headpiece,
                ItemType.Leggings,
                ItemType.Boots,
                ItemType.Gloves,
            ]),
            ItemFilter("Upgrades", lambda item: item.item_type == ItemType.Rune_Mod),
            ItemFilter("Consumables", lambda item: item.category == enum.ItemCategory.Alcohol or
                                                    item.category == enum.ItemCategory.Sweet or
                                                    item.category == enum.ItemCategory.Party or
                                                    item.category == enum.ItemCategory.DeathPenaltyRemoval),
            ItemFilter("Alcohol", lambda item: item.category == enum.ItemCategory.Alcohol),
            ItemFilter("Sweets", lambda item: item.category == enum.ItemCategory.Sweet),
            ItemFilter("Party", lambda item: item.category == enum.ItemCategory.Party),
            ItemFilter("Death Penalty Removal", lambda item: item.category == enum.ItemCategory.DeathPenaltyRemoval),
            ItemFilter("Scrolls", lambda item: item.category == enum.ItemCategory.Scroll),
            ItemFilter("Tomes", lambda item: item.category == enum.ItemCategory.Tome),
            ItemFilter("Keys", lambda item: item.category == enum.ItemCategory.Key),
            ItemFilter("Materials", lambda item: item.category == enum.ItemCategory.Material),
            ItemFilter("Trophies", lambda item: item.category == enum.ItemCategory.Trophy),
            ItemFilter("Reward Trophies", lambda item: item.category == enum.ItemCategory.RewardTrophy),
            ItemFilter("Quest Items", lambda item: item.category == enum.ItemCategory.QuestItem),    
        ]
        
        self.data_collector = data_collector.DataCollector()
        self.filter_weapon_mods()        
        self.filter_items()    
    
    def ensure_on_screen(self) -> bool:   
        if not self.py_io:
            return False
             
        adjusted = False
        screen_width = self.py_io.display_size_x
        screen_height = self.py_io.display_size_y
        min_remaining_space = 100
        
        out_of_max_bounds = (
            settings.current.window_position[0] + settings.current.window_size[0] + min_remaining_space > screen_width or
            settings.current.window_position[1] + settings.current.window_size[1] + (min_remaining_space / 2) > screen_height
        )
    
        if out_of_max_bounds:
            settings.current.window_position = (
                screen_width - settings.current.window_size[0], screen_height - settings.current.window_size[1])
            adjusted = True
        
        out_of_min_bounds = (
            settings.current.window_position[0] < 0 or
            settings.current.window_position[1] < 0
        )
        
        if out_of_min_bounds:
            settings.current.window_position = (
                max(0, settings.current.window_position[0]),
                max(0, settings.current.window_position[1])
            )
            adjusted = True
        
        bigger_than_screen = (
            settings.current.window_size[0] > screen_width or
            settings.current.window_size[1] > screen_height
        )
        
        if bigger_than_screen:
            settings.current.window_size = (
                min(settings.current.window_size[0], screen_width - 5),
                min(settings.current.window_size[1], screen_height - 5)
            )
            adjusted = True
        
        
        if settings.current.window_size[0] < 200 or settings.current.window_size[1] < 100:
            settings.current.window_size = (
                max(settings.current.window_size[0], 200),
                max(settings.current.window_size[1], 100)
            )
            
            adjusted = True
        
        
        return adjusted
    
    def show_main_window(self, ensure_on_screen: bool = False):        
        settings.current.window_visible = True
        
        if ensure_on_screen:
            if self.ensure_on_screen(): 
                PyImGui.set_next_window_pos(
                    settings.current.window_position[0], settings.current.window_position[1]
                )
                PyImGui.set_next_window_size(
                    settings.current.window_size[0], settings.current.window_size[1]
                )        
    
    def hide_main_window(self):        
        settings.current.window_visible = False
    
    def draw_window(self):        
        if self.first_draw:
            PyImGui.set_next_window_pos(
                settings.current.window_position[0], settings.current.window_position[1]
            )
            PyImGui.set_next_window_size(
                settings.current.window_size[0], settings.current.window_size[1]
            )
            PyImGui.set_next_window_collapsed(settings.current.window_collapsed, 0)
                
        if not settings.current.window_visible:
            return
        
        expanded, gui_open = PyImGui.begin_with_close(
            "Loot Ex", settings.current.window_visible, PyImGui.WindowFlags.NoFlag)
        
        if gui_open and settings.current.profile:
            self.window_flags = (
                PyImGui.WindowFlags.NoMove if PyImGui.is_mouse_down(
                    0) else PyImGui.WindowFlags.NoFlag
            )

            profile_names = [
                profile.name for profile in settings.current.profiles]
            profile_index = profile_names.index(settings.current.profile.name) if settings.current.profile else 0
            selected_index = PyImGui.combo(
                "", profile_index, profile_names)

            if profile_index != selected_index:
                ConsoleLog(
                    "LootEx",
                    f"Profile changed to {profile_names[selected_index]}",
                    Console.MessageType.Info,
                )
                settings.current.SetProfile(profile_names[selected_index])                
                settings.current.save()

            PyImGui.same_line(0, 5)

            if PyImGui.button(IconsFontAwesome5.ICON_PLUS):
                self.show_add_profile_popup = not self.show_add_profile_popup
                if self.show_add_profile_popup:
                    PyImGui.open_popup("Add Profile")
                else:
                    PyImGui.close_current_popup()

            ImGui.show_tooltip("Add New Profile")
            PyImGui.same_line(0, 5)

            if PyImGui.button((IconsFontAwesome5.ICON_TRASH)) and len(settings.current.profiles) > 1:
                self.show_delete_profile_popup = not self.show_delete_profile_popup
                if self.show_delete_profile_popup:
                    PyImGui.open_popup("Delete Profile")
                else:
                    PyImGui.close_current_popup()

            ImGui.show_tooltip("Delete Profile '" +
                            settings.current.profile.name + "'")
            PyImGui.same_line(0, 5)

            btnColor = Utils.RGBToColor(
                0, 255, 0, 255) if settings.current.automatic_inventory_handling else Utils.RGBToColor(255, 0, 0, 125)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(btnColor))

            if PyImGui.button((IconsFontAwesome5.ICON_PLAY_CIRCLE if settings.current.automatic_inventory_handling else
                            IconsFontAwesome5.ICON_PAUSE_CIRCLE)):
                settings.current.automatic_inventory_handling = not settings.current.automatic_inventory_handling
                settings.current.save()

            PyImGui.pop_style_color(1)
            ImGui.show_tooltip(
                ("Disable" if settings.current.automatic_inventory_handling else "Enable") + " Inventory Handling")

            PyImGui.same_line(0, 5)
            btnColor = Utils.RGBToColor(
                0, 255, 0, 255) if settings.current.collect_items else Utils.RGBToColor(255, 255, 255, 125)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(btnColor))

            if PyImGui.button(IconsFontAwesome5.ICON_LANGUAGE + IconsFontAwesome5.ICON_USER_SHIELD):
                settings.current.collect_items = not settings.current.collect_items
                settings.current.save()

            PyImGui.pop_style_color(1)
            ImGui.show_tooltip("Collect Items")

            if PyImGui.begin_tab_bar("LootExTabBar"):
                self.draw_general_settings()
                self.draw_filters()
                self.draw_loot_items()
                self.draw_weapon_mods()
                self.draw_runes()
                self.draw_old_school_tab()
                self.draw_blacklist()
                self.draw_data_collector_tab()

            PyImGui.end_tab_bar()

            pos = PyImGui.get_window_pos()
            size = PyImGui.get_window_size()

            if settings.current.window_position != (pos[0], pos[1]):
                # ConsoleLog(
                #     "LootEx",
                #     f"Window position changed to ({pos[0]}, {pos[1]})",
                #     Console.MessageType.Debug,
                # )
                settings.current.window_position = (pos[0], pos[1])
                settings.current.save()

            if settings.current.window_size != (size[0], size[1]) and expanded:
                # ConsoleLog(
                #     "LootEx",
                #     f"Window size changed to ({size[0]}, {size[1]})",
                #     Console.MessageType.Debug,
                # )
                self.mod_heights.clear()
                settings.current.window_size = (size[0], size[1])
                settings.current.save()

            self.draw_delete_profile_popup()
            self.draw_profiles_popup()

            PyImGui.end()

        collapsed = not expanded

        if collapsed != settings.current.window_collapsed:
            settings.current.window_collapsed = collapsed
            settings.current.save()

        if gui_open != settings.current.window_visible:
            settings.current.window_visible = gui_open
            settings.current.manual_window_visible = gui_open
            settings.current.save()

        self.first_draw = False
  
    def draw_vault_controls(self):    
        if not UIManager.IsWindowVisible(WindowID.WindowID_VaultBox):
            return
        
        storage_id = UIManager.GetFrameIDByHash(2315448754)  # "Xunlai Storage" frame hash
        
        if not UIManagerExtensions.IsElementVisible(storage_id):
            return
        
        coords = settings.FrameCoords(storage_id)  # "Xunlai Window" frame hash

        if coords is None:
            return
        
        width = 30
        PyImGui.set_next_window_pos(coords.right - (width) - 20, coords.top + 50)
        PyImGui.set_next_window_size(width, 0)
        PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,
                                    Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)    
        if PyImGui.begin(
            "Loot Ex Vault Controls",
            PyImGui.WindowFlags.NoTitleBar
            | PyImGui.WindowFlags.NoResize
            | PyImGui.WindowFlags.NoBackground
            | PyImGui.WindowFlags.AlwaysAutoResize
            | PyImGui.WindowFlags.NoCollapse
            | PyImGui.WindowFlags.NoMove
            | PyImGui.WindowFlags.NoSavedSettings,
        ):
            PyImGui.pop_style_var(1)
            PyImGui.pop_style_color(1)

            if UI.transparent_button(IconsFontAwesome5.ICON_TH, True, width, width):
                imgui_io = self.py_io
                if imgui_io.key_ctrl:
                    # messaging.SendOpenXunlai(imgui_io.key_shift)
                    pass
                else:
                    inventory_handling.InventoryHandler().CondenseStacks(Bag.Storage_1, Bag.Storage_14)

            ImGui.show_tooltip("Condense items to full stacks" +
                            "\nHold Ctrl to send message to all accounts" +
                            "\nHold Shift to send message to all accounts excluding yourself")

            PyImGui.end()

    def draw_inventory_controls(self):    
        if not UIManager.IsWindowVisible(WindowID.WindowID_InventoryBags):
            if self.inventory_coords is not None:
                self.inventory_coords = None
            return
        
        self.inventory_coords = settings.FrameCoords(UIManager.GetFrameIDByHash(291586130))

        if self.inventory_coords is None:
            return

        width = 30
        PyImGui.set_next_window_pos(self.inventory_coords.left - (width - 5), self.inventory_coords.top)
        PyImGui.set_next_window_size(width, 0)
        PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,
                                Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)

        if PyImGui.begin(
            "Loot Ex Inventory Controls",
            PyImGui.WindowFlags.NoTitleBar
            | PyImGui.WindowFlags.NoResize
            | PyImGui.WindowFlags.NoBackground
            | PyImGui.WindowFlags.AlwaysAutoResize
            | PyImGui.WindowFlags.NoCollapse
            | PyImGui.WindowFlags.NoMove
            | PyImGui.WindowFlags.NoSavedSettings,
        ):
            PyImGui.pop_style_var(1)
            PyImGui.pop_style_color(1)

            self._draw_inventory_toggle_button(width)
            self._draw_date_collection_toggle_button(width)
            self._draw_manual_window_toggle_button(width)
            self._draw_xunlai_storage_button(width)

            PyImGui.end()

        if settings.current.manual_window_visible:
            if not settings.current.window_visible:
                self.show_main_window(True)
        else:
            self.hide_main_window()
            
    def _draw_inventory_toggle_button(self, width):
        if UI.transparent_button(IconsFontAwesome5.ICON_CHECK, settings.current.automatic_inventory_handling, width, width):
            imgui_io = self.py_io

            if imgui_io.key_ctrl:
                if settings.current.automatic_inventory_handling:
                    messaging.SendStop(imgui_io.key_shift)
                else:
                    messaging.SendStart(imgui_io.key_shift)

            else:
                if settings.current.automatic_inventory_handling:
                    inventory_handling.InventoryHandler().Stop()
                else:
                    inventory_handling.InventoryHandler().Start()                    

        # ImGui.show_tooltip(
        #     ("Disable" if settings.current.automatic_inventory_handling else "Enable") +
        #     " Inventory Handling" +
        #     "\nHold Ctrl to send message to all accounts" +
        #     "\nHold Shift to send message to all accounts excluding yourself"
        # )

    def _draw_date_collection_toggle_button(self, width):
        if UI.transparent_button(IconsFontAwesome5.ICON_LANGUAGE, settings.current.collect_items, width, width):
            imgui_io = self.py_io

            if imgui_io.key_ctrl:
                if settings.current.collect_items:
                    messaging.SendPauseDataCollection(imgui_io.key_shift)
                    settings.current.save()
                else:
                    messaging.SendStartDataCollection(imgui_io.key_shift)
                    settings.current.save()

            else:
                if settings.current.collect_items:
                    data_collector.instance.stop_collection()
                    settings.current.save()
                else:
                    data_collector.instance.start_collection()
                    settings.current.save()

        ImGui.show_tooltip(
            ("Disable" if settings.current.collect_items else "Enable") +
            " Item Data Collection" +
            "\nHold Ctrl to send message to all accounts" +
            "\nHold Shift to send message to all accounts excluding yourself"
        )
    
    def _draw_manual_window_toggle_button(self, width):
        if UI.transparent_button(IconsFontAwesome5.ICON_COG, settings.current.manual_window_visible, width, width):
            imgui_io = self.py_io
            if imgui_io.key_ctrl:
                if settings.current.manual_window_visible:
                    messaging.SendHideLootExWindow(imgui_io.key_shift)
                    settings.current.save()
                else:
                    messaging.SendShowLootExWindow(imgui_io.key_shift)
                    settings.current.save()
            else:
                settings.current.manual_window_visible = not settings.current.manual_window_visible
                settings.current.save()

        ImGui.show_tooltip(
            ("Hide" if settings.current.manual_window_visible else "Show") + " Window" +
            "\nHold Ctrl to send message to all accounts" +
            "\nHold Shift to send message to all accounts excluding yourself")

    def _draw_xunlai_storage_button(self, width):
        xunlai_open = Inventory.IsStorageOpen()

        if UI.transparent_button(
            IconsFontAwesome5.ICON_BOX_OPEN if xunlai_open else IconsFontAwesome5.ICON_BOX, xunlai_open, width, width
        ):
            if xunlai_open:
                # Inventory.close_storage()
                pass
            else:
                imgui_io = self.py_io

                if imgui_io.key_ctrl:
                    messaging.SendOpenXunlai(imgui_io.key_shift)
                else:
                    Inventory.OpenXunlaiWindow()

        ImGui.show_tooltip("Open Xunlai Storage" +
                        "\nHold Ctrl to send message to all accounts" +
                        "\nHold Shift to send message to all accounts excluding yourself")

    def draw_debug_item(self, i : int, cached_item: cache.Cached_Item, button_width: int = 200, button_height: int = 50):
        if PyImGui.is_rect_visible(button_width, button_height):        
            if cached_item.id > 0 and (not cached_item.data or not cached_item.data.wiki_scraped):
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ChildBg,
                    Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 125))
                )
            
            collected, missing = self.data_collector.is_item_collected(cached_item.id) if cached_item.id != 0 else (True, "")
            mods_missing, mod_missing = self.data_collector.has_uncollected_mods(cached_item.id) if cached_item.id != 0 else (False, "")
            
            complete = (collected and not mods_missing)
            if not complete:
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ChildBg,
                    Utils.ColorToTuple(Utils.RGBToColor(255, 255, 0, 125))
                )
            
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Border,
                Utils.ColorToTuple(utility.Util.GetRarityColor(cached_item.rarity)["text"])
            )
            
            if PyImGui.begin_child(str(i), (button_width, button_height), True, PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):                                    
                image_size = (32, 32)               
                if PyImGui.is_rect_visible(image_size[0], image_size[1]):                 
                    remaining_size = PyImGui.get_content_region_avail()
                    
                    PyImGui.begin_table("ItemTable", 2, PyImGui.TableFlags.NoBordersInBody, remaining_size[0], remaining_size[1] - 30)
                    PyImGui.table_setup_column("Icon", PyImGui.TableColumnFlags.WidthFixed, image_size[0])
                    PyImGui.table_setup_column("Info", PyImGui.TableColumnFlags.WidthStretch)
                    PyImGui.table_next_row()
                    PyImGui.table_next_column()
                    
                    if cached_item.data and cached_item.data.inventory_icon:
                        texture = os.path.join(self.item_textures_path, cached_item.data.inventory_icon)
                        ImGui.DrawTexture(
                            texture,
                            image_size[0], image_size[1]
                        )
                    elif cached_item.id > 0:
                        texture = os.path.join(self.item_textures_path,"wiki_logo.png")
                        ImGui.DrawTexture(
                            texture,
                            image_size[0], image_size[1]
                        )
                        
                    else:
                        PyImGui.dummy(image_size[0], image_size[1])
                        
                    PyImGui.table_next_column()
                        
                    PyImGui.text_scaled(str(cached_item.id) if cached_item.id > 0 else "", (1,1,1,0.75), 0.7)
                    PyImGui.text_scaled(str(cached_item.model_id) if cached_item.id > 0 else "", (1,1,1,1), 0.8)
                    # PyImGui.text_scaled(f"x{cached_item.quantity}" if cached_item.quantity > 1 else "", (1,1,1,1), 0.8)
                    
                    PyImGui.end_table()
    
                PyImGui.push_style_var2(
                    ImGui.ImGuiStyleVar.WindowPadding, 15.0, 5.0
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ChildBg,
                    Utils.ColorToTuple(Utils.RGBToColor(50, 50, 50, 125))
                )
                PyImGui.begin_child("ItemInfoChild", (0, 0), True, PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse)
                action_texture = self.action_textures.get(cached_item.action, None)                
                if action_texture:
                    ImGui.DrawTexture(action_texture, 14, 14)
                    PyImGui.same_line(0, 5)
                    PyImGui.text(utility.Util.reformat_string(cached_item.action.name))
                    
                PyImGui.end_child()
                PyImGui.pop_style_color(1)
                PyImGui.pop_style_var(1)
                
                
                # PyImGui.set_cursor_pos(x, y + 20)
            if cached_item.id > 0 and (not cached_item.data or not cached_item.data.wiki_scraped):
                PyImGui.pop_style_color(1)
                
            if not complete:
                PyImGui.pop_style_color(1)
            
            PyImGui.end_child()
            PyImGui.pop_style_color(1)
            
            if PyImGui.is_item_clicked(0) and cached_item and cached_item.data and not cached_item.data.wiki_scraped:
                data.Reload()                  
                item = data.Items.get_item(cached_item.item_type, cached_item.model_id)
                
                if item and not item.wiki_scraped:
                    wiki_scraper.WikiScraper.scrape_multiple_entries([item])
            
                
            if cached_item and cached_item.data:
                if PyImGui.is_item_hovered():
                    PyImGui.set_next_window_size(400, 0)
                    
                    PyImGui.begin_tooltip()
                    self.draw_item_header(item_info=cached_item.data)
                    if PyImGui.is_rect_visible(0, 20):
                        PyImGui.begin_table("ItemInfoTable", 2, PyImGui.TableFlags.Borders)
                        PyImGui.table_setup_column("Property")
                        PyImGui.table_setup_column("Value")
                        PyImGui.table_headers_row()
                        PyImGui.table_next_row()
                        
                        PyImGui.table_next_column()
                        PyImGui.text(f"Item Id")
                        
                        PyImGui.table_next_column()
                        PyImGui.text(str(cached_item.id) if cached_item.id > 0 else "N/A")
                        
                        PyImGui.table_next_column()
                        PyImGui.text(f"Model Id")
                        
                        PyImGui.table_next_column()
                        PyImGui.text(str(cached_item.model_id) if cached_item.model_id > 0 else "N/A")
                        
                        PyImGui.table_next_column()
                        PyImGui.text(f"Quantity")
                        
                        PyImGui.table_next_column()
                        PyImGui.text(str(cached_item.quantity) if cached_item.quantity > 0 else "N/A")
                        
                        if cached_item.weapon_mods_to_keep and len(cached_item.weapon_mods_to_keep) > 1:
                            PyImGui.table_next_column()
                            PyImGui.text("Mods to Keep")
                            
                            PyImGui.table_next_column()
                            for mod in cached_item.weapon_mods_to_keep:
                                PyImGui.text(mod.name)
                                
                        if cached_item.runes_to_keep and len(cached_item.runes_to_keep) > 1:
                            PyImGui.table_next_column()
                            PyImGui.text("Runes to Keep")
                            
                            PyImGui.table_next_column()
                            for mod in cached_item.runes_to_keep:
                                PyImGui.text(mod.name)
                        
                        if cached_item.runes:
                            PyImGui.table_next_column()
                            PyImGui.text("Runes")
                            
                            PyImGui.table_next_column()
                            for mod in cached_item.runes:
                                PyImGui.text(utility.Util.reformat_string(mod.name))
                        
                        if cached_item.weapon_mods:
                            PyImGui.table_next_column()
                            PyImGui.text("Mods")
                            
                            PyImGui.table_next_column()
                            for mod in cached_item.weapon_mods:
                                PyImGui.text(utility.Util.reformat_string(mod.name))
                        
                        if cached_item.is_rare_weapon:
                            PyImGui.table_next_column()
                            PyImGui.text("Rare Weapon")

                            PyImGui.table_next_column()
                            PyImGui.text_colored("Yes", (0, 1, 0, 1))
                            
                        if cached_item.is_low_requirement_item:
                            PyImGui.table_next_column()
                            PyImGui.text("Low Req")

                            PyImGui.table_next_column()
                            PyImGui.text_colored("Yes", (0, 1, 0, 1))
                            
                                
                        PyImGui.table_next_column()
                        PyImGui.text("Action")
                        
                        PyImGui.table_next_column()
                        action_texture = self.action_textures.get(cached_item.action, None)
                        
                        if action_texture:
                            ImGui.DrawTexture(action_texture, 14, 16)
                            PyImGui.same_line(0, 5)
                        
                        PyImGui.text(utility.Util.reformat_string(cached_item.action.name))
                                                
                        PyImGui.end_table()
                    
                    if not collected:
                        PyImGui.text_colored(missing, (255, 0, 0, 255))
                        
                    if mods_missing:
                        PyImGui.text_colored(mod_missing, (255, 0, 0, 255))
                    
                    if not cached_item.data.wiki_scraped:
                        PyImGui.text_colored("Wiki data not scraped yet", (255, 0, 0, 255))
                        
                        
                        
                    PyImGui.end_tooltip()
                pass
        else:
            PyImGui.dummy(int(button_width), int(button_height))
        
    def draw_data_collector_tab(self):
        if PyImGui.begin_tab_item("Debug & Data"):
            tab_size = PyImGui.get_content_region_avail()
            child_width = tab_size[0] - 10
            tab1_size = (max(400, child_width * 0.25), tab_size[1])
            tab2_size = (child_width - tab1_size[0], tab_size[1])
            
            if PyImGui.begin_child("DataCollectorChild", tab1_size, True, PyImGui.WindowFlags.NoFlag):
                PyImGui.text("Data Collector")
                PyImGui.separator()
                
                PyImGui.input_text("Textures Path", self.item_textures_path,
                                 PyImGui.InputTextFlags.ReadOnly)
                PyImGui.separator()

                child_size = PyImGui.get_content_region_avail()
                if PyImGui.is_rect_visible(0, 20):
                    if PyImGui.begin_table("DataCollectorTable", 2, PyImGui.TableFlags.ScrollY, 200, child_size[1] - 5):
                        PyImGui.table_setup_column("Data")
                        PyImGui.table_setup_column("Amount", PyImGui.TableColumnFlags.WidthFixed, 50)

                        # PyImGui.table_headers_row()
                        PyImGui.table_next_row()

                        PyImGui.table_next_column()
                        PyImGui.text(f"Weapon Mods")
                        PyImGui.table_next_column()
                        PyImGui.text(f"{len(data.Weapon_Mods)}")

                        PyImGui.table_next_column()
                        PyImGui.text(f"Runes")
                        PyImGui.table_next_column()
                        PyImGui.text(f"{len(data.Runes)}")

                        PyImGui.table_next_column()
                        PyImGui.text(f"Items")
                        PyImGui.table_next_column()
                        PyImGui.text(f"{len(data.Items.All)}")
                        
                        PyImGui.table_next_column()
                        PyImGui.separator()
                        PyImGui.table_next_column()
                        PyImGui.separator()
                        
                        
                        for item_type, items in data.Items.items():                            
                            item_count = len(items)
                            if item_count > 0:
                                PyImGui.table_next_column()
                                PyImGui.text(f"{item_type.name}")
                                PyImGui.table_next_column()
                                PyImGui.text(f"{item_count}")
                                
                    PyImGui.end_table()
                
                PyImGui.same_line(0, 5)
                if PyImGui.begin_child("DataCollectorButtonsChild", (0, child_size[1] - 5), False, PyImGui.WindowFlags.NoFlag):
                    if PyImGui.button("Merge Diffs into Data", 160, 50):
                        ConsoleLog(
                            "LootEx",
                            "Merging diffs into data...",
                            Console.MessageType.Info,
                        )

                        messaging.SendMergingMessage()

                    ImGui.show_tooltip("Merge all diff files into the data files.")

                    if PyImGui.button("Scrape Wiki", 160, 50):
                        wiki_scraper.WikiScraper.scrape_missing_entries()
                        pass

                    if settings.current.development_mode and PyImGui.button("Test", 160, 50):
                                    
                        # if identifier == ModifierIdentifier.Requirement:
                        #     self.requirements = arg1 if arg1 is not None else 0
                        #     self.attribute = Attribute(
                        #         arg2) if arg2 is not None else Attribute.None_ 
                        pass  
                                                 
                PyImGui.end_child()
            
            PyImGui.end_child()
                
            PyImGui.same_line(0, 5)
            
            if PyImGui.begin_child("DataCollectorIventory", tab2_size, True, PyImGui.WindowFlags.NoFlag):
                child_size = PyImGui.get_content_region_avail()
                                                             
                PyImGui.push_item_width(child_size[0] - 135)
                self.bag_index = PyImGui.combo(
                    "##Bag",
                    self.bag_index,
                    self.bag_names
                )
                                        
                PyImGui.push_item_width(100)
                PyImGui.same_line(0, 5)
                index = PyImGui.input_int("##BagRange", self.bag_index)           
                if index > len(self.bag_names) - 1:
                    index = len(self.bag_names) - 1
                elif index < 0:
                    index = 0
                
                if index != self.bag_index:
                    self.bag_index = index
                    self.action_summary = None
                
                bag_range = self.bag_ranges[self.bag_names[self.bag_index]]       
                PyImGui.same_line(0, 5)
                
                self.inventory_view = PyImGui.checkbox("##Inventory View", self.inventory_view)
                ImGui.show_tooltip("Show items in a grid view instead of a list view.")
                                
                if self.actions_timer.IsExpired() or self.action_summary is None:
                    if self.bag_names[self.bag_index] == "Merchant/Trader":
                        self.action_summary = inventory_handling.InventoryHandler().GetActions(item_ids=GLOBAL_CACHE.Trading.Merchant.GetOfferedItems() or GLOBAL_CACHE.Trading.Trader.GetOfferedItems() or GLOBAL_CACHE.Trading.Collector.GetOfferedItems() or GLOBAL_CACHE.Trading.Crafter.GetOfferedItems(),  preview=True)
                    else:
                        self.action_summary = inventory_handling.InventoryHandler().GetActions(start_bag=bag_range[0], end_bag=bag_range[1],  preview=True)
                        
                    self.actions_timer.Reset()
                
                PyImGui.separator()
                
                if self.inventory_view: 
                    if self.action_summary and self.action_summary.cached_inventory and self.inventory_coords: 
                        inventory_width = self.inventory_coords.right - self.inventory_coords.left
                        columns = math.floor((inventory_width - 24) // 37) if self.bag_index == 0 else 5
                        rows = math.ceil(len(self.action_summary.cached_inventory) / columns)
                        
                        if PyImGui.is_rect_visible(0, 20):
                            if PyImGui.begin_table("Inventory Debug Table", columns, PyImGui.TableFlags.NoBordersInBody, 0, 0):
                                remaining_size = PyImGui.get_content_region_avail()
                                button_width = math.floor((remaining_size[0] - 50) / columns)
                                button_height = math.floor((child_size[1] - 75) / rows)
                                
                                PyImGui.table_next_row()
                                
                                for i, item in enumerate(self.action_summary.cached_inventory):
                                    PyImGui.table_next_column()     
                                    self.draw_debug_item(i, item, button_width, button_height)   
                                    
                                        
                            PyImGui.end_table()
                else:
                    if self.action_summary and self.action_summary.cached_inventory: 
                        remaining_size = PyImGui.get_content_region_avail()
                        columns = math.floor(remaining_size[0] // 125)
                        
                        if PyImGui.is_rect_visible(0, 20):
                            if PyImGui.begin_table("Inventory Debug Table", columns, PyImGui.TableFlags.ScrollY, 0, 0):
                                remaining_size = PyImGui.get_content_region_avail()
                                button_width = math.floor((remaining_size[0] - 50) / columns)
                                button_height = 90
                                
                                PyImGui.table_next_row()
                                
                                for i, item in enumerate(self.action_summary.cached_inventory):
                                    PyImGui.table_next_column()     
                                    self.draw_debug_item(i, item, button_width, button_height)   
                                    
                                        
                            PyImGui.end_table()
            
            
            PyImGui.end_child()
            

            PyImGui.end_tab_item()

    def draw_prices_tab(self):
        if PyImGui.begin_tab_item("Prices"):
            tab_size = PyImGui.get_content_region_avail()
            child_width = (tab_size[0] - 10) / 2
            
            PyImGui.begin_child("DataCollectorMaterialsChild", (child_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)
            
            remaining_size = PyImGui.get_content_region_avail()
            if PyImGui.button("Get Material Prices", remaining_size[0], 0):
                ConsoleLog(
                    "LootEx",
                    "Fetching material prices from the wiki...",
                    Console.MessageType.Info,
                )
                
                price_check.PriceCheck.get_material_prices_from_trader()
            
            if PyImGui.is_rect_visible(0, 20):
                PyImGui.begin_table("DataCollectorMaterialsTable", 2, PyImGui.TableFlags.ScrollY | PyImGui.TableFlags.Borders, 0, 0)
                PyImGui.table_setup_column("Material")
                PyImGui.table_setup_column("Price")
                PyImGui.table_headers_row()
                
                PyImGui.table_next_row()
                for material in data.Materials.values():
                    PyImGui.table_next_column()
                    PyImGui.text(material.name)
                    PyImGui.table_next_column()
                    if material.vendor_value is not None:
                        PyImGui.text(utility.Util.format_currency(material.vendor_value))
                    else:
                        PyImGui.text("N/A")
                    ImGui.show_tooltip("Last Checked: " + utility.Util.format_time_ago(datetime.now() - material.vendor_updated) if material.vendor_updated else "Never Updated")

                # for material in data.Rare_Materials.values():
                #     PyImGui.table_next_row()
                #     PyImGui.table_next_column()
                #     PyImGui.text(material.name)
                #     PyImGui.table_next_column()
                #     if material.vendor_value is not None:
                #         PyImGui.text(utility.Util.format_currency(material.vendor_value))
                #     else:
                #         PyImGui.text("N/A")
                #     ImGui.show_tooltip("Last Checked: " + utility.Util.format_time_ago(datetime.now() - material.vendor_updated) if material.vendor_updated else "Never Updated")
                        
                PyImGui.end_table()
            
            
            PyImGui.end_child()
        PyImGui.end_tab_item()
        pass
    
    def draw_delete_profile_popup(self):

        if settings.current.profile is None:
            return

        if self.show_delete_profile_popup:
            PyImGui.open_popup("Delete Profile")

        if PyImGui.begin_popup("Delete Profile"):
            PyImGui.text(
                f"Are you sure you want to delete the profile '{settings.current.profile.name}'?")
            PyImGui.separator()

            if PyImGui.button("Yes", 100, 0):
                profile_names = [profile.name for profile in settings.current.profiles]
                profile_index = profile_names.index(settings.current.profile.name) if settings.current.profile else None
                
                if profile_index is None:
                    self.show_delete_profile_popup = False
                    PyImGui.close_current_popup()
                    return
                            
                settings.current.profiles.pop(profile_index)

                settings.current.SetProfile(settings.current.profiles[0].name if settings.current.profiles else None)
                settings.current.save()
                self.show_delete_profile_popup = False
                PyImGui.close_current_popup()

            PyImGui.same_line(0, 5)

            if PyImGui.button("No", 100, 0):
                self.show_delete_profile_popup = False
                PyImGui.close_current_popup()

            PyImGui.end_popup()

        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.show_delete_profile_popup:
                PyImGui.close_current_popup()
                self.show_delete_profile_popup = False

    def draw_profiles_popup(self):
        if self.show_add_profile_popup:
            PyImGui.open_popup("Add Profile")

        if PyImGui.begin_popup("Add Profile"):
            PyImGui.text("Please enter a name for the new profile:")
            PyImGui.separator()

            profile_exists = self.new_profile_name == "" or any(
                profile.name.lower() == self.new_profile_name.lower() for profile in settings.current.profiles
            )

            if profile_exists:
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                        Utils.RGBToColor(255, 0, 0, 255))
                )

            profile_name_input = PyImGui.input_text(
                "##NewProfileName", self.new_profile_name)
            if profile_name_input is not None and profile_name_input != self.new_profile_name:
                self.new_profile_name = profile_name_input

            if profile_exists:
                PyImGui.pop_style_color(1)
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                        Utils.RGBToColor(255, 255, 255, 120))
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Button, Utils.ColorToTuple(
                        Utils.RGBToColor(26, 38, 51, 125))
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(
                        Utils.RGBToColor(26, 38, 51, 125))
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(
                        Utils.RGBToColor(26, 38, 51, 125))
                )

            PyImGui.same_line(0, 5)

            if PyImGui.button("Create", 100, 0) and not profile_exists:
                if self.new_profile_name != "" and not profile_exists:
                    if settings.current.profile:
                        settings.current.profile.save()

                    new_profile = Profile(self.new_profile_name)
                    new_profile.save()
                    
                    settings.current.profiles.append(new_profile)
                    settings.current.SetProfile(new_profile.name)
                    
                    settings.current.save()

                    self.new_profile_name = ""
                    self.show_add_profile_popup = False
                    PyImGui.close_current_popup()
                else:
                    ConsoleLog("LootEx", "Profile name already exists!",
                            Console.MessageType.Error)

            if profile_exists:
                PyImGui.pop_style_color(4)
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                        Utils.RGBToColor(255, 0, 0, 255))
                )
                PyImGui.text("Profile name already exists!")
                PyImGui.pop_style_color(1)

            PyImGui.end_popup()

        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.show_add_profile_popup:
                PyImGui.close_current_popup()
                self.show_add_profile_popup = False

    def draw_general_settings(self):
        if PyImGui.begin_tab_item("General"):
            tab_size = PyImGui.get_content_region_avail()
            dye_section_width = 250

            if PyImGui.begin_child("GeneralSettingsChild", (tab_size[0] - dye_section_width - 5, tab_size[1]), True, PyImGui.WindowFlags.NoFlag) and settings.current.profile:
                subtab_size = PyImGui.get_content_region_avail()

                PyImGui.text("General")
                PyImGui.separator()
                if PyImGui.begin_child("GeneralSettingsChildInner", (subtab_size[0], 75), True, PyImGui.WindowFlags.NoBackground):
                    polling_interval = PyImGui.slider_float("Polling Interval (sec)", settings.current.profile.polling_interval, 0.1, 5)
                    
                    if polling_interval != settings.current.profile.polling_interval:
                        settings.current.profile.polling_interval = polling_interval
                        inventory_handling.InventoryHandler().SetPollingInterval(polling_interval)
                        settings.current.profile.save()
                        
                    loot_range = PyImGui.slider_int("Loot Range", settings.current.profile.loot_range, 125, 5000)
                    
                    if loot_range != settings.current.profile.loot_range:
                        settings.current.profile.loot_range = loot_range
                        settings.current.profile.save()
                PyImGui.end_child()
                
                PyImGui.text("Merchant Settings")
                def draw_hint():
                    PyImGui.text_wrapped("These settings control the items that are automatically bought from merchants when opening a merchant window.")
                    PyImGui.text_wrapped("Before buying items, LootEx will check your stash for these items and move them to your inventory if they are present.\n"+
                                 "If the item is not present in your stash, it will be bought from the merchant.\n")
                
                PyImGui.same_line(0, 5)
                self.draw_info_icon(draw_action=draw_hint, width=500)
                                        
                PyImGui.separator()
                if PyImGui.begin_child("GeneralSettings_Merchant", (subtab_size[0], 150), True, PyImGui.WindowFlags.NoBackground) and settings.current.profile:
                    self._input_int_setting("Identification Kits", settings.current.profile.identification_kits, os.path.join(self.item_textures_path, "Superior_Identification_Kit.png"))
                    self._input_int_setting("Salvage Kits", settings.current.profile.salvage_kits, os.path.join(self.item_textures_path, "Salvage_Kit.png"))
                    self._input_int_setting("Expert Salvage Kits", settings.current.profile.expert_salvage_kits, os.path.join(self.item_textures_path, "Expert_Salvage_Kit.png"))
                    self._input_int_setting("Lockpicks", settings.current.profile.lockpicks, os.path.join(self.item_textures_path, "Lockpick.png"))

                PyImGui.end_child()
                
                PyImGui.text("Nick Settings")
                PyImGui.separator()
                
                if PyImGui.begin_child("GeneralSettings_Nick", (subtab_size[0], 0), True, PyImGui.WindowFlags.NoBackground) and settings.current.profile:
                    
                    self._slider_int_setting("Nick Weeks to Keep", settings.current.profile.nick_weeks_to_keep, os.path.join(self.item_textures_path, "Gift_of_the_Traveler.png"), -1, 137)                    
                    self._slider_int_setting("Nick Items to Keep", settings.current.profile.nick_items_to_keep, os.path.join(self.item_textures_path, "Red_Iris_Flower.png"), 0, 500)    
                    
                    PyImGui.spacing()
                     
                    height = 20                    
                    nick_gradient = UI.get_gradient_colors((0.5, 1, 0, 0.5), (1, 0, 0, 0.5), settings.current.profile.nick_weeks_to_keep)
                    
                    if PyImGui.is_rect_visible(0, 20):
                        PyImGui.begin_table("NickItemsTable", 3, PyImGui.TableFlags.ScrollY | PyImGui.TableFlags.BordersOuterV | PyImGui.TableFlags.BordersOuterH, 0, 0)    
                        # PyImGui.table_setup_column("Index", PyImGui.TableColumnFlags.WidthFixed, 25)
                        PyImGui.table_setup_column("Icon", PyImGui.TableColumnFlags.WidthFixed, 20)
                        PyImGui.table_setup_column("Name")
                        PyImGui.table_setup_column("Weeks Until Next Nick", PyImGui.TableColumnFlags.WidthFixed, 85)   
                             
                        PyImGui.table_next_column()                
                        PyImGui.table_next_column()                
                        
                        for i, nick_item in enumerate(data.Nick_Cycle):
                            if nick_item.weeks_until_next_nick is None:
                                continue
                            
                            if nick_item.weeks_until_next_nick > settings.current.profile.nick_weeks_to_keep:
                                continue
                            
                            PyImGui.table_next_row()
                            if not PyImGui.is_rect_visible(0, height):
                                PyImGui.dummy(0, height)
                                PyImGui.table_next_row()
                                continue
                            
                            # PyImGui.table_next_column()
                            # PyImGui.text(f"{i}.")
                            # hovered = PyImGui.is_item_hovered()
                            
                            PyImGui.table_next_column()
                            if nick_item.inventory_icon:
                                ImGui.DrawTexture(
                                    os.path.join(self.item_textures_path, nick_item.inventory_icon), height, height)
                            else:
                                PyImGui.dummy(height, height)                            
                            hovered = PyImGui.is_item_hovered()
                            
                            PyImGui.table_next_column()                                                    
                            PyImGui.text(nick_item.name)
                            hovered = PyImGui.is_item_hovered() or hovered
                            
                            
                            color = (0, 1, 0, 0.9) if nick_item.weeks_until_next_nick == 0 else \
                                    (0, 1, 0, 0.7) if nick_item.weeks_until_next_nick == 1 else \
                                    nick_gradient[nick_item.weeks_until_next_nick] if nick_item.weeks_until_next_nick < len(nick_gradient) else (1, 1, 1, 1) 

                            PyImGui.table_next_column()
                            PyImGui.text_colored(
                                "current week" if nick_item.weeks_until_next_nick == 0 else f"next week"  if nick_item.weeks_until_next_nick == 1 else f"{nick_item.weeks_until_next_nick} weeks" , 
                                color
                            )
                            hovered = PyImGui.is_item_hovered() or hovered
                            
                            if hovered:
                                PyImGui.set_next_window_size(400, 0)
                                PyImGui.begin_tooltip()
                                
                                self.draw_item_header(item_info=nick_item, border=False, image_size=50)

                                PyImGui.separator()
                                PyImGui.text(f"Nicholas the Traveler collects these items in: {nick_item.weeks_until_next_nick} weeks")                
                                PyImGui.text(nick_item.drop_info)                
                                PyImGui.end_tooltip()
                                
                        PyImGui.end_table()           
                        
                PyImGui.end_child()
                

            PyImGui.end_child()

            PyImGui.same_line(0, 5)

            if PyImGui.begin_child("Dyes", (dye_section_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag) and settings.current.profile:
                PyImGui.text("Dyes")
                PyImGui.text_wrapped(
                    "Select the dyes you want to pick up and stash.")
                PyImGui.separator()

                if PyImGui.begin_child("DyesSelection", (dye_section_width - 20, 0), True, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoBackground):
                    for dye in DyeColor:
                        if dye != DyeColor.NoColor:
                            file_path = os.path.join(self.item_textures_path, f"{dye.name}_Dye.png")
                            if dye not in settings.current.profile.dyes:
                                settings.current.profile.dyes[dye] = False

                            color = utility.Util.GetDyeColor(
                                dye, 205 if settings.current.profile.dyes[dye] else 125)
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color))
                            hover_color = utility.Util.GetDyeColor(dye)
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(hover_color))                            
                            UI.ImageToggle(file_path, 16.25, 20, 
                                           settings.current.profile.dyes[dye]
                            )
                            
                            PyImGui.same_line(0, 5)
                            
                            selected = PyImGui.checkbox(
                                dye.name, settings.current.profile.dyes[dye])

                            if settings.current.profile.dyes[dye] != selected:
                                settings.current.profile.dyes[dye] = selected
                                settings.current.profile.save()

                            PyImGui.pop_style_color(2)
                            ImGui.show_tooltip("Dye: " + dye.name)

                PyImGui.end_child()

            PyImGui.end_child()

            PyImGui.end_tab_item()

    def _input_int_setting(self, label, current_value, item_textures_path=None):
        if settings.current.profile is None:
            return

        PyImGui.push_item_width(150)
        new_value = PyImGui.input_int("##" + label, current_value)
        if new_value != current_value:
            setattr(settings.current.profile,
                    label.replace(" ", "_").lower(), new_value)
            settings.current.profile.save()
            
        PyImGui.same_line(0, 5)
        if item_textures_path and os.path.exists(item_textures_path):
            ImGui.DrawTexture(
                item_textures_path, 16, 16)
        else:
            PyImGui.dummy(16, 16)
        
        PyImGui.same_line(0, 5)
        PyImGui.text(label)
        
    def _slider_int_setting(self, label, current_value, item_textures_path=None, min_value=0, max_value=100):
        if settings.current.profile is None:
            return

        PyImGui.push_item_width(150)
        new_value = PyImGui.slider_int("##" + label, current_value, min_value, max_value)
        if new_value != current_value:
            setattr(settings.current.profile,
                    label.replace(" ", "_").lower(), new_value)
            settings.current.profile.save()
            
        PyImGui.same_line(0, 5)
        if item_textures_path and os.path.exists(item_textures_path):
            ImGui.DrawTexture(
                item_textures_path, 16, 16)
        else:
            PyImGui.dummy(16, 16)
        
        PyImGui.same_line(0, 5)
        PyImGui.text(label)

    def draw_filters(self):
        if PyImGui.begin_tab_item("Filter Based Actions") and settings.current.profile:
            # Get size of the tab
            tab_size = PyImGui.get_content_region_avail()

            # Left panel: Loot Filter Selection
            if PyImGui.begin_child("filter_selection_child", (tab_size[0] * 0.3, tab_size[1]), True, PyImGui.WindowFlags.NoFlag):
                PyImGui.text("Filter Selection")
                
                def draw_hint():
                    PyImGui.text_wrapped(
                        "Add and configure filters to manage how item groups are handled in your inventory.\n")
                    
                    PyImGui.spacing()                    
                    PyImGui.text_wrapped(
                        "- Filters are checked in the order they are listed, and the first matching filter will determine the action taken on an item. To adjust the order, use the up and down arrows next to each filter.\n" +
                        "- You can add, remove, and reorder filters to customize your inventory management.\n" +
                        "- To add a new filter, click the 'Add Filter' button below.")
                    
                    PyImGui.spacing()
                    PyImGui.separator()
                    PyImGui.text_wrapped("Salvage Filters")
                    PyImGui.spacing()
                    PyImGui.text_wrapped(
                        "Salvage filters will only salvage items that contain the selected material to avoid getting too many unwanted materials.\n" +
                        "Adding another filter with the same criteria but with a different action will handle the items that do not match the first filter's criteria.")
                    
                PyImGui.same_line((tab_size[0] * 0.3) - 35 , 5)
                self.draw_info_icon(draw_action=draw_hint, width=500)
                
                PyImGui.separator()
                subtab_size = PyImGui.get_content_region_avail()

                if PyImGui.begin_child("filter_selection_child", (subtab_size[0], subtab_size[1] - 30), True, PyImGui.WindowFlags.NoBackground):
                    selection_size = PyImGui.get_content_region_avail()
                    button_size = (16, 16)
                    if settings.current.profile and settings.current.profile.filters:
                        for i in range(len(settings.current.profile.filters)):
                            filter = settings.current.profile.filters[i]
                            
                            if PyImGui.selectable(f"{i+1}. "+ filter.name, filter == settings.current.selected_filter, PyImGui.SelectableFlags.NoFlag, (selection_size[0] - 47, 0)):
                                settings.current.selected_filter = filter
                            
                            if PyImGui.is_item_hovered():
                                i = self.filter_actions.index(filter.action) if filter.action in self.filter_actions else 0
                                name = self.filter_action_names[i]
                                ImGui.show_tooltip(name)
                            
                            PyImGui.same_line(0, 10)
                            if UI.transparent_button(text=IconsFontAwesome5.ICON_ARROW_UP+ "##" +filter.name, enabled=False, width=button_size[0], height=button_size[1], draw_background=False):
                                if i > 0:
                                    settings.current.profile.filters.insert(
                                        i - 1, settings.current.profile.filters.pop(i))
                                    settings.current.profile.save()
                                    
                            PyImGui.same_line(0, 10)
                            if UI.transparent_button(text=IconsFontAwesome5.ICON_ARROW_DOWN+ "##" +filter.name, enabled=False, width=button_size[0], height=button_size[1], draw_background=False):
                                if i < len(settings.current.profile.filters) - 1:
                                    settings.current.profile.filters.insert(
                                        i + 1, settings.current.profile.filters.pop(i))
                                    settings.current.profile.save()

                PyImGui.end_child()

                if PyImGui.button("Add Filter", subtab_size[0]):
                    self.show_add_filter_popup = not self.show_add_filter_popup
                    if self.show_add_filter_popup:
                        PyImGui.open_popup("Add Filter")

            PyImGui.end_child()

            PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

            # Right panel: Loot Filter Details
            if PyImGui.begin_child("filter_child", (tab_size[0] - (tab_size[0] * 0.3) - 10, 0), True, PyImGui.WindowFlags.NoFlag):
                if settings.current.selected_filter:
                    filter = settings.current.selected_filter

                    PyImGui.push_item_width(tab_size[0] - (tab_size[0] * 0.3) - 63)
                    # Edit filter name
                    name = PyImGui.input_text(
                        "##name_edit", filter.name)
                    if name and name != filter.name:
                        filter.name = name
                        settings.current.profile.save()

                    PyImGui.same_line(0, 5)

                    # Delete filter button
                    if PyImGui.button(IconsFontAwesome5.ICON_TRASH):
                        settings.current.profile.filters.remove(
                            filter)
                        settings.current.profile.save()
                        settings.current.selected_filter = settings.current.profile.filters[
                            0] if settings.current.profile.filters else None
                        self.show_add_filter_popup = False
                        PyImGui.close_current_popup()               
                    
                    # Filter actions
                    remaining_size = PyImGui.get_content_region_avail()
                    height = min(self.action_heights.get(filter.action, 45), remaining_size[0])
                    if PyImGui.begin_child("filter_actions", (0, height), True, PyImGui.WindowFlags.NoFlag):
                        if filter.action:
                            PyImGui.push_item_width(remaining_size[0] - 20)
                            index = PyImGui.combo("#Action", self.filter_actions.index(
                                filter.action) if filter.action in self.filter_actions else 0, self.filter_action_names)
                            
                            selected_action = self.filter_actions[index]
                            
                            if selected_action != filter.action:
                                filter.action = selected_action
                                settings.current.profile.save()
                        
                        
                        def draw_salvage_options():
                            if not settings.current.profile:
                                return
                            
                            PyImGui.separator()                            
                            PyImGui.push_item_width(100)
                            value = PyImGui.slider_int(
                                "Max Item Value##salvage_threshold", filter.salvage_item_max_vendorvalue, 0, 1500)
                            ImGui.show_tooltip(
                                "Items with a vendor value below this threshold will be salvaged.\n" +
                                "This is useful to avoid salvaging items that are worth more than the materials they yield.")
                            
                            if value != filter.salvage_item_max_vendorvalue:
                                filter.salvage_item_max_vendorvalue = value
                                settings.current.profile.save()
                                                    
                            PyImGui.text_wrapped(f"Salvage only items which are worth less than {utility.Util.format_currency(filter.salvage_item_max_vendorvalue)} and which salvage for")
                            
                            width, height = PyImGui.get_content_region_avail()
                            width = width - 20
                            item_width = 200
                            columns = min(max(1, math.floor(width / item_width)), 10)
                            rows = math.ceil(len(data.Common_Materials) / columns) + math.ceil(len(data.Rare_Materials) / columns)
                                                            
                            self.action_heights[enum.ItemAction.SALVAGE] = min(
                                max(153, (remaining_size[1] - 20) / 2), 
                                (rows * 30) + 123 + 8)
                            self.action_heights[enum.ItemAction.SALVAGE_RARE_MATERIALS] = self.action_heights[enum.ItemAction.SALVAGE]
                            self.action_heights[enum.ItemAction.SALVAGE_COMMON_MATERIALS] = self.action_heights[enum.ItemAction.SALVAGE]
                            self.action_heights[enum.ItemAction.SALVAGE_SMART] = self.action_heights[enum.ItemAction.SALVAGE]
                            
                            PyImGui.begin_child("salvage_materials", (0, 0), True, PyImGui.WindowFlags.NoFlag)      
                                            
                                            
                            if PyImGui.is_rect_visible(0, self.action_heights[enum.ItemAction.SALVAGE] - 20):
                                PyImGui.begin_table("salvage_materials_table", columns, PyImGui.TableFlags.ScrollY, 0, 0)
                                
                                for material in data.Common_Materials.values():
                                    PyImGui.table_next_column()
                                    changed, selected = self.draw_material_selectable(material, filter.materials.get(material.model_id, False))
                                
                                    if changed:
                                        if not selected:
                                            if material.model_id in filter.materials:
                                                del filter.materials[material.model_id]
                                        else:
                                            filter.materials[material.model_id] = selected
                                        
                                        settings.current.profile.save()
                                
                                PyImGui.table_next_row()
                                for _ in range(columns):
                                    PyImGui.table_next_column()
                                    PyImGui.dummy(0, 2)
                                    PyImGui.separator()
                                    PyImGui.dummy(0, 2)
                                
                                for material in data.Rare_Materials.values():
                                    PyImGui.table_next_column()
                                    changed, selected = self.draw_material_selectable(material, filter.materials.get(material.model_id, False))
                                
                                    if changed:
                                        if not selected:
                                            if material.model_id in filter.materials:
                                                del filter.materials[material.model_id]
                                        else:
                                            filter.materials[material.model_id] = selected
                                        
                                        settings.current.profile.save()
                                
                                PyImGui.end_table()
                            PyImGui.end_child()
                                
                        match filter.action:
                            case enum.ItemAction.SALVAGE_SMART:
                                draw_salvage_options()                                        
                                pass
                            case enum.ItemAction.SALVAGE_COMMON_MATERIALS:
                                draw_salvage_options()                                        
                                pass
                            case enum.ItemAction.SALVAGE_RARE_MATERIALS:
                                draw_salvage_options()                                        
                                pass
                            
                            case _:
                                pass

                    PyImGui.end_child()

                    # Filter item types
                    sub_subtab_size = PyImGui.get_content_region_avail()
                    if PyImGui.begin_child("loot_item_types_filter_table", (sub_subtab_size[0] / 3 * 2, 0), True, PyImGui.WindowFlags.NoFlag) and PyImGui.is_rect_visible(0, 20):  
                        width, height = PyImGui.get_content_region_avail()
                        width = width - 20
                        item_width = 200
                        columns = min(max(1, math.floor(width / item_width)), 10)
                                                
                        PyImGui.begin_table(
                            "filter_table", columns, PyImGui.TableFlags.ScrollY)

                        count = 0
                        chunk_size = math.ceil(len(self.item_type_textures) / columns)
                        PyImGui.table_next_column()

                        sorted_item_types = sorted(
                            ItemType, key=lambda x: x.name)

                        for item_type in sorted_item_types:
                            if item_type in self.item_type_textures:
                                count += 1

                                if count > chunk_size:
                                    PyImGui.table_next_column()
                                    count = 1

                                if filter.item_types[item_type] is None:
                                    continue

                                changed, filter.item_types[item_type] = self.draw_item_type_selectable(
                                    item_type, filter.item_types[item_type])
                                if changed:
                                    settings.current.profile.save()
                                ImGui.show_tooltip(
                                f"Item Type: {item_type.name}")
                        PyImGui.end_table()

                    PyImGui.end_child()

                    PyImGui.same_line(sub_subtab_size[0] / 3 * 2 + 20, 0)

                    # Filter rarities
                    if PyImGui.begin_child("loot_rarity_filter_table", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                        for rarity in Rarity:
                            if rarity not in filter.rarities:
                                filter.rarities[rarity] = False

                            color = utility.Util.GetRarityColor(rarity)

                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color["text"]))
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color["content"]))
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(color["frame"]))

                            label = f"Rarity: {rarity.name}"
                            unique_id = f"##{rarity.value}"
                            rarity_selected = PyImGui.checkbox(
                                IconsFontAwesome5.ICON_SHIELD_ALT + " " + label + unique_id, filter.rarities[rarity])

                            if filter.rarities[rarity] != rarity_selected:
                                filter.rarities[rarity] = rarity_selected
                                settings.current.profile.save()

                            PyImGui.pop_style_color(3)
                        
                        PyImGui.dummy(0,5)
                        PyImGui.separator()
                        PyImGui.dummy(0,5)

                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.Text, Utils.ColorToTuple(UI.COLORS.RARE_WEAPONS_TEXT))
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(UI.COLORS.RARE_WEAPONS_FRAME))
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(UI.COLORS.RARE_WEAPONS_FRAME_HOVERED))

                        label = f"Exclude Rare Weapons"
                        unique_id = f"##{label}"
                        selected = PyImGui.checkbox(
                            IconsFontAwesome5.ICON_SHIELD_ALT + " " + label + unique_id, filter.exclude_rare_weapons)

                        if filter.exclude_rare_weapons != selected:
                            filter.exclude_rare_weapons = selected
                            settings.current.profile.save()
                            
                        ImGui.show_tooltip(
                            "Exclude weapons found from Dungeon Boss Chests, Elite Area Boss Chests\nand other marked weapons which are generally traded at a high value.\n\n"+
                            "The list of weapons is updated periodically, but may not be complete.")

                        PyImGui.pop_style_color(3)
                        
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.Text, Utils.ColorToTuple(UI.COLORS.LOW_REQ_WEAPONS_TEXT))
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(UI.COLORS.LOW_REQ_WEAPONS_FRAME))
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(UI.COLORS.LOW_REQ_WEAPONS_FRAME_HOVERED))

                        label = f"Exclude Low Req"
                        unique_id = f"##{label}"
                        selected = PyImGui.checkbox(
                            IconsFontAwesome5.ICON_SHIELD_ALT + " " + label + unique_id, filter.exclude_low_req)

                        if filter.exclude_low_req != selected:
                            filter.exclude_low_req = selected
                            settings.current.profile.save()
                            
                        ImGui.show_tooltip(
                            "Exclude weapons with damage within a tolerance of 1 which are used for Speed Clears\nQ0 8-17 Scythe\nQ6 14-24 Bow\nQ6 7-14 Dagger\n +10 armor vs Demons Shields\n\n"+
                            "The check is a temporary solution until we havea ui to configure them.")

                        PyImGui.pop_style_color(3)
                    PyImGui.end_child()

            PyImGui.end_child()

            PyImGui.end_tab_item()

            self.draw_add_filter_popup()

    def draw_add_filter_popup(self):
        if settings.current.profile is None:
            return

        if self.show_add_filter_popup:
            PyImGui.open_popup("Add Filter")

        if PyImGui.begin_popup("Add Filter"):
            PyImGui.text("Please enter a name for the new filter:")
            PyImGui.separator()

            filter_exists = self.filter_name == "" or any(
                filter.name.lower() == self.filter_name.lower()
                for filter in settings.current.profile.filters
            )

            if filter_exists:
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text,
                    Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)),
                )

            filter_name_input = PyImGui.input_text("##NewFilterName", self.filter_name)
            if filter_name_input is not None and filter_name_input != self.filter_name:
                self.filter_name = filter_name_input

            if filter_exists:
                PyImGui.pop_style_color(1)
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text,
                    Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 120)),
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Button,
                    Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)),
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ButtonHovered,
                    Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)),
                )
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ButtonActive,
                    Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)),
                )

            PyImGui.same_line(0, 5)

            if PyImGui.button("Create", 100, 0) and not filter_exists:
                if self.filter_name != "" and not filter_exists:
                    settings.current.profile.filters.append(
                        Filter(self.filter_name))
                    settings.current.profile.save()

                    self.filter_name = ""
                    self.show_add_filter_popup = False
                    PyImGui.close_current_popup()
                else:
                    ConsoleLog(
                        "LootEx",
                        "Filter name already exists!",
                        Console.MessageType.Error,
                    )

            if filter_exists:
                PyImGui.pop_style_color(4)
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text,
                    Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)),
                )
                PyImGui.text("Filter name already exists!")
                PyImGui.pop_style_color(1)

            PyImGui.end_popup()

        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.show_add_filter_popup:
                PyImGui.close_current_popup()
                self.show_add_filter_popup = False

    def draw_filter_popup(self):
        if self.filter_popup:
            PyImGui.open_popup("Filter Loot Items")

        if PyImGui.begin_popup("Filter Loot Items"):
            
            remaining_size = PyImGui.get_content_region_avail()
            
            for filter in self.filters:
                if filter:
                    if PyImGui.selectable(filter.name, self.selected_filter == filter, PyImGui.SelectableFlags.NoFlag, (remaining_size[0], 0)):
                        self.selected_filter = filter
                        self.filter_items()
                        
                        self.filter_popup = False
                        PyImGui.close_current_popup()
        
            PyImGui.end_popup()
        
        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.filter_popup:
                PyImGui.close_current_popup()
                self.filter_popup = False        
        
    def draw_loot_items(self):
        if PyImGui.begin_tab_item("Item Actions") and settings.current.profile:
            # Get size of the tab
            tab_size = PyImGui.get_content_region_avail()

            # Left panel: Loot Items Selection
            if PyImGui.begin_child("loot_items_selection_child", (tab_size[0] * 0.3, tab_size[1]), False, PyImGui.WindowFlags.NoFlag):
                child_size = PyImGui.get_content_region_avail()

                changed, search = UI.search_field("##search_loot_items", self.item_search, f"{IconsFontAwesome5.ICON_SEARCH} Search for Item Name or Model ID...", child_size[0] - 60)
                if changed:
                    self.item_search = search
                    self.filter_items()            

                PyImGui.same_line(0, 5)
                if PyImGui.button(IconsFontAwesome5.ICON_FILTER):
                    self.filter_popup = not self.filter_popup
                    if self.filter_popup:
                        PyImGui.open_popup("Filter Loot Items")
                    pass
                
                def draw_hint():
                    PyImGui.text_wrapped(
                        "Select items to manage their actions in your inventory.\n" +
                        "You can filter items by name or model ID and filter them through the filter popup.\n\n" +
                        "To select multiple items click on the first item, hold down the SHIFT key and click on the last item.\n" +
                        "All items in between will be selected.")
                                           
                PyImGui.same_line(0, 5)
                self.draw_info_icon(
                    draw_action=draw_hint,
                    width=500
                )            
                
                if PyImGui.begin_child("selectable_items", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                    for item in self.filtered_loot_items:
                        if item and not settings.current.profile.is_blacklisted(item.item_info.item_type, item.item_info.model_id):
                            if PyImGui.is_rect_visible(1, 20):
                                self.draw_selectable_item(item)
                            else:
                                PyImGui.dummy(0, 20)

                PyImGui.end_child()

            PyImGui.end_child()

            PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

            # Right panel: Loot Item Details
            if PyImGui.begin_child("loot_item_child", (tab_size[0] - (tab_size[0] * 0.3) - 10, tab_size[1]), False, PyImGui.WindowFlags.NoFlag):
                selected_loot_item = self.selected_loot_items[0] if self.selected_loot_items and len(
                    self.selected_loot_items) == 1 else None

                if selected_loot_item:
                    item_settings = settings.current.profile.items.get_item_config(selected_loot_item.item_info.item_type, selected_loot_item.item_info.model_id)
                    has_settings = item_settings != None
                    
                    
                    self.draw_item_header(selected_loot_item.item_info, True)

                    if PyImGui.begin_child("item_settings", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                        if has_settings:
                            loot_item = settings.current.profile.items.get_item_config(
                                selected_loot_item.item_info.item_type, selected_loot_item.item_info.model_id)

                            if PyImGui.begin_tab_bar("item_conditions") and loot_item:
                                for condition in loot_item.conditions:
                                    if PyImGui.begin_tab_item(condition.name) and condition and selected_loot_item:
                                        if self.selected_condition != condition:
                                            self.selected_condition = condition
                                            self.condition_name = condition.name

                                        remaining_size = PyImGui.get_content_region_avail()

                                        PyImGui.begin_child(
                                            "item_condition_details", (0, remaining_size[1] - 32), False, PyImGui.WindowFlags.NoFlag)
                                        self.condition_name = PyImGui.input_text(
                                            "##name_edit", self.condition_name)
                                        PyImGui.same_line(0, 5)
                                        if PyImGui.button("Rename") and self.condition_name and self.condition_name != condition.name:
                                            condition.name = self.condition_name
                                            settings.current.profile.save()

                                        PyImGui.separator()

                                        # Get the action names, replace underscores with spaces, split at space, all lowercase and first letter to upper case

                                        action = PyImGui.combo("Action", self.item_actions.index(
                                            condition.action) if condition.action in self.item_actions else 0, self.item_action_names)

                                        if self.item_actions[action] != condition.action:
                                            condition.action = self.item_actions[action]
                                            settings.current.profile.save()

                                        if loot_item:
                                            label_spacing = 120
                                            
                                            if condition.action == enum.ItemAction.STASH:
                                                keep_amount = PyImGui.slider_int(
                                                    "Keep in Inventory", condition.keep_in_inventory, 0, 250) 
                                                if keep_amount != condition.keep_in_inventory:
                                                    condition.keep_in_inventory = keep_amount
                                                    settings.current.profile.save()
                                            
                                            if (utility.Util.IsArmor(loot_item)):
                                                PyImGui.text(
                                                    "IsArmor Type: " + str(True))

                                            elif utility.Util.IsWeapon(loot_item):
                                                PyImGui.text("")
                                                PyImGui.text("Item Stats")
                                                PyImGui.separator()

                                                available_attributes = selected_loot_item.item_info.attributes if selected_loot_item.item_info.attributes else utility.Util.GetAttributes(
                                                    selected_loot_item.item_info.item_type)
                                                if len(available_attributes) > 1:
                                                    available_attributes.insert(
                                                        0, Attribute.None_)

                                                if not condition.requirements:
                                                    condition.requirements = {attribute: models.IntRange(
                                                        0, 13) for attribute in available_attributes}

                                                min_requirement = min(
                                                    [attribute.min for attribute in condition.requirements.values()])
                                                max_requirement = max(
                                                    [attribute.max for attribute in condition.requirements.values()])

                                                min_damage_in_requirements = utility.Util.GetMaxDamage(
                                                    min_requirement, selected_loot_item.item_info.item_type).min
                                                max_damage_in_requirements = utility.Util.GetMaxDamage(
                                                    max_requirement, selected_loot_item.item_info.item_type).max

                                                if not condition.damage_range:
                                                    condition.damage_range = models.IntRange(
                                                        min_damage_in_requirements, max_damage_in_requirements)

                                                UI.vertical_centered_text(
                                                    "Damage Range", label_spacing)
                                                remaining_size = PyImGui.get_content_region_avail()
                                                item_width = (
                                                    remaining_size[0] - 10) / 2

                                                if condition.damage_range.max > max_damage_in_requirements:
                                                    condition.damage_range.max = max_damage_in_requirements
                                                    settings.current.profile.save()

                                                PyImGui.push_item_width(item_width)
                                                value = PyImGui.slider_int(
                                                    "##MinDamage", condition.damage_range.min, 0, min_damage_in_requirements)
                                                if value > condition.damage_range.max:
                                                    condition.damage_range.max = value
                                                    settings.current.profile.save()
                                                elif value != condition.damage_range.min:
                                                    condition.damage_range.min = value
                                                    settings.current.profile.save()

                                                PyImGui.same_line(0, 5)
                                                PyImGui.push_item_width(item_width)
                                                value = PyImGui.slider_int(
                                                    "##MaxDamage", condition.damage_range.max, min_damage_in_requirements, max_damage_in_requirements)
                                                if value < condition.damage_range.min:
                                                    condition.damage_range.min = value
                                                    settings.current.profile.save()

                                                elif value != condition.damage_range.max:
                                                    condition.damage_range.max = value
                                                    settings.current.profile.save()

                                                UI.vertical_centered_text(
                                                    "Prefix|Suffix", label_spacing)
                                                prefix_name = utility.Util.GetWeaponModName(
                                                    condition.prefix_mod) if condition.prefix_mod else ""
                                                PyImGui.push_item_width(item_width)
                                                mod = PyImGui.combo("##Prefix", self.prefix_names.index(
                                                    prefix_name) if condition.prefix_mod else 0, self.prefix_names)
                                                if (self.prefix_names[mod] != prefix_name and mod > 0) or (condition.prefix_mod and mod == 0):
                                                    modname = self.prefix_names[mod]
                                                    if modname != None and modname != "Any":
                                                        # Get the mod struct from data.WeaponMods
                                                        for weapon_mod in data.Weapon_Mods.values():
                                                            if weapon_mod.name == modname:
                                                                condition.prefix_mod = weapon_mod.identifier
                                                                settings.current.profile.save()
                                                                break
                                                    elif condition.prefix_mod and mod == 0:
                                                        condition.prefix_mod = None
                                                        settings.current.profile.save()

                                                PyImGui.same_line(0, 5)
                                                suffix_name = utility.Util.GetWeaponModName(
                                                    condition.suffix_mod) if condition.suffix_mod else ""
                                                PyImGui.push_item_width(item_width)
                                                mod = PyImGui.combo("##Suffix", self.suffix_names.index(
                                                    suffix_name) if condition.suffix_mod else 0, self.suffix_names)
                                                if self.suffix_names[mod] != self.suffix_names and mod > 0 or (condition.suffix_mod and mod == 0):
                                                    modname = self.suffix_names[mod]
                                                    if modname != None and modname != "Any":
                                                        # Get the mod struct from data.WeaponMods
                                                        for weapon_mod in data.Weapon_Mods.values():
                                                            if weapon_mod.name == modname:
                                                                condition.suffix_mod = weapon_mod.identifier
                                                                settings.current.profile.save()
                                                                break
                                                    elif condition.suffix_mod and mod == 0:
                                                        condition.suffix_mod = None
                                                        settings.current.profile.save()

                                                UI.vertical_centered_text(
                                                    "Inherent", label_spacing)
                                                inherent_name = utility.Util.GetWeaponModName(
                                                    condition.inherent_mod) if condition.inherent_mod else ""
                                                PyImGui.push_item_width(item_width)
                                                mod = PyImGui.combo("##Inherent", self.inherent_names.index(utility.Util.GetWeaponModName(
                                                    condition.inherent_mod)) if condition.inherent_mod else 0, self.inherent_names)
                                                if self.inherent_names[mod] != inherent_name and mod > 0 or (condition.inherent_mod and mod == 0):
                                                    modname = self.inherent_names[mod]
                                                    if modname != None and modname != "Any":
                                                        # Get the mod struct from data.WeaponMods
                                                        for weapon_mod in data.Weapon_Mods.values():
                                                            if weapon_mod.name == modname:
                                                                condition.inherent_mod = weapon_mod.identifier
                                                                settings.current.profile.save()
                                                                break
                                                    elif condition.inherent_mod and mod == 0:
                                                        condition.inherent_mod = None
                                                        settings.current.profile.save()

                                                PyImGui.same_line(0, 5)
                                                PyImGui.push_item_width(item_width)
                                                checked = PyImGui.checkbox(
                                                    "Old School Only", condition.old_school_only)
                                                if condition.old_school_only != checked:
                                                    condition.old_school_only = checked
                                                    settings.current.profile.save()

                                                PyImGui.text("")
                                                PyImGui.text("Attribute Ranges")
                                                PyImGui.separator()

                                                for attribute, requirement in condition.requirements.items():
                                                    if requirement == None:
                                                        continue

                                                    UI.vertical_centered_text(
                                                        utility.Util.GetAttributeName(attribute) if attribute != Attribute.None_ else "Any", label_spacing)

                                                    remaining_size = PyImGui.get_content_region_avail()
                                                    item_width = (
                                                        remaining_size[0] - 10) / 2

                                                    PyImGui.push_item_width(
                                                        item_width)
                                                    value = PyImGui.slider_int(
                                                        "##MinRequirement", requirement.min, 0, 13)
                                                    if value > requirement.max:
                                                        requirement.max = value
                                                        settings.current.profile.save()

                                                    elif value != requirement.min:
                                                        requirement.min = value
                                                        settings.current.profile.save()

                                                    PyImGui.same_line(0, 5)
                                                    PyImGui.push_item_width(
                                                        item_width)
                                                    value = PyImGui.slider_int(
                                                        "##MaxRequirement", requirement.max, 0, 13)
                                                    if value < requirement.min:
                                                        requirement.min = value
                                                        settings.current.profile.save()

                                                    elif value != requirement.max:
                                                        requirement.max = value
                                                        settings.current.profile.save()

                                        PyImGui.end_child()

                                        remaining_size = PyImGui.get_content_region_avail()
                                        width = remaining_size[0] / 2

                                        if PyImGui.button(IconsFontAwesome5.ICON_TRASH, width, 25):
                                            if  len(loot_item.conditions) > 1:
                                                loot_item.conditions.remove(condition)
                                                settings.current.profile.save()
                                                
                                            elif loot_item:
                                                settings.current.profile.items.delete_item_config(loot_item.item_type, loot_item.model_id)
                                                settings.current.profile.save()
                                                self.selected_loot_item = None
                                                
                                        ImGui.show_tooltip("Delete Condition")

                                        PyImGui.same_line(0, 5)

                                        if PyImGui.button(IconsFontAwesome5.ICON_PLUS, width, 25):
                                            loot_item.conditions.append(
                                                ConfigurationCondition("New Condition"))
                                            settings.current.profile.save()
                                        ImGui.show_tooltip("Add Condition")

                                        PyImGui.end_tab_item()
                                PyImGui.end_tab_bar()

                        else:
                            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                                Utils.RGBToColor(255, 0, 0, 255)))
                            PyImGui.text_wrapped("Item is not yet configured.")
                            PyImGui.pop_style_color(1)

                            if PyImGui.button(IconsFontAwesome5.ICON_PLUS + " Add to Profile", 0, 25) and selected_loot_item and selected_loot_item.item_info.model_id not in settings.current.profile.items:
                                settings.current.profile.items.add_item(selected_loot_item.item_info)
                                settings.current.profile.save()

                    PyImGui.end_child()

                elif self.selected_loot_items and len(self.selected_loot_items) > 1:
                    PyImGui.begin_child("multiple_items_selected",
                                        (0, 0), True, PyImGui.WindowFlags.NoFlag)

                    PyImGui.text("Multiple Items Selected")
                    PyImGui.separator()
                    PyImGui.text_wrapped(
                        "You can create the default rule to stash them for all of them or delete all rules for these items.")

                    if PyImGui.button(IconsFontAwesome5.ICON_PLUS + " Create Default Rule", 0, 25):
                        for item in self.selected_loot_items:
                            if item and item.item_info.model_id and item.item_info.model_id not in settings.current.profile.items:
                                settings.current.profile.items.add_item(item.item_info)
                                settings.current.profile.save()

                    if PyImGui.button(IconsFontAwesome5.ICON_TRASH + " Delete All Rules", 0, 25):
                        for item in self.selected_loot_items:
                            if item and item.item_info.model_id and item.item_info.model_id in settings.current.profile.items:
                                settings.current.profile.items.delete_item_config(item.item_info.item_type, item.item_info.model_id)
                                settings.current.profile.save()

                    PyImGui.end_child()
                else:
                    self.draw_item_header(None, True)
                    
                    PyImGui.begin_child("item_settings", (0, 0), True, PyImGui.WindowFlags.NoFlag)     
                    PyImGui.text("No Item Selected")                   
                    PyImGui.end_child()

            PyImGui.end_child()

            self.draw_filter_popup()
            PyImGui.end_tab_item()
    
    def draw_info_icon(self, draw_action : Callable | None = None, text : str = "", width : float = 200):
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
        PyImGui.text_colored(IconsFontAwesome5.ICON_QUESTION_CIRCLE, 
                             Utils.ColorToTuple(UI.COLORS.INFO_ICON))
        PyImGui.pop_style_var(1)
        
        if PyImGui.is_item_hovered():
            PyImGui.set_next_window_size(width, 0)
            PyImGui.begin_tooltip()
            
            if draw_action:
                draw_action()
            else:
                PyImGui.text_wrapped(text)
            
            PyImGui.end_tooltip()
    
    def draw_blacklist(self):
        if PyImGui.begin_tab_item("Black- & Whitelist") and settings.current.profile:
            # Get size of the tab
            tab_size = PyImGui.get_content_region_avail()
                        
            changed, search = UI.search_field("##search_loot_items", self.item_search, f"{IconsFontAwesome5.ICON_SEARCH} Search for Item Name or Model ID...", tab_size[0] - 60)
            if changed:
                self.item_search = search
                self.filter_items() 
            
            PyImGui.same_line(0, 5)
            if PyImGui.button(IconsFontAwesome5.ICON_FILTER):
                self.filter_popup = not self.filter_popup
                if self.filter_popup:
                    PyImGui.open_popup("Filter Loot Items")
            
            PyImGui.same_line(0, 5)
            
            def draw_hint():   
                PyImGui.text_wrapped("Search for Items by Name or Model ID.\n"+
                             "You can also filter the items by clicking on the filter icon.\n"+
                             "This will open a popup where you can select the filters to apply.\n")
                             
                PyImGui.spacing()
                PyImGui.separator()
                PyImGui.text_wrapped("Blacklist")
                PyImGui.spacing()
                PyImGui.text_wrapped(
                             "Items in the blacklist will not be processed by the inventory handler.\n"+
                             "This is useful for items that you do not want process in any way.\n"+
                             "You can add items to the blacklist by double-clicking them in the item whitelist.\n"+
                             "You can also remove items from the blacklist by double-clicking them in the blacklist panel.")
                
                PyImGui.spacing()
                PyImGui.separator()
                PyImGui.text_wrapped("Whitelist")
                PyImGui.spacing()
                PyImGui.text_wrapped(
                             "Items in the whitelist will be processed by the inventory handler, if they are configured in either item actions or match a filter based action.\n"+
                             "This is useful for items that you want to keep in your inventory or vault.\n"+
                             "You can add items to the whitelist by double-clicking them in the loot items panel.\n"+
                             "You can also remove items from the whitelist by double-clicking them in the whitelist panel.")
                
            self.draw_info_icon(draw_action=
                                draw_hint, width=500)
            
            PyImGui.separator()
            PyImGui.dummy(0, 5)
            
            tab_size = (PyImGui.get_content_region_avail()[0] - 20)/ 2
            
            PyImGui.text("Whitelisted Items")
            PyImGui.same_line(tab_size, 20)
            PyImGui.text("Blacklisted Items")
            
            # Left panel: Loot Items Selection
            if PyImGui.begin_child("blacklisted_selection_items_child", (tab_size, 0), True, PyImGui.WindowFlags.NoFlag):
                for item in self.filtered_blacklist_items:
                    if item and not settings.current.profile.is_blacklisted(item.item_info.item_type, item.item_info.model_id):
                        if PyImGui.is_rect_visible(1, 20):
                            self.draw_blacklist_selectable_item(item)
                        else:
                            PyImGui.dummy(0, 20)

            PyImGui.end_child()

            PyImGui.same_line(0, 5)
            

            # Right panel: Loot Item Details
            if PyImGui.begin_child("blacklisted_items_child", (tab_size, 0), True, PyImGui.WindowFlags.NoFlag):
                for item in self.filtered_blacklist_items:                                                       
                    if item and settings.current.profile.is_blacklisted(item.item_info.item_type, item.item_info.model_id):
                        if PyImGui.is_rect_visible(1, 20):
                            self.draw_blacklist_selectable_item(item)
                        else:
                            PyImGui.dummy(0, 20)
                
            PyImGui.end_child()

            self.draw_filter_popup()
            PyImGui.end_tab_item()

    def draw_item_header(self, item_info : models.Item | None, border : bool = False, height : float | None = None, image_size : float = 110):       
        image_size = min(image_size, 64)
        height = height if height else self.get_tooltip_height(item_info) + (24 if border else 0) if item_info else 130
        
        if PyImGui.begin_child("item_info", (0, max(height, image_size)), border, PyImGui.WindowFlags.NoFlag):            
            if PyImGui.begin_child("item_texture", (image_size, image_size), False, PyImGui.WindowFlags.NoFlag): 
                if item_info:
                    posX, posY = PyImGui.get_cursor_screen_pos()
                    if UI.is_mouse_in_rect((posX, posY, image_size, image_size)):                                
                        if PyImGui.button(IconsFontAwesome5.ICON_GLOBE, image_size, image_size) and item_info.wiki_url:
                            Player.SendChatCommand(
                                                "wiki " + item_info.name)

                                            # start the url in the default browser
                            webbrowser.open(
                                                item_info.wiki_url)

                        ImGui.show_tooltip(
                                            "Open the wiki page for this item.\n" +
                                            "If the item is not found, it will search for the item name in the wiki." if item_info.wiki_url else "This item does not have a wiki page set yet."
                                        )
                    else:
                        color = Utils.RGBToColor(64, 64, 64, 255)
                        PyImGui.push_style_color(
                                            PyImGui.ImGuiCol.Button, Utils.ColorToTuple(color))
                        PyImGui.push_style_color(
                                            PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(color))
                        PyImGui.push_style_color(
                                            PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(color))
                        if item_info.inventory_icon:
                            ImGui.DrawTexture(os.path.join(self.item_textures_path, item_info.inventory_icon), image_size, image_size)
                        else:
                            PyImGui.button(IconsFontAwesome5.ICON_SHIELD_ALT + "##" + str(
                                                item_info.model_id), image_size, image_size)
                        PyImGui.pop_style_color(3)                                    
            PyImGui.end_child()

            PyImGui.same_line(0, 10)
            PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() + 3)

            if PyImGui.begin_child("item_details", (0, 0), False, PyImGui.WindowFlags.NoFlag):
                if item_info:
                    PyImGui.text("Name: " + item_info.name)

                    PyImGui.text("Model ID: " + str(item_info.model_id))
                    PyImGui.text("Type: " + utility.Util.GetItemType(item_info.item_type).name)
                                    
                    if item_info.nick_index:
                        PyImGui.text("Next Nick Week: " + str(item_info.next_nick_week) + " in " + str(item_info.weeks_until_next_nick) + " weeks")
                                    
                    if item_info.common_salvage:
                        summaries = [salvage_info.summary for salvage_info in item_info.common_salvage.values()]                        
                        PyImGui.text("Salvage: " + ", ".join(summaries))
                                    
                    if item_info.rare_salvage:
                        summaries = [salvage_info.summary for salvage_info in item_info.rare_salvage.values()]   
                        PyImGui.text("Rare Salvage: " + ", ".join(summaries))
                        
                    if item_info.category is not enum.ItemCategory.None_:
                        PyImGui.text("Category: " + str(utility.Util.reformat_string(item_info.category.name)))
                        
                    if item_info.sub_category is not enum.ItemSubCategory.None_:
                        PyImGui.text("Sub Category: " + str(utility.Util.reformat_string(item_info.sub_category.name)))
                
            PyImGui.end_child()
        PyImGui.end_child()
    
    def get_tooltip_height(self, item_info: models.Item) -> float:
        """Calculate the number of lines needed for the tooltip based on the item info."""
        lines = 0
        
        if item_info.name is not None:
            lines += 1
        if item_info.model_id is not None:
            lines += 1
        if item_info.item_type is not None:
            lines += 1
        if item_info.nick_index is not None:
            lines += 1
        if item_info.common_salvage:
            lines += 1
        if item_info.rare_salvage:
            lines += 1
        if item_info.category is not enum.ItemCategory.None_:
            lines += 1
        if item_info.sub_category is not enum.ItemSubCategory.None_:
            lines += 1
                
        return (lines * PyImGui.get_text_line_height_with_spacing()) + 0

    def filter_items(self):        
        self.filtered_loot_items = [
                        SelectableItem(item) for item in data.Items.All
                        if item and item.item_type != ItemType.Unknown and item.name and (item.name.lower().find(self.item_search.lower()) != -1 or str(item.model_id).find(self.item_search.lower()) != -1) and (self.selected_filter is None or self.selected_filter.match(item))
                    ]
        
        self.filtered_blacklist_items = [
                        SelectableItem(item) for item in data.Items.All
                        if item and item.item_type != ItemType.Unknown and item.name and (item.name.lower().find(self.item_search.lower()) != -1 or str(item.model_id).find(self.item_search.lower()) != -1) and (self.selected_filter is None or self.selected_filter.match(item))
                    ]

    def _calc_mod_description_height(self, mod, tab_width: float) -> float:
        base_height = 48
        weapon_types_height = 32
        text_size_x, text_size_y = PyImGui.calc_text_size(mod.description)

        lines_of_text = math.ceil(text_size_x / (tab_width - 60))
        required_text_height = (lines_of_text * text_size_y)

        height = base_height + required_text_height + weapon_types_height
        return height

    def filter_weapon_mods(self):
        if self.mod_search == "":
            self.filtered_weapon_mods = [SelectableWrapper(
                v) for k, v in data.Weapon_Mods.items() if v]

        else:
            self.filtered_weapon_mods = []
            lower_search = self.mod_search.lower()
            
            for mod in data.Weapon_Mods.values():
                if mod and ((mod.name and mod.name.lower().find(lower_search)) != -1 or mod.description.lower().find(lower_search) != -1 or mod.identifier.lower().find(lower_search) != -1):
                    self.filtered_weapon_mods.append(SelectableWrapper(mod))

    def draw_weapon_mods(self):
        if self.first_draw:
            self.filter_weapon_mods()

        tab_name = "Weapon Mods"
        if PyImGui.begin_tab_item(tab_name) and settings.current.profile:
            # Get size of the tab
            tab_size = PyImGui.get_content_region_avail()

            # Search bar for weapon mods
            changed, search = UI.search_field(
                "##SearchWeaponMods",
                self.mod_search,
                f"{IconsFontAwesome5.ICON_SEARCH} Search for Mod Name, Description or internal Id...",
                tab_size[0] - 25
            )
            
            if changed:
                self.mod_search = search
                self.filter_weapon_mods()
            
            PyImGui.same_line(0, 5)
            PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() + 5)
            def draw_hint():
                PyImGui.text_wrapped("Search for Weapon Mods by Name, Description or their internal Id.\n"+
                             "Selected Weapon Mods will be highlighted in the list.\n"+
                             "You can select a Weapon Mod by clicking on any weapon type which the mod can be applied to.\n"+
                             "Selected Weapon types will be highlighted as well.\n")
                
                PyImGui.spacing()
                PyImGui.separator()
                
                PyImGui.text_wrapped("Weapon Mods")
                PyImGui.spacing()
                PyImGui.text_wrapped("Items containing the selected Weapon Mods will be picked up and processed by the inventory handler.\n"+
                                     "Items with more than one selected Weapon Mod will be stashed so you can choose which mod to keep.\n")
                
            self.draw_info_icon(draw_action=draw_hint, width=500)
            
            selection_width = tab_size[0]  # max(255, tab_size[0] * 0.3)
            edit_width = tab_size[0] - selection_width - 20
            PyImGui.dummy(0, 0)
            PyImGui.begin_child(
                "ModSelectionsChild", (selection_width, 0), True, PyImGui.WindowFlags.NoFlag)
            first_mod = False
            last_mod = False
            selected_weapon_mod = None

            for selectable in self.filtered_weapon_mods:
                m: models.WeaponMod = selectable.object
                selected_weapon_mod = m if selectable.is_selected else selected_weapon_mod

                if not m.identifier in self.mod_heights:
                    self.mod_heights[m.identifier] = self._calc_mod_description_height(
                        m, selection_width)

                first_mod = PyImGui.is_rect_visible(
                    1, self.mod_heights[m.identifier]) if not first_mod else first_mod

                if not first_mod or last_mod:
                    PyImGui.dummy(0, int(self.mod_heights[m.identifier]))
                    continue

                last_mod = (first_mod and not PyImGui.is_rect_visible(
                    1, self.mod_heights[m.identifier])) if not last_mod else last_mod

                is_in_profile = settings.current.profile.contains_weapon_mod(
                    m.identifier) if settings.current.profile else None

                def get_frame_color():
                    base_color = (255, 255, 255, 255) if not is_in_profile else (
                        255, 204, 85, 255)
                    return Utils.RGBToColor(base_color[0], base_color[1], base_color[2], 150)

                if is_in_profile:
                    color = Utils.RGBToColor(255, 204, 85, 255)
                    PyImGui.push_style_color(
                        PyImGui.ImGuiCol.Text,
                        Utils.ColorToTuple(color),
                    )

                color = get_frame_color()
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Border,
                    Utils.ColorToTuple(color),
                )

                if selectable.is_hovered:
                    color = Utils.RGBToColor(255, 255, 255, 15)
                    PyImGui.push_style_color(
                        PyImGui.ImGuiCol.ChildBg,
                        Utils.ColorToTuple(color),
                    )

                PyImGui.begin_child(
                    id=f"ModSelectable{m.identifier}", size=(0.0, self.mod_heights[m.identifier]), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse)

                UI.vertical_centered_text(
                    IconsFontAwesome5.ICON_SHIELD_ALT, 35, 24)
                UI.vertical_centered_text(m.applied_name, None, 24)

                if is_in_profile:
                    PyImGui.pop_style_color(1)

                PyImGui.pop_style_color(1)

                if selectable.is_hovered:
                    PyImGui.pop_style_color(1)

                PyImGui.separator()

                # PyImGui.dummy(0, 0)
                # PyImGui.same_line(0, 28)

                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text,
                    (1, 1, 1, 0.75),
                )
                PyImGui.text_wrapped(m.description)
                PyImGui.pop_style_color(1)

                is_tooltip_visible = False
                if settings.current.profile:
                    for weapon_type in ItemType:
                        if not m.has_item_type(weapon_type) or weapon_type >= ItemType.Weapon:
                            continue

                        is_selected = m.identifier in settings.current.profile.weapon_mods and weapon_type.name in settings.current.profile.weapon_mods[
                            m.identifier] and settings.current.profile.weapon_mods[m.identifier][weapon_type.name] or False

                        # textures = self.mod_textures.get(weapon_type, None)
                        # texture = textures.get(m.mod_type, None) if textures else None
                        texture = self.item_type_textures.get(weapon_type, None)
                        if texture:
                            ImGui.DrawTexture(texture, 24, 24)
                        else:
                            PyImGui.dummy(24, 24)
                            
                        PyImGui.same_line(0, 0)
                        
                        selected = UI.toggle_button(
                            label = f"{utility.Util.reformat_string(weapon_type.name)}##{m.identifier}{weapon_type.name}", v = is_selected, width= 100, height= 20,
                            default_color=Utils.ColorToTuple(Utils.RGBToColor(255, 204, 85, 155)),
                            hover_color=Utils.ColorToTuple(Utils.RGBToColor(255, 204, 85, 180)),
                            active_color=Utils.ColorToTuple(Utils.RGBToColor(2255, 204, 85, 180))
                            )
                        if selected != is_selected:
                            if not settings.current.profile.weapon_mods.get(m.identifier, None):
                                settings.current.profile.weapon_mods[m.identifier] = {
                                }

                            if self.py_io.key_ctrl:
                                for weapon_type in ItemType:
                                    settings.current.profile.weapon_mods[
                                        m.identifier][weapon_type.name] = selected
                            else:
                                settings.current.profile.weapon_mods[m.identifier][weapon_type.name] = selected

                            settings.current.profile.save()
                            self.filter_weapon_mods()

                        is_tooltip_visible = is_tooltip_visible or PyImGui.is_item_hovered()

                        ImGui.show_tooltip(
                            f"Toggle {utility.Util.reformat_string(weapon_type.name)} for this mod.\n" +
                            "If selected, the mod will be picked up and stored when found." +
                            "\nHold CTRL to toggle all weapon types at once."
                        )

                        PyImGui.same_line(0, 5)

                PyImGui.end_child()
                selectable.is_hovered = PyImGui.is_item_hovered()

                if PyImGui.is_item_clicked(0) and settings.current.profile:
                    selectable.is_selected = not selectable.is_selected
                    for s in self.filtered_weapon_mods:
                        if s != selectable:
                            s.is_selected = False

                if is_in_profile:
                    PyImGui.pop_style_color(2)

                if not is_tooltip_visible:
                    UI.weapon_mod_tooltip(m)

            PyImGui.end_child()

            # PyImGui.same_line(0, 5)

            # PyImGui.begin_child(
            #     "ModEditChild", (edit_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)

            # PyImGui.text("Mod Details")
            # PyImGui.separator()

            # PyImGui.text("Selected Mod: " + (selected_weapon_mod.name if selected_weapon_mod else "None"))

            # PyImGui.end_child()

            if False:
                # Table headers
                PyImGui.push_style_var(ImGui.ImGuiStyleVar.ChildBorderSize, 0)
                PyImGui.push_style_var2(ImGui.ImGuiStyleVar.CellPadding, 2, 2)
                if PyImGui.begin_child(
                    f"{tab_name}TableHeaders#1",
                    (tab_size[0] - 20 if self.scroll_bar_visible else 0, 20),
                    True,
                    PyImGui.WindowFlags.NoBackground,
                ):
                    PyImGui.begin_table(
                        "Weapon Mods Table",
                        len(weapon_types) + 4,
                        PyImGui.TableFlags.NoFlag,
                    )
                    PyImGui.table_setup_column(
                        "##Texture", PyImGui.TableColumnFlags.WidthFixed, 50)
                    PyImGui.table_setup_column(
                        "Name", PyImGui.TableColumnFlags.WidthFixed, 150)

                    PyImGui.table_setup_column(
                        "Description", PyImGui.TableColumnFlags.WidthFixed, 250)

                    PyImGui.table_setup_column(
                        "Inscription", PyImGui.TableColumnFlags.WidthFixed, 50
                    )

                    for weapon_type in self.weapon_types:
                        PyImGui.table_setup_column(
                            weapon_type.name, PyImGui.TableColumnFlags.WidthFixed, 50
                        )

                    PyImGui.table_headers_row()
                    PyImGui.end_table()

                PyImGui.end_child()

                # Table content
                self.scroll_bar_visible = False
                if PyImGui.begin_child(
                    f"{tab_name}#1", (0, 0), True, PyImGui.WindowFlags.NoBackground
                ):
                    PyImGui.begin_table(
                        "Weapon Mods Table",
                        len(weapon_types) + 4,
                        PyImGui.TableFlags.RowBg | PyImGui.TableFlags.BordersInnerH | PyImGui.TableFlags.ScrollY,
                    )
                    PyImGui.table_setup_column(
                        "##Texture", PyImGui.TableColumnFlags.WidthFixed, 50)
                    PyImGui.table_setup_column(
                        "Name", PyImGui.TableColumnFlags.WidthFixed, 150)

                    PyImGui.table_setup_column(
                        "Description", PyImGui.TableColumnFlags.WidthFixed, 250)

                    PyImGui.table_setup_column(
                        "Inscription", PyImGui.TableColumnFlags.WidthFixed, 50
                    )

                    for weapon_type in self.weapon_types:
                        PyImGui.table_setup_column(
                            weapon_type.name, PyImGui.TableColumnFlags.WidthFixed, 50
                        )

                    server_language = utility.Util.get_server_language()
                    for mod in self.filtered_weapon_mods.values():
                        if not mod or not mod.identifier:
                            continue

                        keep = settings.current.profile.weapon_mods.get(
                            mod.identifier, None) if settings.current.profile else None

                        if keep:
                            color = utility.Util.GetRarityColor(Rarity.Gold)[
                                "text"]
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.Text,
                                Utils.ColorToTuple(color),
                            )

                        PyImGui.table_next_row()
                        # Mod texture
                        PyImGui.table_next_column()
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.Button, Utils.ColorToTuple(
                                Utils.RGBToColor(255, 255, 255, 0))
                        )
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.ButtonHovered,
                            Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)),
                        )
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.ButtonActive,
                            Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)),
                        )
                        PyImGui.push_style_var2(
                            ImGui.ImGuiStyleVar.FramePadding, 5, 8)
                        PyImGui.button(
                            IconsFontAwesome5.ICON_SHIELD_ALT + f"##{mod.identifier}")
                        PyImGui.pop_style_color(3)
                        PyImGui.pop_style_var(1)

                        # Mod name
                        PyImGui.table_next_column()
                        color = utility.Util.GetRarityColor(Rarity.Green)[
                            "text"] if not server_language in mod.names else utility.Util.GetRarityColor(Rarity.White)["text"]
                        # PyImGui.push_style_color(
                        #     PyImGui.ImGuiCol.Text,
                        #     Utils.ColorToTuple(color),
                        # )
                        PyImGui.text_wrapped(mod.applied_name)
                        # PyImGui.pop_style_color(1)
                        weapon_mod_tooltip(mod)
                        # ImGui.show_tooltip(
                        #     f"Mod: {mod.name}\nIdentifier: {mod.identifier}"
                        # )

                        # Mod name
                        PyImGui.table_next_column()
                        PyImGui.text_wrapped(mod.description)
                        weapon_mod_tooltip(mod)
                        # ImGui.show_tooltip(
                        #     f"Mod: {mod.description}\nIdentifier: {mod.identifier}"
                        # )
                        if keep:
                            PyImGui.pop_style_color(1)

                        PyImGui.table_next_column()
                        inscription = "Inscription"

                        if mod.is_inscription:
                            unique_id = f"##{mod.identifier}{inscription}"
                            PyImGui.push_style_var2(
                                ImGui.ImGuiStyleVar.FramePadding, 0, 8)

                            is_selected = (
                                mod.identifier in settings.current.profile.weapon_mods
                                and inscription
                                in settings.current.profile.weapon_mods[mod.identifier]
                                and settings.current.profile.weapon_mods[mod.identifier][inscription]
                            )
                            mod_selected = PyImGui.checkbox(unique_id, is_selected)

                            PyImGui.pop_style_var(1)
                            ImGui.show_tooltip(
                                f"{'Keep' if is_selected else 'Ignore'} {mod.name}"
                            )

                            if is_selected != mod_selected:
                                if mod_selected:
                                    if mod.identifier not in settings.current.profile.weapon_mods:
                                        settings.current.profile.weapon_mods[mod.identifier] = {
                                        }
                                    settings.current.profile.weapon_mods[mod.identifier][
                                        inscription
                                    ] = True
                                else:
                                    settings.current.profile.weapon_mods[mod.identifier].pop(
                                        inscription, None
                                    )
                                    if not settings.current.profile.weapon_mods[mod.identifier]:
                                        settings.current.profile.weapon_mods.pop(
                                            mod.identifier, None)

                                settings.current.profile.save()

                        # Weapon type checkboxes
                        for weapon_type in self.weapon_types:
                            PyImGui.table_next_column()

                            if not mod.is_inscription:
                                hasWeaponType = mod.has_item_type(weapon_type)

                                if hasWeaponType:
                                    unique_id = f"##{mod.identifier}{weapon_type}"
                                    PyImGui.push_style_var2(
                                        ImGui.ImGuiStyleVar.FramePadding, 0, 8)

                                    is_selected = (
                                        mod.identifier in settings.current.profile.weapon_mods
                                        and weapon_type.name
                                        in settings.current.profile.weapon_mods[mod.identifier]
                                        and settings.current.profile.weapon_mods[mod.identifier][weapon_type.name]
                                    )
                                    mod_selected = PyImGui.checkbox(
                                        unique_id, is_selected)

                                    PyImGui.pop_style_var(1)
                                    ImGui.show_tooltip(
                                        f"{'Keep' if is_selected else 'Ignore'} {mod.name} for {weapon_type.name}"
                                    )

                                    if is_selected != mod_selected:
                                        if mod_selected:
                                            if mod.identifier not in settings.current.profile.weapon_mods:
                                                settings.current.profile.weapon_mods[mod.identifier] = {
                                                }
                                            settings.current.profile.weapon_mods[mod.identifier][
                                                weapon_type.name
                                            ] = True
                                        else:
                                            settings.current.profile.weapon_mods[mod.identifier].pop(
                                                weapon_type.name, None
                                            )
                                            if not settings.current.profile.weapon_mods[mod.identifier]:
                                                settings.current.profile.weapon_mods.pop(
                                                    mod.identifier, None)

                                        settings.current.profile.save()

                        self.scroll_bar_visible = self.scroll_bar_visible or PyImGui.get_scroll_max_y() > 0

                PyImGui.pop_style_var(2)
                PyImGui.end_table()
                PyImGui.end_child()

            PyImGui.end_tab_item()

    def draw_runes(self):
        tab_name = "Runes"
        if PyImGui.begin_tab_item(tab_name) and settings.current.profile:
            if PyImGui.begin_child(f"{tab_name}#1", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                PyImGui.text("Rune Selection")

                remaining_space = PyImGui.get_content_region_avail()
                PyImGui.same_line(remaining_space[0] - 270, 5)
                if PyImGui.button("Get Expensive Runes from Merchant", 250, 0):
                    if settings.current.profile:
                        self.show_price_check_popup = not self.show_price_check_popup
                        if self.show_price_check_popup:
                            self.trader_type = "RUNES"
                            PyImGui.open_popup("Get Expensive Runes from Merchant")
                        else:
                            PyImGui.close_current_popup()
                
                def draw_help():
                    PyImGui.text_wrapped(
                        "- Selecting a rune/insignia will mark it as valuable and items containing this rune/insignia will be picked up.\n" +
                        "- If the item is a salvage item and contains only one rune/insignia, the rune/insignia will be extracted by salvaging the item automatically.\n" +
                        "- If the item has multiple Runes/Insignias, the item will be stashed/kept intact so you can decide which to extract."
                    )
                    
                    PyImGui.spacing()
                    PyImGui.separator()
                    PyImGui.text_wrapped("Get Expensive Runes from Merchant")
                    PyImGui.spacing()
                    PyImGui.text_wrapped(
                        "- Move to the Rune Trader in order to click this button.\n"+
                        "- This will check the current sell price for all runes and check those that are above the price threshold or currently unavailable.\n" +
                        "- You can set the price threshold in the popup that appears when you click the button.\n" +
                        "- The runes will be added to your profile and marked as valuable."
                    )
                    PyImGui.spacing()
                    PyImGui.text_wrapped(
                        "If you click the button all selected runes/insignias will be first removed from your profile and then the expensive runes will be added.\n" + 
                        "This means that any runes/insignias you manually selected will be removed")
                
                PyImGui.same_line(0, 5)
                self.draw_info_icon(
                    draw_action=draw_help,
                    width=500
                )

                PyImGui.separator()

                if PyImGui.begin_tab_bar("RunesTabBar"):
                    for profession, runes in data.Runes_by_Profession.items():

                        if not runes:
                            continue

                        profession_name = "Common" if profession == Profession._None else profession.name

                        if not PyImGui.begin_tab_item(profession_name):
                            continue

                        if PyImGui.begin_child("RunesSelection#1", (0, 0), True, PyImGui.WindowFlags.NoBackground):                            
                            for rune in runes.values():
                                if not rune or not rune.identifier:
                                    continue

                                if not PyImGui.is_rect_visible(0, 24):
                                    PyImGui.dummy(0, 24)
                                    continue

                                PyImGui.begin_child(
                                    f"RuneSelectable{rune.identifier}",
                                    (0, 24),
                                    False,
                                    PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse
                                )
                                color = utility.Util.GetRarityColor(
                                    rune.rarity.value)
                                PyImGui.push_style_color(
                                    PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color["text"]))
                                PyImGui.push_style_color(
                                    PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color["content"]))
                                PyImGui.push_style_color(
                                    PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(color["frame"]))

                                texture = os.path.join(
                                    self.item_textures_path, rune.inventory_icon) if rune.inventory_icon else None
                                if texture:
                                    ImGui.DrawTexture(texture, 24, 24)
                                else:
                                    PyImGui.dummy(24, 24)
                                    
                                PyImGui.same_line(0, 5)
                                
                                label = f"{rune.full_name}"
                                unique_id = f"##{rune.identifier}"                                
                                is_valuable = rune.identifier in settings.current.profile.runes and settings.current.profile.runes[rune.identifier].valuable
                                rune_valuable = PyImGui.checkbox(
                                    "##valuable" + unique_id,
                                    is_valuable
                                )
                                
                                is_item_hovered = False
                                hovered = PyImGui.is_item_hovered()
                                if hovered:
                                    PyImGui.begin_tooltip()
                                    PyImGui.text_colored("Mark", (1,1,1,1))
                                    PyImGui.same_line(0, 5)
                                    
                                    PyImGui.text_colored(rune.name, Utils.ColorToTuple(color["text"]))
                                    PyImGui.same_line(0, 5)
                                    PyImGui.text_colored("as valuable to pick them up and extract automatically.", (1,1,1,1))
                                    PyImGui.end_tooltip()
                                
                                is_item_hovered = hovered or is_item_hovered

                                if is_valuable != rune_valuable:
                                    settings.current.profile.set_rune(rune.identifier, rune_valuable)
                                    settings.current.profile.save()

                                PyImGui.same_line(0, 5)
                                
                                is_rune_sell = (rune.identifier in settings.current.profile.runes and settings.current.profile.runes[rune.identifier].should_sell)
                                rune_sell = PyImGui.checkbox(
                                    "##sell" + unique_id,
                                    is_rune_sell
                                )
                                
                                if rune_sell != is_rune_sell:
                                    settings.current.profile.set_rune(rune.identifier, rune_valuable, rune_sell)
                                    settings.current.profile.save()
                                
                                hovered = PyImGui.is_item_hovered()
                                if hovered:
                                    PyImGui.begin_tooltip()
                                    PyImGui.text_colored("Sell", (1,1,1,1))
                                    PyImGui.same_line(0, 5)
                                    
                                    PyImGui.text_colored(rune.name, Utils.ColorToTuple(color["text"]))
                                    PyImGui.same_line(0, 5)
                                    PyImGui.text_colored("to the trader for Gold.", (1,1,1,1))
                                    PyImGui.end_tooltip()
                                    
                                is_item_hovered = hovered or is_item_hovered

                                
                                PyImGui.same_line(0, 5)
                                PyImGui.text(utility.Util.reformat_string(rune.full_name))
                                PyImGui.pop_style_color(3)    
                                
                                PyImGui.same_line(0, 5)
                                PyImGui.text_colored(utility.Util.format_currency(rune.vendor_value), Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 125)))
                                PyImGui.end_child()
                                
                                if not is_item_hovered:
                                    UI.rune_tooltip(rune)
                                
                                
                            PyImGui.end_child()

                        PyImGui.end_tab_item()

                    PyImGui.end_tab_bar()

            PyImGui.end_child()

            self.draw_price_check_popup()
            PyImGui.end_tab_item()

    def draw_price_check_popup(self):
        if settings.current.profile is None:
            return

        if self.show_price_check_popup:
            PyImGui.open_popup("Get Expensive Runes from Merchant")

        if PyImGui.begin_popup("Get Expensive Runes from Merchant"):
            PyImGui.text("Please enter a price threshold:")
            PyImGui.separator()

            price_input = PyImGui.input_int(
                "##PriceThreshold", self.entered_price_threshold)
            if price_input is not None and price_input != self.entered_price_threshold:
                self.entered_price_threshold = price_input

            PyImGui.same_line(0, 5)

            if PyImGui.button("Check Prices", 100, 0):
                if self.trader_type == "RUNES":
                    if self.entered_price_threshold is not None and self.entered_price_threshold > 0:
                        ConsoleLog(
                            "LootEx",
                            f"Checking for expensive runes from merchant with price threshold: {self.entered_price_threshold}",
                            Console.MessageType.Info,
                        )
                        price_check.PriceCheck.get_expensive_runes_from_merchant(
                            self.entered_price_threshold, self.mark_to_sell_runes)
                    else:
                        ConsoleLog(
                            "LootEx",
                            "Price threshold must be greater than 0!",
                            Console.MessageType.Error,
                        )

                self.show_price_check_popup = False
                PyImGui.close_current_popup()

            mark_to_sell = PyImGui.checkbox("Mark to sell", self.mark_to_sell_runes)
            if mark_to_sell != self.mark_to_sell_runes:
                 self.mark_to_sell_runes = mark_to_sell
                 
            PyImGui.end_popup()

        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.show_price_check_popup:
                PyImGui.close_current_popup()
                self.show_price_check_popup = False

    def draw_material_selectable(self, material : models.Material, is_selected) -> tuple[bool, bool]:
        """
        Draws a selectable checkbox for an item type in the GUI.

        Args:
            item_type: The item type to display.
            is_selected: Whether the item type is currently selected.

        Returns:
            A tuple containing:
            - A boolean indicating if the selection state has changed.
            - A boolean indicating the new selection state.
        """
        if settings.current.profile is None:
            return False, False

        text_color = Utils.RGBToColor(
            255, 255, 255, 255) if is_selected else Utils.RGBToColor(255, 255, 255, 125)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text,
                                Utils.ColorToTuple(text_color))

        texture = os.path.join(self.item_textures_path, material.inventory_icon) if material.inventory_icon else None
        if texture:
            ImGui.DrawTexture(texture, 20, 20)
        else:
            PyImGui.dummy(20, 20)
        
        PyImGui.same_line(0, 5)
        
        is_now_selected = PyImGui.checkbox(
            f"{utility.Util.reformat_string(material.name)}", is_selected
        )
        PyImGui.pop_style_color(1)
        
        if PyImGui.is_item_hovered():
            PyImGui.begin_tooltip()
            if PyImGui.is_rect_visible(0, 20):
                if PyImGui.begin_table(str(material.model_id), 2, PyImGui.TableFlags.Borders):
                    PyImGui.table_setup_column(
                        material.name, PyImGui.TableColumnFlags.WidthFixed, 150)
                    PyImGui.table_headers_row()

                    PyImGui.table_next_row()
                    
                    PyImGui.table_next_column()
                    PyImGui.text(f"Vendor Value")
                    
                    PyImGui.table_next_column()
                    PyImGui.text(utility.Util.format_currency(material.vendor_value))
                                
                    PyImGui.table_next_column()
                    PyImGui.text(f"Last Checked")
                    PyImGui.table_next_column()
                    time_ago = f"{utility.Util.format_time_ago(datetime.now() - material.vendor_updated)}\n" if material.vendor_updated else ""
                    PyImGui.text(f"{time_ago}")
                    
                PyImGui.end_table()
            
            PyImGui.end_tooltip()
            

        return is_selected != is_now_selected, is_now_selected

    def draw_item_type_selectable(self, item_type, is_selected) -> tuple[bool, bool]:
        """
        Draws a selectable checkbox for an item type in the GUI.

        Args:
            item_type: The item type to display.
            is_selected: Whether the item type is currently selected.

        Returns:
            A tuple containing:
            - A boolean indicating if the selection state has changed.
            - A boolean indicating the new selection state.
        """
        if settings.current.profile is None:
            return False, False

        text_color = Utils.RGBToColor(
            255, 255, 255, 255) if is_selected else Utils.RGBToColor(255, 255, 255, 125)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text,
                                Utils.ColorToTuple(text_color))
        
        texture = self.item_type_textures.get(item_type, None)
        if texture:
            ImGui.DrawTexture(texture, 20, 20)
        else:
            PyImGui.dummy(20, 20)
            
        PyImGui.same_line(0, 5)

        is_now_selected = PyImGui.checkbox(
            f"{utility.Util.reformat_string(item_type.name)}", is_selected
        )
        PyImGui.pop_style_color(1)

        return is_selected != is_now_selected, is_now_selected

    def draw_blacklist_selectable_item(self, item: SelectableItem):
        """
        Draws a selectable item in the GUI.

        Args:
            item (SelectableItem): The item to be displayed.
        """

        if settings.current.profile is None:
            return

        # Apply background color for selected or hovered items
        if item.is_selected:
            selected_color = Utils.RGBToColor(34, 34, 34, 255)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(selected_color))

        if item.is_hovered:
            hovered_color = Utils.RGBToColor(63, 63, 63, 255)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(hovered_color))

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
        PyImGui.begin_child(
            f"SelectableItem{item.item_info.model_id}",
            (0, 20),
            False,
            PyImGui.WindowFlags.NoFlag,
        )

        if item.item_info.inventory_icon:
            ImGui.DrawTexture(os.path.join(self.item_textures_path, item.item_info.inventory_icon), 20, 20)
        else:
            PyImGui.dummy(20, 20)
        
        PyImGui.same_line(0, 5)
        # Construct item name with attributes if available
        attributes = (
            [utility.Util.GetAttributeName(
                attr) + ", " for attr in item.item_info.attributes]
            if item.item_info.attributes
            else []
        )
        
        profession = utility.Util.GetProfessionName(item.item_info.profession) if item.item_info.profession else ""

        item_name = item.item_info.name
        
            
        if item.item_info.attributes and len(item.item_info.attributes) > 0:
            item_name = (
                f"{item_name} ({''.join(attributes).removesuffix(',')})"
                if len(item.item_info.attributes) > 1
                else f"{item_name} ({utility.Util.GetAttributeName(item.item_info.attributes[0])})"
            )
        elif item.item_info.attributes and len(item.item_info.attributes) == 1:
            item_name = f"{item_name} ({utility.Util.GetAttributeName(item.item_info.attributes[0])})"

        elif profession:
            item_name = f"{item_name} ({profession})"
            
        # Determine text color based on whether the item has settings
        has_settings = item.item_info.model_id in settings.current.profile.items
        text_color = (
            utility.Util.GetRarityColor(Rarity.Gold)["text"]
            if has_settings
            else Utils.RGBToColor(255, 255, 255, 255)
        )
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text,
                                Utils.ColorToTuple(text_color))

        # Draw item name with vertical centering
        PyImGui.set_cursor_pos_x(PyImGui.get_cursor_pos_x() + 5)
        UI.vertical_centered_text(item_name, None, 20)
        PyImGui.pop_style_color(1)

        PyImGui.end_child()
        PyImGui.pop_style_var(1)
        
        blacklisted = settings.current.profile.is_blacklisted(item.item_info.item_type, item.item_info.model_id)
        
        # Pop background color styles if applied
        if item.is_selected:
            PyImGui.pop_style_color(1)

        if item.is_hovered:
            PyImGui.pop_style_color(1)

        clicked = PyImGui.is_mouse_clicked(0) or PyImGui.is_mouse_double_clicked(0) or PyImGui.is_mouse_down(0)
        
        # Update hover and selection states
        item.is_hovered = PyImGui.is_item_hovered() or PyImGui.is_item_clicked(0) or (item.is_hovered and clicked)

        if not item.is_hovered and item.is_clicked:                            
            item.is_clicked = False

        # Show tooltip with item name
        if item.is_hovered:
            PyImGui.set_next_window_size(400, 0)
            PyImGui.begin_tooltip()
            
            self.draw_item_header(item_info=item.item_info, border=False, image_size=50)

            PyImGui.separator()
            PyImGui.text(f"Double-click to {"blacklist" if not blacklisted else "whitelist"} the item.")                
            PyImGui.end_tooltip()
            
            if (item.is_clicked and PyImGui.is_mouse_clicked(0)):
                time_since_click = datetime.now() - item.time_stamp
                
                if time_since_click.microseconds > 500000:
                    item.time_stamp = datetime.now()
                    return
                
                if blacklisted:
                    settings.current.profile.whitelist_item(item.item_info.item_type, item.item_info.model_id)            
                    settings.current.profile.save()
                    item.is_hovered = False
                    item.is_selected = False
                else:
                    settings.current.profile.blacklist_item(item.item_info.item_type, item.item_info.model_id)           
                    settings.current.profile.save()
                    item.is_hovered = False
                    item.is_selected = False
                    
            elif PyImGui.is_mouse_clicked(0) and item.is_hovered:
                item.is_clicked = True
                item.time_stamp = datetime.now()

    def draw_selectable_item(self, item: SelectableItem):
        """
        Draws a selectable item in the GUI.

        Args:
            item (SelectableItem): The item to be displayed.
        """

        if settings.current.profile is None:
            return

        # Apply background color for selected or hovered items
        if item.is_selected:
            selected_color = Utils.RGBToColor(34, 34, 34, 255)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(selected_color))

        if item.is_hovered:
            hovered_color = Utils.RGBToColor(63, 63, 63, 255)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(hovered_color))

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
        PyImGui.begin_child(
            f"SelectableItem{item.item_info.model_id}",
            (0, 20),
            False,
            PyImGui.WindowFlags.NoFlag,
        )

        # Construct item name with attributes if available
        attributes = (
            [utility.Util.GetAttributeName(
                attr) + ", " for attr in item.item_info.attributes]
            if item.item_info.attributes
            else []
        )
        
        profession = utility.Util.GetProfessionName(item.item_info.profession) if item.item_info.profession else ""

        item_name = item.item_info.name
        
            
        if item.item_info.attributes and len(item.item_info.attributes) > 0:
            item_name = (
                f"{item_name} ({''.join(attributes).removesuffix(',')})"
                if len(item.item_info.attributes) > 1
                else f"{item_name} ({utility.Util.GetAttributeName(item.item_info.attributes[0])})"
            )
        elif item.item_info.attributes and len(item.item_info.attributes) == 1:
            item_name = f"{item_name} ({utility.Util.GetAttributeName(item.item_info.attributes[0])})"

        elif profession:
            item_name = f"{item_name} ({profession})"
            
        # Determine text color based on whether the item has settings
        has_settings = settings.current.profile.items.get_item_config(item.item_info.item_type, item.item_info.model_id) is not None
        text_color = (
            utility.Util.GetRarityColor(Rarity.Gold)["text"]
            if has_settings
            else Utils.RGBToColor(255, 255, 255, 255)
        )
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text,
                                Utils.ColorToTuple(text_color))

        if item.item_info.inventory_icon:
            ImGui.DrawTexture(os.path.join(self.item_textures_path, item.item_info.inventory_icon), 20, 20)
        else:
            PyImGui.dummy(20, 20)
                    
                    
        PyImGui.same_line(0, 5)
        # Draw item name with vertical centering
        PyImGui.set_cursor_pos_x(PyImGui.get_cursor_pos_x() + 5)
        UI.vertical_centered_text(item_name, None, 20)
        PyImGui.pop_style_color(1)

        PyImGui.end_child()
        PyImGui.pop_style_var(1)
        
        # Pop background color styles if applied
        if item.is_selected:
            PyImGui.pop_style_color(1)

        if item.is_hovered:
            PyImGui.pop_style_color(1)

        # Update hover and selection states
        item.is_hovered = PyImGui.is_item_hovered()

        # Show tooltip with item name
        if item.is_hovered:
            PyImGui.set_next_window_size(400, 0)
            PyImGui.begin_tooltip()
            
            self.draw_item_header(item_info=item.item_info, border=False, image_size=50)

            PyImGui.separator()
            PyImGui.text("Click to select the item.")
            
            PyImGui.end_tooltip()
            
            
        if PyImGui.is_mouse_double_clicked(0) and item.is_hovered:
            self.selected_loot_items = [item]
            py_io = self.py_io
            
            if item.item_info.model_id in settings.current.profile.items:
                settings.current.profile.remove_item(item.item_info.item_type, item.item_info.model_id)     
                settings.current.profile.save()
            else:
                settings.current.profile.add_item(item.item_info)     
                settings.current.profile.save()

        elif PyImGui.is_mouse_clicked(0) and item.is_hovered:
            if self.py_io.key_shift:
                start = min(self.filtered_loot_items.index(item),
                            self.filtered_loot_items.index(self.selected_loot_items[0]))
                end = max(self.filtered_loot_items.index(item),
                        self.filtered_loot_items.index(self.selected_loot_items[0]))
                self.selected_loot_items = self.filtered_loot_items[start:end + 1]

                for other_item in self.filtered_loot_items:
                    other_item.is_selected = False

                for selected_item in self.selected_loot_items:
                    selected_item.is_selected = True
            else:
                self.selected_loot_items = [item]

                for other_item in self.filtered_loot_items:
                    other_item.is_selected = False

                item.is_selected = True

    def draw_old_school_selectable(self, item: SelectableWrapper) -> bool:
             # Apply background color for selected or hovered items
        if item.is_selected:
            selected_color = Utils.RGBToColor(34, 34, 34, 255)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(selected_color))

        if item.is_hovered:
            hovered_color = Utils.RGBToColor(63, 63, 63, 255)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(hovered_color))

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
        texture_height = 30
        PyImGui.begin_child(
            f"SelectableItem{item.object}",
            (0, texture_height),
            False,
            PyImGui.WindowFlags.NoFlag,
        )
        
        texture = self.item_type_textures.get(item.object, None)
        if texture:
            ImGui.DrawTexture(texture, texture_height, texture_height)
        else:
            PyImGui.dummy(texture_height, texture_height)
            
        PyImGui.same_line(0, 5)
        
        self.vertical_centered_text(
            utility.Util.reformat_string(item.object.name), None, texture_height
        )
        
        PyImGui.end_child()
        PyImGui.pop_style_var(1)
        
        # Pop background color styles if applied
        if item.is_selected:
            PyImGui.pop_style_color(1)

        if item.is_hovered:
            PyImGui.pop_style_color(1)
        
        
        item.is_hovered = PyImGui.is_item_hovered()
        clicked = PyImGui.is_item_clicked(0)
        
        if clicked:
            item.is_selected = not item.is_selected            

        return clicked
        
    def draw_old_school_tab(self):
        if PyImGui.begin_tab_item("Old School"):
            selected_item_type = None
            texture_height = 30
            
            tab_size = PyImGui.get_content_region_avail()

            # Left panel: Loot Items Selection
            if PyImGui.begin_child("Old School Child Left", (tab_size[0] * 0.15, 0), True, PyImGui.WindowFlags.NoFlag):
                    
                for selectable in self.os_low_req_itemtype_selectables:
                    if self.draw_old_school_selectable(selectable):
                        for other_selectable in self.os_low_req_itemtype_selectables:
                            if other_selectable != selectable:
                                other_selectable.is_selected = False
                    
                    if selectable.is_selected:
                        selected_item_type = selectable.object
                                
                    PyImGui.spacing()
            PyImGui.end_child()
            
            PyImGui.same_line(0, 5)
            # Right panel: Loot Items
            if PyImGui.begin_child("Old School Child Right", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                if selected_item_type:                                
                    texture = self.item_type_textures.get(selected_item_type, None)
                    if texture:
                        ImGui.DrawTexture(texture, texture_height, texture_height)
                    else:
                        PyImGui.dummy(texture_height, texture_height)
                        
                    PyImGui.same_line(0, 5)
                    
                    self.vertical_centered_text(
                        utility.Util.reformat_string(selected_item_type.name), None, texture_height
                    )
                    PyImGui.separator()
                    
                
                    requirement = 0
                    max_requirement = 13
                                                        
                    value = PyImGui.slider_int(
                        "Max Requirement", requirement, 0, max_requirement)
                    pass
                
                    width_remaining = PyImGui.get_content_region_avail()[0] - 10
                    
                    if PyImGui.begin_child("Old School Child Mods", (width_remaining / 2, 0), True, PyImGui.WindowFlags.NoFlag):
                        for mod in data.Weapon_Mods.values():
                            if mod.mod_type == enum.ModType.Inherent:
                                if not mod.has_item_type(selected_item_type):
                                    continue
                                
                                selected = PyImGui.selectable(mod.description, False, PyImGui.SelectableFlags.NoFlag, (0,0))
                        pass
                    
                    PyImGui.end_child()
                    
                    PyImGui.same_line(0, 5)
                    
                    if PyImGui.begin_child("Old School Child Skins", (width_remaining / 2, 0), True, PyImGui.WindowFlags.NoFlag):
                        for skin, items in data.ItemsBySkins.items():
                            if any(item.item_type == selected_item_type for item in items):
                                ImGui.DrawTexture(os.path.join(self.item_textures_path, skin), 32, 32)
                                PyImGui.same_line(0, 5)
                                self.vertical_centered_text(
                                    utility.Util.reformat_string(skin), None, 32
                                )
                        pass
                    
                    PyImGui.end_child()
                    
                    
                    
                    
                    
            
            PyImGui.end_child()
            
            PyImGui.end_tab_item()
        
    
    # region general ui elements
    @staticmethod
    def ImageToggle(path : str, width : float, height : float, is_selected : bool) -> bool:
        """
        Draws an image toggle button with the specified icon and width.
        
        Args:
            path (str): The path to the image file.
            width (float): The width of the button.
            height (float): The height of the button.
            is_selected (bool): Whether the button is selected or not.
        
        Returns:
            bool: True if the button was clicked, False otherwise.
        """
        cursor_pos = PyImGui.get_cursor_screen_pos()
        rect = (cursor_pos[0], cursor_pos[1], width, height)
        transparent_color = Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0))   
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text,
            Utils.ColorToTuple(
                Utils.RGBToColor(255, 255, 255, 255)
                if is_selected
                else Utils.RGBToColor(255, 255, 255, 200)
                if UI.is_mouse_in_rect(rect)
                else Utils.RGBToColor(255, 255, 255, 125)
            ),
        )
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,
                                transparent_color)
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(
            Utils.RGBToColor(0, 0, 0, 125)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,
                                transparent_color)

        clicked = ImGui.ImageButton(f"##{path}", path, width, height)

        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(4)

        return clicked
 
    @staticmethod
    def weapon_mod_tooltip(mod: models.WeaponMod):
        if PyImGui.is_item_hovered():
            PyImGui.begin_tooltip()

            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255)),
            )
            PyImGui.text(f"{mod.name}")
            PyImGui.text(f"{mod.description}")

            PyImGui.separator()

            # PyImGui.begin_child(
            #     f"WeaponModTooltip{mod.identifier}",
            #     (400, 0),
            #     True,
            #     PyImGui.WindowFlags.NoBackground,
            # )
            if PyImGui.is_rect_visible(0, 20):
                if PyImGui.begin_table(mod.identifier, 2, PyImGui.TableFlags.Borders):
                    PyImGui.table_setup_column(
                        "Property", PyImGui.TableColumnFlags.WidthFixed, 150)
                    PyImGui.table_setup_column(
                        "Value", PyImGui.TableColumnFlags.WidthStretch)
                    PyImGui.table_headers_row()

                    PyImGui.table_next_row()

                    PyImGui.table_next_column()
                    PyImGui.text(f"Id (internal)")

                    PyImGui.table_next_column()
                    PyImGui.text(f"{mod.identifier}")

                    PyImGui.table_next_column()
                    PyImGui.text(f"Mod Type")

                    PyImGui.table_next_column()
                    PyImGui.text(f"{mod.mod_type.name}")

                    PyImGui.table_next_column()
                    PyImGui.text(f"Applied to Item Types")

                    PyImGui.table_next_column()
                    for item_type in mod.target_types:
                        PyImGui.text(f"{item_type.name}")

                PyImGui.end_table()

            PyImGui.pop_style_color(1)
            # PyImGui.end_child()
            PyImGui.end_tooltip()

    @staticmethod
    def rune_tooltip(mod: models.Rune):
        if PyImGui.is_item_hovered():
            PyImGui.begin_tooltip()

            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255)),
            )
            PyImGui.text(f"{mod.name}")
            PyImGui.text(f"{mod.description}")

            PyImGui.separator()

            # PyImGui.begin_child(
            #     f"WeaponModTooltip{mod.identifier}",
            #     (400, 0),
            #     True,
            #     PyImGui.WindowFlags.NoBackground,
            # )
            if PyImGui.is_rect_visible(0, 20):
                if PyImGui.begin_table(mod.identifier, 2, PyImGui.TableFlags.Borders):
                    PyImGui.table_setup_column(
                        "Property", PyImGui.TableColumnFlags.WidthFixed, 150)
                    PyImGui.table_setup_column(
                        "Value", PyImGui.TableColumnFlags.WidthStretch)
                    PyImGui.table_headers_row()

                    PyImGui.table_next_row()

                    PyImGui.table_next_column()
                    PyImGui.text(f"Id (internal)")

                    PyImGui.table_next_column()
                    PyImGui.text(f"{mod.identifier}")

                    PyImGui.table_next_column()
                    PyImGui.text(f"Mod Type")

                    PyImGui.table_next_column()
                    PyImGui.text(f"{mod.mod_type.name}")

                    PyImGui.table_next_column()
                    PyImGui.text(f"Applied")

                    PyImGui.table_next_column()            
                    PyImGui.text(f"{mod.applied_name}")
                    
                    PyImGui.table_next_column()
                    PyImGui.text(f"Vendor Value")
                    
                    PyImGui.table_next_column()
                    PyImGui.text(utility.Util.format_currency(mod.vendor_value))
                                
                    PyImGui.table_next_column()
                    PyImGui.text(f"Last Checked")
                    PyImGui.table_next_column()
                    time_ago = f"{utility.Util.format_time_ago(datetime.now() - mod.vendor_updated)}\n" if mod.vendor_updated else ""
                    PyImGui.text(f"{time_ago}")
                    
                PyImGui.end_table()

            PyImGui.pop_style_color(1)
            # PyImGui.end_child()
            PyImGui.end_tooltip()

    @staticmethod
    def transparent_button(text : str, enabled : bool, width: float, height : float, draw_background : bool = True) -> bool:
        """
        Draws a transparent button with the specified icon and width.
        
        Args:
            icon (str): The icon to display on the button.
            width (int): The width of the button.
        
        Returns:
            bool: True if the button was clicked, False otherwise.
        """
        
        cursor_pos = PyImGui.get_cursor_screen_pos()
        rect = (cursor_pos[0], cursor_pos[1],
                width, height)
        transparent_color = Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0))   
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text,
            Utils.ColorToTuple(
                Utils.RGBToColor(255, 255, 255, 255)
                if enabled
                else Utils.RGBToColor(255, 255, 255, 200)
                if UI.is_mouse_in_rect(rect)
                else Utils.RGBToColor(255, 255, 255, 125)
            ),
        )
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,
                                transparent_color)
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(
            Utils.RGBToColor(0, 0, 0, 125)) if draw_background else transparent_color)
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,
                                transparent_color)

        clicked = PyImGui.button(text, width, height)

        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(4)

        return clicked

    @staticmethod
    def vertical_centered_text(text: str, same_line_spacing: Optional[float] = None, desired_height: int = 24) -> float:
        """
        Draws text vertically centered within a specified height.

        Args:
            text (str): The text to display.
            same_line_spacing (Optional[float]): Spacing to apply if the text is on the same line.
            desired_height (int): The height within which the text should be centered.

        Returns:
            float: The width of the rendered text.
        """
        # text_size = PyImGui.calc_text_size(text)
        # text_offset = (desired_height - text_size[1]) / 2

        # cursor_y = PyImGui.get_cursor_pos_y()

        # if text_offset > 0:
        #     PyImGui.set_cursor_pos_y(cursor_y + text_offset)

        # PyImGui.text(text)

        # if same_line_spacing:
        #     if text_offset > 0:
        #         PyImGui.set_cursor_pos_y(cursor_y)

        #     PyImGui.set_cursor_pos_x(
        #         PyImGui.get_cursor_pos_x() + text_size[0] + same_line_spacing)

        # return text_size[0]

        textSize = PyImGui.calc_text_size(text)
        textOffset = (desired_height - textSize[1]) / 2

        cursorY = PyImGui.get_cursor_pos_y()
        cusorX = PyImGui.get_cursor_pos_x()

        if textOffset > 0:
            PyImGui.set_cursor_pos_y(cursorY + textOffset)

        PyImGui.text(text)

        if same_line_spacing:
            if textOffset > 0:
                PyImGui.set_cursor_pos_y(cursorY)

            # PyImGui.set_cursor_pos_x(cusorX + textSize[0] + sameline_spacing)
            PyImGui.set_cursor_pos_x(same_line_spacing)

        return textSize[0]

    @staticmethod
    def is_mouse_in_rect(rect: tuple[float, float, float, float]) -> bool:
        """
        Checks if the mouse is within a specified rectangle.

        Args:
            rect (tuple[float, float, float, float]): The rectangle defined by (x, y, width, height).

        Returns:
            bool: True if the mouse is within the rectangle, False otherwise.
        """
        pyimgui_io = PyImGui.get_io()
        mouse_pos = (pyimgui_io.mouse_pos_x, pyimgui_io.mouse_pos_y)
        
        return (rect[0] <= mouse_pos[0] <= rect[0] + rect[2] and
                rect[1] <= mouse_pos[1] <= rect[1] + rect[3])

    @staticmethod
    def toggle_button(label: str, v: bool, width=0, height=0,
                    default_color: tuple[float, float, float, float] = (
                        0.153, 0.318, 0.929, 1.0),
                    hover_color: tuple[float, float, float,
                                        float] = (0.6, 0.6, 0.9, 1.0),
                    active_color: tuple[float, float,
                                        float, float] = (0.6, 0.6, 0.6, 1.0)
                    ) -> bool:
        """
        Purpose: Create a toggle button that changes its state and color based on the current state.
        Args:
            label (str): The label of the button.
            v (bool): The current toggle state (True for on, False for off).
        Returns: bool: The new state of the button after being clicked.
        """
        clicked = False

        if v:
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Button, default_color)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ButtonHovered, hover_color)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ButtonActive, active_color)
            if width != 0 and height != 0:
                clicked = PyImGui.button(label, width, height)
            else:
                clicked = PyImGui.button(label)
            PyImGui.pop_style_color(3)
        else:
            if width != 0 and height != 0:
                clicked = PyImGui.button(label, width, height)
            else:
                clicked = PyImGui.button(label)

        if clicked:
            v = not v

        return v

    @staticmethod
    def search_field(label_id : str, text : str, placeholder : str, width : float = 0.0) -> tuple[bool, str]:
        PyImGui.begin_child("SearchField" + label_id, (width, 24), False, PyImGui.WindowFlags.NoBackground)
        
        remaining_space = PyImGui.get_content_region_avail()
        PyImGui.push_item_width(remaining_space[0])
        search = PyImGui.input_text(label_id, text)
        search_active = PyImGui.is_item_active()
        
        if (search is None or search == "") and not search_active:
            PyImGui.same_line(5, 0)
            PyImGui.begin_child("search_placeholder", (max(width - 10, 1), 24), False, PyImGui.WindowFlags.NoBackground |PyImGui.WindowFlags.NoMouseInputs)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                Utils.RGBToColor(255, 255, 255, 125)))
            UI.vertical_centered_text(placeholder)
            PyImGui.pop_style_color(1)
            PyImGui.end_child()
            
        PyImGui.end_child()

        return (search != text, search)
    
    @staticmethod
    def get_gradient_colors(start_color: tuple[float, float, float, float], end_color: tuple[float, float, float, float], steps: int) -> list[tuple[float, float, float, float]]:
        """
        Generates a list of gradient colors between two specified colors.

        Args:
            start_color (tuple): The starting color in RGBA format.
            end_color (tuple): The ending color in RGBA format.
            steps (int): The number of gradient steps.

        Returns:
            list: A list of colors representing the gradient.
        """
        return [
            (
                start_color[0] + (end_color[0] - start_color[0]) * i / (steps - 1),
                start_color[1] + (end_color[1] - start_color[1]) * i / (steps - 1),
                start_color[2] + (end_color[2] - start_color[2]) * i / (steps - 1),
                start_color[3] + (end_color[3] - start_color[3]) * i / (steps - 1)
            )
            for i in range(steps)
        ] if  steps > 1 else [start_color, end_color]
    # endregion
