from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Optional

import os
import json
import Py4GW

from Py4GWCoreLib.enums_src.GameData_enums import Attribute, DamageType, EnemyType, Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage

from Widgets.ItemHandlersRework.Helpers import GetServerLanguage, IsMatchingItemType
from Widgets.ItemHandlersRework.types import ModType, ModifierIdentifier, ModifierValueArg, ModsModels

item_textures_path = os.path.join(Py4GW.Console.get_projects_path(), "Textures", "Items")
missing_texture_path = os.path.join(Py4GW.Console.get_projects_path(), "Textures", "missing_texture.png")

@dataclass(slots=True)
class Modifier():        
    identifier: int
    arg1: int
    arg2: int
    
@dataclass(slots=True)
class ModifierInfo(Modifier):
    modifier_value_arg: ModifierValueArg = ModifierValueArg.None_
    arg: int = 0
    min: int = 0
    max: int = 0  
    
    @classmethod
    def from_dict(cls, data: dict):
        modifier_info = cls(
            identifier=data.get("Identifier", 0),
            arg1=data.get("Arg1", 0),
            arg2=data.get("Arg2", 0),
            modifier_value_arg=ModifierValueArg[data.get("ModifierValueArg", ModifierValueArg.None_.name)],
            arg=data.get("Arg", 0),
            min=data.get("Min", 0),
            max=data.get("Max", 0)
        )
        return modifier_info
    
@dataclass(slots=True)
class Mod():
    identifier : str = ""
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    
    descriptions: dict[ServerLanguage, str] = field(default_factory=dict)
    mod_type: ModType = ModType.None_    
    modifiers_definition: list[ModifierInfo] = field(default_factory=list)
    upgrade_exists: bool = True
    
@dataclass(slots=True)
class Rune(Mod):
    profession: Profession = Profession._None
    rarity: Rarity = Rarity.White
    
    model_id: int = -1
    model_file_id: int = -1
    texture_file: str = field(init=False)
    
    inventory_icon: Optional[str] = None
    
    vendor_updated: datetime = field(init=False)
    vendor_value: int = field(init=False)
    is_maxed : bool = field(default=False)
    matching_modifiers : list[Modifier] = field(default_factory=list)
    
    def __post_init__(self):
        texture_file = os.path.join(item_textures_path, f"{self.inventory_icon}")
        
        if texture_file and os.path.exists(texture_file):
            self.texture_file = texture_file
        else:
            self.texture_file = missing_texture_path
            
        self.vendor_updated = datetime.min
        self.vendor_value = 0
    
    def matches_modifiers(self, modifiers : list[tuple[int, int, int]]) -> tuple[bool, bool]:
        """
        Check if the rune matches the given modifiers.
        
        Args:
            modifiers (list[tuple[int, int, int]]): A list of tuples containing identifier, arg1, and arg2.
        
        Returns:
            tuple[bool, bool]: A tuple where the first element indicates if it matches any modifier,
                               and the second element indicates if it matches the maximum value.
        """
        
        results : list[tuple[bool, bool]] = []
        
        for mod in self.modifiers_definition:    
            matched = False
            maxed = False    
            
            for identifier, arg1, arg2 in modifiers:
                if mod.identifier != identifier:
                    continue
                
                if mod.modifier_value_arg == ModifierValueArg.Arg1:
                    if arg1 >= mod.min and arg1 <= mod.max and arg2 == mod.arg2:
                        matched = True
                        maxed = arg1 >= mod.max
                        results.append((matched, maxed))
                
                elif mod.modifier_value_arg == ModifierValueArg.Arg2:
                    if arg2 >= mod.min and arg2 <= mod.max and arg1 == mod.arg1:
                        matched = True
                        maxed = arg2 >= mod.max
                        results.append((matched, maxed))

                elif mod.modifier_value_arg == ModifierValueArg.Fixed:
                    if arg1 == mod.arg1 and arg2 == mod.arg2:
                        matched = True
                        maxed = True
                        results.append((matched, maxed))                        
        
            if not matched:
                return False, False        
        
        if not results:
            return False, False
        
        if any(result[0] == False for result in results):
            return False, False
        
        return all(result[0] for result in results), all(result[1] for result in results)        
    
    def copy(self) -> "Rune":
        rune_copy = Rune()
        rune_copy.identifier = self.identifier
        rune_copy.descriptions = self.descriptions.copy()
        rune_copy.names = self.names.copy()
        rune_copy.mod_type = self.mod_type
        rune_copy.profession = self.profession
        rune_copy.rarity = self.rarity
        rune_copy.model_id = self.model_id
        rune_copy.model_file_id = self.model_file_id
        rune_copy.inventory_icon = self.inventory_icon
        rune_copy.modifiers_definition = self.modifiers_definition.copy()
        rune_copy.is_maxed = self.is_maxed
        rune_copy.matching_modifiers = self.matching_modifiers.copy()
        
        return rune_copy
    
    @classmethod
    def from_json(cls, data: dict):
        rune = cls()
        rune.identifier = data.get("Identifier", "")
        
        rune.descriptions = {ServerLanguage[lang]: desc for lang,
                   desc in data.get("Descriptions", {}).items()}
        
        rune.names = {ServerLanguage[lang]: name for lang,
                   name in data.get("Names", {}).items()}
        
        rune.mod_type = ModType[data.get("ModType", ModType.None_.name)]
        rune.profession = Profession[data.get("Profession", Profession._None.name)]
        rune.rarity = Rarity[data.get("Rarity", Rarity.White.name)]
        rune.model_id = data.get("ModelID", -1)
        rune.model_file_id = data.get("ModelFileID", -1)
        rune.modifiers_definition = [ModifierInfo.from_dict(mod_info) for mod_info in data.get("Modifiers", [])]
        
        return rune
    
    @staticmethod
    def get_from_modifiers(modifiers: list[tuple[int, int, int]]) -> list["Rune"] | None:
        if not modifiers:
            return None
                
        mod_infos : list["Rune"] = []
        for rune in RUNES.values():            
            
            matches, is_maxed = rune.matches_modifiers(modifiers)
            if not matches:
                continue
                    
            rune_mod_info = rune.copy()
            rune_mod_info.is_maxed = is_maxed
            # rune_mod_info.modifiers = matches
            
            mod_infos.append(rune_mod_info) 
        
        return mod_infos   

