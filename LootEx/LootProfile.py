from LootEx import LootItem, Settings, LootFilter
from LootEx.Data import Rune, WeaponType
from Py4GWCoreLib import *

import importlib
importlib.reload(LootFilter)

class LootProfile:    
    def __init__(self, profile_name: str):
        self.Name = profile_name
        
        self.Dyes = {}
        for dye in DyeColor:
            if(dye != DyeColor.NoColor):
                self.Dyes[dye] = False

        self.IdentificationKits : int = 1
        self.SalvageKits : int = 2
        self.ExpertSalvageKits : int = 1
        self.Lockpicks : int = 10
        self.SellThreshold : int = 0
        
        # Collection of LootFilters
        self.Filters : list[LootFilter.LootFilter] = []

        self.Runes : dict[str, bool] = {}
        self.WeaponMods : dict[str, dict[str, bool]] = {}
        self.Items : dict[str, LootItem.LootItem] = {}

    def Save(self):
        # Save the profile as a JSON file
        import json
        profile_dict = {
            "Name": self.Name,
            "Dyes": {dye.name: value for dye, value in self.Dyes.items()},
            "IdentificationKits": self.IdentificationKits,
            "SalvageKits": self.SalvageKits,
            "ExpertSalvageKits": self.ExpertSalvageKits,
            "Lockpicks": self.Lockpicks,
            "Filters": [LootFilter.to_dict(filter) for filter in self.Filters],
            "Runes": {rune: value for rune, value in self.Runes.items()},
            "WeaponMods": {                    
                mod_name: {weapon_type: is_active for weapon_type, is_active in types.items()}
                for mod_name, types in self.WeaponMods.items()
            },
            "Items": {item.ModelId.name: LootItem.to_dict(item) for item_id, item in self.Items.items()}
        }
        file_path = os.path.join(Settings.Current.ProfilesPath, self.Name + ".json")

        with open(file_path, 'w') as f:
            json.dump(profile_dict, f, indent=4)
            # ConsoleLog("LootEx", f"Profile saved to {file_path}", Console.MessageType.Info)
    
    def Load(self):
        # Load the profile from a JSON file
        import json
        file_path = os.path.join(Settings.Current.ProfilesPath, self.Name + ".json")

        try:
            with open(file_path, 'r') as f:
                profile_dict = json.load(f)
                self.Name = profile_dict.get("Name", self.Name)
                self.Dyes = {DyeColor[dye]: value for dye, value in profile_dict.get("Dyes", {}).items()}
                self.IdentificationKits = profile_dict.get("IdentificationKits", self.IdentificationKits)
                self.SalvageKits = profile_dict.get("SalvageKits", self.SalvageKits)
                self.ExpertSalvageKits = profile_dict.get("ExpertSalvageKits", self.ExpertSalvageKits)
                self.Lockpicks = profile_dict.get("Lockpicks", self.Lockpicks)
                self.Filters = [LootFilter.from_dict(filter) for filter in profile_dict.get("Filters", [])]
                self.Runes = {rune: value for rune, value in profile_dict.get("Runes", {}).items()}
                self.WeaponMods = {
                    mod_name: {weapon_type: is_active for weapon_type, is_active in types.items()}
                    for mod_name, types in profile_dict.get("WeaponMods", {}).items()                    
                }
                self.Items = {item_id: LootItem.from_dict(item) for item_id, item in profile_dict.get("Items", {}).items()}

        except FileNotFoundError:
            ConsoleLog("LootEx", f"Profile file {file_path} not found. Using default settings.", Console.MessageType.Warning)

    def Delete(self):
        # Delete the profile file
        file_path = os.path.join(Settings.Current.ProfilesPath, self.Name + ".json")
        if os.path.exists(file_path):
            os.remove(file_path)
            ConsoleLog("LootEx", f"Profile {self.Name} deleted.", Console.MessageType.Info)
        else:
            ConsoleLog("LootEx", f"Profile file {file_path} not found.", Console.MessageType.Warning)