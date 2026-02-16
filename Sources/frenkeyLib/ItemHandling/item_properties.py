from dataclasses import dataclass
from typing import Callable, Optional

import Py4GW

from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, ProfessionAttributes, Reduced_Ailment
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier
from Sources.frenkeyLib.ItemHandling.types import ItemBaneSpecies, ItemUpgradeType, ModifierIdentifier
from Sources.frenkeyLib.ItemHandling.upgrades import ITEM_UPGRADES_CLASSES, ItemUpgradeClass, ItemUpgradeId

@dataclass
class ItemProperty:
    modifier: DecodedModifier

    def describe(self) -> str:
        return f"ItemProperty | Modifier {self.modifier.identifier}"
    
    def is_valid(self) -> bool:
        return True
    
@dataclass
class ArmorProperty(ItemProperty):
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
class ArmorPlusAbove(ItemProperty):
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
class EnergyProperty(ItemProperty):
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
class EnergyPlusWhileDown(ItemProperty):
    energy: int
    health_threshold: int

    def describe(self) -> str:
        return f"+{self.energy} Health (while Health is below {self.health_threshold}%)"

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
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def describe(self) -> str:
        return f"PREFIX\n{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}"

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
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def describe(self) -> str:
        return f"SUFFIX\n{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}"

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
    upgrade_id: ItemUpgradeId
    
    def describe(self) -> str:
        return f"Unknown Upgrade (ID {self.upgrade_id})"

@dataclass
class InscriptionProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def describe(self) -> str:
        return f"INSCRIPTION\n{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}"
    
@dataclass
class UpgradeRuneProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def describe(self) -> str:
        return f"RUNE\n{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}\n"
    
@dataclass
class AppliesToRuneProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

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

def get_upgrade_property(modifier: DecodedModifier, modifiers: list[DecodedModifier]) -> ItemProperty:
    upgrade, upgrade_type = get_upgrade(modifier, modifiers)
    
    if upgrade:
        Py4GW.Console.Log("ItemHandling", f"Upgrade {upgrade.name} identified as type {upgrade_type.name}")
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
     

def get_upgrade(modifier : DecodedModifier, modifiers: list[DecodedModifier]) -> tuple["Upgrade", ItemUpgradeType]:
    creator_type, creator = next(((t, up) for t, up in _UPGRADE_FACTORY.items() if modifier.upgrade_id in t.id.values()), (UnknownUpgrade, None))    
    # creator_type, creator = next(((t, up) for t, up in _UPGRADE_FACTORY.items() if modifier.upgrade_id in t.id.values()), (UnknownUpgrade, None))    

    if creator is not None:
        Py4GW.Console.Log("ItemHandling", f"Found upgrade creator for ID {modifier.upgrade_id}: {creator.__name__} (Type: {creator_type.mod_type.name})")
        
        upgrade = creator(modifier, modifiers)
        if upgrade is not None:
            Py4GW.Console.Log("ItemHandling", f"Identified upgrade: {upgrade.name} (ID {modifier.upgrade_id})")
            return upgrade, creator_type.mod_type
    
    return UnknownUpgrade(), ItemUpgradeType.Unknown
        
        
class Upgrade:
    mod_type : ItemUpgradeType
    id : dict[ItemType, ItemUpgradeId]
    property_identifiers: list[ModifierIdentifier]
    properties: list[ItemProperty] = []
    
    names: dict[ServerLanguage, str] = {}
    descriptions: dict[ServerLanguage, str] = {}
    
    @classmethod
    def compose_from_modifiers(cls, modifiers: list[DecodedModifier]) -> Optional["Upgrade"]:        
        upgrade = cls()
        upgrade.properties = []
        
        Py4GW.Console.Log("ItemHandling", f"Composing upgrade {upgrade.__class__.__name__} from modifiers...")
        
        for prop_id in upgrade.property_identifiers:
            prop_mod = next((m for m in modifiers if m.identifier == prop_id), None)
            
            if prop_mod:
                prop = _PROPERTY_FACTORY.get(prop_id, lambda m, _: ItemProperty(modifier=m))(prop_mod, modifiers)
                upgrade.properties.append(prop)
            else:
                Py4GW.Console.Log("ItemHandling", f"Missing modifier for property {prop_id.name} in upgrade {upgrade.__class__.__name__}. Upgrade composition failed.")
                return None
        
        return upgrade

    @property
    def name(self) -> str:
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return self.names.get(server_language, self.names.get(ServerLanguage.English, self.__class__.__name__))
    
    @property
    def description(self) -> str:
        parts = [prop.describe() for prop in self.properties if prop.is_valid()]
        return "\n".join(parts)
    
    
class UnknownUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Unknown
    id = {}
    property_identifiers = []
    
#region Weapon Upgrades
#region Prefixes
class IcyUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Icy_Axe,
        ItemType.Bow: ItemUpgradeId.Icy_Bow,
        ItemType.Daggers: ItemUpgradeId.Icy_Daggers,
        ItemType.Hammer: ItemUpgradeId.Icy_Hammer,
        ItemType.Scythe: ItemUpgradeId.Icy_Scythe,
        ItemType.Spear: ItemUpgradeId.Icy_Spear,
        ItemType.Sword: ItemUpgradeId.Icy_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamageTypeProperty,
    ]

class EbonUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Ebon_Axe,
        ItemType.Bow: ItemUpgradeId.Ebon_Bow,
        ItemType.Daggers: ItemUpgradeId.Ebon_Daggers,
        ItemType.Hammer: ItemUpgradeId.Ebon_Hammer,
        ItemType.Scythe: ItemUpgradeId.Ebon_Scythe,
        ItemType.Spear: ItemUpgradeId.Ebon_Spear,
        ItemType.Sword: ItemUpgradeId.Ebon_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamageTypeProperty,
    ]
    
class ShockingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Shocking_Axe,
        ItemType.Bow: ItemUpgradeId.Shocking_Bow,
        ItemType.Daggers: ItemUpgradeId.Shocking_Daggers,
        ItemType.Hammer: ItemUpgradeId.Shocking_Hammer,
        ItemType.Scythe: ItemUpgradeId.Shocking_Scythe,
        ItemType.Spear: ItemUpgradeId.Shocking_Spear,
        ItemType.Sword: ItemUpgradeId.Shocking_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamageTypeProperty,
    ]
    
class FieryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Fiery_Axe,
        ItemType.Bow: ItemUpgradeId.Fiery_Bow,
        ItemType.Daggers: ItemUpgradeId.Fiery_Daggers,
        ItemType.Hammer: ItemUpgradeId.Fiery_Hammer,
        ItemType.Scythe: ItemUpgradeId.Fiery_Scythe,
        ItemType.Spear: ItemUpgradeId.Fiery_Spear,
        ItemType.Sword: ItemUpgradeId.Fiery_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamageTypeProperty,
    ]

class BarbedUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Barbed_Axe,
        ItemType.Bow: ItemUpgradeId.Barbed_Bow,
        ItemType.Daggers: ItemUpgradeId.Barbed_Daggers,
        ItemType.Scythe: ItemUpgradeId.Barbed_Scythe,
        ItemType.Spear: ItemUpgradeId.Barbed_Spear,
        ItemType.Sword: ItemUpgradeId.Barbed_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]

class CripplingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Crippling_Axe,
        ItemType.Bow: ItemUpgradeId.Crippling_Bow,
        ItemType.Daggers: ItemUpgradeId.Crippling_Daggers,
        ItemType.Scythe: ItemUpgradeId.Crippling_Scythe,
        ItemType.Spear: ItemUpgradeId.Crippling_Spear,
        ItemType.Sword: ItemUpgradeId.Crippling_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]
    
class CruelUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Cruel_Axe,
        ItemType.Daggers: ItemUpgradeId.Cruel_Daggers,
        ItemType.Hammer: ItemUpgradeId.Cruel_Hammer,
        ItemType.Scythe: ItemUpgradeId.Cruel_Scythe,
        ItemType.Spear: ItemUpgradeId.Cruel_Spear,
        ItemType.Sword: ItemUpgradeId.Cruel_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]

class PoisonousUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Poisonous_Axe,
        ItemType.Bow: ItemUpgradeId.Poisonous_Bow,
        ItemType.Daggers: ItemUpgradeId.Poisonous_Daggers,
        ItemType.Scythe: ItemUpgradeId.Poisonous_Scythe,
        ItemType.Spear: ItemUpgradeId.Poisonous_Spear,
        ItemType.Sword: ItemUpgradeId.Poisonous_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]

class SilencingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Bow: ItemUpgradeId.Silencing_Bow,
        ItemType.Daggers: ItemUpgradeId.Silencing_Daggers,
        ItemType.Spear: ItemUpgradeId.Silencing_Spear,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]
    
class FuriousUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Furious_Axe,
        ItemType.Daggers: ItemUpgradeId.Furious_Daggers,
        ItemType.Hammer: ItemUpgradeId.Furious_Hammer,
        ItemType.Scythe: ItemUpgradeId.Furious_Scythe,
        ItemType.Spear: ItemUpgradeId.Furious_Spear,
        ItemType.Sword: ItemUpgradeId.Furious_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.Furious,
    ]

class HeavyUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Heavy_Axe,
        ItemType.Hammer: ItemUpgradeId.Heavy_Hammer,
        ItemType.Scythe: ItemUpgradeId.Heavy_Scythe,
        ItemType.Spear: ItemUpgradeId.Heavy_Spear,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]

class ZealousUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Zealous_Axe,
        ItemType.Bow: ItemUpgradeId.Zealous_Bow,
        ItemType.Daggers: ItemUpgradeId.Zealous_Daggers,
        ItemType.Hammer: ItemUpgradeId.Zealous_Hammer,
        ItemType.Scythe: ItemUpgradeId.Zealous_Scythe,
        ItemType.Spear: ItemUpgradeId.Zealous_Spear,
        ItemType.Sword: ItemUpgradeId.Zealous_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyDegen,
        ModifierIdentifier.EnergyGainOnHit,
    ]

class VampiricUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Vampiric_Axe,
        ItemType.Bow: ItemUpgradeId.Vampiric_Bow,
        ItemType.Daggers: ItemUpgradeId.Vampiric_Daggers,
        ItemType.Hammer: ItemUpgradeId.Vampiric_Hammer,
        ItemType.Scythe: ItemUpgradeId.Vampiric_Scythe,
        ItemType.Spear: ItemUpgradeId.Vampiric_Spear,
        ItemType.Sword: ItemUpgradeId.Vampiric_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthDegen,
        ModifierIdentifier.HealthStealOnHit,
    ]

class SunderingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.Sundering_Axe,
        ItemType.Bow: ItemUpgradeId.Sundering_Bow,
        ItemType.Daggers: ItemUpgradeId.Sundering_Daggers,
        ItemType.Hammer: ItemUpgradeId.Sundering_Hammer,
        ItemType.Scythe: ItemUpgradeId.Sundering_Scythe,
        ItemType.Spear: ItemUpgradeId.Sundering_Spear,
        ItemType.Sword: ItemUpgradeId.Sundering_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPenetration,
    ]

class DefensiveUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.Defensive_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
    ]

class InsightfulUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.Insightful_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
    ]
    
class HaleUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.Hale_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlus,
    ]
#endregion Prefixes

#region Suffixes
class OfDefenseUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfDefense_Axe,
        ItemType.Bow: ItemUpgradeId.OfDefense_Bow,
        ItemType.Daggers: ItemUpgradeId.OfDefense_Daggers,
        ItemType.Hammer: ItemUpgradeId.OfDefense_Hammer,
        ItemType.Staff: ItemUpgradeId.OfDefense_Staff,
        ItemType.Scythe: ItemUpgradeId.OfDefense_Scythe,
        ItemType.Spear: ItemUpgradeId.OfDefense_Spear,
        ItemType.Sword: ItemUpgradeId.OfDefense_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
    ]

class OfWardingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfWarding_Axe,
        ItemType.Bow: ItemUpgradeId.OfWarding_Bow,
        ItemType.Daggers: ItemUpgradeId.OfWarding_Daggers,
        ItemType.Hammer: ItemUpgradeId.OfWarding_Hammer,
        ItemType.Staff: ItemUpgradeId.OfWarding_Staff,
        ItemType.Scythe: ItemUpgradeId.OfWarding_Scythe,
        ItemType.Spear: ItemUpgradeId.OfWarding_Spear,
        ItemType.Sword: ItemUpgradeId.OfWarding_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsElemental,
    ]

class OfShelterUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfShelter_Axe,
        ItemType.Bow: ItemUpgradeId.OfShelter_Bow,
        ItemType.Daggers: ItemUpgradeId.OfShelter_Daggers,
        ItemType.Hammer: ItemUpgradeId.OfShelter_Hammer,
        ItemType.Staff: ItemUpgradeId.OfShelter_Staff,
        ItemType.Scythe: ItemUpgradeId.OfShelter_Scythe,
        ItemType.Spear: ItemUpgradeId.OfShelter_Spear,
        ItemType.Sword: ItemUpgradeId.OfShelter_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]

class OfSlayingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfSlaying_Axe,
        ItemType.Bow: ItemUpgradeId.OfSlaying_Bow,
        ItemType.Hammer: ItemUpgradeId.OfSlaying_Hammer,
        ItemType.Sword: ItemUpgradeId.OfSlaying_Sword,
        ItemType.Staff: ItemUpgradeId.OfSlaying_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsSpecies,
    ]

class OfFortitudeUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfFortitude_Axe,
        ItemType.Bow: ItemUpgradeId.OfFortitude_Bow,
        ItemType.Daggers: ItemUpgradeId.OfFortitude_Daggers,
        ItemType.Hammer: ItemUpgradeId.OfFortitude_Hammer,
        ItemType.Staff: ItemUpgradeId.OfFortitude_Staff,
        ItemType.Scythe: ItemUpgradeId.OfFortitude_Scythe,
        ItemType.Spear: ItemUpgradeId.OfFortitude_Spear,
        ItemType.Sword: ItemUpgradeId.OfFortitude_Sword,
        ItemType.Offhand: ItemUpgradeId.OfFortitude_Focus,
        ItemType.Shield: ItemUpgradeId.OfFortitude_Shield,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlus,
    ]

class OfEnchantingUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfEnchanting_Axe,
        ItemType.Bow: ItemUpgradeId.OfEnchanting_Bow,
        ItemType.Daggers: ItemUpgradeId.OfEnchanting_Daggers,
        ItemType.Hammer: ItemUpgradeId.OfEnchanting_Hammer,
        ItemType.Staff: ItemUpgradeId.OfEnchanting_Staff,
        ItemType.Scythe: ItemUpgradeId.OfEnchanting_Scythe,
        ItemType.Spear: ItemUpgradeId.OfEnchanting_Spear,
        ItemType.Sword: ItemUpgradeId.OfEnchanting_Sword,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseEnchantmentDuration,
    ]

class OfTheProfessionUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Axe: ItemUpgradeId.OfTheProfession_Axe,
        ItemType.Bow: ItemUpgradeId.OfTheProfession_Bow,
        ItemType.Daggers: ItemUpgradeId.OfTheProfession_Daggers,
        ItemType.Hammer: ItemUpgradeId.OfTheProfession_Hammer,
        ItemType.Staff: ItemUpgradeId.OfTheProfession_Staff,
        ItemType.Scythe: ItemUpgradeId.OfTheProfession_Scythe,
        ItemType.Spear: ItemUpgradeId.OfTheProfession_Spear,
        ItemType.Sword: ItemUpgradeId.OfTheProfession_Sword,
        ItemType.Wand: ItemUpgradeId.OfTheProfession_Wand,
    }
    
    property_identifiers = [
        ModifierIdentifier.OfTheProfession,
    ]

class OfAxeMasteryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Axe: ItemUpgradeId.OfAxeMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfMarksmanshipUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Bow: ItemUpgradeId.OfMarksmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfDaggerMasteryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Daggers: ItemUpgradeId.OfDaggerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfAptitudeUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Offhand: ItemUpgradeId.OfAptitude_Focus,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]

class OfDevotionUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Shield: ItemUpgradeId.OfDevotion_Shield,
        ItemType.Offhand: ItemUpgradeId.OfDevotion_Focus,
        ItemType.Staff: ItemUpgradeId.OfDevotion_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlusEnchanted,
    ]

class OfValorUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Offhand: ItemUpgradeId.OfValor_Focus,
        ItemType.Shield: ItemUpgradeId.OfValor_Shield,
        ItemType.Staff: ItemUpgradeId.OfValor_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlusHexed,
    ]

class OfEnduranceUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Offhand: ItemUpgradeId.OfEndurance_Focus,
        ItemType.Shield: ItemUpgradeId.OfEndurance_Shield,
        ItemType.Staff: ItemUpgradeId.OfEndurance_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlusStance,
    ]

class OfSwiftnessUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Offhand: ItemUpgradeId.OfSwiftness_Focus,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]

class OfHammerMasteryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Hammer: ItemUpgradeId.OfHammerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfScytheMasteryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Scythe: ItemUpgradeId.OfScytheMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    
class OfSpearMasteryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Spear: ItemUpgradeId.OfSpearMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfSwordsmanshipUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Sword: ItemUpgradeId.OfSwordsmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfAttributeUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.OfAttribute_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    
class OfMasteryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.OfMastery_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOneItem,
    ]

class SwiftStaffUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.Swift_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]

class AdeptStaffUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Staff: ItemUpgradeId.Adept_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]

class OfMemoryUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Wand: ItemUpgradeId.OfMemory_Wand,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeItemAttribute,
    ]

class OfQuickeningUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Wand: ItemUpgradeId.OfQuickening_Wand,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]
#endregion Suffixes

#region Inscriptions
#region Offhand
class BeJustAndFearNot(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.BeJustAndFearNot,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusHexed,
    ]

class DownButNotOut(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.DownButNotOut,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusWhileDown
    ]

class FaithIsMyShield(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.FaithIsMyShield,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusEnchanted,
    ]

class ForgetMeNot(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.ForgetMeNot,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeItemAttribute,
    ]

class HailToTheKing(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.HailToTheKing,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusAbove,
    ]

class IgnoranceIsBliss(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.IgnoranceIsBliss,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
        ModifierIdentifier.EnergyMinus,
    ]

class KnowingIsHalfTheBattle(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.KnowingIsHalfTheBattle,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusCasting,
    ]

class LifeIsPain(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.LifeIsPain,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
        ModifierIdentifier.HealthMinus,
    ]

class LiveForToday(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.LiveForToday,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
        ModifierIdentifier.EnergyDegen,
    ]

class ManForAllSeasons(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.ManForAllSeasons,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsElemental,
    ]

class MightMakesRight(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.MightMakesRight,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusAttacking,
    ]

class SerenityNow(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.SerenityNow,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]

class SurvivalOfTheFittest(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Offhand: ItemUpgradeId.SurvivalOfTheFittest,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]
#endregion Offhand

#region Weapon

class BrawnOverBrains(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.BrawnOverBrains,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusPercent,
        ModifierIdentifier.EnergyMinus,
    ]

class DanceWithDeath(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.DanceWithDeath,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusStance,
    ]

class DontFearTheReaper(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.DontFearTheReaper,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusHexed,
    ]

class DontThinkTwice(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.DontThinkTwice,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]

class GuidedByFate(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.GuidedByFate,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusEnchanted,
    ]

class StrengthAndHonor(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.StrengthAndHonor,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusWhileUp,
    ]

class ToThePain(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.ToThePain,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusPercent,
        ModifierIdentifier.ArmorMinusAttacking
    ]

class TooMuchInformation(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.TooMuchInformation,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusVsHexed,
    ]

class VengeanceIsMine(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.Weapon: ItemUpgradeId.VengeanceIsMine,
    }
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusWhileDown,
    ]

#endregion Weapon

#region MartialWeapon
class IHaveThePower(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.MartialWeapon: ItemUpgradeId.IHaveThePower,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
    ]

class LetTheMemoryLiveAgain(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.MartialWeapon: ItemUpgradeId.LetTheMemoryLiveAgain,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]

#endregion MartialWeapon

