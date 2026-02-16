from dataclasses import dataclass
from typing import Callable, Optional

import Py4GW

from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, ProfessionAttributes, Reduced_Ailment
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
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
    creator_type = next((t for t in _UPGRADES if modifier.upgrade_id in t.id.values()), None)    
    # creator_type, creator = next(((t, up) for t, up in _UPGRADE_FACTORY.items() if modifier.upgrade_id in t.id.values()), (UnknownUpgrade, None))    

    if creator_type is not None:        
        upgrade = creator_type.compose_from_modifiers(modifier, modifiers)
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
    def compose_from_modifiers(cls, mod : DecodedModifier, modifiers: list[DecodedModifier]) -> Optional["Upgrade"]:        
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

class Insignia(Upgrade):
    mod_type = ItemUpgradeType.Prefix
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None

class Rune(Upgrade):
    mod_type = ItemUpgradeType.Suffix
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    
class AttributeRune(Rune):
    attribute : Attribute
    attribute_level : int

    @classmethod
    def compose_from_modifiers(cls, mod : DecodedModifier, modifiers: list[DecodedModifier]) -> Optional["AttributeRune"]:        
        upgrade = cls()
        upgrade.properties = []
        
        cls.attribute = Attribute(mod.arg1)
        cls.attribute_level = mod.arg2
        
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
    def description(self) -> str:
        parts = [prop.describe() for prop in self.properties if prop.is_valid()]
        return f"+ {self.attribute_level} {AttributeNames.get(self.attribute)}\n" + "\n".join(parts)

    
#region No Profession
class SurvivorInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Survivor,
        ItemType.Chestpiece: ItemUpgradeId.Survivor,
        ItemType.Gloves: ItemUpgradeId.Survivor,
        ItemType.Leggings: ItemUpgradeId.Survivor,
        ItemType.Boots: ItemUpgradeId.Survivor,
    }
    
    property_identifiers = []
    
class RadiantInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Radiant,
        ItemType.Chestpiece: ItemUpgradeId.Radiant,
        ItemType.Gloves: ItemUpgradeId.Radiant,
        ItemType.Leggings: ItemUpgradeId.Radiant,
        ItemType.Boots: ItemUpgradeId.Radiant,
    }
    
    property_identifiers = []
    
class StalwartInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Stalwart,
        ItemType.Chestpiece: ItemUpgradeId.Stalwart,
        ItemType.Gloves: ItemUpgradeId.Stalwart,
        ItemType.Leggings: ItemUpgradeId.Stalwart,
        ItemType.Boots: ItemUpgradeId.Stalwart,
    }
    
    property_identifiers = []

class BrawlersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Brawlers,
        ItemType.Chestpiece: ItemUpgradeId.Brawlers,
        ItemType.Gloves: ItemUpgradeId.Brawlers,
        ItemType.Leggings: ItemUpgradeId.Brawlers,
        ItemType.Boots: ItemUpgradeId.Brawlers,
    }
    
    property_identifiers = []
    
class BlessedInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Blessed,
        ItemType.Chestpiece: ItemUpgradeId.Blessed,
        ItemType.Gloves: ItemUpgradeId.Blessed,
        ItemType.Leggings: ItemUpgradeId.Blessed,
        ItemType.Boots: ItemUpgradeId.Blessed,
    }
    
    property_identifiers = []
    
class HeraldsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Heralds,
        ItemType.Chestpiece: ItemUpgradeId.Heralds,
        ItemType.Gloves: ItemUpgradeId.Heralds,
        ItemType.Leggings: ItemUpgradeId.Heralds,
        ItemType.Boots: ItemUpgradeId.Heralds,
    }
    
    property_identifiers = []
    
class SentrysInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Sentrys,
        ItemType.Chestpiece: ItemUpgradeId.Sentrys,
        ItemType.Gloves: ItemUpgradeId.Sentrys,
        ItemType.Leggings: ItemUpgradeId.Sentrys,
        ItemType.Boots: ItemUpgradeId.Sentrys,
    }
    
    property_identifiers = []
    
class RuneOfMinorVigor(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorVigor,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorVigor,
        ItemType.Gloves: ItemUpgradeId.OfMinorVigor,
        ItemType.Leggings: ItemUpgradeId.OfMinorVigor,
        ItemType.Boots: ItemUpgradeId.OfMinorVigor,
    }
    
    property_identifiers = []
    
class RuneOfMinorVigor2(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorVigor2,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorVigor2,
        ItemType.Gloves: ItemUpgradeId.OfMinorVigor2,
        ItemType.Leggings: ItemUpgradeId.OfMinorVigor2,
        ItemType.Boots: ItemUpgradeId.OfMinorVigor2,
    }
    
    property_identifiers = []

class RuneOfVitae(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfVitae,
        ItemType.Chestpiece: ItemUpgradeId.OfVitae,
        ItemType.Gloves: ItemUpgradeId.OfVitae,
        ItemType.Leggings: ItemUpgradeId.OfVitae,
        ItemType.Boots: ItemUpgradeId.OfVitae,
    }
    
    property_identifiers = []

class RuneOfAttunement(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfAttunement,
        ItemType.Chestpiece: ItemUpgradeId.OfAttunement,
        ItemType.Gloves: ItemUpgradeId.OfAttunement,
        ItemType.Leggings: ItemUpgradeId.OfAttunement,
        ItemType.Boots: ItemUpgradeId.OfAttunement,
    }
    
    property_identifiers = []

class RuneOfMajorVigor(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorVigor,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorVigor,
        ItemType.Gloves: ItemUpgradeId.OfMajorVigor,
        ItemType.Leggings: ItemUpgradeId.OfMajorVigor,
        ItemType.Boots: ItemUpgradeId.OfMajorVigor,
    }
    
    property_identifiers = []

class RuneOfRecovery(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfRecovery,
        ItemType.Chestpiece: ItemUpgradeId.OfRecovery,
        ItemType.Gloves: ItemUpgradeId.OfRecovery,
        ItemType.Leggings: ItemUpgradeId.OfRecovery,
        ItemType.Boots: ItemUpgradeId.OfRecovery,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfRestoration(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfRestoration,
        ItemType.Chestpiece: ItemUpgradeId.OfRestoration,
        ItemType.Gloves: ItemUpgradeId.OfRestoration,
        ItemType.Leggings: ItemUpgradeId.OfRestoration,
        ItemType.Boots: ItemUpgradeId.OfRestoration,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfClarity(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfClarity,
        ItemType.Chestpiece: ItemUpgradeId.OfClarity,
        ItemType.Gloves: ItemUpgradeId.OfClarity,
        ItemType.Leggings: ItemUpgradeId.OfClarity,
        ItemType.Boots: ItemUpgradeId.OfClarity,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]
    
class RuneOfPurity(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfPurity,
        ItemType.Chestpiece: ItemUpgradeId.OfPurity,
        ItemType.Gloves: ItemUpgradeId.OfPurity,
        ItemType.Leggings: ItemUpgradeId.OfPurity,
        ItemType.Boots: ItemUpgradeId.OfPurity,
    }
    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfSuperiorVigor(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorVigor,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorVigor,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorVigor,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorVigor,
        ItemType.Boots: ItemUpgradeId.OfSuperiorVigor,
    }
    
    property_identifiers = []
#endregion No Profession

#region Warrior
class KnightsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Knights,
        ItemType.Chestpiece: ItemUpgradeId.Knights,
        ItemType.Gloves: ItemUpgradeId.Knights,
        ItemType.Leggings: ItemUpgradeId.Knights,
        ItemType.Boots: ItemUpgradeId.Knights,
    }
    
    property_identifiers = []
    
class LieutenantsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Lieutenants,
        ItemType.Chestpiece: ItemUpgradeId.Lieutenants,
        ItemType.Gloves: ItemUpgradeId.Lieutenants,
        ItemType.Leggings: ItemUpgradeId.Lieutenants,
        ItemType.Boots: ItemUpgradeId.Lieutenants,
    }
    
    property_identifiers = []
    
class StonefistInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Stonefist,
        ItemType.Chestpiece: ItemUpgradeId.Stonefist,
        ItemType.Gloves: ItemUpgradeId.Stonefist,
        ItemType.Leggings: ItemUpgradeId.Stonefist,
        ItemType.Boots: ItemUpgradeId.Stonefist,
    }
    
    property_identifiers = []
    
class DreadnoughtInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Dreadnought,
        ItemType.Chestpiece: ItemUpgradeId.Dreadnought,
        ItemType.Gloves: ItemUpgradeId.Dreadnought,
        ItemType.Leggings: ItemUpgradeId.Dreadnought,
        ItemType.Boots: ItemUpgradeId.Dreadnought,
    }
    
    property_identifiers = []
    
class SentinelsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Sentinels,
        ItemType.Chestpiece: ItemUpgradeId.Sentinels,
        ItemType.Gloves: ItemUpgradeId.Sentinels,
        ItemType.Leggings: ItemUpgradeId.Sentinels,
        ItemType.Boots: ItemUpgradeId.Sentinels,
    }
    
    property_identifiers = []
    
