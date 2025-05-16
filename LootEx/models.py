from dataclasses import dataclass, field
from typing import Optional

from LootEx import settings
from LootEx.enum import EnemyType, ModType
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
class WeaponMod():
    struct : str = ""
    descriptions: dict[ServerLanguage, str] = field(default_factory=dict)
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    identifier: int = 0
    arg1: int = 0
    arg2: int = 0
    args: int = 0
    mod_type: ModType = ModType.None_    

    def __post_init__(self):
        self.name : str = self.get_name()
        self.full_name : str = self.get_full_name()
        self.description: str  = self.get_description()

    def update_language(self, language: ServerLanguage):
        self.name : str = self.get_name(language)   
        self.full_name : str = self.get_full_name(language) 
        self.description: str  = self.get_description(language)
    
    def get_name(self, language: Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
                                
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        
        # # # 20% Chance for +1 of Attribute
        # if (self.identifier == 9240):
        #     attribute = Attribute(self.arg1)
        #     name = f"of {utility.Util.GetAttributeName(attribute)}"
        #     self.names = { ServerLanguage.English: name }
            
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
            
        description_format = self.descriptions.get(
            language, self.descriptions.get(ServerLanguage.English, ""))
        
        # 20% Chance for +1 of Attribute
        if (self.identifier == 9240):
            attributeName = Attribute(self.arg1).name
            attributeName = ''.join(
                [' ' + i if i.isupper() else i for i in attributeName]).strip()

            return description_format.format(
                arg1=attributeName,
                arg2=self.arg2,
            )

        # Change Damagetype
        if (self.identifier == 9400):
            damageType = DamageType(self.arg1).name
            damageType = ''.join(
                [' ' + i if i.isupper() else i for i in damageType]).strip()

            return description_format.format(
                arg1=damageType,
                arg2=self.arg2,
            )

        # Armor versus EnemyType
        if (self.identifier == 8520):
            enemyType = EnemyType(self.arg1).name
            enemyType = ''.join(
                [' ' + i if i.isupper() else i for i in enemyType]).strip()

            return description_format.format(
                arg1=enemyType,
                arg2=self.arg2,
            )

        # Damage versus EnemyType
        if (self.identifier == 32896):
            enemyType = EnemyType(self.arg1).name
            enemyType = ''.join(
                [' ' + i if i.isupper() else i for i in enemyType]).strip()
            
            return description_format.format(
                arg1=enemyType,
                arg2=self.arg2,
            )

        # Armor versus DamageType
        if (self.identifier == 41240):
            damageType = DamageType(self.arg1).name
            damageType = ''.join(
                [' ' + i if i.isupper() else i for i in damageType]).strip()

            return description_format.format(
                arg1=damageType,
                arg2=self.arg2,
            )

        # +5 Profession Primary
        if (self.identifier == 10408):
            damageType = Attribute(self.arg1).name
            damageType = ''.join(
                [' ' + i if i.isupper() else i for i in damageType]).strip()

            return description_format.format(
                arg1=damageType,
                arg2=self.arg2,
            )

        return description_format.format(
            arg1=self.arg1,
            arg2=self.arg2,
        )

    def to_json(self) -> dict:
        return {
            'Struct': self.struct,
            'Descriptions': {lang.name: name for lang, name in self.descriptions.items()},
            'Names': {lang.name: name for lang, name in self.names.items()},
            'Identifier': self.identifier,
            'Arg1': self.arg1,
            'Arg2': self.arg2,
            'Args': self.args,
            'ModType': self.mod_type.name
        }

    @staticmethod
    def from_json(json: dict) -> 'WeaponMod':
        return WeaponMod(
            struct=json["Struct"],
            descriptions={ServerLanguage[lang]: name for lang, name in json["Descriptions"].items()},
            names={ServerLanguage[lang]: name for lang, name in json["Names"].items()},
            identifier=json["Identifier"],
            arg1=json["Arg1"],
            arg2=json["Arg2"],
            args=json["Args"],
            mod_type=ModType[json["ModType"]]
        )