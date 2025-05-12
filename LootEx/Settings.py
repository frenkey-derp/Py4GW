from typing import Optional
from Py4GW import Console

from LootEx.LootFilter import LootFilter
from LootEx.LootProfile import LootProfile
from Py4GWCoreLib import Player, UIManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog

class FrameCoords:
    def __init__(self, frame_id):
        self.frame_id = frame_id
        self.left, self.top, self.right, self.bottom = UIManager.GetFrameCoords(self.frame_id) 
        self.height = self.bottom - self.top
        self.width = self.right - self.left  

class Settings:
    def __init__(self):
        self.ProfileCombo : int = 0
        self.LootProfile : Optional[LootProfile] = None
        self.LootProfiles : list[LootProfile] = []
        self.SelectedLootFilter: Optional[LootFilter] = None
        self.AutomaticInventoryHandling : bool = "games" in Player.GetAccountEmail().lower()
        self.WindowSize : tuple[float, float] = (800, 600)
        self.WindowPosition : tuple[float, float] = (500, 200)
        self.WindowCollapsed : bool = False
        self.WindowVisible : bool = False
        self.ManualWindowVisible : bool = False

        self.Settings_file_path : str = ""
        self.ProfilesPath : str = ""
        
        self.inventory_frame_exists = False
        self.inventory_frame_coords: FrameCoords
        self.parent_frame_id: int


    def Save(self):
        # Save the settings as a JSON file

        import json
        settings_dict = {
            "LootProfile": self.LootProfile.Name if self.LootProfile else None,
            "AutomaticInventoryHandling": self.AutomaticInventoryHandling,
            "WindowSize": self.WindowSize,
            "WindowPosition": self.WindowPosition,
            "WindowCollapsed": self.WindowCollapsed,
            "ManualWindowVisible": self.ManualWindowVisible,
        }

        with open(self.Settings_file_path, 'w') as f:
            json.dump(settings_dict, f, indent=4)
            # ConsoleLog("LootEx", f"Settings saved to {self.Settings_file_path}", Console.MessageType.Info)

    def Load(self):
        # Load the settings from a JSON file
        import json

        # Create the directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(self.Settings_file_path), exist_ok=True)
        os.makedirs(self.ProfilesPath, exist_ok=True)

        # Load profiles
        for file_name in os.listdir(self.ProfilesPath):
            if file_name.endswith(".json"):
                profile = LootProfile(file_name[:-5])
                profile.Load()
                self.LootProfiles.append(profile)

        if not self.LootProfiles:
            self.LootProfiles.append(LootProfile("Default"))
            self.LootProfiles[0].Save()
            
        try:
            with open(self.Settings_file_path, 'r') as f:
                settings_dict = json.load(f)
                self.LootProfile = next((profile for profile in self.LootProfiles if profile.Name == settings_dict.get("LootProfile")), None)
                self.ProfileCombo = self.LootProfiles.index(self.LootProfile) if self.LootProfile else 0
                self.AutomaticInventoryHandling = settings_dict.get("AutomaticInventoryHandling", True)
                self.WindowSize = tuple(settings_dict.get("WindowSize", (400, 200)))
                self.WindowPosition = tuple(settings_dict.get("WindowPosition", (200, 200)))
                self.WindowCollapsed = settings_dict.get("WindowCollapsed", False)
                self.ManualWindowVisible = settings_dict.get("ManualWindowVisible", False)
                # ConsoleLog("LootEx", f"Settings loaded from {self.Settings_file_path}", Console.MessageType.Info)

            self.AutomaticInventoryHandling = self.AutomaticInventoryHandling if self.LootProfile != None else False
            self.LootProfile = self.LootProfiles[0] if self.LootProfile is None else self.LootProfile

        except FileNotFoundError:
            ConsoleLog("LootEx", f"Settings file {self.Settings_file_path} not found. Using default settings.", Console.MessageType.Warning)


Current = Settings()