class RuneOfMinorAbsorption(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorAbsorption,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorAbsorption,
        ItemType.Gloves: ItemUpgradeId.OfMinorAbsorption,
        ItemType.Leggings: ItemUpgradeId.OfMinorAbsorption,
        ItemType.Boots: ItemUpgradeId.OfMinorAbsorption,
    }
    
    property_identifiers = []

class RuneOfMinorTactics(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorTactics,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorTactics,
        ItemType.Gloves: ItemUpgradeId.OfMinorTactics,
        ItemType.Leggings: ItemUpgradeId.OfMinorTactics,
        ItemType.Boots: ItemUpgradeId.OfMinorTactics,
    }
    
    property_identifiers = []

class RuneOfMinorStrength(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorStrength,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorStrength,
        ItemType.Gloves: ItemUpgradeId.OfMinorStrength,
        ItemType.Leggings: ItemUpgradeId.OfMinorStrength,
        ItemType.Boots: ItemUpgradeId.OfMinorStrength,
    }
    
    property_identifiers = []

class RuneOfMinorAxeMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorAxeMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorAxeMastery,
        ItemType.Gloves: ItemUpgradeId.OfMinorAxeMastery,
        ItemType.Leggings: ItemUpgradeId.OfMinorAxeMastery,
        ItemType.Boots: ItemUpgradeId.OfMinorAxeMastery,
    }
    
    property_identifiers = []
    
class RuneOfMinorHammerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorHammerMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorHammerMastery,
        ItemType.Gloves: ItemUpgradeId.OfMinorHammerMastery,
        ItemType.Leggings: ItemUpgradeId.OfMinorHammerMastery,
        ItemType.Boots: ItemUpgradeId.OfMinorHammerMastery,
    }
    
    property_identifiers = []
    
class RuneOfMinorSwordsmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorSwordsmanship,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorSwordsmanship,
        ItemType.Gloves: ItemUpgradeId.OfMinorSwordsmanship,
        ItemType.Leggings: ItemUpgradeId.OfMinorSwordsmanship,
        ItemType.Boots: ItemUpgradeId.OfMinorSwordsmanship,
    }
    
    property_identifiers = []
    
class RuneOfMajorAbsorption(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorAbsorption,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorAbsorption,
        ItemType.Gloves: ItemUpgradeId.OfMajorAbsorption,
        ItemType.Leggings: ItemUpgradeId.OfMajorAbsorption,
        ItemType.Boots: ItemUpgradeId.OfMajorAbsorption,
    }
    
    property_identifiers = []
    
class RuneOfMajorTactics(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorTactics,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorTactics,
        ItemType.Gloves: ItemUpgradeId.OfMajorTactics,
        ItemType.Leggings: ItemUpgradeId.OfMajorTactics,
        ItemType.Boots: ItemUpgradeId.OfMajorTactics,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorStrength(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorStrength,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorStrength,
        ItemType.Gloves: ItemUpgradeId.OfMajorStrength,
        ItemType.Leggings: ItemUpgradeId.OfMajorStrength,
        ItemType.Boots: ItemUpgradeId.OfMajorStrength,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorAxeMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorAxeMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorAxeMastery,
        ItemType.Gloves: ItemUpgradeId.OfMajorAxeMastery,
        ItemType.Leggings: ItemUpgradeId.OfMajorAxeMastery,
        ItemType.Boots: ItemUpgradeId.OfMajorAxeMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorHammerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorHammerMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorHammerMastery,
        ItemType.Gloves: ItemUpgradeId.OfMajorHammerMastery,
        ItemType.Leggings: ItemUpgradeId.OfMajorHammerMastery,
        ItemType.Boots: ItemUpgradeId.OfMajorHammerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorSwordsmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorSwordsmanship,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorSwordsmanship,
        ItemType.Gloves: ItemUpgradeId.OfMajorSwordsmanship,
        ItemType.Leggings: ItemUpgradeId.OfMajorSwordsmanship,
        ItemType.Boots: ItemUpgradeId.OfMajorSwordsmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorAbsorption(Rune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorAbsorption,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorAbsorption,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorAbsorption,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorAbsorption,
        ItemType.Boots: ItemUpgradeId.OfSuperiorAbsorption,
    }
    
    property_identifiers = []

class RuneOfSuperiorTactics(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorTactics,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorTactics,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorTactics,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorTactics,
        ItemType.Boots: ItemUpgradeId.OfSuperiorTactics,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorStrength(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorStrength,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorStrength,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorStrength,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorStrength,
        ItemType.Boots: ItemUpgradeId.OfSuperiorStrength,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorAxeMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorAxeMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorAxeMastery,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorAxeMastery,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorAxeMastery,
        ItemType.Boots: ItemUpgradeId.OfSuperiorAxeMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorHammerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorHammerMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorHammerMastery,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorHammerMastery,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorHammerMastery,
        ItemType.Boots: ItemUpgradeId.OfSuperiorHammerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorSwordsmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorSwordsmanship,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorSwordsmanship,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorSwordsmanship,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorSwordsmanship,
        ItemType.Boots: ItemUpgradeId.OfSuperiorSwordsmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]    

class UpgradeMinorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Warrior,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Warrior,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Warrior,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Warrior,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Warrior,
    }
    
    property_identifiers = []

class UpgradeMajorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Warrior,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Warrior,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Warrior,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Warrior,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Warrior,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Warrior,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Warrior,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Warrior,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Warrior,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Warrior,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Warrior,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Warrior,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Warrior,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Warrior,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Warrior,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Warrior,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Warrior,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Warrior,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Warrior,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Warrior,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Warrior,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Warrior,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Warrior,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Warrior,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Warrior,
    }
    
    property_identifiers = []
#endregion Warrior

#region Ranger
class FrostboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Frostbound,
        ItemType.Chestpiece: ItemUpgradeId.Frostbound,
        ItemType.Gloves: ItemUpgradeId.Frostbound,
        ItemType.Leggings: ItemUpgradeId.Frostbound,
        ItemType.Boots: ItemUpgradeId.Frostbound,
    }
    
    property_identifiers = []
    
class PyreboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Pyrebound,
        ItemType.Chestpiece: ItemUpgradeId.Pyrebound,
        ItemType.Gloves: ItemUpgradeId.Pyrebound,
        ItemType.Leggings: ItemUpgradeId.Pyrebound,
        ItemType.Boots: ItemUpgradeId.Pyrebound,
    }
    
    property_identifiers = []
    
class StormboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Stormbound,
        ItemType.Chestpiece: ItemUpgradeId.Stormbound,
        ItemType.Gloves: ItemUpgradeId.Stormbound,
        ItemType.Leggings: ItemUpgradeId.Stormbound,
        ItemType.Boots: ItemUpgradeId.Stormbound,
    }
    
    property_identifiers = []
    
class ScoutsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Scouts,
        ItemType.Chestpiece: ItemUpgradeId.Scouts,
        ItemType.Gloves: ItemUpgradeId.Scouts,
        ItemType.Leggings: ItemUpgradeId.Scouts,
        ItemType.Boots: ItemUpgradeId.Scouts,
    }
    
    property_identifiers = []
    
class EarthboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Earthbound,
        ItemType.Chestpiece: ItemUpgradeId.Earthbound,
        ItemType.Gloves: ItemUpgradeId.Earthbound,
        ItemType.Leggings: ItemUpgradeId.Earthbound,
        ItemType.Boots: ItemUpgradeId.Earthbound,
    }
    
    property_identifiers = []
    
class BeastmastersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Beastmasters,
        ItemType.Chestpiece: ItemUpgradeId.Beastmasters,
        ItemType.Gloves: ItemUpgradeId.Beastmasters,
        ItemType.Leggings: ItemUpgradeId.Beastmasters,
        ItemType.Boots: ItemUpgradeId.Beastmasters,
    }
    
    property_identifiers = []

class RuneOfMinorWildernessSurvival(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorWildernessSurvival,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorWildernessSurvival,
        ItemType.Gloves: ItemUpgradeId.OfMinorWildernessSurvival,
        ItemType.Leggings: ItemUpgradeId.OfMinorWildernessSurvival,
        ItemType.Boots: ItemUpgradeId.OfMinorWildernessSurvival,
    }
    
    property_identifiers = []

class RuneOfMinorExpertise(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorExpertise,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorExpertise,
        ItemType.Gloves: ItemUpgradeId.OfMinorExpertise,
        ItemType.Leggings: ItemUpgradeId.OfMinorExpertise,
        ItemType.Boots: ItemUpgradeId.OfMinorExpertise,
    }
    
    property_identifiers = []

class RuneOfMinorBeastMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorBeastMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorBeastMastery,
        ItemType.Gloves: ItemUpgradeId.OfMinorBeastMastery,
        ItemType.Leggings: ItemUpgradeId.OfMinorBeastMastery,
        ItemType.Boots: ItemUpgradeId.OfMinorBeastMastery,
    }
    
    property_identifiers = []
    
class RuneOfMinorMarksmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorMarksmanship,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorMarksmanship,
        ItemType.Gloves: ItemUpgradeId.OfMinorMarksmanship,
        ItemType.Leggings: ItemUpgradeId.OfMinorMarksmanship,
        ItemType.Boots: ItemUpgradeId.OfMinorMarksmanship,
    }
    
    property_identifiers = []
    
