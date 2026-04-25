from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, NamedTuple, Optional, TypeAlias

from Py4GWCoreLib.Item import Bag, Item
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, DyeColor
from Py4GWCoreLib.enums_src.Item_enums import INVENTORY_BAGS, STORAGE_BAGS, Bags, ItemAction, ItemType, Rarity
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.item_mods_src.item_mod import ItemMod
from Py4GWCoreLib.item_mods_src.properties import ItemProperty
from Py4GWCoreLib.item_mods_src.upgrades import _UPGRADES, ArmorUpgrade, RangeInstruction, Upgrade, WeaponUpgrade, Inscription, OfTheProfession, OfAttributeUpgrade
from Sources.frenkeyLib.ItemHandling.Items.ItemData import DAMAGE_RANGES
from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot

SerializedPropertyFilter: TypeAlias = dict[str, int | str]
PropertyFilter: TypeAlias = ItemProperty | SerializedPropertyFilter


def _property_filters_match(item_snapshot: ItemSnapshot, property_filters: list[PropertyFilter]) -> bool:
    if len(property_filters) == 0:
        return True

    item_properties = {type(prop): prop for prop in item_snapshot.properties}
    item_properties_by_name = {type(prop).__name__: prop for prop in item_snapshot.properties}

    for prop in property_filters:
        if isinstance(prop, dict):
            property_type_name = str(prop.get("property_type", ""))
            if property_type_name not in item_properties_by_name:
                return False
        elif type(prop) not in item_properties:
            return False

    return True


def _serialize_property_filters(property_filters: list[PropertyFilter]) -> list[SerializedPropertyFilter]:
    serialized_filters: list[SerializedPropertyFilter] = []
    for prop in property_filters:
        if isinstance(prop, dict):
            serialized_filters.append(
                {
                    "property_type": str(prop.get("property_type", "")),
                    "modifier_arg": int(prop.get("modifier_arg", -1)),
                }
            )
        else:
            serialized_filters.append(
                {
                    "property_type": type(prop).__name__,
                    "modifier_arg": int(getattr(prop.modifier, "arg", -1)),
                }
            )

    return serialized_filters


def _deserialize_property_filters(data: dict[str, Any]) -> list[PropertyFilter]:
    return [
        {
            "property_type": str(prop.get("property_type", "")),
            "modifier_arg": int(prop.get("modifier_arg", -1)),
        }
        for prop in data.get("properties", [])
        if isinstance(prop, dict)
    ]

class Rule:
    _registry: ClassVar[dict[str, type["Rule"]]] = {}
    ui_selectable: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Rule._registry[cls.__name__] = cls

    def __init__(self):
        self.name = ""
        self.action : ItemAction = ItemAction.NONE
        pass

    def get_item(self, item_id: int) -> Optional[ItemSnapshot]:
        try:
            return ItemSnapshot.from_item_id(item_id)
        
        except Exception:
            return None

    def is_valid(self) -> bool:
        return True

    def applies(self, item_id: int) -> bool:
        raise NotImplementedError("Subclasses must implement the applies method.")

    def _comparison_data(self) -> Any:
        return ()

    def equals(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return False
        
        if type(self) is not type(other):
            return False
        
        return self._comparison_data() == other._comparison_data()

    def __eq__(self, other: object) -> bool:
        return self.equals(other)

    def _serialize_data(self) -> dict[str, Any]:
        return {}

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        return

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "rule_type": type(self).__name__,
            "name": self.name,
            "action": self.action.name,
        }
        payload.update(self._serialize_data())
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Rule | None:
        rule_type_name = str(payload.get("rule_type", ""))
        rule_cls = cls._registry.get(rule_type_name, None)
        if rule_cls is None:
            return None

        rule = rule_cls()
        rule.name = payload.get("name", "")
        rule.action = ItemAction[payload.get("action", "NONE")] if "action" in payload and payload["action"] in ItemAction.__members__ else ItemAction.NONE

        rule._deserialize_data(payload)
        return rule

