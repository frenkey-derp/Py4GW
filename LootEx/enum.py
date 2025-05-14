
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
    
class ModifierIdentifier(IntEnum):
    None_ = 0
    Requirement = 10136
    Damage = 42920
    DamageType = 9400
    ShieldArmor = 42936   