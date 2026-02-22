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
    names = {
		ServerLanguage.English: "Adept",
		ServerLanguage.Spanish: "de adepto",
		ServerLanguage.Italian: "da Adepto",
		ServerLanguage.German: "Experten-",
		ServerLanguage.Korean: "숙련된",
		ServerLanguage.French: "d'adepte",
		ServerLanguage.TraditionalChinese: "行家",
		ServerLanguage.Japanese: "アデプト",
		ServerLanguage.Polish: "Adepta",
		ServerLanguage.Russian: "Adept",
		ServerLanguage.BorkBorkBork: "Aedept",
	}
    
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
    names = {
		ServerLanguage.English: "Barbed",
		ServerLanguage.Spanish: "con espinas",
		ServerLanguage.Italian: "a Punta",
		ServerLanguage.German: "Stachel-",
		ServerLanguage.Korean: "가시 박힌",
		ServerLanguage.French: "à pointes",
		ServerLanguage.TraditionalChinese: "荊棘",
		ServerLanguage.Japanese: "バーブ",
		ServerLanguage.Polish: "Kolców",
		ServerLanguage.Russian: "Barbed",
		ServerLanguage.BorkBorkBork: "Baerbed",
	}
    
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
    names = {
		ServerLanguage.English: "Crippling",
		ServerLanguage.Spanish: "letal",
		ServerLanguage.Italian: "Azzoppante",
		ServerLanguage.German: "Verkrüppelungs-",
		ServerLanguage.Korean: "치명적인",
		ServerLanguage.French: "d'infirmité",
		ServerLanguage.TraditionalChinese: "致殘",
		ServerLanguage.Japanese: "クリップル",
		ServerLanguage.Polish: "Kaleczenia",
		ServerLanguage.Russian: "Crippling",
		ServerLanguage.BorkBorkBork: "Creeppleeng",
	}
        
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
    names = {
		ServerLanguage.English: "Cruel",
		ServerLanguage.Spanish: "cruel",
		ServerLanguage.Italian: "Crudele",
		ServerLanguage.German: "Grausamkeits-",
		ServerLanguage.Korean: "잔인한",
		ServerLanguage.French: "atroce",
		ServerLanguage.TraditionalChinese: "殘酷",
		ServerLanguage.Japanese: "クルーエル",
		ServerLanguage.Polish: "Okrucieństwa",
		ServerLanguage.Russian: "Cruel",
		ServerLanguage.BorkBorkBork: "Crooel",
	}

class DefensiveUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Defensive_Staff,
    }
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
    ]
    names = {
		ServerLanguage.English: "Defensive",
		ServerLanguage.Spanish: "de defensa",
		ServerLanguage.Italian: "da Difesa",
		ServerLanguage.German: "Verteidigungs-",
		ServerLanguage.Korean: "방어적인",
		ServerLanguage.French: "défensif",
		ServerLanguage.TraditionalChinese: "防衛",
		ServerLanguage.Japanese: "ディフェンス",
		ServerLanguage.Polish: "Obrony",
		ServerLanguage.Russian: "Defensive",
		ServerLanguage.BorkBorkBork: "Deffenseefe-a",
	}
    
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
    names = {
		ServerLanguage.English: "Ebon",
		ServerLanguage.Spanish: "con daño de granito",
		ServerLanguage.Italian: "per danno d'ebano",
		ServerLanguage.German: "Ebon-",
		ServerLanguage.Korean: "흑단",
		ServerLanguage.French: "terrestre",
		ServerLanguage.TraditionalChinese: "黑檀",
		ServerLanguage.Japanese: "エボン",
		ServerLanguage.Polish: "z Hebanu",
		ServerLanguage.Russian: "Ebon",
		ServerLanguage.BorkBorkBork: "Ibun",
	}
    
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
    names = {
		ServerLanguage.English: "Fiery",
		ServerLanguage.Spanish: "con daño ardiente",
		ServerLanguage.Italian: "per danno da fuoco",
		ServerLanguage.German: "Hitze-",
		ServerLanguage.Korean: "화염의",
		ServerLanguage.French: "incendiaire",
		ServerLanguage.TraditionalChinese: "火焰",
		ServerLanguage.Japanese: "ファイア",
		ServerLanguage.Polish: "Ognia",
		ServerLanguage.Russian: "Fiery",
		ServerLanguage.BorkBorkBork: "Feeery",
	}
    
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
    names = {
		ServerLanguage.English: "Furious",
		ServerLanguage.Spanish: "de furor",
		ServerLanguage.Italian: "della Furia",
		ServerLanguage.German: "Zorn-",
		ServerLanguage.Korean: "격노한",
		ServerLanguage.French: "de fureur",
		ServerLanguage.TraditionalChinese: "狂怒",
		ServerLanguage.Japanese: "フューリアス",
		ServerLanguage.Polish: "Wściekłości",
		ServerLanguage.Russian: "Furious",
		ServerLanguage.BorkBorkBork: "Fooreeuoos",
	}
    
class HaleUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Hale_Staff,
    }
    property_identifiers = [
        ModifierIdentifier.HealthPlus,
    ]
    names = {
		ServerLanguage.English: "Hale",
		ServerLanguage.Spanish: "de robustez",
		ServerLanguage.Italian: "del Vigore",
		ServerLanguage.German: "Rüstigkeits-",
		ServerLanguage.Korean: "단단한",
		ServerLanguage.French: "de vigueur",
		ServerLanguage.TraditionalChinese: "健壯",
		ServerLanguage.Japanese: "ヘイル",
		ServerLanguage.Polish: "Wigoru",
		ServerLanguage.Russian: "Hale",
		ServerLanguage.BorkBorkBork: "Haele-a",
	}
    
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
    names = {
		ServerLanguage.English: "Heavy",
		ServerLanguage.Spanish: "fuerte",
		ServerLanguage.Italian: "Pesante",
		ServerLanguage.German: "Schwergewichts-",
		ServerLanguage.Korean: "무거운",
		ServerLanguage.French: "de poids",
		ServerLanguage.TraditionalChinese: "沉重",
		ServerLanguage.Japanese: "ヘヴィー",
		ServerLanguage.Polish: "Ciężaru",
		ServerLanguage.Russian: "Heavy",
		ServerLanguage.BorkBorkBork: "Heaefy",
	}
    
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
    names = {
		ServerLanguage.English: "Icy",
		ServerLanguage.Spanish: "con daño frío",
		ServerLanguage.Italian: "per danno da ghiaccio",
		ServerLanguage.German: "Eis-",
		ServerLanguage.Korean: "냉기",
		ServerLanguage.French: "polaire",
		ServerLanguage.TraditionalChinese: "冰凍",
		ServerLanguage.Japanese: "アイス",
		ServerLanguage.Polish: "Lodu",
		ServerLanguage.Russian: "Icy",
		ServerLanguage.BorkBorkBork: "Icy",
	}
    
class InsightfulUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Insightful_Staff,
    }
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
    ]
    names = {
		ServerLanguage.English: "Insightful",
		ServerLanguage.Spanish: "de visión",
		ServerLanguage.Italian: "dell'Astuzia",
		ServerLanguage.German: "Einblick-",
		ServerLanguage.Korean: "통찰력의",
		ServerLanguage.French: "de vision",
		ServerLanguage.TraditionalChinese: "洞察",
		ServerLanguage.Japanese: "インサイト",
		ServerLanguage.Polish: "Przenikliwości",
		ServerLanguage.Russian: "Insightful",
		ServerLanguage.BorkBorkBork: "Inseeghtffool",
	}
    
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
    names = {
		ServerLanguage.English: "Poisonous",
		ServerLanguage.Spanish: "con veneno",
		ServerLanguage.Italian: "del Veleno",
		ServerLanguage.German: "Gift-",
		ServerLanguage.Korean: "맹독의",
		ServerLanguage.French: "de poison",
		ServerLanguage.TraditionalChinese: "淬毒",
		ServerLanguage.Japanese: "ポイズン",
		ServerLanguage.Polish: "Zatrucia",
		ServerLanguage.Russian: "Poisonous",
		ServerLanguage.BorkBorkBork: "Pueesunuoos",
	}
    
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
    names = {
		ServerLanguage.English: "Shocking",
		ServerLanguage.Spanish: "con daño de descarga",
		ServerLanguage.Italian: "per danno da shock",
		ServerLanguage.German: "Schock-",
		ServerLanguage.Korean: "충격의",
		ServerLanguage.French: "de foudre",
		ServerLanguage.TraditionalChinese: "電擊",
		ServerLanguage.Japanese: "ショック",
		ServerLanguage.Polish: "Porażenia",
		ServerLanguage.Russian: "Shocking",
		ServerLanguage.BorkBorkBork: "Shuckeeng",
	}
    
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
    names = {
		ServerLanguage.English: "Silencing",
		ServerLanguage.Spanish: "de silencio",
		ServerLanguage.Italian: "del Silenzio",
		ServerLanguage.German: "Dämpfungs-",
		ServerLanguage.Korean: "침묵의",
		ServerLanguage.French: "de silence",
		ServerLanguage.TraditionalChinese: "沈默",
		ServerLanguage.Japanese: "サイレンス",
		ServerLanguage.Polish: "Uciszenia",
		ServerLanguage.Russian: "Silencing",
		ServerLanguage.BorkBorkBork: "Seelenceeng",
	}
    
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
    names = {
		ServerLanguage.English: "Sundering",
		ServerLanguage.Spanish: "de penetración",
		ServerLanguage.Italian: "della Separazione",
		ServerLanguage.German: "Trenn-",
		ServerLanguage.Korean: "날카로운",
		ServerLanguage.French: "de fractionnement",
		ServerLanguage.TraditionalChinese: "分離",
		ServerLanguage.Japanese: "サンダリング",
		ServerLanguage.Polish: "Rozdzierania",
		ServerLanguage.Russian: "Sundering",
		ServerLanguage.BorkBorkBork: "Soondereeng",
	}
    
