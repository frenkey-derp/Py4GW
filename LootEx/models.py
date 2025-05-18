import re
import base64
from dataclasses import dataclass, field
from typing import Optional
from LootEx import settings
from LootEx.enum import EnemyType, ModType, ModifierValueArg
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import Attribute, Console, DamageType, ItemType, Profession, Rarity, ServerLanguage

class IntRange:
    def __init__(self, min: int = 0, max: Optional[int] = None):
        self.min: int = min
        self.max: int = max if max is not None else min

    def __str__(self) -> str:
        return f"{self.min} - {self.max}"

    def __repr__(self) -> str:
        return f"IntRange({self.min}, {self.max})"

    def __eq__(self, other):
        if isinstance(other, IntRange):
            return self.min == other.min and self.max == other.max
        return False

class ModifierValueRange():
    def __init__(self, modifier_value_arg : ModifierValueArg, min: int = 0, max: Optional[int] = None):
        self.modifier_value_arg: ModifierValueArg = modifier_value_arg
        self.min: int = min
        self.max: int = max if max is not None else min
    pass

@dataclass
class Rune():
    struct : str = ""
    namne : str = ""
    full_name : str = ""
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    descriptions: dict[ServerLanguage, str] = field(default_factory=dict)

    profession: Profession = Profession._None
    rarity: Rarity = Rarity.White
    mod_type: ModType = ModType.None_
    
    identifier: int = 0
    arg1: int = 0
    arg2: int = 0
    args: int = 0

    def __post_init__(self):
        self.name : str = self.get_name()
        self.full_name : str = self.get_full_name()
        
    def update_language(self, language: ServerLanguage):        
        self.name : str = self.get_name(language)
        self.full_name : str = self.get_full_name(language)             
        
    def get_full_name(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
        
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        return name
    
    def get_name(self, language: Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
                                
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        
        type_names = {
            ServerLanguage.English: "Insignia" if self.mod_type == ModType.Prefix else "Rune",
        }
        
        type_name = type_names.get(
            language, type_names.get(ServerLanguage.English, ""))
        
        if type_name in name:
            return name.replace(type_name, "")

        return name
    
    def is_item_modifier(self, modifier) -> bool:
        identifier = modifier.GetIdentifier() if hasattr(modifier, 'GetIdentifier') else -1

        if identifier == self.identifier:
            arg1 = modifier.GetArg1() if hasattr(modifier, 'GetArg1') else -1
            arg2 = modifier.GetArg2() if hasattr(modifier, 'GetArg2') else -1

            return arg1 == self.arg1 and arg2 == self.arg2

        return False
    
    def to_json(self) -> dict:
        return {
            'Struct': self.struct,
            'Names': {lang.name: name for lang, name in self.names.items()},
            'Descriptions': {lang.name: desc for lang, desc in self.descriptions.items()},
            'Profession': self.profession.name,
            'Rarity': self.rarity.name,
            'ModType': self.mod_type.name,
            'Identifier': self.identifier,
            'Arg1': self.arg1,
            'Arg2': self.arg2,
            'Args': self.args
        }    
    
    @staticmethod
    def from_json(json: dict) -> 'Rune':
        return Rune(
            struct=json["Struct"],
            names={ServerLanguage[lang]: name for lang, name in json["Names"].items()},
            descriptions={ServerLanguage[lang]: desc for lang, desc in json["Descriptions"].items()},
            profession=Profession[json["Profession"]],
            rarity=Rarity[json["Rarity"]],
            mod_type=ModType[json["ModType"]],
            identifier=json["Identifier"],
            arg1=json["Arg1"],
            arg2=json["Arg2"],
            args=json["Args"]
        )

@dataclass
class Item():
    model_id: int
    item_type: ItemType
    name : str = ""
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    drop_info: str = ""
    attributes: list[Attribute] = field(default_factory=list)
    wiki_url: str = ""
    materials: list[int] = field(default_factory=list)
    rare_materials: list[int] = field(default_factory=list)
    is_nick_item: bool = False
    profession : Optional[Profession] = Profession._None

    def __post_init__(self):
        self.name : str = self.get_name()

    def update_language(self, language: ServerLanguage):
        self.name : str = self.get_name(language)        
        
    def get_name(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
        
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        return name
    
    def to_json(self) -> dict:
        return {
            "ModelID": self.model_id,
            "Names": {lang.name: name for lang, name in self.names.items()},
            "ItemType": self.item_type.name,
            "DropInfo": self.drop_info,
            "Attributes": [attribute.name for attribute in self.attributes],
            "WikiURL": self.wiki_url,
            "Materials": self.materials,
            "RareMaterials": self.rare_materials,
            "IsNickItem": self.is_nick_item,
            "Profession": self.profession.name if self.profession and self.profession != Profession._None else None
        }

    @staticmethod
    def from_json(json: dict) -> 'Item':
        return Item(
            model_id=json["ModelID"],
            names={ServerLanguage[lang]: name for lang,
                   name in json["Names"].items()},
            item_type=ItemType[json["ItemType"]],
            drop_info=json["DropInfo"],
            attributes=[Attribute[attribute]
                        for attribute in json["Attributes"]],
            wiki_url=json["WikiURL"],
            materials=json["Materials"],
            rare_materials=json["RareMaterials"],
            is_nick_item=json["IsNickItem"],
            profession=Profession[json["Profession"]] if "Profession" in json and json["Profession"] else Profession._None
        )

@dataclass
class ModifierInfo:        
    identifier: int
    arg1: int
    arg2: int
    arg: int
    modifier_value_arg: ModifierValueArg = ModifierValueArg.None_
    min: int = 0
    max: int = 0        

    def __post_init__(self):
        self.arg = (self.arg1 << 8) | self.arg2
    
@dataclass
class ItemMod():
    descriptions: dict[ServerLanguage, str] = field(default_factory=dict)
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    mod_type: ModType = ModType.None_    
    modifiers: list[ModifierInfo] = field(default_factory=list)

    def __post_init__(self):
        self.name : str = self.get_name()
        self.full_name : str = self.get_full_name()
        self.description: str  = self.get_description()
        self.identifier : str = self.generate_binary_identifier()
                
    def generate_binary_identifier(self) -> str:
        # Start with mod_type (1 byte)
        data = bytearray()
        data.append(self.mod_type.value)

        # Append each modifier's identifier (3 bytes) and arg (2 bytes)
        for mod in sorted(self.modifiers, key=lambda m: m.identifier):
            data.extend(mod.identifier.to_bytes(3, byteorder='big'))
            data.extend(mod.arg.to_bytes(2, byteorder='big'))

        # Encode as base64 for safe printable format
        return base64.urlsafe_b64encode(data).decode('ascii')

    @staticmethod
    def decode_binary_identifier(encoded: str) -> tuple[ModType, list[tuple[int, int]]]:
        """
        Decode a base64 encoded weapon mod identifier.

        Returns:
            ModType: The mod type.
            List[Tuple[int, int]]: A list of (identifier, arg) tuples for each modifier.
        """
        data = base64.urlsafe_b64decode(encoded.encode('ascii'))

        mod_type = ModType(data[0])
        modifiers = []

        i = 1
        while i + 4 < len(data):
            identifier = int.from_bytes(data[i:i+3], byteorder='big')
            arg = int.from_bytes(data[i+3:i+5], byteorder='big')
            modifiers.append((identifier, arg))
            i += 5

        return mod_type, modifiers

    def update_language(self, language: ServerLanguage):
        self.name : str = self.get_name(language)   
        self.full_name : str = self.get_full_name(language) 
        self.description: str  = self.get_description(language)
    
    def get_name(self, language: Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
                                
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
            
        return name
    
    def get_full_name(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
        
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))                
        return name
    
    def get_description(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
            
        description = self.descriptions.get(
            language, self.descriptions.get(ServerLanguage.English, ""))
        
        if not description:
            return ""
        
        def get_modifier_by_id(identifier: int) -> Optional[ModifierInfo]:
            for mod in self.modifiers:
                if mod.identifier == identifier:
                    return mod
            return None

        def get_single_modifier() -> Optional[ModifierInfo]:
            return self.modifiers[0] if len(self.modifiers) == 1 else None

        def format_enum_name(name: str) -> str:
            parts = []
            for char in name:
                if char.isupper() and parts:
                    parts.append(' ')
                parts.append(char)
            name = ''.join(parts)
            return name.replace("_", " ")

        def get_formatted_value(mod: ModifierInfo, arg_type: str) -> str:
            if arg_type == "arg1":
                if mod.identifier in (9240, 10408):
                    return format_enum_name(Attribute(mod.arg1).name)
                if mod.identifier in (9400, 41240):
                    return format_enum_name(DamageType(mod.arg1).name)
                if mod.identifier in (8520, 32896):
                    return format_enum_name(EnemyType(mod.arg1).name)
            return str(getattr(mod, arg_type, f"{{{arg_type}}}"))

        def replace_indexed(match: re.Match) -> str:
            arg_type, id_str = match.group(1), match.group(2)
            mod = get_modifier_by_id(int(id_str))
            if not mod:
                return f"{{{arg_type}[{id_str}]}}"
            return get_formatted_value(mod, arg_type)

        def replace_simple(match: re.Match) -> str:
            arg_type = match.group(1)
            mod = get_single_modifier()
            if not mod:
                return f"{{{arg_type}}}"
            return get_formatted_value(mod, arg_type)

        description = re.sub(r"\{(arg1|arg2|arg|min|max)\[(\d+)\]\}", replace_indexed, description)

        if get_single_modifier():
            description = re.sub(r"\{(arg1|arg2|arg|min|max)\}", replace_simple, description)

        return description


@dataclass
class RuneV2(ItemMod):
    _rune_identifier_lookup: dict[str, str] = field(default_factory=dict)
    
    profession: Profession = Profession._None
    rarity: Rarity = Rarity.White

    def __post_init__(self):
        ItemMod.__post_init__(self)


@dataclass
class WeaponMod(ItemMod):
    _mod_identifier_lookup: dict[str, str] = field(default_factory=dict)    
    target_types : list[ItemType] = field(default_factory=list)

    ## extracted weapon mods share the same modelid, thus we need to check the item type it belongs to through ModifierIdentifier.ItemType which gives us a ModTargetType

    def __post_init__(self):
        ItemMod.__post_init__(self)
        self.is_inscription : bool = self.names.get(ServerLanguage.English, "").startswith("\"") if self.names else False
                
    def generate_binary_identifier(self) -> str:
        # Start with mod_type (1 byte)
        data = bytearray()
        data.append(self.mod_type.value)

        # Append each modifier's identifier (3 bytes) and arg (2 bytes)
        for mod in sorted(self.modifiers, key=lambda m: m.identifier):
            data.extend(mod.identifier.to_bytes(3, byteorder='big'))
            data.extend(mod.arg.to_bytes(2, byteorder='big'))

        # Encode as base64 for safe printable format
        return base64.urlsafe_b64encode(data).decode('ascii')

    @staticmethod
    def decode_binary_identifier(encoded: str) -> tuple[ModType, list[tuple[int, int]]]:
        """
        Decode a base64 encoded weapon mod identifier.

        Returns:
            ModType: The mod type.
            List[Tuple[int, int]]: A list of (identifier, arg) tuples for each modifier.
        """
        data = base64.urlsafe_b64decode(encoded.encode('ascii'))

        mod_type = ModType(data[0])
        modifiers = []

        i = 1
        while i + 4 < len(data):
            identifier = int.from_bytes(data[i:i+3], byteorder='big')
            arg = int.from_bytes(data[i+3:i+5], byteorder='big')
            modifiers.append((identifier, arg))
            i += 5

        return mod_type, modifiers

    def update_language(self, language: ServerLanguage):
        self.name : str = self.get_name(language)   
        self.full_name : str = self.get_full_name(language) 
        self.description: str  = self.get_description(language)
    
    def is_item_modifier(self, modifier, target_item_type : Optional[ItemType] = None) -> bool:
        identifier = modifier.GetIdentifier() if hasattr(modifier, 'GetIdentifier') else -1

        for mod in self.modifiers:
            if identifier == mod.identifier:
                arg1 = modifier.GetArg1() if hasattr(modifier, 'GetArg1') else -1
                arg2 = modifier.GetArg2() if hasattr(modifier, 'GetArg2') else -1

                if mod.modifier_value_arg == ModifierValueArg.Arg1:
                    if arg1 < mod.min or arg1 > mod.max or arg2 != mod.arg2:
                        return False
                
                elif mod.modifier_value_arg == ModifierValueArg.Arg2:
                    if arg2 < mod.min or arg2 > mod.max or arg1 != mod.arg1:
                        return False
                                        
                return target_item_type in self.target_types if self.target_types and target_item_type else True
        
        return False

    def get_name(self, language: Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
                                
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
            
        return name
    
    def get_full_name(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
        
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))                
        return name
    
    def get_description(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
            
        description = self.descriptions.get(
            language, self.descriptions.get(ServerLanguage.English, ""))
        
        if not description:
            return ""
        
        def get_modifier_by_id(identifier: int) -> Optional[ModifierInfo]:
            for mod in self.modifiers:
                if mod.identifier == identifier:
                    return mod
            return None

        def get_single_modifier() -> Optional[ModifierInfo]:
            return self.modifiers[0] if len(self.modifiers) == 1 else None

        def format_enum_name(name: str) -> str:
            parts = []
            for char in name:
                if char.isupper() and parts:
                    parts.append(' ')
                parts.append(char)
            name = ''.join(parts)
            return name.replace("_", " ")

        def get_formatted_value(mod: ModifierInfo, arg_type: str) -> str:
            if arg_type == "arg1":
                if mod.identifier in (9240, 10408):
                    return format_enum_name(Attribute(mod.arg1).name)
                if mod.identifier in (9400, 41240):
                    return format_enum_name(DamageType(mod.arg1).name)
                if mod.identifier in (8520, 32896):
                    return format_enum_name(EnemyType(mod.arg1).name)
            return str(getattr(mod, arg_type, f"{{{arg_type}}}"))

        def replace_indexed(match: re.Match) -> str:
            arg_type, id_str = match.group(1), match.group(2)
            mod = get_modifier_by_id(int(id_str))
            if not mod:
                return f"{{{arg_type}[{id_str}]}}"
            return get_formatted_value(mod, arg_type)

        def replace_simple(match: re.Match) -> str:
            arg_type = match.group(1)
            mod = get_single_modifier()
            if not mod:
                return f"{{{arg_type}}}"
            return get_formatted_value(mod, arg_type)

        description = re.sub(r"\{(arg1|arg2|arg|min|max)\[(\d+)\]\}", replace_indexed, description)

        if get_single_modifier():
            description = re.sub(r"\{(arg1|arg2|arg|min|max)\}", replace_simple, description)

        return description

    def has_item_type(self, item_type: ItemType) -> bool:
        if not self.target_types:
            return True

        from LootEx import data
        if (self.target_types):
            for target_type in self.target_types:
                if item_type == target_type or item_type in data.ItemType_MetaTypes.get(target_type, []):
                    return True
        else:
            # If no target types are specified, return True
            return True
                    
        return False
    

    def to_json(self) -> dict:
        return {
            'Identifier': self.identifier,
            'Descriptions': {lang.name: name for lang, name in self.descriptions.items()},
            'Names': {lang.name: name for lang, name in self.names.items()},
            'ModType': self.mod_type.name,
            'TargetTypes': [target_type.name for target_type in self.target_types],                
            'Modifiers': [
                {
                    'Identifier': modifier.identifier,
                    'Arg1': modifier.arg1,
                    'Arg2': modifier.arg2,
                    'Arg': modifier.arg,
                    'ModifierValueArg': modifier.modifier_value_arg.name,
                    'Min': modifier.min,
                    'Max': modifier.max
                } for modifier in self.modifiers
            ]
        }
    
    @staticmethod
    def from_json(json: dict) -> 'WeaponMod':
        return WeaponMod(            
            descriptions={ServerLanguage[lang]: name for lang, name in json["Descriptions"].items()},
            names={ServerLanguage[lang]: name for lang, name in json["Names"].items()},
            mod_type=ModType[json["ModType"]],
            target_types=[ItemType[target_type] for target_type in json["TargetTypes"]] if "TargetTypes" in json else [],
            modifiers=[
                ModifierInfo(
                    identifier=modifier["Identifier"],
                    arg1=modifier["Arg1"],
                    arg2=modifier["Arg2"],
                    arg=modifier["Arg"],
                    modifier_value_arg=ModifierValueArg[modifier["ModifierValueArg"]],
                    min=modifier["Min"],
                    max=modifier["Max"]
                ) for modifier in json["Modifiers"]
            ]
        )    