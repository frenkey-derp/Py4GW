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
from Sources.frenkeyLib.ItemHandling.upgrades import ItemUpgradeId

#region Item Properties
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

@dataclass
class TargetItemTypeProperty(ItemProperty):
    item_type : ItemType
    
    def describe(self) -> str:
        return f"{self.item_type.name}"
#endregion Item Properties

def get_profession_from_attribute(attribute: Attribute) -> Optional[Profession]:
    for prof, attr in ProfessionAttributes.__dict__.items():
        if isinstance(attr, list) and attribute in attr:
            return Profession[prof]
    return None

def get_upgrade_property(modifier: DecodedModifier, modifiers: list[DecodedModifier]) -> ItemProperty:
    upgrade, upgrade_type = get_upgrade(modifier, modifiers)
    
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
     
def get_upgrade(modifier : DecodedModifier, modifiers: list[DecodedModifier]) -> tuple["Upgrade", ItemUpgradeType]:
    creator_type = next((t for t in _UPGRADES if t.has_id(modifier.upgrade_id)), None)    
    # creator_type, creator = next(((t, up) for t, up in _UPGRADE_FACTORY.items() if modifier.upgrade_id in t.id.values()), (UnknownUpgrade, None))    

    if creator_type is not None:        
        upgrade = creator_type.compose_from_modifiers(modifier, modifiers)
        if upgrade is not None:
            Py4GW.Console.Log("ItemHandling", f"Identified upgrade: {upgrade.name} (ID {modifier.upgrade_id})")
            return upgrade, creator_type.mod_type
    
    return UnknownUpgrade(), ItemUpgradeType.Unknown
        
class Upgrade:
    """
    Abstract base class for item upgrades. Each specific upgrade type (e.g., Prefix, Suffix, Inscription) should inherit from this class and implement the necessary properties and methods.
    """
    mod_type : ItemUpgradeType
    localized_name_format : dict[ServerLanguage, str] = {}
    property_identifiers: list[ModifierIdentifier] = []
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

    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return False
    
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
    item_type_id_map = {}
    property_identifiers = []
    
#region Weapon Upgrades
class WeaponUpgrade(Upgrade):
    item_type_id_map : dict[ItemType, ItemUpgradeId]
    
    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return upgrade_id in cls.item_type_id_map.values()

    
#region Prefixes
WEAPON_PREFIX_ITEM_NAME_FORMAT: dict[ItemType, dict[ServerLanguage, str]] = {
    ItemType.Axe: {
        ServerLanguage.English: "{prefix} Axe Haft",
    },
    ItemType.Bow: {
        ServerLanguage.German: "{prefix} Bogensehne",
        ServerLanguage.English: "{prefix} Bow String",
        ServerLanguage.Korean: "{prefix} 활시위",
        ServerLanguage.French: "Corde {prefix}",
        ServerLanguage.Italian: "Corda d'arco {prefix}",
        ServerLanguage.Spanish: "Cuerda de arco {prefix}",
        ServerLanguage.TraditionalChinese: "{prefix} 弓弦",
        ServerLanguage.Japanese: "{prefix} ボウの弦",
        ServerLanguage.Polish: "Cięciwa {prefix}",
        ServerLanguage.Russian: "{prefix} Bow String",
        ServerLanguage.BorkBorkBork: "{prefix} Boostreeng"
    },
    ItemType.Daggers: {
        ServerLanguage.German: "{prefix} Dolchangel",
        ServerLanguage.English: "{prefix} Dagger Tang",
        ServerLanguage.Korean: "{prefix} 단검자루",
        ServerLanguage.French: "Soie de dague {prefix}",
        ServerLanguage.Italian: "Codolo per Pugnale {prefix}",
        ServerLanguage.Spanish: "Afilador de dagas {prefix}",
        ServerLanguage.TraditionalChinese: "{prefix} 匕首刃",
        ServerLanguage.Japanese: "{prefix} ダガーのグリップ",
        ServerLanguage.Polish: "Uchwyt Sztyletu {prefix}",
        ServerLanguage.Russian: "{prefix} Dagger Tang",
        ServerLanguage.BorkBorkBork: "{prefix} Daegger Tung"
    },
    # ItemType.Offhand does not have a prefix mod, so no name format is needed
    ItemType.Hammer: {
        ServerLanguage.German: "{0} Hammerstiel",
        ServerLanguage.English: "{0} Hammer Haft",
        ServerLanguage.Russian: "{0} Hammer Haft"
    },
    ItemType.Scythe: {
        ServerLanguage.English: "{0} Scythe Snathe",
    },
    # ItemType.Shield does not have a prefix mod, so no name format is needed
    ItemType.Spear: {
        ServerLanguage.German: "{0} Speerspitze",
        ServerLanguage.English: "{0} Spearhead",
        ServerLanguage.Korean: "{0} 흡혈의 창촉",
        ServerLanguage.French: "Tête de javelot {0}",
        ServerLanguage.Italian: "Punta per Lancia {0}",
        ServerLanguage.Spanish: "Punta de lanza {0}",
        ServerLanguage.TraditionalChinese: "{0} 矛頭",
        ServerLanguage.Japanese: "{0} スピアヘッド",
        ServerLanguage.Polish: "Grot Włóczni {0}",
        ServerLanguage.Russian: "{0} Spearhead",
        ServerLanguage.BorkBorkBork: "{0} Speaerheaed"
    },
    ItemType.Staff: {
        ServerLanguage.German: "{0} Stabkopf",
        ServerLanguage.English: "{0} Staff Head",
        ServerLanguage.Korean: "{0} 스태프머리",
        ServerLanguage.French: "Pommeau de bâton {0}",
        ServerLanguage.Italian: "Testa del bastone {0}",
        ServerLanguage.Spanish: "Puño de báculo {0}",
        ServerLanguage.TraditionalChinese: "{0} 法杖頭",
        ServerLanguage.Japanese: "{0} スタッフの頭部",
        ServerLanguage.Polish: "Głowica Kostura {0}",
        ServerLanguage.Russian: "{0} Staff Head",
        ServerLanguage.BorkBorkBork: "{0} Staeffff Heaed"
    },
    ItemType.Sword: {
        ServerLanguage.German: "{0} Schwertheft",
        ServerLanguage.English: "{0} Sword Hilt",
        ServerLanguage.Korean: "{0} 칼자루",
        ServerLanguage.French: "Poignée d'épée {0}",
        ServerLanguage.Italian: "Elsa della spada {0}",
        ServerLanguage.Spanish: "Empuñadura de espada {0}",
        ServerLanguage.TraditionalChinese: "{0} 劍柄",
        ServerLanguage.Japanese: "{0} ソードの柄",
        ServerLanguage.Polish: "Rękojeść Miecza {0}",
        ServerLanguage.Russian: "{0} Sword Hilt",
        ServerLanguage.BorkBorkBork: "{0} Svurd Heelt"
    }, 
    # ItemType.Wand does not have a prefix mod, so no name format is needed    
}

