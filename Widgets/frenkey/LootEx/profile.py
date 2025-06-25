import os
import json
from Widgets.frenkey.LootEx import filter, item_configuration, settings
from Widgets.frenkey.LootEx.filter import Filter
from Widgets.frenkey.LootEx.item_configuration import *
from Py4GWCoreLib import Console
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import DyeColor


import importlib
importlib.reload(item_configuration)

class RuneConfiguration:
    def __init__(self, identifier: str = "", valuable: bool = False, should_sell: bool = False):
        self.identifier = identifier
        self.valuable = valuable
        self.should_sell = should_sell
        pass
    
    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "valuable": self.valuable,
            "should_sell": self.should_sell
        }
        
    @staticmethod
    def from_dict(data: dict) -> 'RuneConfiguration':
        rune_config = RuneConfiguration()
        rune_config.valuable = data.get("valuable", False)
        rune_config.should_sell = data.get("should_sell", False)
        rune_config.identifier = data.get("identifier", "")
        
        return rune_config

class ItemConfigurations(dict[ItemType, dict[int, ItemConfiguration]]):
    """A dictionary to hold item configurations by item type and model ID."""
    
    def __init__(self):
        super().__init__()

    def add_item(self, item: models.Item, action: ItemAction = ItemAction.STASH):
        """Add an item configuration to the dictionary."""
        if item.item_type not in self:
            self[item.item_type] = {}
        
        if item.model_id not in self[item.item_type]:
            self[item.item_type][item.model_id] = ItemConfiguration(item.model_id, item.item_type, action)
        else:
            if len(self[item.item_type][item.model_id].conditions) == 1:
                self[item.item_type][item.model_id].conditions[0].action = action
    
    def get_item_config(self, item_type : ItemType, model_id: int) -> ItemConfiguration | None:
        """Get the item configuration for a specific item."""
        if item_type in self and model_id in self[item_type]:
            return self[item_type][model_id]
        
        return None
    
    def delete_item_config(self, item_type : ItemType, model_id: int):
        """Delete an item configuration from the dictionary."""
        
        if item_type in self:            
            if model_id in self[item_type]:
                del self[item_type][model_id]
                
                if not self[item_type]:
                    del self[item_type]

class OldSchoolItemsConfigurations(dict[int, ItemConfiguration]):
    pass

