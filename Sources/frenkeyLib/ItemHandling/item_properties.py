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

class LocalizedString:    
    def __init__(self, localization: Optional[dict[ServerLanguage, str]] = None):
        self._localization = localization or {}
    
    @property
    def default(self) -> str:
        return self.get()
    
    @property
    def english(self) -> str:
        return self.get(ServerLanguage.English)
    
    @property
    def korean(self) -> str:
        return self.get(ServerLanguage.Korean)
    
    @property
    def french(self) -> str:
        return self.get(ServerLanguage.French)
    
    @property
    def german(self) -> str:
        return self.get(ServerLanguage.German)
    
    @property
    def italian(self) -> str:
        return self.get(ServerLanguage.Italian)
    
    @property
    def spanish(self) -> str:
        return self.get(ServerLanguage.Spanish)
    
    @property
    def chinese(self) -> str:
        return self.get(ServerLanguage.TraditionalChinese)
    
    @property
    def japanese(self) -> str:
        return self.get(ServerLanguage.Japanese)
    
    @property
    def polish(self) -> str:
        return self.get(ServerLanguage.Polish)
    
    @property
    def russian(self) -> str:
        return self.get(ServerLanguage.Russian)
    
    @property
    def bork(self) -> str:
        return self.get(ServerLanguage.BorkBorkBork)
        
    def get(self, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        return self._localization.get(language, self._localization.get(ServerLanguage.English, ""))
    
    def __str__(self) -> str:
        return self.get()

    def __repr__(self) -> str:
        return repr(self.get())

    def __format__(self, format_spec: str) -> str:
        return format(self.get(), format_spec)

    def __len__(self) -> int:
        return len(self.get())

    def __add__(self, other):
        return self.get() + str(other)

    def __radd__(self, other):
        return str(other) + self.get()

    def __eq__(self, other):
        return self.get() == str(other)

    def __contains__(self, item):
        return item in self.get()

    # ---------------------------------------------------------
    # Forward ALL other string methods automatically
    # ---------------------------------------------------------

    def __getattr__(self, item):
        return getattr(self.get(), item)
    
LOCALIZED_PROFESSION_NAMES : dict = {
}

LOCALIZED_ATTRIBUTE_NAMES : dict = {
}

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
        ServerLanguage.TraditionalChinese: "the 矛柄 {0}",
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

from typing import Optional
import Py4GW
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, AttributeNames, Profession
from Py4GWCoreLib.enums_src.Item_enums import Rarity
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier
from Sources.frenkeyLib.ItemHandling.item_properties import _PROPERTY_FACTORY, ItemProperty, Upgrade
from Sources.frenkeyLib.ItemHandling.types import ItemUpgradeType, ModifierIdentifier
from Sources.frenkeyLib.ItemHandling.upgrades import ItemUpgradeId

#region Armor Upgrades
class Insignia(Upgrade):
    mod_type = ItemUpgradeType.Prefix

    id : ItemUpgradeId
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    names : dict[ServerLanguage, str] = {}

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
        format_str = cls.names.get(language, "[ABC] {item_name}")
        return format_str.format(item_name=Insignia.INSIGNIA_LOCALIZATION.get(language, "Insignia"))

    @classmethod
    def add_to_item_name(cls, item_name: str, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.names.get(language, "[ABC] {item_name}")
        return format_str.format(name=cls.get_name(language), item_name=item_name)

class Rune(Upgrade):
    mod_type = ItemUpgradeType.Suffix

    id : ItemUpgradeId
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    names : dict[ServerLanguage, str] = {}

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
    def get_rune_name(cls, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        if cls.profession is not Profession._None:
            profession_str = LOCALIZED_PROFESSION_NAMES.get(cls.profession, {}).get(language)
            rune_str = cls.RUNE_LOCALIZATION.get(language, "Rune")
            return f"{profession_str} {rune_str}".strip()
        else:                
            rune_str = cls.RUNE_LOCALIZATION.get(language, "Rune")
            return f"{rune_str}".strip()

    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return cls.id is not None and upgrade_id == cls.id

    @property
    def name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.names.get(language, "[ABC] {item_name}")
        return format_str.format(item_name=Insignia.INSIGNIA_LOCALIZATION.get(language, "Insignia"))

    @classmethod
    def add_to_item_name(cls, item_name: str, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.names.get(language, "[ABC] {item_name}")
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
    id = ItemUpgradeId.Survivor
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Survivor {item_name}",
        ServerLanguage.Korean: "생존자의 {item_name}",
        ServerLanguage.French: "{item_name} du survivant",
        ServerLanguage.German: "Überlebende {item_name}",
        ServerLanguage.Italian: "{item_name} del Superstite",
        ServerLanguage.Spanish: "{item_name} de superviviente",
        ServerLanguage.TraditionalChinese: "生存 {item_name}",
        ServerLanguage.Japanese: "サバイバー {item_name}",
        ServerLanguage.Polish: "{item_name} Przetrwania",
        ServerLanguage.Russian: "Survivor {item_name}",
        ServerLanguage.BorkBorkBork: "Soorfeefur {item_name}",
    }

class RadiantInsignia(Insignia):
    id = ItemUpgradeId.Radiant
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Radiant {item_name}",
        ServerLanguage.Korean: "눈부신 {item_name}",
        ServerLanguage.French: "{item_name} du rayonnement",
        ServerLanguage.German: "Radianten- {item_name}",
        ServerLanguage.Italian: "{item_name} Radianti",
        ServerLanguage.Spanish: "{item_name} radiante",
        ServerLanguage.TraditionalChinese: "閃耀 {item_name}",
        ServerLanguage.Japanese: "ラディアント {item_name}",
        ServerLanguage.Polish: "{item_name} Promieni",
        ServerLanguage.Russian: "Radiant {item_name}",
        ServerLanguage.BorkBorkBork: "Raedeeunt {item_name}",
    }

class StalwartInsignia(Insignia):
    id = ItemUpgradeId.Stalwart
    mod_type = ItemUpgradeType.Prefix

    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]

    names = {
        ServerLanguage.English: "Stalwart {item_name}",
        ServerLanguage.Korean: "튼튼한 {item_name}",
        ServerLanguage.French: "{item_name} robuste",
        ServerLanguage.German: "Entschlossenheits- {item_name}",
        ServerLanguage.Italian: "{item_name} della Robustezza",
        ServerLanguage.Spanish: "{item_name} firme",
        ServerLanguage.TraditionalChinese: "健壯 {item_name}",
        ServerLanguage.Japanese: "スタルウォート {item_name}",
        ServerLanguage.Polish: "{item_name} Stanowczości",
        ServerLanguage.Russian: "Stalwart {item_name}",
        ServerLanguage.BorkBorkBork: "Staelvaert {item_name}",
    }

class BrawlersInsignia(Insignia):
    id = ItemUpgradeId.Brawlers
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Brawler's {item_name}",
        ServerLanguage.Korean: "싸움꾼의 {item_name}",
        ServerLanguage.French: "{item_name} de l'agitateur",
        ServerLanguage.German: "Raufbold- {item_name}",
        ServerLanguage.Italian: "{item_name} da Lottatore",
        ServerLanguage.Spanish: "{item_name} del pendenciero",
        ServerLanguage.TraditionalChinese: "鬥士 {item_name}",
        ServerLanguage.Japanese: "ブラウラー {item_name}",
        ServerLanguage.Polish: "{item_name} Zapaśnika",
        ServerLanguage.Russian: "Brawler's {item_name}",
        ServerLanguage.BorkBorkBork: "Braevler's {item_name}",
    }

class BlessedInsignia(Insignia):
    id = ItemUpgradeId.Blessed
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Blessed {item_name}",
        ServerLanguage.Korean: "축복의 {item_name}",
        ServerLanguage.French: "{item_name} de la bénédiction",
        ServerLanguage.German: "Segens {item_name}",
        ServerLanguage.Italian: "{item_name} della Benedizione",
        ServerLanguage.Spanish: "{item_name} con bendición",
        ServerLanguage.TraditionalChinese: "祝福 {item_name}",
        ServerLanguage.Japanese: "ブレス {item_name}",
        ServerLanguage.Polish: "{item_name} Błogosławieństwa",
        ServerLanguage.Russian: "Blessed {item_name}",
        ServerLanguage.BorkBorkBork: "Blessed {item_name}",
    }

class HeraldsInsignia(Insignia):
    id = ItemUpgradeId.Heralds
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Herald's {item_name}",
        ServerLanguage.Korean: "전령의 {item_name}",
        ServerLanguage.French: "{item_name} de héraut",
        ServerLanguage.German: "Herold- {item_name}",
        ServerLanguage.Italian: "{item_name} da Araldo",
        ServerLanguage.Spanish: "{item_name} de heraldo",
        ServerLanguage.TraditionalChinese: "先驅 {item_name}",
        ServerLanguage.Japanese: "ヘラルド {item_name}",
        ServerLanguage.Polish: "{item_name} Herolda",
        ServerLanguage.Russian: "Herald's {item_name}",
        ServerLanguage.BorkBorkBork: "Heraeld's {item_name}",
    }

class SentrysInsignia(Insignia):
    id = ItemUpgradeId.Sentrys
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Sentry's {item_name}",
        ServerLanguage.Korean: "보초병의 {item_name}",
        ServerLanguage.French: "{item_name} de factionnaire",
        ServerLanguage.German: "Wachposten- {item_name}",
        ServerLanguage.Italian: "{item_name} da Sentinella",
        ServerLanguage.Spanish: "{item_name} de centinela",
        ServerLanguage.TraditionalChinese: "哨兵 {item_name}",
        ServerLanguage.Japanese: "セントリー {item_name}",
        ServerLanguage.Polish: "{item_name} Wartownika",
        ServerLanguage.Russian: "Sentry's {item_name}",
        ServerLanguage.BorkBorkBork: "Sentry's {item_name}",
    }

class RuneOfMinorVigor(Rune):
    id = ItemUpgradeId.OfMinorVigor
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Vigor",
        ServerLanguage.Korean: "{item_name}(하급 활력)",
        ServerLanguage.French: "{item_name} (Vigueur : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Lebenskraft",
        ServerLanguage.Italian: "{item_name} Vigore di grado minore",
        ServerLanguage.Spanish: "{item_name} (vigor de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 活力 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ビガー)",
        ServerLanguage.Polish: "{item_name} (Wigoru niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Vigor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Feegur",
    }

class RuneOfMinorVigor2(Rune):
    id = ItemUpgradeId.OfMinorVigor2
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Vigor",
        ServerLanguage.Korean: "{item_name}(하급 활력)",
        ServerLanguage.French: "{item_name} (Vigueur : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Lebenskraft",
        ServerLanguage.Italian: "{item_name} Vigore di grado minore",
        ServerLanguage.Spanish: "{item_name} (vigor de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 活力 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ビガー)",
        ServerLanguage.Polish: "{item_name} (Wigoru niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Vigor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Feegur",
    }

class RuneOfVitae(Rune):
    id = ItemUpgradeId.OfVitae
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Vitae",
        ServerLanguage.Korean: "{item_name}(이력)",
        ServerLanguage.French: "{item_name} (de la vie)",
        ServerLanguage.German: "{item_name} d. Lebenskraft",
        ServerLanguage.Italian: "{item_name} della Vita",
        ServerLanguage.Spanish: "{item_name} (de vida)",
        ServerLanguage.TraditionalChinese: "生命 {item_name}",
        ServerLanguage.Japanese: "{item_name} (ヴィータ)",
        ServerLanguage.Polish: "{item_name} (Życia)",
        ServerLanguage.Russian: "{item_name} of Vitae",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Feetaee-a",
    }

class RuneOfAttunement(Rune):
    id = ItemUpgradeId.OfAttunement
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Attunement",
        ServerLanguage.Korean: "{item_name}(조율)",
        ServerLanguage.French: "{item_name} (d'affinité)",
        ServerLanguage.German: "{item_name} d. Einstimmung",
        ServerLanguage.Italian: "{item_name} dell'Armonia",
        ServerLanguage.Spanish: "{item_name} (de sintonía)",
        ServerLanguage.TraditionalChinese: "調和 {item_name}",
        ServerLanguage.Japanese: "{item_name} (アチューン)",
        ServerLanguage.Polish: "{item_name} (Dostrojenia)",
        ServerLanguage.Russian: "{item_name} of Attunement",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Aettoonement",
    }

class RuneOfMajorVigor(Rune):
    id = ItemUpgradeId.OfMajorVigor
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    names = {
        ServerLanguage.English: "{item_name} of Major Vigor",
        ServerLanguage.Korean: "{item_name}(상급 활력)",
        ServerLanguage.French: "{item_name} (Vigueur : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Lebenskraft",
        ServerLanguage.Italian: "{item_name} Vigore di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (vigor de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 活力 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ビガー)",
        ServerLanguage.Polish: "{item_name} (Wigoru wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Vigor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Feegur",
    }

class RuneOfRecovery(Rune):
    id = ItemUpgradeId.OfRecovery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

    names = {
        ServerLanguage.English: "{item_name} of Recovery",
        ServerLanguage.Korean: "{item_name}(회복)",
        ServerLanguage.French: "{item_name} (de récupération)",
        ServerLanguage.German: "{item_name} d. Gesundung",
        ServerLanguage.Italian: "{item_name} della Ripresa",
        ServerLanguage.Spanish: "{item_name} (de mejoría)",
        ServerLanguage.TraditionalChinese: "恢復 {item_name}",
        ServerLanguage.Japanese: "{item_name} (リカバリー)",
        ServerLanguage.Polish: "{item_name} (Uzdrowienia)",
        ServerLanguage.Russian: "{item_name} of Recovery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Recufery",
    }

class RuneOfRestoration(Rune):
    id = ItemUpgradeId.OfRestoration
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

    names = {
        ServerLanguage.English: "{item_name} of Restoration",
        ServerLanguage.Korean: "{item_name}(복구)",
        ServerLanguage.French: "{item_name} (de rétablissement)",
        ServerLanguage.German: "{item_name} d. Wiederherstellung",
        ServerLanguage.Italian: "{item_name} del Ripristino",
        ServerLanguage.Spanish: "{item_name} (de restauración)",
        ServerLanguage.TraditionalChinese: "復原 {item_name}",
        ServerLanguage.Japanese: "{item_name} (レストレーション)",
        ServerLanguage.Polish: "{item_name} (Renowacji)",
        ServerLanguage.Russian: "{item_name} of Restoration",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Resturaeshun",
    }

class RuneOfClarity(Rune):
    id = ItemUpgradeId.OfClarity
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

    names = {
        ServerLanguage.English: "{item_name} of Clarity",
        ServerLanguage.Korean: "{item_name}(명석)",
        ServerLanguage.French: "{item_name} (de la clarté)",
        ServerLanguage.German: "{item_name} d. Klarheit",
        ServerLanguage.Italian: "{item_name} della Trasparenza",
        ServerLanguage.Spanish: "{item_name} (de claridad)",
        ServerLanguage.TraditionalChinese: "澄澈 {item_name}",
        ServerLanguage.Japanese: "{item_name} (クラリティ)",
        ServerLanguage.Polish: "{item_name} (Jasności)",
        ServerLanguage.Russian: "{item_name} of Clarity",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Claereety",
    }

class RuneOfPurity(Rune):
    id = ItemUpgradeId.OfPurity
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

    names = {
        ServerLanguage.English: "{item_name} of Purity",
        ServerLanguage.Korean: "{item_name}(순수)",
        ServerLanguage.French: "{item_name} (de la pureté)",
        ServerLanguage.German: "{item_name} d. Reinheit",
        ServerLanguage.Italian: "{item_name} della Purezza",
        ServerLanguage.Spanish: "{item_name} (de pureza)",
        ServerLanguage.TraditionalChinese: "潔淨 {item_name}",
        ServerLanguage.Japanese: "{item_name} (ピュリティ)",
        ServerLanguage.Polish: "{item_name} (Czystości)",
        ServerLanguage.Russian: "{item_name} of Purity",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Pooreety",
    }

