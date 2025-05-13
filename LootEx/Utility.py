from typing import Optional
from LootEx import Data, item_configuration
from LootEx.item_actions import ItemAction
from LootEx.item_configuration import ItemConfiguration

import importlib

from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, Utils
from Py4GWCoreLib.enums import Attribute, ItemType, Rarity, DyeColor

importlib.reload(item_configuration)


class Util:
    @staticmethod
    def GetAttributes(itemType: ItemType) -> list[Attribute]:
        if itemType in Data.AttributeRequirements:
            return Data.AttributeRequirements[itemType]
        else:
            return []

    @staticmethod
    def GetAttributeName(attribute: Attribute) -> str:
        namme = attribute.name

        # Split the name by uppercase letters
        parts = []
        for char in namme:
            if char.isupper() and parts:
                parts.append(' ')
            parts.append(char)

        # Join the parts with spaces and convert to lowercase
        name = ''.join(parts)

        # Split the name by underscores
        name = name.replace("_", " ")

        return name
    
    @staticmethod
    def GetActionName(action : ItemAction) -> str:
        name = action.name

        # Split the name at underscores
        parts = name.split("_")
        
        # Capitalize the first letter of each part
        parts = [part.capitalize() for part in parts]
        
        # Join the parts back together with spaces
        name = ' '.join(parts)

        return name

    @staticmethod
    def GetMaxDamage(requirement: int, itemType: Optional[ItemType] = ItemType.Unknown) -> Data.IntRange:
        requirement = 9 if requirement > 9 else requirement
        itemType = itemType if itemType != None else ItemType.Unknown

        return Data.DamageRanges[itemType][requirement] if itemType in Data.DamageRanges and requirement in Data.DamageRanges[itemType] else Data.IntRange(0, 0)

    @staticmethod
    def IsMaxDamage(damage_range: Data.IntRange, requirement: int, itemType: ItemType = ItemType.Unknown, tollerance: Data.IntRange = Data.IntRange()) -> bool:
        max_damage = Util.GetMaxDamage(requirement, itemType)

        if max_damage.min == 0 and max_damage.max == 0:
            return False

        return damage_range.min == max_damage.min - tollerance.min and damage_range.max >= max_damage.max - tollerance.max

    @staticmethod
    def IsArmor(item: ItemConfiguration) -> bool:
        dataitem = Data.Items[item.model_id] if item.model_id in Data.Items else None

        if dataitem is not None:
            itemtype = dataitem.ItemType
            return itemtype in {
                ItemType.Headpiece,
                ItemType.Chestpiece,
                ItemType.Gloves,
                ItemType.Leggings,
                ItemType.Boots,
            }
        return False

    @staticmethod
    def IsWeapon(item: ItemConfiguration) -> bool:
        dataitem = Data.Items[item.model_id] if item.model_id in Data.Items else None

        if dataitem is not None:
            itemtype = dataitem.ItemType
            if itemtype in {
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
            }:
                return True
        return False

    @staticmethod
    def GetItemType(int) -> ItemType:
        for item_type in ItemType:
            if int == item_type.value:
                return item_type

        return ItemType.Unknown

    @staticmethod
    def GetRarityColor(rarity):
        rarity_colors = {
            Rarity.White: {
                "frame": Utils.RGBToColor(255, 255, 255, 125),
                "content": Utils.RGBToColor(255, 255, 255, 75),
                "text": Utils.RGBToColor(255, 255, 255, 255),
            },
            Rarity.Blue: {
                "frame": Utils.RGBToColor(153, 238, 255, 125),
                "content": Utils.RGBToColor(153, 238, 255, 75),
                "text": Utils.RGBToColor(153, 238, 255, 255),
            },
            Rarity.Green: {
                "frame": Utils.RGBToColor(0, 255, 0, 125),
                "content": Utils.RGBToColor(0, 255, 0, 75),
                "text": Utils.RGBToColor(0, 255, 0, 255),
            },
            Rarity.Purple: {
                "frame": Utils.RGBToColor(187, 136, 238, 125),
                "content": Utils.RGBToColor(187, 136, 238, 75),
                "text": Utils.RGBToColor(187, 136, 238, 255),
            },
            Rarity.Gold: {
                "frame": Utils.RGBToColor(255, 204, 85, 125),
                "content": Utils.RGBToColor(255, 204, 85, 75),
                "text": Utils.RGBToColor(255, 204, 85, 255),
            },
        }

        if (rarity in rarity_colors):
            return rarity_colors[rarity]
        else:
            return {
                "frame": Utils.RGBToColor(255, 255, 255, 125),
                "content": Utils.RGBToColor(255, 255, 255, 75),
                "text": Utils.RGBToColor(255, 255, 255, 255),
            }

    @staticmethod
    def GetDyeColor(dye, alpha=255):
        dye_colors = {
            DyeColor.NoColor: Utils.RGBToColor(255, 255, 255, alpha),
            DyeColor.Gray: Utils.RGBToColor(51, 50, 46, alpha),
            DyeColor.Blue: Utils.RGBToColor(0, 42, 86, alpha),
            DyeColor.Yellow: Utils.RGBToColor(176, 113, 0, alpha),
            DyeColor.Green: Utils.RGBToColor(0, 92, 16, alpha),
            DyeColor.Brown: Utils.RGBToColor(67, 33, 13, alpha),
            DyeColor.Purple: Utils.RGBToColor(59, 13, 81, alpha),
            DyeColor.Pink: Utils.RGBToColor(255, 43, 107, alpha),
            DyeColor.Red: Utils.RGBToColor(166, 0, 0, alpha),
            DyeColor.Silver: Utils.RGBToColor(68, 74, 82, alpha),
            DyeColor.White: Utils.RGBToColor(175, 175, 175, alpha),
            DyeColor.Black: Utils.RGBToColor(15, 15, 15, alpha),
            DyeColor.Orange: Utils.RGBToColor(136, 56, 0, alpha),
        }

        if (dye in dye_colors):
            return dye_colors[dye]
        else:
            return Utils.RGBToColor(255, 255, 255, 125)