class WeaponPrefix(WeaponUpgrade):
    mod_type = ItemUpgradeType.Prefix

    @classmethod
    def get_weapon_upgrade_name(cls, item_type: ItemType, server_language: ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> Optional[str]:
        if item_type in WEAPON_PREFIX_ITEM_NAME_FORMAT:
            item_type_name_formats = WEAPON_PREFIX_ITEM_NAME_FORMAT.get(item_type, {})
            item_type_name_format = item_type_name_formats.get(server_language, item_type_name_formats.get(ServerLanguage.English, "{prefix} " + item_type.name + " Upgrade"))
            name = cls.localized_name_format.get(server_language, cls.localized_name_format.get(ServerLanguage.English, cls.__class__.__name__))
            return item_type_name_format.format(prefix=name)
        
        return None
    
class AdeptStaffUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Adept_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]

class BarbedUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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

class CripplingUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
    
class CruelUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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

class DefensiveUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Defensive_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
    ]

class EbonUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
    
class FieryUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
    
class FuriousUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
    
class HaleUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Hale_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlus,
    ]

class HeavyUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Axe: ItemUpgradeId.Heavy_Axe,
        ItemType.Hammer: ItemUpgradeId.Heavy_Hammer,
        ItemType.Scythe: ItemUpgradeId.Heavy_Scythe,
        ItemType.Spear: ItemUpgradeId.Heavy_Spear,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]

class IcyUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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

class InsightfulUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Insightful_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
    ]

class PoisonousUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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

class ShockingUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
    
class SilencingUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Bow: ItemUpgradeId.Silencing_Bow,
        ItemType.Daggers: ItemUpgradeId.Silencing_Daggers,
        ItemType.Spear: ItemUpgradeId.Silencing_Spear,
    }
    
    property_identifiers = [
        ModifierIdentifier.IncreaseConditionDuration,
    ]
    
class SunderingUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
    
class SwiftStaffUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Swift_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]

class VampiricUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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

class ZealousUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
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
#endregion Prefixes

