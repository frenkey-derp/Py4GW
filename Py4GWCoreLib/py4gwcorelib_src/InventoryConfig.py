from enum import Enum, IntEnum

from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity


class ItemEntry:
    ''' Represents a single item entry in the item data we've collected and provide as json. It's a dummy class for now. '''
    def __init__(self, item_model_id: int = 0, item_type: ItemType = ItemType.Unknown, name: str = "", level: int = 0):
        self.item_model_id: int = item_model_id
        self.item_type: ItemType = item_type
        self.name: str = name
        self.level: int = level
    pass

class ItemData:
    ''' Represents the collection of item data we've gathered and stored as json. It's a singleton class. '''
    instance = None
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(ItemData, cls).__new__(cls)
            cls.instance.__init__()
        
        return cls.instance
    
    def __init__(self):
        self.items: dict[ItemType, dict[int, ItemEntry]] = {}

    def GetItemData(self, item_model_id: int, item_type: ItemType = ItemType.Unknown) -> ItemEntry | None:
        if item_type in self.items:
            if item_model_id in self.items[item_type]:
                return self.items[item_type][item_model_id]


class ItemAction(IntEnum):
    ''' Represents the action to take on an item '''
    NONE = 0
    # Salvage the item for common materials (with lesser kit)
    SalvageCommonMaterial = 1
    # Salvage the item for rare materials (with expert kit)
    SalvageRareMaterial = 2
    ExtractPrefix = 3  # Extract the prefix mod of the item
    ExtractInherent = 4  # Extract the inherent/inscription mod of the item
    ExtractSuffix = 5  # Extract the suffix mod of the item
    Hold = 6  # Do nothing but keep the item in place
    Sell = 7  # Sell the item
    Deposit = 8  # Deposit the item in the xunlai stash
    Destroy = 9  # Destory the item
    Loot = 10  # Loot the item
    # ... Add more actions as needed

class InherentModType(IntEnum):
    Any = 0
    Old_School = 1
    Inscribable = 2


class ItemModel:
    ItemData = ItemData()  # Static cache of item data for all item models which allows us to get data from our ItemData class

    def __init__(self, model_id: int | list[int] = 0, item_type: ItemType = ItemType.Unknown):
        self.model_ids: list[int] = model_id if isinstance(model_id, list) else [
            model_id]
        self.item_type: ItemType = item_type

    @property
    def Name(self) -> str:
        ''' Returns the actual item name ("Bone Dragon Staff" instead of "Bone_Dragon_Staff") of the item model from the ItemData. '''
        
        model_ids = len(self.model_ids)
        if model_ids == 1:
            item_data = self.ItemData.GetItemData(
                self.model_ids[0], self.item_type)

            if item_data:
                return item_data.name

            return f"Unknown Model {self.model_ids[0]}"

        elif model_ids > 1:
            for model_id in self.model_ids:
                item_data = self.ItemData.GetItemData(model_id, self.item_type)

                if item_data:
                    return item_data.name

        return f"Unknown Item"

    def __eq__(self, value):
        ''' Compares the item model with another item model, item type or item model id to make it really convienient when checking against those. '''
        match value:
            case None:
                return False
            case _ if isinstance(value, ItemModel):
                return self.model_ids == value.model_ids and self.item_type == value.item_type

            case _ if isinstance(value, int):
                return value in self.model_ids

            case _ if isinstance(value, ItemType):
                return value == self.item_type

        return False

    def MatchesItemId(self, item_id: int) -> bool:
        model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
        item_type, _ = GLOBAL_CACHE.Item.GetItemType(item_id)
        item_type = ItemType(
            item_type) if item_type in ItemType._value2member_map_ else ItemType.Unknown

        return model_id in self.model_ids and item_type == self.item_type

