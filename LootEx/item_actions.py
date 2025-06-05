from enum import IntEnum
from PyMap import InstanceType

from LootEx.enum import ItemAction

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




class InventoryAction:
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.action: ItemAction = ItemAction.NONE
        self.source_bag: int = 0
        self.source_slot: int = 0
        self.target_bag: int = 0
        self.target_slot: int = 0
        self.quantity: int = 0
