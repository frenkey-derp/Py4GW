# ---------------------------------------------------------
# MODIFIER PARSER ENGINE
# ---------------------------------------------------------


from PyItem import ItemModifier
from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier
from Sources.frenkeyLib.ItemHandling.item_properties import _PROPERTY_FACTORY, ItemProperty
from typing import TypeVar

T = TypeVar("T", bound=ItemProperty)

class ItemModifierParser:
    def __init__(self, runtime_modifiers: list[ItemModifier]):
        self.raw_modifiers: list[DecodedModifier] = []
        self.properties: list[ItemProperty] = []

        # split runtime_modifiers into half, since its duplicated for some reason (each modifier appears twice in the list)
        # runtime_modifiers = runtime_modifiers[:len(runtime_modifiers) // 2]

        self._decode(runtime_modifiers)
        self._build_properties()

    def _decode(self, runtime_modifiers: list[ItemModifier]):        
        for mod in runtime_modifiers:
            decoded = DecodedModifier.from_runtime(mod)
            if decoded is not None:
                self.raw_modifiers.append(decoded)

    def _build_properties(self):
        for mod in self.raw_modifiers:
            factory = _PROPERTY_FACTORY.get(mod.identifier)
            if factory:
                prop = factory(mod, self.raw_modifiers)
                    
                if prop and isinstance(prop, ItemProperty) and type(prop) is not ItemProperty:
                    #only add if no property of that type already exists, since some modifiers have multiple entries with the same identifier but different args (e.g. one for the name and one for the description)
                    if not any(isinstance(p, type(prop)) for p in self.properties):
                        self.properties.append(prop)
                        
    def get_properties(self) -> list[ItemProperty]:
        return self.properties