class RuneOfMajorWildernessSurvival(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorWildernessSurvival,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorWildernessSurvival,
        ItemType.Gloves: ItemUpgradeId.OfMajorWildernessSurvival,
        ItemType.Leggings: ItemUpgradeId.OfMajorWildernessSurvival,
        ItemType.Boots: ItemUpgradeId.OfMajorWildernessSurvival,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorExpertise(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorExpertise,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorExpertise,
        ItemType.Gloves: ItemUpgradeId.OfMajorExpertise,
        ItemType.Leggings: ItemUpgradeId.OfMajorExpertise,
        ItemType.Boots: ItemUpgradeId.OfMajorExpertise,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorBeastMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorBeastMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorBeastMastery,
        ItemType.Gloves: ItemUpgradeId.OfMajorBeastMastery,
        ItemType.Leggings: ItemUpgradeId.OfMajorBeastMastery,
        ItemType.Boots: ItemUpgradeId.OfMajorBeastMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorMarksmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorMarksmanship,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorMarksmanship,
        ItemType.Gloves: ItemUpgradeId.OfMajorMarksmanship,
        ItemType.Leggings: ItemUpgradeId.OfMajorMarksmanship,
        ItemType.Boots: ItemUpgradeId.OfMajorMarksmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorWildernessSurvival(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorWildernessSurvival,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorWildernessSurvival,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorWildernessSurvival,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorWildernessSurvival,
        ItemType.Boots: ItemUpgradeId.OfSuperiorWildernessSurvival,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorExpertise(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorExpertise,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorExpertise,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorExpertise,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorExpertise,
        ItemType.Boots: ItemUpgradeId.OfSuperiorExpertise,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorBeastMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorBeastMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorBeastMastery,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorBeastMastery,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorBeastMastery,
        ItemType.Boots: ItemUpgradeId.OfSuperiorBeastMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorMarksmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorMarksmanship,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorMarksmanship,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorMarksmanship,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorMarksmanship,
        ItemType.Boots: ItemUpgradeId.OfSuperiorMarksmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Ranger,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Ranger,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Ranger,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Ranger,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Ranger,
    }
    
    property_identifiers = []

class UpgradeMajorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Ranger,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Ranger,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Ranger,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Ranger,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Ranger,
    }
    
    property_identifiers = []

class UpgradeSuperiorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Ranger,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Ranger,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Ranger,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Ranger,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Ranger,
    }
    
    property_identifiers = []

class AppliesToMinorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Ranger,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Ranger,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Ranger,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Ranger,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Ranger,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Ranger,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Ranger,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Ranger,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Ranger,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Ranger,
    }
    
    property_identifiers = []
    
class AppliesToSuperiorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Ranger,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Ranger,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Ranger,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Ranger,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Ranger,
    }
    
    property_identifiers = []
#endregion Ranger

#region Monk
class WanderersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Wanderers,
        ItemType.Chestpiece: ItemUpgradeId.Wanderers,
        ItemType.Gloves: ItemUpgradeId.Wanderers,
        ItemType.Leggings: ItemUpgradeId.Wanderers,
        ItemType.Boots: ItemUpgradeId.Wanderers,
    }
    
    property_identifiers = []
    
class DisciplesInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Disciples,
        ItemType.Chestpiece: ItemUpgradeId.Disciples,
        ItemType.Gloves: ItemUpgradeId.Disciples,
        ItemType.Leggings: ItemUpgradeId.Disciples,
        ItemType.Boots: ItemUpgradeId.Disciples,
    }
    
    property_identifiers = []
    
class AnchoritesInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Anchorites,
        ItemType.Chestpiece: ItemUpgradeId.Anchorites,
        ItemType.Gloves: ItemUpgradeId.Anchorites,
        ItemType.Leggings: ItemUpgradeId.Anchorites,
        ItemType.Boots: ItemUpgradeId.Anchorites,
    }
    
    property_identifiers = []

class RuneOfMinorHealingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorHealingPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorHealingPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMinorHealingPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMinorHealingPrayers,
        ItemType.Boots: ItemUpgradeId.OfMinorHealingPrayers,
    }
    
    property_identifiers = []
    
class RuneOfMinorSmitingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorSmitingPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorSmitingPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMinorSmitingPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMinorSmitingPrayers,
        ItemType.Boots: ItemUpgradeId.OfMinorSmitingPrayers,
    }
    
    property_identifiers = []
    
class RuneOfMinorProtectionPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorProtectionPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorProtectionPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMinorProtectionPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMinorProtectionPrayers,
        ItemType.Boots: ItemUpgradeId.OfMinorProtectionPrayers,
    }
    
    property_identifiers = []
    
class RuneOfMinorDivineFavor(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorDivineFavor,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorDivineFavor,
        ItemType.Gloves: ItemUpgradeId.OfMinorDivineFavor,
        ItemType.Leggings: ItemUpgradeId.OfMinorDivineFavor,
        ItemType.Boots: ItemUpgradeId.OfMinorDivineFavor,
    }
    
    property_identifiers = []
    
class RuneOfMajorHealingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorHealingPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorHealingPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMajorHealingPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMajorHealingPrayers,
        ItemType.Boots: ItemUpgradeId.OfMajorHealingPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorSmitingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorSmitingPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorSmitingPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMajorSmitingPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMajorSmitingPrayers,
        ItemType.Boots: ItemUpgradeId.OfMajorSmitingPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorProtectionPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorProtectionPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorProtectionPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMajorProtectionPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMajorProtectionPrayers,
        ItemType.Boots: ItemUpgradeId.OfMajorProtectionPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorDivineFavor(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorDivineFavor,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorDivineFavor,
        ItemType.Gloves: ItemUpgradeId.OfMajorDivineFavor,
        ItemType.Leggings: ItemUpgradeId.OfMajorDivineFavor,
        ItemType.Boots: ItemUpgradeId.OfMajorDivineFavor,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorHealingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorHealingPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorHealingPrayers,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorHealingPrayers,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorHealingPrayers,
        ItemType.Boots: ItemUpgradeId.OfSuperiorHealingPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorSmitingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorSmitingPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorSmitingPrayers,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorSmitingPrayers,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorSmitingPrayers,
        ItemType.Boots: ItemUpgradeId.OfSuperiorSmitingPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorProtectionPrayers(AttributeRune): 
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorProtectionPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorProtectionPrayers,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorProtectionPrayers,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorProtectionPrayers,
        ItemType.Boots: ItemUpgradeId.OfSuperiorProtectionPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]   

class RuneOfSuperiorDivineFavor(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorDivineFavor,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorDivineFavor,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorDivineFavor,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorDivineFavor,
        ItemType.Boots: ItemUpgradeId.OfSuperiorDivineFavor,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Monk,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Monk,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Monk,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Monk,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Monk,
    }
    
    property_identifiers = []

class UpgradeMajorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Monk,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Monk,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Monk,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Monk,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Monk,
    }
    
    property_identifiers = []

class UpgradeSuperiorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Monk,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Monk,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Monk,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Monk,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Monk,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Monk,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Monk,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Monk,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Monk,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Monk,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Monk,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Monk,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Monk,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Monk,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Monk,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Monk,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Monk,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Monk,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Monk,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Monk,
    }
    
    property_identifiers = []
#endregion Monk

#region Necromancer
class BloodstainedInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Bloodstained,
        ItemType.Chestpiece: ItemUpgradeId.Bloodstained,
        ItemType.Gloves: ItemUpgradeId.Bloodstained,
        ItemType.Leggings: ItemUpgradeId.Bloodstained,
        ItemType.Boots: ItemUpgradeId.Bloodstained,
    }
    
    property_identifiers = []
    
class TormentorsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Tormentors,
        ItemType.Chestpiece: ItemUpgradeId.Tormentors,
        ItemType.Gloves: ItemUpgradeId.Tormentors,
        ItemType.Leggings: ItemUpgradeId.Tormentors,
        ItemType.Boots: ItemUpgradeId.Tormentors,
    }
    
    property_identifiers = []
    
class BonelaceInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Bonelace,
        ItemType.Chestpiece: ItemUpgradeId.Bonelace,
        ItemType.Gloves: ItemUpgradeId.Bonelace,
        ItemType.Leggings: ItemUpgradeId.Bonelace,
        ItemType.Boots: ItemUpgradeId.Bonelace,
    }
    
    property_identifiers = []
    
class MinionMastersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.MinionMasters,
        ItemType.Chestpiece: ItemUpgradeId.MinionMasters,
        ItemType.Gloves: ItemUpgradeId.MinionMasters,
        ItemType.Leggings: ItemUpgradeId.MinionMasters,
        ItemType.Boots: ItemUpgradeId.MinionMasters,
    }
    
    property_identifiers = []
    
class BlightersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Blighters,
        ItemType.Chestpiece: ItemUpgradeId.Blighters,
        ItemType.Gloves: ItemUpgradeId.Blighters,
        ItemType.Leggings: ItemUpgradeId.Blighters,
        ItemType.Boots: ItemUpgradeId.Blighters,
    }
    
    property_identifiers = []
    
class UndertakersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Undertakers,
        ItemType.Chestpiece: ItemUpgradeId.Undertakers,
        ItemType.Gloves: ItemUpgradeId.Undertakers,
        ItemType.Leggings: ItemUpgradeId.Undertakers,
        ItemType.Boots: ItemUpgradeId.Undertakers,
    }
    
    property_identifiers = []

class RuneOfMinorBloodMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorBloodMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorBloodMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorBloodMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorBloodMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorBloodMagic,
    }
    
    property_identifiers = []

class RuneOfMinorDeathMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorDeathMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorDeathMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorDeathMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorDeathMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorDeathMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorCurses(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorCurses,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorCurses,
        ItemType.Gloves: ItemUpgradeId.OfMinorCurses,
        ItemType.Leggings: ItemUpgradeId.OfMinorCurses,
        ItemType.Boots: ItemUpgradeId.OfMinorCurses,
    }
    
    property_identifiers = []
    
class RuneOfMinorSoulReaping(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorSoulReaping,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorSoulReaping,
        ItemType.Gloves: ItemUpgradeId.OfMinorSoulReaping,
        ItemType.Leggings: ItemUpgradeId.OfMinorSoulReaping,
        ItemType.Boots: ItemUpgradeId.OfMinorSoulReaping,
    }
    
    property_identifiers = []

class RuneOfMajorBloodMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorBloodMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorBloodMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorBloodMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorBloodMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorBloodMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorDeathMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorDeathMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorDeathMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorDeathMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorDeathMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorDeathMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorCurses(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorCurses,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorCurses,
        ItemType.Gloves: ItemUpgradeId.OfMajorCurses,
        ItemType.Leggings: ItemUpgradeId.OfMajorCurses,
        ItemType.Boots: ItemUpgradeId.OfMajorCurses,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorSoulReaping(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorSoulReaping,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorSoulReaping,
        ItemType.Gloves: ItemUpgradeId.OfMajorSoulReaping,
        ItemType.Leggings: ItemUpgradeId.OfMajorSoulReaping,
        ItemType.Boots: ItemUpgradeId.OfMajorSoulReaping,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorBloodMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorBloodMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorBloodMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorBloodMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorBloodMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorBloodMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorDeathMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorDeathMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorDeathMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorDeathMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorDeathMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorDeathMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorCurses(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorCurses,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorCurses,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorCurses,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorCurses,
        ItemType.Boots: ItemUpgradeId.OfSuperiorCurses,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorSoulReaping(AttributeRune):    
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorSoulReaping,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorSoulReaping,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorSoulReaping,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorSoulReaping,
        ItemType.Boots: ItemUpgradeId.OfSuperiorSoulReaping,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Necromancer,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Necromancer,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Necromancer,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Necromancer,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Necromancer,
    }
    
    property_identifiers = []
    
class UpgradeMajorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Necromancer,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Necromancer,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Necromancer,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Necromancer,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Necromancer,
    }
    
    property_identifiers = []

class UpgradeSuperiorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Necromancer,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Necromancer,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Necromancer,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Necromancer,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Necromancer,
    }
    
    property_identifiers = []

class AppliesToMinorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Necromancer,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Necromancer,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Necromancer,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Necromancer,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Necromancer,
    }
    
    property_identifiers = []

class AppliesToMajorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Necromancer,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Necromancer,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Necromancer,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Necromancer,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Necromancer,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Necromancer,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Necromancer,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Necromancer,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Necromancer,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Necromancer,
    }
    
    property_identifiers = []
#endregion Necromancer

#region Mesmer
class VirtuososInsignia(Insignia):    
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Virtuosos,
        ItemType.Chestpiece: ItemUpgradeId.Virtuosos,
        ItemType.Gloves: ItemUpgradeId.Virtuosos,
        ItemType.Leggings: ItemUpgradeId.Virtuosos,
        ItemType.Boots: ItemUpgradeId.Virtuosos,
    }
    
    property_identifiers = []
    
class ArtificersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Artificers,
        ItemType.Chestpiece: ItemUpgradeId.Artificers,
        ItemType.Gloves: ItemUpgradeId.Artificers,
        ItemType.Leggings: ItemUpgradeId.Artificers,
        ItemType.Boots: ItemUpgradeId.Artificers,
    }
    
    property_identifiers = []
    
class ProdigysInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Prodigys,
        ItemType.Chestpiece: ItemUpgradeId.Prodigys,
        ItemType.Gloves: ItemUpgradeId.Prodigys,
        ItemType.Leggings: ItemUpgradeId.Prodigys,
        ItemType.Boots: ItemUpgradeId.Prodigys,
    }
    
    property_identifiers = []

class RuneOfMinorFastCasting(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorFastCasting,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorFastCasting,
        ItemType.Gloves: ItemUpgradeId.OfMinorFastCasting,
        ItemType.Leggings: ItemUpgradeId.OfMinorFastCasting,
        ItemType.Boots: ItemUpgradeId.OfMinorFastCasting,
    }
    
    property_identifiers = []
    
class RuneOfMinorDominationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorDominationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorDominationMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorDominationMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorDominationMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorDominationMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorIllusionMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorIllusionMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorIllusionMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorIllusionMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorIllusionMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorIllusionMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorInspirationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorInspirationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorInspirationMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorInspirationMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorInspirationMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorInspirationMagic,
    }
    
    property_identifiers = []

class RuneOfMajorFastCasting(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorFastCasting,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorFastCasting,
        ItemType.Gloves: ItemUpgradeId.OfMajorFastCasting,
        ItemType.Leggings: ItemUpgradeId.OfMajorFastCasting,
        ItemType.Boots: ItemUpgradeId.OfMajorFastCasting,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorDominationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorDominationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorDominationMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorDominationMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorDominationMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorDominationMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorIllusionMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorIllusionMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorIllusionMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorIllusionMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorIllusionMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorIllusionMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorInspirationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorInspirationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorInspirationMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorInspirationMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorInspirationMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorInspirationMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]   
    
class RuneOfSuperiorFastCasting(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorFastCasting,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorFastCasting,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorFastCasting,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorFastCasting,
        ItemType.Boots: ItemUpgradeId.OfSuperiorFastCasting,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorDominationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorDominationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorDominationMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorDominationMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorDominationMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorDominationMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorIllusionMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorIllusionMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorIllusionMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorIllusionMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorIllusionMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorIllusionMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorInspirationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorInspirationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorInspirationMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorInspirationMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorInspirationMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorInspirationMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class UpgradeMinorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Mesmer,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Mesmer,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Mesmer,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Mesmer,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Mesmer,
    }
    
    property_identifiers = []

class UpgradeMajorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Mesmer,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Mesmer,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Mesmer,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Mesmer,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Mesmer,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Mesmer,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Mesmer,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Mesmer,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Mesmer,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Mesmer,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Mesmer,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Mesmer,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Mesmer,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Mesmer,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Mesmer,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Mesmer,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Mesmer,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Mesmer,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Mesmer,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Mesmer,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Mesmer,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Mesmer,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Mesmer,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Mesmer,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Mesmer,
    }
    
    property_identifiers = []
#endregion Mesmer

#region Elementalist
class HydromancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Hydromancer,
        ItemType.Chestpiece: ItemUpgradeId.Hydromancer,
        ItemType.Gloves: ItemUpgradeId.Hydromancer,
        ItemType.Leggings: ItemUpgradeId.Hydromancer,
        ItemType.Boots: ItemUpgradeId.Hydromancer,
    }
    
    property_identifiers = []
    
class GeomancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Geomancer,
        ItemType.Chestpiece: ItemUpgradeId.Geomancer,
        ItemType.Gloves: ItemUpgradeId.Geomancer,
        ItemType.Leggings: ItemUpgradeId.Geomancer,
        ItemType.Boots: ItemUpgradeId.Geomancer,
    }
    
    property_identifiers = []
    
class PyromancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Pyromancer,
        ItemType.Chestpiece: ItemUpgradeId.Pyromancer,
        ItemType.Gloves: ItemUpgradeId.Pyromancer,
        ItemType.Leggings: ItemUpgradeId.Pyromancer,
        ItemType.Boots: ItemUpgradeId.Pyromancer,
    }
    
    property_identifiers = []   
    
class AeromancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Aeromancer,
        ItemType.Chestpiece: ItemUpgradeId.Aeromancer,
        ItemType.Gloves: ItemUpgradeId.Aeromancer,
        ItemType.Leggings: ItemUpgradeId.Aeromancer,
        ItemType.Boots: ItemUpgradeId.Aeromancer,
    }
    
    property_identifiers = []
    
class PrismaticInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Prismatic,
        ItemType.Chestpiece: ItemUpgradeId.Prismatic,
        ItemType.Gloves: ItemUpgradeId.Prismatic,
        ItemType.Leggings: ItemUpgradeId.Prismatic,
        ItemType.Boots: ItemUpgradeId.Prismatic,
    }
    
    property_identifiers = []

class RuneOfMinorEnergyStorage(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorEnergyStorage,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorEnergyStorage,
        ItemType.Gloves: ItemUpgradeId.OfMinorEnergyStorage,
        ItemType.Leggings: ItemUpgradeId.OfMinorEnergyStorage,
        ItemType.Boots: ItemUpgradeId.OfMinorEnergyStorage,
    }
    
    property_identifiers = []
    
class RuneOfMinorFireMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorFireMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorFireMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorFireMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorFireMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorFireMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorAirMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorAirMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorAirMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorAirMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorAirMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorAirMagic,
    }
    
    property_identifiers = []

class RuneOfMinorEarthMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorEarthMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorEarthMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorEarthMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorEarthMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorEarthMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorWaterMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorWaterMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorWaterMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorWaterMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorWaterMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorWaterMagic,
    }
    
    property_identifiers = []
    
class RuneOfMajorEnergyStorage(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorEnergyStorage,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorEnergyStorage,
        ItemType.Gloves: ItemUpgradeId.OfMajorEnergyStorage,
        ItemType.Leggings: ItemUpgradeId.OfMajorEnergyStorage,
        ItemType.Boots: ItemUpgradeId.OfMajorEnergyStorage,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorFireMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorFireMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorFireMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorFireMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorFireMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorFireMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorAirMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorAirMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorAirMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorAirMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorAirMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorAirMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorEarthMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorEarthMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorEarthMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorEarthMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorEarthMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorEarthMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorWaterMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorWaterMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorWaterMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorWaterMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorWaterMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorWaterMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorEnergyStorage(AttributeRune): 
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorEnergyStorage,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorEnergyStorage,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorEnergyStorage,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorEnergyStorage,
        ItemType.Boots: ItemUpgradeId.OfSuperiorEnergyStorage,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorFireMagic(AttributeRune): 
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorFireMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorFireMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorFireMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorFireMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorFireMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorAirMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorAirMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorAirMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorAirMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorAirMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorAirMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorEarthMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorEarthMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorEarthMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorEarthMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorEarthMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorEarthMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorWaterMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorWaterMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorWaterMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorWaterMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorWaterMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorWaterMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Elementalist,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Elementalist,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Elementalist,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Elementalist,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Elementalist,
    }
    
    property_identifiers = []

class UpgradeMajorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Elementalist,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Elementalist,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Elementalist,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Elementalist,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Elementalist,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Elementalist,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Elementalist,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Elementalist,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Elementalist,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Elementalist,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Elementalist,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Elementalist,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Elementalist,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Elementalist,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Elementalist,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Elementalist,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Elementalist,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Elementalist,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Elementalist,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Elementalist,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Elementalist,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Elementalist,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Elementalist,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Elementalist,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Elementalist,
    }
    
    property_identifiers = []
#endregion Elementalist

#region Assassin
class VanguardsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Vanguards,
        ItemType.Chestpiece: ItemUpgradeId.Vanguards,
        ItemType.Gloves: ItemUpgradeId.Vanguards,
        ItemType.Leggings: ItemUpgradeId.Vanguards,
        ItemType.Boots: ItemUpgradeId.Vanguards,
    }
    
    property_identifiers = []
    
class InfiltratorsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Infiltrators,
        ItemType.Chestpiece: ItemUpgradeId.Infiltrators,
        ItemType.Gloves: ItemUpgradeId.Infiltrators,
        ItemType.Leggings: ItemUpgradeId.Infiltrators,
        ItemType.Boots: ItemUpgradeId.Infiltrators,
    }
    
    property_identifiers = []
    
class SaboteursInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Saboteurs,
        ItemType.Chestpiece: ItemUpgradeId.Saboteurs,
        ItemType.Gloves: ItemUpgradeId.Saboteurs,
        ItemType.Leggings: ItemUpgradeId.Saboteurs,
        ItemType.Boots: ItemUpgradeId.Saboteurs,
    }
    
    property_identifiers = []
    
class NightstalkersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Nightstalkers,
        ItemType.Chestpiece: ItemUpgradeId.Nightstalkers,
        ItemType.Gloves: ItemUpgradeId.Nightstalkers,
        ItemType.Leggings: ItemUpgradeId.Nightstalkers,
        ItemType.Boots: ItemUpgradeId.Nightstalkers,
    }
    
    property_identifiers = []

class RuneOfMinorCriticalStrikes(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorCriticalStrikes,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorCriticalStrikes,
        ItemType.Gloves: ItemUpgradeId.OfMinorCriticalStrikes,
        ItemType.Leggings: ItemUpgradeId.OfMinorCriticalStrikes,
        ItemType.Boots: ItemUpgradeId.OfMinorCriticalStrikes,
    }
    
    property_identifiers = []
    
class RuneOfMinorDaggerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorDaggerMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorDaggerMastery,
        ItemType.Gloves: ItemUpgradeId.OfMinorDaggerMastery,
        ItemType.Leggings: ItemUpgradeId.OfMinorDaggerMastery,
        ItemType.Boots: ItemUpgradeId.OfMinorDaggerMastery,
    }
    
    property_identifiers = []
    
class RuneOfMinorDeadlyArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorDeadlyArts,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorDeadlyArts,
        ItemType.Gloves: ItemUpgradeId.OfMinorDeadlyArts,
        ItemType.Leggings: ItemUpgradeId.OfMinorDeadlyArts,
        ItemType.Boots: ItemUpgradeId.OfMinorDeadlyArts,
    }

class RuneOfMinorShadowArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorShadowArts,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorShadowArts,
        ItemType.Gloves: ItemUpgradeId.OfMinorShadowArts,
        ItemType.Leggings: ItemUpgradeId.OfMinorShadowArts,
        ItemType.Boots: ItemUpgradeId.OfMinorShadowArts,
    }
    
    property_identifiers = []

class RuneOfMajorCriticalStrikes(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorCriticalStrikes,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorCriticalStrikes,
        ItemType.Gloves: ItemUpgradeId.OfMajorCriticalStrikes,
        ItemType.Leggings: ItemUpgradeId.OfMajorCriticalStrikes,
        ItemType.Boots: ItemUpgradeId.OfMajorCriticalStrikes,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorDaggerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorDaggerMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorDaggerMastery,
        ItemType.Gloves: ItemUpgradeId.OfMajorDaggerMastery,
        ItemType.Leggings: ItemUpgradeId.OfMajorDaggerMastery,
        ItemType.Boots: ItemUpgradeId.OfMajorDaggerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorDeadlyArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorDeadlyArts,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorDeadlyArts,
        ItemType.Gloves: ItemUpgradeId.OfMajorDeadlyArts,
        ItemType.Leggings: ItemUpgradeId.OfMajorDeadlyArts,
        ItemType.Boots: ItemUpgradeId.OfMajorDeadlyArts,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorShadowArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorShadowArts,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorShadowArts,
        ItemType.Gloves: ItemUpgradeId.OfMajorShadowArts,
        ItemType.Leggings: ItemUpgradeId.OfMajorShadowArts,
        ItemType.Boots: ItemUpgradeId.OfMajorShadowArts,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorCriticalStrikes(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorCriticalStrikes,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorCriticalStrikes,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorCriticalStrikes,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorCriticalStrikes,
        ItemType.Boots: ItemUpgradeId.OfSuperiorCriticalStrikes,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorDaggerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorDaggerMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorDaggerMastery,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorDaggerMastery,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorDaggerMastery,
        ItemType.Boots: ItemUpgradeId.OfSuperiorDaggerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorDeadlyArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorDeadlyArts,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorDeadlyArts,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorDeadlyArts,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorDeadlyArts,
        ItemType.Boots: ItemUpgradeId.OfSuperiorDeadlyArts,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorShadowArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorShadowArts,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorShadowArts,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorShadowArts,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorShadowArts,
        ItemType.Boots: ItemUpgradeId.OfSuperiorShadowArts,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class UpgradeMinorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Assassin,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Assassin,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Assassin,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Assassin,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Assassin,
    }
    
    property_identifiers = []

class UpgradeMajorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Assassin,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Assassin,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Assassin,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Assassin,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Assassin,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Assassin,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Assassin,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Assassin,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Assassin,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Assassin,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Assassin,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Assassin,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Assassin,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Assassin,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Assassin,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Assassin,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Assassin,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Assassin,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Assassin,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Assassin,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Assassin,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Assassin,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Assassin,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Assassin,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Assassin,
    }
    
    property_identifiers = []
#endregion Assassin

#region Ritualist
class ShamansInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Shamans,
        ItemType.Chestpiece: ItemUpgradeId.Shamans,
        ItemType.Gloves: ItemUpgradeId.Shamans,
        ItemType.Leggings: ItemUpgradeId.Shamans,
        ItemType.Boots: ItemUpgradeId.Shamans,
    }
    
    property_identifiers = []
    
class GhostForgeInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.GhostForge,
        ItemType.Chestpiece: ItemUpgradeId.GhostForge,
        ItemType.Gloves: ItemUpgradeId.GhostForge,
        ItemType.Leggings: ItemUpgradeId.GhostForge,
        ItemType.Boots: ItemUpgradeId.GhostForge,
    }
    
    property_identifiers = []
    
class MysticsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Mystics,
        ItemType.Chestpiece: ItemUpgradeId.Mystics,
        ItemType.Gloves: ItemUpgradeId.Mystics,
        ItemType.Leggings: ItemUpgradeId.Mystics,
        ItemType.Boots: ItemUpgradeId.Mystics,
    }
    
    property_identifiers = []

class RuneOfMinorChannelingMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorChannelingMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorChannelingMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorChannelingMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorChannelingMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorChannelingMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorRestorationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorRestorationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorRestorationMagic,
        ItemType.Gloves: ItemUpgradeId.OfMinorRestorationMagic,
        ItemType.Leggings: ItemUpgradeId.OfMinorRestorationMagic,
        ItemType.Boots: ItemUpgradeId.OfMinorRestorationMagic,
    }
    
    property_identifiers = []
    