class RuneOfSuperiorVigor(Rune):
    id = ItemUpgradeId.OfSuperiorVigor
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    names = {
        ServerLanguage.English: "{item_name} of Superior Vigor",
        ServerLanguage.Korean: "{item_name}(고급 활력)",
        ServerLanguage.French: "{item_name} (Vigueur : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Lebenskraft",
        ServerLanguage.Italian: "{item_name} Vigore di grado supremo",
        ServerLanguage.Spanish: "{item_name} (vigor de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 活力 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ビガー)",
        ServerLanguage.Polish: "{item_name} (Wigoru najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Vigor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Feegur",
    }

#endregion No Profession

#region Warrior

class KnightsInsignia(Insignia):
    id = ItemUpgradeId.Knights
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Knight's {item_name}",
        ServerLanguage.Korean: "기사의 {item_name}",
        ServerLanguage.French: "{item_name} de chevalier",
        ServerLanguage.German: "Ritter- {item_name}",
        ServerLanguage.Italian: "{item_name} da Cavaliere",
        ServerLanguage.Spanish: "{item_name} de caballero",
        ServerLanguage.TraditionalChinese: "騎士 {item_name}",
        ServerLanguage.Japanese: "ナイト {item_name}",
        ServerLanguage.Polish: "{item_name} Rycerza",
        ServerLanguage.Russian: "Knight's {item_name}",
        ServerLanguage.BorkBorkBork: "Kneeght's {item_name}",
    }

class LieutenantsInsignia(Insignia):
    id = ItemUpgradeId.Lieutenants
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Lieutenant's {item_name}",
        ServerLanguage.Korean: "부관의 {item_name}",
        ServerLanguage.French: "{item_name} du Lieutenant",
        ServerLanguage.German: "Leutnant- {item_name}",
        ServerLanguage.Italian: "{item_name} da Luogotenente",
        ServerLanguage.Spanish: "{item_name} de teniente",
        ServerLanguage.TraditionalChinese: "副官 {item_name}",
        ServerLanguage.Japanese: "ルテナント {item_name}",
        ServerLanguage.Polish: "{item_name} Porucznika",
        ServerLanguage.Russian: "Lieutenant's {item_name}",
        ServerLanguage.BorkBorkBork: "Leeeootenunt's {item_name}",
    }

class StonefistInsignia(Insignia):
    id = ItemUpgradeId.Stonefist
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Stonefist {item_name}",
        ServerLanguage.Korean: "돌주먹의 {item_name}",
        ServerLanguage.French: "{item_name} Poing-de-fer",
        ServerLanguage.German: "Steinfaust- {item_name}",
        ServerLanguage.Italian: "{item_name} di Pietra",
        ServerLanguage.Spanish: "{item_name} de piedra",
        ServerLanguage.TraditionalChinese: "石拳 {item_name}",
        ServerLanguage.Japanese: "ストーンフィスト {item_name}",
        ServerLanguage.Polish: "{item_name} Kamiennej Pięści",
        ServerLanguage.Russian: "Stonefist {item_name}",
        ServerLanguage.BorkBorkBork: "Stuneffeest {item_name}",
    }

class DreadnoughtInsignia(Insignia):
    id = ItemUpgradeId.Dreadnought
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Dreadnought {item_name}",
        ServerLanguage.Korean: "용자의 {item_name}",
        ServerLanguage.French: "{item_name} de Dreadnaught",
        ServerLanguage.German: "Panzerschiff- {item_name}",
        ServerLanguage.Italian: "{item_name} da Dreadnought",
        ServerLanguage.Spanish: "{item_name} de Dreadnought",
        ServerLanguage.TraditionalChinese: "無懼 {item_name}",
        ServerLanguage.Japanese: "ドレッドノート {item_name}",
        ServerLanguage.Polish: "{item_name} Pancernika",
        ServerLanguage.Russian: "Dreadnought {item_name}",
        ServerLanguage.BorkBorkBork: "Dreaednuooght {item_name}",
    }

class SentinelsInsignia(Insignia):
    id = ItemUpgradeId.Sentinels
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Sentinel's {item_name}",
        ServerLanguage.Korean: "감시병의 {item_name}",
        ServerLanguage.French: "{item_name} de sentinelle",
        ServerLanguage.German: "Wächter- {item_name}",
        ServerLanguage.Italian: "{item_name} da Sentinella",
        ServerLanguage.Spanish: "{item_name} de centinela",
        ServerLanguage.TraditionalChinese: "警戒 {item_name}",
        ServerLanguage.Japanese: "センチネル {item_name}",
        ServerLanguage.Polish: "{item_name} Strażnika",
        ServerLanguage.Russian: "Sentinel's {item_name}",
        ServerLanguage.BorkBorkBork: "Senteenel's {item_name}",
    }

class WarriorRuneOfMinorAbsorption(Rune):
    id = ItemUpgradeId.OfMinorAbsorption
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Absorption",
        ServerLanguage.Korean: "{item_name}(하급 흡수)",
        ServerLanguage.French: "{item_name} (Absorption : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Absorption",
        ServerLanguage.Italian: "{item_name} Assorbimento di grado minore",
        ServerLanguage.Spanish: "{item_name} (absorción de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 吸收 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー アブソープション)",
        ServerLanguage.Polish: "{item_name} Wojownika (Pochłaniania niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Absorption",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Aebsurpshun",
    }

class WarriorRuneOfMinorTactics(AttributeRune):
    id = ItemUpgradeId.OfMinorTactics
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Tactics",
        ServerLanguage.Korean: "{item_name}(하급 전술)",
        ServerLanguage.French: "{item_name} (Tactique : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Taktik",
        ServerLanguage.Italian: "{item_name} Tattica di grado minore",
        ServerLanguage.Spanish: "{item_name} (Táctica de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 戰術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー タクティクス)",
        ServerLanguage.Polish: "{item_name} Wojownika (Taktyka niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Tactics",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Taecteecs",
    }

class WarriorRuneOfMinorStrength(AttributeRune):
    id = ItemUpgradeId.OfMinorStrength
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Strength",
        ServerLanguage.Korean: "{item_name}(하급 강인함)",
        ServerLanguage.French: "{item_name} (Force : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Stärke",
        ServerLanguage.Italian: "{item_name} Forza di grado minore",
        ServerLanguage.Spanish: "{item_name} (Fuerza de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 力量 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ストレングス)",
        ServerLanguage.Polish: "{item_name} Wojownika (Siła niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Strength",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Strengt",
    }

class WarriorRuneOfMinorAxeMastery(AttributeRune):
    id = ItemUpgradeId.OfMinorAxeMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Axe Mastery",
        ServerLanguage.Korean: "{item_name}(하급 도끼술)",
        ServerLanguage.French: "{item_name} (Maîtrise de la hache : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Axtbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con l'Ascia di grado minore",
        ServerLanguage.Spanish: "{item_name} (Dominio del hacha de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 精通斧術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー アックス マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Toporach niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Axe Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Aexe-a Maestery",
    }

class WarriorRuneOfMinorHammerMastery(AttributeRune):
    id = ItemUpgradeId.OfMinorHammerMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Hammer Mastery",
        ServerLanguage.Korean: "{item_name}(하급 해머술)",
        ServerLanguage.French: "{item_name} (Maîtrise du marteau : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Hammerbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità col Martello di grado minore",
        ServerLanguage.Spanish: "{item_name} (Dominio del martillo de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 精通鎚術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ハンマー マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Młotach niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Hammer Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Haemmer Maestery",
    }

class WarriorRuneOfMinorSwordsmanship(AttributeRune):
    id = ItemUpgradeId.OfMinorSwordsmanship
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Swordsmanship",
        ServerLanguage.Korean: "{item_name}(하급 검술)",
        ServerLanguage.French: "{item_name} (Maîtrise de l'épée : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Schwertkunst",
        ServerLanguage.Italian: "{item_name} Scherma di grado minore",
        ServerLanguage.Spanish: "{item_name} (Esgrima de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 精通劍術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ソード マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Mieczach niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Swordsmanship",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Svurdsmunsheep",
    }

class WarriorRuneOfMajorAbsorption(Rune):
    id = ItemUpgradeId.OfMajorAbsorption
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    names = {
        ServerLanguage.English: "{item_name} of Major Absorption",
        ServerLanguage.Korean: "{item_name}(상급 흡수)",
        ServerLanguage.French: "{item_name} (Absorption : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Absorption",
        ServerLanguage.Italian: "{item_name} Assorbimento di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (absorción de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 吸收 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー アブソープション)",
        ServerLanguage.Polish: "{item_name} Wojownika (Pochłaniania wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Absorption",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Aebsurpshun",
    }

class WarriorRuneOfMajorTactics(AttributeRune):
    id = ItemUpgradeId.OfMajorTactics
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Tactics",
        ServerLanguage.Korean: "{item_name}(상급 전술)",
        ServerLanguage.French: "{item_name} (Tactique : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Taktik",
        ServerLanguage.Italian: "{item_name} Tattica di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Táctica de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 戰術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー タクティクス)",
        ServerLanguage.Polish: "{item_name} Wojownika (Taktyka wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Tactics",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Taecteecs",
    }

class WarriorRuneOfMajorStrength(AttributeRune):
    id = ItemUpgradeId.OfMajorStrength
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Strength",
        ServerLanguage.Korean: "{item_name}(상급 강인함)",
        ServerLanguage.French: "{item_name} (Force : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Stärke",
        ServerLanguage.Italian: "{item_name} Forza di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Fuerza de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 力量 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ストレングス)",
        ServerLanguage.Polish: "{item_name} Wojownika (Siła wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Strength",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Strengt",
    }

class WarriorRuneOfMajorAxeMastery(AttributeRune):
    id = ItemUpgradeId.OfMajorAxeMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Axe Mastery",
        ServerLanguage.Korean: "{item_name}(상급 도끼술)",
        ServerLanguage.French: "{item_name} (Maîtrise de la hache : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Axtbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con l'Ascia di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Dominio del hacha de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 精通斧術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー アックス マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Toporach wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Axe Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Aexe-a Maestery",
    }

class WarriorRuneOfMajorHammerMastery(AttributeRune):
    id = ItemUpgradeId.OfMajorHammerMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Hammer Mastery",
        ServerLanguage.Korean: "{item_name}(상급 해머술)",
        ServerLanguage.French: "{item_name} (Maîtrise du marteau : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Hammerbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità col Martello di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Dominio del martillo de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 精通鎚術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ハンマー マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Młotach wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Hammer Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Haemmer Maestery",
    }

class WarriorRuneOfMajorSwordsmanship(AttributeRune):
    id = ItemUpgradeId.OfMajorSwordsmanship
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Swordsmanship",
        ServerLanguage.Korean: "{item_name}(상급 검술)",
        ServerLanguage.French: "{item_name} (Maîtrise de l'épée : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Schwertkunst",
        ServerLanguage.Italian: "{item_name} Scherma di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Esgrima de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 精通劍術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ソード マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Mieczach wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Swordsmanship",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Svurdsmunsheep",
    }

class WarriorRuneOfSuperiorAbsorption(Rune):
    id = ItemUpgradeId.OfSuperiorAbsorption
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    names = {
        ServerLanguage.English: "{item_name} of Superior Absorption",
        ServerLanguage.Korean: "{item_name}(고급 흡수)",
        ServerLanguage.French: "{item_name} (Absorption : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Absorption",
        ServerLanguage.Italian: "{item_name} Assorbimento di grado supremo",
        ServerLanguage.Spanish: "{item_name} (absorción de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 吸收 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア アブソープション)",
        ServerLanguage.Polish: "{item_name} Wojownika (Pochłaniania najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Absorption",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Aebsurpshun",
    }

class WarriorRuneOfSuperiorTactics(AttributeRune):
    id = ItemUpgradeId.OfSuperiorTactics
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Tactics",
        ServerLanguage.Korean: "{item_name}(고급 전술)",
        ServerLanguage.French: "{item_name} (Tactique : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Taktik",
        ServerLanguage.Italian: "{item_name} Tattica di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Táctica de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 戰術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア タクティクス)",
        ServerLanguage.Polish: "{item_name} Wojownika (Taktyka najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Tactics",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Taecteecs",
    }

class WarriorRuneOfSuperiorStrength(AttributeRune):
    id = ItemUpgradeId.OfSuperiorStrength
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Strength",
        ServerLanguage.Korean: "{item_name}(고급 강인함)",
        ServerLanguage.French: "{item_name} (Force : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Stärke",
        ServerLanguage.Italian: "{item_name} Forza di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Fuerza de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 力量 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ストレングス)",
        ServerLanguage.Polish: "{item_name} Wojownika (Siła najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Strength",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Strengt",
    }

class WarriorRuneOfSuperiorAxeMastery(AttributeRune):
    id = ItemUpgradeId.OfSuperiorAxeMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Axe Mastery",
        ServerLanguage.Korean: "{item_name}(고급 도끼술)",
        ServerLanguage.French: "{item_name} (Maîtrise de la hache : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Axtbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con l'Ascia di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Dominio del hacha de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 精通斧術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア アックス マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Toporach najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Axe Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Aexe-a Maestery",
    }

class WarriorRuneOfSuperiorHammerMastery(AttributeRune):
    id = ItemUpgradeId.OfSuperiorHammerMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Hammer Mastery",
        ServerLanguage.Korean: "{item_name}(고급 해머술)",
        ServerLanguage.French: "{item_name} (Maîtrise du marteau : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Hammerbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità col Martello di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Dominio del martillo de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 精通鎚術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ハンマー マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Młotach najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Hammer Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Haemmer Maestery",
    }

class WarriorRuneOfSuperiorSwordsmanship(AttributeRune):
    id = ItemUpgradeId.OfSuperiorSwordsmanship
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Swordsmanship",
        ServerLanguage.Korean: "{item_name}(고급 검술)",
        ServerLanguage.French: "{item_name} (Maîtrise de l'épée : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Schwertkunst",
        ServerLanguage.Italian: "{item_name} Scherma di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Esgrima de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 精通劍術 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ソード マスタリー)",
        ServerLanguage.Polish: "{item_name} Wojownika (Biegłość w Mieczach najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Swordsmanship",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Svurdsmunsheep",
    }

