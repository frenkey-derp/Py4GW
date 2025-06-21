from datetime import date, datetime, timedelta
import json
import re
import base64
from dataclasses import dataclass, field
from typing import ClassVar, Iterable, Iterator, List, Optional, SupportsIndex

from PyItem import ItemModifier
from LootEx import settings
from LootEx import enum
from LootEx.enum import Campaign, EnemyType, MaterialType, ModType, ModifierIdentifier, ModifierValueArg
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import Attribute, Console, DamageType, ItemType, ModelID, Profession, Rarity, ServerLanguage

import importlib
importlib.reload(enum)

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
class NickItemEntry:
    Week: date
    Item: str
    Index: int = -1
    ModelId: int = -1

    @staticmethod
    def load_from_file(path: str) -> List['NickItemEntry']:
        with open(path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
            return [
                NickItemEntry(
                    Week=datetime.strptime(entry['Week'], "%m/%d/%y").date(),
                    Item=entry['Item'],
                    Index=entry['Index'] if 'Index' in entry else -1,
                    ModelId=entry['ModelId'] if 'ModelId' in entry else -1
                )
                for entry in raw_data
            ]

    def to_dict(self) -> dict:
        return {
            "Week": self.Week.strftime("%m/%d/%y"),
            "Item": self.Item,
            "ModelId": self.ModelId,
            "Index": self.Index
        }

    @staticmethod
    def save_to_file(path: str, entries: List['NickItemEntry']):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump([entry.to_dict() for entry in entries], file, indent=4, ensure_ascii=False)

class ModifierValueRange():
    def __init__(self, modifier_value_arg : ModifierValueArg, min: int = 0, max: Optional[int] = None):
        self.modifier_value_arg: ModifierValueArg = modifier_value_arg
        self.min: int = min
        self.max: int = max if max is not None else min
    pass

class SalvageInfoCollection(dict[str, 'SalvageInfo']):
    """
    A collection of SalvageInfo objects indexed by material name.
    
    This class extends the built-in dict to provide a more specific type for
    collections of SalvageInfo objects.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def to_dict(self) -> dict:
        return {material_name: salvage_info.to_dict() for material_name, salvage_info in self.items()}
    
    @staticmethod
    def from_dict(data: dict) -> 'SalvageInfoCollection':
        """
        Create a SalvageInfoCollection from a dictionary.
        
        Args:
            data (dict): A dictionary where keys are material names and values are SalvageInfo dictionaries.
        
        Returns:
            SalvageInfoCollection: An instance of SalvageInfoCollection populated with the data.
        """
        collection = SalvageInfoCollection()
        
        for material_name, salvage_info_data in data.items():
            collection[material_name] = SalvageInfo.from_dict(salvage_info_data)
            
        return collection
    
    def get_average_value(self, is_highly_salvageable : bool = False) -> float:
        """
        Calculate the average value of all salvage materials in the collection.
        
        Returns:
            int: The total average value of all materials.
        """
        total_value = 0
        
        for salvage_info in self.values():
            total_value += salvage_info.get_average_value(is_highly_salvageable)
            
        return (total_value / len(self) if self else 0)

@dataclass
class SalvageInfo():
    amount: int = -1
    min_amount: int = -1
    max_amount: int = -1
    material_model_id: int = -1
    material_name: str = "" 
    summary: str = ""
    average_amount: float = 0
    
    def __post_init__(self):
        self.generate_summary()
        
    def get_average_amount(self, is_highly_salvageable : bool = False) -> float:
        amount = 0
        
        if self.amount != -1:
            amount = self.amount
        
        elif self.min_amount != -1 and self.max_amount != -1:
            amount = (self.min_amount + self.max_amount) / 2.0
        
        else:
            from LootEx import data
            material = data.Materials.get(self.material_model_id, None)
            
            if material is None:
                return 0
            
            if material.material_type is MaterialType.Common:
                amount = 8
            
            elif material.material_type is MaterialType.Rare:
                amount = 0.1
            
        return amount * (3 if is_highly_salvageable else 1) if amount > 0 else 0
    
    def get_average_value(self, is_highly_salvageable : bool = False) -> int:
        from LootEx import data
        material = data.Materials.get(self.material_model_id, None)
    
        if material is None:
            return 0
        
        if material.material_type is MaterialType.Common:           
            return int(self.get_average_amount(is_highly_salvageable) * material.vendor_value) if material.vendor_value > 0 else 0
        
        elif material.material_type is MaterialType.Rare:
            return int(self.get_average_amount(is_highly_salvageable) * material.vendor_value) if material.vendor_value > 0 else 0
        
        return 0
        

    def generate_summary(self):
        amount = f"{self.amount}" if self.amount != -1 else f"{self.min_amount} - {self.max_amount}" if self.min_amount != -1 and self.max_amount != -1 else None
        self.summary = f"{amount} {self.material_name}" if amount else self.material_name
        
    
    def to_dict(self) -> dict:
        return {
            "Amount": self.amount,
            "MinAmount": self.min_amount,
            "MaxAmount": self.max_amount,
            "MaterialModelID": self.material_model_id,
            "MaterialName": self.material_name
        }
        
    def __str__(self) -> str:            
        return f"SalvageInfo(Amount={self.amount}, MinAmount={self.min_amount}, MaxAmount={self.max_amount}, MaterialModelID={self.material_model_id}, MaterialName='{self.material_name}')"
    
    def __repr__(self) -> str:
        return f"SalvageInfo(amount={self.amount}, min_amount={self.min_amount}, max_amount={self.max_amount}, material_model_id={self.material_model_id}, material_name='{self.material_name}')"
    
    @staticmethod
    def from_dict(data: dict) -> 'SalvageInfo':
        info = SalvageInfo()
        info.amount = data.get("Amount", -1)
        info.min_amount = data.get("MinAmount", -1)
        info.max_amount = data.get("MaxAmount", -1)
        info.material_model_id = data.get("MaterialModelID", -1)
        info.material_name = data.get("MaterialName", "")
        info.generate_summary()
        
        return info 

class AquisitionInfo():
    def __init__(self):
        self.campaign: Campaign = Campaign.None_
        self.map: str = ""
        self.map_id: int = -1
        self.sources: List[str] = []
        
    def to_dict(self) -> dict:
        return {
            "Campaign": self.campaign.name,
            "Map": self.map,
            "MapID": self.map_id,
            "Sources": self.sources
        }
            
    @staticmethod
    def from_dict(data: dict) -> 'AquisitionInfo':
        info = AquisitionInfo()
        info.campaign = Campaign[data["Campaign"]] if "Campaign" in data else Campaign.None_
        info.map = data.get("Map", "")
        info.map_id = data.get("MapID", -1)
        info.sources = data.get("Sources", [])
        return info
                   
class ItemsByType(dict[ItemType, dict[int, 'Item']]):
    """
    A dictionary that maps ItemType to a list of Item objects.
    
    This class extends the built-in dict to provide a more specific type for
    collections of Item objects categorized by their ItemType.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.All : List['Item'] = []
    
    def add_item(self, item: 'Item'):
        """
        Add an Item to the collection under the specified ItemType.
        
        Args:
            item_type (ItemType): The type of the item to add.
            item (Item): The Item object to add.
        """
        
        if item.item_type not in self:
            self[item.item_type] = {}
        
        if item.model_id not in self[item.item_type]:
            self[item.item_type][item.model_id] = item
            self.All.append(item)
        else:
            existing_item = self[item.item_type][item.model_id]
            existing_item.update(item)
    
    def sort_items(self):
        """
        Sort all items in the collection by their model ID.
        
        This method sorts the items in each ItemType category by their model ID
        and updates the All list to reflect the sorted order.
        """
        for item_type, items in self.items():
            sorted_items = sorted(items.values(), key=lambda item: (item.name, item.model_id))
            self[item_type] = {item.model_id: item for item in sorted_items}
        
        self.All.sort(key=lambda item: item.name)
    
    def get_item_data(self, item_id: int) -> Optional['Item']:
        """
        Get an Item by its item ID.
        Args:
            item_id (int): The ID of the item to retrieve.  
        Returns:
            Item: The Item data object from the specified item ID, or None if not found.
        """
        
        if item_id <= 0:
            return None
        
        item_type = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])
        model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
        
        items = self.get(item_type, {})
        item = items.get(model_id, None)
                
        return item
    
    def get_item(self, item_type: ItemType, model_id : int) -> Optional['Item']:
        """
        Get an Item by its ItemType and model ID.
        
        Args:
            item_type (ItemType): The type of the item to retrieve.
            model_id (int): The model ID of the item to retrieve.
        
        Returns:
            Item: The Item object with the specified ItemType and model ID, or None if not found.
        """
        items = self.get(item_type, {})
        item = items.get(model_id, None)
            
        return item
    
    def to_json(self) -> dict:
        return {item_type.name: {item.model_id : item.to_json() for item in items.values()} for item_type, items in self.items()}
    
    @staticmethod
    def from_dict(data: dict) -> 'ItemsByType':
        """
        Create an ItemByTypes from a dictionary.
        
        Args:
            data (dict): A dictionary where keys are ItemType names and values are lists of Item JSON objects.
        
        Returns:
            ItemByTypes: An instance of ItemByTypes populated with the data.
        """
        item_by_types = ItemsByType()
        
        for item_type_name, items in data.items():
            item_type = ItemType[item_type_name]
            item_by_types[item_type] = {}
            
            for model_id, item_data in items.items():
                item = Item.from_json(item_data)
                item_by_types.add_item(item)
            
        return item_by_types

