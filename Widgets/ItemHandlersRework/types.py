from enum import IntEnum, auto
import os

import Py4GW
from Py4GWCoreLib.enums_src.Item_enums import ItemType


ITEM_TEXTURES_PATH = os.path.join(Py4GW.Console.get_projects_path(), "Textures", "Items")
MISSING_TEXTURE_PATH = os.path.join(Py4GW.Console.get_projects_path(), "Textures", "missing_texture.png")

class MaterialType(IntEnum):
    None_ = 0
    Common = 1
    Rare = 2

class ItemCategory(IntEnum):
    None_ = 0
    Sweet = 1
    Party = 2
    Alcohol = 3
    DeathPenaltyRemoval = 4
    Scroll = 5
    Tome = 6
    Key = 7
    Material = 8
    Trophy = 9
    RewardTrophy = 10
    QuestItem = 11
    RareWeapon = 12
        
class ItemSubCategory(IntEnum):
    None_ = 0
    Points_1 = 1
    Points_2 = 2
    Points_3 = 3
    Points_50 = 4
    LuckyPoint = 5
    CommonXPScroll = 6
    RareXPScroll = 7
    PassageScroll = 8
    NormalTome = 9
    EliteTome = 10
    CoreKey = 11
    PropheciesKey = 12
    FactionsKey = 13
    NightfallKey = 14
    CommonMaterial = 15
    RareMaterial = 16
    
class ItemAction(IntEnum):
    NONE = 0
    Loot = 1
    Collect_Data = 2
    Identify = 3
    Hold = 4
    Stash = 5
    Salvage_Mods = 6
    Salvage = 7
    Salvage_Rare_Materials = 8
    Salvage_Common_Materials = 9
    Sell_To_Merchant = 10
    Sell_To_Trader = 11
    Destroy = 12
    Deposit_Material = 13   

class ActionState(IntEnum):
    Pending = 0
    Running = 1
    Completed = 2
    Timeout = 3
    Failed = 4

class RuleType(IntEnum):
    '''
    Types of rules for item handling.
    The rules are processed in order of their type's enum value. If one rule matches, subsequent rules are not evaluated.
    '''
    
    NONE = -1
        
    '''Rule type that matches the item type and the model id to specify pretty accurately an item.'''
    ByWeaponSkin = auto()   
    
    '''Rule type that matches the skin for an item as well as specific mods and requirements.'''
    BySkin = auto()
         
    '''Rule type that matches the item type and the model id to specify pretty accurately an item.'''
    ByModelId = auto()
    
    '''Rule type that matches the weapon type, specific mods and requirements.'''
    ByWeaponType = auto()    
    
    '''Rule type that matches against the weapon mods on the item.'''
    WeaponMod = auto()
    
    '''Rule type that matches against the runes on the item.'''
    Rune = auto()
    
    '''Rule type that matches the item type and rarity only.'''
    ByItemType = auto()
    
    '''Rule type that matches only vial of dyes based on their dye color.'''
    Dye = auto()
    
class InherentSlotType(IntEnum):
    Any = 0
    Old_School = 1
    Inscribable = 2
    
class ModType(IntEnum):
    None_ = 0
    Inherent = 1
    Prefix = 2
    Suffix = 3
    
class ModifierValueArg(IntEnum):
    None_ = -1
    Arg1 = 0
    Arg2 = 1
    Fixed = 2
    
class ModsModels(IntEnum):
    AxeGrip = 905
    AxeHaft = 893
    BowGrip = 906
    BowString = 894
    DaggerHandle = 6331
    DaggerTang = 6323
    FocusCore = 15551
    HammerGrip = 907
    HammerHaft = 895
    Inscription_EquippableItem = 17059
    Inscription_MartialWeapon = 15540
    Inscription_Offhand = 19123
    Inscription_OffhandOrShield = 15541
    Inscription_SpellcastingWeapon = 19122
    Inscription_Weapon = 15542
    ScytheGrip = 15553
    ScytheSnathe = 15543
    ShieldHandle = 15554
    SpearGrip = 15555
    Spearhead = 15544
    StaffHead = 896
    StaffWrapping = 908
    SwordHilt = 897
    SwordPommel = 909
    WandWrapping = 15552 
    
class ModifierIdentifier(IntEnum):
    None_ = 0
    Requirement = 10136
    Damage = 42920
    Damage_NoReq = 42120
    DamageType = 9400
    ShieldArmor = 42936
    TargetItemType = 9656
    RuneAttribute = 8680
    HealthLoss = 8408
    ImprovedVendorValue = 9720
    HighlySalvageable = 9736
    

ITEM_GROUP_ITEM_TYPES: dict[ItemType, list[ItemType]] = {
    ItemType.Weapon: [
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Scythe,
        ItemType.Spear,
        ItemType.Staff,
        ItemType.Sword,
        ItemType.Wand
    ],

    ItemType.MartialWeapon: [
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Scythe,
        ItemType.Spear,
        ItemType.Sword
    ],

    ItemType.OffhandOrShield: [
        ItemType.Offhand,
        ItemType.Shield
    ],

    ItemType.EquippableItem: [
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Offhand,
        ItemType.Scythe,
        ItemType.Shield,
        ItemType.Spear,
        ItemType.Staff,
        ItemType.Sword,
        ItemType.Wand
    ],

    ItemType.SpellcastingWeapon: [
        # ItemType.Offhand,
        ItemType.Staff,
        ItemType.Wand
    ],
}