class SwiftStaffUpgrade(WeaponPrefix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.Swift_Staff,
    }
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]
    names = {
		ServerLanguage.English: "Swift",
		ServerLanguage.Spanish: "veloz",
		ServerLanguage.Italian: "della Rapidità",
		ServerLanguage.German: "Schnelligkeits-",
		ServerLanguage.Korean: "재빠른",
		ServerLanguage.French: "rapide",
		ServerLanguage.TraditionalChinese: "迅速",
		ServerLanguage.Japanese: "スウィフト",
		ServerLanguage.Polish: "Szybkości",
		ServerLanguage.Russian: "Swift",
		ServerLanguage.BorkBorkBork: "Sveefft",
	}
    
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
    names = {
		ServerLanguage.English: "Vampiric",
		ServerLanguage.Spanish: "de vampiro",
		ServerLanguage.Italian: "del Vampiro",
		ServerLanguage.German: "Vampir-",
		ServerLanguage.Korean: "흡혈의 단검자루",
		ServerLanguage.French: "vampirique",
		ServerLanguage.TraditionalChinese: "吸血鬼 匕首刃",
		ServerLanguage.Japanese: "ヴァンピリック ダガーのグリップ",
		ServerLanguage.Polish: "Wampiryzmu",
		ServerLanguage.Russian: "Vampiric",
		ServerLanguage.BorkBorkBork: "Faempureec",
	}
    
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
    names = {
		ServerLanguage.English: "Zealous",
		ServerLanguage.Spanish: "de afán",
		ServerLanguage.Italian: "Zelante",
		ServerLanguage.German: "Eifer-",
		ServerLanguage.Korean: "광신도의",
		ServerLanguage.French: "de zèle",
		ServerLanguage.TraditionalChinese: "熱望",
		ServerLanguage.Japanese: "ゼラス",
		ServerLanguage.Polish: "Fanatyzmu",
		ServerLanguage.Russian: "Zealous",
		ServerLanguage.BorkBorkBork: "Zeaeluoos",
	}
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
    
    #TODO: This is a temporary solution to the fact that the name of this upgrade is not localized in the game files. Once it is, this can be removed and the name can be pulled from the game files like all other upgrades.
    names = {
		ServerLanguage.English: "of {attribute}",
		ServerLanguage.Spanish: "({attribute})",
		ServerLanguage.Italian: "dell'{attribute}",
		ServerLanguage.German: "d. {attribute}",
		ServerLanguage.Korean: "({attribute})",
		ServerLanguage.French: "({attribute})",
		ServerLanguage.TraditionalChinese: "{attribute}",
		ServerLanguage.Japanese: "({attribute})",
		ServerLanguage.Polish: "({attribute})",
		ServerLanguage.Russian: "of {attribute}",
		ServerLanguage.BorkBorkBork: "ooff {attribute}",
	}
    
class OfAptitudeUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Offhand: ItemUpgradeId.OfAptitude_Focus,
    }
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]
    names = {
		ServerLanguage.English: "of Aptitude",
		ServerLanguage.Spanish: "(de aptitud)",
		ServerLanguage.Italian: "della Perspicacia",
		ServerLanguage.German: "d. Begabung",
		ServerLanguage.Korean: "(총명)",
		ServerLanguage.French: "(d'aptitude)",
		ServerLanguage.TraditionalChinese: "天賦",
		ServerLanguage.Japanese: "(アプティテュード)",
		ServerLanguage.Polish: "(Uzdolnienia)",
		ServerLanguage.Russian: "of Aptitude",
		ServerLanguage.BorkBorkBork: "ooff Aepteetoode-a",
	}
    
class OfAxeMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Axe: ItemUpgradeId.OfAxeMastery,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    names = {
		ServerLanguage.English: "of Axe Mastery",
		ServerLanguage.Spanish: "(Dominio del hacha)",
		ServerLanguage.Italian: "Abilità con l'Ascia",
		ServerLanguage.German: "d. Axtbeherrschung",
		ServerLanguage.Korean: "(도끼술)",
		ServerLanguage.French: "(Maîtrise de la hache)",
		ServerLanguage.TraditionalChinese: "精通斧術",
		ServerLanguage.Japanese: "(アックス マスタリー)",
		ServerLanguage.Polish: "(Biegłość w Toporach)",
		ServerLanguage.Russian: "of Axe Mastery",
		ServerLanguage.BorkBorkBork: "ooff Aexe-a Maestery",
	}
    
class OfDaggerMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Daggers: ItemUpgradeId.OfDaggerMastery,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]   
    names = {
		ServerLanguage.English: "of Dagger Mastery",
		ServerLanguage.Spanish: "(Dominio de la daga)",
		ServerLanguage.Italian: "Abilità con il Pugnale",
		ServerLanguage.German: "d. Dolchbeherrschung",
		ServerLanguage.Korean: "(단검술)",
		ServerLanguage.French: "(Maîtrise de la dague)",
		ServerLanguage.TraditionalChinese: "匕首精通",
		ServerLanguage.Japanese: "(ダガー マスタリー)",
		ServerLanguage.Polish: "(Biegłość w Sztyletach)",
		ServerLanguage.Russian: "of Dagger Mastery",
		ServerLanguage.BorkBorkBork: "ooff Daegger Maestery",
	}
    
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
    names = {
		ServerLanguage.English: "of Defense",
		ServerLanguage.Spanish: "(de protección)",
		ServerLanguage.Italian: "di Difesa",
		ServerLanguage.German: "d. Verteidigung",
		ServerLanguage.Korean: "(방어)",
		ServerLanguage.French: "(de Défense)",
		ServerLanguage.TraditionalChinese: "防衛",
		ServerLanguage.Japanese: "(ディフェンス)",
		ServerLanguage.Polish: "(Obrony)",
		ServerLanguage.Russian: "of Defense",
		ServerLanguage.BorkBorkBork: "ooff Deffense-a",
	}
    
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
    names = {
		ServerLanguage.English: "of Devotion",
		ServerLanguage.Spanish: "(de devoción)",
		ServerLanguage.Italian: "della Devozione",
		ServerLanguage.German: "d. Hingabe",
		ServerLanguage.Korean: "(헌신)",
		ServerLanguage.French: "(de dévotion)",
		ServerLanguage.TraditionalChinese: "奉獻",
		ServerLanguage.Japanese: "(ディボーション)",
		ServerLanguage.Polish: "(Oddania)",
		ServerLanguage.Russian: "of Devotion",
		ServerLanguage.BorkBorkBork: "ooff Defushun",
	}
    
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
    names = {
		ServerLanguage.English: "of Enchanting",
		ServerLanguage.Spanish: "(de encantamientos)",
		ServerLanguage.Italian: "dell'Incantesimo",
		ServerLanguage.German: "d. Verzauberung",
		ServerLanguage.Korean: "(강화)",
		ServerLanguage.French: "(d'Enchantement)",
		ServerLanguage.TraditionalChinese: "附魔",
		ServerLanguage.Japanese: "(エンチャント)",
		ServerLanguage.Polish: "(Zaklinania)",
		ServerLanguage.Russian: "of Enchanting",
		ServerLanguage.BorkBorkBork: "ooff Inchunteeng",
	}
    
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
    names = {
		ServerLanguage.English: "of Endurance",
		ServerLanguage.Spanish: "(de resistencia)",
		ServerLanguage.Italian: "della Resistenza",
		ServerLanguage.German: "d. Ausdauer",
		ServerLanguage.Korean: "(인내)",
		ServerLanguage.French: "(d'endurance)",
		ServerLanguage.TraditionalChinese: "忍耐",
		ServerLanguage.Japanese: "(インデュランス)",
		ServerLanguage.Polish: "(Wytrzymałości)",
		ServerLanguage.Russian: "of Endurance",
		ServerLanguage.BorkBorkBork: "ooff Indoorunce-a",
	}
    
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
    names = {
		ServerLanguage.English: "of Fortitude",
		ServerLanguage.Spanish: "(con poder)",
		ServerLanguage.Italian: "del Coraggio",
		ServerLanguage.German: "d. Tapferkeit",
		ServerLanguage.Korean: "(견고)",
		ServerLanguage.French: "(de Courage)",
		ServerLanguage.TraditionalChinese: "堅忍",
		ServerLanguage.Japanese: "(フォーティチュード)",
		ServerLanguage.Polish: "(Wytrwałości)",
		ServerLanguage.Russian: "of Fortitude",
		ServerLanguage.BorkBorkBork: "ooff Furteetoode-a",
	}
    
class OfHammerMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Hammer: ItemUpgradeId.OfHammerMastery,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    names = {
		ServerLanguage.English: "of Hammer Mastery",
		ServerLanguage.Spanish: "(Dominio del martillo)",
		ServerLanguage.Italian: "Abilità col Martello",
		ServerLanguage.German: "d. Hammerbeherrschung",
		ServerLanguage.Korean: "(해머술)",
		ServerLanguage.French: "(Maîtrise du marteau)",
		ServerLanguage.TraditionalChinese: "精通鎚術",
		ServerLanguage.Japanese: "(ハンマー マスタリー)",
		ServerLanguage.Polish: "(Biegłość w Młotach)",
		ServerLanguage.Russian: "of Hammer Mastery",
		ServerLanguage.BorkBorkBork: "ooff Haemmer Maestery",
	}
    
class OfMarksmanshipUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Bow: ItemUpgradeId.OfMarksmanship,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    names = {
		ServerLanguage.English: "of Marksmanship",
		ServerLanguage.Spanish: "(Puntería)",
		ServerLanguage.Italian: "Precisione",
		ServerLanguage.German: "d. Treffsicherheit",
		ServerLanguage.Korean: "(궁술)",
		ServerLanguage.French: "(Adresse au tir)",
		ServerLanguage.TraditionalChinese: "弓術精通",
		ServerLanguage.Japanese: "(ボウ マスタリー)",
		ServerLanguage.Polish: "(Umiejętności Strzeleckie)",
		ServerLanguage.Russian: "of Marksmanship",
		ServerLanguage.BorkBorkBork: "ooff Maerksmunsheep",
	}
    
class OfMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Staff: ItemUpgradeId.OfMastery_Staff,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOneItem,
    ]
    names = {
		ServerLanguage.English: "of Mastery",
		ServerLanguage.Spanish: "(de maestría)",
		ServerLanguage.Italian: "della Destrezza da Difesa",
		ServerLanguage.German: "d. Beherrschung",
		ServerLanguage.Korean: "(지배)",
		ServerLanguage.French: "(de maîtrise)",
		ServerLanguage.TraditionalChinese: "支配",
		ServerLanguage.Japanese: "(マスタリー)",
		ServerLanguage.Polish: "(Mistrzostwa)",
		ServerLanguage.Russian: "of Mastery",
		ServerLanguage.BorkBorkBork: "ooff Maestery",
	}
    
class OfMemoryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Wand: ItemUpgradeId.OfMemory_Wand,
    }
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeItemAttribute,
    ]
    names = {
		ServerLanguage.English: "of Memory",
		ServerLanguage.Spanish: "(de memoria)",
		ServerLanguage.Italian: "della Memoria",
		ServerLanguage.German: "d. Erinnerung",
		ServerLanguage.Korean: "(기억)",
		ServerLanguage.French: "(de mémoire)",
		ServerLanguage.TraditionalChinese: "記憶",
		ServerLanguage.Japanese: "(メモリー)",
		ServerLanguage.Polish: "(Pamięci)",
		ServerLanguage.Russian: "of Memory",
		ServerLanguage.BorkBorkBork: "ooff Memury",
	}
class OfQuickeningUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Wand: ItemUpgradeId.OfQuickening_Wand,
    }
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]
    names = {
		ServerLanguage.English: "of Quickening",
		ServerLanguage.Spanish: "(de aceleración)",
		ServerLanguage.Italian: "dell'Accelerazione",
		ServerLanguage.German: "d. Beschleunigung",
		ServerLanguage.Korean: "(활기)",
		ServerLanguage.French: "(de rapidité)",
		ServerLanguage.TraditionalChinese: "復甦",
		ServerLanguage.Japanese: "(クイックニング)",
		ServerLanguage.Polish: "(Przyspieszenia)",
		ServerLanguage.Russian: "of Quickening",
		ServerLanguage.BorkBorkBork: "ooff Qooeeckeneeng",
	}
    
class OfScytheMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Scythe: ItemUpgradeId.OfScytheMastery,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    names = {
		ServerLanguage.English: "of Scythe Mastery",
		ServerLanguage.Spanish: "(Dominio de la guadaña)",
		ServerLanguage.Italian: "Abilità con la Falce",
		ServerLanguage.German: "d. Sensenbeherrschung",
		ServerLanguage.Korean: "(사이드술)",
		ServerLanguage.French: "(Maîtrise de la faux)",
		ServerLanguage.TraditionalChinese: "鐮刀精通",
		ServerLanguage.Japanese: "(サイズ マスタリー)",
		ServerLanguage.Polish: "(Biegłość w Kosach)",
		ServerLanguage.Russian: "of Scythe Mastery",
		ServerLanguage.BorkBorkBork: "ooff Scyzee Maestery",
	}
    
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
    names = {
		ServerLanguage.English: "of Shelter",
		ServerLanguage.Spanish: "(de refugio)",
		ServerLanguage.Italian: "del Riparo",
		ServerLanguage.German: "d. Zuflucht",
		ServerLanguage.Korean: "(보호)",
		ServerLanguage.French: "(de Refuge)",
		ServerLanguage.TraditionalChinese: "庇護",
		ServerLanguage.Japanese: "(シェルター)",
		ServerLanguage.Polish: "(Ochrony)",
		ServerLanguage.Russian: "of Shelter",
		ServerLanguage.BorkBorkBork: "ooff Shelter",
	}
    
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

    #TODO: Localize the name of this suffix

class OfSpearMasteryUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Spear: ItemUpgradeId.OfSpearMastery,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    names = {
		ServerLanguage.English: "of Spear Mastery",
		ServerLanguage.Spanish: "(Dominio de la lanza)",
		ServerLanguage.Italian: "Abilità con la Lancia",
		ServerLanguage.German: "d. Speerbeherrschung",
		ServerLanguage.Korean: "(창술)",
		ServerLanguage.French: "(Maîtrise du javelot)",
		ServerLanguage.TraditionalChinese: "矛術精通",
		ServerLanguage.Japanese: "(スピア マスタリー)",
		ServerLanguage.Polish: "(Biegłość we Włóczniach)",
		ServerLanguage.Russian: "of Spear Mastery",
		ServerLanguage.BorkBorkBork: "ooff Speaer Maestery",
	}
    
class OfSwiftnessUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Suffix
    item_type_id_map = {
        ItemType.Offhand: ItemUpgradeId.OfSwiftness_Focus,
    }
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]
    names = {
		ServerLanguage.English: "of Swiftness",
		ServerLanguage.Spanish: "(de rapidez)",
		ServerLanguage.Italian: "della Rapidità",
		ServerLanguage.German: "d. Eile",
		ServerLanguage.Korean: "(신속)",
		ServerLanguage.French: "(de Rapidité)",
		ServerLanguage.TraditionalChinese: "迅捷",
		ServerLanguage.Japanese: "(スウィフトネス)",
		ServerLanguage.Polish: "(Szybkości)",
		ServerLanguage.Russian: "of Swiftness",
		ServerLanguage.BorkBorkBork: "ooff Sveefftness",
	}
    
class OfSwordsmanshipUpgrade(WeaponSuffix):
    mod_type = ItemUpgradeType.Prefix
    item_type_id_map = {
        ItemType.Sword: ItemUpgradeId.OfSwordsmanship,
    }
    property_identifiers = [
        ModifierIdentifier.AttributePlusOne,
    ]
    names = {
		ServerLanguage.English: "of Swordsmanship",
		ServerLanguage.Spanish: "(Esgrima)",
		ServerLanguage.Italian: "Scherma",
		ServerLanguage.German: "d. Schwertkunst",
		ServerLanguage.Korean: "(검술)",
		ServerLanguage.French: "(Maîtrise de l'épée)",
		ServerLanguage.TraditionalChinese: "精通劍術",
		ServerLanguage.Japanese: "(ソード マスタリー)",
		ServerLanguage.Polish: "(Biegłość w Mieczach)",
		ServerLanguage.Russian: "of Swordsmanship",
		ServerLanguage.BorkBorkBork: "ooff Svurdsmunsheep",
	}
    
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
    names = {
		ServerLanguage.English: "of the {profession}",
		ServerLanguage.Spanish: "(el {profession})",
		ServerLanguage.Italian: "dell'arco il {profession}",
		ServerLanguage.German: "d. des {profession}",
		ServerLanguage.Korean: "({profession})",
		ServerLanguage.French: "(le {profession})",
		ServerLanguage.TraditionalChinese: "{profession}",
		ServerLanguage.Japanese: "({profession})",
		ServerLanguage.Polish: "({profession})",
		ServerLanguage.Russian: "of {profession}",
		ServerLanguage.BorkBorkBork: "ooff zee {profession}",
	}
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
    names = {
		ServerLanguage.English: "of Valor",
		ServerLanguage.Spanish: "(de valor)",
		ServerLanguage.Italian: "del Valore",
		ServerLanguage.German: "d. Wertschätzung",
		ServerLanguage.Korean: "(용맹)",
		ServerLanguage.French: "(de valeur)",
		ServerLanguage.TraditionalChinese: "英勇",
		ServerLanguage.Japanese: "(ヴァラー)",
		ServerLanguage.Polish: "(Odwagi)",
		ServerLanguage.Russian: "of Valor",
		ServerLanguage.BorkBorkBork: "ooff Faelur",
	}
    
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
    names = {
		ServerLanguage.English: "of Warding",
		ServerLanguage.Spanish: "(de guardia)",
		ServerLanguage.Italian: "della Protezione",
		ServerLanguage.German: "d. Abwehr",
		ServerLanguage.Korean: "(결계)",
		ServerLanguage.French: "(du Protecteur)",
		ServerLanguage.TraditionalChinese: "結界",
		ServerLanguage.Japanese: "(ウォーディング)",
		ServerLanguage.Polish: "(Zapobiegliwości)",
		ServerLanguage.Russian: "of Warding",
		ServerLanguage.BorkBorkBork: "ooff Vaerdeeng",
	}
