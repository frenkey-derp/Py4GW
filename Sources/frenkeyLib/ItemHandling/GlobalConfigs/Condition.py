from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, NamedTuple, Optional, Sequence, TypeAlias, cast

import Py4GW

from Py4GWCoreLib.enums_src.GameData_enums import Attribute, DyeColor
from Py4GWCoreLib.enums_src.Item_enums import INVENTORY_BAGS, MAX_STACK_SIZE, NICK_CYCLE_COUNT, STORAGE_BAGS, WEAPON_TYPES, ItemType, Rarity, SalvageMode, WeaponType, is_weapon_type_literal
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.item_mods_src.item_mod import ItemMod
from Py4GWCoreLib.item_mods_src.upgrades import ArmorUpgrade, HalvesCastingTimeAttributeUpgrade, HalvesRechargeTimeAttributeUpgrade, Inherent, Inscription, RangeInstruction, Upgrade, WeaponUpgrade
from Py4GWCoreLib.item_data.ItemData import COMMON_MATERIALS, DAMAGE_RANGES, RARE_MATERIALS
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot


class DamageRange(NamedTuple):
    min_value: int
    max_value: int


@dataclass
class RequirementFilter:
    value_range: DamageRange
    allowed_attributes: list[Attribute] = field(default_factory=list)
    disallowed_attributes: list[Attribute] = field(default_factory=list)


@dataclass
class InherentFilter:
    inherent: Inherent
    ranges: dict[str, DamageRange]

    @staticmethod
    def from_inherent(inherent: Inherent, use_full_ranges: bool = False) -> "InherentFilter":
        ranges: dict[str, DamageRange] = {}
        for instruction in type(inherent).upgrade_info:
            if not isinstance(instruction, RangeInstruction):
                continue

            if use_full_ranges:
                ranges[instruction.target] = DamageRange(int(instruction.min_value), int(instruction.max_value))
            else:
                value = int(getattr(inherent, instruction.target, instruction.max_value))
                ranges[instruction.target] = DamageRange(value, value)

        return InherentFilter(inherent=inherent, ranges=ranges)


WeaponRequirementRanges: TypeAlias = dict[int, RequirementFilter]
InherentFilters: TypeAlias = list[InherentFilter]

ModelIdAndItemType = NamedTuple("ModelIdAndItemType", [("model_id", ModelID | int), ("item_type", ItemType)])
ModelFileIdAndItemType = NamedTuple("ModelFileIdAndItemType", [("model_file_id", int), ("item_type", ItemType)])
UpgradeAndItemType = NamedTuple("UpgradeAndItemType", [("upgrade", WeaponUpgrade | Inscription), ("item_types", list[ItemType])])
RangedUpgrade = NamedTuple(
    "RangedUpgrade",
    [("upgrade", WeaponUpgrade | Inscription), ("target", str), ("min_value", float), ("max_value", float), ("item_types", list[ItemType])],
)


@dataclass
class ConditionEvaluationContext:
    item_id: int
    item_snapshot: Optional[ItemSnapshot]
    cache: dict[str, Any] = field(default_factory=dict)


def _default_damage_range(item_type: Optional[ItemType], requirement: int) -> DamageRange:
    if item_type is None:
        return DamageRange(0, 0)

    min_value, max_value = DAMAGE_RANGES.get(item_type, {}).get(requirement, (0, 0))
    return DamageRange(min_value, max_value)


def _normalize_attribute_list(attributes: Any) -> list[Attribute]:
    normalized: list[Attribute] = []
    if not isinstance(attributes, list):
        return normalized

    for attribute in attributes:
        if isinstance(attribute, Attribute):
            if attribute not in normalized and attribute != Attribute.None_:
                normalized.append(attribute)
            continue

        if isinstance(attribute, str) and attribute in Attribute.__members__:
            parsed_attribute = Attribute[attribute]
            if parsed_attribute not in normalized and parsed_attribute != Attribute.None_:
                normalized.append(parsed_attribute)

    return normalized


def _normalize_requirement_filter(value: Any) -> RequirementFilter | None:
    if isinstance(value, RequirementFilter):
        return RequirementFilter(
            value_range=DamageRange(int(value.value_range.min_value), int(value.value_range.max_value)),
            allowed_attributes=_normalize_attribute_list(value.allowed_attributes),
            disallowed_attributes=_normalize_attribute_list(value.disallowed_attributes),
        )

    if isinstance(value, DamageRange):
        return RequirementFilter(
            value_range=DamageRange(int(value.min_value), int(value.max_value)),
        )

    return None


def normalize_requirement_ranges(
    requirements: Optional[WeaponRequirementRanges],
    item_type: Optional[ItemType] = None,
    requirement_min: int = 0,
    requirement_max: int = 13,
) -> WeaponRequirementRanges:
    if requirements is not None:
        normalized: WeaponRequirementRanges = {}
        for requirement, value in requirements.items():
            normalized_filter = _normalize_requirement_filter(value)
            if normalized_filter is None:
                continue
            normalized[int(requirement)] = normalized_filter
        return normalized

    return {}


def serialize_requirement_ranges(requirements: WeaponRequirementRanges) -> list[dict[str, Any]]:
    return [
        {
            "requirement": requirement,
            "min_value": requirement_filter.value_range.min_value,
            "max_value": requirement_filter.value_range.max_value,
            "allowed_attributes": [attribute.name for attribute in requirement_filter.allowed_attributes],
            "disallowed_attributes": [attribute.name for attribute in requirement_filter.disallowed_attributes],
        }
        for requirement, requirement_filter in sorted(requirements.items())
    ]


def deserialize_requirement_ranges(data: dict[str, Any], item_type: Optional[ItemType] = None) -> WeaponRequirementRanges:
    raw_requirements = data.get("requirements")
    if isinstance(raw_requirements, list):
        requirements: WeaponRequirementRanges = {}
        for entry in raw_requirements:
            if not isinstance(entry, dict):
                continue

            requirement = entry.get("requirement")
            min_value = entry.get("min_value")
            max_value = entry.get("max_value")
            if isinstance(requirement, int) and isinstance(min_value, int) and isinstance(max_value, int):
                requirements[requirement] = RequirementFilter(
                    value_range=DamageRange(min_value, max_value),
                    allowed_attributes=_normalize_attribute_list(entry.get("allowed_attributes", [])),
                    disallowed_attributes=_normalize_attribute_list(entry.get("disallowed_attributes", [])),
                )

        return requirements

    return normalize_requirement_ranges(
        None,
        item_type,
        int(data.get("requirement_min", 0)),
        int(data.get("requirement_max", 13)),
    )


