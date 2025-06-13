from datetime import date, timedelta
from LootEx.cache import Cached_Item
from LootEx.enum import ModType, SalvageKitOption, SalvageOption, ItemAction
from Py4GWCoreLib import *
from LootEx import data, data_collector, models, settings, utility, ui_manager_extensions, loot_filter, item_configuration

import importlib

importlib.reload(item_configuration)
importlib.reload(loot_filter)
importlib.reload(settings)
importlib.reload(ui_manager_extensions)

# TODO: Collect salvage data for items, so we can make better decisions on what to salvage and what not to salvage.

salvagetime_results = []
actiontime_results = []
identifytime_results = []
merhcant_time_results = []
actiontime_results = []
time_results = []


class LootHandler:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(LootHandler, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self, reset: bool = False):
        if self._initialized and not reset:
            return

        self._initialized = True
        self.run_once = False

        self.inventory_changed: bool = False
        self.deposited = False
        self.capacity_checked = False
        self.material_capacity = 2500

        # Initialize timers and action queues
        self.salvage_timer = ThrottledTimer(750)
        self.identification_timer = ThrottledTimer(500)
        self.merchant_timer = ThrottledTimer(1000)
        self.deposit_timer = ThrottledTimer(5000)
        self.inventory_timer = ThrottledTimer(250)
        self.compact_inventory_timer = ThrottledTimer(250)

        self.salvage_action_queue = ActionQueueNode(150)
        self.inventory_array: list[int] | None = []
        self.inventory_sizes: dict[Bag, int] | None = {}
        self.inventory_materials: list[Cached_Item] = []
        self.material_storage: list[tuple[int, int]] | None = []
        self.item_storage: list[tuple[int, ItemType, int, int]] | None = []

        self.empty_slots: int = -1
        self.id_kit: int = -1
        self.remaining_uses: int = -1
        self.cached_inventory: list[Cached_Item] = []

        self.merchant_open: bool | None = False
        self.checked_storage_for_merchant_items: bool = False

        self.salvage_queue: list[Cached_Item] = []
        self.salvaged = False
        self.salvage_windows_updated: bool = False
        self.salvaging_item: Cached_Item | None = None
        self.salvage_option: SalvageOption = SalvageOption.None_
        self.salvage_requires_confirmation: bool = False
        self.is_confirm_materials_window_open: bool = False
        self.is_salvage_window_open: bool = False
        self.upgrade_open: bool | None = False

    def soft_reset(self):
        self.empty_slots: int = -1
        self.id_kit = -1
        self.remaining_uses = -1
        self.merchant_open = None
        self.salvaged = False
        self.inventory_array = None
        self.item_storage = None
        self.inventory_materials = []
        self.material_storage = None
        self.salvage_windows_updated = False
        # self.salvaging_item = None

    def reset(self):
        self.ResetSalvageWindow()
        self.__init__(reset=True)
        self.SetPollingInterval(
            settings.current.loot_profile.polling_interval if settings.current.loot_profile else 1)

    def SetPollingInterval(self, interval: float):
        self.inventory_timer.SetThrottleTime(interval * 1000)

    def GetMaterialStorage(self) -> list[tuple[int, int]]:
        if self.material_storage is None:
            material_storage, _ = utility.Util.GetZeroFilledBags(
                Bag.Material_Storage, Bag.Material_Storage)
            self.material_storage = [
                (item_id, 0)
                for item_id in material_storage
            ]

        return self.material_storage

    def GetInventoryArray(self) -> list[int]:
        if self.inventory_array is None:
            inventory, inventory_sizes = utility.Util.GetZeroFilledBags(
                Bag.Backpack, Bag.Bag_2)
            self.inventory_array = inventory
            self.inventory_sizes = inventory_sizes

        return self.inventory_array

    def GetItemStorage(self) -> Tuple[list[tuple[int, ItemType, int, int]], list[tuple[int, ItemType, int, int]]]:
        """Get the item storage, which is a list of tuples containing item_id, ItemType, model_id and quantity.
        The list is sorted by item_id, with empty slots (item_id == 0) at the end.

        Returns:
            list[tuple[int, int, int]]: A list of tuples containing item_id, ItemType, model_id and quantity.
        """

        if self.item_storage is None:
            storage, _ = utility.Util.GetZeroFilledBags(
                Bag.Storage_1, Bag.Storage_14)
            self.item_storage = [
                (item_id, ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0]), GLOBAL_CACHE.Item.GetModelID(
                    item_id), GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))
                for item_id in storage
            ]

        sorted = self.item_storage.copy()
        sorted.sort(key=lambda x: (
            x[0] == 0,  # Ensure empty slots are at the end
            x[1],  # Sort by ItemType
            x[2],  # Then by model_id
            -x[3]  # Then by quantity in descending order
        ), reverse=False)

        return self.item_storage, sorted

    def ResetSalvageWindow(self):
        if ui_manager_extensions.UIManagerExtensions.IsSalvageWindowOpen():
            ui_manager_extensions.UIManagerExtensions.CancelSalvageOption()

        elif ui_manager_extensions.UIManagerExtensions.IsConfirmMaterialsWindowOpen():
            ui_manager_extensions.UIManagerExtensions.CancelLesserSalvage()

    def GetSalvageOption(self, item: Cached_Item) -> Optional[SalvageOption]:
        if item.action == ItemAction.SALVAGE_SMART:
            if item.data is None:
                return None

            common_salvage = (item.data.common_salvage.get_average_value(
                item.is_highly_salvageable) if item.data.common_salvage else 0) - 4
            rare_salvage = ((item.data.rare_salvage.get_average_value(
                item.is_highly_salvageable) if item.data.rare_salvage else 0) + common_salvage) - 12
            rare_salvage = rare_salvage / \
                max(1, len(item.data.rare_salvage) +
                    len(item.data.common_salvage))

            # multiplier = 1.5
            # if item.value >= rare_salvage * multiplier and item.value >= common_salvage * multiplier:
            #     return None
            # else:
            return SalvageOption.LesserCraftingMaterials if common_salvage > rare_salvage else SalvageOption.RareCraftingMaterials
        else:
            match item.action:
                case ItemAction.SALVAGE_COMMON_MATERIALS:
                    return SalvageOption.LesserCraftingMaterials

                case ItemAction.SALVAGE_RARE_MATERIALS:
                    return SalvageOption.RareCraftingMaterials

                case _:
                    return SalvageOption.None_

    def IsVial_Of_DyeToKeep(self, item: Cached_Item) -> bool:
        lootprofile = settings.current.loot_profile

        if lootprofile is None:
            return False

        if item.model_id == ModelID.Vial_Of_Dye:
            if item.dye_info is not None:
                color_id = item.dye_info.dye1.ToInt() if item.dye_info.dye1 else -1
                color = DyeColor(color_id) if color_id != -1 else None
                if color is not None and color in lootprofile.dyes:
                    return lootprofile.dyes[color]

        return False

    def GetSalvageKit(self, option: SalvageKitOption = SalvageKitOption.Lesser) -> int:
        if option == SalvageKitOption.Lesser:
            return GLOBAL_CACHE.Inventory.GetFirstSalvageKit(True)

        if option == SalvageKitOption.LesserOrExpert:
            salvage_kit = GLOBAL_CACHE.Inventory.GetFirstSalvageKit(True)
            return GLOBAL_CACHE.Inventory.GetFirstSalvageKit(False) if salvage_kit == 0 else salvage_kit

        if option == SalvageKitOption.Expert:
            item_array = GLOBAL_CACHE.ItemArray.GetItemArray(
                [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2])

            for item_id in item_array:
                if GLOBAL_CACHE.Item.Usage.IsExpertSalvageKit(item_id):
                    return item_id

        if option == SalvageKitOption.Perfect:
            item_array = GLOBAL_CACHE.ItemArray.GetItemArray(
                [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2])

            for item_id in item_array:
                if GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Perfect_Salvage_Kit:
                    return item_id

        return 0

    def GetSalvageKitOption(self, option: SalvageOption) -> SalvageKitOption:
        match option:
            case SalvageOption.Prefix:
                return SalvageKitOption.Expert

            case SalvageOption.Suffix:
                return SalvageKitOption.Expert

            case SalvageOption.Inherent:
                return SalvageKitOption.Expert

            case SalvageOption.LesserCraftingMaterials:
                return SalvageKitOption.Lesser

            case SalvageOption.RareCraftingMaterials:
                return SalvageKitOption.Expert

            case _:
                # Default to Lesser or Expert for any other option which implies crafting materials
                return SalvageKitOption.LesserOrExpert

    def SalvageItem(self, item: Cached_Item, option: SalvageOption = SalvageOption.LesserCraftingMaterials):

        if item.id <= 0:
            return False

        if option is SalvageOption.None_:
            return False

        if not item.is_salvageable:
            return False

        salvage_kit = self.GetSalvageKit(self.GetSalvageKitOption(option))

        if salvage_kit == 0:
            ConsoleLog("LootEx", "No salvage kit found, cannot salvage item.",
                       Console.MessageType.Warning)
            return False

        ConsoleLog(
            "LootEx", f"Salvaging item: '{item.model_name}' ({item.id}) using kit {utility.Util.GetItemDataName(salvage_kit)} {salvage_kit}", Console.MessageType.Info)
        Inventory.SalvageItem(item.id, salvage_kit)

        rarity_requires_confirmation = item.rarity >= Rarity.Blue
        mods_require_confirmation = item.has_mods and option is not SalvageOption.LesserCraftingMaterials

        self.salvaged = True
        self.salvaging_item = item
        self.salvage_timer.Reset()
        self.salvage_requires_confirmation = mods_require_confirmation or rarity_requires_confirmation

        # if self.salvage_requires_confirmation:
        #     self.ConfirmSalvage(item, option)

        return True

    def CanSalvage(self) -> bool:
        return not self.salvage_requires_confirmation and (self.salvaging_item is None or not self.salvaging_item.ExistsInCache(self.cached_inventory)) and not self.is_confirm_materials_window_open and not self.is_salvage_window_open

    def ResetSalvageConfirmation(self):
        # self.salvage_requires_confirmation = False
        pass

    def ConfirmSalvage(self, item: Cached_Item, option: SalvageOption = SalvageOption.LesserCraftingMaterials) -> bool:
        self.salvage_action_queue.add_action(lambda: True)
        self.salvage_action_queue.add_action(
            self._SendConfirmSalvage, item, option)

        # salvage_action_queue.add_action(lambda : True)
        # self.salvage_action_queue.add_action(self.ResetSalvageConfirmation)

        return True

    def _SendConfirmSalvage(self, item: Cached_Item, option: SalvageOption = SalvageOption.LesserCraftingMaterials) -> bool:
        if option is not SalvageOption.LesserCraftingMaterials:
            if self.is_salvage_window_open:
                ConsoleLog(
                    "LootEx", f"Confirming salvage option: {option.name} for {item.model_name}", Console.MessageType.Info)
                ui_manager_extensions.UIManagerExtensions.SelectSalvageOptionAndSalvage(
                    option)
                self.salvage_requires_confirmation = False
                return True
        else:
            if self.is_confirm_materials_window_open:
                ConsoleLog(
                    "LootEx", f"Confirming lesser salvage for item: {item.model_name}", Console.MessageType.Info)
                ui_manager_extensions.UIManagerExtensions.ConfirmLesserSalvage()
                self.salvage_requires_confirmation = False
            return True

        return False

    def ExtractWantedMods(self, item: Cached_Item) -> bool:
        if item.id == 0:
            return False

        if not item.is_salvageable:
            ConsoleLog("LootEx", f"Item '{item.model_name}' ({item.id}) is not salvageable, cannot extract mods.",
                       Console.MessageType.Warning)
            return False

        salvage_kit = self.GetSalvageKit(SalvageKitOption.Expert)

        if salvage_kit == 0:
            ConsoleLog("LootEx", "No expert salvage kit found, cannot extract mods.",
                       Console.MessageType.Warning)
            return False

        _, mods, runes = self.HasModToKeep(item)

        if not mods and not runes:
            return False

        mod_to_extract: Optional[models.ItemMod] = None

        if mods:
            mod_to_extract = mods[0]
        else:
            mod_to_extract = runes[0]

        ConsoleLog(
            "LootEx", f"Extracting '{mod_to_extract.name}' from item: '{item.model_name}' ({item.id}) using kit {utility.Util.GetItemDataName(salvage_kit)} {salvage_kit}", Console.MessageType.Info)
        Inventory.SalvageItem(item.id, salvage_kit)

        self.salvaged = True
        self.salvaging_item = item
        self.salvage_requires_confirmation = True
        self.salvage_option = utility.Util.GetSalvageOptionFromModType(
            mod_to_extract.mod_type)

        # self.ConfirmSalvage(
        #     item, utility.Util.GetSalvageOptionFromModType(mod_to_extract.mod_type))

        return True

    def __Get_Empty_Storage_Slot(self, stash: list[tuple[int, ItemType, int, int]]) -> tuple[int, int, int]:
        for index, (id, _, _, _) in enumerate(stash):
            if id == 0:
                return index, Bag.Storage_1.value + math.floor(index / 25), index % 25

        return -1, -1, -1

    def __Move_Item_To_Empty_Slot(self, stash: list[tuple[int, ItemType, int, int]], item: Cached_Item, amount):
        if amount > 0:
            index, storage_index, storage_slot = self.__Get_Empty_Storage_Slot(
                stash)

            if index == -1:
                ConsoleLog(
                    "LootEx", "No empty slot found in stash, cannot stash item.", Console.MessageType.Warning)
                return False

            move_amount = min(250, amount)

            ConsoleLog(
                "LootEx", f"Stashing item {move_amount} '{item.model_name}' {item.id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)

            stash[index] = (item.id, item.item_type,
                            item.model_id, move_amount)
            Inventory.MoveItem(item.id, storage_index,
                               storage_slot, move_amount)

    def StashItem(self, item: Cached_Item) -> bool:
        if not settings.current.loot_profile:
            return False

        stash, sorted_stash = self.GetItemStorage()

        if item.is_stackable:
            config_condition = item.config.get_condition(
                item) if item.config else None
            keep_amount = config_condition.keep_in_inventory if config_condition else 0

            amount = item.quantity - keep_amount

            for e in sorted_stash:
                slot = stash.index(e)
                id, item_type, model_id, quantity = e

                storage_index = Bag.Storage_1.value + math.floor(slot / 25)
                storage_slot = slot % 25

                if id == 0:
                    continue

                if model_id == item.model_id:
                    slot_quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(
                        id)

                    if slot_quantity == 250:
                        continue

                    if model_id == ModelID.Vial_Of_Dye:
                        if utility.Util.get_color(id) == item.color:
                            move_amount = min(250 - slot_quantity, amount)
                            ConsoleLog(
                                "LootEx", f"Stashing item  {move_amount} '{item.model_name}' {item.id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)
                            Inventory.MoveItem(
                                item.id, storage_index, storage_slot, move_amount)
                            amount -= move_amount

                            if amount <= 0:
                                break

                    else:
                        move_amount = min(250 - slot_quantity, amount)
                        ConsoleLog(
                            "LootEx", f"Stashing item {move_amount}'{item.model_name}' {item.id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)
                        Inventory.MoveItem(
                            item.id, storage_index, storage_slot, move_amount)
                        amount -= move_amount

                        if amount <= 0:
                            break

            # If we still have items left to stash, find an empty slot
            if amount > 0:
                self.__Move_Item_To_Empty_Slot(stash, item, amount)

        else:
            # Move item to an empty slot
            self.__Move_Item_To_Empty_Slot(stash, item, item.quantity)

        return True

    def TrackTime(self, time_delta: timedelta, action_times: list[timedelta], name="Action"):
        action_times.append(time_delta)

        if len(action_times) > 100:
            action_times.pop(0)

        average_time = sum(action_times, timedelta()) / len(action_times)
        # ConsoleLog(f"LootEx [{name}]", f"Current: {time_delta.microseconds * 0.000001} sec | Average processing time: {average_time.microseconds * 0.000001} sec. | {len(action_times)} entries", Console.MessageType.Debug)

    def GetItemsFromStorage(self, items: dict[int, tuple[ItemType, int]], force: bool = False) -> bool:
        withdrawn_items = False
        if not force and self.checked_storage_for_merchant_items:
            return False

        if not items:
            ConsoleLog("LootEx", "No items to withdraw from storage.",
                       Console.MessageType.Warning)
            return False

        if not self.cached_inventory:
            ConsoleLog("LootEx", "No cached inventory available, cannot withdraw items from storage.",
                       Console.MessageType.Warning)
            return False

        _, sorted_storage = self.GetItemStorage()

        for model_id, (item_type, quantity) in items.items():
            # find a matching item in the sorted_storage
            storage_item_id = next(
                (item[0] for item in sorted_storage if item[2] == model_id and item[1] == item_type), 0)

            if not storage_item_id:
                continue

            occupies_slot = True

            # get slot from the self.cached_inventory for the first item that has id == 0
            inventory_slot = next(
                (index for index, item in enumerate(self.cached_inventory) if item.id == 0), None)

            if GLOBAL_CACHE.Item.Customization.IsStackable(storage_item_id):
                existing_slot = next(
                    (index for index, item in enumerate(self.cached_inventory) if item.item_type == item_type and item.quantity < 250), None)

                if existing_slot:
                    inventory_slot = existing_slot
                    occupies_slot = False

            if inventory_slot is None:
                continue

            if self.inventory_sizes is None:
                return False

            bag, slot = self.GetBagFromSlot(
                inventory_slot, self.inventory_sizes)
            item_data = data.Items.get_item_data(storage_item_id)
            item_name = item_data.name if item_data else "Item Name Unavailable"

            if occupies_slot:
                self.cached_inventory[inventory_slot] = Cached_Item(
                    storage_item_id, inventory_slot)

            else:
                self.cached_inventory[inventory_slot].quantity += quantity

            ConsoleLog(
                "LootEx", f"Withdrawing {quantity}x '{item_name}' ({storage_item_id})", Console.MessageType.Info)
            Inventory.MoveItem(storage_item_id, bag.value, slot, quantity)
            withdrawn_items = True

        self.checked_storage_for_merchant_items = True
        return withdrawn_items

    def CompactStash(self) -> bool:
        return self.CondenseStacks(Bag.Storage_1, Bag.Storage_14) or self.SortBags(Bag.Storage_1, Bag.Storage_10)

    def GetBagFromSlot(self, slot: int, bag_sizes: dict[Bag, int]) -> tuple[Bag, int]:
        offset = 0

        for bag, size in bag_sizes.items():
            if slot < offset + size:
                return bag, slot - offset
            offset += size

        return Bag.NoBag, -1

    def CondenseStacks(self, bag_start: Bag, bag_end: Bag) -> bool:
        if bag_end.value < bag_start.value:
            return False

        class SlotInfo:
            def __init__(self, item_id: int, bag: Bag, slot: int):
                self.item_id = item_id
                self.bag = bag
                self.slot = slot
                self.model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
                self.item_type = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[
                                          0]) if item_id else ItemType.Unknown
                self.stackable = GLOBAL_CACHE.Item.Customization.IsStackable(
                    item_id)
                self.quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(
                    item_id)
                self.color = utility.Util.get_color(item_id)

        item_array, bag_sizes = utility.Util.GetZeroFilledBags(
            bag_start, bag_end)

        slot_infos = [
            SlotInfo(item_id, bag, local_slot)
            for index, item_id in enumerate(item_array)
            for bag, local_slot in [self.GetBagFromSlot(index, bag_sizes)]
            if item_id > 0 and GLOBAL_CACHE.Item.Customization.IsStackable(item_id) and (GLOBAL_CACHE.Item.Properties.GetQuantity(item_id) > 0 < 250)
        ]

        condensed = False
        slot_infos.sort(key=lambda x: (
            x.model_id, x.quantity, x.bag.value, x.slot))

        lookup: dict[ItemType, dict[int, list[SlotInfo]]] = {}
        for slot_info in slot_infos:
            if slot_info.item_type not in lookup:
                lookup[slot_info.item_type] = {}

            if slot_info.model_id not in lookup[slot_info.item_type]:
                lookup[slot_info.item_type][slot_info.model_id] = []

            lookup[slot_info.item_type][slot_info.model_id].append(slot_info)
            lookup[slot_info.item_type][slot_info.model_id].sort(
                key=lambda x: x.quantity, reverse=True)

        # sort the slot_infos in lookup by quantity

        for slot_info in slot_infos:
            if slot_info.stackable and slot_info.quantity < 250:
                for next_slot_info in lookup[slot_info.item_type][slot_info.model_id]:
                    if next_slot_info.item_id == slot_info.item_id or next_slot_info.item_id == 0:
                        continue

                    if next_slot_info.quantity >= 250:
                        continue

                    if next_slot_info.bag == slot_info.bag and next_slot_info.slot == slot_info.slot:
                        continue

                    # Check if the next slot info is not the same item
                    if next_slot_info.item_id != slot_info.item_id:
                        move_amount = min(
                            250 - next_slot_info.quantity, slot_info.quantity)
                        next_slot_info.quantity += move_amount
                        slot_info.quantity -= move_amount

                        Inventory.MoveItem(
                            slot_info.item_id, next_slot_info.bag.value, next_slot_info.slot, move_amount)
                        condensed = True

                        if slot_info.quantity <= 0:
                            slot_info.item_id = 0
                            break

        return condensed

    def CompactInventory(self) -> bool:
        return self.CondenseStacks(Bag.Backpack, Bag.Bag_2) or self.SortBags(Bag.Backpack, Bag.Bag_2)

    def SortBags(self, bag_start: Bag, bag_end: Bag) -> bool:
        if bag_end.value < bag_start.value:
            return False

        # Sort the inventory and comapct it
        # We sort in the following order:
        item_typeOrder = [
            int(ItemType.Kit),
            int(ItemType.Key),
            int(ItemType.Usable),
            int(ItemType.Trophy),
            int(ItemType.Quest_Item),
            int(ItemType.Materials_Zcoins)
        ]

        # then everything else
        item_typeOrder += [int(item)
                           for item in ItemType if int(item) not in item_typeOrder]

        item_array, bag_sizes = utility.Util.GetZeroFilledBags(
            bag_start, bag_end)

        desired_item_array = sorted(
            item_array,
            key=lambda item_id: (
                item_id == 0,
                item_typeOrder.index(
                    GLOBAL_CACHE.Item.GetItemType(item_id)[0]),
                - GLOBAL_CACHE.Item.Properties.GetValue(item_id),
                GLOBAL_CACHE.Item.GetModelID(item_id),
                -GLOBAL_CACHE.Item.Properties.GetQuantity(item_id),
                item_id
            )
        )

        for target_slot, item_id in enumerate(desired_item_array):
            if item_id == 0:
                continue

            if target_slot is not None:
                bag, slot = self.GetBagFromSlot(target_slot, bag_sizes)

                Inventory.MoveItem(item_id, bag.value, slot,
                                   GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))

        return False

    def HasModToKeep(self, item: Cached_Item) -> tuple[bool, list[models.WeaponMod], list[models.Rune]]:
        runes_to_keep: list[models.Rune] = []
        mods_to_keep: list[models.WeaponMod] = []

        if settings.current.loot_profile is not None and settings.current.loot_profile.weapon_mods is not None:

            for rune in item.max_runes:
                if rune.identifier in settings.current.loot_profile.runes:
                    if settings.current.loot_profile.runes[rune.identifier]:
                        runes_to_keep.append(rune)

            for mod in item.max_weapon_mods:
                if mod.identifier in settings.current.loot_profile.weapon_mods:
                    if settings.current.loot_profile.weapon_mods[mod.identifier].get(item.item_type.name, False):
                        mods_to_keep.append(mod)

        return True if runes_to_keep or mods_to_keep else False, mods_to_keep, runes_to_keep

    def CanProcessItem(self, item: Cached_Item) -> bool:
        if settings.current.loot_profile and settings.current.loot_profile.is_blacklisted(item.item_type, item.model_id):
            return False

        # Item is customized, do not process it
        if item.is_customized:
            return False

        return True

    def GetMissingItems(self) -> dict[int, tuple[ItemType, int]]:
        if settings.current.loot_profile is None:
            return {}

        missing_items: dict[int, tuple[ItemType, int]] = {}

        if settings.current.loot_profile.identification_kits > 0:
            identificationKits = Inventory.GetModelCount(
                ModelID.Superior_Identification_Kit)
            identificationKits += Inventory.GetModelCount(
                ModelID.Identification_Kit)
            if identificationKits < settings.current.loot_profile.identification_kits:
                missing_items[ModelID.Superior_Identification_Kit] = (
                    ItemType.Kit, settings.current.loot_profile.identification_kits - identificationKits)

        if settings.current.loot_profile.salvage_kits > 0:
            salvageKits = Inventory.GetModelCount(ModelID.Salvage_Kit)
            if salvageKits < settings.current.loot_profile.salvage_kits:
                missing_items[ModelID.Salvage_Kit] = (
                    ItemType.Kit, settings.current.loot_profile.salvage_kits - salvageKits)

        if settings.current.loot_profile.expert_salvage_kits > 0:
            expertSalvageKits = Inventory.GetModelCount(
                ModelID.Expert_Salvage_Kit)
            expertSalvageKits += Inventory.GetModelCount(
                ModelID.Superior_Salvage_Kit)
            if expertSalvageKits < settings.current.loot_profile.expert_salvage_kits:
                missing_items[ModelID.Expert_Salvage_Kit] = (
                    ItemType.Kit, settings.current.loot_profile.expert_salvage_kits - expertSalvageKits)

        if settings.current.loot_profile.lockpicks > 0:
            lockpicks = Inventory.GetModelCount(ModelID.Lockpick)
            if lockpicks < settings.current.loot_profile.lockpicks:
                missing_items[ModelID.Lockpick] = (
                    ItemType.Key, settings.current.loot_profile.lockpicks - lockpicks)

        return missing_items

    def BuyItemsFromMerchant(self, items_to_buy: dict[int, tuple[ItemType, int]]):
        if not ui_manager_extensions.UIManagerExtensions.IsMerchantWindowOpen():
            ConsoleLog("LootEx", "Merchant window is not open, cannot buy items.",
                       Console.MessageType.Warning)
            return

        merchant_item_list = Trading.Merchant.GetOfferedItems()
        gold_on_character = Inventory.GetGoldOnCharacter()

        for model_id, (item_type, amount) in items_to_buy.items():
            item_id = next((
                item for item in merchant_item_list if GLOBAL_CACHE.Item.GetModelID(item) == model_id and GLOBAL_CACHE.Item.GetItemType(item)[0] == item_type.value), None)

            if item_id is None:
                continue

            value = GLOBAL_CACHE.Item.Properties.GetValue(item_id) * 2
            item_data = data.Items.get_item_data(item_id)
            item_name = item_data.name if item_data else "Item Name Unavailable"
            ConsoleLog(
                "LootEx", f"Buying {amount}x '{item_name}' ({item_id}) from merchant for {utility.Util.format_currency(value * amount)}.", Console.MessageType.Info)

            for i in range(amount):
                if value <= gold_on_character:
                    gold_on_character -= value
                    Trading.Merchant.BuyItem(item_id, value)

                if gold_on_character <= 0:
                    break

            if gold_on_character <= 0:
                break

    def DepositMaterial(self, item: Cached_Item) -> bool:
        if not self.material_capacity:
            return False

        if not item.material:
            return False

        material_storage = self.GetMaterialStorage()
        material_item_id, material_amount = material_storage[item.material.material_storage_slot]

        if material_item_id > 0 and material_amount == 0:
            material_storage[item.material.material_storage_slot] = (
                material_item_id, GLOBAL_CACHE.Item.Properties.GetQuantity(material_item_id))
            material_item_id, material_amount = material_storage[item.material.material_storage_slot]

        max_move_amount = self.material_capacity - material_amount
        move_amount = min(
            max_move_amount, item.quantity)

        if move_amount <= 0:
            return False

        material_storage[item.material.material_storage_slot] = (
            material_item_id, material_amount + move_amount)

        # ConsoleLog(
        #     "LootEx", f"Depositing item {move_amount}x '{item.material.name}' ({item.id}) to material storage.", Console.MessageType.Info)
        Inventory.MoveItem(item.id, Bags.MaterialStorage,
                           item.material.material_storage_slot, move_amount)

        return False

    def UpdateSalvageWindows(self):
        if not self.salvage_windows_updated:
            self.is_salvage_window_open = ui_manager_extensions.UIManagerExtensions.IsSalvageWindowOpen()
            self.is_confirm_materials_window_open = ui_manager_extensions.UIManagerExtensions.IsConfirmMaterialsWindowOpen()
            self.salvage_windows_updated = True

    def IsSalvageAction(self, action: ItemAction) -> bool:
        return action in (ItemAction.SALVAGE_COMMON_MATERIALS, ItemAction.SALVAGE_RARE_MATERIALS, ItemAction.SALVAGE_SMART, ItemAction.SALVAGE_MODS, ItemAction.SALVAGE)

    # TODO: Implement the salvage queue processing logic
    def ProcessSalvageList(self):
        salvage_item = self.salvage_queue[0] if self.salvage_queue else None
        if salvage_item is None:
            return

        salvaged, remaining = salvage_item.IsSalvaged()

        if salvaged:
            if remaining <= 0:
                ConsoleLog(
                    f"LootEx", f"Salvaged {salvage_item.model_name}!", Console.MessageType.Debug)
                self.salvage_queue.pop(0)  # Remove the item from the queue
                salvage_item.salvage_started = None
                self.inventory_changed = True                
                return True

            else:
                ConsoleLog(
                    f"LootEx", f"Salvaged {salvage_item.model_name}, but still has {remaining} remaining.", Console.MessageType.Debug)
                salvage_item.salvage_started = None
                return False

        elif not salvage_item.salvage_started:
            kit = self.GetSalvageKit(
                self.GetSalvageKitOption(salvage_item.salvage_option))

            if kit == 0:
                ConsoleLog(
                    "LootEx", "No salvage kit found, cannot salvage item.", Console.MessageType.Warning)
                return False

            salvage_item.salvage_started = datetime.now()  # ✅ Correct object here
            Inventory.SalvageItem(salvage_item.id, kit)
            ConsoleLog(
                "LootEx", f"Started salvaging on {salvage_item.quantity} {salvage_item.model_name} with kit {kit} with salvage option {salvage_item.salvage_option.name}", Console.MessageType.Debug)
            return True

        elif salvage_item.salvage_started:
            time_since_salvage = datetime.now() - (salvage_item.salvage_started or datetime.now())

            if time_since_salvage.total_seconds() > 10:
                ConsoleLog(
                    "LootEx", f"Salvage operation for {salvage_item.model_name} has timed out after {time_since_salvage.total_seconds()} seconds.", Console.MessageType.Warning)
                self.ResetSalvageWindow()
                salvage_item.salvage_started = None

                if salvage_item.savlage_tries >= 3:
                    self.salvage_queue.remove(salvage_item)
                    return False

                return True

            if salvage_item.salvage_requires_confirmation:
                self.UpdateSalvageWindows()

                match salvage_item.salvage_option:
                    case SalvageOption.LesserCraftingMaterials:
                        if self.is_confirm_materials_window_open:  
                            ConsoleLog(
                                "LootEx", f"Confirming lesser salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name}", Console.MessageType.Info)
                            
                            ui_manager_extensions.UIManagerExtensions.ConfirmLesserSalvage()
                            # salvage_item.salvage_requires_confirmation = False
                            return True

                    case SalvageOption.RareCraftingMaterials | SalvageOption.Prefix | SalvageOption.Suffix | SalvageOption.Inherent:
                        if self.is_salvage_window_open:                  
                            if salvage_item.salvage_option == SalvageOption.Prefix:
                                prefix = None
                                
                                if salvage_item.is_weapon:
                                    prefix = next(
                                        (mod for mod in salvage_item.max_weapon_mods if mod.mod_type == ModType.Prefix), None)
                                elif salvage_item.is_armor:
                                    prefix = next(
                                        (rune for rune in salvage_item.max_runes if rune.mod_type == ModType.Prefix), None)
                                
                                if prefix:
                                    ConsoleLog(
                                        "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name} to extract {prefix.name}", Console.MessageType.Info)
                                else:
                                    ConsoleLog(
                                        "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name} to extract 'Unkown Upgrade'", Console.MessageType.Info)
                            elif salvage_item.salvage_option == SalvageOption.Suffix:
                                suffix = None
                                
                                if salvage_item.is_weapon:
                                    suffix = next(
                                        (mod for mod in salvage_item.max_weapon_mods if mod.mod_type == ModType.Suffix), None)
                                elif salvage_item.is_armor:
                                    suffix = next(
                                        (rune for rune in salvage_item.max_runes if rune.mod_type == ModType.Suffix), None)
                                
                                if suffix:
                                    ConsoleLog(
                                        "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name} to extract {suffix.name}", Console.MessageType.Info)
                                else:
                                    ConsoleLog(
                                        "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name} to extract 'Unkown Upgrade'", Console.MessageType.Info)
                            elif salvage_item.salvage_option == SalvageOption.Inherent:
                                inherent = None
                                
                                if salvage_item.is_weapon:
                                    inherent = next(
                                        (mod for mod in salvage_item.max_weapon_mods if mod.mod_type == ModType.Inherent), None)
                                    
                                elif salvage_item.is_armor:
                                    ConsoleLog(
                                        "LootEx", f"Armors don't have a inherent mod to extract.", Console.MessageType.Info)
                                    return False
                                
                                if inherent:
                                    ConsoleLog(
                                        "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name} to extract {inherent.name}", Console.MessageType.Info)
                                else:
                                    ConsoleLog(
                                        "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name} to extract 'Unkown Upgrade'", Console.MessageType.Info)
                            else:
                                ConsoleLog(
                                    "LootEx", f"Confirming salvage option: {salvage_item.salvage_option.name} for {salvage_item.model_name}", Console.MessageType.Info)
                                
                            ui_manager_extensions.UIManagerExtensions.ConfirmLesserSalvage()
                            ui_manager_extensions.UIManagerExtensions.SelectSalvageOptionAndSalvage(
                                salvage_item.salvage_option)
                            # salvage_item.salvage_requires_confirmation = False
                            return True

        return False

    def GetActions(self, ) -> dict[int, Cached_Item]:
        if not settings.current.loot_profile:
            return {}

        actions: dict[int, Cached_Item] = {}
        cached_inventory: list[Cached_Item] = []

        def ShouldStashItem(item: Cached_Item) -> bool:
            if item.data and item.data.next_nick_week:
                weeks_until = (item.data.next_nick_week -
                               date.today()).days // 7

                if weeks_until <= settings.current.loot_profile.nick_weeks_to_keep if settings.current.loot_profile else False:
                    return True

            if self.IsVial_Of_DyeToKeep(item):
                return True

            # Item has more than one weapon mod we want to keep, do not process it, let the player decide
            if utility.Util.IsWeaponType(item.item_type):
                has_mod_to_keep, _, mods_to_keep = item.HasModToKeep()
                if has_mod_to_keep and (len(mods_to_keep) > 1 or not mods_to_keep[0].upgrade_exists):
                    return True

            # Item has more than one rune or insignia we want to keep do not process it, let the player decide
            if utility.Util.IsArmorType(item.item_type):
                has_mod_to_keep, runes_to_keep, _ = item.HasModToKeep()
                if has_mod_to_keep and (len(runes_to_keep) > 1):
                    return True

            return False

        def ShouldCollectData(item: Cached_Item) -> bool:
            if not item.data:
                return True

            missing_language = item.data.has_missing_names()
            if missing_language:
                ConsoleLog("LootEx", f"Item '{item.model_name}' ({item.id}) has missing data for {missing_language}, collecting data.",
                           Console.MessageType.Warning)
                return True

            if (item.is_armor or item.is_weapon or item.is_upgrade) and data_collector.instance.has_uncollected_mods(item_id)[0]:
                return True

            return False

        def ShouldIdentifyItem(item: Cached_Item) -> bool:
            if not item.is_identified:

                if item.is_weapon or item.is_armor:
                    if item.rarity > Rarity.White or item.value >= 25:
                        return True

            return False

        def ShouldExtractMods(item: Cached_Item) -> bool:
            if item.is_blacklisted:
                return False

            if item.is_salvageable:
                if item.is_weapon or item.is_armor:
                    has_max_mods, runes, weapon_mods = item.HasModToKeep()

                    if has_max_mods:
                        for rune in runes:
                            if settings.current.loot_profile and settings.current.loot_profile.runes.get(rune.identifier, False):
                                return True
                        
                        for weapon_mod in weapon_mods:
                            if settings.current.loot_profile and settings.current.loot_profile.weapon_mods.get(weapon_mod.identifier, {}).get(item.item_type.name, False):
                                return True                        

            return False

        def ShouldSalvageItem(item: Cached_Item) -> bool:
            if not settings.current.loot_profile:
                return False

            if item.is_blacklisted:
                return False

            if not item.is_salvageable:
                return False

            return self.IsSalvageAction(item.action)

        def ShouldSellItemToMerchant(item: Cached_Item) -> bool:
            if not settings.current.loot_profile:
                return False

            if item.is_blacklisted:
                return False

            # If the item is a material, we should not sell it to the merchant, instead we should deposit it to the material storage or visit the material trader
            if item.item_type == ItemType.Materials_Zcoins:
                return False

            # Runes and Insignias should not be sold to the merchant, instead we should visit the rune trader to sell them
            if item.item_type == ItemType.Rune_Mod:
                if item.is_rune:
                    return False

            if item.value <= 0:
                return False

            return item.action == ItemAction.SELL_TO_MERCHANT

        def ShouldDestroyItem(item: Cached_Item) -> bool:
            if not settings.current.loot_profile:
                return False

            if item.is_blacklisted:
                return False

            return item.action == ItemAction.DESTROY

        inventory_array = self.GetInventoryArray()
        self.inventory_changed = False
        
        has_empty_slot = False
        for slot, item_id in enumerate(inventory_array):
            item = Cached_Item(item_id, slot)
            cached_inventory.append(item)

            has_empty_slot = item.id == 0 or has_empty_slot
            if item.id == 0:
                continue

            existing_item = next(
                (item for item in self.cached_inventory if item.id == item_id), None)

            if existing_item and item.is_inventory_item and existing_item.quantity == item.quantity and (existing_item.rarity == item.rarity):
                item.action = existing_item.action
                actions[item_id] = item
                self.inventory_changed = self.inventory_changed or existing_item.slot != item.slot or has_empty_slot
                continue

            if not item.is_inventory_item:
                if item_id in actions:
                    del actions[item_id]

                cached_inventory.remove(item)
                continue
            
            if has_empty_slot:
                self.inventory_changed = True

            actions[item_id] = item
            self.inventory_changed = True

            if item.config:
                action = item.config.get_action(item)
                if action != ItemAction.NONE:
                    item.action = action

                    if self.IsSalvageAction(item.action):
                        salvage_option = self.GetSalvageOption(item)

                        if salvage_option is not None:
                            item.salvage_option = salvage_option
                            rarity_requires_confirmation = item.rarity >= Rarity.Blue
                            mods_require_confirmation = item.has_mods and salvage_option is not SalvageOption.LesserCraftingMaterials
                            item.salvage_requires_confirmation = rarity_requires_confirmation or mods_require_confirmation
                            self.salvage_queue.append(item)
                    continue

            for filter in settings.current.loot_profile.filters:
                action = filter.get_action(item)

                if action != ItemAction.NONE:
                    item.action = action

                    if self.IsSalvageAction(item.action):
                        salvage_option = self.GetSalvageOption(item)

                        if salvage_option is not None:
                            item.salvage_option = salvage_option
                            rarity_requires_confirmation = item.rarity >= Rarity.Blue
                            mods_require_confirmation = item.has_mods and salvage_option is not SalvageOption.LesserCraftingMaterials
                            item.salvage_requires_confirmation = rarity_requires_confirmation or mods_require_confirmation
                            self.salvage_queue.append(item)
                    continue

            # Soft action set for materials to deposit them to the material storage, may be overridden later through filters or item config
            if item.item_type == ItemType.Materials_Zcoins and item.action == ItemAction.NONE:
                if item.model_id in data.Materials:
                    self.inventory_materials.append(item)
                    item.action = ItemAction.DEPOSIT_MATERIAL

            if ShouldCollectData(item):
                item.action = ItemAction.COLLECT_DATA
                continue

            if ShouldIdentifyItem(item):
                item.action = ItemAction.IDENTIFY
                continue

            if ShouldStashItem(item):
                item.action = ItemAction.STASH
                continue

            if ShouldExtractMods(item):
                if item.is_weapon:
                    if item.max_weapon_mods and len(item.max_weapon_mods) == 1:
                        item.action = ItemAction.SALVAGE_MODS
                        item.salvage_option = utility.Util.GetSalvageOptionFromModType(
                            item.max_weapon_mods[0].mod_type)
                        item.salvage_requires_confirmation = True
                        self.salvage_queue.append(item)

                elif item.is_armor:
                    if item.max_runes and len(item.max_runes) == 1:
                        item.action = ItemAction.SALVAGE_MODS
                        item.salvage_option = utility.Util.GetSalvageOptionFromModType(
                            item.max_runes[0].mod_type)
                        item.salvage_requires_confirmation = True
                        self.salvage_queue.append(item)
                continue

            if ShouldSalvageItem(item):
                salvage_option = self.GetSalvageOption(item)
                ConsoleLog(
                    "LootEx", f"Salvage option for item {item.model_name} with action {item.action} is {salvage_option.name if salvage_option else 'None'}", Console.MessageType.Debug)

                if salvage_option is None:
                    continue

                if self.IsSalvageAction(item.action):
                    # self.salvage_option = salvage_option

                    rarity_requires_confirmation = item.rarity >= Rarity.Blue
                    mods_require_confirmation = item.has_mods and salvage_option is not SalvageOption.LesserCraftingMaterials

                    item.salvage_option = salvage_option
                    item.salvage_requires_confirmation = rarity_requires_confirmation or mods_require_confirmation

                    self.salvage_queue.append(item)
                    continue

            if ShouldSellItemToMerchant(item):
                item.action = ItemAction.SELL_TO_MERCHANT
                continue

            if ShouldDestroyItem(item):
                continue

        self.cached_inventory = cached_inventory

        return actions

    def Run(self):
        global time_results, actiontime_results
        self.run_once = False
        self.soft_reset()

        self.is_outpost = GLOBAL_CACHE.Map.IsOutpost()

        if data_collector.instance.is_running():
            return

        if not settings.current.loot_profile or not settings.current.automatic_inventory_handling:
            return

        if settings.current.loot_profile.changed:
            settings.current.loot_profile.changed = False
            self.reset()
            return

        global_time = datetime.now()

        self.ProcessSalvageList()

        if self.salvaging_item:
            self.UpdateSalvageWindows()

            if self.is_salvage_window_open or self.is_confirm_materials_window_open:
                if self.salvage_requires_confirmation:
                    if self._SendConfirmSalvage(self.salvaging_item, self.salvage_option):
                        self.salvaging_item.ResetMods()
                    return

        if self.inventory_timer.IsExpired():
            self.inventory_timer.Reset()

            self.UpdateSalvageWindows()
            self.merchant_open = ui_manager_extensions.UIManagerExtensions.IsMerchantWindowOpen()
            self.upgrade_open = ui_manager_extensions.UIManagerExtensions.IsUpgradeWindowOpen()

            if self.upgrade_open:
                self.reset()
                return

            self.empty_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
            actions = self.GetActions()

            if self.merchant_timer.IsExpired():
                self.merchant_timer.Reset()

                items_to_buy = self.GetMissingItems()
                if items_to_buy:
                    if self.is_outpost and not self.GetItemsFromStorage(items_to_buy):
                        if self.merchant_open:
                            self.BuyItemsFromMerchant(items_to_buy)

            for _, item in actions.items():
                time = datetime.now()
                time_delta = datetime.now() - time
                self.TrackTime(time_delta, actiontime_results, "Action")

                if item.id == -1:
                    ConsoleLog(
                        "LootEx", f"Processing item: '{item.model_name}' {item.id} with action: {item.action.name}", Console.MessageType.Debug)

                match item.action:
                    case ItemAction.COLLECT_DATA:
                        continue

                    case ItemAction.DEPOSIT_MATERIAL:
                        if self.is_outpost and self.inventory_changed:
                            if self.DepositMaterial(item):
                                self.inventory_changed = True
                        continue

                    case ItemAction.STASH:
                        if self.is_outpost:
                            self.StashItem(item)
                            self.inventory_changed = True                            

                    case ItemAction.IDENTIFY:
                        self.id_kit = Inventory.GetFirstIDKit() if self.id_kit == -1 else self.id_kit
                        self.remaining_uses = GLOBAL_CACHE.Item.Usage.GetUses(
                            self.id_kit) if self.remaining_uses == -1 else self.remaining_uses

                        if self.id_kit == 0 or self.remaining_uses <= 0:
                            continue

                        Inventory.IdentifyItem(item.id, self.id_kit)
                        self.remaining_uses -= 1

                    case ItemAction.SALVAGE_SMART | ItemAction.SALVAGE | ItemAction.SALVAGE_COMMON_MATERIALS | ItemAction.SALVAGE_RARE_MATERIALS:
                        continue

                    case ItemAction.SALVAGE_MODS:
                        continue

                    case ItemAction.SELL_TO_MERCHANT:
                        if self.merchant_open:
                            Trading.Merchant.SellItem(
                                item.id, item.quantity * item.value)
                            self.inventory_changed = True

                    case ItemAction.DESTROY:
                        ConsoleLog(
                            "LootEx", f"Destroying item: '{item.model_name}' ({item.id})", Console.MessageType.Info)
                        # Inventory.DestroyItem(item_id)
                        # self.inventory_changed = True

                    case _:
                        pass

            if self.inventory_changed:
                self.CompactInventory()

            time_delta = datetime.now() - global_time
            self.TrackTime(time_delta, time_results, "Global")
            ConsoleLog(
                "LootEx", f"Processed {len(actions)} items in {time_delta.microseconds * 0.000001} sec.", Console.MessageType.Debug)

    def Stop(self):
        ConsoleLog("LootEx", "Stopping loot handling",
                   Console.MessageType.Info)

        self.reset()
        settings.current.automatic_inventory_handling = False
        settings.current.save()

        return True

    def Start(self) -> bool:
        ConsoleLog("LootEx", "Starting loot handling",
                   Console.MessageType.Info)

        self.reset()
        settings.current.automatic_inventory_handling = True
        settings.current.save()

        return True

# endregion