#endregion Suffixes

#region Inscriptions
class Inscription(Upgrade):
    inventory_icon : str
    id : ItemUpgradeId
    names : dict[ServerLanguage, str] = {}
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
        return inscription_format.format(name=self.names.get(language, self.names.get(ServerLanguage.English, "")))

#region Offhand
class BeJustAndFearNot(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.BeJustAndFearNot    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusHexed,
    ]
    names = {
		ServerLanguage.English: "\"Be Just and Fear Not\"",
	}
    
class DownButNotOut(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.DownButNotOut    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusWhileDown
    ]
    names = {
		ServerLanguage.English: "\"Down But Not Out\"",
	}
    
class FaithIsMyShield(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.FaithIsMyShield    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusEnchanted,
    ]
    names = {
		ServerLanguage.English: "\"Faith is My Shield\"",
		ServerLanguage.Spanish: "\"La fe es mi escudo\"",
		ServerLanguage.Italian: "\"La Fede è il Mio Scudo\"",
		ServerLanguage.German: "\"Der Glaube ist mein Schild!\"",
		ServerLanguage.Korean: "신념은 나의 방패다",
		ServerLanguage.French: "\"La foi est mon bouclier\"",
		ServerLanguage.TraditionalChinese: "\"信念是盾\"",
		ServerLanguage.Japanese: "フェイス イズ マイ シールド",
		ServerLanguage.Polish: "\"Wiara jest mą tarczą\"",
		ServerLanguage.Russian: "\"Вера послужит мне щитом\"",
		ServerLanguage.BorkBorkBork: "\"Faeeet is My Sheeeld\"",
	}
    
class ForgetMeNot(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.ForgetMeNot    
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeItemAttribute,
    ]
    names = {
		ServerLanguage.English: "\"Forget Me Not\"",
		ServerLanguage.Spanish: "\"No me olvides\"",
		ServerLanguage.Italian: "\"Non Ti Scordar di Me\"",
		ServerLanguage.German: "\"Vergesst mein nicht!\"",
		ServerLanguage.Korean: "물망초",
		ServerLanguage.French: "\"Souvenir gravé à jamais\"",
		ServerLanguage.TraditionalChinese: "\"勿忘我\"",
		ServerLanguage.Japanese: "フォーゲット ミー ノット",
		ServerLanguage.Polish: "\"Nie zapomnij mnie\"",
		ServerLanguage.Russian: "\"Незабудка\"",
		ServerLanguage.BorkBorkBork: "\"Furget Me-a Nut\"",
	}
    
class HailToTheKing(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.HailToTheKing    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusAbove,
    ]
    names = {
		ServerLanguage.English: "\"Hail to the King\"",
		ServerLanguage.Spanish: "\"Viva el rey\"",
		ServerLanguage.Italian: "\"Viva il Re\"",
		ServerLanguage.German: "\"Gelobt sei der König\"",
		ServerLanguage.Korean: "국왕 폐하 만세",
		ServerLanguage.French: "\"Longue vie au roi\"",
		ServerLanguage.TraditionalChinese: "\"與王致敬\"",
		ServerLanguage.Japanese: "ヘイル トゥ ザ キング",
		ServerLanguage.Polish: "\"Niech żyje król\"",
		ServerLanguage.Russian: "\"Да здравствует король!\"",
		ServerLanguage.BorkBorkBork: "\"Haeeel tu zee Keeng\"",
	}
    
class IgnoranceIsBliss(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.IgnoranceIsBliss    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
        ModifierIdentifier.EnergyMinus,
    ]
    names = {
		ServerLanguage.English: "\"Ignorance is Bliss\"",
		ServerLanguage.Spanish: "\"La ignorancia es felicidad\"",
		ServerLanguage.Italian: "\"Benedetta Ignoranza\"",
		ServerLanguage.German: "\"Was ich nicht weiß ...\"",
		ServerLanguage.Korean: "모르는 게 약이다",
		ServerLanguage.French: "\"Il vaut mieux ne pas savoir\"",
		ServerLanguage.TraditionalChinese: "\"傻人有傻福\"",
		ServerLanguage.Japanese: "イグノーランス イズ ブリス",
		ServerLanguage.Polish: "\"Ignorancja jest błogosławieństwem\"",
		ServerLanguage.Russian: "\"Счастлив в неведении\"",
		ServerLanguage.BorkBorkBork: "\"Ignurunce-a is Bleess\"",
	}
    
