from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, Reduced_Ailment
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Sources.frenkeyLib.ItemHandling.Mods.decoded_modifier import DecodedModifier
from Sources.frenkeyLib.ItemHandling.Mods.types import ItemBaneSpecies, ItemUpgradeId
from Sources.frenkeyLib.ItemHandling.encoded_strings import EncodedString, EncodedStrings

if TYPE_CHECKING:
    from Sources.frenkeyLib.ItemHandling.Mods.upgrades import Upgrade

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
            case Rarity.Blue | Rarity.White:
                return EncodedStrings.ITEM_BONUS
            
            case Rarity.Purple:
                return EncodedStrings.ITEM_UNCOMMON
            
            case Rarity.Gold:
                return EncodedStrings.ITEM_RARE
            
            case Rarity.Green:
                return EncodedStrings.ITEM_UNIQUE
    
    def is_valid(self) -> bool:
        return True

    @property
    def encoded_description(self) -> EncodedString:
        return self.__encoded_description
        
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
        encoded_bytes = bytes([*EncodedStrings.ITEM_BASIC, 0x86, 0xA, 0xA, 0x1, *EncodedStrings.ARMOR_BYTES, 0x1, 0x1, self.armor, 0x1, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"Armor: {self.armor}")
    
@dataclass
class ArmorEnergyRegen(ItemProperty):
    energy_regen: int

    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*self.get_bonus_color(), *EncodedStrings.PLUS_NUM_TEMPLATE, *EncodedStrings.ENERGY_RECOVERY_BYTES, 0x1, 0x1, self.energy_regen, 0x1, 0x1, 0x0])
        return EncodedString(encoded_bytes, f"Energy recovery: +{self.energy_regen}")

@dataclass
class ArmorMinusAttacking(ItemProperty):
    armor: int
    
    def create_encoded_description(self) -> EncodedString:
        encoded_bytes = bytes([*self.get_bonus_color(), *EncodedStrings.MINUS_NUM_TEMPLATE, *EncodedStrings.ARMOR_BYTES, 0x1, 0x1, self.armor, 0x1, 0x1, 0x0, *EncodedStrings.WHILE_ATTACKING_BYTES])
        return EncodedString(encoded_bytes, f"Armor: -{self.armor} (while attacking)")
    
@dataclass
class ArmorPenetration(ItemProperty):
    armor_pen: int
    chance: int

    def create_encoded_description(self) -> EncodedString:
        encoded = bytes([
            *self.get_bonus_color(),
            *EncodedStrings.PLUS_PERCENT_TEMPLATE, 0x45, 0xA, 0x1, 0x0, 0x1, 0x1, self.armor_pen, 0x1, 0x1, 0x0,
            *EncodedStrings.ITEM_DULL,
            *EncodedStrings.PARENTHESIS_STR1,
            *EncodedStrings.CHANCE_TEMPLATE, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0,
            0x1, 0x0
        ])
        return EncodedString(encoded, f"Armor penetration +{self.armor_pen}% (Chance: {self.chance}%)")
    
@dataclass
class ArmorPlus(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor")

@dataclass
class ArmorPlusAttacking(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(bytes([0xB4, 0xA, 0x1, 0x0]), "(while attacking)"))

@dataclass
class ArmorPlusCasting(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_CASTING_BYTES, "(while casting)"))

@dataclass
class ArmorPlusEnchanted(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_ENCHANTED_BYTES, "(while Enchanted)"))

@dataclass
class ArmorPlusHexed(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_HEXED_BYTES, "(while Hexed)"))

@dataclass
class ArmorPlusAbove(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class ArmorPlusVsDamage(ItemProperty):
    armor: int
    damage_type: DamageType

    def create_encoded_description(self) -> EncodedString:
        base = EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor")
        clause_bytes = EncodedStrings.VS_DAMAGE_BYTES.get(self.damage_type)
        if clause_bytes:
            return EncodedStrings._append_line_with_fallback(base, EncodedStrings._dull_parenthesized(clause_bytes, f"(vs. {self.damage_type.name} damage)"), f"(vs. {self.damage_type.name} damage)")
        return EncodedString(base.encoded, f"{base.fallback} (vs. {self.damage_type.name} damage)")

@dataclass
class ArmorPlusVsElemental(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(EncodedStrings.VS_ELEMENTAL_DAMAGE_BYTES, "(vs. elemental damage)"), "(vs. elemental damage)")

@dataclass
class ArmorPlusVsPhysical(ItemProperty):
    armor: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(EncodedStrings.VS_PHYSICAL_DAMAGE_BYTES, "(vs. physical damage)"), "(vs. physical damage)")

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
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ARMOR_BYTES, self.armor, "Armor"), EncodedStrings._dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class AttributePlusOne(ItemProperty):
    attribute: Attribute
    chance: int
    attribute_level: int = 1

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = EncodedStrings._attribute_bytes(self.attribute)
        if attribute_bytes:
            base = EncodedString(bytes([*self.get_bonus_color(), 0x84, 0xA, 0xA, 0x1, 0x64, 0x9, 0x1, 0x0, 0x1, 0x1, 0x1, self.attribute_level]), f"{EncodedStrings._attribute_name(self.attribute)} +{self.attribute_level}")
            clause_raw = bytes([0xC1, 0xA, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0])
            
            return EncodedStrings._append_line_with_fallback(base, EncodedStrings._dull_parenthesized(clause_raw, f"({self.chance}% chance while using skills)"), f"({self.chance}% chance while using skills)")
        return EncodedString(bytes(), f"{EncodedStrings._attribute_name(self.attribute)} +1 ({self.chance}% chance while using skills)")

