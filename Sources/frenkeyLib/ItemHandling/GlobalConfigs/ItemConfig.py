from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.BuyConfig import BuyConfig, BuyInstruction
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.UpgradesConfig import UpgradesConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.SalvageConfig import SalvageConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.SellConfig import SellConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.DepositConfig import DepositConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.ProtectedItemsConfig import ProtectedItemsConfig


class ItemConfig:
    instance = None
    initalized = False
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(ItemConfig, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):  
        if self.initalized:
            return
              
        self.Buy = BuyConfig()
        self.Deposit = DepositConfig()
        self.Loot = LootConfig()
        self.Protected = ProtectedItemsConfig()
        self.Salvage = SalvageConfig()
        self.Sell = SellConfig()
        self.Upgrades = UpgradesConfig()
        
        self.initalized = True
    
    def GetItemsToBuy(self, include_storage : bool = True) -> list[BuyInstruction]:
        return self.Buy.GetItemsToBuy(include_storage=include_storage)
    
    def GetItemsToDeposit(self, bags : list[Bag]) -> list[int]:
        return self.Deposit.GetItemsToDeposit(bags)
    
    def GetItemsToLoot(self, distance : float = Range.Compass.value, multibox_loot: bool = False, allow_unasigned_loot: bool = False) -> list[int]:
        return self.Loot.GetfilteredLootArray(distance, multibox_loot=multibox_loot, allow_unasigned_loot=allow_unasigned_loot)
    
    def GetProtectedItems(self, bags : list[Bag]):
        return self.Protected.GetProtectedItems(bags)
    
    def GetItemsToSalvage(self, bags : list[Bag]) -> list[int]:
        return self.Salvage.GetItemsToSalvage(bags)  
    
    def GetItemsToSell(self, bags : list[Bag]) -> list[int]:
        return self.Sell.GetItemsToSell(bags)
    
    def GetUpgradesToExtract(self, bags : list[Bag]) -> list[int]:
        return self.Upgrades.GetUpgradesToExtract(bags)
    
    
        