from LootEx.item_actions import InventoryAction, ItemActions, ItemAction
from Py4GWCoreLib import *
from LootEx import settings
from LootEx.loot_profile import LootProfile

import importlib
importlib.reload(settings)

# self.skillbar_action_queue = ActionQueueNode(100)


def HandleInventoryLoot() -> int:
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
        ActionQueueManager().AddAction("IDENTIFY", IdentifyItem, item_id)
        return 300

    if not ActionQueueManager().IsEmpty("SALVAGE"):
        ActionQueueManager().ProcessQueue("SALVAGE")
        return 800

    hasItemToSalvage, item_id = HasItemToSalvage()
    if hasItemToSalvage:
        quantity = Item.Properties.GetQuantity(item_id)
        ActionQueueManager().ResetQueue("IDENTIFY")

        for _ in range(quantity):
            ActionQueueManager().AddAction("SALVAGE", SalvageItem, item_id)
            ActionQueueManager().AddAction("SALVAGE", Inventory.AcceptSalvageMaterialsWindow)

    if CompactInventory():
        return 50

    return 50


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
    if not Item.Usage.IsIdentified(item_id) and not Item.Usage.IsIDKit(item_id):
        return ItemAction.IDENTIFY

    profile = settings.current.loot_profile
    instance_type = PyMap.PyMap().instance_type.Get()

    if profile is None:
        return ItemAction.NONE

    model_id = ModelID(Item.GetModelID(item_id))

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


class ItemMoveAction:
    def __init__(self, item_id: int, source_bag: Bags, target_bag: Bags, source_slot: int, target_slot: int):

        self.item_id = item_id
        self.target_bag: Bags = target_bag
        self.source_bag = source_bag
        self.source_slot = source_slot
        self.target_slot = target_slot
        self.quantity = Item.Properties.GetQuantity(item_id)

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
            item_typeOrder.index(int(Item.GetItemType(item_id)[0])),
            -Item.Rarity.GetRarity(item_id)[0],
            Item.GetModelID(item_id),
            -Item.Properties.GetQuantity(item_id),
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
            if Item.Usage.IsIdentified(item_id) or Item.Usage.IsIDKit(item_id):
                continue

            ConsoleLog("LootEx", "Item to identify: " + Item.GetName(item_id) +
                       " (Id: " + str(item_id), Console.MessageType.Info)
            return True, item_id

    return False, -1


def IdentifyItem(item_id) -> bool:
    id_kit = Inventory.GetFirstIDKit()

    if id_kit == 0:
        return False

    if item_id != -1:
        ConsoleLog("LootEx", "Identify item: " +
                   Item.GetName(item_id), Console.MessageType.Info)
        Inventory.IdentifyItem(item_id, id_kit)
        return True

    return False


def HasItemToSalvage() -> tuple[bool, int]:
    for bag_id in range(Bags.Backpack, Bags.Bag2 + 1):
        bag_to_check = ItemArray.CreateBagList(bag_id)
        item_array = ItemArray.GetItemArray(bag_to_check)

        for item_id in item_array:
            if not Item.Usage.IsSalvageable(item_id):
                continue

            if Item.Usage.IsSalvageKit(item_id):
                continue

            if not Item.Usage.IsIdentified(item_id):
                continue

            if Item.GetItemType(item_id)[0] == ItemType.Materials_Zcoins:
                continue

            value = Item.Properties.GetValue(item_id)
            if value > 125:
                continue

            if Item.GetItemType(item_id)[0] == ItemType.Salvage and not Item.Rarity.IsWhite(item_id):
                continue

            if Item.Properties.IsCustomized(item_id):
                continue

            ConsoleLog("LootEx", "Item to salvage: " + Item.GetName(item_id) +
                       " (Id: " + str(item_id) + ")", Console.MessageType.Info)
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
                merchant_item_list, lambda item_id: Item.GetModelID(item_id) == ModelID.Superior_Identification_Kit)

            if len(merchant_item_list) > 0:
                for i in range(idtificationKits_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = Item.Properties.GetValue(item_id) * 2

                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    salvageKits = Inventory.GetModelCount(ModelID.Salvage_Kit)
    if (salvageKits < settings.current.loot_profile.salvage_kits):
        salvageKits_to_buy = settings.current.loot_profile.salvage_kits - salvageKits
        if salvageKits_to_buy > 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(
                merchant_item_list, lambda item_id: Item.GetModelID(item_id) == ModelID.Salvage_Kit)

            if len(merchant_item_list) > 0:
                for i in range(salvageKits_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = Item.Properties.GetValue(item_id) * 2
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
                merchant_item_list, lambda item_id: Item.GetModelID(item_id) == ModelID.Expert_Salvage_Kit)

            if len(merchant_item_list) > 0:
                for i in range(expertSalvageKits_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = Item.Properties.GetValue(item_id) * 2
                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    lockpicks = Inventory.GetModelCount(ModelID.Lockpick)
    if (lockpicks < settings.current.loot_profile.lockpicks):
        lockpicks_to_buy = settings.current.loot_profile.lockpicks - lockpicks
        if lockpicks_to_buy > 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(
                merchant_item_list, lambda item_id: Item.GetModelID(item_id) == ModelID.Lockpick)

            if len(merchant_item_list) > 0:
                for i in range(lockpicks_to_buy):
                    item_id = merchant_item_list[0]
                    # value reported is sell value not buy value
                    value = Item.Properties.GetValue(item_id) * 2
                    if value < coins:
                        ActionQueueManager().AddAction("MERCHANT", BuyItem, item_id, value)
                        coins -= value

    return not ActionQueueManager().IsEmpty("MERCHANT")
