from __future__ import annotations

import time
from enum import IntEnum
from typing import Any, Callable, Optional, cast

import Py4GW
import PyInventory
from PyItem import DyeColor

from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Bag, Item
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.Item_enums import MAX_STACK_SIZE, ItemType
from Py4GWCoreLib.enums_src.Item_enums import MAX_STACK_SIZE
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE
from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot
from Sources.frenkeyLib.ItemHandling.Rules.types import MATERIAL_SLOTS, SalvageMode
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions
from Sources.frenkeyLib.ItemHandling.utility import GetDestinationSlots, GetItemsLocations

INVENTORY_BAGS = [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2]
STORAGE_BAGS = [Bag.Storage_1, Bag.Storage_2, Bag.Storage_3, Bag.Storage_4, Bag.Storage_5, Bag.Storage_6, Bag.Storage_7, Bag.Storage_8, Bag.Storage_9, Bag.Storage_10, Bag.Storage_11, Bag.Storage_12, Bag.Storage_13, Bag.Storage_14]
SALVAGE_WINDOW_HASH = 684387150
LESSER_CONFIRM_HASH = 140452905

class BTNodes:
    NodeState = BehaviorTree.NodeState

    @staticmethod
    def _resolve_item_ids(node: BehaviorTree.Node, item_ids: Optional[list[int]], item_ids_key: str) -> list[int]:
        if item_ids is not None:
            return item_ids
        elif item_ids_key in node.blackboard:
            return node.blackboard[item_ids_key]
        else:
            return []

    @staticmethod
    def _success_if(condition: bool) -> BehaviorTree.NodeState:
        return BehaviorTree.NodeState.SUCCESS if condition else BehaviorTree.NodeState.FAILURE

    @staticmethod
    def _bag_sizes(bags: list[Bag]) -> dict[Bag, int]:
        sizes: dict[Bag, int] = {}
        for bag in bags:
            bag_obj = PyInventory.Bag(bag.value, bag.name)
            bag_obj.GetContext()
            sizes[bag] = bag_obj.GetSize()
        return sizes

    @staticmethod
    def _iter_bag_items(bags: list[Bag]) -> list[tuple[int, Bag, int]]:
        out: list[tuple[int, Bag, int]] = []
        for bag in bags:
            bag_obj = PyInventory.Bag(bag.value, bag.name)
            bag_obj.GetContext()
            for itm in bag_obj.GetItems():
                out.append((itm.item_id, bag, itm.slot))
        return out

    @staticmethod
    def _build_sort_key(mode: str) -> Callable[[int], tuple]:
        if mode == "value_desc":
            return lambda item_id: (-Item.Properties.GetValue(item_id), Item.GetModelID(item_id), item_id)
        if mode == "rarity_desc":
            return lambda item_id: (-Item.Rarity.GetRarity(item_id)[0], Item.GetModelID(item_id), item_id)
        # default: item type, rarity, model, value
        return lambda item_id: (
            Item.GetItemType(item_id)[0],
            Item.Rarity.GetRarity(item_id)[0],
            Item.GetModelID(item_id),
            Item.Properties.GetValue(item_id),
            item_id,
        )

    @staticmethod
    def _frame_exists(frame_id: int) -> bool:
        return isinstance(frame_id, int) and frame_id > 0 and UIManager.FrameExists(frame_id)

    @staticmethod
    def _safe_quantity(item_id: int) -> int:
        try:
            return Item.Properties.GetQuantity(item_id)
        except Exception:
            return 0

    @staticmethod
    def _safe_is_inventory_item(item_id: int) -> bool:
        try:
            return Item.Type.IsInventoryItem(item_id)
        except Exception:
            return False

    @staticmethod
    def _find_salvage_kit(prefer_expert: bool = False, allow_lesser_fallback: bool = True) -> int:
        inventory_item_ids = [item_id for item_id, _, _ in BTNodes._iter_bag_items(INVENTORY_BAGS)]
        salvage_kits = [item_id for item_id in inventory_item_ids if Item.Usage.IsSalvageKit(item_id)]
        if not salvage_kits:
            return 0

        expert_kits = [item_id for item_id in salvage_kits if Item.Usage.IsExpertSalvageKit(item_id) or Item.Usage.IsPerfectSalvageKit(item_id)]
        lesser_kits = [item_id for item_id in salvage_kits if Item.Usage.IsLesserKit(item_id)]

        def _pick_lowest_uses(items: list[int]) -> int:
            if not items:
                return 0
            return min(items, key=lambda item_id: Item.Usage.GetUses(item_id))

        if prefer_expert:
            expert = _pick_lowest_uses(expert_kits)
            if expert != 0:
                return expert
            if allow_lesser_fallback:
                return _pick_lowest_uses(lesser_kits)
            return 0

        lesser = _pick_lowest_uses(lesser_kits)
        if lesser != 0:
            return lesser
        return _pick_lowest_uses(expert_kits)

    class Merchant:
        @staticmethod
        def SellItems(
            item_ids: list[int] | None = None,
            item_ids_key: str = "item_ids",
            aftercast_ms: int = 150,
        ):
            def _sell(node: BehaviorTree.Node):
                ids = BTNodes._resolve_item_ids(node, item_ids, item_ids_key)
                if not ids:
                    return BehaviorTree.NodeState.FAILURE

                sold_any = False
                for item_id in ids:
                    qty = Item.Properties.GetQuantity(item_id)
                    if qty <= 0:
                        continue
                    Trading.Merchant.SellItem(item_id, Item.Properties.GetValue(item_id) * qty)
                    sold_any = True

                return BTNodes._success_if(sold_any)

            return BehaviorTree.ActionNode(name="Merchant.SellItems", action_fn=_sell, aftercast_ms=aftercast_ms)

        @staticmethod
        def BuyItems(
            item_ids: list[int] | None = None,
            quantities: list[int] | None = None,
            costs: list[int] | None = None,
            item_ids_key: str = "merchant_item_ids",
            quantities_key: str = "merchant_quantities",
            costs_key: str = "merchant_costs",
            aftercast_ms: int = 150,
        ):
            def _buy(node: BehaviorTree.Node):
                ids = BTNodes._resolve_item_ids(node, item_ids, item_ids_key)
                if not ids:
                    return BehaviorTree.NodeState.FAILURE

                qtys = quantities if quantities is not None else node.blackboard.get(quantities_key, [])
                prices = costs if costs is not None else node.blackboard.get(costs_key, [])

                bought_any = False
                for i, offered_item_id in enumerate(ids):
                    count = qtys[i] if i < len(qtys) else 1
                    price = prices[i] if i < len(prices) else Item.Properties.GetValue(offered_item_id) * 2
                    for _ in range(max(0, count)):
                        Trading.Merchant.BuyItem(offered_item_id, price)
                        bought_any = True

                return BTNodes._success_if(bought_any)

            return BehaviorTree.ActionNode(name="Merchant.BuyItems", action_fn=_buy, aftercast_ms=aftercast_ms)

    class Trader:
        @staticmethod
        def BuyItems(
            item_ids: list[int] | None = None,
            costs: list[int] | None = None,
            item_ids_key: str = "trader_buy_item_ids",
            costs_key: str = "trader_buy_costs",
            state_key: str = "_trader_buy_state",
            quote_timeout_ms: int = 1500,
            aftercast_ms: int = 100,
        ):
            def _buy(node: BehaviorTree.Node):
                ids = BTNodes._resolve_item_ids(node, item_ids, item_ids_key)
                if not ids:
                    return BehaviorTree.NodeState.FAILURE

                given_costs = costs if costs is not None else node.blackboard.get(costs_key, [])
                if given_costs:
                    any_action = False
                    for i, item_id in enumerate(ids):
                        if i < len(given_costs):
                            Trading.Trader.BuyItem(item_id, int(given_costs[i]))
                            any_action = True
                    return BTNodes._success_if(any_action)

                state = node.blackboard.get(state_key)
                if state is None:
                    state = {"index": 0, "requested_at": 0.0}
                    node.blackboard[state_key] = state

                idx = state["index"]
                if idx >= len(ids):
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

                item_id = ids[idx]
                if state["requested_at"] <= 0:
                    Trading.Trader.RequestQuote(item_id)
                    state["requested_at"] = time.monotonic()
                    return BehaviorTree.NodeState.RUNNING

                quoted_item_id = Trading.Trader.GetQuotedItemID()
                quoted_cost = Trading.Trader.GetQuotedValue()
                if quoted_item_id == item_id and quoted_cost >= 0:
                    Trading.Trader.BuyItem(item_id, quoted_cost)
                    state["index"] += 1
                    state["requested_at"] = 0.0
                    return BehaviorTree.NodeState.RUNNING if state["index"] < len(ids) else BehaviorTree.NodeState.SUCCESS

                if (time.monotonic() - state["requested_at"]) * 1000 >= quote_timeout_ms:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree.ActionNode(name="Trader.BuyItems", action_fn=_buy, aftercast_ms=aftercast_ms)

        @staticmethod
        def SellItems(
            item_ids: list[int] | None = None,
            costs: list[int] | None = None,
            item_ids_key: str = "trader_sell_item_ids",
            costs_key: str = "trader_sell_costs",
            state_key: str = "_trader_sell_state",
            quote_timeout_ms: int = 1500,
            aftercast_ms: int = 100,
        ):
            def _sell(node: BehaviorTree.Node):
                ids = BTNodes._resolve_item_ids(node, item_ids, item_ids_key)
                if not ids:
                    return BehaviorTree.NodeState.FAILURE

                given_costs = costs if costs is not None else node.blackboard.get(costs_key, [])
                if given_costs:
                    any_action = False
                    for i, item_id in enumerate(ids):
                        if i < len(given_costs):
                            Trading.Trader.SellItem(item_id, int(given_costs[i]))
                            any_action = True
                    return BTNodes._success_if(any_action)

                state = node.blackboard.get(state_key)
                if state is None:
                    state = {"index": 0, "requested_at": 0.0}
                    node.blackboard[state_key] = state

                idx = state["index"]
                if idx >= len(ids):
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

                item_id = ids[idx]
                if state["requested_at"] <= 0:
                    Trading.Trader.RequestSellQuote(item_id)
                    state["requested_at"] = time.monotonic()
                    return BehaviorTree.NodeState.RUNNING

                quoted_item_id = Trading.Trader.GetQuotedItemID()
                quoted_cost = Trading.Trader.GetQuotedValue()
                if quoted_item_id == item_id and quoted_cost >= 0:
                    Trading.Trader.SellItem(item_id, quoted_cost)
                    state["index"] += 1
                    state["requested_at"] = 0.0
                    return BehaviorTree.NodeState.RUNNING if state["index"] < len(ids) else BehaviorTree.NodeState.SUCCESS

                if (time.monotonic() - state["requested_at"]) * 1000 >= quote_timeout_ms:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree.ActionNode(name="Trader.SellItems", action_fn=_sell, aftercast_ms=aftercast_ms)

    class Items:
        class SavalvageProgress():
            def __init__(self, item_id: int, salvage_started_at: float, initial_qty: int):
                self.item_id = item_id
                self.salvage_started_at = salvage_started_at
                self.initial_qty = initial_qty
                self.confirm_clicked_at = 0.0
                self.salvaged_any = False
                self.waiting_started = False
                
        @staticmethod
        def IdentifyItems(
            item_ids: list[int] | None = None,
            fail_if_no_kit: bool = True,
            succeed_if_already_identified: bool = True,
            aftercast_ms: int = 150,
        ):
            def _identify(node: BehaviorTree.Node):
                if not item_ids:
                    return BehaviorTree.NodeState.FAILURE

                identified_any = False
                items = [ITEM_CACHE.get_item_snapshot(iid) for iid in item_ids]
                
                for item in items:
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    kit_id = Inventory.GetFirstIDKit()
                    
                    if kit_id == 0:
                        return BehaviorTree.NodeState.FAILURE if fail_if_no_kit else (BehaviorTree.NodeState.SUCCESS if identified_any else (BehaviorTree.NodeState.SUCCESS if succeed_if_already_identified else BehaviorTree.NodeState.FAILURE))
                    
                    Inventory.IdentifyItem(item.id, kit_id)
                    identified_any = True

                return BehaviorTree.NodeState.SUCCESS if identified_any else (BehaviorTree.NodeState.SUCCESS if succeed_if_already_identified else BehaviorTree.NodeState.FAILURE)

            return BehaviorTree.ActionNode(name="Items.IdentifyItems", action_fn=_identify, aftercast_ms=aftercast_ms)

        @staticmethod
        def SalvageItem(
            item_id : int,
            use_lesser_kit: bool = True,
            fail_if_no_kit: bool = True,
            salvage_mode: "SalvageMode | int" = 0,
            allow_lesser_fallback_for_expert: bool = True,
            state_key: str = "_salvage_state",
            timeout_ms_per_item: int = 1500,
            aftercast_ms: int = 0,
        ):
            def _reset_state(node: BehaviorTree.Node):
                node.blackboard.pop(state_key, None)
                
            def _is_mod_salvaged(item: ItemSnapshot, salvage_mode: SalvageMode) -> bool:
                match salvage_mode:
                    case SalvageMode.Prefix:
                        return item.prefix is None
                    
                    case SalvageMode.Suffix:
                        return item.suffix is None
                    
                    case SalvageMode.Inherent:
                        return item.inscription is None
            
                return False
            
            def _salvage(node: BehaviorTree.Node):        
                if item_id is None or item_id <= 0:
                    _reset_state(node)
                    return BehaviorTree.NodeState.FAILURE
                
                try:
                    mode = SalvageMode(int(salvage_mode))
                except Exception:
                    mode = SalvageMode.NONE
                
                if mode == SalvageMode.NONE:
                    return BehaviorTree.NodeState.FAILURE
                                
                state = node.blackboard.get(state_key)
                state = cast(BTNodes.Items.SavalvageProgress, state) if state else None
                item = ITEM_CACHE.get_item_snapshot(item_id)
                
                log_prefix = f"{node.name}|Item '{item.data.names.get(ServerLanguage.English, 'Unknown') if item and item.data else 'Unknown'} ({item_id})"
                
                if (state and item_id != state.item_id) or item is None or not item.is_valid or not item.is_salvageable or not item.is_inventory_item or _is_mod_salvaged(item, mode):
                    _reset_state(node)                        
                    return BehaviorTree.NodeState.SUCCESS
                
                if state is None:
                    state = BTNodes.Items.SavalvageProgress(item_id=item.id, salvage_started_at=0.0, initial_qty=item.quantity)                   
                    node.blackboard[state_key] = state
                    
                now = time.monotonic()

                if Inventory.GetFreeSlotCount() <= 0:
                    _reset_state(node)
                    return BehaviorTree.NodeState.FAILURE

                # Start salvage once per item.
                if not state.salvage_started_at:
                    prefer_expert = mode in (
                        SalvageMode.Prefix,
                        SalvageMode.Suffix,
                        SalvageMode.Inherent,
                        SalvageMode.RareCraftingMaterials,
                    )
                    
                    if prefer_expert:
                        kit_id = BTNodes._find_salvage_kit(prefer_expert=True, allow_lesser_fallback=allow_lesser_fallback_for_expert)
                    else:
                        kit_id = BTNodes._find_salvage_kit(prefer_expert=False, allow_lesser_fallback=use_lesser_kit)

                    if kit_id <= 0:
                        _reset_state(node)
                        return BehaviorTree.NodeState.FAILURE

                    Inventory.SalvageItem(item_id, kit_id)
                    state.salvage_started_at = now
                    state.waiting_started = True
                    return BehaviorTree.NodeState.RUNNING

                # Handle salvage windows/frames while waiting for completion.
                if UIManagerExtensions.IsConfirmLesserMaterialsWindowOpen():
                    if UIManagerExtensions.ConfirmLesserSalvage():
                        state.confirm_clicked_at = now
                        return BehaviorTree.NodeState.RUNNING

                if UIManagerExtensions.IsSalvageWindowOpen():
                    if UIManagerExtensions.SelectSalvageOptionAndSalvage(mode):
                        state.confirm_clicked_at = now
                        return BehaviorTree.NodeState.RUNNING
                    else:
                        UIManagerExtensions.CancelSalvageOption()
                        _reset_state(node)
                        return BehaviorTree.NodeState.FAILURE

                # Completion checks.
                current_qty = item.quantity
                initial_qty = state.initial_qty
                confirm_clicked_at = state.confirm_clicked_at

                qty_changed = current_qty < initial_qty
                item_gone = not item.is_inventory_item
                mod_salvaged = _is_mod_salvaged(item, mode)
                windows_closed_after_confirm = (
                    confirm_clicked_at > 0.0
                    and not UIManagerExtensions.AnySalvageRelatedWindowOpen()
                    and (now - confirm_clicked_at) >= 0.20
                )

                if qty_changed or item_gone or windows_closed_after_confirm or mod_salvaged:
                    return BehaviorTree.NodeState.SUCCESS

                if (now - float(state.salvage_started_at)) * 1000 >= timeout_ms_per_item:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree.ActionNode(name="Items.SalvageItems", action_fn=_salvage, aftercast_ms=aftercast_ms)

        @staticmethod
        def DestroyItems(
            item_ids: list[int] | None = None,
            aftercast_ms: int = 100,
            succeed_always: bool = True,
        ):
            def _destroy(node: BehaviorTree.Node):
                if not item_ids:
                    return BehaviorTree.NodeState.FAILURE

                destroyed_any = False
                items = [ITEM_CACHE.get_item_snapshot(iid) for iid in item_ids]                
                for item in items:
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    Inventory.DestroyItem(item.id)
                    destroyed_any = True

                return BehaviorTree.NodeState.SUCCESS if succeed_always else BTNodes._success_if(destroyed_any)

            return BehaviorTree.ActionNode(name="Items.DestroyItems", action_fn=_destroy, aftercast_ms=aftercast_ms)

        class ItemTransferInstructions:
            def __init__(self, bag: Bag, slot: int, stack_item: Optional[ItemSnapshot], available_space: int = MAX_STACK_SIZE):                
                self.bag = bag
                self.slot = slot
                self.stack_item = stack_item                
                self.available_space = available_space - stack_item.quantity if stack_item and stack_item.is_stackable else available_space
                
                self.items : list[tuple[ItemSnapshot, int]] = []
        
        @staticmethod
        def GetTransferInstructions(
            item_ids: list[int],
            target : list[Bag],
            fill_materials_first: bool = True,
        ) -> dict[Bag, dict[int, BTNodes.Items.ItemTransferInstructions]]:
            
            locations = GetItemsLocations(item_ids)
            source = list(set(bag for bag, _ in locations))
            
            to_inventory = any(bag in INVENTORY_BAGS for bag in target)
            to_storage = any(bag in STORAGE_BAGS or bag == Bag.Material_Storage for bag in target)
            
            from_inventory = any(bag in INVENTORY_BAGS for bag in source)
            from_storage = any(bag in STORAGE_BAGS or bag == Bag.Material_Storage for bag in source)
           
            material_storage_snapshot = ITEM_CACHE.get_bag_snapshot(Bag.Material_Storage) if (from_storage or to_storage) else {}
            target_snapshot = ITEM_CACHE.get_bags_snapshot(target)
            moving_instructions : dict[Bag, dict[int, BTNodes.Items.ItemTransferInstructions]] = {}
            
            #get max quantity from material_storage_snapshot.get(Bag.Material_Storage, {}).values() and ceil to the next MAX_STACK_SIZE to determine the max capacity
            material_storage_capacity = (
                max(
                    (item.quantity for item in material_storage_snapshot.values() if item),
                    default=0
                )
                + MAX_STACK_SIZE - 1
            ) // MAX_STACK_SIZE * MAX_STACK_SIZE
            if material_storage_capacity <= 0:
                material_storage_capacity = MAX_STACK_SIZE
                                            
            for item_id in item_ids:                            
                item = ITEM_CACHE.get_item_snapshot(item_id)
                
                if not item or not item.is_valid or (item.is_inventory_item and to_inventory) or (item.is_storage_item and to_storage) or (not item.is_inventory_item and from_inventory) or (not item.is_storage_item and from_storage):
                    continue
                
                if item.is_stackable:
                    if fill_materials_first and from_inventory and (item.is_material or item.is_rare_material):
                        for slot, stack_item in material_storage_snapshot.items():
                            if stack_item and stack_item.is_valid and stack_item.is_stackable and stack_item.same_kind_as(item) and stack_item.quantity < material_storage_capacity:
                                moving_instructions.setdefault(Bag.Material_Storage, {})
                                dest = moving_instructions[Bag.Material_Storage].setdefault(slot, BTNodes.Items.ItemTransferInstructions(Bag.Material_Storage, slot, stack_item, available_space=material_storage_capacity))
                                
                                if dest.available_space > 0:
                                    qty_to_move = min(dest.available_space, item.quantity)
                                    dest.available_space -= qty_to_move
                                    dest.items.append((item, qty_to_move))
                                    item.quantity -= qty_to_move
                                    
                                    stack_item.quantity += qty_to_move  # simulate the move in the cache to get correct available space for subsequent stacks of the same item
                                    
                                    if item.quantity <= 0:
                                        Py4GW.Console.Log("GetTransferInstructions", f"Planned to move {qty_to_move} of '{item.data.names.get(ServerLanguage.English, 'Unknown') if item.data else 'Unknown Item'}' (ID: {item.id}) to Material Storage bag {Bag.Material_Storage.name} slot {slot}")
                                        break
                        
                        if item.quantity <= 0:
                            Py4GW.Console.Log("GetTransferInstructions", f"Item quantity reduced to 0, moving on to next item.")
                            break                                
                        
                    # get all items with the same model and type that have free space in their stacks and add them as potential destinations for the current item until we have found enough space for the whole stack. This way we minimize fragmentation in the bank and maximize the chances of fitting all items. We get them all from bag_enum, bag in inventory_snapshot.items()
                    stacks_of_same_kind_with_space = [(i, bag_id) for bag_id, bag in target_snapshot.items() for i in bag.values() if i and i.is_valid and i.is_stackable and i.same_kind_as(item) and i.quantity < MAX_STACK_SIZE]
                    
                    #sorted by least free space to most free space to fill up more full stacks first, then by bag and slot, so we fill from the beginning of the bank to the end to minimize fragmentation
                    stacks_of_same_kind_with_space.sort(key=lambda x: (-x[0].quantity, x[1].value, x[0].slot))
                    
                    for stack_item, bag in stacks_of_same_kind_with_space:
                        if stack_item.quantity >= MAX_STACK_SIZE:
                            continue
                        
                        moving_instructions.setdefault(bag, {})
                        dest = moving_instructions[bag].setdefault(stack_item.slot, BTNodes.Items.ItemTransferInstructions(bag, stack_item.slot, stack_item))
                        if dest.available_space > 0:
                            qty_to_move = min(dest.available_space, item.quantity)
                            dest.available_space -= qty_to_move
                            dest.items.append((item, qty_to_move))
                            item.quantity -= qty_to_move
                            
                            stack_item.quantity += qty_to_move  # simulate the move in the cache to get correct available space for subsequent stacks of the same item
                            
                            if item.quantity <= 0:
                                Py4GW.Console.Log("GetTransferInstructions", f"Item quantity reduced to 0, moving on to next item.")
                                break
                    
                    
                        if item.quantity <= 0:
                            break
                    
                if item.quantity > 0:
                    for bag_enum, bag in target_snapshot.items():
                        for slot, stack_item in bag.items():
                            if stack_item is None:
                                moving_instructions.setdefault(bag_enum, {})
                                dest = moving_instructions[bag_enum].setdefault(slot, BTNodes.Items.ItemTransferInstructions(bag_enum, slot, None))
                                
                                qty_to_move = min(dest.available_space, item.quantity)
                                dest.available_space -= qty_to_move
                                dest.items.append((item, qty_to_move))
                                item.quantity -= qty_to_move
                                                                
                                if item.quantity <= 0:
                                    break
                        
                        if item.quantity <= 0:
                            break
                
            return moving_instructions            
        
        @staticmethod
        def DepositItems(
            item_ids: list[int],
            target : list[Bag] = STORAGE_BAGS,
            anniversary_panel: bool = False,
            fill_materials_first: bool = True,
            fail_if_no_space: bool = True,
            aftercast_ms: int = 25,
        ):
            if not anniversary_panel and Bag.Storage_14 in target:
                target = [b for b in target if b != Bag.Storage_14]
            
            def _deposit(node: BehaviorTree.Node):
                instructions = BTNodes.Items.GetTransferInstructions(item_ids, target, fill_materials_first)
                moved_any = False
                
                if not instructions:
                    return BehaviorTree.NodeState.FAILURE if fail_if_no_space else BehaviorTree.NodeState.SUCCESS
                
                for bag in instructions.values():
                    for dest in bag.values():
                        for item, qty in dest.items:
                            Inventory.MoveItem(item.id, dest.bag.value, dest.slot, qty)
                            Py4GW.Console.Log(node.name, f"Moving {qty} of '{item.data.names.get(ServerLanguage.English, 'Unknown') if item.data else 'Unknown Item'}' (ID: {item.id}) to bag {dest.bag.name} slot {dest.slot}")
                            moved_any = True
                
                return BehaviorTree.NodeState.SUCCESS if moved_any else BehaviorTree.NodeState.FAILURE

            return BehaviorTree.ActionNode(name="Items.DepositItems", action_fn=_deposit, aftercast_ms=aftercast_ms)
        
        @staticmethod
        def WithdrawItems(
            item_ids: list[int],
            target : list[Bag] = INVENTORY_BAGS,
            fill_materials_first: bool = True,
            fail_if_no_space: bool = True,
            aftercast_ms: int = 25,
        ):                   
            def _withdraw(node: BehaviorTree.Node):
                instructions = BTNodes.Items.GetTransferInstructions(item_ids, target, fill_materials_first)
                moved_any = False
                
                if not instructions:
                    return BehaviorTree.NodeState.FAILURE if fail_if_no_space else BehaviorTree.NodeState.SUCCESS
                
                for bag in instructions.values():
                    for dest in bag.values():
                        for item, qty in dest.items:
                            Inventory.MoveItem(item.id, dest.bag.value, dest.slot, qty)
                            Py4GW.Console.Log(node.name, f"Moving {qty} of '{item.data.names.get(ServerLanguage.English, 'Unknown') if item.data else 'Unknown Item'}' (ID: {item.id}) to bag {dest.bag.name} slot {dest.slot}")
                            moved_any = True
                
                return BehaviorTree.NodeState.SUCCESS if moved_any else BehaviorTree.NodeState.FAILURE

            return BehaviorTree.ActionNode(name="Items.WithdrawItems", action_fn=_withdraw, aftercast_ms=aftercast_ms)

    class Bags:
        @staticmethod
        def FillMaterialStorage(
            source : list[Bag] = STORAGE_BAGS,
            aftercast_ms: int = 150,
            succeed_if_already_filled: bool = True,
        ):
            def _fill_material_storage(node: BehaviorTree.Node):
                source_bags = [bag for bag in source if bag != Bag.Material_Storage]
                if not source_bags:
                    return BehaviorTree.NodeState.FAILURE

                source_snapshot = ITEM_CACHE.get_bags_snapshot(source_bags)
                material_snapshot = ITEM_CACHE.get_bag_snapshot(Bag.Material_Storage)

                material_storage_capacity = (
                    max((item.quantity for item in material_snapshot.values() if item), default=0) + MAX_STACK_SIZE - 1
                ) // MAX_STACK_SIZE * MAX_STACK_SIZE
                if material_storage_capacity <= 0:
                    material_storage_capacity = MAX_STACK_SIZE

                moved_any = False
                transfer_instructions: dict[int, BTNodes.Items.ItemTransferInstructions] = {}
                bag_item_map : dict[int, Bag] = {item_id: bag for bag, bag_items in source_snapshot.items() for item_id, item in bag_items.items() if item}
                
                for _, bag_items in source_snapshot.items():
                    for _, item in bag_items.items():
                        if item is None or not item.is_valid or not item.is_stackable or bag_item_map.get(item.id) == Bag.Material_Storage:
                            continue
                        
                        if not (item.is_material or item.is_rare_material):
                            continue
                        
                        slot = MATERIAL_SLOTS.get(item.model_id, None)
                        if slot is None:
                            continue
                        
                        material = material_snapshot.get(slot, None)
                        transfer_instructions.setdefault(slot, BTNodes.Items.ItemTransferInstructions(Bag.Material_Storage, slot, material, available_space=material_storage_capacity))
                        inst = transfer_instructions.get(slot)
                        
                        if inst is None:
                            continue
                        
                        qty_to_move = min(inst.available_space, item.quantity)
                        
                        if qty_to_move <= 0:
                            continue
                        
                        inst.available_space -= qty_to_move
                        inst.items.append((item, qty_to_move))
                        item.quantity -= qty_to_move
                
                for dest in transfer_instructions.values():
                    for item, qty in dest.items:
                        Inventory.MoveItem(item.id, dest.bag.value, dest.slot, qty)
                        Py4GW.Console.Log(node.name, f"Moving {qty} of '{item.data.names.get(ServerLanguage.English, 'Unknown') if item.data else 'Unknown Item'}' (ID: {item.id}) to Material Storage slot {dest.slot}")
                        moved_any = True

                return BTNodes._success_if(moved_any or succeed_if_already_filled)

            return BehaviorTree.ActionNode(name="Inventory.FillMaterialStorage", action_fn=_fill_material_storage, aftercast_ms=aftercast_ms)
        
        @staticmethod
        def CompactBags(
            bags : list[Bag] = INVENTORY_BAGS,         
            aftercast_ms: int = 150,
        ):
            def _compact(node: BehaviorTree.Node):
                snapshot = ITEM_CACHE.get_bags_snapshot(bags)
                grouped_items : dict[tuple[ItemType, int, int], list[tuple[Bag, int, ItemSnapshot]]] = {}
                moved_any = False
                
                for bag in bags:
                    for slot, item in snapshot.get(bag, {}).items():
                        if item and item.is_valid and item.is_stackable and item.quantity < MAX_STACK_SIZE:
                            key = (item.item_type, item.model_id, item.color.value)
                            grouped_items.setdefault(key, []).append((bag, slot, item))
                            
                for _, items in grouped_items.items():
                    if len(items) <= 1:
                        continue
                    
                    items.sort(key=lambda x: x[2].quantity, reverse=True)
                    target_bag, target_slot, target_item = items[0]
                    
                    for source_bag, source_slot, source_item in items[1:]:
                        if target_item.quantity >= MAX_STACK_SIZE:
                            break
                        
                        qty_to_move = min(source_item.quantity, MAX_STACK_SIZE - target_item.quantity)
                        if qty_to_move <= 0:
                            continue
                        
                        Inventory.MoveItem(source_item.id, target_bag.value, target_slot, qty_to_move)
                        Py4GW.Console.Log(node.name, f"Moved {qty_to_move} of '{source_item.data.names.get(ServerLanguage.English, 'Unknown') if source_item.data else 'Unknown Item'}' (ID: {source_item.id}) from bag {source_bag.name} slot {source_slot} to bag {target_bag.name} slot {target_slot}")
                        moved_any = True
                        target_item.quantity += qty_to_move
                        source_item.quantity -= qty_to_move
                
                
                return BTNodes._success_if(moved_any)
            return BehaviorTree.ActionNode(name="Inventory.CompactBags", action_fn=_compact, aftercast_ms=aftercast_ms)

        @staticmethod
        def SortBags(
            bags : list[Bag] = INVENTORY_BAGS,         
            aftercast_ms: int = 150,
        ):
            def _sort(node: BehaviorTree.Node):
                snapshot = ITEM_CACHE.get_bags_snapshot(bags)

                # TODO: Here we want to implement our sorting configuration, for now this is just the default behavior
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
                
                index_to_bag_map : dict[int, tuple[Bag, int]] = {}
                index = 0
                
                for bag in bags:
                    for slot in snapshot.get(bag, {}).keys():
                        index_to_bag_map[index] = (bag, slot)
                        index += 1
                            
                items = [item for bag in bags for slot, item in snapshot.get(bag, {}).items() if item and item.is_valid]
                sorted_items = sorted(
                    items,
                    key=lambda item: (
                        item.item_type == ItemType.Unknown,
                        item_typeOrder.index(item.item_type),
                        item.model_id,
                        -item.rarity.value,
                        -item.quantity,
                        -item.value,
                        item.color.value,
                        item.id
                    )
                )
                
                for index, item in enumerate(sorted_items):
                    bag, slot = index_to_bag_map.get(index, (None, None))
                    
                    if bag is None or slot is None:
                        continue
                
                    Inventory.MoveItem(item.id, bag.value, slot, item.quantity)
                
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree.ActionNode(name="Inventory.SortBags", action_fn=_sort, aftercast_ms=aftercast_ms)

    class Crafting:
        @staticmethod
        def CraftItemByOutputModel(
            output_model_id: int,
            cost: int,
            trade_item_ids: list[int],
            trade_item_quantities: list[int],
            aftercast_ms: int = 250,
        ):
            def _craft():
                offered_items = Trading.Crafter.GetOfferedItems()
                output_item_id = next((iid for iid in offered_items if Item.GetModelID(iid) == output_model_id), 0)
                if output_item_id <= 0:
                    return BehaviorTree.NodeState.FAILURE

                k = min(len(trade_item_ids), len(trade_item_quantities))
                if k == 0:
                    return BehaviorTree.NodeState.FAILURE

                Trading.Crafter.CraftItem(output_item_id, cost, trade_item_ids[:k], trade_item_quantities[:k])
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree.ActionNode(name="Crafting.CraftItemByOutputModel", action_fn=_craft, aftercast_ms=aftercast_ms)

        @staticmethod
        def CraftItem(
            output_item_id: int,
            cost: int,
            trade_item_ids: list[int],
            trade_item_quantities: list[int],
            aftercast_ms: int = 250,
        ):
            def _craft():
                k = min(len(trade_item_ids), len(trade_item_quantities))
                if output_item_id <= 0 or k == 0:
                    return BehaviorTree.NodeState.FAILURE
                Trading.Crafter.CraftItem(output_item_id, cost, trade_item_ids[:k], trade_item_quantities[:k])
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree.ActionNode(name="Crafting.CraftItem", action_fn=_craft, aftercast_ms=aftercast_ms)

        @staticmethod
        def CraftItems(
            recipes: list[dict[str, Any]] | None = None,
            recipes_key: str = "craft_recipes",
            aftercast_ms: int = 250,
        ):
            def _craft(node: BehaviorTree.Node):
                payload = recipes if recipes is not None else node.blackboard.get(recipes_key, [])
                if not payload:
                    return BehaviorTree.NodeState.FAILURE

                crafted_any = False
                for recipe in payload:
                    output_item_id = int(recipe.get("output_item_id", 0))
                    cost = int(recipe.get("cost", 0))
                    item_ids = recipe.get("trade_item_ids", [])
                    quantities = recipe.get("trade_item_quantities", [])
                    k = min(len(item_ids), len(quantities))
                    if output_item_id <= 0 or k == 0:
                        continue
                    Trading.Crafter.CraftItem(output_item_id, cost, item_ids[:k], quantities[:k])
                    crafted_any = True

                return BTNodes._success_if(crafted_any)

            return BehaviorTree.ActionNode(name="Crafting.CraftItems", action_fn=_craft, aftercast_ms=aftercast_ms)
