
from typing import override

from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity

from Widgets.ItemHandlersRework.ItemCache import ITEM_CACHE
from Widgets.ItemHandlersRework.types import ItemAction, RuleType

class test:
    def __init__(self):
        self.rules : list[RuleInterface] = []
    
    
    def to_dict(self) -> dict:
        return {
            "rules": [rule.to_dict() for rule in self.rules]
        }
        
    def load_from_dict(self, data: dict):
        rules_data = data.get("rules", [])
        self.rules = [RuleInterface.from_dict(rule_data) for rule_data in rules_data]
       
class Rarities:
    def __init__(self):
        self.White = True
        self.Blue = True
        self.Purple = True
        self.Gold = True
        self.Green = True
    
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
    
class RuleInterface:
    def __init__(self):
        self.action = ItemAction.NONE
        self.type = RuleType.NONE
    
    @property
    def Action(self) -> ItemAction:
        return self.action
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.name,
            "action": self.action.name
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        rule_type_str = data.get("type", "NONE")
        
        rule_type = RuleType[rule_type_str]
        
        match rule_type:
            case RuleType.ByItemType:
                return ByItemTypeRule.from_dict(data)
            
            case RuleType.ByModelId:    
                return ByModelIdRule.from_dict(data)
            
            case RuleType.BySkin:
                return BySkinRule.from_dict(data)
            
            case RuleType.WeaponMod:
                return WeaponModRule.from_dict(data)
            
        
        return cls()
        
    def IsMatch(self, item_id) -> bool:
        ''' Method to check if the rule matches the given item ID. '''
        raise NotImplementedError("IsMatch method must be implemented by subclasses.")
        
class ByItemTypeRule(RuleInterface):
    def __init__(self, action: ItemAction = ItemAction.NONE, item_type: ItemType = ItemType.Unknown, rarities: Rarities = Rarities()):
        super().__init__()
        
        self.type = RuleType.ByItemType
        self.action = action
        self.item_type : ItemType = item_type
        
        self.rarities : Rarities = rarities
    
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "item_type": self.item_type.name,
            "rarities": self.rarities.to_dict()
        })
        return data
    
    @override
    @classmethod
    def from_dict(cls, data: dict):
        item_type_str = data.get("item_type", "Unknown")
        item_type = ItemType[item_type_str]
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
        
        action_str = data.get("action", "NONE")
        action = ItemAction[action_str]
        
        return cls(action=action, item_type=item_type, rarities=rarities)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return item.base.item_type == self.item_type and self.rarities.HasRarity(item.base.rarity)
        
class ByModelIdRule(RuleInterface):
    def __init__(self, action: ItemAction = ItemAction.NONE, item_type: ItemType = ItemType.Unknown, model_id: int = 0, rarities: Rarities = Rarities()):
        super().__init__()
        
        self.type = RuleType.ByModelId
        self.action = action
        self.item_type : ItemType = item_type
        self.model_id : int = model_id
        
        self.rarities : Rarities = rarities
    
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "item_type": self.item_type.name,
            "model_id": self.model_id,
            "rarities": self.rarities.to_dict()
        })
        return data
    
    @override
    @classmethod
    def from_dict(cls, data: dict):
        item_type_str = data.get("item_type", "Unknown")
        item_type = ItemType[item_type_str]
        
        model_id = data.get("model_id", 0)
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
        
        action_str = data.get("action", "NONE")
        action = ItemAction[action_str]
        
        return cls(action=action, item_type=item_type, model_id=model_id, rarities=rarities)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        if item is None:
            return False
        
        return item.base.model_id == self.model_id and item.base.item_type == self.item_type and self.rarities.HasRarity(item.base.rarity)
    
class BySkinRule(RuleInterface):
    def __init__(self, action: ItemAction = ItemAction.NONE, skin_id: str = "", rarities: Rarities = Rarities()):
        super().__init__()
        
        self.type = RuleType.BySkin
        self.action = action
        self.skin_name : str = skin_id
        self.rarities : Rarities = rarities
    
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "skin_name": self.skin_name,
            "rarities": self.rarities.to_dict()
        })
        return data
    
    @override
    @classmethod
    def from_dict(cls, data: dict):
        skin_name = data.get("skin_name", "")
        
        rarities_data = data.get("rarities", {})
        rarities = Rarities.from_dict(rarities_data)
        
        action_str = data.get("action", "NONE")
        action = ItemAction[action_str]
        
        return cls(action=action, skin_id=skin_name, rarities=rarities)

    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return self.skin_name == item.derived.skin and self.rarities.HasRarity(item.base.rarity)

class WeaponModRule(RuleInterface):
    def __init__(self, action: ItemAction = ItemAction.NONE):
        super().__init__()
        
        self.type = RuleType.WeaponMod
        self.action = action        
    
    @override
    def to_dict(self) -> dict:
        data = super().to_dict()
        return data
    
    @override
    @classmethod
    def from_dict(cls, data: dict):
        action_str = data.get("action", "NONE")
        action = ItemAction[action_str]
        
        return cls(action=action)
    
    def IsMatch(self, item_id) -> bool:
        item = ITEM_CACHE.GetItem(item_id)
        
        if item is None:
            return False
        
        return False