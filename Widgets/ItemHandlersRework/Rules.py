
from dataclasses import dataclass, field
from typing import ClassVar, Type, override

from Py4GWCoreLib.enums_src.GameData_enums import DyeColor
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity

from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Widgets.ItemHandlersRework.ItemCache import ITEM_CACHE
from Widgets.ItemHandlersRework.types import InherentSlotType, ItemAction, RuleType
       
@dataclass(slots=True)
class Rarities:
    White: bool = True
    Blue: bool = True
    Purple: bool = True
    Gold: bool = True
    Green: bool = True
    
    def HasRarity(self, rarity: Rarity | str) -> bool:
        rarity_str = rarity.name if isinstance(rarity, Rarity) else str(rarity)
        return getattr(self, rarity_str, False)
    
    def to_dict(self) -> dict:
        return {
            "White": self.White,
            "Blue": self.Blue,
            "Purple": self.Purple,
            "Gold": self.Gold,
            "Green": self.Green
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        rarities = cls()
        rarities.White = data.get("White", True)
        rarities.Blue = data.get("Blue", True)
        rarities.Purple = data.get("Purple", True)
        rarities.Gold = data.get("Gold", True)
        rarities.Green = data.get("Green", True)
        return rarities

@dataclass(slots=True)
class ModInfo:
    identifier: str = ""
    min: int = 0
    max: int = 0
    
    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "min": self.min,
            "max": self.max
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        mod_info = cls()
        mod_info.identifier = data.get("identifier", "")
        mod_info.min = data.get("min", 0)
        mod_info.max = data.get("max", 0)
        return mod_info
        
@dataclass(slots=True)
class RuleInterface:
    name: str
    action: ItemAction
    
    RULE_TYPE: ClassVar[RuleType] = RuleType.NONE
    _registry: ClassVar[dict[RuleType, Type["RuleInterface"]]] = {}
        
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.RULE_TYPE.name,
            "action": self.action.name
        }
        
    @classmethod
    def register(cls, rule_type: RuleType):
        def decorator(subclass):
            subclass.RULE_TYPE = rule_type
            cls._registry[rule_type] = subclass
            return subclass
        return decorator

    @classmethod
    def from_dict(cls, data: dict):
        rule_type = RuleType[data.get("type", RuleType.NONE.name)]
        rule_cls = cls._registry.get(rule_type, cls)
        return rule_cls._from_dict_internal(data)

    @classmethod
    def _from_dict_internal(cls, data: dict):
        return cls(
            name=data.get("name", "Unnamed Rule"),
            action=ItemAction[data.get("action", ItemAction.NONE.name)],
        )
    
    def IsMatch(self, item_id) -> bool:
        ''' Method to check if the rule matches the given item ID. '''
        raise NotImplementedError("IsMatch method must be implemented by subclasses.")

@RuleInterface.register(RuleType.Dye)
@dataclass(slots=True)
class DyeRule(RuleInterface):
    dye_colors : dict[DyeColor, bool] = field(default_factory=lambda: {dye_color: True for dye_color in DyeColor})
        
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "dye_colors": {dye_color.name: enabled for dye_color, enabled in self.dye_colors.items()}
        })
        return data
    
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        dye_colors_data = data.get("dye_colors", {})
        dye_colors = {DyeColor[dye_color_str]: enabled for dye_color_str, enabled in dye_colors_data.items() if dye_color_str in DyeColor.__members__}
                
        return cls(name=name, action=action, dye_colors=dye_colors)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return item.base.model_id == ModelID.Vial_Of_Dye and self.dye_colors.get(item.state.color, False)

@RuleInterface.register(RuleType.ByItemType)
@dataclass(slots=True)
class ByItemTypeRule(RuleInterface):
    item_type : ItemType
    rarities : Rarities = field(default_factory=Rarities)
        
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "item_type": self.item_type.name,
            "rarities": self.rarities.to_dict()
        })
        return data
    
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        item_type_str = data.get("item_type", "Unknown")
        item_type = ItemType[item_type_str]
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        return cls(name=name, action=action, item_type=item_type, rarities=rarities)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return item.base.item_type == self.item_type and self.rarities.HasRarity(item.base.rarity)
        
@RuleInterface.register(RuleType.ByModelId)
@dataclass(slots=True)
class ByModelIdRule(RuleInterface):
    item_type : ItemType
    model_id : int
    
    rarities : Rarities = field(default_factory=Rarities)
    
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "item_type": self.item_type.name,
            "model_id": self.model_id,
            "rarities": self.rarities.to_dict()
        })
        return data
    
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        item_type_str = data.get("item_type", "Unknown")
        item_type = ItemType[item_type_str]
        
        model_id = data.get("model_id", 0)
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
        
        return cls(name=name, action=action, item_type=item_type, model_id=model_id, rarities=rarities)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        if item is None:
            return False
        
        return item.base.model_id == self.model_id and item.base.item_type == self.item_type and self.rarities.HasRarity(item.base.rarity)
    
