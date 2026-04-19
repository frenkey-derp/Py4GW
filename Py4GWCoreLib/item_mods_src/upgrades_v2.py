from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Callable, ClassVar, Generic, Optional, Protocol, SupportsFloat, SupportsInt, TypeVar, cast

from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, AttributeNames, DamageType, Profession, Reduced_Ailment
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.item_mods_src.decoded_modifier import DecodedModifier
from Py4GWCoreLib.item_mods_src.types import ItemBaneSpecies, ItemUpgrade, ItemUpgradeId, ItemUpgradeType, ModifierIdentifier, ModifierIdentifierSpec
from Py4GWCoreLib.item_mods_src.upgrades import _get_property_factory
from Py4GWCoreLib.native_src.internals import string_table
from Py4GWCoreLib.native_src.internals.encoded_strings import GWEncoded, GWStringEncoded

from Py4GWCoreLib.item_mods_src.properties import *

class NumericValue(SupportsInt, SupportsFloat, Protocol):
    """Protocol for values that behave like orderable numeric types."""

    def __lt__(self, other: Any, /) -> bool: ...
    def __le__(self, other: Any, /) -> bool: ...
    def __gt__(self, other: Any, /) -> bool: ...
    def __ge__(self, other: Any, /) -> bool: ...

NumberT = TypeVar("NumberT", bound=NumericValue)
ValueT = TypeVar("ValueT")
PropertyT = TypeVar("PropertyT", bound=ItemProperty)
UpgradeT = TypeVar("UpgradeT", bound="Upgrade")

class ItemProperties(dict[ModifierIdentifier, ItemProperty]):
    def get(self, key: ModifierIdentifier | type[PropertyT], default: Any = None) -> Any:
        if isinstance(key, type):
            for prop in self.values():
                if isinstance(prop, key):
                    return prop
            return default
        
        return super().get(key, default)

@dataclass(slots=True)
class InstructionResult:
    target: str
    value: Any = None
    applied: bool = False
    reason: Optional[str] = None


class Instruction(Generic[UpgradeT, ValueT]):
    """
    Declarative rule that fills one upgrade field from one or more item properties.

    Each instruction knows:
    - which upgrade attribute it controls
    - how to read a candidate value from ItemProperties
    - how to validate the candidate value
    """

    def __init__(
        self,
        identifier: ModifierIdentifierSpec,
        target: str,
        value_getter: Callable[[ItemProperties, UpgradeT], ValueT | None],
    ) -> None:
        self.identifier = identifier
        self.target = target
        self.value_getter = value_getter

    def get_value(self, properties: ItemProperties, upgrade: UpgradeT) -> ValueT | None:
        return self.value_getter(properties, upgrade)

    def evaluate(self, value: ValueT | None) -> bool:
        return value is not None

    def apply(self, upgrade: UpgradeT, properties: ItemProperties) -> InstructionResult:
        value = self.get_value(properties, upgrade)
        if not self.evaluate(value):
            return InstructionResult(
                target=self.target,
                value=value,
                applied=False,
                reason="candidate value did not satisfy the instruction",
            )

        setattr(upgrade, self.target, value)
        return InstructionResult(target=self.target, value=value, applied=True)

class RangeInstruction(Instruction[UpgradeT, NumberT]):
    def __init__(
        self,
        identifier: ModifierIdentifierSpec,
        target: str,
        min_value: NumberT,
        max_value: NumberT,
        value_getter: Callable[[ItemProperties, UpgradeT], NumberT | None],
    ) -> None:
        super().__init__(identifier, target, value_getter)
        self.min_value = min_value
        self.max_value = max_value

    @property
    def range(self) -> tuple[NumberT, NumberT]:
        return self.min_value, self.max_value

    def evaluate(self, value: NumberT | None) -> bool:
        return value is not None and self.min_value <= value <= self.max_value

class EnumInstruction(Instruction[UpgradeT, Enum]):
    def __init__(
        self,
        identifier: ModifierIdentifierSpec,
        target: str,
        enum_type: type[Enum],
        value_getter: Callable[[ItemProperties, UpgradeT], Enum | None],
    ) -> None:
        super().__init__(identifier, target, value_getter)
        self.enum_type = enum_type

    def evaluate(self, value: Enum | None) -> bool:
        return value is not None and isinstance(value, self.enum_type)

class SelectInstruction(Instruction[UpgradeT, ValueT]):
    def __init__(
        self,
        identifier: ModifierIdentifierSpec,
        target: str,
        options: list[ValueT] | tuple[ValueT, ...],
        value_getter: Callable[[ItemProperties, UpgradeT], ValueT | None],
    ) -> None:
        super().__init__(identifier, target, value_getter)
        self.options = tuple(options)

    @property
    def options_list(self) -> tuple[ValueT, ...]:
        return self.options

    def evaluate(self, value: ValueT | None) -> bool:
        return value is not None and value in self.options

class FixedValueInstruction(Instruction[UpgradeT, ValueT]):
    def __init__(
        self,
        identifier: ModifierIdentifierSpec,
        target: str,
        fixed_value: ValueT,
        value_getter: Callable[[ItemProperties, UpgradeT], ValueT | None],
    ) -> None:
        super().__init__(identifier, target, value_getter)
        self.fixed_value = fixed_value

    def evaluate(self, value: ValueT | None) -> bool:
        return value == self.fixed_value