#region Suffixes
WEAPON_SUFFIX_ITEM_NAME_FORMAT: dict[ItemType, dict[ServerLanguage, str]] = {
    ItemType.Axe: {
        ServerLanguage.German: "Axtgriff {suffix}",
        ServerLanguage.English: "Axe Grip {suffix}",
        ServerLanguage.Korean: "도끼손잡이 {suffix}",
        ServerLanguage.French: "Poignée de hache {suffix}",
        ServerLanguage.Italian: "Impugnatura dell'ascia {suffix}",
        ServerLanguage.Spanish: "Empuñadura de hacha {suffix}",
        ServerLanguage.TraditionalChinese: "{suffix} 斧把手",
        ServerLanguage.Japanese: "アックスのグリップ {suffix}",
        ServerLanguage.Polish: "Stylisko Topora {suffix}",
        ServerLanguage.Russian: "Axe Grip {suffix}",
        ServerLanguage.BorkBorkBork: "Aexe-a Greep {suffix}",
    },
    ItemType.Bow: {
        ServerLanguage.German: "Bogengriff {suffix}",
        ServerLanguage.English: "Bow Grip {suffix}",
        ServerLanguage.Korean: "활손잡이 {suffix}",
        ServerLanguage.French: "Poignée d'arc {suffix}",
        ServerLanguage.Italian: "Impugnatura dell'arco {suffix}",
        ServerLanguage.Spanish: "Empuñadura de arco {suffix}",
        ServerLanguage.TraditionalChinese: "{suffix} 弓柄",
        ServerLanguage.Japanese: "ボウのグリップ {suffix}",
        ServerLanguage.Polish: "Łęczysko {suffix}",
        ServerLanguage.Russian: "Bow Grip {suffix}",
        ServerLanguage.BorkBorkBork: "Boo Greep {suffix}"
    },
    ItemType.Daggers: {
        ServerLanguage.German: "Dolchgriff {0}",
        ServerLanguage.English: "Dagger Handle {0}",
        ServerLanguage.Korean: "단검손자루 {0}",
        ServerLanguage.French: "Poignée de dague {0}",
        ServerLanguage.Italian: "Impugnatura per Pugnale {0}",
        ServerLanguage.Spanish: "Empuñadura para daga {0}",
        ServerLanguage.TraditionalChinese: "{0} 匕首握柄",
        ServerLanguage.Japanese: "ダガーの柄 {0}",
        ServerLanguage.Polish: "Rękojeść Sztyletu {0}",
        ServerLanguage.Russian: "Dagger Handle {0}",
        ServerLanguage.BorkBorkBork: "Daegger Hundle-a {0}"
    },
    ItemType.Offhand: {
        ServerLanguage.German: "Fokus-Kern {0}",
        ServerLanguage.English: "Focus Core {0}",
        ServerLanguage.Korean: "포커스장식 {0}",
        ServerLanguage.French: "Noyau de focus {0}",
        ServerLanguage.Italian: "Nucleo del Focus {0}",
        ServerLanguage.Spanish: "Mango de foco {0}",
        ServerLanguage.TraditionalChinese: "{0} 聚能器核心",
        ServerLanguage.Japanese: "フォーカスのグリップ {0}",
        ServerLanguage.Polish: "Rdzeń Fokusu {0}",
        ServerLanguage.Russian: "Focus Core {0}",
        ServerLanguage.BorkBorkBork: "Fucoos Cure-a {0}"
    },
    ItemType.Hammer: {
        ServerLanguage.German: "Hammergriff {0}",
        ServerLanguage.English: "Hammer Grip {0}",
        ServerLanguage.Korean: "해머손잡이{0}",
        ServerLanguage.French: "Poignée de marteau {0}",
        ServerLanguage.Italian: "Impugnatura del martello {0}",
        ServerLanguage.Spanish: "Empuñadura de martillo {0}",
        ServerLanguage.TraditionalChinese: "{0} 鎚把手",
        ServerLanguage.Japanese: "ハンマーのグリップ {0}",
        ServerLanguage.Polish: "Uchwyt Młota {0}",
        ServerLanguage.Russian: "Hammer Grip {0}",
        ServerLanguage.BorkBorkBork: "Haemmer Greep {0}"
    },
    ItemType.Scythe: {
        ServerLanguage.German: "Sensengriff {0}",
        ServerLanguage.English: "Scythe Grip {0}",
        ServerLanguage.Korean: "사이드손잡이 {0}",
        ServerLanguage.French: "Poignée de faux {0}",
        ServerLanguage.Italian: "Impugnatura {0}",
        ServerLanguage.Spanish: "Empuñadura de guadaña {0}",
        ServerLanguage.TraditionalChinese: "{0} 鐮刀把",
        ServerLanguage.Japanese: "サイズのグリップ {0}",
        ServerLanguage.Polish: "Drzewce Kosy {0}",
        ServerLanguage.Russian: "Scythe Grip {0}",
        ServerLanguage.BorkBorkBork: "Scyzee Greep {0}"
    },
    ItemType.Shield: {
        ServerLanguage.German: "Schildgriff {0}",
        ServerLanguage.English: "Shield Handle {0}",
        ServerLanguage.Korean: "방패손잡이 {0}",
        ServerLanguage.French: "Poignée de bouclier {0}",
        ServerLanguage.Italian: "Impugnatura dello Scudo {0}",
        ServerLanguage.Spanish: "Mango de escudo {0}",
        ServerLanguage.TraditionalChinese: "{0} 盾握柄",
        ServerLanguage.Japanese: "シールドの柄 {0}",
        ServerLanguage.Polish: "Uchwyt Tarczy {0}",
        ServerLanguage.Russian: "Shield Handle {0}",
        ServerLanguage.BorkBorkBork: "Sheeeld Hundle-a {0}"
    },
    ItemType.Spear: {
        ServerLanguage.German: "Speergriff {0}",
        ServerLanguage.English: "Spear Grip {0}",
        ServerLanguage.Korean: "창손잡이(네크로맨서) {0}",
        ServerLanguage.French: "Poignée de javelot {0}",
        ServerLanguage.Italian: "Impugnatura della Lancia {0}",
        ServerLanguage.Spanish: "Empuñadura de lanza {0}",
        ServerLanguage.TraditionalChinese: "the Necromancer 矛柄 {0}",
        ServerLanguage.Japanese: "スピアのグリップ (ネクロマンサー) {0}",
        ServerLanguage.Polish: "Drzewce Włóczni {0}",
        ServerLanguage.Russian: "Spear Grip of некромант {0}",
        ServerLanguage.BorkBorkBork: "Speaer Greep {0}"
    },
    ItemType.Staff: {
        ServerLanguage.German: "Stabhülle {0}",
        ServerLanguage.English: "Staff Wrapping {0}",
        ServerLanguage.Korean: "스태프손잡이{0}",
        ServerLanguage.French: "Gaine de bâton {0}",
        ServerLanguage.Italian: "Fascia del bastone {0}",
        ServerLanguage.Spanish: "Envoltura de báculo {0}",
        ServerLanguage.TraditionalChinese: "{0} 法杖把手",
        ServerLanguage.Japanese: "スタッフの柄 {0}",
        ServerLanguage.Polish: "Okład Kostura {0}",
        ServerLanguage.Russian: "Staff Wrapping {0}",
        ServerLanguage.BorkBorkBork: "Staeffff Vraeppeeng {0}"
    },
    ItemType.Sword: {
        ServerLanguage.German: "Schwertknauf {0}",
        ServerLanguage.English: "Sword Pommel {0}",
        ServerLanguage.Korean: "칼머리 {0}",
        ServerLanguage.French: "Pommeau d'épée {0}",
        ServerLanguage.Italian: "Pomolo della spada {0}",
        ServerLanguage.Spanish: "Pomo de espada {0}",
        ServerLanguage.TraditionalChinese: "{0} 劍柄首",
        ServerLanguage.Japanese: "ソードの柄頭 {0}",
        ServerLanguage.Polish: "Głowica Miecza {0}",
        ServerLanguage.Russian: "Sword Pommel {0}",
        ServerLanguage.BorkBorkBork: "Svurd Pummel {0}"
    }, 
    ItemType.Wand: {
        ServerLanguage.German: "Zauberstab-Hülle {0}",
        ServerLanguage.English: "Wand Wrapping {0}",
        ServerLanguage.Korean: "지팡이자루 {0}",
        ServerLanguage.French: "Gaine de baguette {0}",
        ServerLanguage.Italian: "Fascia della Bacchetta {0}",
        ServerLanguage.Spanish: "Envoltura de varita {0}",
        ServerLanguage.TraditionalChinese: "{0} 魔杖把手",
        ServerLanguage.Japanese: "ワンドの布 {0}",
        ServerLanguage.Polish: "Okład Różdżki {0}",
        ServerLanguage.Russian: "Wand Wrapping {0}",
        ServerLanguage.BorkBorkBork: "Vund Vraeppeeng {0}"
    },
}