class UpgradeMinorRuneWarrior(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Warrior
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneWarrior(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Warrior
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneWarrior(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Warrior
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneWarrior(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Warrior
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneWarrior(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Warrior
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneWarrior(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Warrior
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Warrior

#region Ranger

class FrostboundInsignia(Insignia):
    id = ItemUpgradeId.Frostbound
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Frostbound {item_name}",
        ServerLanguage.Korean: "얼음결계의 {item_name}",
        ServerLanguage.French: "{item_name} de givre",
        ServerLanguage.German: "Permafrost--{item_name}",
        ServerLanguage.Italian: "{item_name} da Ghiaccio",
        ServerLanguage.Spanish: "{item_name} de montaña",
        ServerLanguage.TraditionalChinese: "霜縛 {item_name}",
        ServerLanguage.Japanese: "フロストバウンド {item_name}",
        ServerLanguage.Polish: "{item_name} Spętanego przez Lód",
        ServerLanguage.Russian: "Frostbound {item_name}",
        ServerLanguage.BorkBorkBork: "Frustbuoond {item_name}",
    }

class PyreboundInsignia(Insignia):
    id = ItemUpgradeId.Pyrebound
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Pyrebound {item_name}",
        ServerLanguage.Korean: "화염결계의 {item_name}",
        ServerLanguage.French: "{item_name} du bûcher",
        ServerLanguage.German: "Scheiterhaufen--{item_name}",
        ServerLanguage.Italian: "{item_name} da Rogo",
        ServerLanguage.Spanish: "{item_name} de leñero",
        ServerLanguage.TraditionalChinese: "火縛 {item_name}",
        ServerLanguage.Japanese: "パイアーバウンド {item_name}",
        ServerLanguage.Polish: "{item_name} Spętanego przez Ogień",
        ServerLanguage.Russian: "Pyrebound {item_name}",
        ServerLanguage.BorkBorkBork: "Pyrebuoond {item_name}",
    }

class StormboundInsignia(Insignia):
    id = ItemUpgradeId.Stormbound
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Stormbound {item_name}",
        ServerLanguage.Korean: "폭풍결계의 {item_name}",
        ServerLanguage.French: "{item_name} de tonnerre",
        ServerLanguage.German: "Unwetter--{item_name}",
        ServerLanguage.Italian: "{item_name} da Bufera",
        ServerLanguage.Spanish: "{item_name} de hidromántico",
        ServerLanguage.TraditionalChinese: "風縛 {item_name}",
        ServerLanguage.Japanese: "ストームバウンド {item_name}",
        ServerLanguage.Polish: "{item_name} Spętanego przez Sztorm",
        ServerLanguage.Russian: "Stormbound {item_name}",
        ServerLanguage.BorkBorkBork: "Sturmbuoond {item_name}",
    }

class ScoutsInsignia(Insignia):
    id = ItemUpgradeId.Scouts
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Scout's {item_name}",
        ServerLanguage.Korean: "정찰병의 {item_name}",
        ServerLanguage.French: "{item_name} d'éclaireur",
        ServerLanguage.German: "Späher--{item_name}",
        ServerLanguage.Italian: "{item_name} da Perlustratore",
        ServerLanguage.Spanish: "{item_name} de explorador",
        ServerLanguage.TraditionalChinese: "偵查者 {item_name}",
        ServerLanguage.Japanese: "スカウト {item_name}",
        ServerLanguage.Polish: "{item_name} Zwiadowcy",
        ServerLanguage.Russian: "Scout's {item_name}",
        ServerLanguage.BorkBorkBork: "Scuoot's {item_name}",
    }

class EarthboundInsignia(Insignia):
    id = ItemUpgradeId.Earthbound
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Earthbound {item_name}",
        ServerLanguage.Korean: "대지결계의 {item_name}",
        ServerLanguage.French: "{item_name} terrestre",
        ServerLanguage.German: "Erdbindungs--{item_name}",
        ServerLanguage.Italian: "{item_name} da Terra",
        ServerLanguage.Spanish: "{item_name} de tierra",
        ServerLanguage.TraditionalChinese: "地縛 {item_name}",
        ServerLanguage.Japanese: "アースバウンド {item_name}",
        ServerLanguage.Polish: "{item_name} Spętanego przez Ziemię",
        ServerLanguage.Russian: "Earthbound {item_name}",
        ServerLanguage.BorkBorkBork: "Iaerthbuoond {item_name}",
    }

class BeastmastersInsignia(Insignia):
    id = ItemUpgradeId.Beastmasters
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Beastmaster's {item_name}",
        ServerLanguage.Korean: "조련사의 {item_name}",
        ServerLanguage.French: "{item_name} de belluaire",
        ServerLanguage.German: "Tierbändiger--{item_name}",
        ServerLanguage.Italian: "{item_name} da Domatore",
        ServerLanguage.Spanish: "{item_name} de domador",
        ServerLanguage.TraditionalChinese: "野獸大師 {item_name}",
        ServerLanguage.Japanese: "ビーストマスター {item_name}",
        ServerLanguage.Polish: "{item_name} Władcy Zwierząt",
        ServerLanguage.Russian: "Beastmaster's {item_name}",
        ServerLanguage.BorkBorkBork: "Beaestmaester's {item_name}",
    }

class RangerRuneOfMinorWildernessSurvival(AttributeRune):
    id = ItemUpgradeId.OfMinorWildernessSurvival
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Wilderness Survival",
        ServerLanguage.Korean: "{item_name}(하급 생존술)",
        ServerLanguage.French: "{item_name} (Survie : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Überleben in der Wildnis",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Sopravvivenza nella Natura di grado minore",
        ServerLanguage.Spanish: "{item_name} (Supervivencia naturaleza de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 求生 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー サバイバル)",
        ServerLanguage.Polish: "{item_name} (Przetrwanie w Dziczy niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Wilderness Survival",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Meenur Veelderness Soorfeefael",
    }

class RangerRuneOfMinorExpertise(AttributeRune):
    id = ItemUpgradeId.OfMinorExpertise
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Expertise",
        ServerLanguage.Korean: "{item_name}(하급 전문성)",
        ServerLanguage.French: "{item_name} (Expertise : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Fachkenntnis",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Esperienza di grado minore",
        ServerLanguage.Spanish: "{item_name} (Pericia de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 專精 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー エキスパーティーズ)",
        ServerLanguage.Polish: "{item_name} (Specjalizacja niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Expertise",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Meenur Ixperteese-a",
    }

class RangerRuneOfMinorBeastMastery(AttributeRune):
    id = ItemUpgradeId.OfMinorBeastMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Beast Mastery",
        ServerLanguage.Korean: "{item_name}(하급 동물 친화)",
        ServerLanguage.French: "{item_name} (Domptage : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Tierbeherrschung",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Potere sulle Belve di grado minore",
        ServerLanguage.Spanish: "{item_name} (Dominio de bestias de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 野獸支配 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ビースト マスタリー)",
        ServerLanguage.Polish: "{item_name} (Panowanie nad Zwierzętami niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Beast Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Meenur Beaest Maestery",
    }

class RangerRuneOfMinorMarksmanship(AttributeRune):
    id = ItemUpgradeId.OfMinorMarksmanship
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Marksmanship",
        ServerLanguage.Korean: "{item_name}(하급 궁술)",
        ServerLanguage.French: "{item_name} (Adresse au tir : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Treffsicherheit",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Precisione di grado minore",
        ServerLanguage.Spanish: "{item_name} (Puntería de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 弓術精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ボウ マスタリー)",
        ServerLanguage.Polish: "{item_name} (Umiejętności Strzeleckie niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Marksmanship",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Meenur Maerksmunsheep",
    }

class RangerRuneOfMajorWildernessSurvival(AttributeRune):
    id = ItemUpgradeId.OfMajorWildernessSurvival
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Wilderness Survival",
        ServerLanguage.Korean: "{item_name}(상급 생존술)",
        ServerLanguage.French: "{item_name} (Survie : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Überleben in der Wildnis",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Sopravvivenza nella Natura di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Supervivencia naturaleza de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 求生 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー サバイバル)",
        ServerLanguage.Polish: "{item_name} (Przetrwanie w Dziczy wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Wilderness Survival",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Maejur Veelderness Soorfeefael",
    }

class RangerRuneOfMajorExpertise(AttributeRune):
    id = ItemUpgradeId.OfMajorExpertise
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Expertise",
        ServerLanguage.Korean: "{item_name}(상급 전문성)",
        ServerLanguage.French: "{item_name} (Expertise : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Fachkenntnis",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Esperienza di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Pericia de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 專精 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー エキスパーティーズ)",
        ServerLanguage.Polish: "{item_name} (Specjalizacja wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Expertise",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Maejur Ixperteese-a",
    }

class RangerRuneOfMajorBeastMastery(AttributeRune):
    id = ItemUpgradeId.OfMajorBeastMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Beast Mastery",
        ServerLanguage.Korean: "{item_name}(상급 동물 친화)",
        ServerLanguage.French: "{item_name} (Domptage : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Tierbeherrschung",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Potere sulle Belve di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Dominio de bestias de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 野獸支配 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ビースト マスタリー)",
        ServerLanguage.Polish: "{item_name} (Panowanie nad Zwierzętami wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Beast Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Maejur Beaest Maestery",
    }

class RangerRuneOfMajorMarksmanship(AttributeRune):
    id = ItemUpgradeId.OfMajorMarksmanship
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Marksmanship",
        ServerLanguage.Korean: "{item_name}(상급 궁술)",
        ServerLanguage.French: "{item_name} (Adresse au tir : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Treffsicherheit",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Precisione di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Puntería de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 弓術精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ボウ マスタリー)",
        ServerLanguage.Polish: "{item_name} (Umiejętności Strzeleckie wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Marksmanship",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Maejur Maerksmunsheep",
    }

class RangerRuneOfSuperiorWildernessSurvival(AttributeRune):
    id = ItemUpgradeId.OfSuperiorWildernessSurvival
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Wilderness Survival",
        ServerLanguage.Korean: "{item_name}(고급 생존술)",
        ServerLanguage.French: "{item_name} (Survie : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Überleben in der Wildnis",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Sopravvivenza nella Natura di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Supervivencia naturaleza de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 求生 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア サバイバル)",
        ServerLanguage.Polish: "{item_name} (Przetrwanie w Dziczy najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Wilderness Survival",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Soopereeur Veelderness Soorfeefael",
    }

class RangerRuneOfSuperiorExpertise(AttributeRune):
    id = ItemUpgradeId.OfSuperiorExpertise
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Expertise",
        ServerLanguage.Korean: "{item_name}(고급 전문성)",
        ServerLanguage.French: "{item_name} (Expertise : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Fachkenntnis",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Esperienza di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Pericia de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 專精 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア エキスパーティーズ)",
        ServerLanguage.Polish: "{item_name} (Specjalizacja najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Expertise",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Soopereeur Ixperteese-a",
    }

class RangerRuneOfSuperiorBeastMastery(AttributeRune):
    id = ItemUpgradeId.OfSuperiorBeastMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Beast Mastery",
        ServerLanguage.Korean: "{item_name}(고급 동물 친화)",
        ServerLanguage.French: "{item_name} (Domptage : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Tierbeherrschung",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Potere sulle Belve di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Dominio de bestias de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 野獸支配 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ビースト マスタリー)",
        ServerLanguage.Polish: "{item_name} (Panowanie nad Zwierzętami najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Beast Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Soopereeur Beaest Maestery",
    }

class RangerRuneOfSuperiorMarksmanship(AttributeRune):
    id = ItemUpgradeId.OfSuperiorMarksmanship
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Marksmanship",
        ServerLanguage.Korean: "{item_name}(고급 궁술)",
        ServerLanguage.French: "{item_name} (Adresse au tir : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Treffsicherheit",
        ServerLanguage.Italian: "{item_name} dell'Esploratore Precisione di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Puntería de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 弓術精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ボウ マスタリー)",
        ServerLanguage.Polish: "{item_name} (Umiejętności Strzeleckie najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Marksmanship",
        ServerLanguage.BorkBorkBork: "{item_name} {item_name} ooff Soopereeur Maerksmunsheep",
    }

class UpgradeMinorRuneRanger(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Ranger
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneRanger(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Ranger
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneRanger(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Ranger
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneRanger(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Ranger
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneRanger(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Ranger
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneRanger(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Ranger
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Ranger

#region Monk

class WanderersInsignia(Insignia):
    id = ItemUpgradeId.Wanderers
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Wanderer's {item_name}",
        ServerLanguage.Korean: "방랑자의 {item_name}",
        ServerLanguage.French: "{item_name} de vagabond",
        ServerLanguage.German: "Wanderer--{item_name}",
        ServerLanguage.Italian: "{item_name} da Vagabondo",
        ServerLanguage.Spanish: "{item_name} de trotamundos",
        ServerLanguage.TraditionalChinese: "流浪者 {item_name}",
        ServerLanguage.Japanese: "ワンダラー {item_name}",
        ServerLanguage.Polish: "{item_name} Wędrowca",
        ServerLanguage.Russian: "Wanderer's {item_name}",
        ServerLanguage.BorkBorkBork: "Vunderer's {item_name}",
    }

class DisciplesInsignia(Insignia):
    id = ItemUpgradeId.Disciples
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Disciple's {item_name}",
        ServerLanguage.Korean: "사도의 {item_name}",
        ServerLanguage.French: "{item_name} de disciple",
        ServerLanguage.German: "Jünger--{item_name}",
        ServerLanguage.Italian: "{item_name} da Discepolo",
        ServerLanguage.Spanish: "{item_name} de discípulo",
        ServerLanguage.TraditionalChinese: "門徒 {item_name}",
        ServerLanguage.Japanese: "ディサイプル {item_name}",
        ServerLanguage.Polish: "{item_name} Ucznia",
        ServerLanguage.Russian: "Disciple's {item_name}",
        ServerLanguage.BorkBorkBork: "Deesceeple-a's {item_name}",
    }

class AnchoritesInsignia(Insignia):
    id = ItemUpgradeId.Anchorites
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Anchorite's {item_name}",
        ServerLanguage.Korean: "은둔자의 {item_name}",
        ServerLanguage.French: "{item_name} d'anachorète",
        ServerLanguage.German: "Einsiedler--{item_name}",
        ServerLanguage.Italian: "{item_name} da Anacoreta",
        ServerLanguage.Spanish: "{item_name} de anacoreta",
        ServerLanguage.TraditionalChinese: "隱士 {item_name}",
        ServerLanguage.Japanese: "アンコライト {item_name}",
        ServerLanguage.Polish: "{item_name} Pustelnika",
        ServerLanguage.Russian: "Anchorite's {item_name}",
        ServerLanguage.BorkBorkBork: "Unchureete-a's {item_name}",
    }

class MonkRuneOfMinorHealingPrayers(AttributeRune):
    id = ItemUpgradeId.OfMinorHealingPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Healing Prayers",
        ServerLanguage.Korean: "{item_name}(하급 치유)",
        ServerLanguage.French: "{item_name} (Prières de guérison : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Heilgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Curative di grado minore",
        ServerLanguage.Spanish: "{item_name} (Plegarias curativas de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 治療祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ヒーリング)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Uzdrawiające niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Healing Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Heaeleeng Praeyers",
    }

class MonkRuneOfMinorSmitingPrayers(AttributeRune):
    id = ItemUpgradeId.OfMinorSmitingPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Smiting Prayers",
        ServerLanguage.Korean: "{item_name}(하급 천벌)",
        ServerLanguage.French: "{item_name} (Prières de châtiment : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Peinigungsgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Punitive di grado minore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de ataque de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 懲戒祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ホーリー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ofensywne niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Smiting Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Smeeteeng Praeyers",
    }

class MonkRuneOfMinorProtectionPrayers(AttributeRune):
    id = ItemUpgradeId.OfMinorProtectionPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Protection Prayers",
        ServerLanguage.Korean: "{item_name}(하급 보호)",
        ServerLanguage.French: "{item_name} (Prières de protection : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Schutzgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Protettive di grado minore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de protección de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 防護祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー プロテクション)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ochronne niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Protection Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Prutecshun Praeyers",
    }

class MonkRuneOfMinorDivineFavor(AttributeRune):
    id = ItemUpgradeId.OfMinorDivineFavor
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Divine Favor",
        ServerLanguage.Korean: "{item_name}(하급 신의 은총)",
        ServerLanguage.French: "{item_name} (Faveur divine : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Gunst der Götter",
        ServerLanguage.Italian: "{item_name} Favore Divino di grado minore",
        ServerLanguage.Spanish: "{item_name} (Favor divino de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 神恩 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ディヴァイン)",
        ServerLanguage.Polish: "{item_name} (Łaska Bogów niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Divine Favor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Deefeene-a Faefur",
    }

class MonkRuneOfMajorHealingPrayers(AttributeRune):
    id = ItemUpgradeId.OfMajorHealingPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Healing Prayers",
        ServerLanguage.Korean: "{item_name}(상급 치유)",
        ServerLanguage.French: "{item_name} (Prières de guérison : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Heilgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Curative di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Plegarias curativas de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 治療祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ヒーリング)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Uzdrawiające wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Healing Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Heaeleeng Praeyers",
    }

class MonkRuneOfMajorSmitingPrayers(AttributeRune):
    id = ItemUpgradeId.OfMajorSmitingPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Smiting Prayers",
        ServerLanguage.Korean: "{item_name}(상급 천벌)",
        ServerLanguage.French: "{item_name} (Prières de châtiment : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Peinigungsgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Punitive di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de ataque de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 懲戒祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ホーリー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ofensywne wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Smiting Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Smeeteeng Praeyers",
    }

class MonkRuneOfMajorProtectionPrayers(AttributeRune):
    id = ItemUpgradeId.OfMajorProtectionPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Protection Prayers",
        ServerLanguage.Korean: "{item_name}(상급 보호)",
        ServerLanguage.French: "{item_name} (Prières de protection : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Schutzgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Protettive di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de protección de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 防護祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー プロテクション)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ochronne wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Protection Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Prutecshun Praeyers",
    }