def property_value(
    property_type: type[PropertyT],
    selector: Callable[[PropertyT], ValueT | None],
) -> Callable[[ItemProperties, UpgradeT], ValueT | None]:
    """Create a getter that reads a value from the first matching ItemProperty."""

    def getter(properties: ItemProperties, _: UpgradeT) -> ValueT | None:
        prop = properties.get(property_type)
        if prop is None:
            return None
        return selector(prop)

    return getter

def ranged(
    identifier: ModifierIdentifierSpec,
    target: str,
    min_value: NumberT,
    max_value: NumberT,
    value_getter: Callable[[ItemProperties, UpgradeT], NumberT | None],
) -> RangeInstruction[UpgradeT, NumberT]:
    return RangeInstruction(identifier, target, min_value, max_value, value_getter)

def enum(
    identifier: ModifierIdentifierSpec,
    target: str,
    enum_type: type[Enum],
    value_getter: Callable[[ItemProperties, UpgradeT], Enum | None],
) -> EnumInstruction[UpgradeT]:
    return EnumInstruction(identifier, target, enum_type, value_getter)

def select(
    identifier: ModifierIdentifierSpec,
    target: str,
    options: list[ValueT] | tuple[ValueT, ...],
    value_getter: Callable[[ItemProperties, UpgradeT], ValueT | None],
) -> SelectInstruction[UpgradeT, ValueT]:
    return SelectInstruction(identifier, target, options, value_getter)

def fixed(
    identifier: ModifierIdentifierSpec,
    target: str,
    fixed_value: ValueT,
    value_getter: Callable[[ItemProperties, UpgradeT], ValueT | None],
) -> FixedValueInstruction[UpgradeT, ValueT]:
    return FixedValueInstruction(identifier, target, fixed_value, value_getter)