class WeaponSuffix(WeaponUpgrade):
    mod_type = ItemUpgradeType.Suffix
    
    @classmethod
    def get_weapon_upgrade_name(cls, item_type: ItemType, server_language: ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> Optional[str]:
        if item_type in WEAPON_PREFIX_ITEM_NAME_FORMAT:
            item_type_name_formats = WEAPON_PREFIX_ITEM_NAME_FORMAT.get(item_type, {})
            item_type_name_format = item_type_name_formats.get(server_language, item_type_name_formats.get(ServerLanguage.English, item_type.name + " Upgrade of {prefix}"))
            name = cls.localized_name_format.get(server_language, cls.localized_name_format.get(ServerLanguage.English, cls.__class__.__name__))
            return item_type_name_format.format(prefix=name)
        
        return None
    
class OfAttributeUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.OfAttribute_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    
class OfAptitudeUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Offhand: ItemUpgradeId.OfAptitude_Focus,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]

class OfAxeMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Axe: ItemUpgradeId.OfAxeMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfDaggerMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Daggers: ItemUpgradeId.OfDaggerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]   
    
class OfDefenseUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
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

class OfDevotionUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
        ItemType.Shield: ItemUpgradeId.OfDevotion_Shield,
        ItemType.Offhand: ItemUpgradeId.OfDevotion_Focus,
        ItemType.Staff: ItemUpgradeId.OfDevotion_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlusEnchanted,
    ]

class OfEnchantingUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
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

class OfEnduranceUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
        ItemType.Offhand: ItemUpgradeId.OfEndurance_Focus,
        ItemType.Shield: ItemUpgradeId.OfEndurance_Shield,
        ItemType.Staff: ItemUpgradeId.OfEndurance_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlusStance,
    ]

class OfFortitudeUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
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

class OfHammerMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Hammer: ItemUpgradeId.OfHammerMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfMarksmanshipUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Bow: ItemUpgradeId.OfMarksmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.OfMastery_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOneItem,
    ]

class OfMemoryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Wand: ItemUpgradeId.OfMemory_Wand,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeItemAttribute,
    ]

class OfQuickeningUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Wand: ItemUpgradeId.OfQuickening_Wand,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]

class OfScytheMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Scythe: ItemUpgradeId.OfScytheMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    
class OfShelterUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
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

class OfSlayingUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
        ItemType.Axe: ItemUpgradeId.OfSlaying_Axe,
        ItemType.Bow: ItemUpgradeId.OfSlaying_Bow,
        ItemType.Hammer: ItemUpgradeId.OfSlaying_Hammer,
        ItemType.Sword: ItemUpgradeId.OfSlaying_Sword,
        ItemType.Staff: ItemUpgradeId.OfSlaying_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsSpecies,
    ]

class OfSpearMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Spear: ItemUpgradeId.OfSpearMastery,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfSwiftnessUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
        ItemType.Offhand: ItemUpgradeId.OfSwiftness_Focus,
    }
    
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]

class OfSwordsmanshipUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Sword: ItemUpgradeId.OfSwordsmanship,
    }
    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]

class OfTheProfessionUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
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

class OfValorUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
        ItemType.Offhand: ItemUpgradeId.OfValor_Focus,
        ItemType.Shield: ItemUpgradeId.OfValor_Shield,
        ItemType.Staff: ItemUpgradeId.OfValor_Staff,
    }
    
    property_identifiers = [
        ModifierIdentifier.HealthPlusHexed,
    ]

class OfWardingUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
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
#endregion Suffixes