class ModelIdsRule(Rule):
    """
    A rule that checks if an item has a ModelID contained in a specified list of model IDs.
    **CAUTION**: This rule is very basic and can result in unwanted matches as model IDs can be shared between different items and item types!
    """

    def __init__(self, model_ids: Optional[list[ModelID|int]] = None):
        super().__init__()
        self.model_ids: list[ModelID|int] = model_ids if model_ids is not None else []

    def is_valid(self) -> bool:
        return len(self.model_ids) > 0

    def applies(self, item_id):
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        model_id = item_snapshot.model_id
        if model_id is None:
            return False
        
        for mid in self.model_ids:
            if isinstance(mid, ModelID):
                if model_id == mid.value:
                    return True
            elif model_id == mid:
                return True
        
        return False

    def _serialize_data(self) -> dict[str, Any]:
        return {"model_ids": [int(mid.value) if isinstance(mid, ModelID) else mid for mid in self.model_ids]}

    def _comparison_data(self) -> Any:
        normalized_model_ids = {
            int(mid.value) if isinstance(mid, ModelID) else mid
            for mid in self.model_ids
        }
        return tuple(sorted(normalized_model_ids))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_ids = []
        for mid in data.get("model_ids", []):
            if isinstance(mid, int):
                try:
                    self.model_ids.append(ModelID(mid))
                except ValueError:
                    self.model_ids.append(mid)
                    
class ItemTypesRule(Rule):
    """
    A rule that checks if an item :class:`ItemType` is a specified item type.
    """

    def __init__(self, item_types: Optional[list[ItemType]] = None):
        super().__init__()
        self.item_types: list[ItemType] = item_types if item_types is not None else []

    def is_valid(self) -> bool:
        return len(self.item_types) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        item_type = item_snapshot.item_type
        return item_type in self.item_types if item_type else False

    def _serialize_data(self) -> dict[str, Any]:
        return {"item_types": [item_type.name for item_type in self.item_types]}

    def _comparison_data(self) -> Any:
        return tuple(sorted(item_type.name for item_type in self.item_types))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.item_types = [
            ItemType[name]
            for name in data.get("item_types", [])
            if isinstance(name, str) and name in ItemType.__members__
        ]

ModelIdAndItemType = NamedTuple("ModelIdAndItemType", [("model_id", ModelID|int), ("item_type", ItemType)])
class ModelIdsAndItemTypesRule(Rule):
    """
    A rule that checks if an item has a ModelID contained in a specified list of model IDs and an ItemType contained in a specified list of item types. Both conditions must be met for the rule to apply.
    **CAUTION**: This rule is very basic and can result in unwanted matches as model IDs can be shared between different items and item types!
    """

    def __init__(self, model_ids: Optional[list[ModelIdAndItemType]] = None):
        super().__init__()
        self.items: list[ModelIdAndItemType] = model_ids if model_ids is not None else []

    def is_valid(self) -> bool:
        return len(self.items) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False
        
        model_id = item_snapshot.model_id
        item_type = item_snapshot.item_type
        for mid, it in self.items:
            if ((model_id == mid.value if isinstance(mid, ModelID) else model_id == mid) and item_type == it):
                return True

        return False
    
    def _serialize_data(self) -> dict[str, Any]:
        return {
            "model_ids": [
                {
                    "model_id": int(mid.value) if isinstance(mid, ModelID) else mid,
                    "item_type": item_type.name,
                }
                for mid, item_type in self.items
            ]
        }
        
    def _comparison_data(self) -> Any:
        normalized_model_ids = [
            (
                int(mid.value) if isinstance(mid, ModelID) else mid,
                item_type.name
            )
            for mid, item_type in self.items
        ]
        return tuple(sorted(normalized_model_ids))
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.items = []
        for entry in data.get("model_ids", []):
            if not isinstance(entry, dict):
                continue
            
            mid = entry.get("model_id", None)
            item_type_name = entry.get("item_type", None)
            if mid is None or item_type_name is None or not isinstance(item_type_name, str) or item_type_name not in ItemType.__members__:
                continue
            
            item_type = ItemType[item_type_name]
            if isinstance(mid, int):
                try:
                    model_id = ModelID(mid)
                    self.items.append(ModelIdAndItemType(model_id, item_type))
                except ValueError:
                    self.items.append(ModelIdAndItemType(mid, item_type))

class EncodedNameRule(Rule):
    """
    A rule that checks if an item's encoded name matches a specified encoded name. The encoded name is the combination of the item's name and its upgrades, as returned by the API's encoded_name field.
    """

    def __init__(self, encoded_names: Optional[list[str]] = None):
        super().__init__()
        self.encoded_names: list[str] = encoded_names if encoded_names is not None else []

    def is_valid(self) -> bool:
        return len(self.encoded_names) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        encoded_name = item_snapshot.name_enc
        return encoded_name in self.encoded_names if encoded_name else False

    def _serialize_data(self) -> dict[str, Any]:
        return {"encoded_names": self.encoded_names}

    def _comparison_data(self) -> Any:
        return tuple(sorted(self.encoded_names))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.encoded_names = [
            name for name in data.get("encoded_names", [])
            if isinstance(name, str)
        ]