def requirement_range_matches(item_snapshot: ItemSnapshot, requirements: WeaponRequirementRanges) -> bool:
    requirement_filter = requirements.get(int(item_snapshot.requirement))
    if requirement_filter is None:
        return False

    if int(item_snapshot.requirement) == 0:
        return item_snapshot.attribute == Attribute.None_

    value_range = requirement_filter.value_range
    if value_range.min_value == 0 and value_range.max_value == 0:
        value_range = _default_damage_range(item_snapshot.item_type, item_snapshot.requirement)

    if item_snapshot.min_damage < value_range.min_value or item_snapshot.max_damage > value_range.max_value:
        return False

    item_attribute = item_snapshot.attribute
    if item_attribute in requirement_filter.disallowed_attributes:
        return False

    if requirement_filter.allowed_attributes and item_attribute not in requirement_filter.allowed_attributes:
        return False

    return True


def requirement_comparison_data(requirements: WeaponRequirementRanges) -> tuple[Any, ...]:
    return tuple(
        sorted(
            (
                requirement,
                requirement_filter.value_range.min_value,
                requirement_filter.value_range.max_value,
                tuple(attribute.name for attribute in requirement_filter.allowed_attributes),
                tuple(attribute.name for attribute in requirement_filter.disallowed_attributes),
            )
            for requirement, requirement_filter in requirements.items()
        )
    )


def requirement_ranges_to_attribute_requirements(
    requirements: Optional[WeaponRequirementRanges],
    item_type: Optional[ItemType] = None,
    requirement_min: int = 0,
    requirement_max: int = 13,
) -> list["AttributeRequirement"]:
    normalized = normalize_requirement_ranges(requirements, item_type, requirement_min, requirement_max)
    converted: list[AttributeRequirement] = []
    selected_weapon_type = cast(Optional[WeaponType], item_type) if item_type in WEAPON_TYPES else None

    for attribute_level, requirement_filter in sorted(normalized.items()):
        requirement = AttributeRequirement(
            attribute=list(requirement_filter.allowed_attributes),
            attribute_level=int(attribute_level),
            weapon_type=selected_weapon_type,
        )
        if selected_weapon_type is not None:
            requirement.apply_max_ranges(selected_weapon_type)

        value_range = requirement_filter.value_range
        if value_range.min_value != 0 or value_range.max_value != 0:
            requirement.min_values = (int(value_range.min_value), int(value_range.max_value))

        converted.append(requirement)

    return converted


def attribute_requirements_to_requirement_ranges(requirements: Sequence["AttributeRequirement"]) -> WeaponRequirementRanges:
    converted: WeaponRequirementRanges = {}
    for requirement in requirements:
        converted[int(requirement.attribute_level)] = RequirementFilter(
            value_range=DamageRange(int(requirement.min_values[0]), int(requirement.min_values[1])),
            allowed_attributes=list(requirement.attributes),
            disallowed_attributes=[],
        )

    return converted


def _normalize_range_bounds(min_value: Any, max_value: Any, fallback: DamageRange) -> DamageRange:
    try:
        normalized_min = int(min_value)
        normalized_max = int(max_value)
    except (TypeError, ValueError):
        return fallback

    if normalized_min > normalized_max:
        normalized_min, normalized_max = normalized_max, normalized_min

    return DamageRange(normalized_min, normalized_max)


def normalize_inherent_filters(inherents: Optional[Sequence[InherentFilter | Inherent]]) -> InherentFilters:
    if inherents is None:
        return []

    normalized: InherentFilters = []
    for inherent in inherents:
        if isinstance(inherent, InherentFilter):
            normalized.append(inherent)
        elif isinstance(inherent, Inherent):
            normalized.append(InherentFilter.from_inherent(inherent))

    return normalized


def serialize_inherent_filters(inherents: InherentFilters) -> list[dict[str, Any]]:
    return [
        {
            "inherent": inherent_filter.inherent.to_dict(),
            "ranges": [
                {
                    "target": target,
                    "min_value": value_range.min_value,
                    "max_value": value_range.max_value,
                }
                for target, value_range in sorted(inherent_filter.ranges.items())
            ],
        }
        for inherent_filter in inherents
    ]


def _deserialize_inherent_range_filters(entry: dict[str, Any], inherent: Inherent) -> dict[str, DamageRange]:
    default_filter = InherentFilter.from_inherent(inherent)
    ranges = dict(default_filter.ranges)
    raw_ranges = entry.get("ranges", [])

    if isinstance(raw_ranges, dict):
        raw_ranges = [
            {**value, "target": target}
            for target, value in raw_ranges.items()
            if isinstance(value, dict)
        ]

    if not isinstance(raw_ranges, list):
        return ranges

    for raw_range in raw_ranges:
        if not isinstance(raw_range, dict):
            continue

        target = raw_range.get("target")
        if not isinstance(target, str) or target not in ranges:
            continue

        ranges[target] = _normalize_range_bounds(
            raw_range.get("min_value"),
            raw_range.get("max_value"),
            ranges[target],
        )

    return ranges


def deserialize_inherent_filters(data: dict[str, Any]) -> InherentFilters:
    raw_inherents = data.get("inherents", [])
    if not raw_inherents:
        raw_inherents = data.get("properties", [])

    inherents: InherentFilters = []
    for entry in raw_inherents:
        if not isinstance(entry, dict):
            continue

        raw_upgrade = entry.get("inherent", entry)
        if not isinstance(raw_upgrade, dict):
            continue

        upgrade = Upgrade.from_dict(raw_upgrade)
        if isinstance(upgrade, Inherent):
            if "inherent" in entry:
                ranges = _deserialize_inherent_range_filters(entry, upgrade)
            else:
                ranges = InherentFilter.from_inherent(upgrade).ranges
            inherents.append(InherentFilter(inherent=upgrade, ranges=ranges))

    return inherents


def _inherent_range_targets(inherent: Inherent) -> set[str]:
    return {
        instruction.target
        for instruction in type(inherent).upgrade_info
        if isinstance(instruction, RangeInstruction)
    }


def _inherent_fixed_values(inherent: Inherent) -> dict[str, Any]:
    range_targets = _inherent_range_targets(inherent)
    return {
        property_name: Upgrade._normalize_comparison_value(getattr(inherent, property_name))
        for property_name in type(inherent)._get_serializable_property_names()
        if property_name not in range_targets
    }


def _single_inherent_filter_matches(expected: InherentFilter, actual: Upgrade) -> bool:
    if type(actual) is not type(expected.inherent):
        return False

    if not isinstance(actual, Inherent):
        return False

    if _inherent_fixed_values(expected.inherent) != _inherent_fixed_values(actual):
        return False

    for target, value_range in expected.ranges.items():
        actual_value = getattr(actual, target, None)
        if actual_value is None or actual_value < value_range.min_value or actual_value > value_range.max_value:
            return False

    return True


def inherent_filter_matches(expected: InherentFilter, item_inherents: list[Upgrade]) -> bool:
    return any(_single_inherent_filter_matches(expected, inherent) for inherent in item_inherents)


def inherent_comparison_data(inherents: InherentFilters) -> tuple[Any, ...]:
    return tuple(
        sorted(
            (
                type(inherent_filter.inherent).__name__,
                tuple(sorted(_inherent_fixed_values(inherent_filter.inherent).items())),
                tuple(sorted(inherent_filter.ranges.items())),
            )
            for inherent_filter in inherents
        )
    )


