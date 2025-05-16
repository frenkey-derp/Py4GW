from typing import Optional
from LootEx.loot_filter import LootFilter
from LootEx.loot_profile import LootProfile
from Py4GWCoreLib import Player, UIManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, Console
from Py4GWCoreLib.enums import ServerLanguage


class FrameCoords:
    def __init__(self, frame_id: int):
        self.frame_id = frame_id
        self.left, self.top, self.right, self.bottom = UIManager.GetFrameCoords(
            self.frame_id)
        self.height = self.bottom - self.top
        self.width = self.right - self.left


class Settings:
    def __init__(self):
        self.profile_combo: int = 0
        self.loot_profile: Optional[LootProfile] = None
        self.loot_profiles: list[LootProfile] = []
        self.selected_loot_filter: Optional[LootFilter] = None
        self.automatic_inventory_handling: bool = "games" in Player.GetAccountEmail().lower()
        self.window_size: tuple[float, float] = (800, 600)
        self.window_position: tuple[float, float] = (500, 200)
        self.window_collapsed: bool = False
        self.window_visible: bool = False
        self.manual_window_visible: bool = False

        self.settings_file_path: str = ""
        self.profiles_path: str = ""
        self.data_collection_path: str = ""
        
        self.inventory_frame_exists: bool = False
        self.inventory_frame_coords: Optional[FrameCoords] = None
        self.parent_frame_id: Optional[int] = None
                
        self.language : ServerLanguage = ServerLanguage.English

    def set_language(self, lang = ServerLanguage.English):
        self.language = lang


    def save(self):
        """Save the settings as a JSON file."""
        import json

        settings_dict = {
            "loot_profile": self.loot_profile.name if self.loot_profile else None,
            "automatic_inventory_handling": self.automatic_inventory_handling,
            "window_size": self.window_size,
            "window_position": self.window_position,
            "window_collapsed": self.window_collapsed,
            "manual_window_visible": self.manual_window_visible,
        }
        # ConsoleLog(
        #     "LootEx", f"Saving settings to '{self.settings_file_path}'...", Console.MessageType.Debug)
        if self.settings_file_path == "":
            return
        
        # Create the directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        
        with open(self.settings_file_path, 'w') as file:
            json.dump(settings_dict, file, indent=4)

    def load(self):
        """Load the settings from a JSON file."""
        import json
        import os

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        os.makedirs(self.profiles_path, exist_ok=True)
        os.makedirs(self.data_collection_path, exist_ok=True)

        # Load profiles
        for file_name in os.listdir(self.profiles_path):
            if file_name.endswith(".json"):
                profile = LootProfile(file_name[:-5])
                profile.load()
                self.loot_profiles.append(profile)

        if not self.loot_profiles:
            default_profile = LootProfile("Default")
            default_profile.save()
            self.loot_profiles.append(default_profile)

        try:
            with open(self.settings_file_path, 'r') as file:
                settings_dict = json.load(file)
                self.loot_profile = next(
                    (profile for profile in self.loot_profiles if profile.name ==
                     settings_dict.get("loot_profile")),
                    None
                )
                self.profile_combo = self.loot_profiles.index(
                    self.loot_profile) if self.loot_profile else 0
                self.automatic_inventory_handling = settings_dict.get(
                    "automatic_inventory_handling", True)
                self.window_size = tuple(
                    settings_dict.get("window_size", (400, 200)))
                self.window_position = tuple(
                    settings_dict.get("window_position", (200, 200)))
                self.window_collapsed = settings_dict.get(
                    "window_collapsed", False)
                self.manual_window_visible = settings_dict.get(
                    "manual_window_visible", False)

            self.automatic_inventory_handling = (
                self.automatic_inventory_handling if self.loot_profile else False
            )
            self.loot_profile = self.loot_profiles[0] if self.loot_profile is None else self.loot_profile

        except FileNotFoundError:
            ConsoleLog(
                "LootEx",
                f"Settings file {self.settings_file_path} not found. Using default settings.",
                Console.MessageType.Warning,
            )


current = Settings()
