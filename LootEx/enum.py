
from enum import IntEnum
from Py4GWCoreLib.enums import ModelID

COMMON_MATERIALS: list[int] = [
    ModelID.Bone,
    ModelID.Iron_Ingot,
    ModelID.Tanned_Hide_Square,
    ModelID.Scale,
    ModelID.Chitin_Fragment,
    ModelID.Bolt_Of_Cloth,
    ModelID.Wood_Plank,
    ModelID.Granite_Slab,
    ModelID.Pile_Of_Glittering_Dust,
    ModelID.Plant_Fiber,
    ModelID.Feather,    
]

RARE_MATERIALS: list[int] = [
    ModelID.Fur_Square,
    ModelID.Bolt_Of_Linen,
    ModelID.Bolt_Of_Damask,
    ModelID.Bolt_Of_Silk,
    ModelID.Glob_Of_Ectoplasm,
    ModelID.Steel_Ingot,
    ModelID.Deldrimor_Steel_Ingot,
    ModelID.Monstrous_Claw,
    ModelID.Monstrous_Eye,
    ModelID.Monstrous_Fang,
    ModelID.Ruby,
    ModelID.Sapphire,
    ModelID.Diamond,
    ModelID.Onyx_Gemstone,
    ModelID.Lump_Of_Charcoal,
    ModelID.Obsidian_Shard,
    ModelID.Tempered_Glass_Vial,
    ModelID.Leather_Square,
    ModelID.Elonian_Leather_Square,
    ModelID.Vial_Of_Ink,
    ModelID.Roll_Of_Parchment,
    ModelID.Roll_Of_Vellum,
    ModelID.Spiritwood_Plank,
    ModelID.Amber_Chunk,
    ModelID.Jadeite_Shard
]

class MaterialType(IntEnum):
    None_ = 0
    Common = 1
    Rare = 2

class Campaign(IntEnum):
    None_ = 0
    Core = 1
    Prophecies = 2
    Factions = 3
    Nightfall = 4
    EyeOfTheNorth = 5

class MessageActions(IntEnum):
    None_ = 0
    PauseDataCollection = 1
    ResumeDataCollection = 2
    StartDataCollection = 3
    ReloadData = 4
    StartLootHandling = 5
    StopLootHandling = 6
    ShowLootExWindow = 7
    HideLootExWindow = 8
    OpenXunlai = 9    
    
class SalvageOption(IntEnum):
    None_ = 0
    Prefix = 1
    Suffix = 2
    Inherent = 3
    CraftingMaterials = 4
    LesserCraftingMaterials = 5
    RareCraftingMaterials = 6
    
class SalvageKitOption(IntEnum):
    None_ = 0
    Lesser = 1
    LesserOrExpert = 2
    Expert = 3
    Perfect = 4

class WeaponType(IntEnum):
    Axe = 1
    Sword = 2
    Spear = 3
    Wand = 4
    Daggers = 5
    Hammer = 6
    Scythe = 7
    Bow = 8
    Staff = 9
    Focus = 10
    Shield = 11

class ModType(IntEnum):
    None_ = 0
    Inherent = 1
    Prefix = 2
    Suffix = 3

class EnemyType(IntEnum):
    Undead = 0
    Charr = 1
    Troll = 2
    Plant = 3
    Skeleton = 4
    Giant = 5
    Dwarf = 6
    Tengu = 7
    Demon = 8
    Dragon = 9
    Ogre = 10
    
class ModifierValueArg(IntEnum):
    None_ = -1
    Arg1 = 0
    Arg2 = 1
    Fixed = 2

class ModifierIdentifier(IntEnum):
    None_ = 0
    Requirement = 10136
    Damage = 42920
    DamageType = 9400
    ShieldArmor = 42936
    TargetItemType = 9656
    RuneAttribute = 8680
    HealthLoss = 8408