@dataclass(eq=False)
class Upgrade:
    """
    Abstract base class for item upgrades. Each specific upgrade type (e.g., Prefix, Suffix, Inscription) should inherit from this class and implement the necessary properties and methods.
    """
    _registry: ClassVar[dict[str, type["Upgrade"]]] = {}
    mod_type: ClassVar[ItemUpgradeType] = ItemUpgradeType.Unknown
    id: ClassVar[ItemUpgrade] = ItemUpgrade.Unknown
    
    properties: ItemProperties = field(default_factory=ItemProperties)
    
    rarity: Rarity = field(init=False, default=Rarity.Blue, repr=False, compare=False)
    upgrade_id: ItemUpgradeId = field(init=False, default=ItemUpgradeId.Unknown, repr=False, compare=False)
    modifier: Optional[DecodedModifier] = field(init=False, default=None, repr=False, compare=False)
    is_inherent: bool = field(init=False, default=False, repr=False, compare=False)
    language: ServerLanguage = field(init=False, repr=False, compare=False)
    
    upgrade_info: ClassVar[tuple[Instruction["Upgrade", Any], ...]] 

    __encoded_name: GWStringEncoded = field(init=False, repr=False, compare=False)
    __encoded_description: GWStringEncoded = field(init=False, repr=False, compare=False)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Upgrade._registry[cls.__name__] = cls

    def __post_init__(self):
        object.__setattr__(self, "is_inherent", False)
        object.__setattr__(self, "language", ServerLanguage(string_table._loaded_language) if string_table._loaded_language in ServerLanguage._value2member_map_ else ServerLanguage.English)
        object.__setattr__(self, "rarity", getattr(type(self), "rarity", Rarity.Blue))
        object.__setattr__(self, "upgrade_id", ItemUpgradeId.Unknown)
        object.__setattr__(self, "modifier", None)
        object.__setattr__(self, "properties", ItemProperties())
        
        self._refresh_encoded_strings()

    def __setattr__(self, name: str, value: Any) -> None:
        if name in type(self)._get_serializable_property_names() and "_property_values" in self.__dict__:
            object.__setattr__(self, name, value)
            self._refresh_encoded_strings()
            return

        object.__setattr__(self, name, value)

    #region Upgrade Composition from Modifiers
    @classmethod
    def _pre_compose(cls, upgrade: "Upgrade", mod: DecodedModifier, all_modifiers: list[DecodedModifier], remaining_modifiers: list[DecodedModifier]) -> None:
        return None

    @classmethod
    def _post_compose(cls, upgrade: "Upgrade", mod: DecodedModifier, all_modifiers: list[DecodedModifier], remaining_modifiers: list[DecodedModifier]) -> None:
        return None
        
    @classmethod
    def compose_from_modifiers(cls, mod : DecodedModifier, remaining_modifiers: list[DecodedModifier], all_modifiers: list[DecodedModifier], rarity: Rarity = Rarity.Blue) -> Optional["Upgrade"]:        
        upgrade = cls()
        upgrade.upgrade_id = mod.upgrade_id
        upgrade.rarity = rarity
        upgrade.modifier = mod

        cls._pre_compose(upgrade, mod, all_modifiers, remaining_modifiers)

        property_factory = _get_property_factory()
        matched_modifiers = cls._match_property_modifiers(remaining_modifiers)
        if matched_modifiers is None:
            return None

        for prop_key, prop_mod in matched_modifiers:
            prop = property_factory.get(prop_mod.identifier, lambda m, _, rarity: ItemProperty(modifier=m, rarity=rarity))(prop_mod, remaining_modifiers, rarity)
            upgrade.properties[prop_key] = prop

        cls._post_compose(upgrade, mod, all_modifiers, remaining_modifiers)
        upgrade._refresh_encoded_strings()
        return upgrade
   
    @staticmethod
    def _normalize_property_identifier_spec(identifier_spec: ModifierIdentifierSpec) -> tuple[ModifierIdentifier, ...]:
        if isinstance(identifier_spec, tuple):
            return identifier_spec
        return (identifier_spec,)
    
    @classmethod
    def _get_property_identifier_key(cls, identifier_spec: ModifierIdentifierSpec) -> ModifierIdentifier:
        return cls._normalize_property_identifier_spec(identifier_spec)[0]

    @classmethod
    def _match_property_modifiers(cls, modifiers: list[DecodedModifier]) -> Optional[list[tuple[ModifierIdentifier, DecodedModifier]]]:
        matched_modifiers: list[tuple[ModifierIdentifier, DecodedModifier]] = []
        used_modifiers: list[DecodedModifier] = []
        matched_by_key: dict[ModifierIdentifier, DecodedModifier] = {}

        for inst in cls.upgrade_info:
            prop_key = cls._get_property_identifier_key(inst.identifier)
            prop_mod = matched_by_key.get(prop_key)
            if prop_mod is None:
                identifier_options = cls._normalize_property_identifier_spec(inst.identifier)
                prop_mod = next((m for m in modifiers if m not in used_modifiers and m.identifier in identifier_options), None)
                if prop_mod is not None:
                    matched_by_key[prop_key] = prop_mod
                    used_modifiers.append(prop_mod)
            if prop_mod is None:
                return None

            matched_modifiers.append((prop_key, prop_mod))

        return matched_modifiers
    #endregion Upgrade Composition from Modifiers
    
    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return cls.id.has_id(upgrade_id)

    #region Equality and Matching
    @classmethod
    def _get_serializable_property_names(cls) -> list[str]:
        return [field_info.name for field_info in fields(cls) if field_info.init]

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, Enum):
            return {
                "enum_type": type(value).__name__,
                "value": value.name,
            }

        if isinstance(value, list):
            return [Upgrade._serialize_value(entry) for entry in value]

        if isinstance(value, tuple):
            return [Upgrade._serialize_value(entry) for entry in value]

        if isinstance(value, dict):
            return {str(key): Upgrade._serialize_value(entry) for key, entry in value.items()}

        return value

    @staticmethod
    def _deserialize_value(value: Any) -> Any:
        if isinstance(value, list):
            return [Upgrade._deserialize_value(entry) for entry in value]

        if isinstance(value, dict):
            enum_type = value.get("enum_type")
            enum_value = value.get("value")
            if isinstance(enum_type, str) and isinstance(enum_value, str):
                enum_cls = globals().get(enum_type)
                if isinstance(enum_cls, type) and issubclass(enum_cls, Enum) and enum_value in enum_cls.__members__:
                    return enum_cls[enum_value]

            return {str(key): Upgrade._deserialize_value(entry) for key, entry in value.items()}

        return value

    @staticmethod
    def _normalize_comparison_value(value: Any) -> Any:
        if isinstance(value, Enum):
            return (type(value).__name__, value.name)

        if isinstance(value, list):
            return tuple(Upgrade._normalize_comparison_value(entry) for entry in value)

        if isinstance(value, tuple):
            return tuple(Upgrade._normalize_comparison_value(entry) for entry in value)

        if isinstance(value, dict):
            return tuple(sorted((str(key), Upgrade._normalize_comparison_value(entry)) for key, entry in value.items()))

        return value

    def _comparison_data(self) -> tuple[str, tuple[tuple[str, Any], ...]]:
        comparison_values = {
            property_name: self._normalize_comparison_value(getattr(self, property_name))
            for property_name in self._get_serializable_property_names()
        }
        return type(self).__name__, tuple(sorted(comparison_values.items()))

    def equals(self, other: object) -> bool:
        return isinstance(other, Upgrade) and self._comparison_data() == other._comparison_data()

    def matches(self, other: object) -> bool:
        return self.equals(other)

    def __eq__(self, other: object) -> bool:
        return self.equals(other)
    #endregion Equality and Matching
    
    #region Serialization
    def to_dict(self) -> dict[str, Any]:
        values = {
            property_name: self._serialize_value(getattr(self, property_name))
            for property_name in self._get_serializable_property_names()
        }

        payload: dict[str, Any] = {
            "upgrade_type": type(self).__name__,
            "values": values,
        }

        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Optional["Upgrade"]:
        upgrade_type_name = str(payload.get("upgrade_type", ""))
        upgrade_cls = cls._registry.get(upgrade_type_name)
        if upgrade_cls is None:
            return None

        raw_values = payload.get("values", {})
        if not isinstance(raw_values, dict):
            raw_values = {}

        values = {
            str(key): cls._deserialize_value(value)
            for key, value in raw_values.items()
        }
        return upgrade_cls(**values)
    #endregion Serialization
    
    #region Encoded String Generation
    def get_text_color(self, name : bool = False) -> bytes:
        match self.rarity:
            case Rarity.Blue | Rarity.White:
                return GWEncoded.ITEM_ENHANCE if name else GWEncoded.ITEM_BONUS
            
            case Rarity.Purple:
                return GWEncoded.ITEM_UNCOMMON
            
            case Rarity.Gold:
                return GWEncoded.ITEM_RARE
            
            case Rarity.Green:
                return GWEncoded.ITEM_UNIQUE
            
    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(bytes(), f"no encoded name ({self.__class__.__name__})")
    
    def create_encoded_description(self) -> GWStringEncoded:
        if not self.properties:
            return GWStringEncoded(bytes(), f"no encoded description ({self.__class__.__name__})")

        parts = [prop.encoded_description for prop in self.properties.values() if prop.encoded_description]
        return GWEncoded.combine_encoded_strings(parts, f"no encoded description ({self.__class__.__name__})")
    
    def _refresh_encoded_strings(self) -> None:
        self.__encoded_name = self.create_encoded_name()
        self.__encoded_description = self.create_encoded_description()

    #endregion Encoded String Generation
    
    @property
    def name(self) -> str:
        return self.__encoded_name.full
    
    @property
    def name_plain(self) -> str:
        return self.__encoded_name.plain    
    
    @property
    def description_plain(self) -> str:
        return self.__encoded_description.bonuses_only or self.__encoded_description.plain or "no encoded description (short)"
    
    @property
    def description(self) -> str:
        return self.__encoded_description.full
        
    @property
    def display_summary(self) -> str:
        name = self.name_plain
        description = self.description_plain
        
        return f"{name}\n{description}" if description else name
    
    @property
    def item_type(self) -> Optional[ItemType]:
        if isinstance(self, WeaponUpgrade):
            return self.target_item_type
        
        elif isinstance(self, Inscription):
            return self.target_item_type
        
        return None
    
    @property
    def is_maxed(self) -> bool:
        for instruction in self.upgrade_info:
            if isinstance(instruction, RangeInstruction):
                value = getattr(self, instruction.target)
                if value < instruction.max_value:
                    return False
                
        return True
    
    @classmethod
    def get_static_name(cls, rarity : Rarity = Rarity.Blue) -> str: 
        temp_instance = cls()
        temp_instance.rarity = rarity
        temp_instance.__encoded_name = temp_instance.create_encoded_name()
        
        return temp_instance.name_plain