@dataclass
class AttributePlusOneItem(ItemProperty):
    chance: int
    attribute_level: int = 1

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.ITEM_ATTRIBUTE_PLUS_ONE_BYTES, self.attribute_level]), "Item's attribute +1"), EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class DamageCustomized(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_percent(EncodedStrings.ITEM_BASIC, EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage")

@dataclass
class DamagePlusEnchanted(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class DamagePlusHexed(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class DamagePlusPercent(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage")

@dataclass
class DamagePlusStance(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"), "(while in a Stance)")

@dataclass
class DamagePlusVsHexed(ItemProperty):
    damage_increase: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage"), EncodedStrings._dull_parenthesized(EncodedStrings.VS_HEXED_FOES_BYTES, "(vs. Hexed foes)"), "(vs. Hexed foes)")

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
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage"), EncodedStrings._dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class DamagePlusWhileUp(ItemProperty):
    damage_increase: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBC, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_percent(self.get_bonus_color(), EncodedStrings.DAMAGE_BYTES, self.damage_increase, "Damage"), EncodedStrings._dull_parenthesized(clause_raw, f"(while Health is above {self.health_threshold}%)"), f"(while Health is above {self.health_threshold}%)")

@dataclass
class DamageTypeProperty(ItemProperty):
    damage_type: DamageType

    def create_encoded_description(self) -> EncodedString:
        damage_bytes = EncodedStrings.DAMAGE_TYPE_BYTES.get(self.damage_type)
        if damage_bytes:
            
            # return EncodedString(bytes([*EncodedStrings.ITEM_BASIC, 0xB, 0x1, *damage_bytes, 0x1, 0x0]), f"{self.damage_type.name} Dmg")
            return EncodedString(bytes([*EncodedStrings.ITEM_BASIC, 0xA, 0x1, 0x8B, 0xA, 0xA, 0x1, 0x4C, 0xA, 0x1, 0x0, 0xB, 0x1, *damage_bytes, 0x1, 0x0]), f"{self.damage_type.name} Dmg")
        return EncodedString(bytes(), f"{self.damage_type.name} Dmg")

@dataclass
class EnergyProperty(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_num(EncodedStrings.ITEM_BASIC, EncodedStrings.ENERGY_BYTES, self.energy, "Energy")

@dataclass
class Energy2(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_num(EncodedStrings.ITEM_BASIC, EncodedStrings.ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyDegen(ItemProperty):
    energy_regen: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_minus_num(self.get_bonus_color(), EncodedStrings.ENERGY_REGEN_BYTES, self.energy_regen, "Energy regeneration")

@dataclass
class EnergyGainOnHit(ItemProperty):
    energy_gain: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_colon_num(self.get_bonus_color(), EncodedStrings.ENERGY_GAIN_ON_HIT_BYTES, self.energy_gain, "Energy gain on hit")

@dataclass
class EnergyMinus(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_minus_num(self.get_bonus_color(), EncodedStrings.ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyPlus(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ENERGY_BYTES, self.energy, "Energy")

@dataclass
class EnergyPlusEnchanted(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ENERGY_BYTES, self.energy, "Energy"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class EnergyPlusHexed(ItemProperty):
    energy: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ENERGY_BYTES, self.energy, "Energy"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class EnergyPlusWhileBelow(ItemProperty):
    energy: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ENERGY_BYTES, self.energy, "Energy"), EncodedStrings._dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class Furious(ItemProperty):
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.DOUBLE_ADRENALINE_BYTES]), "Double Adrenaline on hit"), EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesCastingTimeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = EncodedStrings._attribute_bytes(self.attribute)
        if attribute_bytes:
            base = EncodedStrings._encoded(bytes([*self.get_bonus_color(), 0x81, 0xA, 0xA, 0x1, 0x47, 0xA, 0x1, 0x0, 0xB, 0x1, *attribute_bytes, 0x1, 0x0, 0x1, 0x0]), f"Halves casting time of {EncodedStrings._attribute_name(self.attribute)} spells")
            return EncodedStrings._append_line_with_fallback(base, EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")
        return EncodedString(bytes(), f"Halves casting time of {EncodedStrings._attribute_name(self.attribute)} spells (Chance: {self.chance}%)")

@dataclass
class HalvesCastingTimeGeneral(ItemProperty):
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.HALVES_CASTING_BYTES]), "Halves casting time of spells"), EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesCastingTimeItemAttribute(ItemProperty):
    chance: int
    attribute : Attribute = field(default=Attribute.None_)

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.HALVES_CASTING_ITEM_ATTRIBUTE_BYTES]), "Halves casting time on spells of item's attribute"), EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesSkillRechargeAttribute(ItemProperty):
    chance: int
    attribute: Attribute

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = EncodedStrings._attribute_bytes(self.attribute)
        if attribute_bytes:
            base = EncodedStrings._encoded(bytes([*self.get_bonus_color(), 0x81, 0xA, 0xA, 0x1, 0x58, 0xA, 0x1, 0x0, 0xB, 0x1, *attribute_bytes, 0x1, 0x0, 0x1, 0x0]), f"Halves skill recharge of {EncodedStrings._attribute_name(self.attribute)} spells")
            return EncodedStrings._append_line_with_fallback(base, EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")
        return EncodedStrings._encoded(bytes(), f"Halves skill recharge of {EncodedStrings._attribute_name(self.attribute)} spells (Chance: {self.chance}%)")

@dataclass
class HalvesSkillRechargeGeneral(ItemProperty):
    chance: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.HALVES_RECHARGE_BYTES]), "Halves skill recharge of spells"), EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HalvesSkillRechargeItemAttribute(ItemProperty):
    chance: int
    attribute : Attribute = field(default=Attribute.None_)

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.HALVES_RECHARGE_ITEM_ATTRIBUTE_BYTES]), "Halves skill recharge on spells of item's attribute"), EncodedStrings._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

