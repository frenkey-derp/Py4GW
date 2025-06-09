from LootEx import utility
from LootEx.enum import ItemAction, ItemCategory
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
        self.exclude_low_req: bool = False
        self.exclude_rare_weapons: bool = False
        self.exclude_rare_items: bool = False
        self.salvage_item_max_vendorvalue = 1500

    def handles_item(self, item) -> bool:
        
        item_type_match = any(utility.Util.IsMatchingItemType(item.item_type, item_type_enum)
                              for item_type_enum in self.item_types if self.item_types[item_type_enum])

        if not item_type_match:
            return False


        if not self.rarities.get(item.rarity, False) or self.rarities[item.rarity] is False:
            return False

        if self.exclude_rare_weapons and (item.data is None or item.data.category == ItemCategory.RareWeapon):
            return False
        
        if self.exclude_low_req and utility.Util.is_low_requirement_item(item.item_id):
            return False

        if self.action == ItemAction.SALVAGE or self.action == ItemAction.SALVAGE_SMART or self.action == ItemAction.SALVAGE_RARE_MATERIALS or self.action == ItemAction.SALVAGE_COMMON_MATERIALS:
            if self.materials:
                if not item.data:
                    return False

                material_match = False
                common_materials = [
                    m.material_model_id for m in item.data.common_salvage.values()]
                rare_materials = [
                    m.material_model_id for m in item.data.rare_salvage.values()]

                for material in self.materials:
                    if material in common_materials or material in rare_materials:
                        material_match = True
                        break

                if not material_match:
                    return False

                if item.value > self.salvage_item_max_vendorvalue:
                    return False

        return True

    def get_action(self, item) -> ItemAction:
        if item.action != ItemAction.NONE:
            return item.action
                
        if self.handles_item(item):
            return self.action

        return ItemAction.NONE

    @staticmethod
    def to_dict(data: "LootFilter") -> dict:
        return {
            "name": data.name,
            "item_types": {item_type.name: value for item_type, value in data.item_types.items()},
            "rarities": {rarity.name: value for rarity, value in data.rarities.items()},
            "materials": {material: value for material, value in data.materials.items()},
            "exclude_rare_weapons": data.exclude_rare_weapons,
            "exclude_rare_items": data.exclude_rare_items,
            "exclude_low_req": data.exclude_low_req,
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

        loot_filter.exclude_rare_weapons = data.get(
            "exclude_rare_weapons", False)
        loot_filter.exclude_rare_items = data.get("exclude_rare_items", False)
        
        loot_filter.exclude_low_req = data.get("exclude_low_req", False)

        loot_filter.salvage_item_max_vendorvalue = data.get(
            "salvage_item_max_vendorvalue", 1500)

        item_types: dict[str, bool] = data.get("item_types", {})
        loot_filter.item_types = {
            ItemType[item_type]: value for item_type, value in item_types.items()}

        rarities: dict[str, bool] = data.get("rarities", {})
        loot_filter.rarities = {
            Rarity[rarity]: value for rarity, value in rarities.items()}

        materials = data.get("materials", {})
        loot_filter.materials = {
            int(material): value for material, value in materials.items()}

        return loot_filter