@dataclass(eq=False)
class UnknownUpgrade(Upgrade):
    mod_type = ItemUpgradeType.Unknown
    id = ItemUpgrade.Unknown
    
#region Weapon Upgrades
@dataclass(eq=False)
class WeaponUpgrade(Upgrade):
    target_item_type: ItemType = field(init=False, default=ItemType.Unknown, repr=False, compare=False)

    @classmethod
    def _pre_compose(cls, upgrade: "Upgrade", mod: DecodedModifier, all_modifiers: list[DecodedModifier], remaining_modifiers: list[DecodedModifier]) -> None:
        weapon_upgrade = cast(WeaponUpgrade, upgrade)
        weapon_upgrade.target_item_type = cls.id.get_item_type(weapon_upgrade.upgrade_id)        
         
#region Prefixes

@dataclass(eq=False)
class WeaponPrefix(WeaponUpgrade):
    mod_type = ItemUpgradeType.Prefix
    
@dataclass(eq=False)
class IncreaseConditionDurationUpgrade(WeaponPrefix):
    condition: Ailment | None = None
    
    def create_encoded_description(self) -> GWStringEncoded:
        if self.condition is None:
            return super().create_encoded_description()
        
        encoded = GWEncoded.CONDITION_INCREASE_BYTES.get(self.condition)
        fallback = f"Lengthens {self.condition.name.replace('_', ' ')} duration on foes by 33%"
        
        if encoded:
            return GWStringEncoded(bytes([*self.get_text_color(), *encoded, *GWEncoded._dull_parenthesized(GWEncoded.STACKING_BYTES, "(Stacking)")]), fallback)
        
        return GWStringEncoded(bytes(), fallback)

@dataclass(eq=False)
class DamageTypeUpgrade(WeaponPrefix):
    damage_type: DamageType | None = None
    
    def create_encoded_description(self) -> GWStringEncoded:
        if self.damage_type is None:
            return super().create_encoded_description()
        
        damage_bytes = GWEncoded.DAMAGE_TYPE_BYTES.get(self.damage_type)
        if damage_bytes:            
            return GWStringEncoded(bytes([*GWEncoded.ITEM_BASIC, 0xA, 0x1, 0x8B, 0xA, 0xA, 0x1, 0x4C, 0xA, 0x1, 0x0, 0xB, 0x1, *damage_bytes, 0x1, 0x0]), f"{self.damage_type.name} Dmg")
        
        return GWStringEncoded(bytes(), f"{self.damage_type.name} Dmg")

@dataclass
class AdeptUpgrade(WeaponPrefix):
    id: ClassVar[ItemUpgrade] = ItemUpgrade.Adept
    chance: int = 20

    upgrade_info = (
        ranged(
            identifier= ModifierIdentifier.HalvesCastingTimeItemAttribute,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                HalvesCastingTimeAttribute,
                lambda prop: prop.chance,
            ),
        ),
    )
    
    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x1, 0x81, 0x94, 0x5D, 0x1, 0x0]), f"Adept")
    
    def create_encoded_description(self) -> GWStringEncoded:
        parts = [
            GWEncoded._append_line_with_fallback(GWEncoded._encoded(bytes([*self.get_text_color(), *GWEncoded.HALVES_CASTING_ITEM_ATTRIBUTE_BYTES]), "Halves casting time on spells of item's attribute"), GWEncoded._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")
        ]
        
        return GWEncoded.combine_encoded_strings(parts, "no encoded description")

@dataclass(eq=False)
class BarbedUpgrade(IncreaseConditionDurationUpgrade):
    id = ItemUpgrade.Barbed
    condition = Ailment.Bleeding

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.IncreaseConditionDuration,
            target="condition",
            fixed_value=Ailment.Bleeding,
            value_getter=property_value(
                IncreaseConditionDuration,
                lambda prop: prop.condition,
            ),
        ),
    )
    
    def create_encoded_name(self) -> GWStringEncoded:
         return GWStringEncoded(self.get_text_color(True) + bytes([0x69, 0xA, 0x1, 0x0]), f"Barbed")

