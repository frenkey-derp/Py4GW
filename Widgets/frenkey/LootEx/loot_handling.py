from Widgets.frenkey.LootEx import settings
from Widgets.frenkey.LootEx.cache import Cached_Item
from Widgets.frenkey.LootEx.enum import ItemAction
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import Console, ItemType, ModelID


class LootHandler:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(LootHandler, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self, reset: bool = False):
        if self._initialized and not reset:
            return

        self._initialized = True
        
        
    def Should_Loot_Item(self, item_id: int) -> bool:
        # ConsoleLog("LootEx", f"Checking if item {item_id} should be looted.", Console.MessageType.Debug)
        
        if settings.current.profile is None:
            ConsoleLog("LootEx", "No profile selected. Cannot determine loot action.", Console.MessageType.Warning)
            return False
        
        cached_item = Cached_Item(item_id)
        
        if cached_item.model_id == ModelID.Vial_Of_Dye:
            if cached_item.IsVial_Of_DyeToKeep():
                return True
        
        if cached_item.config:
            action = cached_item.config.get_action(cached_item)
            if action == ItemAction.LOOT:
                return True

        for filter in settings.current.profile.filters:
            action = filter.get_action(cached_item)

            if action == ItemAction.LOOT:
                return True
        
        # If the item is a salvage item we check for runes we want to pick up and sell
        if cached_item.is_armor:
            if cached_item.runes_to_keep:
                return True
        
        # If the item is a weapon we check if it has a weapon mod we want to keep
        if cached_item.is_weapon:
            if cached_item.weapon_mods_to_keep:
                return True
            
        return False