@dataclass(slots=True)
class WeaponMod(Mod):
    target_types : list[ItemType] = field(default_factory=list)
    item_mods : dict[ItemType, ModsModels] = field(default_factory=dict)
    item_type_specific : dict[ItemType, ModifierInfo] = field(default_factory=dict)
    
    Value : int = 0
    Modifiers : list[tuple[int, int, int]] = field(default_factory=list)
    Arg1 : int = 0
    Arg2 : int = 0
    IsMaxed : bool = False
    Description : str = ""
         
    def copy(self) -> "WeaponMod":
        weapon_mod = WeaponMod()
        weapon_mod.identifier = self.identifier
        weapon_mod.descriptions = self.descriptions.copy()
        weapon_mod.names = self.names.copy()
        weapon_mod.mod_type = self.mod_type
        weapon_mod.target_types = self.target_types.copy()
        weapon_mod.item_mods = self.item_mods.copy()
        weapon_mod.item_type_specific = self.item_type_specific.copy()
        weapon_mod.modifiers_definition = self.modifiers_definition.copy()
        weapon_mod.Value = self.Value
        weapon_mod.Modifiers = self.Modifiers.copy()
        weapon_mod.Arg1 = self.Arg1
        weapon_mod.Arg2 = self.Arg2
        weapon_mod.IsMaxed = self.IsMaxed
        weapon_mod.Description = self.Description
        
        return weapon_mod
         
    @staticmethod
    def get_from_modifiers(modifiers: list[tuple[int, int, int]], item_type: ItemType = ItemType.Unknown, model_id: int = -1) -> list["WeaponMod"] | None:
        if not modifiers:
            return None
    
        mod_infos : list["WeaponMod"] = []
        
        identifiers = [identifier for identifier, _, _ in modifiers]                   
        potential_weapon_mods = [weapon_mod for weapon_mod in WEAPON_MODS.values() if any(mod.identifier in identifiers for mod in weapon_mod.modifiers_definition)] 
        
        for weapon_mod in potential_weapon_mods:
            found = False
            
            # Find all indexes of our first weapon_mod.modifiers identifiers in the modifiers list
            matching_indexes = [index for index, (identifier, _, _) in enumerate(modifiers) if any(mod.identifier == identifier for mod in weapon_mod.modifiers_definition)]
            
            # Check if we have any match for a sequential match of all weapon_mod.modifiers in modifiers
            match_found = False
            matched_Modifiers = []
            
            for start_index in matching_indexes:
                match_found = True
                for offset, mod in enumerate(weapon_mod.modifiers_definition):
                    current_index = start_index + offset
                    if current_index >= len(modifiers):
                        match_found = False
                        matched_Modifiers = []
                        break
                    
                    identifier, arg1, arg2 = modifiers[current_index]
                    if mod.identifier != identifier:
                        match_found = False
                        matched_Modifiers = []
                        break
                    
                    match(mod.modifier_value_arg):
                        case ModifierValueArg.Arg1:
                            if not (arg1 >= mod.min and arg1 <= mod.max and arg2 == mod.arg2):
                                match_found = False
                                matched_Modifiers = []
                                break
                            
                        case ModifierValueArg.Arg2:
                            if not (arg2 >= mod.min and arg2 <= mod.max and arg1 == mod.arg1):
                                match_found = False
                                matched_Modifiers = []
                                break
                            
                        case ModifierValueArg.Fixed:
                            if not (arg1 == mod.arg1 and arg2 == mod.arg2):
                                match_found = False
                                matched_Modifiers = []
                                break
                            
                        case ModifierValueArg.None_:
                            pass
                
                    
                    if item_type in weapon_mod.item_type_specific:
                        item_type_specific = weapon_mod.item_type_specific[item_type]
                        item_type_index = current_index - 1
                        
                        if item_type_index < 0 or item_type_index >= len(modifiers):
                            match_found = False
                            matched_Modifiers = []
                            break
                        
                        identifier_it, arg1_it, arg2_it = modifiers[item_type_index]
                        if not (identifier_it == item_type_specific.identifier and arg1_it == item_type_specific.arg1 and arg2_it == item_type_specific.arg2):
                            match_found = False
                            matched_Modifiers = []
                            break
                
                if match_found:
                    matched_Modifiers = modifiers[start_index:start_index + len(weapon_mod.modifiers_definition)]
                    break
            
            if not match_found:
                continue
                        
            if item_type == ItemType.Rune_Mod:
                applied_to_item_type_mod = next((identifier, arg1, arg2) for identifier, arg1, arg2 in modifiers if identifier == ModifierIdentifier.TargetItemType)
                applied_to_item_type = ItemType(applied_to_item_type_mod[1])

                mod_model_id = weapon_mod.item_mods.get(applied_to_item_type, None) or 0
                                
                if not mod_model_id == model_id:
                    continue

            else:
                matches_item_type = any(IsMatchingItemType(item_type, target_item_type) for target_item_type in weapon_mod.item_mods.keys())
                if not matches_item_type:
                    continue
                            
            def get_variable_mod_info() -> Optional[ModifierInfo]:
                if len(weapon_mod.modifiers_definition) == 1:
                    return weapon_mod.modifiers_definition[0]
                    
                for mod in weapon_mod.modifiers_definition:
                    if mod.modifier_value_arg in (ModifierValueArg.Arg1, ModifierValueArg.Arg2):                    
                        return mod
                    
                for mod in weapon_mod.modifiers_definition:
                    if mod.modifier_value_arg is ModifierValueArg.Fixed:  
                        return mod
                    
                for mod in weapon_mod.modifiers_definition:
                    return mod
                    
                return None
        
            def get_mod_value(mod_info: ModifierInfo) -> int:                
                if not mod_info:
                    return 0
                
                for identifier, arg1, arg2 in matched_Modifiers:
                    if mod_info.identifier != identifier:
                        continue
                    
                    if mod_info.modifier_value_arg == ModifierValueArg.Arg1:
                        return arg1
                    
                    elif mod_info.modifier_value_arg == ModifierValueArg.Arg2:
                        return arg2
                    
                    elif mod_info.modifier_value_arg == ModifierValueArg.Fixed:
                        return 0
                    
                    elif mod_info.modifier_value_arg == ModifierValueArg.None_:
                        return 0
                
                return 0
            
            mod_info = get_variable_mod_info()
            
            if not mod_info:
                continue
            
            weapon_mod = weapon_mod.copy()
            weapon_mod.Value = get_mod_value(mod_info)
            weapon_mod.Modifiers = matched_Modifiers
            weapon_mod.Arg1 = mod_info.arg1
            weapon_mod.Arg2 = mod_info.arg2
            weapon_mod.IsMaxed = weapon_mod.Value >= mod_info.max 
            weapon_mod.Description = weapon_mod.get_description()
                            
            mod_infos.append(weapon_mod)
            
        return mod_infos
    
    def get_description(self, language: Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = GetServerLanguage()

        description = self.descriptions.get(
            language, self.descriptions.get(ServerLanguage.English, "")
        )

        if not description:
            return ""
                
        def get_modifier_info_by_id(identifier: int) -> Optional[ModifierInfo]:
            for mod in self.modifiers_definition:
                if mod.identifier == identifier:
                    return mod
                
            return None

        def get_single_modifier() -> Optional[ModifierInfo]:
            return self.modifiers_definition[0] if len(self.modifiers_definition) == 1 else None

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
                if mod.identifier in (9240, 10408, 8680):
                    return format_enum_name(Attribute(mod.arg1).name)
                if mod.identifier in (9400, 41240):
                    return format_enum_name(DamageType(mod.arg1).name)
                if mod.identifier in (8520, 32896):
                    return format_enum_name(EnemyType(mod.arg1).name)
                            
            return str(getattr(mod, arg_type, f"{{{arg_type}}}"))

        def get_modifier_values(identifier: int) -> tuple[int, int]:
            for iden, arg1, arg2 in self.Modifiers:
                if iden == identifier:
                    return arg1, arg2
                
            return 0, 0

        def replace_indexed(match: re.Match) -> str:
            arg_type, id_str = match.group(1), match.group(2)
            modifier_info = get_modifier_info_by_id(int(id_str))
            
            if not modifier_info:
                return f"{{{arg_type}[{id_str}]}}"
            
            arg1, arg2 = get_modifier_values(modifier_info.identifier)
                        
            if modifier_info.modifier_value_arg == ModifierValueArg.Arg1 and arg_type == "arg1":
                return str(arg1)
            
            if modifier_info.modifier_value_arg == ModifierValueArg.Arg2 and arg_type == "arg2":
                return str(arg2)    
            
            return get_formatted_value(modifier_info, arg_type)

        def replace_simple(match: re.Match) -> str:
            arg_type = match.group(1)
            modifier = get_single_modifier()
            
            if not modifier:
                return f"{{{arg_type}}}"
            
            arg1, arg2 = get_modifier_values(modifier.identifier)

            if arg_type == "arg1" and modifier.modifier_value_arg == ModifierValueArg.Arg1:
                return str(arg1)
            
            if arg_type == "arg2" and modifier.modifier_value_arg == ModifierValueArg.Arg2:
                return str(arg2)

            return get_formatted_value(modifier, arg_type)

        
        # Replace indexed arguments: {arg1[42]}, {arg2[12]}, etc.
        # description = re.sub(r"\{(arg1|arg2|arg|min|max)\[(\d+)\]\}", replace_indexed, description)
        description = re.sub(r"\{(arg1|arg2|arg|min|max)\[(\d+)\]\}", replace_indexed, description, flags=re.DOTALL)


        # Replace simple arguments: {arg1}, {arg2}, etc.
        # if get_single_modifier():
        description = re.sub(r"\{(arg1|arg2|arg|min|max)\}", replace_simple, description, flags=re.DOTALL)

        return description
    
    @classmethod
    def from_json(cls, data: dict):
        weapon_mod = cls()
        weapon_mod.identifier = data.get("Identifier", "")
        
        weapon_mod.descriptions = {ServerLanguage[lang]: desc for lang,
                   desc in data.get("Descriptions", {}).items()}
        
        weapon_mod.names = {ServerLanguage[lang]: name for lang,
                   name in data.get("Names", {}).items()}
        
        weapon_mod.mod_type = ModType[data.get("ModType", ModType.None_.name)]
        weapon_mod.item_mods = {ItemType[item_type]: ModsModels[mod_info] for item_type, mod_info in data.get("ItemMods", {}).items()}
        weapon_mod.target_types = [ItemType[target_type] for target_type in data.get("TargetTypes", [])]
        weapon_mod.upgrade_exists = data.get("UpgradeExists", True)
        weapon_mod.item_type_specific = {ItemType[item_type]: ModifierInfo.from_dict(mod_info) for item_type, mod_info in data.get("ItemTypeSpecific", {}).items()}
        weapon_mod.modifiers_definition = [ModifierInfo.from_dict(mod_info) for mod_info in data.get("Modifiers", [])]
        return weapon_mod

RUNES : dict[str, Rune] = {}
WEAPON_MODS : dict[str, WeaponMod] = {}

file_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(file_directory, "data")
path = os.path.join(data_directory, "runes.json")

with open(path, 'r', encoding='utf-8') as file:
    runes = json.load(file)

    RUNES = {rune_data["Identifier"]: Rune.from_json(rune_data) for rune_data in runes.values()}
    
path = os.path.join(data_directory, "weapon_mods.json")
with open(path, 'r', encoding='utf-8') as file:
    weapon_mods = json.load(file)
    WEAPON_MODS = {wu_data["Identifier"]: WeaponMod.from_json(wu_data) for wu_data in weapon_mods.values()}