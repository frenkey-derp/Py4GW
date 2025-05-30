from LootEx.item_actions import InventoryAction, ItemActions, ItemAction
from Py4GWCoreLib import *
from LootEx import settings, utility
from LootEx.loot_profile import LootProfile

import importlib
importlib.reload(settings)

# self.skillbar_action_queue = ActionQueueNode(100)

salvaged = False
deposited = False
capacity_checked = False
material_capacity = 2500

def HandleInventoryLoot() -> int:
    if Map.IsOutpost():
        if (DepositMaterials()):
            return 50            

    return 250

    if not ActionQueueManager().IsEmpty("MERCHANT"):
        ActionQueueManager().ProcessQueue("MERCHANT")
        return 300

    if SetupItemsToBuy():
        return 300

    if not ActionQueueManager().IsEmpty("IDENTIFY"):
        ActionQueueManager().ProcessQueue("IDENTIFY")
        return 300

    hasItemToIdentify, item_id = HasItemToIdentify()

    if hasItemToIdentify:
        ActionQueueManager().ResetQueue("SALVAGE")
        ActionQueueManager().ResetQueue("MERCHANT")
        ActionQueueManager().AddAction("IDENTIFY", IdentifyItem, item_id)
        return 300

    if not ActionQueueManager().IsEmpty("SALVAGE"):
        ActionQueueManager().ProcessQueue("SALVAGE")
        return 800

    hasItemToSalvage, item_id = HasItemToSalvage()
    if hasItemToSalvage:
        quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)
        ActionQueueManager().ResetQueue("IDENTIFY")
        ActionQueueManager().ResetQueue("MERCHANT")

        for _ in range(quantity):
            ActionQueueManager().AddAction("SALVAGE", SalvageItem, item_id)
            ActionQueueManager().AddAction("SALVAGE", Inventory.AcceptSalvageMaterialsWindow)

    hasItemToSell, item_id = HasItemToSell()
    if hasItemToSell:
        ActionQueueManager().ResetQueue("IDENTIFY")
        ActionQueueManager().ResetQueue("SALVAGE")
        ActionQueueManager().AddAction("MERCHANT", SellItem, item_id)
        return 300

    if CompactInventory():
        return 50

    return 50