class RuneOfMinorCommuning(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorCommuning,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorCommuning,
        ItemType.Gloves: ItemUpgradeId.OfMinorCommuning,
        ItemType.Leggings: ItemUpgradeId.OfMinorCommuning,
        ItemType.Boots: ItemUpgradeId.OfMinorCommuning,
    }
    
    property_identifiers = []
    
class RuneOfMinorSpawningPower(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorSpawningPower,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorSpawningPower,
        ItemType.Gloves: ItemUpgradeId.OfMinorSpawningPower,
        ItemType.Leggings: ItemUpgradeId.OfMinorSpawningPower,
        ItemType.Boots: ItemUpgradeId.OfMinorSpawningPower,
    }
    
    property_identifiers = []

class RuneOfMajorChannelingMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorChannelingMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorChannelingMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorChannelingMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorChannelingMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorChannelingMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorRestorationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorRestorationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorRestorationMagic,
        ItemType.Gloves: ItemUpgradeId.OfMajorRestorationMagic,
        ItemType.Leggings: ItemUpgradeId.OfMajorRestorationMagic,
        ItemType.Boots: ItemUpgradeId.OfMajorRestorationMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorCommuning(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorCommuning,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorCommuning,
        ItemType.Gloves: ItemUpgradeId.OfMajorCommuning,
        ItemType.Leggings: ItemUpgradeId.OfMajorCommuning,
        ItemType.Boots: ItemUpgradeId.OfMajorCommuning,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorSpawningPower(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorSpawningPower,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorSpawningPower,
        ItemType.Gloves: ItemUpgradeId.OfMajorSpawningPower,
        ItemType.Leggings: ItemUpgradeId.OfMajorSpawningPower,
        ItemType.Boots: ItemUpgradeId.OfMajorSpawningPower,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorChannelingMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorChannelingMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorChannelingMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorChannelingMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorChannelingMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorChannelingMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorRestorationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorRestorationMagic,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorRestorationMagic,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorRestorationMagic,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorRestorationMagic,
        ItemType.Boots: ItemUpgradeId.OfSuperiorRestorationMagic,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorCommuning(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorCommuning,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorCommuning,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorCommuning,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorCommuning,
        ItemType.Boots: ItemUpgradeId.OfSuperiorCommuning,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorSpawningPower(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorSpawningPower,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorSpawningPower,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorSpawningPower,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorSpawningPower,
        ItemType.Boots: ItemUpgradeId.OfSuperiorSpawningPower,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Ritualist,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Ritualist,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Ritualist,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Ritualist,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Ritualist,
    }
    
    property_identifiers = []

class UpgradeMajorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Ritualist,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Ritualist,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Ritualist,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Ritualist,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Ritualist,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Ritualist,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Ritualist,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Ritualist,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Ritualist,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Ritualist,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Ritualist,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Ritualist,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Ritualist,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Ritualist,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Ritualist,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Ritualist,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Ritualist,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Ritualist,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Ritualist,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Ritualist,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Ritualist,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Ritualist,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Ritualist,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Ritualist,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Ritualist,
    }
    
    property_identifiers = []
#endregion Ritualist

#region Dervish
class WindwalkerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Windwalker,
        ItemType.Chestpiece: ItemUpgradeId.Windwalker,
        ItemType.Gloves: ItemUpgradeId.Windwalker,
        ItemType.Leggings: ItemUpgradeId.Windwalker,
        ItemType.Boots: ItemUpgradeId.Windwalker,
    }
    
    property_identifiers = []
    
class ForsakenInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Forsaken,
        ItemType.Chestpiece: ItemUpgradeId.Forsaken,
        ItemType.Gloves: ItemUpgradeId.Forsaken,
        ItemType.Leggings: ItemUpgradeId.Forsaken,
        ItemType.Boots: ItemUpgradeId.Forsaken,
    }
    
    property_identifiers = []

class RuneOfMinorMysticsm(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorMysticism,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorMysticism,
        ItemType.Gloves: ItemUpgradeId.OfMinorMysticism,
        ItemType.Leggings: ItemUpgradeId.OfMinorMysticism,
        ItemType.Boots: ItemUpgradeId.OfMinorMysticism,
    }
    
    property_identifiers = []

class RuneOfMinorEarthPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorEarthPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorEarthPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMinorEarthPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMinorEarthPrayers,
        ItemType.Boots: ItemUpgradeId.OfMinorEarthPrayers,
    }
    
    property_identifiers = []
    
class RuneOfMinorScytheMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorScytheMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorScytheMastery,
        ItemType.Gloves: ItemUpgradeId.OfMinorScytheMastery,
        ItemType.Leggings: ItemUpgradeId.OfMinorScytheMastery,
        ItemType.Boots: ItemUpgradeId.OfMinorScytheMastery,
    }
    
    property_identifiers = []
    
class RuneOfMinorWindPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorWindPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorWindPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMinorWindPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMinorWindPrayers,
        ItemType.Boots: ItemUpgradeId.OfMinorWindPrayers,
    }
    
    property_identifiers = []
    
class RuneOfMajorMysticsm(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorMysticism,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorMysticism,
        ItemType.Gloves: ItemUpgradeId.OfMajorMysticism,
        ItemType.Leggings: ItemUpgradeId.OfMajorMysticism,
        ItemType.Boots: ItemUpgradeId.OfMajorMysticism,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorEarthPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorEarthPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorEarthPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMajorEarthPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMajorEarthPrayers,
        ItemType.Boots: ItemUpgradeId.OfMajorEarthPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorScytheMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorScytheMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorScytheMastery,
        ItemType.Gloves: ItemUpgradeId.OfMajorScytheMastery,
        ItemType.Leggings: ItemUpgradeId.OfMajorScytheMastery,
        ItemType.Boots: ItemUpgradeId.OfMajorScytheMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorWindPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorWindPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorWindPrayers,
        ItemType.Gloves: ItemUpgradeId.OfMajorWindPrayers,
        ItemType.Leggings: ItemUpgradeId.OfMajorWindPrayers,
        ItemType.Boots: ItemUpgradeId.OfMajorWindPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorMysticsm(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorMysticism,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorMysticism,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorMysticism,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorMysticism,
        ItemType.Boots: ItemUpgradeId.OfSuperiorMysticism,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorEarthPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorEarthPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorEarthPrayers,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorEarthPrayers,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorEarthPrayers,
        ItemType.Boots: ItemUpgradeId.OfSuperiorEarthPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorScytheMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorScytheMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorScytheMastery,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorScytheMastery,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorScytheMastery,
        ItemType.Boots: ItemUpgradeId.OfSuperiorScytheMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorWindPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorWindPrayers,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorWindPrayers,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorWindPrayers,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorWindPrayers,
        ItemType.Boots: ItemUpgradeId.OfSuperiorWindPrayers,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class UpgradeMinorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Dervish,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Dervish,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Dervish,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Dervish,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Dervish,
    }
    
    property_identifiers = []

class UpgradeMajorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Dervish,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Dervish,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Dervish,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Dervish,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Dervish,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Dervish,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Dervish,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Dervish,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Dervish,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Dervish,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Dervish,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Dervish,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Dervish,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Dervish,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Dervish,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Dervish,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Dervish,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Dervish,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Dervish,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Dervish,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Dervish,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Dervish,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Dervish,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Dervish,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Dervish,
    }
    
    property_identifiers = []
#endregion Dervish

#region Paragon
class CenturionsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = {
        ItemType.Headpiece: ItemUpgradeId.Centurions,
        ItemType.Chestpiece: ItemUpgradeId.Centurions,
        ItemType.Gloves: ItemUpgradeId.Centurions,
        ItemType.Leggings: ItemUpgradeId.Centurions,
        ItemType.Boots: ItemUpgradeId.Centurions,
    }
    
    property_identifiers = []   

class RuneOfMinorLeadership(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorLeadership,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorLeadership,
        ItemType.Gloves: ItemUpgradeId.OfMinorLeadership,
        ItemType.Leggings: ItemUpgradeId.OfMinorLeadership,
        ItemType.Boots: ItemUpgradeId.OfMinorLeadership,
    }
    
    property_identifiers = []
    
class RuneOfMinorMotivation(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorMotivation,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorMotivation,
        ItemType.Gloves: ItemUpgradeId.OfMinorMotivation,
        ItemType.Leggings: ItemUpgradeId.OfMinorMotivation,
        ItemType.Boots: ItemUpgradeId.OfMinorMotivation,
    }
    
    property_identifiers = []

class RuneOfMinorCommand(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorCommand,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorCommand,
        ItemType.Gloves: ItemUpgradeId.OfMinorCommand,
        ItemType.Leggings: ItemUpgradeId.OfMinorCommand,
        ItemType.Boots: ItemUpgradeId.OfMinorCommand,
    }
    
    property_identifiers = []
    
class RuneOfMinorSpearMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMinorSpearMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMinorSpearMastery,
        ItemType.Gloves: ItemUpgradeId.OfMinorSpearMastery,
        ItemType.Leggings: ItemUpgradeId.OfMinorSpearMastery,
        ItemType.Boots: ItemUpgradeId.OfMinorSpearMastery,
    }
    
    property_identifiers = []
    