@dataclass
class Item():
    model_id: int
    item_type: ItemType = ItemType.Unknown
    name : str = ""
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    drop_info: str = ""
    attributes: list[Attribute] = field(default_factory=list)
    wiki_url: str = ""
    common_salvage: SalvageInfoCollection = field(default_factory=SalvageInfoCollection)
    rare_salvage: SalvageInfoCollection = field(default_factory=SalvageInfoCollection)
    nick_index: Optional[int] = None
    profession : Optional[Profession] = None
    contains_amount: bool = False    
    inventory_icon: Optional[str] = None
    inventory_icon_url: Optional[str] = None
    category: enum.ItemCategory = enum.ItemCategory.None_
    sub_category: enum.ItemSubCategory = enum.ItemSubCategory.None_    
    wiki_scraped: bool = False
    
    @property
    def is_nick_item(self) -> bool:
        return self.nick_index is not None
    
    def __post_init__(self):
        self.name : str = self.get_name()
        self.next_nick_week: Optional[date] = self.get_next_nick_date()
        self.weeks_until_next_nick: Optional[int] = self.get_weeks_until_next_nick()

    def get_weeks_until_next_nick(self) -> Optional[int]:
        if self.nick_index is None:
            return None
        
        next_nick_date = self.get_next_nick_date()
        if next_nick_date:
            today = date.today()
            delta = next_nick_date - today
            if delta.days >= 0:
                return delta.days // 7
            
        return None        

    def get_next_nick_date(self) -> Optional[date]:
        if self.nick_index is None:
            return None
        
        from LootEx import data
        start_date = datetime.combine(data.Nick_Cycle_Start_Date, datetime.min.time())
        
        today = date.today()
        monday_of_current_week = today - timedelta(days=today.weekday())
        dt = datetime.combine(monday_of_current_week, datetime.min.time())
                
        for i in range(0, 100):
            nick_date = start_date + timedelta(weeks=self.nick_index + (i * data.Nick_Cycle_Count))                     
            
            if nick_date > dt:
                return date(nick_date.year, nick_date.month, nick_date.day)
       
    def has_missing_names(self) -> ServerLanguage | bool:
        if not self.names:
            return ServerLanguage.English
        
        for lang in ServerLanguage:
            if lang != ServerLanguage.Unknown:
                if lang not in self.names or not self.names[lang]:
                    return lang
        
        return False
    
    def update_language(self, language: ServerLanguage):
        self.name : str = self.get_name(language)      
        
    def has_name(self, language: ServerLanguage) -> bool:        
        return language in self.names  
        
    def get_name(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
        
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        
        if not name:
            # Get the first available name if the requested language is not found
            name = next(iter(self.names.values()), "") + " (No English Name)"
                
        pattern = r"^\s*\d+\s+|(\d+個)$"        
        self.contains_amount = re.search(pattern, name) is not None
        
        return name
    
    def set_name(self, name: str, language: ServerLanguage = ServerLanguage.English):
        self.names[language] = name        
        self.name = self.get_name(language)        
    
    def update(self, item: "Item"):
        if item.model_id != self.model_id:
            ConsoleLog("LootEx", f"Cannot update item with different model ID: {item.model_id} != {self.model_id}", Console.MessageType.Error)
            return
        
        self.item_type = item.item_type
        self.name = item.name
        
        for lang, name in item.names.items():
            if lang not in self.names or not self.names[lang]:
                self.names[lang] = name
                
        if item.drop_info:            
            self.drop_info = item.drop_info
        
        if item.attributes:
            for attribute in item.attributes:
                if attribute not in self.attributes:
                    self.attributes.append(attribute)
                    
        if item.wiki_url:
            self.wiki_url = item.wiki_url
                
        if item.nick_index is not None:
            self.nick_index = item.nick_index
        
        if item.profession is not None:
            if self.profession is None or self.profession == Profession._None:
                self.profession = item.profession
                
        self.update_language(settings.current.language)
                
    def to_json(self) -> dict:
        def get_wiki_url():
            if self.wiki_url:
                return self.wiki_url
            
            english_name = self.names.get(ServerLanguage.English, "")
            if not english_name:
                return None
            
            # Generate a wiki URL based on the English name
            base_url = "https://wiki.guildwars.com/wiki/"
            formatted_name = re.sub(r'\s+', '_', english_name.strip())
            return f"{base_url}{formatted_name}"
        
        return {
            "ModelID": self.model_id,
            "Names": {lang.name: name for lang, name in self.names.items()},
            "ItemType": self.item_type.name,
            "DropInfo": self.drop_info,
            "Attributes": [attribute.name for attribute in self.attributes] if self.attributes else [],
            "CommonSalvage": (self.common_salvage or SalvageInfoCollection()).to_dict(),
            "RareSalvage": (self.rare_salvage or SalvageInfoCollection()).to_dict(),
            "WikiURL": self.wiki_url or get_wiki_url(),
            "InventoryIcon": self.inventory_icon,
            "InventoryIconURL": self.inventory_icon_url,
            "NickIndex": self.nick_index,
            "Profession": self.profession.name if self.profession and self.profession != Profession._None else None,
            "Category": self.category.name if self.category else None,
            "SubCategory": self.sub_category.name if self.sub_category else None,
            "WikiScraped": self.wiki_scraped
        }

    @staticmethod
    def from_json(json: dict) -> 'Item':
        return Item(
            model_id=json["ModelID"],
            names={ServerLanguage[lang]: name for lang,
                   name in json["Names"].items()},
            item_type=ItemType[json["ItemType"]],
            drop_info=json["DropInfo"],
            inventory_icon=json.get("InventoryIcon", None),
            inventory_icon_url=json.get("InventoryIconURL", None),
            attributes=[Attribute[attr] for attr in json["Attributes"]] if "Attributes" in json and json["Attributes"] else [],
            wiki_url=json["WikiURL"],
            common_salvage=SalvageInfoCollection.from_dict(json.get("CommonSalvage", {})),
            rare_salvage=SalvageInfoCollection.from_dict(json.get("RareSalvage", {})), 
            nick_index=json["NickIndex"] if "NickIndex" in json else None,
            profession=Profession[json["Profession"]] if "Profession" in json and json["Profession"] else None,
            category=enum.ItemCategory[json["Category"]] if "Category" in json and json["Category"] else enum.ItemCategory.None_,
            sub_category=enum.ItemSubCategory[json["SubCategory"]] if "SubCategory" in json and json["SubCategory"] else enum.ItemSubCategory.None_,
            wiki_scraped=json.get("WikiScraped", False) 
        )

@dataclass
class Material(Item):    
    vendor_updated: datetime = datetime.min
    vendor_value: int = 0
    material_type: MaterialType = MaterialType.Common
    material_storage_slot : int = -1
    
    def to_json(self):
        dict = super().to_json()
        dict["VendorValue"] = self.vendor_value
        dict["VendorUpdated"] = self.vendor_updated.isoformat() if self.vendor_updated else None
        dict["MaterialType"] = self.material_type.name
        dict["MaterialStorageSlot"] = self.material_storage_slot if self.material_storage_slot != -1 else None
        return dict
    
    @staticmethod
    def from_json(json: dict) -> 'Material':
        item = Item.from_json(json)
        material_type = MaterialType[json.get("MaterialType", "None_")]
        if material_type is MaterialType.None_:
            material_type=MaterialType.Common if item.model_id in enum.COMMON_MATERIALS else MaterialType.Rare
            
        
        return Material(
            model_id=item.model_id,
            names=item.names,
            item_type=item.item_type,
            drop_info=item.drop_info,
            attributes=item.attributes,
            wiki_url=item.wiki_url,
            common_salvage=item.common_salvage,
            rare_salvage=item.rare_salvage,
            nick_index=item.nick_index,
            profession=item.profession,
            vendor_value=json.get("VendorValue", 0),
            vendor_updated=datetime.fromisoformat(json["VendorUpdated"]) if "VendorUpdated" in json else datetime.min,
            material_type=material_type,
            inventory_icon=item.inventory_icon,
            inventory_icon_url=item.inventory_icon_url,
            category=item.category,
            sub_category=item.sub_category,
            wiki_scraped= item.wiki_scraped,
            material_storage_slot=json.get("MaterialStorageSlot", -1) if "MaterialStorageSlot" in json else -1
        )

@dataclass
class ModifierInfo:        
    identifier: int
    arg1: int
    arg2: int
    modifier_value_arg: ModifierValueArg = ModifierValueArg.None_
    arg: int = 0
    min: int = 0
    max: int = 0        

    def __post_init__(self):
        self.arg = (self.arg1 << 8) | self.arg2

    @staticmethod
    def unpack_arg(arg: int) -> tuple[int, int]:
        arg1 = (arg >> 8) & 0xFF
        arg2 = arg & 0xFF
        return arg1, arg2

    @staticmethod
    def pack_arg(arg1: int, arg2: int) -> int:
        return (arg1 << 8) | arg2 
    
@dataclass
class ItemMod():
    descriptions: dict[ServerLanguage, str] = field(default_factory=dict)
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    mod_type: ModType = ModType.None_    
    modifiers: list[ModifierInfo] = field(default_factory=list)
    upgrade_exists: bool = True

    def __post_init__(self):
        self.name : str = self.get_name()
        self.full_name : str = self.get_full_name()
        self.description: str  = self.get_description()
        self.identifier : str = self.generate_binary_identifier()
        self.applied_name : str = self.get_applied_name()
        
    def set_name(self, name: str, language: ServerLanguage = ServerLanguage.English):
        self.names[language] = name        
        self.name = self.get_name(language)   
                
    def has_missing_names(self) -> ServerLanguage | bool:
        if not self.names:
            return ServerLanguage.English
        
        for lang in ServerLanguage:
            if lang != ServerLanguage.Unknown:
                if lang not in self.names or not self.names[lang]:
                    return lang
        
        return False
    
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
        self.applied_name : str = self.get_applied_name(language)  
    
    def get_applied_name(self, language: Optional[ServerLanguage] = None) -> str:
        name = self.get_name(language)
        return name
    
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
                if mod.identifier in (9240, 10408, 8680):
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
class Rune(ItemMod):
    _rune_identifier_lookup: dict[str, str] = field(default_factory=dict)
    
    vendor_updated: datetime = datetime.min
    vendor_value: int = 0
    profession: Profession = Profession._None
    rarity: Rarity = Rarity.White
    inventory_icon: Optional[str] = None
    inventory_icon_url: Optional[str] = None
        
    def get_applied_name(self, language: Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = settings.current.language
                                
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        
        rune_patterns : dict[ServerLanguage, str] = {
            ServerLanguage.English:             r".*Rune (?=of)",
            ServerLanguage.Spanish:            r".*(?=\()",
            ServerLanguage.Italian:            r"Runa.*(Guerriero|Mistico|Esploratore|Negromante|Ipnotizzatore|Elementalista|Assassino|Ritualista|Paragon|Derviscio)|(Runa)",
            ServerLanguage.German:             r".*Rune (?=d\.)",
            ServerLanguage.Korean:             r".*(?=\()",
            ServerLanguage.French:             r".*(?=\()",
            ServerLanguage.TraditionalChinese: r"(符文)|(\S+符文)",
            ServerLanguage.Japanese:           r".*(?=\()",
            ServerLanguage.Polish:             r".*(?=\()",
            ServerLanguage.Russian:            r".*Rune (?=of)",
            ServerLanguage.BorkBorkBork:       r".*Roone.*(?=ooff)"
        }

        insignia_patterns : dict[ServerLanguage, str] = {
            ServerLanguage.English:           r"Insignia.*]|Insignia",
            ServerLanguage.Spanish:           r"Insignia.*]|Insignia",
            ServerLanguage.Italian:           r"Insegne.*]|Insegne",
            ServerLanguage.German:            r"\[.*|Befähigung",
            ServerLanguage.Korean:            r"휘장.*|휘장",
            ServerLanguage.French:            r"Insigne.*]|Insigne",
            ServerLanguage.TraditionalChinese:r"徽記.*|徽記",
            ServerLanguage.Japanese:          r"記章.*|記章",
            ServerLanguage.Polish:            r".*Symbol|Symbol",
            ServerLanguage.Russian:           r"Insignia.*]|Insignia",
            ServerLanguage.BorkBorkBork:      r"Inseegneea.*]|Inseegneea",
        }
        
        modified_name = name
        
        if self.mod_type == ModType.Suffix:
            pattern = rune_patterns.get(language, None)
            
            if pattern:
                modified_name = re.sub(pattern, '', name)
                
        elif self.mod_type == ModType.Prefix:         
            pattern = insignia_patterns.get(language, None)
            
            if pattern:
                modified_name = re.sub(pattern, '', name).strip()

        return modified_name.strip()

    def is_in_item_modifier(self, modifiers : list["ItemModifier"]) -> bool:
        for mod in self.modifiers:
            matched = False

            for modifier in [m for m in modifiers if m.GetIdentifier() == mod.identifier]:
                if modifier:
                    arg1 = modifier.GetArg1()
                    arg2 = modifier.GetArg2()

                    if mod.modifier_value_arg == ModifierValueArg.Arg1:
                        if arg1 >= mod.min and arg1 <= mod.max and arg2 == mod.arg2:
                            matched = True
                    
                    elif mod.modifier_value_arg == ModifierValueArg.Arg2:
                        if arg2 >= mod.min and arg2 <= mod.max and arg1 == mod.arg1:
                            matched = True

                    elif mod.modifier_value_arg == ModifierValueArg.Fixed:
                        if arg1 == mod.arg1 and arg2 == mod.arg2:
                            matched = True
            
            if not matched:
                return False
        
        return True
    
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
        
        for mod in self.modifiers:    
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
        
        
    def to_json(self) -> dict:
        return {
            'Identifier': self.identifier,
            'Descriptions': {lang.name: name for lang, name in self.descriptions.items()},
            'Names': {lang.name: n for lang, n in self.names.items()},
            'ModType': self.mod_type.name,
            'Profession': self.profession.name,
            'Rarity': self.rarity.name,
            'UpgradeExists': self.upgrade_exists,
            'VendorUpdated': self.vendor_updated.isoformat() if self.vendor_updated else None,
            'VendorValue': self.vendor_value,
            'InventoryIcon': self.inventory_icon,
            'InventoryIconURL': self.inventory_icon_url,
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
    def from_json(json: dict) -> 'Rune':
        return Rune(           
            descriptions={ServerLanguage[lang]: name for lang, name in json["Descriptions"].items()},
            names={ServerLanguage[lang]: name for lang, name in json["Names"].items()},
            mod_type=ModType[json["ModType"]],
            profession=Profession[json["Profession"]],
            rarity=Rarity[json["Rarity"]],
            upgrade_exists=json.get("UpgradeExists", True),
            vendor_updated=datetime.fromisoformat(json["VendorUpdated"]) if "VendorUpdated" in json else datetime.min,
            vendor_value=json.get("VendorValue", 0),
            inventory_icon=json.get("InventoryIcon", None),
            inventory_icon_url=json.get("InventoryIconURL", None),
            modifiers=[
                ModifierInfo(
                    identifier=modifier["Identifier"],
                    arg1=modifier["Arg1"],
                    arg2=modifier["Arg2"],
                    arg=modifier["Arg"] if "Arg" in modifier else 0,
                    modifier_value_arg=ModifierValueArg[modifier["ModifierValueArg"]],
                    min=modifier["Min"] if "Min" in modifier else 0,
                    max=modifier["Max"] if "Max" in modifier else 0
                ) for modifier in json["Modifiers"]
            ]
        )


@dataclass
class WeaponMod(ItemMod):
    _mod_identifier_lookup: dict[str, str] = field(default_factory=dict)    
    target_types : list[ItemType] = field(default_factory=list)

    ## extracted weapon mods share the same modelid, thus we need to check the item type it belongs to through ModifierIdentifier.ItemType which gives us a ModTargetType

    def generate_binary_identifier(self) -> str:
        # Start with mod_type (1 byte)
        data = bytearray()
        data.append(self.mod_type.value)

        # Append each modifier's identifier (3 bytes) and arg (2 bytes)
        for mod in sorted(self.modifiers, key=lambda m: m.identifier):
            data.extend(mod.identifier.to_bytes(3, byteorder='big'))
            data.extend(mod.arg.to_bytes(2, byteorder='big'))
            
            for target_type in self.target_types:
                data.extend(target_type.value.to_bytes(1, byteorder='big'))

        # Encode as base64 for safe printable format
        return base64.urlsafe_b64encode(data).decode('ascii')
    
    def __post_init__(self):
        ItemMod.__post_init__(self)
        self.is_inscription : bool = self.names.get(ServerLanguage.English, "").startswith("\"") if self.names else False

    def is_in_item_modifier(self, modifiers : list["ItemModifier"], item_type : ItemType, tolerance : int = -1) -> bool:
        is_tolerance_set = tolerance if tolerance >= 0 else 0
                
        for mod in self.modifiers:            
            if not is_tolerance_set:
                tolerance = mod.arg1 if mod.modifier_value_arg == ModifierValueArg.Arg1 else mod.arg2 if mod.modifier_value_arg == ModifierValueArg.Arg2 else 0
                
            matched = False
            for modifier in [m for m in modifiers if m.GetIdentifier() == mod.identifier]:                
                arg1 = modifier.GetArg1()
                arg2 = modifier.GetArg2()

                if mod.modifier_value_arg == ModifierValueArg.Arg1:
                    if arg1 >= mod.min and arg1 <= mod.max and arg2 == mod.arg2:
                        matched = arg1 >= mod.max - tolerance
                
                elif mod.modifier_value_arg == ModifierValueArg.Arg2:
                    if arg2 >= mod.min and arg2 <= mod.max and arg1 == mod.arg1:
                        matched = arg2 >= mod.max - tolerance

                elif mod.modifier_value_arg == ModifierValueArg.Fixed:
                    if arg1 == mod.arg1 and arg2 == mod.arg2:
                        matched = True
                        
                elif mod.modifier_value_arg == ModifierValueArg.None_:
                    matched = True
                        
            if not matched:       
                return False
            
            
        from LootEx import utility
        if item_type == ItemType.Rune_Mod:
            applied_to_item_type_mod = next(modifier for modifier in modifiers if modifier.GetIdentifier() == ModifierIdentifier.TargetItemType)
            applied_to_item_type_id = applied_to_item_type_mod.GetArg1()
            applied_to_item_type = ItemType(applied_to_item_type_id)
                        
            return any(utility.Util.IsMatchingItemType(applied_to_item_type, target_item_type) for target_item_type in self.target_types)
            
        else:
            return any(utility.Util.IsMatchingItemType(item_type, target_item_type) for target_item_type in self.target_types)
     
    def matches_modifiers(self, modifiers : list[tuple[int, int, int]], item_type : ItemType) -> tuple[bool, bool]:
        """
        Check if the rune matches the given modifiers.
        
        Args:
            modifiers (list[tuple[int, int, int]]): A list of tuples containing identifier, arg1, and arg2.
        
        Returns:
            tuple[bool, bool]: A tuple where the first element indicates if it matches any modifier,
                                and the second element indicates if it matches the maximum value.
        """
        
        results : list[tuple[bool, bool]] = []
        
        for mod in self.modifiers:    
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
        
        from LootEx import utility
        if item_type == ItemType.Rune_Mod:
            applied_to_item_type_mod = next((identifier, arg1, arg2) for identifier, arg1, arg2 in modifiers if identifier == ModifierIdentifier.TargetItemType)
            applied_to_item_type = ItemType(applied_to_item_type_mod[1])
                        
            return any(utility.Util.IsMatchingItemType(applied_to_item_type, target_item_type) for target_item_type in self.target_types), all(result[1] for result in results)
            
        else:
            return any(utility.Util.IsMatchingItemType(item_type, target_item_type) for target_item_type in self.target_types), all(result[1] for result in results)
    
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
            'UpgradeExists': self.upgrade_exists,          
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
    
    def update(self, item_mod: 'WeaponMod'):
        if item_mod.mod_type != self.mod_type:
            ConsoleLog("LootEx", f"Cannot update weapon mod with different mod type: {item_mod.mod_type} != {self.mod_type}", Console.MessageType.Error)
            return
                
        for lang, name in item_mod.names.items():
            if lang not in self.names or not self.names[lang] or self.names[lang] == "" or self.names[lang] != name:
                self.names[lang] = name
                
        for lang, description in item_mod.descriptions.items():
            if lang not in self.descriptions or not self.descriptions[lang] or self.descriptions[lang] == "" or self.descriptions[lang] != description:
                self.descriptions[lang] = description
    
    @staticmethod
    def from_json(json: dict) -> 'WeaponMod':
        return WeaponMod(            
            descriptions={ServerLanguage[lang]: name for lang, name in json["Descriptions"].items()},
            names={ServerLanguage[lang]: name for lang, name in json["Names"].items()},
            mod_type=ModType[json["ModType"]],
            target_types=[ItemType[target_type] for target_type in json["TargetTypes"]] if "TargetTypes" in json else [],
            upgrade_exists=json["UpgradeExists"],
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