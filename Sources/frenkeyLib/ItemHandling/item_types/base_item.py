from typing import Optional

from PyItem import DyeInfo

from Py4GWCoreLib.Item import Item as GameItem
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, DyeColor, Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Sources.frenkeyLib.ItemHandling.item_modifier_parser import ItemModifierParser
from Sources.frenkeyLib.ItemHandling.item_properties import ArmorProperty, AttributeRequirement, DamageCustomized, DamageProperty, DamageTypeProperty, EnergyProperty, InscriptionProperty, ItemProperty, PrefixProperty, SuffixProperty, UpgradeRuneProperty

class Item:
    item_id : int
    
    names: dict[ServerLanguage, str] = {}
    descriptions: dict[ServerLanguage, str] = {}
    item_type : ItemType
    model_id: int
    model_file_id: int
    value: int
    
    @property
    def name(self) -> str:
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return self.names.get(server_language, self.names.get(ServerLanguage.English, self.__class__.__name__))
    
    @property
    def description(self) -> str:
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return self.descriptions.get(server_language, self.descriptions.get(ServerLanguage.English, "No description available."))
    
    @classmethod
    def from_item_id(cls,item_id: int) -> Optional['Item']:
        item_type = ItemType(GameItem.GetItemType(item_id)[0])
        
        match item_type:
            case ItemType.Salvage:
                return Salvage.from_item_id(item_id)            
            case ItemType.Axe:
                return Axe.from_item_id(item_id)            
            case ItemType.Bag:
                return Bag.from_item_id(item_id)            
            case ItemType.Boots:
                return Boots.from_item_id(item_id)
            case ItemType.Bow:
                return Bow.from_item_id(item_id)
            case ItemType.Bundle:
                return Bundle.from_item_id(item_id)
            case ItemType.Chestpiece:
                return Chestpiece.from_item_id(item_id)
            case ItemType.Rune_Mod:
                return Rune_Mod.from_item_id(item_id)
            case ItemType.Usable:
                return Usable.from_item_id(item_id)
            case ItemType.Dye:
                return Dye.from_item_id(item_id)
            case ItemType.Materials_Zcoins:
                return Materials_Zcoins.from_item_id(item_id)
            case ItemType.Offhand:
                return Offhand.from_item_id(item_id)
            case ItemType.Gloves:
                return Gloves.from_item_id(item_id)
            case ItemType.Hammer:
                return Hammer.from_item_id(item_id)
            case ItemType.Headpiece:
                return Headpiece.from_item_id(item_id)
            case ItemType.CC_Shards:
                return CC_Shards.from_item_id(item_id)
            case ItemType.Key:
                return Key.from_item_id(item_id)
            case ItemType.Leggings:
                return Leggings.from_item_id(item_id)
            case ItemType.Gold_Coin:
                return Gold_Coin.from_item_id(item_id)
            case ItemType.Quest_Item:
                return Quest_Item.from_item_id(item_id)
            case ItemType.Wand:
                return Wand.from_item_id(item_id)
            case ItemType.Shield:
                return Shield.from_item_id(item_id)
            case ItemType.Staff:
                return Staff.from_item_id(item_id)
            case ItemType.Sword:
                return Sword.from_item_id(item_id)
            case ItemType.Kit:
                return Kit.from_item_id(item_id)
            case ItemType.Trophy:
                return Trophy.from_item_id(item_id)
            case ItemType.Scroll:
                return Scroll.from_item_id(item_id)
            case ItemType.Daggers:
                return Daggers.from_item_id(item_id)
            case ItemType.Present:
                return Present.from_item_id(item_id)
            case ItemType.Minipet:
                return Minipet.from_item_id(item_id)
            case ItemType.Scythe:
                return Scythe.from_item_id(item_id)
            case ItemType.Spear:
                return Spear.from_item_id(item_id)
            case ItemType.Storybook:
                return Storybook.from_item_id(item_id)
            case ItemType.Costume:
                return Costume.from_item_id(item_id)
            case ItemType.Costume_Headpiece:
                return Costume_Headpiece.from_item_id(item_id)
            
            
            case _:
                return UnknownItem.from_item_id(item_id)
        
class UnknownItem(Item):
    item_type : ItemType = ItemType.Unknown
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['UnknownItem']:
        item = UnknownItem()
        item.item_id = item_id            
        return item

