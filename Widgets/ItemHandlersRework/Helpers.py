from PyItem import DyeInfo
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import DyeColor
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


@staticmethod
def GetColorFromDyeInfo(dye_info: DyeInfo) -> DyeColor:
    """
    Get the dye color associated with the dye info.
    Args:
        dye_info (DyeInfo): The dye information.
    Returns:
        DyeColor: The dye color of the item.
    """

    if dye_info is not None:
        color_id = dye_info.dye1.ToInt() if dye_info.dye1 else -1
        color = DyeColor(color_id) if color_id != -1 else None
        return color if color is not None else DyeColor.NoColor