#region Inscriptions
class Inscription(Upgrade):
    inventory_icon : str
    id : ItemUpgradeId
    localized_names : dict[ServerLanguage, str] = {}
    target_item_type : ItemType
    
    INSCRIPTION_LOCALIZATION = {
            ServerLanguage.English: "Inscription: {name}",
            ServerLanguage.German: "Inschrift: {name}",
            ServerLanguage.French: "Inscription : {name}",
            ServerLanguage.Spanish: "Inscripción: {name}",
            ServerLanguage.Italian: "Iscrizione: {name}",
            ServerLanguage.TraditionalChinese: "鑄印：{name}",
            ServerLanguage.Korean: "마력석: {name}",
            ServerLanguage.Japanese: "刻印：{name}",
            ServerLanguage.Polish: "Inskrypcja: {name}",
            ServerLanguage.Russian: "Надпись: {name}",
            ServerLanguage.BorkBorkBork: "Inscreepshun: {name}"
        }
    
    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return upgrade_id == cls.id
    
    @property
    def name(self) -> str:
        language = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))
        inscription_format = self.INSCRIPTION_LOCALIZATION.get(language, self.INSCRIPTION_LOCALIZATION[ServerLanguage.English])
        return inscription_format.format(name=self.localized_names.get(language, self.localized_names.get(ServerLanguage.English, "")))

#region Offhand
class BeJustAndFearNot(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.BeJustAndFearNot    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusHexed,
    ]

class DownButNotOut(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.DownButNotOut    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusWhileDown
    ]

class FaithIsMyShield(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.FaithIsMyShield    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusEnchanted,
    ]

class ForgetMeNot(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.ForgetMeNot    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeItemAttribute,
    ]

class HailToTheKing(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.HailToTheKing    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusAbove,
    ]

class IgnoranceIsBliss(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.IgnoranceIsBliss    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
        ModifierIdentifier.EnergyMinus,
    ]

class KnowingIsHalfTheBattle(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.KnowingIsHalfTheBattle
    property_identifiers = [
        ModifierIdentifier.ArmorPlusCasting,
    ]

class LifeIsPain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.LifeIsPain    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
        ModifierIdentifier.HealthMinus,
    ]

class LiveForToday(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.LiveForToday    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
        ModifierIdentifier.EnergyDegen,
    ]

class ManForAllSeasons(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.ManForAllSeasons    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsElemental,
    ]

class MightMakesRight(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.MightMakesRight    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusAttacking,
    ]

class SerenityNow(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.SerenityNow        
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]

class SurvivalOfTheFittest(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.SurvivalOfTheFittest    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]
#endregion Offhand

#region Weapon