def DepositMaterials() -> bool:
    global deposited, capacity_checked, material_capacity
    
    if not deposited:
        ConsoleLog("LootEx", "Depositing materials into material storage", Console.MessageType.Info)
        
        items = GLOBAL_CACHE.ItemArray.GetRawItemArray(
            [Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2])

        items = ItemArray.Filter.ByCondition(
            items, lambda item: GLOBAL_CACHE.Item.GetItemType(item.item_id)[0] == ItemType.Materials_Zcoins.value)
        
        material_storage = GLOBAL_CACHE.ItemArray.GetRawItemArray(
            [Bags.MaterialStorage])
        
        model_ids = [i.model_id for i in items]
        
        ## filter the material_storage items to only include those which share the same model_id as the items in the inventory
        material_storage = ItemArray.Filter.ByCondition(
            material_storage, 
            lambda item: item.model_id in model_ids
        )
        
        deposited = True
        
        for material in material_storage:        
            item = next(
                (item for item in items if item.model_id == material.model_id), None)
            
            if item is not None:
                move_amount = min(material_capacity - material.quantity, item.quantity)
                
                if move_amount <= 0:
                    continue
                
                Inventory.MoveItem(item.item_id, Bags.MaterialStorage, material.slot, move_amount)
                
        return True
                
    elif not capacity_checked:
        ConsoleLog("LootEx", "Checking material storage capacity", Console.MessageType.Info)
        
        material_storage = GLOBAL_CACHE.ItemArray.GetRawItemArray(
            [Bags.MaterialStorage])
        
        max_quantity = max([item.quantity for item in material_storage])
        
        ## calculate the estimated capacity based on the max quantity by rounding it up to the nearest 250 if it is not already a multiple of 250
        
        estimated_capacity = (max_quantity // 250) * 250
        if max_quantity % 250 != 0:
            ## if it is not a multiple of 250, add 250 to the estimated capacity
            ## this ensures that the material storage capacity is always a multiple of 250
            estimated_capacity += 250
        ConsoleLog("LootEx", f"Estimated material storage capacity: {estimated_capacity}", Console.MessageType.Info)

        
        if estimated_capacity != material_capacity:
            material_capacity = estimated_capacity
            ConsoleLog("LootEx", f"Material storage capacity set to {material_capacity}", Console.MessageType.Info)
                 
        capacity_checked = True
        
                        
    return False


def ProcessInventoryActions() -> bool:
    return False


def CreateItemActions() -> list[InventoryAction]:
    item_actions = []

    bag_ids = [Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2]
    bag_total_slots = 0
    for bag_id in bag_ids:
        bag = PyInventory.Bag(bag_id.value, bag_id.name)
        bag_size = bag.GetSize()
        bag_total_slots += bag_size
        bag_items = bag.GetItems()

        for item in bag_items:
            item_action = InventoryAction(item.item_id)
            item_action.action = GetItemAction(item.item_id)
            item_action.source_bag = bag_id
            item_action.source_slot = item.slot
            item_actions.append(item_action)

    # Filter out the _None actions
    item_actions = [
        action for action in item_actions if action.Action != ItemAction.NONE]

    # Sort the item actions by action type and then slot
    item_actions.sort(key=lambda x: (x.Action, x.SourceBag, x.SourceSlot))

    return item_actions


def GetItemAction(item_id: int) -> ItemAction:
    if not GLOBAL_CACHE.Item.Usage.IsIdentified(item_id) and not GLOBAL_CACHE.Item.Usage.IsIDKit(item_id):
        return ItemAction.IDENTIFY

    profile = settings.current.loot_profile
    instance_type = PyMap.PyMap().instance_type.Get()

    if profile is None:
        return ItemAction.NONE

    model_id = ModelID(GLOBAL_CACHE.Item.GetModelID(item_id))

    # if profile.Items[model_id.name] is not None:
    #     action = profile.Items[model_id.name].ItemActions.GetAction(instance_type)
    #     if action != ItemAction._None:
    #         return action

    if profile.filters:
        for filter in profile.filters:
            if filter.handles_item_id(item_id):
                action = filter.get_action(instance_type)
                return action

    return ItemAction.NONE


def HasModToKeep(item_id: int) -> bool:
    mods = utility.Util.GetMods(item_id)
    _, item_type = GLOBAL_CACHE.Item.GetItemType(item_id)

    if settings.current.loot_profile is not None and settings.current.loot_profile.weapon_mods is not None:

        for mod in mods:
            if mod.identifier in settings.current.loot_profile.weapon_mods:
                if settings.current.loot_profile.weapon_mods[mod.identifier].get(item_type, False):
                    return True

    return False


class ItemMoveAction:
    def __init__(self, item_id: int, source_bag: Bags, target_bag: Bags, source_slot: int, target_slot: int):

        self.item_id = item_id
        self.target_bag: Bags = target_bag
        self.source_bag = source_bag
        self.source_slot = source_slot
        self.target_slot = target_slot
        self.quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)

    def execute(self):
        # Settings.Current.WriteLog("Moving item: " + Item.GetName(self.item_id) + " (Id: "+ str(self.item_id) + ") from [Bag: " + self.source_bag.name + " | Slot: " + str(self.source_slot) + "] to " + "[Bag: " + self.target_bag.name + " | Slot: " + str(self.target_slot) + "]", Console.MessageType.Info)
        Inventory.MoveItem(self.item_id, self.target_bag,
                           self.target_slot, self.quantity)


def CompactInventory() -> bool:
    # Sort the inventory and comapct it
    # We sort in the following order:
    item_typeOrder = [
        int(ItemType.Kit),
        int(ItemType.Key),
        int(ItemType.Materials_Zcoins)
    ]

    # then everything else
    item_typeOrder += [int(item)
                       for item in ItemType if int(item) not in item_typeOrder]

    bags_to_check = ItemArray.CreateBagList(
        Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2)
    item_array = sorted(
        ItemArray.GetItemArray(bags_to_check),
        key=lambda item_id: (
            item_typeOrder.index(
                int(GLOBAL_CACHE.Item.GetItemType(item_id)[0])),
            -GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)[0],
            GLOBAL_CACHE.Item.GetModelID(item_id),
            -GLOBAL_CACHE.Item.Properties.GetQuantity(item_id),
            item_id
        )
    )

    item_action_array = []

    def GetBagFromSlot(slot: int) -> tuple[Bags, int]:
        backpack_size = PyInventory.Bag(
            Bags.Backpack.value, Bags.Backpack.name).GetSize()
        belt_pouch_size = PyInventory.Bag(
            Bags.BeltPouch.value, Bags.BeltPouch.name).GetSize()
        bag1_size = PyInventory.Bag(Bags.Bag1.value, Bags.Bag1.name).GetSize()
        bag2_size = PyInventory.Bag(Bags.Bag2.value, Bags.Bag2.name).GetSize()

        if slot < backpack_size:
            return Bags.Backpack, slot - 0

        elif slot < backpack_size + belt_pouch_size:
            return Bags.BeltPouch, slot - backpack_size

        elif slot < backpack_size + belt_pouch_size + bag1_size:
            return Bags.Bag1, slot - backpack_size - belt_pouch_size

        elif slot < backpack_size + belt_pouch_size + bag1_size + bag2_size:
            return Bags.Bag2, slot - backpack_size - belt_pouch_size - bag1_size

        return Bags.NoBag, -1

    bag_ids = [Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2]
    bag_total_slots = 0
    for bag_id in bag_ids:
        bag = PyInventory.Bag(bag_id.value, bag_id.name)
        bag_size = bag.GetSize()
        bag_total_slots += bag_size
        bag_items = bag.GetItems()

        for item in bag_items:
            target_bag, target_slot = GetBagFromSlot(
                item_array.index(item.item_id))
            item_action_array.append(ItemMoveAction(
                item.item_id, bag_id, target_bag, item.slot, target_slot))

    for item_action in item_action_array:
        if item_action.source_slot != item_action.target_slot:
            ActionQueueManager().AddAction("ACTION", item_action.execute)
            return True

    return False


