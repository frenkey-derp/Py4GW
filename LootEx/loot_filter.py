from PyMap import InstanceType
from LootEx import item_actions
from LootEx.item_actions import ItemActions
from Py4GWCoreLib import *


class LootFilter:
    def __init__(self, filter_name: str):
        self.name = filter_name
        self.item_types = {item_type: False for item_type in ItemType}
        self.rarities = {rarity: False for rarity in Rarity}
        self.actions = ItemActions()

    def handles_item_id(self, item_id: int) -> bool:
        item_type = Item.GetItemType(item_id)[0]
        if ItemType(item_type) in self.item_types and self.item_types[ItemType(item_type)]:
            return True

        if self.rarities[Rarity(Item.Rarity.GetRarity(item_id)[0])]:
            return True

        return False

    def get_action(self, instance_type: InstanceType) -> item_actions.ItemAction:
        return self.actions.get_action(instance_type)

    @staticmethod
    def to_dict(data) -> dict:
        return {
            "name": data.name,
            "item_types": {item_type.name: value for item_type, value in data.item_types.items()},
            "rarities": {rarity.name: value for rarity, value in data.rarities.items()},
            "actions": ItemActions.to_dict(data.actions),
        }

    @staticmethod
    def from_dict(data) -> "LootFilter":
        loot_filter = LootFilter(data["name"])
        loot_filter.item_types = {
            ItemType[item_type]: value for item_type, value in data["item_types"].items()}
        loot_filter.rarities = {
            Rarity[rarity]: value for rarity, value in data["rarities"].items()}
        loot_filter.actions = ItemActions.from_dict(data["actions"])
        return loot_filter