@RuleInterface.register(RuleType.ByWeaponType)
@dataclass(slots=True)
class ByWeaponTypeRule(RuleInterface):
    weapon_type : ItemType 
    rarities : Rarities = field(default_factory=Rarities)
    
    requirements: dict[int, tuple[int, int]] = field(default_factory=dict)
    
    inherent_slot : InherentSlotType = InherentSlotType.Any
    inherent_mods : dict[str, ModInfo] = field(default_factory=dict)
            
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "weapon_type": self.weapon_type.name,
            "rarities": self.rarities.to_dict(),
            "inherent_slot": self.inherent_slot.name,
            "inherent_mods": {key: mod.to_dict() for key, mod in self.inherent_mods.items()},
            "requirements": {str(req): {"min": val[0], "max": val[1]} for req, val in self.requirements.items()},            
        })
        return data
    
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        weapon_type_str = data.get("weapon_type", ItemType.Unknown.name)
        weapon_type = ItemType[weapon_type_str]
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
                                
        inherent_slot_str = data.get("inherent_slot", InherentSlotType.Any.name)
        inherent_slot = InherentSlotType[inherent_slot_str]
        
        inherent_mods_data = data.get("inherent_mods", {})
        inherent_mods = {key: ModInfo.from_dict(mod) for key, mod in inherent_mods_data.items()}
        
        requirements_data = data.get("requirements", {})
        requirements = {}
        for req, val in requirements_data.items():
            requirements[int(req)] = (val.get("min", 0), val.get("max", 0))
        
        return cls(name=name, action=action, weapon_type=weapon_type, rarities=rarities, requirements=requirements, inherent_slot=inherent_slot, inherent_mods=inherent_mods)

@dataclass(slots=True)
class ByWeaponSkinRule(RuleInterface):
    skin_name : str
    rarities : Rarities = field(default_factory=Rarities)
    
    requirement_range : tuple[int, int] = (9, 9)
    max_damage_only : bool = True
    
    inherent_slot : InherentSlotType = InherentSlotType.Any
    inherent_mods : dict[str, ModInfo] = field(default_factory=dict)
        
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "skin_name": self.skin_name,
            "rarities": self.rarities.to_dict(),
            "requirement_range": {
                "min": self.requirement_range[0],
                "max": self.requirement_range[1]
            },
            "max_damage_only": self.max_damage_only,
            "inherent_slot": self.inherent_slot.name,
            "inherent_mods": {key: mod.to_dict() for key, mod in self.inherent_mods.items()}
        })
        return data
    
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        skin_name = data.get("skin_name", "")
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
                
        requirement_range_data = data.get("requirement_range", {"min": 9, "max": 9})
        requirement_range = (requirement_range_data.get("min", 9), requirement_range_data.get("max", 9))
        
        max_damage_only = data.get("max_damage_only", True)
        
        inherent_slot_str = data.get("inherent_slot", InherentSlotType.Any.name)
        inherent_slot = InherentSlotType[inherent_slot_str]
        
        inherent_mods_data = data.get("inherent_mods", {})
        inherent_mods = {key: ModInfo.from_dict(mod) for key, mod in inherent_mods_data.items()}
        
        return cls(name=name, action=action, skin_name=skin_name, rarities=rarities, requirement_range=requirement_range, max_damage_only=max_damage_only, inherent_slot=inherent_slot, inherent_mods=inherent_mods)

    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return self.skin_name == item.derived.skin and self.rarities.HasRarity(item.base.rarity)

@RuleInterface.register(RuleType.BySkin)
@dataclass(slots=True)
class BySkinRule(RuleInterface):    
    skin_name : str
    
    rarities : Rarities = field(default_factory=Rarities)

    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "skin_name": self.skin_name,
            "rarities": self.rarities.to_dict()
        })
        return data
    
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        skin_name = data.get("skin_name", "")
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
        
        
        return cls(name=name, action=action, skin_name=skin_name, rarities=rarities)

    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return self.skin_name == item.derived.skin and self.rarities.HasRarity(item.base.rarity)

@RuleInterface.register(RuleType.WeaponMod)
@dataclass(slots=True)
class WeaponModRule(RuleInterface):
    weapon_mod_id : str 
    
    type : RuleType = RuleType.WeaponMod

    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        return data
    
    @override
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        weapon_mod_id = data.get("weapon_mod_id", "")
                
        return cls(name=name, action=action, weapon_mod_id=weapon_mod_id, type=RuleType.WeaponMod)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        if item.state.weapon_mods and item.state.weapon_mods.get(self.weapon_mod_id, None) is not None:
            return True
        
        return False
    
@RuleInterface.register(RuleType.Rune)
@dataclass(slots=True)
class RuneRule(RuleInterface):        
    rune_id : str   
    
    type : RuleType = RuleType.Rune
    
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        return data
    
    @override
    @classmethod
    def _from_dict_internal(cls, data: dict):
        name = data.get("name", "Unnamed Rule")
        action_str = data.get("action", ItemAction.NONE.name)
        action = ItemAction[action_str]
        
        rune_id = data.get("rune_id", "")
                
        return cls(name=name, rune_id=rune_id, action=action, type=RuleType.Rune)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        if item.state.runes and item.state.runes.get(self.rune_id, None) is not None:
            return True
        
        return False