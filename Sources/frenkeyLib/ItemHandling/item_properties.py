from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Optional
from unittest import case

from PyItem import ItemModifier
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, ProfessionAttributes, Reduced_Ailment
from Sources.frenkeyLib.ItemHandling.insignias import _INSIGNIA_REGISTRY, Insignia
from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier, ItemProperty
from Sources.frenkeyLib.ItemHandling.types import ItemBaneSpecies, ItemUpgradeType, ModifierIdentifier
from Sources.frenkeyLib.ItemHandling.upgrades import ITEM_UPGRADES, ItemUpgradeClass, ItemUpgrade

@dataclass
class Armor(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"Armor: {self.armor}"

@dataclass
class ArmorEnergyRegen(ItemProperty):
    energy_regen: int

    def describe(self) -> str:
        return f"Energy recovery +{self.energy_regen}"

@dataclass
class ArmorMinusAttacking(ItemProperty):
    armor: int
    
    def describe(self) -> str:
        return f"-{self.armor} Armor (while attacking)"

@dataclass
class ArmorPenetration(ItemProperty):
    armor_pen: int
    chance: int

    def describe(self) -> str:
        return f"Armor penetration +{self.armor_pen}% (Chance: {self.chance}%)"

@dataclass
class ArmorPlus(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor"

@dataclass
class ArmorPlusAttacking(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Attacking)"

@dataclass
class ArmorPlusCasting(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Casting)"

@dataclass
class ArmorPlusEnchanted(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Enchanted)"

@dataclass
class ArmorPlusHexed(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Hexed)"

@dataclass
class ArmorPlusHexed2(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Hexed)"

@dataclass
class ArmorPlusVsDamage(ItemProperty):
    armor: int
    damage_type: DamageType

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. {self.damage_type.name} Dmg)"

@dataclass
class ArmorPlusVsElemental(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. Elemental Dmg)"

@dataclass
class ArmorPlusVsPhysical(ItemProperty):
    armor: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. Physical Dmg)"

@dataclass
class ArmorPlusVsSpecies(ItemProperty):
    armor: int
    species: ItemBaneSpecies

    def describe(self) -> str:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"+{self.armor} Armor (vs. {species})"

@dataclass
class ArmorPlusWhileDown(ItemProperty):
    armor: int
    health_threshold: int

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Health is below {self.health_threshold}%)"

@dataclass
class AttributePlusOne(ItemProperty):
    attribute: Attribute
    chance: int

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attribute)} +1 ({self.chance}% chance while using skills)"

@dataclass
class AttributePlusOneItem(ItemProperty):
    chance: int

    def describe(self) -> str:
        return f"Item's attribute +1 (Chance: {self.chance}%)"

@dataclass
class DamageCustomized(ItemProperty):
    damage_increase: int

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}%"

@dataclass
class DamagePlusEnchanted(ItemProperty):
    damage_increase: int

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (while Enchanted)"

@dataclass
class DamagePlusHexed(ItemProperty):
    damage_increase: int

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (while Hexed)"

@dataclass
class DamagePlusPercent(ItemProperty):
    damage_increase: int

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}%"

@dataclass
class DamagePlusStance(ItemProperty):
    damage_increase: int

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (while in a Stance)"

@dataclass
class DamagePlusVsHexed(ItemProperty):
    damage_increase: int

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (vs. Hexed Foes)"

@dataclass
class DamagePlusVsSpecies(ItemProperty):
    damage_increase: int
    species: ItemBaneSpecies

    def describe(self) -> str:
        increase = self.damage_increase
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"Damage +{increase}% (vs. {species.lower()})"

@dataclass
class DamagePlusWhileDown(ItemProperty):
    damage_increase: int
    health_threshold: int

    def describe(self) -> str:
        increase = self.damage_increase
        threshold = self.health_threshold
        
        return f"Damage +{increase}% (while Health is below {threshold}%)"