class ItemModels(Enum):  # Container
    NONE = ItemModel(0, ItemType.Unknown)
    Voltaic_Spear = ItemModel(2071, ItemType.Spear)
    Bone_Dragon_Staff = ItemModel([i for i in range(1987, 2008)], ItemType.Staff)
    Earth_Staff = ItemModel([595, 602, 603, 605, 607], ItemType.Staff)
    Earth_Staff_Metal = ItemModel([885, 1288], ItemType.Staff)
    # Add all other item models as we collect them ...


#region Rules
class InventoryRule:
    ''' Base class for all inventory rules. 
        Override Matches, to_dict and load_from_dict in subclasses.'''
    def __init__(self, item_action: ItemAction = ItemAction.NONE):
        self.action: ItemAction = item_action

    def Matches(self, item_id: int) -> bool:
        ''' Override in subclasses '''
        return False

    def to_dict(self) -> dict:
        ''' Override in subclasses '''
        return {
            "action": self.action.name,
        }

    def load_from_dict(self, data: dict):
        ''' Override in subclasses '''
        action = ItemAction[data.get("action", ItemAction.NONE.name)]
        self.action = action

class ItemModelRule(InventoryRule):
    ''' Rule that matches specific item models and optionally rarities. '''
    def __init__(self, item_action: ItemAction = ItemAction.NONE, item_model: ItemModels = ItemModels.NONE, rarities: dict[Rarity, bool] = {}):
        super().__init__(item_action=item_action)
        self.item_model: ItemModels = item_model
        self.rarities: dict[Rarity, bool] = rarities

    def Matches(self, item_id: int) -> bool:
        if self.item_model and self.item_model.value.MatchesItemId(item_id):
            if self.rarities:
                rarity = GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)
                rarity = Rarity(
                    rarity) if rarity in Rarity._value2member_map_ else None

                if not rarity:
                    return False

                return self.rarities.get(rarity, False)

            else:
                return True

        return False

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "item_model": self.item_model.name,
            "rarities": [rarity.name for rarity, enabled in self.rarities.items() if enabled]
        })
        return data

    def load_from_dict(self, data: dict):
        super().load_from_dict(data)

        item_model_name = data.get("item_model", ItemModels.NONE.name)
        self.item_model = ItemModels[item_model_name] if item_model_name in ItemModels.__members__ else ItemModels.NONE
        self.rarities = {Rarity[rarity_name]: True for rarity_name in data.get(
            "rarities", []) if rarity_name in Rarity.__members__}

class ItemTypeRule(InventoryRule):
    ''' Rule that matches item types and optionally rarities. '''
    def __init__(self, item_action: ItemAction = ItemAction.NONE, item_types: list[ItemType] = [], rarities: list[Rarity] = []):
        super().__init__(item_action=item_action)
        self.item_type: dict[ItemType, bool] = {
            item_type: True for item_type in item_types}
        self.rarities: dict[Rarity, bool] = {
            rarity: True for rarity in rarities}

    def Matches(self, item_id: int) -> bool:
        item_type, _ = GLOBAL_CACHE.Item.GetItemType(item_id)
        item_type = ItemType(
            item_type) if item_type in ItemType._value2member_map_ else ItemType.Unknown

        if self.item_type.get(item_type, False):
            if self.rarities:
                rarity = GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)
                rarity = Rarity(
                    rarity) if rarity in Rarity._value2member_map_ else None

                if not rarity:
                    return False

                return self.rarities.get(rarity, False)
            else:
                return True

        return False

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "item_type": [item.name for item, enabled in self.item_type.items() if enabled],
            "rarities": [rarity.name for rarity, enabled in self.rarities.items() if enabled]
        })
        return data

    def load_from_dict(self, data: dict):
        super().load_from_dict(data)

        self.item_type = {ItemType[item_name]: True for item_name in data.get(
            "item_type", []) if item_name in ItemType.__members__}
        self.rarities = {Rarity[rarity_name]: True for rarity_name in data.get(
            "rarities", []) if rarity_name in Rarity.__members__}