class RuneOfMajorLeadership(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorLeadership,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorLeadership,
        ItemType.Gloves: ItemUpgradeId.OfMajorLeadership,
        ItemType.Leggings: ItemUpgradeId.OfMajorLeadership,
        ItemType.Boots: ItemUpgradeId.OfMajorLeadership,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorMotivation(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorMotivation,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorMotivation,
        ItemType.Gloves: ItemUpgradeId.OfMajorMotivation,
        ItemType.Leggings: ItemUpgradeId.OfMajorMotivation,
        ItemType.Boots: ItemUpgradeId.OfMajorMotivation,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorCommand(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorCommand,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorCommand,
        ItemType.Gloves: ItemUpgradeId.OfMajorCommand,
        ItemType.Leggings: ItemUpgradeId.OfMajorCommand,
        ItemType.Boots: ItemUpgradeId.OfMajorCommand,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfMajorSpearMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfMajorSpearMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfMajorSpearMastery,
        ItemType.Gloves: ItemUpgradeId.OfMajorSpearMastery,
        ItemType.Leggings: ItemUpgradeId.OfMajorSpearMastery,
        ItemType.Boots: ItemUpgradeId.OfMajorSpearMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorLeadership(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorLeadership,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorLeadership,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorLeadership,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorLeadership,
        ItemType.Boots: ItemUpgradeId.OfSuperiorLeadership,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorMotivation(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorMotivation,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorMotivation,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorMotivation,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorMotivation,
        ItemType.Boots: ItemUpgradeId.OfSuperiorMotivation,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorCommand(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorCommand,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorCommand,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorCommand,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorCommand,
        ItemType.Boots: ItemUpgradeId.OfSuperiorCommand,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class RuneOfSuperiorSpearMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    id = {
        ItemType.Headpiece: ItemUpgradeId.OfSuperiorSpearMastery,
        ItemType.Chestpiece: ItemUpgradeId.OfSuperiorSpearMastery,
        ItemType.Gloves: ItemUpgradeId.OfSuperiorSpearMastery,
        ItemType.Leggings: ItemUpgradeId.OfSuperiorSpearMastery,
        ItemType.Boots: ItemUpgradeId.OfSuperiorSpearMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]
    
class UpgradeMinorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMinorRune_Paragon,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMinorRune_Paragon,
        ItemType.Gloves: ItemUpgradeId.UpgradeMinorRune_Paragon,
        ItemType.Leggings: ItemUpgradeId.UpgradeMinorRune_Paragon,
        ItemType.Boots: ItemUpgradeId.UpgradeMinorRune_Paragon,
    }
    
    property_identifiers = []

class UpgradeMajorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeMajorRune_Paragon,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeMajorRune_Paragon,
        ItemType.Gloves: ItemUpgradeId.UpgradeMajorRune_Paragon,
        ItemType.Leggings: ItemUpgradeId.UpgradeMajorRune_Paragon,
        ItemType.Boots: ItemUpgradeId.UpgradeMajorRune_Paragon,
    }
    
    property_identifiers = []
    
class UpgradeSuperiorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.UpgradeSuperiorRune_Paragon,
        ItemType.Chestpiece: ItemUpgradeId.UpgradeSuperiorRune_Paragon,
        ItemType.Gloves: ItemUpgradeId.UpgradeSuperiorRune_Paragon,
        ItemType.Leggings: ItemUpgradeId.UpgradeSuperiorRune_Paragon,
        ItemType.Boots: ItemUpgradeId.UpgradeSuperiorRune_Paragon,
    }
    
    property_identifiers = []
    
class AppliesToMinorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMinorRune_Paragon,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMinorRune_Paragon,
        ItemType.Gloves: ItemUpgradeId.AppliesToMinorRune_Paragon,
        ItemType.Leggings: ItemUpgradeId.AppliesToMinorRune_Paragon,
        ItemType.Boots: ItemUpgradeId.AppliesToMinorRune_Paragon,
    }
    
    property_identifiers = []
    
class AppliesToMajorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToMajorRune_Paragon,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToMajorRune_Paragon,
        ItemType.Gloves: ItemUpgradeId.AppliesToMajorRune_Paragon,
        ItemType.Leggings: ItemUpgradeId.AppliesToMajorRune_Paragon,
        ItemType.Boots: ItemUpgradeId.AppliesToMajorRune_Paragon,
    }
    
    property_identifiers = []

class AppliesToSuperiorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = {
        ItemType.Headpiece: ItemUpgradeId.AppliesToSuperiorRune_Paragon,
        ItemType.Chestpiece: ItemUpgradeId.AppliesToSuperiorRune_Paragon,
        ItemType.Gloves: ItemUpgradeId.AppliesToSuperiorRune_Paragon,
        ItemType.Leggings: ItemUpgradeId.AppliesToSuperiorRune_Paragon,
        ItemType.Boots: ItemUpgradeId.AppliesToSuperiorRune_Paragon,
    }
    
    property_identifiers = []
#endregion Paragon

#endregion Armor Upgrades
_UPGRADES: list[type[Upgrade]] = [
    IcyUpgrade,
    EbonUpgrade,
    ShockingUpgrade,
    FieryUpgrade,
    BarbedUpgrade,
    CripplingUpgrade,
    CruelUpgrade,
    PoisonousUpgrade,
    SilencingUpgrade,
    FuriousUpgrade,
    HeavyUpgrade,
    ZealousUpgrade,
    VampiricUpgrade,
    SunderingUpgrade,
    DefensiveUpgrade,
    InsightfulUpgrade,
    HaleUpgrade,
    OfDefenseUpgrade,
    OfWardingUpgrade,
    OfShelterUpgrade,
    OfSlayingUpgrade,
    OfFortitudeUpgrade,
    OfEnchantingUpgrade,
    OfTheProfessionUpgrade,
    OfAxeMasteryUpgrade,
    OfMarksmanshipUpgrade,
    OfDaggerMasteryUpgrade,
    OfHammerMasteryUpgrade,
    OfScytheMasteryUpgrade,
    OfSpearMasteryUpgrade,
    OfSwordsmanshipUpgrade,
    OfAttributeUpgrade,
    OfMasteryUpgrade,
    SwiftStaffUpgrade,
    AdeptStaffUpgrade,
    OfMemoryUpgrade,
    OfQuickeningUpgrade,
    OfAptitudeUpgrade,
    OfDevotionUpgrade,
    OfValorUpgrade,
    OfEnduranceUpgrade,
    OfSwiftnessUpgrade,
    
    BeJustAndFearNot,
    DownButNotOut,
    FaithIsMyShield,
    ForgetMeNot,
    HailToTheKing,
    IgnoranceIsBliss,
    KnowingIsHalfTheBattle,
    LifeIsPain,
    LiveForToday,
    ManForAllSeasons,
    MightMakesRight,
    SerenityNow,
    SurvivalOfTheFittest,
    BrawnOverBrains,
    DanceWithDeath,
    DontFearTheReaper,
    DontThinkTwice,
    GuidedByFate,
    StrengthAndHonor,
    ToThePain,
    TooMuchInformation,
    VengeanceIsMine,
    IHaveThePower,
    LetTheMemoryLiveAgain,
    CastOutTheUnclean,
    FearCutsDeeper,
    ICanSeeClearlyNow,
    LeafOnTheWind,
    LikeARollingStone,
    LuckOfTheDraw,
    MasterOfMyDomain,
    NotTheFace,
    NothingToFear,
    OnlyTheStrongSurvive,
    PureOfHeart,
    RidersOnTheStorm,
    RunForYourLife,
    ShelteredByFaith,
    SleepNowInTheFire,
    SoundnessOfMind,
    StrengthOfBody,
    SwiftAsTheWind,
    TheRiddleOfSteel,
    ThroughThickAndThin,
    MeasureForMeasure,
    ShowMeTheMoney,
    AptitudeNotAttitude,
    DontCallItAComeback,
    HaleAndHearty,
    HaveFaith,
    IAmSorrow,
    SeizeTheDay,
        
    # No Profession
    SurvivorInsignia,
    RadiantInsignia,
    StalwartInsignia,
    BrawlersInsignia,
    BlessedInsignia,
    HeraldsInsignia,
    SentrysInsignia,
    
    RuneOfMinorVigor,
    RuneOfMinorVigor2,
    RuneOfVitae,
    RuneOfAttunement,
    RuneOfMajorVigor,
    RuneOfRecovery,
    RuneOfRestoration,
    RuneOfClarity,
    RuneOfPurity,
    RuneOfSuperiorVigor,
    
    # Warrior
    KnightsInsignia,
    LieutenantsInsignia,
    StonefistInsignia,
    DreadnoughtInsignia,
    SentinelsInsignia,
    
    RuneOfMinorAbsorption,
    RuneOfMinorTactics,
    RuneOfMinorStrength,
    RuneOfMinorAxeMastery,
    RuneOfMinorHammerMastery,
    RuneOfMinorSwordsmanship,
    RuneOfMajorAbsorption,
    RuneOfMajorTactics,
    RuneOfMajorStrength,
    RuneOfMajorAxeMastery,
    RuneOfMajorHammerMastery,
    RuneOfMajorSwordsmanship,
    RuneOfSuperiorAbsorption,
    RuneOfSuperiorTactics,
    RuneOfSuperiorStrength,
    RuneOfSuperiorAxeMastery,
    RuneOfSuperiorHammerMastery,
    RuneOfSuperiorSwordsmanship,
    
    UpgradeMinorRuneWarrior,
    UpgradeMajorRuneWarrior,
    UpgradeSuperiorRuneWarrior,
    AppliesToMinorRuneWarrior,
    AppliesToMajorRuneWarrior,
    AppliesToSuperiorRuneWarrior,
    
    # Ranger    
    FrostboundInsignia,
    PyreboundInsignia,
    StormboundInsignia,
    ScoutsInsignia,
    EarthboundInsignia,
    BeastmastersInsignia,
    
    RuneOfMinorWildernessSurvival,
    RuneOfMinorExpertise,
    RuneOfMinorBeastMastery,
    RuneOfMinorMarksmanship,
    RuneOfMajorWildernessSurvival,
    RuneOfMajorExpertise,
    RuneOfMajorBeastMastery,
    RuneOfMajorMarksmanship,
    RuneOfSuperiorWildernessSurvival,
    RuneOfSuperiorExpertise,
    RuneOfSuperiorBeastMastery,
    RuneOfSuperiorMarksmanship,
    
    UpgradeMinorRuneRanger,
    UpgradeMajorRuneRanger,
    UpgradeSuperiorRuneRanger,
    AppliesToMinorRuneRanger,
    AppliesToMajorRuneRanger,
    AppliesToSuperiorRuneRanger,
    
    # Monk
    WanderersInsignia,
    DisciplesInsignia,
    AnchoritesInsignia,
    
    RuneOfMinorHealingPrayers,
    RuneOfMinorSmitingPrayers,
    RuneOfMinorProtectionPrayers,
    RuneOfMinorDivineFavor,
    RuneOfMajorHealingPrayers,
    RuneOfMajorSmitingPrayers,
    RuneOfMajorProtectionPrayers,
    RuneOfMajorDivineFavor,
    RuneOfSuperiorHealingPrayers,
    RuneOfSuperiorSmitingPrayers,
    RuneOfSuperiorProtectionPrayers,
    RuneOfSuperiorDivineFavor,
    
    UpgradeMinorRuneMonk,
    UpgradeMajorRuneMonk,
    UpgradeSuperiorRuneMonk,
    AppliesToMinorRuneMonk,
    AppliesToMajorRuneMonk,
    AppliesToSuperiorRuneMonk,
    
    # Necromancer
    BloodstainedInsignia,
    TormentorsInsignia,
    BonelaceInsignia,
    MinionMastersInsignia,
    BlightersInsignia,
    UndertakersInsignia,
    RuneOfMinorBloodMagic,
    RuneOfMinorDeathMagic,
    RuneOfMinorCurses,
    RuneOfMinorSoulReaping,
    RuneOfMajorBloodMagic,
    RuneOfMajorDeathMagic,
    RuneOfMajorCurses,
    RuneOfMajorSoulReaping,
    RuneOfSuperiorBloodMagic,
    RuneOfSuperiorDeathMagic,
    RuneOfSuperiorCurses,
    RuneOfSuperiorSoulReaping,
    
    UpgradeMinorRuneNecromancer,
    UpgradeMajorRuneNecromancer,
    UpgradeSuperiorRuneNecromancer,
    AppliesToMinorRuneNecromancer,
    AppliesToMajorRuneNecromancer,
    AppliesToSuperiorRuneNecromancer,
    
    # Mesmer 
    VirtuososInsignia,
    ArtificersInsignia,
    ProdigysInsignia,
    
    RuneOfMinorFastCasting,
    RuneOfMinorDominationMagic,
    RuneOfMinorIllusionMagic,
    RuneOfMinorInspirationMagic,
    RuneOfMajorFastCasting,
    RuneOfMajorDominationMagic,
    RuneOfMajorIllusionMagic,
    RuneOfMajorInspirationMagic,
    RuneOfSuperiorFastCasting,
    RuneOfSuperiorDominationMagic,
    RuneOfSuperiorIllusionMagic,
    RuneOfSuperiorInspirationMagic,
    
    UpgradeMinorRuneMesmer,
    UpgradeMajorRuneMesmer,
    UpgradeSuperiorRuneMesmer,
    AppliesToMinorRuneMesmer,
    AppliesToMajorRuneMesmer,
    AppliesToSuperiorRuneMesmer,
    
    # Elementalist
    HydromancerInsignia,
    GeomancerInsignia,
    PyromancerInsignia,
    AeromancerInsignia,
    PrismaticInsignia,
    
    RuneOfMinorEnergyStorage,
    RuneOfMinorFireMagic,
    RuneOfMinorAirMagic,
    RuneOfMinorEarthMagic,
    RuneOfMinorWaterMagic,
    RuneOfMajorEnergyStorage,
    RuneOfMajorFireMagic,
    RuneOfMajorAirMagic,
    RuneOfMajorEarthMagic,
    RuneOfMajorWaterMagic,
    RuneOfSuperiorEnergyStorage,
    RuneOfSuperiorFireMagic,
    RuneOfSuperiorAirMagic,
    RuneOfSuperiorEarthMagic,
    RuneOfSuperiorWaterMagic,
    
    UpgradeMinorRuneElementalist,
    UpgradeMajorRuneElementalist,
    UpgradeSuperiorRuneElementalist,
    AppliesToMinorRuneElementalist,
    AppliesToMajorRuneElementalist,
    AppliesToSuperiorRuneElementalist,
    
    # Assassin
    VanguardsInsignia,
    InfiltratorsInsignia,
    SaboteursInsignia,
    NightstalkersInsignia,
    
    RuneOfMinorCriticalStrikes,
    RuneOfMinorDaggerMastery,
    RuneOfMinorDeadlyArts,
    RuneOfMinorShadowArts,
    RuneOfMajorCriticalStrikes,
    RuneOfMajorDaggerMastery,
    RuneOfMajorDeadlyArts,
    RuneOfMajorShadowArts,
    RuneOfSuperiorCriticalStrikes,
    RuneOfSuperiorDaggerMastery,
    RuneOfSuperiorDeadlyArts,
    RuneOfSuperiorShadowArts,
    
    UpgradeMinorRuneAssassin,
    UpgradeMajorRuneAssassin,
    UpgradeSuperiorRuneAssassin,
    AppliesToMinorRuneAssassin,
    AppliesToMajorRuneAssassin,
    AppliesToSuperiorRuneAssassin,
    
    # Ritualist
    ShamansInsignia,
    GhostForgeInsignia,
    MysticsInsignia,
    
    RuneOfMinorChannelingMagic,
    RuneOfMinorRestorationMagic,
    RuneOfMinorCommuning,
    RuneOfMinorSpawningPower,
    RuneOfMajorChannelingMagic,
    RuneOfMajorRestorationMagic,
    RuneOfMajorCommuning,
    RuneOfMajorSpawningPower,
    RuneOfSuperiorChannelingMagic,
    RuneOfSuperiorRestorationMagic,
    RuneOfSuperiorCommuning,
    RuneOfSuperiorSpawningPower,
    
    UpgradeMinorRuneRitualist,
    UpgradeMajorRuneRitualist,
    UpgradeSuperiorRuneRitualist,
    AppliesToMinorRuneRitualist,
    AppliesToMajorRuneRitualist,
    AppliesToSuperiorRuneRitualist,
    
    # Dervish
    WindwalkerInsignia,
    ForsakenInsignia,
    
    RuneOfMinorMysticsm,
    RuneOfMinorEarthPrayers,
    RuneOfMinorScytheMastery,
    RuneOfMinorWindPrayers,
    RuneOfMajorMysticsm,
    RuneOfMajorEarthPrayers,
    RuneOfMajorScytheMastery,
    RuneOfMajorWindPrayers,
    RuneOfSuperiorMysticsm,
    RuneOfSuperiorEarthPrayers,
    RuneOfSuperiorScytheMastery,
    RuneOfSuperiorWindPrayers,
    
    UpgradeMinorRuneDervish,
    UpgradeMajorRuneDervish,
    UpgradeSuperiorRuneDervish,
    AppliesToMinorRuneDervish,
    AppliesToMajorRuneDervish,
    AppliesToSuperiorRuneDervish,
    
    # Paragon
    CenturionsInsignia,
    
    RuneOfMinorLeadership,
    RuneOfMinorMotivation,
    RuneOfMinorCommand,
    RuneOfMinorSpearMastery,
    RuneOfMajorLeadership,
    RuneOfMajorMotivation,
    RuneOfMajorCommand,
    RuneOfMajorSpearMastery,
    RuneOfSuperiorLeadership,
    RuneOfSuperiorMotivation,
    RuneOfSuperiorCommand,
    RuneOfSuperiorSpearMastery,   
    
    UpgradeMinorRuneParagon,
    UpgradeMajorRuneParagon,
    UpgradeSuperiorRuneParagon,
    AppliesToMinorRuneParagon,
    AppliesToMajorRuneParagon,
    AppliesToSuperiorRuneParagon, 
]

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

