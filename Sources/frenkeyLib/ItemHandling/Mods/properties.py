import re
from typing import TYPE_CHECKING
from dataclasses import InitVar, dataclass, field
import typing
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, Reduced_Ailment
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.native_src.internals import string_table
from Sources.frenkeyLib.ItemHandling.Mods.decoded_modifier import DecodedModifier
from Sources.frenkeyLib.ItemHandling.Mods.types import ItemBaneSpecies, ItemUpgradeId
from Sources.frenkeyLib.ItemHandling.encoded_strings import EncodedStrings

if TYPE_CHECKING:
    from Sources.frenkeyLib.ItemHandling.Mods.upgrades import Upgrade

ITEM_BASIC = bytes([0x2, 0x0, 0x3B, 0xA, 0xA, 0x1]) #item type, also white
ITEM_BONUS = bytes([0x2, 0x0, 0x3C, 0xA, 0xA, 0x1]) #bonus text, also blue
ITEM_COMMON = bytes([0x2, 0x0, 0x3D, 0xA, 0xA, 0x1]) #white
ITEM_DULL = bytes([0x2, 0x0, 0x3E, 0xA, 0xA, 0x1]) #grey for conditions and other less important info
ITEM_ENHANCE = bytes([0x2, 0x0, 0x3F, 0xA, 0xA, 0x1]) #blue
ITEM_RARE = bytes([0x2, 0x0, 0x40, 0xA, 0xA, 0x1]) #gold
ITEM_RESTRICT = bytes([0x2, 0x0, 0x41, 0xA, 0xA, 0x1])
ITEM_UNCOMMON = bytes([0x2, 0x0, 0x42, 0xA, 0xA, 0x1]) #purple
ITEM_UNIQUE = bytes([0x2, 0x0, 0x43, 0xA, 0xA, 0x1]) #green

PLUS_NUM_TEMPLATE = bytes([0x84, 0xA, 0xA, 0x1])
PLUS_PERCENT_TEMPLATE = bytes([0x85, 0xA, 0xA, 0x1])
COLON_NUM_TEMPLATE = bytes([0x86, 0xA, 0xA, 0x1])
MINUS_NUM_TEMPLATE = bytes([0x7E, 0xA, 0xA, 0x1])
CHANCE_TEMPLATE = bytes([0x87, 0xA, 0xA, 0x1])
REQUIRES_TEMPLATE = bytes([0xA9, 0xA, 0xA, 0x1])

ARMOR_BYTES = bytes([0x44, 0xA, 0x1, 0x0])
DAMAGE_BYTES = bytes([0x4C, 0xA, 0x1, 0x0])
ENERGY_BYTES = bytes([0x17, 0x9, 0x1, 0x0])
ENERGY_RECOVERY_BYTES = bytes([0x18, 0x9, 0x1, 0x0])
ENERGY_REGEN_BYTES = bytes([0x51, 0xA, 0x1, 0x0])
ENERGY_GAIN_ON_HIT_BYTES = bytes([0x50, 0xA, 0x1, 0x0])
HEALTH_BYTES = bytes([0x52, 0xA, 0x1, 0x0])
HEALTH_REGEN_BYTES = bytes([0x53, 0xA, 0x1, 0x0])
LIFE_DRAINING_BYTES = bytes([0x54, 0xA, 0x1, 0x0])
DOUBLE_ADRENALINE_BYTES = bytes([0x57, 0xA, 0x1, 0x0])
HALVES_CASTING_BYTES = bytes([0x80, 0xA, 0xA, 0x1, 0x47, 0xA, 0x1, 0x0, 0x1, 0x0])
HALVES_CASTING_ITEM_ATTRIBUTE_BYTES = bytes([0x1, 0x81, 0xC4, 0x5D, 0xA, 0x1, 0x47, 0xA, 0x1, 0x0, 0x1, 0x0])
HALVES_RECHARGE_BYTES = bytes([0x80, 0xA, 0xA, 0x1, 0x58, 0xA, 0x1, 0x0, 0x1, 0x0])
HALVES_RECHARGE_ITEM_ATTRIBUTE_BYTES = bytes([0x1, 0x81, 0xC4, 0x5D, 0xA, 0x1, 0x58, 0xA, 0x1, 0x0, 0x1, 0x0])
ITEM_ATTRIBUTE_PLUS_ONE_BYTES = bytes([0x84, 0xA, 0xA, 0x1, 0x1, 0x81, 0x86, 0x5E, 0x1, 0x0, 0x1, 0x1, 0x1])
HIGHLY_SALVAGEABLE_BYTES = bytes([0x95, 0xA, 0x1, 0x0])
STACKING_BYTES = bytes([0xB1, 0xA, 0x1, 0x0])
NON_STACKING_BYTES = EncodedStrings.NON_STACKING

