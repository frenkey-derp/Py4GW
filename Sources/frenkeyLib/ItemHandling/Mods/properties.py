import re
from typing import TYPE_CHECKING
from dataclasses import InitVar, dataclass
import typing
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, Reduced_Ailment
from Py4GWCoreLib.enums_src.Item_enums import ItemType
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

COLOR_TAG_RE = re.compile(r'<c=@[^>]+>(.*?)</c>')

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
ITEM_ATTRIBUTE_PLUS_ONE_BYTES = bytes([0x84, 0xA, 0xA, 0x1, 0x1, 0x81, 0xC4, 0x5D, 0x1, 0x0, 0x1, 0x1, 0x1, 0x1, 0x1, 0x0])
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

DAMAGE_TYPE_BYTES = {
    DamageType.Blunt: bytes([0xDE, 0x8]),
    DamageType.Cold: bytes([0xE1, 0x8]),
    DamageType.Earth: bytes([0xE2, 0x8]),
    DamageType.Fire: bytes([0xE4, 0x8]),
    DamageType.Lightning: bytes([0xE3, 0x8]),
    DamageType.Piercing: bytes([0xDF, 0x8]),
    DamageType.Slashing: bytes([0xE0, 0x8]),
}

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


def _decode_bytes(encoded_bytes: bytes, fallback: str) -> str:
    decoded = string_table.decode(encoded_bytes)
    return decoded if decoded else fallback