@dataclass
class DamagePlusWhileUp(ItemProperty):
    damage_increase: int
    health_threshold: int

    def describe(self) -> str:
        increase = self.damage_increase
        threshold = self.health_threshold
        
        return f"Damage +{increase}% (while Health is above +{threshold}%)"

@dataclass
class DamageTypeProperty(ItemProperty):
    damage_type: DamageType

    def describe(self) -> str:
        return f"{self.damage_type.name} Dmg"

@dataclass
class Energy(ItemProperty):
    energy: int

    def describe(self) -> str:
        return f"Energy +{self.energy}"

@dataclass
class Energy2(ItemProperty):
    energy: int

    def describe(self) -> str:
        return f"Energy +{self.energy}"

@dataclass
class EnergyDegen(ItemProperty):
    energy_regen: int

    def describe(self) -> str:
        return f"Energy regeneration -{self.energy_regen}"

@dataclass
class EnergyGainOnHit(ItemProperty):
    energy_gain: int

    def describe(self) -> str:
        return f"Energy gain on hit: {self.energy_gain}"

@dataclass
class EnergyMinus(ItemProperty):
    energy: int

    def describe(self) -> str:
        return f"-{self.energy} Energy"

@dataclass
class EnergyPlus(ItemProperty):
    energy: int

    def describe(self) -> str:
        return f"+{self.energy} Energy"

@dataclass
class EnergyPlusEnchanted(ItemProperty):
    energy: int

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Enchanted)"

@dataclass
class EnergyPlusHexed(ItemProperty):
    energy: int

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Hexed)"

@dataclass
class EnergyPlusWhileBelow(ItemProperty):
    energy: int
    health_threshold: int

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Health is below {self.health_threshold}%)"

@dataclass
class Furious(ItemProperty):
    chance: int

    def describe(self) -> str:
        return f"Double Adrenaline on hit (Chance: +{self.chance}%)"

@dataclass
class HalvesCastingTimeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    def describe(self) -> str:
        return f"Halves casting time of {AttributeNames.get(self.attribute)} spells (Chance: {self.chance}%)"

@dataclass
class HalvesCastingTimeGeneral(ItemProperty):
    chance: int

    def describe(self) -> str:
        return f"Halves casting time of spells (Chance: +{self.chance}%)"

@dataclass
class HalvesCastingTimeItemAttribute(ItemProperty):
    chance: int

    def describe(self) -> str:
        return f"Halves casting time on spells of item's attribute (Chance: {self.chance}%)"

@dataclass
class HalvesSkillRechargeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    def describe(self) -> str:
        return f"Halves skill recharge of {AttributeNames.get(self.attribute)} spells (Chance: {self.chance}%)"

@dataclass
class HalvesSkillRechargeGeneral(ItemProperty):
    chance: int

    def describe(self) -> str:
        return f"Halves skill recharge of spells (Chance: +{self.chance}%)"

@dataclass
class HalvesSkillRechargeItemAttribute(ItemProperty):
    chance: int

    def describe(self) -> str:
        return f"Halves skill recharge on spells of item's attribute (Chance: {self.chance}%)"

@dataclass
class HeadpieceAttribute(ItemProperty):
    attribute: Attribute
    attribute_level: int

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attribute)} +{self.attribute_level}"

@dataclass
class HeadpieceGenericAttribute(ItemProperty):
    def describe(self) -> str:
        return f"Item's attribute +1"

@dataclass
class HealthDegen(ItemProperty):
    health_regen: int

    def describe(self) -> str:
        return f"Health regeneration -{self.health_regen}"

@dataclass
class HealthMinus(ItemProperty):
    health: int

    def describe(self) -> str:
        return f"-{self.health} Health"

@dataclass
class HealthPlus(ItemProperty):
    health: int

    def describe(self) -> str:
        return f"+{self.health} Health"

