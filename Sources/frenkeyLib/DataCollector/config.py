from dataclasses import dataclass

from Py4GWCoreLib.IniManager import IniManager


@dataclass
class DataCollectorConfig:
    ini_path: str = 'Widgets/System/'
    main_ini_filename: str = 'DataCollector.ini'
    floating_ini_filename: str = 'DataCollectorFloating.ini'
    settings_section: str = 'Settings'
    enabled_var_name: str = 'collector_enabled'
    enabled_key_name: str = 'collector_enabled'

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
            self.enabled_key_name,
            True,
        )
        ini.load_once(self.main_ini_key)
        ini.load_once(self.floating_ini_key)

        self.ini_init = True
        return True