def HasItemToIdentify() -> tuple[bool, int]:
    for bag_id in range(Bags.Backpack, Bags.Bag2 + 1):
        bag_to_check = ItemArray.CreateBagList(bag_id)
        item_array = ItemArray.GetItemArray(bag_to_check)

        for item_id in item_array:
            if GLOBAL_CACHE.Item.Usage.IsIdentified(item_id) or GLOBAL_CACHE.Item.Usage.IsIDKit(item_id):
                continue

            # ConsoleLog("LootEx", "Item to identify: " + GLOBAL_CACHE.Item.GetName(item_id) +
            #            " (Id: " + str(item_id), Console.MessageType.Info)
            return True, item_id

    return False, -1


def IdentifyItem(item_id) -> bool:
    id_kit = Inventory.GetFirstIDKit()

    if id_kit == 0:
        return False

    if item_id != -1:
        ConsoleLog("LootEx", "Identify item: " +
                   GLOBAL_CACHE.Item.GetName(item_id), Console.MessageType.Info)
        Inventory.IdentifyItem(item_id, id_kit)
        return True

    return False


def HasItemToSalvage() -> tuple[bool, int]:
    if settings.current.loot_profile is None:
        return False, -1

    for bag_id in range(Bags.Backpack, Bags.Bag2 + 1):
        bag_to_check = ItemArray.CreateBagList(bag_id)
        item_array = ItemArray.GetItemArray(bag_to_check)

        for item_id in item_array:
            if not GLOBAL_CACHE.Item.Usage.IsSalvageable(item_id):
                continue

            if GLOBAL_CACHE.Item.Usage.IsSalvageKit(item_id):
                continue

            if not GLOBAL_CACHE.Item.Usage.IsIdentified(item_id):
                continue

            if GLOBAL_CACHE.Item.GetItemType(item_id)[0] == ItemType.Materials_Zcoins:
                continue

            if HasModToKeep(item_id):
                continue

            if utility.Util.has_missing_mods(item_id):
                continue

            if utility.Util.is_missing_item(item_id):
                continue

            value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
            if value > settings.current.loot_profile.sell_threshold:
                continue

            if GLOBAL_CACHE.Item.GetItemType(item_id)[0] == ItemType.Salvage and not GLOBAL_CACHE.Item.Rarity.IsWhite(item_id):
                continue

            if GLOBAL_CACHE.Item.Properties.IsCustomized(item_id):
                continue

            # ConsoleLog("LootEx", "Item to salvage: " + GLOBAL_CACHE.Item.GetName(item_id) +
            #            " (Id: " + str(item_id) + ")", Console.MessageType.Info)
            return True, item_id
    return False, -1


def SalvageItem(item_id) -> bool:
    salvage_kit = Inventory.GetFirstSalvageKit(True)

    if salvage_kit == 0:
        return False

    if item_id != -1:
        ConsoleLog("LootEx", "Salvage item: " + str(item_id) +
                   " with salvage kit " + str(salvage_kit), Console.MessageType.Info)
        Inventory.SalvageItem(item_id, salvage_kit)
        return True

    return False


