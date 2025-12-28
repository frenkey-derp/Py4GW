from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Widgets.ItemHandlersRework.types import ITEM_GROUP_ITEM_TYPES

@staticmethod
def IsArmorType(itemtype: ItemType) -> bool:
    return itemtype in {
        ItemType.Headpiece,
        ItemType.Chestpiece,
        ItemType.Gloves,
        ItemType.Leggings,
        ItemType.Boots,
        ItemType.Salvage,
    }


@staticmethod
def IsWeaponType(itemtype: ItemType) -> bool:
    return itemtype in {
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Offhand,
        ItemType.Scythe,
        ItemType.Shield,
        ItemType.Spear,
        ItemType.Staff,
        ItemType.Sword,
        ItemType.Wand
    }
    

@staticmethod
def GetServerLanguage():
    preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
    server_language = ServerLanguage(preference)
    return server_language

@staticmethod
def IsMatchingItemType(item_type1: ItemType, item_type2: ItemType):
    """
    Check if two item types are the same or if one is a subtype of the other.

    Args:
        item_type1 (ItemType): The first item type.
        item_type2 (ItemType): The second item type.

    Returns:
        bool: True if they are the same or one is a subtype of the other, False otherwise.
    """
    return item_type1 == item_type2 or item_type1 in ITEM_GROUP_ITEM_TYPES.get(item_type2, [])