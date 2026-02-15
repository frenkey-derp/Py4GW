from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional, Dict, Type

import Py4GW
from PyItem import ItemModifier

@dataclass(frozen=True)
class DecodedModifier:
    identifier: int
    arg1: int
    arg2: int
    arg: int
    raw_bits: int

    @classmethod
    def from_runtime(cls, modifier : ItemModifier) -> Optional[DecodedModifier]:
        if modifier is None or not modifier.IsValid():
            return None

        runtime_identifier = modifier.GetIdentifier()
        normalized_identifier = (runtime_identifier >> 4) & 0x3FF

        return cls(
            identifier=normalized_identifier,
            arg1=modifier.GetArg1(),
            arg2=modifier.GetArg2(),
            arg=(modifier.GetArg1() << 8) | modifier.GetArg2(),
            raw_bits=modifier.GetModBits(),
        )

# ---------------------------------------------------------
# BASE PROPERTY SYSTEM
# ---------------------------------------------------------

class ItemProperty:
    identifier: int

    def __init__(self, modifier: DecodedModifier):
        self.modifier = modifier

    def describe(self) -> str:
        return f"Modifier {self.identifier}"
    
    def is_valid(self) -> bool:
        return True