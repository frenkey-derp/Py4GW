from dataclasses import dataclass
from typing import List, Optional

import PyItem

from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier
from Sources.frenkeyLib.ItemHandling.item_properties import _PROPERTY_FACTORY, ItemProperty
from Sources.frenkeyLib.ItemHandling.types import ModifierIdentifier

START_UPGRADE_IDS = {
    ModifierIdentifier.AttributeRune,
    ModifierIdentifier.Insignia_RuneOfAbsorption,  # whatever 0x240 is called
}

TARGET_IDS = {
    ModifierIdentifier.TooltipDescription,             # whatever 0x253 is called
}

@dataclass
class ParsedUpgrade:
    start_mod: DecodedModifier
    target_mod: Optional[DecodedModifier] = None
    effect_mod: Optional[DecodedModifier] = None
    
class ModifierStream:
    def __init__(self, modifiers: List[DecodedModifier]):
        self._mods = modifiers
        self._index = 0

    def peek(self) -> Optional[DecodedModifier]:
        if self._index >= len(self._mods):
            return None
        return self._mods[self._index]

    def read(self) -> Optional[DecodedModifier]:
        if self._index >= len(self._mods):
            return None
        mod = self._mods[self._index]
        self._index += 1
        return mod

    def eof(self) -> bool:
        return self._index >= len(self._mods)
    
class ParserState:
    def handle(self, parser: "ModifierParser", mod: DecodedModifier):
        raise NotImplementedError
    
class IdleState(ParserState):
    def handle(self, parser: "ModifierParser", mod: DecodedModifier):
        if mod.identifier in START_UPGRADE_IDS:
            parser.current_upgrade = ParsedUpgrade(start_mod=mod)
            parser.set_state(UpgradeStartedState())
        else:
            parser.emit_property(mod)

class UpgradeStartedState(ParserState):
    def handle(self, parser: "ModifierParser", mod: DecodedModifier):
        if mod.identifier in TARGET_IDS:
            if parser.current_upgrade:
                parser.current_upgrade.target_mod = mod
                parser.set_state(UpgradeTargetState())
        else:
            if parser.current_upgrade:
                parser.current_upgrade.effect_mod = mod
                parser.emit_upgrade()
    
            parser.set_state(IdleState())
            
class UpgradeTargetState(ParserState):
    def handle(self, parser: "ModifierParser", mod: DecodedModifier):
        if parser.current_upgrade:
            parser.current_upgrade.effect_mod = mod
            parser.emit_upgrade()
            
        parser.set_state(IdleState())
        
class ModifierParser:
    def __init__(self, raw_modifiers: list[PyItem.ItemModifier]):
        self.raw_modifiers = raw_modifiers
        
        modifiers = [DecodedModifier.from_runtime(mod) for mod in raw_modifiers]
        self.modifiers : list[DecodedModifier] = [mod for mod in modifiers if mod is not None]
        
        self.stream = ModifierStream(self.modifiers)
        self.state: ParserState = IdleState()
        self.current_upgrade: Optional[ParsedUpgrade] = None
        self.upgrades: list[ParsedUpgrade] = []
        self.properties: list[ItemProperty] = []

    def set_state(self, state: ParserState):
        self.state = state

    def emit_upgrade(self):
        if self.current_upgrade:
            self.upgrades.append(self.current_upgrade)
            self.current_upgrade = None

    def emit_property(self, mod: DecodedModifier):
        prop = _PROPERTY_FACTORY.get(mod.identifier)
        if prop:
            self.properties.append(prop(mod, self.modifiers))

    def parse(self):
        while not self.stream.eof():
            mod = self.stream.read()
            if mod:
                self.state.handle(self, mod)