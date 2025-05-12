from PyMap import InstanceType
from LootEx import ItemAction
from LootEx.ItemAction import ItemActions
from Py4GWCoreLib import *

class LootFilter:
    def __init__(self, filter_name: str):
        self.Name = filter_name
        self.ItemTypes = {}

        for item_type in ItemType:
            self.ItemTypes[item_type] = False

        self.Rarities = {}
        for rarity in Rarity:
            self.Rarities[rarity] = False
        
        self.Actions = ItemActions()
    
    def HandlesItemId(self, item_id: int) -> bool:
        item_type = Item.GetItemType(item_id)[0]
        if item_type in self.ItemTypes and self.ItemTypes[item_type]:
            return True

        if self.Rarities[Item.Rarity.GetRarity(item_id)[0]]:
            return True

        return False
    
    def GetAction(self, instance_type: InstanceType) -> ItemAction.ItemAction:
        return self.Actions.GetAction(instance_type)
    
@staticmethod
def to_dict(data) -> dict:
    return {
        "Name": data.Name,
        "ItemTypes": {item_type.name: value for item_type, value in data.ItemTypes.items()},
        "Rarities": {rarity.name: value for rarity, value in data.Rarities.items()},
        "Actions": ItemActions.to_dict(data.Actions)
    }

@staticmethod
def from_dict(data) -> LootFilter:
    filter = LootFilter(data["Name"])
    filter.ItemTypes = {ItemType[item_type]: value for item_type, value in data["ItemTypes"].items()}
    filter.Rarities = {Rarity[rarity]: value for rarity, value in data["Rarities"].items()}
    filter.Actions = ItemActions.from_dict(data["Actions"])
    return filter