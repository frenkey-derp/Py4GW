from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional, Self, cast

from Py4GWCoreLib.enums_src.Item_enums import Bags, ItemType, Rarity
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot


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


def _base_sort_key(item: ItemSnapshot) -> tuple[Any, ...]:
    item_type_order = _default_item_type_order()
    return (
        item.item_type == ItemType.Unknown,
        item_type_order.index(item.item_type),
        item.model_id,
        -item.rarity.value,
        -item.quantity,
        -item.value,
        item.color.value,
        item.id,
    )


class Sorter:
    _registry: ClassVar[dict[str, type['Sorter']]] = {}
    ui_selectable: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Sorter._registry[cls.__name__] = cls

    @property
    def display_name(self) -> str:
        return type(self).__name__.removesuffix('Sorter')

    def get_sort_key(self, item: ItemSnapshot) -> Any:
        raise NotImplementedError('Subclasses must implement get_sort_key().')

    def _serialize_data(self) -> dict[str, Any]:
        return {}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        return

    def to_dict(self) -> dict[str, Any]:
        payload = {'sorter_type': type(self).__name__}
        payload.update(self._serialize_data())
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | str | None) -> 'Sorter | None':
        if isinstance(payload, str):
            payload = {'sorter_type': payload}

        if not isinstance(payload, dict):
            return None

        sorter_type_name = str(payload.get('sorter_type', ''))
        sorter_cls = cls._registry.get(sorter_type_name)
        if sorter_cls is None:
            return None

        sorter = sorter_cls()
        sorter._deserialize_data(payload)
        return sorter


class DefaultSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return _base_sort_key(item)


class QuantityDescSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return (-item.quantity, *_base_sort_key(item))


class QuantityAscSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return (item.quantity, *_base_sort_key(item))


class ValueDescSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return (-item.value, *_base_sort_key(item))


class ValueAscSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return (item.value, *_base_sort_key(item))


class RarityDescSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return (-item.rarity.value, *_base_sort_key(item))


class ModelIdAscSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return (item.model_id, *_base_sort_key(item))


class NameAscSorter(Sorter):
    def get_sort_key(self, item: ItemSnapshot) -> Any:
        return ((item.complete_name or item.singular_name or item.name or '').lower(), *_base_sort_key(item))


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


@dataclass(slots=True)
class SlotGroupConfig:
    bag: Bags
    slots: list[int] = field(default_factory=list)
    sorter: Sorter = field(default_factory=DefaultSorter)
    matcher: SlotMatcherConfig = field(default_factory=SlotMatcherConfig)
    name: str = ''
    enabled: bool = True

    def normalized_slots(self) -> list[int]:
        unique_slots = {
            max(0, int(slot))
            for slot in self.slots
            if isinstance(slot, int) or (isinstance(slot, str) and str(slot).strip().isdigit())
        }
        return sorted(unique_slots)

    def display_name(self) -> str:
        return self.name.strip() or f'{self.bag.name} [{self.slot_range_text()}]'

    def slot_range_text(self) -> str:
        slots = self.normalized_slots()
        return ', '.join(str(slot) for slot in slots) if slots else 'No Slots'

    def matches(self, item: Optional[ItemSnapshot]) -> bool:
        return self.enabled and self.matcher.matches(item)

    def to_dict(self) -> dict[str, Any]:
        return {
            'bag': self.bag.name,
            'slots': self.normalized_slots(),
            'sorter': self.sorter.to_dict(),
            'matcher': self.matcher.to_dict(),
            'name': self.name,
            'enabled': self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'SlotGroupConfig | None':
        bag_name = data.get('bag')
        if not isinstance(bag_name, str) or bag_name not in Bags.__members__:
            return None

        raw_sorter = data.get('sorter', data.get('sort_policy', 'DefaultSorter'))
        legacy_sorter_map = {
            'Default': 'DefaultSorter',
            'QuantityDesc': 'QuantityDescSorter',
            'QuantityAsc': 'QuantityAscSorter',
            'ValueDesc': 'ValueDescSorter',
            'ValueAsc': 'ValueAscSorter',
            'RarityDesc': 'RarityDescSorter',
            'ModelIdAsc': 'ModelIdAscSorter',
            'NameAsc': 'NameAscSorter',
        }
        if isinstance(raw_sorter, str):
            raw_sorter = legacy_sorter_map.get(raw_sorter, raw_sorter)
        sorter = Sorter.from_dict(raw_sorter) or DefaultSorter()
        matcher_data = data.get('matcher', {})
        matcher = SlotMatcherConfig.from_dict(matcher_data if isinstance(matcher_data, dict) else {})
        raw_slots = data.get('slots', [])

        slots: list[int] = []
        if isinstance(raw_slots, list):
            for slot in raw_slots:
                try:
                    slots.append(max(0, int(slot)))
                except (TypeError, ValueError):
                    continue

        return cls(
            bag=Bags[bag_name],
            slots=slots,
            sorter=sorter,
            matcher=matcher,
            name=str(data.get('name', '') or ''),
            enabled=bool(data.get('enabled', True)),
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
        self.default_sorter: Sorter = DefaultSorter()
        self.slot_groups: list[SlotGroupConfig] = []

    def get_groups_for_bag(self, bag: Bags) -> list[SlotGroupConfig]:
        return [group for group in self.slot_groups if group.bag == bag]

    def get_group_for_slot(self, bag: Bags, slot: int) -> SlotGroupConfig | None:
        for group in self.slot_groups:
            if group.bag == bag and slot in group.normalized_slots():
                return group
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            'default_sorter': self.default_sorter.to_dict(),
            'slot_groups': [group.to_dict() for group in self.slot_groups],
        }

    def load_dict(self, data: dict[str, Any]) -> None:
        raw_default_sorter = data.get('default_sorter', data.get('default_sort_policy', 'DefaultSorter'))
        legacy_sorter_map = {
            'Default': 'DefaultSorter',
            'QuantityDesc': 'QuantityDescSorter',
            'QuantityAsc': 'QuantityAscSorter',
            'ValueDesc': 'ValueDescSorter',
            'ValueAsc': 'ValueAscSorter',
            'RarityDesc': 'RarityDescSorter',
            'ModelIdAsc': 'ModelIdAscSorter',
            'NameAsc': 'NameAscSorter',
        }
        if isinstance(raw_default_sorter, str):
            raw_default_sorter = legacy_sorter_map.get(raw_default_sorter, raw_default_sorter)
        self.default_sorter = Sorter.from_dict(raw_default_sorter) or DefaultSorter()

        self.slot_groups.clear()
        raw_groups = data.get('slot_groups', [])
        if not isinstance(raw_groups, list):
            raw_groups = []

        for raw_group in raw_groups:
            if not isinstance(raw_group, dict):
                continue
            group = SlotGroupConfig.from_dict(raw_group)
            if group is not None:
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