@dataclass(eq=False)
class CripplingUpgrade(IncreaseConditionDurationUpgrade):
    id = ItemUpgrade.Crippling
    condition = Ailment.Crippled

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.IncreaseConditionDuration,
            target="condition",
            fixed_value=Ailment.Crippled,
            value_getter=property_value(
                IncreaseConditionDuration,
                lambda prop: prop.condition,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6A, 0xA, 0x1, 0x0]), f"Crippling")
        
@dataclass(eq=False)
class CruelUpgrade(IncreaseConditionDurationUpgrade):
    id = ItemUpgrade.Cruel
    condition = Ailment.Deep_Wound

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.IncreaseConditionDuration,
            target="condition",
            fixed_value=Ailment.Deep_Wound,
            value_getter=property_value(
                IncreaseConditionDuration,
                lambda prop: prop.condition,
            ),
        ),
    )

    
    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6B, 0xA, 0x1, 0x0]), f"Cruel")

    
@dataclass(eq=False)
class DefensiveUpgrade(WeaponPrefix):
    id = ItemUpgrade.Defensive
    armor: int = 5
    
    upgrade_info = (
        ranged(
            identifier= ModifierIdentifier.ArmorPlus,
            target="armor",
            min_value=4,
            max_value=5,
            value_getter=property_value(
                ArmorPlus,
                lambda prop: prop.armor,
            ),
        ),
    )
    
    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6D, 0xA, 0x1, 0x0]), f"Defensive")
    
    def create_encoded_description(self) -> GWStringEncoded:
        return GWEncoded._bonus_plus_num(self.get_text_color(), GWEncoded.ARMOR_BYTES, self.armor, "Armor")

@dataclass(eq=False)
class EbonUpgrade(DamageTypeUpgrade):
    id = ItemUpgrade.Ebon
    damage_type = DamageType.Earth

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.DamageTypeProperty,
            target="damage_type",
            fixed_value=DamageType.Earth,
            value_getter=property_value(
                DamageTypeProperty,
                lambda prop: prop.damage_type,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0xD5, 0x8, 0x1, 0x0]), "Ebon")

@dataclass(eq=False)
class FieryUpgrade(DamageTypeUpgrade):
    id = ItemUpgrade.Fiery
    damage_type = DamageType.Fire

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.DamageTypeProperty,
            target="damage_type",
            fixed_value=DamageType.Fire,
            value_getter=property_value(
                DamageTypeProperty,
                lambda prop: prop.damage_type,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0xD7, 0x8, 0x1, 0x0]), "Fiery")

@dataclass(eq=False)
class FuriousUpgrade(WeaponPrefix):
    id = ItemUpgrade.Furious
    chance: int = 10

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.Furious,
            target="chance",
            min_value=2,
            max_value=10,
            value_getter=property_value(
                Furious,
                lambda prop: prop.chance,
            ),
        ),
    )

    def create_encoded_description(self) -> GWStringEncoded:
        return GWEncoded._append_line_with_fallback(GWEncoded._encoded(bytes([*self.get_text_color(), *GWEncoded.DOUBLE_ADRENALINE_BYTES]), "Double Adrenaline on hit"), GWEncoded._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6F, 0xA, 0x1, 0x0]), "Furious")

@dataclass(eq=False)
class HaleUpgrade(WeaponPrefix):
    id = ItemUpgrade.Hale
    health: int = 30

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HealthPlus,
            target="health",
            min_value=10,
            max_value=30,
            value_getter=property_value(
                HealthPlus,
                lambda prop: prop.health,
            ),
        ),
    )

    def create_encoded_description(self) -> GWStringEncoded:
        return GWEncoded._bonus_plus_num(self.get_text_color(), GWEncoded.HEALTH_BYTES, self.health, "Health")

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x70, 0xA, 0x1, 0x0]), "Hale")

@dataclass(eq=False)
class HeavyUpgrade(IncreaseConditionDurationUpgrade):
    id = ItemUpgrade.Heavy
    condition = Ailment.Weakness

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.IncreaseConditionDuration,
            target="condition",
            fixed_value=Ailment.Weakness,
            value_getter=property_value(
                IncreaseConditionDuration,
                lambda prop: prop.condition,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x72, 0xA, 0x1, 0x0]), "Heavy")

@dataclass(eq=False)
class IcyUpgrade(DamageTypeUpgrade):
    id = ItemUpgrade.Icy
    damage_type = DamageType.Cold

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.DamageTypeProperty,
            target="damage_type",
            fixed_value=DamageType.Cold,
            value_getter=property_value(
                DamageTypeProperty,
                lambda prop: prop.damage_type,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0xD4, 0x8, 0x1, 0x0]), "Icy")

