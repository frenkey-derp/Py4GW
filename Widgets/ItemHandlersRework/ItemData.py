
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import json
import math
import os
import re
from typing import Optional
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Widgets.ItemHandlersRework.Helpers import GetServerLanguage
from Widgets.ItemHandlersRework.types import ITEM_TEXTURES_PATH, MISSING_TEXTURE_PATH, ItemCategory, ItemSubCategory, MaterialType

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
            from Widgets.frenkey.LootEx.data import Data
            data = Data()
            material = data.Materials.get(self.material_model_id, None)
            
            if material is None:
                return 0
            
            if material.material_type is MaterialType.Common:
                amount = 8
            
            elif material.material_type is MaterialType.Rare:
                amount = 0.1
            
        return amount * (3 if is_highly_salvageable else 1) if amount > 0 else 0
    
    def get_average_value(self, is_highly_salvageable : bool = False) -> int:
        from Widgets.frenkey.LootEx.data import Data
        data = Data()
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
class ItemData():    
    model_id: int
    item_type: ItemType = ItemType.Unknown
    model_file_id: int = -1
    name : str = ""
    names: dict[ServerLanguage, str] = field(default_factory=dict)
    acquisition: str = ""
    description: str = ""
    attributes: list[Attribute] = field(default_factory=list)
    wiki_url: str = ""
    common_salvage: SalvageInfoCollection = field(default_factory=SalvageInfoCollection)
    rare_salvage: SalvageInfoCollection = field(default_factory=SalvageInfoCollection)
    nick_index: Optional[int] = None
    profession : Optional[Profession] = None
    contains_amount: bool = False    
    inventory_icon: Optional[str] = None
    category: ItemCategory = ItemCategory.None_
    sub_category: ItemSubCategory = ItemSubCategory.None_    
    wiki_scraped: bool = False
    is_account_data : bool = False
    
    @property
    def is_nick_item(self) -> bool:
        return self.nick_index is not None
    
    def get_name(self, language : Optional[ServerLanguage] = None) -> str:
        if language is None:
            language = GetServerLanguage()
        
        name = self.names.get(
            language, self.names.get(ServerLanguage.English, ""))
        
        if not name:
            # Get the first available name if the requested language is not found
            name = next(iter(self.names.values()), "") + " (No English Name)"
                
        pattern = r"^\s*\d+\s+|(\d+個)$"        
        self.contains_amount = re.search(pattern, name) is not None
        
        return name
        
    def get_weeks_until_next_nick(self) -> Optional[int]:
        if self.nick_index is None:
            return None
        
        today = datetime.now()
        monday_of_current_week = today.date() - timedelta(days=today.weekday())
        this_week = datetime.combine(monday_of_current_week, datetime.min.time())
        
        next_nick_date = self.get_next_nick_date()
        if next_nick_date is not None:
            delta = next_nick_date - this_week.date()
            
            if delta.days >= 0:
                return math.ceil(delta.days / 7)
            
        return None     
       
    def get_next_nick_date(self) -> Optional[date]:
        if self.nick_index is None:
            return None

        from Widgets.frenkey.LootEx.data import Data
        data = Data()

        start_date = datetime.combine(data.Nick_Cycle_Start_Date, datetime.min.time())
        today = datetime.now()

        # Monday 00:00 of current week
        monday_of_current_week = today.date() - timedelta(days=today.weekday())
        dt = datetime.combine(monday_of_current_week, datetime.min.time())
        
        # Iterate over possible nick cycles
        for i in range(0, 100):
            nick_date = datetime.combine(start_date + timedelta(weeks=self.nick_index + (i * data.Nick_Cycle_Count)), datetime.min.time())
            
            # If current time matches the start of this nick cycle
            if dt == nick_date:
                return nick_date.date()

            # Or if the cycle starts after current time
            if nick_date >= today:
                return nick_date.date()

    def __post_init__(self):
        self.name : str = self.get_name()
        self.next_nick_week: Optional[date] = self.get_next_nick_date()
        self.weeks_until_next_nick: Optional[int] = self.get_weeks_until_next_nick()
        
        texture_file = os.path.join(ITEM_TEXTURES_PATH, f"{self.inventory_icon}")
        if texture_file and os.path.exists(texture_file):
            self.texture_file = texture_file
        else:
            self.texture_file = MISSING_TEXTURE_PATH
        
    @classmethod
    def from_json(cls, data: dict) -> 'ItemData':
        model_id = data.get("ModelID", 0)
        model_file_id = data.get("ModelFileID", -1)
        names = {ServerLanguage[lang]: name for lang, name in data.get("Names", {}).items()}
        item_type = ItemType[data.get("ItemType", "Unknown")]
        acquisition = data.get("Acquisition", "")
        description = data.get("Description", "")
        inventory_icon = data.get("InventoryIcon", None)
        inventory_icon_url = data.get("InventoryIconURL", None)
        attributes = [Attribute[attr] for attr in data.get("Attributes", [])]
        wiki_url = data.get("WikiURL", "")
        common_salvage = SalvageInfoCollection.from_dict(data.get("CommonSalvage", {}))
        rare_salvage = SalvageInfoCollection.from_dict(data.get("RareSalvage", {}))
        nick_index = data.get("NickIndex", None)
        profession = Profession[data["Profession"]] if "Profession" in data and data["Profession"] else None
        category = ItemCategory[data.get("Category", "None_")]
        sub_category = ItemSubCategory[data.get("SubCategory", "None_")]
        wiki_scraped = data.get("WikiScraped", False)
        
        return cls(
            model_id=model_id,
            model_file_id=model_file_id,
            names=names,
            item_type=item_type,
            acquisition=acquisition,
            description=description,
            inventory_icon=inventory_icon,
            attributes=attributes,
            wiki_url=wiki_url,
            common_salvage=common_salvage,
            rare_salvage=rare_salvage,
            nick_index=nick_index,
            profession=profession,
            category=category,
            sub_category=sub_category,
            wiki_scraped=wiki_scraped
        )
        

ITEMS : dict[ItemType, dict[int, ItemData]] = {}

file_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(file_directory, "data")
path = os.path.join(data_directory, "items.json")
    
with open(path, 'r', encoding='utf-8') as file:
    items = json.load(file)
    
    for item_data in items:
        item = ItemData.from_json(item_data)
        
        if item.item_type not in ITEMS:
            ITEMS[item.item_type] = {}
        
        ITEMS[item.item_type][item.model_id] = item
    