class Profile:
    def __init__(self, profile_name: str):
        self.name = profile_name

        self.dyes = {dye: False for dye in DyeColor if dye != DyeColor.NoColor}
        self.identification_kits: int = 1
        self.salvage_kits: int = 2
        self.expert_salvage_kits: int = 1
        self.lockpicks: int = 10
        self.sell_threshold: int = 200
        self.nick_weeks_to_keep: int = -1
        self.nick_items_to_keep: int = 0
        self.changed : bool = False
        self.polling_interval : float = 1  # Default polling interval in seconds

        # Collection of Filters
        self.filters: list[filter.Filter] = []

        self.runes: dict[str, RuneConfiguration] = {}
        self.weapon_mods: dict[str, dict[str, bool]] = {}
        self.items: ItemConfigurations = ItemConfigurations()
        self.blacklist: dict[ItemType, dict[int, bool]] = {}

    def save(self):
        """Save the profile as a JSON file."""
        self.changed = True
        
        profile_dict = {
            "name": self.name,
            "dyes": {dye.name: value for dye, value in self.dyes.items()},
            "identification_kits": self.identification_kits,
            "salvage_kits": self.salvage_kits,
            "expert_salvage_kits": self.expert_salvage_kits,
            "lockpicks": self.lockpicks,
            "sell_threshold": self.sell_threshold,
            "nick_weeks_to_keep": self.nick_weeks_to_keep,
            "nick_items_to_keep": self.nick_items_to_keep,
            "filters": [Filter.to_dict(filter) for filter in self.filters],
            "polling_interval": self.polling_interval,
            "runes":  {
                rune_identifier: rune_config.to_dict()
                for rune_identifier, rune_config in self.runes.items()
            },
            "weapon_mods": {
                mod_name: {weapon_type: is_active for weapon_type,
                           is_active in types.items()}
                for mod_name, types in self.weapon_mods.items()
            },
            "items": {
                item_type.name: {
                    item_id: ItemConfiguration.to_dict(item_config)
                    for item_id, item_config in items.items()
                }
                for item_type, items in self.items.items()                
            },
            "blacklist": {
                item_type.name: list(self.blacklist[item_type].keys())
                for item_type in self.blacklist
            }                
        }
        
        file_path = os.path.join(
            settings.current.profiles_path, f"{self.name}.json")

        with open(file_path, 'w') as file:
            # ConsoleLog(
            #     "LootEx", f"Saving profile {self.name}...", Console.MessageType.Debug)
            json.dump(profile_dict, file, indent=4)

    def load(self):
        """Load the profile from a JSON file."""
        file_path = os.path.join(
            settings.current.profiles_path, f"{self.name}.json")

        try:
            with open(file_path, 'r') as file:
                profile_dict = json.load(file)
                self.name = profile_dict.get("name", self.name)
                self.polling_interval = profile_dict.get("polling_interval", self.polling_interval)
                self.nick_weeks_to_keep = profile_dict.get(
                    "nick_weeks_to_keep", self.nick_weeks_to_keep)
                self.nick_items_to_keep = profile_dict.get(
                    "nick_items_to_keep", self.nick_items_to_keep)
                self.dyes = {DyeColor[dye]: value for dye,
                             value in profile_dict.get("dyes", {}).items()}
                self.identification_kits = profile_dict.get(
                    "identification_kits", self.identification_kits)
                self.salvage_kits = profile_dict.get(
                    "salvage_kits", self.salvage_kits)
                self.expert_salvage_kits = profile_dict.get(
                    "expert_salvage_kits", self.expert_salvage_kits)
                self.lockpicks = profile_dict.get("lockpicks", self.lockpicks)
                self.sell_threshold = profile_dict.get(
                    "sell_threshold", self.sell_threshold)
                self.filters = [Filter.from_dict(
                    filter) for filter in profile_dict.get("filters", [])]
                self.runes =  {
                    rune_identifier: RuneConfiguration.from_dict(rune_config)
                    for rune_identifier, rune_config in profile_dict.get("runes", {}).items()
                }
                self.weapon_mods = {
                    mod_name: {weapon_type: is_active for weapon_type,
                               is_active in types.items()}
                    for mod_name, types in profile_dict.get("weapon_mods", {}).items()
                }
                
                self.blacklist = {
                    ItemType[item_type]: {int(model_id): True for model_id in model_ids}
                    for item_type, model_ids in profile_dict.get("blacklist", {}).items()
                }
                
                configured_items = profile_dict.get("items", {})
                for item_type_name, items in configured_items.items():
                    for item_id, item in items.items():
                        item_config = ItemConfiguration.from_dict(item)
                        item_type = ItemType[item_type_name]
                        
                        if item_type not in self.items:
                            self.items[item_type] = {}
                        
                        self.items[item_type][int(item_id)] = item_config                

        except FileNotFoundError:
            ConsoleLog(
                "LootEx", f"Profile file {file_path} not found. Using default settings.", Console.MessageType.Warning)

    def delete(self):
        """Delete the profile file."""
        file_path = os.path.join(
            settings.current.profiles_path, f"{self.name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            ConsoleLog(
                "LootEx", f"Profile {self.name} deleted.", Console.MessageType.Info)
        else:
            ConsoleLog(
                "LootEx", f"Profile file {file_path} not found.", Console.MessageType.Warning)

    def set_rune(self, rune_identifier: str, is_valuable: bool, should_sell: bool | None = None):
        """Set the value of a rune in the profile."""
        config = self.runes.get(rune_identifier, RuneConfiguration(rune_identifier, is_valuable))
        
        if should_sell is not None and config.should_sell != should_sell:
            config.should_sell = should_sell
        
        if config.valuable != is_valuable:
            config.valuable = is_valuable
            
        self.changed = True
        
        if rune_identifier not in self.runes:
            self.runes[rune_identifier] = config
            return
                
        if not self.runes[rune_identifier].valuable and not self.runes[rune_identifier].should_sell:
            if rune_identifier in self.runes:
                del self.runes[rune_identifier]
        
        
    def contains_weapon_mod(self, mod_name: str) -> bool:
        """Check if the profile contains a specific weapon mod."""
        return mod_name in self.weapon_mods and any(self.weapon_mods[mod_name].values())

    def add_item_by_model(self, item_type : ItemType, model_id: int, action: ItemAction = ItemAction.STASH):
        """Add an item to the profile by model ID."""
        if item_type not in self.items:
            self.items[item_type] = {}
        
        if model_id not in self.items[item_type]:
            self.items[item_type][model_id] = ItemConfiguration(model_id, item_type, action)
        else:
            if len(self.items[item_type][model_id].conditions) == 1:
                self.items[item_type][model_id].conditions[0].action = action
            
    def add_item(self, item: models.Item, action: ItemAction = ItemAction.STASH):
        """Add an item to the profile."""
        if item.item_type not in self.items:
            self.items[item.item_type] = {}
        
        if item.model_id not in self.items[item.item_type]:
            self.items[item.item_type][item.model_id] = ItemConfiguration(item.model_id, item.item_type, action)
        else:
            if len(self.items[item.item_type][item.model_id].conditions) == 1:
                self.items[item.item_type][item.model_id].conditions[0].action = action

    def blacklist_item(self, item_type : ItemType, model_id: int):
        """Blacklist an item in the profile."""      
        if item_type not in self.blacklist:
            self.blacklist[item_type] = {}
            
              
        if model_id not in self.blacklist[item_type]:
            self.blacklist[item_type][model_id] = True

    def whitelist_item(self, item_type : ItemType, model_id: int):
        """Remove an item from the blacklist in the profile."""
        if item_type in self.blacklist:
            if model_id in self.blacklist[item_type]:
                del self.blacklist[item_type][model_id]
                
                if not self.blacklist[item_type]:
                    del self.blacklist[item_type]

    def is_blacklisted(self, item_type : ItemType, model_id: int) -> bool:
        """Check if an item is blacklisted in the profile."""
        return item_type in self.blacklist and model_id in self.blacklist[item_type]

    def remove_item(self, item_type : ItemType, model_id: int):
        """Remove an item from the profile."""
        if item_type in self.items:
            if model_id in self.items[item_type]:
                del self.items[item_type][model_id]
                if not self.items[item_type]:
                    del self.items[item_type]