class BrawnOverBrains(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.BrawnOverBrains
    property_identifiers = [
        ModifierIdentifier.DamagePlusPercent,
        ModifierIdentifier.EnergyMinus,
    ]

class DanceWithDeath(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.DanceWithDeath
    property_identifiers = [
        ModifierIdentifier.DamagePlusStance,
    ]

class DontFearTheReaper(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.DontFearTheReaper
    property_identifiers = [
        ModifierIdentifier.DamagePlusHexed,
    ]

class DontThinkTwice(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.DontThinkTwice
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]

class GuidedByFate(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.GuidedByFate
    property_identifiers = [
        ModifierIdentifier.DamagePlusEnchanted,
    ]

class StrengthAndHonor(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.StrengthAndHonor
    property_identifiers = [
        ModifierIdentifier.DamagePlusWhileUp,
    ]

class ToThePain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.ToThePain
    property_identifiers = [
        ModifierIdentifier.DamagePlusPercent,
        ModifierIdentifier.ArmorMinusAttacking
    ]

class TooMuchInformation(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.TooMuchInformation
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusVsHexed,
    ]

class VengeanceIsMine(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.VengeanceIsMine
    
    property_identifiers = [
        ModifierIdentifier.DamagePlusWhileDown,
    ]

#endregion Weapon

#region MartialWeapon
class IHaveThePower(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.MartialWeapon
    id = ItemUpgradeId.IHaveThePower
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
    ]

class LetTheMemoryLiveAgain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.MartialWeapon
    id = ItemUpgradeId.LetTheMemoryLiveAgain
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]

#endregion MartialWeapon

#region OffhandOrShield
class CastOutTheUnclean(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.CastOutTheUnclean    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class FearCutsDeeper(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.FearCutsDeeper    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class ICanSeeClearlyNow(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.ICanSeeClearlyNow
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,   
    ]

class LeafOnTheWind(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.LeafOnTheWind    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class LikeARollingStone(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.LikeARollingStone    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class LuckOfTheDraw(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.LuckOfTheDraw
    property_identifiers = [
        ModifierIdentifier.ReceiveLessDamage,
    ]

class MasterOfMyDomain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.MasterOfMyDomain    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOneItem,
    ]

class NotTheFace(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.NotTheFace    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage
    ]

class NothingToFear(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.NothingToFear
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageHexed,
    ]

class OnlyTheStrongSurvive(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.OnlyTheStrongSurvive    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class PureOfHeart(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.PureOfHeart
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class RidersOnTheStorm(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.RidersOnTheStorm
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class RunForYourLife(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.RunForYourLife
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageStance,
    ]

class ShelteredByFaith(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.ShelteredByFaith    
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageEnchanted,
    ]

class SleepNowInTheFire(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.SleepNowInTheFire        
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class SoundnessOfMind(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.SoundnessOfMind
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class StrengthOfBody(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.StrengthOfBody
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class SwiftAsTheWind(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.SwiftAsTheWind
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]

class TheRiddleOfSteel(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.TheRiddleOfSteel    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]

class ThroughThickAndThin(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.ThroughThickAndThin
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
#endregion OffhandOrShield

#region EquippableItem
class MeasureForMeasure(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.EquippableItem
    id = ItemUpgradeId.MeasureForMeasure
    property_identifiers = [
        ModifierIdentifier.HighlySalvageable,
    ]
    
class ShowMeTheMoney(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.EquippableItem
    id = ItemUpgradeId.ShowMeTheMoney
    property_identifiers = [
        ModifierIdentifier.IncreasedSaleValue,
    ]    
#endregion EquippableItem

#region SpellcastingWeapon
class AptitudeNotAttitude(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.AptitudeNotAttitude
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]

class DontCallItAComeback(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.DontCallItAComeback    
    property_identifiers = [
        ModifierIdentifier.EnergyPlusWhileBelow,
    ]

class HaleAndHearty(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.HaleAndHearty
    property_identifiers = [
        ModifierIdentifier.EnergyPlusWhileDown,
    ]

class HaveFaith(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.HaveFaith
    property_identifiers = [
        ModifierIdentifier.EnergyPlusEnchanted,
    ]

class IAmSorrow(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.IAmSorrow        
    property_identifiers = [
        ModifierIdentifier.EnergyPlusHexed,
    ]

class SeizeTheDay(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.SeizeTheDay    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
        ModifierIdentifier.EnergyDegen,
    ]
#endregion SpellcastingWeapon
#endregion Inscriptions

#endregion Weapon Upgrades

#region Armor Upgrades
class Insignia(Upgrade):
    id : ItemUpgradeId
    mod_type = ItemUpgradeType.Prefix
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    localized_name_format : dict[ServerLanguage, str] = {}

    INSIGNIA_LOCALIZATION = {
        ServerLanguage.English: "Insignia",
        ServerLanguage.Spanish: "Insignia",
        ServerLanguage.Italian: "Insegna",
        ServerLanguage.German: "Befähigung",
        ServerLanguage.Korean: "휘장",
        ServerLanguage.French: "Insigne",
        ServerLanguage.TraditionalChinese: "徽記",
        ServerLanguage.Japanese: "記章",
        ServerLanguage.Polish: "Symbol",
        ServerLanguage.Russian: "Insignia",
        ServerLanguage.BorkBorkBork: "Inseegneea"
    }

    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return cls.id is not None and upgrade_id == cls.id

    @property
    def name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(item_name=Insignia.INSIGNIA_LOCALIZATION.get(language, "Insignia"))

    @classmethod
    def add_to_item_name(cls, item_name: str, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(name=cls.get_name(language), item_name=item_name)

class Rune(Upgrade):
    id : ItemUpgradeId
    mod_type = ItemUpgradeType.Suffix
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    localized_name_format : dict[ServerLanguage, str] = {}

    RANK_LOCALIZATION = {
        Rarity.Blue: {
            ServerLanguage.English: "Minor",
            ServerLanguage.Spanish: "de grado menor",
            ServerLanguage.Italian: "di grado minore",
            ServerLanguage.German: "d. kleineren",
            ServerLanguage.Korean: "하급",
            ServerLanguage.French: "bonus mineur",
            ServerLanguage.TraditionalChinese: "初級",
            ServerLanguage.Japanese: "マイナー",
            ServerLanguage.Polish: "niższego poziomu",
            ServerLanguage.Russian: "Minor",
            ServerLanguage.BorkBorkBork: "Meenur"
        },
        Rarity.Purple: {
            ServerLanguage.English: "Major",
            ServerLanguage.Spanish: "de grado mayor",
            ServerLanguage.Italian: "di grado maggiore",
            ServerLanguage.German: "d. hohen",
            ServerLanguage.Korean: "상급",
            ServerLanguage.French: "bonus majeur",
            ServerLanguage.TraditionalChinese: "中級",
            ServerLanguage.Japanese: "メジャー",
            ServerLanguage.Polish: "wyższego poziomu",
            ServerLanguage.Russian: "Major",
            ServerLanguage.BorkBorkBork: "Maejur"
            },
        Rarity.Gold: {
            ServerLanguage.English: "Superior",
            ServerLanguage.Spanish: "de grado excepcional",
            ServerLanguage.Italian: "di grado supremo",
            ServerLanguage.German: "d. überlegenen",
            ServerLanguage.Korean: "고급",
            ServerLanguage.French: "bonus supérieur",
            ServerLanguage.TraditionalChinese: "高級",
            ServerLanguage.Japanese: "スーペリア",
            ServerLanguage.Polish: "najwyższego poziomu",
            ServerLanguage.Russian: "Superior",
            ServerLanguage.BorkBorkBork: "Soopereeur"
        }
    }

    RUNE_LOCALIZATION = {
        ServerLanguage.English: "Rune",
        ServerLanguage.Spanish: "Runa",
        ServerLanguage.Italian: "Runa",
        ServerLanguage.German: "Rune",
        ServerLanguage.Korean: "룬",
        ServerLanguage.French: "Rune",
        ServerLanguage.TraditionalChinese: "符文",
        ServerLanguage.Japanese: "ルーン",
        ServerLanguage.Polish: "Runa",
        ServerLanguage.Russian: "Rune",
        ServerLanguage.BorkBorkBork: "Roone-a"
    }

    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return cls.id is not None and upgrade_id == cls.id

    @property
    def name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(item_name=Insignia.INSIGNIA_LOCALIZATION.get(language, "Insignia"))

    @classmethod
    def add_to_item_name(cls, item_name: str, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(name=cls.get_name(language), item_name=item_name)

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
    id = ItemUpgradeId.Survivor

class RadiantInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Radiant

class StalwartInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Stalwart
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]

class BrawlersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Brawlers

class BlessedInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Blessed

class HeraldsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Heralds

class SentrysInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Sentrys

class RuneOfMinorVigor(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorVigor

class RuneOfMinorVigor2(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorVigor2

class RuneOfVitae(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfVitae

class RuneOfAttunement(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfAttunement

class RuneOfMajorVigor(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorVigor

class RuneOfRecovery(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfRecovery
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfRestoration(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfRestoration
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfClarity(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfClarity
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfPurity(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfPurity
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfSuperiorVigor(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorVigor
#endregion No Profession

#region Warrior

class KnightsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Knights

class LieutenantsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Lieutenants

class StonefistInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Stonefist

class DreadnoughtInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Dreadnought

class SentinelsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Sentinels

class RuneOfMinorAbsorption(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorAbsorption

class RuneOfMinorTactics(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorTactics

class RuneOfMinorStrength(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorStrength

class RuneOfMinorAxeMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorAxeMastery

class RuneOfMinorHammerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorHammerMastery

class RuneOfMinorSwordsmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSwordsmanship

class RuneOfMajorAbsorption(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorAbsorption

class RuneOfMajorTactics(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorTactics

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorStrength(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorStrength

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorAxeMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorAxeMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorHammerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorHammerMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorSwordsmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSwordsmanship

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorAbsorption(Rune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorAbsorption

class RuneOfSuperiorTactics(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorTactics

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorStrength(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorStrength

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorAxeMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorAxeMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorHammerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorHammerMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorSwordsmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSwordsmanship

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Warrior

class UpgradeMajorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Warrior

class UpgradeSuperiorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Warrior

class AppliesToMinorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Warrior

class AppliesToMajorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Warrior

class AppliesToSuperiorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Warrior
#endregion Warrior

#region Ranger

class FrostboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Frostbound

class PyreboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Pyrebound

class StormboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Stormbound

class ScoutsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Scouts

class EarthboundInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Earthbound

class BeastmastersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Beastmasters

class RuneOfMinorWildernessSurvival(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorWildernessSurvival

class RuneOfMinorExpertise(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorExpertise

class RuneOfMinorBeastMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorBeastMastery

class RuneOfMinorMarksmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorMarksmanship

class RuneOfMajorWildernessSurvival(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorWildernessSurvival

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorExpertise(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorExpertise

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorBeastMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorBeastMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorMarksmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorMarksmanship

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorWildernessSurvival(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorWildernessSurvival

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorExpertise(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorExpertise

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorBeastMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorBeastMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorMarksmanship(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorMarksmanship

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Ranger

class UpgradeMajorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Ranger

class UpgradeSuperiorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Ranger

class AppliesToMinorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Ranger

class AppliesToMajorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Ranger

class AppliesToSuperiorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Ranger
#endregion Ranger

#region Monk

class WanderersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Wanderers

class DisciplesInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Disciples

class AnchoritesInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Anchorites

class RuneOfMinorHealingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorHealingPrayers

class RuneOfMinorSmitingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSmitingPrayers

class RuneOfMinorProtectionPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorProtectionPrayers

class RuneOfMinorDivineFavor(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDivineFavor

class RuneOfMajorHealingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorHealingPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorSmitingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSmitingPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorProtectionPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorProtectionPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorDivineFavor(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDivineFavor

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorHealingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorHealingPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorSmitingPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSmitingPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorProtectionPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorProtectionPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorDivineFavor(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDivineFavor

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Monk

class UpgradeMajorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Monk

class UpgradeSuperiorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Monk

class AppliesToMinorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Monk

class AppliesToMajorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Monk

class AppliesToSuperiorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Monk
#endregion Monk

#region Necromancer

class BloodstainedInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Bloodstained

class TormentorsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Tormentors

class BonelaceInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Bonelace

class MinionMastersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.MinionMasters

class BlightersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Blighters

class UndertakersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Undertakers

class RuneOfMinorBloodMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorBloodMagic

class RuneOfMinorDeathMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDeathMagic

class RuneOfMinorCurses(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCurses

class RuneOfMinorSoulReaping(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSoulReaping

class RuneOfMajorBloodMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorBloodMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorDeathMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDeathMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorCurses(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCurses

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorSoulReaping(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSoulReaping

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorBloodMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorBloodMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorDeathMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDeathMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorCurses(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCurses

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorSoulReaping(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSoulReaping

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Necromancer

class UpgradeMajorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Necromancer

class UpgradeSuperiorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Necromancer

class AppliesToMinorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Necromancer

class AppliesToMajorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Necromancer

class AppliesToSuperiorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Necromancer
#endregion Necromancer

#region Mesmer

class VirtuososInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Virtuosos

class ArtificersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Artificers

class ProdigysInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Prodigys

class RuneOfMinorFastCasting(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorFastCasting

class RuneOfMinorDominationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDominationMagic

class RuneOfMinorIllusionMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorIllusionMagic

class RuneOfMinorInspirationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorInspirationMagic

class RuneOfMajorFastCasting(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorFastCasting

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorDominationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDominationMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorIllusionMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorIllusionMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorInspirationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorInspirationMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorFastCasting(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorFastCasting

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorDominationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDominationMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorIllusionMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorIllusionMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorInspirationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorInspirationMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Mesmer

class UpgradeMajorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Mesmer

class UpgradeSuperiorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Mesmer

class AppliesToMinorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Mesmer

class AppliesToMajorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Mesmer

class AppliesToSuperiorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Mesmer
#endregion Mesmer

#region Elementalist

class HydromancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Hydromancer

class GeomancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Geomancer

class PyromancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Pyromancer

class AeromancerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Aeromancer

class PrismaticInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Prismatic

class RuneOfMinorEnergyStorage(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorEnergyStorage

class RuneOfMinorFireMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorFireMagic

class RuneOfMinorAirMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorAirMagic

class RuneOfMinorEarthMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorEarthMagic

class RuneOfMinorWaterMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorWaterMagic

class RuneOfMajorEnergyStorage(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorEnergyStorage

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorFireMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorFireMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorAirMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorAirMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorEarthMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorEarthMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorWaterMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorWaterMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorEnergyStorage(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorEnergyStorage

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorFireMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorFireMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorAirMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorAirMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorEarthMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorEarthMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorWaterMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorWaterMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Elementalist

class UpgradeMajorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Elementalist

class UpgradeSuperiorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Elementalist

class AppliesToMinorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Elementalist

class AppliesToMajorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Elementalist

class AppliesToSuperiorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Elementalist
#endregion Elementalist

#region Assassin

class VanguardsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Vanguards

class InfiltratorsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Infiltrators

class SaboteursInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Saboteurs

class NightstalkersInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Nightstalkers

class RuneOfMinorCriticalStrikes(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCriticalStrikes

class RuneOfMinorDaggerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDaggerMastery

class RuneOfMinorDeadlyArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDeadlyArts

class RuneOfMinorShadowArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorShadowArts

class RuneOfMajorCriticalStrikes(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCriticalStrikes

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorDaggerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDaggerMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorDeadlyArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDeadlyArts

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorShadowArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorShadowArts

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorCriticalStrikes(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCriticalStrikes

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorDaggerMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDaggerMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorDeadlyArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDeadlyArts

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorShadowArts(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorShadowArts

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Assassin

class UpgradeMajorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Assassin

class UpgradeSuperiorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Assassin

class AppliesToMinorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Assassin

class AppliesToMajorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Assassin

class AppliesToSuperiorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Assassin
#endregion Assassin

#region Ritualist

class ShamansInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Shamans

class GhostForgeInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.GhostForge

class MysticsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Mystics

class RuneOfMinorChannelingMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorChannelingMagic

class RuneOfMinorRestorationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorRestorationMagic

class RuneOfMinorCommuning(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCommuning

class RuneOfMinorSpawningPower(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSpawningPower

class RuneOfMajorChannelingMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorChannelingMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorRestorationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorRestorationMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorCommuning(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCommuning

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorSpawningPower(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSpawningPower

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorChannelingMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorChannelingMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorRestorationMagic(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorRestorationMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorCommuning(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCommuning

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorSpawningPower(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSpawningPower

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Ritualist

class UpgradeMajorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Ritualist

class UpgradeSuperiorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Ritualist

class AppliesToMinorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Ritualist

class AppliesToMajorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Ritualist

class AppliesToSuperiorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Ritualist
#endregion Ritualist

#region Dervish

class WindwalkerInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Windwalker

class ForsakenInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Forsaken

class RuneOfMinorMysticsm(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorMysticism

class RuneOfMinorEarthPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorEarthPrayers

class RuneOfMinorScytheMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorScytheMastery

class RuneOfMinorWindPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorWindPrayers

class RuneOfMajorMysticsm(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorMysticism

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorEarthPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorEarthPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorScytheMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorScytheMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorWindPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorWindPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorMysticsm(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorMysticism

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorEarthPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorEarthPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorScytheMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorScytheMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorWindPrayers(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorWindPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Dervish

class UpgradeMajorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Dervish

class UpgradeSuperiorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Dervish

class AppliesToMinorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Dervish

class AppliesToMajorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Dervish

class AppliesToSuperiorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Dervish
#endregion Dervish

#region Paragon

class CenturionsInsignia(Insignia):
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Centurions

class RuneOfMinorLeadership(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorLeadership

class RuneOfMinorMotivation(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorMotivation

class RuneOfMinorCommand(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCommand

class RuneOfMinorSpearMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSpearMastery

class RuneOfMajorLeadership(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorLeadership

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorMotivation(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorMotivation

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorCommand(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCommand

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfMajorSpearMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSpearMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorLeadership(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorLeadership

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorMotivation(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorMotivation

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorCommand(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCommand

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RuneOfSuperiorSpearMastery(AttributeRune):
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSpearMastery

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Paragon

class UpgradeMajorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Paragon

class UpgradeSuperiorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Paragon

class AppliesToMinorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Paragon

class AppliesToMajorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Paragon

class AppliesToSuperiorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Paragon
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
    ModifierIdentifier.TargetItemType: lambda m, _: TargetItemTypeProperty(modifier=m, item_type=ItemType(m.arg1)),
    ModifierIdentifier.AttributeRune: lambda m, mods: get_upgrade_property(m, mods),
    ModifierIdentifier.Insignia_RuneOfAbsorption: lambda m, mods: get_upgrade_property(m, mods),
}