def _plus_num(token: bytes, value: int, fallback_label: str) -> str:
    return _decode_bytes(
        PLUS_NUM_TEMPLATE + token + bytes([0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label} +{value}",
    )


def _minus_num(token: bytes, value: int, fallback_label: str) -> str:
    return _decode_bytes(
        MINUS_NUM_TEMPLATE + token + bytes([0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label} -{value}",
    )


def _plus_percent(token: bytes, value: int, fallback_label: str) -> str:
    return _decode_bytes(
        PLUS_PERCENT_TEMPLATE + token + bytes([0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label} +{value}%",
    )


def _colon_num(token: bytes, value: int, fallback_label: str) -> str:
    return _decode_bytes(
        COLON_NUM_TEMPLATE + token + bytes([0x1, 0x1, value, 0x1, 0x1, 0x0]),
        f"{fallback_label}: {value}",
    )


def _parenthesized(raw: bytes, fallback: str) -> str:
    return _decode_bytes(EncodedStrings.PARENTHESIS_STR1 + raw + bytes([0x1, 0x0]), fallback)


def _chance(chance: int) -> str:
    return _decode_bytes(
        CHANCE_TEMPLATE + bytes([0x48, 0xA, 0x1, 0x0, 0x1, 0x1, chance, 0x1, 0x1, 0x0, 0x1, 0x0]),
        f"(Chance: {chance}%)",
    )


def _with_clause(base: str, clause: str) -> str:
    return f"{base} {clause}" if clause else base


def _join_lines(*parts: str) -> str:
    return "\n".join(part for part in parts if part)


def _attribute_bytes(attribute: Attribute) -> bytes | None:
    return EncodedStrings.ATTRIBUTE_NAMES.get(attribute)


def _attribute_name(attribute: Attribute) -> str:
    encoded = _attribute_bytes(attribute)
    if encoded:
        decoded = string_table.decode(encoded + bytes([0x1, 0x0]))
        if decoded:
            return decoded
        
    return attribute.name.replace("_", " ")

class EncodedString:        
    COLOR_TAG_RE = re.compile(r'<c=@[^>]+>(.*?)</c>')
    STAT_TAGS = (
        "<c=@ItemBonus>",
        "<c=@ItemUncommon>",
        "<c=@ItemRare>",
    )
    META_PREFIXES = [
        bytes([0x59, 0xA]), # Value
        bytes([0x1, 0x81, 0x1C, 0x14]), # Attaches to: %str1%
        bytes([0x97, 0xA, 0x1, 0x0]), # Use to apply to another item.
    ]

    def __init__(self, encoded: bytes, fallback: str):
        self.encoded = encoded
        self.fallback = fallback
        
        self.__plain = ""
        self.__bonuses_only = ""
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
    def bonuses_only(self) -> str:
        if not self.__bonuses_only:
            decoded = self.decode()
            lines = decoded.splitlines()
            bonus_lines = [line for line in lines if line.startswith(EncodedString.STAT_TAGS)]
            bonuses_only = "\n".join(bonus_lines)
            self.__bonuses_only = self.COLOR_TAG_RE.sub(r"\1", bonuses_only)
        
        return self.__bonuses_only
    
    @property
    def full(self) -> str:
        if not self.__full:
            self.__full = self.decode()
        
        return self.__full
    

@dataclass
class ItemProperty:
    modifier: DecodedModifier
    
    def __post_init__(self):
        self.__encoded_description = self.create_encoded_description()
        
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes(), "No description available...")
    
    
    def is_valid(self) -> bool:
        return True
    
    @property
    def description(self) -> str:
        return self.__encoded_description.full
    
    @property
    def simple_description(self) -> str:        
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
        encoded_bytes = bytes([*ITEM_BONUS, *PLUS_NUM_TEMPLATE, *ENERGY_RECOVERY_BYTES, 0x1, 0x1, self.energy_regen, 0x1, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"Energy recovery: +{self.energy_regen}")

@dataclass
class ArmorMinusAttacking(ItemProperty):
    armor: int
    
    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*ITEM_BONUS, *MINUS_NUM_TEMPLATE, *ARMOR_BYTES, 0x1, 0x1, self.armor, 0x1, 0x1, 0x0, *WHILE_ATTACKING_BYTES])
        return EncodedString(encoded_bytes, f"Armor: -{self.armor} (while attacking)")
    
@dataclass
class ArmorPenetration(ItemProperty):
    armor_pen: int
    chance: int

    @property
    def description(self) -> str:
        encoded_bytes = bytes([0xA, 0x1, 0x85, 0xA, 0xA, 0x1, 0x45, 0xA, 0x1, 0x0, 0x1, 0x1, self.armor_pen, 0x1, 0x1, 0x0, 0x2, 0x0, 0x3E, 0xA, 0xA, 0x1, 0xA8, 0xA, 0xA, 0x1, 0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0, 0x2])
        decoded = string_table.decode(encoded_bytes)
        if decoded:
            return decoded
        return f"Armor penetration: {self.armor_pen} ({self.chance}% chance while using skills) - Decoding..."
    
@dataclass
class ArmorPlus(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _plus_num(ARMOR_BYTES, self.armor, "Armor")

@dataclass
class ArmorPlusAttacking(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(WHILE_ATTACKING_BYTES, "(while attacking)"))

@dataclass
class ArmorPlusCasting(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(WHILE_CASTING_BYTES, "(while casting)"))

@dataclass
class ArmorPlusEnchanted(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"))

@dataclass
class ArmorPlusHexed(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class ArmorPlusAbove(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class ArmorPlusVsDamage(ItemProperty):
    armor: int
    damage_type: DamageType

    @property
    def description(self) -> str:
        clause_bytes = VS_DAMAGE_BYTES.get(self.damage_type)
        clause = _decode_bytes(clause_bytes, f"(vs. {self.damage_type.name} damage)") if clause_bytes else f"(vs. {self.damage_type.name} damage)"
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), clause)

@dataclass
class ArmorPlusVsElemental(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(VS_ELEMENTAL_DAMAGE_BYTES, "(vs. elemental damage)"))

@dataclass
class ArmorPlusVsPhysical(ItemProperty):
    armor: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), _parenthesized(VS_PHYSICAL_DAMAGE_BYTES, "(vs. physical damage)"))

@dataclass
class ArmorPlusVsSpecies(ItemProperty):
    armor: int
    species: ItemBaneSpecies

    @property
    def description(self) -> str:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"+{self.armor} Armor (vs. {species})"

@dataclass
class ArmorPlusWhileDown(ItemProperty):
    armor: int
    health_threshold: int

    @property
    def description(self) -> str:
        clause = _parenthesized(
            bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0]),
            f"(while Health is below {self.health_threshold}%)",
        )
        return _with_clause(_plus_num(ARMOR_BYTES, self.armor, "Armor"), clause)