class ModelFileIdRule(Rule):
    """
    A rule that checks if an item has a ModelFileID contained in a specified list of model file IDs.
    **CAUTION**: This rule is very basic and can result in unwanted matches as multiple items can share the same model file ID!
    """

    def __init__(self, model_file_ids: Optional[list[int]] = None):
        super().__init__()
        self.model_file_ids: list[int] = model_file_ids if model_file_ids is not None else []

    def is_valid(self) -> bool:
        return len(self.model_file_ids) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        model_file_id = item_snapshot.model_file_id
        return model_file_id in self.model_file_ids if model_file_id else False

    def _serialize_data(self) -> dict[str, Any]:
        return {"model_file_ids": self.model_file_ids}

    def _comparison_data(self) -> Any:
        return tuple(sorted(self.model_file_ids))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_file_ids = [
            mid for mid in data.get("model_file_ids", [])
            if isinstance(mid, int)
        ]

ModelFileIdAndItemType = NamedTuple("ModelFileIdAndItemType", [("model_file_id", int), ("item_type", ItemType)])
class ModelFileIdAndItemTypeRule(Rule):
    """
    A rule that checks if an item has a ModelFileID contained in a specified list of model file IDs and an ItemType contained in a specified list of item types. Both conditions must be met for the rule to apply.
    **CAUTION**: This rule is very basic and can result in unwanted matches as multiple items can share the same model file ID!
    """

    def __init__(self, model_file_ids_and_item_types: Optional[list[ModelFileIdAndItemType]] = None):
        super().__init__()
        self.model_file_ids_and_item_types: list[ModelFileIdAndItemType] = model_file_ids_and_item_types if model_file_ids_and_item_types is not None else []

    def is_valid(self) -> bool:
        return len(self.model_file_ids_and_item_types) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        model_file_id = item_snapshot.model_file_id
        item_type = item_snapshot.item_type
        for entry in self.model_file_ids_and_item_types:
            if ((model_file_id == entry.model_file_id if model_file_id else False) and item_type == entry.item_type):
                return True

        return False
    
    def _serialize_data(self) -> dict[str, Any]:
        return {
            "model_file_ids_and_item_types": [
                {
                    "model_file_id": entry.model_file_id,
                    "item_type": entry.item_type.name,
                }
                for entry in self.model_file_ids_and_item_types
            ]
        }
        
    def _comparison_data(self) -> Any:
        normalized_data = [
            (entry.model_file_id, entry.item_type.name)
            for entry in self.model_file_ids_and_item_types
        ]
        return tuple(sorted(normalized_data))
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_file_ids_and_item_types = []
        for entry in data.get("model_file_ids_and_item_types", []):
            if not isinstance(entry, dict):
                continue
            
            mid = entry.get("model_file_id", None)
            item_type_name = entry.get("item_type", None)
            if mid is None or item_type_name is None or not isinstance(item_type_name, str) or item_type_name not in ItemType.__members__:
                continue

            self.model_file_ids_and_item_types.append(
                ModelFileIdAndItemType(
                    model_file_id=mid,
                    item_type=ItemType[item_type_name]
                )
            )


