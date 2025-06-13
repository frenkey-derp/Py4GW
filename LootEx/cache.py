from datetime import datetime
from PyItem import DyeInfo, ItemModifier, PyItem
from LootEx import data, models, settings, utility
from LootEx.data_collector import GLOBAL_CACHE
from LootEx.enum import ModifierIdentifier
from Py4GWCoreLib import ItemArray
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import Attribute, Console, DyeColor, ItemType, Rarity


class Cached_Item:
    def __init__(self, item_id: int, slot: int = -1):
        from LootEx import utility, settings, data, models, enum

        item = PyItem(item_id) if item_id > 0 else None

        self.id: int = item_id
        self.model_id: int = item.model_id if item else -1
        self.item_type: ItemType = ItemType(
            item.item_type.ToInt()) if item else ItemType.Unknown
        self.rarity: Rarity = Rarity(
            item.rarity.value) if item and item.rarity else Rarity.White

        self.is_identified: bool = item.is_identified if item else False
        self.value: int = item.value if item else 0
        self.is_salvageable: bool = item.is_salvageable if item else False
        self.is_inscribable: bool = item.is_inscribable if item else False
        self.quantity: int = item.quantity if item else 0
        self.is_stackable: bool = item.is_stackable if item else False
        self.is_customized: bool = item.is_customized if item else False
        self.dye_info: DyeInfo = item.dye_info if item else DyeInfo()

        self.is_weapon: bool = utility.Util.IsWeaponType(self.item_type)
        self.is_armor: bool = utility.Util.IsArmorType(self.item_type)
        self.is_upgrade: bool = self.item_type == ItemType.Rune_Mod
        self.is_rune: bool = False
        self.target_item_type: ItemType = ItemType.Unknown

        self.slot: int = item.slot if item else slot
        self.is_inventory_item: bool = item.is_inventory_item if item else False

        self.color: DyeColor = utility.Util.get_color_from_info(
            self.dye_info) if self.dye_info else DyeColor.NoColor

        self.shield_armor: tuple[int, int] = (0, 0)
        self.damage: tuple[int, int] = (0, 0)
        attribute, requirements = (Attribute.None_, 0)

        self.attribute: Attribute = attribute
        self.requirements: int = requirements

        self.material: models.Material | None = None
        if self.item_type == ItemType.Materials_Zcoins:
            if self.model_id in data.Materials:
                self.material = data.Materials[self.model_id]

        self.data: models.Item | None = data.Items.get_item(
            self.item_type, self.model_id) if self.model_id > -1 and self.item_type in data.Items else None
        self.model_name: str = self.data.name if self.data else "Unknown Item"
        self.config = settings.current.loot_profile.items.get_item_config(
            self.item_type, self.model_id) if settings.current.loot_profile and self.model_id > -1 else None
        self.is_blacklisted: bool = settings.current.loot_profile.is_blacklisted(
            self.item_type, self.model_id) if settings.current.loot_profile and self.model_id > -1 else False

        self.action: enum.ItemAction = enum.ItemAction.NONE
        self.savlage_tries: int = 0
        self.salvage_started: datetime | None = None
        self.salvage_requires_confirmation: bool = False
        self.salvage_option: enum.SalvageOption = enum.SalvageOption.None_

        self.has_mods: bool = False
        self.modifiers: list[ItemModifier] = item.modifiers if item else []

        self.mods: list[models.Rune | models.WeaponMod] = []
        self.runes: list[models.Rune] = []
        self.weapon_mods: list[models.WeaponMod] = []

        self.max_runes: list[models.Rune] = []
        self.max_weapon_mods: list[models.WeaponMod] = []
        self.is_highly_salvageable: bool = False
        self.has_increased_value: bool = False
        self.GetModsFromModifiers()

        pass

    def Update(self):
        item = PyItem(self.id)
        # self.quantity = item.quantity if item.is_inventory_item else 0
        # self.is_inventory_item = item.is_inventory_item
        pass

    def ExistsInCache(self, cache: list["Cached_Item"]) -> bool:
        item = next((item for item in cache if item.id == self.id), None)
        return item is not None and item.quantity >= self.quantity

    def ExistsInInventory(self) -> bool:
        if self.id <= 0:
            return False

        item = PyItem(self.id)
        return item.is_inventory_item

    def IsSalvaged(self) -> tuple[bool, int]:
        if self.id <= 0:
            return False, -1

        item = PyItem(self.id)
        salvaged = not item.is_inventory_item or item.quantity < self.quantity or item.model_id != self.model_id
        self.quantity = item.quantity if item.is_inventory_item else 0

        return salvaged, self.quantity

    def ExistsInBags(self, start_bag: Bag, end_bag: Bag | None = None) -> bool:
        if end_bag is None:
            end_bag = start_bag

        bags = GLOBAL_CACHE.Item.raw_item_array.get_bags(
            list(range(start_bag.value, end_bag.value + 1)))

        inventory: list[int] = GLOBAL_CACHE.ItemArray.GetItemArray(bags)

        item = inventory.index(self.id) if self.id in inventory else -1
        quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(
            self.id) if self.id else -1
        return item > -1 and quantity < self.quantity

    def ResetMods(self):
        self.mods = []
        self.runes = []
        self.weapon_mods = []
        self.has_mods = False
        self.max_runes = []
        self.max_weapon_mods = []
        self.is_highly_salvageable = False
        self.has_increased_value = False

    def GetModsFromModifiers(self):
        modifier_values: list[tuple[int, int, int]] = [
            (modifier.GetIdentifier(), modifier.GetArg1(), modifier.GetArg2())
            for modifier in self.modifiers if modifier is not None
        ]

        if not modifier_values:
            return

        for identifier, arg1, arg2 in modifier_values:
            if identifier is None or arg1 is None or arg2 is None:
                continue

            if identifier == ModifierIdentifier.TargetItemType:
                self.target_item_type = ItemType(
                    arg1) if arg1 is not None else ItemType.Unknown
                self.is_rune = arg1 == 0 and arg2 == 0 and self.is_upgrade

            if identifier == ModifierIdentifier.Damage:
                self.damage = (
                    arg1, arg2) if arg1 is not None and arg2 is not None else (0, 0)

            if identifier == ModifierIdentifier.Damage_NoReq:
                self.damage = (
                    arg1, arg2) if arg1 is not None and arg2 is not None else (0, 0)

            if identifier == ModifierIdentifier.ShieldArmor:
                self.shield_armor = (
                    arg1, arg2) if arg1 is not None and arg2 is not None else (0, 0)

            if identifier == ModifierIdentifier.Requirement:
                self.requirements = arg1 if arg1 is not None else 0
                self.attribute = Attribute(
                    arg2) if arg2 is not None else Attribute.None_
            
            if identifier == ModifierIdentifier.ImprovedVendorValue:
                self.has_increased_value = True
                
            if identifier == ModifierIdentifier.HighlySalvageable:
                self.is_highly_salvageable = True

        for identifier, arg1, arg2 in modifier_values:
            if self.is_armor or self.is_upgrade:
                for rune in data.Runes.values():
                    is_rune, is_max = rune.is_item_modifier(
                        identifier, arg1, arg2)

                    if is_max:
                        self.max_runes.append(rune)

                    if is_rune:
                        self.runes.append(rune)
                        break

            if self.is_weapon or self.is_upgrade:
                for weapon_mod in data.Weapon_Mods.values():
                    is_weapon_mod, is_max = weapon_mod.is_item_modifier(
                        identifier, arg1, arg2)
                    is_matching_type = any(utility.Util.IsMatchingItemType(self.target_item_type, target_item_type) for target_item_type in weapon_mod.target_types) if self.item_type == ItemType.Rune_Mod else any(
                        utility.Util.IsMatchingItemType(self.item_type, target_item_type) for target_item_type in weapon_mod.target_types)

                    if not is_matching_type:
                        continue

                    if is_max:
                        self.max_weapon_mods.append(weapon_mod)

                    if is_weapon_mod:
                        self.weapon_mods.append(weapon_mod)
                        break
        
        self.mods = self.runes + self.weapon_mods
        self.has_mods = bool(self.runes or self.weapon_mods)

    def GetModsX(self, tolerance: int = -1) -> tuple[list[models.Rune | models.WeaponMod], list[models.Rune], list[models.WeaponMod]]:
        if self.mods is None:
            if self.is_weapon or self.is_armor or self.item_type == ItemType.Rune_Mod:
                mods, runes, weapon_mods = utility.Util.GetMods(
                    self.id, tolerance)

                self.mods = mods
                self.runes = runes
                self.weapon_mods = weapon_mods
                self.is_highly_salvageable = any(
                    mod.identifier == "AQAmCAAeKA==" for mod in mods)
                self.has_increased_value = any(
                    mod.identifier == "AQAl-AAvKA==" for mod in mods)

                if settings.current.loot_profile is not None and settings.current.loot_profile.weapon_mods is not None:
                    self.max_runes = [
                        rune for rune in runes if rune.identifier in settings.current.loot_profile.runes and settings.current.loot_profile.runes[rune.identifier]
                    ]

                    self.max_weapon_mods = [
                        mod for mod in weapon_mods if mod.identifier in settings.current.loot_profile.weapon_mods and settings.current.loot_profile.weapon_mods[mod.identifier].get(self.item_type.name, False)
                    ]

        self.mods = self.mods or []
        self.runes = self.runes or []
        self.weapon_mods = self.weapon_mods or []

        return self.mods, self.runes, self.weapon_mods

    def HasModToKeep(self) -> tuple[bool, list[models.Rune], list[models.WeaponMod]]:
        return True if self.max_runes or self.max_weapon_mods else False, self.max_runes, self.max_weapon_mods

    def HasMods(self) -> bool:
        return self.has_mods