@dataclass
class AttributePlusOne(ItemProperty):
    attribute: Attribute
    chance: int

    @property
    def description(self) -> str:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            base = _plus_num(attribute_bytes, 1, _attribute_name(self.attribute))
            clause = _parenthesized(
                bytes([0xC1, 0xA, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0]),
                f"({self.chance}% chance while using skills)",
            )
            return _with_clause(base, clause)
        return f"{_attribute_name(self.attribute)} +1 ({self.chance}% chance while using skills)"

@dataclass
class AttributePlusOneItem(ItemProperty):
    chance: int

    @property
    def description(self) -> str:
        return _with_clause(_decode_bytes(ITEM_ATTRIBUTE_PLUS_ONE_BYTES, "Item's attribute +1"), _chance(self.chance))

@dataclass
class DamageCustomized(ItemProperty):
    damage_increase: int

    @property
    def description(self) -> str:
        return _plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage")

@dataclass
class DamagePlusEnchanted(ItemProperty):
    damage_increase: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage"), _parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"))

@dataclass
class DamagePlusHexed(ItemProperty):
    damage_increase: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage"), _parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class DamagePlusPercent(ItemProperty):
    damage_increase: int

    @property
    def description(self) -> str:
        return _plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage")

@dataclass
class DamagePlusStance(ItemProperty):
    damage_increase: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage"), _parenthesized(WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"))

@dataclass
class DamagePlusVsHexed(ItemProperty):
    damage_increase: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage"), _parenthesized(VS_HEXED_FOES_BYTES, "(vs. Hexed foes)"))

@dataclass
class DamagePlusVsSpecies(ItemProperty):
    damage_increase: int
    species: ItemBaneSpecies

    @property
    def description(self) -> str:
        increase = self.damage_increase
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"Damage +{increase}% (vs. {species.lower()})"