@dataclass
class HealthPlusEnchanted(ItemProperty):
    health: int

    def describe(self) -> str:
        return f"+{self.health} Health (while Enchanted)"

@dataclass
class HealthPlusHexed(ItemProperty):
    health: int

    def describe(self) -> str:
        return f"+{self.health} Health (while Hexed)"

@dataclass
class HealthPlusStance(ItemProperty):
    health: int

    def describe(self) -> str:
        return f"+{self.health} Health (while in a Stance)"

@dataclass
class HealthPlusWhileDown(ItemProperty):
    health: int
    health_threshold: int

    def describe(self) -> str:
        return f"+{self.health} Health (while Health is below {self.health_threshold}%)"

@dataclass
class HealthStealOnHit(ItemProperty):
    health_steal: int

    def describe(self) -> str:
        return f"Life Draining: {self.health_steal}"

@dataclass
class HighlySalvageable(ItemProperty):
    def describe(self) -> str:
        return f"Highly salvageable"

@dataclass
class IncreaseConditionDuration(ItemProperty):
    condition: Ailment

    def describe(self) -> str:
        return f"Lengthens {self.condition.name.replace('_', ' ')} duration on foes by 33%"

@dataclass
class IncreaseEnchantmentDuration(ItemProperty):
    enchantment_duration: int

    def describe(self) -> str:
        return f"Enchantments last {self.enchantment_duration}% longer"

@dataclass
class IncreasedSaleValue(ItemProperty):
    def describe(self) -> str:
        return f"Improved sale value"

@dataclass
class Infused(ItemProperty):
    def describe(self) -> str:
        return f"Infused"

@dataclass
class OfTheProfession(ItemProperty):
    attribute: Attribute
    attribute_level: int
    profession: Profession

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attribute)}: {self.attribute_level} (if your rank is lower. No effect in PvP.)"

@dataclass
class PrefixProperty(ItemProperty):
    upgrade_id: int
    upgrade: ItemUpgradeClass

    def describe(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}"

@dataclass
class ReceiveLessDamage(ItemProperty):
    damage_reduction: int
    chance: int

    def describe(self) -> str:
        return f"Received damage -{self.damage_reduction} (Chance: {self.chance}%)"

@dataclass
class ReceiveLessPhysDamageEnchanted(ItemProperty):
    damage_reduction: int

    def describe(self) -> str:
        return f"Received physical damage -{self.damage_reduction} (while Enchanted)"

@dataclass
class ReceiveLessPhysDamageHexed(ItemProperty):
    damage_reduction: int

    def describe(self) -> str:
        return f"Received physical damage -{self.damage_reduction} (while Hexed)"

@dataclass
class ReceiveLessPhysDamageStance(ItemProperty):
    damage_reduction: int

    def describe(self) -> str:
        return f"Received physical damage -{self.damage_reduction} (while in a Stance)"

@dataclass
class ReduceConditionDuration(ItemProperty):
    condition: Reduced_Ailment

    def describe(self) -> str:
        return f"Reduces {self.condition.name} duration on you by 20% (Stacking)"

@dataclass
class ReduceConditionTupleDuration(ItemProperty):
    condition_1: Reduced_Ailment
    condition_2: Reduced_Ailment

    def describe(self) -> str:
        return f"Reduces {self.condition_1.name.replace('_', ' ')} duration on you by 20% (Non-stacking)\nReduces {self.condition_2.name.replace('_', ' ')} duration on you by 20% (Non-stacking)"

@dataclass
class ReducesDiseaseDuration(ItemProperty):
    def describe(self) -> str:
        return f"Reduces disease duration on you by 20%"

@dataclass
class SuffixProperty(ItemProperty):
    upgrade_id: int
    upgrade: ItemUpgradeClass

    def describe(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}"

@dataclass
class AttributeRequirement(ItemProperty):
    attribute: Attribute
    attribute_level: int

    def describe(self) -> str:
        return f"(Requires {self.attribute_level} {AttributeNames.get(self.attribute)})"