class WeaponSkinRule(Rule):
    """
    A rule that checks if a weapon matches one of the specified model file ids.
    In addition, the rule can restrict requirement, max damage, and required item properties.
    """

    def __init__(
        self,
        model_file_ids: Optional[list[int]] = None,
        requirement_min: int = 0,
        requirement_max: int = 13,
        only_max_damage: bool = True,
        properties: Optional[list[PropertyFilter]] = None,
    ):
        super().__init__()
        self.model_file_ids: list[int] = model_file_ids if model_file_ids is not None else []
        self.requirement_min: int = requirement_min
        self.requirement_max: int = requirement_max
        self.only_max_damage: bool = only_max_damage
        self.properties: list[PropertyFilter] = properties if properties is not None else []

    def is_valid(self) -> bool:
        return len(self.model_file_ids) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None or item_snapshot.model_file_id not in self.model_file_ids:
            return False

        if self.requirement_min > item_snapshot.requirement or self.requirement_max < item_snapshot.requirement:
            return False

        if self.only_max_damage:
            damage_for_requirement = DAMAGE_RANGES.get(item_snapshot.item_type, {}).get(item_snapshot.requirement, (0, 0))
            if item_snapshot.max_damage < damage_for_requirement[1] or item_snapshot.min_damage < damage_for_requirement[0]:
                return False

        return _property_filters_match(item_snapshot, self.properties)

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "model_file_ids": list(self.model_file_ids),
            "requirement_min": self.requirement_min,
            "requirement_max": self.requirement_max,
            "only_max_damage": self.only_max_damage,
            "properties": _serialize_property_filters(self.properties),
        }

    def _comparison_data(self) -> Any:
        return (
            tuple(sorted(self.model_file_ids)),
            self.requirement_min,
            self.requirement_max,
            self.only_max_damage,
            tuple(
                sorted(
                    (str(prop.get("property_type", "")), int(prop.get("modifier_arg", -1)))
                    for prop in _serialize_property_filters(self.properties)
                )
            ),
        )

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.model_file_ids = [mid for mid in data.get("model_file_ids", []) if isinstance(mid, int)]
        self.requirement_min = int(data.get("requirement_min", 0))
        self.requirement_max = int(data.get("requirement_max", 13))
        self.only_max_damage = bool(data.get("only_max_damage", True))
        self.properties = _deserialize_property_filters(data)


class WeaponTypeRule(Rule):
    """
    A rule that checks if an item is a specific weapon type with requirement, max damage, and optional property filters.
    """

    def __init__(
        self,
        item_type: Optional[ItemType] = None,
        requirement_min: int = 0,
        requirement_max: int = 13,
        only_max_damage: bool = True,
        properties: Optional[list[PropertyFilter]] = None,
    ):
        super().__init__()
        self.item_type: ItemType | None = item_type
        self.requirement_min: int = requirement_min
        self.requirement_max: int = requirement_max
        self.only_max_damage: bool = only_max_damage
        self.properties: list[PropertyFilter] = properties if properties is not None else []

    def is_valid(self) -> bool:
        return self.item_type is not None

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None or item_snapshot.item_type != self.item_type:
            return False

        if self.requirement_min > item_snapshot.requirement or self.requirement_max < item_snapshot.requirement:
            return False

        if self.only_max_damage:
            damage_for_requirement = DAMAGE_RANGES.get(item_snapshot.item_type, {}).get(item_snapshot.requirement, (0, 0))
            if item_snapshot.max_damage < damage_for_requirement[1] or item_snapshot.min_damage < damage_for_requirement[0]:
                return False

        return _property_filters_match(item_snapshot, self.properties)

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "item_type": self.item_type.name if self.item_type is not None else None,
            "requirement_min": self.requirement_min,
            "requirement_max": self.requirement_max,
            "only_max_damage": self.only_max_damage,
            "properties": _serialize_property_filters(self.properties),
        }

    def _comparison_data(self) -> Any:
        return (
            self.item_type.name if self.item_type is not None else None,
            self.requirement_min,
            self.requirement_max,
            self.only_max_damage,
            tuple(
                sorted(
                    (str(prop.get("property_type", "")), int(prop.get("modifier_arg", -1)))
                    for prop in _serialize_property_filters(self.properties)
                )
            ),
        )

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        item_type_name = data.get("item_type", None)
        self.item_type = ItemType[item_type_name] if isinstance(item_type_name, str) and item_type_name in ItemType.__members__ else None
        self.requirement_min = int(data.get("requirement_min", 0))
        self.requirement_max = int(data.get("requirement_max", 13))
        self.only_max_damage = bool(data.get("only_max_damage", True))
        self.properties = _deserialize_property_filters(data)


class SalvagesToMaterialRule(Rule):
    """
    A rule that checks if an item can salvage into any of the specified materials.
    """

    def __init__(self, materials: Optional[list[ModelID|int]] = None):
        super().__init__()
        self.materials: list[ModelID|int] = materials if materials is not None else []

    def is_valid(self) -> bool:
        return len(self.materials) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None or not item_snapshot.is_salvageable or item_snapshot.data is None:
            return False

        common = [entry.model_id for entry in (item_snapshot.data.common_salvage.values() if item_snapshot.data.common_salvage else {})]
        rare = [entry.model_id for entry in (item_snapshot.data.rare_salvage.values() if item_snapshot.data.rare_salvage else {})]
        return any(material in common + rare for material in self.materials)

    def _serialize_data(self) -> dict[str, Any]:
        return {"materials": [material.name if isinstance(material, ModelID) else str(material) for material in self.materials]}

    def _comparison_data(self) -> Any:
        return tuple(sorted(material.name if isinstance(material, ModelID) else str(material) for material in self.materials))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        materials = [
            ModelID[name] if isinstance(name, str) and name in ModelID.__members__ else int(name) if isinstance(name, (str, int)) and str(name).isdigit() else None
            for name in data.get("materials", [])
            if (isinstance(name, str) and name in ModelID.__members__) or (isinstance(name, (str, int)) and str(name).isdigit())
        ]
        
        self.materials = [material for material in materials if material is not None]

