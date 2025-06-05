from LootEx.item_actions import ItemAction, ItemActions
from LootEx import models
from Py4GWCoreLib import *

import importlib
importlib.reload(models)

class ConfigurationCondition:
    def __init__(self, name: str = "New Condition"):
        self.name: str = name
        self.item_type: Optional[ItemType] = None
        self.damage_range: Optional[models.IntRange] = None
        self.requirements: Optional[dict[Attribute, models.IntRange]] = None

        self.prefix_mod: Optional[str] = None
        self.suffix_mod: Optional[str] = None
        self.inherent_mod: Optional[str] = None
        self.old_school_only: bool = False
        self.threshold: Optional[int] = None

        self.rarities: dict[Rarity, bool] = {
            rarity: False for rarity in Rarity}

        self.item_actions: ItemActions = ItemActions(ItemAction.STASH, ItemAction.STASH)


class ItemConfiguration:
    def __init__(self, model_id: int):
        self.model_id: int = model_id
        default_condition = ConfigurationCondition("Default")

        self.conditions: list[ConfigurationCondition] = [default_condition]

    @staticmethod
    def to_dict(data) -> dict:
        return {
            "model_id": data.model_id,
            "conditions": [
                {
                    "name": condition.name,
                    "item_type": condition.item_type.name if condition.item_type else None,
                    "damage_range": (condition.damage_range.min, condition.damage_range.max)
                    if condition.damage_range
                    else None,
                    "prefix_mod": condition.prefix_mod,
                    "suffix_mod": condition.suffix_mod,
                    "inherent_mod": condition.inherent_mod,
                    "old_school_only": condition.old_school_only,
                    "threshold": condition.threshold,
                    "rarities": {
                        rarity.name: value for rarity, value in condition.rarities.items()
                    },
                    "item_actions": ItemActions.to_dict(condition.item_actions),
                    "requirements": {
                        attribute.name: (requirement.min, requirement.max)
                        for attribute, requirement in condition.requirements.items()
                    }
                    if condition.requirements
                    else None,
                }
                for condition in data.conditions
            ],
        }

    @staticmethod
    def from_dict(data) -> "ItemConfiguration":
        model_id = data["model_id"]

        item = ItemConfiguration(model_id)
        item.conditions = []

        for condition_data in data.get("conditions", []):
            name = condition_data.get("name", None)
            
            if not name:
                raise ValueError("Condition name is required")
            
            condition = ConfigurationCondition(name)
            
            item_type = condition_data.get("item_type", None)
            item_type = (
                ItemType[item_type]
                if item_type in ItemType.__members__
                else None
            )
            
            condition.item_type = item_type
            
            damage_range = condition_data.get("damage_range", None)
            damage_range = (
                models.IntRange(
                    condition_data["damage_range"][0], condition_data["damage_range"][1]
                )
                if condition_data["damage_range"]
                else None
            )
            
            condition.damage_range = damage_range
            condition.prefix_mod = condition_data.get("prefix_mod", None)
            condition.suffix_mod = condition_data.get("suffix_mod", None)
            condition.inherent_mod = condition_data.get("inherent_mod", None)
            condition.old_school_only = condition_data.get("old_school_only", False)
            condition.threshold = condition_data.get("threshold", None)
            
            rarities = condition_data.get("rarities", {})
            rarities = {
                Rarity[rarity]: value
                for rarity, value in rarities.items()
                if rarity in Rarity.__members__
            } if rarities else {}
            
            condition.rarities = rarities
            condition.item_actions = ItemActions.from_dict(condition_data.get("item_actions", {}))

            requirements = condition_data.get("requirements", {})
            requirements = (
                {
                    Attribute[attribute]: models.IntRange(
                        requirement[0], requirement[1])
                    for attribute, requirement in requirements.items()
                    if attribute in Attribute.__members__
                }
                if requirements
                else None
            )
            condition.requirements = requirements
            item.conditions.append(condition)

        return item