class MonkRuneOfMajorDivineFavor(AttributeRune):
    id = ItemUpgradeId.OfMajorDivineFavor
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Divine Favor",
        ServerLanguage.Korean: "{item_name}(상급 신의 은총)",
        ServerLanguage.French: "{item_name} (Faveur divine : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Gunst der Götter",
        ServerLanguage.Italian: "{item_name} Favore Divino di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Favor divino de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 神恩 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ディヴァイン)",
        ServerLanguage.Polish: "{item_name} (Łaska Bogów wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Divine Favor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Deefeene-a Faefur",
    }

class MonkRuneOfSuperiorHealingPrayers(AttributeRune):
    id = ItemUpgradeId.OfSuperiorHealingPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Healing Prayers",
        ServerLanguage.Korean: "{item_name}(고급 치유)",
        ServerLanguage.French: "{item_name} (Prières de guérison : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Heilgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Curative di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Plegarias curativas de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 治療祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ヒーリング)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Uzdrawiające najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Healing Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Heaeleeng Praeyers",
    }

class MonkRuneOfSuperiorSmitingPrayers(AttributeRune):
    id = ItemUpgradeId.OfSuperiorSmitingPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Smiting Prayers",
        ServerLanguage.Korean: "{item_name}(고급 천벌)",
        ServerLanguage.French: "{item_name} (Prières de châtiment : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Peinigungsgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Punitive di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Plegarias de ataque de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 懲戒祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ホーリー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ofensywne najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Smiting Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Smeeteeng Praeyers",
    }

class MonkRuneOfSuperiorProtectionPrayers(AttributeRune):
    id = ItemUpgradeId.OfSuperiorProtectionPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Protection Prayers",
        ServerLanguage.Korean: "{item_name}(고급 보호)",
        ServerLanguage.French: "{item_name} (Prières de protection : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Schutzgebete",
        ServerLanguage.Italian: "{item_name} Preghiere Protettive di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Plegarias de protección de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 防護祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア プロテクション)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ochronne najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Protection Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Prutecshun Praeyers",
    }

class MonkRuneOfSuperiorDivineFavor(AttributeRune):
    id = ItemUpgradeId.OfSuperiorDivineFavor
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Divine Favor",
        ServerLanguage.Korean: "{item_name}(고급 신의 은총)",
        ServerLanguage.French: "{item_name} (Faveur divine : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Gunst der Götter",
        ServerLanguage.Italian: "{item_name} Favore Divino di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Favor divino de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 神恩 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ディヴァイン)",
        ServerLanguage.Polish: "{item_name} (Łaska Bogów najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Divine Favor",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Deefeene-a Faefur",
    }

class UpgradeMinorRuneMonk(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Monk
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneMonk(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Monk
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneMonk(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Monk
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneMonk(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Monk
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneMonk(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Monk
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneMonk(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Monk
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Monk

#region Necromancer

class BloodstainedInsignia(Insignia):
    id = ItemUpgradeId.Bloodstained
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Bloodstained {item_name}",
        ServerLanguage.Korean: "혈흔의 {item_name}",
        ServerLanguage.French: "{item_name} de Sang",
        ServerLanguage.German: "Blutfleck--{item_name}",
        ServerLanguage.Italian: "{item_name} di Sangue",
        ServerLanguage.Spanish: "{item_name} con sangre",
        ServerLanguage.TraditionalChinese: "血腥 {item_name}",
        ServerLanguage.Japanese: "ブラッドステイン {item_name}",
        ServerLanguage.Polish: "{item_name} Okrwawienia",
        ServerLanguage.Russian: "Bloodstained {item_name}",
        ServerLanguage.BorkBorkBork: "Bluudstaeeened {item_name}",
    }

class TormentorsInsignia(Insignia):
    id = ItemUpgradeId.Tormentors
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Tormentor's {item_name}",
        ServerLanguage.Korean: "고문가의 {item_name}",
        ServerLanguage.French: "{item_name} de persécuteur",
        ServerLanguage.German: "Folterer--{item_name}",
        ServerLanguage.Italian: "{item_name} da Tormentatore",
        ServerLanguage.Spanish: "{item_name} de torturador",
        ServerLanguage.TraditionalChinese: "苦痛者 {item_name}",
        ServerLanguage.Japanese: "トルメンター {item_name}",
        ServerLanguage.Polish: "{item_name} Oprawcy",
        ServerLanguage.Russian: "Tormentor's {item_name}",
        ServerLanguage.BorkBorkBork: "Turmentur's {item_name}",
    }

class BonelaceInsignia(Insignia):
    id = ItemUpgradeId.Bonelace
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Bonelace {item_name}",
        ServerLanguage.Korean: "해골장식 {item_name}",
        ServerLanguage.French: "{item_name} de dentelle",
        ServerLanguage.German: "Klöppelspitzen--{item_name}",
        ServerLanguage.Italian: "{item_name} di Maglia d'Ossa",
        ServerLanguage.Spanish: "{item_name} de cordones de hueso",
        ServerLanguage.TraditionalChinese: "骨飾 {item_name}",
        ServerLanguage.Japanese: "ボーンレース {item_name}",
        ServerLanguage.Polish: "{item_name} Kościanej Lancy",
        ServerLanguage.Russian: "Bonelace {item_name}",
        ServerLanguage.BorkBorkBork: "Bunelaece-a {item_name}",
    }

class MinionMastersInsignia(Insignia):
    id = ItemUpgradeId.MinionMasters
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Minion Master's {item_name}",
        ServerLanguage.Korean: "언데드마스터의 {item_name}",
        ServerLanguage.French: "{item_name} du Maître des serviteurs",
        ServerLanguage.German: "Dienermeister--{item_name}",
        ServerLanguage.Italian: "{item_name} da Domasgherri",
        ServerLanguage.Spanish: "{item_name} de maestro de siervos",
        ServerLanguage.TraditionalChinese: "爪牙大師 {item_name}",
        ServerLanguage.Japanese: "ミニオン マスター {item_name}",
        ServerLanguage.Polish: "{item_name} Władcy Sług",
        ServerLanguage.Russian: "Minion Master's {item_name}",
        ServerLanguage.BorkBorkBork: "Meeneeun Maester's {item_name}",
    }

class BlightersInsignia(Insignia):
    id = ItemUpgradeId.Blighters
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Blighter's {item_name}",
        ServerLanguage.Korean: "오염자의 {item_name}",
        ServerLanguage.French: "{item_name} de destructeur",
        ServerLanguage.German: "Verderber--{item_name}",
        ServerLanguage.Italian: "{item_name} da Malfattore",
        ServerLanguage.Spanish: "{item_name} de malhechor",
        ServerLanguage.TraditionalChinese: "破壞者 {item_name}",
        ServerLanguage.Japanese: "ブライター {item_name}",
        ServerLanguage.Polish: "{item_name} Złoczyńcy",
        ServerLanguage.Russian: "Blighter's {item_name}",
        ServerLanguage.BorkBorkBork: "Bleeghter's {item_name}",
    }

class UndertakersInsignia(Insignia):
    id = ItemUpgradeId.Undertakers
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Undertaker's {item_name}",
        ServerLanguage.Korean: "장의사의 {item_name}",
        ServerLanguage.French: "{item_name} du fossoyeur",
        ServerLanguage.German: "Leichenbestatter--{item_name}",
        ServerLanguage.Italian: "{item_name} da Becchino",
        ServerLanguage.Spanish: "{item_name} de enterrador",
        ServerLanguage.TraditionalChinese: "承受者 {item_name}",
        ServerLanguage.Japanese: "アンダーテイカー {item_name}",
        ServerLanguage.Polish: "{item_name} Grabarza",
        ServerLanguage.Russian: "Undertaker's {item_name}",
        ServerLanguage.BorkBorkBork: "Undertaeker's {item_name}",
    }

class NecromancerRuneOfMinorBloodMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorBloodMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Blood Magic",
        ServerLanguage.Korean: "{item_name}(하급 피)",
        ServerLanguage.French: "{item_name} (Magie du sang : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Blutmagie",
        ServerLanguage.Italian: "{item_name} Magia del Sangue di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de sangre de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 血魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ブラッド)",
        ServerLanguage.Polish: "{item_name} (Magia Krwi niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Blood Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Bluud Maegeec",
    }

class NecromancerRuneOfMinorDeathMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorDeathMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Death Magic",
        ServerLanguage.Korean: "{item_name}(하급 죽음)",
        ServerLanguage.French: "{item_name} (Magie de la mort : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Todesmagie",
        ServerLanguage.Italian: "{item_name} Magia della Morte di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de muerte de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 死亡魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー デス)",
        ServerLanguage.Polish: "{item_name} (Magia Śmierci niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Death Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Deaet Maegeec",
    }

class NecromancerRuneOfMinorCurses(AttributeRune):
    id = ItemUpgradeId.OfMinorCurses
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Curses",
        ServerLanguage.Korean: "{item_name}(하급 저주)",
        ServerLanguage.French: "{item_name} (Malédictions : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Flüche",
        ServerLanguage.Italian: "{item_name} Maledizioni di grado minore",
        ServerLanguage.Spanish: "{item_name} (Maldiciones de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 詛咒 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー カース)",
        ServerLanguage.Polish: "{item_name} (Klątwy niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Curses",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Coorses",
    }

class NecromancerRuneOfMinorSoulReaping(AttributeRune):
    id = ItemUpgradeId.OfMinorSoulReaping
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Soul Reaping",
        ServerLanguage.Korean: "{item_name}(하급 영혼)",
        ServerLanguage.French: "{item_name} (Moisson des âmes : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Seelensammlung",
        ServerLanguage.Italian: "{item_name} Sottrazione dell'Anima di grado minore",
        ServerLanguage.Spanish: "{item_name} (Cosecha de almas de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 靈魂吸取 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ソウル リーピング)",
        ServerLanguage.Polish: "{item_name} (Wydzieranie Duszy niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Soul Reaping",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Suool Reaepeeng",
    }

class NecromancerRuneOfMajorBloodMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorBloodMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Blood Magic",
        ServerLanguage.Korean: "{item_name}(상급 피)",
        ServerLanguage.French: "{item_name} (Magie du sang : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Blutmagie",
        ServerLanguage.Italian: "{item_name} Magia del Sangue di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de sangre de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 血魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ブラッド)",
        ServerLanguage.Polish: "{item_name} (Magia Krwi wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Blood Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Bluud Maegeec",
    }

class NecromancerRuneOfMajorDeathMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorDeathMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Death Magic",
        ServerLanguage.Korean: "{item_name}(상급 죽음)",
        ServerLanguage.French: "{item_name} (Magie de la mort : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Todesmagie",
        ServerLanguage.Italian: "{item_name} Magia della Morte di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de muerte de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 死亡魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー デス)",
        ServerLanguage.Polish: "{item_name} (Magia Śmierci wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Death Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Deaet Maegeec",
    }

class NecromancerRuneOfMajorCurses(AttributeRune):
    id = ItemUpgradeId.OfMajorCurses
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Curses",
        ServerLanguage.Korean: "{item_name}(상급 저주)",
        ServerLanguage.French: "{item_name} (Malédictions : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Flüche",
        ServerLanguage.Italian: "{item_name} Maledizioni di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Maldiciones de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 詛咒 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー カース)",
        ServerLanguage.Polish: "{item_name} (Klątwy wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Curses",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Coorses",
    }

class NecromancerRuneOfMajorSoulReaping(AttributeRune):
    id = ItemUpgradeId.OfMajorSoulReaping
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Soul Reaping",
        ServerLanguage.Korean: "{item_name}(상급 영혼)",
        ServerLanguage.French: "{item_name} (Moisson des âmes : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Seelensammlung",
        ServerLanguage.Italian: "{item_name} Sottrazione dell'Anima di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Cosecha de almas de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 靈魂吸取 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ソウル リーピング)",
        ServerLanguage.Polish: "{item_name} (Wydzieranie Duszy wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Soul Reaping",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Suool Reaepeeng",
    }

class NecromancerRuneOfSuperiorBloodMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorBloodMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Blood Magic",
        ServerLanguage.Korean: "{item_name}(고급 피)",
        ServerLanguage.French: "{item_name} (Magie du sang : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Blutmagie",
        ServerLanguage.Italian: "{item_name} Magia del Sangue di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de sangre de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 血魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ブラッド)",
        ServerLanguage.Polish: "{item_name} (Magia Krwi najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Blood Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Bluud Maegeec",
    }

class NecromancerRuneOfSuperiorDeathMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorDeathMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Death Magic",
        ServerLanguage.Korean: "{item_name}(고급 죽음)",
        ServerLanguage.French: "{item_name} (Magie de la mort : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Todesmagie",
        ServerLanguage.Italian: "{item_name} Magia della Morte di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de muerte de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 死亡魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア デス)",
        ServerLanguage.Polish: "{item_name} (Magia Śmierci najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Death Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Deaet Maegeec",
    }

class NecromancerRuneOfSuperiorCurses(AttributeRune):
    id = ItemUpgradeId.OfSuperiorCurses
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Curses",
        ServerLanguage.Korean: "{item_name}(고급 저주)",
        ServerLanguage.French: "{item_name} (Malédictions : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Flüche",
        ServerLanguage.Italian: "{item_name} Maledizioni di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Maldiciones de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 詛咒 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア カース)",
        ServerLanguage.Polish: "{item_name} (Klątwy najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Curses",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Coorses",
    }

class NecromancerRuneOfSuperiorSoulReaping(AttributeRune):
    id = ItemUpgradeId.OfSuperiorSoulReaping
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Soul Reaping",
        ServerLanguage.Korean: "{item_name}(고급 영혼)",
        ServerLanguage.French: "{item_name} (Moisson des âmes : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Seelensammlung",
        ServerLanguage.Italian: "{item_name} Sottrazione dell'Anima di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Cosecha de almas de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 靈魂吸取 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ソウル リーピング)",
        ServerLanguage.Polish: "{item_name} (Wydzieranie Duszy najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Soul Reaping",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Suool Reaepeeng",
    }

class UpgradeMinorRuneNecromancer(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Necromancer
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneNecromancer(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Necromancer
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneNecromancer(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Necromancer
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneNecromancer(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Necromancer
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneNecromancer(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Necromancer
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneNecromancer(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Necromancer
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Necromancer

#region Mesmer

class VirtuososInsignia(Insignia):
    id = ItemUpgradeId.Virtuosos
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Virtuoso's {item_name}",
        ServerLanguage.Korean: "거장의 {item_name}",
        ServerLanguage.French: "{item_name} de virtuose",
        ServerLanguage.German: "Virtuosen--{item_name}",
        ServerLanguage.Italian: "{item_name} da Intenditore",
        ServerLanguage.Spanish: "{item_name} de virtuoso",
        ServerLanguage.TraditionalChinese: "鑑賞家 {item_name}",
        ServerLanguage.Japanese: "ヴァーチュオーソ {item_name}",
        ServerLanguage.Polish: "{item_name} Wirtuoza",
        ServerLanguage.Russian: "Virtuoso's {item_name}",
        ServerLanguage.BorkBorkBork: "Furtoousu's {item_name}",
    }

class ArtificersInsignia(Insignia):
    id = ItemUpgradeId.Artificers
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Artificer's {item_name}",
        ServerLanguage.Korean: "장인의 {item_name}",
        ServerLanguage.French: "{item_name} de l'artisan",
        ServerLanguage.German: "Feuerwerker--{item_name}",
        ServerLanguage.Italian: "{item_name} da Artefice",
        ServerLanguage.Spanish: "{item_name} de artífice",
        ServerLanguage.TraditionalChinese: "巧匠 {item_name}",
        ServerLanguage.Japanese: "アーティファサー {item_name}",
        ServerLanguage.Polish: "{item_name} Rzemieślnika",
        ServerLanguage.Russian: "Artificer's {item_name}",
        ServerLanguage.BorkBorkBork: "Aerteeffeecer's {item_name}",
    }

class ProdigysInsignia(Insignia):
    id = ItemUpgradeId.Prodigys
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Prodigy's {item_name}",
        ServerLanguage.Korean: "천재의 {item_name}",
        ServerLanguage.French: "{item_name} prodige",
        ServerLanguage.German: "Wunder--{item_name}",
        ServerLanguage.Italian: "{item_name} da Prodigio",
        ServerLanguage.Spanish: "{item_name} de prodigio",
        ServerLanguage.TraditionalChinese: "奇蹟 {item_name}",
        ServerLanguage.Japanese: "プロディジー {item_name}",
        ServerLanguage.Polish: "{item_name} Geniusza",
        ServerLanguage.Russian: "Prodigy's {item_name}",
        ServerLanguage.BorkBorkBork: "Prudeegy's {item_name}",
    }

class MesmerRuneOfMinorFastCasting(AttributeRune):
    id = ItemUpgradeId.OfMinorFastCasting
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Fast Casting",
        ServerLanguage.Korean: "{item_name}(하급 빠른 시전)",
        ServerLanguage.French: "{item_name} (Incantation rapide : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Schnellwirkung",
        ServerLanguage.Italian: "{item_name} Lancio Rapido di grado minore",
        ServerLanguage.Spanish: "{item_name} (Lanzar conjuros rápido de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 快速施法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ファスト キャスト)",
        ServerLanguage.Polish: "{item_name} (Szybkie Rzucanie Czarów niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Fast Casting",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Faest Caesteeng",
    }

class MesmerRuneOfMinorDominationMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorDominationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Domination Magic",
        ServerLanguage.Korean: "{item_name}(하급 지배)",
        ServerLanguage.French: "{item_name} (Magie de domination : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Beherrschungsmagie",
        ServerLanguage.Italian: "{item_name} Magia del Dominio di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de dominación de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 支配魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ドミネーション)",
        ServerLanguage.Polish: "{item_name} (Magia Dominacji niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Domination Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Dumeenaeshun Maegeec",
    }

class MesmerRuneOfMinorIllusionMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorIllusionMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Illusion Magic",
        ServerLanguage.Korean: "{item_name}(하급 환상)",
        ServerLanguage.French: "{item_name} (Magie de l'illusion : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Illusionsmagie",
        ServerLanguage.Italian: "{item_name} Magia Illusoria di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de ilusión de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 幻術魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー イリュージョン)",
        ServerLanguage.Polish: "{item_name} (Magia Iluzji niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Illusion Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Illooseeun Maegeec",
    }

class MesmerRuneOfMinorInspirationMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorInspirationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Inspiration Magic",
        ServerLanguage.Korean: "{item_name}(하급 영감)",
        ServerLanguage.French: "{item_name} (Magie de l'inspiration : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Inspirationsmagie",
        ServerLanguage.Italian: "{item_name} Magia di Ispirazione di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de inspiración de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 靈感魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー インスピレーション)",
        ServerLanguage.Polish: "{item_name} (Magia Inspiracji niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Inspiration Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Inspuraeshun Maegeec",
    }

class MesmerRuneOfMajorFastCasting(AttributeRune):
    id = ItemUpgradeId.OfMajorFastCasting
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Fast Casting",
        ServerLanguage.Korean: "{item_name}(상급 빠른 시전)",
        ServerLanguage.French: "{item_name} (Incantation rapide : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Schnellwirkung",
        ServerLanguage.Italian: "{item_name} Lancio Rapido di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Lanzar conjuros rápido de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 快速施法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ファスト キャスト)",
        ServerLanguage.Polish: "{item_name} (Szybkie Rzucanie Czarów wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Fast Casting",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Faest Caesteeng",
    }

class MesmerRuneOfMajorDominationMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorDominationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Domination Magic",
        ServerLanguage.Korean: "{item_name}(상급 지배)",
        ServerLanguage.French: "{item_name} (Magie de domination : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Beherrschungsmagie",
        ServerLanguage.Italian: "{item_name} Magia del Dominio di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de dominación de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 支配魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ドミネーション)",
        ServerLanguage.Polish: "{item_name} (Magia Dominacji wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Domination Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Dumeenaeshun Maegeec",
    }

class MesmerRuneOfMajorIllusionMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorIllusionMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Illusion Magic",
        ServerLanguage.Korean: "{item_name}(상급 환상)",
        ServerLanguage.French: "{item_name} (Magie de l'illusion : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Illusionsmagie",
        ServerLanguage.Italian: "{item_name} Magia Illusoria di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de ilusión de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 幻術魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー イリュージョン)",
        ServerLanguage.Polish: "{item_name} (Magia Iluzji wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Illusion Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Illooseeun Maegeec",
    }

class MesmerRuneOfMajorInspirationMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorInspirationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Inspiration Magic",
        ServerLanguage.Korean: "{item_name}(상급 영감)",
        ServerLanguage.French: "{item_name} (Magie de l'inspiration : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Inspirationsmagie",
        ServerLanguage.Italian: "{item_name} Magia di Ispirazione di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de inspiración de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 靈感魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー インスピレーション)",
        ServerLanguage.Polish: "{item_name} (Magia Inspiracji wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Inspiration Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Inspuraeshun Maegeec",
    }

class MesmerRuneOfSuperiorFastCasting(AttributeRune):
    id = ItemUpgradeId.OfSuperiorFastCasting
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Fast Casting",
        ServerLanguage.Korean: "{item_name}(고급 빠른 시전)",
        ServerLanguage.French: "{item_name} (Incantation rapide : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Schnellwirkung",
        ServerLanguage.Italian: "{item_name} Lancio Rapido di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Lanzar conjuros rápido de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 快速施法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ファスト キャスト)",
        ServerLanguage.Polish: "{item_name} (Szybkie Rzucanie Czarów najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Fast Casting",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Faest Caesteeng",
    }

class MesmerRuneOfSuperiorDominationMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorDominationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Domination Magic",
        ServerLanguage.Korean: "{item_name}(고급 지배)",
        ServerLanguage.French: "{item_name} (Magie de domination : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Beherrschungsmagie",
        ServerLanguage.Italian: "{item_name} Magia del Dominio di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de dominación de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 支配魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ドミネーション)",
        ServerLanguage.Polish: "{item_name} (Magia Dominacji najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Domination Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Dumeenaeshun Maegeec",
    }

class MesmerRuneOfSuperiorIllusionMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorIllusionMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Illusion Magic",
        ServerLanguage.Korean: "{item_name}(고급 환상)",
        ServerLanguage.French: "{item_name} (Magie de l'illusion : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Illusionsmagie",
        ServerLanguage.Italian: "{item_name} Magia Illusoria di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de ilusión de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 幻術魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア イリュージョン)",
        ServerLanguage.Polish: "{item_name} (Magia Iluzji najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Illusion Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Illooseeun Maegeec",
    }

class MesmerRuneOfSuperiorInspirationMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorInspirationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Inspiration Magic",
        ServerLanguage.Korean: "{item_name}(고급 영감)",
        ServerLanguage.French: "{item_name} (Magie de l'inspiration : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Inspirationsmagie",
        ServerLanguage.Italian: "{item_name} Magia di Ispirazione di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de inspiración de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 靈感魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア インスピレーション)",
        ServerLanguage.Polish: "{item_name} (Magia Inspiracji najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Inspiration Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Inspuraeshun Maegeec",
    }

class UpgradeMinorRuneMesmer(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Mesmer
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneMesmer(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Mesmer
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneMesmer(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Mesmer
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneMesmer(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Mesmer
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneMesmer(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Mesmer
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneMesmer(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Mesmer
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Mesmer

#region Elementalist

class HydromancerInsignia(Insignia):
    id = ItemUpgradeId.Hydromancer
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Hydromancer {item_name}",
        ServerLanguage.Korean: "물의술사의 {item_name}",
        ServerLanguage.French: "{item_name} d'hydromancie",
        ServerLanguage.German: "Hydromanten--{item_name}",
        ServerLanguage.Italian: "{item_name} da Idromante",
        ServerLanguage.Spanish: "{item_name} de hidromante",
        ServerLanguage.TraditionalChinese: "水法師 {item_name}",
        ServerLanguage.Japanese: "ハイドロマンサー {item_name}",
        ServerLanguage.Polish: "{item_name} Hydromanty",
        ServerLanguage.Russian: "Hydromancer {item_name}",
        ServerLanguage.BorkBorkBork: "Hydrumuncer {item_name}",
    }

class GeomancerInsignia(Insignia):
    id = ItemUpgradeId.Geomancer
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Geomancer {item_name}",
        ServerLanguage.Korean: "대지술사의 {item_name}",
        ServerLanguage.French: "{item_name} de géomancie",
        ServerLanguage.German: "Geomanten--{item_name}",
        ServerLanguage.Italian: "{item_name} da Geomante",
        ServerLanguage.Spanish: "{item_name} de geomante",
        ServerLanguage.TraditionalChinese: "地法師 {item_name}",
        ServerLanguage.Japanese: "ジオマンサー {item_name}",
        ServerLanguage.Polish: "{item_name} Geomanty",
        ServerLanguage.Russian: "Geomancer {item_name}",
        ServerLanguage.BorkBorkBork: "Geumuncer {item_name}",
    }

class PyromancerInsignia(Insignia):
    id = ItemUpgradeId.Pyromancer
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Pyromancer {item_name}",
        ServerLanguage.Korean: "화염술사의 {item_name}",
        ServerLanguage.French: "{item_name} de pyromancie",
        ServerLanguage.German: "Pyromanten--{item_name}",
        ServerLanguage.Italian: "{item_name} da Piromante",
        ServerLanguage.Spanish: "{item_name} de piromante",
        ServerLanguage.TraditionalChinese: "火法師 {item_name}",
        ServerLanguage.Japanese: "パイロマンサー {item_name}",
        ServerLanguage.Polish: "{item_name} Piromanty",
        ServerLanguage.Russian: "Pyromancer {item_name}",
        ServerLanguage.BorkBorkBork: "Pyrumuncer {item_name}",
    }

class AeromancerInsignia(Insignia):
    id = ItemUpgradeId.Aeromancer
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Aeromancer {item_name}",
        ServerLanguage.Korean: "바람술사의 {item_name}",
        ServerLanguage.French: "{item_name} d'aéromancie",
        ServerLanguage.German: "Aeromanten--{item_name}",
        ServerLanguage.Italian: "{item_name} da Aeromante",
        ServerLanguage.Spanish: "{item_name} de aeromante",
        ServerLanguage.TraditionalChinese: "風法師 {item_name}",
        ServerLanguage.Japanese: "エアロマンサー {item_name}",
        ServerLanguage.Polish: "{item_name} Aeromanty",
        ServerLanguage.Russian: "Aeromancer {item_name}",
        ServerLanguage.BorkBorkBork: "Aeerumuncer {item_name}",
    }

class PrismaticInsignia(Insignia):
    id = ItemUpgradeId.Prismatic
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Prismatic {item_name}",
        ServerLanguage.Korean: "무지갯빛 {item_name}",
        ServerLanguage.French: "{item_name} prismatique",
        ServerLanguage.German: "Spektral--{item_name}",
        ServerLanguage.Italian: "{item_name} a Prisma",
        ServerLanguage.Spanish: "{item_name} de prismático",
        ServerLanguage.TraditionalChinese: "稜鏡 {item_name}",
        ServerLanguage.Japanese: "プリズマティック {item_name}",
        ServerLanguage.Polish: "{item_name} Pryzmatu",
        ServerLanguage.Russian: "Prismatic {item_name}",
        ServerLanguage.BorkBorkBork: "Preesmaeteec {item_name}",
    }

class ElementalistRuneOfMinorEnergyStorage(AttributeRune):
    id = ItemUpgradeId.OfMinorEnergyStorage
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Energy Storage",
        ServerLanguage.Korean: "{item_name}(하급 에너지 축적)",
        ServerLanguage.French: "{item_name} (Conservation d'énergie : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Energiespeicherung",
        ServerLanguage.Italian: "{item_name} Riserva di Energia di grado minore",
        ServerLanguage.Spanish: "{item_name} (Almacenamiento energía de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 能量儲存 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ストレージ)",
        ServerLanguage.Polish: "{item_name} (Zapas Energii niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Energy Storage",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Inergy Sturaege-a",
    }

class ElementalistRuneOfMinorFireMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorFireMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Fire Magic",
        ServerLanguage.Korean: "{item_name}(하급 불)",
        ServerLanguage.French: "{item_name} (Magie du feu : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Feuermagie",
        ServerLanguage.Italian: "{item_name} Magia del Fuoco di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de fuego de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 火系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ファイア)",
        ServerLanguage.Polish: "{item_name} (Magia Ognia niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Fire Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Fure-a Maegeec",
    }

class ElementalistRuneOfMinorAirMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorAirMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Air Magic",
        ServerLanguage.Korean: "{item_name}(하급 바람)",
        ServerLanguage.French: "{item_name} (Magie de l'air : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Luftmagie",
        ServerLanguage.Italian: "{item_name} Magia dell'Aria di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de aire de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 風系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー エアー)",
        ServerLanguage.Polish: "{item_name} (Magia Powietrza niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Air Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Aeur Maegeec",
    }

class ElementalistRuneOfMinorEarthMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorEarthMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Earth Magic",
        ServerLanguage.Korean: "{item_name}(하급 대지)",
        ServerLanguage.French: "{item_name} (Magie de la terre : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Erdmagie",
        ServerLanguage.Italian: "{item_name} Magia della Terra di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de tierra de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 土系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー アース)",
        ServerLanguage.Polish: "{item_name} (Magia Ziemi niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Earth Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Iaert Maegeec",
    }

class ElementalistRuneOfMinorWaterMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorWaterMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Water Magic",
        ServerLanguage.Korean: "{item_name}(하급 물)",
        ServerLanguage.French: "{item_name} (Magie de l'eau : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Wassermagie",
        ServerLanguage.Italian: "{item_name} Magia dell'Acqua di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de agua de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 水系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ウォーター)",
        ServerLanguage.Polish: "{item_name} (Magia Wody niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Water Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Vaeter Maegeec",
    }

class ElementalistRuneOfMajorEnergyStorage(AttributeRune):
    id = ItemUpgradeId.OfMajorEnergyStorage
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Energy Storage",
        ServerLanguage.Korean: "{item_name}(상급 에너지 축적)",
        ServerLanguage.French: "{item_name} (Conservation d'énergie : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Energiespeicherung",
        ServerLanguage.Italian: "{item_name} Riserva di Energia di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Almacenamiento energía de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 能量儲存 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ストレージ)",
        ServerLanguage.Polish: "{item_name} (Zapas Energii wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Energy Storage",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Inergy Sturaege-a",
    }

class ElementalistRuneOfMajorFireMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorFireMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Fire Magic",
        ServerLanguage.Korean: "{item_name}(상급 불)",
        ServerLanguage.French: "{item_name} (Magie du feu : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Feuermagie",
        ServerLanguage.Italian: "{item_name} Magia del Fuoco di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de fuego de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 火系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ファイア)",
        ServerLanguage.Polish: "{item_name} (Magia Ognia wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Fire Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Fure-a Maegeec",
    }

class ElementalistRuneOfMajorAirMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorAirMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Air Magic",
        ServerLanguage.Korean: "{item_name}(상급 바람)",
        ServerLanguage.French: "{item_name} (Magie de l'air : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Luftmagie",
        ServerLanguage.Italian: "{item_name} Magia dell'Aria di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de aire de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 風系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー エアー)",
        ServerLanguage.Polish: "{item_name} (Magia Powietrza wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Air Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Aeur Maegeec",
    }

class ElementalistRuneOfMajorEarthMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorEarthMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Earth Magic",
        ServerLanguage.Korean: "{item_name}(상급 대지)",
        ServerLanguage.French: "{item_name} (Magie de la terre : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Erdmagie",
        ServerLanguage.Italian: "{item_name} Magia della Terra di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de tierra de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 土系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー アース)",
        ServerLanguage.Polish: "{item_name} (Magia Ziemi wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Earth Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Iaert Maegeec",
    }

class ElementalistRuneOfMajorWaterMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorWaterMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Water Magic",
        ServerLanguage.Korean: "{item_name}(상급 물)",
        ServerLanguage.French: "{item_name} (Magie de l'eau : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Wassermagie",
        ServerLanguage.Italian: "{item_name} Magia dell'Acqua di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de agua de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 水系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ウォーター)",
        ServerLanguage.Polish: "{item_name} (Magia Wody wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Water Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Vaeter Maegeec",
    }

