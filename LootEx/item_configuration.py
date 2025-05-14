from LootEx.Data import IntRange
from LootEx.item_actions import ItemAction, ItemActions, LootItemMode
from Py4GWCoreLib import *


class ConfigurationCondition:
    def __init__(self, name: str = "New Condition"):
        self.name: str = name
        self.item_type: Optional[ItemType] = None
        self.damage_range: Optional[IntRange] = None
        self.requirements: Optional[dict[Attribute, IntRange]] = None

        self.prefix_mod: Optional[str] = None
        self.suffix_mod: Optional[str] = None
        self.inherent_mod: Optional[str] = None
        self.old_school_only: bool = False

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
            "model_id": data.model_id.name if data.model_id else None,
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
        model_id = (
            ModelID[data["model_id"]]
            if data["model_id"] in ModelID.__members__
            else None
        )

        if model_id is None:
            raise ValueError(f"Invalid model_id: {data['model_id']}")

        item = ItemConfiguration(model_id)
        item.conditions = []

        for condition_data in data["conditions"]:
            condition = ConfigurationCondition(condition_data["name"])
            condition.item_type = (
                ItemType[condition_data["item_type"]]
                if condition_data["item_type"] in ItemType.__members__
                else None
            )
            condition.damage_range = (
                IntRange(
                    condition_data["damage_range"][0], condition_data["damage_range"][1]
                )
                if condition_data["damage_range"]
                else None
            )
            condition.prefix_mod = condition_data["prefix_mod"]
            condition.suffix_mod = condition_data["suffix_mod"]
            condition.inherent_mod = condition_data["inherent_mod"]
            condition.old_school_only = condition_data["old_school_only"]
            condition.rarities = {
                Rarity[rarity]: value
                for rarity, value in condition_data["rarities"].items()
                if rarity in Rarity.__members__
            }
            condition.item_actions = ItemActions.from_dict(
                condition_data["item_actions"]
            )

            condition.requirements = (
                {
                    Attribute[attribute]: IntRange(
                        requirement[0], requirement[1])
                    for attribute, requirement in condition_data[
                        "requirements"
                    ].items()
                    if attribute in Attribute.__members__
                }
                if condition_data["requirements"]
                else None
            )

            item.conditions.append(condition)

        return item