#region OffhandOrShield
class CastOutTheUnclean(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.CastOutTheUnclean,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class FearCutsDeeper(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.FearCutsDeeper,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]


class ICanSeeClearlyNow(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.ICanSeeClearlyNow,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,   
    ]

class LeafOnTheWind(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.LeafOnTheWind,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class LikeARollingStone(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.LikeARollingStone,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class LuckOfTheDraw(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.LuckOfTheDraw,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReceiveLessDamage,
    ]

class MasterOfMyDomain(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.MasterOfMyDomain,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOneItem,
    ]

class NotTheFace(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.NotTheFace,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage
    ]

class NothingToFear(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.NothingToFear,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageHexed,
    ]

class OnlyTheStrongSurvive(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.OnlyTheStrongSurvive,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class PureOfHeart(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.PureOfHeart,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class RidersOnTheStorm(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.RidersOnTheStorm,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class RunForYourLife(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.RunForYourLife,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageStance,
    ]

class ShelteredByFaith(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.ShelteredByFaith,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageEnchanted,
    ]

class SleepNowInTheFire(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.SleepNowInTheFire,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class SoundnessOfMind(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.SoundnessOfMind,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class StrengthOfBody(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.StrengthOfBody,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class SwiftAsTheWind(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.SwiftAsTheWind,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class TheRiddleOfSteel(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.TheRiddleOfSteel,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class ThroughThickAndThin(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.OffhandOrShield: ItemUpgradeId.ThroughThickAndThin,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
#endregion OffhandOrShield

#region EquippableItem
class MeasureForMeasure(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.EquippableItem: ItemUpgradeId.MeasureForMeasure,
    }
    
    property_identifiers = [
        ModifierIdentifier.HighlySalvageable,
    ]
    
class ShowMeTheMoney(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.EquippableItem: ItemUpgradeId.ShowMeTheMoney,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreasedSaleValue,
    ]    
#endregion EquippableItem

#region SpellcastingWeapon
class AptitudeNotAttitude(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.SpellcastingWeapon: ItemUpgradeId.AptitudeNotAttitude,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]

class DontCallItAComeback(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.SpellcastingWeapon: ItemUpgradeId.DontCallItAComeback,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlusWhileBelow,
    ]

class HaleAndHearty(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.SpellcastingWeapon: ItemUpgradeId.HaleAndHearty,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlusWhileDown,
    ]

class HaveFaith(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.SpellcastingWeapon: ItemUpgradeId.HaveFaith,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlusEnchanted,
    ]

class IAmSorrow(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.SpellcastingWeapon: ItemUpgradeId.IAmSorrow,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlusHexed,
    ]

class SeizeTheDay(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    id = {
        ItemType.SpellcastingWeapon: ItemUpgradeId.SeizeTheDay,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
        ModifierIdentifier.EnergyDegen,
    ]
#endregion SpellcastingWeapon
#endregion Inscriptions

#endregion Weapon Upgrades

#region Armor Upgrades
#region Prefixes
class SurvivorInsignia(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Survivor,
        ItemType.Chestpiece: ItemUpgradeId.Survivor,
        ItemType.Gloves: ItemUpgradeId.Survivor,
        ItemType.Leggings: ItemUpgradeId.Survivor,
        ItemType.Boots: ItemUpgradeId.Survivor,
    }
    
    property_identifiers = []
#endregion Prefixes

#region Suffixes
#endregion Suffixes
#endregion Armor Upgrades

_UPGRADE_FACTORY: dict[type[Upgrade], Callable[[DecodedModifier, list[DecodedModifier]], Optional[Upgrade]]] = {
    IcyUpgrade: lambda mod, mods: IcyUpgrade.compose_from_modifiers(mods),
    EbonUpgrade: lambda mod, mods: EbonUpgrade.compose_from_modifiers(mods),
    ShockingUpgrade: lambda mod, mods: ShockingUpgrade.compose_from_modifiers(mods),
    FieryUpgrade: lambda mod, mods: FieryUpgrade.compose_from_modifiers(mods),
    BarbedUpgrade: lambda mod, mods: BarbedUpgrade.compose_from_modifiers(mods),
    CripplingUpgrade: lambda mod, mods: CripplingUpgrade.compose_from_modifiers(mods),
    CruelUpgrade: lambda mod, mods: CruelUpgrade.compose_from_modifiers(mods),
    PoisonousUpgrade: lambda mod, mods: PoisonousUpgrade.compose_from_modifiers(mods),
    SilencingUpgrade: lambda mod, mods: SilencingUpgrade.compose_from_modifiers(mods),
    FuriousUpgrade: lambda mod, mods: FuriousUpgrade.compose_from_modifiers(mods),
    HeavyUpgrade: lambda mod, mods: HeavyUpgrade.compose_from_modifiers(mods),
    ZealousUpgrade: lambda mod, mods: ZealousUpgrade.compose_from_modifiers(mods),
    VampiricUpgrade: lambda mod, mods: VampiricUpgrade.compose_from_modifiers(mods),
    SunderingUpgrade: lambda mod, mods: SunderingUpgrade.compose_from_modifiers(mods),
    DefensiveUpgrade: lambda mod, mods: DefensiveUpgrade.compose_from_modifiers(mods),
    InsightfulUpgrade: lambda mod, mods: InsightfulUpgrade.compose_from_modifiers(mods),
    HaleUpgrade: lambda mod, mods: HaleUpgrade.compose_from_modifiers(mods),    
    OfDefenseUpgrade: lambda mod, mods: OfDefenseUpgrade.compose_from_modifiers(mods),
    OfWardingUpgrade: lambda mod, mods: OfWardingUpgrade.compose_from_modifiers(mods),
    OfShelterUpgrade: lambda mod, mods: OfShelterUpgrade.compose_from_modifiers(mods),
    OfSlayingUpgrade: lambda mod, mods: OfSlayingUpgrade.compose_from_modifiers(mods),
    OfFortitudeUpgrade: lambda mod, mods: OfFortitudeUpgrade.compose_from_modifiers(mods),
    OfEnchantingUpgrade: lambda mod, mods: OfEnchantingUpgrade.compose_from_modifiers(mods),
    OfTheProfessionUpgrade: lambda mod, mods: OfTheProfessionUpgrade.compose_from_modifiers(mods),
    OfAxeMasteryUpgrade: lambda mod, mods: OfAxeMasteryUpgrade.compose_from_modifiers(mods),
    OfMarksmanshipUpgrade: lambda mod, mods: OfMarksmanshipUpgrade.compose_from_modifiers(mods),
    OfDaggerMasteryUpgrade: lambda mod, mods: OfDaggerMasteryUpgrade.compose_from_modifiers(mods),
    OfHammerMasteryUpgrade: lambda mod, mods: OfHammerMasteryUpgrade.compose_from_modifiers(mods),
    OfScytheMasteryUpgrade: lambda mod, mods: OfScytheMasteryUpgrade.compose_from_modifiers(mods),
    OfSpearMasteryUpgrade: lambda mod, mods: OfSpearMasteryUpgrade.compose_from_modifiers(mods),
    OfSwordsmanshipUpgrade: lambda mod, mods: OfSwordsmanshipUpgrade.compose_from_modifiers(mods),
    OfAttributeUpgrade: lambda mod, mods: OfAttributeUpgrade.compose_from_modifiers(mods),
    OfMasteryUpgrade: lambda mod, mods: OfMasteryUpgrade.compose_from_modifiers(mods),  
    SwiftStaffUpgrade: lambda mod, mods: SwiftStaffUpgrade.compose_from_modifiers(mods),
    AdeptStaffUpgrade: lambda mod, mods: AdeptStaffUpgrade.compose_from_modifiers(mods),
    OfMemoryUpgrade: lambda mod, mods: OfMemoryUpgrade.compose_from_modifiers(mods),
    OfQuickeningUpgrade: lambda mod, mods: OfQuickeningUpgrade.compose_from_modifiers(mods),
    
    BeJustAndFearNot: lambda mod, mods: BeJustAndFearNot.compose_from_modifiers(mods),
    DownButNotOut: lambda mod, mods: DownButNotOut.compose_from_modifiers(mods),
    FaithIsMyShield: lambda mod, mods: FaithIsMyShield.compose_from_modifiers(mods),
    ForgetMeNot: lambda mod, mods: ForgetMeNot.compose_from_modifiers(mods),
    HailToTheKing: lambda mod, mods: HailToTheKing.compose_from_modifiers(mods),
    IgnoranceIsBliss: lambda mod, mods: IgnoranceIsBliss.compose_from_modifiers(mods),
    KnowingIsHalfTheBattle: lambda mod, mods: KnowingIsHalfTheBattle.compose_from_modifiers(mods),
    LifeIsPain: lambda mod, mods: LifeIsPain.compose_from_modifiers(mods),
    LiveForToday: lambda mod, mods: LiveForToday.compose_from_modifiers(mods),
    ManForAllSeasons: lambda mod, mods: ManForAllSeasons.compose_from_modifiers(mods),
    MightMakesRight: lambda mod, mods: MightMakesRight.compose_from_modifiers(mods),
    SerenityNow: lambda mod, mods: SerenityNow.compose_from_modifiers(mods),        
    SurvivalOfTheFittest: lambda mod, mods: SurvivalOfTheFittest.compose_from_modifiers(mods),
    BrawnOverBrains: lambda mod, mods: BrawnOverBrains.compose_from_modifiers(mods),
    DanceWithDeath: lambda mod, mods: DanceWithDeath.compose_from_modifiers(mods),
    DontFearTheReaper: lambda mod, mods: DontFearTheReaper.compose_from_modifiers(mods),
    DontThinkTwice: lambda mod, mods: DontThinkTwice.compose_from_modifiers(mods),
    GuidedByFate: lambda mod, mods: GuidedByFate.compose_from_modifiers(mods),
    StrengthAndHonor: lambda mod, mods: StrengthAndHonor.compose_from_modifiers(mods),
    ToThePain: lambda mod, mods: ToThePain.compose_from_modifiers(mods),
    TooMuchInformation: lambda mod, mods: TooMuchInformation.compose_from_modifiers(mods),
    VengeanceIsMine: lambda mod, mods: VengeanceIsMine.compose_from_modifiers(mods),
    IHaveThePower: lambda mod, mods: IHaveThePower.compose_from_modifiers(mods),
    LetTheMemoryLiveAgain: lambda mod, mods: LetTheMemoryLiveAgain.compose_from_modifiers(mods),
    CastOutTheUnclean: lambda mod, mods: CastOutTheUnclean.compose_from_modifiers(mods),
    FearCutsDeeper: lambda mod, mods: FearCutsDeeper.compose_from_modifiers(mods),
    ICanSeeClearlyNow: lambda mod, mods: ICanSeeClearlyNow.compose_from_modifiers(mods),
    LeafOnTheWind: lambda mod, mods: LeafOnTheWind.compose_from_modifiers(mods),
    LikeARollingStone: lambda mod, mods: LikeARollingStone.compose_from_modifiers(mods),
    LuckOfTheDraw: lambda mod, mods: LuckOfTheDraw.compose_from_modifiers(mods),
    MasterOfMyDomain: lambda mod, mods: MasterOfMyDomain.compose_from_modifiers(mods),
    NotTheFace: lambda mod, mods: NotTheFace.compose_from_modifiers(mods),
    NothingToFear: lambda mod, mods: NothingToFear.compose_from_modifiers(mods),
    OnlyTheStrongSurvive: lambda mod, mods: OnlyTheStrongSurvive.compose_from_modifiers(mods),
    PureOfHeart: lambda mod, mods: PureOfHeart.compose_from_modifiers(mods  ),
    RidersOnTheStorm: lambda mod, mods: RidersOnTheStorm.compose_from_modifiers(mods),
    RunForYourLife: lambda mod, mods: RunForYourLife.compose_from_modifiers(mods),
    ShelteredByFaith: lambda mod, mods: ShelteredByFaith.compose_from_modifiers(mods),
    SleepNowInTheFire: lambda mod, mods: SleepNowInTheFire.compose_from_modifiers(mods),
    SoundnessOfMind: lambda mod, mods: SoundnessOfMind.compose_from_modifiers(mods),
    StrengthOfBody: lambda mod, mods: StrengthOfBody.compose_from_modifiers(mods),
    SwiftAsTheWind: lambda mod, mods: SwiftAsTheWind.compose_from_modifiers(mods),
    TheRiddleOfSteel: lambda mod, mods: TheRiddleOfSteel.compose_from_modifiers(mods),
    ThroughThickAndThin: lambda mod, mods: ThroughThickAndThin.compose_from_modifiers(mods),
    MeasureForMeasure: lambda mod, mods: MeasureForMeasure.compose_from_modifiers(mods),
    ShowMeTheMoney: lambda mod, mods: ShowMeTheMoney.compose_from_modifiers(mods),
    AptitudeNotAttitude: lambda mod, mods: AptitudeNotAttitude.compose_from_modifiers(mods),
    DontCallItAComeback: lambda mod, mods: DontCallItAComeback.compose_from_modifiers(mods),
    HaleAndHearty: lambda mod, mods: HaleAndHearty.compose_from_modifiers(mods),
    HaveFaith: lambda mod, mods: HaveFaith.compose_from_modifiers(mods),
    IAmSorrow: lambda mod, mods: IAmSorrow.compose_from_modifiers(mods),
    SeizeTheDay: lambda mod, mods: SeizeTheDay.compose_from_modifiers(mods),
}    

_PROPERTY_FACTORY: dict[ModifierIdentifier, Callable[[DecodedModifier, list[DecodedModifier]], ItemProperty]] = {
    ModifierIdentifier.Armor1: lambda m, _: ArmorProperty(modifier=m, armor=m.arg1),
    ModifierIdentifier.Armor2: lambda m, _: ArmorProperty(modifier=m, armor=m.arg1),
    ModifierIdentifier.ArmorEnergyRegen: lambda m, _: ArmorEnergyRegen(modifier=m, energy_regen=m.arg1),
    ModifierIdentifier.ArmorMinusAttacking: lambda m, _: ArmorMinusAttacking(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPenetration: lambda m, _: ArmorPenetration(modifier=m, armor_pen=m.arg2, chance=m.arg1),
    ModifierIdentifier.ArmorPlus: lambda m, _: ArmorPlus(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusAttacking: lambda m, _: ArmorPlusAttacking(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusCasting: lambda m, _: ArmorPlusCasting(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusEnchanted: lambda m, _: ArmorPlusEnchanted(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusHexed: lambda m, _: ArmorPlusHexed(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusAbove: lambda m, _: ArmorPlusAbove(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsDamage: lambda m, _: ArmorPlusVsDamage(modifier=m, armor=m.arg2, damage_type=DamageType(m.arg1)),
    ModifierIdentifier.ArmorPlusVsElemental: lambda m, _: ArmorPlusVsElemental(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsPhysical: lambda m, _: ArmorPlusVsPhysical(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsPhysical2: lambda m, _: ArmorPlusVsPhysical(modifier=m, armor=m.arg2),
    ModifierIdentifier.ArmorPlusVsSpecies: lambda m, _: ArmorPlusVsSpecies(modifier=m, armor=m.arg2, species=ItemBaneSpecies(m.arg1)),
    ModifierIdentifier.ArmorPlusWhileDown: lambda m, _: ArmorPlusWhileDown(modifier=m, armor=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.AttributePlusOne: lambda m, _: AttributePlusOne(modifier=m, attribute=Attribute(m.arg1), chance=m.arg2),
    ModifierIdentifier.AttributePlusOneItem: lambda m, _: AttributePlusOneItem(modifier=m, chance=m.arg2),
    ModifierIdentifier.AttributeRequirement: lambda m, _: AttributeRequirement(modifier=m, attribute=Attribute(m.arg1), attribute_level=m.arg2),
    ModifierIdentifier.BaneSpecies: lambda m, _: BaneProperty(modifier=m, species=ItemBaneSpecies(m.arg1)),
    ModifierIdentifier.Damage: lambda m, _: DamageProperty(modifier=m, min_damage=m.arg2, max_damage=m.arg1),
    ModifierIdentifier.Damage2: lambda m, _: DamageProperty(modifier=m, min_damage=m.arg2, max_damage=m.arg1),
    ModifierIdentifier.DamageCustomized: lambda m, _: DamageCustomized(modifier=m, damage_increase=m.arg1 - 100),
    ModifierIdentifier.DamagePlusEnchanted: lambda m, _: DamagePlusEnchanted(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusHexed: lambda m, _: DamagePlusHexed(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusPercent: lambda m, _: DamagePlusPercent(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusStance: lambda m, _: DamagePlusStance(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusVsHexed: lambda m, _: DamagePlusVsHexed(modifier=m, damage_increase=m.arg2),
    ModifierIdentifier.DamagePlusVsSpecies: lambda m, _: DamagePlusVsSpecies(modifier=m, damage_increase=m.arg1, species=ItemBaneSpecies(m.arg2)),
    ModifierIdentifier.DamagePlusWhileDown: lambda m, _: DamagePlusWhileDown(modifier=m, damage_increase=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.DamagePlusWhileUp: lambda m, _: DamagePlusWhileUp(modifier=m, damage_increase=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.DamageTypeProperty: lambda m, _: DamageTypeProperty(modifier=m, damage_type=DamageType(m.arg1)),
    ModifierIdentifier.Energy: lambda m, _: EnergyProperty(modifier=m, energy=m.arg1),
    ModifierIdentifier.Energy2: lambda m, _: EnergyProperty(modifier=m, energy=m.arg1),
    ModifierIdentifier.EnergyDegen: lambda m, _: EnergyDegen(modifier=m, energy_regen=m.arg2),
    ModifierIdentifier.EnergyGainOnHit: lambda m, _: EnergyGainOnHit(modifier=m, energy_gain=m.arg2),
    ModifierIdentifier.EnergyMinus: lambda m, _: EnergyMinus(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlus : lambda m, _: EnergyPlus(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlusEnchanted: lambda m, _: EnergyPlusEnchanted(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlusHexed: lambda m, _: EnergyPlusHexed(modifier=m, energy=m.arg2),
    ModifierIdentifier.EnergyPlusWhileBelow: lambda m, _: EnergyPlusWhileBelow(modifier=m, energy=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.EnergyPlusWhileDown: lambda m, _: EnergyPlusWhileDown(modifier=m, energy=m.arg2, health_threshold=m.arg1),
    ModifierIdentifier.Furious: lambda m, _: Furious(modifier=m, chance=m.arg2),
    ModifierIdentifier.HalvesCastingTimeAttribute: lambda m, _: HalvesCastingTimeAttribute(modifier=m, chance=m.arg1, attribute=Attribute(m.arg2)),
    ModifierIdentifier.HalvesCastingTimeGeneral: lambda m, _: HalvesCastingTimeGeneral(modifier=m, chance=m.arg1),
    ModifierIdentifier.HalvesCastingTimeItemAttribute: lambda m, _: HalvesCastingTimeItemAttribute(modifier=m, chance=m.arg1),
    ModifierIdentifier.HalvesSkillRechargeAttribute: lambda m, _: HalvesSkillRechargeAttribute(modifier=m, chance=m.arg1, attribute=Attribute(m.arg2)),
    ModifierIdentifier.HalvesSkillRechargeGeneral: lambda m, _: HalvesSkillRechargeGeneral(modifier=m, chance=m.arg1),
    ModifierIdentifier.HalvesSkillRechargeItemAttribute: lambda m, _: HalvesSkillRechargeItemAttribute(modifier=m, chance=m.arg1),
    ModifierIdentifier.HeadpieceAttribute: lambda m, _: HeadpieceAttribute(modifier=m, attribute=Attribute(m.arg1), attribute_level=m.arg2),
    ModifierIdentifier.HeadpieceGenericAttribute: lambda m, _: HeadpieceGenericAttribute(modifier=m),
    ModifierIdentifier.HealthDegen: lambda m, _: HealthDegen(modifier=m, health_regen=m.arg2),
    ModifierIdentifier.HealthMinus: lambda m, _: HealthMinus(modifier=m, health=m.arg2),
    ModifierIdentifier.HealthPlus: lambda m, _: HealthPlus(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlus2 : lambda m, _: HealthPlus(modifier=m, health=m.arg2),
    ModifierIdentifier.HealthPlusEnchanted: lambda m, _: HealthPlusEnchanted(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlusHexed: lambda m, _: HealthPlusHexed(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthPlusStance: lambda m, _: HealthPlusStance(modifier=m, health=m.arg1),
    ModifierIdentifier.HealthStealOnHit: lambda m, _: HealthStealOnHit(modifier=m, health_steal=m.arg1),
    ModifierIdentifier.HighlySalvageable: lambda m, _: HighlySalvageable(modifier=m),
    ModifierIdentifier.IncreaseConditionDuration: lambda m, _: IncreaseConditionDuration(modifier=m, condition=Ailment(m.arg2)),
    ModifierIdentifier.IncreaseEnchantmentDuration: lambda m, _: IncreaseEnchantmentDuration(modifier=m, enchantment_duration=m.arg2),
    ModifierIdentifier.IncreasedSaleValue: lambda m, _: IncreasedSaleValue(modifier=m),
    ModifierIdentifier.Infused: lambda m, _: Infused(modifier=m),
    ModifierIdentifier.OfTheProfession: lambda m, _: OfTheProfession(modifier=m, attribute=Attribute(m.arg1), attribute_level=m.arg2, profession=get_profession_from_attribute(Attribute(m.arg1)) or Profession._None),
    ModifierIdentifier.ReceiveLessPhysDamageEnchanted: lambda m, _: ReceiveLessPhysDamageEnchanted(modifier=m, damage_reduction=m.arg2),
    ModifierIdentifier.ReceiveLessPhysDamageHexed: lambda m, _: ReceiveLessPhysDamageHexed(modifier=m, damage_reduction=m.arg2),
    ModifierIdentifier.ReceiveLessPhysDamageStance: lambda m, _: ReceiveLessPhysDamageStance(modifier=m, damage_reduction=m.arg2),
    ModifierIdentifier.ReduceConditionDuration: lambda m, _: ReduceConditionDuration(modifier=m, condition=Reduced_Ailment(m.arg1)),
    ModifierIdentifier.ReduceConditionTupleDuration: lambda m, _: ReduceConditionTupleDuration(modifier=m, condition_1=Reduced_Ailment(m.arg2), condition_2=Reduced_Ailment(m.arg1)),
    ModifierIdentifier.ReducesDiseaseDuration: lambda m, _: ReducesDiseaseDuration(modifier=m),
    ModifierIdentifier.ReceiveLessDamage: lambda m, _: ReceiveLessDamage(modifier=m, damage_reduction=m.arg2, chance=m.arg1),
    ModifierIdentifier.Upgrade1: lambda m, mods: get_upgrade_property(m, mods),
    ModifierIdentifier.Upgrade2: lambda m, mods: get_upgrade_property(m, mods),
}

