from PyMap import InstanceType
from enum import IntEnum


class ItemAction(IntEnum):
    _None = 0
    Identify = 1
    Salvage = 2
    Sell = 3
    Stash = 4
    SalvageRareMaterials = 5
    Destroy = 6 

class ItemActions:
    def __init__(self, explorable : ItemAction = ItemAction._None, outpost : ItemAction = ItemAction._None):
        self.Explorable : ItemAction = explorable
        self.Outpost : ItemAction = outpost

    def GetAction(self, instanceType: InstanceType) -> ItemAction:
        if instanceType == InstanceType.Outpost:
            return self.Outpost
        elif instanceType == InstanceType.Explorable:
            return self.Explorable
        else:
            return ItemAction._None

    @staticmethod
    def to_dict(data) -> dict:
        return {
            "Explorable": data.Explorable.name,
            "Outpost": data.Outpost.name
        } 

    @staticmethod
    def from_dict(data):
        explorable = ItemAction[data["Explorable"]] if data["Explorable"] in ItemAction.__members__ else ItemAction._None
        outpost = ItemAction[data["Outpost"]] if data["Outpost"] in ItemAction.__members__ else ItemAction._None
        return ItemActions(explorable, outpost)

class LootAction(IntEnum):
    _None = 0
    Loot = 1
    Ignore = 2
    LootIfStackable = 3

class LootItemMode(IntEnum):
    ModelId = 0
    ItemType = 1

class InventoryAction(IntEnum):
    def __init__(self, item_id: int):
        self.ItemId = item_id
        self.Action : ItemAction = ItemAction._None
        self.SourceBag : int = 0
        self.SourceSlot : int = 0   
        self.TargetBag : int = 0
        self.TargetSlot : int = 0
        self.Quantity : int = 0