class Condition:
    """Base condition that checks one reusable rule fragment against an item."""
    _registry: ClassVar[dict[str, type["Condition"]]] = {}
    ui_selectable: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Condition._registry[cls.__name__] = cls

    def is_valid(self) -> bool:
        return True

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        raise NotImplementedError("Subclasses must implement evaluate().")

    def _comparison_data(self) -> Any:
        return ()

    def equals(self, other: object) -> bool:
        return isinstance(other, Condition) and type(self) is type(other) and self._comparison_data() == other._comparison_data()

    def __eq__(self, other: object) -> bool:
        return self.equals(other)

    def _serialize_data(self) -> dict[str, Any]:
        return {}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        return

    def to_dict(self) -> dict[str, Any]:
        payload = {"condition_type": type(self).__name__}
        payload.update(self._serialize_data())
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Condition | None":
        condition_type_name = str(payload.get("condition_type", ""))
        condition_cls = cls._registry.get(condition_type_name)
        if condition_cls is None:
            return None

        try:
            condition = condition_cls()
            condition._deserialize_data(payload)
            return condition
        except Exception:
            return None


class ModelIdsCondition(Condition):
    """Matches items whose model ID is in the configured list."""
    def __init__(self, model_ids: Optional[list[ModelID | int]] = None):
        self.model_ids: list[ModelID | int] = model_ids if model_ids is not None else []

    def is_valid(self) -> bool:
        return len(self.model_ids) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None or item_snapshot.model_id is None:
            return False

        for model_id in self.model_ids:
            if isinstance(model_id, ModelID) and item_snapshot.model_id == model_id.value:
                return True
            if item_snapshot.model_id == model_id:
                return True

        return False

    def _comparison_data(self) -> Any:
        normalized_model_ids = {
            int(model_id.value) if isinstance(model_id, ModelID) else int(model_id)
            for model_id in self.model_ids
        }
        return tuple(sorted(normalized_model_ids))

    def _serialize_data(self) -> dict[str, Any]:
        return {"model_ids": [int(model_id.value) if isinstance(model_id, ModelID) else int(model_id) for model_id in self.model_ids]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_ids = []
        for model_id in data.get("model_ids", []):
            if not isinstance(model_id, int):
                continue

            try:
                self.model_ids.append(ModelID(model_id))
            except ValueError:
                self.model_ids.append(model_id)


class ItemTypesCondition(Condition):
    """Matches items whose item type is one of the selected types."""
    def __init__(self, item_types: Optional[list[ItemType]] = None):
        self.item_types: list[ItemType] = item_types if item_types is not None else []

    def is_valid(self) -> bool:
        return len(self.item_types) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        return any(item_snapshot.item_type.matches(target_type) for target_type in self.item_types)

    def _comparison_data(self) -> Any:
        return tuple(sorted(item_type.name for item_type in self.item_types))

    def _serialize_data(self) -> dict[str, Any]:
        return {"item_types": [item_type.name for item_type in self.item_types]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.item_types = [
            ItemType[name]
            for name in data.get("item_types", [])
            if isinstance(name, str) and name in ItemType.__members__
        ]


class ExactItemTypeCondition(Condition):
    """Matches items whose type matches one exact item type."""
    def __init__(self, item_type: Optional[ItemType] = None):
        self.item_type = item_type

    def is_valid(self) -> bool:
        return self.item_type is not None

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        return item_snapshot is not None and self.item_type is not None and item_snapshot.item_type == self.item_type

    def _comparison_data(self) -> Any:
        return self.item_type.name if self.item_type is not None else None

    def _serialize_data(self) -> dict[str, Any]:
        return {"item_type": self.item_type.name if self.item_type is not None else None}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        item_type_name = data.get("item_type")
        self.item_type = ItemType[item_type_name] if isinstance(item_type_name, str) and item_type_name in ItemType.__members__ else None


class ModelIdsAndItemTypesCondition(Condition):
    """Matches specific combinations of model ID and item type."""
    def __init__(self, items: Optional[list[ModelIdAndItemType]] = None):
        self.modelids_and_itemtypes: list[ModelIdAndItemType] = items if items is not None else []

    def is_valid(self) -> bool:
        return len(self.modelids_and_itemtypes) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        for model_id, item_type in self.modelids_and_itemtypes:
            normalized_model_id = model_id.value if isinstance(model_id, ModelID) else model_id
            if item_snapshot.model_id == normalized_model_id and item_snapshot.item_type.matches(item_type):
                return True

        return False

    def _comparison_data(self) -> Any:
        return tuple(
            sorted(
                (
                    int(model_id.value) if isinstance(model_id, ModelID) else int(model_id),
                    item_type.name,
                )
                for model_id, item_type in self.modelids_and_itemtypes
            )
        )

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "model_id": int(model_id.value) if isinstance(model_id, ModelID) else int(model_id),
                    "item_type": item_type.name,
                }
                for model_id, item_type in self.modelids_and_itemtypes
            ]
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.modelids_and_itemtypes = []
        for entry in data.get("items", []):
            if not isinstance(entry, dict):
                continue

            model_id = entry.get("model_id")
            item_type_name = entry.get("item_type")
            if not isinstance(model_id, int) or not isinstance(item_type_name, str) or item_type_name not in ItemType.__members__:
                continue

            try:
                normalized_model_id: ModelID | int = ModelID(model_id)
            except ValueError:
                normalized_model_id = model_id

            self.modelids_and_itemtypes.append(ModelIdAndItemType(normalized_model_id, ItemType[item_type_name]))


