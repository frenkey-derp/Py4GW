from dataclasses import dataclass
from dataclasses import field
from datetime import datetime, timedelta
from enum import IntEnum, auto
import json
import os
from typing import Any, Iterable, Optional, Sequence, TypeVar, cast

import Py4GW
import PyImGui


from Py4GWCoreLib import ImGui
from Py4GWCoreLib import Merchant as MerchantTrading
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.ImGui_src.types import Alignment
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Py4GWcorelib import Utils
from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.UIManager import CollectorWindow, CrafterWindow, MerchantWindow
from Py4GWCoreLib.enums_src.GameData_enums import Allegiance, Attribute, Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.enums_src.Title_enums import TITLE_NAME, TITLE_TIERS, TitleID
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot
from Py4GWCoreLib.item_mods_src.upgrades import Upgrade
from Py4GWCoreLib.py4gwcorelib_src.Color import Color


project_path = Py4GW.Console.get_projects_path()
MODULE_NAME = "Data Collection Helper"
MODULE_ICON = os.path.join("Textures", "Module_Icons", "Research Code.png")
DATA_DIRECTORY_PATH = os.path.join(project_path, 'Widgets', 'Data', 'npc_catalog')
    
def tooltip():
    PyImGui.set_next_window_size((400, 0))
    PyImGui.begin_tooltip()

    # Title
    title_color = Color(255, 200, 100, 255)
    ImGui.image(MODULE_ICON, (32, 32))
    PyImGui.same_line(0, 10)
    ImGui.push_font("Regular", 20)
    ImGui.text_aligned(MODULE_NAME, alignment=Alignment.MidLeft, color=title_color.color_tuple, height=32)
    ImGui.pop_font()
    PyImGui.spacing()
    PyImGui.spacing()
    PyImGui.separator()

    # Description
    ImGui.text_wrapped("This widget will help you collect data in Guild Wars by providing various tools and utilities to streamline the process.")

    PyImGui.spacing()
    PyImGui.separator()
    PyImGui.spacing()

    # Credits
    PyImGui.text_colored("Credits:", title_color.to_tuple_normalized())
    PyImGui.bullet_text("Developed by frenkey")

    PyImGui.end_tooltip()

class FactionRequirement(IntEnum):
    None_ = 0
    Kurzick = auto()
    Luxon = auto()
    
@dataclass
class CraftingRequirements:
    materials: dict[ModelID, int] = field(default_factory=dict)
    gold: int = 0
    skill_points: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            'materials': {str(int(model_id)): amount for model_id, amount in self.materials.items()},
            'gold': self.gold,
            'skill_points': self.skill_points,
        }

    @staticmethod
    def from_dict(data: Optional[dict]) -> 'CraftingRequirements':
        materials: dict[ModelID, int] = {}
        for model_id, amount in dict(data.get('materials', {}) if data else {}).items():
            try:
                materials[ModelID(int(model_id))] = int(amount or 0)
            except Exception:
                continue

        return CraftingRequirements(
            materials=materials,
            gold=int((data or {}).get('gold', 0) or 0),
            skill_points=None if (data or {}).get('skill_points') is None else int((data or {}).get('skill_points') or 0),
        )


@dataclass
class Item:
    name: str
    item_type: ItemType = ItemType.Unknown
    model_id: int = 0

    SERIALIZATION_KIND = 'item'
    
    def to_dict(self) -> dict:
        return {
            'kind': self.SERIALIZATION_KIND,
            'name': self.name,
            'item_type': self.item_type.name,
            'model_id': self.model_id,
        }

    @classmethod
    def _base_kwargs_from_dict(cls, data: dict) -> dict[str, Any]:
        item_type_name = str(data.get('item_type', ItemType.Unknown.name))
        return {
            'name': str(data.get('name', '')),
            'item_type': ItemType[item_type_name] if item_type_name in ItemType.__members__ else ItemType.Unknown,
            'model_id': int(data.get('model_id', 0) or 0),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        return cls(**cls._base_kwargs_from_dict(data))


@dataclass
class Craftable:
    required_materials: CraftingRequirements = field(default_factory=CraftingRequirements, kw_only=True)

    def _craftable_to_dict(self) -> dict:
        return {
            'required_materials': self.required_materials.to_dict(),
        }

    @staticmethod
    def _craftable_from_dict(data: dict) -> dict[str, Any]:
        return {
            'required_materials': CraftingRequirements.from_dict(data.get('required_materials')),
        }
    
@dataclass
class Collectible:
    required_collectible: tuple[int, int] = field(default_factory=tuple[int, int], kw_only=True)

    def _collectible_to_dict(self) -> dict:
        return {
            'required_collectible': (str(int(self.required_collectible[0])), self.required_collectible[1]) if self.required_collectible else None,
        }

    @staticmethod
    def _collectible_from_dict(data: dict) -> dict[str, Any]:
        raw_collectible = data.get('required_collectible')
        if not raw_collectible:
            return {
                'required_collectible': tuple[int, int](),
            }
        return {
            'required_collectible': (int(raw_collectible[0]), int(raw_collectible[1])),
        }


def _serialize_upgrade(upgrade: Optional[Upgrade]) -> Optional[str]:
    if upgrade is None:
        return None
    return json.dumps(upgrade.to_dict(), ensure_ascii=False, separators=(',', ':'))


def _serialize_upgrades(upgrades: list[Upgrade]) -> list[str]:
    serialized: list[str] = []
    for upgrade in upgrades:
        if upgrade is None:
            continue
        payload = _serialize_upgrade(upgrade)
        if payload is not None:
            serialized.append(payload)
    return serialized

def _deserialize_upgrade(data: Optional[str]) -> Optional[Upgrade]:
    if data is None:
        return None
    try:
        payload = json.loads(data)
        if not isinstance(payload, dict):
            return None
        return Upgrade.from_dict(payload)
    except Exception:
        return None
    
def _deserialize_upgrades(data: Optional[list[str]]) -> list[Upgrade]:
    if data is None:
        return []
    upgrades: list[Upgrade] = []
    for entry in data:
        try:
            upgrade = _deserialize_upgrade(entry)
            if upgrade is not None:
                upgrades.append(upgrade)
        except Exception:
            continue
    return upgrades


def _deserialize_damage(data: dict[str, Any]) -> Optional[tuple[int, int]]:
    raw_damage = data.get('damage')
    if raw_damage is None:
        return None

    damage_entries = list(raw_damage)
    if len(damage_entries) < 2:
        return None

    minimum = int(damage_entries[0] or 0)
    maximum = int(damage_entries[1] or 0)
    if minimum == 0 and maximum == 0:
        return None

    return minimum, maximum


def _strip_none_for_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_none_for_json(item)
            for key, item in value.items()
            if item is not None
        }

    if isinstance(value, list):
        return [_strip_none_for_json(item) for item in value if item is not None]

    if isinstance(value, tuple):
        return [_strip_none_for_json(item) for item in value if item is not None]

    return value

@dataclass
class Weapon(Item):
    requirement: int = 0
    attribute: Attribute = Attribute.None_
    damage: Optional[tuple[int, int]] = None  # min, max
    energy: Optional[int] = None
    prefix: Optional[Upgrade] = None
    suffix: Optional[Upgrade] = None
    inscription: Optional[Upgrade] = None
    inherent: list[Upgrade] = field(default_factory=list)

    SERIALIZATION_KIND = 'weapon'

    def to_dict(self) -> dict:
        payload = super().to_dict()
        payload.update(
            {
                'requirement': self.requirement,
                'attribute': self.attribute.name,
                'damage': [self.damage[0], self.damage[1]] if self.damage is not None and (self.damage[0] != 0 or self.damage[1] != 0) else None,
                'energy': self.energy,
                'prefix': _serialize_upgrade(self.prefix),
                'suffix': _serialize_upgrade(self.suffix),
                'inscription': _serialize_upgrade(self.inscription),
                'inherent': _serialize_upgrades(self.inherent),
            }
        )
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'Weapon':
        attribute_name = str(data.get('attribute', Attribute.None_.name))
        damage_data = _deserialize_damage(data)
        energy_data = data.get('energy', None)
        
        return cls(
            **Weapon._base_kwargs_from_dict(data),
            requirement=int(data.get('requirement', 0) or 0),
            attribute=Attribute[attribute_name] if attribute_name in Attribute.__members__ else Attribute.None_,
            damage=damage_data,
            energy=int(energy_data) if energy_data is not None else None,
            prefix=_deserialize_upgrade(data.get('prefix', None)),
            suffix=_deserialize_upgrade(data.get('suffix', None)),
            inscription=_deserialize_upgrade(data.get('inscription', None)),
            inherent=_deserialize_upgrades(data.get('inherent', [])),
        )

@dataclass
class Armor(Item):
    armor_rating: int = 0
    profession: Profession = Profession._None

    SERIALIZATION_KIND = 'armor'
    
    def to_dict(self) -> dict:
        payload = super().to_dict()
        payload.update(
            {
                'armor_rating': self.armor_rating,
                'profession': self.profession.name,
            }
        )
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'Armor':
        profession_name = str(data.get('profession', Profession._None.name))
        return cls(
            **Armor._base_kwargs_from_dict(data),
            armor_rating=int(data.get('armor_rating', 0) or 0),
            profession=Profession[profession_name] if profession_name in Profession.__members__ else Profession._None,
        )



@dataclass
class CraftableWeapon(Weapon, Craftable):
    SERIALIZATION_KIND = 'craftable_weapon'

    def to_dict(self) -> dict:
        payload = Weapon.to_dict(self)
        payload.update(self._craftable_to_dict())
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'CraftableWeapon':
        attribute_name = str(data.get('attribute', Attribute.None_.name))
        return cls(
            **Weapon._base_kwargs_from_dict(data),
            requirement=int(data.get('requirement', 0) or 0),
            attribute=Attribute[attribute_name] if attribute_name in Attribute.__members__ else Attribute.None_,
            damage=_deserialize_damage(data),
            energy=int(data.get('energy', 0) or 0) if data.get('energy', None) is not None else None,
            prefix=_deserialize_upgrade(data.get('prefix', None)),
            suffix=_deserialize_upgrade(data.get('suffix', None)),
            inscription=_deserialize_upgrade(data.get('inscription', None)),
            inherent=_deserialize_upgrades(data.get('inherent', [])),
            **Craftable._craftable_from_dict(data),
        )


@dataclass
class CraftableArmor(Armor, Craftable):
    SERIALIZATION_KIND = 'craftable_armor'

    def to_dict(self) -> dict:
        payload = Armor.to_dict(self)
        payload.update(self._craftable_to_dict())
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'CraftableArmor':
        profession_name = str(data.get('profession', Profession._None.name))
        return cls(
            **Armor._base_kwargs_from_dict(data),
            armor_rating=int(data.get('armor_rating', 0) or 0),
            profession=Profession[profession_name] if profession_name in Profession.__members__ else Profession._None,
            **Craftable._craftable_from_dict(data),
        )

@dataclass
class CollectibleWeapon(Weapon, Collectible):
    SERIALIZATION_KIND = 'collectible_weapon'

    def to_dict(self) -> dict:
        payload = Weapon.to_dict(self)
        payload.update(self._collectible_to_dict())
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'CollectibleWeapon':
        attribute_name = str(data.get('attribute', Attribute.None_.name))
        return cls(
            **Weapon._base_kwargs_from_dict(data),
            requirement=int(data.get('requirement', 0) or 0),
            attribute=Attribute[attribute_name] if attribute_name in Attribute.__members__ else Attribute.None_,
            damage=_deserialize_damage(data),
            energy=int(data.get('energy', 0) or 0) if data.get('energy', None) is not None else None,
            prefix=_deserialize_upgrade(data.get('prefix', None)),
            suffix=_deserialize_upgrade(data.get('suffix', None)),
            inscription=_deserialize_upgrade(data.get('inscription', None)),
            inherent=_deserialize_upgrades(data.get('inherent', [])),
            **Collectible._collectible_from_dict(data),
        )


@dataclass
class CollectibleArmor(Armor, Collectible):
    SERIALIZATION_KIND = 'collectible_armor'

    def to_dict(self) -> dict:
        payload = Armor.to_dict(self)
        payload.update(self._collectible_to_dict())
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'CollectibleArmor':
        profession_name = str(data.get('profession', Profession._None.name))
        return cls(
            **Armor._base_kwargs_from_dict(data),
            armor_rating=int(data.get('armor_rating', 0) or 0),
            profession=Profession[profession_name] if profession_name in Profession.__members__ else Profession._None,
            **Collectible._collectible_from_dict(data),
        )


@dataclass
class CollectorItem(Item, Collectible):
    SERIALIZATION_KIND = 'collector_item'

    def to_dict(self) -> dict:
        payload = Item.to_dict(self)
        payload.update(self._collectible_to_dict())
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'CollectorItem':
        return cls(
            **Item._base_kwargs_from_dict(data),
            **Collectible._collectible_from_dict(data),
        )


@dataclass
class CraftableItem(Item, Craftable):
    SERIALIZATION_KIND = 'craftable_item'

    def to_dict(self) -> dict:
        payload = Item.to_dict(self)
        payload.update(self._craftable_to_dict())
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> 'CraftableItem':
        return cls(
            **Item._base_kwargs_from_dict(data),
            **Craftable._craftable_from_dict(data),
        )


ITEM_KIND_MAP = {
    Item.SERIALIZATION_KIND: Item,
    Weapon.SERIALIZATION_KIND: Weapon,
    Armor.SERIALIZATION_KIND: Armor,
    CraftableItem.SERIALIZATION_KIND: CraftableItem,
    CraftableWeapon.SERIALIZATION_KIND: CraftableWeapon,
    CraftableArmor.SERIALIZATION_KIND: CraftableArmor,
    CollectorItem.SERIALIZATION_KIND: CollectorItem,
    CollectibleWeapon.SERIALIZATION_KIND: CollectibleWeapon,
    CollectibleArmor.SERIALIZATION_KIND: CollectibleArmor,
}


TItem = TypeVar('TItem', bound=Item)