@dataclass
class HeadpieceAttribute(ItemProperty):
    attribute: Attribute
    attribute_level: int

    def create_encoded_description(self) -> EncodedString:
        attribute_bytes = EncodedStrings._attribute_bytes(self.attribute)
        if attribute_bytes:
            return EncodedStrings._bonus_plus_num(self.get_bonus_color(), attribute_bytes, self.attribute_level, EncodedStrings._attribute_name(self.attribute))
        return EncodedStrings._encoded(bytes(), f"{EncodedStrings._attribute_name(self.attribute)} +{self.attribute_level}")

@dataclass
class HeadpieceGenericAttribute(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._encoded(bytes([*self.get_bonus_color(), *EncodedStrings.ITEM_ATTRIBUTE_PLUS_ONE_BYTES]), "Item's attribute +1")

@dataclass
class HealthDegen(ItemProperty):
    health_regen: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_minus_num(self.get_bonus_color(), EncodedStrings.HEALTH_REGEN_BYTES, self.health_regen, "Health regeneration")

@dataclass
class HealthMinus(ItemProperty):
    health: int

    encoded_string = EncodedStrings.HEALTH_MINUS_75

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_minus_num(self.get_bonus_color(), EncodedStrings.HEALTH_BYTES, self.health, "Health")

@dataclass
class HealthPlus(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.HEALTH_BYTES, self.health, "Health")

@dataclass
class HealthPlusEnchanted(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.HEALTH_BYTES, self.health, "Health"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class HealthPlusHexed(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.HEALTH_BYTES, self.health, "Health"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class HealthPlusStance(ItemProperty):
    health: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.HEALTH_BYTES, self.health, "Health"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"), "(while in a Stance)")

@dataclass
class EnergyPlusWhileDown(ItemProperty):
    energy: int
    health_threshold: int

    def create_encoded_description(self) -> EncodedString:
        clause_raw = bytes([0xBB, 0xA, 0xA, 0x1, 0x52, 0xA, 0x1, 0x0, 0x1, 0x1, self.health_threshold, 0x1, 0x1, 0x0, 0x1, 0x0])
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_plus_num(self.get_bonus_color(), EncodedStrings.ENERGY_BYTES, self.energy, "Energy"), EncodedStrings._dull_parenthesized(clause_raw, f"(while Health is below {self.health_threshold}%)"), f"(while Health is below {self.health_threshold}%)")

@dataclass
class HealthStealOnHit(ItemProperty):
    health_steal: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._bonus_colon_num(self.get_bonus_color(), EncodedStrings.LIFE_DRAINING_BYTES, self.health_steal, "Life Draining")

@dataclass
class HighlySalvageable(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*self.get_bonus_color(), *EncodedStrings.HIGHLY_SALVAGEABLE_BYTES]), "Highly salvageable")