class ElementalistRuneOfSuperiorEnergyStorage(AttributeRune):
    id = ItemUpgradeId.OfSuperiorEnergyStorage
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Energy Storage",
        ServerLanguage.Korean: "{item_name}(고급 에너지 축적)",
        ServerLanguage.French: "{item_name} (Conservation d'énergie : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Energiespeicherung",
        ServerLanguage.Italian: "{item_name} Riserva di Energia di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Almacenamiento energía de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 能量儲存 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ストレージ)",
        ServerLanguage.Polish: "{item_name} (Zapas Energii najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Energy Storage",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Inergy Sturaege-a",
    }

class ElementalistRuneOfSuperiorFireMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorFireMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Fire Magic",
        ServerLanguage.Korean: "{item_name}(고급 불)",
        ServerLanguage.French: "{item_name} (Magie du feu : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Feuermagie",
        ServerLanguage.Italian: "{item_name} Magia del Fuoco di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de fuego de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 火系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ファイア)",
        ServerLanguage.Polish: "{item_name} (Magia Ognia najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Fire Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Fure-a Maegeec",
    }

class ElementalistRuneOfSuperiorAirMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorAirMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Air Magic",
        ServerLanguage.Korean: "{item_name}(고급 바람)",
        ServerLanguage.French: "{item_name} (Magie de l'air : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Luftmagie",
        ServerLanguage.Italian: "{item_name} Magia dell'Aria di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de aire de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 風系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア エアー)",
        ServerLanguage.Polish: "{item_name} (Magia Powietrza najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Air Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Aeur Maegeec",
    }

class ElementalistRuneOfSuperiorEarthMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorEarthMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Earth Magic",
        ServerLanguage.Korean: "{item_name}(고급 대지)",
        ServerLanguage.French: "{item_name} (Magie de la terre : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Erdmagie",
        ServerLanguage.Italian: "{item_name} Magia della Terra di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de tierra de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 土系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア アース)",
        ServerLanguage.Polish: "{item_name} (Magia Ziemi najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Earth Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Iaert Maegeec",
    }

class ElementalistRuneOfSuperiorWaterMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorWaterMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Water Magic",
        ServerLanguage.Korean: "{item_name}(고급 물)",
        ServerLanguage.French: "{item_name} (Magie de l'eau : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Wassermagie",
        ServerLanguage.Italian: "{item_name} Magia dell'Acqua di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de agua de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 水系魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ウォーター)",
        ServerLanguage.Polish: "{item_name} (Magia Wody najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Water Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Vaeter Maegeec",
    }

class UpgradeMinorRuneElementalist(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Elementalist
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneElementalist(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Elementalist
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneElementalist(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Elementalist
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneElementalist(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Elementalist
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneElementalist(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Elementalist
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneElementalist(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Elementalist
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Elementalist

#region Assassin

class VanguardsInsignia(Insignia):
    id = ItemUpgradeId.Vanguards
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Vanguard's {item_name}",
        ServerLanguage.Korean: "선봉대의 {item_name}",
        ServerLanguage.French: "{item_name} de l'avant-garde",
        ServerLanguage.German: "Hauptmann--{item_name}",
        ServerLanguage.Italian: "{item_name} da Avanguardia",
        ServerLanguage.Spanish: "{item_name} de avanzado",
        ServerLanguage.TraditionalChinese: "前鋒 {item_name}",
        ServerLanguage.Japanese: "ヴァンガード {item_name}",
        ServerLanguage.Polish: "{item_name} Awangardy",
        ServerLanguage.Russian: "Vanguard's {item_name}",
        ServerLanguage.BorkBorkBork: "Fungooaerd's {item_name}",
    }

class InfiltratorsInsignia(Insignia):
    id = ItemUpgradeId.Infiltrators
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Infiltrator's {item_name}",
        ServerLanguage.Korean: "침입자의 {item_name}",
        ServerLanguage.French: "{item_name} de l'infiltré",
        ServerLanguage.German: "Eindringlings--{item_name}",
        ServerLanguage.Italian: "{item_name} da Spia",
        ServerLanguage.Spanish: "{item_name} de infiltrado",
        ServerLanguage.TraditionalChinese: "滲透者 {item_name}",
        ServerLanguage.Japanese: "インフィルトレイター {item_name}",
        ServerLanguage.Polish: "{item_name} Infiltratora",
        ServerLanguage.Russian: "Infiltrator's {item_name}",
        ServerLanguage.BorkBorkBork: "Inffeeltraetur's {item_name}",
    }

class SaboteursInsignia(Insignia):
    id = ItemUpgradeId.Saboteurs
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Saboteur's {item_name}",
        ServerLanguage.Korean: "파괴자의 {item_name}",
        ServerLanguage.French: "{item_name} de saboteur",
        ServerLanguage.German: "Saboteur--{item_name}",
        ServerLanguage.Italian: "{item_name} da Sabotatore",
        ServerLanguage.Spanish: "{item_name} de saboteador",
        ServerLanguage.TraditionalChinese: "破壞者 {item_name}",
        ServerLanguage.Japanese: "サボター {item_name}",
        ServerLanguage.Polish: "{item_name} Sabotażysty",
        ServerLanguage.Russian: "Saboteur's {item_name}",
        ServerLanguage.BorkBorkBork: "Saebuteoor's {item_name}",
    }

class NightstalkersInsignia(Insignia):
    id = ItemUpgradeId.Nightstalkers
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Nightstalker's {item_name}",
        ServerLanguage.Korean: "밤추종자의 {item_name}",
        ServerLanguage.French: "{item_name} de traqueur nocturne",
        ServerLanguage.German: "Nachtpirscher--{item_name}",
        ServerLanguage.Italian: "{item_name} da Inseguitore Notturno",
        ServerLanguage.Spanish: "{item_name} de acechador nocturno",
        ServerLanguage.TraditionalChinese: "夜行者 {item_name}",
        ServerLanguage.Japanese: "ナイトストーカー {item_name}",
        ServerLanguage.Polish: "{item_name} Nocnego Tropiciela",
        ServerLanguage.Russian: "Nightstalker's {item_name}",
        ServerLanguage.BorkBorkBork: "Neeghtstaelker's {item_name}",
    }

class AssassinRuneOfMinorCriticalStrikes(AttributeRune):
    id = ItemUpgradeId.OfMinorCriticalStrikes
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Critical Strikes",
        ServerLanguage.Korean: "{item_name}(하급 치명타)",
        ServerLanguage.French: "{item_name} d'(Attaques critiques : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Kritische Stöße",
        ServerLanguage.Italian: "{item_name} Colpi Critici di grado minore",
        ServerLanguage.Spanish: "{item_name} (Impactos críticos de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 致命攻擊 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー クリティカル ストライク)",
        ServerLanguage.Polish: "{item_name} (Trafienia Krytyczne niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Critical Strikes",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Creeteecael Streekes",
    }

class AssassinRuneOfMinorDaggerMastery(AttributeRune):
    id = ItemUpgradeId.OfMinorDaggerMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Dagger Mastery",
        ServerLanguage.Korean: "{item_name}(하급 단검술)",
        ServerLanguage.French: "{item_name} d'(Maîtrise de la dague : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Dolchbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con il Pugnale di grado minore",
        ServerLanguage.Spanish: "{item_name} (Dominio de la daga de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 匕首精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ダガー マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość w Sztyletach niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Dagger Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Daegger Maestery",
    }

class AssassinRuneOfMinorDeadlyArts(AttributeRune):
    id = ItemUpgradeId.OfMinorDeadlyArts
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Deadly Arts",
        ServerLanguage.Korean: "{item_name}(하급 죽음의 기예)",
        ServerLanguage.French: "{item_name} d'(Arts létaux : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Tödliche Künste",
        ServerLanguage.Italian: "{item_name} Arti Letali di grado minore",
        ServerLanguage.Spanish: "{item_name} (Artes mortales de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 暗殺技巧 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー デッドリー アーツ)",
        ServerLanguage.Polish: "{item_name} (Sztuka Śmierci niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Deadly Arts",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Deaedly Aerts",
    }

class AssassinRuneOfMinorShadowArts(AttributeRune):
    id = ItemUpgradeId.OfMinorShadowArts
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Shadow Arts",
        ServerLanguage.Korean: "{item_name}(하급 그림자 기예)",
        ServerLanguage.French: "{item_name} d'(Arts des ombres : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Schattenkünste",
        ServerLanguage.Italian: "{item_name} Arti dell'Ombra di grado minore",
        ServerLanguage.Spanish: "{item_name} (Artes sombrías de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 暗影技巧 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー シャドウ アーツ)",
        ServerLanguage.Polish: "{item_name} (Sztuka Cienia niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Shadow Arts",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Shaedoo Aerts",
    }

class AssassinRuneOfMajorCriticalStrikes(AttributeRune):
    id = ItemUpgradeId.OfMajorCriticalStrikes
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Critical Strikes",
        ServerLanguage.Korean: "{item_name}(상급 치명타)",
        ServerLanguage.French: "{item_name} d'(Attaques critiques : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Kritische Stöße",
        ServerLanguage.Italian: "{item_name} Colpi Critici di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Impactos críticos de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 致命攻擊 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー クリティカル ストライク)",
        ServerLanguage.Polish: "{item_name} (Trafienia Krytyczne wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Critical Strikes",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Creeteecael Streekes",
    }

class AssassinRuneOfMajorDaggerMastery(AttributeRune):
    id = ItemUpgradeId.OfMajorDaggerMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Dagger Mastery",
        ServerLanguage.Korean: "{item_name}(상급 단검술)",
        ServerLanguage.French: "{item_name} d'(Maîtrise de la dague : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Dolchbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con il Pugnale di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Dominio de la daga de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 匕首精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ダガー マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość w Sztyletach wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Dagger Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Daegger Maestery",
    }

class AssassinRuneOfMajorDeadlyArts(AttributeRune):
    id = ItemUpgradeId.OfMajorDeadlyArts
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Deadly Arts",
        ServerLanguage.Korean: "{item_name}(상급 죽음의 기예)",
        ServerLanguage.French: "{item_name} d'(Arts létaux : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Tödliche Künste",
        ServerLanguage.Italian: "{item_name} Arti Letali di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Artes mortales de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 暗殺技巧 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー デッドリー アーツ)",
        ServerLanguage.Polish: "{item_name} (Sztuka Śmierci wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Deadly Arts",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Deaedly Aerts",
    }

class AssassinRuneOfMajorShadowArts(AttributeRune):
    id = ItemUpgradeId.OfMajorShadowArts
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Shadow Arts",
        ServerLanguage.Korean: "{item_name}(상급 그림자 기예)",
        ServerLanguage.French: "{item_name} d'(Arts des ombres : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Schattenkünste",
        ServerLanguage.Italian: "{item_name} Arti dell'Ombra di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Artes sombrías de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 暗影技巧 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー シャドウ アーツ)",
        ServerLanguage.Polish: "{item_name} (Sztuka Cienia wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Shadow Arts",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Shaedoo Aerts",
    }

class AssassinRuneOfSuperiorCriticalStrikes(AttributeRune):
    id = ItemUpgradeId.OfSuperiorCriticalStrikes
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Critical Strikes",
        ServerLanguage.Korean: "{item_name}(고급 치명타)",
        ServerLanguage.French: "{item_name} d'(Attaques critiques : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Kritische Stöße",
        ServerLanguage.Italian: "{item_name} Colpi Critici di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Impactos críticos de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 致命攻擊 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア クリティカル ストライク)",
        ServerLanguage.Polish: "{item_name} (Trafienia Krytyczne najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Critical Strikes",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Creeteecael Streekes",
    }

class AssassinRuneOfSuperiorDaggerMastery(AttributeRune):
    id = ItemUpgradeId.OfSuperiorDaggerMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Dagger Mastery",
        ServerLanguage.Korean: "{item_name}(고급 단검술)",
        ServerLanguage.French: "{item_name} d'(Maîtrise de la dague : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Dolchbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con il Pugnale di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Dominio de la daga de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 匕首精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ダガー マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość w Sztyletach najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Dagger Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Daegger Maestery",
    }

class AssassinRuneOfSuperiorDeadlyArts(AttributeRune):
    id = ItemUpgradeId.OfSuperiorDeadlyArts
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Deadly Arts",
        ServerLanguage.Korean: "{item_name}(고급 죽음의 기예)",
        ServerLanguage.French: "{item_name} d'(Arts létaux : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Tödliche Künste",
        ServerLanguage.Italian: "{item_name} Arti Letali di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Artes mortales de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 暗殺技巧 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア デッドリー アーツ)",
        ServerLanguage.Polish: "{item_name} (Sztuka Śmierci najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Deadly Arts",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Deaedly Aerts",
    }

class AssassinRuneOfSuperiorShadowArts(AttributeRune):
    id = ItemUpgradeId.OfSuperiorShadowArts
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Shadow Arts",
        ServerLanguage.Korean: "{item_name}(고급 그림자 기예)",
        ServerLanguage.French: "{item_name} d'(Arts des ombres : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Schattenkünste",
        ServerLanguage.Italian: "{item_name} Arti dell'Ombra di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Artes sombrías de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 暗影技巧 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア シャドウ アーツ)",
        ServerLanguage.Polish: "{item_name} (Sztuka Cienia najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Shadow Arts",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Shaedoo Aerts",
    }

class UpgradeMinorRuneAssassin(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Assassin
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneAssassin(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Assassin
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneAssassin(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Assassin
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneAssassin(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Assassin
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneAssassin(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Assassin
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneAssassin(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Assassin
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Assassin

#region Ritualist

class ShamansInsignia(Insignia):
    id = ItemUpgradeId.Shamans
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Shaman's {item_name}",
        ServerLanguage.Korean: "주술사의 {item_name}",
        ServerLanguage.French: "{item_name} de chaman",
        ServerLanguage.German: "Schamanen--{item_name}",
        ServerLanguage.Italian: "{item_name} da Sciamano",
        ServerLanguage.Spanish: "{item_name} de chamán",
        ServerLanguage.TraditionalChinese: "巫醫 {item_name}",
        ServerLanguage.Japanese: "シャーマン {item_name}",
        ServerLanguage.Polish: "{item_name} Szamana",
        ServerLanguage.Russian: "Shaman's {item_name}",
        ServerLanguage.BorkBorkBork: "Shaemun's {item_name}",
    }

class GhostForgeInsignia(Insignia):
    id = ItemUpgradeId.GhostForge
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Ghost Forge {item_name}",
        ServerLanguage.Korean: "유령화로의 {item_name}",
        ServerLanguage.French: "{item_name} de la forge du fantôme",
        ServerLanguage.German: "Geisterschmiede--{item_name}",
        ServerLanguage.Italian: "{item_name} della Fucina Spettrale",
        ServerLanguage.Spanish: "{item_name} de fragua fantasma",
        ServerLanguage.TraditionalChinese: "魂鎔 {item_name}",
        ServerLanguage.Japanese: "ゴースト フォージ {item_name}",
        ServerLanguage.Polish: "{item_name} Kuźni Duchów",
        ServerLanguage.Russian: "Ghost Forge {item_name}",
        ServerLanguage.BorkBorkBork: "Ghust Furge-a {item_name}",
    }

class MysticsInsignia(Insignia):
    id = ItemUpgradeId.Mystics
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Mystic's {item_name}",
        ServerLanguage.Korean: "신비술사의 {item_name}",
        ServerLanguage.French: "{item_name} mystique",
        ServerLanguage.German: "Mystiker--{item_name}",
        ServerLanguage.Italian: "{item_name} del Misticismo",
        ServerLanguage.Spanish: "{item_name} de místico",
        ServerLanguage.TraditionalChinese: "祕法 {item_name}",
        ServerLanguage.Japanese: "ミスティック {item_name}",
        ServerLanguage.Polish: "{item_name} Mistyka",
        ServerLanguage.Russian: "Mystic's {item_name}",
        ServerLanguage.BorkBorkBork: "Mysteec's {item_name}",
    }

class RitualistRuneOfMinorChannelingMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorChannelingMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Channeling Magic",
        ServerLanguage.Korean: "{item_name}(하급 마력 증폭)",
        ServerLanguage.French: "{item_name} (Magie de la canalisation : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Kanalisierungsmagie",
        ServerLanguage.Italian: "{item_name} Magia di Incanalamento di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de canalización de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 導引魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー チャネリング)",
        ServerLanguage.Polish: "{item_name} (Magia Połączeń niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Channeling Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Chunneleeng Maegeec",
    }

class RitualistRuneOfMinorRestorationMagic(AttributeRune):
    id = ItemUpgradeId.OfMinorRestorationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Restoration Magic",
        ServerLanguage.Korean: "{item_name}(하급 마력 회복)",
        ServerLanguage.French: "{item_name} (Magie de restauration : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Wiederherstellungsmagie",
        ServerLanguage.Italian: "{item_name} Magia del Ripristino di grado minore",
        ServerLanguage.Spanish: "{item_name} (Magia de restauración de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 復原魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー レストレーション)",
        ServerLanguage.Polish: "{item_name} (Magia Odnowy niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Restoration Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Resturaeshun Maegeec",
    }

class RitualistRuneOfMinorCommuning(AttributeRune):
    id = ItemUpgradeId.OfMinorCommuning
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Communing",
        ServerLanguage.Korean: "{item_name}(하급 교감)",
        ServerLanguage.French: "{item_name} (Communion : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Zwiesprache",
        ServerLanguage.Italian: "{item_name} Raccoglimento di grado minore",
        ServerLanguage.Spanish: "{item_name} (Comunión de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 神諭 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー コミューン)",
        ServerLanguage.Polish: "{item_name} (Zjednoczenie niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Communing",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Cummooneeng",
    }