def _deserialize_item(data: dict, default_cls: type[Item] = Item) -> Item:
    kind = str(data.get('kind', '') or '')
    item_cls = ITEM_KIND_MAP.get(kind)
    if item_cls is None:
        if 'required_collectible' in data:
            if 'armor_rating' in data or 'profession' in data:
                item_cls = CollectibleArmor
            elif 'requirement' in data or 'attribute' in data or 'damage' in data:
                item_cls = CollectibleWeapon
            else:
                item_cls = CollectorItem
        elif 'required_materials' in data:
            if 'armor_rating' in data or 'profession' in data:
                item_cls = CraftableArmor
            elif 'requirement' in data or 'attribute' in data or 'damage' in data:
                item_cls = CraftableWeapon
            else:
                item_cls = CraftableItem
        elif 'armor_rating' in data or 'profession' in data:
            item_cls = Armor
        elif 'requirement' in data or 'attribute' in data or 'damage' in data:
            item_cls = Weapon
        else:
            item_cls = default_cls
    return item_cls.from_dict(data)



@dataclass
class Npc:
    name: str = ''
    model_id: int = 0
    encoded_name: bytes = b''
    allegiance : Allegiance = Allegiance.Neutral
    required_title_id: Optional[TitleID] = None
    required_title_rank: Optional[int] = None
    required_faction: Optional[FactionRequirement] = None
    unreachable: Optional[bool] = None

    def _base_to_dict(self) -> dict:
        return {
            'name': self.name,
            'encoded_name': list(self.encoded_name),
            'model_id': self.model_id,
            'allegiance': self.allegiance.name,
            'required_title_id': self.required_title_id.name if self.required_title_id is not None else None,
            'required_title_rank': self.required_title_rank,
            'required_faction': self.required_faction.name if self.required_faction is not None else None,
            'unreachable': self.unreachable,
        }

    @staticmethod
    def _base_from_dict(data: dict) -> dict:
        allegiance_name = str(data.get('allegiance', Allegiance.Neutral.name))
        raw_title_name = data.get('required_title_id', None)
        raw_faction_name = data.get('required_faction', None)
        title_name = str(raw_title_name) if raw_title_name is not None else ''
        faction_name = str(raw_faction_name) if raw_faction_name is not None else ''

        required_title_id: Optional[TitleID] = None
        if title_name and title_name != TitleID._None.name and title_name in TitleID.__members__:
            required_title_id = TitleID[title_name]

        required_faction: Optional[FactionRequirement] = None
        if faction_name and faction_name != FactionRequirement.None_.name and faction_name in FactionRequirement.__members__:
            required_faction = FactionRequirement[faction_name]

        required_title_rank_raw = data.get('required_title_rank', None)
        required_title_rank = None if required_title_rank_raw is None else int(required_title_rank_raw or 0)
        if required_title_id is None or required_title_rank == 0:
            required_title_rank = None

        return {
            'name': str(data.get('name', '')),
            'encoded_name': bytes(data.get('encoded_name', [])),
            'model_id': int(data.get('model_id', 0) or 0),
            'allegiance': Allegiance[allegiance_name] if allegiance_name in Allegiance.__members__ else Allegiance.Neutral,
            'required_title_id': required_title_id,
            'required_title_rank': required_title_rank,
            'required_faction': required_faction,
            'unreachable': data.get('unreachable', None),
        }

    def service_label(self) -> str:
        return self.__class__.__name__

    def interaction_label(self) -> str:
        restrictions: list[str] = []
        if self.required_title_id is not None and self.required_title_rank is not None and self.required_title_rank > 0:
            restrictions.append(f'{TITLE_NAME.get(int(self.required_title_id), self.required_title_id.name)} r{self.required_title_rank}')
        if self.required_faction is not None and self.required_faction != FactionRequirement.None_:
            restrictions.append(self.required_faction.name)
        return ', '.join(restrictions) if restrictions else 'Open'

    def HasMapUnlocked(self) -> bool:
        return True

    def GetMapIDs(self) -> list[int]:
        return []

    def GetDisplayMapID(self) -> int:
        map_ids = self.GetMapIDs()
        return map_ids[0] if map_ids else 0

    def GetDisplayPosition(self) -> tuple[float, float]:
        return (0.0, 0.0)

    def HasStationaryData(self) -> bool:
        return False

    def GetAgentId(self) -> int:
        return 0

    def MoveTo(self):
        return

    def CanInteract(self) -> bool:        
        if self.required_faction is not None and self.required_faction != FactionRequirement.None_ and not _meets_faction_requirement(self.required_faction):
            return False
        
        if self.required_title_id is not None and self.required_title_rank is not None and self.required_title_rank > 0:
            return _get_title_rank(self.required_title_id) >= self.required_title_rank
        
        if self.unreachable is not None:
            return not self.unreachable
        
        return True

    def _service_window_is_open(self) -> bool:
        return CrafterWindow.IsOpen()

    def _close_service_window(self):
        CrafterWindow.Close()

    def _get_offered_items(self) -> list[int]:
        offered_items = MerchantTrading.Trading.Crafter.GetOfferedItems()
        return list(offered_items or [])

    def IsCrafterOpen(self) -> bool:
        return False

    def CloseCrafter(self):
        if self._service_window_is_open():
            self._close_service_window()

    def CollectData(self) -> bool:
        return False

    def GetCollectedCount(self) -> int:
        return 0

    def GetCollectionSummary(self) -> str:
        return 'N/A'


@dataclass
class FoeSpawn:
    map_id: int = 0
    position: tuple[float, float] = (0.0, 0.0)

    def to_dict(self) -> dict:
        return {
            'map_id': self.map_id,
            'position': [self.position[0], self.position[1]],
        }

    @staticmethod
    def from_dict(data: dict) -> 'FoeSpawn':
        position_data = list(data.get('position', [0.0, 0.0]))
        return FoeSpawn(
            map_id=int(data.get('map_id', 0) or 0),
            position=(
                float(position_data[0]) if len(position_data) > 0 else 0.0,
                float(position_data[1]) if len(position_data) > 1 else 0.0,
            ),
        )

    def HasMapUnlocked(self) -> bool:
        return Map.IsMapUnlocked(self.map_id)


@dataclass
class Foe(Npc):
    primary_profession: Optional[Profession] = None
    secondary_profession: Optional[Profession] = None
    spawns: list[FoeSpawn] = field(default_factory=list)

    def __post_init__(self):
        self.allegiance = Allegiance.Enemy

    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload.update(
            {
                'primary_profession': self.primary_profession.name if self.primary_profession is not None else None,
                'secondary_profession': self.secondary_profession.name if self.secondary_profession is not None else None,
                'spawns': [spawn.to_dict() for spawn in self.spawns],
            }
        )
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Foe':
        raw_primary_name = data.get('primary_profession', None)
        raw_secondary_name = data.get('secondary_profession', None)
        primary_name = str(raw_primary_name) if raw_primary_name is not None else ''
        secondary_name = str(raw_secondary_name) if raw_secondary_name is not None else ''
        legacy_map_id = int(data.get('map_id', 0) or 0)
        spawns: list[FoeSpawn] = []
        for spawn in list(data.get('spawns', [])):
            if isinstance(spawn, dict):
                spawns.append(FoeSpawn.from_dict(spawn))
            else:
                spawn_values = list(spawn)
                spawns.append(
                    FoeSpawn(
                        map_id=legacy_map_id,
                        position=(
                            float(spawn_values[0]) if len(spawn_values) > 0 else 0.0,
                            float(spawn_values[1]) if len(spawn_values) > 1 else 0.0,
                        ),
                    )
                )
        return Foe(
            **Npc._base_from_dict(data),
            primary_profession=Profession[primary_name] if primary_name and primary_name != Profession._None.name and primary_name in Profession.__members__ else None,
            secondary_profession=Profession[secondary_name] if secondary_name and secondary_name != Profession._None.name and secondary_name in Profession.__members__ else None,
            spawns=spawns,
        )

    def GetCollectedCount(self) -> int:
        return len(self.spawns)

    def GetCollectionSummary(self) -> str:
        primary = self.primary_profession.name if self.primary_profession is not None else '?'
        secondary = self.secondary_profession.name if self.secondary_profession is not None else '?'
        return f'{len(self.spawns)} spawn(s) / {primary}-{secondary}'

    def HasMapUnlocked(self) -> bool:
        return any(spawn.HasMapUnlocked() for spawn in self.spawns) if self.spawns else False

    def GetMapIDs(self) -> list[int]:
        return list(dict.fromkeys(spawn.map_id for spawn in self.spawns if spawn.map_id != 0))

    def GetDisplayMapID(self) -> int:
        if not self.spawns:
            return 0
        current_base_map_id = Map.GetBaseMapID()
        current_spawn = next((spawn for spawn in self.spawns if Map.GetBaseMapID(spawn.map_id) == current_base_map_id), None)
        if current_spawn is not None:
            return current_spawn.map_id
        return self.spawns[0].map_id

    def GetDisplayPosition(self) -> tuple[float, float]:
        if not self.spawns:
            return (0.0, 0.0)
        current_base_map_id = Map.GetBaseMapID()
        current_spawn = next((spawn for spawn in self.spawns if Map.GetBaseMapID(spawn.map_id) == current_base_map_id), None)
        if current_spawn is not None:
            return current_spawn.position
        return self.spawns[0].position

    def HasStationaryData(self) -> bool:
        return bool(self.spawns)

@dataclass
class StationaryNpc(Npc):
    map_id: int = 0
    position: tuple[float, float] = (0.0, 0.0)

    def _base_to_dict(self) -> dict:
        payload = super()._base_to_dict()
        payload.update(
            {
                'map_id': self.map_id,
                'position': [self.position[0], self.position[1]],
            }
        )
        return payload

    @staticmethod
    def _base_from_dict(data: dict) -> dict:
        payload = Npc._base_from_dict(data)
        position_data = list(data.get('position', [0.0, 0.0]))
        payload.update(
            {
                'map_id': int(data.get('map_id', 0) or 0),
                'position': (
                    float(position_data[0]) if len(position_data) > 0 else 0.0,
                    float(position_data[1]) if len(position_data) > 1 else 0.0,
                ),
            }
        )
        return payload

    def HasMapUnlocked(self) -> bool:
        return Map.IsMapUnlocked(self.map_id)

    def GetMapIDs(self) -> list[int]:
        return [self.map_id] if self.map_id != 0 else []

    def GetDisplayMapID(self) -> int:
        return self.map_id

    def GetDisplayPosition(self) -> tuple[float, float]:
        return self.position

    def HasStationaryData(self) -> bool:
        return self.position != (0.0, 0.0) and self.map_id != 0

    def GetAgentId(self) -> int:
        if not Routines.Checks.Map.IsMapReady():
            return 0

        if self.position == (0.0, 0.0):
            return 0

        agents = AgentArray.GetAgentArray()
        agents = AgentArray.Filter.ByDistance(agents, self.position, 100.0)

        for agent_id in agents:
            if agent_id is not None and Agent.GetModelID(agent_id) == self.model_id:
                return agent_id

        return 0

    def MoveTo(self):
        if not Routines.Checks.Map.IsMapReady():
            return

        if Map.GetBaseMapID() != Map.GetBaseMapID(self.map_id):
            if Map.IsMapUnlocked(self.map_id):
                Map.Travel(self.map_id)
                return
            Py4GW.Console.Log(MODULE_NAME, f"Map '{Map.GetMapName(self.map_id)}' is not unlocked yet.", Py4GW.Console.MessageType.Warning)
            return

        Player.Move(self.position[0], self.position[1])

        if not self.CanInteract():
            Py4GW.Console.Log(MODULE_NAME, f"'{self.name}' requires {self.interaction_label()} before it will interact.", Py4GW.Console.MessageType.Warning)
            return

        if (agent_id := self.GetAgentId()) != 0:
            Player.ChangeTarget(agent_id)
            Player.Interact(agent_id)

    def IsCrafterOpen(self) -> bool:
        if not Routines.Checks.Map.IsMapReady():
            return False

        if Map.GetBaseMapID() != Map.GetBaseMapID(self.map_id):
            return False

        agent_id = self.GetAgentId()
        if agent_id == 0:
            return False

        if Player.GetTargetID() != agent_id:
            return False

        return self._service_window_is_open()

@dataclass
class Ally(StationaryNpc):
    def __post_init__(self):
        self.allegiance = Allegiance.Ally

    def to_dict(self) -> dict:
        return self._base_to_dict()

    @staticmethod
    def from_dict(data: dict) -> 'Ally':
        return Ally(**StationaryNpc._base_from_dict(data))

    def GetCollectionSummary(self) -> str:
        return self.interaction_label()
        
@dataclass
class Merchant(Ally):
    items: list[Item] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload['items'] = [item.to_dict() for item in self.items]
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Merchant':
        return Merchant(
            **StationaryNpc._base_from_dict(data),
            items=[_deserialize_item(entry, Item) for entry in list(data.get('items', []))],
        )

    def _service_window_is_open(self) -> bool:
        return MerchantWindow.IsOpen()

    def _close_service_window(self):
        MerchantWindow.Close()

    def _get_offered_items(self) -> list[int]:
        return list(MerchantTrading.Trading.Merchant.GetOfferedItems() or [])

    def CollectData(self) -> bool:
        if not self.IsCrafterOpen():
            Py4GW.Console.Log(MODULE_NAME, f"Merchant '{self.name}' is not open. Please open their merchant window before collecting data.", Py4GW.Console.MessageType.Warning)
            return False

        snapshots = [ItemSnapshot.from_item_id(item_id) for item_id in self._get_offered_items()]
        collected_count = 0
        pending_name_update = False
        for item in snapshots:
            if item is None or not item.is_valid:
                continue
            item_name = _get_snapshot_name(item)
            if not item_name:
                pending_name_update = True
                continue
            if _upsert_named_item(self.items, _build_item_from_snapshot(item)):
                collected_count += 1

        _log_collection_result(self.name, collected_count, 'merchant item')
        if pending_name_update:
            Py4GW.Console.Log(MODULE_NAME, f"Some collected items from '{self.name}' are missing names and will be updated once the names are available. Please collect from this merchant again...", Py4GW.Console.MessageType.Warning)
        return not pending_name_update and collected_count > 0

    def GetCollectedCount(self) -> int:
        return len(self.items)

    def GetCollectionSummary(self) -> str:
        return f'{len(self.items)} items / {self.interaction_label()}'

