from argparse import Action
import re
import webbrowser

from Widgets.frenkey.Core.iterable import chunked
from Widgets.frenkey.Core import style, texture_map, gui
from Widgets.frenkey.LootEx import action_rule, loot_handling, profile, settings, data, price_check, item_configuration, utility, enum, cache, ui_manager_extensions, inventory_handling, wiki_scraper, filter, models, messaging, data_collector,wiki_scraper
from Widgets.frenkey.LootEx.item_configuration import ItemConfiguration, ConfigurationCondition
from Widgets.frenkey.LootEx.filter import Filter
from Widgets.frenkey.LootEx.profile import Profile
from Widgets.frenkey.LootEx.ui_manager_extensions import UIManagerExtensions
from Py4GWCoreLib import *

import ctypes
from ctypes import windll

import importlib

from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
importlib.reload(gui)
importlib.reload(style)
importlib.reload(settings)
importlib.reload(action_rule)
importlib.reload(texture_map)
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

GUI = gui.GUI()


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
    
class RuleFilter:
    def __init__(self, name: str, lambda_function: Callable[[action_rule.ActionRule], bool]):
        self.name: str = name
        self.lambda_function: Callable[[action_rule.ActionRule], bool] = lambda_function
        pass
    
    def match(self, rule: action_rule.ActionRule) -> bool:
        """
        Checks if the rule matches the filter criteria.
        
        Args:
            rule (action_rule.ActionRule): The rule to check against the filter.
        
        Returns:
            bool: True if the rule matches the filter, False otherwise.
        """
        
        return self.lambda_function(rule)
    
