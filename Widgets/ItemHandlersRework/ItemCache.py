from dataclasses import dataclass
from typing import Optional

from PyItem import DyeInfo, ItemModifier, PyItem
from Py4GWCoreLib.Item import Item
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, DyeColor, Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog

from Widgets.ItemHandlersRework.Helpers import IsArmorType, IsWeaponType
from Widgets.ItemHandlersRework.Mods import Rune, WeaponUpgrade
from Widgets.ItemHandlersRework.types import ModType

@dataclass(slots=True)
class ItemBase:
    item_id: int
    model_id: int
    model_file_id: int
    item_type: ItemType
    rarity: Rarity
    
    profession: Profession
    is_stackable: bool
    is_inscribable: bool
    is_salvageable: bool
    is_useable: bool

    is_weapon: bool
    is_armor: bool
    is_upgrade: bool


    @classmethod
    def from_item(cls, item: PyItem):
        model_id = item.model_id
        model_file_id = item.model_file_id
        
        item_type_value = item.item_type.ToInt()
        item_type = ItemType(item_type_value)
        
        rarity_value = item.rarity.value
        rarity = Rarity(rarity_value)
        
        profession_value = item.profession
        profession = Profession(profession_value) if profession_value in Profession._value2member_map_ else Profession._None
        
        is_stackable = item.is_stackable
        is_inscribable = item.is_inscribable
        is_salvageable = item.is_salvageable
        is_usable = item.is_usable
        
        is_weapon = IsWeaponType(item_type)
        is_armor = IsArmorType(item_type)
        is_upgrade = item_type == ItemType.Rune_Mod
        
        return cls(
            item_id=item.item_id,
            model_id=model_id,
            model_file_id=model_file_id,
            item_type=item_type,
            rarity=rarity,
            profession=profession,
            is_stackable=is_stackable,
            is_inscribable=is_inscribable,
            is_salvageable=is_salvageable,
            is_useable=is_usable,
            is_weapon=is_weapon,
            is_armor=is_armor,
            is_upgrade=is_upgrade
        )

@dataclass(slots=True)
class ItemState:
    quantity: int
    uses: int
    value: int
    slot: int

    is_valid: bool
    is_identified: bool
    is_inventory_item: bool
    is_storage_item: bool
    is_customized: bool

    dye_info: DyeInfo
    modifiers: list[tuple[int, int, int]]  # List of (identifier, arg1, arg2)
    
    runes : Optional[dict[ModType, Rune]] = None 
    max_runes : Optional[dict[ModType, Rune]] = None 
    
    weapon_upgrades : Optional[dict[ModType, WeaponUpgrade]] = None     
    max_weapon_upgrades : Optional[dict[ModType, WeaponUpgrade]] = None

    @classmethod
    def from_item(cls, item: PyItem):
        quantity = item.quantity
        uses = item.uses
        value = item.value
        slot = item.slot

        is_valid = item.IsItemValid(item.item_id)
        is_identified = item.is_identified
        is_inventory_item = item.is_inventory_item
        is_storage_item = item.is_storage_item
        is_customized = item.is_customized

        dye_info = item.dye_info
        modifiers = [
            (modifier.GetIdentifier(), modifier.GetArg1(), modifier.GetArg2())
            for modifier in item.modifiers if modifier is not None
        ]
        
        contained_runes = Rune.get_from_modifiers(modifiers)
        runes = {rune.mod_type: rune for rune in contained_runes} if contained_runes else {}        
        max_runes = {mod_type: rune for mod_type, rune in runes.items() if rune.is_maxed} if runes else {}
        
        item_type = ItemType(item.item_type.ToInt())
        contained_weapon_upgrades = WeaponUpgrade.get_from_modifiers(modifiers, item_type, item.model_id)      
          
        weapon_upgrades = {upgrade.mod_type: upgrade for upgrade in contained_weapon_upgrades} if contained_weapon_upgrades else {}
        max_weapon_upgrades = {mod_type: upgrade for mod_type, upgrade in weapon_upgrades.items() if upgrade.IsMaxed} if weapon_upgrades else {}
        
        return cls(
            quantity=quantity,
            uses=uses,
            value=value,
            slot=slot,
            is_valid=is_valid,
            is_identified=is_identified,
            is_inventory_item=is_inventory_item,
            is_storage_item=is_storage_item,
            is_customized=is_customized,
            dye_info=dye_info,
            modifiers=modifiers,
            runes=runes,
            max_runes=max_runes,
            weapon_upgrades=weapon_upgrades,
            max_weapon_upgrades=max_weapon_upgrades
        )
        
    def update(self, item: PyItem):
        quantity = item.quantity
        uses = item.uses
        value = item.value
        slot = item.slot
        
        is_valid = item.IsItemValid(item.item_id)
        is_identified = item.is_identified
        is_inventory_item = item.is_inventory_item
        is_storage_item = item.is_storage_item
        is_customized = item.is_customized
        
        dye_info = item.dye_info
        
        self.quantity = quantity
        self.uses = uses
        self.value = value
        self.slot = slot
        self.is_valid = is_valid
        self.is_identified = is_identified
        self.is_inventory_item = is_inventory_item
        self.is_storage_item = is_storage_item
        self.is_customized = is_customized
        self.dye_info = dye_info
        self.modifiers = [
            (modifier.GetIdentifier(), modifier.GetArg1(), modifier.GetArg2())
            for modifier in item.modifiers if modifier is not None
        ]
        
        contained_runes = Rune.get_from_modifiers(self.modifiers)
        self.runes = {rune.mod_type: rune for rune in contained_runes} if contained_runes else {}        
        self.max_runes = {mod_type: rune for mod_type, rune in self.runes.items() if rune.is_maxed} if self.runes else {}
        
        item_type = ItemType(item.item_type.ToInt())
        contained_weapon_upgrades = WeaponUpgrade.get_from_modifiers(self.modifiers, item_type, item.model_id)          
          
        self.weapon_upgrades = {upgrade.mod_type: upgrade for upgrade in contained_weapon_upgrades} if contained_weapon_upgrades else {}
        self.max_weapon_upgrades = {mod_type: upgrade for mod_type, upgrade in self.weapon_upgrades.items() if upgrade.IsMaxed} if self.weapon_upgrades else {}
    