class RitualistRuneOfMinorSpawningPower(AttributeRune):
    id = ItemUpgradeId.OfMinorSpawningPower
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Spawning Power",
        ServerLanguage.Korean: "{item_name}(하급 생성)",
        ServerLanguage.French: "{item_name} (Puissance de l'Invocation : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Macht des Herbeirufens",
        ServerLanguage.Italian: "{item_name} Riti Sacrificali di grado minore",
        ServerLanguage.Spanish: "{item_name} (Engendramiento de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 召喚 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー スポーン パワー)",
        ServerLanguage.Polish: "{item_name} (Moc Przywoływania niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Spawning Power",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Spaevneeng Pooer",
    }

class RitualistRuneOfMajorChannelingMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorChannelingMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Channeling Magic",
        ServerLanguage.Korean: "{item_name}(상급 마력 증폭)",
        ServerLanguage.French: "{item_name} (Magie de la canalisation : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Kanalisierungsmagie",
        ServerLanguage.Italian: "{item_name} Magia di Incanalamento di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de canalización de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 導引魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー チャネリング)",
        ServerLanguage.Polish: "{item_name} (Magia Połączeń wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Channeling Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Chunneleeng Maegeec",
    }

class RitualistRuneOfMajorRestorationMagic(AttributeRune):
    id = ItemUpgradeId.OfMajorRestorationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Restoration Magic",
        ServerLanguage.Korean: "{item_name}(상급 마력 회복)",
        ServerLanguage.French: "{item_name} (Magie de restauration : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Wiederherstellungsmagie",
        ServerLanguage.Italian: "{item_name} Magia del Ripristino di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Magia de restauración de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 復原魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー レストレーション)",
        ServerLanguage.Polish: "{item_name} (Magia Odnowy wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Restoration Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Resturaeshun Maegeec",
    }

class RitualistRuneOfMajorCommuning(AttributeRune):
    id = ItemUpgradeId.OfMajorCommuning
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Communing",
        ServerLanguage.Korean: "{item_name}(상급 교감)",
        ServerLanguage.French: "{item_name} (Communion : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Zwiesprache",
        ServerLanguage.Italian: "{item_name} Raccoglimento di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Comunión de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 神諭 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー コミューン)",
        ServerLanguage.Polish: "{item_name} (Zjednoczenie wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Communing",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Cummooneeng",
    }

class RitualistRuneOfMajorSpawningPower(AttributeRune):
    id = ItemUpgradeId.OfMajorSpawningPower
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Spawning Power",
        ServerLanguage.Korean: "{item_name}(상급 생성)",
        ServerLanguage.French: "{item_name} (Puissance de l'Invocation : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Macht des Herbeirufens",
        ServerLanguage.Italian: "{item_name} Riti Sacrificali di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Engendramiento de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 召喚 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー スポーン パワー)",
        ServerLanguage.Polish: "{item_name} (Moc Przywoływania wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Spawning Power",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Spaevneeng Pooer",
    }

class RitualistRuneOfSuperiorChannelingMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorChannelingMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Channeling Magic",
        ServerLanguage.Korean: "{item_name}(고급 마력 증폭)",
        ServerLanguage.French: "{item_name} (Magie de la canalisation : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Kanalisierungsmagie",
        ServerLanguage.Italian: "{item_name} Magia di Incanalamento di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de canalización de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 導引魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア チャネリング)",
        ServerLanguage.Polish: "{item_name} (Magia Połączeń najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Channeling Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Chunneleeng Maegeec",
    }

class RitualistRuneOfSuperiorRestorationMagic(AttributeRune):
    id = ItemUpgradeId.OfSuperiorRestorationMagic
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Restoration Magic",
        ServerLanguage.Korean: "{item_name}(고급 마력 회복)",
        ServerLanguage.French: "{item_name} (Magie de restauration : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Wiederherstellungsmagie",
        ServerLanguage.Italian: "{item_name} Magia del Ripristino di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Magia de restauración de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 復原魔法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア レストレーション)",
        ServerLanguage.Polish: "{item_name} (Magia Odnowy najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Restoration Magic",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Resturaeshun Maegeec",
    }

class RitualistRuneOfSuperiorCommuning(AttributeRune):
    id = ItemUpgradeId.OfSuperiorCommuning
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Communing",
        ServerLanguage.Korean: "{item_name}(고급 교감)",
        ServerLanguage.French: "{item_name} (Communion : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Zwiesprache",
        ServerLanguage.Italian: "{item_name} Raccoglimento di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Comunión de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 神諭 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア コミューン)",
        ServerLanguage.Polish: "{item_name} (Zjednoczenie najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Communing",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Cummooneeng",
    }

class RitualistRuneOfSuperiorSpawningPower(AttributeRune):
    id = ItemUpgradeId.OfSuperiorSpawningPower
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Spawning Power",
        ServerLanguage.Korean: "{item_name}(고급 생성)",
        ServerLanguage.French: "{item_name} (Puissance de l'Invocation : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Macht des Herbeirufens",
        ServerLanguage.Italian: "{item_name} Riti Sacrificali di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Engendramiento de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 召喚 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア スポーン パワー)",
        ServerLanguage.Polish: "{item_name} (Moc Przywoływania najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Spawning Power",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Spaevneeng Pooer",
    }

class UpgradeMinorRuneRitualist(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Ritualist
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneRitualist(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Ritualist
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneRitualist(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Ritualist
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneRitualist(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Ritualist
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneRitualist(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Ritualist
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneRitualist(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Ritualist
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Ritualist

#region Dervish

class WindwalkerInsignia(Insignia):
    id = ItemUpgradeId.Windwalker
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Windwalker {item_name}",
        ServerLanguage.Korean: "여행가의 {item_name}",
        ServerLanguage.French: "{item_name} du Marche-vent",
        ServerLanguage.German: "Windläufer--{item_name}",
        ServerLanguage.Italian: "{item_name} da Camminatore nel Vento",
        ServerLanguage.Spanish: "{item_name} de caminante del viento",
        ServerLanguage.TraditionalChinese: "風行者 {item_name}",
        ServerLanguage.Japanese: "ウインドウォーカー {item_name}",
        ServerLanguage.Polish: "{item_name} Włóczywiatru",
        ServerLanguage.Russian: "Windwalker {item_name}",
        ServerLanguage.BorkBorkBork: "Veendvaelker {item_name}",
    }

class ForsakenInsignia(Insignia):
    id = ItemUpgradeId.Forsaken
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Forsaken {item_name}",
        ServerLanguage.Korean: "고독한 {item_name}",
        ServerLanguage.French: "{item_name} de l'oubli",
        ServerLanguage.German: "Verlassenen--{item_name}",
        ServerLanguage.Italian: "{item_name} da Abbandonato",
        ServerLanguage.Spanish: "{item_name} de abandonado",
        ServerLanguage.TraditionalChinese: "背離 {item_name}",
        ServerLanguage.Japanese: "フォーセイク {item_name}",
        ServerLanguage.Polish: "{item_name} Zapomnienia",
        ServerLanguage.Russian: "Forsaken {item_name}",
        ServerLanguage.BorkBorkBork: "Fursaekee {item_name}",
    }

class DervishRuneOfMinorMysticism(AttributeRune):
    id = ItemUpgradeId.OfMinorMysticism
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Mysticism",
        ServerLanguage.Korean: "{item_name}(하급 신비주의)",
        ServerLanguage.French: "{item_name} (Mysticisme : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Mystik",
        ServerLanguage.Italian: "{item_name} Misticismo di grado minore",
        ServerLanguage.Spanish: "{item_name} (Misticismo de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 祕法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ミスティシズム)",
        ServerLanguage.Polish: "{item_name} (Mistycyzm niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Mysticism",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Mysteeceesm",
    }

class DervishRuneOfMinorEarthPrayers(AttributeRune):
    id = ItemUpgradeId.OfMinorEarthPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Earth Prayers",
        ServerLanguage.Korean: "{item_name}(하급 대지의 기도)",
        ServerLanguage.French: "{item_name} (Prières de la Terre : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Erdgebete",
        ServerLanguage.Italian: "{item_name} Preghiere della Terra di grado minore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de tierra de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 地之祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー アース プレイヤー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ziemi niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Earth Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Iaert Praeyers",
    }

class DervishRuneOfMinorScytheMastery(AttributeRune):
    id = ItemUpgradeId.OfMinorScytheMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Scythe Mastery",
        ServerLanguage.Korean: "{item_name}(하급 사이드술)",
        ServerLanguage.French: "{item_name} (Maîtrise de la faux : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Sensenbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con la Falce di grado minore",
        ServerLanguage.Spanish: "{item_name} (Dominio de la guadaña de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 鐮刀精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー サイズ マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość w Kosach niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Scythe Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Scyzee Maestery",
    }

class DervishRuneOfMinorWindPrayers(AttributeRune):
    id = ItemUpgradeId.OfMinorWindPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Wind Prayers",
        ServerLanguage.Korean: "{item_name}(하급 바람의 기도)",
        ServerLanguage.French: "{item_name} (Prières du Vent : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Windgebete",
        ServerLanguage.Italian: "{item_name} Preghiere del Vento di grado minore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de viento de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 風之祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー ウインド プレイヤー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Wiatru niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Wind Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Veend Praeyers",
    }

class DervishRuneOfMajorMysticism(AttributeRune):
    id = ItemUpgradeId.OfMajorMysticism
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Mysticism",
        ServerLanguage.Korean: "{item_name}(상급 신비주의)",
        ServerLanguage.French: "{item_name} (Mysticisme : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Mystik",
        ServerLanguage.Italian: "{item_name} Misticismo di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Misticismo de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 祕法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ミスティシズム)",
        ServerLanguage.Polish: "{item_name} (Mistycyzm wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Mysticism",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Mysteeceesm",
    }

class DervishRuneOfMajorEarthPrayers(AttributeRune):
    id = ItemUpgradeId.OfMajorEarthPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Earth Prayers",
        ServerLanguage.Korean: "{item_name}(상급 대지의 기도)",
        ServerLanguage.French: "{item_name} (Prières de la Terre : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Erdgebete",
        ServerLanguage.Italian: "{item_name} Preghiere della Terra di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de tierra de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 地之祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー アース プレイヤー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ziemi wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Earth Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Iaert Praeyers",
    }

class DervishRuneOfMajorScytheMastery(AttributeRune):
    id = ItemUpgradeId.OfMajorScytheMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Scythe Mastery",
        ServerLanguage.Korean: "{item_name}(상급 사이드술)",
        ServerLanguage.French: "{item_name} (Maîtrise de la faux : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Sensenbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con la Falce di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Dominio de la guadaña de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 鐮刀精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー サイズ マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość w Kosach wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Scythe Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Scyzee Maestery",
    }

class DervishRuneOfMajorWindPrayers(AttributeRune):
    id = ItemUpgradeId.OfMajorWindPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Wind Prayers",
        ServerLanguage.Korean: "{item_name}(상급 바람의 기도)",
        ServerLanguage.French: "{item_name} (Prières du Vent : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Windgebete",
        ServerLanguage.Italian: "{item_name} Preghiere del Vento di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Plegarias de viento de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 風之祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー ウインド プレイヤー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Wiatru wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Wind Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Veend Praeyers",
    }

class DervishRuneOfSuperiorMysticism(AttributeRune):
    id = ItemUpgradeId.OfSuperiorMysticism
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Mysticism",
        ServerLanguage.Korean: "{item_name}(고급 신비주의)",
        ServerLanguage.French: "{item_name} (Mysticisme : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Mystik",
        ServerLanguage.Italian: "{item_name} Misticismo di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Misticismo de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 祕法 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ミスティシズム)",
        ServerLanguage.Polish: "{item_name} (Mistycyzm najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Mysticism",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Mysteeceesm",
    }

class DervishRuneOfSuperiorEarthPrayers(AttributeRune):
    id = ItemUpgradeId.OfSuperiorEarthPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Earth Prayers",
        ServerLanguage.Korean: "{item_name}(고급 대지의 기도)",
        ServerLanguage.French: "{item_name} (Prières de la Terre : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Erdgebete",
        ServerLanguage.Italian: "{item_name} Preghiere della Terra di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Plegarias de tierra de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 地之祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア アース プレイヤー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Ziemi najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Earth Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Iaert Praeyers",
    }

class DervishRuneOfSuperiorScytheMastery(AttributeRune):
    id = ItemUpgradeId.OfSuperiorScytheMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Scythe Mastery",
        ServerLanguage.Korean: "{item_name}(고급 사이드술)",
        ServerLanguage.French: "{item_name} (Maîtrise de la faux : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Sensenbeherrschung",
        ServerLanguage.Italian: "{item_name} Abilità con la Falce di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Dominio de la guadaña de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 鐮刀精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア サイズ マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość w Kosach najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Scythe Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Scyzee Maestery",
    }

class DervishRuneOfSuperiorWindPrayers(AttributeRune):
    id = ItemUpgradeId.OfSuperiorWindPrayers
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Wind Prayers",
        ServerLanguage.Korean: "{item_name}(고급 바람의 기도)",
        ServerLanguage.French: "{item_name} (Prières du Vent : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Windgebete",
        ServerLanguage.Italian: "{item_name} Preghiere del Vento di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Plegarias de viento de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 風之祈禱 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア ウインド プレイヤー)",
        ServerLanguage.Polish: "{item_name} (Modlitwy Wiatru najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Wind Prayers",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Veend Praeyers",
    }