class RaritiesRule(Rule):
    """
    A rule that checks if an item :class:`Rarity` is a specified rarity.
    """

    def __init__(self, rarities: Optional[list[Rarity]] = None):
        super().__init__()
        self.rarities: list[Rarity] = rarities if rarities is not None else []

    def is_valid(self) -> bool:
        return len(self.rarities) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        rarity = item_snapshot.rarity
        return rarity in self.rarities if rarity else False

    def _serialize_data(self) -> dict[str, Any]:
        return {"rarities": [rarity.name for rarity in self.rarities]}

    def _comparison_data(self) -> Any:
        return tuple(sorted(rarity.name for rarity in self.rarities))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.rarities = [
            Rarity[name]
            for name in data.get("rarities", [])
            if isinstance(name, str) and name in Rarity.__members__
        ]

class RaritiesAndItemTypesRule(Rule):
    """
    A rule that checks if an item matches any of the specified rarities and any of the specified item types. Both conditions must be met for the rule to apply.
    """

    def __init__(self, rarities: Optional[list[Rarity]] = None, item_types: Optional[list[ItemType]] = None):
        super().__init__()
        self.rarities: list[Rarity] = rarities if rarities is not None else []
        self.item_types: list[ItemType] = item_types if item_types is not None else []

    def is_valid(self) -> bool:
        return len(self.rarities) > 0 and len(self.item_types) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        rarity = item_snapshot.rarity
        item_type = item_snapshot.item_type
        return (rarity in self.rarities if rarity else False) and (item_type in self.item_types if item_type else False)

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "rarities": [rarity.name for rarity in self.rarities],
            "item_types": [item_type.name for item_type in self.item_types],
        }

    def _comparison_data(self) -> Any:
        rarities_data = tuple(sorted(rarity.name for rarity in self.rarities))
        item_types_data = tuple(sorted(item_type.name for item_type in self.item_types))
        return (rarities_data, item_types_data)

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.rarities = [
            Rarity[name]
            for name in data.get("rarities", [])
            if isinstance(name, str) and name in Rarity.__members__
        ]
        self.item_types = [
            ItemType[name]
            for name in data.get("item_types", [])
            if isinstance(name, str) and name in ItemType.__members__
        ]

class DyesRule(Rule):
    """
    A rule if an item is a **Vial of Dye** of a specific :class:`DyeColor`. This is determined by the item's dye color.
    """

    def __init__(self, dye_colors: Optional[list[DyeColor]] = None):
        super().__init__()
        self.dye_colors: list[DyeColor] = dye_colors if dye_colors is not None else []

    def is_valid(self) -> bool:
        return self.dye_colors is not None and len(self.dye_colors) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False

        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False

        item_type = item_snapshot.item_type
        if not item_type or item_type != ItemType.Dye:
            return False
        
        item_color = item_snapshot.color
        return item_color in self.dye_colors if item_color else False

    def _serialize_data(self) -> dict[str, Any]:
        return {"dye_colors": [color.name for color in self.dye_colors]}

    def _comparison_data(self) -> Any:
        return tuple(sorted(color.name for color in self.dye_colors))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.dye_colors = [
            DyeColor[name]
            for name in data.get("dye_colors", [])
            if isinstance(name, str) and name in DyeColor.__members__
        ]

