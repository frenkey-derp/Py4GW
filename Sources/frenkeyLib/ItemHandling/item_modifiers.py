from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, List, Optional, Dict, Type

import Py4GW
from PyItem import ItemModifier

from Sources.frenkeyLib.ItemHandling.types import ItemModifierParam, ModifierIdentifier

@dataclass(frozen=True)
class DecodedModifier:
    modifier: ItemModifier
    identifier: ModifierIdentifier
    param: ItemModifierParam
    arg1: int
    arg2: int
    arg: int
    raw_bits: int
    upgrade_id: int
    flags: int
    
    @staticmethod
    def _parse_raw_bits(value) -> int:
        if isinstance(value, int):
            return value

        if not isinstance(value, str):
            raise TypeError("Invalid raw modifier type")

        value = value.strip()

        # Binary
        if all(c in "01" for c in value):
            return int(value, 2)

        # Hex
        if value.lower().startswith("0x"):
            return int(value, 16)

        # Decimal fallback
        return int(value)
    
    @classmethod
    def from_runtime(cls, modifier : ItemModifier) -> Optional["DecodedModifier"]:
        if modifier is None or not modifier.IsValid():
            return None

        runtime_identifier = modifier.GetIdentifier()
        stripped_identifier = (runtime_identifier >> 4) & 0x3FF
        
        if stripped_identifier not in ModifierIdentifier._value2member_map_:
            return None
        
        raw = cls._parse_raw_bits(modifier.GetModBits())

        identifier = ModifierIdentifier(stripped_identifier)
        param_value = ItemModifierParam((runtime_identifier  >> 16) & 0xF)
        upgrade_id = raw & 0xFFFF
        flags = (raw >> 30) & 0x3

        arg1 = modifier.GetArg1()
        arg2 = modifier.GetArg2()

        return cls(
            modifier=modifier,
            identifier=identifier,
            param=param_value,
            arg1=arg1,
            arg2=arg2,
            arg=(arg1 << 8) | arg2,
            raw_bits=raw,
            upgrade_id=upgrade_id,
            flags=flags,
        )

@dataclass
class ItemProperty:
    modifier: DecodedModifier

    def describe(self) -> str:
        return f"ItemProperty | Modifier {self.modifier.identifier}"
    
    def is_valid(self) -> bool:
        return True