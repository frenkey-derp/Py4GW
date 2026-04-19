from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Callable, ClassVar, Generic, Optional, Protocol, SupportsFloat, SupportsInt, TypeVar, cast

from Py4GWCoreLib.enums_src.GameData_enums import Ailment, Attribute, DamageType
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.item_mods_src.decoded_modifier import DecodedModifier
from Py4GWCoreLib.item_mods_src.types import ItemUpgrade, ItemUpgradeId, ItemUpgradeType, ModifierIdentifier, ModifierIdentifierSpec
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

class ItemProperties(list[ItemProperty]):
    def get(self, type_: type[PropertyT]) -> Optional[PropertyT]:
        for prop in self:
            if isinstance(prop, type_):
                return prop
        return None

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

        for inst in cls.upgrade_info:
            identifier_options = cls._normalize_property_identifier_spec(inst.identifier)
            prop_mod = next((m for m in modifiers if m not in used_modifiers and m.identifier in identifier_options), None)
            if prop_mod is None:
                return None

            matched_modifiers.append((cls._get_property_identifier_key(inst.identifier), prop_mod))
            used_modifiers.append(prop_mod)

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
        return GWStringEncoded(bytes(), f"no encoded description ({self.__class__.__name__})")
    
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
    
    def create_encoded_name(self) -> GWStringEncoded:
         return GWStringEncoded(self.get_text_color(True) + bytes([0x69, 0xA, 0x1, 0x0]), f"Barbed")

@dataclass(eq=False)
class CripplingUpgrade(WeaponPrefix):
    id = ItemUpgrade.Crippling
    condition = Ailment.Crippled

    def create_encoded_name(self) -> GWStringEncoded:
        return GWStringEncoded(self.get_text_color(True) + bytes([0x6A, 0xA, 0x1, 0x0]), f"Crippling")
        
@dataclass(eq=False)
class CruelUpgrade(WeaponPrefix):
    id = ItemUpgrade.Cruel
    condition = Ailment.Deep_Wound

    
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
    
#endregion Prefixes
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