from __future__ import annotations

import time
from enum import IntEnum
from typing import Any, Callable, cast

import Py4GW
import PyInventory

from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Bag, Item
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE
from Sources.frenkeyLib.ItemHandling.Rules.types import SalvageMode
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions


class BTNodes:
    NodeState = BehaviorTree.NodeState
    INVENTORY_BAGS = [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2]
    SALVAGE_WINDOW_HASH = 684387150
    LESSER_CONFIRM_HASH = 140452905

    @staticmethod
    def _success_if(condition: bool) -> BehaviorTree.NodeState:
        return BehaviorTree.NodeState.SUCCESS if condition else BehaviorTree.NodeState.FAILURE

    @staticmethod
    def _resolve_item_ids(node: BehaviorTree.Node, item_ids: list[int] | None, item_ids_key: str) -> list[int]:
        if item_ids is not None:
            return [iid for iid in item_ids if iid]
        value = node.blackboard.get(item_ids_key, [])
        return [iid for iid in value if iid]

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
        inventory_item_ids = [item_id for item_id, _, _ in BTNodes._iter_bag_items(BTNodes.INVENTORY_BAGS)]
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
            item_ids_key: str = "item_ids",
            fail_if_no_kit: bool = True,
            succeed_if_already_identified: bool = True,
            aftercast_ms: int = 150,
        ):
            def _identify(node: BehaviorTree.Node):
                ids = BTNodes._resolve_item_ids(node, item_ids, item_ids_key)
                if not ids:
                    return BehaviorTree.NodeState.FAILURE

                identified_any = False
                items = [ITEM_CACHE.get_item_snapshot(iid) for iid in ids]
                
                for item in items:
                    if item is None:
                        continue
                    
                    if item.is_identified:
                        if succeed_if_already_identified:
                            identified_any = True
                            
                        continue
                    
                    kit_id = Inventory.GetFirstIDKit()
                    
                    if kit_id == 0:
                        return BehaviorTree.NodeState.FAILURE if fail_if_no_kit else BTNodes._success_if(identified_any)
                    
                    Inventory.IdentifyItem(item.id, kit_id)
                    identified_any = True

                return BTNodes._success_if(identified_any or all(item.is_identified for item in items if item is not None))

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
                
                if (state and item_id != state.item_id) or item is None or not item.is_valid or not item.is_salvageable or not item.is_inventory_item:
                    _reset_state(node)                        
                    return BehaviorTree.NodeState.SUCCESS
                
                if state is None:
                    state = BTNodes.Items.SavalvageProgress(item_id=item.id, salvage_started_at=0.0, initial_qty=item.quantity)                   
                    node.blackboard[state_key] = state
                    
                now = time.monotonic()

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
                
                windows_closed_after_confirm = (
                    confirm_clicked_at > 0.0
                    and not UIManagerExtensions.AnySalvageRelatedWindowOpen()
                    and (now - confirm_clicked_at) >= 0.20
                )

                if qty_changed or item_gone or windows_closed_after_confirm:
                    return BehaviorTree.NodeState.SUCCESS

                if (now - float(state.salvage_started_at)) * 1000 >= timeout_ms_per_item:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree.ActionNode(name="Items.SalvageItems", action_fn=_salvage, aftercast_ms=aftercast_ms)

        @staticmethod
        def DestroyItems(
            item_ids: list[int] | None = None,
            item_ids_key: str = "item_ids",
            aftercast_ms: int = 100,
        ):
            def _destroy(node: BehaviorTree.Node):
                ids = BTNodes._resolve_item_ids(node, item_ids, item_ids_key)
                if not ids:
                    return BehaviorTree.NodeState.FAILURE

                destroyed_any = False
                for item_id in ids:
                    Inventory.DestroyItem(item_id)
                    destroyed_any = True

                return BTNodes._success_if(destroyed_any)

            return BehaviorTree.ActionNode(name="Items.DestroyItems", action_fn=_destroy, aftercast_ms=aftercast_ms)

        @staticmethod
        def DepositItems(
            item_ids: list[int] | None = None,
            item_ids_key: str = "item_ids",
            anniversary_panel: bool = True,
            aftercast_ms: int = 200,
        ):
            def _deposit(node: BehaviorTree.Node):
                moved_any = False
                return BTNodes._success_if(moved_any)

            return BehaviorTree.ActionNode(name="Items.DepositItems", action_fn=_deposit, aftercast_ms=aftercast_ms)

    class InventoryOps:
        @staticmethod
        def CompactInventory(
            bags: list[Bag] | None = None,
            max_stack_size: int = 250,
            aftercast_ms: int = 150,
        ):
            def _compact():
                bag_list = bags if bags is not None else BTNodes.INVENTORY_BAGS
                items = BTNodes._iter_bag_items(bag_list)

                by_model: dict[int, list[int]] = {}
                for item_id, _, _ in items:
                    if not Item.Customization.IsStackable(item_id):
                        continue
                    by_model.setdefault(Item.GetModelID(item_id), []).append(item_id)

                moved_any = False
                for _, stack_ids in by_model.items():
                    while True:
                        # Refresh quantities each round; item IDs can vanish after merges.
                        live = []
                        for stack_id in stack_ids:
                            qty = Item.Properties.GetQuantity(stack_id)
                            if qty > 0:
                                live.append((stack_id, qty))
                        if len(live) <= 1:
                            break

                        live.sort(key=lambda x: x[1])  # small -> large
                        src_id, src_qty = live[0]
                        dst_id, dst_qty = next((i, q) for i, q in reversed(live) if q < max_stack_size)
                        to_move = min(src_qty, max_stack_size - dst_qty)
                        if to_move <= 0:
                            break

                        dst_bag, dst_slot = Inventory.FindItemBagAndSlot(dst_id)
                        if dst_bag is None or dst_slot is None:
                            break

                        Inventory.MoveItem(src_id, dst_bag, dst_slot, to_move)
                        moved_any = True

                return BTNodes._success_if(moved_any)

            return BehaviorTree.ActionNode(name="Inventory.CompactInventory", action_fn=_compact, aftercast_ms=aftercast_ms)

        @staticmethod
        def SortInventory(
            bags: list[Bag] | None = None,
            sort_mode: str = "type_rarity_model_value",
            descending: bool = False,
            aftercast_ms: int = 150,
        ):
            def _sort():
                bag_list = bags if bags is not None else BTNodes.INVENTORY_BAGS
                sizes = BTNodes._bag_sizes(bag_list)
                items = [item_id for item_id, _, _ in BTNodes._iter_bag_items(bag_list)]
                if not items:
                    return BehaviorTree.NodeState.FAILURE

                key_fn = BTNodes._build_sort_key(sort_mode)
                sorted_items = sorted(items, key=key_fn, reverse=descending)

                target_slots: list[tuple[Bag, int]] = []
                for bag in bag_list:
                    for slot in range(sizes[bag]):
                        target_slots.append((bag, slot))

                moved_any = False
                for idx, item_id in enumerate(sorted_items):
                    if idx >= len(target_slots):
                        break
                    target_bag, target_slot = target_slots[idx]
                    cur_bag, cur_slot = Inventory.FindItemBagAndSlot(item_id)
                    if cur_bag is None or cur_slot is None:
                        continue
                    if cur_bag == target_bag.value and cur_slot == target_slot:
                        continue
                    Inventory.MoveItem(item_id, target_bag.value, target_slot, Item.Properties.GetQuantity(item_id))
                    moved_any = True

                return BTNodes._success_if(moved_any)

            return BehaviorTree.ActionNode(name="Inventory.SortInventory", action_fn=_sort, aftercast_ms=aftercast_ms)

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
