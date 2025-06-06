import os
import json
from LootEx import item_configuration, loot_filter, settings
from LootEx.loot_filter import LootFilter
from LootEx.item_configuration import *
from Py4GWCoreLib import Console
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import DyeColor


import importlib
importlib.reload(item_configuration)


class LootProfile:
    def __init__(self, profile_name: str):
        self.name = profile_name

        self.dyes = {dye: False for dye in DyeColor if dye != DyeColor.NoColor}
        self.identification_kits: int = 1
        self.salvage_kits: int = 2
        self.expert_salvage_kits: int = 1
        self.lockpicks: int = 10
        self.sell_threshold: int = 200
        self.nick_weeks_to_keep: int = 0
        self.nick_items_to_keep: int = 0

        # Collection of LootFilters
        self.filters: list[loot_filter.LootFilter] = []

        self.runes: dict[str, bool] = {}
        self.weapon_mods: dict[str, dict[str, bool]] = {}
        self.items: dict[int, ItemConfiguration] = {}
        self.blacklist: dict[int, bool] = {}

    def save(self):
        """Save the profile as a JSON file."""
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
            "blacklist": self.blacklist,
            "filters": [LootFilter.to_dict(filter) for filter in self.filters],
            "runes": self.runes,
            "weapon_mods": {
                mod_name: {weapon_type: is_active for weapon_type,
                           is_active in types.items()}
                for mod_name, types in self.weapon_mods.items()
            },
            "items": {item.model_id: ItemConfiguration.to_dict(item) for item_id, item in self.items.items()}
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
                self.filters = [LootFilter.from_dict(
                    filter) for filter in profile_dict.get("filters", [])]
                self.runes = profile_dict.get("runes", self.runes)
                self.weapon_mods = {
                    mod_name: {weapon_type: is_active for weapon_type,
                               is_active in types.items()}
                    for mod_name, types in profile_dict.get("weapon_mods", {}).items()
                }
                self.items = {item_id: ItemConfiguration.from_dict(
                    item) for item_id, item in profile_dict.get("items", {}).items()}
                self.blacklist = {
                    int(model_id): True for model_id in profile_dict.get("blacklist", {}).keys()}

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

    def contains_weapon_mod(self, mod_name: str) -> bool:
        """Check if the profile contains a specific weapon mod."""
        return mod_name in self.weapon_mods and any(self.weapon_mods[mod_name].values())

    def add_item(self, model_id: int, action: ItemAction = ItemAction.STASH):
        """Add an item to the profile."""
        if model_id not in self.items:
            self.items[model_id] = ItemConfiguration(model_id, action)

    def blacklist_item(self, model_id: int):
        """Blacklist an item in the profile."""        
        if model_id not in self.blacklist:
            self.blacklist[model_id] = True

    def whitelist_item(self, model_id: int):
        """Remove an item from the blacklist in the profile."""
        if model_id in self.blacklist:
            del self.blacklist[model_id]

    def is_blacklisted(self, model_id: int) -> bool:
        """Check if an item is blacklisted in the profile."""
        return model_id in self.blacklist

    def remove_item(self, model_id: int):
        """Remove an item from the profile."""
        if model_id in self.items:
            del self.items[model_id]