@dataclass
class StockInstruction:
    model_id: ModelID
    item_type: ItemType
    quantity: int
    include_storage: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": int(self.model_id.value),
            "item_type": self.item_type.name,
            "quantity": self.quantity,
            "include_storage": self.include_storage,
        }

    def comparison_data(self) -> tuple[int, str, int, bool]:
        return (
            int(self.model_id.value),
            self.item_type.name,
            self.quantity,
            self.include_storage,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StockInstruction | None:
        try:
            model_id = ModelID(int(data["model_id"]))
            item_type = ItemType[str(data["item_type"])]
            quantity = int(data["quantity"])
            include_storage = bool(data.get("include_storage", True))
        except (KeyError, ValueError, TypeError):
            return None

        return cls(
            model_id=model_id,
            item_type=item_type,
            quantity=quantity,
            include_storage=include_storage,
        )

class ExtractUpgradeRule(Rule):
    ui_selectable: ClassVar[bool] = False
    
    def __init__(self):
        super().__init__()
        self.action : ItemAction = ItemAction.ExtractUpgrade

UpgradeAndItemType = NamedTuple("UpgradeAndItemType", [("upgrade", WeaponUpgrade | Inscription), ("item_types", list[ItemType])])

class MaxWeaponUpgradeRule(ExtractUpgradeRule):
    ui_selectable: ClassVar[bool] = True
    
    def __init__(self, upgrades: Optional[list[UpgradeAndItemType]] = None):
        super().__init__()
        self.weapon_upgrades: list[UpgradeAndItemType] = upgrades if upgrades is not None else []
        
    def is_valid(self) -> bool:
        return len(self.weapon_upgrades) > 0
    
    def applies(self, item_id) -> bool:
        if not self.is_valid():
            return False
        
        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False
        
        prefix, suffix, inscription, inherent = ItemMod.get_item_upgrades(item_id)
        weapon_upgrades = [upgrade for upgrade in [prefix, suffix, inscription, *(inherent or [])] if (isinstance(upgrade, (WeaponUpgrade, Inscription)))]
        
        for u in self.weapon_upgrades:
            for item_upgrade in weapon_upgrades:
                if u.upgrade.matches(item_upgrade):
                    return True
        
        return False
    
    def _serialize_data(self) -> dict[str, Any]:
        # if upgrade is OfTheProfession or OfAttribute --> save attribute, else only save upgrade type name
        return {
            "weapon_upgrades": [
                {
                    "upgrade": u.upgrade.__class__.__name__,
                } if isinstance(u.upgrade, (Inscription)) else
                {
                    "upgrade": u.upgrade.__class__.__name__,
                    "item_types": [item_type.name for item_type in u.item_types],
                } if not isinstance(u.upgrade, (OfTheProfession, OfAttributeUpgrade)) else {
                    "upgrade": u.upgrade.__class__.__name__,
                    "attribute": u.upgrade.attribute.name,
                    "item_types": [item_type.name for item_type in u.item_types],
                }
                for u in self.weapon_upgrades
            ]
        }
        
    def _comparison_data(self) -> Any:
        normalized_upgrades = [u.upgrade._comparison_data() for u in self.weapon_upgrades]
        return tuple(sorted(normalized_upgrades))
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.weapon_upgrades = []
        for d in data.get("weapon_upgrades", []):
            if not isinstance(d, dict):
                continue
            
            name = d.get("upgrade", None)
            if not isinstance(name, str):
                continue
            
            upgrade_cls = next(
                (
                    upgrade_type
                    for upgrade_type in _UPGRADES
                    if upgrade_type.__name__ == name and issubclass(upgrade_type, (WeaponUpgrade, Inscription))
                ),
                None,
            )
            if upgrade_cls is not None:
                if issubclass(upgrade_cls, (OfTheProfession, OfAttributeUpgrade)):
                    attribute_name = d.get("attribute", None)
                    attribute = Attribute[attribute_name] if isinstance(attribute_name, str) and attribute_name in Attribute.__members__ else None
                    if attribute is not None:
                        upgrade = upgrade_cls()
                        upgrade.attribute = attribute
                        
                        self.weapon_upgrades.append(
                            UpgradeAndItemType(
                                upgrade=upgrade,
                                item_types=[ItemType[item_type] for item_type in d.get("item_types", []) if isinstance(item_type, str) and item_type in ItemType.__members__]
                            )
                        )
                        
                elif issubclass(upgrade_cls, Inscription):
                    self.weapon_upgrades.append(
                        UpgradeAndItemType(
                            upgrade=upgrade_cls(),
                            item_types=[]
                        )
                    )
                    
                else:
                    self.weapon_upgrades.append(
                        UpgradeAndItemType(
                            upgrade=upgrade_cls(),
                            item_types=[ItemType[item_type] for item_type in d.get("item_types", []) if isinstance(item_type, str) and item_type in ItemType.__members__]
                        )
                    )

class ArmorUpgradeRule(ExtractUpgradeRule):
    ui_selectable: ClassVar[bool] = True
    
    def __init__(self, runes: Optional[list[ArmorUpgrade]] = None):
        super().__init__()
        self.armor_upgrades: list[ArmorUpgrade] = runes if runes is not None else []
        
    def is_valid(self) -> bool:
        return len(self.armor_upgrades) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False
        
        prefix, suffix, inscription, inherent = ItemMod.get_item_upgrades(item_id)
        armor_upgrades = [upgrade for upgrade in [prefix, suffix, inscription, *(inherent or [])] if isinstance(upgrade, ArmorUpgrade)]
        
        for rune in self.armor_upgrades:
            for item_rune in armor_upgrades:
                if rune.matches(item_rune):
                    return True
        
        return False
    
    def _serialize_data(self) -> dict[str, Any]:
        return {
            "runes": [upgrade.__class__.__name__ for upgrade in self.armor_upgrades]
        }
    
    def _comparison_data(self) -> Any:
        normalized_data = []
        for upgrade in self.armor_upgrades:
            normalized_data.append(upgrade._comparison_data())
        
        return tuple(sorted(normalized_data))
    
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.armor_upgrades = []
        for name in data.get("runes", []):
            if not isinstance(name, str):
                continue

            upgrade_cls = next(
                (
                    upgrade_type
                    for upgrade_type in _UPGRADES
                    if upgrade_type.__name__ == name and issubclass(upgrade_type, ArmorUpgrade)
                ),
                None,
            )
            if upgrade_cls is not None:
                self.armor_upgrades.append(upgrade_cls())

RangedUpgrade = NamedTuple("RangedUpgrade", [("upgrade", WeaponUpgrade | Inscription), ("target", str), ("min_value", float), ("max_value", float), ("item_types", list[ItemType])])
class UpgradeRangeRule(ExtractUpgradeRule):
    ui_selectable: ClassVar[bool] = True
    
    """
    A rule that checks if an item has an upgrade within a specified range of values. The range is defined by a minimum and maximum value for the upgrade, and the rule applies if the item has an upgrade with a value that falls within that range.
    """
    def __init__(self, upgrade_ranges: Optional[list[RangedUpgrade]] = None):
        super().__init__()
        self.upgrade_ranges: list[RangedUpgrade] = upgrade_ranges if upgrade_ranges is not None else []
    
    def is_valid(self) -> bool:
        return len(self.upgrade_ranges) > 0
    
    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False
        
        prefix, suffix, inscription, _ = ItemMod.get_item_upgrades(item_id)
        item_upgrades : list[Upgrade] = [upgrade for upgrade in [prefix, suffix, inscription] if upgrade is not None]
        
        for upgrade_range in self.upgrade_ranges:
            item_upgrade = next(
                (
                    upgrade
                    for upgrade in item_upgrades
                    if isinstance(upgrade, (WeaponUpgrade, Inscription)) and upgrade_range.upgrade.matches(upgrade)
                ),
                None,
            )
            if item_upgrade is None:
                continue

            upgrade_value = getattr(item_upgrade, upgrade_range.target, None)
            if isinstance(upgrade_value, (int, float)) and upgrade_range.min_value <= upgrade_value <= upgrade_range.max_value:
                return True

        return False
    
    def _serialize_data(self) -> dict[str, Any]:
        return {
            "upgrade_ranges": [
                {
                    "upgrade": upgrade_range.upgrade.__class__.__name__,
                    "target": upgrade_range.target,
                    "min_value": upgrade_range.min_value,
                    "max_value": upgrade_range.max_value,
                    "item_types": [item_type.name for item_type in upgrade_range.item_types],
                }
                for upgrade_range in self.upgrade_ranges
            ]
        }
        
    def _comparison_data(self) -> Any:
        normalized_data = []
        for upgrade_range in self.upgrade_ranges:
            normalized_data.append((
                upgrade_range.upgrade._comparison_data(),
                upgrade_range.target,
                upgrade_range.min_value,
                upgrade_range.max_value,
            ))
        
        return tuple(sorted(normalized_data))
        
    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.upgrade_ranges = []
        for entry in data.get("upgrade_ranges", []):
            if not isinstance(entry, dict):
                continue
            
            name = entry.get("upgrade", None)
            if not isinstance(name, str):
                continue
            
            upgrade_cls = next(
                (
                    upgrade_type
                    for upgrade_type in _UPGRADES
                    if upgrade_type.__name__ == name and issubclass(upgrade_type, (WeaponUpgrade, Inscription))
                ),
                None,
            )
            if upgrade_cls is not None:
                target = entry.get("target", None)
                min_value = entry.get("min_value", None)
                max_value = entry.get("max_value", None)
                
                valid_targets = {
                    instruction.target
                    for instruction in upgrade_cls.upgrade_info
                    if isinstance(instruction, RangeInstruction)
                }

                if not isinstance(target, str) and len(valid_targets) == 1:
                    target = next(iter(valid_targets))

                if isinstance(target, str) and target in valid_targets and isinstance(min_value, (int, float)) and isinstance(max_value, (int, float)):
                    self.upgrade_ranges.append(
                        RangedUpgrade(
                            upgrade=upgrade_cls(),
                            target=target,
                            min_value=float(min_value),
                            max_value=float(max_value),
                            item_types=[ItemType[item_type_name] for item_type_name in entry.get("item_types", []) if isinstance(item_type_name, str)]
                        )
                    )
    
    
class UpgradesRule(ExtractUpgradeRule):
    ui_selectable: ClassVar[bool] = True
    
    """
    A rule that checks if an item has a one of the specified upgrades.
    """
    def __init__(self, upgrades: Optional[list[(tuple[Upgrade, list[ItemType]] | Upgrade)]] = None):
        super().__init__()
        #add ItemType.EquippableItem to all upgrades that are not already tuples
        normalized_upgrades: list[tuple[Upgrade, list[ItemType]]] = []
        if upgrades is not None:
            for upgrade in upgrades:
                if isinstance(upgrade, Upgrade):
                    normalized_upgrades.append((upgrade, []))
                    
                elif isinstance(upgrade, tuple) and len(upgrade) == 2 and isinstance(upgrade[0], Upgrade) and (isinstance(upgrade[1], list) and all(isinstance(item_type, ItemType) for item_type in upgrade[1]) or upgrade[1] is None):
                    normalized_upgrades.append((upgrade[0], upgrade[1] if upgrade[1] is not None else []))
                    
        self.upgrades: list[tuple[Upgrade, list[ItemType]]] = normalized_upgrades

    def is_valid(self) -> bool:
        return len(self.upgrades) > 0

    def applies(self, item_id: int) -> bool:
        if not self.is_valid():
            return False
        
        item_snapshot = self.get_item(item_id)
        if item_snapshot is None:
            return False
        
        item_type = item_snapshot.item_type
        if item_type == ItemType.Rune_Mod:
            item_type = ItemMod.get_target_item_type(item_id) or item_type
        
        prefix, suffix, inscription, inherent = ItemMod.get_item_upgrades(item_id)
        item_upgrades = [upgrade for upgrade in [prefix, suffix, inscription, *(inherent or [])] if upgrade is not None]
        
        ## check if any of the specified upgrades match an upgrade on the item, while also matching the item type requirement by checking ItemType.is_matching_item_type() to allow for meta types like Weapon or EquippableItem
        for rule_upgrade, valid_item_types in self.upgrades:
            if valid_item_types is not None and len(valid_item_types) > 0 and not any(item_type.matches(valid_type) for valid_type in valid_item_types):
                continue
            
            for item_upgrade in item_upgrades:
                if rule_upgrade.matches(item_upgrade):
                    return True

        return False

    def _serialize_data(self) -> dict[str, Any]:
        return {
            "upgrades": [
                {
                    "upgrade": upgrade.to_dict(),
                    "item_types": [item_type.name for item_type in item_types] if item_types is not None else None,
                }
                for upgrade, item_types in self.upgrades
            ]
        }

    def _comparison_data(self) -> Any:
        normalized_data = []
        for upgrade, item_types in self.upgrades:
            item_type_names = tuple(sorted(item_type.name for item_type in item_types)) if item_types is not None else None
            normalized_data.append((upgrade._comparison_data(), item_type_names))
        
        return tuple(sorted(normalized_data))

    def _deserialize_data(self, data: dict[str, Any]) -> None:
        self.upgrades = []
        for entry in data.get("upgrades", []):
            upgrade_data = entry.get("upgrade", None)
            item_type_names = entry.get("item_types", None)

            if upgrade_data is None:
                continue
            
            upgrade = Upgrade.from_dict(upgrade_data)
            if upgrade is None:
                continue
            
            item_types : list[ItemType] | None = None
            if item_type_names is not None:
                item_types = []
                for name in item_type_names:
                    if isinstance(name, str) and name in ItemType.__members__:
                        item_types.append(ItemType[name])
            
            self.upgrades.append((upgrade, item_types if item_types is not None else []))
