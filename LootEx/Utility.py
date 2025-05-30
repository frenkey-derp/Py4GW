from typing import Dict, List, Optional, Tuple
from LootEx import data, item_configuration
from LootEx import models
from LootEx.enum import ModifierIdentifier, ModifierValueArg
from LootEx.item_actions import ItemAction
from LootEx.item_configuration import ItemConfiguration

import importlib

from LootEx.models import ModifierInfo, Rune, WeaponMod
from Py4GWCoreLib import GlobalCache, Item, Party, UIManager
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog, Utils
from Py4GWCoreLib.enums import Attribute, DamageType, ItemType, NumberPreference, Rarity, DyeColor, ServerLanguage

from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
importlib.reload(item_configuration)
importlib.reload(data)


class Util:    
    merchant_threshold = 10
    merchantwindow_coords : list[tuple[int, int, int, int]] = []
    
    @staticmethod
    def IsMerchantWindowOpen() -> bool:        
        return len(Util.merchantwindow_coords) == Util.merchant_threshold and all(coord == Util.merchantwindow_coords[0] for coord in Util.merchantwindow_coords)

    @staticmethod
    def UpdateMerchantWindowOpen():
        id = UIManager.GetFrameIDByHash(3613855137)
        
        if not UIManager.FrameExists(id):
            return
        
        if not UIManager.IsVisible(id):
            return
        
        left, top, right, bottom = UIManager.GetFrameCoords(id)
        Util.merchantwindow_coords.append((left, top, right, bottom))
        
        if len(Util.merchantwindow_coords) > Util.merchant_threshold:
            Util.merchantwindow_coords.pop(0)
        
        if len(Util.merchantwindow_coords) < Util.merchant_threshold:
            return
            
        if right > 10000:
            Util.merchantwindow_coords.clear()
            return


    @staticmethod
    def get_mod_mask(identifier: int, arg1: int, arg2: int) -> str:
        """
        Generate a 4-byte legacy mod representation based on Identifier, Arg1, and Arg2.

        Byte layout:
            Byte 0: Arg2
            Byte 1: Arg1
            Bytes 2–3: Identifier (little-endian)

        :param identifier: 16-bit mod identifier (0x0000 - 0xFFFF)
        :param arg1: 8-bit argument 1 (0x00 - 0xFF)
        :param arg2: 8-bit argument 2 (0x00 - 0xFF)
        :return: 4-byte legacy mod representation
        """
        if not (0 <= arg1 <= 0xFF):
            raise ValueError("Arg1 must be a byte (0-255)")
        if not (0 <= arg2 <= 0xFF):
            raise ValueError("Arg2 must be a byte (0-255)")
        if not (0 <= identifier <= 0xFFFF):
            raise ValueError("Identifier must be a 16-bit value (0-65535)")

        identifier_bytes = identifier.to_bytes(
            2, byteorder='little')  # Bytes 2–3
        result = bytearray(4)
        result[0] = arg2     # Byte 0
        result[1] = arg1     # Byte 1
        result[2] = identifier_bytes[0]  # Byte 2
        result[3] = identifier_bytes[1]  # Byte 3
        return bytes(result).hex().upper()

    # TODO: Add handling for non max mods
    @staticmethod
    def GetMods(item_id: int):
        item_type = ItemType[Item.GetItemType(item_id)[1]]
        mods = []

        is_rune = item_type == ItemType.Rune_Mod and GLOBAL_CACHE.Item.Customization.Modifiers.GetModifierValues(
            item_id, ModifierIdentifier.TargetItemType)[0] == 0

        # ConsoleLog("LootEx", f"Item ID: {item_id} - Item Type: {item_type}")
        modifiers = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(item_id)

        if Util.IsArmorType(item_type) or is_rune:
            matching_runes = [
                rune for rune in data.Runes if rune.is_item_modifier(modifiers)]
            mods.extend(matching_runes)

        elif Util.IsWeaponType(item_type) or item_type == ItemType.Rune_Mod:
            matching_mods = [
                weapon_mod for weapon_mod in data.Weapon_Mods.values() if weapon_mod.is_item_modifier(modifiers, item_type)]
            mods.extend(matching_mods)
            
        else:
            return []

        mods.sort(key=lambda x: x.mod_type, reverse=True)

        return mods

    @staticmethod
    def GetModFromRune_Mod(item_id: int):
        """
        Retrieves the weapon mod associated with a specific item ID if that item is a Rune or Mod.
        Args:
            item_id (int): The unique identifier of the item.
        Returns:
            Optional[WeaponMod]: The weapon mod associated with the item ID, 
            or None if no matching mod is found.
        """

        item_type = Item.GetItemType(item_id)

        if (item_type == ItemType.Rune_Mod):
            _, value, _ = Item.Customization.Modifiers.GetModifierValues(
                item_id, ModifierIdentifier.TargetItemType)
            target_item_type = ItemType(value) if value else None

            for mod in Item.Customization.Modifiers.GetModifiers(item_id):
                matching_mod = next((weapon_mod for weapon_mod in data.Weapon_Mods.values() if weapon_mod.is_item_modifier(
                    mod, target_item_type)), None)

                if matching_mod is not None:
                    matching_mod = next(
                        (weapon_mod for weapon_mod in data.Runes if weapon_mod.is_item_modifier(mod)), None)

                return matching_mod
        else:
            return None

    @staticmethod
    def GetWeaponModFromRune_Mod(item_id: int) -> Optional[WeaponMod]:
        """
        Retrieves the weapon mod associated with a specific item ID if that item is a Rune or Mod.
        Args:
            item_id (int): The unique identifier of the item.
        Returns:
            Optional[WeaponMod]: The weapon mod associated with the item ID, 
            or None if no matching mod is found.
        """

        item_type = Item.GetItemType(item_id)

        if (item_type == ItemType.Rune_Mod):
            _, value, _ = Item.Customization.Modifiers.GetModifierValues(
                item_id, ModifierIdentifier.TargetItemType)
            target_item_type = ItemType(value) if value else None

            for mod in Item.Customization.Modifiers.GetModifiers(item_id):
                matching_mod = next((weapon_mod for weapon_mod in data.Weapon_Mods.values() if weapon_mod.is_item_modifier(
                    mod, target_item_type)), None)
                return matching_mod
        else:
            return None

    @staticmethod
    def GetRuneFromRune_Mod(item_id: int) -> Optional[Rune]:
        """
        Retrieves the weapon mod associated with a specific item ID if that item is a Rune or Mod.
        Args:
            item_id (int): The unique identifier of the item.
        Returns:
            Optional[WeaponMod]: The weapon mod associated with the item ID, 
            or None if no matching mod is found.
        """

        item_type = Item.GetItemType(item_id)

        if (item_type == ItemType.Rune_Mod):
            for mod in Item.Customization.Modifiers.GetModifiers(item_id):
                matching_mod = next(
                    (weapon_mod for weapon_mod in data.Runes if weapon_mod.is_item_modifier(mod)), None)
                return matching_mod
        else:
            return None

    @staticmethod
    def GetItemRequirements(item_id: int) -> Optional[tuple[Attribute, int]]:
        """
        Retrieves the attribute and requirement level for a given item.
        Args:
            item_id (int): The unique identifier of the item.
        Returns:
            Optional[tuple[Attribute, int]]: A tuple containing the attribute 
            (as an `Attribute` object) and the requirement level (as an integer) 
            if the item has a requirement. Returns `None` if no requirements are found.
        """
        _, attribute_id, requirement = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifierValues(
            item_id, ModifierIdentifier.Requirement)

        if attribute_id == None or requirement == None:
            return None

        attribute = Attribute(attribute_id)
        return attribute, requirement

    @staticmethod
    def GetItemDamage(item_id: int) -> Optional[tuple[int, int]]:
        """
        Retrieves the minimum and maximum damage values for a given item.
        This method fetches the damage modifier values associated with the specified
        item ID. If no damage values are found, it returns None. Otherwise, it returns
        a tuple containing the minimum and maximum damage values, defaulting to 0 if
        either value is missing.
        Args:
            item_id (int): The unique identifier of the item.
        Returns:
            Optional[tuple[int, int]]: A tuple containing the minimum and maximum damage
            values, or None if no damage values are available.
        """
        _, max_damage, min_damage = Item.Customization.Modifiers.GetModifierValues(
            item_id, ModifierIdentifier.Damage)

        if max_damage == None and min_damage == None:
            return None

        return min_damage if min_damage else 0, max_damage if max_damage else 0

    @staticmethod
    def GetItemDamageType(item_id: int) -> Optional[DamageType]:
        """
        Retrieves the damage type associated with a specific item.

        Args:
            item_id (int): The unique identifier of the item.

        Returns:
            Optional[DamageType]: The damage type of the item if it exists, 
            otherwise None.
        """
        _, damage_type_id, _ = Item.Customization.Modifiers.GetModifierValues(
            item_id, ModifierIdentifier.DamageType)
        return DamageType(damage_type_id) if damage_type_id else None

    @staticmethod
    def GetShieldArmor(item_id: int) -> Optional[tuple[int, int]]:
        """
        Retrieves the armor value for a shield item.

        Args:
            item_id (int): The unique identifier of the item.

        Returns:
            Optional[int]: The armor value of the shield if it exists, otherwise None.
        """
        _, armor_at_or_above_requirement, armor_below_requirement = Item.Customization.Modifiers.GetModifierValues(
            item_id, ModifierIdentifier.ShieldArmor)

        if armor_at_or_above_requirement == None or armor_below_requirement == None:
            return None

        return armor_at_or_above_requirement, armor_below_requirement

    @staticmethod
    def GetAttributes(itemType: ItemType) -> list[Attribute]:
        if itemType in data.Item_Attributes:
            return data.Item_Attributes[itemType]
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
    def GetActionName(action: ItemAction) -> str:
        name = action.name

        # Split the name at underscores
        parts = name.split("_")

        # Capitalize the first letter of each part
        parts = [part.capitalize() for part in parts]

        # Join the parts back together with spaces
        name = ' '.join(parts)

        return name

    @staticmethod
    def GetMaxDamage(requirement: int, itemType: Optional[ItemType] = ItemType.Unknown) -> models.IntRange:
        requirement = 9 if requirement > 9 else requirement
        itemType = itemType if itemType != None else ItemType.Unknown

        return data.DamageRanges[itemType][requirement] if itemType in data.DamageRanges and requirement in data.DamageRanges[itemType] else models.IntRange(0, 0)

    @staticmethod
    def IsMaxDamage(damage_range: models.IntRange, requirement: int, itemType: ItemType = ItemType.Unknown, tollerance: models.IntRange = models.IntRange()) -> bool:
        max_damage = Util.GetMaxDamage(requirement, itemType)

        if max_damage.min == 0 and max_damage.max == 0:
            return False

        return damage_range.min == max_damage.min - tollerance.min and damage_range.max >= max_damage.max - tollerance.max

    @staticmethod
    def GetDataItem(model_id: int) -> Optional[models.Item]:
        dataitem = next(
            (data_item for data_item in data.Items.values() if model_id == data_item.model_id), None)
        return dataitem

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
    def IsArmor(item: ItemConfiguration) -> bool:
        dataitem = Util.GetDataItem(item.model_id)
        return Util.IsArmorType(dataitem.item_type) if dataitem is not None else False

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
    def IsWeapon(item: ItemConfiguration) -> bool:
        dataitem = Util.GetDataItem(item.model_id)
        return Util.IsWeaponType(dataitem.item_type) if dataitem is not None else False

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

    @staticmethod
    def GetWeaponModName(mod_identifier: str, refresh: bool = False) -> str:
        """
        Get the name of the weapon mod based on its hex representation.

        Args:
            mod_identifier (str): The hex representation of the weapon mod.

        Returns:
            str: The name of the weapon mod.
        """
        if not WeaponMod._mod_identifier_lookup or refresh:
            WeaponMod._mod_identifier_lookup = {
                mod.identifier: mod.full_name for mod in data.Weapon_Mods.values()
            }

        return WeaponMod._mod_identifier_lookup.get(mod_identifier, "Unknown Weapon Mod")

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
        return item_type1 == item_type2 or item_type1 in data.ItemType_MetaTypes.get(item_type2, [])

    @staticmethod
    def GetWeaponTypeFromAttribute(attribute: Attribute) -> ItemType:
        """
        Get the weapon type associated with a specific attribute.

        Args:
            attribute (Attribute): The attribute to check.

        Returns:
            ItemType: The associated weapon type, or ItemType.Unknown if not found.
        """
        for item_type, attributes in data.Item_Attributes.items():
            if attribute in attributes:
                return item_type

        return ItemType.Unknown

    @staticmethod
    def parse_modifier_from_hex(hex_str: str) -> List[ModifierInfo]:
        identifier = int(hex_str[0:4], 16)  # 0x21E8 = 8680
        arg = int(hex_str[4:8], 16)         # 0x0803 = 2051
        arg1, arg2 = ModifierInfo.unpack_arg(arg)

        return [
            ModifierInfo(
                identifier=identifier,
                arg1=arg1,
                arg2=arg2,
                modifier_value_arg=ModifierValueArg.Fixed,
            )
        ]
    
    @staticmethod
    def get_server_language():
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return server_language
    
    
    @staticmethod
    def is_inscription_item(item_name : str) -> bool:
        """
        Check if the item is an inscription item based on its name.

        Args:
            item_name (str): The name of the item.

        Returns:
            bool: True if the item is an inscription item, False otherwise.
        """
        patterns = {
            ServerLanguage.English: "Inscription: ",
            ServerLanguage.German: "Inschrift: ",
            ServerLanguage.French: "Inscription : ",
            ServerLanguage.Spanish: "Incripción: ",
            ServerLanguage.Italian: "Iscrizione: ",
            ServerLanguage.TraditionalChinese: "鑄印：",
            ServerLanguage.Japanese: "刻印：",
            ServerLanguage.Polish: "Inskrypcja: ",
            ServerLanguage.Russian: "Надпись: ",
            ServerLanguage.BorkBorkBork: "Inscreepshun: "
        }
            
        server_language = Util.get_server_language()
        pattern = patterns.get(server_language, "Inscription: ")
        return item_name.startswith(pattern) if pattern else False
    
    @staticmethod
    def is_inscription_model_item(model_id : int) -> bool:
        """
        Check if the item is an inscription item based on its model ID.

        Args:
            model_id (int): The model ID of the item.

        Returns:
            bool: True if the item is an inscription item, False otherwise.
        """
        model_ids = [
            15540,
            15541,
            15542,
            19122,
            19123,
            17059,
        ]

        return model_id in model_ids
    
    @staticmethod
    def is_missing_item(item_id: int) -> bool:
        model_id = Item.GetModelID(item_id)
        
        return data.Items.get(model_id) is None
    
    @staticmethod
    def has_missing_mods(item_id : int) -> bool:
        mods = Util.GetMods(item_id)
        
        if not mods or len(mods) == 0:
            return False
        
        for mod in mods:
            if mod.names is None or len(mod.names) == 0:
                return True
            
            for lang in ServerLanguage:
                if lang not in mod.names or mod.names[lang] is None or mod.names[lang] == "":
                    return True
        
        return False
    
    @staticmethod
    def get_target_item_type_from_mod(item_id: int) -> Optional[ItemType]:
        """
        Get the target item type from a rune mod item.

        Args:
            item_id (int): The unique identifier of the rune mod item.

        Returns:
            Optional[ItemType]: The target item type if found, otherwise None.
        """
        _, value, _ = Item.Customization.Modifiers.GetModifierValues(
            item_id, ModifierIdentifier.TargetItemType)
        
        return ItemType(value) if value else None