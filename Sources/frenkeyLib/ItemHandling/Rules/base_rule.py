from Py4GWCoreLib.enums_src.GameData_enums import DyeColor
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE
from Sources.frenkeyLib.ItemHandling.Items.ItemData import DAMAGE_RANGES
from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot
from Sources.frenkeyLib.ItemHandling.Mods.properties import DamagePlusEnchanted, DamagePlusHexed, DamagePlusStance, DamagePlusVsHexed, DamagePlusWhileDown, DamagePlusWhileUp, ItemProperty
from Sources.frenkeyLib.ItemHandling.Mods.upgrades import Upgrade
from Sources.frenkeyLib.ItemHandling.Rules.types import ItemAction


class BaseRule:
    def __init__(self, name: str):
        self.name = name
        self.action : ItemAction = ItemAction.NONE
    
    def is_valid(self) -> bool:
        return self.action != ItemAction.NONE
    
    def applies(self, item_id: int) -> bool:
        raise NotImplementedError("Subclasses must implement the applies method.")
    
    def get_item(self, item_id: int) -> ItemSnapshot:
        return ITEM_CACHE.get_item_snapshot(item_id)

class ModelIdRule(BaseRule):
    """
    ***CAUTION***: This rule is ***not recommended*** for general use, as model IDs can be shared between different items and item types!
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        self.model_id : ModelID
    
    def is_valid(self) -> bool:
        return super().is_valid() and self.model_id is not None
    
    def applies(self, item_id):
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return item.model_id == self.model_id.value

class ItemTypesRule(BaseRule):
    """
    A rule that checks if an item :class:`ItemType` is a specified item type. 
    """
    def __init__(self, name: str):
        super().__init__(name)
        
        self.item_types : list[ItemType] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.item_types) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return item.item_type in self.item_types
    
class RaritiesRule(BaseRule):
    """
    A rule that checks if an item :class:`Rarity` is a specified rarity.
    """
    def __init__(self, name: str):
        super().__init__(name)
        
        self.rarities : list[Rarity] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.rarities) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return item.rarity in self.rarities

class DyesRule(BaseRule):
    """
    A rule if an item is a **Vial of Dye** of a specific :class:`DyeColor`. This is determined by the item's dye color
    """
    def __init__(self, name: str):
        super().__init__(name)
        
        self.dye_colors : list[DyeColor] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.dye_colors) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return item.color in self.dye_colors and item.item_type == ItemType.Dye

class ItemSkinRule(BaseRule):
    """
    A rule that checks if an item has a specific skin.

    This is determined by the item's skin property, which is derived
    from the item data in :file:`items.json`.

    See the raw file at `Sources/frenkeyLib/ItemHandling/Items/items.json`
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        self.item_skins : list[str] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.item_skins) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return item.data is not None and item.data.skin in self.item_skins

class ItemTypeAndRarityRule(BaseRule):
    """
    A rule that checks if an item is a specific item type and rarity.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        self.item_types : list[ItemType] = []
        self.rarities : list[Rarity] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.item_types) > 0 and len(self.rarities) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return item.item_type in self.item_types and item.rarity in self.rarities
    
class WeaponSkinRule(BaseRule):
    """
    A rule that checks if a weapon has a specific skin. This is determined by the item's skin property, which is derived from the item data in :file:`items.json`.
    \nIn addition, the rule can check if the item's requirement is within a specified range and if the item's damage range is within a certain range.
    """
        
    def __init__(self, name: str):
        super().__init__(name)
        
        self.weapon_skins : list[str] = []
        self.requirement_min : int = 0
        self.requirement_max : int = 0
        self.only_max_damage : bool = True
        
        self.properties : list[ItemProperty] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.weapon_skins) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        if item.data is None or item.data.skin not in self.weapon_skins:
            return False
        
        if self.requirement_min > item.requirement or self.requirement_max < item.requirement:
            return False
        
        if self.only_max_damage:
            damage_for_requirement = DAMAGE_RANGES.get(item.item_type, {}).get(item.model_id, (0, 0))
            
            if item.max_damage < damage_for_requirement[1] or item.min_damage < damage_for_requirement[0]:
                return False
        
        #TODO: Create some proper check against properties so we can check for specific properties like "Damage +X while hexed" or "Damage +X vs hexed"
        if len(self.properties) > 0:
            item_properties = {type(p): p for p in item.properties}
            for prop in self.properties:
                if type(prop) not in item_properties:
                    return False
                
                item_prop = item_properties[type(prop)]
                if prop.modifier.arg != item_prop.modifier.arg:
                    return False
        
        return True            

class WeaponTypeRule(BaseRule):
    """
    A rule that checks if an item is a specific weapon type, requirement, damage range and specific properties
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        self.item_type : ItemType
        self.requirement_min : int = 0
        self.requirement_max : int = 0
        self.only_max_damage : bool = True
        
        self.properties : list[ItemProperty] = []
    
    def is_valid(self) -> bool:
        return super().is_valid() and self.item_type is not None
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        if item.data is None or item.item_type != self.item_type:
            return False
        
        if self.requirement_min > item.requirement or self.requirement_max < item.requirement:
            return False
        
        if self.only_max_damage:
            damage_for_requirement = DAMAGE_RANGES.get(item.item_type, {}).get(item.model_id, (0, 0))
            
            if item.max_damage < damage_for_requirement[1] or item.min_damage < damage_for_requirement[0]:
                return False
        
        #TODO: Create some proper check against properties so we can check for specific properties like "Damage +X while hexed" or "Damage +X vs hexed"
        if len(self.properties) > 0:
            item_properties = {type(p): p for p in item.properties}
            for prop in self.properties:
                if type(prop) not in item_properties:
                    return False
                
                item_prop = item_properties[type(prop)]
                if prop.modifier.arg != item_prop.modifier.arg:
                    return False
        
        return True
    
class UpgradeRule(BaseRule):
    """
    A rule that checks if an item has a specific upgrade. This is determined by the item's properties, which are derived from the item's modifiers.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        self.upgrade : Upgrade
    
    def is_valid(self) -> bool:
        return super().is_valid() and self.upgrade is not None
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item = self.get_item(item_id)
        return self.upgrade in [item.prefix, item.suffix, item.inscription]