class EncodedNamesCondition(Condition):
    """Matches items by their encoded name bytes."""
    def __init__(self, encoded_names: Optional[list[bytes]] = None):
        self.encoded_names: list[bytes] = encoded_names if encoded_names is not None else []

    def is_valid(self) -> bool:
        return len(self.encoded_names) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None or item_snapshot.name_enc is None:
            return False

        return item_snapshot.name_enc in self.encoded_names

    def _comparison_data(self) -> Any:
        return tuple(sorted(self.encoded_names))

    def _serialize_data(self) -> dict[str, Any]:
        return {"encoded_names": [list(name) for name in self.encoded_names]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        encoded_names: list[bytes] = []
        for value in data.get("encoded_names", []):
            if isinstance(value, list) and all(isinstance(part, int) for part in value):
                encoded_names.append(bytes(value))

        self.encoded_names = encoded_names


class ModelFileIdsCondition(Condition):
    """Matches items whose model file ID is in the configured list."""
    def __init__(self, model_file_ids: Optional[list[int]] = None):
        self.model_file_ids: list[int] = model_file_ids if model_file_ids is not None else []

    def is_valid(self) -> bool:
        return len(self.model_file_ids) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        return item_snapshot is not None and item_snapshot.model_file_id in self.model_file_ids

    def _comparison_data(self) -> Any:
        return tuple(sorted(self.model_file_ids))

    def _serialize_data(self) -> dict[str, Any]:
        return {"model_file_ids": list(self.model_file_ids)}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_file_ids = [model_file_id for model_file_id in data.get("model_file_ids", []) if isinstance(model_file_id, int)]


class ModelFileIdsAndItemTypesCondition(Condition):
    """Matches specific combinations of model file ID and item type."""
    def __init__(self, items: Optional[list[ModelFileIdAndItemType]] = None):
        self.model_file_ids_and_item_types: list[ModelFileIdAndItemType] = items if items is not None else []

    def is_valid(self) -> bool:
        return len(self.model_file_ids_and_item_types) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        return any(
            item_snapshot.model_file_id == entry.model_file_id and item_snapshot.item_type.matches(entry.item_type)
            for entry in self.model_file_ids_and_item_types
        )

    def _comparison_data(self) -> Any:
        return tuple(sorted((entry.model_file_id, entry.item_type.name) for entry in self.model_file_ids_and_item_types))

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "model_file_id": entry.model_file_id,
                    "item_type": entry.item_type.name,
                }
                for entry in self.model_file_ids_and_item_types
            ]
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_file_ids_and_item_types = []
        for entry in data.get("items", []):
            if not isinstance(entry, dict):
                continue

            model_file_id = entry.get("model_file_id")
            item_type_name = entry.get("item_type")
            if not isinstance(model_file_id, int) or not isinstance(item_type_name, str) or item_type_name not in ItemType.__members__:
                continue

            self.model_file_ids_and_item_types.append(ModelFileIdAndItemType(model_file_id=model_file_id, item_type=ItemType[item_type_name]))


class StackQuantityCondition(Condition):
    """Matches items whose stack quantity falls inside the configured inclusive range."""
    def __init__(self, min_quantity: int = 0, max_quantity: int = 250):
        self.min_quantity = max(0, min(250, int(min_quantity)))
        self.max_quantity = max(0, min(250, int(max_quantity)))
        if self.min_quantity > self.max_quantity:
            self.min_quantity, self.max_quantity = self.max_quantity, self.min_quantity

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        return item_snapshot is not None and self.min_quantity <= item_snapshot.quantity <= self.max_quantity

    def _comparison_data(self) -> Any:
        return (self.min_quantity, self.max_quantity)

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "min_quantity": self.min_quantity,
            "max_quantity": self.max_quantity,
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        min_quantity = data.get("min_quantity", 0)
        max_quantity = data.get("max_quantity", 250)
        self.min_quantity = max(0, min(250, int(min_quantity if isinstance(min_quantity, int) else 0)))
        self.max_quantity = max(0, min(250, int(max_quantity if isinstance(max_quantity, int) else 250)))
        if self.min_quantity > self.max_quantity:
            self.min_quantity, self.max_quantity = self.max_quantity, self.min_quantity


class AttributeRequirement:
    def __init__(self, attribute : list[Attribute] = [], attribute_level: int = 0, weapon_type: Optional[WeaponType] = None):
        self.attributes = attribute
        self.weapon_type : ItemType = ItemType.Unknown if weapon_type is None else weapon_type
        
        self.attribute_level : int = attribute_level
        self.min_values : tuple[int, int] = (0, 0)
            
    def to_dict(self) -> dict[str, Any]:
        return {
            "attributes": [attribute.name for attribute in self.attributes],
            "attribute_level": self.attribute_level,
            "weapon_type": self.weapon_type.name,
            "min_values": self.min_values,
        }
        
    @staticmethod
    def from_dict(data: dict[str, Any]) -> Optional["AttributeRequirement"]:        
        requirement = AttributeRequirement()
        
        attribute_names = data.get("attributes", [])
        attribute_level = data.get("attribute_level", 0)
        weapon_type_name = data.get("weapon_type")
        min_values = data.get("min_values", (0, 0))
        
        if isinstance(attribute_names, list):
            requirement.attributes = [Attribute[name] for name in attribute_names if name in Attribute.__members__]
        
        if isinstance(attribute_level, int):
            requirement.attribute_level = attribute_level

        if isinstance(weapon_type_name, str) and weapon_type_name in ItemType.__members__:
            weapon_type = ItemType[weapon_type_name]
            
            if weapon_type == ItemType.Unknown or weapon_type in WEAPON_TYPES:
                requirement.weapon_type = weapon_type

        if isinstance(min_values, (list, tuple)) and len(min_values) == 2 and all(isinstance(value, int) for value in min_values):
            requirement.min_values = (min_values[0], min_values[1])
            
        return requirement
    
    def get_ranges_for_weapon_type(self, item_type: ItemType, attribute_level : Optional[int] = None) -> Optional[tuple[tuple[int, int], tuple[int, int]]]:
        attribute_level = attribute_level if attribute_level is not None else self.attribute_level

        if item_type.is_weapon_type():
            if (ranges := DAMAGE_RANGES.get(item_type)) and ranges is not None:
                normalized_requirement = min(max(0, int(attribute_level)), 9)
                if (req_0_range := ranges.get(0)) is not None and (max_range := ranges.get(normalized_requirement)) is not None:
                    return req_0_range, max_range

        return None
    
    @staticmethod
    def _clamp(value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(value, maximum))
    
    def apply_max_ranges(self, item_type : ItemType):
        self.weapon_type = item_type

        if (ranges := self.get_ranges_for_weapon_type(item_type, self.attribute_level)) is None:
            return
            
        req_0, max_range = ranges

        if req_0 is None or max_range is None:
            return

        self.min_values = (
            int(max_range[0]),
            int(max_range[1]),
        )
    
    @property
    def has_damage_ranges(self) -> bool:
        return self.weapon_type.is_weapon_type() and not self.weapon_type in [ItemType.Offhand, ItemType.Shield]
    
    @property
    def has_armor_range(self) -> bool:
        return self.weapon_type == ItemType.Shield
    
    @property
    def has_energy_range(self) -> bool:
        return self.weapon_type == ItemType.Offhand   
    
    