WHILE_ATTACKING_BYTES = bytes([0x2, 0x0, 0x3E, 0xA, 0xA, 0x1, 0xA8, 0xA, 0xA, 0x1, 0xB4, 0xA, 0x1, 0x0, 0x1, 0x0, 0x2, 0x0, 0x2, 0x1, 0x2, 0x0])
WHILE_CASTING_BYTES = bytes([0xB5, 0xA, 0x1, 0x0])
WHILE_ENCHANTED_BYTES = bytes([0xB7, 0xA, 0x1, 0x0])
WHILE_HEXED_BYTES = bytes([0xB8, 0xA, 0x1, 0x0])
WHILE_IN_A_STANCE_BYTES = bytes([0xBA, 0xA, 0x1, 0x0])
WHILE_USING_PREPARATION_BYTES = bytes([0xBF, 0xA, 0x1, 0x0])
WHILE_ACTIVATING_SKILLS_BYTES = bytes([0xC0, 0xA, 0x1, 0x0])
VS_HEXED_FOES_BYTES = bytes([0xAE, 0xA, 0x1, 0x0])
VS_ELEMENTAL_DAMAGE_BYTES = bytes([0xAD, 0xA, 0x1, 0x0])
VS_PHYSICAL_DAMAGE_BYTES = bytes([0xB0, 0xA, 0x1, 0x0])
ENCHANTMENTS_LAST_BYTES = bytes([0xA5, 0xA, 0x1, 0x0])
IMPROVED_SALE_VALUE_BYTES = bytes([0xA6, 0xA, 0x1, 0x0])
INFUSED_BYTES = bytes([0xC9, 0xA, 0x1, 0x0])
REDUCES_DISEASE_DURATION_BYTES = bytes([0xA7, 0xA, 0xA, 0x1, 0x92, 0x62, 0x1, 0x0, 0x1, 0x0])

VS_DAMAGE_BYTES = {
    DamageType.Blunt: bytes([0xAC, 0xA, 0xA, 0x1, 0xDE, 0x8, 0x1, 0x0, 0x1, 0x0]),
    DamageType.Cold: bytes([0xAC, 0xA, 0xA, 0x1, 0xE1, 0x8, 0x1, 0x0, 0x1, 0x0]),
    DamageType.Earth: bytes([0xAC, 0xA, 0xA, 0x1, 0xE2, 0x8, 0x1, 0x0, 0x1, 0x0]),
    DamageType.Fire: bytes([0xAC, 0xA, 0xA, 0x1, 0xE4, 0x8, 0x1, 0x0, 0x1, 0x0]),
    DamageType.Lightning: bytes([0xAC, 0xA, 0xA, 0x1, 0xE3, 0x8, 0x1, 0x0, 0x1, 0x0]),
    DamageType.Piercing: bytes([0xAC, 0xA, 0xA, 0x1, 0xDF, 0x8, 0x1, 0x0, 0x1, 0x0]),
    DamageType.Slashing: bytes([0xAC, 0xA, 0xA, 0x1, 0xE0, 0x8, 0x1, 0x0, 0x1, 0x0]),
}