@dataclass
class DamagePlusWhileDown(ItemProperty):
    damage_increase: int
    health_threshold: int

    @property
    def description(self) -> str:
        clause = _parenthesized(
            bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0]),
            f"(while Health is below {self.health_threshold}%)",
        )
        return _with_clause(_plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage"), clause)

@dataclass
class DamagePlusWhileUp(ItemProperty):
    damage_increase: int
    health_threshold: int

    @property
    def description(self) -> str:
        clause = _parenthesized(
            bytes([0xBC, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0]),
            f"(while Health is above {self.health_threshold}%)",
        )
        return _with_clause(_plus_percent(DAMAGE_BYTES, self.damage_increase, "Damage"), clause)

@dataclass
class DamageTypeProperty(ItemProperty):
    damage_type: DamageType

    @property
    def description(self) -> str:
        damage_bytes = DAMAGE_TYPE_BYTES.get(self.damage_type)
        if damage_bytes:
            return _decode_bytes(bytes([0xB, 0x1]) + damage_bytes + bytes([0x1, 0x0]), f"{self.damage_type.name} Dmg")
        return f"{self.damage_type.name} Dmg"

@dataclass
class EnergyProperty(ItemProperty):
    energy: int

    @property
    def description(self) -> str:
        return _plus_num(ENERGY_BYTES, self.energy, "Energy")

@dataclass
class Energy2(ItemProperty):
    energy: int

    @property
    def description(self) -> str:
        return _plus_num(ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyDegen(ItemProperty):
    energy_regen: int

    @property
    def description(self) -> str:
        return _minus_num(ENERGY_REGEN_BYTES, self.energy_regen, "Energy regeneration")

@dataclass
class EnergyGainOnHit(ItemProperty):
    energy_gain: int

    @property
    def description(self) -> str:
        return _colon_num(ENERGY_GAIN_ON_HIT_BYTES, self.energy_gain, "Energy gain on hit")

@dataclass
class EnergyMinus(ItemProperty):
    energy: int

    @property
    def description(self) -> str:
        return _minus_num(ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyPlus(ItemProperty):
    energy: int

    @property
    def description(self) -> str:
        return _plus_num(ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyPlusEnchanted(ItemProperty):
    energy: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ENERGY_BYTES, self.energy, "Energy"), _parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"))

@dataclass
class EnergyPlusHexed(ItemProperty):
    energy: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(ENERGY_BYTES, self.energy, "Energy"), _parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class EnergyPlusWhileBelow(ItemProperty):
    energy: int
    health_threshold: int

    @property
    def description(self) -> str:
        clause = _parenthesized(
            bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0]),
            f"(while Health is below {self.health_threshold}%)",
        )
        return _with_clause(_plus_num(ENERGY_BYTES, self.energy, "Energy"), clause)

@dataclass
class Furious(ItemProperty):
    chance: int

    @property
    def description(self) -> str:
        return _with_clause(_decode_bytes(DOUBLE_ADRENALINE_BYTES, "Double Adrenaline on hit"), _chance(self.chance))

@dataclass
class HalvesCastingTimeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    @property
    def description(self) -> str:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            base = _decode_bytes(bytes([0x81, 0xA, 0xA, 0x1, 0x47, 0xA, 0x1, 0x0, 0xB, 0x1]) + attribute_bytes + bytes([0x1, 0x0, 0x1, 0x0]), f"Halves casting time of {_attribute_name(self.attribute)} spells")
            return _with_clause(base, _chance(self.chance))
        return f"Halves casting time of {_attribute_name(self.attribute)} spells {_chance(self.chance)}"

@dataclass
class HalvesCastingTimeGeneral(ItemProperty):
    chance: int

    @property
    def description(self) -> str:
        return _with_clause(_decode_bytes(HALVES_CASTING_BYTES, "Halves casting time of spells"), _chance(self.chance))

@dataclass
class HalvesCastingTimeItemAttribute(ItemProperty):
    chance: int

    @property
    def description(self) -> str:
        return _with_clause(_decode_bytes(HALVES_CASTING_ITEM_ATTRIBUTE_BYTES, "Halves casting time on spells of item's attribute"), _chance(self.chance))

@dataclass
class HalvesSkillRechargeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    @property
    def description(self) -> str:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            base = _decode_bytes(bytes([0x81, 0xA, 0xA, 0x1, 0x58, 0xA, 0x1, 0x0, 0xB, 0x1]) + attribute_bytes + bytes([0x1, 0x0, 0x1, 0x0]), f"Halves skill recharge of {_attribute_name(self.attribute)} spells")
            return _with_clause(base, _chance(self.chance))
        return f"Halves skill recharge of {_attribute_name(self.attribute)} spells {_chance(self.chance)}"

@dataclass
class HalvesSkillRechargeGeneral(ItemProperty):
    chance: int

    @property
    def description(self) -> str:
        return _with_clause(_decode_bytes(HALVES_RECHARGE_BYTES, "Halves skill recharge of spells"), _chance(self.chance))

@dataclass
class HalvesSkillRechargeItemAttribute(ItemProperty):
    chance: int

    @property
    def description(self) -> str:
        return f"Halves skill recharge on spells of item's attribute {_chance(self.chance)}"

@dataclass
class HeadpieceAttribute(ItemProperty):
    attribute: Attribute
    attribute_level: int

    @property
    def description(self) -> str:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            return _plus_num(attribute_bytes, self.attribute_level, _attribute_name(self.attribute))
        return f"{_attribute_name(self.attribute)} +{self.attribute_level}"

@dataclass
class HeadpieceGenericAttribute(ItemProperty):
    @property
    def description(self) -> str:
        return _decode_bytes(ITEM_ATTRIBUTE_PLUS_ONE_BYTES, "Item's attribute +1")

@dataclass
class HealthDegen(ItemProperty):
    health_regen: int

    @property
    def description(self) -> str:
        return _minus_num(HEALTH_REGEN_BYTES, self.health_regen, "Health regeneration")

@dataclass
class HealthMinus(ItemProperty):
    health: int

    encoded_string = EncodedStrings.HEALTH_MINUS_75
    
    @property
    def description(self) -> str:
        
        encoded = bytes([0x7E, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health, 0x1, 0x1, 0x0])
        decoded = string_table.decode(encoded)
        
        if decoded:
            return decoded
        
        return f"Health -{self.health} - Decoding..."

@dataclass
class HealthPlus(ItemProperty):
    health: int

    @property
    def description(self) -> str:
        return _plus_num(HEALTH_BYTES, self.health, "Health")

@dataclass
class HealthPlusEnchanted(ItemProperty):
    health: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(HEALTH_BYTES, self.health, "Health"), _parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"))

@dataclass
class HealthPlusHexed(ItemProperty):
    health: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(HEALTH_BYTES, self.health, "Health"), _parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class HealthPlusStance(ItemProperty):
    health: int

    @property
    def description(self) -> str:
        return _with_clause(_plus_num(HEALTH_BYTES, self.health, "Health"), _parenthesized(WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"))

@dataclass
class EnergyPlusWhileDown(ItemProperty):
    energy: int
    health_threshold: int

    @property
    def description(self) -> str:
        clause = _parenthesized(
            bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0]),
            f"(while Health is below {self.health_threshold}%)",
        )
        return _with_clause(_plus_num(ENERGY_BYTES, self.energy, "Energy"), clause)

@dataclass
class HealthStealOnHit(ItemProperty):
    health_steal: int

    @property
    def description(self) -> str:
        return _colon_num(LIFE_DRAINING_BYTES, self.health_steal, "Life Draining")

@dataclass
class HighlySalvageable(ItemProperty):
    @property
    def description(self) -> str:
        return _decode_bytes(HIGHLY_SALVAGEABLE_BYTES, "Highly salvageable")

@dataclass
class IncreaseConditionDuration(ItemProperty):
    condition: Ailment

    @property
    def description(self) -> str:
        encoded = CONDITION_INCREASE_BYTES.get(self.condition)
        fallback = f"Lengthens {self.condition.name.replace('_', ' ')} duration on foes by 33%"
        return _decode_bytes(encoded, fallback) if encoded else fallback

@dataclass
class IncreaseEnchantmentDuration(ItemProperty):
    enchantment_duration: int

    @property
    def description(self) -> str:
        return _decode_bytes(
            bytes([0xA2, 0xA, 0x1, 0x1, self.enchantment_duration, 0x1, 0x1]),
            f"Enchantments last {self.enchantment_duration}% longer",
        )

@dataclass
class IncreasedSaleValue(ItemProperty):
    @property
    def description(self) -> str:
        return _decode_bytes(IMPROVED_SALE_VALUE_BYTES, "Improved sale value")

@dataclass
class Infused(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*ITEM_BASIC, *INFUSED_BYTES]), "Infused")