class WeaponRequirementCondition(Condition):
    """Matches weapons with any specified requirement for a certain attribute."""

    def __init__(self, requirements: Optional[list[AttributeRequirement]] = None):
        self.requirements: list[AttributeRequirement] = requirements if requirements is not None else []

    def is_valid(self) -> bool:
        return len(self.requirements) > 0
    
    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        for requirement in self.requirements:
            if requirement.weapon_type not in WEAPON_TYPES:
                continue

            if not item_snapshot.item_type.matches(requirement.weapon_type):
                continue

            if item_snapshot.requirement != requirement.attribute_level:
                continue

            if requirement.attribute_level > 0 and (not requirement.attributes or item_snapshot.attribute not in requirement.attributes):
                continue

            if requirement.has_energy_range and (item_snapshot.energy is None or item_snapshot.energy < requirement.min_values[0]):
                continue
            
            if requirement.has_energy_range and (item_snapshot.energy is None or item_snapshot.energy > requirement.min_values[1]):
                continue

            if requirement.has_armor_range and (item_snapshot.armor is None or item_snapshot.armor < requirement.min_values[0]):
                continue
            
            if requirement.has_armor_range and (item_snapshot.armor is None or item_snapshot.armor > requirement.min_values[1]):
                continue

            if requirement.has_damage_ranges:
                if item_snapshot.min_damage is None or item_snapshot.max_damage is None:
                    continue

                if item_snapshot.min_damage < requirement.min_values[0] or item_snapshot.max_damage < requirement.min_values[1]:
                    continue
            
            return True

        return False
    
    def _comparison_data(self) -> Any:
        return tuple(
            sorted(
                (
                    tuple(attribute.name for attribute in requirement.attributes),
                    requirement.attribute_level,
                    requirement.weapon_type.name,
                    requirement.min_values,
                )
                for requirement in self.requirements
            )
        )
        
    def _serialize_data(self) -> dict[str, Any]:
        return {
            "requirements": [requirement.to_dict() for requirement in self.requirements],
        }
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        raw_requirements = data.get("requirements", [])
        self.requirements = []
        for raw_requirement in raw_requirements:
            if not isinstance(raw_requirement, dict):
                continue
            
            requirement = AttributeRequirement.from_dict(raw_requirement)
            if requirement is not None:
                # requirement.apply_max_ranges(requirement.weapon_type)
                self.requirements.append(requirement)


class QuantityMatchCondition(Condition):
    """Partitions same-kind inventory stacks into kept and excess groups, then matches the configured group."""
    COUNT_MODE_TOTAL_QUANTITY: ClassVar[str] = "total_quantity"
    COUNT_MODE_FULL_STACKS: ClassVar[str] = "full_stacks"
    COUNT_MODES: ClassVar[tuple[str, ...]] = (
        COUNT_MODE_TOTAL_QUANTITY,
        COUNT_MODE_FULL_STACKS,
    )
    COUNT_SCOPE_INVENTORY_ONLY: ClassVar[str] = "inventory_only"
    COUNT_SCOPE_INVENTORY_AND_STORAGE: ClassVar[str] = "inventory_and_storage"
    COUNT_SCOPES: ClassVar[tuple[str, ...]] = (
        COUNT_SCOPE_INVENTORY_ONLY,
        COUNT_SCOPE_INVENTORY_AND_STORAGE,
    )

    def __init__(
        self,
        keep_quantity: int = MAX_STACK_SIZE,
        match_excess: bool = True,
        count_mode: str = COUNT_MODE_TOTAL_QUANTITY,
        count_scope: str = COUNT_SCOPE_INVENTORY_ONLY,
    ):
        self.quantity_limit = max(0, min(5000, int(keep_quantity)))
        self.match_excess = bool(match_excess)
        self.count_mode = count_mode if count_mode in self.COUNT_MODES else self.COUNT_MODE_TOTAL_QUANTITY
        self.count_scope = count_scope if count_scope in self.COUNT_SCOPES else self.COUNT_SCOPE_INVENTORY_ONLY

    def _threshold_quantity(self) -> int:
        threshold = max(0, self.quantity_limit)
        if self.count_mode == self.COUNT_MODE_FULL_STACKS:
            return threshold * MAX_STACK_SIZE
        return threshold

    def _counted_bags(self) -> list[Any]:
        return [*INVENTORY_BAGS, *STORAGE_BAGS] if self.count_scope == self.COUNT_SCOPE_INVENTORY_AND_STORAGE else list(INVENTORY_BAGS)

    def _measured_quantity(self, item_snapshot: ItemSnapshot) -> int:
        return max(0, int(item_snapshot.quantity))

    def _select_kept_item_ids(self, matching_items: list[ItemSnapshot], keep_quantity: int) -> set[int]:
        if keep_quantity <= 0:
            return set()

        reachable: dict[int, tuple[int, tuple[int, ...]]] = {0: (0, tuple())}
        for inventory_item in matching_items:
            quantity = self._measured_quantity(inventory_item)
            if quantity <= 0:
                continue

            next_reachable = dict(reachable)
            for total_quantity, (item_count, item_ids) in reachable.items():
                new_total = total_quantity + quantity
                new_entry = (item_count + 1, item_ids + (int(inventory_item.id),))
                existing_entry = next_reachable.get(new_total)
                if existing_entry is None or new_entry[0] < existing_entry[0]:
                    next_reachable[new_total] = new_entry
            reachable = next_reachable

        best_total: int | None = None
        best_item_count = 0
        best_item_ids: tuple[int, ...] = tuple()
        for total_quantity, (item_count, item_ids) in reachable.items():
            if total_quantity < keep_quantity:
                continue

            if best_total is None:
                best_total = total_quantity
                best_item_count = item_count
                best_item_ids = item_ids
                continue

            current_key = (
                item_count,
                total_quantity,
                item_ids,
            )
            best_key = (
                best_item_count,
                best_total,
                best_item_ids,
            )
            if current_key < best_key:
                best_total = total_quantity
                best_item_count = item_count
                best_item_ids = item_ids

        return set(best_item_ids)

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None or not item_snapshot.is_valid or (not item_snapshot.is_inventory_item and not item_snapshot.is_storage_item) or not item_snapshot.is_stackable:
            return False

        counted_bags = self._counted_bags()
        matching_items = [
            counted_item
            for counted_item in ItemSnapshot.get_bags_items(counted_bags)
            if counted_item.is_valid and counted_item.same_kind_as(item_snapshot)
        ]
        if not matching_items or not any(int(matching_item.id) == int(item_snapshot.id) for matching_item in matching_items):
            return False

        ordered_items = sorted(
            matching_items,
            key=lambda inventory_item: (int(inventory_item.bag.value), int(inventory_item.slot), int(inventory_item.id)),
        )
        
        threshold_quantity = self._threshold_quantity()
        total_quantity = sum(self._measured_quantity(inventory_item) for inventory_item in ordered_items)
        if total_quantity <= threshold_quantity:
            return not self.match_excess

        kept_item_ids = self._select_kept_item_ids(ordered_items, threshold_quantity)
        matches_excess = int(item_snapshot.id) not in kept_item_ids
        return matches_excess if self.match_excess else not matches_excess

    def _comparison_data(self) -> Any:
        return (self.quantity_limit, self.match_excess, self.count_mode, self.count_scope)

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "keep_quantity": self.quantity_limit,
            "match_excess": self.match_excess,
            "count_mode": self.count_mode,
            "count_scope": self.count_scope,
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        raw_value = data.get("keep_quantity", MAX_STACK_SIZE)
        self.quantity_limit = int(raw_value if isinstance(raw_value, int) else MAX_STACK_SIZE)
        self.match_excess = bool(data.get("match_excess", True))
        raw_count_mode = data.get("count_mode", self.COUNT_MODE_TOTAL_QUANTITY)
        self.count_mode = raw_count_mode if isinstance(raw_count_mode, str) and raw_count_mode in self.COUNT_MODES else self.COUNT_MODE_TOTAL_QUANTITY
        raw_count_scope = data.get("count_scope", self.COUNT_SCOPE_INVENTORY_ONLY)
        self.count_scope = raw_count_scope if isinstance(raw_count_scope, str) and raw_count_scope in self.COUNT_SCOPES else self.COUNT_SCOPE_INVENTORY_ONLY