class UpgradeMinorRuneDervish(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Dervish
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneDervish(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Dervish
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneDervish(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Dervish
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneDervish(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Dervish
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneDervish(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Dervish
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneDervish(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Dervish
    mod_type = ItemUpgradeType.AppliesToRune

#endregion Dervish

#region Paragon

class CenturionsInsignia(Insignia):
    id = ItemUpgradeId.Centurions
    mod_type = ItemUpgradeType.Prefix

    names = {
        ServerLanguage.English: "Centurion's {item_name}",
        ServerLanguage.Korean: "백부장의 {item_name}",
        ServerLanguage.French: "{item_name} du centurion",
        ServerLanguage.German: "Zenturio--{item_name}",
        ServerLanguage.Italian: "{item_name} da Centurione",
        ServerLanguage.Spanish: "{item_name} de centurión",
        ServerLanguage.TraditionalChinese: "百夫長 {item_name}",
        ServerLanguage.Japanese: "センチュリオン {item_name}",
        ServerLanguage.Polish: "{item_name} Centuriona",
        ServerLanguage.Russian: "Centurion's {item_name}",
        ServerLanguage.BorkBorkBork: "Centooreeun's {item_name}",
    }

class ParagonRuneOfMinorLeadership(AttributeRune):
    id = ItemUpgradeId.OfMinorLeadership
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Leadership",
        ServerLanguage.Korean: "{item_name}(하급 리더십)",
        ServerLanguage.French: "{item_name} (Charisme : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Führung",
        ServerLanguage.Italian: "{item_name} del Leadership di grado minore",
        ServerLanguage.Spanish: "{item_name} (Liderazgo de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 領導 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー リーダーシップ)",
        ServerLanguage.Polish: "{item_name} (Przywództwo niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Leadership",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Leaedersheep",
    }

class ParagonRuneOfMinorMotivation(AttributeRune):
    id = ItemUpgradeId.OfMinorMotivation
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Motivation",
        ServerLanguage.Korean: "{item_name}(하급 격려)",
        ServerLanguage.French: "{item_name} (Motivation : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Motivation",
        ServerLanguage.Italian: "{item_name} del Motivazione di grado minore",
        ServerLanguage.Spanish: "{item_name} (Motivación de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 激勵 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー モチベーション)",
        ServerLanguage.Polish: "{item_name} (Motywacja niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Motivation",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Muteefaeshun",
    }

class ParagonRuneOfMinorCommand(AttributeRune):
    id = ItemUpgradeId.OfMinorCommand
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Command",
        ServerLanguage.Korean: "{item_name}(하급 통솔)",
        ServerLanguage.French: "{item_name} (Commandement : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Befehlsgewalt",
        ServerLanguage.Italian: "{item_name} del Comando di grado minore",
        ServerLanguage.Spanish: "{item_name} (Mando de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 命令 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー コマンド)",
        ServerLanguage.Polish: "{item_name} (Rozkazy niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Command",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Cummund",
    }

class ParagonRuneOfMinorSpearMastery(AttributeRune):
    id = ItemUpgradeId.OfMinorSpearMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue

    names = {
        ServerLanguage.English: "{item_name} of Minor Spear Mastery",
        ServerLanguage.Korean: "{item_name}(하급 창술)",
        ServerLanguage.French: "{item_name} (Maîtrise du javelot : bonus mineur)",
        ServerLanguage.German: "{item_name} d. kleineren Speerbeherrschung",
        ServerLanguage.Italian: "{item_name} del Abilità con la Lancia di grado minore",
        ServerLanguage.Spanish: "{item_name} (Dominio de la lanza de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 矛術精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (マイナー スピア マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość we Włóczniach niższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Minor Spear Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Meenur Speaer Maestery",
    }

class ParagonRuneOfMajorLeadership(AttributeRune):
    id = ItemUpgradeId.OfMajorLeadership
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Leadership",
        ServerLanguage.Korean: "{item_name}(상급 리더십)",
        ServerLanguage.French: "{item_name} (Charisme : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Führung",
        ServerLanguage.Italian: "{item_name} del Leadership di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Liderazgo de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 領導 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー リーダーシップ)",
        ServerLanguage.Polish: "{item_name} (Przywództwo wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Leadership",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Leaedersheep",
    }

class ParagonRuneOfMajorMotivation(AttributeRune):
    id = ItemUpgradeId.OfMajorMotivation
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Motivation",
        ServerLanguage.Korean: "{item_name}(상급 격려)",
        ServerLanguage.French: "{item_name} (Motivation : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Motivation",
        ServerLanguage.Italian: "{item_name} del Motivazione di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Motivación de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 激勵 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー モチベーション)",
        ServerLanguage.Polish: "{item_name} (Motywacja wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Motivation",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Muteefaeshun",
    }

class ParagonRuneOfMajorCommand(AttributeRune):
    id = ItemUpgradeId.OfMajorCommand
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Command",
        ServerLanguage.Korean: "{item_name}(상급 통솔)",
        ServerLanguage.French: "{item_name} (Commandement : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Befehlsgewalt",
        ServerLanguage.Italian: "{item_name} del Comando di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Mando de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 命令 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー コマンド)",
        ServerLanguage.Polish: "{item_name} (Rozkazy wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Command",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Cummund",
    }

class ParagonRuneOfMajorSpearMastery(AttributeRune):
    id = ItemUpgradeId.OfMajorSpearMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Major Spear Mastery",
        ServerLanguage.Korean: "{item_name}(상급 창술)",
        ServerLanguage.French: "{item_name} (Maîtrise du javelot : bonus majeur)",
        ServerLanguage.German: "{item_name} d. hohen Speerbeherrschung",
        ServerLanguage.Italian: "{item_name} del Abilità con la Lancia di grado maggiore",
        ServerLanguage.Spanish: "{item_name} (Dominio de la lanza de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 矛術精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (メジャー スピア マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość we Włóczniach wyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Major Spear Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Maejur Speaer Maestery",
    }

class ParagonRuneOfSuperiorLeadership(AttributeRune):
    id = ItemUpgradeId.OfSuperiorLeadership
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Leadership",
        ServerLanguage.Korean: "{item_name}(고급 리더십)",
        ServerLanguage.French: "{item_name} (Charisme : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Führung",
        ServerLanguage.Italian: "{item_name} del Leadership di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Liderazgo de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 領導 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア リーダーシップ)",
        ServerLanguage.Polish: "{item_name} (Przywództwo najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Leadership",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Leaedersheep",
    }

class ParagonRuneOfSuperiorMotivation(AttributeRune):
    id = ItemUpgradeId.OfSuperiorMotivation
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Motivation",
        ServerLanguage.Korean: "{item_name}(고급 격려)",
        ServerLanguage.French: "{item_name} (Motivation : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Motivation",
        ServerLanguage.Italian: "{item_name} del Motivazione di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Motivación de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 激勵 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア モチベーション)",
        ServerLanguage.Polish: "{item_name} (Motywacja najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Motivation",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Muteefaeshun",
    }

class ParagonRuneOfSuperiorCommand(AttributeRune):
    id = ItemUpgradeId.OfSuperiorCommand
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Command",
        ServerLanguage.Korean: "{item_name}(고급 통솔)",
        ServerLanguage.French: "{item_name} (Commandement : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Befehlsgewalt",
        ServerLanguage.Italian: "{item_name} del Comando di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Mando de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 命令 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア コマンド)",
        ServerLanguage.Polish: "{item_name} (Rozkazy najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Command",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Cummund",
    }

class ParagonRuneOfSuperiorSpearMastery(AttributeRune):
    id = ItemUpgradeId.OfSuperiorSpearMastery
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

    names = {
        ServerLanguage.English: "{item_name} of Superior Spear Mastery",
        ServerLanguage.Korean: "{item_name}(고급 창술)",
        ServerLanguage.French: "{item_name} (Maîtrise du javelot : bonus supérieur)",
        ServerLanguage.German: "{item_name} d. überlegenen Speerbeherrschung",
        ServerLanguage.Italian: "{item_name} del Abilità con la Lancia di grado supremo",
        ServerLanguage.Spanish: "{item_name} (Dominio de la lanza de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 矛術精通 {item_name}",
        ServerLanguage.Japanese: "{item_name} (スーペリア スピア マスタリー)",
        ServerLanguage.Polish: "{item_name} (Biegłość we Włóczniach najwyższego poziomu)",
        ServerLanguage.Russian: "{item_name} of Superior Spear Mastery",
        ServerLanguage.BorkBorkBork: "{item_name} ooff Soopereeur Speaer Maestery",
    }

class UpgradeMinorRuneParagon(Upgrade):
    id = ItemUpgradeId.UpgradeMinorRune_Paragon
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeMajorRuneParagon(Upgrade):
    id = ItemUpgradeId.UpgradeMajorRune_Paragon
    mod_type = ItemUpgradeType.UpgradeRune

class UpgradeSuperiorRuneParagon(Upgrade):
    id = ItemUpgradeId.UpgradeSuperiorRune_Paragon
    mod_type = ItemUpgradeType.UpgradeRune

class AppliesToMinorRuneParagon(Upgrade):
    id = ItemUpgradeId.AppliesToMinorRune_Paragon
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToMajorRuneParagon(Upgrade):
    id = ItemUpgradeId.AppliesToMajorRune_Paragon
    mod_type = ItemUpgradeType.AppliesToRune

class AppliesToSuperiorRuneParagon(Upgrade):
    id = ItemUpgradeId.AppliesToSuperiorRune_Paragon
    mod_type = ItemUpgradeType.AppliesToRune

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
    
    WarriorRuneOfMinorAbsorption,
    WarriorRuneOfMinorTactics,
    WarriorRuneOfMinorStrength,
    WarriorRuneOfMinorAxeMastery,
    WarriorRuneOfMinorHammerMastery,
    WarriorRuneOfMinorSwordsmanship,
    WarriorRuneOfMajorAbsorption,
    WarriorRuneOfMajorTactics,
    WarriorRuneOfMajorStrength,
    WarriorRuneOfMajorAxeMastery,
    WarriorRuneOfMajorHammerMastery,
    WarriorRuneOfMajorSwordsmanship,
    WarriorRuneOfSuperiorAbsorption,
    WarriorRuneOfSuperiorTactics,
    WarriorRuneOfSuperiorStrength,
    WarriorRuneOfSuperiorAxeMastery,
    WarriorRuneOfSuperiorHammerMastery,
    WarriorRuneOfSuperiorSwordsmanship,
    
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
    
    RangerRuneOfMinorWildernessSurvival,
    RangerRuneOfMinorExpertise,
    RangerRuneOfMinorBeastMastery,
    RangerRuneOfMinorMarksmanship,
    RangerRuneOfMajorWildernessSurvival,
    RangerRuneOfMajorExpertise,
    RangerRuneOfMajorBeastMastery,
    RangerRuneOfMajorMarksmanship,
    RangerRuneOfSuperiorWildernessSurvival,
    RangerRuneOfSuperiorExpertise,
    RangerRuneOfSuperiorBeastMastery,
    RangerRuneOfSuperiorMarksmanship,
    
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
    
    MonkRuneOfMinorHealingPrayers,
    MonkRuneOfMinorSmitingPrayers,
    MonkRuneOfMinorProtectionPrayers,
    MonkRuneOfMinorDivineFavor,
    MonkRuneOfMajorHealingPrayers,
    MonkRuneOfMajorSmitingPrayers,
    MonkRuneOfMajorProtectionPrayers,
    MonkRuneOfMajorDivineFavor,
    MonkRuneOfSuperiorHealingPrayers,
    MonkRuneOfSuperiorSmitingPrayers,
    MonkRuneOfSuperiorProtectionPrayers,
    MonkRuneOfSuperiorDivineFavor,
    
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
    NecromancerRuneOfMinorBloodMagic,
    NecromancerRuneOfMinorDeathMagic,
    NecromancerRuneOfMinorCurses,
    NecromancerRuneOfMinorSoulReaping,
    NecromancerRuneOfMajorBloodMagic,
    NecromancerRuneOfMajorDeathMagic,
    NecromancerRuneOfMajorCurses,
    NecromancerRuneOfMajorSoulReaping,
    NecromancerRuneOfSuperiorBloodMagic,
    NecromancerRuneOfSuperiorDeathMagic,
    NecromancerRuneOfSuperiorCurses,
    NecromancerRuneOfSuperiorSoulReaping,
    
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
    
    MesmerRuneOfMinorFastCasting,
    MesmerRuneOfMinorDominationMagic,
    MesmerRuneOfMinorIllusionMagic,
    MesmerRuneOfMinorInspirationMagic,
    MesmerRuneOfMajorFastCasting,
    MesmerRuneOfMajorDominationMagic,
    MesmerRuneOfMajorIllusionMagic,
    MesmerRuneOfMajorInspirationMagic,
    MesmerRuneOfSuperiorFastCasting,
    MesmerRuneOfSuperiorDominationMagic,
    MesmerRuneOfSuperiorIllusionMagic,
    MesmerRuneOfSuperiorInspirationMagic,
    
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
    
    ElementalistRuneOfMinorEnergyStorage,
    ElementalistRuneOfMinorFireMagic,
    ElementalistRuneOfMinorAirMagic,
    ElementalistRuneOfMinorEarthMagic,
    ElementalistRuneOfMinorWaterMagic,
    ElementalistRuneOfMajorEnergyStorage,
    ElementalistRuneOfMajorFireMagic,
    ElementalistRuneOfMajorAirMagic,
    ElementalistRuneOfMajorEarthMagic,
    ElementalistRuneOfMajorWaterMagic,
    ElementalistRuneOfSuperiorEnergyStorage,
    ElementalistRuneOfSuperiorFireMagic,
    ElementalistRuneOfSuperiorAirMagic,
    ElementalistRuneOfSuperiorEarthMagic,
    ElementalistRuneOfSuperiorWaterMagic,
    
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
    
    AssassinRuneOfMinorCriticalStrikes,
    AssassinRuneOfMinorDaggerMastery,
    AssassinRuneOfMinorDeadlyArts,
    AssassinRuneOfMinorShadowArts,
    AssassinRuneOfMajorCriticalStrikes,
    AssassinRuneOfMajorDaggerMastery,
    AssassinRuneOfMajorDeadlyArts,
    AssassinRuneOfMajorShadowArts,
    AssassinRuneOfSuperiorCriticalStrikes,
    AssassinRuneOfSuperiorDaggerMastery,
    AssassinRuneOfSuperiorDeadlyArts,
    AssassinRuneOfSuperiorShadowArts,
    
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
    
    RitualistRuneOfMinorChannelingMagic,
    RitualistRuneOfMinorRestorationMagic,
    RitualistRuneOfMinorCommuning,
    RitualistRuneOfMinorSpawningPower,
    RitualistRuneOfMajorChannelingMagic,
    RitualistRuneOfMajorRestorationMagic,
    RitualistRuneOfMajorCommuning,
    RitualistRuneOfMajorSpawningPower,
    RitualistRuneOfSuperiorChannelingMagic,
    RitualistRuneOfSuperiorRestorationMagic,
    RitualistRuneOfSuperiorCommuning,
    RitualistRuneOfSuperiorSpawningPower,
    
    UpgradeMinorRuneRitualist,
    UpgradeMajorRuneRitualist,
    UpgradeSuperiorRuneRitualist,
    AppliesToMinorRuneRitualist,
    AppliesToMajorRuneRitualist,
    AppliesToSuperiorRuneRitualist,
    
    # Dervish
    WindwalkerInsignia,
    ForsakenInsignia,
    
    DervishRuneOfMinorMysticism,
    DervishRuneOfMinorEarthPrayers,
    DervishRuneOfMinorScytheMastery,
    DervishRuneOfMinorWindPrayers,
    DervishRuneOfMajorMysticism,
    DervishRuneOfMajorEarthPrayers,
    DervishRuneOfMajorScytheMastery,
    DervishRuneOfMajorWindPrayers,
    DervishRuneOfSuperiorMysticism,
    DervishRuneOfSuperiorEarthPrayers,
    DervishRuneOfSuperiorScytheMastery,
    DervishRuneOfSuperiorWindPrayers,
    
    UpgradeMinorRuneDervish,
    UpgradeMajorRuneDervish,
    UpgradeSuperiorRuneDervish,
    AppliesToMinorRuneDervish,
    AppliesToMajorRuneDervish,
    AppliesToSuperiorRuneDervish,
    
    # Paragon
    CenturionsInsignia,
    
    ParagonRuneOfMinorLeadership,
    ParagonRuneOfMinorMotivation,
    ParagonRuneOfMinorCommand,
    ParagonRuneOfMinorSpearMastery,
    ParagonRuneOfMajorLeadership,
    ParagonRuneOfMajorMotivation,
    ParagonRuneOfMajorCommand,
    ParagonRuneOfMajorSpearMastery,
    ParagonRuneOfSuperiorLeadership,
    ParagonRuneOfSuperiorMotivation,
    ParagonRuneOfSuperiorCommand,
    ParagonRuneOfSuperiorSpearMastery,   
    
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

