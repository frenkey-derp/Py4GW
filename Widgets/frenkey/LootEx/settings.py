import datetime
from typing import Optional
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Widgets.frenkey.LootEx import inventory_handling
from Widgets.frenkey.LootEx.filter import Filter
from Widgets.frenkey.LootEx.profile import Profile
from Py4GWCoreLib import Player, UIManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, Console
from Py4GWCoreLib.enums import ServerLanguage
import json
import os


class FrameCoords:
    def __init__(self, frame_id: int):
        self.frame_id = frame_id
        self.left, self.top, self.right, self.bottom = UIManager.GetFrameCoords(
            self.frame_id)
        self.height = self.bottom - self.top
        self.width = self.right - self.left


class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
            
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.profile: Profile | None = None
        self.character_profiles: dict[str, str] = {}
        self.profiles: list[Profile] = []
        self.selected_filter: Optional[Filter] = None
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
        
        self.collect_items: bool = False
        self.last_xunlai_check : datetime.datetime = datetime.datetime.min
        
        self.changed = False
        self.development_mode: bool = os.path.exists("C:\\frenkey_development") 
        
    def set_language(self, lang = ServerLanguage.English):
        self.language = lang
        
    
    def SetProfile(self, profile_name: str | None):
        self.profile = Profile("Default")
        
        if profile_name is not None:            
            for profile in self.profiles:
                if profile.name == profile_name:
                    self.profile = profile
                    break
                
            if self.profile is None:
                self.profile = self.profiles[0] if self.profiles else Profile("Default")
            
            if not self.profiles:
                self.profiles.append(self.profile)
                
        if self.profile:
            inventory_handling.InventoryHandler().SetPollingInterval(self.profile.polling_interval)

    def save(self):
        """Save the settings as a JSON file."""
        settings_dict = {
            "character_profiles":  self.character_profiles,
            "automatic_inventory_handling": self.automatic_inventory_handling,
            "window_size": self.window_size,
            "window_position": self.window_position,
            "window_collapsed": self.window_collapsed,
            "manual_window_visible": self.manual_window_visible,
            "collect_items": self.collect_items,
            "last_xunlai_check": self.last_xunlai_check.isoformat(),
        }
        # ConsoleLog(
        #     "LootEx", f"Saving settings to '{self.settings_file_path}'...", Console.MessageType.Debug)
        if self.settings_file_path == "":
            return
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        
        with open(self.settings_file_path, 'w') as file:
            json.dump(settings_dict, file, indent=4)

    def load(self):
        """Load the settings from a JSON file."""

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        os.makedirs(self.profiles_path, exist_ok=True)
        os.makedirs(self.data_collection_path, exist_ok=True)

        # Load profiles
        for file_name in os.listdir(self.profiles_path):
            if file_name.endswith(".json"):
                profile = Profile(file_name[:-5])
                profile.load()
                self.profiles.append(profile)

        if not self.profiles:
            default_profile = Profile("Default")
            default_profile.save()
            default_profile.load()
            self.profiles.append(default_profile)

        try:
            with open(self.settings_file_path, 'r') as file:
                settings_dict = json.load(file)
                self.character_profiles  = settings_dict.get("character_profiles", {})
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
                self.collect_items = settings_dict.get("collect_items", False)
                last_xunlai_check_str = settings_dict.get("last_xunlai_check", None)
                if last_xunlai_check_str:
                    self.last_xunlai_check = datetime.datetime.fromisoformat(
                        last_xunlai_check_str)

            self.automatic_inventory_handling = (
                self.automatic_inventory_handling if self.profile else False
            )

        except FileNotFoundError:
            ConsoleLog(
                "LootEx",
                f"Settings file for {GLOBAL_CACHE.Player.GetAccountEmail()} not found. Using default settings.",
                Console.MessageType.Warning,
            )


current = Settings()