class NickItemCondition(Condition):
    """Matches Nicholas the Traveler items whose next cycle happens within the configured number of weeks."""
    def __init__(self, weeks_before_next_cycle: int = 0):
        self.weeks_before_next_cycle = max(0, min(NICK_CYCLE_COUNT, int(weeks_before_next_cycle)))

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        item_data = item_snapshot.data if item_snapshot is not None else None
        weeks_until_next_nick = item_data.weeks_until_next_nick if item_data is not None else None
        return weeks_until_next_nick is not None and weeks_until_next_nick <= self.weeks_before_next_cycle

    def _comparison_data(self) -> Any:
        return self.weeks_before_next_cycle

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "weeks_before_next_cycle": self.weeks_before_next_cycle,
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        raw_value = data.get("weeks_before_next_cycle", 0)
        self.weeks_before_next_cycle = max(0, min(NICK_CYCLE_COUNT, int(raw_value if isinstance(raw_value, int) else 0)))


class IsMaterialCondition(Condition):
    """Matches common and rare materials, or only rare materials when configured."""
    def __init__(self, rare_materials: bool = True, common_materials: bool = True):
        self.rare_materials = bool(rare_materials)
        self.common_materials = bool(common_materials)

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        model_id = int(item_snapshot.model_id)
        if self.rare_materials:
            return model_id in RARE_MATERIALS

        return model_id in COMMON_MATERIALS or model_id in RARE_MATERIALS

    def _comparison_data(self) -> Any:
        return self.rare_materials, self.common_materials

    def _serialize_data(self) -> dict[str, Any]:
        return {"rare_materials": self.rare_materials, "common_materials": self.common_materials}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.rare_materials = bool(data.get("rare_materials", False))
        self.common_materials = bool(data.get("common_materials", False))


class InherentFiltersCondition(Condition):
    """Matches weapon inherents, including optional numeric ranges on the inherent values."""
    def __init__(self, inherents: Optional[Sequence[InherentFilter | Inherent]] = None, inscribable: bool = False):
        self.inscribable = inscribable
        self.inherents = normalize_inherent_filters(inherents)

    def is_valid(self) -> bool:
        return len(self.inherents) > 0 or self.inscribable

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        item_inherents = item_snapshot.inherents if item_snapshot.inherents else []
        if self.inscribable and item_snapshot.is_inscribable:
            return True
        
        return any(inherent_filter_matches(inherent, item_inherents) for inherent in self.inherents)

    def _comparison_data(self) -> Any:
        return inherent_comparison_data(self.inherents), self.inscribable

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "inherents": serialize_inherent_filters(self.inherents),
            "inscribable": self.inscribable,
            }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.inherents = deserialize_inherent_filters(data)
        self.inscribable = bool(data.get("inscribable", True))


class InscribableCondition(Condition):
    """Matches items that are inscribable."""
    def __init__(self, inscribable: bool = True):
        super().__init__()
        self.inscribable = inscribable
        
    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        return context.item_snapshot is not None and context.item_snapshot.is_inscribable == self.inscribable

    def _comparison_data(self) -> Any:
        return (self.inscribable,)
    
    def _serialize_data(self) -> dict[str, Any]:
        return {"inscribable": self.inscribable}
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.inscribable = bool(data.get("inscribable", True))


class HalvesCastAndRechargeAttributeCondition(Condition):
    """Matches spellcasting weapons with either a HCT or HSR inherent sharing the same attribute as the weapon itself."""
    def __init__(self,):
        super().__init__()
        
    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return False

        item_inherents = item_snapshot.inherents or []
        upgrade = next((inherent for inherent in item_inherents if isinstance(inherent, (HalvesCastingTimeAttributeUpgrade, HalvesRechargeTimeAttributeUpgrade))), None)
        
        if upgrade is None:
            return False

        item_attribute = item_snapshot.attribute
        return item_attribute == upgrade.attribute


