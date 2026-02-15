# ---------------------------------------------------------
# MODIFIER PARSER ENGINE
# ---------------------------------------------------------

from collections.abc import Iterable
from typing import Optional

import Py4GW
from PyItem import ItemModifier
from Sources.frenkeyLib.ItemHandling.insignias import Insignia
from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier, ItemProperty
from Sources.frenkeyLib.ItemHandling.item_properties import _PROPERTY_REGISTRY
from typing import TypeVar, Type, Optional, List, Dict, Iterable

T = TypeVar("T", bound=ItemProperty)

class ItemModifierParser:
    def __init__(self, runtime_modifiers: list[ItemModifier]):
        self.raw_modifiers: list[DecodedModifier] = []
        self.properties: list[ItemProperty] = []

        self._decode(runtime_modifiers)
        self._build_properties()

    def _decode(self, runtime_modifiers: list[ItemModifier]):
        
        for mod in runtime_modifiers:
            decoded = DecodedModifier.from_runtime(mod)
            if decoded is not None:
                self.raw_modifiers.append(decoded)

    def _build_properties(self):
        for mod in self.raw_modifiers:
            property_cls = _PROPERTY_REGISTRY.get(mod.identifier)
            if property_cls:
                prop = property_cls(mod)
                # only add properties that are not yet added, to avoid duplicates from multiple modifiers with the same identifier
                # if not any(isinstance(p, property_cls) and not isinstance(p, Insignia) for p in self.properties):
                if prop.is_valid():
                    self.properties.append(prop)

    # ----------------------------
    # Public API
    # ----------------------------

    def get_properties(self) -> list[ItemProperty]:
        return self.properties

    def get_property(self, property_type: Type[T]) -> Optional[T]:
        for prop in self.properties:
            if isinstance(prop, property_type):
                return prop
        return None

    def has_identifier(self, identifier: int) -> bool:
        return any(mod.identifier == identifier for mod in self.raw_modifiers)

    def get_all_identifiers(self) -> list[int]:
        return [mod.identifier for mod in self.raw_modifiers]
