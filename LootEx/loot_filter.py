from PyMap import InstanceType
from LootEx import item_actions
from LootEx.enum import ItemAction
from LootEx.item_actions import ItemActions
from Py4GWCoreLib import *


class LootFilter:
    def __init__(self, filter_name: str):
        self.name: str = filter_name
        self.item_types: dict[ItemType, bool] = {
            item_type: False for item_type in ItemType}
        self.rarities: dict[Rarity, bool] = {
            rarity: False for rarity in Rarity}
        self.materials: dict[int, bool] = {}
        self.action: ItemAction = ItemAction.STASH
        self.exclude_rare_weapons: bool = False
        self.exclude_rare_items: bool = False
        self.salvage_item_max_vendorvalue = 1500

    def handles_item_id(self, item_id: int) -> bool:
        item_type = Item.GetItemType(item_id)[0]
        if ItemType(item_type) in self.item_types and self.item_types[ItemType(item_type)]:
            return True

        if self.rarities[Rarity(Item.Rarity.GetRarity(item_id)[0])]:
            return True

        return False

    @staticmethod
    def to_dict(data : "LootFilter") -> dict:
        return {
            "name": data.name,
            "item_types": {item_type.name: value for item_type, value in data.item_types.items()},
            "rarities": {rarity.name: value for rarity, value in data.rarities.items()},
            "materials": {material: value for material, value in data.materials.items()},
            "exclude_rare_weapons": data.exclude_rare_weapons,
            "exclude_rare_items": data.exclude_rare_items,
            "salvage_item_max_vendorvalue": data.salvage_item_max_vendorvalue,
            "action": data.action.name
        }

    @staticmethod
    def from_dict(data) -> "LootFilter":
        name = data.get("name", None)
        
        if not name:
            raise ValueError("LootFilter must have a name")
        
        loot_filter = LootFilter(name)
        
        action = ItemAction[data.get("action", "STASH")]
        loot_filter.action = action
        
        loot_filter.exclude_rare_weapons = data.get("exclude_rare_weapons", False)
        loot_filter.exclude_rare_items = data.get("exclude_rare_items", False)
        
        loot_filter.salvage_item_max_vendorvalue = data.get("salvage_item_max_vendorvalue", 1500)
        
        item_types: dict[str, bool] = data.get("item_types", {})                
        loot_filter.item_types = {
            ItemType[item_type]: value for item_type, value in item_types.items()}
        
        rarities: dict[str, bool] = data.get("rarities", {})
        loot_filter.rarities = {
            Rarity[rarity]: value for rarity, value in rarities.items()}
                
        materials = data.get("materials", {})
        loot_filter.materials = {int(material): value for material, value in materials.items()}
        
        return loot_filter
