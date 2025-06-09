from LootEx import models, settings, utility
from LootEx.data_collector import GLOBAL_CACHE
from Py4GWCoreLib.enums import Attribute, ItemType, Rarity

class Cached_Item:
    def __init__(self, item_id : int):
        from LootEx import utility, settings, data, models, enum
        
        self.item_id : int = item_id
        self.model_id : int = GLOBAL_CACHE.Item.GetModelID(item_id)
        self.item_type : ItemType = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])
        self.rarity : Rarity = Rarity(GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)[0])
        self.value : int = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
        self.is_weapon : bool = utility.Util.IsWeaponType(self.item_type)
        self.is_armor : bool = utility.Util.IsArmorType(self.item_type)
        self.is_salvageable : bool = GLOBAL_CACHE.Item.Usage.IsSalvageable(item_id)
        self.is_inscribable : bool = GLOBAL_CACHE.Item.Customization.IsInscribable(item_id)
        self.quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)
        
        
        attribute, requirements = utility.Util.GetItemRequirements(item_id)
        self.attribute : Attribute = attribute
        self.requirements : int = requirements
        self.damage = utility.Util.GetItemDamage(item_id)
        
        self.data : models.Item | None = data.Items.get_item(self.item_type, self.model_id)            
        self.config = settings.current.loot_profile.items.get_item_config(self.item_type, self.model_id) if settings.current.loot_profile else None
        self.is_blacklisted : bool = settings.current.loot_profile.is_blacklisted(self.item_type, self.model_id) if settings.current.loot_profile else False
        
        self.is_identified : bool = GLOBAL_CACHE.Item.Usage.IsIdentified(item_id)
        self.action : enum.ItemAction = enum.ItemAction.NONE
        
        self.mods : list[models.Rune | models.WeaponMod] | None = None
        self.runes : list[models.Rune]  | None= None
        self.weapon_mods : list[models.WeaponMod] | None = None
        
        self.runes_to_keep : list[models.Rune] = []
        self.weapon_mods_to_keep : list[models.WeaponMod] = []
        
        pass

    def GetMods(self) -> tuple[list[models.Rune | models.WeaponMod], list[models.Rune], list[models.WeaponMod]]:
        if self.mods is None:                        
            if self.is_salvageable:
                if self.is_weapon or self.is_armor:                        
                    mods, runes, weapon_mods = utility.Util.GetMods(self.item_id, 0)      
                                        
                    self.mods = mods
                    self.runes = runes
                    self.weapon_mods = weapon_mods
                                    
                    if settings.current.loot_profile is not None and settings.current.loot_profile.weapon_mods is not None:
                        self.runes_to_keep = [
                            rune for rune in runes if rune.identifier in settings.current.loot_profile.runes and settings.current.loot_profile.runes[rune.identifier]
                        ]
                        
                        self.weapon_mods_to_keep = [
                            mod for mod in weapon_mods if mod.identifier in settings.current.loot_profile.weapon_mods and settings.current.loot_profile.weapon_mods[mod.identifier].get(self.item_type.name, False)
                        ]    
                                
        self.mods = self.mods or []          
        self.runes = self.runes or []
        self.weapon_mods = self.weapon_mods or []
                
        return self.mods, self.runes, self.weapon_mods

    def HasModToKeep(self) -> tuple[bool, list[models.Rune], list[models.WeaponMod]]:
        self.GetMods()
                            
        return True if self.runes_to_keep or self.weapon_mods_to_keep else False, self.runes_to_keep, self.weapon_mods_to_keep