class TraderType(IntEnum):
    Unknown = auto() 
    Rune = auto() 
    Dye = auto() 
    Material = auto() 
    RareMaterial = auto()
    RareScroll = auto()
    Sigil = auto()
    
    @staticmethod
    def get_type_from_name(name: str) -> 'TraderType':
        name = name.lower()
        if 'rune trader' in name:
            return TraderType.Rune
        if 'dye trader' in name:
            return TraderType.Dye
        if 'rare material trader' in name:
            return TraderType.RareMaterial
        if 'rare scroll trader' in name:
            return TraderType.RareScroll
        if 'sigil trader' in name:
            return TraderType.Sigil
        if 'material trader' in name:
            return TraderType.Material
        return TraderType.Unknown
    
@dataclass
class Trader(Ally):
    items: list[Item] = field(default_factory=list)
    _trader_type: TraderType = field(default=TraderType.Unknown, repr=False)
        
    @property
    def trader_type(self) -> TraderType:
        return self._trader_type
    
    @trader_type.setter
    def trader_type(self, value: TraderType):
        self._trader_type = value
        self.items = self._get_trader_items_by_type(value)
        
    def _get_trader_items_by_type(self, trader_type: TraderType) -> list[Item]:
        return []  # Placeholder for actual implementation to return items based on trader type, traders have a fixed set of items we don't need to ingame collect them

    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload['trader_type'] = self.trader_type.name
        payload['items'] = [item.to_dict() for item in self.items]
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Trader':
        trader_type_name = str(data.get('trader_type', TraderType.Unknown.name))
        trader = Trader(
            **StationaryNpc._base_from_dict(data),
            items=[_deserialize_item(entry, Item) for entry in list(data.get('items', []))],
            _trader_type=TraderType[trader_type_name] if trader_type_name in TraderType.__members__ else TraderType.Unknown,
        )
        return trader

    def _service_window_is_open(self) -> bool:
        return MerchantWindow.IsOpen()

    def _close_service_window(self):
        MerchantWindow.Close()

    def CollectData(self) -> bool:
        inferred_type = TraderType.get_type_from_name(self.name)
        if self.trader_type == TraderType.Unknown and inferred_type != TraderType.Unknown:
            self.trader_type = inferred_type
            return True
        return False

    def GetCollectedCount(self) -> int:
        return len(self.items)

    def GetCollectionSummary(self) -> str:
        return f'{self.trader_type.name} / {self.interaction_label()}'
        
@dataclass
class Artisan(Ally):
    items: list[CraftableItem] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload['items'] = [item.to_dict() for item in self.items]
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Artisan':
        return Artisan(
            **StationaryNpc._base_from_dict(data),
            items=[cast(CraftableItem, _deserialize_item(entry, CraftableItem)) for entry in list(data.get('items', []))],
        )

    def CollectData(self) -> bool:
        return _collect_simple_crafter_items(self, self.items)

    def GetCollectedCount(self) -> int:
        return len(self.items)

    def GetCollectionSummary(self) -> str:
        return f'{len(self.items)} items'


@dataclass
class ConsumableCrafter(Ally):
    consumables: list[CraftableItem] = field(default_factory=list)
            
    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload['consumables'] = [item.to_dict() for item in self.consumables]
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'ConsumableCrafter':
        return ConsumableCrafter(
            **StationaryNpc._base_from_dict(data),
            consumables=[cast(CraftableItem, _deserialize_item(entry, CraftableItem)) for entry in list(data.get('consumables', []))],
        )

    def CollectData(self) -> bool:
        return _collect_simple_crafter_items(self, self.consumables)

    def GetCollectedCount(self) -> int:
        return len(self.consumables)

    def GetCollectionSummary(self) -> str:
        return f'{len(self.consumables)} consumables'


@dataclass
class Weaponsmith(Ally):
    weapons: list[CraftableWeapon] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload['weapons'] = [weapon.to_dict() for weapon in self.weapons]
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Weaponsmith':
        return Weaponsmith(
            **StationaryNpc._base_from_dict(data),
            weapons=[cast(CraftableWeapon, _deserialize_item(entry, CraftableWeapon)) for entry in list(data.get('weapons', []))],
        )

    def CollectData(self) -> bool:
        if not self.IsCrafterOpen():
            Py4GW.Console.Log(MODULE_NAME, f"Crafter '{self.name}' is not open. Please move to the crafter and open their crafting window before collecting data.", Py4GW.Console.MessageType.Warning)
            return False

        items = [ItemSnapshot.from_item_id(item_id) for item_id in self._get_offered_items()]
        collected_count = 0
        pending_name_update = False

        for item in items:
            if item is None or not item.is_valid or not item.is_weapon:
                continue

            weapon_name = _get_snapshot_name(item)
            if not weapon_name:
                pending_name_update = True
                continue

            weapon = _build_craftable_weapon_from_snapshot(item)
            if _upsert_named_item(self.weapons, weapon):
                collected_count += 1

        _log_collection_result(self.name, collected_count, 'weapon')
        if pending_name_update:
            Py4GW.Console.Log(MODULE_NAME, f"Some collected items from '{self.name}' are missing names and will be updated once the names are available. Please collect from this crafter again...", Py4GW.Console.MessageType.Warning)
        return not pending_name_update and collected_count > 0

    def GetCollectedCount(self) -> int:
        return len(self.weapons)

    def GetCollectionSummary(self) -> str:
        return f'{len(self.weapons)} weapons'


@dataclass
class Collector(Ally):
    items: list[Item] = field(default_factory=list)

    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload['items'] = [item.to_dict() for item in self.items]
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Collector':
        return Collector(
            **StationaryNpc._base_from_dict(data),
            items=[cast(Item, _deserialize_item(entry, CollectorItem)) for entry in list(data.get('items', []))],
        )

    def _service_window_is_open(self) -> bool:
        return CollectorWindow.IsOpen()

    def _close_service_window(self):
        CollectorWindow.Close()

    def _get_offered_items(self) -> list[int]:
        offered_items = MerchantTrading.Trading.Collector.GetOfferedItems()
        return list(offered_items or [])

    def CollectData(self) -> bool:
        if not self.IsCrafterOpen():
            Py4GW.Console.Log(MODULE_NAME, f"Collector '{self.name}' is not open. Please move to the collector and open their exchange window before collecting data.", Py4GW.Console.MessageType.Warning)
            return False

        items = [ItemSnapshot.from_item_id(item_id) for item_id in self._get_offered_items()]
        collected_count = 0
        pending_name_update = False

        exchange_item = next(
            (
                entry.required_collectible
                for entry in self.items
                if isinstance(entry, Collectible) and entry.required_collectible
            ),
            None,
        )

        for item in items:
            if item is None or not item.is_valid:
                continue

            if exchange_item is not None and item.model_id == exchange_item[0]:
                continue

            item_name = _get_snapshot_name(item)
            if not item_name:
                pending_name_update = True
                continue
            
            existing = next((existing_item for existing_item in self.items if _same_item_identity(existing_item, item)), None)
            collectible_item = _build_collectible_item_typed_from_snapshot(item, exchange_item)
            if _upsert_named_item(self.items, collectible_item):
                collected_count += 1

        _log_collection_result(self.name, collected_count, 'collector')
        if pending_name_update:
            Py4GW.Console.Log(MODULE_NAME, f"Some collected items from '{self.name}' are missing names and will be updated once the names are available. Please collect from this crafter again...", Py4GW.Console.MessageType.Warning)
        return not pending_name_update and collected_count > 0

    def GetCollectedCount(self) -> int:
        return len(self.items)

    def GetCollectionSummary(self) -> str:
        unresolved = sum(
            1
            for item in self.items
            if isinstance(item, Collectible)
            and item.required_collectible
            and item.required_collectible[0] == 0
        )
        return f'{len(self.items)} items / {unresolved} unresolved'


