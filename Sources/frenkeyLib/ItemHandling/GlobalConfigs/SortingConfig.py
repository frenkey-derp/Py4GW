from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum, auto
from typing import Any, ClassVar, Optional, Self, cast

from Py4GWCoreLib.enums_src.Item_enums import Bags, ItemType, Rarity
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot

class SortField(StrEnum):
    ItemType = 'ItemType'
    ModelId = 'ModelId'
    Rarity = 'Rarity'
    Profession = 'Profession'
    Quantity = 'Quantity'
    Value = 'Value'
    Color = 'Color'
    Name = 'Name'
    Id = 'Id'


def _default_item_type_order() -> list[int]:
    item_type_order = [
        int(ItemType.Kit),
        int(ItemType.Key),
        int(ItemType.Usable),
        int(ItemType.Trophy),
        int(ItemType.Quest_Item),
        int(ItemType.Materials_Zcoins),
    ]
    item_type_order += [int(item_type) for item_type in ItemType if int(item_type) not in item_type_order]
    return item_type_order

class SortDirection(IntEnum):
    Ascending = auto()
    Descending = auto()

@dataclass(slots=True)
class SortArgument:
    field: SortField = SortField.ItemType
    direction: SortDirection = SortDirection.Ascending

    @property
    def display_name(self) -> str:
        return self.field.value

    def get_value(self, item: ItemSnapshot) -> Any:
        if self.field == SortField.ItemType:
            item_type_order = _default_item_type_order()
            if item.item_type == ItemType.Unknown:
                return len(item_type_order) + 1
            return item_type_order.index(item.item_type)
        if self.field == SortField.Profession:
            return int(item.profession)
        if self.field == SortField.ModelId:
            return int(item.model_id)
        if self.field == SortField.Rarity:
            return int(item.rarity.value)
        if self.field == SortField.Quantity:
            return int(item.quantity)
        if self.field == SortField.Value:
            return int(item.value)
        if self.field == SortField.Color:
            return int(item.color.value)
        if self.field == SortField.Name:
            return (item.complete_name or item.singular_name or item.name or '').lower()
        return int(item.id)

    def to_dict(self) -> dict[str, Any]:
        return {
            'field': self.field.value,
            'direction': self.direction.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SortArgument | None':
        field_name = data.get('field')
        if not isinstance(field_name, str) or field_name not in SortField._value2member_map_:
            return None
        direction_name = data.get('direction', 'Ascending')
        direction = SortDirection[direction_name] if direction_name in SortDirection.__members__ else SortDirection.Ascending
        return cls(
            field=SortField(field_name),
            direction=direction,
        )


def _default_sort_arguments() -> list[SortArgument]:
    return [
        SortArgument(SortField.ItemType, direction=SortDirection.Ascending),
        SortArgument(SortField.ModelId, direction=SortDirection.Ascending),
        SortArgument(SortField.Rarity, direction=SortDirection.Descending),
        SortArgument(SortField.Profession, direction=SortDirection.Ascending),
        SortArgument(SortField.Quantity, direction=SortDirection.Descending),
        SortArgument(SortField.Value, direction=SortDirection.Descending),
        SortArgument(SortField.Color, direction=SortDirection.Ascending),
        SortArgument(SortField.Id, direction=SortDirection.Ascending),
    ]


class Sorter:
    def __init__(self, arguments: Optional[list[SortArgument]] = None):
        self.arguments: list[SortArgument] = list(arguments) if arguments is not None else _default_sort_arguments()

    @property
    def display_name(self) -> str:
        if not self.arguments:
            return 'No Sort Arguments'
        preview = ', '.join(
            f'{argument.display_name} {argument.direction.name}'
            for argument in self.arguments[:3]
        )
        return f'{preview}{"..." if len(self.arguments) > 3 else ""}'

    @staticmethod
    def _invert_string(value: str) -> tuple[int, ...]:
        return tuple(-ord(character) for character in value)

    def _transform_value(self, value: Any, descending: bool) -> Any:
        if not descending:
            return value
        if isinstance(value, bool):
            return not value
        if isinstance(value, (int, float)):
            return -value
        if isinstance(value, str):
            return self._invert_string(value)
        if isinstance(value, tuple):
            return tuple(self._transform_value(entry, descending) for entry in value)
        return value

    def get_sort_key(self, item: ItemSnapshot) -> tuple[Any, ...]:
        key_parts = [
            self._transform_value(argument.get_value(item), argument.direction == SortDirection.Descending)
            for argument in self.arguments
        ]
        if not any(argument.field == SortField.Id for argument in self.arguments):
            key_parts.append(int(item.id))
        return tuple(key_parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            'arguments': [argument.to_dict() for argument in self.arguments],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | str | None) -> 'Sorter | None':
        if not isinstance(payload, dict):
            return None

        raw_arguments = payload.get('arguments', [])
        arguments: list[SortArgument] = []
        if isinstance(raw_arguments, list):
            for raw_argument in raw_arguments:
                if not isinstance(raw_argument, dict):
                    continue
                argument = SortArgument.from_dict(raw_argument)
                if argument is not None:
                    arguments.append(argument)

        return cls(arguments=arguments or _default_sort_arguments())


class DefaultSorter(Sorter):
    def __init__(self):
        super().__init__(_default_sort_arguments())


@dataclass(slots=True)
class SlotMatcherConfig:
    model_ids: list[ModelID | int] = field(default_factory=list)
    item_types: list[ItemType] = field(default_factory=list)
    rarities: list[Rarity] = field(default_factory=list)
    min_quantity: int = 0
    max_quantity: int = 250

    def matches(self, item: Optional[ItemSnapshot]) -> bool:
        if item is None or not item.is_valid:
            return False

        if self.model_ids:
            normalized_model_ids = {
                int(model_id.value) if isinstance(model_id, ModelID) else int(model_id)
                for model_id in self.model_ids
            }
            if int(item.model_id) not in normalized_model_ids:
                return False

        if self.item_types and not any(item.item_type.matches(item_type) for item_type in self.item_types):
            return False

        if self.rarities and item.rarity not in self.rarities:
            return False

        if item.quantity < self.min_quantity or item.quantity > self.max_quantity:
            return False

        return True

    def is_restrictive(self) -> bool:
        return bool(self.model_ids or self.item_types or self.rarities or self.min_quantity > 0 or self.max_quantity < 250)

    def summary(self) -> str:
        parts: list[str] = []
        if self.model_ids:
            parts.append(f'Model IDs: {len(self.model_ids)}')
        if self.item_types:
            parts.append(f'Item Types: {len(self.item_types)}')
        if self.rarities:
            parts.append(f'Rarities: {len(self.rarities)}')
        if self.min_quantity > 0 or self.max_quantity < 250:
            parts.append(f'Qty {self.min_quantity}-{self.max_quantity}')
        return ', '.join(parts) if parts else 'Any item'

    def to_dict(self) -> dict[str, Any]:
        return {
            'model_ids': [
                int(model_id.value) if isinstance(model_id, ModelID) else int(model_id)
                for model_id in self.model_ids
            ],
            'item_types': [item_type.name for item_type in self.item_types],
            'rarities': [rarity.name for rarity in self.rarities],
            'min_quantity': max(0, int(self.min_quantity)),
            'max_quantity': max(0, int(self.max_quantity)),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SlotMatcherConfig':
        raw_model_ids = data.get('model_ids', [])
        raw_item_types = data.get('item_types', [])
        raw_rarities = data.get('rarities', [])

        model_ids: list[ModelID | int] = []
        for model_id_raw in raw_model_ids if isinstance(raw_model_ids, list) else []:
            if not isinstance(model_id_raw, int):
                continue
            try:
                model_ids.append(ModelID(model_id_raw))
            except ValueError:
                model_ids.append(int(model_id_raw))

        item_types = [
            ItemType[item_type_name]
            for item_type_name in raw_item_types if isinstance(raw_item_types, list)
            if isinstance(item_type_name, str) and item_type_name in ItemType.__members__
        ]
        rarities = [
            Rarity[rarity_name]
            for rarity_name in raw_rarities if isinstance(raw_rarities, list)
            if isinstance(rarity_name, str) and rarity_name in Rarity.__members__
        ]

        min_quantity = max(0, int(data.get('min_quantity', 0) or 0))
        max_quantity = max(min_quantity, int(data.get('max_quantity', 250) or 250))
        return cls(
            model_ids=model_ids,
            item_types=item_types,
            rarities=rarities,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
        )


@dataclass(frozen=True, slots=True)
class SlotReference:
    bag: Bags
    slot: int

    def to_dict(self) -> dict[str, Any]:
        return {
            'bag': self.bag.name,
            'slot': max(0, int(self.slot)),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SlotReference | None':
        bag_name = data.get('bag')
        slot = data.get('slot')
        if not isinstance(bag_name, str) or bag_name not in Bags.__members__:
            return None
        if not isinstance(slot, int):
            return None
        return cls(bag=Bags[bag_name], slot=max(0, int(slot)))


@dataclass(slots=True)
class SlotGroupConfig:
    slot_refs: list[SlotReference] = field(default_factory=list)
    sorter: Sorter = field(default_factory=DefaultSorter)
    matcher: SlotMatcherConfig = field(default_factory=SlotMatcherConfig)
    name: str = ''
    enabled: bool = True
    is_default: bool = False

    def normalized_slot_refs(self) -> list[SlotReference]:
        unique_slot_refs = {
            SlotReference(slot_ref.bag, max(0, int(slot_ref.slot)))
            for slot_ref in self.slot_refs
            if isinstance(slot_ref, SlotReference)
        }
        return sorted(unique_slot_refs, key=lambda slot_ref: (slot_ref.bag.value, slot_ref.slot))

    def normalized_slots_for_bag(self, bag: Bags) -> list[int]:
        return [
            slot_ref.slot
            for slot_ref in self.normalized_slot_refs()
            if slot_ref.bag == bag
        ]

    def bags(self) -> list[Bags]:
        return sorted({slot_ref.bag for slot_ref in self.normalized_slot_refs()}, key=lambda bag: bag.value)

    def display_name(self) -> str:
        if self.is_default:
            return self.name.strip() or 'Default Sort Policy'
        return self.name.strip() or self.slot_range_text()

    def slot_range_text(self) -> str:
        if self.is_default:
            return 'All unassigned slots'
        slot_refs = self.normalized_slot_refs()
        if not slot_refs:
            return 'No Slots'
        grouped_slots: dict[Bags, list[int]] = {}
        for slot_ref in slot_refs:
            grouped_slots.setdefault(slot_ref.bag, []).append(slot_ref.slot)
        return ' | '.join(
            f'{bag.name}: {", ".join(str(slot) for slot in slots)}'
            for bag, slots in sorted(grouped_slots.items(), key=lambda item: item[0].value)
        )

    def owns_slot(self, bag: Bags, slot: int) -> bool:
        return any(slot_ref.bag == bag and slot_ref.slot == slot for slot_ref in self.normalized_slot_refs())

    def matches(self, item: Optional[ItemSnapshot]) -> bool:
        return self.enabled and self.matcher.matches(item)

    def to_dict(self) -> dict[str, Any]:
        return {
            'slot_refs': [slot_ref.to_dict() for slot_ref in self.normalized_slot_refs()],
            'sorter': self.sorter.to_dict(),
            'matcher': self.matcher.to_dict(),
            'name': self.name,
            'enabled': self.enabled,
            'is_default': self.is_default,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SlotGroupConfig | None':
        raw_sorter = data.get('sorter', data.get('sort_policy', 'DefaultSorter'))

        sorter = Sorter.from_dict(raw_sorter) or DefaultSorter()
        matcher_data = data.get('matcher', {})
        matcher = SlotMatcherConfig.from_dict(matcher_data if isinstance(matcher_data, dict) else {})
        slot_refs: list[SlotReference] = []
        raw_slot_refs = data.get('slot_refs', [])
        if isinstance(raw_slot_refs, list):
            for raw_slot_ref in raw_slot_refs:
                if not isinstance(raw_slot_ref, dict):
                    continue
                slot_ref = SlotReference.from_dict(raw_slot_ref)
                if slot_ref is not None:
                    slot_refs.append(slot_ref)
        else:
            bag_name = data.get('bag')
            raw_slots = data.get('slots', [])
            if isinstance(bag_name, str) and bag_name in Bags.__members__ and isinstance(raw_slots, list):
                for slot in raw_slots:
                    try:
                        slot_refs.append(SlotReference(Bags[bag_name], max(0, int(slot))))
                    except (TypeError, ValueError):
                        continue

        return cls(
            slot_refs=slot_refs,
            sorter=sorter,
            matcher=matcher,
            name=str(data.get('name', '') or ''),
            enabled=bool(data.get('enabled', True)),
            is_default=bool(data.get('is_default', False)),
        )


@dataclass(slots=True)
class BagSortPreviewEntry:
    bag: Bags
    slot: int
    item: Optional[ItemSnapshot]
    source_bag: Optional[Bags]
    source_slot: Optional[int]
    group_name: str
    group_summary: str
    sorter: Sorter
    used_fallback: bool = False


@dataclass(slots=True)
class BagSortPlan:
    layout: dict[Bags, dict[int, Optional[ItemSnapshot]]] = field(default_factory=dict)
    entries: list[BagSortPreviewEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SortingConfig:
    _initialized: bool = False
    _instance: ClassVar[Self | None] = None

    def __new__(cls: type[Self]) -> Self:
        instance = cast(Self | None, cls._instance)
        if instance is None:
            instance = cast(Self, super().__new__(cls))
            instance._initialized = False
            cls._instance = instance
        return instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self.default_group: SlotGroupConfig = SlotGroupConfig(
            sorter=DefaultSorter(),
            name='Default Sort Policy',
            enabled=True,
            is_default=True,
        )
        self.slot_groups: list[SlotGroupConfig] = []

    def get_groups_for_bag(self, bag: Bags) -> list[SlotGroupConfig]:
        return [
            group
            for group in self.slot_groups
            if group.enabled and group.normalized_slots_for_bag(bag)
        ]

    def get_group_for_slot(self, bag: Bags, slot: int) -> SlotGroupConfig | None:
        for group in self.slot_groups:
            if group.owns_slot(bag, slot):
                return group
        return None

    @property
    def default_sorter(self) -> Sorter:
        return self.default_group.sorter

    @default_sorter.setter
    def default_sorter(self, sorter: Sorter) -> None:
        self.default_group.sorter = sorter

    def to_dict(self) -> dict[str, Any]:
        return {
            'default_group': self.default_group.to_dict(),
            'slot_groups': [group.to_dict() for group in self.slot_groups],
        }

    def load_dict(self, data: dict[str, Any]) -> None:
        raw_default_group = data.get('default_group')
        
        if isinstance(raw_default_group, dict):
            default_group = SlotGroupConfig.from_dict(raw_default_group)
            if default_group is not None:
                default_group.is_default = True
                default_group.slot_refs = []
                if default_group.name.strip() == '':
                    default_group.name = 'Default Sort Policy'
                self.default_group = default_group
            else:
                self.default_group = SlotGroupConfig(sorter=DefaultSorter(), name='Default Sort Policy', enabled=True, is_default=True)
        else:
            raw_default_sorter = data.get('default_sorter', data.get('default_sort_policy', 'DefaultSorter'))
            self.default_group = SlotGroupConfig(
                sorter=Sorter.from_dict(raw_default_sorter) or DefaultSorter(),
                name='Default Sort Policy',
                enabled=True,
                is_default=True,
            )

        self.slot_groups.clear()
        raw_groups = data.get('slot_groups', [])
        if not isinstance(raw_groups, list):
            raw_groups = []

        for raw_group in raw_groups:
            if not isinstance(raw_group, dict):
                continue
            group = SlotGroupConfig.from_dict(raw_group)
            if group is not None:
                group.is_default = False
                self.slot_groups.append(group)

    @classmethod
    def Load(cls: type[Self], file_path: str) -> Self:
        if not os.path.isfile(file_path):
            return cls()

        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        instance = cls()
        instance.load_dict(json_data or {})
        return instance
