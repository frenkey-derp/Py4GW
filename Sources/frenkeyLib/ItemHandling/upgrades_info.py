class ItemInfo:
    Suffix: str
    Prefix: str
    
class WeaponItemInfo(ItemInfo):
    Inherent : str
    MinDamage : str
    MaxDamage : str
    DamageType : str
    Armor : str
    
class ArmorItemInfo(ItemInfo):
    Armor : str
    Infused : str