@dataclass
class Armorer(Ally):
    professions_armor_rating: dict[Profession, int] = field(default_factory=dict)
    armors: dict[Profession, list[CraftableArmor]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        payload = self._base_to_dict()
        payload.update(
            {
                'professions_armor_rating': {
                profession.name: armor_rating
                for profession, armor_rating in self.professions_armor_rating.items()
                },
                'armors': {
                profession.name: [armor.to_dict() for armor in armors]
                for profession, armors in self.armors.items()
                },
            }
        )
        return payload

    @staticmethod
    def from_dict(data: dict) -> 'Armorer':
        professions_armor_rating: dict[Profession, int] = {}
        for profession_name, armor_rating in dict(data.get('professions_armor_rating', {})).items():
            if profession_name not in Profession.__members__:
                continue
            professions_armor_rating[Profession[profession_name]] = int(armor_rating or 0)

        armors: dict[Profession, list[CraftableArmor]] = {}
        for profession_name, entries in dict(data.get('armors', {})).items():
            if profession_name not in Profession.__members__:
                continue
            profession = Profession[profession_name]
            armors[profession] = [cast(CraftableArmor, _deserialize_item(entry, CraftableArmor)) for entry in list(entries or [])]

        return Armorer(
            **StationaryNpc._base_from_dict(data),
            professions_armor_rating=professions_armor_rating,
            armors=armors,
        )

    def CollectData(self) -> bool:
        if not self.IsCrafterOpen():
            Py4GW.Console.Log(MODULE_NAME, f"Crafter '{self.name}' is not open. Please move to the crafter and open their crafting window before collecting data.", Py4GW.Console.MessageType.Warning)
            return False
        
        items = [ItemSnapshot.from_item_id(item_id) for item_id in self._get_offered_items()]
        collected_count = 0

        pending_name_update = False
        for item in items:
            if item is None or not item.is_valid or not item.is_armor:
                continue

            profession = item.profession if item.profession not in (None, Profession._None) else _get_current_profession()
            if profession in (None, Profession._None):
                continue

            armor_name = _get_snapshot_name(item)
            if not armor_name:
                pending_name_update = True
                continue
                    
            def _same_armor_item_identity(existing: Any, candidate: Any) -> bool:
                same_type = existing.item_type == candidate.item_type or _is_unknown_item_type(existing.item_type) or _is_unknown_item_type(candidate.item_type)
                same_profession = getattr(existing, 'profession', None) == getattr(candidate, 'profession', None)

                return same_profession and same_type

            existing = next(
                (
                    existing_armor
                    for entries in self.armors.values()
                    for existing_armor in entries
                    if _same_armor_item_identity(existing_armor, item)
                ),
                None,
            )

            if existing is not None:
                existing.name = armor_name  # Update name even if other fields are not merged to ensure future identity matches
                existing.model_id = item.model_id  # Update model_id as well for better future matching
                collected_count += 1
                continue

            armor = _build_craftable_armor_from_snapshot(item)
            armor.name = armor_name
            armor.armor_rating = int(self.professions_armor_rating.get(profession, 0) or 0)
            armor.profession = profession
            if self._upsert_craftable_armor(armor):
                collected_count += 1

        _log_collection_result(self.name, collected_count, 'armor')
        if pending_name_update:
            Py4GW.Console.Log(MODULE_NAME, f"Some collected items from '{self.name}' are missing names and will be updated once the names are available. Please collect from this crafter again...", Py4GW.Console.MessageType.Warning)
            
        return not pending_name_update and collected_count > 0

    def _upsert_craftable_armor(self, armor: CraftableArmor) -> bool:
        entries = self.armors.setdefault(armor.profession, [])
        existing_index = next(
            (
                index for index, existing in enumerate(entries)
                if _same_item_identity(existing, armor)
            ),
            -1,
        )

        if existing_index >= 0:
            existing = entries[existing_index]
            if not _merge_armor_fields(existing, armor):
                return False
        else:
            entries.append(armor)

        entries.sort(key=lambda entry: (entry.item_type.name, entry.name))
        return True
        
    def Save(self):
        save_crafters_to_json()

    def GetCollectedCount(self) -> int:
        return sum(len(entries) for entries in self.armors.values())

    def GetCollectionSummary(self) -> str:
        return _format_armor_ratings(self)
        
P = Profession

PROPH_ARMOR_35 = {
    P.Warrior: 35,
    P.Ranger: 25,
    P.Monk: 15,
    P.Necromancer: 15,
    P.Mesmer: 15,
    P.Elementalist: 15,
}
PROPH_ARMOR_50 = {
    P.Warrior: 50,
    P.Ranger: 40,
    P.Monk: 30,
    P.Necromancer: 30,
    P.Mesmer: 30,
    P.Elementalist: 30,
}
PROPH_ARMOR_59 = {
    P.Warrior: 59,
    P.Ranger: 49,
    P.Monk: 39,
    P.Necromancer: 39,
    P.Mesmer: 39,
    P.Elementalist: 39,
}
PROPH_ARMOR_65 = {
    P.Warrior: 65,
    P.Ranger: 55,
    P.Monk: 45,
    P.Necromancer: 45,
    P.Mesmer: 45,
    P.Elementalist: 45,
}
PROPH_ARMOR_71 = {
    P.Warrior: 71,
    P.Ranger: 61,
    P.Monk: 51,
    P.Necromancer: 51,
    P.Mesmer: 51,
    P.Elementalist: 51,
}
PROPH_ARMOR_80 = {
    P.Warrior: 80,
    P.Ranger: 70,
    P.Monk: 60,
    P.Necromancer: 60,
    P.Mesmer: 60,
    P.Elementalist: 60,
}
FACTIONS_ARMOR_35 = {
    P.Warrior: 35,
    P.Ranger: 25,
    P.Monk: 15,
    P.Necromancer: 15,
    P.Mesmer: 15,
    P.Elementalist: 15,
    P.Assassin: 25,
    P.Ritualist: 15,
}
FACTIONS_ARMOR_50 = {
    P.Warrior: 50,
    P.Ranger: 40,
    P.Monk: 30,
    P.Necromancer: 30,
    P.Mesmer: 30,
    P.Elementalist: 30,
    P.Assassin: 40,
    P.Ritualist: 30,
}
FACTIONS_ARMOR_65 = {
    P.Warrior: 65,
    P.Ranger: 55,
    P.Monk: 45,
    P.Necromancer: 45,
    P.Mesmer: 45,
    P.Elementalist: 45,
    P.Assassin: 55,
    P.Ritualist: 45,
}
FACTIONS_ARMOR_80 = {
    P.Warrior: 80,
    P.Ranger: 70,
    P.Monk: 60,
    P.Necromancer: 60,
    P.Mesmer: 60,
    P.Elementalist: 60,
    P.Assassin: 70,
    P.Ritualist: 60,
}
FULL_ARMOR_80 = {
    P.Warrior: 80,
    P.Ranger: 70,
    P.Monk: 60,
    P.Necromancer: 60,
    P.Mesmer: 60,
    P.Elementalist: 60,
    P.Assassin: 70,
    P.Ritualist: 60,
    P.Paragon: 80,
    P.Dervish: 70,
}
NIGHTFALL_ARMOR_35 = {
    P.Warrior: 35,
    P.Ranger: 25,
    P.Monk: 15,
    P.Necromancer: 15,
    P.Mesmer: 15,
    P.Elementalist: 15,
    P.Paragon: 35,
    P.Dervish: 25,
}
NIGHTFALL_ARMOR_50 = {
    P.Warrior: 50,
    P.Ranger: 40,
    P.Monk: 30,
    P.Necromancer: 30,
    P.Mesmer: 30,
    P.Elementalist: 30,
    P.Paragon: 50,
    P.Dervish: 40,
}
NIGHTFALL_ARMOR_65 = {
    P.Warrior: 65,
    P.Ranger: 55,
    P.Monk: 45,
    P.Necromancer: 45,
    P.Mesmer: 45,
    P.Elementalist: 45,
    P.Paragon: 65,
    P.Dervish: 55,
}

CRAFTERS = [
    
    Armorer(name='Sol Pyrrhus', map_id=63, professions_armor_rating=PROPH_ARMOR_71.copy()),
    
    Armorer(name='Oroku', map_id=240, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Voldo the Exotic', map_id=239, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Koumei', map_id=351, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Maiya', map_id=351, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Wei Qi', map_id=351, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    
    Armorer(name='Eternal Forgemaster', map_id=34, professions_armor_rating=FULL_ARMOR_80.copy()),
    Armorer(name='Keeper of Armor', map_id=503, professions_armor_rating=FULL_ARMOR_80.copy()),
    
    Armorer(name='Mehinu', map_id=449, professions_armor_rating=NIGHTFALL_ARMOR_35, position=(-11202.0, 9346.0), model_id=4774, encoded_name=bytes([0x1, 0x81, 0x54, 0x20, 0x38, 0x91, 0xB6, 0x9C, 0x44, 0x3E, 0x0, 0x0])),
    Armorer(name='Pasu', map_id=491, professions_armor_rating=NIGHTFALL_ARMOR_50, position=(3944.0, 2378.0), model_id=4773, encoded_name=bytes([0x1, 0x81, 0xC5, 0x3F, 0x6F, 0xBC, 0xCB, 0xD4, 0x5B, 0x6D, 0x0, 0x0])),
    Armorer(name='Sulee', map_id=492, professions_armor_rating=NIGHTFALL_ARMOR_65, position=(607.0, 2710.0), model_id=4774, encoded_name=bytes([0x1, 0x81, 0xBE, 0x3F, 0xB7, 0xB0, 0x2A, 0x98, 0x1F, 0x2, 0x0, 0x0])),
    Armorer(name='Mateneh', map_id=414, professions_armor_rating=FULL_ARMOR_80, position=(-1805.0, -4050.0), model_id=5718, encoded_name=bytes([0x1, 0x81, 0x9A, 0x21, 0x2B, 0xFB, 0x48, 0xDA, 0x4D, 0x7B, 0x0, 0x0])),
    Armorer(name='Burreh', map_id=436, professions_armor_rating=FULL_ARMOR_80, position=(-4916.0, 8985.0), model_id=5437, encoded_name=bytes([0x1, 0x81, 0xC6, 0x21, 0x2F, 0xE7, 0xF0, 0xC4, 0x6C, 0x7C, 0x0, 0x0])),
    Armorer(name='Ahamid', map_id=436, professions_armor_rating=FULL_ARMOR_80, position=(-5870.0, 8255.0), model_id=4792, encoded_name=bytes([0x1, 0x81, 0x1, 0x57, 0xF0, 0xF4, 0xA9, 0x81, 0xA, 0x2A, 0x0, 0x0])),
    Armorer(name='Palmod', map_id=438, professions_armor_rating=FULL_ARMOR_80, position=(-14036.0, 8632.0), model_id=5674, encoded_name=bytes([0x1, 0x81, 0x96, 0x2D, 0xA3, 0xE0, 0xD5, 0x9B, 0x23, 0x44, 0x0, 0x0])),
    Armorer(name='Vatundo', map_id=493, professions_armor_rating=FULL_ARMOR_80, position=(-3164.0, 16472.0), model_id=4773, encoded_name=bytes([0x1, 0x81, 0x3A, 0x53, 0x95, 0x8B, 0xE7, 0xF1, 0x4A, 0x51, 0x0, 0x0])),
    Armorer(name='Klub', map_id=640, professions_armor_rating=FULL_ARMOR_80, position=(12781.0, 16732.0), model_id=6810, encoded_name=bytes([0x2, 0x81, 0x9D, 0x1E, 0x36, 0x82, 0xCC, 0xBF, 0xD2, 0x7C, 0x0, 0x0])),
    Armorer(name='Brett', map_id=642, professions_armor_rating=FULL_ARMOR_80, position=(-552.0, 1250.0), model_id=6101, encoded_name=bytes([0x2, 0x81, 0xAC, 0x1E, 0x4F, 0x8B, 0x7F, 0xFE, 0xDA, 0x14, 0x0, 0x0])),
    Armorer(name='Radi', map_id=644, professions_armor_rating=FULL_ARMOR_80, position=(18894.0, -3806.0), model_id=6436, encoded_name=bytes([0x2, 0x81, 0xBC, 0x1E, 0xC1, 0xE2, 0x11, 0xA5, 0xBC, 0x65, 0x0, 0x0])),
    Armorer(name='Gobrech Stonefoot', map_id=652, professions_armor_rating=FULL_ARMOR_80, position=(1860.0, 1681.0), model_id=6287, encoded_name=bytes([0x2, 0x81, 0xDB, 0x25, 0xA7, 0xE4, 0x25, 0xBB, 0x53, 0x5D, 0x0, 0x0])),
    Armorer(name='Jolvor Stoneforge', map_id=675, professions_armor_rating=FULL_ARMOR_80, position=(5419.0, -27343.0), model_id=1553, encoded_name=bytes([0x2, 0x81, 0x42, 0x39, 0x6C, 0xCE, 0x9E, 0x95, 0x50, 0x65, 0x0, 0x0])),
    
    Armorer(name='Kambei', map_id=242, professions_armor_rating=FACTIONS_ARMOR_35, position=(-7260.0, 12622.0), model_id=3323, encoded_name=bytes([0x24, 0x57, 0x9A, 0x9F, 0x67, 0xBC, 0xA4, 0x3B, 0x0, 0x0])),
    Armorer(name='Moon Ahn', map_id=242, professions_armor_rating=FACTIONS_ARMOR_35, position=(-7115.0, 12636.0), model_id=3324, encoded_name=bytes([0x23, 0x57, 0xB5, 0xB9, 0xA5, 0xE7, 0xB5, 0x18, 0x0, 0x0])),
    Armorer(name='Nu Leng', map_id=242, professions_armor_rating=FACTIONS_ARMOR_35, position=(-6614.0, 12465.0), model_id=3323, encoded_name=bytes([0x22, 0x57, 0xC2, 0xCC, 0x6C, 0xB0, 0xCC, 0x8, 0x0, 0x0])),
    Armorer(name='Maeko', map_id=251, professions_armor_rating=FACTIONS_ARMOR_50, position=(16647.0, 16881.0), model_id=3324, encoded_name=bytes([0x19, 0x57, 0x3B, 0x8D, 0x9, 0x8E, 0x27, 0x31, 0x0, 0x0])),
    Armorer(name='Seiji', map_id=251, professions_armor_rating=FACTIONS_ARMOR_50, position=(16656.0, 17055.0), model_id=3323, encoded_name=bytes([0x1A, 0x57, 0x4B, 0xC7, 0xCC, 0x8F, 0x91, 0x21, 0x0, 0x0])),
    Armorer(name='Taura', map_id=251, professions_armor_rating=FACTIONS_ARMOR_50, position=(16425.0, 17446.0), model_id=3332, encoded_name=bytes([0x1B, 0x57, 0x80, 0xD2, 0x9F, 0xDF, 0xE1, 0x7B, 0x0, 0x0])),
    Armorer(name='Fugui Ge', map_id=250, professions_armor_rating=FACTIONS_ARMOR_65, position=(20381.0, 9576.0), model_id=3323, encoded_name=bytes([0xE, 0x57, 0x35, 0xB7, 0x51, 0x89, 0x8, 0x77, 0x0, 0x0])),
    Armorer(name='Lain', map_id=250, professions_armor_rating=FACTIONS_ARMOR_65, position=(20508.0, 9497.0), model_id=3324, encoded_name=bytes([0xF, 0x57, 0x3A, 0xBC, 0xD2, 0x85, 0x8, 0x1F, 0x0, 0x0])),
    Armorer(name='Tsukare', map_id=250, professions_armor_rating=FACTIONS_ARMOR_65, position=(19709.0, 9444.0), model_id=3331, encoded_name=bytes([0x10, 0x57, 0xE0, 0xFF, 0x2A, 0xBF, 0x5D, 0x48, 0x0, 0x0])),
    Armorer(name='Morbach', map_id=77, professions_armor_rating=FACTIONS_ARMOR_80, position=(6961.0, -1537.0), model_id=3454, encoded_name=bytes([0x9C, 0x6D, 0xA7, 0x89, 0x9F, 0xEE, 0xF1, 0x67, 0x0, 0x0])),
    Armorer(name='Giygas', map_id=130, professions_armor_rating=FACTIONS_ARMOR_80, position=(23180.0, 11879.0), model_id=3454, encoded_name=bytes([0x93, 0x6D, 0xB0, 0xB1, 0x8F, 0xEE, 0xC7, 0x31, 0x0, 0x0])),
    Armorer(name='Tateos', map_id=193, professions_armor_rating=FACTIONS_ARMOR_80, position=(4785.0, 798.0), model_id=3670, encoded_name=bytes([0xC4, 0x6D, 0x8E, 0xEC, 0xFC, 0xF0, 0x8A, 0x3F, 0x0, 0x0])),
    Armorer(name='Kakumei', map_id=194, professions_armor_rating=FACTIONS_ARMOR_80, position=(-700.0, -5156.0), model_id=3323, encoded_name=bytes([0xF5, 0x6D, 0xDC, 0xCE, 0xC8, 0xB1, 0x43, 0x4A, 0x0, 0x0])),
    Armorer(name='Suki', map_id=194, professions_armor_rating=FACTIONS_ARMOR_80, position=(-891.0, -5382.0), model_id=3324, encoded_name=bytes([0xF6, 0x6D, 0x2, 0xE8, 0x35, 0x8D, 0x50, 0x22, 0x0, 0x0])),
    Armorer(name='Ryoko', map_id=194, professions_armor_rating=FACTIONS_ARMOR_80, position=(-1682.0, -3970.0), model_id=3324, encoded_name=bytes([0xF7, 0x6D, 0x88, 0x9F, 0xC, 0xAE, 0x6A, 0x2B, 0x0, 0x0])),
    Armorer(name='Mikolas', map_id=279, professions_armor_rating=FACTIONS_ARMOR_80, position=(13037.0, -21167.0), model_id=3670, encoded_name=bytes([0x1F, 0x7B, 0x85, 0x8A, 0xB5, 0xD8, 0x94, 0x61, 0x0, 0x0])),
    
    Armorer(name='Samuka', map_id=55, professions_armor_rating=PROPH_ARMOR_50, position=(2343.0, 6843.0), model_id=2008, encoded_name=bytes([0x56, 0x2D, 0x98, 0xC2, 0x8E, 0x9E, 0x8D, 0x55, 0x0, 0x0])),
    Armorer(name='Shada', map_id=136, professions_armor_rating=PROPH_ARMOR_59, position=(20437.0, -10959.0), model_id=2008, encoded_name=bytes([0x4F, 0x2D, 0xC6, 0xB5, 0xA2, 0x86, 0x7C, 0x3A, 0x0, 0x0])),
    Armorer(name='Hagen', map_id=156, professions_armor_rating=PROPH_ARMOR_80, position=(-12914.0, 18003.0), model_id=1559, encoded_name=bytes([0xB0, 0x2D, 0x1A, 0xB6, 0xAF, 0xA5, 0x5A, 0x7C, 0x0, 0x0])),
    Armorer(name='Karl', map_id=157, professions_armor_rating=PROPH_ARMOR_80, position=(5184.0, -14389.0), model_id=1559, encoded_name=bytes([0xB3, 0x2D, 0x22, 0xA9, 0xBF, 0xD0, 0x53, 0x79, 0x0, 0x0])),
    
    Armorer(name='Banoit', map_id=81, professions_armor_rating=PROPH_ARMOR_35, position=(1545.0, 5585.0), model_id=2118, encoded_name=bytes([0x9B, 0x2D, 0x83, 0xEA, 0xD5, 0xAE, 0xAA, 0x18, 0x0, 0x0])),
    Armorer(name='Corwen', map_id=81, professions_armor_rating=PROPH_ARMOR_50, position=(1905.0, 6218.0), model_id=2120, encoded_name=bytes([0x9C, 0x2D, 0x9D, 0xA4, 0xC8, 0x89, 0x27, 0x8, 0x0, 0x0])),
    Armorer(name='Harlan', map_id=40, professions_armor_rating=PROPH_ARMOR_35, position=(22887.0, 10033.0), model_id=2118, encoded_name=bytes([0x8E, 0x2D, 0x56, 0xA0, 0x24, 0x8F, 0x6D, 0x2F, 0x0, 0x0])),
    Armorer(name='Breyshaw', map_id=134, professions_armor_rating=PROPH_ARMOR_50, position=(6561.0, 5157.0), model_id=2118, encoded_name=bytes([0xC6, 0x2D, 0x19, 0xC0, 0x7E, 0xE7, 0x2, 0x6E, 0x0, 0x0])),
    Armorer(name='Kathir', map_id=109, professions_armor_rating=PROPH_ARMOR_71, position=(1889.0, 1637.0), model_id=2046, encoded_name=bytes([0x6A, 0x2D, 0xA6, 0xFB, 0x33, 0xD5, 0xD2, 0x55, 0x0, 0x0])),
    Armorer(name='Morgren', map_id=20, professions_armor_rating=PROPH_ARMOR_80, position=(814.0, 4651.0), model_id=1558, encoded_name=bytes([0xBA, 0x2D, 0x4D, 0x87, 0x1D, 0xE3, 0xD3, 0xD, 0x0, 0x0])),
    Armorer(name='Seifred', map_id=20, professions_armor_rating=PROPH_ARMOR_80, position=(1742.0, 5162.0), model_id=1558, encoded_name=bytes([0xB9, 0x2D, 0xB8, 0xFE, 0xFE, 0xC8, 0x84, 0x51, 0x0, 0x0])),
    Armorer(name='Alemeth', map_id=49, professions_armor_rating=PROPH_ARMOR_65, position=(6016.0, -8406.0), model_id=2089, encoded_name=bytes([0x82, 0x2D, 0x91, 0xA0, 0x1C, 0x8C, 0xB7, 0x3, 0x0, 0x0])),
    Armorer(name='Kailan', map_id=57, professions_armor_rating=PROPH_ARMOR_59, position=(17558.0, -18033.0), model_id=2028, encoded_name=bytes([0x49, 0x2D, 0x55, 0xD1, 0x8, 0xE6, 0x23, 0x53, 0x0, 0x0])),
    Armorer(name='Hanita', map_id=139, professions_armor_rating=PROPH_ARMOR_65, position=(-14449.0, 2275.0), model_id=2016, encoded_name=bytes([0x79, 0x2D, 0x55, 0xFA, 0xE0, 0x86, 0x4C, 0x62, 0x0, 0x0])),
    Armorer(name='Saphir', map_id=142, professions_armor_rating=PROPH_ARMOR_59, position=(173.0, -4431.0), model_id=1544, encoded_name=bytes([0x7F, 0x2D, 0xEC, 0xB6, 0x23, 0xEC, 0xCA, 0x31, 0x0, 0x0])),
    
]

RAW_CRAFTERS = CRAFTERS.copy()
ARTISANS: list[Artisan] = []
CONSUMABLE_CRAFTERS: list[ConsumableCrafter] = []
WEAPONSMITHS: list[Weaponsmith] = []
COLLECTORS: list[Collector] = []
MERCHANTS: list[Merchant] = []
TRADERS: list[Trader] = []
ALLIES: list[Ally] = []
FOES: list[Foe] = []
_data_initialized = False


CRAFTER_TYPE_MAP = {
    'armorers': (CRAFTERS, Armorer),
    'artisans': (ARTISANS, Artisan),
    'consumable_crafters': (CONSUMABLE_CRAFTERS, ConsumableCrafter),
    'weaponsmiths': (WEAPONSMITHS, Weaponsmith),
    'collectors': (COLLECTORS, Collector),
    'merchants': (MERCHANTS, Merchant),
    'traders': (TRADERS, Trader),
    'allies': (ALLIES, Ally),
    'foes': (FOES, Foe),
}

PROFESSION_ORDER = [
    Profession.Warrior,
    Profession.Ranger,
    Profession.Monk,
    Profession.Necromancer,
    Profession.Mesmer,
    Profession.Elementalist,
    Profession.Assassin,
    Profession.Ritualist,
    Profession.Paragon,
    Profession.Dervish,
]

PROFESSION_LABELS = {
    Profession.Warrior: 'W',
    Profession.Ranger: 'R',
    Profession.Monk: 'Mo',
    Profession.Necromancer: 'N',
    Profession.Mesmer: 'Me',
    Profession.Elementalist: 'E',
    Profession.Assassin: 'A',
    Profession.Ritualist: 'Rt',
    Profession.Paragon: 'P',
    Profession.Dervish: 'D',
}

search_query = ''
show_unlocked_only = False
show_armorers = True
show_artisans = True
show_consumable_crafters = True
show_weaponsmiths = True
show_collectors = True
show_merchants = True
show_traders = True
show_allies = False
show_foes = False
out_posts = Map.GetOutpostIDs()
sweep_stop_requested = False
sweep_is_running = False
sweep_status = 'Idle'
sweep_current_name = ''
sweep_current_index = 0
sweep_total = 0
_data_revision = 0
_visible_npcs_cache: list['AnyNpc'] = []
_visible_npcs_cache_key: tuple[Any, ...] | None = None
_stats_cache: dict[str, Any] = {}
_stats_cache_revision = -1
_last_passive_scan_at: datetime | None = None
_last_scan_instance_key: tuple[int, int, int, int] | None = None
_scanned_agent_ids_current_map: set[int] = set()
_pending_agent_scan_attempts_current_map: dict[int, int] = {}
_current_map_stationary_npcs: list[StationaryNpc] = []
_current_map_missing_stationary_npcs: list[StationaryNpc] = []
_pending_auto_save = False
_last_auto_save_at: datetime | None = None
_dirty_category_keys: set[str] = set()

AnyCrafter = Armorer | Artisan | ConsumableCrafter | Weaponsmith | Collector | Merchant
AnyNpc = Armorer | Artisan | ConsumableCrafter | Weaponsmith | Collector | Merchant | Trader | Ally | Foe


def _ensure_initialized():
    global _data_initialized

    if _data_initialized:
        return

    load_crafters_from_json()
    _data_initialized = True


def _get_current_profession() -> Profession:
    agent = Agent.GetAgentByID(Player.GetAgentID())
    living_agent = agent.GetAsAgentLiving() if agent is not None else None

    if living_agent is None:
        return Profession._None

    try:
        return Profession(living_agent.primary)
    except Exception:
        return Profession._None


def _get_current_map_instance_key() -> tuple[int, int, int, int]:
    return (
        int(Map.GetMapID() or 0),
        int(Map.GetDistrict() or 0),
        int(Map.GetRegion()[0] or 0),
        int(Map.GetLanguage()[0] or 0),
    )


def _get_title_rank(title_id: TitleID) -> int:
    title = Player.GetTitle(int(title_id))
    if title is None:
        return 0

    tiers = TITLE_TIERS.get(int(title_id), [])
    if tiers:
        return sum(1 for tier in tiers if title.current_points >= tier.required)
    return int(title.current_title_tier_index or 0)


def _is_stationary_npc_in_map(npc: StationaryNpc, map_id: int) -> bool:
    return npc.map_id != 0 and Map.GetBaseMapID(npc.map_id) == Map.GetBaseMapID(map_id)


def _is_stationary_npc_missing_metadata(npc: StationaryNpc) -> bool:
    return npc.position == (0.0, 0.0) or npc.model_id == 0 or not npc.encoded_name


def _rebuild_current_map_stationary_indexes(map_id: int):
    global _current_map_stationary_npcs
    global _current_map_missing_stationary_npcs

    stationary_npcs = [
        npc
        for npc in [*_iter_all_crafters(), *TRADERS, *ALLIES]
        if _is_stationary_npc_in_map(npc, map_id)
    ]
    _current_map_stationary_npcs = stationary_npcs
    _current_map_missing_stationary_npcs = [npc for npc in stationary_npcs if _is_stationary_npc_missing_metadata(npc)]


def _meets_faction_requirement(requirement: FactionRequirement) -> bool:
    kurzick_current = int(Player.GetKurzickData()[0] or 0)
    luxon_current = int(Player.GetLuxonData()[0] or 0)
    if requirement == FactionRequirement.Kurzick:
        return kurzick_current > luxon_current
    if requirement == FactionRequirement.Luxon:
        return luxon_current > kurzick_current
    return True


def _get_armor_rating_for_profession(profession: Profession) -> int:
    if profession in (Profession.Warrior, Profession.Paragon):
        return 80
    if profession in (Profession.Ranger, Profession.Assassin, Profession.Dervish):
        return 70
    if profession in (Profession.Monk, Profession.Necromancer, Profession.Mesmer, Profession.Elementalist, Profession.Ritualist):
        return 60
    return 0


def _iter_all_crafters() -> list[AnyCrafter]:
    return [*CRAFTERS, *ARTISANS, *CONSUMABLE_CRAFTERS, *WEAPONSMITHS, *COLLECTORS, *MERCHANTS]


def _iter_all_npcs() -> list[AnyNpc]:
    return [*_iter_all_crafters(), *TRADERS, *ALLIES, *FOES]


def _get_category_key_for_npc(npc: Npc) -> str:
    if isinstance(npc, Armorer):
        return 'armorers'
    if isinstance(npc, Artisan):
        return 'artisans'
    if isinstance(npc, ConsumableCrafter):
        return 'consumable_crafters'
    if isinstance(npc, Weaponsmith):
        return 'weaponsmiths'
    if isinstance(npc, Collector):
        return 'collectors'
    if isinstance(npc, Merchant):
        return 'merchants'
    if isinstance(npc, Trader):
        return 'traders'
    if isinstance(npc, Foe):
        return 'foes'
    return 'allies'


def _get_snapshot_name(item: ItemSnapshot) -> str:
    return item.names.plain_singular if item.names.plain_singular != 'Unknown Item' else ''

def _build_craftable_item_from_snapshot(item: ItemSnapshot) -> CraftableItem | CraftableWeapon | CraftableArmor:
    item_name = _get_snapshot_name(item)
    if item.is_weapon:
        return CraftableWeapon(
            name=item_name,
            item_type=item.item_type,
            model_id=item.model_id,
            requirement=item.requirement,
            attribute=item.attribute,
            damage=(item.min_damage, item.max_damage),
            energy=item.energy,
            prefix=item.prefix,
            suffix=item.suffix,
            inscription=item.inscription,
            inherent=list(item.inherents or []),
        )
    if item.is_armor:
        profession = item.profession if item.profession not in (None, Profession._None) else _get_current_profession()
        return CraftableArmor(
            name=item_name,
            item_type=item.item_type,
            model_id=item.model_id,
            profession=profession,
            armor_rating=item.armor
        )
    return CraftableItem(
        name=item_name,
        item_type=item.item_type,
        model_id=item.model_id,
    )


def _build_craftable_weapon_from_snapshot(item: ItemSnapshot) -> CraftableWeapon:
    return cast(CraftableWeapon, _build_craftable_item_from_snapshot(item))


def _build_craftable_armor_from_snapshot(item: ItemSnapshot) -> CraftableArmor:
    return cast(CraftableArmor, _build_craftable_item_from_snapshot(item))


def _build_plain_craftable_item_from_snapshot(item: ItemSnapshot) -> CraftableItem:
    item_name = _get_snapshot_name(item)
    return CraftableItem(
        name=item_name,
        item_type=item.item_type,
        model_id=item.model_id,
    )


def _build_item_from_snapshot(item: ItemSnapshot) -> Item | Weapon | Armor:
    item_name = _get_snapshot_name(item)
    if item.is_weapon:
        return Weapon(
            name=item_name,
            item_type=item.item_type,
            model_id=item.model_id,
            requirement=item.requirement,
            attribute=item.attribute,
            damage=(item.min_damage, item.max_damage),
            energy=item.energy,
            prefix=item.prefix,
            suffix=item.suffix,
            inscription=item.inscription,
            inherent=list(item.inherents or []),
        )
    if item.is_armor:
        profession = item.profession if item.profession not in (None, Profession._None) else _get_current_profession()
        return Armor(
            name=item_name,
            item_type=item.item_type,
            model_id=item.model_id,
            profession=profession,
            armor_rating=item.armor,
        )
    return Item(
        name=item_name,
        item_type=item.item_type,
        model_id=item.model_id,
    )


def _build_collectible_item_from_snapshot(item: ItemSnapshot, required_collectible: tuple[int, int] | None) -> Item:
    item_name = _get_snapshot_name(item)
    if item.is_weapon:
        return CollectibleWeapon(
            name=item_name,
            item_type=item.item_type,
            model_id=item.model_id,
            requirement=item.requirement,
            attribute=item.attribute,
            damage=(item.min_damage, item.max_damage),
            energy=item.energy,
            prefix=item.prefix,
            suffix=item.suffix,
            inscription=item.inscription,
            inherent=list(item.inherents or []),
            required_collectible=required_collectible or tuple[int, int](),
        )
        
    if item.is_armor:
        profession = item.profession if item.profession not in (None, Profession._None) else _get_current_profession()

        return CollectibleArmor(
            name=item_name,
            item_type=item.item_type,
            model_id=item.model_id,
            profession=profession,
            armor_rating=item.armor,
            required_collectible=required_collectible or tuple[int, int](),
        )
        
    return CollectorItem(
        name=item_name,
        item_type=item.item_type,
        model_id=item.model_id,
        required_collectible=required_collectible or tuple[int, int](),
    )


def _build_collectible_item_typed_from_snapshot(
    item: ItemSnapshot,
    required_collectible: tuple[int, int] | None,
) -> CollectibleWeapon | CollectibleArmor | CollectorItem:
    return cast(CollectibleWeapon | CollectibleArmor | CollectorItem, _build_collectible_item_from_snapshot(item, required_collectible))


def _normalize_item_name(name: str) -> str:
    return ''.join(character.lower() for character in name if character.isalnum())


def _is_missing_name(name: str) -> bool:
    return not name or name.startswith('Model')


def _is_unknown_item_type(item_type: ItemType) -> bool:
    return item_type == ItemType.Unknown


def _named_item_sort_key(item: Any) -> tuple[str, str]:
    item_type = item.item_type.name if hasattr(item.item_type, 'name') else str(item.item_type)
    return item_type, item.name


def _has_specific_attribute(item: Any) -> bool:
    return getattr(item, 'attribute', Attribute.None_) != Attribute.None_


def _has_specific_profession(item: Any) -> bool:
    return getattr(item, 'profession', Profession._None) != Profession._None


def _item_specificity_rank(item: Any) -> int:
    if isinstance(item, CollectibleWeapon):
        return 4
    if isinstance(item, CollectibleArmor):
        return 4
    if isinstance(item, Weapon):
        return 3
    if isinstance(item, Armor):
        return 3
    if isinstance(item, CollectorItem):
        return 2
    return 1


def _same_item_identity(existing: Any, candidate: Any) -> bool:
    same_name = _normalize_item_name(existing.name) == _normalize_item_name(candidate.name)
    same_type = existing.item_type == candidate.item_type or _is_unknown_item_type(existing.item_type) or _is_unknown_item_type(candidate.item_type)
    same_attribute = (
        not _has_specific_attribute(existing)
        or not _has_specific_attribute(candidate)
        or getattr(existing, 'attribute', Attribute.None_) == getattr(candidate, 'attribute', Attribute.None_)
    )
    same_profession = (
        not _has_specific_profession(existing)
        or not _has_specific_profession(candidate)
        or getattr(existing, 'profession', Profession._None) == getattr(candidate, 'profession', Profession._None)
    )
    same_collectible = getattr(existing, 'required_collectible', None) == getattr(candidate, 'required_collectible', None)

    if existing.model_id and candidate.model_id and not hasattr(existing, 'attribute'):
        return existing.model_id == candidate.model_id and same_type

    if same_collectible and same_collectible != tuple[int, int]():
        return same_name and same_type and same_attribute and same_profession

    return same_name and same_type and same_attribute and same_profession


def _merge_base_item_fields(existing: Any, candidate: Any) -> bool:
    changed = False

    if _is_missing_name(existing.name) and not _is_missing_name(candidate.name):
        existing.name = candidate.name
        changed = True

    if _is_unknown_item_type(existing.item_type) and not _is_unknown_item_type(candidate.item_type):
        existing.item_type = candidate.item_type
        changed = True

    if int(existing.model_id or 0) == 0 and int(candidate.model_id or 0) != 0:
        existing.model_id = candidate.model_id
        changed = True

    if hasattr(existing, 'required_materials'):
        existing_requirements = getattr(existing, 'required_materials', None)
        candidate_requirements = getattr(candidate, 'required_materials', None)
        if isinstance(existing_requirements, CraftingRequirements) and isinstance(candidate_requirements, CraftingRequirements):
            if existing_requirements == CraftingRequirements() and candidate_requirements != CraftingRequirements():
                existing.required_materials = candidate_requirements
                changed = True

    if hasattr(existing, 'required_collectible'):
        existing_collectible = getattr(existing, 'required_collectible', None)
        candidate_collectible = getattr(candidate, 'required_collectible', None)
        if not existing_collectible and candidate_collectible:
            existing.required_collectible = candidate_collectible
            changed = True

    return changed


def _merge_weapon_fields(existing: Weapon, candidate: Weapon) -> bool:
    changed = _merge_base_item_fields(existing, candidate)

    if existing.requirement == 0 and candidate.requirement != 0:
        existing.requirement = candidate.requirement
        changed = True
    if existing.attribute == Attribute.None_ and candidate.attribute != Attribute.None_:
        existing.attribute = candidate.attribute
        changed = True
    if existing.damage == (0, 0) or existing.damage is None and candidate.damage != (0, 0):
        existing.damage = candidate.damage
        changed = True
    if existing.energy is None and candidate.energy is not None:
        existing.energy = candidate.energy
        changed = True
    if existing.prefix is None and candidate.prefix is not None:
        existing.prefix = candidate.prefix
        changed = True
    if existing.suffix is None and candidate.suffix is not None:
        existing.suffix = candidate.suffix
        changed = True
    if existing.inscription is None and candidate.inscription is not None:
        existing.inscription = candidate.inscription
        changed = True
    if not existing.inherent and candidate.inherent:
        existing.inherent = list(candidate.inherent)
        changed = True

    return changed


def _merge_armor_fields(existing: Armor, candidate: Armor) -> bool:
    changed = _merge_base_item_fields(existing, candidate)

    if existing.armor_rating == 0 and candidate.armor_rating != 0:
        existing.armor_rating = candidate.armor_rating
        changed = True
    if existing.profession == Profession._None and candidate.profession != Profession._None:
        existing.profession = candidate.profession
        changed = True

    return changed


def _upsert_named_item(items: list[Any], candidate: Any) -> bool:
    existing_index = next((index for index, existing in enumerate(items) if _same_item_identity(existing, candidate)), -1)
    if existing_index >= 0:
        existing = items[existing_index]
        if _item_specificity_rank(candidate) > _item_specificity_rank(existing):
            replacement = candidate
            if isinstance(existing, Weapon) and isinstance(replacement, Weapon):
                _merge_weapon_fields(replacement, existing)
            elif isinstance(existing, Armor) and isinstance(replacement, Armor):
                _merge_armor_fields(replacement, existing)
            else:
                _merge_base_item_fields(replacement, existing)
            items[existing_index] = replacement
            changed = True
        elif isinstance(existing, Weapon) and isinstance(candidate, Weapon):
            changed = _merge_weapon_fields(existing, candidate)
        elif isinstance(existing, Armor) and isinstance(candidate, Armor):
            changed = _merge_armor_fields(existing, candidate)
        else:
            changed = _merge_base_item_fields(existing, candidate)
        if not changed:
            return False
    else:
        items.append(candidate)
        changed = True

    items.sort(key=_named_item_sort_key)
    return changed


def _log_collection_result(crafter_name: str, collected_count: int, item_label: str):
    if collected_count > 0:
        Py4GW.Console.Log(MODULE_NAME, f"Collected {collected_count} {item_label} entries from '{crafter_name}'.", Py4GW.Console.MessageType.Success)
    else:
        Py4GW.Console.Log(MODULE_NAME, f"No new {item_label} entries were found for '{crafter_name}'.", Py4GW.Console.MessageType.Warning)


def _touch_data_revision():
    global _data_revision

    _data_revision += 1


def _mark_data_dirty(category_keys: str | Iterable[str] | None = None, queue_save: bool = False):
    global _pending_auto_save
    global _dirty_category_keys

    _touch_data_revision()

    if category_keys is None:
        _dirty_category_keys.update(CRAFTER_TYPE_MAP.keys())
    elif isinstance(category_keys, str):
        _dirty_category_keys.add(category_keys)
    else:
        _dirty_category_keys.update(category_keys)

    if queue_save:
        _pending_auto_save = True


def _flush_pending_auto_save():
    global _pending_auto_save
    global _last_auto_save_at

    if not _pending_auto_save:
        return

    now = datetime.utcnow()
    if _last_auto_save_at is not None and now - _last_auto_save_at < timedelta(seconds=3):
        return

    save_crafters_to_json()
    _pending_auto_save = False
    _last_auto_save_at = now


def _collect_simple_crafter_items(crafter: Npc, items: list[CraftableItem]) -> bool:
    if not crafter.IsCrafterOpen():
        Py4GW.Console.Log(MODULE_NAME, f"Crafter '{crafter.name}' is not open. Please move to the crafter and open their crafting window before collecting data.", Py4GW.Console.MessageType.Warning)
        return False

    snapshots = [ItemSnapshot.from_item_id(item_id) for item_id in crafter._get_offered_items()]
    collected_count = 0
    pending_name_update = False

    for item in snapshots:
        if item is None or not item.is_valid:
            continue

        item_name = _get_snapshot_name(item)
        if not item_name:
            pending_name_update = True
            continue

        craftable_item = _build_plain_craftable_item_from_snapshot(item)
        if _upsert_named_item(items, craftable_item):
            collected_count += 1

    _log_collection_result(crafter.name, collected_count, 'craftable item')
    if pending_name_update:
        Py4GW.Console.Log(MODULE_NAME, f"Some collected items from '{crafter.name}' are missing names and will be updated once the names are available. Please collect from this crafter again...", Py4GW.Console.MessageType.Warning)
    return not pending_name_update and collected_count > 0


def _get_category_file_paths() -> dict[str, str]:
    return {key: os.path.join(DATA_DIRECTORY_PATH, f'{key}.json') for key in CRAFTER_TYPE_MAP}


def save_crafters_to_json():
    global _dirty_category_keys

    category_paths = _get_category_file_paths()
    os.makedirs(DATA_DIRECTORY_PATH, exist_ok=True)

    dirty_keys = list(_dirty_category_keys)
    if not dirty_keys:
        Py4GW.Console.Log(
            MODULE_NAME,
            'No category files have changed; skipping JSON save.',
            Py4GW.Console.MessageType.Info,
        )
        return

    saved_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

    for key in dirty_keys:
        container, _ = CRAFTER_TYPE_MAP[key]
        entries = [_strip_none_for_json(npc.to_dict()) for npc in container]
        with open(category_paths[key], 'w', encoding='utf-8') as file:
            json.dump(
                _strip_none_for_json({
                    'version': 3,
                    'saved_at': saved_at,
                    'category': key,
                    'entries': entries,
                }),
                file,
                indent=4,
                ensure_ascii=False,
            )

    total_count = sum(len(CRAFTER_TYPE_MAP[key][0]) for key in dirty_keys)
    Py4GW.Console.Log(
        MODULE_NAME,
        f"Saved {len(dirty_keys)} changed file(s) with {total_count} NPCs to '{DATA_DIRECTORY_PATH}'.",
        Py4GW.Console.MessageType.Success,
    )
    for key in dirty_keys:
        _dirty_category_keys.discard(key)
    _touch_data_revision()


def load_crafters_from_json():
    global _dirty_category_keys

    category_paths = _get_category_file_paths()
    loaded_any = False
    if not all(os.path.exists(category_path) for category_path in category_paths.values()):
        Py4GW.Console.Log(
            MODULE_NAME,
            f"NPC data files do not exist yet in '{DATA_DIRECTORY_PATH}'.",
            Py4GW.Console.MessageType.Warning,
        )
        return False

    for key, (container, crafter_type) in CRAFTER_TYPE_MAP.items():
        with open(category_paths[key], 'r', encoding='utf-8') as file:
            payload = json.load(file)
        container[:] = [crafter_type.from_dict(entry) for entry in list(payload.get('entries', []))]
        loaded_any = loaded_any or bool(container)

    if not loaded_any:
        Py4GW.Console.Log(
            MODULE_NAME,
            f"No NPC entries were found in '{DATA_DIRECTORY_PATH}'.",
            Py4GW.Console.MessageType.Warning,
        )
        return False

    total_count = sum(len(container) for container, _ in CRAFTER_TYPE_MAP.values())
    Py4GW.Console.Log(
        MODULE_NAME,
        f"Loaded {total_count} NPCs from '{DATA_DIRECTORY_PATH}'.",
        Py4GW.Console.MessageType.Success,
    )
    _dirty_category_keys.clear()
    
    updated = False
    for crafter in CRAFTERS:
        if not _is_position_collected(crafter) or not crafter.encoded_name:
            #Check RAW_CRAFTERS for position data
            raw_match = next((raw for raw in RAW_CRAFTERS if raw.name == crafter.name and raw.map_id == crafter.map_id), None)
            if raw_match:
                crafter.position = raw_match.position
                crafter.model_id = raw_match.model_id
                crafter.encoded_name = raw_match.encoded_name
                updated = True
                
    if updated:
        _mark_data_dirty('armorers')
        save_crafters_to_json()
    else:
        _touch_data_revision()
        
    return True


def _find_current_open_crafter() -> AnyNpc | None:
    current_map_id = Map.GetBaseMapID()
    for crafter in _iter_all_npcs():
        if current_map_id not in [Map.GetBaseMapID(map_id) for map_id in crafter.GetMapIDs()]:
            continue
        
        if crafter.IsCrafterOpen():
            return crafter
        
    return None


def _collect_current_open_crafter():
    crafter = _find_current_open_crafter()
    if crafter is None:
        Py4GW.Console.Log(
            MODULE_NAME,
            'No known service window is currently open on this map.',
            Py4GW.Console.MessageType.Warning,
        )
        return

    collected_count = crafter.CollectData()
    if collected_count > 0:
        _mark_data_dirty(_get_category_key_for_npc(crafter))
        save_crafters_to_json()

def _format_armor_ratings(crafter: Armorer) -> str:
    return '  '.join(
        f'{PROFESSION_LABELS[profession]}:{crafter.professions_armor_rating[profession]}'
        for profession in PROFESSION_ORDER
        if profession in crafter.professions_armor_rating
    )


def _matches_search(crafter: AnyNpc, query: str) -> bool:
    if not query:
        return True

    query = query.lower()
    map_names = [Map.GetMapName(map_id).lower() for map_id in crafter.GetMapIDs()]
    service_name = crafter.service_label().lower()
    return query in crafter.name.lower() or any(query in map_name for map_name in map_names) or query in service_name


def _is_type_visible(crafter: AnyNpc) -> bool:
    if isinstance(crafter, Armorer):
        return show_armorers
    if isinstance(crafter, Artisan):
        return show_artisans
    if isinstance(crafter, ConsumableCrafter):
        return show_consumable_crafters
    if isinstance(crafter, Weaponsmith):
        return show_weaponsmiths
    if isinstance(crafter, Collector):
        return show_collectors
    if isinstance(crafter, Merchant):
        return show_merchants
    if isinstance(crafter, Trader):
        return show_traders
    if isinstance(crafter, Foe):
        return show_foes
    if isinstance(crafter, Ally):
        return show_allies
    return True


def _get_filter_cache_key() -> tuple[Any, ...]:
    return (
        _data_revision,
        search_query.strip().lower(),
        show_unlocked_only,
        show_armorers,
        show_artisans,
        show_consumable_crafters,
        show_weaponsmiths,
        show_collectors,
        show_merchants,
        show_traders,
        show_allies,
        show_foes,
    )


def _get_visible_crafters() -> list[AnyNpc]:
    global _visible_npcs_cache
    global _visible_npcs_cache_key

    cache_key = _get_filter_cache_key()
    if _visible_npcs_cache_key == cache_key:
        return list(_visible_npcs_cache)

    visible: list[AnyNpc] = []
    for crafter in _iter_all_npcs():
        if not _is_type_visible(crafter):
            continue
        if show_unlocked_only and not crafter.HasMapUnlocked():
            continue
        if not _matches_search(crafter, search_query.strip()):
            continue
        visible.append(crafter)
    _visible_npcs_cache = visible
    _visible_npcs_cache_key = cache_key
    return list(visible)


def _is_position_collected(crafter: AnyNpc) -> bool:
    if isinstance(crafter, StationaryNpc):
        return crafter.HasStationaryData() and crafter.model_id != 0
    if isinstance(crafter, Foe):
        return bool(crafter.spawns) and crafter.model_id != 0
    return crafter.model_id != 0
    
def _is_auto_reachable_crafter(crafter: AnyNpc) -> bool:
    return (
        isinstance(crafter, StationaryNpc)
        and crafter.HasMapUnlocked()
        and crafter.map_id in out_posts
        and crafter.position != (0.0, 0.0)
        and crafter.model_id != 0
    )


def _has_missing_collection_data(crafter: AnyNpc) -> bool:
    if isinstance(crafter, Armorer):
        profession = _get_current_profession()
        if profession == Profession._None or profession not in crafter.professions_armor_rating:
            return False
        armors = crafter.armors.get(profession, [])
        return not armors or any(not armor.name or armor.name.startswith('Model') or armor.model_id == 0 or armor.armor_rating == 0 for armor in armors)
    
    if isinstance(crafter, Collector):
        profession =  _get_current_profession()
        armor_items = [item for item in crafter.items if isinstance(item, CollectibleArmor)]
        remaining_items = [item for item in crafter.items if not item in armor_items]       
        profession_armors = [item for item in armor_items if item.profession == profession]
        
        incomplete_profession_armors = [item for item in profession_armors if item.model_id == 0 or not item.name or item.armor_rating == 0]
        
        needs_profession_armor = len(incomplete_profession_armors) > 0
        has_non_armor_items = len(remaining_items) > 0
        incomplete_items = [item for item in remaining_items if item.model_id == 0 or not item.name]
        
        
        return needs_profession_armor or \
               (has_non_armor_items and bool(not crafter.items or len(incomplete_items) > 0))
               
    if isinstance(crafter, Weaponsmith):
        return (len(crafter.weapons) > 0 and any(weapon.model_id == 0 or not weapon.name for weapon in crafter.weapons))
    if isinstance(crafter, ConsumableCrafter):
        return not crafter.consumables or any(item.model_id == 0 or not item.name for item in crafter.consumables)
    if isinstance(crafter, Artisan):
        return not crafter.items or any(item.model_id == 0 or not item.name for item in crafter.items)
    if isinstance(crafter, Merchant):
        return not crafter.items or any(item.model_id == 0 or not item.name for item in crafter.items)
    return False


def _get_sort_value(crafter: AnyNpc, profession: Profession) -> int:
    if isinstance(crafter, Armorer) and profession is not None:
        return crafter.professions_armor_rating.get(profession, -1)
    return crafter.GetCollectedCount()


def _get_auto_reachable_crafters() -> list[AnyCrafter]:
    crafters = [
        crafter
        for crafter in _get_visible_crafters()
        if _is_auto_reachable_crafter(crafter) and _has_missing_collection_data(crafter) and crafter.CanInteract()
    ]
            
    sorted_crafters = sorted(crafters, key=lambda c: (c.GetDisplayMapID(), c.name))
    
    return [crafter for crafter in sorted_crafters if isinstance(crafter, AnyCrafter)]


def _get_dashboard_stats() -> dict[str, Any]:
    global _stats_cache
    global _stats_cache_revision

    if _stats_cache_revision == _data_revision:
        return dict(_stats_cache)

    all_npcs = _iter_all_npcs()
    stats = {
        'all_npcs': all_npcs,
        'unlocked_count': sum(1 for npc in all_npcs if npc.HasMapUnlocked()),
        'auto_reachable_count': len(_get_auto_reachable_crafters()),
        'total_collected_entries': sum(npc.GetCollectedCount() for npc in all_npcs),
        'armorer_count': len(CRAFTERS),
        'artisan_count': len(ARTISANS),
        'consumable_crafter_count': len(CONSUMABLE_CRAFTERS),
        'weaponsmith_count': len(WEAPONSMITHS),
        'collector_count': len(COLLECTORS),
        'merchant_count': len(MERCHANTS),
        'trader_count': len(TRADERS),
        'ally_count': len(ALLIES),
        'foe_count': len(FOES),
    }
    _stats_cache = stats
    _stats_cache_revision = _data_revision
    return dict(stats)


def _set_sweep_status(status: str, crafter_name: str = '', current_index: int = 0, total: int = 0):
    global sweep_status
    global sweep_current_name
    global sweep_current_index
    global sweep_total

    sweep_status = status
    sweep_current_name = crafter_name
    sweep_current_index = current_index
    sweep_total = total


def _finish_sweep(status: str):
    global sweep_is_running
    global sweep_stop_requested

    sweep_is_running = False
    sweep_stop_requested = False
    _set_sweep_status(status)


def _start_crafter_sweep():
    global sweep_is_running
    global sweep_stop_requested

    if sweep_is_running:
        return

    reachable_crafters = _get_auto_reachable_crafters()
    if not reachable_crafters:
        _set_sweep_status('No unlocked auto-reachable crafters found.')
        return

    sweep_is_running = True
    sweep_stop_requested = False
    _set_sweep_status('Starting crafter sweep...', total=len(reachable_crafters))
    GLOBAL_CACHE.Coroutines.append(_run_crafter_sweep(reachable_crafters))


def _request_stop_crafter_sweep():
    global sweep_stop_requested

    GLOBAL_CACHE.Coroutines.clear()  # Clear any pending steps to expedite stopping
    if not sweep_is_running:
        return

    sweep_stop_requested = True
    _set_sweep_status('Stopping after current step...', sweep_current_name, sweep_current_index, sweep_total)


def _run_crafter_sweep(crafters: list[AnyCrafter]):
    total = len(crafters)
    closed_count = 0

    for index, crafter in enumerate(crafters, start=1):
        if sweep_stop_requested:
            _finish_sweep(f'Sweep stopped ({closed_count}/{total} completed).')
            return

        map_id = crafter.GetDisplayMapID()
        position = crafter.GetDisplayPosition()
        map_name = Map.GetMapName(map_id)
        _set_sweep_status(f'Traveling to {map_name}...', crafter.name, index, total)

        if Map.GetBaseMapID() != Map.GetBaseMapID(map_id):
            travel_success = yield from Routines.Yield.Map.TravelToOutpost(map_id, timeout=20000, log=False)
            if not travel_success:
                Py4GW.Console.Log(
                    MODULE_NAME,
                    f"Skipping '{crafter.name}' because travel to '{map_name}' failed.",
                    Py4GW.Console.MessageType.Warning,
                )
                continue

            yield from Routines.Yield.wait(500, break_on_map_transition=True)

        if sweep_stop_requested:
            _finish_sweep(f'Sweep stopped ({closed_count}/{total} completed).')
            return

        _set_sweep_status('Walking to crafter...', crafter.name, index, total)
        distance_to_crafter = Utils.Distance(Player.GetXY(), position)
        Py4GW.Console.Log(
            MODULE_NAME,
            f"Distance to '{crafter.name}' is {distance_to_crafter:.1f}. Allowing up to {int(distance_to_crafter * 10)} ms for movement.",
            Py4GW.Console.MessageType.Info,
        )
        
        move_success = yield from Routines.Yield.Movement.FollowPath([position], tolerance=200, timeout=int(distance_to_crafter * 50), log=False)
        if not move_success:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"Skipping '{crafter.name}' because movement to the stored position failed.",
                Py4GW.Console.MessageType.Warning,
            )
            continue

        _set_sweep_status(f"Opening {crafter.service_label().lower()} window...", crafter.name, index, total)
        window_opened = yield from _open_crafter_window(crafter)
        if not window_opened:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"Skipping '{crafter.name}' because the service window did not open.",
                Py4GW.Console.MessageType.Warning,
            )
            continue

        _set_sweep_status(f"Collecting visible {crafter.service_label().lower()} data...", crafter.name, index, total)
        try:
            collected = crafter.CollectData()
            if collected:
                _mark_data_dirty(_get_category_key_for_npc(crafter))
                save_crafters_to_json()
        except Exception as exc:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"Skipping '{crafter.name}' because data collection failed: {exc}",
                Py4GW.Console.MessageType.Warning,
            )
            continue

        _set_sweep_status('Service window open, waiting 2 seconds...', crafter.name, index, total)
        yield from Routines.Yield.wait(2000)
        crafter.CloseCrafter()
        yield from Routines.Yield.wait(500)
        closed_count += 1

    _finish_sweep(f'Sweep complete ({closed_count}/{total} windows opened).')