@dataclass(eq=False)
class InsightfulUpgrade(WeaponPrefix):
    id = ItemUpgrade.Insightful
    energy: int = 5

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.EnergyPlus,
            target="energy",
            min_value=1,
            max_value=5,
            value_getter=property_value(
                EnergyPlus,
                lambda prop: prop.energy,
            ),
        ),
    )

    def create_encoded_description(self) -> GWStringEncoded:
        return GWEncoded._bonus_plus_num(self.get_text_color(), GWEncoded.ENERGY_BYTES, self.energy, "Energy")

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x73, 0xA, 0x1, 0x0]), "Insightful")

@dataclass(eq=False)
class PoisonousUpgrade(IncreaseConditionDurationUpgrade):
    id = ItemUpgrade.Poisonous
    condition = Ailment.Poison

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.IncreaseConditionDuration,
            target="condition",
            fixed_value=Ailment.Poison,
            value_getter=property_value(
                IncreaseConditionDuration,
                lambda prop: prop.condition,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x75, 0xA, 0x1, 0x0]), "Poisonous")

@dataclass(eq=False)
class ShockingUpgrade(DamageTypeUpgrade):
    id = ItemUpgrade.Shocking
    damage_type = DamageType.Lightning

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.DamageTypeProperty,
            target="damage_type",
            fixed_value=DamageType.Lightning,
            value_getter=property_value(
                DamageTypeProperty,
                lambda prop: prop.damage_type,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0xD6, 0x8, 0x1, 0x0]), "Shocking")

@dataclass(eq=False)
class SilencingUpgrade(IncreaseConditionDurationUpgrade):
    id = ItemUpgrade.Silencing
    condition = Ailment.Dazed

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.IncreaseConditionDuration,
            target="condition",
            fixed_value=Ailment.Dazed,
            value_getter=property_value(
                IncreaseConditionDuration,
                lambda prop: prop.condition,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6C, 0xA, 0x1, 0x0]), "Silencing")

@dataclass(eq=False)
class SunderingUpgrade(WeaponPrefix):
    id = ItemUpgrade.Sundering
    chance: int = 20
    armor_penetration: int = 20

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.ArmorPenetration,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                ArmorPenetration,
                lambda prop: prop.chance,
            ),
        ),
        select(
            identifier=ModifierIdentifier.ArmorPenetration,
            target="armor_penetration",
            options=[10, 20],
            value_getter=property_value(
                ArmorPenetration,
                lambda prop: prop.armor_penetration,
            ),
        ),
    )

    def create_encoded_description(self) -> GWStringEncoded:
        encoded = bytes([
            *self.get_text_color(),
            *GWEncoded.PLUS_PERCENT_TEMPLATE, 0x45, 0xA, 0x1, 0x0, 0x1, 0x1, self.armor_penetration, 0x1, 0x1, 0x0,
            *GWEncoded.ITEM_DULL,
            *GWEncoded.PARENTHESIS_STR1,
            *GWEncoded.CHANCE_TEMPLATE, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0,
            0x1, 0x0
        ])
        return GWStringEncoded(encoded, f"Armor penetration +{self.armor_penetration}% (Chance: {self.chance}%)")
    
    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x74, 0xA, 0x1, 0x0]), "Sundering")

@dataclass(eq=False)
class SwiftUpgrade(WeaponPrefix):
    id = ItemUpgrade.Swift
    chance: int = 10

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesCastingTimeGeneral,
            target="chance",
            min_value=5,
            max_value=10,
            value_getter=property_value(
                HalvesCastingTimeGeneral,
                lambda prop: prop.chance,
            ),
        ),
    )

    def create_encoded_description(self) -> GWStringEncoded:
        return GWEncoded._append_line_with_fallback(GWEncoded._encoded(bytes([*self.get_text_color(), *GWEncoded.HALVES_CASTING_BYTES]), "Halves casting time of spells"), GWEncoded._dull_parenthesized(bytes([0x87, 0xA, 0xA, 0x1, 0x48, 0xA, 0x1, 0x0, 0x1, 0x1, self.chance, 0x1, 0x1, 0x0, 0x1, 0x0]), f"(Chance: {self.chance}%)"), f"(Chance: {self.chance}%)")

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x1, 0x81, 0x95, 0x5D, 0x1, 0x0]), "Swift")

@dataclass(eq=False)
class VampiricUpgrade(WeaponPrefix):
    id = ItemUpgrade.Vampiric
    health_regeneration: int = -1
    health_steal: int = 5

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HealthRegeneneration,
            target="health_regeneration",
            min_value=-1,
            max_value=-1,
            value_getter=property_value(
                HealthRegeneneration,
                lambda prop: prop.health_regeneration,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.HealthStealOnHit,
            target="health_steal",
            min_value=1,
            max_value=5,
            value_getter=property_value(
                HealthStealOnHit,
                lambda prop: prop.health_steal,
            ),
        ),
    )
    

    def create_encoded_description(self) -> GWStringEncoded:
        parts = [
            GWEncoded._bonus_colon_num(self.get_text_color(), GWEncoded.LIFE_DRAINING_BYTES, self.health_steal, "Life Draining"),
            GWEncoded._bonus_minus_num(self.get_text_color(), GWEncoded.HEALTH_REGEN_BYTES, abs(self.health_regeneration), "Health regeneration")
        ]
        
        return GWEncoded.combine_encoded_strings(parts, "no encoded description")
    

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x71, 0xA, 0x1, 0x0]), "Vampiric")