class SalvagesToMaterialsCondition(Condition):
    """Matches items that can salvage into one of the selected materials."""
    def __init__(self, materials: Optional[list[ModelID | int]] = None):
        self.materials: list[ModelID | int] = materials if materials is not None else []

    def is_valid(self) -> bool:
        return len(self.materials) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        if item_snapshot is None or not item_snapshot.is_salvageable or item_snapshot.data is None:
            return False

        common = [entry.model_id for entry in (item_snapshot.data.common_salvage.values() if item_snapshot.data.common_salvage else {})]
        rare = [entry.model_id for entry in (item_snapshot.data.rare_salvage.values() if item_snapshot.data.rare_salvage else {})]
        all_materials = set(common + rare)
        return any((material.value if isinstance(material, ModelID) else material) in all_materials for material in self.materials)

    def _comparison_data(self) -> Any:
        return tuple(sorted(int(material.value) if isinstance(material, ModelID) else int(material) for material in self.materials))

    def _serialize_data(self) -> dict[str, Any]:
        return {"materials": [int(material.value) if isinstance(material, ModelID) else int(material) for material in self.materials]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.materials = []
        for material in data.get("materials", []):
            if not isinstance(material, int):
                continue

            try:
                self.materials.append(ModelID(material))
            except ValueError:
                self.materials.append(material)


class RaritiesCondition(Condition):
    """Matches items whose rarity is one of the selected rarities."""
    def __init__(self, rarities: Optional[list[Rarity]] = None):
        self.rarities: list[Rarity] = rarities if rarities is not None else []

    def is_valid(self) -> bool:
        return len(self.rarities) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        return context.item_snapshot is not None and context.item_snapshot.rarity in self.rarities

    def _comparison_data(self) -> Any:
        return tuple(sorted(rarity.name for rarity in self.rarities))

    def _serialize_data(self) -> dict[str, Any]:
        return {"rarities": [rarity.name for rarity in self.rarities]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.rarities = [
            Rarity[name]
            for name in data.get("rarities", [])
            if isinstance(name, str) and name in Rarity.__members__
        ]


class UnidentifiedCondition(Condition):
    """Matches items that are still unidentified."""
    def __init__(self, identified: bool = False):
        super().__init__()
        self.identified = identified
        
    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        return context.item_snapshot is not None and context.item_snapshot.is_identified == self.identified

    def _comparison_data(self) -> Any:
        return (self.identified,)
    
    def _serialize_data(self) -> dict[str, Any]:
        return {"identified": self.identified}
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.identified = bool(data.get("identified", False))


class IsCustomizedCondition(Condition):
    """Matches items based on whether they are customized."""
    def __init__(self, customized: bool = True):
        super().__init__()
        self.customized = customized

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        return context.item_snapshot is not None and context.item_snapshot.is_customized == self.customized

    def _comparison_data(self) -> Any:
        return (self.customized,)

    def _serialize_data(self) -> dict[str, Any]:
        return {"customized": self.customized}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.customized = bool(data.get("customized", True))


class DyeColorsCondition(Condition):
    ui_selectable: ClassVar[bool] = False
    
    """Matches dye items whose color is one of the selected dye colors."""
    def __init__(self, dye_colors: Optional[list[DyeColor]] = None):
        self.dye_colors: list[DyeColor] = dye_colors if dye_colors is not None else []

    def is_valid(self) -> bool:
        return len(self.dye_colors) > 0

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        item_snapshot = context.item_snapshot
        return item_snapshot is not None and item_snapshot.item_type == ItemType.Dye and item_snapshot.color in self.dye_colors

    def _comparison_data(self) -> Any:
        return tuple(sorted(color.name for color in self.dye_colors))

    def _serialize_data(self) -> dict[str, Any]:
        return {"dye_colors": [color.name for color in self.dye_colors]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.dye_colors = [
            DyeColor[name]
            for name in data.get("dye_colors", [])
            if isinstance(name, str) and name in DyeColor.__members__
        ]


class UpgradeMatchCondition(Condition):
    """Base condition for matching extractable upgrades on items."""
    ui_selectable: ClassVar[bool] = False

    @staticmethod
    def _get_extractable_upgrades(item_id: int) -> list[tuple[Upgrade, SalvageMode]]:
        prefix, suffix, inscription, _ = ItemMod.get_item_upgrades(item_id)
        extractable_upgrades: list[tuple[Upgrade, SalvageMode]] = []

        if prefix is not None:
            extractable_upgrades.append((prefix, SalvageMode.Prefix))

        if suffix is not None:
            extractable_upgrades.append((suffix, SalvageMode.Suffix))

        if inscription is not None:
            extractable_upgrades.append((inscription, SalvageMode.Inscription))

        return extractable_upgrades

    @staticmethod
    def _get_upgrade_matching_item_type(item_id: int, item_snapshot: ItemSnapshot) -> Optional[ItemType]:
        item_type = item_snapshot.item_type
        if item_type == ItemType.Rune_Mod:
            item_type = ItemMod.get_target_item_type(item_id) or item_type

        return item_type

    @staticmethod
    def _dedupe_matching_upgrades(matches: list[tuple[Upgrade, SalvageMode]]) -> list[tuple[Upgrade, SalvageMode]]:
        deduped: list[tuple[Upgrade, SalvageMode]] = []
        seen_modes: set[SalvageMode] = set()

        for upgrade, salvage_mode in matches:
            if salvage_mode in seen_modes:
                continue

            seen_modes.add(salvage_mode)
            deduped.append((upgrade, salvage_mode))

        return deduped

    def get_matching_upgrades(self, context: ConditionEvaluationContext) -> list[tuple[Upgrade, SalvageMode]]:
        return []

    def evaluate(self, context: ConditionEvaluationContext) -> bool:
        return len(self.get_matching_upgrades(context)) > 0


class MaxWeaponUpgradesCondition(UpgradeMatchCondition):
    """Matches selected max-value weapon upgrades or inscriptions, optionally limited by item type."""
    ui_selectable: ClassVar[bool] = False

    def __init__(self, upgrades: Optional[list[UpgradeAndItemType]] = None):
        self.weapon_upgrades: list[UpgradeAndItemType] = upgrades if upgrades is not None else []

    def is_valid(self) -> bool:
        return len(self.weapon_upgrades) > 0

    def get_matching_upgrades(self, context: ConditionEvaluationContext) -> list[tuple[Upgrade, SalvageMode]]:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return []

        item_type = self._get_upgrade_matching_item_type(context.item_id, item_snapshot)
        extractable_upgrades = self._get_extractable_upgrades(context.item_id)
        matches: list[tuple[Upgrade, SalvageMode]] = []

        for selected_upgrade, valid_item_types in self.weapon_upgrades:
            if item_type is not None and valid_item_types and not any(item_type.matches(valid_type) for valid_type in valid_item_types):
                continue

            for item_upgrade, salvage_mode in extractable_upgrades:
                if isinstance(item_upgrade, (WeaponUpgrade, Inscription)) and selected_upgrade.matches(item_upgrade):
                    matches.append((item_upgrade, salvage_mode))

        return self._dedupe_matching_upgrades(matches)

    def _comparison_data(self) -> Any:
        return tuple(
            sorted(
                (
                    upgrade.upgrade._comparison_data(),
                    tuple(sorted(item_type.name for item_type in upgrade.item_types)),
                )
                for upgrade in self.weapon_upgrades
            )
        )

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "weapon_upgrades": [
                {
                    "upgrade": upgrade.upgrade.to_dict(),
                    "item_types": [item_type.name for item_type in upgrade.item_types],
                }
                for upgrade in self.weapon_upgrades
            ]
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.weapon_upgrades = []
        for entry in data.get("weapon_upgrades", []):
            if not isinstance(entry, dict):
                continue

            upgrade_data = entry.get("upgrade")
            if not isinstance(upgrade_data, dict):
                continue

            upgrade = Upgrade.from_dict(upgrade_data)
            if not isinstance(upgrade, (WeaponUpgrade, Inscription)):
                continue

            item_types = [
                ItemType[item_type_name]
                for item_type_name in entry.get("item_types", [])
                if isinstance(item_type_name, str) and item_type_name in ItemType.__members__
            ]
            self.weapon_upgrades.append(UpgradeAndItemType(upgrade=upgrade, item_types=item_types))


class ArmorUpgradesCondition(UpgradeMatchCondition):
    """Matches armor containing selected runes or insignias."""
    ui_selectable: ClassVar[bool] = False

    def __init__(self, upgrades: Optional[list[ArmorUpgrade]] = None):
        self.armor_upgrades: list[ArmorUpgrade] = upgrades if upgrades is not None else []

    def is_valid(self) -> bool:
        return len(self.armor_upgrades) > 0

    def get_matching_upgrades(self, context: ConditionEvaluationContext) -> list[tuple[Upgrade, SalvageMode]]:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return []

        extractable_upgrades = self._get_extractable_upgrades(context.item_id)
        matches: list[tuple[Upgrade, SalvageMode]] = []

        for armor_upgrade in self.armor_upgrades:
            for item_upgrade, salvage_mode in extractable_upgrades:
                if isinstance(item_upgrade, ArmorUpgrade) and armor_upgrade.matches(item_upgrade):
                    matches.append((item_upgrade, salvage_mode))

        return self._dedupe_matching_upgrades(matches)

    def _comparison_data(self) -> Any:
        return tuple(sorted(upgrade._comparison_data() for upgrade in self.armor_upgrades))

    def _serialize_data(self) -> dict[str, Any]:
        return {"armor_upgrades": [upgrade.to_dict() for upgrade in self.armor_upgrades]}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.armor_upgrades = []
        for entry in data.get("armor_upgrades", []):
            if not isinstance(entry, dict):
                continue

            upgrade = Upgrade.from_dict(entry)
            if isinstance(upgrade, ArmorUpgrade):
                self.armor_upgrades.append(upgrade)


class UpgradeRangesCondition(UpgradeMatchCondition):
    """Matches upgrades whose numeric values fall inside configured ranges."""
    ui_selectable: ClassVar[bool] = False

    def __init__(self, upgrade_ranges: Optional[list[RangedUpgrade]] = None):
        self.upgrade_ranges: list[RangedUpgrade] = upgrade_ranges if upgrade_ranges is not None else []

    def is_valid(self) -> bool:
        return len(self.upgrade_ranges) > 0

    def get_matching_upgrades(self, context: ConditionEvaluationContext) -> list[tuple[Upgrade, SalvageMode]]:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return []

        item_type = self._get_upgrade_matching_item_type(context.item_id, item_snapshot)
        extractable_upgrades = self._get_extractable_upgrades(context.item_id)
        matches: list[tuple[Upgrade, SalvageMode]] = []

        for upgrade_range in self.upgrade_ranges:
            if item_type is not None and upgrade_range.item_types and not any(item_type.matches(valid_type) for valid_type in upgrade_range.item_types):
                continue

            for item_upgrade, salvage_mode in extractable_upgrades:
                if not isinstance(item_upgrade, (WeaponUpgrade, Inscription)):
                    continue

                if not upgrade_range.upgrade.matches(item_upgrade):
                    continue

                upgrade_value = getattr(item_upgrade, upgrade_range.target, None)
                if isinstance(upgrade_value, (int, float)) and upgrade_range.min_value <= upgrade_value <= upgrade_range.max_value:
                    matches.append((item_upgrade, salvage_mode))

        return self._dedupe_matching_upgrades(matches)

    def _comparison_data(self) -> Any:
        return tuple(
            sorted(
                (
                    upgrade_range.upgrade._comparison_data(),
                    upgrade_range.target,
                    upgrade_range.min_value,
                    upgrade_range.max_value,
                    tuple(sorted(item_type.name for item_type in upgrade_range.item_types)),
                )
                for upgrade_range in self.upgrade_ranges
            )
        )

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "upgrade_ranges": [
                {
                    "upgrade": upgrade_range.upgrade.to_dict(),
                    "target": upgrade_range.target,
                    "min_value": upgrade_range.min_value,
                    "max_value": upgrade_range.max_value,
                    "item_types": [item_type.name for item_type in upgrade_range.item_types],
                }
                for upgrade_range in self.upgrade_ranges
            ]
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.upgrade_ranges = []
        for entry in data.get("upgrade_ranges", []):
            if not isinstance(entry, dict):
                continue

            upgrade_data = entry.get("upgrade")
            target = entry.get("target")
            min_value = entry.get("min_value")
            max_value = entry.get("max_value")
            if not isinstance(upgrade_data, dict) or not isinstance(target, str) or not isinstance(min_value, (int, float)) or not isinstance(max_value, (int, float)):
                continue

            upgrade = Upgrade.from_dict(upgrade_data)
            if not isinstance(upgrade, (WeaponUpgrade, Inscription)):
                continue

            valid_targets = {
                instruction.target
                for instruction in type(upgrade).upgrade_info
                if isinstance(instruction, RangeInstruction)
            }
            if target not in valid_targets:
                continue

            item_types = [
                ItemType[item_type_name]
                for item_type_name in entry.get("item_types", [])
                if isinstance(item_type_name, str) and item_type_name in ItemType.__members__
            ]
            self.upgrade_ranges.append(
                RangedUpgrade(
                    upgrade=upgrade,
                    target=target,
                    min_value=float(min_value),
                    max_value=float(max_value),
                    item_types=item_types,
                )
            )


class UpgradesCondition(UpgradeMatchCondition):
    """Matches selected upgrades without requiring them to be maxed or ranged."""
    ui_selectable: ClassVar[bool] = True

    def __init__(self, upgrades: Optional[list[tuple[Upgrade, list[ItemType]] | Upgrade]] = None):
        normalized_upgrades: list[tuple[Upgrade, list[ItemType]]] = []
        if upgrades is not None:
            for upgrade in upgrades:
                if isinstance(upgrade, Upgrade):
                    normalized_upgrades.append((upgrade, []))
                elif (
                    isinstance(upgrade, tuple)
                    and len(upgrade) == 2
                    and isinstance(upgrade[0], Upgrade)
                    and isinstance(upgrade[1], list)
                    and all(isinstance(item_type, ItemType) for item_type in upgrade[1])
                ):
                    normalized_upgrades.append((upgrade[0], upgrade[1]))

        self.upgrades: list[tuple[Upgrade, list[ItemType]]] = normalized_upgrades

    def is_valid(self) -> bool:
        return len(self.upgrades) > 0

    def get_matching_upgrades(self, context: ConditionEvaluationContext) -> list[tuple[Upgrade, SalvageMode]]:
        item_snapshot = context.item_snapshot
        if item_snapshot is None:
            return []

        item_type = self._get_upgrade_matching_item_type(context.item_id, item_snapshot)
        extractable_upgrades = self._get_extractable_upgrades(context.item_id)
        matches: list[tuple[Upgrade, SalvageMode]] = []

        for rule_upgrade, valid_item_types in self.upgrades:
            if item_type is not None and valid_item_types and not any(item_type.matches(valid_type) for valid_type in valid_item_types):
                continue

            for item_upgrade, salvage_mode in extractable_upgrades:
                if rule_upgrade.matches(item_upgrade):
                    matches.append((item_upgrade, salvage_mode))

        return self._dedupe_matching_upgrades(matches)

    def _comparison_data(self) -> Any:
        return tuple(
            sorted(
                (
                    upgrade._comparison_data(),
                    tuple(sorted(item_type.name for item_type in item_types)),
                )
                for upgrade, item_types in self.upgrades
            )
        )

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "upgrades": [
                {
                    "upgrade": upgrade.to_dict(),
                    "item_types": [item_type.name for item_type in item_types],
                }
                for upgrade, item_types in self.upgrades
            ]
        }

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.upgrades = []
        for entry in data.get("upgrades", []):
            if not isinstance(entry, dict):
                continue

            upgrade_data = entry.get("upgrade")
            if not isinstance(upgrade_data, dict):
                continue

            upgrade = Upgrade.from_dict(upgrade_data)
            if upgrade is None:
                continue

            item_types = [
                ItemType[name]
                for name in entry.get("item_types", [])
                if isinstance(name, str) and name in ItemType.__members__
            ]
            self.upgrades.append((upgrade, item_types))
