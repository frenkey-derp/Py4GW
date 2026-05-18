from dataclasses import dataclass
import os
from typing import Callable, Generic, Optional

import Py4GW

from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.item_data.ItemData import ItemData
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Sources.frenkeyLib.Core.data_dict import DataDict, DataList
from Sources.frenkeyLib.DataCollector.data_collector import get_path_providers
from Sources.frenkeyLib.DataCollector.data_collector_widget import Ally, Armorer, Artisan, ConsumableCrafter, Foe, Merchant, Trader, Weaponsmith
from Sources.frenkeyLib.Core.json_serializable import T_DICT_KEY, T_SERIALIZABLE_VALUE

class BaseCollector:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.run_throttle = ThrottledTimer(250)
        self.save_throttle = ThrottledTimer(1_000)
        self.current_context_key = ''
        self.checked_ids: set[int] = set()

    def run(self):
        self._handle_context_change()
        
        if not self._is_ready():
            return
        
        if self.run_throttle.IsExpired():
            self.run_throttle.Reset()
            
            self._collect()

        if self.save_throttle.IsExpired():
            self.save_throttle.Reset()
            
            data = getattr(self, 'data', None)
            
            if isinstance(data, (DataDict, DataList)) and data.requires_save:
                data.save()

    def _is_ready(self) -> bool:
        return Map.IsMapReady() and Player.IsPlayerLoaded()
    
    def _collect(self):
        raise NotImplementedError

    def _flush_cache(self):
        self.checked_ids.clear()

    def _handle_context_change(self):
        context_key = self._get_context_key()
        if context_key == self.current_context_key:
            return

        self.current_context_key = context_key
        self._flush_cache()

    def _get_context_key(self) -> str:
        account_email = str(Player.GetAccountEmail() or '').strip()
        player_name = str(Player.GetName() or '').strip()
        map_id = int(Map.GetMapID() or 0)
        return f'{account_email}|{player_name}|{map_id}'
    
    @staticmethod
    def get_path_providers(file_name : str) -> tuple[Callable[..., str], Callable[..., str]]:        
        def local_path_provider() -> str:
            return os.path.join(Py4GW.Console.get_projects_path(), "Settings", "Global", "Widgets", "Data Collector", file_name)

        def default_path_provider() -> str:
            return os.path.join(Py4GW.Console.get_projects_path(), "Sources", "frenkeyLib", "data", file_name)

        return local_path_provider, default_path_provider

class ListCollector(BaseCollector, DataList[T_SERIALIZABLE_VALUE]):
    def __init__(self,
        get_local_path: Callable[..., str],
        get_default_path: Callable[..., str],
        *,
        version: str = '1.0',
        value_type: Optional[type[T_SERIALIZABLE_VALUE]] = None,
        key_decoder: Optional[Callable[[str], T_DICT_KEY]] = None,
        key_encoder: Optional[Callable[[T_DICT_KEY], str]] = None,
    ):
        super().__init__(
            get_local_path,
            get_default_path,
            version=version,
            value_type=value_type,
            key_decoder=key_decoder,
            key_encoder=key_encoder,
        )
        self.load()