@dataclass
class OfTheProfession(ItemProperty):
    attribute: Attribute
    attribute_level: int
    profession: Profession

    @property
    def description(self) -> str:
        return f"{AttributeNames.get(self.attribute)}: {self.attribute_level} (if your rank is lower. No effect in PvP.)"

@dataclass
class PrefixProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    @property
    def description(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}"

@dataclass
class ReceiveLessDamage(ItemProperty):
    damage_reduction: int
    chance: int

    @property
    def description(self) -> str:
        return f"Received damage -{self.damage_reduction} {_chance(self.chance)}"

@dataclass
class ReceiveLessPhysDamageEnchanted(ItemProperty):
    damage_reduction: int

    @property
    def description(self) -> str:
        return _with_clause(
            _minus_num(bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"),
            _parenthesized(WHILE_ENCHANTED_BYTES, "(while Enchanted)"),
        )

@dataclass
class ReceiveLessPhysDamageHexed(ItemProperty):
    damage_reduction: int

    @property
    def description(self) -> str:
        return _with_clause(
            _minus_num(bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"),
            _parenthesized(WHILE_HEXED_BYTES, "(while Hexed)"),
        )

@dataclass
class ReceiveLessPhysDamageStance(ItemProperty):
    damage_reduction: int

    @property
    def description(self) -> str:
        return _with_clause(
            _minus_num(bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"),
            _parenthesized(WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"),
        )

@dataclass
class ReduceConditionDuration(ItemProperty):
    condition: Reduced_Ailment

    @property
    def description(self) -> str:
        encoded = REDUCED_CONDITION_BYTES.get(self.condition)
        base = _decode_bytes(encoded, f"Reduces {self.condition.name} duration on you by 20%") if encoded else f"Reduces {self.condition.name} duration on you by 20%"
        return _with_clause(base, _parenthesized(STACKING_BYTES, "(Stacking)"))

@dataclass
class ReduceConditionTupleDuration(ItemProperty):
    condition_1: Reduced_Ailment
    condition_2: Reduced_Ailment

    @property
    def description(self) -> str:
        base_1 = _decode_bytes(REDUCED_CONDITION_BYTES.get(self.condition_1, b""), f"Reduces {self.condition_1.name.replace('_', ' ')} duration on you by 20%")
        base_2 = _decode_bytes(REDUCED_CONDITION_BYTES.get(self.condition_2, b""), f"Reduces {self.condition_2.name.replace('_', ' ')} duration on you by 20%")
        suffix = _decode_bytes(NON_STACKING_BYTES, "(Non-stacking)")
        return _join_lines(_with_clause(base_1, suffix), _with_clause(base_2, suffix))

@dataclass
class ReducesDiseaseDuration(ItemProperty):
    @property
    def description(self) -> str:
        return _decode_bytes(REDUCES_DISEASE_DURATION_BYTES, "Reduces disease duration on you by 20%")

@dataclass
class SuffixProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    @property
    def description(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}"

@dataclass
class AttributeRequirement(ItemProperty):
    attribute: Attribute
    attribute_level: int

    @property
    def description(self) -> str:
        attribute_bytes = _attribute_bytes(self.attribute)
        if attribute_bytes:
            encoded = REQUIRES_TEMPLATE + attribute_bytes + bytes([0x1, 0x0, 0x1, 0x1, self.attribute_level, 0x1, 0x1, 0x0, 0x1, 0x0])
            return _decode_bytes(encoded, f"(Requires {self.attribute_level} {_attribute_name(self.attribute)})")
        return f"(Requires {self.attribute_level} {_attribute_name(self.attribute)})"

@dataclass
class BaneProperty(ItemProperty):
    species: ItemBaneSpecies
    
    @property
    def description(self) -> str:
        species = self.species.name if self.species != ItemBaneSpecies.Unknown else f"ID {self.modifier.arg1}"
        return f"Bane: {species}"
    
@dataclass
class DamageProperty(ItemProperty):
    min_damage: int
    max_damage: int
    damage_type : DamageType
    
    @property
    def description(self) -> str:
        encoded_bytes = bytes([0x89, 0xA, 0xA, 0x1, 0x4E, 0xA, 0x1, 0x0, 0xB, 0x1, *EncodedStrings.DAMAGE_TYPE_BYTES.get(self.damage_type, bytes()), 0x1, 0x0, 0x1, 0x1, self.min_damage, 0x1, 0x2, 0x1, self.max_damage, 0x1, 0x1, 0x0])
        return string_table.decode(encoded_bytes) or ""

@dataclass
class UnknownUpgradeProperty(ItemProperty):
    upgrade_id: ItemUpgradeId
    
    @property
    def description(self) -> str:
        return f"Unknown Upgrade (ID {self.upgrade_id})"

@dataclass
class InscriptionProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    @property
    def description(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}"
    
@dataclass
class UpgradeRuneProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    @property
    def description(self) -> str:
        return f"RUNE\n{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}\n{self.upgrade.description if self.upgrade else ''}\n"
    
@dataclass
class AppliesToRuneProperty(ItemProperty):    
    upgrade_id: ItemUpgradeId
    upgrade: "Upgrade"

    @property
    def description(self) -> str:
        return f"{self.upgrade.name if self.upgrade else f'Unknown (ID {self.upgrade_id})'}"

@dataclass
class TooltipProperty(ItemProperty):
    pass

@dataclass
class TargetItemTypeProperty(ItemProperty):
    item_type : ItemType
    
    @property
    def description(self) -> str:
        return f"{self.item_type.name}"
#endregion Item Properties
