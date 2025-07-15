from Widgets.frenkey.LootEx import models, enum
from Widgets.frenkey.LootEx.enum import ItemAction
from Py4GWCoreLib import *

import importlib
importlib.reload(models)

class LowReqRule:
    def __init__(self, item_type: ItemType):
        self.item_type: ItemType = item_type
        self.requirements: dict[int, models.IntRange] = {}
        self.mods: dict[str, models.ModInfo] = {}
        self.mods_type: enum.ActionModsType = enum.ActionModsType.Any
        
    def to_dict(self) -> dict:
        return {
            "item_type": self.item_type.name,
            "mods_type": self.mods_type.name,
            "requirements": {
                req: (damage_range.min, damage_range.max) for req, damage_range in self.requirements.items()
            },
            "mods": {
                mod_id: mod.to_dict() for mod_id, mod in self.mods.items()
            },
        }
        
    @staticmethod
    def from_dict(data: dict) -> "LowReqRule":
        item_type = ItemType[data["item_type"]]
        
        rule = LowReqRule(item_type)
        rule.mods_type = enum.ActionModsType[data.get("mods_type", "Any")]
        
        for req, (min_value, max_value) in data.get("requirements", {}).items():
            rule.requirements[int(req)] = models.IntRange(min_value, max_value)
            
        for mod_id, mod_data in data.get("mods", {}).items():
            rule.mods[mod_id] = models.ModInfo.from_dict(mod_data)
        
        
        return rule
    
    def add_mod(self, mod: models.ItemMod):
        if mod.identifier not in self.mods:
            self.mods[mod.identifier] = models.ModInfo(mod)
        else:
            existing_mod = self.mods[mod.identifier]
            modifier_range = mod.get_modifier_range()
            existing_mod.min = modifier_range.max
            existing_mod.max = modifier_range.max
            
    def remove_mod(self, mod: models.ItemMod):
        if mod.identifier in self.mods:
            del self.mods[mod.identifier]