@dataclass(slots=True)
class ItemDerived:
    data: object | None
    material: object | None

    color: DyeColor
    skin: str | None

    target_item_type: ItemType
    attribute: Attribute
    requirements: int
    damage: tuple[int, int]
    shield_armor: tuple[int, int]

    is_rune: bool
    has_mods: bool
    is_highly_salvageable: bool
    has_increased_value: bool

    is_rare_weapon: bool
    is_rare_weapon_to_keep: bool

    name: str 
    
    @classmethod
    def from_item(cls, item: PyItem):
        # Placeholder for derived data population
        return cls(
            data=None,
            material=None,
            color=DyeColor.NoColor,
            skin=None,
            target_item_type=ItemType.Unknown,
            attribute=Attribute.None_,
            requirements=0,
            damage=(0, 0),
            shield_armor=(0, 0),
            is_rune=False,
            has_mods=False,
            is_highly_salvageable=False,
            has_increased_value=False,
            is_rare_weapon=False,
            is_rare_weapon_to_keep=False,
            name=""
        )
    
    def update(self, item: PyItem):
        # Placeholder for derived data update
        pass

class ItemView:
    def __init__(self, base: ItemBase, state: ItemState, derived: ItemDerived):
        
        self.id = base.item_id
        self.base = base
        self.state = state
        self.derived = derived
    
    def update(self) -> bool:        
        item_instance = Item.item_instance(self.base.item_id)
        
        if not item_instance.IsItemValid(self.base.item_id):
            return False
        
        self.state.update(item_instance)
        self.derived.update(item_instance)
        return True
    
class ItemCache:    
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(ItemCache, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
        
        self.item_views : dict[int, ItemView] = {}
        self.updated : dict[int, bool] = {}
        
        self.game_state = -1
        self.map_id = -1
    
    def GetItem(self, item_id) -> ItemView | None:        
        item_view = self.item_views.get(item_id, None)
        
        if item_view is not None:
            if not self.updated.get(item_id, False):
                self.updated[item_id] = True
                
                exists = item_view.update()   
                
                if not exists:
                    del self.item_views[item_id]
                    return None
                                 
        else:
            item = Item.item_instance(item_id)
            
            item_base = ItemBase.from_item(item)
            item_state = ItemState.from_item(item)
            item_derived = ItemDerived.from_item(item)
            
            item_view = ItemView(item_base, item_state, item_derived)
            self.item_views[item_id] = item_view
             
        return item_view
    
    def Wipe(self):
        self.item_views.clear()
    
    def Update(self):
        map_id = Map.GetMapID()
        
        if self.map_id != map_id or Map.IsMapLoading():
            self.Wipe()
            self.map_id = map_id
        
        self.updated.clear()
            
        pass
    

ITEM_CACHE = ItemCache()