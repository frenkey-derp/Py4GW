from dataclasses import dataclass

from Py4GWCoreLib.IniManager import IniManager


@dataclass
class DataCollectorConfig:
    ini_path: str = 'Widgets/System/'
    main_ini_filename: str = 'DataCollector.ini'
    floating_ini_filename: str = 'DataCollectorFloating.ini'
    settings_section: str = 'Settings'
    
    enabled_var_name: str = 'collector_enabled'    

    main_ini_key: str = ''
    floating_ini_key: str = ''
    ini_init: bool = False

    def ensure_ini(self) -> bool:
        if self.ini_init:
            return True

        ini = IniManager()
        self.main_ini_key = ini.ensure_global_key(
            self.ini_path,
            self.main_ini_filename,
        )
        self.floating_ini_key = ini.ensure_global_key(
            self.ini_path,
            self.floating_ini_filename,
        )
        if not self.main_ini_key or not self.floating_ini_key:
            return False

        ini.add_bool(
            self.main_ini_key,
            self.enabled_var_name,
            self.settings_section,
            self.enabled_var_name,
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectAllies",
            self.settings_section,
            "CollectAllies",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectArmorer",
            self.settings_section,
            "CollectArmorer",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectArtisans",
            self.settings_section,
            "CollectArtisans",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectCollectors",
            self.settings_section,
            "CollectCollectors",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectConsumableCrafters",
            self.settings_section,
            "CollectConsumableCrafters",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectFoes",
            self.settings_section,
            "CollectFoes",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectMerchants",
            self.settings_section,
            "CollectMerchants",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectTraders",
            self.settings_section,
            "CollectTraders",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectWeaponsmiths",
            self.settings_section,
            "CollectWeaponsmiths",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectItems",
            self.settings_section,
            "CollectItems",
            True,
        )
        
        ini.add_bool(
            self.main_ini_key,
            "CollectChests",
            self.settings_section,
            "CollectChests",
            True,
        )
        
        ini.load_once(self.main_ini_key)
        ini.load_once(self.floating_ini_key)

        self.ini_init = True
        return True

