import os
from typing import Callable

import Py4GW

from Py4GWCoreLib.IniManager import IniManager
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector
from Sources.frenkeyLib.DataCollector.collectors.allies_collector import ALLIES
from Sources.frenkeyLib.DataCollector.collectors.armor_collector import ARMORERS
from Sources.frenkeyLib.DataCollector.collectors.artisan_collector import ARTISANS
from Sources.frenkeyLib.DataCollector.collectors.chest_collector import CHESTS
from Sources.frenkeyLib.DataCollector.collectors.collectors_collector import COLLECTORS
from Sources.frenkeyLib.DataCollector.collectors.consumable_crafters_collector import CONSUMABLE_CRAFTERS
from Sources.frenkeyLib.DataCollector.collectors.foe_collector import FOES
from Sources.frenkeyLib.DataCollector.collectors.item_collector import ITEMS
from Sources.frenkeyLib.DataCollector.collectors.merchant_collector import MERCHANTS
from Sources.frenkeyLib.DataCollector.collectors.trader_collector import TRADERS
from Sources.frenkeyLib.DataCollector.collectors.weaponsmith_collector import WEAPONSMITHS
from Sources.frenkeyLib.DataCollector.config import DataCollectorConfig


def get_path_providers(file_name : str) -> tuple[Callable[..., str], Callable[..., str]]:        
    def local_path_provider() -> str:
        return os.path.join(Py4GW.Console.get_projects_path(), "Settings", "Global", "Widgets", "Data Collector", file_name)

    def default_path_provider() -> str:
        return os.path.join(Py4GW.Console.get_projects_path(), "Sources", "frenkeyLib", "data", file_name)

    return local_path_provider, default_path_provider

class DataCollectorRuntime:
    def __init__(self, module_name: str, module_icon: str):
        self.module_name = module_name
        self.module_icon = module_icon
        self.config = DataCollectorConfig()
        self.run_throttle = ThrottledTimer(250)
        self.collectors : dict[str, BaseCollector] = {
            'Allies': ALLIES,
            'Armorer': ARMORERS,
            'Artisans': ARTISANS,
            'Collectors': COLLECTORS,
            'Consumable Crafters': CONSUMABLE_CRAFTERS,
            'Foes': FOES,
            'Merchants': MERCHANTS,
            'Traders': TRADERS,
            'Weaponsmiths': WEAPONSMITHS,
            'Items': ITEMS,
            'Chests': CHESTS,
        }
        self.collector_enabled = True
        self._settings_loaded = False

    def ensure_state(self) -> bool:
        if not self.config.ensure_ini():
            Py4GW.Console.Log(self.module_name, 'Failed to ensure configuration INI file.', Py4GW.Console.MessageType.Error)
            return False

        if not self._settings_loaded:
            self._load_settings()
            self._settings_loaded = True

        return True

    def _load_settings(self):
        self.collector_enabled = bool(
            IniManager().getBool(
                self.config.main_ini_key,
                self.config.enabled_var_name,
                default=True,
                section=self.config.settings_section,
            )
        )

    def _save_settings(self):
        ini = IniManager()
        ini.set(
            self.config.main_ini_key,
            self.config.enabled_var_name,
            bool(self.collector_enabled),
            section=self.config.settings_section,
        )
        ini.save_vars(self.config.main_ini_key)

    def set_collector_enabled(self, enabled: bool):
        if not self.ensure_state():
            return

        enabled = bool(enabled)
        if enabled:
            Py4GW.Console.Log(
                self.module_name,
                'Data collector is enabled. Thank you for contributing by collecting data!',
                Py4GW.Console.MessageType.Success,
            )
        else:
            Py4GW.Console.Log(
                self.module_name,
                'Data collector is disabled. Enable the collector again to start contributing by collecting data.',
                Py4GW.Console.MessageType.Warning,
            )

        self.collector_enabled = enabled
        self._save_settings()

    def run(self):
        if not self.ensure_state():
            return

        for collector in self.collectors.values():
            collector.run()
