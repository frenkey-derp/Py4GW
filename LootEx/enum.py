
from enum import IntEnum

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
    
class ModTargetType(IntEnum):
    Salvage = 0
    Axe = 2
    Bag = 3
    Boots = 4
    Bow = 5
    Bundle = 6
    Chestpiece = 7
    Rune_Mod = 8
    Usable =9
    Dye = 10
    Materials_Zcoins = 11
    Offhand = 12
    Gloves = 13
    Hammer = 15
    Headpiece = 16
    CC_Shards = 17
    Key = 18
    Leggings = 19
    Gold_Coin = 20
    Quest_Item = 21
    Wand = 22
    Shield = 24
    Staff = 26
    Sword = 27
    Kit = 29
    Trophy = 30
    Scroll = 31
    Daggers = 32
    Present = 33
    Minipet = 34
    Scythe = 35
    Spear = 36
    FocusOrShield = 39
    EquipableItem = 40
    Storybook = 43
    Costume = 44
    Costume_Headpiece = 45
    Unknown = 255

class ModifierIdentifier(IntEnum):
    None_ = 0
    Requirement = 10136
    Damage = 42920
    DamageType = 9400
    ShieldArmor = 42936
    ItemType = 9656