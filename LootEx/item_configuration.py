from LootEx import models, enum, utility
from LootEx.enum import ItemAction
from Py4GWCoreLib import *

import importlib
importlib.reload(models)

class ConfigurationCondition:
    def __init__(self, name: str = "New Condition", action: ItemAction = ItemAction.STASH):
        self.name: str = name
        self.damage_range: Optional[models.IntRange] = None
        self.requirements: Optional[dict[Attribute, models.IntRange]] = None

        self.prefix_mod: Optional[str] = None
        self.suffix_mod: Optional[str] = None
        self.inherent_mod: Optional[str] = None
        self.old_school_only: bool = False
        self.threshold: Optional[int] = None
        self.keep_in_inventory: int = 0

        self.rarities: dict[Rarity, bool] = {
            rarity: False for rarity in Rarity}

        self.action: ItemAction = action


class ItemConfiguration:
    def __init__(self, model_id: int, action: ItemAction = ItemAction.STASH):
        self.model_id: int = model_id
        self.conditions: list[ConfigurationCondition] = [ConfigurationCondition("Default", action)]

    @staticmethod
    def to_dict(data) -> dict:
        return {
            "model_id": data.model_id,
            "conditions": [
                {
                    "name": condition.name,
                    "keep_in_inventory": condition.keep_in_inventory,
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
                    "action": condition.action.name,
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
            condition.action = ItemAction[condition_data.get("action", "STASH")]
            
            condition.keep_in_inventory = condition_data.get("keep_in_inventory", 0)
            
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

    def get_condition(self, item_id: int) -> Optional[ConfigurationCondition]:
        item_type = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])
        
        #sort the conditions based on their assigned action value 
        sorted_conditions = sorted(self.conditions, key=lambda c: c.action.value)
        
        for condition in sorted_conditions:
            if utility.Util.IsWeaponType(item_type):
                mods = utility.Util.GetMods(item_id)
                
                has_prefix = condition.prefix_mod is None or any(mod.identifier == condition.prefix_mod for mod in mods)
                has_suffix = condition.suffix_mod is None or any(mod.identifier == condition.suffix_mod for mod in mods)
                has_inherent = condition.inherent_mod is None or any(mod.identifier == condition.inherent_mod for mod in mods)
                
                if not (has_prefix and has_suffix and has_inherent):
                    continue
                
                if condition.old_school_only and GLOBAL_CACHE.Item.Customization.IsInscribable(item_id):
                    continue
                
                attribute, requirements = utility.Util.GetItemRequirements(item_id)
                if condition.requirements:
                    if not condition.requirements.get(attribute, None):
                        continue
                    
                    requirement = condition.requirements[attribute]
                    if requirement.min > requirements or requirement.max < requirements:
                        continue
                
                min_dmg, max_dmg = utility.Util.GetItemDamage(item_id)
                if condition.damage_range and (condition.damage_range.min > min_dmg or condition.damage_range.max < max_dmg):
                    continue
                
                rarity = Rarity(GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)[0])
                if rarity not in condition.rarities or not condition.rarities[rarity]:
                    continue
                
                return condition            
            else:
                if condition.action == ItemAction.STASH:
                    amount = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)
                    
                    if amount <= condition.keep_in_inventory:                        
                        continue
                
                return condition
            
        return None
              
    def get_action(self, item_id: int) -> enum.ItemAction:        
        condition = self.get_condition(item_id)
        
        if condition:
            return condition.action
        
        return ItemAction.NONE
        