def _open_crafter_window(crafter: AnyCrafter, timeout_ms: int = 1500):
    elapsed = 0
    retry_interval = 250
    reissue_interval = 1000
    since_reissue = reissue_interval

    while elapsed <= timeout_ms:
        if sweep_stop_requested:
            return False

        if not crafter.CanInteract():
            Py4GW.Console.Log(MODULE_NAME, f"Skipping '{crafter.name}' because your character does not currently meet {crafter.interaction_label()}.", Py4GW.Console.MessageType.Warning)
            return False

        if crafter._service_window_is_open():
            return True

        agent_id = crafter.GetAgentId()
        if agent_id == 0:
            yield from Routines.Yield.wait(retry_interval)
            elapsed += retry_interval
            since_reissue += retry_interval
            continue

        if since_reissue >= reissue_interval:
            yield from Routines.Yield.Agents.ChangeTarget(agent_id)
            yield from Routines.Yield.Agents.InteractAgent(agent_id)
            since_reissue = 0

        player_distance = Utils.Distance(Player.GetXY(), Agent.GetXY(agent_id))
        if player_distance > 220.0:
            yield from Routines.Yield.Movement.FollowPath([crafter.GetDisplayPosition()], tolerance=150, timeout=5000, log=False)
        else:
            yield from Routines.Yield.wait(retry_interval)

        elapsed += retry_interval
        since_reissue += retry_interval

    return crafter._service_window_is_open()