class Salvage(Item):
    suffix: Optional[ItemProperty] = None
    prefix : Optional[ItemProperty] = None
    profession : Optional[Profession] = None
    
    commonly_salvaged_to : list[Item] = []
    rarely_salvaged_to : list[Item] = []
    item_type : ItemType = ItemType.Salvage
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Salvage']:
        item = Salvage()
        item.item_id = item_id            
        return item
            
class Bag(Item):
    item_type : ItemType = ItemType.Bag
    slots : int
    dye_info: DyeInfo
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Bag']:
        item = Bag()
        item.item_id = item_id            
        return item

class Bundle(Item):
    item_type : ItemType = ItemType.Bundle
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Bundle']:
        item = Bundle()
        item.item_id = item_id            
        return item

class Rune_Mod(Item):
    item_type : ItemType = ItemType.Rune_Mod
    mod_property : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Rune_Mod']:
        item = Rune_Mod()
        item.item_id = item_id            
        return item

class Usable(Item):
    item_type : ItemType = ItemType.Usable
    remaining_uses : int
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Usable']:
        item = Usable()
        item.item_id = item_id            
        return item

class Dye(Item):
    item_type : ItemType = ItemType.Dye
    remaining_uses : int
    dye_info: DyeInfo
    color : DyeColor
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Dye']:
        item = Dye()
        item.item_id = item_id            
        return item

class Materials_Zcoins(Item):
    item_type : ItemType = ItemType.Materials_Zcoins
    
    commonly_salvaged_to : list[Item] = []
    rarely_salvaged_to : list[Item] = []
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Materials_Zcoins']:
        item = Materials_Zcoins()
        item.item_id = item_id            
        return item

class CC_Shards(Item):    
    item_type : ItemType = ItemType.CC_Shards
    commonly_salvaged_to : list[Item] = []
    rarely_salvaged_to : list[Item] = []
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['CC_Shards']:
        item = CC_Shards()
        item.item_id = item_id            
        return item

class Key(Item):
    item_type : ItemType = ItemType.Key
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Key']:
        item = Key()
        item.item_id = item_id            
        return item
    
class Gold_Coin(Item):
    item_type : ItemType = ItemType.Gold_Coin
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Gold_Coin']:
        item = Gold_Coin()
        item.item_id = item_id            
        return item

class Quest_Item(Item):
    item_type : ItemType = ItemType.Quest_Item
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Quest_Item']:
        item = Quest_Item()
        item.item_id = item_id            
        return item

class Kit(Item):
    item_type : ItemType = ItemType.Kit
    remaining_uses : int
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Kit']:
        item = Kit()
        item.item_id = item_id            
        return item
    
class Trophy(Item):    
    item_type : ItemType = ItemType.Trophy
    commonly_salvaged_to : list[Item] = []
    rarely_salvaged_to : list[Item] = []
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Trophy']:
        item = Trophy()
        item.item_id = item_id            
        return item

class Scroll(Item):
    item_type : ItemType = ItemType.Scroll
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Scroll']:
        item = Scroll()
        item.item_id = item_id            
        return item

class Present(Item):
    item_type : ItemType = ItemType.Present
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Present']:
        item = Present()
        item.item_id = item_id            
        return item
    
class Minipet(Item):
    item_type : ItemType = ItemType.Minipet
    dedicated : bool
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Minipet']:
        item = Minipet()
        item.item_id = item_id            
        return item

class Storybook(Item):
    item_type : ItemType = ItemType.Storybook
    filled_pages : int
    total_pages : int
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Storybook']:
        item = Storybook()
        item.item_id = item_id            
        return item

class Costume(Item):
    item_type : ItemType = ItemType.Costume
    dye_info: DyeInfo
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Costume']:
        item = Costume()
        item.item_id = item_id            
        return item

class Costume_Headpiece(Item):
    item_type : ItemType = ItemType.Costume_Headpiece
    dye_info: DyeInfo
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Costume_Headpiece']:
        item = Costume_Headpiece()
        item.item_id = item_id            
        return item

class Armor(Item):
    armor: int
    infused : bool
    energy_bonus : int
    energy_regen_bonus : int
    
    dye_info: DyeInfo
    insignia : Optional[ItemProperty] = None
    rune : Optional[ItemProperty] = None
    
    commonly_salvaged_to : list[Item] = []
    rarely_salvaged_to : list[Item] = []
    
class Boots(Armor):
    item_type : ItemType = ItemType.Boots
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Boots']:
        item = Boots()
        item.item_id = item_id            
        return item