def BuyItem(item_id: int, value: int):
    if item_id == 0:
        return

    if Inventory.GetFreeSlotCount() == 0:
        return

    coins = Inventory.GetGoldOnCharacter()
    if coins < value:
        return

    Trading.Merchant.BuyItem(item_id, value)


def SetupItemsToBuy() -> bool:
    if (settings.current.loot_profile is None):
        return False

    if Inventory.GetFreeSlotCount() == 0:
        return False

    coins = Inventory.GetGoldOnCharacter()

    idtificationKits = Inventory.GetModelCount(
        ModelID.Superior_Identification_Kit)
    if (idtificationKits < settings.current.loot_profile.identification_kits):
        idtificationKits_to_buy = settings.current.loot_profile.identification_kits - idtificationKits
        if idtificationKits_to_buy > 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(
                merchant_item_list, lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Superior_Identification_Kit)

            if len(merchant_item_list) > 0:
                for i in range(idtificationKits_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = GLOBAL_CACHE.Item.Properties.GetValue(item_id) * 2

                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    salvageKits = Inventory.GetModelCount(ModelID.Salvage_Kit)
    if (salvageKits < settings.current.loot_profile.salvage_kits):
        salvageKits_to_buy = settings.current.loot_profile.salvage_kits - salvageKits
        if salvageKits_to_buy > 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(
                merchant_item_list, lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Salvage_Kit)

            if len(merchant_item_list) > 0:
                for i in range(salvageKits_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = GLOBAL_CACHE.Item.Properties.GetValue(item_id) * 2
                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    expertSalvageKits = Inventory.GetModelCount(ModelID.Expert_Salvage_Kit)
    if (expertSalvageKits < settings.current.loot_profile.expert_salvage_kits):
        expertSalvageKits_to_buy = settings.current.loot_profile.expert_salvage_kits - \
            expertSalvageKits
        if expertSalvageKits_to_buy > 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(
                merchant_item_list, lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Expert_Salvage_Kit)

            if len(merchant_item_list) > 0:
                for i in range(expertSalvageKits_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = GLOBAL_CACHE.Item.Properties.GetValue(item_id) * 2
                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    lockpicks = Inventory.GetModelCount(ModelID.Lockpick)
    if (lockpicks < settings.current.loot_profile.lockpicks):
        lockpicks_to_buy = settings.current.loot_profile.lockpicks - lockpicks
        if lockpicks_to_buy > 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(
                merchant_item_list, lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Lockpick)

            if len(merchant_item_list) > 0:
                for i in range(lockpicks_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = GLOBAL_CACHE.Item.Properties.GetValue(item_id) * 2
                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    return not ActionQueueManager().IsEmpty("MERCHANT")


def HasItemToSell() -> tuple[bool, int]:
    if settings.current.loot_profile is None:
        return False, -1

    return False, -1

    for bag_id in range(Bags.Backpack, Bags.Bag2 + 1):
        bag_to_check = ItemArray.CreateBagList(bag_id)
        item_array = GLOBAL_CACHE.ItemArray.GetItemArray(bag_to_check)

        for item_id in item_array:
            id, name = GLOBAL_CACHE.Item.GetItemType(item_id)

            item_type = ItemType(id)

            if not GLOBAL_CACHE.Item.Usage.IsIdentified(item_id):
                continue

            if not utility.Util.IsWeaponType(item_type) and not utility.Util.IsArmorType(item_type) and item_type != ItemType.Trophy:
                continue

            if item_type == ItemType.Materials_Zcoins:
                continue

            if GLOBAL_CACHE.Item.Properties.IsCustomized(item_id):
                continue

            if HasModToKeep(item_id):
                continue

            if utility.Util.has_missing_mods(item_id):
                continue

            if utility.Util.is_missing_item(item_id):
                continue

            value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
            if value <= 0:
                continue

            ConsoleLog("LootEx", "Item to sell: " + GLOBAL_CACHE.Item.GetName(item_id) +
                       " (Id: " + str(item_id) + ")", Console.MessageType.Info)
            return True, item_id

    return False, -1


def SellItem(item_id: int) -> bool:
    if item_id == 0:
        return False

    if Inventory.GetFreeSlotCount() == 0:
        return False

    coins = Inventory.GetGoldOnCharacter()
    value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)

    if 100000 < (coins + value):
        return False

    ConsoleLog("LootEx", "Sell item: " + GLOBAL_CACHE.Item.GetName(item_id) +
               " (Id: " + str(item_id) + ") for " + str(value) + " coins", Console.MessageType.Info)
    Trading.Merchant.SellItem(item_id, value)

    return True