def get_armor_rating_as_constant_name(crafter: Armorer) -> str:
    for constant_name, armor_dict in globals().items():
        if isinstance(armor_dict, dict) and all(
            profession in armor_dict and armor_dict[profession] == crafter.professions_armor_rating.get(profession, -1)
            for profession in crafter.professions_armor_rating
        ):
            return constant_name
        
    return "CUSTOM"


def _build_crafter_clipboard_text(crafter: AnyCrafter, position: tuple[float, float], model_id: int, encoded_name: bytes) -> str:
    encoded_name_text = ', '.join(f'0x{byte:X}' for byte in encoded_name)
    base_args = (
        f"name='{crafter.name}', "
        f"map_id={crafter.map_id}, "
    )
    if isinstance(crafter, Armorer):
        base_args += f'professions_armor_rating={get_armor_rating_as_constant_name(crafter)}, '
    base_args += (
        f'position=({position[0]:.1f}, {position[1]:.1f}), '
        f'model_id={model_id}, '
        f'encoded_name=bytes([{encoded_name_text}])'
    )
    return f'{crafter.__class__.__name__}({base_args}),'


def _update_npc_metadata(npc: Npc, position: tuple[float, float], model_id: int, encoded_name: bytes) -> bool:
    changed = False
    if npc.model_id == 0 and model_id != 0:
        npc.model_id = model_id
        changed = True
    if not npc.encoded_name and encoded_name:
        npc.encoded_name = encoded_name
        changed = True
    return changed


