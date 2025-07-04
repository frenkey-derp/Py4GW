from Py4GWCoreLib import Agent, AgentArray, Player
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Widgets.frenkey.LootEx import settings
from Widgets.frenkey.LootEx.cache import Cached_Item
from Widgets.frenkey.LootEx.enum import ItemAction
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, LootConfig
from Py4GWCoreLib.enums import Console, ItemType, ModelID, Range, SharedCommandType


class LootHandler:
    instance = None
    lootconfig = LootConfig()

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(LootHandler, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self, reset: bool = False):
        if self._initialized and not reset:
            return

        self._initialized = True

    def reset(self):        
        self.lootconfig.reset()
        
        if settings.current.profile is None:
            return
        
        pass
    
    def LootingRoutineActive(self):
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        index, message = GLOBAL_CACHE.ShMem.PreviewNextMessage(account_email)
        
        if index == -1 or message is None:
            return False
        
        if message.Command != SharedCommandType.PickUpLoot:
            return False
        
        return True
    
    def CheckExisingLoot(self):    
        if self.LootingRoutineActive():
            # ConsoleLog("LootEx", "Looting routine is already active. Skipping loot check.", Console.MessageType.Warning)
            return
        
        # ConsoleLog("LootEx", "Checking existing loot in the world.", Console.MessageType.Debug)        
        loot_array = GLOBAL_CACHE.AgentArray.GetItemArray()
        loot_array = AgentArray.Filter.ByDistance(loot_array, Player.GetXY(), Range.SafeCompass.value)
        
        for agent_id in loot_array:
            item_data = GLOBAL_CACHE.Agent.GetItemAgent(agent_id)
            
            if item_data is None:
                continue
            
            item_id = item_data.item_id
            
            if self.Should_Loot_Item(item_id):
                self.lootconfig.AddItemIDToWhitelist(item_id)
            else:
                self.lootconfig.AddItemIDToBlacklist(item_id)
                        
    def Should_Loot_Item(self, item_id: int) -> bool:
        ConsoleLog("LootEx", f"Checking if item {item_id} should be looted.", Console.MessageType.Debug)
        
        if settings.current.profile is None:
            ConsoleLog("LootEx", "No profile selected. Cannot determine loot action.", Console.MessageType.Warning)
            return False
        
        cached_item = Cached_Item(item_id)
        
        if not cached_item.data:
            return True
        
        if cached_item.model_id == ModelID.Vial_Of_Dye:
            if cached_item.IsVial_Of_DyeToKeep():
                return True
            else:
                return False
        
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
            
        return True