from enum import IntEnum
from typing import Optional
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, ProfessionAttributes, Reduced_Ailment
from Sources.frenkeyLib.ItemHandling.insignias import _INSIGNIA_REGISTRY, Insignia
from Sources.frenkeyLib.ItemHandling.item_modifiers import ItemProperty

_PROPERTY_REGISTRY: dict[int, type[ItemProperty]] = {}
def register_property(cls: type[ItemProperty]) -> type[ItemProperty]:
    _PROPERTY_REGISTRY[cls.identifier] = cls
    return cls


class ItemBaneSpecies(IntEnum):
    Undead = 0
    Charr = 1
    Trolls = 2
    Plants = 3
    Skeletons = 4
    Giants = 5
    Dwarves = 6
    Tengus = 7
    Demons = 8
    Dragons = 9
    Ogres = 10
    Unknown = -1

class BaneSpecies(ItemProperty):
    identifier = 0x008

    @property
    def species(self) -> ItemBaneSpecies:
        return ItemBaneSpecies(self.modifier.arg1)

    def describe(self) -> str:
        match self.species:
            case ItemBaneSpecies.Charr:
                return "of Charrslaying"
            case ItemBaneSpecies.Demons:
                return "of Demonslaying"
            case ItemBaneSpecies.Dragons:
                return "of Dragonslaying"
            case ItemBaneSpecies.Dwarves:
                return "of Dwarfslaying"
            case ItemBaneSpecies.Giants:
                return "of Giantslaying"
            case ItemBaneSpecies.Ogres:
                return "of Ogreslaying"
            case ItemBaneSpecies.Plants:
                return "of Pruning"
            case ItemBaneSpecies.Tengus:
                return "of Tenguslaying"
            case ItemBaneSpecies.Trolls:                
                return "of Trollslaying"
            case ItemBaneSpecies.Undead:
                return "of Deathbane"            
            case ItemBaneSpecies.Skeletons:
                return "of Skeletonslaying"
            case _:
                return f"of Slaying of Unknown Species (ID {self.modifier.arg1})"
register_property(BaneSpecies)