def _update_stationary_npc_metadata(npc: StationaryNpc, position: tuple[float, float], model_id: int, encoded_name: bytes) -> bool:
    changed = _update_npc_metadata(npc, position, model_id, encoded_name)
    if npc.position == (0.0, 0.0) and position != (0.0, 0.0):
        npc.position = position
        changed = True
    return changed


def _find_npc_match(container: Sequence[StationaryNpc], name: str, map_id: int, model_id: int = 0) -> StationaryNpc | None:
    normalized_name = _normalize_item_name(name)
    base_map_id = Map.GetBaseMapID(map_id)
    for npc in container:
        if not _normalize_item_name(npc.name) in normalized_name:
            continue
        if Map.GetBaseMapID(npc.map_id) != base_map_id:
            continue
        if model_id != 0 and npc.model_id not in (0, model_id):
            continue
        return npc
    return None


def _classify_service_npc(name: str) -> type[AnyNpc]:
    lowered_name = name.lower()
    if 'trader' in lowered_name:
        return Trader
    if 'merchant' in lowered_name:
        return Merchant
    return Ally


def _resolve_profession_name(name: str) -> Optional[Profession]:
    normalized = name.replace(' ', '')
    if not normalized or normalized == Profession._None.name:
        return None
    return Profession[normalized] if normalized in Profession.__members__ else None


def _find_foe_match(name: str, model_id: int, encoded_name: bytes, primary: Optional[Profession], secondary: Optional[Profession]) -> Foe | None:
    normalized_name = _normalize_item_name(name)
    for foe in FOES:
        if model_id != 0 and foe.model_id not in (0, model_id):
            continue
        if encoded_name and foe.encoded_name and foe.encoded_name != encoded_name:
            continue
        if foe.primary_profession != primary or foe.secondary_profession != secondary:
            continue
        if normalized_name and _normalize_item_name(foe.name) != normalized_name:
            continue
        return foe
    return None