@dataclass(eq=False)
class ZealousUpgrade(WeaponPrefix):
    id = ItemUpgrade.Zealous
    energy_regeneration: int = -1
    energy_gain: int = 1

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.EnergyRegeneration,
            target="energy_regeneration",
            min_value=-1,
            max_value=-1,
            value_getter=property_value(
                EnergyRegeneration,
                lambda prop: prop.energy_regeneration,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.EnergyGainOnHit,
            target="energy_gain",
            min_value=1,
            max_value=1,
            value_getter=property_value(
                EnergyGainOnHit,
                lambda prop: prop.energy_gain,
            ),
        ),
    )

    def create_encoded_description(self) -> GWStringEncoded:
        parts = [
            GWEncoded._bonus_colon_num(self.get_text_color(), GWEncoded.ENERGY_GAIN_ON_HIT_BYTES, self.energy_gain, "Energy gain on hit"),
            GWEncoded._bonus_minus_num(self.get_text_color(), GWEncoded.ENERGY_REGEN_BYTES, abs(self.energy_regeneration), "Energy regeneration")
        ]
        
        return GWEncoded.combine_encoded_strings(parts, "no encoded description")
    
    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6E, 0xA, 0x1, 0x0]), "Zealous")
    
#endregion Prefixes

#region Suffixes

@dataclass(eq=False)
class WeaponSuffix(WeaponUpgrade):
    mod_type = ItemUpgradeType.Suffix

@dataclass(eq=False)
class OfAttributeUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfAttribute
    chance: int = 20
    attribute: Attribute = Attribute.None_
    attribute_level: int = 1

    upgrade_info = (
        enum(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            enum_type=Attribute,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute_level",
            min_value=1,
            max_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0xB, 0x1]) + GWEncoded.ATTRIBUTE_NAMES.get(self.attribute, bytes()) + bytes([0x1, 0x0, 0x1, 0x0]), f"of {AttributeNames.get(self.attribute, self.attribute.name)}", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Attribute"])

@dataclass(eq=False)
class OfAptitudeUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfAptitude
    chance: int = 20

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesCastingTimeItemAttribute,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                HalvesCastingTimeItemAttribute,
                lambda prop: prop.chance,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x96, 0x5D, 0x1, 0x0]), "of Aptitude", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Aptitude"])

@dataclass(eq=False)
class OfAxeMasteryUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfAxeMastery
    attribute = Attribute.AxeMastery

@dataclass(eq=False)
class OfDaggerMasteryUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfDaggerMastery
    attribute = Attribute.DaggerMastery

@dataclass(eq=False)
class OfDefenseUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfDefense
    armor: int = 5

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.ArmorPlus,
            target="armor",
            min_value=4,
            max_value=5,
            value_getter=property_value(
                ArmorPlus,
                lambda prop: prop.armor,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x77, 0xA, 0x1, 0x0]), "of Defense", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Defense"])

@dataclass(eq=False)
class OfDevotionUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfDevotion
    health: int = 45

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HealthPlusEnchanted,
            target="health",
            min_value=30,
            max_value=45,
            value_getter=property_value(
                HealthPlusEnchanted,
                lambda prop: prop.health,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x97, 0x5D, 0x1, 0x0]), "of Devotion", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Devotion"])

@dataclass(eq=False)
class OfEnchantingUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfEnchanting
    enchantment_duration: int = 20

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.IncreaseEnchantmentDuration,
            target="enchantment_duration",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                IncreaseEnchantmentDuration,
                lambda prop: prop.enchantment_duration,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x78, 0xA, 0x1, 0x0]), "of Enchanting", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Enchanting"])

@dataclass(eq=False)
class OfEnduranceUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfEndurance
    health: int = 45

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HealthPlusStance,
            target="health",
            min_value=30,
            max_value=45,
            value_getter=property_value(
                HealthPlusStance,
                lambda prop: prop.health,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x98, 0x5D, 0x1, 0x0]), "of Endurance", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Endurance"])

@dataclass(eq=False)
class OfFortitudeUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfFortitude
    health: int = 30

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HealthPlus,
            target="health",
            min_value=10,
            max_value=30,
            value_getter=property_value(
                HealthPlus,
                lambda prop: prop.health,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x79, 0xA, 0x1, 0x0]), "of Fortitude", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Fortitude"])

@dataclass(eq=False)
class OfHammerMasteryUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfHammerMastery
    attribute = Attribute.HammerMastery

@dataclass(eq=False)
class OfMarksmanshipUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfMarksmanship
    attribute = Attribute.Marksmanship

@dataclass(eq=False)
class OfMasteryUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfMastery
    chance: int = 20
    attribute_level: int = 1

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.AttributePlusOneItem,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                AttributePlusOneItem,
                lambda prop: prop.chance,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.AttributePlusOneItem,
            target="attribute_level",
            min_value=1,
            max_value=1,
            value_getter=property_value(
                AttributePlusOneItem,
                lambda prop: prop.attribute_level,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x99, 0x5D, 0x1, 0x0]), "of Mastery", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Mastery"])

@dataclass(eq=False)
class OfMemoryUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfMemory
    chance: int = 20

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesSkillRechargeItemAttribute,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                HalvesSkillRechargeItemAttribute,
                lambda prop: prop.chance,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x9A, 0x5D, 0x1, 0x0]), "of Memory", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Memory"])

