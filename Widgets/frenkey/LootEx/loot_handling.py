from Py4GWCoreLib import Agent, AgentArray, Player
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Widgets.frenkey.LootEx.settings import Settings
from Widgets.frenkey.LootEx.cache import Cached_Item
from Widgets.frenkey.LootEx.enum import ItemAction
from Py4GWCoreLib.Py4GWcorelib import ActionQueueManager, ConsoleLog, LootConfig
from Py4GWCoreLib.enums import Console, ItemType, ModelID, Range, SharedCommandType


class LootHandler:
    instance = None
    lootconfig = LootConfig()
    settings = Settings()

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
        
        if self.settings.profile is None:
            return
        
        pass
    
    def Stop(self):
        ConsoleLog("LootEx", "Stopping Loot Handler", Console.MessageType.Info)
        LootHandler.lootconfig.RemoveCustomItemCheck(self.Should_Loot_Item)
        self.settings.enable_loot_filters = False
        self.settings.save()
        

    def Start(self):
        ConsoleLog("LootEx", "Starting Loot Handler", Console.MessageType.Info)
        LootHandler.lootconfig.AddCustomItemCheck(self.Should_Loot_Item)
        self.settings.enable_loot_filters = True
        self.settings.save()
        

    def SetLootRange(self, loot_range: int):
        if self.settings.profile is None:
            ConsoleLog("LootEx", "No profile selected. Cannot set loot range.", Console.MessageType.Warning)
            return
                
        for index, message in GLOBAL_CACHE.ShMem.GetAllMessages():            
            if message.Command == SharedCommandType.PickUpLoot:
                GLOBAL_CACHE.ShMem.MarkMessageAsFinished(message.ReceiverEmail, index)
                
        # self.lootconfig.ClearItemIDWhitelist()
        # self.lootconfig.ClearItemIDBlacklist()
        ActionQueueManager().ResetAllQueues()        
    
    def LootingRoutineActive(self):
        account_email = GLOBAL_CACHE.Player.GetAccountEmail()
        index, message = GLOBAL_CACHE.ShMem.PreviewNextMessage(account_email)
        
        if index == -1 or message is None:
            return False
        
        if message.Command != SharedCommandType.PickUpLoot:
            return False
        
        return True
    
    def CheckExisingLoot(self):                    
        if not self.settings.profile or not self.settings.enable_loot_filters or not self.settings.profile.loot_range:
            return
        
        # if self.LootingRoutineActive():
        #     # ConsoleLog("LootEx", "Looting routine is already active. Skipping loot check.", Console.MessageType.Warning)
        #     return
        
        # ConsoleLog("LootEx", "Checking existing loot in the world.", Console.MessageType.Debug)        
        loot_array = GLOBAL_CACHE.AgentArray.GetItemArray()
        distance = self.settings.profile.loot_range if self.settings.profile else Range.SafeCompass.value
        loot_array = AgentArray.Filter.ByDistance(loot_array, Player.GetXY(), distance)
        
        # self.lootconfig.ClearItemIDWhitelist()
        # self.lootconfig.ClearItemIDBlacklist()
        
        for agent_id in loot_array:
            item_data = GLOBAL_CACHE.Agent.GetItemAgent(agent_id)
            
            if item_data is None:
                continue
            
            item_id = item_data.item_id
            
            if self.Should_Loot_Item(item_id):
                self.lootconfig.AddItemIDToWhitelist(item_id)
            else:
                self.lootconfig.AddItemIDToBlacklist(item_id)
                        
    def IsEnabled(self) -> bool:
        return self.settings.enable_loot_filters and self.settings.profile is not None
                        
    def Should_Loot_Item(self, item_id: int) -> bool:
        # ConsoleLog("LootEx", f"Checking if item {item_id} should be looted.", Console.MessageType.Debug)
        
        if self.settings.profile is None:
            ConsoleLog("LootEx", "No profile selected. Cannot determine loot action.", Console.MessageType.Warning)
            return False
        
        if self.settings.enable_loot_filters == False:
            return False
        
        cached_item = Cached_Item(item_id)
        
        if not cached_item.data:
            return True
        
        if cached_item.model_id == ModelID.Vial_Of_Dye:
            if cached_item.IsVial_Of_DyeToKeep():
                # ConsoleLog("LootEx", f"Item {item_id} is a Vial of Dye that we want to keep.", Console.MessageType.Debug)
                return True
            else:
                # ConsoleLog("LootEx", f"Item {item_id} is a Vial of Dye that we do not want to keep.", Console.MessageType.Debug)
                return False
        
        if cached_item.matches_weapon_rule:
            return True
        
        if cached_item.matches_skin_rule:
            return True

        for filter in self.settings.profile.filters:
            action = filter.get_action(cached_item)

            if action == ItemAction.Loot:
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