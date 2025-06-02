from enum import IntEnum
from PyMap import InstanceType


class ItemAction(IntEnum):
    NONE = 0
    IDENTIFY = 1
    SALVAGE = 2
    SELL = 3
    STASH = 4
    SALVAGE_RARE_MATERIALS = 5
    SALVAGE_MODS = 6
    DESTROY = 7
    COLLECT_DATA = 8


class ItemActions:
    def __init__(self, explorable: ItemAction = ItemAction.NONE, outpost: ItemAction = ItemAction.NONE):
        self.explorable: ItemAction = explorable
        self.outpost: ItemAction = outpost

    def get_action(self, instance_type: InstanceType) -> ItemAction:
        if instance_type == InstanceType.Outpost:
            return self.outpost
        elif instance_type == InstanceType.Explorable:
            return self.explorable
        return ItemAction.NONE

    @staticmethod
    def to_dict(data) -> dict:
        return {
            "explorable": data.explorable.name,
            "outpost": data.outpost.name
        }

    @staticmethod
    def from_dict(data):
        explorable = ItemAction[data["explorable"]
                                ] if data["explorable"] in ItemAction.__members__ else ItemAction.NONE
        outpost = ItemAction[data["outpost"]
                             ] if data["outpost"] in ItemAction.__members__ else ItemAction.NONE
        return ItemActions(explorable, outpost)


class LootAction(IntEnum):
    NONE = 0
    LOOT = 1
    IGNORE = 2
    LOOT_IF_STACKABLE = 3


class LootItemMode(IntEnum):
    MODEL_ID = 0
    ITEM_TYPE = 1


class InventoryAction:
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.action: ItemAction = ItemAction.NONE
        self.source_bag: int = 0
        self.source_slot: int = 0
        self.target_bag: int = 0
        self.target_slot: int = 0
        self.quantity: int = 0