@dataclass
class BaneProperty(ItemProperty):
    species: ItemBaneSpecies
    
    def describe(self) -> str:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"Bane: {species}"
    
@dataclass
class DamageProperty(ItemProperty):
    min_damage: int
    max_damage: int
    
    def describe(self) -> str:
        return f"{self.min_damage}-{self.max_damage} Damage"

@dataclass
class UnknownUpgradeProperty(ItemProperty):
    upgrade_id: int
    
    def describe(self) -> str:
        return f"Unknown Upgrade (ID {self.upgrade_id})"

@dataclass
class InscriptionProperty(ItemProperty):
    upgrade_id: int
    upgrade: ItemUpgradeClass

    def describe(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}"
    
@dataclass
class UpgradeRuneProperty(ItemProperty):
    upgrade_id: int
    upgrade: ItemUpgradeClass

    def describe(self) -> str:
        return f"RUNE: {self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}"
    
@dataclass
class AppliesToRuneProperty(ItemProperty):
    upgrade_id: int
    upgrade: ItemUpgradeClass

    def describe(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}"

@dataclass
class TooltipProperty(ItemProperty):
    pass

def get_profession_from_attribute(attribute: Attribute) -> Optional[Profession]:
    for prof, attr in ProfessionAttributes.__dict__.items():
        if isinstance(attr, list) and attribute in attr:
            return Profession[prof]
    return None

def get_upgrade_property(modifier: DecodedModifier) -> ItemProperty:
    upgrade = next((u for u in ITEM_UPGRADES if u.upgrade_id == modifier.upgrade_id), None)
    upgrade_type = upgrade.upgrade_type if upgrade else None
    
    if upgrade:
        match upgrade_type:
            case ItemUpgradeType.Prefix:
                return PrefixProperty(modifier=modifier, upgrade_id=modifier.upgrade_id, upgrade=upgrade)
            
            case ItemUpgradeType.Suffix:
                return SuffixProperty(modifier=modifier, upgrade_id=modifier.upgrade_id, upgrade=upgrade)
            
            case ItemUpgradeType.Inscription:
                return InscriptionProperty(modifier=modifier, upgrade_id=modifier.upgrade_id, upgrade=upgrade)
            
            case ItemUpgradeType.UpgradeRune:
                return UpgradeRuneProperty(modifier=modifier, upgrade_id=modifier.upgrade_id, upgrade=upgrade)
            
            case ItemUpgradeType.AppliesToRune:
                return AppliesToRuneProperty(modifier=modifier, upgrade_id=modifier.upgrade_id, upgrade=upgrade)
    
    return UnknownUpgradeProperty(modifier=modifier, upgrade_id=modifier.upgrade_id)
        