@dataclass(eq=False)
class OfQuickeningUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfQuickening
    chance: int = 10

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesSkillRechargeGeneral,
            target="chance",
            min_value=5,
            max_value=10,
            value_getter=property_value(
                HalvesSkillRechargeGeneral,
                lambda prop: prop.chance,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x9B, 0x5D, 0x1, 0x0]), "of Quickening", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Quickening"])

@dataclass(eq=False)
class OfScytheMasteryUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfScytheMastery
    attribute = Attribute.ScytheMastery

@dataclass(eq=False)
class OfShelterUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfShelter
    armor: int = 7

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.ArmorPlusVsPhysical,
            target="armor",
            min_value=4,
            max_value=7,
            value_getter=property_value(
                ArmorPlusVsPhysical,
                lambda prop: prop.armor,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x7B, 0xA, 0x1, 0x0]), "of Shelter", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Shelter"])

@dataclass(eq=False)
class OfSlayingUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfSlaying
    species: ItemBaneSpecies = ItemBaneSpecies.Unknown
    damage_increase: int = 20

    upgrade_info = (
        select(
            identifier=ModifierIdentifier.BaneSpecies,
            target="species",
            options=tuple(species for species in ItemBaneSpecies if species != ItemBaneSpecies.Unknown),
            value_getter=property_value(
                BaneProperty,
                lambda prop: prop.species,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.DamagePlusVsSpecies,
            target="damage_increase",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                DamagePlusVsSpecies,
                lambda prop: prop.damage_increase,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + GWEncoded.SLAYING_SUFFIXES.get(self.species, bytes()), f"of {self.species.name}-Slaying", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", f"{self.species.name}-Slaying" if self.species != ItemBaneSpecies.Unknown else "Slaying"])

@dataclass(eq=False)
class OfSpearMasteryUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfSpearMastery
    attribute = Attribute.SpearMastery

@dataclass(eq=False)
class OfSwiftnessUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfSwiftness
    chance: int = 10

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesCastingTimeGeneral,
            target="chance",
            min_value=5,
            max_value=10,
            value_getter=property_value(
                HalvesCastingTimeGeneral,
                lambda prop: prop.chance,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x7C, 0xA, 0x1, 0x0]), "of Swiftness", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Swiftness"])

@dataclass(eq=False)
class OfSwordsmanshipUpgrade(OfAttributeUpgrade):
    id = ItemUpgrade.OfSwordsmanship
    attribute = Attribute.Swordsmanship

@dataclass(eq=False)
class OfTheProfessionUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfTheProfession
    profession: Profession = Profession._None
    attribute: Attribute = Attribute.None_
    attribute_level: int = 5

    upgrade_info = (
        enum(
            identifier=ModifierIdentifier.OfTheProfession,
            target="attribute",
            enum_type=Attribute,
            value_getter=property_value(
                OfTheProfession,
                lambda prop: prop.attribute,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.OfTheProfession,
            target="attribute_level",
            min_value=4,
            max_value=5,
            value_getter=property_value(
                OfTheProfession,
                lambda prop: prop.attribute_level,
            ),
        ),
        enum(
            identifier=ModifierIdentifier.OfTheProfession,
            target="profession",
            enum_type=Profession,
            value_getter=property_value(
                OfTheProfession,
                lambda prop: prop.profession,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + GWEncoded.THE_PROFESSION.get(self.profession, bytes()), f"of {self.profession.name if self.profession != Profession._None else 'Unknown Profession'}", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", self.profession.name if self.profession != Profession._None else "Profession"])

@dataclass(eq=False)
class OfValorUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfValor
    health: int = 60

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HealthPlusHexed,
            target="health",
            min_value=45,
            max_value=60,
            value_getter=property_value(
                HealthPlusHexed,
                lambda prop: prop.health,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x1, 0x81, 0x9C, 0x5D, 0x1, 0x0]), "of Valor", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Valor"])

@dataclass(eq=False)
class OfWardingUpgrade(WeaponSuffix):
    id = ItemUpgrade.OfWarding
    armor: int = 7

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.ArmorPlusVsElemental,
            target="armor",
            min_value=4,
            max_value=7,
            value_getter=property_value(
                ArmorPlusVsElemental,
                lambda prop: prop.armor,
            ),
        ),
    )

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + GWEncoded.STR1_OF_STR2 + GWEncoded.PLACEHOLDER_TO_REMOVE + bytes([0x7D, 0xA, 0x1, 0x0]), "of Warding", GWEncoded.PLACEHOLDER_TO_REMOVE, ["", "Warding"])

#endregion Suffixes
#endregion Weapon Upgrades

#region Inscriptions    
@dataclass(eq=False)
class Inscription(Upgrade):
    mod_type = ItemUpgradeType.Inscription
    target_item_type: ItemType = field(init=False, default=ItemType.Unknown, repr=False, compare=False)

    @classmethod
    def _pre_compose(cls, upgrade: "Upgrade", mod: DecodedModifier, all_modifiers: list[DecodedModifier], remaining_modifiers: list[DecodedModifier]) -> None:
        inscription = cast(Inscription, upgrade)
        inscription.target_item_type = cls.id.get_item_type(inscription.upgrade_id)   
        
#endregion Inscriptions

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
    SwiftUpgrade,
    AdeptUpgrade,
    OfMemoryUpgrade,
    OfQuickeningUpgrade,
    OfAptitudeUpgrade,
    OfDevotionUpgrade,
    OfValorUpgrade,
    OfEnduranceUpgrade,
    OfSwiftnessUpgrade,
]