class UI:
    _instance = None
    
    class ActionInfo:
        def __init__(self, name: str, description: str, icon: str):
            self.name: str = name
            self.description: str = description
            self.icon: str = icon
    
    class ActionInfos(dict[enum.ItemAction, "UI.ActionInfo"]):
        def __init__(self, dict : dict[enum.ItemAction, "UI.ActionInfo"] = {}):
            super().__init__()

            for action, info in dict.items():
                self[action] = info
                
            self.update({
                action: UI.ActionInfo(
                    name=action.name.replace("_", " ").title(),
                    description="",
                    icon=""
                ) for action in enum.ItemAction
            })
        
        def __getitem__(self, key: enum.ItemAction) -> "UI.ActionInfo":
            return super().__getitem__(key)
        
        def get_texture(self, action: enum.ItemAction, default = None):
            """
            Returns the texture path for the given action.
            
            Args:
                action (enum.ItemAction): The action for which to get the texture.
            
            Returns:
                str: The texture path for the action.
            """
            if action not in self:
                return default
            
            return self[action].icon
        
        def get_name(self, action: enum.ItemAction, default = None):
            """
            Returns the name for the given action.
            
            Args:
                action (enum.ItemAction): The action for which to get the name.
            
            Returns:
                str: The name for the action.
            """
            if action not in self:
                return default
            
            return self[action].name
        
        def get_description(self, action: enum.ItemAction, default = None):
            """
            Returns the description for the given action.
            
            Args:
                action (enum.ItemAction): The action for which to get the description.
            
            Returns:
                str: The description for the action.
            """
            if action not in self:
                return default
            
            return self[action].description

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UI, cls).__new__(cls)
        
        return cls._instance
    
    def __init__(self):       
        # self.cached_item = cache.Cached_Item(1401) 
        self.style = style.Style()
        file_directory = os.path.dirname(os.path.abspath(__file__))
        self.icon_textures_path = os.path.join(file_directory, "textures")
        self.item_textures_path = "Textures\\Items"
        self.actions_timer = ThrottledTimer()
        self.action_summary: inventory_handling.InventoryHandler.ActionsSummary | None = None
        
        self.action_infos : UI.ActionInfos = UI.ActionInfos({
            enum.ItemAction.Loot: UI.ActionInfo("Loot (Pick Up)", "If the item is dropped, pick it up.", texture_map.CoreTextures.UI_Reward_Bag_Hovered.value),
            enum.ItemAction.Collect_Data: UI.ActionInfo("Collect Data", "Collect data about the item.", os.path.join(self.icon_textures_path, "wiki_logo.png")),
            enum.ItemAction.Identify: UI.ActionInfo("Identify", "Use an Identification Kit to identify the item.", os.path.join(self.item_textures_path, "Identification_Kit.png")),
            enum.ItemAction.Stash: UI.ActionInfo("Stash", "Stash the item in your Xunlai Chest.", os.path.join(self.icon_textures_path, "xunlai_chest.png")),
            enum.ItemAction.Salvage_Mods: UI.ActionInfo("Salvage Mods", "Salvage the mods from the item.", os.path.join(self.item_textures_path, "Inscription_equippable_items.png")),
            enum.ItemAction.Salvage: UI.ActionInfo("Salvage for Common or Rare Materials", "Use a Salvage Kit to salvage the item.", os.path.join(self.icon_textures_path, "expert_or_common_salvage_kit.png")),
            enum.ItemAction.Salvage_Common_Materials: UI.ActionInfo("Salvage Common Materials", "Use a Salvage Kit to salvage common materials from the item.", os.path.join(self.item_textures_path, "Salvage Kit.png")),
            enum.ItemAction.Salvage_Rare_Materials: UI.ActionInfo("Salvage Rare Materials", "Use an Expert Salvage Kit to salvage rare materials from the item.", os.path.join(self.item_textures_path, "Expert Salvage Kit.png")),
            enum.ItemAction.Sell_To_Merchant: UI.ActionInfo("Sell to Merchant", "Sell the item to a merchant for gold.", texture_map.CoreTextures.UI_Gold.value),
            enum.ItemAction.Sell_To_Trader: UI.ActionInfo("Sell to Trader (Runes, Scrolls, Dyes...)", "Sell the item to a trader for gold.", os.path.join(self.item_textures_path, "Gold.png")),
            enum.ItemAction.Destroy: UI.ActionInfo("Destroy", "Destroy the item permanently.", texture_map.CoreTextures.UI_Destroy.value),
            enum.ItemAction.Deposit_Material: UI.ActionInfo("Deposit Material", "Deposit the item as a material in your Xunlai Chest.", os.path.join(self.icon_textures_path, "xunlai_chest.png")),
            enum.ItemAction.NONE: UI.ActionInfo("No Action", "No action will be performed on the item.", ""),
        })        
                
        self.action_textures: dict[enum.ItemAction, str] = {   
            # enum.ItemAction.NONE: os.path.join(self.item_textures_path, "Data_Collector.png"),        
            enum.ItemAction.Loot: texture_map.CoreTextures.UI_Reward_Bag_Hovered.value,    
            enum.ItemAction.Collect_Data: os.path.join(self.icon_textures_path, "wiki_logo.png"),      
            enum.ItemAction.Identify: os.path.join(self.item_textures_path, "Identification_Kit.png"),      
            enum.ItemAction.Stash: os.path.join(self.icon_textures_path, "xunlai_chest.png"),      
            enum.ItemAction.Salvage_Mods: os.path.join(self.item_textures_path, "Inscription_equippable_items.png"),
            enum.ItemAction.Salvage: os.path.join(self.icon_textures_path, "expert_or_common_salvage_kit.png"),
            enum.ItemAction.Salvage_Common_Materials: os.path.join(self.item_textures_path, "Salvage Kit.png"),  
            enum.ItemAction.Salvage_Rare_Materials: os.path.join(self.item_textures_path, "Expert Salvage Kit.png"),
            enum.ItemAction.Sell_To_Merchant: texture_map.CoreTextures.UI_Gold.value,
            enum.ItemAction.Sell_To_Trader: texture_map.CoreTextures.UI_Gold.value,
            enum.ItemAction.Destroy: texture_map.CoreTextures.UI_Destroy.value,
            enum.ItemAction.Deposit_Material: os.path.join(self.icon_textures_path, "xunlai_chest.png"),
        }
        
        self.py_io = PyImGui.get_io()
        self.selected_loot_items: list[SelectableItem] = []
        
        
        self.rule_search: str = ""
        self.selected_rule_changed: bool = True
        self.mod_range_popup: bool = False
        self.selected_rule: action_rule.ActionRule | None = None
        self.selected_rule_mod: models.WeaponMod | None = None
        self.selected_mod_info: models.ModInfo | None = None
        self.selectable_rules: list[SelectableWrapper] = []
        self.selectable_items : list[models.Item] = []
        
        self.dmg_range_popup: bool = False
        self.selected_rule_damage_range: models.IntRange | None = None
        self.selected_damage_range: models.IntRange | None = None
        self.selected_damage_range_min: models.IntRange | None = None
        
        self.inventory_view: bool = True
        self.item_search: str = ""
        self.filtered_loot_items: list[SelectableItem] = []        
        self.filtered_skins: list[SelectableItem] = []        
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
        self.rarity_item_types : list[ItemType] = [
            ItemType.Axe,
            ItemType.Bow,
            ItemType.Daggers,
            ItemType.Hammer,
            ItemType.Scythe,
            ItemType.Spear,
            ItemType.Sword,
            ItemType.Staff,
            ItemType.Wand,
            ItemType.Offhand,
            ItemType.Shield, 
            ItemType.Salvage,                       
        ]
        
        self.item_type_textures: dict[ItemType, str] = {
            ItemType.Salvage: os.path.join(self.item_textures_path, "Salvage Heavy Armor.png"),
            ItemType.Axe: os.path.join(self.item_textures_path, "Great Axe.png"),
            ItemType.Bag: os.path.join(self.item_textures_path, "Bag.png"),
            ItemType.Boots: os.path.join(self.icon_textures_path, "templar_armor_feet.png"),
            ItemType.Bow: os.path.join(self.item_textures_path, "Ivory Bow.png"),
            ItemType.Bundle: os.path.join(self.item_textures_path, "War Supplies.png"),
            ItemType.Chestpiece: os.path.join(self.icon_textures_path, "templar_armor_chestpiece.png"),
            ItemType.Rune_Mod: os.path.join(self.item_textures_path, "Rune All Sup.png"),
            ItemType.Usable: os.path.join(self.item_textures_path, "Birthday Cupcake.png"),
            ItemType.Dye: os.path.join(self.item_textures_path, "White Dye.png"),
            ItemType.Materials_Zcoins: os.path.join(self.item_textures_path, "Wood Plank.png"),
            ItemType.Offhand: os.path.join(self.item_textures_path, "Channeling Focus.png"),
            ItemType.Gloves: os.path.join(self.icon_textures_path, "templar_armor_gloves.png"),
            ItemType.Hammer: os.path.join(self.item_textures_path, "PvP Hammer.png"),
            ItemType.Headpiece: os.path.join(self.icon_textures_path, "templar_armor_helmet.png"),
            ItemType.CC_Shards: os.path.join(self.item_textures_path, "Candy Cane Shard.png"),
            ItemType.Key: os.path.join(self.item_textures_path, "Zaishen Key.png"),
            ItemType.Leggings: os.path.join(self.icon_textures_path, "templar_armor_leggins.png"),
            ItemType.Gold_Coin: os.path.join(self.item_textures_path, "Gold.png"),
            ItemType.Quest_Item: os.path.join(self.item_textures_path, "Top Right Map Piece.png"),
            ItemType.Wand: os.path.join(self.item_textures_path, "Shaunur's Scepter.png"),
            ItemType.Shield: os.path.join(self.item_textures_path, "Crude Shield.png"),
            ItemType.Staff : os.path.join(self.item_textures_path, "Holy Staff.png"),
            ItemType.Sword: os.path.join(self.item_textures_path, "Short Sword.png"),
            ItemType.Kit: os.path.join(self.item_textures_path, "Superior Salvage Kit.png"),
            ItemType.Trophy: os.path.join(self.item_textures_path, "Destroyer Core.png"),
            ItemType.Scroll: os.path.join(self.item_textures_path, "Scroll of the Lightbringer.png"),
            ItemType.Daggers: os.path.join(self.item_textures_path, "Balthazar's Daggers.png"),
            ItemType.Present: os.path.join(self.item_textures_path, "Birthday Present.png"),
            ItemType.Minipet: os.path.join(self.item_textures_path, "Miniature Celestial Tiger.png"),
            ItemType.Scythe: os.path.join(self.item_textures_path, "Suntouched Scythe.png"),
            ItemType.Spear: os.path.join(self.item_textures_path, "Suntouched Spear.png"),
            ItemType.Storybook: os.path.join(self.item_textures_path, "Young Heroes of Tyria.png"),
            ItemType.Costume: os.path.join(self.item_textures_path, "Shining Blade costume.png"),
            ItemType.Costume_Headpiece: os.path.join(self.item_textures_path, "Divine_Halo.png"),
            ItemType.Unknown: "",
        }
        
        self.inscription_type_textures: dict[ItemType, str] = {
            ItemType.Weapon: os.path.join(self.item_textures_path, "Inscription weapons.png"),
            ItemType.MartialWeapon: os.path.join(self.item_textures_path, "Inscription martial weapons.png"),
            ItemType.Offhand: os.path.join(self.item_textures_path, "Inscription focus items.png"),
            ItemType.OffhandOrShield: os.path.join(self.item_textures_path, "Inscription focus items or shields.png"),
            ItemType.EquippableItem: os.path.join(self.item_textures_path, "Inscription equippable items.png"),
            ItemType.SpellcastingWeapon: os.path.join(self.item_textures_path, "Inscription spellcasting weapons.png"),
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

        sorted_item_types = [
            ItemType.Axe,
            ItemType.Bow,
            ItemType.Daggers,
            ItemType.Hammer,
            ItemType.Scythe,
            ItemType.Spear,
            ItemType.Sword,
            ItemType.Staff,
            ItemType.Wand,
            ItemType.Offhand,
            ItemType.Shield,
            
            ItemType.Headpiece,
            ItemType.Chestpiece,
            ItemType.Gloves,
            ItemType.Leggings,
            ItemType.Boots,
            
            ItemType.Scroll,
            ItemType.Usable,
            ItemType.Dye,
            ItemType.Key,
            ItemType.Gold_Coin,
            ItemType.Quest_Item,
            ItemType.Kit,
            ItemType.Rune_Mod,
            ItemType.CC_Shards,
            ItemType.Materials_Zcoins,
            ItemType.Salvage,
            ItemType.Present,
            ItemType.Minipet,
            ItemType.Trophy,
            
            ItemType.Weapon,
            ItemType.MartialWeapon,
            ItemType.OffhandOrShield,
            ItemType.EquippableItem,
            ItemType.SpellcastingWeapon,
            ItemType.Costume,
            ItemType.Costume_Headpiece,
            ItemType.Storybook,
            ItemType.Bundle,
            ItemType.Unknown,
        ]
        
        self.filter_actions = [
            enum.ItemAction.Loot,
            enum.ItemAction.Stash,
            enum.ItemAction.Salvage,
            enum.ItemAction.Salvage_Common_Materials,
            enum.ItemAction.Salvage_Rare_Materials,
            enum.ItemAction.Sell_To_Merchant,
            enum.ItemAction.Sell_To_Trader,
            enum.ItemAction.Destroy,
        ]
        
        default_item_types = [
            item_type for item_type in sorted_item_types if item_type not in [
                ItemType.Unknown,
                ItemType.Weapon,
                ItemType.MartialWeapon,
                ItemType.OffhandOrShield,
                ItemType.EquippableItem,
                ItemType.SpellcastingWeapon,
                ItemType.Costume,
                ItemType.Costume_Headpiece,
                ItemType.Storybook,
                ItemType.Bundle,                
                    
                ItemType.Headpiece,
                ItemType.Chestpiece,
                ItemType.Gloves,
                ItemType.Leggings,
                ItemType.Boots,
            ]
        ]
        
        self.action_item_types_map : dict[enum.ItemAction, list[ItemType]] = {            
            enum.ItemAction.Loot : [
                item_type for item_type in sorted_item_types if item_type not in [
                    ItemType.Weapon,
                    ItemType.MartialWeapon,
                    ItemType.OffhandOrShield,
                    ItemType.EquippableItem,
                    ItemType.SpellcastingWeapon,
                ]
            ],
            enum.ItemAction.Stash : [
                item_type for item_type in sorted_item_types if item_type not in [
                    ItemType.Weapon,
                    ItemType.MartialWeapon,
                    ItemType.OffhandOrShield,
                    ItemType.EquippableItem,
                    ItemType.SpellcastingWeapon,
                    ItemType.Bundle,
                ]
            ],
            enum.ItemAction.Salvage : [
                ItemType.Axe,
                ItemType.Bow,
                ItemType.Daggers,
                ItemType.Hammer,
                ItemType.Scythe,
                ItemType.Spear,
                ItemType.Sword,
                ItemType.Staff,
                ItemType.Wand,
                ItemType.Offhand,
                ItemType.Shield,
                ItemType.CC_Shards,
                ItemType.Materials_Zcoins,
                ItemType.Salvage,
                ItemType.Trophy,
            ],
            enum.ItemAction.Salvage_Common_Materials : [
                ItemType.Axe,
                ItemType.Bow,
                ItemType.Daggers,
                ItemType.Hammer,
                ItemType.Scythe,
                ItemType.Spear,
                ItemType.Sword,
                ItemType.Staff,
                ItemType.Wand,
                ItemType.Offhand,
                ItemType.Shield,
                ItemType.CC_Shards,
                ItemType.Materials_Zcoins,
                ItemType.Salvage,
                ItemType.Trophy,
            ],
            enum.ItemAction.Salvage_Rare_Materials : [
                ItemType.Axe,
                ItemType.Bow,
                ItemType.Daggers,
                ItemType.Hammer,
                ItemType.Scythe,
                ItemType.Spear,
                ItemType.Sword,
                ItemType.Staff,
                ItemType.Wand,
                ItemType.Offhand,
                ItemType.Shield,
                ItemType.CC_Shards,
                ItemType.Materials_Zcoins,
                ItemType.Salvage,
                ItemType.Trophy,
            ],
            enum.ItemAction.Sell_To_Merchant : default_item_types,
            enum.ItemAction.Sell_To_Trader : [
                ItemType.Scroll,
                ItemType.Dye,
                ItemType.Materials_Zcoins,
                ItemType.Rune_Mod,
            ],
            enum.ItemAction.Destroy : default_item_types,
        }
        
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
            enum.ItemAction.Loot,
            enum.ItemAction.Stash,
            enum.ItemAction.Sell_To_Merchant,
            enum.ItemAction.Sell_To_Trader,
            enum.ItemAction.Salvage,
            enum.ItemAction.Salvage_Common_Materials,
            enum.ItemAction.Salvage_Rare_Materials,
            enum.ItemAction.Destroy,
        ]
        self.item_action_names = [
            "Loot (Pick Up)",
            "Stash",
            "Sell to Merchant",
            "Sell to Trader (Scrolls, Dyes...)",
            "Smart Salvage (Common or Rare Materials)",
            "Salvage for Common Materials",
            "Salvage for Rare Materials",
            "Destroy",
            ]
                
        
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
                            enum.ItemAction.Salvage: 250,
                        }
        self.selected_filter: Optional[ItemFilter] = None
        self.filters : list[ItemFilter] = [
            ItemFilter("All Items", lambda item: True),
            
            ItemFilter("Weapons", lambda item: item.item_type in self.weapon_types),
            ItemFilter("Axe", lambda item: item.item_type == ItemType.Axe),
            ItemFilter("Bow", lambda item: item.item_type == ItemType.Bow),
            ItemFilter("Daggers", lambda item: item.item_type == ItemType.Daggers),            
            ItemFilter("Hammer", lambda item: item.item_type == ItemType.Hammer),
            ItemFilter("Scythe", lambda item: item.item_type == ItemType.Scythe),
            ItemFilter("Spear", lambda item: item.item_type == ItemType.Spear),
            ItemFilter("Sword", lambda item: item.item_type == ItemType.Sword),
            ItemFilter("Staff", lambda item: item.item_type == ItemType.Staff),
            ItemFilter("Wand", lambda item: item.item_type == ItemType.Wand),
            ItemFilter("Offhand", lambda item: item.item_type == ItemType.Offhand),
            ItemFilter("Shield", lambda item: item.item_type == ItemType.Shield),
            
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
        self.selected_skin_filter: Optional[ItemFilter] = None
        self.skin_search = ""
        self.skin_select_popup = False
        self.skin_select_popup_open = False
        self.show_add_rule_popup = False
        self.rule_name = ""        
        self.rule_filter_popup = False
        self.selected_rule_filter: Optional[RuleFilter] = None
        self.rule_filters : list[RuleFilter] = [
            RuleFilter("All Items", lambda rule: True),   
            RuleFilter("Weapons", lambda rule: any(item_type in self.weapon_types for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Axe", lambda rule: any(item_type == ItemType.Axe for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Bow", lambda rule: any(item_type == ItemType.Bow for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Daggers", lambda rule: any(item_type == ItemType.Daggers for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Hammer", lambda rule: any(item_type == ItemType.Hammer for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Scythe", lambda rule: any(item_type == ItemType.Scythe for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Spear", lambda rule: any(item_type == ItemType.Spear for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Sword", lambda rule: any(item_type == ItemType.Sword for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Staff", lambda rule: any(item_type == ItemType.Staff for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Wand", lambda rule: any(item_type == ItemType.Wand for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Offhand", lambda rule: any(item_type == ItemType.Offhand for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Shield", lambda rule: any(item_type == ItemType.Shield for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Armor", lambda rule: any(item_type in [
                ItemType.Chestpiece,
                ItemType.Headpiece,
                ItemType.Leggings,
                ItemType.Boots,
                ItemType.Gloves,
            ] for item_type in [item.item_type for item in rule.get_items()])),
            RuleFilter("Upgrades", lambda rule: any(item.item_type == ItemType.Rune_Mod for item in rule.get_items())),
            RuleFilter("Consumables", lambda rule: any(item.category in [
                enum.ItemCategory.Alcohol,
                enum.ItemCategory.Sweet,
                enum.ItemCategory.Party,
                enum.ItemCategory.DeathPenaltyRemoval
            ] for item in rule.get_items())),
            RuleFilter("Alcohol", lambda rule: any(item.category == enum.ItemCategory.Alcohol for item in rule.get_items())),
            RuleFilter("Sweets", lambda rule: any(item.category == enum.ItemCategory.Sweet for item in rule.get_items())),
            RuleFilter("Party", lambda rule: any(item.category == enum.ItemCategory.Party for item in rule.get_items())),
            RuleFilter("Death Penalty Removal", lambda rule: any(item.category == enum.ItemCategory .DeathPenaltyRemoval for item in rule.get_items())),
            RuleFilter("Scrolls", lambda rule: any(item.category == enum.ItemCategory.Scroll for item in rule.get_items())),
            RuleFilter("Tomes", lambda rule: any(item.category == enum.ItemCategory.Tome for item in rule.get_items())),
            RuleFilter("Keys", lambda rule: any(item.category == enum.ItemCategory.Key for item in rule.get_items())),
            RuleFilter("Materials", lambda rule: any(item.category == enum.ItemCategory.Material for item in rule.get_items())),
            RuleFilter("Trophies", lambda rule: any(item.category == enum.ItemCategory.Trophy for item in rule.get_items())),
            RuleFilter("Reward Trophies", lambda rule: any(item.category == enum.ItemCategory.RewardTrophy for item in rule.get_items())),
            RuleFilter("Quest Items", lambda rule: any(item.category == enum.ItemCategory.QuestItem for item in rule.get_items())),            
        ]
                
        self.data_collector = data_collector.DataCollector()
        self.filter_weapon_mods()        
        self.filter_items()    
        self.filter_rules()
        
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
        if not settings.current.window_visible:
            return
            
        if self.first_draw:
            PyImGui.set_next_window_pos(
                settings.current.window_position[0], settings.current.window_position[1]
            )
            PyImGui.set_next_window_size(
                settings.current.window_size[0], settings.current.window_size[1]
            )
            PyImGui.set_next_window_collapsed(settings.current.window_collapsed, 0)
        
        window_style = style.Style()
        window_style.push_style()
            
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
            
            width = PyImGui.get_content_region_avail()[0]
            PyImGui.push_item_width(width - 100)
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
            
            if GUI.image_button(texture_map.CoreTextures.UI_Destroy.value, (20, 20)) and len(settings.current.profiles) > 1:
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

            if PyImGui.begin_tab_bar("LootExTabBar"):
                self.draw_general_settings()
                self.draw_by_item_type()
                self.draw_by_item_skin()
                self.draw_low_req()
                self.draw_weapon_mods()
                self.draw_runes()
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

        window_style.pop_style()
        
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
            
            localization_missing, language = self.data_collector.is_missing_localization(cached_item.id)
            collected, missing = self.data_collector.is_item_collected(cached_item.id) if cached_item.id != 0 else (True, "")
            mods_missing, mod_missing = self.data_collector.has_uncollected_mods(cached_item.id) if cached_item.id != 0 else (False, "")
            complete = True
            
            if not localization_missing:
                complete = (collected and not mods_missing)
                
                if not complete:
                    PyImGui.push_style_color(
                        PyImGui.ImGuiCol.ChildBg,
                        Utils.ColorToTuple(Utils.RGBToColor(255, 255, 0, 125))
                    )
            else:
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ChildBg,
                    Utils.ColorToTuple(Utils.RGBToColor(255, 178, 102, 125))
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
                action_texture = self.action_infos.get_texture(cached_item.action, None)                
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
                
            if not complete or localization_missing:
                PyImGui.pop_style_color(1)
            
            PyImGui.end_child()
            PyImGui.pop_style_color(1)
            
            if PyImGui.is_item_clicked(0) and cached_item and cached_item.data and not cached_item.data.wiki_scraped:
                data.Reload()                  
                item = data.Items.get_item(cached_item.item_type, cached_item.model_id)
                
                if item and not item.wiki_scraped:
                    wiki_scraper.WikiScraper.scrape_multiple_entries([item])
                    # messaging.SendMergingMessage()
                    
            
                
            if cached_item:
                if PyImGui.is_item_hovered():
                    PyImGui.set_next_window_size(400, 0)
                    
                    PyImGui.begin_tooltip()
                    if cached_item.data:
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
                        PyImGui.text_colored(language or missing, (255, 0, 0, 255))
                        
                    if localization_missing:
                        PyImGui.text_colored(language, (255, 0, 0, 255))
                        
                    if mods_missing:
                        PyImGui.text_colored(mod_missing, (255, 0, 0, 255))
                    
                    if cached_item.data and not cached_item.data.wiki_scraped:
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
                        data.SaveRunes()
                        data.SaveWeaponMods(True)
                        
                        
                                                 
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
                        loot_handling.LootHandler().SetLootRange(loot_range)
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
                    self._input_int_setting("Identification Kits", settings.current.profile.identification_kits, os.path.join(self.item_textures_path, "Superior Identification Kit.png"))
                    self._input_int_setting("Salvage Kits", settings.current.profile.salvage_kits, os.path.join(self.item_textures_path, "Salvage Kit.png"))
                    self._input_int_setting("Expert Salvage Kits", settings.current.profile.expert_salvage_kits, os.path.join(self.item_textures_path, "Expert Salvage Kit.png"))
                    self._input_int_setting("Lockpicks", settings.current.profile.lockpicks, os.path.join(self.item_textures_path, "Lockpick.png"))

                PyImGui.end_child()
                
                PyImGui.text("Nick Settings")
                PyImGui.separator()
                
                if PyImGui.begin_child("GeneralSettings_Nick", (subtab_size[0], 0), True, PyImGui.WindowFlags.NoBackground) and settings.current.profile:
                    
                    self._slider_int_setting("Nick Weeks to Keep", settings.current.profile.nick_weeks_to_keep, os.path.join(self.item_textures_path, "Gift_of_the_Traveler.png"), -1, 137)                    
                    self._slider_int_setting("Nick Items to Keep", settings.current.profile.nick_items_to_keep, os.path.join(self.item_textures_path, "Red_Iris_Flower.png"), 0, 500)    
                    
                    PyImGui.spacing()
                     
                    height = 20                    
                    nick_gradient = GUI.get_gradient_colors((0.5, 1, 0, 0.5), (1, 0, 0, 0.5), settings.current.profile.nick_weeks_to_keep + 1)
                    nick_item_size = PyImGui.get_content_region_avail()
                    
                    if PyImGui.is_rect_visible(1, height + 4):
                        PyImGui.begin_table("NickItemsTable", 3, PyImGui.TableFlags.ScrollY | PyImGui.TableFlags.BordersOuterV | PyImGui.TableFlags.BordersOuterH, nick_item_size[0], nick_item_size[1])    
                        # PyImGui.table_setup_column("Index", PyImGui.TableColumnFlags.WidthFixed, 25)
                        PyImGui.table_setup_column("Icon", PyImGui.TableColumnFlags.WidthFixed, 20)
                        PyImGui.table_setup_column("Name")
                        PyImGui.table_setup_column("Weeks Until Next Nick", PyImGui.TableColumnFlags.WidthFixed, 85)   
                        
                        for i, nick_item in enumerate(data.Nick_Cycle):
                             
                            if nick_item.weeks_until_next_nick is None:
                                continue
                            
                            if nick_item.weeks_until_next_nick > settings.current.profile.nick_weeks_to_keep:
                                continue
                            
                            # PyImGui.table_next_row()
                            if not PyImGui.is_rect_visible(1, height):
                                PyImGui.dummy(1, height)
                                PyImGui.table_next_column()
                                PyImGui.table_next_column()
                                PyImGui.table_next_column()
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
                            GUI.vertical_centered_text(nick_item.name, None, height)
                            hovered = PyImGui.is_item_hovered() or hovered
                            
                            
                            color = (0, 1, 0, 0.9) if nick_item.weeks_until_next_nick == 0 else \
                                    (0, 1, 0, 0.7) if nick_item.weeks_until_next_nick == 1 else \
                                    nick_gradient[nick_item.weeks_until_next_nick] if nick_item.weeks_until_next_nick < len(nick_gradient) else (1, 1, 1, 1) 

                            PyImGui.table_next_column()
                                                   
                            GUI.vertical_centered_text("current week" if nick_item.weeks_until_next_nick == 0 else f"next week"  if nick_item.weeks_until_next_nick == 1 else f"{nick_item.weeks_until_next_nick} weeks", None, height, color=color)
                            # PyImGui.text_colored(
                            #     "current week" if nick_item.weeks_until_next_nick == 0 else f"next week"  if nick_item.weeks_until_next_nick == 1 else f"{nick_item.weeks_until_next_nick} weeks" , 
                            #     color
                            # )
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
                            file_path = os.path.join(self.item_textures_path, f"{dye.name} Dye.png")
                            if dye not in settings.current.profile.dyes:
                                settings.current.profile.dyes[dye] = False

                            color = utility.Util.GetDyeColor(
                                dye, 205 if settings.current.profile.dyes[dye] else 125)
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color))
                            hover_color = utility.Util.GetDyeColor(dye)
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(hover_color))                            
                            UI.ImageToggleXX(file_path, 16.25, 20, 
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

    def draw_by_item_type(self):
        if PyImGui.begin_tab_item("By Item Type") and settings.current.profile:
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
                            
                            if PyImGui.selectable(f"{i+1}. "+ filter.name, filter == settings.current.selected_filter, PyImGui.SelectableFlags.NoFlag, (selection_size[0] - 37, 0)):
                                settings.current.selected_filter = filter
                            
                            if PyImGui.is_item_hovered():
                                i = self.filter_actions.index(filter.action) if filter.action in self.filter_actions else 0
                                name = self.filter_action_names[i]
                                ImGui.show_tooltip(name)
                            
                            PyImGui.same_line(0, 10)
                            
                            screen_cursor = PyImGui.get_cursor_screen_pos()
                            down_rect = (screen_cursor[0], screen_cursor[1], button_size[0], button_size[1])
                            down_hovered = GUI.is_mouse_in_rect(down_rect)
                            is_clicked = PyImGui.is_mouse_clicked(0) and down_hovered
                            texture = texture_map.CoreTextures.UI_Down_Active if is_clicked else texture_map.CoreTextures.UI_Down_Hovered if down_hovered else texture_map.CoreTextures.UI_Down
                            ImGui.DrawTexture(texture_path=texture.value, width=button_size[0], height=button_size[1])
                            
                            if is_clicked:
                                if i < len(settings.current.profile.filters) - 1:
                                    settings.current.profile.move_filter(filter, i + 1)
                                    settings.current.profile.save()

                            PyImGui.same_line(0, 0)
                            
                            screen_cursor = PyImGui.get_cursor_screen_pos()
                            up_rect = (screen_cursor[0], screen_cursor[1], button_size[0], button_size[1])
                            up_hovered = GUI.is_mouse_in_rect(up_rect)
                            is_clicked = PyImGui.is_mouse_clicked(0) and up_hovered
                            texture = texture_map.CoreTextures.UI_Up_Active if is_clicked else texture_map.CoreTextures.UI_Up_Hovered if up_hovered else texture_map.CoreTextures.UI_Up
                            ImGui.DrawTexture(texture_path=texture.value, width=button_size[0], height=button_size[1])
                            
                            if is_clicked:
                                if i > 0:                                    
                                    settings.current.profile.move_filter(filter, i - 1)
                                    settings.current.profile.save()
                            
                PyImGui.end_child()

                if PyImGui.button("Add Filter", subtab_size[0]):
                    self.show_add_filter_popup = not self.show_add_filter_popup
                    if self.show_add_filter_popup:
                        PyImGui.open_popup("Add Filter")

            PyImGui.end_child()

            PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

            # Right panel: Loot Filter Details
            if PyImGui.begin_child("filter_child", (tab_size[0] - (tab_size[0] * 0.3) - 10, 0), settings.current.selected_filter is None, PyImGui.WindowFlags.NoFlag):
                if settings.current.selected_filter:
                    filter = settings.current.selected_filter

                    if PyImGui.begin_child("filter_name_child", (0, 45), True, PyImGui.WindowFlags.NoFlag): 
                        PyImGui.push_item_width(tab_size[0] - (tab_size[0] * 0.3) - 63)
                        # Edit filter name
                        name = PyImGui.input_text(
                            "##name_edit", filter.name)
                        if name and name != filter.name:
                            filter.name = name
                            settings.current.profile.save()

                        PyImGui.same_line(0, 5)

                        # Delete filter button
                        if GUI.image_button(texture_map.CoreTextures.UI_Destroy.value, (20, 20)):
                            settings.current.profile.remove_filter(
                                filter)
                            settings.current.profile.save()
                            settings.current.selected_filter = settings.current.profile.filters[
                                0] if settings.current.profile.filters else None
                            self.show_add_filter_popup = False
                            PyImGui.close_current_popup()               
                    PyImGui.end_child()
                        
                    # Filter actions
                    remaining_size = PyImGui.get_content_region_avail()
                    height = min(self.action_heights.get(filter.action, 45), remaining_size[0])
                    if PyImGui.begin_child("filter_actions", (0, height), True, PyImGui.WindowFlags.NoFlag):                         
                        if filter.action:
                            action_texture = self.action_textures.get(filter.action, None)
                            height = 24
                            if action_texture:
                                ImGui.DrawTexture(action_texture, height, height)
                            else:
                                PyImGui.dummy(height, height)
                            PyImGui.same_line(0, 5)            
                            PyImGui.push_item_width(PyImGui.get_content_region_avail()[0])
                            action = PyImGui.combo("##RuleAction", self.item_actions.index(
                                filter.action) if filter.action in self.item_actions else 0, self.item_action_names)
                            
                            if self.item_actions[action] != filter.action:
                                filter.action = self.item_actions[action]
                                settings.current.profile.save()
                            
                            ImGui.show_tooltip((f"{self.action_infos.get_name(enum.ItemAction.Loot)} and " if filter.action not in [enum.ItemAction.NONE, enum.ItemAction.Loot, enum.ItemAction.Destroy] else "") + f"{self.action_infos.get_name(filter.action)}")
                                        
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
                            width = width - 50
                            item_width = 36
                            columns = max(1, math.floor(width / item_width))
                            
                            has_common_materials = len(data.Common_Materials) > 0 if filter.action in [enum.ItemAction.Salvage, enum.ItemAction.Salvage_Common_Materials] else False
                            has_rare_materials = len(data.Rare_Materials) > 0 if filter.action in [enum.ItemAction.Salvage, enum.ItemAction.Salvage_Rare_Materials] else False
                            
                            rows = (math.ceil(len(data.Common_Materials) / columns) if has_common_materials else 0) + (math.ceil(len(data.Rare_Materials) / columns) if has_rare_materials else 0)
                                                            
                            self.action_heights[enum.ItemAction.Salvage_Rare_Materials] = (rows * item_width) + 123 + 8
                            self.action_heights[enum.ItemAction.Salvage_Common_Materials] = (rows * item_width) + 125 + 8
                            self.action_heights[enum.ItemAction.Salvage] = (rows * item_width) + 123 + 8 + 20
                            
                            PyImGui.begin_child("salvage_materials", (0, 0), True, PyImGui.WindowFlags.NoFlag)      
                                                                                        
                            if PyImGui.is_rect_visible(0, self.action_heights[enum.ItemAction.Salvage] - 20):
                                PyImGui.begin_table("salvage_materials_table", columns, PyImGui.TableFlags.ScrollY, 0, 0)                                
                                if filter.action == enum.ItemAction.Salvage or filter.action == enum.ItemAction.Salvage_Common_Materials:
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
                                
                                
                                if filter.action == enum.ItemAction.Salvage:
                                    ypos = PyImGui.get_cursor_pos_y() + 2
                                    for _ in range(columns):
                                        PyImGui.table_next_column()
                                        PyImGui.set_cursor_pos_y(ypos)
                                        PyImGui.separator()
                                    
                                if filter.action == enum.ItemAction.Salvage_Rare_Materials or filter.action == enum.ItemAction.Salvage:    
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
                            case enum.ItemAction.Salvage:
                                draw_salvage_options()                                        
                                pass
                            case enum.ItemAction.Salvage_Common_Materials:
                                draw_salvage_options()                                        
                                pass
                            case enum.ItemAction.Salvage_Rare_Materials:
                                draw_salvage_options()                                        
                                pass
                            
                            case _:
                                pass

                    PyImGui.end_child()

                    # Filter item types
                    sub_subtab_size = PyImGui.get_content_region_avail()
                    rarity_width = 60 if sub_subtab_size[1] > 268 else 80
                    if PyImGui.begin_child("loot_item_types_filter_table", (sub_subtab_size[0] - rarity_width - 5, 0), True, PyImGui.WindowFlags.NoFlag) and PyImGui.is_rect_visible(0, 20):  
                        PyImGui.text("Item Types")
                        PyImGui.separator()
                        width, height = PyImGui.get_content_region_avail()
                        width = width - 20
                        item_width = 36
                        columns = max(1, math.floor(width / item_width))
                        
                        if PyImGui.is_rect_visible(1, 20):                                                    
                            PyImGui.begin_table(
                                "filter_table", columns, PyImGui.TableFlags.ScrollY)

                            PyImGui.table_next_column()

                            for item_type in self.action_item_types_map[filter.action]:
                                if item_type in self.item_type_textures:
                                    if filter.item_types[item_type] is None:
                                        continue

                                    changed, filter.item_types[item_type] = self.draw_item_type_selectable(
                                        item_type, filter.item_types[item_type])
                                    PyImGui.table_next_column()
                                        
                                    if changed:
                                        if self.py_io.key_ctrl:
                                            selected = filter.item_types[item_type]
                                            # Toggle all item types
                                            for it in self.action_item_types_map[filter.action] or ItemType:
                                                if it in filter.item_types:
                                                    filter.item_types[it] = selected
                                                    
                                        settings.current.profile.save()
                                        
                            PyImGui.end_table()

                    PyImGui.end_child()

                    PyImGui.same_line(0, 5)

                    # Filter rarities
                    if PyImGui.begin_child("loot_rarity_filter_table", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                        count = 0
                        # ConsoleLog("LootEx", PyImGui.get_content_region_max()[1])
                        
                        PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)
                        PyImGui.text("Rarities")
                        
                        texture = os.path.join(self.item_textures_path, "Platinum Sickles.png")
                        texture_exists = os.path.exists(texture) and os.path.isfile(texture) and texture.endswith((".png", ".jpg", ".jpeg", ".webp"))
                        
                        # PyImGui.separator()   
                        for rarity, selected in filter.rarities.items():  
                            factor = 52 / 64
                            skin_size = 42
                            frame_size = (skin_size * factor, skin_size)
                            PyImGui.set_cursor_pos_x(PyImGui.get_cursor_pos_x() + 3)
                            screen_cursor = PyImGui.get_cursor_screen_pos()
                            is_hovered = GUI.is_mouse_in_rect((screen_cursor[0], screen_cursor[1], frame_size[0], frame_size[1])) and PyImGui.is_window_hovered()
                            alpha = 255 if is_hovered else 225 if (selected) else 50
                            texture_alpha = 255 if is_hovered else 225 if (selected) else 100
                            frame_color =  GUI.get_rarity_rgba_color(rarity, texture_alpha) if selected else (100,100,100, texture_alpha)
                            texture_color =  (255 ,255,255 , texture_alpha) if selected else (100,100,100, 200 if is_hovered else 125 )
                            
                            # PyImGui.begin_child(f"rarity_{rarity}", (frame_size[0], frame_size[1]), False, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar)
                            
                            if is_hovered:
                                rect = (screen_cursor[0], screen_cursor[1], screen_cursor[0] + frame_size[0], screen_cursor[1] + frame_size[1])           
                                PyImGui.draw_list_add_rect_filled(rect[0], rect[1], rect[2], rect[3], Utils.RGBToColor(frame_color[0], frame_color[1], frame_color[2], 50), 1.0, 0)                                                     
                                                            
                            cursor = PyImGui.get_cursor_pos()
                            # PyImGui.set_cursor_pos(cursor[0] + (frame_size * count), cursor[1])
                            ImGui.DrawTextureExtended(texture_path=texture_map.CoreTextures.UI_Inventory_Slot.value, size=(frame_size[0], frame_size[1]), tint=frame_color)
                            PyImGui.set_cursor_pos(cursor[0], cursor[1] + ((frame_size[1] - skin_size) / 2))
                            
                            if texture_exists:                                        
                                ImGui.DrawTextureExtended(texture_path=texture, size=(skin_size, skin_size), tint=texture_color)
                            else:
                                PyImGui.push_style_color(
                                    PyImGui.ImGuiCol.Text, frame_color)
                                PyImGui.text(IconsFontAwesome5.ICON_SHIELD_ALT)  
                                PyImGui.pop_style_color(1)
                            # PyImGui.end_child()
                            
                            if PyImGui.is_item_clicked(0) and is_hovered:                                
                                if self.py_io.key_ctrl:
                                    for r in filter.rarities.keys():
                                        filter.rarities[r] = not selected
                                else:
                                    filter.rarities[rarity] = not selected
                                    
                                settings.current.profile.save()
                            
                            if is_hovered:
                                ImGui.show_tooltip(f"Rarity: {rarity.name}")
                                
                            count += 1  
                            # PyImGui.same_line(10 + ((frame_size[0] + 2) * count), 0)
                                        
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
                    settings.current.profile.add_filter(
                        Filter(self.filter_name)
                    )
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
    
    #region By Skin Tab    
    def draw_rule_filter_popup(self):
        if self.rule_filter_popup:
            PyImGui.open_popup("Filter Rules")

        if PyImGui.begin_popup("Filter Rules"):
            
            remaining_size = PyImGui.get_content_region_avail()
            
            for filter in self.rule_filters:
                if filter:
                    if PyImGui.selectable(filter.name, self.selected_rule_filter == filter, PyImGui.SelectableFlags.NoFlag, (remaining_size[0], 0)):
                        self.selected_rule_filter = filter
                        self.filter_rules()
                        
                        self.rule_filter_popup = False
                        PyImGui.close_current_popup()
        
            PyImGui.end_popup()
        
        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.rule_filter_popup:
                PyImGui.close_current_popup()
                self.rule_filter_popup = False        
    
    def filter_rules(self):
        if not settings.current.profile:
            return
        
        self.selectable_rules = []
        search = self.rule_search.lower()
        
        for rule in settings.current.profile.rules:
            if self.selected_rule_filter is None or self.selected_rule_filter.match(rule):
                if not search or \
                    search in rule.skin.lower() or \
                    any(search in str(model_id) for model_id in [
                            model_info.model_id for model_info in rule.models
                    ]):
                    
                    self.selectable_rules.append(SelectableWrapper(rule, self.selected_rule == rule))                

        pass
    
    def draw_selectable_rule(self, rule: action_rule.ActionRule, is_selected: bool, is_hovered: bool = False) -> tuple[bool, bool]:
        size = 32        
        skin_size = size - 6        
        padding = (size - skin_size) / 2
        delete_clicked = False
        
        if PyImGui.is_rect_visible(1, size):
            if PyImGui.begin_child(f"rule_{rule.skin}", (0, size), False, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar):
                texture = os.path.join(self.item_textures_path, f"{rule.skin}")   
                remaining_size = PyImGui.get_content_region_avail()
                
                screen_cursor = PyImGui.get_cursor_screen_pos()   
                is_visible = PyImGui.is_rect_visible(10, 1)      
                is_hovered = GUI.is_mouse_in_rect((screen_cursor[0], screen_cursor[1], remaining_size[0], remaining_size[1])) and is_visible and PyImGui.is_window_hovered()
                
                if is_hovered:
                    PyImGui.draw_list_add_rect_filled(screen_cursor[0], screen_cursor[1], screen_cursor[0] + remaining_size[0], screen_cursor[1] + size, self.style.Hovered_Item.color_int, 1.0, 0)
                    PyImGui.draw_list_add_rect(screen_cursor[0], screen_cursor[1], screen_cursor[0] + remaining_size[0], screen_cursor[1] + size, self.style.Hovered_Item.color_int, 1.0, 0, 2.0)
                    
                if is_selected:
                    PyImGui.draw_list_add_rect_filled(screen_cursor[0], screen_cursor[1], screen_cursor[0] + remaining_size[0], screen_cursor[1] + size, self.style.Selected_Item.color_int, 1.0, 0)
                    PyImGui.draw_list_add_rect(screen_cursor[0], screen_cursor[1], screen_cursor[0] + remaining_size[0], screen_cursor[1] + size, self.style.Selected_Item.color_int, 1.0, 0, 2.0)
                
                cursor = PyImGui.get_cursor_pos()
                PyImGui.set_cursor_pos(cursor[0] + padding, cursor[1] + padding)
                
                PyImGui.begin_child(f"skin_texture_child{rule.skin}", (skin_size, skin_size), False, PyImGui.WindowFlags.NoFlag| PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar)
                if texture.endswith(((".jpg",".png"))) and os.path.exists(texture):
                    ImGui.DrawTextureExtended(texture_path=texture, size=(skin_size, skin_size))                    
                else:            
                    ImGui.push_font("Bold", 28)
                    text_size = PyImGui.calc_text_size(IconsFontAwesome5.ICON_QUESTION)
                    PyImGui.set_cursor_pos((((skin_size - text_size[0])) / 2), 4 + ((skin_size - text_size[1]) / 2))
                    PyImGui.text(IconsFontAwesome5.ICON_QUESTION)
                    ImGui.pop_font()
                PyImGui.end_child()
                            
                PyImGui.same_line(0, 5)
                without_file_ending = rule.skin.split(".")[0]
                
                GUI.vertical_centered_text(text=without_file_ending or "No Skin Selected", desired_height=skin_size + 4)
                
                if is_selected:
                    PyImGui.same_line(0, 5)
                    delete_rect = (screen_cursor[0] + remaining_size[0] - 30, screen_cursor[1] + 6, 24, 24)
                    delete_hovered = GUI.is_mouse_in_rect(delete_rect)
                    
                    PyImGui.set_cursor_screen_pos(delete_rect[0], delete_rect[1])
                    ImGui.DrawTextureExtended(texture_path=texture_map.CoreTextures.UI_Cancel_Hovered.value if delete_hovered else texture_map.CoreTextures.UI_Cancel.value, size=(24, 24), tint=(150,150,150,255) if not delete_hovered else (255,255,255,255))
                    
                    if PyImGui.is_item_clicked(0):                        
                        delete_clicked = True
                        
                        if settings.current.profile:
                            settings.current.profile.remove_rule(rule)
                            settings.current.profile.save()
                            
                        self.selected_rule = None
                        self.selected_rule_changed = True
                        self.filter_rules()                        
                        pass
                    
                    ImGui.show_tooltip("Delete Rule")
                                
            PyImGui.end_child()
            
        else:
            PyImGui.dummy(0, skin_size)
        
        is_hovered = PyImGui.is_item_hovered()
        
        if not delete_clicked and PyImGui.is_item_clicked(0):
            is_selected = not is_selected
        
        return is_selected, is_hovered
    
    def draw_skin_selectable(self, skin: str, is_selected: bool) -> tuple[bool, bool]:
        size = 38
        padding = 4
        skin_size = size - (padding * 2)
        
        if PyImGui.is_rect_visible(0, size):            
            if PyImGui.begin_child(f"skin_{skin}", (0, size), False, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar):
                texture = os.path.join(self.item_textures_path, f"{skin}")   
                remaining_size = PyImGui.get_content_region_avail()
                
                cursor = PyImGui.get_cursor_screen_pos()   
                is_visible = PyImGui.is_rect_visible(10, 1)      
                is_hovered = GUI.is_mouse_in_rect((cursor[0], cursor[1], remaining_size[0], remaining_size[1])) and is_visible and PyImGui.is_window_hovered()
                
                if is_hovered:
                    PyImGui.draw_list_add_rect_filled(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + size, self.style.Hovered_Item.color_int, 1.0, 0)
                    PyImGui.draw_list_add_rect(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + size, self.style.Hovered_Item.color_int, 1.0, 0, 2.0)
                    
                if is_selected:
                    PyImGui.draw_list_add_rect_filled(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + size, self.style.Selected_Item.color_int, 1.0, 0)
                    PyImGui.draw_list_add_rect(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + size, self.style.Selected_Item.color_int, 1.0, 0, 2.0)
                
                cursor = PyImGui.get_cursor_pos()
                PyImGui.set_cursor_pos(cursor[0] + padding, cursor[1] + padding)
                
                PyImGui.begin_child(f"skin_texture_child{skin}", (skin_size, skin_size), False, PyImGui.WindowFlags.NoFlag| PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar)
                if texture.endswith((".jpg",".png")) and os.path.exists(texture):
                    ImGui.DrawTextureExtended(texture_path=texture, size=(skin_size, skin_size))                    
                else:            
                    ImGui.push_font("Bold", 28)
                    text_size = PyImGui.calc_text_size(IconsFontAwesome5.ICON_QUESTION)
                    PyImGui.set_cursor_pos((((skin_size - text_size[0])) / 2), 4 + ((skin_size - text_size[1]) / 2))
                    PyImGui.text(IconsFontAwesome5.ICON_QUESTION)
                    ImGui.pop_font()
                PyImGui.end_child()
                            
                PyImGui.same_line(0, 5)
                without_file_ending = skin.split(".")[0]
                
                GUI.vertical_centered_text(text=without_file_ending or "No Skin Selected", desired_height=skin_size + 4)
                                
            PyImGui.end_child()
            
        else:
            PyImGui.dummy(0, skin_size)
        
        is_hovered = PyImGui.is_item_hovered()
        
        if PyImGui.is_item_clicked(0):
            is_selected = not is_selected
        
        return is_selected, is_hovered
            
    def draw_skin_select_popup(self):
        if not settings.current.profile or not self.selected_rule:
            return
        
        opened = False
        is_mouse_over = False
        if self.skin_select_popup:
            if not self.skin_select_popup_open:
                PyImGui.set_next_window_size(300, 600)
                PyImGui.set_next_window_pos(self.py_io.mouse_pos_x, self.py_io.mouse_pos_y)
                opened = True
        else:
            self.skin_select_popup_open = False
            return
            
        self.skin_select_popup_open = PyImGui.begin("Select Skin", PyImGui.WindowFlags.NoTitleBar | PyImGui.WindowFlags.NoResize | PyImGui.WindowFlags.NoMove)
        
        if self.skin_select_popup_open:     
            popup_size = PyImGui.get_content_region_avail()       
            changed, search = UI.search_field("##search_skin", self.skin_search, f"Search for skin name or model id ...", popup_size[0] - 30)
            if changed:
                self.skin_search = search.lower()
        
            PyImGui.same_line(0, 5)
            
            if PyImGui.button(IconsFontAwesome5.ICON_FILTER):
                self.filter_popup = not self.filter_popup
                if self.filter_popup:
                    PyImGui.open_popup("Filter Loot Items")
                pass
                
            
            existing_skins_from_rules = [
                rule.skin for rule in settings.current.profile.rules if rule.skin and rule != self.selected_rule
            ]
            
            if PyImGui.begin_child("skin_selection_list", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                sorted_skins = sorted(data.ItemsBySkins.items(), key=lambda x: x[0].lower())
                
                for skin, items in sorted_skins:
                    if skin in existing_skins_from_rules:
                        continue
                    
                    if not self.skin_search or self.skin_search in skin.lower():
                        if not self.selected_filter or any(self.selected_filter.match(item) for item in items):
                            selected, hovered = self.draw_skin_selectable(skin, skin == self.selected_rule.skin if self.selected_rule else False)
                            
                            if self.selected_rule_changed and selected:
                                self.selected_rule_changed = False
                                PyImGui.set_scroll_here_y(0.5)
                                                            
                            if selected and skin != self.selected_rule.skin:
                                if self.selected_rule:
                                    self.selected_rule.skin = skin                                   
                                    self.selectable_items = data.ItemsBySkins.get(self.selected_rule.skin, []) if self.selected_rule else []
                                    
                                    self.skin_search = ""            
                                    settings.current.profile.save()     
                                    
                                    self.skin_select_popup = False  
                                
            PyImGui.end_child()
                
            window_pos = PyImGui.get_window_pos()
            window_size = PyImGui.get_window_size()
            window_rect = (window_pos[0], window_pos[1], window_size[0], window_size[1])
            is_mouse_over = GUI.is_mouse_in_rect(window_rect)
        
        PyImGui.end()   

        if self.skin_select_popup_open and not is_mouse_over:
            if not self.filter_popup:
                if PyImGui.is_mouse_clicked(0):
                    self.skin_select_popup_open = False
                    self.skin_select_popup = False
                
        self.draw_filter_popup()
    
    def draw_item_selectable(self, item: models.Item, is_selected: bool) -> tuple[bool, bool]:
        size = 38
        padding = 4
        skin_size = size - (padding * 2)
        
        if PyImGui.is_rect_visible(size, size):            
            if PyImGui.begin_child(f"item_{item.model_id}_{item.inventory_icon or ""}", (0, size), False, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.AlwaysAutoResize):
                texture = os.path.join(self.item_textures_path, f"{item.inventory_icon}")   
                remaining_size = PyImGui.get_content_region_avail()
                
                cursor = PyImGui.get_cursor_screen_pos()   
                is_visible = PyImGui.is_rect_visible(10, 1)      
                is_hovered = GUI.is_mouse_in_rect((cursor[0], cursor[1], remaining_size[0], remaining_size[1])) and is_visible and PyImGui.is_window_hovered()
                
                if is_hovered:
                    PyImGui.draw_list_add_rect_filled(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + remaining_size[1], self.style.Hovered_Colored_Item.color_int, 1.0, 0)
                    PyImGui.draw_list_add_rect(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + remaining_size[1], self.style.Hovered_Colored_Item.color_int, 1.0, 0, 2.0)
                    
                if is_selected:
                    PyImGui.draw_list_add_rect_filled(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + remaining_size[1], self.style.Selected_Colored_Item.color_int, 1.0, 0)
                    PyImGui.draw_list_add_rect(cursor[0], cursor[1], cursor[0] + remaining_size[0], cursor[1] + remaining_size[1], self.style.Selected_Colored_Item.color_int, 1.0, 0, 2.0)
                
                cursor = PyImGui.get_cursor_pos()
                PyImGui.set_cursor_pos(cursor[0] + padding, cursor[1] + padding)
                
                PyImGui.begin_child(f"skin_texture_child{item.model_id}_{item.inventory_icon or ""}", (skin_size, skin_size), False, PyImGui.WindowFlags.NoFlag| PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar)
                if texture.endswith((".jpg",".png")) and os.path.exists(texture):
                    ImGui.DrawTextureExtended(texture_path=texture, size=(skin_size, skin_size))                    
                else:            
                    ImGui.push_font("Bold", 28)
                    text_size = PyImGui.calc_text_size(IconsFontAwesome5.ICON_QUESTION)
                    PyImGui.set_cursor_pos((((skin_size - text_size[0])) / 2), 4 + ((skin_size - text_size[1]) / 2))
                    PyImGui.text(IconsFontAwesome5.ICON_QUESTION)
                    ImGui.pop_font()
                PyImGui.end_child()
                            
                PyImGui.same_line(0, 5)
                
                color = (1, 1, 1, (255 / 255 if is_selected else 100 / 255))
                GUI.vertical_centered_text(text=item.name + ("\n" + "\n".join([utility.Util.reformat_string(attribute.name) for attribute in item.attributes]) if len(item.attributes) == 1 else ""), desired_height=skin_size + 4, color=color)
                                
            PyImGui.end_child()
            
        else:
            PyImGui.dummy(size, size)
        
        is_hovered = PyImGui.is_item_hovered()
        
        if is_hovered:
            PyImGui.set_next_window_size(400, 0)
            PyImGui.begin_tooltip()
            
            self.draw_item_header(item_info=item, border=False, image_size=50)
            PyImGui.dummy(50, 0)
            PyImGui.same_line(0, 10)
            height = len(item.attributes) * PyImGui.get_text_line_height() + (28 if item.attributes else 0)
            PyImGui.begin_child("advanced details", (0, height), False, PyImGui.WindowFlags.NoFlag)
            if item.attributes:
                PyImGui.text("Attributes")
                PyImGui.separator()
                PyImGui.text("\n".join([utility.Util.reformat_string(attribute.name) for attribute in item.attributes]) if item.attributes else "")
                
            PyImGui.end_child()
            
            PyImGui.end_tooltip()
            
        
        clicked = False
        
        if PyImGui.is_item_clicked(0):
            is_selected = not is_selected
            clicked = True
        
        return is_selected, clicked
    
    def draw_mod_selectable(self, mod: models.WeaponMod, is_selected: bool, mod_info : models.ModInfo | None) -> tuple[bool, bool]:
        clicked = False
        cog_clicked = False
        is_hovered = False
        cog_hovered = False
        
        if PyImGui.begin_child(f"mod_{mod.identifier}_selectable", (0, 32), False, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse):
            size = PyImGui.get_content_region_avail()
            screen_cursor = PyImGui.get_cursor_screen_pos()
            is_hovered = GUI.is_mouse_in_rect((screen_cursor[0], screen_cursor[1], size[0], size[1])) and PyImGui.is_window_hovered()
            
            if is_hovered:
                PyImGui.draw_list_add_rect_filled(screen_cursor[0], screen_cursor[1], screen_cursor[0] + size[0], screen_cursor[1] + size[1], self.style.Hovered_Colored_Item.color_int, 1.0, 0)
                PyImGui.draw_list_add_rect(screen_cursor[0], screen_cursor[1], screen_cursor[0] + size[0], screen_cursor[1] + size[1], self.style.Hovered_Colored_Item.color_int, 1.0, 0, 2.0)
                
            if is_selected:
                PyImGui.draw_list_add_rect_filled(screen_cursor[0], screen_cursor[1], screen_cursor[0] + size[0], screen_cursor[1] + size[1], self.style.Selected_Colored_Item.color_int, 1.0, 0)
                PyImGui.draw_list_add_rect(screen_cursor[0], screen_cursor[1], screen_cursor[0] + size[0], screen_cursor[1] + size[1], self.style.Selected_Colored_Item.color_int, 1.0, 0, 2.0)
            
            PyImGui.set_cursor_screen_pos(screen_cursor[0] + 5, screen_cursor[1] + 4)
            mod_range = mod.get_modifier_range()
            args = (mod_info.min, mod_info.max) if mod_info else (mod_range.max, mod_range.max)
            color = (1, 1, 1, (255 / 255 if is_selected else 100 / 255))
            GUI.vertical_centered_text(text=mod.get_custom_description(arg1_min=args[0], arg1_max=args[1], arg2_min=args[0], arg2_max=args[1]), desired_height=int(size[1] - 4), color=color)
            # GUI.vertical_centered_text(mod.get_description(), None, int(size[1] - 4))
            
            if is_hovered and is_selected:
                cog_rect = (screen_cursor[0] + size[0] - 25, screen_cursor[1] + ((size[1] - 16) / 2), 16, 16)
                cog_hovered = GUI.is_mouse_in_rect(cog_rect)
                PyImGui.set_cursor_screen_pos(screen_cursor[0] + size[0] - 25, screen_cursor[1] + ((size[1] - 16) / 2))
                ImGui.DrawTextureExtended(texture_path=texture_map.CoreTextures.Cog.value, size=(16,16), tint=(150,150,150,255) if not cog_hovered else (255,255,255,255))
                
                if cog_hovered and PyImGui.is_item_clicked(0):
                    # ConsoleLog("LootEx", "Cog clicked for mod range selection.")
                    cog_clicked = True
                    self.mod_range_popup = True
                    
                    self.selected_rule_mod = mod
                    self.selected_mod_info = mod_info                                        
        
        PyImGui.end_child()
        
        if not cog_clicked and PyImGui.is_item_clicked(0):
            is_selected = not is_selected
            clicked = True
        
        if is_hovered and not cog_hovered:
            self.weapon_mod_tooltip(mod)
        elif cog_hovered:
            ImGui.show_tooltip("Click to set modifier range for this mod.")
            
        return is_selected, clicked
    
    def draw_mod_range_popup(self, mod: models.WeaponMod | None, mod_info: models.ModInfo | None):
        if not settings.current.profile:
            return
        
        if not mod or not mod_info:
            return
        
        if self.mod_range_popup:
            PyImGui.open_popup("Mod Range")

        if PyImGui.begin_popup("Mod Range"):
            mod_range = mod.get_modifier_range()
            
            PyImGui.text(f"Set range for {mod.get_custom_description(arg1_min=mod_info.min, arg1_max=mod_info.max, arg2_min=mod_info.min, arg2_max=mod_info.max)}")
            PyImGui.separator()
            
            min_value = mod_info.min
            max_value = mod_info.max
            
            min_value = PyImGui.slider_int("Min Value", min_value, mod_range.min, mod_range.max)
            if min_value != mod_info.min and min_value <= max_value:
                mod_info.min = min_value
                settings.current.profile.save()
            
            max_value = PyImGui.slider_int("Max Value", max_value, mod_range.min, mod_range.max)
            if max_value != mod_info.max and max_value >= min_value:
                mod_info.max = max_value
                settings.current.profile.save()            
                
            PyImGui.end_popup()
            
        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.mod_range_popup:
                PyImGui.close_current_popup()
                self.mod_range_popup = False
    
    def draw_by_item_skin(self):
        if self.first_draw:
            self.filter_rules()
            
        if PyImGui.begin_tab_item("By Skin") and settings.current.profile:
                        # Get size of the tab
            tab_size = PyImGui.get_content_region_avail()
            tab_hovered = PyImGui.is_item_hovered()

            # Left panel: Loot Items Selection
            if PyImGui.begin_child("skin_selection_child", (tab_size[0] * 0.3, tab_size[1]), False, PyImGui.WindowFlags.NoFlag):
                child_size = PyImGui.get_content_region_avail()

                changed, search = UI.search_field("##search_rule", self.rule_search, f"Search for rule name, skin name or model id ...", child_size[0] - 30)
                if changed:
                    self.rule_search = search
                    self.filter_rules()            

                # PyImGui.same_line(0, 5)
                # if PyImGui.button(IconsFontAwesome5.ICON_FILTER):
                #     self.rule_filter_popup = not self.rule_filter_popup
                #     if self.rule_filter_popup:
                #         PyImGui.open_popup("Filter Rules")
                #     pass
                
                def draw_hint():
                    PyImGui.text_wrapped(
                        "Select item skins to manage the actions performed on them once in your inventory.")
                                           
                PyImGui.same_line(0, 5)
                PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() + 5)
                self.draw_info_icon(
                    draw_action=draw_hint,                 
                    width=500
                )            
                
                if PyImGui.begin_child("skin selection region", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                    subtab_size = PyImGui.get_content_region_avail()
                    
                    if PyImGui.begin_child("selectable_skins", (subtab_size[0], subtab_size[1] - 30), False, PyImGui.WindowFlags.NoFlag):
                        for selectable_rule in self.selectable_rules:
                            rule : action_rule.ActionRule = selectable_rule.object
                            
                            is_selected, is_hovered = self.draw_selectable_rule(rule, selectable_rule.is_selected, selectable_rule.is_hovered)
                            selectable_rule.is_hovered = is_hovered
                            
                            if is_selected != selectable_rule.is_selected:
                                selectable_rule.is_selected = is_selected
                                
                                if is_selected:
                                    self.selected_rule = selectable_rule.object
                                    self.selectable_items = data.ItemsBySkins.get(self.selected_rule.skin, []) if self.selected_rule else []
                                    
                                    for sel_rule in self.selectable_rules:
                                        if sel_rule.object != self.selected_rule:
                                            sel_rule.is_selected = False
                                else:
                                    self.selected_rule = None
                                
                                self.selected_rule_changed = True

                    PyImGui.end_child()
                    
                    if PyImGui.button("Add Rule", subtab_size[0]):
                        settings.current.profile.add_rule(
                            action_rule.ActionRule()
                        )
                        self.filter_rules()
                        settings.current.profile.save()
                                        
                PyImGui.end_child()
                
            PyImGui.end_child()

            PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

            # Right panel: Loot Item Details
            if PyImGui.begin_child("skin_child", (tab_size[0] - (tab_size[0] * 0.3) - 10, tab_size[1]), self.selected_rule is None, PyImGui.WindowFlags.NoFlag):
                if self.selected_rule:
                    rule : action_rule.ActionRule = self.selected_rule
                    texture = os.path.join(self.item_textures_path, f"{rule.skin}")
                    texture_exists = texture.endswith(((".jpg",".png"))) and os.path.exists(texture)
                    
                    remaingng_size = PyImGui.get_content_region_avail()

                    has_rarities = any(item.item_type in self.rarity_item_types for item in self.selectable_items)
                    is_weapon = any(utility.Util.IsWeaponType(item.item_type) for item in self.selectable_items)
                    rarity_width = 200 if has_rarities else 0
                    
                    if PyImGui.begin_child("skin_selection", ((remaingng_size[0] - ((rarity_width + 5) if has_rarities else 0)), 73), True, PyImGui.WindowFlags.NoFlag):
                        size = 52
                        padding = 8
                        skin_size = size - (padding * 2)
                        
                        cursor = PyImGui.get_cursor_screen_pos()
                        is_texture_hovered = GUI.is_mouse_in_rect((cursor[0], cursor[1], size, size))
                        is_mouse_down = PyImGui.is_mouse_down(0)
                        
                        rect = (cursor[0], cursor[1], cursor[0] + size, cursor[1] + size)   
                        if is_texture_hovered and not is_mouse_down:
                            PyImGui.draw_list_add_rect_filled(rect[0], rect[1], rect[2], rect[3], self.style.Hovered_Item.color_int, 1.0, 0)
                            PyImGui.draw_list_add_rect(rect[0], rect[1], rect[2], rect[3], self.style.Hovered_Item.color_int, 1.0, 0, 2.0)
                            
                        elif is_texture_hovered and is_mouse_down:
                            PyImGui.draw_list_add_rect_filled(rect[0], rect[1], rect[2], rect[3], self.style.Selected_Item.color_int, 1.0, 0)
                            PyImGui.draw_list_add_rect(rect[0], rect[1], rect[2], rect[3], self.style.Selected_Item.color_int, 1.0, 0, 2.0)
                            
                        PyImGui.begin_child(f"selected_rule {rule.skin}", (size, size), False, PyImGui.WindowFlags.NoFlag| PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar)
                        if texture_exists:
                            cursor = PyImGui.get_cursor_pos()
                            PyImGui.set_cursor_pos(cursor[0] + padding, cursor[1] + padding)
                            ImGui.DrawTextureExtended(texture_path=texture, size=(skin_size, skin_size))                    
                        else:            
                            ImGui.push_font("Bold", 28)
                            text_size = PyImGui.calc_text_size(IconsFontAwesome5.ICON_QUESTION)
                            PyImGui.set_cursor_pos((((size - text_size[0])) / 2), 4 + ((size - text_size[1]) / 2))
                            PyImGui.text(IconsFontAwesome5.ICON_QUESTION)
                            ImGui.pop_font()
                            
                        PyImGui.end_child()
                        
                        PyImGui.same_line(0, 20)
                        if PyImGui.is_item_clicked(0):
                            self.skin_select_popup = not self.skin_select_popup
                            self.selected_rule_changed = True
                            
                        ImGui.push_font("Bold", 22)
                        GUI.vertical_centered_text(text=rule.skin.split(".")[0] or "No Skin Selected", desired_height=size + padding)
                        ImGui.pop_font()
                                                
                    PyImGui.end_child()                    
                                    
                    if has_rarities: 
                        PyImGui.same_line(0, 5)
                        
                        if PyImGui.begin_child("rule rarities", (rarity_width, 73), True, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar):   
                            count = 0
                            none_selected = False
                            
                            PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)
                            PyImGui.text("Rarities")
                            
                            # PyImGui.separator()   
                            for rarity, selected in rule.rarities.items():  
                                factor = 52 / 64
                                skin_size = 42
                                frame_size = (skin_size * factor, skin_size)
                                screen_cursor = PyImGui.get_cursor_screen_pos()
                                is_hovered = GUI.is_mouse_in_rect((screen_cursor[0], screen_cursor[1], frame_size[0], frame_size[1])) and PyImGui.is_window_hovered()
                                alpha = 255 if is_hovered else 225 if (selected) else 50
                                texture_alpha = 255 if is_hovered else 225 if (selected) else 100
                                frame_color =  GUI.get_rarity_rgba_color(rarity, texture_alpha) if selected else (100,100,100, texture_alpha)
                                texture_color =  (255 ,255,255 , texture_alpha) if selected else (100,100,100, 200 if is_hovered else 125 )
                                
                                # PyImGui.begin_child(f"rarity_{rarity}", (frame_size[0], frame_size[1]), False, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoScrollWithMouse | PyImGui.WindowFlags.NoScrollbar)
                                
                                if is_hovered:
                                    rect = (screen_cursor[0], screen_cursor[1], screen_cursor[0] + frame_size[0], screen_cursor[1] + frame_size[1])           
                                    PyImGui.draw_list_add_rect_filled(rect[0], rect[1], rect[2], rect[3], Utils.RGBToColor(frame_color[0], frame_color[1], frame_color[2], 50), 1.0, 0)                                                     
                                                                
                                cursor = PyImGui.get_cursor_pos()
                                # PyImGui.set_cursor_pos(cursor[0] + (frame_size * count), cursor[1])
                                ImGui.DrawTextureExtended(texture_path=texture_map.CoreTextures.UI_Inventory_Slot.value, size=(frame_size[0], frame_size[1]), tint=frame_color)
                                PyImGui.set_cursor_pos(cursor[0], cursor[1] + ((frame_size[1] - skin_size) / 2))
                                
                                if texture_exists:                                        
                                    ImGui.DrawTextureExtended(texture_path=texture, size=(skin_size, skin_size), tint=texture_color)
                                else:
                                    PyImGui.dummy(skin_size, skin_size)  
                                # PyImGui.end_child()
                                
                                if PyImGui.is_item_clicked(0):
                                    
                                    if self.py_io.key_ctrl:
                                        for r in rule.rarities.keys():
                                            rule.rarities[r] = not selected
                                    else:
                                        rule.rarities[rarity] = not selected
                                        
                                    settings.current.profile.save()
                                
                                ImGui.show_tooltip(f"Rarity: {rarity.name}")
                                count += 1  
                                PyImGui.same_line(10 + ((frame_size[0] + 2) * count), 0)
                                
                        PyImGui.end_child()                                
                                                               
                    if PyImGui.begin_child("rule action", (0, 45), True, PyImGui.WindowFlags.NoFlag):    
                        action_texture = self.action_textures.get(rule.action, None)
                        height = 24
                        if action_texture:
                            ImGui.DrawTexture(action_texture, height, height)
                        else:
                            PyImGui.dummy(height, height)
                        PyImGui.same_line(0, 5)            
                        PyImGui.push_item_width(PyImGui.get_content_region_avail()[0])
                        action = PyImGui.combo("##RuleAction", self.item_actions.index(
                            rule.action) if rule.action in self.item_actions else 0, self.item_action_names)
                        
                        if self.item_actions[action] != rule.action:
                            rule.action = self.item_actions[action]
                            settings.current.profile.save()
                        
                        ImGui.show_tooltip((f"{self.action_infos.get_name(enum.ItemAction.Loot)} and " if rule.action not in [enum.ItemAction.NONE, enum.ItemAction.Loot, enum.ItemAction.Destroy] else "") + f"{self.action_infos.get_name(rule.action)}")
                    PyImGui.end_child()
                         
                    if PyImGui.begin_child("rule_settings", (0, 0), False, PyImGui.WindowFlags.NoFlag):
                        remaining_size = PyImGui.get_content_region_avail()
                        config_width = min(480, remaining_size[0] / 3 * 2)
                        items_width = remaining_size[0] - config_width if is_weapon else remaining_size[0]
                        
                        if PyImGui.begin_child("rule items", (items_width, 0), True, PyImGui.WindowFlags.NoFlag):
                            if PyImGui.is_rect_visible(1, 20):
                                ##TODO: FIX THIS AS ITS AN INVALID CALCULATION
                                items = len(self.selectable_items)
                                items_height = (items * 45) + 112
                                columns = int(max(1, math.floor(items_width / 210) if items_height > remaingng_size[1] else 1))
                                
                                if PyImGui.begin_table("rule_items_table", columns, PyImGui.TableFlags.NoBordersInBody | PyImGui.TableFlags.ScrollY): 
                                    PyImGui.table_next_column()
                                                                                            
                                    for item in self.selectable_items:
                                        if item:
                                            existing_model_info = next((
                                                model_info for model_info in rule.models
                                                if model_info.model_id == item.model_id and model_info.item_type == item.item_type
                                            ), None)
                                            
                                            is_selected = existing_model_info is not None
                                            none_selected = rule.models is None or len(rule.models) == 0
                                            
                                            selected, clicked = self.draw_item_selectable(item, none_selected or is_selected)
                                            if clicked:
                                                if self.py_io.key_ctrl:
                                                    if existing_model_info:
                                                        rule.models.clear()
                                                        
                                                    else:
                                                        rule.models.clear()
                                                        rule.models.append(
                                                            action_rule.ItemModelInfo(item_type=item.item_type, model_id=item.model_id)
                                                        )
                                                else:
                                                    if existing_model_info:
                                                        rule.models.remove(existing_model_info)
                                                        
                                                    else:
                                                        rule.models.append(
                                                            action_rule.ItemModelInfo(item_type=item.item_type, model_id=item.model_id)
                                                        )
                                                settings.current.profile.save()
                                                
                                            PyImGui.table_next_column()
                                    
                                    PyImGui.end_table()
                            
                        PyImGui.end_child()
                        
                        if is_weapon:
                            PyImGui.same_line(0, 5)
                            
                            if PyImGui.begin_child("rule configs", (config_width, 0), False, PyImGui.WindowFlags.NoFlag):    
                                remaingng_size = PyImGui.get_content_region_avail()
                                requirements_size = (remaingng_size[0], 90)
                                if PyImGui.begin_child("rule requirements", (0, requirements_size[1]), True, PyImGui.WindowFlags.NoFlag):
                                    PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)
                                    ImGui.push_font("Bold", 15)
                                    range_text = f"{rule.requirements.min}...{rule.requirements.max}" if rule.requirements.min != rule.requirements.max else f"{rule.requirements.min}"
                                    PyImGui.text(f"Requires {range_text} of Items Attribute")
                                    ImGui.pop_font()
                                    
                                    slider_width = 100
                                    
                                    GUI.vertical_centered_text("Attribute Range:", 115, 24)
                                    
                                    PyImGui.push_item_width(slider_width)
                                    min_value = PyImGui.input_int("##MinReq", rule.requirements.min)
                                    min_value = max(min_value, 0)
                                    if min_value != rule.requirements.min:
                                        if min_value > rule.requirements.max:
                                            min_value = rule.requirements.max
                                            
                                        rule.requirements.min = min_value
                                        settings.current.profile.save()                                        
                                        
                                    PyImGui.same_line(0, 5)
                                    
                                    PyImGui.push_item_width(slider_width)
                                    max_value = PyImGui.input_int("##MaxReq", rule.requirements.max) 
                                    max_value = min(max_value, 13)
                                    if max_value != rule.requirements.max or min_value != rule.requirements.min:
                                        if max_value < min_value:
                                            max_value = min_value
                                            
                                        rule.requirements.min = min_value
                                        rule.requirements.max = max_value
                                        settings.current.profile.save()
                                    
                                    is_shield = any(item.item_type == ItemType.Shield for item in self.selectable_items)
                                    is_focus = any(item.item_type == ItemType.Offhand for item in self.selectable_items)
                                    is_weapon = any(utility.Util.IsWeaponType(item.item_type) and item.item_type not in [ItemType.Shield, ItemType.Offhand] for item in self.selectable_items)
                                    stat_types = [f"{"Damage" if is_weapon else ""}", f"{"Energy" if is_focus else ""}", f"{"Armor" if is_shield else ""}", ] 
                                    stat_types = [stat for stat in stat_types if stat]  # Remove empty strings
                                    only_max = PyImGui.checkbox(f"Only max {"/".join(stat_types)} for selected Attribute Range", rule.requirements.max_damage_only)            
                                    if only_max != rule.requirements.max_damage_only:
                                        rule.requirements.max_damage_only = only_max
                                        settings.current.profile.save()                   
                                    
                                PyImGui.end_child()
                                
                                if PyImGui.begin_child("rule mods", (0, (remaingng_size[1] - 6) - requirements_size[1]), True, PyImGui.WindowFlags.NoFlag):
                                    ImGui.push_font("Bold", 15)
                                    PyImGui.text("Mods")
                                    ImGui.pop_font()
                                    
                                    combo_width = 150
                                    mods_size = PyImGui.get_content_region_avail()
                                    PyImGui.same_line(mods_size[0] - combo_width + 10, 0)
                                    PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)                                    
                                    PyImGui.push_item_width(combo_width)
                                    mod_type_selection = [utility.Util.reformat_string(mod.name) for mod in  enum.ActionModsType]
                                    index = mod_type_selection.index(utility.Util.reformat_string(rule.mods_type.name))
                                    mod_index = PyImGui.combo("##ModType", index, mod_type_selection)
                                    
                                    if index != mod_index:
                                        rule.mods_type = enum.ActionModsType(mod_index)
                                        settings.current.profile.save()
                                        
                                    PyImGui.spacing()
                                    if mod_index != 1:
                                        ImGui.push_font("Bold", 15)
                                        PyImGui.text("Any inscribable version of the selected items.")
                                        ImGui.pop_font()
                                    
                                    if mod_index == 0:
                                        PyImGui.separator()
                                    
                                    if mod_index != 2:
                                        ImGui.push_font("Bold", 15)
                                        target_text = "any max inherent mod" if not rule.mods else f"one of {len(rule.mods)} inherent mods"
                                        PyImGui.text(f"Any old school version with {target_text}")    
                                        ImGui.pop_font()
                                                                          
                                        selectable_mods : list[models.WeaponMod] = []
                                        
                                        if PyImGui.begin_child("selectable_mods", (0, 0), False, PyImGui.WindowFlags.NoFlag):
                                            for mod in data.Weapon_Mods.values():
                                                if mod.mod_type == enum.ModType.Inherent:
                                                    for item in self.selectable_items:
                                                        if not mod.has_item_type(item.item_type):
                                                            continue
                                                        
                                                        if not mod in selectable_mods:
                                                            selectable_mods.append(mod)                                                
                                            
                                            #sort by is_selected (selectable_mod.identifier in rule.mods)
                                            # selectable_mods.sort(key=lambda x: x.identifier in rule.mods, reverse=True)
                                            
                                            #sort by name, but if mod.modifiers has 9240 put it to the end
                                            selectable_mods.sort(key=lambda x: (any(m.identifier == 9240 for m in x.modifiers), x.get_custom_description()), reverse=False)
                                            
                                            for selectable_mod in selectable_mods:
                                                is_selected = selectable_mod.identifier in rule.mods
                                                mod_info = rule.mods.get(selectable_mod.identifier, None)
                                                
                                                selected, clicked = self.draw_mod_selectable(selectable_mod, is_selected, mod_info)
                                                
                                                if selected != is_selected:             
                                                    if selected:
                                                        if self.py_io.key_ctrl:
                                                            for m in selectable_mods:
                                                                rule.add_mod(m)
                                                        else:
                                                            rule.add_mod(selectable_mod)                                       
                                                    else:
                                                        if self.py_io.key_ctrl:
                                                            rule.mods.clear()
                                                        else:
                                                            rule.remove_mod(selectable_mod)
                                                    
                                                    settings.current.profile.save()
                                                
                                        PyImGui.end_child()
                                        
                                    ##Idea: draw info with range e.g. "Damage +13 ... 15% (while Health above 50%)"
                                PyImGui.end_child()
                                
                            PyImGui.end_child()
                    
                    PyImGui.end_child()
                    
                    
                pass
            
            PyImGui.end_child()
            
            # self.draw_rule_filter_popup()
            self.draw_skin_select_popup()
            self.draw_mod_range_popup(self.selected_rule_mod, self.selected_mod_info)
            
            PyImGui.end_tab_item()
    
    #endregion
    
    #region Low Req
    ##TODO: Select requirements and damage, select OS mods ranges, rarities
    
    def draw_low_req_selectable(self, item: SelectableWrapper) -> bool:
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
            f"LowReqSelectableItem{item.object}",
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
        
        GUI.vertical_centered_text(
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
    
    def draw_requirements_selectable(self, item_type : ItemType, requirement : int, damage_range : models.IntRange | None, damage_range_info : models.IntRange, selected : bool) -> bool:
        item_type_requirment_texts = {
            ItemType.Axe: "{0} Axe Mastery",
            ItemType.Bow: "{0} Marksmanship",
            ItemType.Daggers : "{0} Dagger Mastery",
            ItemType.Hammer: "{0} Hammer Mastery",
            ItemType.Scythe: "{0} Scythe Mastery",
            ItemType.Spear: "{0} Spear Mastery",
            ItemType.Sword: "{0} Sword Mastery",
            ItemType.Staff: "{0} Caster Attributes",
            ItemType.Wand: "{0} Caster Attributes",
            ItemType.Shield: "{0} Shield Attributes",
            ItemType.Offhand: "{0} Caster Attributes",
        }         
        
        damage_range_text = ""
        value_range = damage_range if damage_range else damage_range_info
        
        match (item_type):
            
            case ItemType.Axe | ItemType.Bow | ItemType.Daggers | ItemType.Hammer | ItemType.Scythe | ItemType.Spear | ItemType.Sword | ItemType.Staff | ItemType.Wand:
                min_damage_format = ("({0}...{1})" if damage_range and damage_range.min != damage_range_info.min else "{0}")
                max_damage_format = ("({0}...{1})" if  damage_range and damage_range.max != damage_range_info.max else "{0}")
                value_text = min_damage_format.format(value_range.min, damage_range_info.min) + "-" + max_damage_format.format(value_range.max, damage_range_info.max) if value_range.min != value_range.max else min_damage_format.format(value_range.min, damage_range_info.min)
                damage_range_text = "Damage: " + value_text
                
            case ItemType.Shield:
                min_damage_format = "{0}" 
                max_damage_format = "{0}"
                value_text = min_damage_format.format(value_range.min) + "..." + max_damage_format.format(value_range.max) if value_range.min != value_range.max else min_damage_format.format(value_range.min)
                damage_range_text = "Armor: " + value_text
            
            case ItemType.Offhand:
                min_damage_format = "{0}"
                max_damage_format = "{0}"
                value_text = min_damage_format.format(value_range.min) + "..." + max_damage_format.format(value_range.max) if value_range.min != value_range.max else min_damage_format.format(value_range.min)
                damage_range_text = "Energy: " + value_text
                
                
        cog_hovered = False
        cog_clicked = False
        is_hovered = False
        
        height = 40
        if PyImGui.is_rect_visible(1, height):
            if PyImGui.begin_child(f"LowReqSelectable{item_type}_{requirement}_{damage_range}",(0, height), False, PyImGui.WindowFlags.NoFlag):
                size = PyImGui.get_content_region_avail()
                text_size = size[1] / 2 + 2
                screen_cursor = PyImGui.get_cursor_screen_pos()
                is_hovered = GUI.is_mouse_in_rect((screen_cursor[0], screen_cursor[1], size[0], size[1])) and PyImGui.is_window_hovered()
                
                if selected:
                    PyImGui.draw_list_add_rect_filled(screen_cursor[0], screen_cursor[1], screen_cursor[0] + size[0], screen_cursor[1] + size[1], self.style.Selected_Colored_Item.color_int, self.style.FrameRounding.value1, 0)
                
                if is_hovered:
                    PyImGui.draw_list_add_rect_filled(screen_cursor[0], screen_cursor[1], screen_cursor[0] + size[0], screen_cursor[1] + size[1], self.style.Hovered_Colored_Item.color_int, self.style.FrameRounding.value1, 0) 
                
                item_type_text = item_type_requirment_texts.get(item_type, "Unknown")
                PyImGui.set_cursor_pos_x(PyImGui.get_cursor_pos_x() + 5)
                
                ImGui.push_font("Regular", 15)
                GUI.vertical_centered_text(f"Requires {item_type_text.format(requirement)}", None, text_size + 6)
                ImGui.pop_font()
                
                PyImGui.set_cursor_pos_x(PyImGui.get_cursor_pos_x() + 5)
                PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 8)
                GUI.vertical_centered_text(damage_range_text, None, text_size)
                
                if is_hovered and selected:
                    cog_rect = (screen_cursor[0] + size[0] - 25, screen_cursor[1] + ((size[1] - 16) / 2), 16, 16)
                    cog_hovered = GUI.is_mouse_in_rect(cog_rect)
                    PyImGui.set_cursor_screen_pos(screen_cursor[0] + size[0] - 25, screen_cursor[1] + ((size[1] - 16) / 2))
                    ImGui.DrawTextureExtended(texture_path=texture_map.CoreTextures.Cog.value, size=(16,16), tint=(150,150,150,255) if not cog_hovered else (255,255,255,255))
                    
                    if cog_hovered and PyImGui.is_item_clicked(0):
                        ConsoleLog("LootEx", "Cog clicked for mod range selection.")
                        cog_clicked = True
                        self.dmg_range_popup = True
                        
                        self.selected_rule_damage_range = damage_range
                        self.selected_damage_range = damage_range_info   
                        
                        requirements = data.DamageRanges.get(item_type, None)
                        self.selected_damage_range_min = requirements.get(0) if requirements else models.IntRange(0, 0)
            
            
            PyImGui.end_child()
            
            if PyImGui.is_item_clicked(0) and is_hovered and not cog_clicked:
                selected = not selected
        else:
            PyImGui.dummy(0, height)
            
        return selected
    
    
    def draw_damage_range_popup(self, selected_rule_damage_range : models.IntRange | None, damage_range : models.IntRange | None, min_range : models.IntRange | None):
        if not settings.current.profile:
            return
        
        if not selected_rule_damage_range or not damage_range or not min_range:
            return
        
        if self.dmg_range_popup:
            PyImGui.open_popup("Damage Range")

        if PyImGui.begin_popup("Damage Range"):            
            PyImGui.text(f"Set damage range")
            PyImGui.separator()
            
            min_value = selected_rule_damage_range.min
            max_value = selected_rule_damage_range.max
            
            min_value = PyImGui.slider_int("Min Value", min_value, min_range.min, damage_range.min)
            if min_value != selected_rule_damage_range.min and min_value <= max_value:
                selected_rule_damage_range.min = min_value
                settings.current.profile.save()
            
            max_value = PyImGui.slider_int("Max Value", max_value, damage_range.min, damage_range.max)
            if max_value != selected_rule_damage_range.max and max_value >= min_value:
                selected_rule_damage_range.max = max_value
                settings.current.profile.save()            
                
            PyImGui.end_popup()
            
        if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
            if self.dmg_range_popup:
                PyImGui.close_current_popup()
                self.dmg_range_popup = False
        
    def draw_low_req(self):
        if self.first_draw:
            # self.filter_items()
            pass
        
        if PyImGui.begin_tab_item("By Weapon Type") and settings.current.profile:            
            selected_item_type : ItemType | None = None
            texture_height = 30
            
            tab_size = PyImGui.get_content_region_avail()

            # Left panel: Loot Items Selection
            if PyImGui.begin_child("Low Req Child Left", (tab_size[0] * 0.15, 0), True, PyImGui.WindowFlags.NoFlag):
                    
                for selectable in self.os_low_req_itemtype_selectables:
                    if self.draw_low_req_selectable(selectable):
                        for other_selectable in self.os_low_req_itemtype_selectables:
                            if other_selectable != selectable:
                                other_selectable.is_selected = False
                    
                    if selectable.is_selected:
                        selected_item_type = selectable.object
                                
                    PyImGui.spacing()
                    
            PyImGui.end_child()
            
            PyImGui.same_line(0, 5)
            
            rule = settings.current.profile.low_req_rules.get(selected_item_type, None) if selected_item_type else None
            if PyImGui.begin_child("Low Req Child Right", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                if selected_item_type and rule:                                
                    texture = self.item_type_textures.get(selected_item_type, None)
                    if texture:
                        ImGui.DrawTexture(texture, texture_height, texture_height)
                    else:
                        PyImGui.dummy(texture_height, texture_height)
                        
                    PyImGui.same_line(0, 5)
                    
                    GUI.vertical_centered_text(
                        utility.Util.reformat_string(selected_item_type.name), None, texture_height
                    )
                    PyImGui.separator()
                                    
                    width_remaining = PyImGui.get_content_region_avail()[0] - 10
                    
                    if PyImGui.begin_child("Low Req Req & Damage", (width_remaining / 2, 0), True, PyImGui.WindowFlags.NoFlag):
                        requirements = data.DamageRanges.get(selected_item_type, None)
                        
                        if requirements:
                            for req, damage_range in requirements.items():
                                rule_damage_range = rule.requirements.get(req, None)
                            
                                is_selected = rule_damage_range is not None                                
                                selected = self.draw_requirements_selectable(selected_item_type, req, rule_damage_range, damage_range, is_selected)   
                                
                                if selected != is_selected:
                                    if selected:
                                        if self.py_io.key_ctrl:
                                            for r in requirements.keys():
                                                rule.requirements[r] = rule_damage_range or models.IntRange(damage_range.min, damage_range.max)
                                        else:
                                            rule.requirements[req] = rule_damage_range or models.IntRange(damage_range.min, damage_range.max)
                                        
                                    else:
                                        if self.py_io.key_ctrl:
                                            rule.requirements.clear()
                                        else:
                                            if req in rule.requirements:
                                                del rule.requirements[req]
                                            
                                    settings.current.profile.save()
                                                        
                        pass
                    
                    PyImGui.end_child()
                    
                    PyImGui.same_line(0, 5)  
                    
                    if PyImGui.begin_child("Low Req Child Mods", (width_remaining / 2, 0), True, PyImGui.WindowFlags.NoFlag):
                        ImGui.push_font("Bold", 15)
                        PyImGui.text("Mods")
                        ImGui.pop_font()
                        
                        combo_width = 150
                        mods_size = PyImGui.get_content_region_avail()
                        PyImGui.same_line(mods_size[0] - combo_width + 10, 0)
                        PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)                                    
                        PyImGui.push_item_width(combo_width)
                        mod_type_selection = [utility.Util.reformat_string(mod.name) for mod in  enum.ActionModsType]
                        index = mod_type_selection.index(utility.Util.reformat_string(rule.mods_type.name))
                        mod_index = PyImGui.combo("##ModType", index, mod_type_selection)
                        
                        if index != mod_index:
                            rule.mods_type = enum.ActionModsType(mod_index)
                            settings.current.profile.save()
                            
                        PyImGui.spacing()
                        if mod_index != 1:
                            ImGui.push_font("Bold", 15)
                            PyImGui.text("Any inscribable version of the selected items.")
                            ImGui.pop_font()
                        
                        if mod_index == 0:
                            PyImGui.separator()
                        
                        if mod_index != 2:
                            ImGui.push_font("Bold", 15)
                            target_text = "any max inherent mod" if not rule.mods else f"one of {len(rule.mods)} inherent mods"
                            PyImGui.text(f"Any old school version with {target_text}")    
                            ImGui.pop_font()
                                                                
                            selectable_mods : list[models.WeaponMod] = []
                            
                            if PyImGui.begin_child("selectable_mods", (0, 0), False, PyImGui.WindowFlags.NoFlag):
                                for mod in data.Weapon_Mods.values():
                                    if mod.mod_type == enum.ModType.Inherent:
                                        if not mod.has_item_type(selected_item_type):
                                            continue
                                        
                                        if not mod in selectable_mods:
                                            selectable_mods.append(mod)                                                
                                
                                #sort by is_selected (selectable_mod.identifier in rule.mods)
                                # selectable_mods.sort(key=lambda x: x.identifier in rule.mods, reverse=True)
                                
                                #sort by name, but if mod.modifiers has 9240 put it to the end
                                selectable_mods.sort(key=lambda x: (any(m.identifier == 9240 for m in x.modifiers), x.get_custom_description()), reverse=False)
                                
                                for selectable_mod in selectable_mods:
                                    is_selected = selectable_mod.identifier in rule.mods
                                    mod_info = rule.mods.get(selectable_mod.identifier, None)
                                    
                                    selected, clicked = self.draw_mod_selectable(selectable_mod, is_selected, mod_info)
                                    
                                    if selected != is_selected:             
                                        if selected:
                                            if self.py_io.key_ctrl:
                                                for m in selectable_mods:
                                                    rule.add_mod(m)
                                            else:
                                                rule.add_mod(selectable_mod)                                       
                                        else:
                                            if self.py_io.key_ctrl:
                                                rule.mods.clear()
                                            else:
                                                rule.remove_mod(selectable_mod)
                                        
                                        settings.current.profile.save()
                                    
                            PyImGui.end_child()
                            
                    
                    PyImGui.end_child()                  
                    
            PyImGui.end_child()
            
            self.draw_mod_range_popup(self.selected_rule_mod, self.selected_mod_info)
            self.draw_damage_range_popup(self.selected_rule_damage_range, self.selected_damage_range, self.selected_damage_range_min)
            PyImGui.end_tab_item()
    
    #endregion
    
    def draw_by_model_id(self):
        if PyImGui.begin_tab_item("By Model ID") and settings.current.profile:
            # Get size of the tab
            tab_size = PyImGui.get_content_region_avail()

            # Left panel: Loot Items Selection
            if PyImGui.begin_child("loot_items_selection_child", (tab_size[0] * 0.3, tab_size[1]), False, PyImGui.WindowFlags.NoFlag):
                child_size = PyImGui.get_content_region_avail()

                changed, search = UI.search_field("##search_loot_items", self.item_search, f"Search for Item Name or Model ID...", child_size[0] - 60)
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
                
                if PyImGui.begin_child("selectable items", (0, 0), True, PyImGui.WindowFlags.NoFlag):
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
                                            
                                            if condition.action == enum.ItemAction.Stash:
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

                                                GUI.vertical_centered_text(
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

                                                GUI.vertical_centered_text(
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

                                                GUI.vertical_centered_text(
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

                                                    GUI.vertical_centered_text(
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
        screen_cursor = PyImGui.get_cursor_screen_pos()
        rect = (screen_cursor[0], screen_cursor[1], 24, 24)
        hovered = GUI.is_mouse_in_rect(rect)
        
        texture = texture_map.CoreTextures.UI_Help_Icon_Hovered if hovered else texture_map.CoreTextures.UI_Help_Icon
        ImGui.DrawTexture(texture.value, rect[2], rect[3])
        # PyImGui.text_colored(IconsFontAwesome5.ICON_QUESTION_CIRCLE, self.style.Info_Icon.color_tuple)
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
                        
            changed, search = UI.search_field("##search_loot_items", self.item_search, f"Search for Item Name or Model ID...", tab_size[0] - 60)
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
                    if GUI.is_mouse_in_rect((posX, posY, image_size, image_size)):                                
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

    def _calc_mod_description_height(self, mod : models.WeaponMod, tab_width: float) -> float:
        base_height = 48
        
        weapon_types_height = 36
        text_size_x, text_size_y = PyImGui.calc_text_size(mod.description)

        lines_of_text = math.ceil(text_size_x / (tab_width - 60))
        required_text_height = (lines_of_text * text_size_y)

        height = base_height + required_text_height + (0 if mod.is_inscription else weapon_types_height)
                
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
                f"Search for Mod Name, Description or internal Id...",
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
            
            PyImGui.begin_child(
                "ModSelectionsChild", (selection_width, 0), True, PyImGui.WindowFlags.NoFlag)

            selected_weapon_mod = None
            
            remaining_size = PyImGui.get_content_region_avail()
            columns = max(1, math.floor(int(remaining_size[0] / 350)))
            column_width = int(remaining_size[0] / columns)
            
            for chunk in chunked(self.filtered_weapon_mods, columns):
                max_height_in_row = max(self._calc_mod_description_height(
                    selectable.object, column_width) for selectable in chunk)
                
                for selectable in chunk:
                    m: models.WeaponMod = selectable.object
                    self.mod_heights[m.identifier] = max_height_in_row
            
            
            if PyImGui.is_rect_visible(1, 20):
                PyImGui.begin_table(
                    "Weapon Mods Table",
                    columns,
                    PyImGui.TableFlags.NoBordersInBody |PyImGui.TableFlags.ScrollY,
                )          
                
                PyImGui.table_next_column()                  

                for selectable in self.filtered_weapon_mods:
                    m: models.WeaponMod = selectable.object
                    selected_weapon_mod = m if selectable.is_selected else selected_weapon_mod

                    is_in_profile = settings.current.profile.contains_weapon_mod(
                        m.identifier) if settings.current.profile else None

                    def get_frame_color():
                        base_color = self.style.Border if not is_in_profile else self.style.Selected_Colored_Item
                        return Utils.RGBToColor(base_color.r, base_color.g, base_color.b, (150 if is_in_profile else base_color.a))

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
                                  
                    if m.is_inscription:
                        texture = self.inscription_type_textures.get(m.target_types[0], None)
                        if texture:
                            ImGui.DrawTextureExtended(texture_path=os.path.join(self.item_textures_path, texture), size=(16, 16), tint=(255,255,255,255) if is_in_profile else (150,150,150, 255) if selectable.is_hovered else (100, 100, 100, 255))
                            PyImGui.same_line(0, 5)
                        pass
                        
                    ImGui.push_font("Regular", 16)
                    PyImGui.text(m.applied_name)
                    ImGui.pop_font()

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
                        texture_size = 32
                        offset_y = (PyImGui.get_content_region_avail()[1] - texture_size) / 2
                        cursor_y = PyImGui.get_cursor_pos_y()
                        
                        PyImGui.set_cursor_pos_y(self.mod_heights[m.identifier] - 8 - texture_size)
                        
                        if m.is_inscription:
                            pass
                        else:
                            for weapon_type in ItemType:
                                if not m.has_item_type(weapon_type) or weapon_type in self.inscription_type_textures:
                                    continue

                                is_selected = m.identifier in settings.current.profile.weapon_mods and weapon_type.name in settings.current.profile.weapon_mods[
                                    m.identifier] and settings.current.profile.weapon_mods[m.identifier][weapon_type.name] or False

                                # textures = self.mod_textures.get(weapon_type, None)
                                # texture = textures.get(m.mod_type, None) if textures else None
                                texture = self.item_type_textures.get(weapon_type, None)         
                                                                
                                cursor = PyImGui.get_cursor_screen_pos() 
                                rect = (cursor[0], cursor[1], texture_size, texture_size)
                                hovered = GUI.is_mouse_in_rect(rect)
                                
                                if texture:
                                    # ImGui.DrawTexture(texture, 24, 24)
                                    # tint = (255,255,255,255) if is_selected else (150,150,150, 255) if hovered else (64, 64,64, 255)
                                    # ImGui.DrawTextureExtended(texture_path=texture, size=(texture_size, texture_size))
                                    # background = (255, 204, 85, 180) if is_selected else (51, 77, 102, 255) if hovered else (26, 38, 51, 255)
                                    background = self.style.Selected_Colored_Item if is_selected else self.style.ButtonHovered if hovered else self.style.Button
                                    selected = UI.ImageToggle(id=f"{m.identifier}{weapon_type.name}", selected=is_selected, texture_path=texture, size=(texture_size, texture_size), tint=(255,255,255,255), background=background.rgb_tuple)
                                    # PyImGui.text(weapon_type.name)
                                
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
                                else:
                                    PyImGui.dummy(texture_size, texture_size)                            
                                    
                                is_tooltip_visible = is_tooltip_visible or PyImGui.is_item_hovered()

                                ImGui.show_tooltip(
                                    f"Toggle {utility.Util.reformat_string(weapon_type.name)} for this mod.\n" +
                                    "If selected, the mod will be picked up and stored when found." +
                                    "\nHold CTRL to toggle all weapon types at once."
                                )

                                PyImGui.same_line(0, 5)
                                
                    PyImGui.new_line()
                    PyImGui.dummy(10, 12)  
                    PyImGui.end_child()
                
                    if m.is_inscription:
                        if PyImGui.is_item_clicked(0):
                            selectable.is_selected = not selectable.is_selected
                            
                            if selectable.is_selected:
                                if not settings.current.profile.weapon_mods.get(m.identifier, None):
                                    settings.current.profile.weapon_mods[m.identifier] = {}
                                    
                                for weapon_type in ItemType:                                        
                                    settings.current.profile.weapon_mods[
                                        m.identifier][weapon_type.name] = selectable.is_selected
                            else:
                                settings.current.profile.weapon_mods.pop(m.identifier, None)
                            
                            settings.current.profile.save()
                            
                    selectable.is_hovered = PyImGui.is_item_hovered()

                    if is_in_profile:
                        PyImGui.pop_style_color(2)

                    if not is_tooltip_visible:
                        UI.weapon_mod_tooltip(m)
                    
                    PyImGui.table_next_column()
                
                PyImGui.end_table()
                
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
                y_pos = PyImGui.get_cursor_pos_y()
                ImGui.push_font("Regular", 18)
                PyImGui.set_cursor_pos_y(y_pos + 5)
                PyImGui.text("Rune Selection")
                ImGui.pop_font()

                remaining_space = PyImGui.get_content_region_avail()
                PyImGui.same_line(remaining_space[0] - 270, 5)
                PyImGui.set_cursor_pos_y(y_pos - 5)
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
                PyImGui.set_cursor_pos_y(y_pos - 5)
                self.draw_info_icon(
                    draw_action=draw_help,
                    width=500
                )

                PyImGui.set_cursor_pos_y(PyImGui.get_cursor_pos_y() - 5)
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

        texture = os.path.join(self.item_textures_path, material.inventory_icon) if material.inventory_icon else None
       
        texture_size = 32
        cursor = PyImGui.get_cursor_screen_pos()
        rect = (cursor[0], cursor[1], texture_size, texture_size)        
        hovered = GUI.is_mouse_in_rect(rect)        
        background = self.style.Selected_Colored_Item.rgb_tuple if is_selected else self.style.ButtonHovered.rgb_tuple if hovered else self.style.Button.rgb_tuple
        is_now_selected = is_selected
        
        if texture:
            is_now_selected = UI.ImageToggle(id=f"{texture}{material.model_id}", selected=is_selected, texture_path=texture, size=(texture_size, texture_size), tint=(255, 255, 255, 255) if is_selected else (200, 200, 200, 255) if hovered else (125, 125, 125, 255), background=background)
        else:
            PyImGui.dummy(texture_size, texture_size)
            
        ImGui.show_tooltip(f"{material.name}")
            
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
        
        texture = self.item_type_textures.get(item_type, None)
        texture_size = 32
        cursor = PyImGui.get_cursor_screen_pos()
        rect = (cursor[0], cursor[1], texture_size, texture_size)        
        hovered = GUI.is_mouse_in_rect(rect)        
        background = self.style.Selected_Colored_Item.rgb_tuple if is_selected else self.style.ButtonHovered.rgb_tuple if hovered else self.style.Button.rgb_tuple
        is_now_selected = is_selected
        
        is_now_selected = UI.ImageToggle(id=f"{texture}{item_type.name}", selected=is_selected, texture_path=texture or "", size=(texture_size, texture_size), tint=(255, 255, 255, 255) if is_selected else (200, 200, 200, 255) if hovered else (125, 125, 125, 255), background=background)
                
        ImGui.show_tooltip(f"Item Type: {utility.Util.reformat_string(item_type.name)}")
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
        GUI.vertical_centered_text(item_name, None, 20)
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
        GUI.vertical_centered_text(item_name, None, 20)
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

    # region general ui elements
    @staticmethod
    def ImageToggle(id : str, selected : bool, texture_path: str, size : tuple[float, float], label : str = "",  padding : tuple[float, float] = (2, 2), tint: tuple[int, int, int, int] = (255, 255, 255, 255), background : tuple[int, int, int, int] = (255, 255, 255, 0)) -> bool:
        cursor = PyImGui.get_cursor_screen_pos()
        
        label_size = PyImGui.calc_text_size(label) if label else (0, 0)
        texture_size = (size[0] - padding[0] * 2, size[1] - padding[1] * 2)
        
        width = size[0] + 5 + label_size[0] if label else size[0]
        height = size[1]
        
        rect = (cursor[0], cursor[1], size[0] + 5 + label_size[0], size[1])
        hovered = GUI.is_mouse_in_rect(rect)
                
        tint = (255,255,255,255) if selected else (150,150,150,255) if hovered else (64,64,64,255)
        background_color = Utils.RGBToColor(background[0], background[1], background[2], background[3])
        
        # PyImGui.push_style_color(PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(
        #     Utils.RGBToColor(background[0], background[1], background[2], background[3])))
        
        # cursor = PyImGui.get_cursor_pos()
        window_style = style.Style()
        PyImGui.draw_list_add_rect_filled(cursor[0], cursor[1], cursor[0] + size[0],  cursor[1] + size[1], background_color, window_style.FrameRounding.value1, 0)
        
        PyImGui.begin_child(f"ImageToggle{id}{texture_path}", (width, height), False, PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse)
        
        # cursor = PyImGui.get_cursor_pos()
        PyImGui.set_cursor_pos(padding[0], padding[1])
        
        if texture_path:
            ImGui.DrawTextureExtended(texture_path=texture_path, size=texture_size, tint=tint)
        else:
            ImGui.push_font("Bold", 28)
            text_size = PyImGui.calc_text_size(IconsFontAwesome5.ICON_QUESTION)
            PyImGui.set_cursor_pos((size[0] - text_size[0]) / 2, (size[1] - (28 - 6)) / 2)
            PyImGui.text(IconsFontAwesome5.ICON_QUESTION)
            ImGui.pop_font()
            pass
                
        if label:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255 if selected else 200 if hovered else 125)))
            PyImGui.set_cursor_pos(size[0] + 5, (size[1] - label_size[1]) / 2 + 3)
            PyImGui.text(label)
            PyImGui.pop_style_color(1)
        
        PyImGui.end_child()
        
        # PyImGui.pop_style_color(1)
                        
        if PyImGui.is_item_clicked(0):
            selected = not selected
            
        return selected
                        
    @staticmethod
    def ImageToggleXX(path : str, width : float, height : float, is_selected : bool) -> bool:
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
                if GUI.is_mouse_in_rect(rect)
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
                if GUI.is_mouse_in_rect(rect)
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
            ImGui.push_font("Regular", 10)
            GUI.vertical_centered_text(IconsFontAwesome5.ICON_SEARCH, 25, 24)
            ImGui.pop_font()
            texture_size = PyImGui.calc_text_size(placeholder)
            PyImGui.set_cursor_pos(20, PyImGui.get_cursor_pos_y() + 2 + (24 - texture_size[1]) / 2)
            PyImGui.text(placeholder)
            PyImGui.pop_style_color(1)
            PyImGui.end_child()
            
        PyImGui.end_child()

        return (search != text, search)
    
    # endregion