_PROPERTY_FACTORY: dict[ModifierIdentifier, Callable[[DecodedModifier], ItemProperty]] = {
    ModifierIdentifier.Armor1: lambda m: Armor(modifier=m, armor=m.arg1),
    ModifierIdentifier.Armor2: lambda m: Armor(modifier=m, armor=m.arg1),
    ModifierIdentifier.ArmorEnergyRegen: lambda m: ArmorEnergyRegen(modifier=m, energy_regen=m.arg1),
    ModifierIdentifier.ArmorMinusAttacking: lambda m: ArmorMinusAttacking(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPenetration: lambda m: ArmorPenetration(modifier=m, armor_pen=m.arg2, chance=m.arg1),
    ModifierIdentifier.ArmorPlus: lambda m: ArmorPlus(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusAttacking: lambda m: ArmorPlusAttacking(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusCasting: lambda m: ArmorPlusCasting(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusEnchanted: lambda m: ArmorPlusEnchanted(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusHexed: lambda m: ArmorPlusHexed(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusHexed2: lambda m: ArmorPlusHexed2(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsDamage: lambda m: ArmorPlusVsDamage(modifier=m, armor=m.arg2, damage_type=DamageType(m.arg1)),
    ModifierIdentifier.ArmorPlusVsElemental: lambda m: ArmorPlusVsElemental(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsPhysical: lambda m: ArmorPlusVsPhysical(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsPhysical2: lambda m: ArmorPlusVsPhysical(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsSpecies: lambda m: ArmorPlusVsSpecies(modifier=m, armor=m.arg2, species=ItemBaneSpecies(m.arg1)),
    ModifierIdentifier.ArmorPlusWhileDown: lambda m: ArmorPlusWhileDown(modifier=m, armor=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.AttributePlusOne: lambda m: AttributePlusOne(modifier=m, attribute=Attribute(m.arg1), chance=m.arg2),
    ModifierIdentifier.AttributePlusOneItem: lambda m: AttributePlusOneItem(modifier=m, chance=m.arg2),
    ModifierIdentifier.AttributeRequirement: lambda m: AttributeRequirement(modifier=m, attribute=Attribute(m.arg1), attribute_level=m.arg2),
    ModifierIdentifier.BaneSpecies: lambda m: BaneProperty(modifier=m, species=ItemBaneSpecies(m.arg1)),
    ModifierIdentifier.Damage: lambda m: DamageProperty(modifier=m, min_damage=m.arg2, max_damage=m.arg1),
    ModifierIdentifier.Damage2: lambda m: DamageProperty(modifier=m, min_damage=m.arg2, max_damage=m.arg1),
    ModifierIdentifier.DamageCustomized: lambda m: DamageCustomized(modifier=m, damage_increase=m.arg1 - 100),
    ModifierIdentifier.DamagePlusEnchanted: lambda m: DamagePlusEnchanted(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusHexed: lambda m: DamagePlusHexed(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusPercent: lambda m: DamagePlusPercent(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusStance: lambda m: DamagePlusStance(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusVsHexed: lambda m: DamagePlusVsHexed(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusVsSpecies: lambda m: DamagePlusVsSpecies(modifier=m, damage_increase=m.arg1, species=ItemBaneSpecies(m.arg2)),
    ModifierIdentifier.DamagePlusWhileDown: lambda m: DamagePlusWhileDown(modifier=m, damage_increase=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.DamagePlusWhileUp: lambda m: DamagePlusWhileUp(modifier=m, damage_increase=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.DamageTypeProperty: lambda m: DamageTypeProperty(modifier=m, damage_type=DamageType(m.arg1)),
    ModifierIdentifier.Energy: lambda m: Energy(modifier=m, energy=m.arg1),
    ModifierIdentifier.Energy2: lambda m: Energy(modifier=m, energy=m.arg1),
    ModifierIdentifier.EnergyDegen: lambda m: EnergyDegen(modifier=m, energy_regen=m.arg2),
    ModifierIdentifier.EnergyGainOnHit: lambda m: EnergyGainOnHit(modifier=m, energy_gain=m.arg2),
    ModifierIdentifier.EnergyMinus: lambda m: EnergyMinus(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlus : lambda m: EnergyPlus(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlusEnchanted: lambda m: EnergyPlusEnchanted(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlusHexed: lambda m: EnergyPlusHexed(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlusWhileBelow: lambda m: EnergyPlusWhileBelow(modifier=m, energy=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.Furious: lambda m: Furious(modifier=m, chance=m.arg2),
    ModifierIdentifier.HalvesCastingTimeAttribute: lambda m: HalvesCastingTimeAttribute(modifier=m, chance=m.arg1, attribute=Attribute(m.arg2)),
    ModifierIdentifier.HalvesCastingTimeGeneral: lambda m: HalvesCastingTimeGeneral(modifier=m, chance=m.arg1),
    ModifierIdentifier.HalvesCastingTimeItemAttribute: lambda m: HalvesCastingTimeItemAttribute(modifier=m, chance=m.arg1),
    ModifierIdentifier.HalvesSkillRechargeAttribute: lambda m: HalvesSkillRechargeAttribute(modifier=m, chance=m.arg1, attribute=Attribute(m.arg2)),
    ModifierIdentifier.HalvesSkillRechargeGeneral: lambda m: HalvesSkillRechargeGeneral(modifier=m, chance=m.arg1),
    ModifierIdentifier.HalvesSkillRechargeItemAttribute: lambda m: HalvesSkillRechargeItemAttribute(modifier=m, chance=m.arg1),
    ModifierIdentifier.HeadpieceAttribute: lambda m: HeadpieceAttribute(modifier=m, attribute=Attribute(m.arg2), attribute_level=m.arg1),
    ModifierIdentifier.HeadpieceGenericAttribute: lambda m: HeadpieceGenericAttribute(modifier=m),
    ModifierIdentifier.HealthDegen: lambda m: HealthDegen(modifier=m, health_regen=m.arg2),
    ModifierIdentifier.HealthMinus: lambda m: HealthMinus(modifier=m, health=m.arg2),
    ModifierIdentifier.HealthPlus: lambda m: HealthPlus(modifier=m, health=m.arg2),
    ModifierIdentifier.HealthPlus2 : lambda m: HealthPlus(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlusEnchanted: lambda m: HealthPlusEnchanted(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlusHexed: lambda m: HealthPlusHexed(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlusStance: lambda m: HealthPlusStance(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlusWhileDown: lambda m: HealthPlusWhileDown(modifier=m, health=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.HealthStealOnHit: lambda m: HealthStealOnHit(modifier=m, health_steal=m.arg1),
    ModifierIdentifier.HighlySalvageable: lambda m: HighlySalvageable(modifier=m),
    ModifierIdentifier.IncreaseConditionDuration: lambda m: IncreaseConditionDuration(modifier=m, condition=Ailment(m.arg2)),
    ModifierIdentifier.IncreaseEnchantmentDuration: lambda m: IncreaseEnchantmentDuration(modifier=m, enchantment_duration=m.arg2),
    ModifierIdentifier.IncreasedSaleValue: lambda m: IncreasedSaleValue(modifier=m),
    ModifierIdentifier.Infused: lambda m: Infused(modifier=m),
    ModifierIdentifier.OfTheProfession: lambda m: OfTheProfession(modifier=m, attribute=Attribute(m.arg1), attribute_level=m.arg2, profession=get_profession_from_attribute(Attribute(m.arg1)) or Profession._None),
    ModifierIdentifier.ReceiveLessPhysDamageEnchanted: lambda m: ReceiveLessPhysDamageEnchanted(modifier=m, damage_reduction=m.arg2),
    ModifierIdentifier.ReceiveLessPhysDamageHexed: lambda m: ReceiveLessPhysDamageHexed(modifier=m, damage_reduction=m.arg2),
    ModifierIdentifier.ReceiveLessPhysDamageStance: lambda m: ReceiveLessPhysDamageStance(modifier=m, damage_reduction=m.arg2),
    ModifierIdentifier.ReduceConditionDuration: lambda m: ReduceConditionDuration(modifier=m, condition=Reduced_Ailment(m.arg1)),
    ModifierIdentifier.ReduceConditionTupleDuration: lambda m: ReduceConditionTupleDuration(modifier=m, condition_1=Reduced_Ailment(m.arg2), condition_2=Reduced_Ailment(m.arg1)),
    ModifierIdentifier.ReducesDiseaseDuration: lambda m: ReducesDiseaseDuration(modifier=m),
    ModifierIdentifier.ReceiveLessDamage: lambda m: ReceiveLessDamage(modifier=m, damage_reduction=m.arg2, chance=m.arg1),
    ModifierIdentifier.Upgrade1: lambda m: get_upgrade_property(m),
    ModifierIdentifier.Upgrade2: lambda m: get_upgrade_property(m),
}