class WeaponRule(ItemTypeRule):
    ''' Rule that matches weapon item types and optionally rarities, requirements and mods. '''
    def __init__(self, item_action: ItemAction = ItemAction.NONE):
        super().__init__(item_action=item_action)

        self.requirements: dict[int, tuple[int, int]] = {}
        self.mods: dict[str, tuple[int, int]] = {}
        self.mods_type: InherentModType = InherentModType.Any

    def Matches(self, item_id: int) -> bool:
        if not super().Matches(item_id):
            return False

        return True
#endregion

class InventoryConfig:
    ''' Singleton class that holds all inventory rules and provides methods to get the action for a given item id.
    Can be serialized to/from a dictionary for easy saving/loading.
    '''
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(InventoryConfig, cls).__new__(cls)
            cls.instance.__init__()

        return cls.instance

    def __init__(self):
        self.item_model_rules: list[ItemModelRule] = []
        self.item_type_rules: list[ItemTypeRule] = []
        self.weapon_rules: list[WeaponRule] = []

    def GetItemAction(self, item_id: int) -> ItemAction:
        for rule in [self.item_model_rules, self.item_type_rules, self.weapon_rules]:
            if rule.Matches(item_id):
                return rule.action

        return ItemAction.NONE

    def AddItemModel(self, item_model: ItemModels, action: ItemAction):
        rule = ItemModelRule()
        rule.item_model = item_model
        rule.action = action
        self.item_model_rules.append(rule)

    def add_rule(self, rule: InventoryRule):
        match rule:
            case ItemModelRule():
                self.item_model_rules.append(rule)
            case ItemTypeRule():
                self.item_type_rules.append(rule)
            case WeaponRule():
                self.weapon_rules.append(rule)
            case _:
                raise ValueError(f"Unsupported rule type: {type(rule)}")

    def remove_rule(self, rule: InventoryRule):
        match rule:
            case ItemModelRule():
                if rule in self.item_model_rules:
                    self.item_model_rules.remove(rule)
            case ItemTypeRule():
                if rule in self.item_type_rules:
                    self.item_type_rules.remove(rule)
            case WeaponRule():
                if rule in self.weapon_rules:
                    self.weapon_rules.remove(rule)
            case _:
                raise ValueError(f"Unsupported rule type: {type(rule)}")

    def to_dict(self) -> dict:
        return {
            "item_model_rules": [rule.to_dict() for rule in self.item_model_rules],
            "item_type_rules": [rule.to_dict() for rule in self.item_type_rules],
            "weapon_rules": [rule.to_dict() for rule in self.weapon_rules],
        }
        
    def load_from_dict(self, data: dict):
        self.item_model_rules = []
        self.item_type_rules = []
        self.weapon_rules = []
        
        for rule_data in data.get("item_model_rules", []):
            rule = ItemModelRule()
            rule.load_from_dict(rule_data)
            self.item_model_rules.append(rule)
            
        for rule_data in data.get("item_type_rules", []):
            rule = ItemTypeRule()
            rule.load_from_dict(rule_data)
            self.item_type_rules.append(rule)
            
        for rule_data in data.get("weapon_rules", []):
            rule = WeaponRule()
            rule.load_from_dict(rule_data)
            self.weapon_rules.append(rule)


#### Usage Examples

# Add a rule to salvage all white/blue axes, swords and daggers for common materials
InventoryConfig().add_rule(ItemTypeRule(
    item_action=ItemAction.SalvageCommonMaterial,
    item_types=[ItemType.Axe, ItemType.Sword, ItemType.Daggers],
    rarities=[Rarity.White, Rarity.Blue]))

# Add a rule to sell all gold axes
InventoryConfig().add_rule(ItemTypeRule(
    item_action=ItemAction.Sell,
    item_types=[ItemType.Axe],
    rarities=[Rarity.Gold]))

# Add a rule to deposit voltaic spears
InventoryConfig().AddItemModel(ItemModels.Voltaic_Spear, ItemAction.Deposit)

# Alternative way to add a rule to deposit voltaic spears
InventoryConfig().add_rule(ItemModelRule(
    item_action=ItemAction.Deposit,
    item_model=ItemModels.Bone_Dragon_Staff
))