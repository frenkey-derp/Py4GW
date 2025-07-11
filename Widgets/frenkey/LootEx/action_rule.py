from Widgets.frenkey.LootEx import data, models, enum
from Widgets.frenkey.LootEx.enum import ItemAction
from Py4GWCoreLib import *

import importlib
importlib.reload(models)

class ModInfo:
    def __init__(self, mod : models.ItemMod | None = None):
        self.identifier: str = ""
        self.min: int = 0
        self.max: int = 0
        
        if mod:
            self.identifier = mod.identifier
            modifier_range = mod.get_modifier_range()
            self.min = modifier_range.min
            self.max = modifier_range.max
        
    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "min": self.min,
            "max": self.max
        }
        
    @staticmethod
    def from_dict(data: dict) -> "ModInfo":
        mod = ModInfo()
        
        mod.identifier = data.get("identifier", "")
        mod.min = data.get("min", 0)
        mod.max = data.get("max", 0)
        
        return mod         
    
class RequirementInfo:
    def __init__(self, attribute: Attribute, min_value: int, max_value: int, max_damage_only: bool = False):
        self.attribute: Attribute = attribute
        self.min: int = min_value
        self.max: int = max_value
        self.max_damage_only: bool = False         

    def to_dict(self) -> dict:
        return {
            "attribute": self.attribute.name,
            "min": self.min,
            "max": self.max,
            "max_damage_only": self.max_damage_only
        }

    @staticmethod
    def from_dict(data: dict) -> "RequirementInfo":
        return RequirementInfo(
            Attribute[data["attribute"]],
            data["min"],
            data["max"],
            data.get("max_damage_only", False)
        )

class ItemModelInfo:
    def __init__(self, model_id: int, item_type: ItemType):
        self.model_id: int = model_id
        self.item_type: ItemType = item_type

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "item_type": self.item_type.name
        }

    @staticmethod
    def from_dict(data: dict) -> "ItemModelInfo":
        return ItemModelInfo(
            data["model_id"],
            ItemType[data["item_type"]]
        )

class ActionRule:
    def __init__(self, skin_name: str = "", action: ItemAction = ItemAction.STASH):
        self.skin: str = skin_name
        self.action : ItemAction = action
        self.models: list[ItemModelInfo] = []
        self.rarities: dict[Rarity, bool] = {
            rarity: False for rarity in Rarity
            }
        
        self.requirements: dict[Attribute, RequirementInfo] = {}
        self.mods : dict[str, ModInfo] = {}
    
    def to_dict(self) -> dict:
        return {
            "skin": self.skin,
            "action": self.action.name,
            "model_ids": [model_id.to_dict() for model_id in self.models],
            "rarities": {rarity.name: enabled for rarity, enabled in self.rarities.items()},
            "requirements": {attr.name: req.to_dict() for attr, req in self.requirements.items()},
            "mods": {mod_id: mod.to_dict() for mod_id, mod in self.mods.items()}
        }
        
    @staticmethod
    def from_dict(data: dict) -> "ActionRule":
        rule = ActionRule(
            skin_name=data["skin"],
            action=ItemAction[data["action"]]
        )
        
        rule.models = [
            ItemModelInfo.from_dict(model_id) for model_id in data.get("model_ids", [])
        ]
        rule.rarities = {Rarity[rarity]: enabled for rarity, enabled in data.get("rarities", {}).items()}
        
        for attr_name, req_data in data.get("requirements", {}).items():
            rule.requirements[Attribute[attr_name]] = RequirementInfo.from_dict(req_data)
        
        for mod_id, mod_data in data.get("mods", {}).items():
            rule.mods[mod_id] = ModInfo.from_dict(mod_data)
        
        return rule
    
    def get_items(self):                            
        if not self.models:
            items = [item for item in data.Items.All if item.inventory_icon == self.skin]
        else:                
            items = [item for model in self.models if (item := data.Items.get_item(model.item_type, model.model_id)) is not None]
        
        return items