class Chestpiece(Armor):
    item_type : ItemType = ItemType.Chestpiece
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Chestpiece']:
        item = Chestpiece()
        item.item_id = item_id            
        return item

class Gloves(Armor):
    item_type : ItemType = ItemType.Gloves
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Gloves']:
        item = Gloves()
        item.item_id = item_id            
        return item

class Headpiece(Armor):
    item_type : ItemType = ItemType.Headpiece
    attribute_bonus : Optional[tuple[Attribute, int]]  = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Headpiece']:
        item = Headpiece()
        item.item_id = item_id            
        return item

class Leggings(Armor):
    item_type : ItemType = ItemType.Leggings
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Leggings']:
        item = Leggings()
        item.item_id = item_id            
        return item

class Weapon(Item):
    attribute : Attribute
    customized : bool
    inscribeable : bool
    dye_info: DyeInfo
    
    requirement : Optional[AttributeRequirement] = None
    commonly_salvaged_to : list[Item] = []
    rarely_salvaged_to : list[Item] = []
        
    def assign_properties(self, properties: list[ItemProperty]):
        for prop in properties:
            if hasattr(self, 'damage') and isinstance(prop, DamageProperty):
                self.damage = prop
                
            if hasattr(self, 'damage_type') and isinstance(prop, DamageTypeProperty):
                self.damage_type = prop
                
            if hasattr(self, 'requirement') and isinstance(prop, AttributeRequirement):
                self.requirement = prop
                
            if hasattr(self, 'prefix') and isinstance(prop, PrefixProperty):
                self.prefix = prop
                
            elif hasattr(self, 'suffix') and isinstance(prop, SuffixProperty):
                self.suffix = prop
                
            elif hasattr(self, 'inherent') and isinstance(prop, InscriptionProperty):
                self.inherent = prop
                
            elif hasattr(self, 'customized') and isinstance(prop, DamageCustomized):
                self.customized = True
            
            elif hasattr(self, 'energy') and isinstance(prop, EnergyProperty):
                self.energy = prop
                
            elif hasattr(self, 'armor') and isinstance(prop, ArmorProperty):
                self.armor = prop
    
class Axe(Weapon):
    item_type : ItemType = ItemType.Axe
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Axe']:
        item = Axe()
        item.item_id = item_id
            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        
        return item

class Bow(Weapon):
    item_type : ItemType = ItemType.Bow
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Bow']:
        item = Bow()
        item.item_id = item_id            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        return item

class Offhand(Weapon):
    item_type : ItemType = ItemType.Offhand
    
    energy : Optional[EnergyProperty] = None
    
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Offhand']:
        item = Offhand()
        item.item_id = item_id            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        return item

class Hammer(Weapon):
    item_type : ItemType = ItemType.Hammer
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Hammer']:
        item = Hammer()
        item.item_id = item_id            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        return item

class Wand(Weapon):
    item_type : ItemType = ItemType.Wand
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None

    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Wand']:
        item = Wand()
        item.item_id = item_id
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        return item
    
class Shield(Weapon):
    item_type : ItemType = ItemType.Shield
    
    armor : Optional[ArmorProperty] = None
    
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Shield']:
        item = Shield()
        item.item_id = item_id
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
                   
        return item

class Staff(Weapon):
    item_type : ItemType = ItemType.Staff
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    energy : Optional[EnergyProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Staff']:
        item = Staff()
        item.item_id = item_id
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        return item

class Sword(Weapon):
    item_type : ItemType = ItemType.Sword
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Sword']:
        item = Sword()
        item.item_id = item_id            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        return item

class Daggers(Weapon):
    item_type : ItemType = ItemType.Daggers
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Daggers']:
        item = Daggers()
        item.item_id = item_id            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        
        return item

class Scythe(Weapon):
    item_type : ItemType = ItemType.Scythe
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Scythe']:
        item = Scythe()
        item.item_id = item_id
            
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        
        return item          
    
class Spear(Weapon):
    item_type : ItemType = ItemType.Spear
    
    damage : Optional[DamageProperty] = None
    damage_type : Optional[DamageTypeProperty] = None
    
    prefix : Optional[ItemProperty] = None
    suffix: Optional[ItemProperty] = None
    inherent : Optional[ItemProperty] = None
    
    @classmethod
    def from_item_id(cls, item_id: int) -> Optional['Spear']:
        item = Spear()
        item.item_id = item_id
        runtime_modifiers = GameItem.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        item.assign_properties(parser.get_properties())
        
        return item