class KnowingIsHalfTheBattle(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.KnowingIsHalfTheBattle
    property_identifiers = [
        ModifierIdentifier.ArmorPlusCasting,
    ]
    names = {
		ServerLanguage.English: "\"Knowing is Half the Battle\"",
	}
    
class LifeIsPain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.LifeIsPain    
    property_identifiers = [
        ModifierIdentifier.ArmorPlus,
        ModifierIdentifier.HealthMinus,
    ]
    names = {
		ServerLanguage.English: "\"Life is Pain\"",
	}
    
class LiveForToday(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.LiveForToday    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
        ModifierIdentifier.EnergyDegen,
    ]
    names = {
		ServerLanguage.English: "\"Live for Today\"",
		ServerLanguage.Spanish: "\"Vive el presente\"",
		ServerLanguage.Italian: "\"Vivi alla Giornata\"",
		ServerLanguage.German: "\"Lebt den Tag\"",
		ServerLanguage.Korean: "오늘을 위해 최선을",
		ServerLanguage.French: "\"Aujourd'hui, la vie\"",
		ServerLanguage.TraditionalChinese: "\"活在當下\"",
		ServerLanguage.Japanese: "リブ フォー トゥデイ",
		ServerLanguage.Polish: "\"Żyj dniem dzisiejszym\"",
		ServerLanguage.Russian: "\"Живи сегодняшним днем\"",
		ServerLanguage.BorkBorkBork: "\"Leefe-a fur Tudaey\"",
	}
    
class ManForAllSeasons(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.ManForAllSeasons    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsElemental,
    ]
    names = {
		ServerLanguage.English: "\"Man for All Seasons\"",
	}
    
class MightMakesRight(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.MightMakesRight    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusAttacking,
    ]
    names = {
		ServerLanguage.English: "\"Might Makes Right\"",
	}
    
class SerenityNow(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.SerenityNow        
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]
    names = {
		ServerLanguage.English: "\"Serenity Now\"",
		ServerLanguage.Spanish: "\"Calma ahora\"",
		ServerLanguage.Italian: "\"Serenità Immediata\"",
		ServerLanguage.German: "\"Auf die Gelassenheit\"",
		ServerLanguage.Korean: "평정을 찾아라",
		ServerLanguage.French: "\"Un peu de sérénité\"",
		ServerLanguage.TraditionalChinese: "\"平靜\"",
		ServerLanguage.Japanese: "セレニティ ナウ",
		ServerLanguage.Polish: "\"Niech nastanie spokój\"",
		ServerLanguage.Russian: "\"Спокойствие, только спокойствие!\"",
		ServerLanguage.BorkBorkBork: "\"Sereneety Noo\"",
	}
    
class SurvivalOfTheFittest(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Offhand
    id = ItemUpgradeId.SurvivalOfTheFittest    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]
    names = {
		ServerLanguage.English: "\"Survival of the Fittest\"",
		ServerLanguage.Spanish: "\"Supervivencia del más fuerte\"",
		ServerLanguage.Italian: "\"Sopravvivenza Integrale\"",
		ServerLanguage.German: "\"Hart wie Stahl\"",
		ServerLanguage.Korean: "적자생존",
		ServerLanguage.French: "\"La survie du plus fort\"",
		ServerLanguage.TraditionalChinese: "\"適者生存\"",
		ServerLanguage.Japanese: "サバイバル オブ ザ フィッテスト",
		ServerLanguage.Polish: "\"Przetrwają najsilniejsi\"",
		ServerLanguage.Russian: "\"Естественный отбор\"",
		ServerLanguage.BorkBorkBork: "\"Soorfeefael ooff zee Feettest\"",
	}
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
    names = {
		ServerLanguage.English: "\"Brawn over Brains\"",
		ServerLanguage.Spanish: "\"Más vale maña que fuerza\"",
		ServerLanguage.Italian: "\"Più Muscoli che Cervello\"",
		ServerLanguage.German: "\"Körper über Geist\"",
		ServerLanguage.Korean: "힘보다는 머리",
		ServerLanguage.French: "\"Tout en muscles\"",
		ServerLanguage.TraditionalChinese: "\"有勇無謀\"",
		ServerLanguage.Japanese: "ブローン オーバー ブレイン",
		ServerLanguage.Polish: "\"Siła ponad umysł\"",
		ServerLanguage.Russian: "\"Сила есть -ума не надо\"",
		ServerLanguage.BorkBorkBork: "\"Braevn oofer Braeeens\"",
	}
        
class DanceWithDeath(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.DanceWithDeath
    property_identifiers = [
        ModifierIdentifier.DamagePlusStance,
    ]
    names = {
		ServerLanguage.English: "\"Dance with Death\"",
		ServerLanguage.Spanish: "\"Baila con la muerte\"",
		ServerLanguage.Italian: "\"Balla coi Lutti\"",
		ServerLanguage.German: "\"Tanz mit dem Tod\"",
		ServerLanguage.Korean: "마력석: 죽음과 함께 춤을",
		ServerLanguage.French: "\"Danse avec la mort\"",
		ServerLanguage.TraditionalChinese: "\"與死亡共舞\"",
		ServerLanguage.Japanese: "ダンス ウィズ デス",
		ServerLanguage.Polish: "\"Taniec ze śmiercią\"",
		ServerLanguage.Russian: "\"Танец со смертью\"",
		ServerLanguage.BorkBorkBork: "\"Dunce-a veet Deaet\"",
	}
         
class DontFearTheReaper(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.DontFearTheReaper
    property_identifiers = [
        ModifierIdentifier.DamagePlusHexed,
    ]
    names = {
		ServerLanguage.English: "\"Don't Fear the Reaper\"",
		ServerLanguage.Spanish: "\"No temas la guadaña\"",
		ServerLanguage.Italian: "\"Non Temere la Falce\"",
		ServerLanguage.German: "\"Keine Angst vorm Sensenmann\"",
		ServerLanguage.Korean: "사신을 두려워하지 마라",
		ServerLanguage.French: "\"Ne craignez pas le Faucheur\"",
		ServerLanguage.TraditionalChinese: "\"無懼死亡\"",
		ServerLanguage.Japanese: "ドント フィアー ザ リーパー",
		ServerLanguage.Polish: "\"Nie bój się żniwiarza\"",
		ServerLanguage.Russian: "\"Не бойся жнеца\"",
		ServerLanguage.BorkBorkBork: "\"Dun't Feaer zee Reaeper\"",
	}
    
class DontThinkTwice(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.DontThinkTwice
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeGeneral,
    ]
    names = {
		ServerLanguage.English: "\"Don't Think Twice\"",
		ServerLanguage.Spanish: "\"No te lo pienses\"",
		ServerLanguage.Italian: "\"Non Pensarci Due Volte\"",
		ServerLanguage.German: "\"Zauderei ist keine Zier\"",
		ServerLanguage.Korean: "두 번 생각하지 마라",
		ServerLanguage.French: "\"Pas le temps de réfléchir\"",
		ServerLanguage.TraditionalChinese: "\"別再考慮\"",
		ServerLanguage.Japanese: "ドント シンク トゥワイス",
		ServerLanguage.Polish: "\"Nie zastanawiaj się\"",
		ServerLanguage.Russian: "\"А что тут думать?\"",
		ServerLanguage.BorkBorkBork: "\"Dun't Theenk Tveece-a\"",
	}
    
class GuidedByFate(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.GuidedByFate
    property_identifiers = [
        ModifierIdentifier.DamagePlusEnchanted,
    ]
    names = {
		ServerLanguage.English: "\"Guided by Fate\"",
		ServerLanguage.Spanish: "\"Guiado por el destino\"",
		ServerLanguage.Italian: "\"Guidato dal Fato\"",
		ServerLanguage.German: "\"Wink des Schicksals\"",
		ServerLanguage.Korean: "마력석: 운명의 이끌림",
		ServerLanguage.French: "\"Soyez maître de votre destin\"",
		ServerLanguage.TraditionalChinese: "\"命運\"",
		ServerLanguage.Japanese: "ガイデッド バイ フェイト",
		ServerLanguage.Polish: "\"Prowadzi mnie przeznaczenie\"",
		ServerLanguage.Russian: "\"Ведомый роком\"",
		ServerLanguage.BorkBorkBork: "\"Gooeeded by Faete-a\"",
	}
    
class StrengthAndHonor(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.StrengthAndHonor
    property_identifiers = [
        ModifierIdentifier.DamagePlusWhileUp,
    ]
    names = {
		ServerLanguage.English: "\"Strength and Honor\"",
		ServerLanguage.Spanish: "\"Fuerza y honor\"",
		ServerLanguage.Italian: "\"Forza e Onore\"",
		ServerLanguage.German: "\"Stärke und Ehre\"",
		ServerLanguage.Korean: "마력석: 힘과 명예",
		ServerLanguage.French: "\"Force et honneur\"",
		ServerLanguage.TraditionalChinese: "\"力與榮耀\"",
		ServerLanguage.Japanese: "ストレングス アンド オナー",
		ServerLanguage.Polish: "\"Siła i honor\"",
		ServerLanguage.Russian: "\"Сила и честь\"",
		ServerLanguage.BorkBorkBork: "\"Strengt und Hunur\"",
	}
    
class ToThePain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.ToThePain
    property_identifiers = [
        ModifierIdentifier.DamagePlusPercent,
        ModifierIdentifier.ArmorMinusAttacking
    ]
    names = {
		ServerLanguage.English: "\"To the Pain!\"",
		ServerLanguage.Spanish: "\"¡A que duele!\"",
		ServerLanguage.Italian: "\"Patisci!\"",
		ServerLanguage.German: "\"Fühlt den Schmerz!\"",
		ServerLanguage.Korean: "오직 공격뿐!",
		ServerLanguage.French: "\"Vive la douleur !\"",
		ServerLanguage.TraditionalChinese: "\"受死吧！\"",
		ServerLanguage.Japanese: "トゥ ザ ペイン！",
		ServerLanguage.Polish: "\"Niech żyje ból!\"",
		ServerLanguage.Russian: "\"Боль!\"",
		ServerLanguage.BorkBorkBork: "\"Tu zee Paeeen!\"",
	}
    
class TooMuchInformation(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.TooMuchInformation    
    property_identifiers = [
        ModifierIdentifier.DamagePlusVsHexed,
    ]
    names = {
		ServerLanguage.English: "\"Too Much Information\"",
		ServerLanguage.Spanish: "\"Demasiada información\"",
		ServerLanguage.Italian: "\"Troppe Informazioni\"",
		ServerLanguage.German: "\"Zuviel Information\"",
		ServerLanguage.Korean: "너무 많은 정보",
		ServerLanguage.French: "\"Trop de détails\"",
		ServerLanguage.TraditionalChinese: "\"多說無益\"",
		ServerLanguage.Japanese: "トゥー マッチ インフォメーション",
		ServerLanguage.Polish: "\"Za dużo informacji\"",
		ServerLanguage.Russian: "\"Слишком много информации\"",
		ServerLanguage.BorkBorkBork: "\"Tuu Mooch Inffurmaeshun\"",
	}
    
class VengeanceIsMine(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.Weapon
    id = ItemUpgradeId.VengeanceIsMine    
    property_identifiers = [
        ModifierIdentifier.DamagePlusWhileDown,
    ]    
    names = {
		ServerLanguage.English: "\"Vengeance is Mine\"",
		ServerLanguage.Spanish: "\"La venganza será mía\"",
		ServerLanguage.Italian: "\"La Vendetta è Mia\"",
		ServerLanguage.German: "\"Die Rache ist mein\"",
		ServerLanguage.Korean: "복수는 나의 것",
		ServerLanguage.French: "\"La vengeance sera mienne\"",
		ServerLanguage.TraditionalChinese: "\"我要報仇\"",
		ServerLanguage.Japanese: "ヴェンジャンス イズ マイン",
		ServerLanguage.Polish: "\"Zemsta należy do mnie\"",
		ServerLanguage.Russian: "\"Аз воздам\"",
		ServerLanguage.BorkBorkBork: "\"Fengeunce-a is Meene-a\"",
	}
#endregion Weapon

#region MartialWeapon
class IHaveThePower(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.MartialWeapon
    id = ItemUpgradeId.IHaveThePower
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
    ]
    names = {
		ServerLanguage.English: "\"I have the power!\"",
		ServerLanguage.Spanish: "\"¡Tengo el poder!\"",
		ServerLanguage.Italian: "\"A Me Il Potere!\"",
		ServerLanguage.German: "\"Ich habe die Kraft!\"",
		ServerLanguage.Korean: "마력석: 내겐 에너지가 있다!",
		ServerLanguage.French: "\"Je détiens le pouvoir !\"",
		ServerLanguage.TraditionalChinese: "\"充滿力量！\"",
		ServerLanguage.Japanese: "アイ ハブ ザ パワー！",
		ServerLanguage.Polish: "\"Mam moc!\"",
		ServerLanguage.Russian: "\"Сила в моих руках!\"",
		ServerLanguage.BorkBorkBork: "\"I haefe-a zee pooer!\"",
	}
    
class LetTheMemoryLiveAgain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.MartialWeapon
    id = ItemUpgradeId.LetTheMemoryLiveAgain
    property_identifiers = [
        ModifierIdentifier.HalvesSkillRechargeGeneral,
    ]
    names = {
		ServerLanguage.English: "\"Let the Memory Live Again\"",
		ServerLanguage.Spanish: "\"Que vuelvan los recuerdos\"",
		ServerLanguage.Italian: "\"Facciamo Rivivere i Ricordi\"",
		ServerLanguage.German: "\"Auf die Erinnerung!\"",
		ServerLanguage.Korean: "기억이여, 되살아나라",
		ServerLanguage.French: "\"Vers l'infini et au-delà\"",
		ServerLanguage.TraditionalChinese: "\"記憶復甦\"",
		ServerLanguage.Japanese: "レット ザ メモリー リブ アゲイン",
		ServerLanguage.Polish: "\"Niech pamięć ponownie ożyje\"",
		ServerLanguage.Russian: "\"Пусть оживут воспоминания\"",
		ServerLanguage.BorkBorkBork: "\"Let zee Memury Leefe-a Aegaeeen\"",
	}
    
#endregion MartialWeapon

#region OffhandOrShield
class CastOutTheUnclean(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.CastOutTheUnclean    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Cast Out the Unclean\"",
		ServerLanguage.Spanish: "\"Desterremos a los impuros\"",
		ServerLanguage.Italian: "\"Esorcizza l'Eresia\"",
		ServerLanguage.German: "\"Gute Besserung!\"",
		ServerLanguage.Korean: "불결한 건 가랏!",
		ServerLanguage.French: "\"Au rebut les impurs\"",
		ServerLanguage.TraditionalChinese: "\"驅除不潔\"",
		ServerLanguage.Japanese: "キャスト アウト ザ アンクリーン",
		ServerLanguage.Polish: "\"Wyrzuć nieczystych\"",
		ServerLanguage.Russian: "\"Изгнать нечистых\"",
		ServerLanguage.BorkBorkBork: "\"Caest Oooot zee Uncleun\"",
	}
    
class FearCutsDeeper(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.FearCutsDeeper    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Fear Cuts Deeper\"",
		ServerLanguage.Spanish: "\"El miedo hace más daño\"",
		ServerLanguage.Italian: "\"Il Timore Trafigge\"",
		ServerLanguage.German: "\"Die Furcht schneidet tiefer\"",
		ServerLanguage.Korean: "공포는 더 깊은 상처를 낸다",
		ServerLanguage.French: "\"La peur fait plus de mal\"",
		ServerLanguage.TraditionalChinese: "\"戒除恐懼\"",
		ServerLanguage.Japanese: "フィアー カッツ ディーパー",
		ServerLanguage.Polish: "\"Strach rani głęboko\"",
		ServerLanguage.Russian: "\"Страх острее бритвы\"",
		ServerLanguage.BorkBorkBork: "\"Feaer Coots Deeper\"",
	}
    
class ICanSeeClearlyNow(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.ICanSeeClearlyNow
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,   
    ]
    names = {
		ServerLanguage.English: "\"I Can See Clearly Now\"",
		ServerLanguage.Spanish: "\"He abierto los ojos\"",
		ServerLanguage.Italian: "\"Chiara Come Un'Alba\"",
		ServerLanguage.German: "\"Klar wie Morgentau\"",
		ServerLanguage.Korean: "마력석: 모든 게 뚜렷하게 보인다",
		ServerLanguage.French: "\"Je vois clair à présent\"",
		ServerLanguage.TraditionalChinese: "\"光明再現\"",
		ServerLanguage.Japanese: "アイ キャン シー クリアリー ナウ",
		ServerLanguage.Polish: "\"Widzę to teraz wyraźnie\"",
		ServerLanguage.Russian: "\"Теперь я ясно вижу\"",
		ServerLanguage.BorkBorkBork: "\"I Cun See-a Cleaerly Noo\"",
	}
    
class LeafOnTheWind(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.LeafOnTheWind    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
    names = {
		ServerLanguage.English: "\"Leaf on the Wind\"",
		ServerLanguage.Spanish: "\"Hoja en el viento\"",
		ServerLanguage.Italian: "\"Foglia nel Vento\"",
		ServerLanguage.German: "\"Grashalm im Wind\"",
		ServerLanguage.Korean: "바람에 떠다니는 나뭇잎",
		ServerLanguage.French: "\"La feuille portée par le vent\"",
		ServerLanguage.TraditionalChinese: "\"風中之葉\"",
		ServerLanguage.Japanese: "リーフ オン ザ ウインド",
		ServerLanguage.Polish: "\"Liść na wietrze\"",
		ServerLanguage.Russian: "\"Лист на ветру\"",
		ServerLanguage.BorkBorkBork: "\"Leaeff oon zee Veend\"",
	}
    
class LikeARollingStone(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.LikeARollingStone    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
    names = {
		ServerLanguage.English: "\"Like a Rolling Stone\"",
		ServerLanguage.Spanish: "\"Like a Rolling Stone\"",
		ServerLanguage.Italian: "\"Come Una Pietra Scalciata\"",
		ServerLanguage.German: "\"Marmor, Stein und Erde bricht\"",
		ServerLanguage.Korean: "구르는 돌처럼",
		ServerLanguage.French: "\"Solide comme le roc\"",
		ServerLanguage.TraditionalChinese: "\"漂泊者\"",
		ServerLanguage.Japanese: "ライク ア ローリング ストーン",
		ServerLanguage.Polish: "\"Jak wędrowiec\"",
		ServerLanguage.Russian: "\"Как перекати-поле\"",
		ServerLanguage.BorkBorkBork: "\"Leeke-a a Rulleeng Stune-a\"",
	}
    
class LuckOfTheDraw(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.LuckOfTheDraw
    property_identifiers = [
        ModifierIdentifier.ReceiveLessDamage,
    ]
    names = {
		ServerLanguage.English: "\"Luck of the Draw\"",
		ServerLanguage.Spanish: "\"La suerte del apostante\"",
		ServerLanguage.Italian: "\"La Fortuna è Cieca\"",
		ServerLanguage.German: "\"Glück im Spiel ...\"",
		ServerLanguage.Korean: "비김의 행운",
		ServerLanguage.French: "\"Une question de chance\"",
		ServerLanguage.TraditionalChinese: "\"全憑運氣\"",
		ServerLanguage.Japanese: "ラック オブ ザ ドロー",
		ServerLanguage.Polish: "\"Szczęśliwe rozdanie\"",
		ServerLanguage.Russian: "\"Счастливый жребий\"",
		ServerLanguage.BorkBorkBork: "\"Loock ooff zee Draev\"",
	}
    
class MasterOfMyDomain(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.MasterOfMyDomain    
    property_identifiers = [
        ModifierIdentifier.AttributePlusOneItem,
    ]
    names = {
		ServerLanguage.English: "\"Master of My Domain!\"",
		ServerLanguage.Spanish: "\"Amo de mi reino\"",
		ServerLanguage.Italian: "\"Padrone in Casa Mia\"",
		ServerLanguage.German: "\"Herr in meinem Haus\"",
		ServerLanguage.Korean: "마력석: 내 공간의 지배자",
		ServerLanguage.French: "\"Maître du Domaine\"",
		ServerLanguage.TraditionalChinese: "\"這是我的地盤！\"",
		ServerLanguage.Japanese: "マスター オブ マイ ドメイン",
		ServerLanguage.Polish: "\"Pan mego królestwa\"",
		ServerLanguage.Russian: "\"Я сам себе хозяин\"",
		ServerLanguage.BorkBorkBork: "\"Maester ooff My Dumaeeen\"",
	}
    
class NotTheFace(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.NotTheFace    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage
    ]
    names = {
		ServerLanguage.English: "\"Not the Face!\"",
		ServerLanguage.Spanish: "\"¡En la cara no!\"",
		ServerLanguage.Italian: "\"Non al Volto!\"",
		ServerLanguage.German: "\"Nicht das Gesicht!\"",
		ServerLanguage.Korean: "얼굴은 안 돼!",
		ServerLanguage.French: "\"Pas le visage !\"",
		ServerLanguage.TraditionalChinese: "\"不要打臉！\"",
		ServerLanguage.Japanese: "ノット ザ フェース！",
		ServerLanguage.Polish: "\"Nie po twarzy!\"",
		ServerLanguage.Russian: "\"Только не в лицо!\"",
		ServerLanguage.BorkBorkBork: "\"Nut zee faece-a!\"",
	}
    
class NothingToFear(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.NothingToFear
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageHexed,
    ]
    names = {
		ServerLanguage.English: "\"Nothing to Fear\"",
		ServerLanguage.Spanish: "\"Nada que temer\"",
		ServerLanguage.Italian: "\"Niente Paura\"",
		ServerLanguage.German: "\"Nichts zu befürchten\"",
		ServerLanguage.Korean: "두려울 건 없다",
		ServerLanguage.French: "\"Rien à craindre\"",
		ServerLanguage.TraditionalChinese: "\"無畏無懼\"",
		ServerLanguage.Japanese: "ナッシング トゥ フィアー",
		ServerLanguage.Polish: "\"Nieulękły\"",
		ServerLanguage.Russian: "\"Нечего бояться\"",
		ServerLanguage.BorkBorkBork: "\"Nutheeng tu Feaer\"",
	}
    
class OnlyTheStrongSurvive(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.OnlyTheStrongSurvive    
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Only the Strong Survive\"",
		ServerLanguage.Spanish: "\"Sólo sobreviven los más fuertes\"",
		ServerLanguage.Italian: "\"Superstite è soltanto il Forte\"",
		ServerLanguage.German: "\"Nur die Stärksten überleben!\"",
		ServerLanguage.Korean: "강자만이 살아남는다",
		ServerLanguage.French: "\"Seuls les plus forts survivent\"",
		ServerLanguage.TraditionalChinese: "\"強者生存\"",
		ServerLanguage.Japanese: "オンリー ザ ストロング サバイブ",
		ServerLanguage.Polish: "\"Tylko silni przetrwają\"",
		ServerLanguage.Russian: "\"Выживает сильнейший\"",
		ServerLanguage.BorkBorkBork: "\"Oonly zee Strung Soorfeefe-a\"",
	}
    
class PureOfHeart(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.PureOfHeart
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Pure of Heart\"",
		ServerLanguage.Spanish: "\"Puro de corazón\"",
		ServerLanguage.Italian: "\"Purezza di Cuore\"",
		ServerLanguage.German: "\"Mein Herz ist rein\"",
		ServerLanguage.Korean: "심장의 깨끗함",
		ServerLanguage.French: "\"Pureté du coeur\"",
		ServerLanguage.TraditionalChinese: "\"純淨之心\"",
		ServerLanguage.Japanese: "ピュア オブ ハート",
		ServerLanguage.Polish: "\"Czystość serca\"",
		ServerLanguage.Russian: "\"Чистые сердцем\"",
		ServerLanguage.BorkBorkBork: "\"Poore-a ooff Heaert\"",
	}
    
class RidersOnTheStorm(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.RidersOnTheStorm
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
    names = {
		ServerLanguage.English: "\"Riders on the Storm\"",
		ServerLanguage.Spanish: "\"Jinetes de la tormenta\"",
		ServerLanguage.Italian: "\"Viaggiatori nella Burrasca\"",
		ServerLanguage.German: "\"Geblitzt wird nicht!\"",
		ServerLanguage.Korean: "폭풍의 기수",
		ServerLanguage.French: "\"Les chevaliers du ciel\"",
		ServerLanguage.TraditionalChinese: "\"暴風騎士\"",
		ServerLanguage.Japanese: "ライダー オン ザ ストーム",
		ServerLanguage.Polish: "\"Jeźdźcy burzy\"",
		ServerLanguage.Russian: "\"Всадники бури\"",
		ServerLanguage.BorkBorkBork: "\"Reeders oon zee Sturm\"",
	}
    
class RunForYourLife(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.RunForYourLife
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageStance,
    ]
    names = {
		ServerLanguage.English: "\"Run For Your Life!\"",
		ServerLanguage.Spanish: "\"¡Ponte a salvo!\"",
		ServerLanguage.Italian: "\"Gambe in Spalla!\"",
		ServerLanguage.German: "\"Rennt um Euer Leben!\"",
		ServerLanguage.Korean: "살기 위해 달려라!",
		ServerLanguage.French: "\"Sauve-qui-peut !\"",
		ServerLanguage.TraditionalChinese: "\"逃命\"",
		ServerLanguage.Japanese: "ラン フォー ユア ライフ！",
		ServerLanguage.Polish: "\"Ratuj się kto może!\"",
		ServerLanguage.Russian: "\"Спасайся, кто может!\"",
		ServerLanguage.BorkBorkBork: "\"Roon Fur Yuoor Leeffe-a!\"",
	}
    
class ShelteredByFaith(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.ShelteredByFaith    
    property_identifiers = [
        ModifierIdentifier.ReceiveLessPhysDamageEnchanted,
    ]
    names = {
		ServerLanguage.English: "\"Sheltered by Faith\"",
		ServerLanguage.Spanish: "\"Fe ciega\"",
		ServerLanguage.Italian: "\"Rifugio della Speranza\"",
		ServerLanguage.German: "\"Vertrauen ist gut\"",
		ServerLanguage.Korean: "신념의 보호",
		ServerLanguage.French: "\"Protégé par la Foi\"",
		ServerLanguage.TraditionalChinese: "\"信念守護\"",
		ServerLanguage.Japanese: "シェルター バイ フェイス",
		ServerLanguage.Polish: "\"Chroniony przez wiarę\"",
		ServerLanguage.Russian: "\"Под защитой веры\"",
		ServerLanguage.BorkBorkBork: "\"Sheltered by Faeeet\"",
	}
    
class SleepNowInTheFire(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.SleepNowInTheFire        
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
    names = {
		ServerLanguage.English: "\"Sleep Now in the Fire\"",
		ServerLanguage.Spanish: "\"Descansa en la hoguera\"",
		ServerLanguage.Italian: "\"Dormi Ardentemente\"",
		ServerLanguage.German: "\"Geborgenheit im Feuer\"",
		ServerLanguage.Korean: "화염 속에 잠들라",
		ServerLanguage.French: "\"Faisons la lumière sur les ténèbres\"",
		ServerLanguage.TraditionalChinese: "\"烈焰中歇息\"",
		ServerLanguage.Japanese: "スリープ ナウ イン ザ ファイア",
		ServerLanguage.Polish: "\"Zaśnij w ogniu\"",
		ServerLanguage.Russian: "\"Покойся в пламени\"",
		ServerLanguage.BorkBorkBork: "\"Sleep Noo in zee Fure-a\"",
	}
    
class SoundnessOfMind(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.SoundnessOfMind
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Soundness of Mind\"",
		ServerLanguage.Spanish: "\"Sano juicio\"",
		ServerLanguage.Italian: "\"Mente Sana\"",
		ServerLanguage.German: "\"Ein gesunder Geist ...\"",
		ServerLanguage.Korean: "마음의 소리",
		ServerLanguage.French: "\"Bon sens\"",
		ServerLanguage.TraditionalChinese: "\"堅定意念\"",
		ServerLanguage.Japanese: "サウンドネス オブ マインド",
		ServerLanguage.Polish: "\"Mądrość umysłu\"",
		ServerLanguage.Russian: "\"Здравый рассудок\"",
		ServerLanguage.BorkBorkBork: "\"Suoondness ooff Meend\"",
	}
    
class StrengthOfBody(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.StrengthOfBody
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Strength of Body\"",
		ServerLanguage.Spanish: "\"Fuerza bruta\"",
		ServerLanguage.Italian: "\"Corpo Gagliardo\"",
		ServerLanguage.German: "\"Hart im Nehmen\"",
		ServerLanguage.Korean: "육체의 힘",
		ServerLanguage.French: "\"La Force réside du corps\"",
		ServerLanguage.TraditionalChinese: "\"力貫全身\"",
		ServerLanguage.Japanese: "ストレングス オブ ボディ",
		ServerLanguage.Polish: "\"Siła ciała\"",
		ServerLanguage.Russian: "\"Сила тела\"",
		ServerLanguage.BorkBorkBork: "\"Strengt ooff Budy\"",
	}
    
class SwiftAsTheWind(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.SwiftAsTheWind
    property_identifiers = [
        ModifierIdentifier.ReduceConditionDuration,
    ]
    names = {
		ServerLanguage.English: "\"Swift as the Wind\"",
		ServerLanguage.Spanish: "\"Veloz como el viento\"",
		ServerLanguage.Italian: "\"Raffica di Bora\"",
		ServerLanguage.German: "\"Schnell wie der Wind\"",
		ServerLanguage.Korean: "바람처럼 빠르게",
		ServerLanguage.French: "\"Rapide comme le vent\"",
		ServerLanguage.TraditionalChinese: "\"迅捷如風\"",
		ServerLanguage.Japanese: "スウィフト アズ ザ ウインド",
		ServerLanguage.Polish: "\"Szybki niczym wiatr\"",
		ServerLanguage.Russian: "\"Быстрый как ветер\"",
		ServerLanguage.BorkBorkBork: "\"Sveefft aes zee Veend\"",
	}

class TheRiddleOfSteel(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.TheRiddleOfSteel    
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
    names = {
		ServerLanguage.English: "\"The Riddle of Steel\"",
		ServerLanguage.Spanish: "\"El enigma de acero\"",
		ServerLanguage.Italian: "\"Enigma d'Acciaio\"",
		ServerLanguage.German: "\"Hieb-und stahlfest\"",
		ServerLanguage.Korean: "강철의 수수께끼",
		ServerLanguage.French: "\"L'énigme de l'acier\"",
		ServerLanguage.TraditionalChinese: "\"鋼鐵之謎\"",
		ServerLanguage.Japanese: "ザ リドル オブ スチール",
		ServerLanguage.Polish: "\"Zagadka stali\"",
		ServerLanguage.Russian: "\"Стальной щит\"",
		ServerLanguage.BorkBorkBork: "\"Zee Reeddle-a ooff Steel\"",
	}
    
class ThroughThickAndThin(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.OffhandOrShield
    id = ItemUpgradeId.ThroughThickAndThin
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsDamage,
    ]
    names = {
		ServerLanguage.English: "\"Through Thick and Thin\"",
		ServerLanguage.Spanish: "\"En lo bueno y en lo malo\"",
		ServerLanguage.Italian: "\"Nella Buona e nella Cattiva Sorte\"",
		ServerLanguage.German: "\"Durch Dick und Dünn\"",
		ServerLanguage.Korean: "무엇이든 막아내리",
		ServerLanguage.French: "\"Contre vents et marées\"",
		ServerLanguage.TraditionalChinese: "\"同甘共苦\"",
		ServerLanguage.Japanese: "スルー シック アンド シン",
		ServerLanguage.Polish: "\"Poprzez gąszcz\"",
		ServerLanguage.Russian: "\"Сквозь огонь и воду\"",
		ServerLanguage.BorkBorkBork: "\"Thruoogh Theeck und Theen\"",
	}
#endregion OffhandOrShield

#region EquippableItem
class MeasureForMeasure(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.EquippableItem
    id = ItemUpgradeId.MeasureForMeasure
    property_identifiers = [
        ModifierIdentifier.HighlySalvageable,
    ]
    names = {
		ServerLanguage.English: "\"Measure for Measure\"",
		ServerLanguage.Spanish: "\"Ojo por ojo\"",
		ServerLanguage.Italian: "\"Occhio per Occhio\"",
		ServerLanguage.German: "\"Maß für Maß\"",
		ServerLanguage.Korean: "다다익선",
		ServerLanguage.French: "\"Mesure pour mesure.\"",
		ServerLanguage.TraditionalChinese: "\"以牙還牙\"",
		ServerLanguage.Japanese: "メジャー フォー メジャー",
		ServerLanguage.Polish: "\"Miarka za miarkę\"",
		ServerLanguage.Russian: "\"Око за око\"",
		ServerLanguage.BorkBorkBork: "\"Meaesoore-a fur Meaesoore-a\"",
	}
        
class ShowMeTheMoney(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.EquippableItem
    id = ItemUpgradeId.ShowMeTheMoney
    property_identifiers = [
        ModifierIdentifier.IncreasedSaleValue,
    ]    
    names = {
		ServerLanguage.English: "\"Show me the money!\"",
		ServerLanguage.Spanish: "\"¡Enséñame la pasta!\"",
		ServerLanguage.Italian: "\"Mostrami la Grana!\"",
		ServerLanguage.German: "\"Geld macht glücklich!\"",
		ServerLanguage.Korean: "돈이다!",
		ServerLanguage.French: "\"Par ici la monnaie !\"",
		ServerLanguage.TraditionalChinese: "\"給我錢！\"",
		ServerLanguage.Japanese: "ショー ミー ザ マネー！",
		ServerLanguage.Polish: "\"Pokaż pieniądze!\"",
		ServerLanguage.Russian: "\"Покажи мне деньги!\"",
		ServerLanguage.BorkBorkBork: "\"Shoo me-a zee muney!\"",
	}
#endregion EquippableItem

#region SpellcastingWeapon
class AptitudeNotAttitude(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.AptitudeNotAttitude
    property_identifiers = [
        ModifierIdentifier.HalvesCastingTimeItemAttribute,
    ]
    names = {
		ServerLanguage.English: "\"Aptitude not Attitude\"",
		ServerLanguage.Spanish: "\"Aptitud, no actitud\"",
		ServerLanguage.Italian: "\"Inclinazione non Finzione\"",
		ServerLanguage.German: "\"Gut gewirkt ist halb gewonnen\"",
		ServerLanguage.Korean: "마력석: 특성이 아니라 재능이다",
		ServerLanguage.French: "\"Les compétences prévalent\"",
		ServerLanguage.TraditionalChinese: "\"能力而非態度\"",
		ServerLanguage.Japanese: "アプティテュード ノット アティテュード",
		ServerLanguage.Polish: "\"Talent a nie nastawienie\"",
		ServerLanguage.Russian: "\"Главное -способности, а не отношение к делу\"",
		ServerLanguage.BorkBorkBork: "\"Aepteetoode-a nut Aetteetoode-a\"",
	}
    
class DontCallItAComeback(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.DontCallItAComeback    
    property_identifiers = [
        ModifierIdentifier.EnergyPlusWhileBelow,
    ]
    names = {
		ServerLanguage.English: "\"Don't call it a comeback!\"",
		ServerLanguage.Spanish: "\"¡No será la última palabra!\"",
		ServerLanguage.Italian: "\"Non Consideratelo un Ritorno!\"",
		ServerLanguage.German: "\"Sie kehren niemals wieder\"",
		ServerLanguage.Korean: "단순한 회복이 아니다!",
		ServerLanguage.French: "\"Aucun recours !\"",
		ServerLanguage.TraditionalChinese: "\"別說我不行！\"",
		ServerLanguage.Japanese: "ドント コール イット ア カムバック！",
		ServerLanguage.Polish: "\"Nie nazywaj tego powrotem!\"",
		ServerLanguage.Russian: "\"Не считай это местью!\"",
		ServerLanguage.BorkBorkBork: "\"Dun't caell it a cumebaeck!\"",
	}
    
class HaleAndHearty(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.HaleAndHearty
    property_identifiers = [
        ModifierIdentifier.EnergyPlusWhileDown,
    ]
    names = {
		ServerLanguage.English: "\"Hale and Hearty\"",
		ServerLanguage.Spanish: "\"Viejo pero joven\"",
		ServerLanguage.Italian: "\"Vivo e Vegeto\"",
		ServerLanguage.German: "\"Gesund und munter\"",
		ServerLanguage.Korean: "마력석: 원기왕성하게!",
		ServerLanguage.French: "\"En pleine santé\"",
		ServerLanguage.TraditionalChinese: "\"健壯的\"",
		ServerLanguage.Japanese: "ヘイル アンド ハーティー",
		ServerLanguage.Polish: "\"Zdrowy i krzepki\"",
		ServerLanguage.Russian: "\"Сильный и здоровый\"",
		ServerLanguage.BorkBorkBork: "\"Haele-a und Heaerty\"",
	}
    
class HaveFaith(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.HaveFaith
    property_identifiers = [
        ModifierIdentifier.EnergyPlusEnchanted,
    ]
    names = {
		ServerLanguage.English: "\"Have Faith\"",
		ServerLanguage.Spanish: "\"Tened fe\"",
		ServerLanguage.Italian: "\"Abbi Fede\"",
		ServerLanguage.German: "\"Habt Vertrauen\"",
		ServerLanguage.Korean: "신념을 가져라",
		ServerLanguage.French: "\"Ayez la foi\"",
		ServerLanguage.TraditionalChinese: "\"信念\"",
		ServerLanguage.Japanese: "ハブ フェイス",
		ServerLanguage.Polish: "\"Miej wiarę\"",
		ServerLanguage.Russian: "\"Не теряй веру\"",
		ServerLanguage.BorkBorkBork: "\"Haefe-a Faeeet\"",
	}
    
class IAmSorrow(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.IAmSorrow        
    property_identifiers = [
        ModifierIdentifier.EnergyPlusHexed,
    ]
    names = {
		ServerLanguage.English: "\"I am Sorrow.\"",
		ServerLanguage.Spanish: "\"Un mar de lágrimas\"",
		ServerLanguage.Italian: "\"Io Sono la Sofferenza\"",
		ServerLanguage.German: "\"Ich bin es Leid\"",
		ServerLanguage.Korean: "너무 슬프군",
		ServerLanguage.French: "\"Je suis la douleur\"",
		ServerLanguage.TraditionalChinese: "\"倍感憂傷\"",
		ServerLanguage.Japanese: "アイ アム ソロウ",
		ServerLanguage.Polish: "\"Jestem smutkiem.\"",
		ServerLanguage.Russian: "\"Я -воплощение скорби\"",
		ServerLanguage.BorkBorkBork: "\"I aem Surroo.\"",
	}
    
class SeizeTheDay(Inscription):
    mod_type = ItemUpgradeType.Inscription
    target_item_type = ItemType.SpellcastingWeapon
    id = ItemUpgradeId.SeizeTheDay    
    property_identifiers = [
        ModifierIdentifier.EnergyPlus,
        ModifierIdentifier.EnergyDegen,
    ]
    names = {
		ServerLanguage.English: "\"Seize the Day\"",
		ServerLanguage.Spanish: "\"Vive el presente\"",
		ServerLanguage.Italian: "\"Vivi alla Giornata\"",
		ServerLanguage.German: "\"Lebt den Tag\"",
		ServerLanguage.Korean: "오늘을 위해 최선을",
		ServerLanguage.French: "\"Aujourd'hui, la vie\"",
		ServerLanguage.TraditionalChinese: "\"活在當下\"",
		ServerLanguage.Japanese: "リブ フォー トゥデイ",
		ServerLanguage.Polish: "\"Żyj dniem dzisiejszym\"",
		ServerLanguage.Russian: "\"Живи сегодняшним днем\"",
		ServerLanguage.BorkBorkBork: "\"Leefe-a fur Tudaey\"",
	}
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