CONDITION_INCREASE_BYTES = {
    Ailment.Crippled: bytes([0xA4, 0xA, 0xA, 0x1, 0x8E, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Ailment.Dazed: bytes([0xA4, 0xA, 0xA, 0x1, 0x96, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Ailment.Deep_Wound: bytes([0xA4, 0xA, 0xA, 0x1, 0x90, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Ailment.Weakness: bytes([0xA4, 0xA, 0xA, 0x1, 0x98, 0x62, 0x1, 0x0, 0x1, 0x0]),
}

REDUCED_CONDITION_BYTES = {
    Reduced_Ailment.Bleeding: bytes([0xA7, 0xA, 0xA, 0x1, 0x88, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Blind: bytes([0xA7, 0xA, 0xA, 0x1, 0x8A, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Crippled: bytes([0xA7, 0xA, 0xA, 0x1, 0x8E, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Dazed: bytes([0xA7, 0xA, 0xA, 0x1, 0x96, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Deep_Wound: bytes([0xA7, 0xA, 0xA, 0x1, 0x90, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Disease: bytes([0xA7, 0xA, 0xA, 0x1, 0x92, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Poison: bytes([0xA7, 0xA, 0xA, 0x1, 0x94, 0x62, 0x1, 0x0, 0x1, 0x0]),
    Reduced_Ailment.Weakness: bytes([0xA7, 0xA, 0xA, 0x1, 0x98, 0x62, 0x1, 0x0, 0x1, 0x0]),
}
def _attribute_bytes(attribute: Attribute) -> bytes | None:
    return EncodedStrings.ATTRIBUTE_NAMES.get(attribute)


def _attribute_name(attribute: Attribute) -> str:
    encoded = _attribute_bytes(attribute)
    if encoded:
        decoded = string_table.decode(encoded + bytes([0x1, 0x0]))
        if decoded:
            return decoded
        
    return attribute.name.replace("_", " ")


def _encoded(encoded_bytes: bytes, fallback: str) -> "EncodedString":
    return EncodedString(encoded_bytes, fallback)


def _bonus_plus_num(bonus_color: bytes, token: bytes, value: int, fallback_label: str) -> "EncodedString":
    return _encoded(
        bytes([*bonus_color, *PLUS_NUM_TEMPLATE, *token, 0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label} +{value}",
    )


def _bonus_minus_num(bonus_color: bytes, token: bytes, value: int, fallback_label: str) -> "EncodedString":
    return _encoded(
        bytes([*bonus_color, *MINUS_NUM_TEMPLATE, *token, 0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label} -{value}",
    )


def _bonus_plus_percent(bonus_color: bytes, token: bytes, value: int, fallback_label: str) -> "EncodedString":
    return _encoded(
        bytes([*bonus_color, *PLUS_PERCENT_TEMPLATE, *token, 0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label} +{value}%",
    )


def _bonus_colon_num(bonus_color: bytes, token: bytes, value: int, fallback_label: str) -> "EncodedString":
    return _encoded(
        bytes([*bonus_color, *COLON_NUM_TEMPLATE, *token, 0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label}: {value}",
    )


def _dull_parenthesized(raw: bytes, fallback: str) -> bytes:
    return bytes([*ITEM_DULL, *EncodedStrings.PARENTHESIS_STR1, *raw, 0x1, 0x0])


def _append_line(base: "EncodedString", line_bytes: bytes) -> "EncodedString":
    return _encoded(base.encoded + line_bytes, base.fallback)


def _append_line_with_fallback(base: "EncodedString", line_bytes: bytes, fallback_suffix: str) -> "EncodedString":
    separator = "\n" if base.fallback else ""
    return _encoded(base.encoded + line_bytes, f"{base.fallback}{separator}{fallback_suffix}")

class EncodedString:        
    COLOR_TAG_RE = re.compile(r'<c=@[^>]+>(.*?)</c>')
    STAT_TAGS = (
        "<c=@ItemBonus>",
        "<c=@ItemUncommon>",
        "<c=@ItemRare>",
    )

    def __init__(self, encoded: bytes, fallback: str):
        self.encoded = encoded
        self.fallback = fallback
        
        self.__plain = ""
        self.__full = ""

    def decode(self) -> str:
        decoded = string_table.decode(self.encoded)
        return decoded if decoded else self.fallback
    
    @property
    def plain(self) -> str:
        if not self.__plain:
            decoded = self.decode()
            self.__plain = self.COLOR_TAG_RE.sub(r"\1", decoded)
        
        return self.__plain
    
    @property
    def full(self) -> str:
        if not self.__full:
            self.__full = self.decode()
        
        return self.__full
    

@dataclass
class ItemProperty:
    modifier: DecodedModifier
    rarity: Rarity
    
    def __post_init__(self):
        self.__encoded_description = self.create_encoded_description()
        
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"No description available... ({self.__class__.__name__})")
    
    def get_bonus_color(self) -> bytes:
        match self.rarity:
            case Rarity.White:
                return ITEM_BASIC
            
            case Rarity.Blue:
                return ITEM_BONUS
            
            case Rarity.Purple:
                return ITEM_UNCOMMON
            
            case Rarity.Gold:
                return ITEM_RARE
            
            case Rarity.Green:
                return ITEM_UNIQUE
    
    def is_valid(self) -> bool:
        return True
        
    @property
    def description(self) -> str:
        return self.__encoded_description.full
    
    @property
    def plain_description(self) -> str:        
        return self.__encoded_description.plain
    
@dataclass
class ArmorProperty(ItemProperty):
    armor: int
    
    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*ITEM_BASIC, 0x86, 0xA, 0xA, 0x1, *ARMOR_BYTES, 0x1, 0x1, self.armor, 0x1, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"Armor: {self.armor}")
    
@dataclass
class ArmorEnergyRegen(ItemProperty):
    energy_regen: int

    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*self.get_bonus_color(), *PLUS_NUM_TEMPLATE, *ENERGY_RECOVERY_BYTES, 0x1, 0x1, self.energy_regen, 0x1, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"Energy recovery: +{self.energy_regen}")

@dataclass
class ArmorMinusAttacking(ItemProperty):
    armor: int
    
    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*self.get_bonus_color(), *MINUS_NUM_TEMPLATE, *ARMOR_BYTES, 0x1, 0x1, self.armor, 0x1, 0x1, 0x0, *WHILE_ATTACKING_BYTES])
        return EncodedString(encoded_bytes, f"Armor: -{self.armor} (while attacking)")
    
@dataclass
class ArmorPenetration(ItemProperty):
    armor_pen: int
    chance: int

    def create_encoded_description(self) -> EncodedString:
        encoded = bytes([
            *self.get_bonus_color(),
            *PLUS_PERCENT_TEMPLATE, 0x45, 0xA, 0x1, 0x0, 0x1, 0x1, self.armor_pen, 0x1, 0x1, 0x0,
            *ITEM_DULL,
            *EncodedStrings.PARENTHESIS_STR1,
            *CHANCE_TEMPLATE, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0,
            0x1, 0x0
        ])
        return EncodedString(encoded, f"Armor penetration +{self.armor_pen}% (Chance: {self.chance}%)")
    
@dataclass
class ArmorPlus(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor")

@dataclass
class ArmorPlusAttacking(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(bytes([0xB4, 0xA, 0x1, 0x0]), "(while attacking)"))

@dataclass
class ArmorPlusCasting(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(WHILE_CASTING_BYTES, "(while casting)"))

@dataclass
class ArmorPlusEnchanted(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"))

@dataclass
class ArmorPlusHexed(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class ArmorPlusAbove(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class ArmorPlusVsDamage(ItemProperty):
    armor: int
    damage_type: DamageType

    def create_encoded_description(self) -> EncodedString:
        base = _bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor")
        clause_bytes = VS_DAMAGE_BYTES.get(self.damage_type)
        if clause_bytes:
            return _append_line_with_fallback(base, _dull_parenthesized(clause_bytes, f"(vs. {self.damage_type.name} damage)"), f"(vs. {self.damage_type.name} damage)")
        return _encoded(base.encoded, f"{base.fallback} (vs. {self.damage_type.name} damage)")

@dataclass
class ArmorPlusVsElemental(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(VS_ELEMENTAL_DAMAGE_BYTES, "(vs. elemental damage)"), "(vs. elemental damage)")

@dataclass
class ArmorPlusVsPhysical(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(VS_PHYSICAL_DAMAGE_BYTES, "(vs. physical damage)"), "(vs. physical damage)")

@dataclass
class ArmorPlusVsSpecies(ItemProperty):
    armor: int
    species: ItemBaneSpecies

    def create_encoded_description(self) -> EncodedString:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return EncodedString(bytes(), f"Armor +{self.armor}\n(vs. {species})")

@dataclass
class ArmorPlusWhileDown(ItemProperty):
    armor: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ARMOR_BYTES, self.armor, "Armor"), _dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class AttributePlusOne(ItemProperty):
    attribute: Attribute
    chance: int
    attribute_level: int = 1

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            base = EncodedString(bytes([*self.get_bonus_color(), 0x84, 0xA, 0xA, 0x1, 0x64, 0x9, 0x1, 0x0, 0x1, 0x1, 0x1, self.attribute_level]), f"{_attribute_name(self.attribute)} +{self.attribute_level}")
            clause_raw = bytes([0xC1, 0xA, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0])
            
            return _append_line_with_fallback(base, _dull_parenthesized(clause_raw, f"({self.chance}% chance while using skills)"), f"({self.chance}% chance while using skills)")
        return EncodedString(bytes(), f"{_attribute_name(self.attribute)} +1 ({self.chance}% chance while using skills)")

@dataclass
class AttributePlusOneItem(ItemProperty):
    chance: int
    attribute_level: int = 1

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_encoded(bytes([*self.get_bonus_color(), *ITEM_ATTRIBUTE_PLUS_ONE_BYTES, self.attribute_level]), "Item's attribute +1"), _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class DamageCustomized(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_percent(ITEM_BASIC, DAMAGE_BYTES, self.damage_increase, "Damage")

@dataclass
class DamagePlusEnchanted(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage"), _dull_parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class DamagePlusHexed(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage"), _dull_parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class DamagePlusPercent(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage")

@dataclass
class DamagePlusStance(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage"), _dull_parenthesized(WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"), "(while in a Stance)")

@dataclass
class DamagePlusVsHexed(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage"), _dull_parenthesized(VS_HEXED_FOES_BYTES, "(vs. Hexed foes)"), "(vs. Hexed foes)")

@dataclass
class DamagePlusVsSpecies(ItemProperty):
    damage_increase: int
    species: ItemBaneSpecies

    def create_encoded_description(self) -> EncodedString:
        increase = self.damage_increase
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return EncodedString(bytes(), f"Damage +{increase}% (vs. {species.lower()})")

@dataclass
class DamagePlusWhileDown(ItemProperty):
    damage_increase: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return _append_line_with_fallback(_bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage"), _dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class DamagePlusWhileUp(ItemProperty):
    damage_increase: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBC, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return _append_line_with_fallback(_bonus_plus_percent(self.get_bonus_color(), DAMAGE_BYTES, self.damage_increase, "Damage"), _dull_parenthesized(clause_raw, f"(while Health is above {self.health_threshold}%)"), f"(while Health is above {self.health_threshold}%)")

@dataclass
class DamageTypeProperty(ItemProperty):
    damage_type: DamageType

    def create_encoded_description(self) -> EncodedString:
        damage_bytes = EncodedStrings.DAMAGE_TYPE_BYTES.get(self.damage_type)
        if damage_bytes:
            return EncodedString(bytes([*ITEM_BASIC, 0xB, 0x1, *damage_bytes, 0x1, 0x0]), f"{self.damage_type.name} Dmg")
        return EncodedString(bytes(), f"{self.damage_type.name} Dmg")

@dataclass
class EnergyProperty(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_num(ITEM_BASIC, ENERGY_BYTES, self.energy, "Energy")

@dataclass
class Energy2(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_num(ITEM_BASIC, ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyDegen(ItemProperty):
    energy_regen: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_minus_num(self.get_bonus_color(), ENERGY_REGEN_BYTES, self.energy_regen, "Energy regeneration")

@dataclass
class EnergyGainOnHit(ItemProperty):
    energy_gain: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_colon_num(self.get_bonus_color(), ENERGY_GAIN_ON_HIT_BYTES, self.energy_gain, "Energy gain on hit")

@dataclass
class EnergyMinus(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_minus_num(self.get_bonus_color(), ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyPlus(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_num(self.get_bonus_color(), ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyPlusEnchanted(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ENERGY_BYTES, self.energy, "Energy"), _dull_parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class EnergyPlusHexed(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ENERGY_BYTES, self.energy, "Energy"), _dull_parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class EnergyPlusWhileBelow(ItemProperty):
    energy: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ENERGY_BYTES, self.energy, "Energy"), _dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class Furious(ItemProperty):
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_encoded(bytes([*self.get_bonus_color(), *DOUBLE_ADRENALINE_BYTES]), "Double Adrenaline on hit"), _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesCastingTimeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            base = _encoded(bytes([*self.get_bonus_color(), 0x81, 0xA, 0xA, 0x1, 0x47, 0xA, 0x1, 0x0, 0xB, 0x1, *attribute_bytes, 0x1, 0x0, 0x1, 0x0]), f"Halves casting time of {_attribute_name(self.attribute)} spells")
            return _append_line_with_fallback(base, _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")
        return EncodedString(bytes(), f"Halves casting time of {_attribute_name(self.attribute)} spells (Chance: {self.chance}%)")

@dataclass
class HalvesCastingTimeGeneral(ItemProperty):
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_encoded(bytes([*self.get_bonus_color(), *HALVES_CASTING_BYTES]), "Halves casting time of spells"), _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesCastingTimeItemAttribute(ItemProperty):
    chance: int
    attribute : Attribute = field(default=Attribute.None_)

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_encoded(bytes([*self.get_bonus_color(), *HALVES_CASTING_ITEM_ATTRIBUTE_BYTES]), "Halves casting time on spells of item's attribute"), _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesSkillRechargeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            base = _encoded(bytes([*self.get_bonus_color(), 0x81, 0xA, 0xA, 0x1, 0x58, 0xA, 0x1, 0x0, 0xB, 0x1, *attribute_bytes, 0x1, 0x0, 0x1, 0x0]), f"Halves skill recharge of {_attribute_name(self.attribute)} spells")
            return _append_line_with_fallback(base, _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")
        return EncodedString(bytes(), f"Halves skill recharge of {_attribute_name(self.attribute)} spells (Chance: {self.chance}%)")

@dataclass
class HalvesSkillRechargeGeneral(ItemProperty):
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_encoded(bytes([*self.get_bonus_color(), *HALVES_RECHARGE_BYTES]), "Halves skill recharge of spells"), _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesSkillRechargeItemAttribute(ItemProperty):
    chance: int
    attribute : Attribute = field(default=Attribute.None_)

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_encoded(bytes([*self.get_bonus_color(), *HALVES_RECHARGE_ITEM_ATTRIBUTE_BYTES]), "Halves skill recharge on spells of item's attribute"), _dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HeadpieceAttribute(ItemProperty):
    attribute: Attribute
    attribute_level: int

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            return _bonus_plus_num(self.get_bonus_color(), attribute_bytes, self.attribute_level, _attribute_name(self.attribute))
        return EncodedString(bytes(), f"{_attribute_name(self.attribute)} +{self.attribute_level}")

@dataclass
class HeadpieceGenericAttribute(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return _encoded(bytes([*self.get_bonus_color(), *ITEM_ATTRIBUTE_PLUS_ONE_BYTES]), "Item's attribute +1")

@dataclass
class HealthDegen(ItemProperty):
    health_regen: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_minus_num(self.get_bonus_color(), HEALTH_REGEN_BYTES, self.health_regen, "Health regeneration")

@dataclass
class HealthMinus(ItemProperty):
    health: int

    encoded_string = EncodedStrings.HEALTH_MINUS_75

    def create_encoded_description(self) -> EncodedString:
        return _bonus_minus_num(self.get_bonus_color(), HEALTH_BYTES, self.health, "Health")

@dataclass
class HealthPlus(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_plus_num(self.get_bonus_color(), HEALTH_BYTES, self.health, "Health")

@dataclass
class HealthPlusEnchanted(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), HEALTH_BYTES, self.health, "Health"), _dull_parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class HealthPlusHexed(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), HEALTH_BYTES, self.health, "Health"), _dull_parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class HealthPlusStance(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), HEALTH_BYTES, self.health, "Health"), _dull_parenthesized(WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"), "(while in a Stance)")

@dataclass
class EnergyPlusWhileDown(ItemProperty):
    energy: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return _append_line_with_fallback(_bonus_plus_num(self.get_bonus_color(), ENERGY_BYTES, self.energy, "Energy"), _dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class HealthStealOnHit(ItemProperty):
    health_steal: int

    def create_encoded_description(self) -> EncodedString:
        return _bonus_colon_num(self.get_bonus_color(), LIFE_DRAINING_BYTES, self.health_steal, "Life Draining")

@dataclass
class HighlySalvageable(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*self.get_bonus_color(), *HIGHLY_SALVAGEABLE_BYTES]), "Highly salvageable")

@dataclass
class IncreaseConditionDuration(ItemProperty):
    condition: Ailment

    def create_encoded_description(self) -> EncodedString:
        encoded = CONDITION_INCREASE_BYTES.get(self.condition)
        fallback = f"Lengthens {self.condition.name.replace('_', ' ')} duration on foes by 33%"
        if encoded:
            return EncodedString(bytes([*self.get_bonus_color(), *encoded]), fallback)
        return EncodedString(bytes(), fallback)

@dataclass
class IncreaseEnchantmentDuration(ItemProperty):
    enchantment_duration: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*self.get_bonus_color(), 0xA, 0x1, 0xA2, 0xA, 0x1, 0x1, self.enchantment_duration, 0x1, 0x1, 0x0]), f"Enchantments last {self.enchantment_duration}% longer")

@dataclass
class IncreasedSaleValue(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*self.get_bonus_color(), *IMPROVED_SALE_VALUE_BYTES]), "Improved sale value")

@dataclass
class Infused(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*ITEM_BASIC, *INFUSED_BYTES]), "Infused")

@dataclass
class OfTheProfession(ItemProperty):
    attribute: Attribute
    attribute_level: int
    profession: Profession

    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*self.get_bonus_color(), 0x86, 0xA, 0xA, 0x1, *EncodedStrings.ATTRIBUTE_NAMES.get(self.attribute, bytes()), 0x1, 0x0, 0x1, 0x1, 0x5, 0x1, 0x1, 0x0, 0x2, 0x0, 0x3E, 0xA, 0xA, 0x1, 0xA8, 0xA, 0xA, 0x1, 0x2, 0x81, 0xA8, 0x38, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"{AttributeNames.get(self.attribute)}: {self.attribute_level} (if your rank is lower. No effect in PvP.)")

@dataclass
class PrefixProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}")

@dataclass
class ReceiveLessDamage(ItemProperty):
    damage_reduction: int
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"Received damage -{self.damage_reduction} (Chance: {self.chance}%)")

@dataclass
class ReceiveLessPhysDamageEnchanted(ItemProperty):
    damage_reduction: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_minus_num(self.get_bonus_color(), bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"), _dull_parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class ReceiveLessPhysDamageHexed(ItemProperty):
    damage_reduction: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_minus_num(self.get_bonus_color(), bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"), _dull_parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class ReceiveLessPhysDamageStance(ItemProperty):
    damage_reduction: int

    def create_encoded_description(self) -> EncodedString:
        return _append_line_with_fallback(_bonus_minus_num(self.get_bonus_color(), bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"), _dull_parenthesized(WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"), "(while in a Stance)")

@dataclass
class ReduceConditionDuration(ItemProperty):
    condition: Reduced_Ailment

    def create_encoded_description(self) -> EncodedString:
        encoded = REDUCED_CONDITION_BYTES.get(self.condition)
        fallback = f"Reduces {self.condition.name} duration on you by 20%"
        base = EncodedString(bytes([*self.get_bonus_color(), *encoded]), fallback) if encoded else EncodedString(bytes(), fallback)
        return _append_line_with_fallback(base, _dull_parenthesized(STACKING_BYTES, "(Stacking)"), "(Stacking)")

@dataclass
class ReduceConditionTupleDuration(ItemProperty):
    condition_1: Reduced_Ailment
    condition_2: Reduced_Ailment

    def create_encoded_description(self) -> EncodedString:
        encoded_1 = REDUCED_CONDITION_BYTES.get(self.condition_1, b"")
        encoded_2 = REDUCED_CONDITION_BYTES.get(self.condition_2, b"")
        fallback_1 = f"Reduces {self.condition_1.name.replace('_', ' ')} duration on you by 20%"
        fallback_2 = f"Reduces {self.condition_2.name.replace('_', ' ')} duration on you by 20%"
        base_1 = bytes([*ITEM_UNCOMMON, *encoded_1]) if encoded_1 else bytes()
        base_2 = bytes([*ITEM_UNCOMMON, *encoded_2]) if encoded_2 else bytes()
        suffix = _dull_parenthesized(bytes([0xB2, 0xA, 0x1, 0x0]), "(Non-stacking)")
        encoded = bytes([*base_1, *suffix, *base_2, *suffix])
        fallback = f"{fallback_1} (Non-stacking)\n{fallback_2} (Non-stacking)"
        return EncodedString(encoded, fallback)

@dataclass
class ReducesDiseaseDuration(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*self.get_bonus_color(), *REDUCES_DISEASE_DURATION_BYTES]), "Reduces disease duration on you by 20%")

@dataclass
class SuffixProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}")

@dataclass
class AttributeRequirement(ItemProperty):
    attribute: Attribute
    attribute_level: int

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            encoded = REQUIRES_TEMPLATE + attribute_bytes + bytes([0x1, 0x0, 0x1, 0x1, self.attribute_level, 0x1, 0x1, 0x0, 0x1, 0x0])
            return EncodedString(bytes([*ITEM_DULL, *encoded]), f"(Requires {self.attribute_level} {_attribute_name(self.attribute)})")
        return EncodedString(bytes(), f"(Requires {self.attribute_level} {_attribute_name(self.attribute)})")

@dataclass
class BaneProperty(ItemProperty):
    species: ItemBaneSpecies
    
    def create_encoded_description(self) -> EncodedString:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return EncodedString(bytes(), f"Bane: {species}")
    
@dataclass
class DamageProperty(ItemProperty):
    min_damage: int
    max_damage: int
    damage_type : DamageType
    
    def create_encoded_description(self) -> EncodedString:
        damage_bytes = EncodedStrings.DAMAGE_TYPE_BYTES.get(self.damage_type, bytes())
        encoded_bytes = bytes([*ITEM_BASIC, 0x89, 0xA, 0xA, 0x1, 0x4E, 0xA, 0x1, 0x0, 0xB, 0x1, *damage_bytes, 0x1, 0x0, 0x1, 0x1, self.min_damage, 0x1, 0x2, 0x1, self.max_damage, 0x1, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"{self.damage_type.name} Dmg: {self.min_damage}-{self.max_damage}")

@dataclass
class UnknownUpgradeProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"Unknown Upgrade (ID {self.upgrade_id})")

@dataclass
class InscriptionProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}")
    
@dataclass
class UpgradeRuneProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"RUNE\n{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}\n")
    
@dataclass
class AppliesToRuneProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}")

@dataclass
class TooltipProperty(ItemProperty):
    pass

@dataclass
class TargetItemTypeProperty(ItemProperty):
    item_type : ItemType
    
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), f"{self.item_type.name}")
#endregion Item Properties
