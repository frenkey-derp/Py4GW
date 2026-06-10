from typing import ClassVar, Self, cast

from Py4GWCoreLib.global_configs.RuleConfig import RuleConfig
from Py4GWCoreLib.global_configs.SortingConfig import SlotMatcherConfig

class InventoryConfig(RuleConfig):    
    _initialized: bool = False    
    _instances: ClassVar[dict[type[Self], Self]] = {}
    disallowed_rule_types: ClassVar[tuple[type, ...]] = (SlotMatcherConfig,)

    def __new__(cls: type[Self]) -> Self:
        instance = cast(Self | None, cls._instances.get(cls))
        if instance is None:
            instance = cast(Self, super().__new__(cls))
            instance._initialized = False
            cls._instances[cls] = instance
        return instance
    
    def __init__(self: Self) -> None:
        if self._initialized:
            self._ensure_profile_sync()
            return
        
        self._initialized = True
        super().__init__()
        self._ensure_profile_sync()

    def _ensure_profile_sync(self) -> None:
        try:
            from Py4GWCoreLib.global_configs.ProfileManager import GlobalConfigProfileManager

            GlobalConfigProfileManager().refresh_and_sync()
        except Exception:
            pass
