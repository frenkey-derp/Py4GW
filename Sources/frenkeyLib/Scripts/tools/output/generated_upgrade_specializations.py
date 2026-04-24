from dataclasses import dataclass
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, Profession
from Py4GWCoreLib.item_mods_src.properties import ArmorPlusVsSpecies, AttributePlusOne, DamagePlusVsSpecies, HalvesCastingTimeAttribute, HalvesSkillRechargeAttribute, OfTheProfession
from Py4GWCoreLib.item_mods_src.types import ItemBaneSpecies, ModifierIdentifier
from Py4GWCoreLib.item_mods_src.upgrades import ArmorVsSpeciesUpgrade, HalvesCastingTimeAttributeUpgrade, HalvesRechargeTimeAttributeUpgrade, OfAttributeUpgrade, OfSlayingUpgrade, OfTheProfessionUpgrade, enum, fixed, property_value, ranged


@dataclass(eq=False)
class DivineFavorPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.DivineFavor

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.DivineFavor,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class HealingPrayersPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.HealingPrayers

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.HealingPrayers,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class SmitingPrayersPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.SmitingPrayers

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.SmitingPrayers,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class ProtectionPrayersPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.ProtectionPrayers

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.ProtectionPrayers,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class SoulReapingPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.SoulReaping

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.SoulReaping,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class BloodMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.BloodMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.BloodMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class DeathMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.DeathMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.DeathMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class CursesPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.Curses

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.Curses,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class FastCastingPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.FastCasting

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.FastCasting,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class IllusionMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.IllusionMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.IllusionMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class DominationMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.DominationMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.DominationMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class InspirationMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.InspirationMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.InspirationMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class EnergyStoragePlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.EnergyStorage

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.EnergyStorage,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class AirMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.AirMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.AirMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class EarthMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.EarthMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.EarthMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class FireMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.FireMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.FireMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class WaterMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.WaterMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.WaterMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class SpawningPowerPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.SpawningPower

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.SpawningPower,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class CommuningPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.Communing

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.Communing,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class RestorationMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.RestorationMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.RestorationMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )

@dataclass(eq=False)
class ChannelingMagicPlusOneUpgrade(AttributePlusOneUpgrade):
    attribute = Attribute.ChannelingMagic

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=11,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne, 
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.ChannelingMagic,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
    )