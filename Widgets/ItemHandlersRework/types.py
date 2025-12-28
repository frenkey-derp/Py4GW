from enum import IntEnum
from Py4GWCoreLib.enums_src.Item_enums import ItemType

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
    NONE = -1
    ByItemType = 0
    ByModelId = 1
    BySkin = 2
    WeaponMod = 3

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