def _upsert_foe_spawn(agent_id: int, map_id: int, updated: bool) -> bool:
    name = Agent.GetNameByID(agent_id)
    if not name:
        return updated

    model_id = int(Agent.GetModelID(agent_id) or 0)
    position = Agent.GetXY(agent_id)
    encoded_name = bytes(Agent.GetEncNameByID(agent_id))
    primary_name, secondary_name = Agent.GetProfessionNames(agent_id)
    primary = _resolve_profession_name(primary_name)
    secondary = _resolve_profession_name(secondary_name)
    existing = _find_foe_match(name, model_id, encoded_name, primary, secondary)

    if existing is None:
        FOES.append(
            Foe(
                name=name,
                model_id=model_id,
                encoded_name=encoded_name,
                primary_profession=primary,
                secondary_profession=secondary,
                spawns=[FoeSpawn(map_id=map_id, position=position)] if position != (0.0, 0.0) else [],
            )
        )
        return True

    if _update_npc_metadata(existing, position, model_id, encoded_name):
        updated = True

    if position != (0.0, 0.0) and all(
        Map.GetBaseMapID(spawn.map_id) != Map.GetBaseMapID(map_id)
        or Utils.Distance(position, spawn.position) >= 2500.0
        for spawn in existing.spawns
    ):
        existing.spawns.append(FoeSpawn(map_id=map_id, position=position))
        updated = True

    return updated


def _scan_current_map_npcs():
    global _last_passive_scan_at
    global _last_scan_instance_key
    global _scanned_agent_ids_current_map
    global _pending_agent_scan_attempts_current_map
    global _current_map_stationary_npcs
    global _current_map_missing_stationary_npcs

    if not Routines.Checks.Map.IsMapReady():
        return

    now = datetime.utcnow()
    current_map_id = Map.GetBaseMapID()
    current_instance_key = _get_current_map_instance_key()
    if _last_scan_instance_key != current_instance_key:
        _last_scan_instance_key = current_instance_key
        _last_passive_scan_at = None
        _scanned_agent_ids_current_map.clear()
        _pending_agent_scan_attempts_current_map.clear()
        _rebuild_current_map_stationary_indexes(current_map_id)

    if _last_passive_scan_at is not None and now - _last_passive_scan_at < timedelta(seconds=1):
        return
    _last_passive_scan_at = now

    agent_ids = [
        agent_id
        for agent_id in AgentArray.GetAgentArray()
        if agent_id and agent_id not in _scanned_agent_ids_current_map
    ]
    if not agent_ids:
        return

    updated = False
    dirty_categories: set[str] = set()
    for agent_id in agent_ids:
        if not Agent.IsValid(agent_id) or not Agent.IsNPC(agent_id):
            _scanned_agent_ids_current_map.add(agent_id)
            _pending_agent_scan_attempts_current_map.pop(agent_id, None)
            continue

        name = Agent.GetNameByID(agent_id)
        if not name:
            attempts = _pending_agent_scan_attempts_current_map.get(agent_id, 0) + 1
            if attempts >= 3:
                _scanned_agent_ids_current_map.add(agent_id)
                _pending_agent_scan_attempts_current_map.pop(agent_id, None)
            else:
                _pending_agent_scan_attempts_current_map[agent_id] = attempts
            continue
        _scanned_agent_ids_current_map.add(agent_id)
        _pending_agent_scan_attempts_current_map.pop(agent_id, None)

        position = Agent.GetXY(agent_id)
        model_id = int(Agent.GetModelID(agent_id) or 0)
        encoded_name = bytes(Agent.GetEncNameByID(agent_id))
        allegiance_value, _ = Agent.GetAllegiance(agent_id)
        try:
            allegiance = Allegiance(allegiance_value)
        except Exception:
            allegiance = Allegiance.Neutral

        known_npc = _find_npc_match(_current_map_missing_stationary_npcs, name, current_map_id, model_id)
        if known_npc is None:
            known_npc = _find_npc_match(_current_map_stationary_npcs, name, current_map_id, model_id)
        if known_npc is not None:
            if _update_stationary_npc_metadata(known_npc, position, model_id, encoded_name):
                updated = True
                dirty_categories.add(_get_category_key_for_npc(known_npc))
                if not _is_stationary_npc_missing_metadata(known_npc):
                    _current_map_missing_stationary_npcs = [
                        npc for npc in _current_map_missing_stationary_npcs if npc is not known_npc
                    ]
            if isinstance(known_npc, Trader) and known_npc.trader_type == TraderType.Unknown:
                known_npc.trader_type = TraderType.get_type_from_name(known_npc.name)
                updated = True
                dirty_categories.add('traders')
            continue

        if allegiance == Allegiance.Enemy:
            if Agent.IsSpawned(agent_id):
                continue
            
            previous_updated = updated
            updated = _upsert_foe_spawn(agent_id, current_map_id, updated)
            if updated != previous_updated:
                dirty_categories.add('foes')
            continue

        target_cls = _classify_service_npc(name)
        if target_cls is Trader:
            existing_trader = _find_npc_match(TRADERS, name, current_map_id, model_id)
            if existing_trader is None:
                trader = Trader(
                    name=name,
                    map_id=current_map_id,
                    position=position,
                    model_id=model_id,
                    encoded_name=encoded_name,
                    _trader_type=TraderType.get_type_from_name(name),
                )
                TRADERS.append(trader)
                _current_map_stationary_npcs.append(trader)
                updated = True
                dirty_categories.add('traders')
            elif _update_stationary_npc_metadata(existing_trader, position, model_id, encoded_name):
                updated = True
                dirty_categories.add('traders')
            continue

        if target_cls is Merchant:
            existing_merchant = _find_npc_match(MERCHANTS, name, current_map_id, model_id)
            if existing_merchant is None:
                merchant = Merchant(
                    name=name,
                    map_id=current_map_id,
                    position=position,
                    model_id=model_id,
                    encoded_name=encoded_name,
                )
                MERCHANTS.append(merchant)
                _current_map_stationary_npcs.append(merchant)
                updated = True
                dirty_categories.add('merchants')
            elif _update_stationary_npc_metadata(existing_merchant, position, model_id, encoded_name):
                updated = True
                dirty_categories.add('merchants')
            continue

        existing_ally = _find_npc_match(ALLIES, name, current_map_id, model_id)
        if existing_ally is None:
            ally = Ally(
                name=name,
                map_id=current_map_id,
                position=position,
                model_id=model_id,
                encoded_name=encoded_name,
                allegiance=allegiance,
            )
            ALLIES.append(ally)
            _current_map_stationary_npcs.append(ally)
            updated = True
            dirty_categories.add('allies')
        elif _update_stationary_npc_metadata(existing_ally, position, model_id, encoded_name):
            updated = True
            dirty_categories.add('allies')

    if updated:
        _mark_data_dirty(dirty_categories, queue_save=True)

def draw_window():
    _ensure_initialized()

    global search_query
    global show_unlocked_only
    global show_armorers
    global show_artisans
    global show_consumable_crafters
    global show_weaponsmiths
    global show_collectors
    global show_merchants
    global show_traders
    global show_allies
    global show_foes
    global sweep_is_running

    current_map_id = Map.GetBaseMapID()
    current_map_name = Map.GetMapName(current_map_id)
    current_profession = _get_current_profession()
    if current_profession == Profession._None:
        current_profession = Profession.Warrior
    visible_crafters = _get_visible_crafters()
    sorted_by_map = sorted(visible_crafters, key=lambda c: (c.GetDisplayMapID(), c.name))
    stats = _get_dashboard_stats()
    all_crafters = stats['all_npcs']

    PyImGui.text(f'Current map: {current_map_name} ({current_map_id})')
    PyImGui.text(
        f"NPCs: {len(visible_crafters)} shown / {len(all_crafters)} total / {stats['unlocked_count']} unlocked"
        f" | A:{stats['armorer_count']} Ar:{stats['artisan_count']} C:{stats['consumable_crafter_count']} W:{stats['weaponsmith_count']}"
        f" Co:{stats['collector_count']} M:{stats['merchant_count']} T:{stats['trader_count']} Al:{stats['ally_count']} F:{stats['foe_count']}"
    )
    PyImGui.text(f"Auto-reachable sweep targets: {stats['auto_reachable_count']}")
    PyImGui.text(f"Collected entries across all services: {stats['total_collected_entries']}")
    PyImGui.text(f'JSON dir: {DATA_DIRECTORY_PATH}')
    PyImGui.text('Collection note: map scans now passively record visible NPCs every map. Service item data still depends on the currently open window.')
    PyImGui.text(f'Sweep status: {sweep_status}')
    if sweep_current_name:
        PyImGui.text(f'Current sweep target: {sweep_current_name} ({sweep_current_index}/{sweep_total})')
    if ImGui.button('Collect open NPC##crafter_collect_open', width=150):
        _collect_current_open_crafter()
    PyImGui.same_line(0, 10)
    if ImGui.button('Save JSON##crafter_save_json', width=100):
        save_crafters_to_json()
    PyImGui.same_line(0, 10)
    if ImGui.button('Load JSON##crafter_load_json', width=100):
        load_crafters_from_json()
    if ImGui.button('Sweep + collect reachable##crafter_sweep_start', width=180, disabled=sweep_is_running):
        _start_crafter_sweep()
    PyImGui.same_line(0, 10)
    if ImGui.button('Stop sweep##crafter_sweep_stop', width=100, disabled=not sweep_is_running):
        sweep_is_running = False
        _request_stop_crafter_sweep()
    PyImGui.separator()

    PyImGui.set_next_item_width(260)
    search_query = PyImGui.input_text('Search##crafter_search', search_query, 128)
    PyImGui.same_line(0, 10)
    show_unlocked_only = PyImGui.checkbox('Unlocked only', show_unlocked_only)
    show_armorers = PyImGui.checkbox('Armorers', show_armorers)
    PyImGui.same_line(0, 10)
    show_artisans = PyImGui.checkbox('Artisans', show_artisans)
    PyImGui.same_line(0, 10)
    show_consumable_crafters = PyImGui.checkbox('Consumables', show_consumable_crafters)
    show_weaponsmiths = PyImGui.checkbox('Weaponsmiths', show_weaponsmiths)
    PyImGui.same_line(0, 10)
    show_collectors = PyImGui.checkbox('Collectors', show_collectors)
    PyImGui.same_line(0, 10)
    show_merchants = PyImGui.checkbox('Merchants', show_merchants)
    show_traders = PyImGui.checkbox('Traders', show_traders)
    PyImGui.same_line(0, 10)
    show_allies = PyImGui.checkbox('Allies', show_allies)
    show_foes = PyImGui.checkbox('Foes', show_foes)
    PyImGui.separator()

    style = ImGui.get_style()
    
    table_flags = (
        PyImGui.TableFlags.Borders
        | PyImGui.TableFlags.RowBg
        | PyImGui.TableFlags.ScrollY
        | PyImGui.TableFlags.Resizable
        | PyImGui.TableFlags.SizingStretchProp
    )
    if PyImGui.begin_table('##armor_crafters_table', 8, table_flags):
        PyImGui.table_setup_column('Type', PyImGui.TableColumnFlags.WidthFixed, 95)
        PyImGui.table_setup_column('Name', PyImGui.TableColumnFlags.WidthStretch, 140)
        PyImGui.table_setup_column('Map', PyImGui.TableColumnFlags.WidthStretch, 170)
        PyImGui.table_setup_column('Unlocked', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_setup_column('Access', PyImGui.TableColumnFlags.WidthStretch, 110)
        PyImGui.table_setup_column('Summary', PyImGui.TableColumnFlags.WidthStretch, 180)
        PyImGui.table_setup_column('Action', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_setup_column('Collected', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_headers_row()

        row_height = 0
        fallback_row_height = 25
        for index, crafter in enumerate(sorted_by_map):
            if PyImGui.is_rect_visible(10, row_height or fallback_row_height):
                    
                pos_collected = _is_position_collected(crafter)
                if not pos_collected:
                    style.Text.push_color_direct((255, 100, 100, 255))
                
                display_map_id = crafter.GetDisplayMapID()
                display_position = crafter.GetDisplayPosition()
                map_name = Map.GetMapName(display_map_id) if display_map_id != 0 else 'Unknown Map'
                is_unlocked = crafter.HasMapUnlocked()
                is_outpost = display_map_id in out_posts
                is_here = display_map_id != 0 and current_map_id == Map.GetBaseMapID(display_map_id)

                PyImGui.table_next_row()
                row_height = int(max(row_height, PyImGui.get_content_region_avail()[1]))

                PyImGui.table_set_column_index(0)
                PyImGui.text(crafter.service_label())

                PyImGui.table_set_column_index(1)
                PyImGui.text(crafter.name)

                PyImGui.table_set_column_index(2)
                PyImGui.text(f'{map_name} ({display_map_id})' if display_map_id != 0 else map_name)

                PyImGui.table_set_column_index(3)
                PyImGui.text('Yes' if is_unlocked else 'No')

                PyImGui.table_set_column_index(4)
                PyImGui.text(crafter.interaction_label())

                PyImGui.table_set_column_index(5)
                PyImGui.text(crafter.GetCollectionSummary())

                PyImGui.table_set_column_index(6)
                can_move = isinstance(crafter, StationaryNpc)
                button_label = 'N/A'
                button_disabled = True
                if can_move:
                    button_label = 'Move' if (display_position != (0.0, 0.0) and is_here) else 'Here' if is_here else 'Travel' if is_outpost else 'Manual'
                    button_disabled = (display_position == (0.0, 0.0) and is_here) or not is_unlocked or (not is_outpost and not is_here)
                if ImGui.button(f'{button_label}##crafter_move_{crafter.name}_{index}', width=-1, disabled=button_disabled):
                    crafter.MoveTo()
                                    

                PyImGui.table_set_column_index(7)
                PyImGui.text(str(crafter.GetCollectedCount()))
                
                if not pos_collected:
                    style.Text.pop_color()
            else:
                # Skip rendering this row but still advance the table row index
                PyImGui.dummy(0, row_height or fallback_row_height)
                
        PyImGui.end_table()

def scan_for_crafters_with_missing_data():
    _scan_current_map_npcs()
    
    
def main():
    _ensure_initialized()

    if not Routines.Checks.Map.IsMapReady():
        return
    
    PyImGui.set_next_window_size((800, 400), PyImGui.ImGuiCond.FirstUseEver)
    if PyImGui.begin(MODULE_NAME, PyImGui.WindowFlags.NoFlag):
        draw_window()
    PyImGui.end()
    
    scan_for_crafters_with_missing_data()
    _flush_pending_auto_save()

    

if __name__ == "__main__":
    main()
