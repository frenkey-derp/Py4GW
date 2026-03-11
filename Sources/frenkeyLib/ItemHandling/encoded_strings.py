from enum import Enum
from Py4GWCoreLib.enums_src.GameData_enums import Attribute
from Py4GWCoreLib.enums_src.Item_enums import ItemType

class EncodedStrings():
    ATTRIBUTE_NAMES = {
        Attribute.FastCasting: [0x1E, 0x9],
        Attribute.IllusionMagic: [0x20, 0x9],
        Attribute.DominationMagic: [0x22, 0x9],
        Attribute.InspirationMagic: [0x24, 0x9],
        Attribute.BloodMagic: [0x26, 0x9],
        Attribute.DeathMagic: [0x2A, 0x9],
        Attribute.SoulReaping: [0x2C, 0x9],
        Attribute.Curses: [0x28, 0x9],    
        Attribute.AirMagic: [0x2E, 0x9],
        Attribute.EarthMagic: [0x30, 0x9],
        Attribute.FireMagic: [0x34, 0x9],
        Attribute.WaterMagic: [0x36, 0x9],
        Attribute.EnergyStorage: [0x32, 0x9],
        Attribute.HealingPrayers: [0x3A, 0x9],
        Attribute.SmitingPrayers: [0x3E, 0x9],
        Attribute.ProtectionPrayers: [0x3C, 0x9],
        Attribute.DivineFavor: [0x38, 0x9],
        Attribute.Strength: [0x40, 0x9],    
        Attribute.AxeMastery: [0x42, 0x9],
        Attribute.HammerMastery: [0x44, 0x9],
        Attribute.Swordsmanship: [0x46, 0x9],
        Attribute.Tactics: [0x48, 0x9],    
        Attribute.BeastMastery: [0x50, 0x9],
        Attribute.Expertise: [0x52, 0x9],
        Attribute.WildernessSurvival: [0x54, 0x9],
        Attribute.Marksmanship: [0x56, 0x9],
        Attribute.DaggerMastery: [0x5A, 0x9],
        Attribute.DeadlyArts: [0x5C, 0x9],
        Attribute.ShadowArts: [0x5E, 0x9],
        Attribute.Communing: [0x60, 0x9],
        Attribute.RestorationMagic: [0x64, 0x9],    
        Attribute.ChannelingMagic: [0x66, 0x9],
        Attribute.CriticalStrikes: [0x58, 0x9],
        Attribute.SpawningPower: [0x62, 0x9],
        Attribute.SpearMastery: [0x1, 0x81, 0x20, 0x11],
        Attribute.Command: [0x1, 0x81, 0xD5, 0x6],
        Attribute.Motivation: [0x1, 0x81, 0x1A, 0x12],
        Attribute.Leadership: [0x1, 0x81, 0x33, 0x12],
        Attribute.ScytheMastery: [0x1, 0x81, 0x22, 0x11],
        Attribute.WindPrayers: [0x1, 0x81, 0x35, 0x12],
        Attribute.EarthPrayers: [0x1, 0x81, 0x37, 0x12],
        Attribute.Mysticism: [0x1, 0x81, 0x39, 0x12],
    }

    STR1_STR2 = bytes([0x30, 0xA, 0xA, 0x1]) # %str1% %str2%
    STR2_STR1_OF_STR3 = bytes([0x31, 0xA, 0xA, 0x1]) # %str2% %str1% of %str3%
    STR2_STR1_BRACKET_STR3 = bytes([0x32, 0xA, 0xA, 0x1]) # %str2% %str1% [%str3%]
    STR1_OF_STR2 = bytes([0x33, 0xA, 0xA, 0x1]) # %str1% of %str2%
    STR1_BRACKET_STR2 = bytes([0x34, 0xA, 0xA, 0x1]) # %str1% [%str2%]
    INSCRIPTION_STR1 = bytes([0x1, 0x81, 0xC5, 0x5D, 0xA, 0x1]) # Inscription: %str1%


    WEAPON_PREFIXES: dict[ItemType, bytes] = {
        ItemType.Axe : bytes([*STR1_STR2, 0xB0, 0x22, 0x1, 0x0]), #Axe Haft
        ItemType.Bow : bytes([*STR1_STR2, 0xB1, 0x22, 0x1, 0x0]), #Bow String
        ItemType.Daggers : bytes([*STR1_STR2, 0xBE, 0x55, 0x1, 0x0]), #Dagger Tang
        # ItemType.Offhand does not have a prefix mod, so no name format is needed
        ItemType.Hammer : bytes([*STR1_STR2, 0xB2, 0x22, 0x1, 0x0]), #Hammer Haft
        ItemType.Scythe : bytes([*STR1_STR2, 0x1, 0x81, 0x73, 0x1C]), #Scythe Snathe
        # ItemType.Shield does not have a prefix mod, so no name format is needed
        ItemType.Spear : bytes([*STR1_STR2, 0x1, 0x81, 0x70, 0x1C, 0x1, 0x0]), #Spearhead
        ItemType.Staff : bytes([*STR1_STR2, 0xB3, 0x22, 0x1, 0x0]), #Staff Head
        ItemType.Sword : bytes([*STR1_STR2, 0xB4, 0x22, 0x1, 0x0]), #Sword Hilt
        # ItemType.Wand does not have a prefix mod, so no name format is needed    
    }

    WEAPON_SUFFIXES: dict[ItemType, bytes] = {
        ItemType.Axe : bytes([*STR1_OF_STR2, 0xB0, 0x22, 0x1, 0x0]), #Axe Grip
        ItemType.Bow : bytes([*STR1_OF_STR2, 0xBD, 0x22, 0x1, 0x0]), #Bow Grip
        ItemType.Daggers : bytes([*STR1_OF_STR2, 0xC1, 0x55, 0x1, 0x0]), #Dagger Handle
        ItemType.Offhand : bytes([*STR1_OF_STR2, 0x1, 0x81, 0xEB, 0x1C, 0x1, 0x0]), #Focus Core
        ItemType.Hammer : bytes([*STR1_OF_STR2, 0xBE, 0x22, 0x1, 0x0]), #Hammer Grip
        ItemType.Scythe : bytes([*STR1_OF_STR2, 0x1, 0x81, 0x73, 0x1C]), #Scythe Grip
        ItemType.Shield : bytes([*STR1_OF_STR2, 0x1, 0x81, 0xED, 0x1C, 0x1, 0x0]), #Shield Handle
        ItemType.Spear : bytes([*STR1_OF_STR2, 0x1, 0x81, 0x74, 0x1C, 0x1, 0x0]), #Spear Grip
        ItemType.Staff : bytes([*STR1_OF_STR2, 0xBF, 0x22, 0x1, 0x0]), #Staff Wrapping
        ItemType.Sword : bytes([*STR1_OF_STR2, 0xC0, 0x22, 0x1, 0x0]), #Sword Pommel
        ItemType.Wand : bytes([*STR1_OF_STR2, 0x1, 0x81, 0xEC, 0x1C, 0x1, 0x0]), #Wand Wrapping
    }