@dataclass
class IncreaseConditionDuration(ItemProperty):
    condition: Ailment

    def create_encoded_description(self) -> EncodedString:
        encoded = EncodedStrings.CONDITION_INCREASE_BYTES.get(self.condition)
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
        return EncodedString(bytes([*self.get_bonus_color(), *EncodedStrings.IMPROVED_SALE_VALUE_BYTES]), "Improved sale value")

@dataclass
class Infused(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*EncodedStrings.ITEM_BASIC, *EncodedStrings.INFUSED_BYTES]), "Infused")

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
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_minus_num(self.get_bonus_color(), bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_ENCHANTED_BYTES, "(while Enchanted)"), "(while Enchanted)")

@dataclass
class ReceiveLessPhysDamageHexed(ItemProperty):
    damage_reduction: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_minus_num(self.get_bonus_color(), bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_HEXED_BYTES, "(while Hexed)"), "(while Hexed)")

@dataclass
class ReceiveLessPhysDamageStance(ItemProperty):
    damage_reduction: int

    def create_encoded_description(self) -> EncodedString:
        return EncodedStrings._append_line_with_fallback(EncodedStrings._bonus_minus_num(self.get_bonus_color(), bytes([0x1, 0x81, 0x4F, 0x5D, 0x1, 0x0]), self.damage_reduction, "Received physical damage"), EncodedStrings._dull_parenthesized(EncodedStrings.WHILE_IN_A_STANCE_BYTES, "(while in a Stance)"), "(while in a Stance)")

@dataclass
class ReduceConditionDuration(ItemProperty):
    condition: Reduced_Ailment

    def create_encoded_description(self) -> EncodedString:
        encoded = EncodedStrings.REDUCED_CONDITION_BYTES.get(self.condition)
        fallback = f"Reduces {self.condition.name} duration on you by 20%"
        base = EncodedString(bytes([*self.get_bonus_color(), *encoded]), fallback) if encoded else EncodedString(bytes(), fallback)
        return EncodedStrings._append_line_with_fallback(base, EncodedStrings._dull_parenthesized(EncodedStrings.STACKING_BYTES, "(Stacking)"), "(Stacking)")

@dataclass
class ReduceConditionTupleDuration(ItemProperty):
    condition_1: Reduced_Ailment
    condition_2: Reduced_Ailment

    def create_encoded_description(self) -> EncodedString:
        encoded_1 = EncodedStrings.REDUCED_CONDITION_BYTES.get(self.condition_1, b"")
        encoded_2 = EncodedStrings.REDUCED_CONDITION_BYTES.get(self.condition_2, b"")
        fallback_1 = f"Reduces {self.condition_1.name.replace('_', ' ')} duration on you by 20%"
        fallback_2 = f"Reduces {self.condition_2.name.replace('_', ' ')} duration on you by 20%"
        base_1 = bytes([*EncodedStrings.ITEM_UNCOMMON, *encoded_1]) if encoded_1 else bytes()
        base_2 = bytes([*EncodedStrings.ITEM_UNCOMMON, *encoded_2]) if encoded_2 else bytes()
        suffix = EncodedStrings._dull_parenthesized(bytes([0xB2, 0xA, 0x1, 0x0]), "(Non-stacking)")
        encoded = bytes([*base_1, *suffix, *base_2, *suffix])
        fallback = f"{fallback_1} (Non-stacking)\n{fallback_2} (Non-stacking)"
        return EncodedString(encoded, fallback)

@dataclass
class ReducesDiseaseDuration(ItemProperty):
    def create_encoded_description(self) -> EncodedString:
        return EncodedString(bytes([*self.get_bonus_color(), *EncodedStrings.REDUCES_DISEASE_DURATION_BYTES]), "Reduces disease duration on you by 20%")

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
        attribute_bytes = EncodedStrings._attribute_bytes(self.attribute)
        if attribute_bytes:
            encoded = EncodedStrings.REQUIRES_TEMPLATE + attribute_bytes + bytes([0x1, 0x0, 0x1, 0x1, self.attribute_level, 0x1, 0x1, 0x0, 0x1, 0x0])
            return EncodedString(bytes([*EncodedStrings.ITEM_DULL, *encoded]), f"(Requires {self.attribute_level} {EncodedStrings._attribute_name(self.attribute)})")
        return EncodedString(bytes(), f"(Requires {self.attribute_level} {EncodedStrings._attribute_name(self.attribute)})")

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
        encoded_bytes = bytes([*EncodedStrings.ITEM_BASIC, 0x89, 0xA, 0xA, 0x1, 0x4E, 0xA, 0x1, 0x0, 0xB, 0x1, *damage_bytes, 0x1, 0x0, 0x1, 0x1, self.min_damage, 0x1, 0x2, 0x1, self.max_damage, 0x1, 0x1, 0x0])
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