class Damage(ItemProperty):
    identifier = 0x27A

    @property
    def min_damage(self) -> int:
        return self.modifier.arg2

    @property
    def max_damage(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"{self.min_damage}-{self.max_damage} Damage"
register_property(Damage)

class Damage2(ItemProperty):
    identifier = 0x248

    @property
    def min_damage(self) -> int:
        return self.modifier.arg2

    @property
    def max_damage(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"{self.min_damage}-{self.max_damage} Damage"
register_property(Damage2)

class AttributeRequirement(ItemProperty):
    identifier = 0x279

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg1)

    @property
    def required(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"(Requires {self.required} {AttributeNames.get(self.attribute)})"
register_property(AttributeRequirement)

class Armor1(ItemProperty):
    identifier = 0x27B

    @property
    def armor(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Armor: {self.armor}"
register_property(Armor1)

class Armor2(ItemProperty):
    identifier = 0x23C

    @property
    def armor(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Armor: {self.armor}"
register_property(Armor2)

class Energy(ItemProperty):
    identifier = 0x27C

    @property
    def energy(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Energy +{self.energy}"
register_property(Energy)

class Energy2(ItemProperty):
    identifier = 0x22C

    @property
    def energy(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Energy +{self.energy}"
register_property(Energy2)

class OfTheProfession(ItemProperty):
    identifier = 0x28A

    @property
    def attibute(self) -> Attribute:
        return Attribute(self.modifier.arg1)

    @property
    def attribute_level(self) -> int:
        return self.modifier.arg2

    @property
    def profession_id(self) -> Profession:
        attribute = self.attibute

        # find attribute in ProfessionAttributes
        for prof, attr in ProfessionAttributes.__dict__.items():
            if isinstance(attr, list) and attribute in attr:
                return Profession[prof]

        return Profession._None

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attibute)}: {self.attribute_level} (if your rank is lower. No effect in PvP.)"
register_property(OfTheProfession)

class DamageTypeProperty(ItemProperty):
    identifier = 0x24B

    @property
    def damage_type(self) -> DamageType:
        return DamageType(self.modifier.arg1)

    def describe(self) -> str:
        return f"{self.damage_type.name} Dmg"
register_property(DamageTypeProperty)

class IncreasedSaleValue(ItemProperty):
    identifier = 0x25F

    def describe(self) -> str:
        return f"Improved sale value"
register_property(IncreasedSaleValue)

class HighlySalvageable(ItemProperty):
    identifier = 0x260

    def describe(self) -> str:
        return f"Highly salvageable"
register_property(HighlySalvageable)

class DamageCustomized(ItemProperty):
    identifier = 0x249

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg1 - 100

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}%"
register_property(DamageCustomized)

class DamagePlusPercent(ItemProperty):
    identifier = 0x223

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}%"
register_property(DamagePlusPercent)

class DamagePlusVsHexed(ItemProperty):
    identifier = 0x225

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (vs. Hexed Foes)"
register_property(DamagePlusVsHexed)

class DamagePlusEnchanted(ItemProperty):
    identifier = 0x226

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (while Enchanted)"
register_property(DamagePlusEnchanted)

class DamagePlusWhileUp(ItemProperty):
    identifier = 0x227

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    @property
    def health_threshold(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        increase = self.damage_increase
        threshold = self.health_threshold

        return f"Damage +{increase}% (while Health is above +{threshold}%)"
register_property(DamagePlusWhileUp)

class DamagePlusWhileDown(ItemProperty):
    identifier = 0x228

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    @property
    def health_threshold(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        increase = self.damage_increase
        threshold = self.health_threshold

        return f"Damage +{increase}% (while Health is below {threshold}%)"
register_property(DamagePlusWhileDown)

class DamagePlusHexed(ItemProperty):
    identifier = 0x229

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (while Hexed)"
register_property(DamagePlusHexed)

class DamagePlusStance(ItemProperty):
    identifier = 0x22A

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        increase = self.damage_increase
        return f"Damage +{increase}% (while in a Stance)"
register_property(DamagePlusStance)

class DamagePlusVsSpecies(ItemProperty):
    identifier = 0x224

    @property
    def damage_increase(self) -> int:
        return self.modifier.arg1

    @property
    def species(self) -> ItemBaneSpecies:
        return ItemBaneSpecies(self.modifier.arg2)

    def describe(self) -> str:
        increase = self.damage_increase
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"Damage +{increase}% (vs. {species.lower()})"
register_property(DamagePlusVsSpecies)

class HalvesCastingTimeGeneral(ItemProperty):
    identifier = 0x220

    @property
    def chance(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Halves casting time of spells (Chance: +{self.chance}%)"
register_property(HalvesCastingTimeGeneral)

class HalvesCastingTimeAttribute(ItemProperty):
    identifier = 0x221

    @property
    def chance(self) -> int:
        return self.modifier.arg1

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg2)

    def describe(self) -> str:
        return f"Halves casting time of {AttributeNames.get(self.attribute)} spells (Chance: {self.chance}%)"
register_property(HalvesCastingTimeAttribute)

class HalvesCastingTimeItemAttribute(ItemProperty):
    identifier = 0x280

    @property
    def chance(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Halves casting time on spells of item's attribute (Chance: {self.chance}%)"
register_property(HalvesCastingTimeItemAttribute)

class HalvesSkillRechargeGeneral(ItemProperty):
    identifier = 0x23A

    @property
    def chance(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Halves skill recharge of spells (Chance: +{self.chance}%)"
register_property(HalvesSkillRechargeGeneral)

class HalvesSkillRechargeAttribute(ItemProperty):
    identifier = 0x239
    
    @property
    def chance(self) -> int:
        return self.modifier.arg1

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg2)

    def describe(self) -> str:
        return f"Halves skill recharge of {AttributeNames.get(self.attribute)} spells (Chance: {self.chance}%)"
register_property(HalvesSkillRechargeAttribute)

class HalvesSkillRechargeItemAttribute(ItemProperty):
    identifier = 0x282

    @property
    def chance(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Halves skill recharge on spells of item's attribute (Chance: {self.chance}%)"
register_property(HalvesSkillRechargeItemAttribute)

class EnergyPlus(ItemProperty):
    identifier = 0x22D

    @property
    def energy(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.energy} Energy"
register_property(EnergyPlus)

class EnergyPlusEnchanted(ItemProperty):
    identifier = 0x22F

    @property
    def energy(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Enchanted)"
register_property(EnergyPlusEnchanted)

class EnergyPlusHexed(ItemProperty):
    identifier = 0x232

    @property
    def energy(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Hexed)"
register_property(EnergyPlusHexed)

class EnergyPlusWhileAbove(ItemProperty):
    identifier = 0x231

    @property
    def energy(self) -> int:
        return self.modifier.arg2

    @property
    def health_threshold(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Health is above {self.health_threshold}%)"
register_property(EnergyPlusWhileAbove)

class EnergyPlusWhileBelow(ItemProperty):
    identifier = 0x231

    @property
    def energy(self) -> int:
        return self.modifier.arg2

    @property
    def health_threshold(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.energy} Energy (while Health is below {self.health_threshold}%)"
register_property(EnergyPlusWhileBelow)

class EnergyMinus(ItemProperty):
    identifier = 0x20B

    @property
    def energy(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"-{self.energy} Energy"
register_property(EnergyMinus)

class EnergyDegen(ItemProperty):
    identifier = 0x20C

    @property
    def energy_regen(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Energy regeneration -{self.energy_regen}"
register_property(EnergyDegen)

# class EnergyRegen(ItemProperty):
#     identifier = 0x262

#     @property
#     def energy_regen(self) -> int:
#         return self.modifier.arg2

#     def describe(self) -> str:
#         return f"Energy regeneration +{self.energy_regen}"
# register_property(EnergyRegen)

class EnergyGainOnHit(ItemProperty):
    identifier = 0x251

    @property
    def energy_gain(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Energy gain on hit: {self.energy_gain}"
register_property(EnergyGainOnHit)

class ArmorPlus(ItemProperty):
    identifier = 0x210

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor"
register_property(ArmorPlus)

class ArmorPlusVsDamage(ItemProperty):
    identifier = 0x211

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    @property
    def damage_type(self) -> DamageType:
        return DamageType(self.modifier.arg1)

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. {self.damage_type.name} Dmg)"
register_property(ArmorPlusVsDamage)

class ArmorPlusVsPhysical(ItemProperty):
    identifier = 0x215

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. Physical Dmg)"
register_property(ArmorPlusVsPhysical)

class ArmorPlusVsPhysical2(ItemProperty):
    identifier = 0x216

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. Physical Dmg)"
register_property(ArmorPlusVsPhysical2)

class ArmorPlusVsElemental(ItemProperty):
    identifier = 0x212

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (vs. Elemental Dmg)"
register_property(ArmorPlusVsElemental)

class ArmorPlusVsSpecies(ItemProperty):
    identifier = 0x214

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    @property
    def species(self) -> ItemBaneSpecies:
        return ItemBaneSpecies(self.modifier.arg1)

    def describe(self) -> str:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"+{self.armor} Armor (vs. {species})"
register_property(ArmorPlusVsSpecies)

class ArmorPlusAttacking(ItemProperty):
    identifier = 0x217

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Attacking)"
register_property(ArmorPlusAttacking)

class ArmorPlusCasting(ItemProperty):
    identifier = 0x218

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Casting)"
register_property(ArmorPlusCasting)

class ArmorPlusEnchanted(ItemProperty):
    identifier = 0x219

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Enchanted)"
register_property(ArmorPlusEnchanted)

class ArmorPlusHexed2(ItemProperty):
    identifier = 0x21A

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Hexed)"
register_property(ArmorPlusHexed2)

class ArmorPlusHexed(ItemProperty):
    identifier = 0x21C

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Hexed)"
register_property(ArmorPlusHexed)

class ArmorPlusWhileDown(ItemProperty):
    identifier = 0x21B

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    @property
    def health_threshold(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.armor} Armor (while Health is below {self.health_threshold}%)"
register_property(ArmorPlusWhileDown)

class ArmorMinusAttacking(ItemProperty):
    identifier = 0x201

    @property
    def armor(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"-{self.armor} Armor (while attacking)"
register_property(ArmorMinusAttacking)

class ArmorPenetration(ItemProperty):
    identifier = 0x23F

    @property
    def armor_pen(self) -> int:
        return self.modifier.arg2

    @property
    def chance(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Armor penetration +{self.armor_pen}% (Chance: {self.chance}%)"
register_property(ArmorPenetration)

class HealthPlus(ItemProperty):
    identifier = 0x289

    @property
    def health(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"+{self.health} Health"
register_property(HealthPlus)

class HealthPlus2(ItemProperty):
    identifier = 0x234

    @property
    def health(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.health} Health"
register_property(HealthPlus2)

class HealthPlusWhileDown(ItemProperty):
    identifier = 0x230

    @property
    def health(self) -> int:
        return self.modifier.arg2

    @property
    def health_threshold(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.health} Health (while Health is below {self.health_threshold}%)"
register_property(HealthPlusWhileDown)

class HealthPlusHexed(ItemProperty):
    identifier = 0x237

    @property
    def health(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.health} Health (while Hexed)"
register_property(HealthPlusHexed)

class HealthPlusStance(ItemProperty):
    identifier = 0x238

    @property
    def health(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.health} Health (while in a Stance)"
register_property(HealthPlusStance)

class HealthPlusEnchanted(ItemProperty):
    identifier = 0x236

    @property
    def health(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"+{self.health} Health (while Enchanted)"
register_property(HealthPlusEnchanted)

class HealthMinus(ItemProperty):
    identifier = 0x20D

    @property
    def health(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"-{self.health} Health"
register_property(HealthMinus)

class HealthDegen(ItemProperty):
    identifier = 0x20E

    @property
    def health_regen(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Health regeneration -{self.health_regen}"
register_property(HealthDegen)

class HealthStealOnHit(ItemProperty):
    identifier = 0x252

    @property
    def health_steal(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Life Draining: {self.health_steal}"
register_property(HealthStealOnHit)

class ReceiveLessDamage(ItemProperty):
    identifier = 0x207

    @property
    def damage_reduction(self) -> int:
        return self.modifier.arg2
    
    @property
    def chance(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Received damage -{self.damage_reduction} (Chance: {self.chance}%)"
register_property(ReceiveLessDamage)

class ReceiveLessPhysDamageEnchanted(ItemProperty):
    identifier = 0x208

    @property
    def damage_reduction(self) -> int:
        return self.modifier.arg2
    
    def describe(self) -> str:
        return f"Received physical damage -{self.damage_reduction} (while Enchanted)"
register_property(ReceiveLessPhysDamageEnchanted)

class ReceiveLessPhysDamageHexed(ItemProperty):
    identifier = 0x209

    @property
    def damage_reduction(self) -> int:
        return self.modifier.arg2
    
    def describe(self) -> str:
        return f"Received physical damage -{self.damage_reduction} (while Hexed)"
register_property(ReceiveLessPhysDamageHexed)

class ReceiveLessPhysDamageStance(ItemProperty):
    identifier = 0x20A

    @property
    def damage_reduction(self) -> int:
        return self.modifier.arg2
    
    def describe(self) -> str:
        return f"Received physical damage -{self.damage_reduction} (while in a Stance)"
register_property(ReceiveLessPhysDamageStance)

class AttributePlusOne(ItemProperty):
    identifier = 0x241

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg1)
    
    @property
    def chance(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attribute)} +1 ({self.chance}% chance while using skills)"
register_property(AttributePlusOne)

class AttributePlusOneItem(ItemProperty):
    identifier = 0x283

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg1)
    
    @property
    def chance(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Item's attribute +1 (Chance: {self.chance}%)"
register_property(AttributePlusOneItem)

class ReduceConditionDuration(ItemProperty):
    identifier = 0x285

    @property
    def condition(self) -> Reduced_Ailment:
        return Reduced_Ailment(self.modifier.arg1)

    def describe(self) -> str:
        return f"Reduces {self.condition.name} duration on you by 20% (Stacking)"
register_property(ReduceConditionDuration)

class ReduceConditionTupleDuration(ItemProperty):
    identifier = 0x277

    @property
    def condition_1(self) -> Reduced_Ailment:
        return Reduced_Ailment(self.modifier.arg1)

    @property
    def condition_2(self) -> Reduced_Ailment:
        return Reduced_Ailment(self.modifier.arg2)

    def describe(self) -> str:
        return f"Reduces {self.condition_1.name.replace('_', ' ')} duration on you by 20% (Non-stacking)\nReduces {self.condition_2.name.replace('_', ' ')} duration on you by 20% (Non-stacking)"
register_property(ReduceConditionTupleDuration)

class IncreaseEnchantmentDuration(ItemProperty):
    identifier = 0x22B

    @property
    def enchantment_duration(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Enchantments last {self.enchantment_duration}% longer"
register_property(IncreaseEnchantmentDuration)

class IncreaseConditionDuration(ItemProperty):
    identifier = 0x246

    @property
    def condition(self) -> Ailment:
        return Ailment(self.modifier.arg2)

    def describe(self) -> str:
        return f"Lengthens {self.condition.name.replace('_', ' ')} duration on foes by 33%"
register_property(IncreaseConditionDuration)

class Furious(ItemProperty):
    identifier = 0x23B

    @property
    def chance(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Double Adrenaline on hit (Chance: +{self.chance}%)"
register_property(Furious)

class ReducesDiseaseDuration(ItemProperty):
    identifier = 0x247

    def describe(self) -> str:
        return f"Reduces disease duration on you by 20%"
register_property(ReducesDiseaseDuration)

class RuneAttribute(ItemProperty):
    identifier = 0x21E

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg1)
    
    @property
    def attribute_level(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attribute)} +{self.attribute_level}"
register_property(RuneAttribute)

class HeadpieceAttribute(ItemProperty):
    identifier = 0x21F

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg1)
    
    @property
    def attribute_level(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"{AttributeNames.get(self.attribute)} +{self.attribute_level}"
register_property(HeadpieceAttribute)

# class ArmorVsElemental(ItemProperty):
#     identifier = 0x20F

#     @property
#     def armor(self) -> int:
#         return self.modifier.arg1

#     def describe(self) -> str:
#         return f"+{self.armor} Armor (vs. elemental dmg)XX"
# register_property(ArmorVsElemental)

class ArmorEnergyRegen(ItemProperty):
    identifier = 0x22e

    @property
    def energy_regen(self) -> int:
        return self.modifier.arg1

    def describe(self) -> str:
        return f"Energy recovery +{self.energy_regen}"
register_property(ArmorEnergyRegen)

class HeadpieceGenericAttribute(ItemProperty):
    # identifier = 0x262
    identifier = 0x284

    @property
    def attribute(self) -> Attribute:
        return Attribute(self.modifier.arg1)
    
    @property
    def attribute_level(self) -> int:
        return self.modifier.arg2

    def describe(self) -> str:
        return f"Item's attribute +{self.attribute_level}"
register_property(HeadpieceGenericAttribute)

class InsigniaProperty(ItemProperty):
    identifier = 0x240
    
    @property
    def insignia(self) -> Optional[Insignia]:
        property_cls = _INSIGNIA_REGISTRY.get(self.modifier.arg)
        if property_cls:
            prop = property_cls(self.modifier)
            if isinstance(prop, Insignia):
                return prop
            
        return None
        
    def describe(self) -> str:
        insignia = self.insignia
        if insignia:
            return f"{insignia.describe()}"
        else:
            return f"Unknown Insignia (ID {self.modifier.arg})"
    
    def is_valid(self) -> bool:
        return self.insignia is not None
    
register_property(InsigniaProperty)
