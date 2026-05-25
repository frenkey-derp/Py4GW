"""
BT routines file notes
======================

This file is both:
- part of the public BT grouped routine surface
- a discovery source for higher-level tooling

Authoring and discovery conventions
-----------------------------------
- Keep existing class names as the system-level grouping surface.
- Use `PascalCase` for public/front-facing routine methods.
- Use `snake_case` for helper/internal methods.
- Use `_snake_case` for explicitly private helpers.
- Keep helper/internal methods out of the public discovery surface.

Routine docstring template
--------------------------
Each user-facing routine method should use:
- a free human-readable description first
- a structured `Meta:` block after it

Template:

    \"\"\"
    One or more human-readable paragraphs explaining what the routine builds.

    Meta:
      Expose: true
      Audience: beginner
      Display: Loot Item
      Purpose: Build a tree that interacts with a target item flow.
      UserDescription: Use this when you want to perform a common item interaction routine.
      Notes: Keep metadata single-line. Structural truth should stay in code.
    \"\"\"

Docstring parsing rules
-----------------------
- Only the `Meta:` section is intended for machine parsing.
- Keep metadata lines single-line and in `Key: Value` form.
- Unknown keys should be safe for tooling to ignore.
- Prefer adding presentation/help metadata in docstrings instead of duplicating
  structural metadata that already exists in code.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from collections.abc import Sequence
from typing import Callable, Optional, cast
from unittest import case

from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Item
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.item_data.ItemData import MATERIAL_STORAGE_SLOTS
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.SortingConfig import BagSortPlan, BagSortPreviewEntry, SlotGroupConfig, SortingConfig

from ...Agent import Agent
from ...GlobalCache import GLOBAL_CACHE
from ...GlobalCache.WhiteboardLocks import clear_loot_lock, post_loot_lock
from ...Map import Map
from ...Player import Player
from ...Py4GWcorelib import ConsoleLog, Console
from ...UIManager import AnySalvageWindow, CrafterWindow, ExpertSalvageUnidentifiedWindow, LesserSalvageWindow, MerchantWindow, SalvageConfirmationPopup, SalvageOptionsWindow, TraderWindow, UIManager
from ...enums import CONSUMABLE_MODELID_TO_EFFECT_NAME
from ...enums_src.Item_enums import INVENTORY_BAGS, INVENTORY_WITH_EQUIPMENT_BAGS, MAX_GOLD_CHARACTER, MAX_GOLD_STORAGE, MAX_STACK_SIZE, STORAGE_BAGS, Bags, ItemType, Rarity, SalvageMode, TradingNPCType
from ...enums_src.Model_enums import ModelID
from ...enums_src.UI_enums import ControlAction
from ...py4gwcorelib_src.Lootconfig_src import LootConfig
from ...py4gwcorelib_src.BehaviorTree import BehaviorTree
from .composite import BTComposite
from .player import BTPlayer


def _log(source: str, message: str, *, log: bool = False, message_type=Console.MessageType.Info) -> None:
    ConsoleLog(source, message, message_type, log=log)


def _fail_log(source: str, message: str, message_type=Console.MessageType.Warning) -> None:
    ConsoleLog(source, message, message_type, log=True)


def _success_if(condition: bool) -> BehaviorTree.NodeState:
    """
    Convert a boolean condition into a success-or-failure node state.

    Meta:
        Expose: false
        Audience: advanced
        Display: Internal Success If Helper
        Purpose: Normalize simple boolean results into `BehaviorTree.NodeState` values for helper routines.
        UserDescription: Internal support routine.
        Notes: Returns success for truthy input and failure for falsy input.
    """
    return BehaviorTree.NodeState.SUCCESS if condition else BehaviorTree.NodeState.FAILURE

def get_item_name(item_id: int) -> str:
    item = ItemSnapshot.from_item_id(item_id)
    return item.names.plain if item and item.names.plain != item.names.fallback else f"Item (ID: {item_id})"

ItemIdentifier = ModelID | int | list[int] | bytes | tuple[int | ModelID, ItemType] | str

class BTItems:
    """
    Public BT helper group for inventory and item-management routines.

    Meta:
      Expose: true
      Audience: advanced
      Display: Items
      Purpose: Group public BT routines related to inventory item spawning, movement, destruction, and lookup.
      UserDescription: Built-in BT helper group for item and inventory routines.
      Notes: Public `PascalCase` methods in this class are discovery candidates when marked exposed.
    """
    BONUS_ITEM_MODELS : list[tuple[int, ItemType]]= [
        (ModelID.Bonus_Luminescent_Scepter, ItemType.Wand),
        (ModelID.Bonus_Nevermore_Flatbow, ItemType.Bow),
        (ModelID.Bonus_Rhinos_Charge, ItemType.Hammer),
        (ModelID.Bonus_Serrated_Shield, ItemType.Shield),
        (ModelID.Bonus_Soul_Shrieker, ItemType.Staff),
        (ModelID.Bonus_Tigers_Roar, ItemType.Offhand),
        (ModelID.Bonus_Wolfs_Favor, ItemType.Offhand),
        (ModelID.Igneous_Summoning_Stone, ItemType.Usable),
    ]

    @staticmethod
    def _resolve_model_id_value(modelID_or_encStr: int | str) -> int:
        if isinstance(modelID_or_encStr, str):
            return Agent.GetModelIDByEncString(modelID_or_encStr)
        return int(modelID_or_encStr)

    @staticmethod
    def EquipInventoryBag(
        modelID_or_encStr: int | str,
        target_bag: int,
        timeout_ms: int = 2500,
        poll_interval_ms: int = 125,
        log: bool = False,
    ) -> BehaviorTree:
        """
        Build a tree that equips an inventory bag item into the requested bag slot.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Equip Inventory Bag
          Purpose: Equip an inventory bag item into a specific bag slot.
          UserDescription: Use this when you want to equip a belt pouch or bag from inventory into its container slot.
          Notes: Mirrors the bag-equip helper flow, including the backpack-slot fallback when native item use does not populate the target bag.
        """
        from ...Py4GWcorelib import Utils

        inventory_frame_hash = 291586130
        state = {
            "stage": "init",
            "resolved_model_id": 0,
            "item_id": 0,
            "native_deadline_ms": 0,
            "final_deadline_ms": 0,
            "next_check_ms": 0,
            "key_up_ms": 0,
        }

        def _reset_state() -> None:
            state["stage"] = "init"
            state["resolved_model_id"] = 0
            state["item_id"] = 0
            state["native_deadline_ms"] = 0
            state["final_deadline_ms"] = 0
            state["next_check_ms"] = 0
            state["key_up_ms"] = 0

        def _bag_is_populated() -> bool:
            target_container_item = GLOBAL_CACHE.Inventory.GetBagContainerItem(target_bag)
            target_bag_size = GLOBAL_CACHE.Inventory.GetBagSize(target_bag)
            return target_container_item != 0 or target_bag_size > 0

        def _get_backpack_slot_frame_id() -> int:
            return UIManager.GetChildFrameID(
                inventory_frame_hash,
                [0, 0, 0, Bags.Backpack - 1, 2],
            )

        def _equip_inventory_bag(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            now = int(Utils.GetBaseTimestamp())

            if _bag_is_populated():
                _reset_state()
                return BehaviorTree.NodeState.SUCCESS

            if state["stage"] == "init":
                resolved_model_id = BTItems._resolve_model_id_value(modelID_or_encStr)
                item_id = GLOBAL_CACHE.Inventory.GetFirstModelID(resolved_model_id)
                if item_id == 0:
                    _fail_log("EquipInventoryBag", f"Item model {resolved_model_id} not found in inventory.", Console.MessageType.Error)
                    _reset_state()
                    return BehaviorTree.NodeState.FAILURE

                GLOBAL_CACHE.Inventory.UseItem(item_id)
                state["stage"] = "wait_native"
                state["resolved_model_id"] = resolved_model_id
                state["item_id"] = item_id
                state["native_deadline_ms"] = now + min(timeout_ms, 250)
                state["final_deadline_ms"] = now + timeout_ms
                state["next_check_ms"] = now + poll_interval_ms
                node.blackboard["equip_inventory_bag_last_model_id"] = resolved_model_id
                node.blackboard["equip_inventory_bag_last_item_id"] = item_id
                return BehaviorTree.NodeState.RUNNING

            if state["stage"] == "wait_native":
                if now < int(state["next_check_ms"]):
                    return BehaviorTree.NodeState.RUNNING

                if now <= int(state["native_deadline_ms"]):
                    state["next_check_ms"] = now + poll_interval_ms
                    return BehaviorTree.NodeState.RUNNING

                if GLOBAL_CACHE.Inventory.MoveModelToBagSlot(int(state["resolved_model_id"]), Bags.Backpack, 0):
                    _log(
                        "EquipInventoryBag",
                        f"Native UseItem did not populate bag {target_bag}; trying backpack slot double-click fallback for model {int(state['resolved_model_id'])}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    state["stage"] = "fallback_wait_before_open"
                    state["next_check_ms"] = now + poll_interval_ms
                else:
                    _log(
                        "EquipInventoryBag",
                        f"Fallback move to backpack slot 0 failed for model {int(state['resolved_model_id'])}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    state["stage"] = "final_wait"
                    state["next_check_ms"] = now + poll_interval_ms

                return BehaviorTree.NodeState.RUNNING

            if state["stage"] == "fallback_wait_before_open":
                if now < int(state["next_check_ms"]):
                    return BehaviorTree.NodeState.RUNNING

                if not GLOBAL_CACHE.Inventory.IsInventoryBagsOpen():
                    UIManager.Keydown(ControlAction.ControlAction_ToggleAllBags.value, 0)
                    state["stage"] = "fallback_toggle_bags_release"
                    state["key_up_ms"] = now + 75
                    return BehaviorTree.NodeState.RUNNING

                state["stage"] = "fallback_wait_before_double_click"
                state["next_check_ms"] = now + poll_interval_ms
                return BehaviorTree.NodeState.RUNNING

            if state["stage"] == "fallback_toggle_bags_release":
                if now < int(state["key_up_ms"]):
                    return BehaviorTree.NodeState.RUNNING

                UIManager.Keyup(ControlAction.ControlAction_ToggleAllBags.value, 0)
                state["stage"] = "fallback_wait_before_double_click"
                state["next_check_ms"] = now + poll_interval_ms
                return BehaviorTree.NodeState.RUNNING

            if state["stage"] == "fallback_wait_before_double_click":
                if now < int(state["next_check_ms"]):
                    return BehaviorTree.NodeState.RUNNING

                frame_id = _get_backpack_slot_frame_id()
                if not UIManager.FrameExists(frame_id):
                    _fail_log("EquipInventoryBag", "Frame does not exist for backpack slot 0.", Console.MessageType.Error)
                    _reset_state()
                    return BehaviorTree.NodeState.FAILURE

                UIManager.TestMouseAction(frame_id=frame_id, current_state=9, wparam_value=0, lparam_value=0)
                state["stage"] = "fallback_double_click_confirm"
                state["next_check_ms"] = now + 60
                return BehaviorTree.NodeState.RUNNING

            if state["stage"] == "fallback_double_click_confirm":
                if now < int(state["next_check_ms"]):
                    return BehaviorTree.NodeState.RUNNING

                frame_id = _get_backpack_slot_frame_id()
                if not UIManager.FrameExists(frame_id):
                    _fail_log("EquipInventoryBag", "Frame does not exist for backpack slot 0.", Console.MessageType.Error)
                    _reset_state()
                    return BehaviorTree.NodeState.FAILURE

                UIManager.TestMouseClickAction(frame_id=frame_id, current_state=9, wparam_value=0, lparam_value=0)
                state["stage"] = "final_wait"
                state["next_check_ms"] = now + 60
                return BehaviorTree.NodeState.RUNNING

            if state["stage"] == "final_wait":
                if now < int(state["next_check_ms"]):
                    return BehaviorTree.NodeState.RUNNING

                if _bag_is_populated():
                    _reset_state()
                    return BehaviorTree.NodeState.SUCCESS

                if now <= int(state["final_deadline_ms"]):
                    state["next_check_ms"] = now + poll_interval_ms
                    return BehaviorTree.NodeState.RUNNING

                _fail_log(
                    "EquipInventoryBag",
                    (
                        f"Failed to equip model {int(state['resolved_model_id'])} item {int(state['item_id'])} into bag {target_bag} within {timeout_ms}ms. "
                        f"container_item={GLOBAL_CACHE.Inventory.GetBagContainerItem(target_bag)} "
                        f"size={GLOBAL_CACHE.Inventory.GetBagSize(target_bag)}."
                    ),
                    Console.MessageType.Error,
                )
                _reset_state()
                return BehaviorTree.NodeState.FAILURE

            _reset_state()
            return BehaviorTree.NodeState.FAILURE

        return BehaviorTree(
            BehaviorTree.ConditionNode(
                name=f"EquipInventoryBag({modelID_or_encStr}, {target_bag})",
                condition_fn=_equip_inventory_bag,
            )
        )

    @staticmethod
    def GetItemNameByItemID(item_id: int, log: bool = False) -> BehaviorTree:
        """
        Build a tree that requests and retrieves an item name by item id.

        Meta:
          Expose: true
          Audience: advanced
          Display: Get Item Name By Item ID
          Purpose: Request an item name and store the resolved name on the blackboard.
          UserDescription: Use this when you need the item name text for a known item id during tree execution.
          Notes: Stores the resolved name in `blackboard['result']` and waits up to 2000ms for the name to become ready.
        """
        def _request_item_name(node):
            """
            Request item-name resolution for the provided item id.

            Meta:
              Expose: false
              Audience: advanced
              Display: Internal Request Item Name Helper
              Purpose: Dispatch the item-name request before the wait step begins.
              UserDescription: Internal support routine.
              Notes: Returns success immediately after sending the request.
            """
            GLOBAL_CACHE.Item.RequestName(item_id)
            _log(
                "GetItemNameByItemID",
                f"Requested item name for item_id={item_id}.",
                log=log,
            )
            return BehaviorTree.NodeState.SUCCESS

        def _check_item_name_ready(node):
            """
            Check whether the requested item name has been populated yet.

            Meta:
              Expose: false
              Audience: advanced
              Display: Internal Check Item Name Ready Helper
              Purpose: Gate the repeater until the requested item name is available.
              UserDescription: Internal support routine.
              Notes: Returns failure while the item name is still pending so the repeater keeps waiting.
            """
            if not GLOBAL_CACHE.Item.IsNameReady(item_id):
                return BehaviorTree.NodeState.FAILURE
            return BehaviorTree.NodeState.SUCCESS

        def _get_item_name(node):
            """
            Read the resolved item name and store it on the blackboard.

            Meta:
              Expose: false
              Audience: advanced
              Display: Internal Get Item Name Helper
              Purpose: Store the resolved item name in `blackboard['result']` for later steps.
              UserDescription: Internal support routine.
              Notes: Returns failure if the name is still empty after the ready check sequence.
            """
            name = ''
            if GLOBAL_CACHE.Item.IsNameReady(item_id):
                name = GLOBAL_CACHE.Item.GetName(item_id)

            node.blackboard["result"] = name
            if name:
                _log(
                    "GetItemNameByItemID",
                    f"Resolved item_id={item_id} to '{name}'.",
                    log=log,
                )
            else:
                _log(
                    "GetItemNameByItemID",
                    f"Failed to resolve item name for item_id={item_id} before timeout.",
                    message_type=Console.MessageType.Warning,
                    log=log,
                )
            return BehaviorTree.NodeState.SUCCESS if name else BehaviorTree.NodeState.FAILURE

        tree = BehaviorTree.SequenceNode(
            name="GetItemNameByItemIDRoot",
            children=[
                BehaviorTree.ActionNode(name="RequestItemName", action_fn=_request_item_name),
                BehaviorTree.RepeaterUntilSuccessNode(
                    name="WaitUntilItemNameReadyRepeater",
                    timeout_ms=2000,
                    child=BehaviorTree.SelectorNode(
                        name="WaitUntilItemNameReadySelector",
                        children=[
                            BehaviorTree.ConditionNode(name="CheckItemNameReady", condition_fn=_check_item_name_ready),
                            BehaviorTree.SequenceNode(
                                name="WaitForThrottle",
                                children=[
                                    BehaviorTree.WaitForTimeNode(name="Throttle100ms", duration_ms=100),
                                    BehaviorTree.FailerNode(name="FailToRepeat")
                                ]
                            ),
                        ]
                    )
                ),
                BehaviorTree.ActionNode(name="GetItemName", action_fn=_get_item_name)
            ]
        )
        return BehaviorTree(tree)

    @staticmethod
    def _collect_sellable_inventory_item_ids(exclude_models: list[int] | None = None) -> list[int]:
        excluded_models = set(exclude_models or [])
        sellable_item_ids: list[int] = []

        for item_id in GLOBAL_CACHE.Inventory.GetAllInventoryItemIds():
            if item_id == 0:
                continue

            model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
            if model_id in excluded_models:
                continue

            item_value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
            if item_value <= 0:
                continue

            sellable_item_ids.append(item_id)

        return sellable_item_ids
    
    @staticmethod
    def _collect_zero_value_inventory_item_ids(exclude_models: list[int] | None = None) -> list[int]:
        excluded_models = set(exclude_models or [])
        zero_value_item_ids: list[int] = []

        for item_id in GLOBAL_CACHE.Inventory.GetAllInventoryItemIds():
            if item_id == 0:
                continue

            model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
            if model_id in excluded_models:
                continue

            item_value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
            if item_value > 0:
                continue

            zero_value_item_ids.append(item_id)

        return zero_value_item_ids

    @staticmethod
    def NeedsInventoryCleanup(exclude_models: list[int] | None = None) -> BehaviorTree:
        def _needs_inventory_cleanup() -> bool:
            return bool(BTItems._collect_sellable_inventory_item_ids(exclude_models=exclude_models)) or bool(
                BTItems._collect_zero_value_inventory_item_ids(exclude_models=exclude_models)
            )

        return BehaviorTree(
            BehaviorTree.ConditionNode(
                name="NeedsInventoryCleanupExcluding",
                condition_fn=_needs_inventory_cleanup,
            )
        )

    @staticmethod
    def SellInventoryItems(
        exclude_models: list[int] | None = None,
        log: bool = False,
    ) -> BehaviorTree:
        """
        Build a tree that sells all inventory items with value greater than zero while excluding specified models.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Sell Inventory Items
          Purpose: Sell all inventory items with value greater than zero while excluding specified models.
          UserDescription: Use this when you want to clear out inventory space by selling items but want to keep certain models.
          Notes: Processes all eligible items in a single tick by queuing them up in the merchant action queue; logs the count of sold items if logging is enabled.
        """
        def _collect_items(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            sellable_item_ids = BTItems._collect_sellable_inventory_item_ids(exclude_models=exclude_models)
            node.blackboard["merchant_sell_item_ids"] = sellable_item_ids
            node.blackboard["merchant_sell_queued_count"] = 0

            if not sellable_item_ids:
                _log(
                    "SellInventoryItems",
                    "No eligible inventory items found to sell.",
                    message_type=Console.MessageType.Info,
                    log=log,
                )
                return BehaviorTree.NodeState.SUCCESS

            excluded_models_text = ", ".join(str(model_id) for model_id in sorted(set(exclude_models or []))) or "none"
            _log(
                "SellInventoryItems",
                f"Selling {len(sellable_item_ids)} inventory items. Excluded models: {excluded_models_text}.",
                message_type=Console.MessageType.Info,
                log=log,
            )

            return BehaviorTree.NodeState.SUCCESS

        def _queue_sell_items(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            from Py4GWCoreLib.Py4GWcorelib import ActionQueueManager
            item_ids = list(node.blackboard.get("merchant_sell_item_ids", []))
            if not item_ids:
                node.blackboard["merchant_sell_queued_count"] = 0
                return BehaviorTree.NodeState.SUCCESS

            merchant_queue = ActionQueueManager()
            merchant_queue.ResetQueue("ACTION")

            queued_count = 0
            for item_id in item_ids:
                quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)
                value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
                cost = quantity * value

                if quantity <= 0 or value <= 0:
                    continue

                merchant_queue.AddAction(
                    "ACTION",
                    GLOBAL_CACHE.Trading._merchant_instance.merchant_sell_item,
                    item_id,
                    cost,
                )
                queued_count += 1

            node.blackboard["merchant_sell_queued_count"] = queued_count
            return BehaviorTree.NodeState.SUCCESS

        def _wait_for_sell_queue_to_finish(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            from Py4GWCoreLib.Py4GWcorelib import ActionQueueManager
            queued_count = int(node.blackboard.get("merchant_sell_queued_count", 0) or 0)
            if queued_count <= 0:
                return BehaviorTree.NodeState.SUCCESS

            if not ActionQueueManager().IsEmpty("ACTION"):
                return BehaviorTree.NodeState.RUNNING

            _log(
                "SellInventoryItems",
                f"Sold {queued_count} inventory items through merchant queue.",
                message_type=Console.MessageType.Info,
                log=log,
            )
            return BehaviorTree.NodeState.SUCCESS

        tree = BehaviorTree.SequenceNode(
            name="SellInventoryItemsExcluding",
            children=[
                BehaviorTree.ActionNode(
                    name="CollectSellableInventoryItems",
                    action_fn=_collect_items,
                    aftercast_ms=0,
                ),
                BehaviorTree.ActionNode(
                    name="QueueMerchantSellItems",
                    action_fn=_queue_sell_items,
                    aftercast_ms=0,
                ),
                BehaviorTree.ActionNode(
                    name="WaitForMerchantSellQueue",
                    action_fn=_wait_for_sell_queue_to_finish,
                    aftercast_ms=0,
                ),
            ],
        )
        return BehaviorTree(tree)

    @staticmethod
    def DestroyZeroValueItems(
        exclude_models: list[int] | None = None,
        log: bool = False,
        aftercast_ms: int = 250,
    ) -> BehaviorTree:
        state = {
            "next_attempt_ms": 0,
        }

        def _collect_items(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            zero_value_item_ids = BTItems._collect_zero_value_inventory_item_ids(exclude_models=exclude_models)
            node.blackboard["zero_value_destroy_item_ids"] = zero_value_item_ids
            node.blackboard["zero_value_destroy_index"] = 0
            if zero_value_item_ids:
                _log(
                    "DestroyZeroValueItems",
                    f"Found {len(zero_value_item_ids)} zero-value items to destroy.",
                    log=log,
                )
            else:
                _log(
                    "DestroyZeroValueItems",
                    "No zero-value items found to destroy.",
                    log=log,
                )
            return BehaviorTree.NodeState.SUCCESS

        def _destroy_items(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            from Py4GWCoreLib.Py4GWcorelib import Utils
            now = Utils.GetBaseTimestamp()
            if now < int(state["next_attempt_ms"]):
                return BehaviorTree.NodeState.RUNNING

            item_ids = list(node.blackboard.get("zero_value_destroy_item_ids", []))
            item_index = int(node.blackboard.get("zero_value_destroy_index", 0) or 0)
            if item_index >= len(item_ids):
                return BehaviorTree.NodeState.SUCCESS

            item_id = item_ids[item_index]
            model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
            GLOBAL_CACHE.Inventory.DestroyItem(item_id)
            node.blackboard["zero_value_destroy_index"] = item_index + 1
            state["next_attempt_ms"] = int(now + aftercast_ms)

            _log(
                "DestroyZeroValueItems",
                f"Queued destroy for zero-value item model {model_id} (item_id={item_id}).",
                message_type=Console.MessageType.Info,
                log=log,
            )

            return BehaviorTree.NodeState.RUNNING

        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name="DestroyZeroValueItemsExcluding",
                children=[
                    BehaviorTree.ActionNode(
                        name="CollectZeroValueItems",
                        action_fn=_collect_items,
                        aftercast_ms=0,
                    ),
                    BehaviorTree.ConditionNode(
                        name="DestroyZeroValueItems",
                        condition_fn=_destroy_items,
                    ),
                ],
            )
        )

    class Utility:
        @staticmethod
        def GetModelIDFromIdentifier(identifier: ItemIdentifier) -> Optional[int]:
            if isinstance(identifier, int):
                return identifier
            
            if isinstance(identifier, ModelID):
                return int(identifier)
            
            if isinstance(identifier, tuple):
                model_id, _ = identifier
                return int(model_id)
            
            return None
        
        @staticmethod
        def GetItemID(identifier : ItemIdentifier, bags : Optional[list[Bags]|Bags] = None) -> int:       
            """
            Get the item id of the first inventory item matching the provided parameter, which can be one of:
            - model id (int | ModelID)
            - encoded item name (bytes | list[int])
            - item name (str)
            - tuple of model id and item type (tuple[int | ModelID, ItemType])
            """
            
            bags = [bags] if isinstance(bags, Bags) else bags
            bags = bags if bags else [
                *INVENTORY_WITH_EQUIPMENT_BAGS,
                Bags.UnclaimedItems,
                Bags.EquippedItems,
                *STORAGE_BAGS,
                Bags.MaterialStorage,
                Bags.NoBag                
            ]
            
            for bag in bags:
                for item in ItemSnapshot.get_bag_snapshot(bag).values():
                    if item is None or not item.is_valid:
                        continue
                                            
                    match identifier:
                        case int() | ModelID():
                            if item.model_id == identifier:
                                return item.id
                        
                        case list():
                            if item.name_enc == bytes(identifier):
                                return item.id
                            
                        case bytes():
                            if item.name_enc == identifier:
                                return item.id
                        
                        case str():
                            if item.name == identifier or item.singular_name == identifier:
                                return item.id
                        
                        case tuple() if len(identifier) == 2:
                            model_id, item_type = identifier
                            if item.model_id == model_id and item.item_type == item_type:
                                return item.id
                            
            return 0

        @staticmethod
        def IdentifierMatchesItem(identifier: ItemIdentifier, item_id: int | ItemSnapshot) -> bool:
            if item_id == 0:
                return False
            
            item_snapshot = ItemSnapshot.from_item_id(item_id) if not isinstance(item_id, ItemSnapshot) else item_id
            if item_snapshot is None or not item_snapshot.is_valid:
                return False
            
            match identifier:
                case int() | ModelID():
                    return item_snapshot.model_id == identifier
                
                case list():
                    return item_snapshot.name_enc == bytes(identifier)
                
                case bytes():
                    return item_snapshot.name_enc == identifier
                
                case str():
                    return item_snapshot.name == identifier or item_snapshot.singular_name == identifier
                
                case tuple() if len(identifier) == 2:
                    model_id, expected_item_type = identifier
                    return item_snapshot.model_id == model_id and item_snapshot.item_type == expected_item_type
                
            return False
        
        @staticmethod
        def ResolveItemIDFromNPCThen(
            identifier: ItemIdentifier,
            next_node_fn: Callable[[int], BehaviorTree | BehaviorTree.Node],
            npc_type : TradingNPCType = TradingNPCType.Unknown,
            fail_if_none_resolved: bool = True,            
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a tree that resolves an item id from the currently open trader window based on the provided identifier.

            Meta:
              Expose: true
              Audience: advanced
              Display: Resolve Item ID From Trader Then
              Purpose: Resolve an item id from the currently open trader window based on the provided identifier.
              UserDescription: Use this when you need to resolve an item id from the trader's offered items based on model id, item name, or encoded name.
              Notes: Stores the resolved id on the blackboard and fails if no matching item is found.
            """
            def _resolve_item_id_from_trader(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                item_id = 0
                offered_item_ids = [
                    *(Trading.Trader.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Trader) else []),
                    *(Trading.Trader.GetOfferedItems2() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Trader) else []),
                    *(Trading.Collector.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Collector) else []),
                    *(Trading.Crafter.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Crafter) else []),
                    *(Trading.Merchant.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Merchant) else []),
                ]
                
                items = ItemSnapshot.get_items(offered_item_ids)
                for item in items:
                    if BTItems.Utility.IdentifierMatchesItem(identifier, item) :
                        item_id = item.id
                        break

                node.blackboard['resolved_item_id'] = item_id
                _log(
                    "ResolveItemIDFromNPCThen",
                    f"Resolved item id {item_id} from trader {npc_type.name} for identifier {identifier}.",
                    message_type=Console.MessageType.Info,
                    log=log,
                )
                
                if fail_if_none_resolved:
                    return BehaviorTree.NodeState.SUCCESS if item_id else BehaviorTree.NodeState.FAILURE
                else:
                    return BehaviorTree.NodeState.SUCCESS

            tree = BehaviorTree.SequenceNode(
                name=f"ResolveItemIDFromTrader({identifier})",
                children=[
                    BehaviorTree.ActionNode(
                        name=f"ResolveItemIDFromTraderAction({identifier})",
                        action_fn=_resolve_item_id_from_trader,
                    ),
                    BehaviorTree.SubtreeNode(
                        name=f"ResolvedItemContinuation({identifier})",
                        subtree_fn=lambda node: next_node_fn(int(node.blackboard.get('resolved_item_id', 0) or 0)),
                    ),
                ],
            )
            return BehaviorTree(tree)
        
        @staticmethod
        def ResolveItemIDsFromNPCThen(
            identifiers: list[ItemIdentifier],
            next_node_fn: Callable[[list[int]], BehaviorTree | BehaviorTree.Node],
            npc_type : TradingNPCType = TradingNPCType.Unknown,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a tree that resolves multiple item ids from the currently open trader window based on the provided identifiers.

            Meta:
              Expose: true
              Audience: advanced
              Display: Resolve Item IDs From Trader Then
              Purpose: Resolve multiple item ids from the currently open trader window based on the provided identifiers.
              UserDescription: Use this when you need to resolve multiple item ids from the trader's offered items based on model ids, item names, or encoded names.
              Notes: Stores the resolved ids on the blackboard and fails if any identifier does not match a found item.
            """
            def _resolve_item_ids_from_trader(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                resolved_item_ids = []
                offered_item_ids = [
                    *(Trading.Trader.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Trader) else []),
                    *(Trading.Trader.GetOfferedItems2() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Trader) else []),
                    *(Trading.Collector.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Collector) else []),
                    *(Trading.Crafter.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Crafter) else []),
                    *(Trading.Merchant.GetOfferedItems() if npc_type in (TradingNPCType.Unknown, TradingNPCType.Merchant) else []),
                ]
                
                items = ItemSnapshot.get_items(offered_item_ids)
                for identifier in identifiers:
                    item_id = 0
                    for item in items:
                        if BTItems.Utility.IdentifierMatchesItem(identifier, item):
                            item_id = item.id
                            break
                    resolved_item_ids.append(item_id)

                node.blackboard['resolved_item_ids'] = resolved_item_ids
                _log(
                    "ResolveItemIDsFromNPCThen",
                    f"Resolved item ids {resolved_item_ids} from trader {npc_type.name} for identifiers {identifiers}.",
                    message_type=Console.MessageType.Info if all(resolved_item_ids) else Console.MessageType.Warning,
                    log=log,
                )
                return BehaviorTree.NodeState.SUCCESS if all(resolved_item_ids) else BehaviorTree.NodeState.FAILURE

            tree = BehaviorTree.SequenceNode(
                name=f"ResolveItemIDsFromTrader({identifiers})",
                children=[
                    BehaviorTree.ActionNode(
                        name=f"ResolveItemIDsFromTraderAction({identifiers})",
                        action_fn=_resolve_item_ids_from_trader,
                    ),
                    BehaviorTree.SubtreeNode(
                        name=f"ResolvedItemsContinuation({identifiers})",
                        subtree_fn=lambda node: next_node_fn([int(i) for i in node.blackboard.get('resolved_item_ids', [])]),
                    ),
                ],
            )
            return BehaviorTree(tree)
        
        @staticmethod
        def ResolveItemIDThen(
            identifier: ItemIdentifier,
            next_node_fn: Callable[[int], BehaviorTree | BehaviorTree.Node],
            bags: Optional[list[Bags] | Bags] = None,
            fail_if_none_resolved: bool = True,            
            blackboard_key: str = 'resolved_item_id',
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a tree that resolves an item id at runtime and then continues with a dynamic child node.

            Meta:
              Expose: true
              Audience: advanced
              Display: Resolve Item ID Then
              Purpose: Resolve an item id from item lookup input and pass it into a follow-up BT node factory.
              UserDescription: Use this when a later BT step needs a live item id resolved from model id, item name, or encoded name.
              Notes: Stores the resolved id on the blackboard and fails if no matching item is found.
            """

            def _resolve_item_id(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                item_id = BTItems.Utility.GetItemID(identifier, bags=bags)
                node.blackboard[blackboard_key] = item_id
                _log(
                    "ResolveItemIDThen",
                    f"Resolved identifier {identifier} to item_id={item_id} using bags={bags}.",
                    message_type=Console.MessageType.Info if item_id else Console.MessageType.Warning,
                    log=log,
                )
                if fail_if_none_resolved:
                    return BehaviorTree.NodeState.SUCCESS if item_id else BehaviorTree.NodeState.FAILURE
                else:
                    return BehaviorTree.NodeState.SUCCESS

            tree = BehaviorTree.SequenceNode(
                name='ResolveItemIDThenRoot',
                children=[
                    BehaviorTree.ActionNode(
                        name=f'ResolveItemID({identifier})',
                        action_fn=_resolve_item_id,
                    ),
                    BehaviorTree.SubtreeNode(
                        name=f'ResolvedItemContinuation({identifier})',
                        subtree_fn=lambda node: next_node_fn(int(node.blackboard.get(blackboard_key, 0) or 0)),
                    ),
                ],
            )
            return BehaviorTree(tree)

        @staticmethod
        def ResolveItemIdsThen(
            identifiers: list[ItemIdentifier],
            next_node_fn: Callable[[list[int]], BehaviorTree | BehaviorTree.Node],
            bags: Optional[list[Bags] | Bags] = None,
            allow_partial: bool = False,
            fail_if_none_resolved: bool = True,
            blackboard_key: str = 'resolved_item_ids',
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a tree that resolves multiple item ids at runtime and then continues with a dynamic child node.

            Meta:
              Expose: true
              Audience: advanced
              Display: Resolve Item IDs Then
              Purpose: Resolve multiple item ids from item lookup input and pass them into a follow-up BT node factory.
              UserDescription: Use this when a later BT step needs live item ids resolved from model ids, item names, or encoded names.
              Notes: Stores the resolved ids on the blackboard and fails if no matching items are found.
            """
            
            def _resolve_item_ids(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                item_ids = [BTItems.Utility.GetItemID(identifier, bags=bags) for identifier in identifiers]
                node.blackboard[blackboard_key] = item_ids
                _log(
                    "ResolveItemIdsThen",
                    f"Resolved identifiers {identifiers} to item ids {item_ids} using bags={bags}.",
                    message_type=Console.MessageType.Info if any(item_ids) else Console.MessageType.Warning,
                    log=log,
                )
                
                partial_match = any(item_ids)
                all_match = all(item_ids)
                
                if fail_if_none_resolved and not partial_match:
                    return BehaviorTree.NodeState.FAILURE
                
                elif allow_partial:
                    return BehaviorTree.NodeState.SUCCESS
                
                else:
                    return BehaviorTree.NodeState.SUCCESS if all_match else BehaviorTree.NodeState.FAILURE

            tree = BehaviorTree.SequenceNode(
                name='ResolveItemIDsThenRoot',
                children=[
                    BehaviorTree.ActionNode(
                        name=f'ResolveItemIDs({identifiers})',
                        action_fn=_resolve_item_ids,
                    ),
                    BehaviorTree.SubtreeNode(
                        name=f'ResolvedItemsContinuation({identifiers})',
                        subtree_fn=lambda node: next_node_fn(list(node.blackboard.get(blackboard_key, []))),
                    ),
                ],
            )
            return BehaviorTree(tree)

    class BonusItems:
        """
        This section provides routines for spawning bonus items and optionally destroying them while preserving selected models.\n
        Bonus items are items granted by the game client when the `/bonus` command is issued in chat.
        """
        
        @staticmethod
        def SpawnBonusItems(log: bool = False, aftercast_ms: int = 250) -> BehaviorTree:
            """
            Build a tree that issues the `/bonus` command to spawn bonus items.

            Meta:
            Expose: true
            Audience: beginner
            Display: Spawn Bonus Items
            Purpose: Spawn available bonus items through the `/bonus` command.
            UserDescription: Use this when you want bonus items to appear in inventory before other item routines run.
            Notes: Completes after a configurable aftercast delay to allow the inventory to update.
            """
            def _spawn_bonus_items():
                """
                Issue the `/bonus` command to spawn bonus inventory items.

                Meta:
                Expose: false
                Audience: advanced
                Display: Internal Spawn Bonus Items Helper
                Purpose: Send the `/bonus` chat command for the enclosing item routine.
                UserDescription: Internal support routine.
                Notes: Returns success immediately after sending the command.
                """
                Player.SendChatCommand("bonus")
                _log("SpawnBonusItems", "Sent /bonus command.", message_type=Console.MessageType.Info, log=log)
                return BehaviorTree.NodeState.SUCCESS

            tree = BehaviorTree.ActionNode(
                name="SpawnBonusItems",
                action_fn=_spawn_bonus_items,
                aftercast_ms=aftercast_ms,
            )
            return BehaviorTree(tree)

        @staticmethod
        def DestroyBonusItems(
            exclude_list: Optional[list[int]] = None,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that destroys spawned bonus items except for excluded models.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Destroy Bonus Items
            Purpose: Destroy bonus item models while preserving any excluded models.
            UserDescription: Use this after spawning bonus items when you only want to keep selected bonus models.
            Notes: Runs a composed destroy pass over the known bonus item model list.
            """
            
            bonus_models_to_destroy = [
                model_identifier
                for model_identifier in BTItems.BONUS_ITEM_MODELS
                if exclude_list is None or model_identifier[0] not in exclude_list
            ]

            def _build_destroy_bonus_items_subtree(_: BehaviorTree.Node) -> BehaviorTree:
                item_ids = [
                    BTItems.Utility.GetItemID(model_identifier, bags=INVENTORY_BAGS)
                    for model_identifier in bonus_models_to_destroy
                ]
                resolved_item_ids = [item_id for item_id in item_ids if item_id > 0]

                return BTComposite.Sequence(
                    BTPlayer.PrintMessageToConsole(
                        source="DestroyBonusItems",
                        message=(
                            f"Resolved {len(resolved_item_ids)}/{len(bonus_models_to_destroy)} bonus items for destruction. "
                            f"Target models: {bonus_models_to_destroy}"
                        ),
                    ),
                    BTItems.Items.DestroyItems(
                        item_ids=resolved_item_ids,
                        succeed_always=False,
                        log=log,
                        aftercast_ms=aftercast_ms,
                    ),
                    name="DestroyBonusItemsResolved",
                )

            return BehaviorTree(
                BehaviorTree.SubtreeNode(
                    name="DestroyBonusItems",
                    subtree_fn=_build_destroy_bonus_items_subtree,
                )
            )

        @staticmethod
        def SpawnAndDestroyBonusItems(
            exclude_list: Optional[list[int]] = None,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that spawns bonus items and then destroys all except for excluded models.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Spawn and Destroy Bonus Items
            Purpose: Spawn bonus items and then destroy all except for excluded models.
            UserDescription: Use this when you want to spawn bonus items and then remove unwanted ones.
            Notes: Runs a composed spawn and destroy pass over the known bonus item model list.
            """
            exclude_list = exclude_list or [ModelID.Igneous_Summoning_Stone]
            
            return BTComposite.Sequence(
                BTItems.BonusItems.SpawnBonusItems(log=log, aftercast_ms=aftercast_ms),
                BTPlayer.Wait(250),
                BTItems.BonusItems.DestroyBonusItems(exclude_list=exclude_list, log=log, aftercast_ms=aftercast_ms),
                name="SpawnAndDestroyBonusItems",
            )

    class Consumables:
        @staticmethod
        def UseConsumable(identifier: ItemIdentifier, effect_name: str = "", aftercast_ms: int = 250) -> BehaviorTree:
            """
            Build a tree that uses a single consumable item when runtime checks allow it.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Use Consumable
            Purpose: Use one consumable item with map, life-state, and active-effect checks.
            UserDescription: Use this when you want to consume one item safely without duplicating active effects.
            Notes: Succeeds quietly when the effect is already active or the item is missing.
            """
            def _use_consumable(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                from ..Checks import Checks
                from ...Map import Map

                if not Checks.Map.MapValid():
                    return BehaviorTree.NodeState.FAILURE

                if not Map.IsExplorable():
                    return BehaviorTree.NodeState.FAILURE

                if Agent.IsDead(Player.GetAgentID()):
                    return BehaviorTree.NodeState.FAILURE

                resolved_model_id = BTItems.Utility.GetModelIDFromIdentifier(identifier)
                resolved_effect_name = effect_name or (CONSUMABLE_MODELID_TO_EFFECT_NAME.get(int(resolved_model_id), "") if resolved_model_id else "")
                
                if resolved_effect_name:
                    effect_id = GLOBAL_CACHE.Skill.GetID(resolved_effect_name)
                    
                    if effect_id and GLOBAL_CACHE.Effects.HasEffect(Player.GetAgentID(), effect_id):
                        return BehaviorTree.NodeState.SUCCESS

                item_id = BTItems.Utility.GetItemID(identifier, bags=INVENTORY_BAGS)
                if item_id == 0:
                    return BehaviorTree.NodeState.FAILURE
                
                item = ItemSnapshot.from_item_id(item_id)
                resolved_model_id = item.model_id if item else 0
                resolved_effect_name = effect_name or CONSUMABLE_MODELID_TO_EFFECT_NAME.get(int(resolved_model_id), "")

                if resolved_effect_name:
                    effect_id = GLOBAL_CACHE.Skill.GetID(resolved_effect_name)
                    
                    if GLOBAL_CACHE.Effects.HasEffect(Player.GetAgentID(), effect_id):
                        return BehaviorTree.NodeState.SUCCESS

                Inventory.UseItem(item_id)
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name=f"UseConsumable({identifier})",
                    action_fn=_use_consumable,
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def UseConsumables(identifiers_and_effects: Sequence[tuple[ItemIdentifier, str]], aftercast_ms: int = 250) -> BehaviorTree:
            """
            Build a tree that uses multiple consumables from a list of `(identifier, effect_name)` pairs.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Use Consumables
            Purpose: Use several consumable items with map, life-state, and active-effect checks.
            UserDescription: Use this when you want to consume multiple items safely without duplicating active effects.
            Notes: Succeeds quietly for any item whose effect is already active or is missing; processes the full list in one tick.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="UseConsumables",
                    children=[
                        BTItems.Consumables.UseConsumable(
                            identifier=identifier,
                            effect_name=effect_name,
                            aftercast_ms=aftercast_ms,
                        )
                        for identifier, effect_name in identifiers_and_effects
                    ],
                )
            )
                   
    class Loot:
        @staticmethod
        def LootItems(distance: float, timeout_ms: int = 10000, aftercast_ms: int = 250) -> BehaviorTree:
            """
            Build a tree that loots nearby items until no loot remains, inventory fills, or timeout expires.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Loot Items
            Purpose: Interact with nearby loot items using the active loot configuration.
            UserDescription: Use this when you want to perform a bounded nearby loot pass.
            Notes: Stops when no items remain, bags are full, or the timeout expires.
            """
            state = {
                "started_at": 0.0,
                "last_item_agent_id": 0,
                "claimed_item_agent_id": 0,
            }

            def _loot_items() -> BehaviorTree.NodeState:                                
                from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig

                if state["started_at"] == 0.0:
                    state["started_at"] = time.monotonic()

                loot_item_agent_ids = LootConfig().GetfilteredLootArray(
                    distance=distance,
                    multibox_loot=True,
                    allow_unasigned_loot=False,
                )
                
                has_empty_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount() > 0
                
                if not loot_item_agent_ids:
                    state["started_at"] = 0.0
                    if state["claimed_item_agent_id"]:
                        clear_loot_lock(state["claimed_item_agent_id"])
                        state["claimed_item_agent_id"] = 0
                    return BehaviorTree.NodeState.SUCCESS

                if (time.monotonic() - state["started_at"]) * 1000 >= timeout_ms:
                    state["started_at"] = 0.0
                    if state["claimed_item_agent_id"]:
                        clear_loot_lock(state["claimed_item_agent_id"])
                        state["claimed_item_agent_id"] = 0
                    return BehaviorTree.NodeState.SUCCESS
                
                item_agent_id = 0
                loot_items = [(agent_id, snapshot)
                              for agent_id, item_data in (
                                  (agent_id, Agent.GetItemAgentByID(agent_id))
                                  for agent_id in loot_item_agent_ids)
                              if item_data is not None and (snapshot := ItemSnapshot.from_item_id(item_data.item_id)) is not None
]
                
                for agent_id, loot_item in loot_items:                    
                    if has_empty_slots or ((available := BTItems.Inventory.HasSpaceForItem(loot_item.id, start_bag=Bags.Backpack, end_bag=Bags.Bag2)) and available[0]):
                        owner_id = Agent.GetItemAgentOwnerID(agent_id)
                        if owner_id == 0:
                            if post_loot_lock(agent_id) < 0:
                                continue
                            state["claimed_item_agent_id"] = agent_id
                        else:
                            state["claimed_item_agent_id"] = 0
                        item_agent_id = agent_id
                        break
                    
                if item_agent_id == 0:
                    state["started_at"] = 0.0
                    return BehaviorTree.NodeState.SUCCESS

                state["last_item_agent_id"] = item_agent_id
                Player.ChangeTarget(item_agent_id)
                Player.Interact(item_agent_id, False)
                
                if not Agent.IsValid(item_agent_id) and state["claimed_item_agent_id"]:
                    clear_loot_lock(state["claimed_item_agent_id"])
                    state["claimed_item_agent_id"] = 0
                    
                elif Agent.IsValid(item_agent_id):
                    live_loot = LootConfig().GetfilteredLootArray(
                        distance=distance,
                        multibox_loot=True,
                        allow_unasigned_loot=False,
                    )
                    
                    if item_agent_id not in live_loot and state["claimed_item_agent_id"]:
                        clear_loot_lock(state["claimed_item_agent_id"])
                        state["claimed_item_agent_id"] = 0
                        
                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="LootItems",
                    action_fn=_loot_items,
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def AddModelToLootWhitelist(model_id: int, aftercast_ms: int = 250) -> BehaviorTree:
            """
            Build a tree that adds a model id to the loot whitelist.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Add Model To Loot Whitelist
            Purpose: Add an item model id to the active loot whitelist.
            UserDescription: Use this when a routine should mark an item model as lootable before item collection starts.
            Notes: Returns success immediately after mutating the local loot configuration.
            """
            from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig
            
            def _add_model_to_loot_whitelist() -> BehaviorTree.NodeState:
                LootConfig().AddModelIDToWhitelist(model_id)
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name=f"AddModelToLootWhitelist({model_id})",
                    action_fn=_add_model_to_loot_whitelist,
                    aftercast_ms=aftercast_ms,
                )
            )

    class Inventory:
        @staticmethod
        def _can_access_storage_gold() -> bool:
            return Map.IsOutpost() or Map.IsGuildHall()

        @staticmethod
        def _get_gold_amounts() -> tuple[int, int]:
            return int(Inventory.GetGoldOnCharacter() or 0), int(Inventory.GetGoldInStorage() or 0)

        @staticmethod
        def _get_spendable_gold(allow_withdraw_gold: bool = False, remaining_storage_gold: int = 0) -> int:
            gold_on_character, gold_in_storage = BTItems.Inventory._get_gold_amounts()
            if allow_withdraw_gold and BTItems.Inventory._can_access_storage_gold():
                return gold_on_character + max(0, gold_in_storage - max(0, int(remaining_storage_gold)))
            return gold_on_character

        @staticmethod
        def _withdraw_gold_for_amount(required_amount: int, remaining_storage_gold: int = 0) -> int:
            if required_amount <= 0 or not BTItems.Inventory._can_access_storage_gold():
                return 0

            gold_on_character, gold_in_storage = BTItems.Inventory._get_gold_amounts()
            usable_storage_gold = max(0, gold_in_storage - max(0, int(remaining_storage_gold)))
            if gold_on_character >= required_amount or usable_storage_gold <= 0:
                return 0

            to_withdraw = min(required_amount - gold_on_character, usable_storage_gold, MAX_GOLD_CHARACTER - gold_on_character)
            if to_withdraw <= 0:
                return 0

            Inventory.WithdrawGold(to_withdraw)
            return to_withdraw

        @staticmethod
        def _deposit_gold_to_limit(remaining_inv_gold: int = 5000) -> int:
            if not BTItems.Inventory._can_access_storage_gold():
                return 0

            gold_on_character, gold_in_storage = BTItems.Inventory._get_gold_amounts()
            storage_capacity = max(0, MAX_GOLD_STORAGE - gold_in_storage)
            desired_on_character = max(0, min(int(remaining_inv_gold), MAX_GOLD_CHARACTER))
            to_deposit = min(max(0, gold_on_character - desired_on_character), storage_capacity)
            if to_deposit <= 0:
                return 0

            Inventory.DepositGold(to_deposit)
            return to_deposit

        @staticmethod
        def HasSpaceForItem(item_id: int, start_bag: Bags, end_bag: Bags, quantity: Optional[int] = None) -> tuple[bool, int]:
            item = ItemSnapshot.from_item_id(item_id)
            qty = quantity if quantity is not None else item.quantity if item else 0
            
            if not item or not item.is_valid:
                return False, 0
            
            inventory_snapshot = ItemSnapshot.get_inventory_snapshot(start_bag, end_bag)
            item_stacks = [i for bag in inventory_snapshot.values() for i in bag.values() if i is not None and 
                        i.is_valid and i.is_stackable and i.model_id == item.model_id and 
                        i.item_type == item.item_type and i.quantity < MAX_STACK_SIZE] if item and item.is_stackable else []
            
            # Check for existing stacks with space for (partial) item.quantity. If we can fit the item into existing stacks, we don't need to check for free slots
            if item_stacks:
                total_available_space = sum(MAX_STACK_SIZE - stack.quantity for stack in item_stacks)
                if total_available_space >= qty:
                    return True, total_available_space
            
            # If the item is not stackable or we don't have enough space in existing stacks, check for free slots
            free_slots = sum((MAX_STACK_SIZE if item.is_stackable else 1) for bag in inventory_snapshot.values() for i in bag.values() if i is None)
            return free_slots > 0, free_slots
        
        @staticmethod
        def Restock(
            identifier: ItemIdentifier,
            quantity: int,
            allow_partial: bool = True,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build an action node that restocks inventory from storage bags.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Restock Bags
              Purpose: Move enough storage items into inventory to reach a target quantity.
              UserDescription: Use this when you want a BT step that refills inventory stock from storage rather than from a merchant.
              Notes: Fails when matching storage items cannot be found or no valid transfer destinations exist.
            """
            model_id = BTItems.Utility.GetModelIDFromIdentifier(identifier)
            item_type = identifier[1] if isinstance(identifier, tuple) and len(identifier) == 2 else None
            
            def _restock(node: BehaviorTree.Node):        
                inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                current_qty = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.model_id == model_id and i.item_type == item_type) if inventory_snapshot else 0
                left_to_restock = max(0, quantity - current_qty)
                
                if left_to_restock <= 0:
                    _log(
                        "Inventory.Restock",
                        f"Already have required quantity for identifier {identifier}: current={current_qty}, target={quantity}.",
                        log=log,
                    )
                    return BehaviorTree.NodeState.SUCCESS
                
                storage_snapshot = ItemSnapshot.get_bags_snapshot(STORAGE_BAGS)
                desired_items = [i for bag in storage_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.model_id == model_id and i.item_type == item_type] if storage_snapshot else []
                
                if not desired_items:
                    _log(
                        "Inventory.Restock",
                        f"No storage items found for identifier {identifier}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE
                
                item_ids = []
                quantities = []
                planned_total = 0
                
                sort_by_lowest_qty = sorted(desired_items, key=lambda i: i.quantity)
                for item in sort_by_lowest_qty:
                    if item.quantity <= 0:
                        continue
                    
                    has_space, space_for_qty = BTItems.Inventory.HasSpaceForItem(item.id, Bags.Backpack, Bags.Bag2, quantity=item.quantity)
                    if not has_space or space_for_qty <= 0:
                        continue
                                        
                    qty_to_move = min(space_for_qty, item.quantity, left_to_restock)
                    current_qty += qty_to_move
                    planned_total += qty_to_move
                    
                    item_ids.append(item.id)
                    quantities.append(qty_to_move)
                    left_to_restock -= qty_to_move
                    
                    if left_to_restock <= 0:
                        break

                if planned_total <= 0:
                    _log(
                        "Inventory.Restock",
                        f"Could not plan any transfer for identifier {identifier}; left_to_restock={left_to_restock}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE

                if not allow_partial and left_to_restock > 0:
                    _log(
                        "Inventory.Restock",
                        f"Partial restock for identifier {identifier} is not allowed; planned={planned_total}, target={quantity}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE
                
                instructions = BTItems.Items.GetTransferInstructions(item_ids, INVENTORY_BAGS, quantities=quantities)
                if not instructions:
                    _log(
                        "Inventory.Restock",
                        f"Failed to build transfer instructions for identifier {identifier}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE
                
                _log(
                    "Inventory.Restock",
                    f"Restocking identifier {identifier}: moving planned total {planned_total} toward target {quantity}.",
                    log=log,
                )
                
                for bag in instructions.values():
                    for dest in bag.values():
                        for item, qty in dest.items:
                            BTItems.Items._move_item_to_transfer_destination(item, dest, qty, node.name)

                return (
                    BehaviorTree.NodeState.SUCCESS
                    if allow_partial or left_to_restock <= 0
                    else BehaviorTree.NodeState.FAILURE
                )

            return BehaviorTree(
                BehaviorTree.ActionNode(name=f"Bags.Restock({model_id}, {item_type}, {quantity})", action_fn=_restock)
            )
        
        @staticmethod
        def RestockItems(
            identifiers_and_quantities: Sequence[tuple[ItemIdentifier, int]],
            allow_partial: bool = True,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build an action node that restocks multiple inventory items from storage bags.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Restock Multiple Items
              Purpose: Move enough storage items into inventory to reach target quantities.
              UserDescription: Use this when you want a BT step that refills multiple inventory stocks from storage rather than from a merchant.
              Notes: Fails when matching storage items cannot be found or no valid transfer destinations exist for any item.
            """
            restock_nodes = [
                BTItems.Inventory.Restock(
                    identifier=identifier,
                    quantity=quantity,
                    allow_partial=allow_partial,
                    log=log,
                )
                for identifier, quantity in identifiers_and_quantities
            ]
            return BehaviorTree(BehaviorTree.SequenceNode(name="RestockItems", children=restock_nodes))
                
        @staticmethod
        def DepositGold(
            amount: Optional[int] = None,
            amount_to_leave_on_character: int = 0,
            allow_partial: bool = True,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that deposits gold from inventory to storage to reach a target inventory amount.
            If allow_partial is true, will deposit as much as possible down to the target amount; otherwise, fails if the full amount cannot be deposited.
            """        
            
            def _deposit():
                if not BTItems.Inventory._can_access_storage_gold():
                    return BehaviorTree.NodeState.FAILURE
                
                gold_on_character, gold_in_storage = BTItems.Inventory._get_gold_amounts()
                amount_to_deposit = amount if amount is not None else gold_on_character - amount_to_leave_on_character
                
                storage_capacity = max(0, MAX_GOLD_STORAGE - gold_in_storage)
                requested_amount = max(0, int(amount_to_deposit))
                amount_to_deposit = min(requested_amount, gold_on_character - amount_to_leave_on_character, storage_capacity)

                if requested_amount <= 0:
                    _log("DepositGold", f"No gold needs to be deposited to reach target amount of {amount_to_leave_on_character} on character.", message_type=Console.MessageType.Info, log=log)
                    return BehaviorTree.NodeState.SUCCESS
                
                if amount_to_deposit <= 0:
                    _log("DepositGold", f"Failed to deposit gold to reach target amount of {amount_to_leave_on_character} on character. Not enough gold on character or no storage capacity.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                if not allow_partial and amount_to_deposit < requested_amount:
                    _log("DepositGold", f"Failed to deposit gold to reach target amount of {amount_to_leave_on_character} on character. Not enough gold on character or no storage capacity to deposit the full requested amount of {requested_amount}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                _log("DepositGold", f"Depositing {amount_to_deposit} gold to reach target amount of {amount_to_leave_on_character} on character.", message_type=Console.MessageType.Info, log=log)
                Inventory.DepositGold(amount_to_deposit)
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(BehaviorTree.ActionNode(name=f"Inventory.DepositGold({amount})", action_fn=_deposit, aftercast_ms=aftercast_ms))
        
        @staticmethod
        def WithdrawGold(
            amount: int = 0,
            allow_partial: bool = True,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that withdraws gold from storage to reach a target inventory amount.
            If allow_partial is true, will withdraw as much as possible up to the target amount; otherwise, fails if the full amount cannot be withdrawn.
            """
            
            def _withdraw():
                if not BTItems.Inventory._can_access_storage_gold():
                    _log("WithdrawGold", "Cannot access storage gold in the current location.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                gold_on_character, gold_in_storage = BTItems.Inventory._get_gold_amounts()
                requested_amount = max(0, int(amount))
                amount_to_withdraw = min(requested_amount, gold_in_storage, MAX_GOLD_CHARACTER - gold_on_character)

                if requested_amount <= 0:
                    _log("WithdrawGold", "No gold needs to be withdrawn.", log=log)
                    return BehaviorTree.NodeState.SUCCESS
                if amount_to_withdraw <= 0:
                    _log("WithdrawGold", f"Failed to withdraw gold. requested={requested_amount}, storage={gold_in_storage}, character={gold_on_character}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                if not allow_partial and amount_to_withdraw < requested_amount:
                    _log("WithdrawGold", f"Failed to withdraw full requested amount {requested_amount}; only {amount_to_withdraw} is available.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                _log("WithdrawGold", f"Withdrawing {amount_to_withdraw} gold.", log=log)
                Inventory.WithdrawGold(amount_to_withdraw)
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(BehaviorTree.ActionNode(name=f"Inventory.WithdrawGold({amount})", action_fn=_withdraw, aftercast_ms=aftercast_ms))
        
        @staticmethod
        def BalanceGold(
            amount: int = 0,
            allow_partial: bool = True,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that balances gold between inventory and storage to reach a target inventory amount.
            """
            
            def _balance():
                if not BTItems.Inventory._can_access_storage_gold():
                    _log("BalanceGold", "Cannot access storage gold in the current location.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                target_amount = max(0, min(int(amount), MAX_GOLD_CHARACTER))
                gold_on_character, gold_in_storage = BTItems.Inventory._get_gold_amounts()

                if gold_on_character == target_amount:
                    _log("BalanceGold", f"Gold is already balanced at the target amount of {target_amount} on character.", message_type=Console.MessageType.Info, log=log)
                    return BehaviorTree.NodeState.SUCCESS

                if gold_on_character > target_amount:
                    to_deposit = min(gold_on_character - target_amount, MAX_GOLD_STORAGE - gold_in_storage)
                    if to_deposit <= 0 or (not allow_partial and gold_on_character - to_deposit != target_amount):
                        _log("BalanceGold", f"Failed to deposit gold to reach target amount of {target_amount}.", message_type=Console.MessageType.Warning, log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    Inventory.DepositGold(to_deposit)
                    _log("BalanceGold", f"Deposited {to_deposit} gold to reach target amount of {target_amount}.", message_type=Console.MessageType.Info, log=log)
                    return BehaviorTree.NodeState.SUCCESS

                to_withdraw = min(target_amount - gold_on_character, gold_in_storage, MAX_GOLD_CHARACTER - gold_on_character)
                if to_withdraw <= 0 or (not allow_partial and gold_on_character + to_withdraw != target_amount):
                    _log("BalanceGold", f"Failed to withdraw gold to reach target amount of {target_amount}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                Inventory.WithdrawGold(to_withdraw)
                _log("BalanceGold", f"Withdrew {to_withdraw} gold to reach target amount of {target_amount}.", message_type=Console.MessageType.Info, log=log)
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(BehaviorTree.ActionNode(name=f"Inventory.BalanceGold({amount})", action_fn=_balance, aftercast_ms=aftercast_ms))
        
        @staticmethod
        def EquipItemID(
            item_id: int,
            agent_id: Optional[int] = None,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that equips an inventory item.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Equip Item
              Purpose: Equip a specific inventory item by id.
              UserDescription: Use this when you want a BT step that equips a known inventory item.
              Notes: Fails if the item is not found, not in inventory, or cannot be equipped.
            """
            agent_id = agent_id or Player.GetAgentID()
            
            def _equip(node: BehaviorTree.Node):
                item = ItemSnapshot.from_item_id(item_id)
                if not item or not item.is_valid or (not item.is_inventory_item and not item.is_storage_item):
                    return BehaviorTree.NodeState.FAILURE

                _log(
                    "EquipItemByModelID",
                    f"Equipping {get_item_name(item_id)} on agent {Agent.GetNameByID(agent_id)}.",
                    log=log,
                )
                Inventory.EquipItem(item_id, agent_id)
                
                _log(
                    "EquipItemByModelID",
                    f"Equipped {get_item_name(item_id)} on agent {Agent.GetNameByID(agent_id)}.",
                    log=log,
                )
                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(BehaviorTree.ActionNode(name=f"Inventory.EquipItem({item_id})", action_fn=_equip, aftercast_ms=aftercast_ms))
        
        @staticmethod
        def EquipItem(
            identifier: ItemIdentifier,
            agent_id: Optional[int] = None,
            aftercast_ms: int = 250,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build an action node that equips an inventory item matching a model id and item type.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Equip Model ID
              Purpose: Equip an inventory item matching a model id and item type.
              UserDescription: Use this when you want a BT step that equips an inventory item based on its model rather than a specific item id.
              Notes: Fails if no matching inventory item is found or if the found item cannot be equipped.
            """
            agent_id = agent_id or Player.GetAgentID()            
            return BTItems.Utility.ResolveItemIDThen(
                    identifier=identifier,
                    next_node_fn=lambda resolved_id: 
                            BTItems.Inventory.EquipItemID(
                                resolved_id,
                                log=log,
                                aftercast_ms=aftercast_ms,
                            ),
                    )
        
        @staticmethod 
        def IsItemInBags(
            identifier: ItemIdentifier,
            bags : Bags | list[Bags] = INVENTORY_BAGS,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a condition node that checks for the presence of an inventory item matching the provided identifier.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Is Item In Inventory
              Purpose: Check if an inventory item matching the provided identifier exists.
              UserDescription: Use this when you want a BT condition that checks for an inventory item based on model id, item name, or encoded name.
              Notes: Returns success if at least one matching inventory item is found; otherwise, returns failure.
            """
            
            bags = bags if isinstance(bags, list) else [bags]
            def _is_item_in_inventory(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                item_id = BTItems.Utility.GetItemID(identifier, bags=bags)
                _log(
                    "IsItemInBags",
                    f"Checked identifier {identifier} in bags {[bag.name for bag in bags]}: item_id={item_id}.",
                    message_type=Console.MessageType.Info if item_id else Console.MessageType.Warning,
                    log=log,
                )
                return BehaviorTree.NodeState.SUCCESS if item_id else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(BehaviorTree.ConditionNode(name=f"IsItemInInventory({identifier})", condition_fn=_is_item_in_inventory))
        
        @staticmethod
        def IsItemEquipped(
            identifier: ItemIdentifier,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a condition node that checks if an item matching the provided identifier is currently equipped.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Is Item Equipped
              Purpose: Check if an item matching the provided identifier is currently equipped.
              UserDescription: Use this when you want a BT condition that checks for an equipped item based on model id, item name, or encoded name.
              Notes: Returns success if at least one matching equipped item is found; otherwise, returns failure.
            """
            return BTItems.Inventory.IsItemInBags(identifier=identifier, bags=Bags.EquippedItems, log=log)
        
        @staticmethod
        def HasItemQuantity(
            identifier: ItemIdentifier,
            quantity: int,
            bags : Bags | list[Bags] = INVENTORY_BAGS,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build a condition node that checks for at least a certain quantity of items matching the provided identifier.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Has Item Quantity
              Purpose: Check if at least a certain quantity of items matching the provided identifier exists.
              UserDescription: Use this when you want a BT condition that checks for a specific quantity of items based on model id, item name, or encoded name.
              Notes: Returns success if the total quantity of matching items found is greater than or equal to the requested quantity; otherwise, returns failure.
            """
            
            bags = bags if isinstance(bags, list) else [bags]
            def _has_item_quantity(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                item_id = BTItems.Utility.GetItemID(identifier, bags=bags)
                
                if not item_id:
                    _log(
                        "HasItemQuantity",
                        f"No item found for identifier {identifier} in bags {[bag.name for bag in bags]}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE
                
                item = ItemSnapshot.from_item_id(item_id)
                if not item or not item.is_valid:
                    _log(
                        "HasItemQuantity",
                        f"Resolved item_id={item_id} for identifier {identifier}, but the item is invalid.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE
                
                inventory_snapshot = ItemSnapshot.get_inventory_snapshot(*bags)
                total_quantity = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and (i.model_id == item.model_id and i.item_type == item.item_type)) if inventory_snapshot else 0
                _log(
                    "HasItemQuantity",
                    f"Checked quantity for identifier {identifier}: total={total_quantity}, required={quantity}.",
                    message_type=Console.MessageType.Info if total_quantity >= quantity else Console.MessageType.Warning,
                    log=log,
                )
                
                return BehaviorTree.NodeState.SUCCESS if total_quantity >= quantity else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(BehaviorTree.ConditionNode(name=f"HasItemQuantity({identifier}, {quantity})", condition_fn=_has_item_quantity))
        
    class Merchant:
        """
        BT helper group for merchant-window item transactions.

        Meta:
          Expose: true
          Audience: advanced
          Display: Merchant
          Purpose: Group BT helper routines that buy, sell, and restock items through merchant interactions.
          UserDescription: Built-in BT helper group for merchant-window actions.
          Notes: These routines expect the merchant window to already be open when they run.
        """
        @staticmethod 
        def Restock(
            model_id: int,
            item_type: ItemType,
            quantity: int,
            allow_partial: bool = True,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            log: bool = False,
        ) -> BehaviorTree:
            """
            Build an action node that restocks a merchant item until the requested inventory quantity is met.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Restock
              Purpose: Buy enough copies of a merchant item to reach a target quantity in inventory.
              UserDescription: Use this when you want a BT step that tops inventory back up from an open merchant window.
              Notes: Fails when the merchant window is closed, the item is not offered, there is no space, or the player cannot afford enough stock.
            """
            def _restock(node: BehaviorTree.Node):
                if not MerchantWindow.IsOpen():
                    _log("Merchant.Restock", "Merchant window is not open.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                current_qty = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.model_id == model_id and i.item_type == item_type) if inventory_snapshot else 0
                
                if current_qty >= quantity:
                    _log("Merchant.Restock", f"Already stocked enough of model {model_id}: current={current_qty}, target={quantity}.", log=log)
                    return BehaviorTree.NodeState.SUCCESS
                
                offered_items = Trading.Merchant.GetOfferedItems()
                item_id = next((iid for iid in offered_items if Item.GetModelID(iid) == model_id and Item.GetItemType(iid)[0] == item_type), None)
                
                if not item_id:
                    _log("Merchant.Restock", f"Merchant does not offer model {model_id} with item type {item_type}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                available_gold = BTItems.Inventory._get_spendable_gold(allow_withdraw_gold, remaining_storage_gold)
                quantity_to_buy = quantity - current_qty
            
                price = (Item.Properties.GetValue(item_id) * 2)
                affordable_qty = available_gold // price if price > 0 else quantity_to_buy
                has_space, space_for_qty = BTItems.Inventory.HasSpaceForItem(item_id, Bags.Backpack, Bags.Bag2, quantity=affordable_qty)
                count = min(quantity_to_buy, affordable_qty, space_for_qty)
                
                if not has_space or count <= 0:
                    _log("Merchant.Restock", f"Cannot restock model {model_id}; no space or no affordable quantity.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                if price > 0 and Inventory.GetGoldOnCharacter() < price:
                    if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(price, remaining_storage_gold) > 0:
                        _log("Merchant.Restock", f"Withdrawing gold before restocking model {model_id}.", log=log)
                        return BehaviorTree.NodeState.RUNNING
                    _log("Merchant.Restock", f"Not enough gold to restock model {model_id}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                                     
                _log("Merchant.Restock", f"Buying {count} of model {model_id} to reach target {quantity}.", log=log)
                for _ in range(max(0, count)):
                    Trading.Merchant.BuyItem(item_id, price)

                if not allow_partial and current_qty + count < quantity:
                    _log("Merchant.Restock", f"Partial merchant restock for model {model_id} is not allowed.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.RUNNING

                return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Merchant.Restock", action_fn=_restock)
            )
        
        @staticmethod
        def SellItem(
            item_id: int,
            allow_partial: bool = True,
            deposit_gold: bool = False,
            remaining_inv_gold: int = 5000,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
        
            return BTItems.Merchant.SellItems(
                [item_id],
                allow_partial=allow_partial,
                deposit_gold=deposit_gold,
                remaining_inv_gold=remaining_inv_gold,
                log=log,
                aftercast_ms=aftercast_ms,
            )
        
        @staticmethod
        def SellItems(
            item_ids: list[int],
            allow_partial: bool = True,
            deposit_gold: bool = False,
            remaining_inv_gold: int = 5000,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that sells a list of inventory items through the open merchant window.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Sell Items
              Purpose: Sell one or more inventory items to the currently open merchant.
              UserDescription: Use this when you want a BT step that sells known item ids at a merchant.
              Notes: Ignores invalid or non-inventory items and succeeds only if at least one item is sold.
            """
            def _sell(node: BehaviorTree.Node):
                if not MerchantWindow.IsOpen():
                    _log("Merchant.SellItems", "Merchant window is not open.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                items = [item for item in (ItemSnapshot.from_item_id(iid) for iid in item_ids) if item and item.is_valid and item.is_inventory_item]
                if not items:
                    _log("Merchant.SellItems", "No valid inventory items were provided to sell.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                if deposit_gold and Inventory.GetGoldOnCharacter() > remaining_inv_gold:
                    if BTItems.Inventory._deposit_gold_to_limit(remaining_inv_gold) > 0:
                        _log("Merchant.SellItems", f"Depositing gold to keep {remaining_inv_gold} on character before selling.", log=log)
                        return BehaviorTree.NodeState.RUNNING

                current_gold = Inventory.GetGoldOnCharacter()
                available_room = MAX_GOLD_CHARACTER - current_gold
                sellable_items: list[ItemSnapshot] = []
                reserved_room = 0

                for item in items:
                    proceeds = Item.Properties.GetValue(item.id) * item.quantity
                    if proceeds <= 0:
                        continue
                    if reserved_room + proceeds > available_room:
                        break
                    reserved_room += proceeds
                    sellable_items.append(item)

                if not sellable_items:
                    _log("Merchant.SellItems", "No sellable items fit the current gold-cap constraints.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                if not allow_partial and len(sellable_items) < len(items):
                    _log("Merchant.SellItems", "Not all requested items can be sold and partial selling is disabled.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                sold_any = False
                for item in sellable_items:
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    _log("Merchant.SellItems", f"Selling {item.names.plain} (ID: {item.id}) x{item.quantity}.", log=log)
                    Trading.Merchant.SellItem(item.id, Item.Properties.GetValue(item.id) * item.quantity)
                    sold_any = True

                return _success_if(sold_any)

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Merchant.SellItems", action_fn=_sell, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def BuyItem(
            item_id: int,
            quantity: int = 1,
            allow_partial: bool = True,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
        
            return BTItems.Merchant.BuyItems(
                [(item_id, quantity)],
                allow_partial=allow_partial,
                allow_withdraw_gold=allow_withdraw_gold,
                remaining_storage_gold=remaining_storage_gold,
                aftercast_ms=aftercast_ms,
                log=log,
            )
        
        @staticmethod
        def BuyItems(
            item_ids_quantities: list[tuple[int, int]],
            allow_partial: bool = True,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that buys several offered merchant items with quantity limits.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Buy Items
              Purpose: Buy one or more offered merchant items while respecting gold and bag-space limits.
              UserDescription: Use this when you want a BT step that purchases several merchant items in one pass.
              Notes: Skips items that are unavailable, unaffordable, or cannot fit in inventory, and succeeds only if at least one purchase is made.
            """
            def _buy(node: BehaviorTree.Node):
                if not MerchantWindow.IsOpen():
                    _log("Merchant.BuyItems", "Merchant window is not open.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                offered_items = Trading.Merchant.GetOfferedItems()
                valid_item_ids_quantities = [(item_id, qty) for item_id, qty in item_ids_quantities if item_id in offered_items]
                
                if not valid_item_ids_quantities:
                    _log("Merchant.BuyItems", "None of the requested items are offered by the merchant.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                bought_any = False
                available_gold = BTItems.Inventory._get_spendable_gold(allow_withdraw_gold, remaining_storage_gold)
                pending_withdraw = False
                all_requested_fulfilled = True
                
                for i, (offered_item_id, quantity) in enumerate(item_ids_quantities):
                    price =  (Item.Properties.GetValue(offered_item_id) * 2)
                    affordable_qty = available_gold // price if price > 0 else quantity
                    has_space, qty = BTItems.Inventory.HasSpaceForItem(offered_item_id, Bags.Backpack, Bags.Bag2, quantity=affordable_qty)
                    count = min(quantity, affordable_qty, qty)
                    
                    if not has_space or count <= 0:
                        all_requested_fulfilled = False
                        _log("Merchant.BuyItems", f"Cannot buy {get_item_name(offered_item_id)} x{quantity} - not enough space in inventory.", message_type=Console.MessageType.Warning, log=log)
                        continue

                    if price > 0 and Inventory.GetGoldOnCharacter() < price and allow_withdraw_gold:
                        pending_withdraw = BTItems.Inventory._withdraw_gold_for_amount(price, remaining_storage_gold) > 0
                        if pending_withdraw:
                            _log("Merchant.BuyItems", f"Withdrawing gold for {get_item_name(offered_item_id)} x{quantity}.", message_type=Console.MessageType.Info, log=log)
                            break
                                        
                    for _ in range(max(0, count)):
                        _log("Merchant.BuyItems", f"Buying {get_item_name(offered_item_id)} x{quantity}.", message_type=Console.MessageType.Info, log=log)
                        Trading.Merchant.BuyItem(offered_item_id, price)
                        bought_any = True
                        
                    if count < quantity:
                        all_requested_fulfilled = False

                if pending_withdraw:
                    return BehaviorTree.NodeState.RUNNING
                
                if not allow_partial and not all_requested_fulfilled:
                    _log("Merchant.BuyItems", "Failed to buy all requested items and partial purchases are not allowed.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                return _success_if(bought_any)

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Merchant.BuyItems", action_fn=_buy, aftercast_ms=aftercast_ms)
            )

    class Trader:
        """
        BT helper group for quoted trader buy and sell flows.

        Meta:
          Expose: true
          Audience: advanced
          Display: Trader
          Purpose: Group BT helper routines that interact with trader quotes and transactional progress state.
          UserDescription: Built-in BT helper group for trader-window purchase and sale flows.
          Notes: These routines manage quote polling and transaction confirmation through blackboard state.
        """
        class TraderProgress:
            """
            Internal runtime progress container for multi-step trader transactions.

            Meta:
              Expose: false
              Audience: advanced
              Display: Internal Trader Progress
              Purpose: Store quote and transaction progress state for trader buy and sell helper routines.
              UserDescription: Internal support helper class.
              Notes: This class is blackboard-backed runtime state and not intended for direct discovery.
            """
            def __init__(self):                
                """
                Initialize default trader progress bookkeeping fields.

                Meta:
                  Expose: false
                  Audience: advanced
                  Display: Internal Trader Progress Initializer
                  Purpose: Set up initial quote, trade, and quantity-tracking fields for trader flows.
                  UserDescription: Internal support routine.
                  Notes: Used by trader buy and sell helpers to persist progress across ticks.
                """
                self.initial_qty = 0
                self.current_qty = 0
                self.desired_qty = 0
                
                self.quote_requested_at = 0.0
                self.traded_at = 0.0
                
                self.requested = False
                self.traded = False
                self.trade_confirmed = False
            
            def reset(self):        
                """
                Reset transient quote and trade confirmation fields.

                Meta:
                  Expose: false
                  Audience: advanced
                  Display: Internal Trader Progress Reset Helper
                  Purpose: Clear quote timing and trade confirmation state while preserving quantity targets.
                  UserDescription: Internal support routine.
                  Notes: Used when a trader flow needs to restart a quote-confirmation cycle.
                """
                self.quote_requested_at = 0.0
                self.traded_at = 0.0
                
                self.requested = False
                self.traded = False
                self.trade_confirmed = False
        
        @staticmethod
        def BuyItem(
            item_id : int,
            quantity: int = 1,
            quote_timeout_ms: int = 500,
            allow_partial: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that buys a trader item by repeatedly requesting quotes until the desired quantity is reached.

            Meta:
              Expose: true
              Audience: advanced
              Display: Buy Item
              Purpose: Purchase a trader item through the quote-confirmation flow until a target quantity is reached.
              UserDescription: Use this when you want a BT step that handles trader quote timing automatically for one item.
              Notes: Stores progress in the blackboard under `trader_buy_progress` and returns running while the quote cycle is active.
            """
            def _buy(node: BehaviorTree.Node):
                now = time.monotonic()
                
                if not TraderWindow.IsOpen():
                    return BehaviorTree.NodeState.FAILURE
                
                offered_items = Trading.Trader.GetOfferedItems()
                
                if item_id not in offered_items:
                    return BehaviorTree.NodeState.FAILURE
                
                item = ItemSnapshot.from_item_id(item_id)
                if not item or not item.is_valid:
                    return BehaviorTree.NodeState.FAILURE
                                 
                state_key = f"{node.id}_trader_buy_progress"
                state = node.blackboard.get(state_key)
                state = cast(BTItems.Trader.TraderProgress, state) if state else None
                
                if state is None:
                    state = BTItems.Trader.TraderProgress()
                    inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                    state.initial_qty = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.same_kind_as(item)) if inventory_snapshot else 0
                    state.current_qty = state.initial_qty
                    state.desired_qty = state.initial_qty + quantity
                    node.blackboard[state_key] = state
                
                if state.current_qty < state.desired_qty:
                    quote = Trading.Trader.GetQuotedValue()
                    quote_available = Trading.Trader.GetQuotedItemID() == item_id
                    
                    if not state.requested:
                        Trading.Trader.RequestQuote(item_id)
                        state.quote_requested_at = now
                        state.requested = True
                        return BehaviorTree.NodeState.RUNNING
                                        
                    if not state.traded:                        
                        if quote_available and quote > 0:
                            if Inventory.GetGoldOnCharacter() < quote:
                                if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(quote, remaining_storage_gold) > 0:
                                    return BehaviorTree.NodeState.RUNNING
                                node.blackboard.pop(state_key, None)
                                if allow_partial and state.current_qty > state.initial_qty:
                                    return BehaviorTree.NodeState.SUCCESS
                                return BehaviorTree.NodeState.FAILURE
                            Trading.Trader.BuyItem(item_id, quote)
                            state.traded = True
                            state.traded_at = now
                            
                            return BehaviorTree.NodeState.RUNNING
                    
                    if not state.trade_confirmed:
                        inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                        state.current_qty = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.same_kind_as(item)) if inventory_snapshot else 0
                        state.trade_confirmed = state.current_qty > state.initial_qty
                        
                        
                        if state.trade_confirmed:
                            state.initial_qty = state.current_qty
                            state.requested = False
                            state.traded = False
                            state.trade_confirmed = False
                            state.quote_requested_at = 0.0
                            state.traded_at = 0.0
                            return BehaviorTree.NodeState.RUNNING
                                        
                    if state.traded_at and (now - state.traded_at) * 1000 >= quote_timeout_ms:
                        state.traded = False
                        state.trade_confirmed = False
                        state.traded_at = 0.0
                        return BehaviorTree.NodeState.RUNNING
                    
                    if state.quote_requested_at and (now - state.quote_requested_at) * 1000 >= quote_timeout_ms:
                        state.requested = False
                        state.quote_requested_at = 0.0
                        return BehaviorTree.NodeState.RUNNING
                    
                    return BehaviorTree.NodeState.RUNNING
                
                else:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Trader.BuyItem", action_fn=_buy, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def BuyItems(
            item_ids_quantities: list[tuple[int, int]],
            quote_timeout_ms: int = 500,
            allow_partial: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            log: bool = False,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that buys multiple trader items sequentially.

            Meta:
              Expose: true
              Audience: advanced
              Display: Buy Items
              Purpose: Purchase multiple trader items while requesting a fresh quote before every individual buy.
              UserDescription: Use this when you want one BT flow that buys several different trader entries.
              Notes: Runs the single-item trader buy BT sequentially for each `(item_id, quantity)` entry.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Trader.BuyItems",
                    children=[
                        BTItems.Trader.BuyItem(
                            item_id=item_id,
                            quantity=quantity,
                            quote_timeout_ms=quote_timeout_ms,
                            allow_partial=allow_partial,
                            allow_withdraw_gold=allow_withdraw_gold,
                            remaining_storage_gold=remaining_storage_gold,
                            aftercast_ms=aftercast_ms,
                        ).root
                        for item_id, quantity in item_ids_quantities
                    ],
                )
            )

        @staticmethod
        def SellItem(
            item_id : int,
            quantity: int = 1,
            quote_timeout_ms: int = 500,
            allow_partial: bool = True,
            deposit_gold: bool = False,
            remaining_inv_gold: int = 5000,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that sells a trader item through repeated quote-confirmation cycles.

            Meta:
              Expose: true
              Audience: advanced
              Display: Sell Item
              Purpose: Sell a trader item until the desired quantity has been removed from inventory.
              UserDescription: Use this when you want a BT step that handles trader sell quotes automatically for one item.
              Notes: Stores progress in the blackboard under `trader_sell_progress` and returns running while the quote cycle is active.
            """
            def _sell(node: BehaviorTree.Node):
                now = time.monotonic()
                
                if not TraderWindow.IsOpen():
                    return BehaviorTree.NodeState.FAILURE
                                
                item = ItemSnapshot.from_item_id(item_id)
                
                if not item or not item.is_valid or not item.is_inventory_item:
                    return BehaviorTree.NodeState.SUCCESS
                                 
                state_key = f"{node.id}_trader_sell_progress"
                state = node.blackboard.get(state_key)
                state = cast(BTItems.Trader.TraderProgress, state) if state else None
                
                if state is None:
                    state = BTItems.Trader.TraderProgress()
                    inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                    state.initial_qty = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.same_kind_as(item)) if inventory_snapshot else 0
                    state.current_qty = state.initial_qty
                    state.desired_qty = state.initial_qty - (quantity if not item.is_material or item.is_rare_material else quantity // 10 * 10)
                    node.blackboard[state_key] = state 
                
                if state.current_qty > state.desired_qty:
                    if deposit_gold and Inventory.GetGoldOnCharacter() > remaining_inv_gold:
                        if BTItems.Inventory._deposit_gold_to_limit(remaining_inv_gold) > 0:
                            return BehaviorTree.NodeState.RUNNING

                    quote = Trading.Trader.GetQuotedValue()
                    quote_available = Trading.Trader.GetQuotedItemID() == item_id
                    
                    if not state.requested:
                        Trading.Trader.RequestSellQuote(item_id)
                        state.quote_requested_at = now
                        state.requested = True
                        return BehaviorTree.NodeState.RUNNING
                                        
                    if not state.traded:                        
                        if quote_available and quote > 0:
                            if (MAX_GOLD_CHARACTER - Inventory.GetGoldOnCharacter()) < quote:
                                if deposit_gold and BTItems.Inventory._deposit_gold_to_limit(remaining_inv_gold) > 0:
                                    return BehaviorTree.NodeState.RUNNING
                                node.blackboard.pop(state_key, None)
                                if allow_partial and state.current_qty < state.initial_qty:
                                    return BehaviorTree.NodeState.SUCCESS
                                return BehaviorTree.NodeState.FAILURE
                            Trading.Trader.SellItem(item_id, quote)
                            state.traded = True
                            state.traded_at = now
                            
                            return BehaviorTree.NodeState.RUNNING
                    
                    if not state.trade_confirmed:
                        inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                        state.current_qty = sum(i.quantity for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.same_kind_as(item)) if inventory_snapshot else 0
                        state.trade_confirmed = state.current_qty < state.initial_qty
                        
                        if state.trade_confirmed:
                            state.initial_qty = state.current_qty
                            state.requested = False
                            state.traded = False
                            state.trade_confirmed = False
                            state.quote_requested_at = 0.0
                            state.traded_at = 0.0
                            return BehaviorTree.NodeState.RUNNING
                                        
                    if state.traded_at and (now - state.traded_at) * 1000 >= quote_timeout_ms:
                        state.traded = False
                        state.trade_confirmed = False
                        state.traded_at = 0.0
                        return BehaviorTree.NodeState.RUNNING
                    
                    if state.quote_requested_at and (now - state.quote_requested_at) * 1000 >= quote_timeout_ms:
                        state.requested = False
                        state.quote_requested_at = 0.0
                        return BehaviorTree.NodeState.RUNNING
                    
                    return BehaviorTree.NodeState.RUNNING
                
                else:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Trader.SellItem", action_fn=_sell, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def SellItems(
            item_ids_quantities: list[tuple[int, int]],
            quote_timeout_ms: int = 500,
            allow_partial: bool = True,
            deposit_gold: bool = False,
            remaining_inv_gold: int = 5000,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that sells multiple trader items sequentially.

            Meta:
              Expose: true
              Audience: advanced
              Display: Sell Items
              Purpose: Sell multiple trader items while requesting a fresh quote before every individual sale.
              UserDescription: Use this when you want one BT flow that sells several different trader inventory items.
              Notes: Runs the single-item trader sell BT sequentially for each `(item_id, quantity)` entry.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Trader.SellItems",
                    children=[
                        BTItems.Trader.SellItem(
                            item_id=item_id,
                            quantity=quantity,
                            quote_timeout_ms=quote_timeout_ms,
                            allow_partial=allow_partial,
                            deposit_gold=deposit_gold,
                            remaining_inv_gold=remaining_inv_gold,
                            aftercast_ms=aftercast_ms,
                        ).root
                        for item_id, quantity in item_ids_quantities
                    ],
                )
            )

    class Items:
        """
        BT helper group for inventory item usage, destruction, movement, salvage, and transfer flows.

        Meta:
          Expose: true
          Audience: advanced
          Display: Items
          Purpose: Group BT helper routines that act on inventory and storage items.
          UserDescription: Built-in BT helper group for inventory, salvage, storage, and transfer actions.
          Notes: Includes both direct inventory actions and storage-transfer planning helpers.
        """
        @staticmethod
        def UseItems(
            item_ids: list[int],
            quantities: Optional[list[int]] = None,
            aftercast_ms: int = 250,
            log: bool = False,
        ):
            """
            Build an action node that uses one or more inventory items.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Use Items
              Purpose: Use one or more inventory items, optionally with per-item quantity counts.
              UserDescription: Use this when you want a BT step that consumes or activates known inventory items.
              Notes: Invalid items are skipped and success depends on whether any item was actually used.
            """
            def _use(node: BehaviorTree.Node):
                if not item_ids:
                    _log("Items.UseItems", "No item ids were provided.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                used_any = False
                items = [ItemSnapshot.from_item_id(iid) for iid in item_ids]
                
                for index, item in enumerate(items):
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    quantity = quantities[index] if quantities and index < len(quantities) else 1
                    _log("Items.UseItems", f"Using {item.names.plain} (ID: {item.id}) x{quantity}.", log=log)
                    for _ in range(max(0, quantity)):
                        Inventory.UseItem(item.id)
                        used_any = True

                if not used_any:
                    _log("Items.UseItems", "No valid inventory items were used.", message_type=Console.MessageType.Warning, log=log)
                return BehaviorTree.NodeState.SUCCESS if used_any else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.UseItems", action_fn=_use, aftercast_ms=aftercast_ms)
            )
        
        @staticmethod
        def DropItems(
            item_ids: list[int],
            aftercast_ms: int = 250,
            succeed_if_any_dropped: bool = True,
            log: bool = False,
        ):
            """
            Build an action node that drops one or more inventory items.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Drop Items
              Purpose: Drop one or more inventory items onto the ground.
              UserDescription: Use this when you want a BT step that removes known items from bags by dropping them.
              Notes: Invalid items are skipped and success depends on whether any item was dropped.
            """
            def _drop(node: BehaviorTree.Node):
                if not item_ids:
                    _log("Items.DropItems", "No item ids were provided.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                dropped_any = False
                items = [ItemSnapshot.from_item_id(iid) for iid in item_ids]
                
                for item in items:
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    _log("Items.DropItems", f"Dropping {item.names.plain} (ID: {item.id}) x{item.quantity}.", log=log)
                    Inventory.DropItem(item.id, item.quantity)
                    dropped_any = True

                if not dropped_any:
                    _log("Items.DropItems", "No valid inventory items were dropped.", message_type=Console.MessageType.Warning, log=log)
                return BehaviorTree.NodeState.SUCCESS if dropped_any else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.DropItems", action_fn=_drop, aftercast_ms=aftercast_ms)
            )
        
        @staticmethod
        def IdentifyItems(
            item_ids: list[int] | None = None,
            fail_if_no_kit: bool = True,
            succeed_if_already_identified: bool = True,
            aftercast_ms: int = 250,
            log: bool = False,
        ):
            """
            Build an action node that identifies one or more inventory items.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Identify Items
              Purpose: Identify inventory items using the first available identification kit.
              UserDescription: Use this when you want a BT step that identifies a known set of items.
              Notes: Supports configurable behavior when no kit is found or items were already identified.
            """
            def _identify(node: BehaviorTree.Node):
                if not item_ids:
                    _log("Items.IdentifyItems", "No item ids were provided.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE

                identified_any = False
                items = [ItemSnapshot.from_item_id(iid) for iid in item_ids]
                
                for item in items:
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    kit_id = Inventory.GetFirstIDKit()
                    
                    if kit_id == 0:
                        _log("Items.IdentifyItems", f"No identification kit available for {item.names.plain} (ID: {item.id}).", message_type=Console.MessageType.Warning, log=log)
                        return BehaviorTree.NodeState.FAILURE if fail_if_no_kit else (BehaviorTree.NodeState.SUCCESS if identified_any else (BehaviorTree.NodeState.SUCCESS if succeed_if_already_identified else BehaviorTree.NodeState.FAILURE))
                    
                    _log("Items.IdentifyItems", f"Identifying {item.names.plain} (ID: {item.id}) with kit {kit_id}.", log=log)
                    Inventory.IdentifyItem(item.id, kit_id)
                    identified_any = True

                if not identified_any and not succeed_if_already_identified:
                    _log("Items.IdentifyItems", "No valid inventory items were identified.", message_type=Console.MessageType.Warning, log=log)
                return BehaviorTree.NodeState.SUCCESS if identified_any else (BehaviorTree.NodeState.SUCCESS if succeed_if_already_identified else BehaviorTree.NodeState.FAILURE)

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.IdentifyItems", action_fn=_identify, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def DestroyItems(
            item_ids: list[int] | None = None,
            aftercast_ms: int = 250,
            succeed_always: bool = True,
            log: bool = False,
        ):
            """
            Build an action node that destroys one or more inventory items.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Destroy Items
              Purpose: Destroy one or more inventory items by item id.
              UserDescription: Use this when you want a BT step that deletes known items from inventory.
              Notes: Can be configured to succeed even when no item was actually destroyed.
            """
            def _destroy(node: BehaviorTree.Node):
                if not item_ids:
                    return BehaviorTree.NodeState.FAILURE

                destroyed_any = False
                items = [ItemSnapshot.from_item_id(iid) for iid in item_ids]                
                for item in items:
                    if item is None or not item.is_valid or not item.is_inventory_item:
                        continue
                    
                    _log(node.name, f"Destroying '{item.names.full}' (ID: {item.id}) from bag {item.bag.name} slot {item.slot} quantity {item.quantity}", log=log)
                    Inventory.DestroyItem(item.id)
                    destroyed_any = True

                return BehaviorTree.NodeState.SUCCESS if succeed_always else _success_if(destroyed_any)

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.DestroyItems", action_fn=_destroy, aftercast_ms=aftercast_ms)
            )

        class SavalvageProgress():
            """
            Internal runtime progress container for salvage operations.

            Meta:
              Expose: false
              Audience: advanced
              Display: Internal Salvage Progress
              Purpose: Store salvage timing, desired quantity, and confirmation state across ticks.
              UserDescription: Internal support helper class.
              Notes: This class is runtime-only salvage bookkeeping and not intended for discovery.
            """
            def __init__(self, item_id: int, salvage_started_at: float, initial_qty: int, salvage_amount: int):
                """
                Initialize salvage progress tracking for one target item.

                Meta:
                  Expose: false
                  Audience: advanced
                  Display: Internal Salvage Progress Initializer
                  Purpose: Set up the initial salvage state for a single item and target salvage amount.
                  UserDescription: Internal support routine.
                  Notes: Tracks desired quantity reduction and the timing of salvage UI confirmations.
                """
                self.item_id = item_id
                self.salvage_started_at = salvage_started_at
                self.initial_qty = initial_qty
                self.desired_qty = initial_qty - salvage_amount
                self.salvage_amount = salvage_amount
                self.confirm_clicked_at = 0.0
                self.window_detected_at = 0.0
                self.salvaged_any = False
                
        @staticmethod
        def SalvageItem(
            item_id : int,
            salvage_mode: "SalvageMode | int" = 0,
            salvage_amount: Optional[int] = None,
            preferred_kit_id: Optional[int] = None,
            allow_expert_for_common_materials: bool = False,
            restock_salvage_kits: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            state_key: str = "_salvage_state",
            timeout_ms_per_item: int = 1500,
            aftercast_ms: int = 250,
            debug_enabled: bool = False,
        ) -> BehaviorTree:
            """
            Build an action node that salvages an item using the requested salvage mode and UI flow.

            Meta:
              Expose: true
              Audience: advanced
              Display: Salvage Item
              Purpose: Drive the salvage window workflow for a target item until the requested salvage completes or fails.
              UserDescription: Use this when you want a BT step that manages salvage UI and progress automatically for one item.
              Notes: Stores runtime state in the blackboard, supports expert or lesser kits, and returns running while the salvage flow is in progress.
            """
            def _reset_state(node: BehaviorTree.Node):
                node.blackboard.pop(state_key, None)

            pop_up_delays = 0
            
            def _resolve_preferred_kit(valid_model_ids: tuple[ModelID, ...]) -> int:
                if preferred_kit_id is None or preferred_kit_id <= 0:
                    return 0

                preferred = ItemSnapshot.from_item_id(preferred_kit_id)
                if preferred is None or not preferred.is_valid or not preferred.is_salvage_kit or preferred.uses <= 0:
                    return 0

                try:
                    preferred_model_id = ModelID(preferred.model_id)
                except ValueError:
                    return 0

                return preferred.id if preferred_model_id in valid_model_ids else 0

            def _get_expert_salvage_kit() -> int:
                preferred = _resolve_preferred_kit((ModelID.Expert_Salvage_Kit, ModelID.Superior_Salvage_Kit))
                if preferred > 0:
                    return preferred

                inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                expert_kits = [i for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.is_salvage_kit and i.model_id in (ModelID.Expert_Salvage_Kit, ModelID.Superior_Salvage_Kit)]
                
                if not expert_kits:
                    return 0
                
                return min(expert_kits, key=lambda k: k.uses).id
            
            def _get_lesser_salvage_kit() -> int:
                preferred = _resolve_preferred_kit((ModelID.Salvage_Kit,))
                if preferred > 0:
                    return preferred

                inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                lesser_kits = [i for bag in inventory_snapshot.values() for i in bag.values() if i is not None and i.is_valid and i.is_salvage_kit and i.model_id == ModelID.Salvage_Kit]
                
                if not lesser_kits:
                    return 0
                
                return min(lesser_kits, key=lambda k: k.uses).id

            def _get_upgrade_salvage_kit() -> int:
                preferred = _resolve_preferred_kit((ModelID.Perfect_Salvage_Kit, ModelID.Expert_Salvage_Kit, ModelID.Superior_Salvage_Kit))
                if preferred > 0:
                    return preferred

                inventory_snapshot = ItemSnapshot.get_inventory_snapshot(Bags.Backpack, Bags.Bag2)
                upgrade_kits = [
                    i for bag in inventory_snapshot.values() for i in bag.values()
                    if i is not None and i.is_valid and i.is_salvage_kit and i.model_id in (
                        ModelID.Perfect_Salvage_Kit,
                        ModelID.Expert_Salvage_Kit,
                        ModelID.Superior_Salvage_Kit,
                    )
                ]

                if not upgrade_kits:
                    return 0

                return min(upgrade_kits, key=lambda k: k.uses).id

            def _try_restock_salvage_kit(valid_model_ids: tuple[ModelID, ...]) -> bool:
                if not restock_salvage_kits or not MerchantWindow.IsOpen():
                    return False

                offered_item_id = next(
                    (
                        offered_item_id
                        for offered_item_id in Trading.Merchant.GetOfferedItems()
                        if Item.GetModelID(offered_item_id) in {model.value for model in valid_model_ids}
                    ),
                    0,
                )
                if offered_item_id <= 0:
                    return False

                price = int(Item.Properties.GetValue(offered_item_id) or 0) * 2
                if price <= 0:
                    return False

                if Inventory.GetGoldOnCharacter() < price:
                    if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(price, remaining_storage_gold) > 0:
                        return True
                    return False

                Trading.Merchant.BuyItem(offered_item_id, price)
                return True
            
            def _is_mod_salvaged(item: ItemSnapshot, salvage_mode: SalvageMode) -> bool:
                match salvage_mode:
                    case SalvageMode.Prefix:
                        return item.prefix is None
                    
                    case SalvageMode.Suffix:
                        return item.suffix is None
                    
                    case SalvageMode.Inscription:
                        return item.inscription is None
            
                return False
            
            def _salvage(node: BehaviorTree.Node):        
                if item_id is None or item_id <= 0:
                    _log(node.name, f"Invalid item_id={item_id}.")
                    return BehaviorTree.NodeState.FAILURE
                
                try:
                    mode = SalvageMode(int(salvage_mode))
                except Exception:
                    mode = SalvageMode.NONE
                
                if mode == SalvageMode.NONE:
                    _log(node.name, f"Invalid salvage mode for item id {item_id}: raw={salvage_mode!r}.")
                    return BehaviorTree.NodeState.FAILURE
                                 
                state = node.blackboard.get(state_key)
                state = cast(BTItems.Items.SavalvageProgress, state) if state else None
                item = ItemSnapshot.from_item_id(item_id)
                item_name = {item.complete_name if item else 'Unknown Item'}
                
                if state and item_id != state.item_id:
                    _log(node.name, f"State item mismatch: requested={item_id}, state_item={state.item_id}.")
                    return BehaviorTree.NodeState.SUCCESS

                if item is None:
                    _log(node.name, f"Item {item_name} [{item_id}] no longer exists.")
                    return BehaviorTree.NodeState.SUCCESS

                if not item.is_valid:
                    _log(node.name, f"Item {item_name} [{item_id}] is not valid.")
                    return BehaviorTree.NodeState.SUCCESS

                if not item.is_salvageable:
                    _log(node.name, f"Item {item_name} [{item_id}] is no longer salvageable.")
                    return BehaviorTree.NodeState.SUCCESS

                if not item.is_inventory_item:
                    _log(node.name, f"Item {item_name} [{item_id}] is no longer in inventory.")
                    return BehaviorTree.NodeState.SUCCESS

                if _is_mod_salvaged(item, mode):
                    _log(node.name, f"Requested salvage mode {mode.name} already resolved for item {item_name} [{item_id}].")
                    return BehaviorTree.NodeState.SUCCESS
                
                if state is None:
                    state = BTItems.Items.SavalvageProgress(item_id=item.id, salvage_started_at=0.0, initial_qty=item.quantity, salvage_amount=min(item.quantity, salvage_amount if salvage_amount else item.quantity))                   
                    node.blackboard[state_key] = state
                    _log(
                        node.name,
                        f"Initialized salvage state for item={item_name} [{item_id}] mode={mode.name} "
                        f"qty={item.quantity} desired_qty={state.desired_qty} timeout_ms={timeout_ms_per_item}."
                    )
                    
                now = time.monotonic()
                salvage_window_open = AnySalvageWindow.IsOpen()

                if Inventory.GetFreeSlotCount() <= 0:
                    _log(node.name, f"Cannot salvage item {item_name} [{item_id}]: no free inventory slots.", message_type=Console.MessageType.Warning)
                    return BehaviorTree.NodeState.FAILURE

                # Start salvage once per item.
                if not state.salvage_started_at:
                    if salvage_window_open:
                        _log(
                            node.name,
                            f"Cannot start salvage for item={item_name} [{item_id}] while another salvage-related window is open."
                            f"Closing existing salvage windows and waiting before retrying."
                        )
                        AnySalvageWindow.Cancel()
                        return BehaviorTree.NodeState.RUNNING

                    if mode == SalvageMode.LesserCraftingMaterials:
                        kit_id = _get_lesser_salvage_kit()
                        if allow_expert_for_common_materials and kit_id == 0:
                            kit_id = _get_expert_salvage_kit()
                        valid_kit_models = (ModelID.Salvage_Kit, ModelID.Expert_Salvage_Kit, ModelID.Superior_Salvage_Kit) if allow_expert_for_common_materials else (ModelID.Salvage_Kit,)
                    elif mode == SalvageMode.RareCraftingMaterials:
                        kit_id = _get_expert_salvage_kit()
                        valid_kit_models = (ModelID.Expert_Salvage_Kit, ModelID.Superior_Salvage_Kit)
                    else:
                        kit_id = _get_upgrade_salvage_kit()
                        valid_kit_models = (ModelID.Perfect_Salvage_Kit, ModelID.Expert_Salvage_Kit, ModelID.Superior_Salvage_Kit)

                    kit = ItemSnapshot.from_item_id(kit_id)
                    if kit_id <= 0 or (kit is None or kit.model_id == ModelID.Salvage_Kit and (item.rarity > Rarity.White and not item.is_identified)):
                        if _try_restock_salvage_kit(valid_kit_models):
                            return BehaviorTree.NodeState.RUNNING
                        _log(
                            node.name,
                            f"Failed to resolve valid salvage kit for item={item_name} [{item_id}] mode={mode.name}. "
                            f"kit_id={kit_id} kit_model={(kit.model_id if kit else 'None')} "
                            f"item_rarity={item.rarity.name} item_identified={item.is_identified}.",
                            message_type=Console.MessageType.Warning,
                        )
                        return BehaviorTree.NodeState.FAILURE

                    _log(
                        node.name,
                        f"Starting salvage item={item_name} [{item_id}] mode={mode.name} kit_id={kit_id} "
                        f"kit_model={kit.model_id if kit else 'None'} item_qty={item.quantity} "
                        f"preferred_kit_id={preferred_kit_id or 0}."
                    )
                    Inventory.SalvageItem(item_id, kit_id)
                    state.salvage_started_at = now
                    return BehaviorTree.NodeState.RUNNING

                # Handle salvage windows/frames while waiting for completion.
                if LesserSalvageWindow.IsOpen():
                    if not state.window_detected_at:
                        state.window_detected_at = now
                    elapsed_ms = int((now - state.window_detected_at) * 1000)
                    if elapsed_ms < pop_up_delays:
                        _log(
                            node.name,
                            f"Confirm lesser materials window open for item={item_name} [{item_id}]; "
                            f"waiting {elapsed_ms}/{pop_up_delays} ms before confirm."
                        )
                        return BehaviorTree.NodeState.RUNNING
                    if LesserSalvageWindow.Confirm():
                        state.confirm_clicked_at = now
                        state.window_detected_at = 0.0
                        _log(node.name, f"Confirmed lesser materials salvage for item={item_name} [{item_id}].")
                        return BehaviorTree.NodeState.RUNNING
                    
                if SalvageConfirmationPopup.IsOpen():
                    if not state.window_detected_at:
                        state.window_detected_at = now
                    elapsed_ms = int((now - state.window_detected_at) * 1000)
                    if elapsed_ms < pop_up_delays:
                        _log(
                            node.name,
                            f"Confirm mod/material warning visible for item={item_name} [{item_id}]; "
                            f"waiting {elapsed_ms}/{pop_up_delays} ms before confirm."
                        )
                        return BehaviorTree.NodeState.RUNNING
                    if SalvageConfirmationPopup.Confirm():
                        state.confirm_clicked_at = now
                        state.window_detected_at = 0.0
                        _log(node.name, f"Confirmed mod/material warning for item={item_name} [{item_id}].")
                        return BehaviorTree.NodeState.RUNNING
                    
                if ExpertSalvageUnidentifiedWindow.IsOpen():
                    if not state.window_detected_at:
                        state.window_detected_at = now
                    elapsed_ms = int((now - state.window_detected_at) * 1000)
                    if elapsed_ms < pop_up_delays:
                        _log(
                            node.name,
                            f"Unidentified salvage warning open for item={item_name} [{item_id}]; "
                            f"waiting {elapsed_ms}/{pop_up_delays} ms before confirm."
                        )
                        return BehaviorTree.NodeState.RUNNING
                    if ExpertSalvageUnidentifiedWindow.Confirm():
                        state.confirm_clicked_at = now
                        state.window_detected_at = 0.0
                        _log(node.name, f"Confirmed unidentified salvage warning for item={item_name} [{item_id}].")
                        return BehaviorTree.NodeState.RUNNING
                    
                if SalvageOptionsWindow.IsOpen():
                    if not state.window_detected_at:
                        state.window_detected_at = now
                    elapsed_ms = int((now - state.window_detected_at) * 1000)
                    if elapsed_ms < pop_up_delays:
                        _log(
                            node.name,
                            f"Salvage choice window open for item={item_name} [{item_id}], "
                            f"waiting {elapsed_ms}/{pop_up_delays} ms before selecting mode={mode.name}."
                        )
                        return BehaviorTree.NodeState.RUNNING
                    if SalvageOptionsWindow.SelectOption(mode):
                        SalvageOptionsWindow.Confirm()
                        state.confirm_clicked_at = now
                        state.window_detected_at = 0.0
                        _log(node.name, f"Selected salvage option {mode.name} for item={item_name} [{item_id}].")
                        return BehaviorTree.NodeState.RUNNING
                    else:
                        _log(node.name, f"Failed to select salvage option {mode.name} for item={item_name} [{item_id}]; cancelling.", message_type=Console.MessageType.Warning)
                        state.window_detected_at = 0.0
                        SalvageOptionsWindow.Cancel()
                        return BehaviorTree.NodeState.FAILURE

                if state.window_detected_at:
                    state.window_detected_at = 0.0

                # Completion checks.
                current_qty = item.quantity
                initial_qty = state.initial_qty
                desired_qty = state.desired_qty
                confirm_clicked_at = state.confirm_clicked_at

                qty_changed = current_qty < initial_qty
                item_gone = not item.is_inventory_item
                mod_salvaged = _is_mod_salvaged(item, mode)
                windows_closed_after_confirm = (
                    confirm_clicked_at > 0.0
                    and not salvage_window_open
                    and (now - confirm_clicked_at) >= 0.20
                )
                
                time_since_confirm = (now - confirm_clicked_at) * 1000 if confirm_clicked_at > 0.0 else None
                if time_since_confirm is not None and time_since_confirm < pop_up_delays:
                    _log(
                        node.name,
                        f"Salvage confirm clicked for item={item_name} [{item_id}] but waiting for windows to close..."
                        f"Elapsed since confirm: {int(time_since_confirm)} ms."
                    )
                    return BehaviorTree.NodeState.RUNNING
                
                if salvage_window_open:
                    _log(
                        node.name,
                        f"Waiting for salvage-related windows to close for item={item_name} [{item_id}] "
                        f"before restarting or finishing salvage."
                    )
                    return BehaviorTree.NodeState.RUNNING

                if not item_gone and item.is_stackable and qty_changed and current_qty > desired_qty:
                    _log(
                        node.name,
                        f"Partial salvage item={item_name} [{item_id}]: initial_qty={initial_qty}, current_qty={current_qty}, "
                        f"desired_qty={desired_qty}. Restarting for remaining quantity."
                    )
                    state.salvage_started_at = 0.0
                    state.initial_qty = item.quantity
                    
                    return BehaviorTree.NodeState.RUNNING

                if qty_changed or item_gone or windows_closed_after_confirm or mod_salvaged:
                    _log(
                        node.name,
                        f"Salvage complete item={item_name} [{item_id}] mode={mode.name} "
                        f"qty_changed={qty_changed} item_gone={item_gone} "
                        f"windows_closed_after_confirm={windows_closed_after_confirm} mod_salvaged={mod_salvaged} "
                        f"initial_qty={initial_qty} current_qty={current_qty} desired_qty={desired_qty}."
                    )
                    return BehaviorTree.NodeState.SUCCESS

                if (now - float(state.salvage_started_at)) * 1000 >= timeout_ms_per_item:
                    cancelled_window = False
                    if salvage_window_open:
                        cancelled_window = AnySalvageWindow.Cancel()
                    _log(
                        node.name,
                        f"Timeout item={item_name} [{item_id}] mode={mode.name} after {timeout_ms_per_item} ms. "
                        f"initial_qty={initial_qty} current_qty={current_qty} desired_qty={desired_qty} "
                        f"confirm_clicked_at={confirm_clicked_at:.3f} "
                        f"windows={{salvage:{SalvageOptionsWindow.IsOpen()}, "
                        f"lesser_confirm:{LesserSalvageWindow.IsOpen()}, "
                        f"material_confirm:{SalvageConfirmationPopup.IsOpen()}, "
                        f"unidentified:{ExpertSalvageUnidentifiedWindow.IsOpen()}}} "
                        f"cancelled_window={cancelled_window} "
                        f"free_slots={Inventory.GetFreeSlotCount()}.",
                        message_type=Console.MessageType.Warning,
                    )
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                _log(
                    node.name,
                    f"Waiting item={item_name} [{item_id}] mode={mode.name} "
                    f"elapsed_ms={int((now - float(state.salvage_started_at)) * 1000)} "
                    f"initial_qty={initial_qty} current_qty={current_qty} desired_qty={desired_qty} "
                    f"confirm_clicked_at={confirm_clicked_at:.3f} "
                )
                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.SalvageItems", action_fn=_salvage, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def SalvageItems(
            salvage_requests: list[tuple[int, "SalvageMode | int", Optional[int]]],
            preferred_kit_id: Optional[int] = None,
            allow_expert_for_common_materials: bool = False,
            restock_salvage_kits: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            timeout_ms_per_item: int = 1500,
            aftercast_ms: int = 250,
            debug_enabled: bool = False,
        ) -> BehaviorTree:
            """
            Build a tree that salvages multiple items sequentially.

            Meta:
              Expose: true
              Audience: advanced
              Display: Salvage Items
              Purpose: Salvage several inventory items in sequence while reusing the existing per-item salvage UI flow.
              UserDescription: Use this when you want one BT flow that salvages multiple target items.
              Notes: Assigns a unique blackboard state key to each child salvage node to avoid progress collisions.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Items.SalvageItems",
                    children=[
                        BTItems.Items.SalvageItem(
                            item_id=item_id,
                            salvage_mode=salvage_mode,
                            salvage_amount=salvage_amount,
                            preferred_kit_id=preferred_kit_id,
                            allow_expert_for_common_materials=allow_expert_for_common_materials,
                            restock_salvage_kits=restock_salvage_kits,
                            allow_withdraw_gold=allow_withdraw_gold,
                            remaining_storage_gold=remaining_storage_gold,
                            state_key=f"_salvage_state_{index}",
                            timeout_ms_per_item=timeout_ms_per_item,
                            aftercast_ms=aftercast_ms,
                            debug_enabled=debug_enabled,
                        ).root
                        for index, (item_id, salvage_mode, salvage_amount) in enumerate(salvage_requests)
                    ],
                )
            )

        class ItemTransferInstructions:
            """
            Internal transfer-plan entry describing how much item quantity should move into one destination slot.

            Meta:
              Expose: false
              Audience: advanced
              Display: Internal Item Transfer Instructions
              Purpose: Represent one target bag-slot destination and the item quantities that should be moved there.
              UserDescription: Internal support helper class.
              Notes: Used by storage and inventory transfer planning helpers before actual move actions are issued.
            """
            def __init__(self, bag: Bags, slot: int, stack_item: Optional[ItemSnapshot], available_space: int = MAX_STACK_SIZE):                
                """
                Initialize a transfer instruction for one destination slot.

                Meta:
                  Expose: false
                  Audience: advanced
                  Display: Internal Item Transfer Instructions Initializer
                  Purpose: Set up destination bag, slot, stack context, and available space for item transfer planning.
                  UserDescription: Internal support routine.
                  Notes: Available space is reduced automatically when the destination already contains a partial stack.
                """
                self.bag = bag
                self.slot = slot
                self.stack_item = stack_item                
                self.available_space = available_space - stack_item.quantity if stack_item and stack_item.is_stackable else available_space
                
                self.items : list[tuple[ItemSnapshot, int]] = []

        @staticmethod
        def _get_material_storage_capacity(material_storage_snapshot: dict[int, Optional[ItemSnapshot]]) -> int:
            capacity = (
                max(
                    (item.quantity for item in material_storage_snapshot.values() if item),
                    default=0,
                )
                + MAX_STACK_SIZE
                - 1
            ) // MAX_STACK_SIZE * MAX_STACK_SIZE

            return capacity if capacity > 0 else MAX_STACK_SIZE

        @staticmethod
        def _cleanup_empty_transfer_instruction(
            moving_instructions: dict[Bags, dict[int, "BTItems.Items.ItemTransferInstructions"]],
            bag: Bags,
            slot: int,
        ) -> None:
            bag_instructions = moving_instructions.get(bag)
            if not bag_instructions:
                return

            instruction = bag_instructions.get(slot)
            if instruction is not None and not instruction.items:
                bag_instructions.pop(slot, None)

            if not bag_instructions:
                moving_instructions.pop(bag, None)

        @staticmethod
        def _get_planned_transfer_item_ids(
            moving_instructions: dict[Bags, dict[int, "BTItems.Items.ItemTransferInstructions"]],
        ) -> list[int]:
            planned_item_ids: list[int] = []
            seen_item_ids: set[int] = set()

            for bag_instructions in moving_instructions.values():
                for instruction in bag_instructions.values():
                    for item, _ in instruction.items:
                        if item.id in seen_item_ids:
                            continue

                        seen_item_ids.add(item.id)
                        planned_item_ids.append(item.id)

            return planned_item_ids

        @staticmethod
        def _format_transfer_destination(bag: Bags, slot: int) -> str:
            if bag == Bags.MaterialStorage:
                return f"Material Storage slot {slot}"

            return f"bag {bag.name} slot {slot}"

        @staticmethod
        def _get_planned_destinations_for_item(
            moving_instructions: dict[Bags, dict[int, "BTItems.Items.ItemTransferInstructions"]],
            item_id: int,
        ) -> list[str]:
            destinations: list[str] = []

            for bag, bag_instructions in moving_instructions.items():
                for slot, instruction in bag_instructions.items():
                    qty_for_item = sum(qty for planned_item, qty in instruction.items if planned_item.id == item_id)
                    if qty_for_item <= 0:
                        continue

                    destinations.append(
                        f"{qty_for_item} to {BTItems.Items._format_transfer_destination(bag, slot)}"
                    )

            return destinations

        @staticmethod
        def _move_item_to_transfer_destination(
            item: ItemSnapshot,
            destination: "BTItems.Items.ItemTransferInstructions",
            quantity: int,
            log_category: str,
        ) -> None:
            target_bag = Bags.MaterialStorage if destination.bag == Bags.MaterialStorage else destination.bag.value
            Inventory.MoveItem(item.id, target_bag, destination.slot, quantity)
            _log(
                log_category,
                f"Moving {quantity} of '{item.names.plain}' (ID: {item.id}) to {BTItems.Items._format_transfer_destination(destination.bag, destination.slot)}",
            )
        
        @staticmethod
        def GetTransferInstructions(
            item_ids: list[int],
            target : list[Bags],
            quantities: Optional[list[int]] = None,
            fill_materials_first: bool = False,
            log: bool = False,
        ) -> dict[Bags, dict[int, BTItems.Items.ItemTransferInstructions]]:
            """
            Build a destination-slot transfer plan for moving items into target bags.

            Meta:
              Expose: true
              Audience: advanced
              Display: Get Transfer Instructions
              Purpose: Compute a bag-slot transfer plan that minimizes fragmentation and respects stack rules.
              UserDescription: Use this when you need a planning step that figures out where item quantities should move before issuing inventory actions.
              Notes: Supports inventory-to-storage and storage-to-inventory planning, including optional material-storage prefill behavior.
            """
            to_inventory = any(bag in INVENTORY_BAGS for bag in target)
            to_storage = any(bag in STORAGE_BAGS or bag == Bags.MaterialStorage for bag in target) if not to_inventory else False
           
            material_storage_snapshot = ItemSnapshot.get_bag_snapshot(Bags.MaterialStorage) if to_storage else {}
            target_snapshot = ItemSnapshot.get_bags_snapshot(target)
            moving_instructions : dict[Bags, dict[int, BTItems.Items.ItemTransferInstructions]] = {}
            
            material_storage_capacity = BTItems.Items._get_material_storage_capacity(material_storage_snapshot)
                                            
            for index, item_id in enumerate(item_ids):
                item = ItemSnapshot.from_item_id(item_id)
                qty = quantities[index] if quantities and index < len(quantities) else item.quantity if item else 0
                requested_qty = qty
                item_is_inventory = item.is_inventory_item if item is not None else False
                item_is_storage = item.is_storage_item if item is not None else False
                
                if (
                    not item
                    or not item.is_valid
                    or (item_is_inventory and to_inventory)
                    or (item_is_storage and to_storage)
                    or (not item_is_inventory and not item_is_storage)
                ):
                    continue

                def _plan_into_destination(
                    dest_bag: Bags,
                    dest_slot: int,
                    stack_item: Optional[ItemSnapshot],
                    available_space: int,
                ) -> None:
                    nonlocal qty
                    if qty <= 0:
                        return

                    moving_instructions.setdefault(dest_bag, {})
                    dest = moving_instructions[dest_bag].setdefault(
                        dest_slot,
                        BTItems.Items.ItemTransferInstructions(dest_bag, dest_slot, stack_item, available_space=available_space),
                    )

                    if dest.available_space <= 0:
                        return

                    qty_to_move = min(dest.available_space, qty)
                    if qty_to_move <= 0:
                        return

                    dest.available_space -= qty_to_move
                    if item is not None:
                        dest.items.append((item, qty_to_move))
                    
                    qty -= qty_to_move
                
                if item.is_stackable:
                    material_slot = MATERIAL_STORAGE_SLOTS.get(item.model_id)
                    if fill_materials_first and item_is_inventory and (item.is_material or item.is_rare_material) and material_slot is not None:
                        stack_item = material_storage_snapshot.get(material_slot)
                        if stack_item is None or not stack_item.is_valid or stack_item.same_kind_as(item):
                            _plan_into_destination(
                                Bags.MaterialStorage,
                                material_slot,
                                stack_item,
                                material_storage_capacity,
                            )
                        
                    # get all items with the same model and type that have free space in their stacks and add them as potential destinations for the current item until we have found enough space for the whole stack. This way we minimize fragmentation in the bank and maximize the chances of fitting all items. We get them all from bag_enum, bag in inventory_snapshot.items()
                    stacks_of_same_kind_with_space = [(i, bag_id) for bag_id, bag in target_snapshot.items() for i in bag.values() if i and i.is_valid and i.is_stackable and i.same_kind_as(item) and i.quantity < MAX_STACK_SIZE]
                    
                    #sorted by least free space to most free space to fill up more full stacks first, then by bag and slot, so we fill from the beginning of the bank to the end to minimize fragmentation
                    stacks_of_same_kind_with_space.sort(key=lambda x: (-x[0].quantity, x[1].value, x[0].slot))
                    
                    for stack_item, bag in stacks_of_same_kind_with_space:
                        if stack_item.quantity >= MAX_STACK_SIZE or (bag == Bags.MaterialStorage and stack_item.slot == material_slot):
                            continue

                        stack_capacity = material_storage_capacity if bag == Bags.MaterialStorage else MAX_STACK_SIZE
                        _plan_into_destination(bag, stack_item.slot, stack_item, stack_capacity)

                        if qty <= 0:
                            break
                    
                if qty > 0:
                    for bag_enum, bag in target_snapshot.items():
                        for slot, stack_item in bag.items():
                            if stack_item is None:
                                available_space = material_storage_capacity if bag_enum == Bags.MaterialStorage else (MAX_STACK_SIZE if item.is_stackable else 1)
                                _plan_into_destination(bag_enum, slot, None, available_space)
                                                                
                                if qty <= 0:
                                    break
                        
                        if qty <= 0:
                            break

                planned_qty = requested_qty - qty
                destinations = BTItems.Items._get_planned_destinations_for_item(moving_instructions, item.id)
                destination_text = ", ".join(destinations) if destinations else "no destination"

                if planned_qty <= 0:
                    _log(
                        "GetTransferInstructions",
                        f"Could not plan a move for '{item.names.plain}' (ID: {item.id}).",
                        log=log,
                    )
                elif planned_qty < requested_qty:
                    _log(
                        "GetTransferInstructions",
                        f"Planned partial move of {planned_qty}/{requested_qty} for '{item.names.plain}' (ID: {item.id}).\n{destination_text}.",
                        log=log,
                    )
                    
                elif planned_qty == requested_qty:
                    _log(
                        "GetTransferInstructions",
                        f"Planned to move {requested_qty} of '{item.names.plain}' (ID: {item.id}).\n{destination_text}.",
                        log=log,
                    )
                
            return moving_instructions            
        
        @staticmethod
        def DepositItems(
            item_ids: list[int],
            target : list[Bags] = STORAGE_BAGS,
            fill_materials_first: bool = True,
            fail_if_no_space: bool = True,
            aftercast_ms: int = 250,
            precomputed_instructions: Optional[dict[Bags, dict[int, "BTItems.Items.ItemTransferInstructions"]]] = None,
            log: bool = False,
        ):
            """
            Build an action node that deposits items into storage bags using transfer planning.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Deposit Items
              Purpose: Move inventory items into storage according to computed transfer instructions.
              UserDescription: Use this when you want a BT step that deposits known items into storage automatically.
              Notes: Can optionally fail when no valid storage destination exists and supports anniversary-panel bag filtering.
            """
            
            def _deposit(node: BehaviorTree.Node):
                instructions = precomputed_instructions if precomputed_instructions is not None else BTItems.Items.GetTransferInstructions(item_ids, target, fill_materials_first=fill_materials_first)
                moved_any = False
                
                if not instructions:
                    _log("Items.DepositItems", f"No deposit instructions could be created for item ids {item_ids}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE if fail_if_no_space else BehaviorTree.NodeState.SUCCESS
                
                for bag in instructions.values():
                    for dest in bag.values():
                        for item, qty in dest.items:
                            _log("Items.DepositItems", f"Depositing {item.names.plain} (ID: {item.id}) x{qty} to {dest.bag.name} slot {dest.slot}.", log=log)
                            BTItems.Items._move_item_to_transfer_destination(item, dest, qty, node.name)
                            moved_any = True
                
                if not moved_any:
                    _log("Items.DepositItems", "Deposit instructions existed, but no item was moved.", message_type=Console.MessageType.Warning, log=log)
                return BehaviorTree.NodeState.SUCCESS if moved_any else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.DepositItems", action_fn=_deposit, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def GetDepositableItemIds(
            item_ids: list[int],
            target: list[Bags] = STORAGE_BAGS,
            fill_materials_first: bool = True,
            log_plans: bool = False,
        ) -> list[int]:
            instructions = BTItems.Items.GetTransferInstructions(
                item_ids,
                target,
                fill_materials_first=fill_materials_first,
                log=log_plans,
            )

            return BTItems.Items._get_planned_transfer_item_ids(instructions)
        
        @staticmethod
        def WithdrawItems(
            item_ids: list[int],
            target : list[Bags] = INVENTORY_BAGS,
            fill_materials_first: bool = True,
            fail_if_no_space: bool = True,
            aftercast_ms: int = 250,
            log: bool = False,
        ):                   
            """
            Build an action node that withdraws items from storage into inventory using transfer planning.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Withdraw Items
              Purpose: Move storage items into inventory according to computed transfer instructions.
              UserDescription: Use this when you want a BT step that pulls known items from storage automatically.
              Notes: Can optionally fail when no valid inventory destination exists.
            """
            def _withdraw(node: BehaviorTree.Node):
                instructions = BTItems.Items.GetTransferInstructions(item_ids, target, fill_materials_first=fill_materials_first)
                moved_any = False
                
                if not instructions:
                    _log("Items.WithdrawItems", f"No withdraw instructions could be created for item ids {item_ids}.", message_type=Console.MessageType.Warning, log=log)
                    return BehaviorTree.NodeState.FAILURE if fail_if_no_space else BehaviorTree.NodeState.SUCCESS
                
                for bag in instructions.values():
                    for dest in bag.values():
                        for item, qty in dest.items:
                            _log("Items.WithdrawItems", f"Withdrawing {item.names.plain} (ID: {item.id}) x{qty} to {dest.bag.name} slot {dest.slot}.", log=log)
                            BTItems.Items._move_item_to_transfer_destination(item, dest, qty, node.name)
                            moved_any = True
                
                if not moved_any:
                    _log("Items.WithdrawItems", "Withdraw instructions existed, but no item was moved.", message_type=Console.MessageType.Warning, log=log)
                return BehaviorTree.NodeState.SUCCESS if moved_any else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Items.WithdrawItems", action_fn=_withdraw, aftercast_ms=aftercast_ms)
            )

    class XunlaiStorage:
        """
        BT helper group for Xunlai storage-specific operations.
        
        Meta:
          Expose: true
            Audience: intermediate
            Display: Xunlai Storage
            Purpose: Group BT helper routines that manage Xunlai storage interactions and organization.
            UserDescription: Built-in BT helper group for Xunlai storage management routines.
            Notes: These routines typically involve transfer planning and may include Xunlai-specific bag handling logic.
        """
        
        @staticmethod
        def FillMaterialStorage(
            source : list[Bags] = STORAGE_BAGS,
            aftercast_ms: int = 250,
            succeed_if_already_filled: bool = True,
        ):
            """
            Build an action node that fills material storage from the provided source bags.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Fill Material Storage
              Purpose: Move stackable material items into their material-storage slots.
              UserDescription: Use this when you want a BT step that consolidates materials into material storage automatically.
              Notes: Succeeds when any move is made or, optionally, when the storage is already effectively full.
            """
            def _fill_material_storage(node: BehaviorTree.Node):
                source_bags = [bag for bag in source if bag != Bags.MaterialStorage]
                if not source_bags:
                    return BehaviorTree.NodeState.FAILURE

                source_snapshot = ItemSnapshot.get_bags_snapshot(source_bags)
                material_snapshot = ItemSnapshot.get_bag_snapshot(Bags.MaterialStorage)

                material_storage_capacity = (
                    max((item.quantity for item in material_snapshot.values() if item), default=0) + MAX_STACK_SIZE - 1
                ) // MAX_STACK_SIZE * MAX_STACK_SIZE
                if material_storage_capacity <= 0:
                    material_storage_capacity = MAX_STACK_SIZE

                moved_any = False
                transfer_instructions: dict[int, BTItems.Items.ItemTransferInstructions] = {}
                bag_item_map : dict[int, Bags] = {item_id: bag for bag, bag_items in source_snapshot.items() for item_id, item in bag_items.items() if item}
                
                for _, bag_items in source_snapshot.items():
                    for _, item in bag_items.items():
                        if item is None or not item.is_valid or not item.is_stackable or bag_item_map.get(item.id) == Bags.MaterialStorage:
                            continue
                        
                        if not (item.is_material or item.is_rare_material):
                            continue
                        
                        slot = MATERIAL_STORAGE_SLOTS.get(item.model_id, None)
                        if slot is None:
                            continue
                        
                        material = material_snapshot.get(slot, None)
                        transfer_instructions.setdefault(slot, BTItems.Items.ItemTransferInstructions(Bags.MaterialStorage, slot, material, available_space=material_storage_capacity))
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
                        BTItems.Items._move_item_to_transfer_destination(item, dest, qty, node.name)
                        moved_any = True

                return _success_if(moved_any or succeed_if_already_filled)

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Inventory.FillMaterialStorage", action_fn=_fill_material_storage, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def DepositItem(
            item_id: int,
            target : list[Bags] = STORAGE_BAGS,
            fill_materials_first: bool = True,
            fail_if_no_space: bool = True,
            aftercast_ms: int = 250,
        ):
            """
            Build an action node that deposits a single item into storage using transfer planning.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Deposit Item
              Purpose: Move one inventory item into storage according to computed transfer instructions.
              UserDescription: Use this when you want a BT step that deposits a known item into storage automatically.
              Notes: Can optionally fail when no valid storage destination exists and supports anniversary-panel bag filtering.
            """
            return BTItems.Items.DepositItems(
                item_ids=[item_id],
                target=target,
                fill_materials_first=fill_materials_first,
                fail_if_no_space=fail_if_no_space,
                aftercast_ms=aftercast_ms,
        )

    class Bags:
        """
        BT helper group for bag-level operations, compaction, and sorting flows.

        Meta:
          Expose: true
          Audience: advanced
          Display: Bags
          Purpose: Group BT helper routines that reorganize or refill inventory and storage bags.
          UserDescription: Built-in BT helper group for bag maintenance and organization routines.
          Notes: These routines typically operate on bag snapshots and issue multiple move actions per execution.
        """
        
        @staticmethod
        def GetBagLocation(item_id: int) -> tuple[Optional[Bags], Optional[int]]:
            """
            Get the bag enum for a given item id.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Get Bag For Item
            Purpose: Determine which bag an inventory item is currently in.
            UserDescription: Use this when you have an item id and need to know which bag it's located in.
            Notes: Returns None if the item is not found in any bag.
            """
            bags = [
                *INVENTORY_WITH_EQUIPMENT_BAGS,
                Bags.UnclaimedItems,
                Bags.EquippedItems,
                *STORAGE_BAGS,
                Bags.MaterialStorage,
                Bags.NoBag                
            ]
            for bag in bags:
                snapshot = ItemSnapshot.get_bag_snapshot(bag)
                item = next((item for item in snapshot.values() if item and item.is_valid and item.id == item_id), None)
                if item is not None:
                    return bag, item.slot
                
            return None, None
            
        @staticmethod
        def MoveTo(
            item_id: int,
            target_bag: int = Bags.Backpack,
            slot: int = 0,
            log: bool = False,
            required: bool = True,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that moves the first matching model id into a target bag slot.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Move Model To Bag Slot
            Purpose: Move an inventory item model into a specific bag and slot.
            UserDescription: Use this when you want a known model to be organized into a specific inventory location.
            Notes: Optional mode succeeds quietly on failure, while required mode fails and logs a warning.
            """
            def _move_item_to_bag_slot():
                """
                Move the first matching model id into the requested bag slot.

                Meta:
                Expose: false
                Audience: advanced
                Display: Internal Move Model To Bag Slot Helper
                Purpose: Perform the actual inventory move request for the enclosing routine.
                UserDescription: Internal support routine.
                Notes: Required mode fails on move failure; optional mode succeeds quietly.
                """
                bag, item_slot = BTItems.Bags.GetBagLocation(item_id)
                
                try:
                    desired_bag = Bags(target_bag) if isinstance(target_bag, int) else target_bag
                except ValueError:
                    _fail_log(
                        "MoveModelToBagSlot",
                        f"Invalid target bag {target_bag} for item ID {item_id}.",
                    )
                    return BehaviorTree.NodeState.FAILURE
                
                if bag == desired_bag and item_slot == slot:
                    return BehaviorTree.NodeState.SUCCESS
                
                if bag is None or item_slot is None:
                    if required:
                        _fail_log(
                            "MoveModelToBagSlot",
                            f"Item with ID {item_id} not found in any bag; cannot move to bag {desired_bag.name} slot {slot}.",
                        )
                        
                        return BehaviorTree.NodeState.FAILURE
                    return BehaviorTree.NodeState.SUCCESS
                
                Inventory.MoveItem(item_id, desired_bag, slot)
                item = ItemSnapshot.from_item_id(item_id)
                item_name = item.names.plain if item and item.names.plain != item.names.fallback else f"Item (ID: {item_id})"
                
                _log(
                    "MoveModelToBagSlot",
                    f"Moved {item_name} to slot {slot} in {desired_bag.name}.",
                    message_type=Console.MessageType.Info,
                    log=log,
                )
                return BehaviorTree.NodeState.SUCCESS

            tree = BehaviorTree.ActionNode(
                name="MoveModelToBagSlot",
                action_fn=_move_item_to_bag_slot,
                aftercast_ms=aftercast_ms,
            )
            return BehaviorTree(tree)

        @staticmethod
        def GetBagSortPlan(
            bags: list[Bags] = INVENTORY_BAGS,
        ) -> BagSortPlan:
            snapshot = ItemSnapshot.get_bags_snapshot(bags)
            sorting_config = SortingConfig()
            plan = BagSortPlan()
            remaining_items: list[ItemSnapshot] = [
                item
                for bag in bags
                for _, item in sorted(snapshot.get(bag, {}).items())
                if item is not None and item.is_valid
            ]
            occupied_slots: set[tuple[Bags, int]] = set()

            for bag in bags:
                plan.layout[bag] = {
                    slot: None
                    for slot in sorted(snapshot.get(bag, {}).keys())
                }

            explicit_groups: list[tuple[Bags, SlotGroupConfig, list[int]]] = []
            for bag in bags:
                bag_groups = sorted(
                    sorting_config.get_groups_for_bag(bag),
                    key=lambda group: min(group.normalized_slots_for_bag(bag)) if group.normalized_slots_for_bag(bag) else 9999,
                )
                for group in bag_groups:
                    slots = [
                        slot
                        for slot in group.normalized_slots_for_bag(bag)
                        if slot in plan.layout.get(bag, {}) and (bag, slot) not in occupied_slots
                    ]
                    if not slots:
                        continue

                    explicit_groups.append((bag, group, slots))
                    occupied_slots.update((bag, slot) for slot in slots)

            for bag, group, slots in explicit_groups:
                matching_items = sorted(
                    [item for item in remaining_items if group.matches(item)],
                    key=lambda item: group.sorter.get_sort_key(item),
                )

                for slot_index, slot in enumerate(slots):
                    planned_item = matching_items[slot_index] if slot_index < len(matching_items) else None
                    if planned_item is not None:
                        remaining_items.remove(planned_item)

                    plan.layout[bag][slot] = planned_item
                    plan.entries.append(
                        BagSortPreviewEntry(
                            bag=bag,
                            slot=slot,
                            item=planned_item,
                            source_bag=planned_item.bag if planned_item is not None else None,
                            source_slot=planned_item.slot if planned_item is not None else None,
                            group_name=group.display_name(),
                            group_summary=group.matcher.summary(),
                            sorter=group.sorter,
                            used_fallback=False,
                        )
                    )

            default_slots = [
                (bag, slot)
                for bag in bags
                for slot in sorted(plan.layout.get(bag, {}).keys())
                if (bag, slot) not in occupied_slots
            ]
            default_sorted_items = sorted(
                remaining_items,
                key=lambda item: sorting_config.default_sorter.get_sort_key(item),
            )

            assigned_default_count = 0
            for bag, slot in default_slots:
                planned_item = default_sorted_items[assigned_default_count] if assigned_default_count < len(default_sorted_items) else None
                if planned_item is not None:
                    assigned_default_count += 1

                plan.layout[bag][slot] = planned_item
                plan.entries.append(
                    BagSortPreviewEntry(
                        bag=bag,
                        slot=slot,
                        item=planned_item,
                        source_bag=planned_item.bag if planned_item is not None else None,
                        source_slot=planned_item.slot if planned_item is not None else None,
                        group_name='Default',
                        group_summary='Any item',
                        sorter=sorting_config.default_sorter,
                        used_fallback=False,
                    )
                )

            remaining_items = default_sorted_items[assigned_default_count:]
            fallback_slots = [
                entry
                for entry in plan.entries
                if entry.item is None and entry.group_name != 'Default'
            ]

            if remaining_items and fallback_slots:
                plan.warnings.append(
                    'Some items did not match any open/default slot and were placed into reserved slots as fallback.'
                )
                for fallback_entry in fallback_slots:
                    if not remaining_items:
                        break

                    planned_item = remaining_items.pop(0)
                    fallback_entry.item = planned_item
                    fallback_entry.source_bag = planned_item.bag
                    fallback_entry.source_slot = planned_item.slot
                    fallback_entry.used_fallback = True
                    plan.layout[fallback_entry.bag][fallback_entry.slot] = planned_item

            if remaining_items:
                plan.warnings.append(
                    f'{len(remaining_items)} item(s) could not be assigned by the planner and will remain unsorted until more slots are available.'
                )

            plan.entries.sort(key=lambda entry: (entry.bag.value, entry.slot))
            return plan

        @staticmethod
        def GetPlannedBagLayout(
            bags: list[Bags] = INVENTORY_BAGS,
        ) -> dict[Bags, dict[int, Optional[ItemSnapshot]]]:
            """
            Build the planned bag layout for the current default sort order without moving items.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Get Planned Bag Layout
              Purpose: Compute the target bag-slot layout that Sort Bags would currently try to produce.
              UserDescription: Use this when you want to inspect or compare the default planned bag arrangement before executing it.
              Notes: Returns a slot map using the current live snapshot and the same ordering rules as Sort Bags.
            """
            return BTItems.Bags.GetBagSortPlan(bags).layout

        @staticmethod
        def CompactBags(
            bags : list[Bags] = INVENTORY_BAGS,         
            aftercast_ms: int = 250,
        ):
            """
            Build an action node that merges partial stacks across bags.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Compact Bags
              Purpose: Reduce stack fragmentation by combining partial stacks of matching items.
              UserDescription: Use this when you want a BT step that tidies bag stacks and frees space.
              Notes: Operates only on stackable items and succeeds only if at least one move is performed.
            """
            def _compact(node: BehaviorTree.Node):
                snapshot = ItemSnapshot.get_bags_snapshot(bags)
                grouped_items : dict[tuple[ItemType, int, int], list[tuple[Bags, int, ItemSnapshot]]] = {}
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
                        _log(node.name, f"Moved {qty_to_move} of '{source_item.names.plain}' (ID: {source_item.id}) from bag {source_bag.name} slot {source_slot} to bag {target_bag.name} slot {target_slot}")
                        moved_any = True
                        target_item.quantity += qty_to_move
                        source_item.quantity -= qty_to_move
                
                
                return _success_if(moved_any)
            return BehaviorTree(
                BehaviorTree.ActionNode(name="Inventory.CompactBags", action_fn=_compact, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def SortBags(
            bags : list[Bags] = INVENTORY_BAGS,         
            aftercast_ms: int = 250,
        ):
            """
            Build an action node that sorts items across bags using the current default sort order.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Sort Bags
              Purpose: Reorder bag contents according to the current item-type and value-based sorting rules.
              UserDescription: Use this when you want a BT step that applies the current default bag sort order.
              Notes: The sort configuration is still marked as provisional in the implementation comments.
            """
            def _sort(node: BehaviorTree.Node):
                planned_layout = BTItems.Bags.GetPlannedBagLayout(bags)
                moved_any = False

                for bag in bags:
                    for slot, planned_item in sorted(planned_layout.get(bag, {}).items()):
                        if planned_item is None or not planned_item.is_valid:
                            continue

                        if planned_item.bag == bag and planned_item.slot == slot:
                            continue

                        Inventory.MoveItem(planned_item.id, bag.value, slot, planned_item.quantity)
                        moved_any = True

                return _success_if(moved_any)

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Inventory.SortBags", action_fn=_sort, aftercast_ms=aftercast_ms)
            )

    class Crafting:
        """
        BT helper group for crafter recipe execution flows.

        Meta:
          Expose: true
          Audience: advanced
          Display: Crafting
          Purpose: Group BT helper routines that issue crafter recipe actions.
          UserDescription: Built-in BT helper group for crafting actions.
          Notes: These routines expect the relevant crafting context to already be open and valid.
        """
        
        @dataclass
        class Ingredient:
            model_id: int
            required_quantity: int
            item_id: int = 0
            available_quantity: int = 0

        @staticmethod
        def _normalize_recipe_ingredients(
            material_model_ids: Sequence[int],
            material_quantities: Sequence[int],
        ) -> tuple[list[int], list[int]]:
            normalized_quantities_by_model: dict[int, int] = {}
            ordered_model_ids: list[int] = []

            for model_id, required_quantity in zip(material_model_ids, material_quantities):
                if model_id not in normalized_quantities_by_model:
                    ordered_model_ids.append(model_id)
                    normalized_quantities_by_model[model_id] = 0
                normalized_quantities_by_model[model_id] += required_quantity

            return ordered_model_ids, [normalized_quantities_by_model[model_id] for model_id in ordered_model_ids]

        @staticmethod
        def _get_output_item_id(output_model_id: int) -> int:
            offered_items = ItemSnapshot.get_items(Trading.Crafter.GetOfferedItems())
            for item in offered_items:
                if item and item.is_valid and item.model_id == output_model_id:
                    return item.id
            return 0

        @staticmethod
        def _compact_ingredient_stacks(material_model_ids: Sequence[int]) -> bool:
            recipe_model_ids = set(material_model_ids)
            if not recipe_model_ids:
                return False

            inventory = ItemSnapshot.get_bags_items(INVENTORY_BAGS)
            grouped_items: dict[int, list[ItemSnapshot]] = {}

            for item in inventory:
                if (
                    item
                    and item.is_valid
                    and item.is_stackable
                    and item.quantity < MAX_STACK_SIZE
                    and item.model_id in recipe_model_ids
                ):
                    grouped_items.setdefault(item.model_id, []).append(item)

            for model_id, items in grouped_items.items():
                if len(items) <= 1:
                    continue

                items.sort(key=lambda candidate: candidate.quantity, reverse=True)
                target_item = items[0]

                for source_item in items[1:]:
                    qty_to_move = min(source_item.quantity, MAX_STACK_SIZE - target_item.quantity)
                    if qty_to_move <= 0:
                        continue

                    Inventory.MoveItem(source_item.id, target_item.bag.value, target_item.slot, qty_to_move)
                    _log(
                        "Crafting.CraftItemByModelID",
                        (
                            f"Compacting ingredient model {model_id}: moved {qty_to_move} "
                            f"from item_id={source_item.id} to item_id={target_item.id}."
                        ),
                    )
                    return True

            return False

        @staticmethod
        def _get_live_ingredients(
            material_model_ids: Sequence[int],
            material_quantities: Sequence[int],
        ) -> tuple[list["BTItems.Crafting.Ingredient"], dict[int, int]]:
            inventory = ItemSnapshot.get_bags_items(INVENTORY_BAGS)
            ingredients: list[BTItems.Crafting.Ingredient] = []
            available_by_model: dict[int, int] = {model_id: 0 for model_id in material_model_ids}

            for model_id, required_quantity in zip(material_model_ids, material_quantities):
                matching_items = [
                    item
                    for item in inventory
                    if item and item.is_valid and item.model_id == model_id and item.quantity > 0
                ]
                available_by_model[model_id] = sum(item.quantity for item in matching_items)

                if matching_items:
                    ingredients.append(
                        BTItems.Crafting.Ingredient(
                            model_id=model_id,
                            required_quantity=required_quantity,
                            item_id=matching_items[0].id,
                            available_quantity=matching_items[0].quantity,
                        )
                    )
                else:
                    ingredients.append(BTItems.Crafting.Ingredient(model_id=model_id, required_quantity=required_quantity))

            return ingredients, available_by_model

        @staticmethod
        def _get_max_craftable_quantity(
            requested_quantity: int,
            cost: int,
            material_model_ids: Sequence[int],
            material_quantities: Sequence[int],
            available_gold: Optional[int] = None,
        ) -> int:
            if requested_quantity <= 0:
                return 0

            _, available_by_model = BTItems.Crafting._get_live_ingredients(material_model_ids, material_quantities)
            craftable_quantity = requested_quantity

            for model_id, required_quantity in zip(material_model_ids, material_quantities):
                if required_quantity <= 0:
                    continue
                craftable_quantity = min(craftable_quantity, available_by_model.get(model_id, 0) // required_quantity)

            if cost > 0:
                spendable_gold = Inventory.GetGoldOnCharacter() if available_gold is None else int(available_gold)
                craftable_quantity = min(craftable_quantity, spendable_gold // cost)

            return max(0, craftable_quantity)

        @staticmethod
        def _get_live_direct_ingredients(
            material_item_ids: Sequence[int],
            material_quantities: Sequence[int],
        ) -> tuple[list["BTItems.Crafting.Ingredient"], dict[int, int], bool]:
            recipe_items: list[tuple[ItemSnapshot, int]] = []

            for item_id, required_quantity in zip(material_item_ids, material_quantities):
                if required_quantity <= 0:
                    return [], {}, False

                item = ItemSnapshot.from_item_id(item_id)
                if item is None or not item.is_valid:
                    return [], {}, False

                recipe_items.append((item, required_quantity))

            normalized_quantities_by_model: dict[int, int] = {}
            ordered_model_ids: list[int] = []

            for item, required_quantity in recipe_items:
                if item.model_id not in normalized_quantities_by_model:
                    ordered_model_ids.append(item.model_id)
                    normalized_quantities_by_model[item.model_id] = 0
                normalized_quantities_by_model[item.model_id] += required_quantity

            normalized_quantities = [normalized_quantities_by_model[model_id] for model_id in ordered_model_ids]
            ingredients, available_by_model = BTItems.Crafting._get_live_ingredients(ordered_model_ids, normalized_quantities)
            return ingredients, available_by_model, True
                
        @staticmethod
        def CraftItem(
            output_item_id: int,
            cost: int,
            material_item_ids: list[int],
            material_quantities: list[int],
            quantity: int = 1,
            allow_partial: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build an action node that crafts one item recipe.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Craft Item
              Purpose: Issue one crafter recipe request with the provided material ids and quantities.
              UserDescription: Use this when you want a BT step that crafts one configured recipe.
              Notes: Fails when the output item id is invalid or the recipe input arrays are empty.
            """
            def _craft(node: BehaviorTree.Node):
                k = min(len(material_item_ids), len(material_quantities))

                if output_item_id <= 0 or k == 0 or quantity <= 0:
                    return BehaviorTree.NodeState.FAILURE

                recipe_item_ids = material_item_ids[:k]
                recipe_quantities = material_quantities[:k]
                state_key = f"{node.id}_craft_item"
                state = cast(Optional[dict], node.blackboard.get(state_key))

                if state is None:
                    ingredients, available_by_model, resolved = BTItems.Crafting._get_live_direct_ingredients(
                        recipe_item_ids,
                        recipe_quantities,
                    )
                    if not resolved:
                        return BehaviorTree.NodeState.FAILURE

                    craftable_now = quantity
                    for ingredient in ingredients:
                        craftable_now = min(
                            craftable_now,
                            available_by_model.get(ingredient.model_id, 0) // ingredient.required_quantity,
                        )

                    if cost > 0:
                        craftable_now = min(craftable_now, BTItems.Inventory._get_spendable_gold(allow_withdraw_gold, remaining_storage_gold) // cost)

                    if craftable_now < quantity and not allow_partial:
                        return BehaviorTree.NodeState.FAILURE

                    state = {
                        "target_quantity": quantity if not allow_partial else craftable_now,
                        "crafted_quantity": 0,
                    }
                    node.blackboard[state_key] = state

                crafted_quantity = int(state.get("crafted_quantity", 0) or 0)
                target_quantity = int(state.get("target_quantity", 0) or 0)

                if crafted_quantity >= target_quantity:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

                ingredients, available_by_model, resolved = BTItems.Crafting._get_live_direct_ingredients(
                    recipe_item_ids,
                    recipe_quantities,
                )
                if not resolved:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                if BTItems.Crafting._compact_ingredient_stacks([ingredient.model_id for ingredient in ingredients]):
                    return BehaviorTree.NodeState.RUNNING

                ingredients, available_by_model, resolved = BTItems.Crafting._get_live_direct_ingredients(
                    recipe_item_ids,
                    recipe_quantities,
                )
                if not resolved:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                for ingredient in ingredients:
                    if (
                        available_by_model.get(ingredient.model_id, 0) < ingredient.required_quantity
                        or ingredient.available_quantity < ingredient.required_quantity
                        or ingredient.item_id == 0
                    ):
                        node.blackboard.pop(state_key, None)
                        return BehaviorTree.NodeState.FAILURE

                if cost > 0 and Inventory.GetGoldOnCharacter() < cost:
                    if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(cost, remaining_storage_gold) > 0:
                        return BehaviorTree.NodeState.RUNNING
                    node.blackboard.pop(state_key, None)
                    if allow_partial and crafted_quantity > 0:
                        return BehaviorTree.NodeState.SUCCESS
                    return BehaviorTree.NodeState.FAILURE

                Trading.Crafter.CraftItem(
                    output_item_id,
                    cost,
                    [ingredient.item_id for ingredient in ingredients],
                    [ingredient.required_quantity for ingredient in ingredients],
                )
                state["crafted_quantity"] = crafted_quantity + 1
                node.blackboard[state_key] = state
                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Crafting.CraftItem", action_fn=_craft, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def CraftItems(
            recipes: list[tuple[int, int, list[int], list[int], int]],
            allow_partial: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that crafts multiple direct-id recipes sequentially.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Craft Items
              Purpose: Craft several configured crafter recipes in sequence using direct offered item ids.
              UserDescription: Use this when you want to craft multiple different crafter outputs in one BT flow.
              Notes: Runs the single-item craft BT for each recipe entry in order.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Crafting.CraftItems",
                    children=[
                        BTItems.Crafting.CraftItem(
                            output_item_id=output_item_id,
                            cost=cost,
                            material_item_ids=material_item_ids,
                            material_quantities=material_quantities,
                            quantity=quantity,
                            allow_partial=allow_partial,
                            allow_withdraw_gold=allow_withdraw_gold,
                            remaining_storage_gold=remaining_storage_gold,
                            aftercast_ms=aftercast_ms,
                        ).root
                        for output_item_id, cost, material_item_ids, material_quantities, quantity in recipes
                    ],
                )
            )

        @staticmethod
        def CraftItemModelID(
            output_model_id: int,
            cost: int,
            material_model_ids: list[int],
            material_quantities: list[int],
            quantity: int = 1,
            allow_partial: bool = True,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            log: bool = False,
            aftercast_ms: int = 250,            
        ) -> BehaviorTree:
            """
            Build an action node that crafts one item recipe by output model id.

            Meta:
                Expose: true
                Audience: intermediate
                Display: Craft Item By Model ID
                Purpose: Issue one crafter recipe request with the provided material ids and quantities, targeting an output model id.
                UserDescription: Use this when you want a BT step that crafts one configured recipe by model id.
                Notes: Fails when the output model id is invalid or the recipe input arrays are empty.
            """
            def _craft(node: BehaviorTree.Node):
                k = min(len(material_model_ids), len(material_quantities))

                if output_model_id <= 0 or k == 0 or quantity <= 0:
                    _log(
                        "Crafting.CraftItemByModelID",
                        f"Invalid recipe configuration: output_model_id={output_model_id}, material_model_ids={material_model_ids}, material_quantities={material_quantities}, quantity={quantity}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE

                recipe_model_ids = material_model_ids[:k]
                recipe_quantities = material_quantities[:k]
                recipe_model_ids, recipe_quantities = BTItems.Crafting._normalize_recipe_ingredients(
                    recipe_model_ids,
                    recipe_quantities,
                )
                if any(required_quantity <= 0 for required_quantity in recipe_quantities):
                    _log(
                        "Crafting.CraftItemByModelID",
                        f"Invalid recipe configuration: output_model_id={output_model_id}, material_model_ids={material_model_ids}, material_quantities={material_quantities}, quantity={quantity}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE

                state_key = f"{node.id}_craft_item_model_id"
                state = cast(Optional[dict], node.blackboard.get(state_key))

                if state is None:
                    craftable_now = BTItems.Crafting._get_max_craftable_quantity(
                        quantity,
                        cost,
                        recipe_model_ids,
                        recipe_quantities,
                        available_gold=BTItems.Inventory._get_spendable_gold(allow_withdraw_gold, remaining_storage_gold),
                    )
                    if craftable_now <= 0:
                        _log(
                            "Crafting.CraftItemByModelID",
                            f"Cannot craft item with output model ID {output_model_id} due to insufficient materials or gold.",
                            message_type=Console.MessageType.Info,
                            log=log,
                        )
                        return BehaviorTree.NodeState.FAILURE

                    if not allow_partial and craftable_now < quantity:
                        _log(
                            "Crafting.CraftItemByModelID",
                            f"Cannot craft full quantity {quantity} of item with output model ID {output_model_id} (craftable: {craftable_now}) and partial crafting is not allowed.",
                            message_type=Console.MessageType.Info,
                            log=log,
                        )
                        return BehaviorTree.NodeState.FAILURE

                    state = {
                        "target_quantity": quantity if not allow_partial else craftable_now,
                        "crafted_quantity": 0,
                    }
                    node.blackboard[state_key] = state

                crafted_quantity = int(state.get("crafted_quantity", 0) or 0)
                target_quantity = int(state.get("target_quantity", 0) or 0)

                if crafted_quantity >= target_quantity:
                    node.blackboard.pop(state_key, None)
                    _log(
                        "Crafting.CraftItemByModelID",
                        f"Crafting complete for item with output model ID {output_model_id}: crafted {crafted_quantity}/{target_quantity}.",
                        message_type=Console.MessageType.Info,
                        log=log,
                    )
                    return BehaviorTree.NodeState.SUCCESS

                if BTItems.Crafting._compact_ingredient_stacks(recipe_model_ids):
                    _log(
                        "Crafting.CraftItemByModelID",
                        f"Compacted ingredient stacks for crafting item with output model ID {output_model_id}.",
                        message_type=Console.MessageType.Debug,
                        log=log,
                    )
                    return BehaviorTree.NodeState.RUNNING

                output_item_id = BTItems.Crafting._get_output_item_id(output_model_id)
                if output_item_id == 0:
                    node.blackboard.pop(state_key, None)
                    _log(
                        "Crafting.CraftItemByModelID",
                        f"Failed to resolve output item ID for model ID {output_model_id}.",
                        message_type=Console.MessageType.Warning,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE

                ingredients, available_by_model = BTItems.Crafting._get_live_ingredients(recipe_model_ids, recipe_quantities)

                for ingredient in ingredients:
                    if (
                        available_by_model.get(ingredient.model_id, 0) < ingredient.required_quantity
                        or ingredient.available_quantity < ingredient.required_quantity
                        or ingredient.item_id == 0
                    ):
                        node.blackboard.pop(state_key, None)
                        if allow_partial and crafted_quantity > 0:
                            _log(
                                "Crafting.CraftItemByModelID",
                                f"Partially crafted {crafted_quantity}/{target_quantity} of item with output model ID {output_model_id} due to insufficient materials, and partial crafting is allowed.",
                                message_type=Console.MessageType.Info,
                                log=log,
                            )
                            return BehaviorTree.NodeState.SUCCESS
                        
                        _log(
                            "Crafting.CraftItemByModelID",
                            f"Insufficient materials for crafting item with output model ID {output_model_id}. Needed {ingredient.required_quantity} of model ID {ingredient.model_id}, but only {available_by_model.get(ingredient.model_id, 0)} available.",
                            message_type=Console.MessageType.Info,
                            log=log,
                        )
                        return BehaviorTree.NodeState.FAILURE

                if cost > 0 and Inventory.GetGoldOnCharacter() < cost:
                    if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(cost, remaining_storage_gold) > 0:
                        _log(
                            "Crafting.CraftItemByModelID",
                            f"Withdrew gold for crafting item with output model ID {output_model_id}.",
                            message_type=Console.MessageType.Debug,
                            log=log,
                        )
                        return BehaviorTree.NodeState.RUNNING
                    node.blackboard.pop(state_key, None)
                    if allow_partial and crafted_quantity > 0:
                        _log(
                            "Crafting.CraftItemByModelID",
                            f"Partially crafted {crafted_quantity}/{target_quantity} of item with output model ID {output_model_id} due to insufficient gold, and partial crafting is allowed.",
                            message_type=Console.MessageType.Info,
                            log=log,
                        )
                        return BehaviorTree.NodeState.SUCCESS
                    
                    _log(
                        "Crafting.CraftItemByModelID",
                        f"Insufficient gold for crafting item with output model ID {output_model_id}. Needed {cost} gold, but only {Inventory.GetGoldOnCharacter()} available.",
                        message_type=Console.MessageType.Info,
                        log=log,
                    )
                    return BehaviorTree.NodeState.FAILURE

                Trading.Crafter.CraftItem(
                    output_item_id,
                    cost,
                    [ingredient.item_id for ingredient in ingredients],
                    [ingredient.required_quantity for ingredient in ingredients],
                )
                state["crafted_quantity"] = crafted_quantity + 1
                node.blackboard[state_key] = state
                _log(
                    "Crafting.CraftItemByModelID",
                    f"Crafted 1 unit of item with output model ID {output_model_id} (crafted {state['crafted_quantity']}/{state['target_quantity']}).",
                    message_type=Console.MessageType.Info,
                    log=log,
                )
                return BehaviorTree.NodeState.RUNNING
            
            return BehaviorTree(
                BehaviorTree.ActionNode(name="Crafting.CraftItemByModelID", action_fn=_craft, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def CraftItemsModelID(
            recipes: list[tuple[int, int, list[int], list[int], int, bool]],
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that crafts multiple model-id recipes sequentially.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Craft Items By Model ID
              Purpose: Craft several configured crafter recipes in sequence using output and material model ids.
              UserDescription: Use this when you want to craft multiple different outputs by model id in one BT flow.
              Notes: Runs the single model-id craft BT for each recipe entry in order.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Crafting.CraftItemsByModelID",
                    children=[
                        BTItems.Crafting.CraftItemModelID(
                            output_model_id=output_model_id,
                            cost=cost,
                            material_model_ids=material_model_ids,
                            material_quantities=material_quantities,
                            quantity=quantity,
                            allow_partial=allow_partial,
                            allow_withdraw_gold=allow_withdraw_gold,
                            remaining_storage_gold=remaining_storage_gold,
                            aftercast_ms=aftercast_ms,
                        ).root
                        for output_model_id, cost, material_model_ids, material_quantities, quantity, allow_partial in recipes
                    ],
                )
            )

        @staticmethod
        def CustomizeWeapon(
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that clicks the crafter customize-weapon button.

            Meta:
            Expose: true
            Audience: intermediate
            Display: Customize Weapon
            Purpose: Click the customize-weapon button when the merchant window is open.
            UserDescription: Use this when you want to trigger weapon customization from an open merchant or crafter window.
            Notes: Resolves the target frame through `frame_aliases.json` using the provided label.
            """
            def _click_customize_weapon() -> BehaviorTree.NodeState:
                return BehaviorTree.NodeState.SUCCESS if CrafterWindow.CustomizeWeapon() else BehaviorTree.NodeState.FAILURE

            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="Crafting.CustomizeWeapon",
                    action_fn=_click_customize_weapon,
                    aftercast_ms=aftercast_ms,
                )
            )
            
    class Collector:
        """
        BT helper group for collector item pickup flows.

        Meta:
          Expose: true
          Audience: advanced
          Display: Collector
          Purpose: Group BT helper routines that issue collector item pickup actions.
          UserDescription: Built-in BT helper group for collector pickup actions.
          Notes: These routines expect the relevant collector context to already be open and valid.
        """
        
        @staticmethod
        def _get_output_item_id(output_model_id: int) -> int:
            offered_items = ItemSnapshot.get_items(Trading.Collector.GetOfferedItems())
            for item in offered_items:
                if item and item.is_valid and item.model_id == output_model_id:
                    return item.id
            return 0

        @staticmethod
        def ExchangeItem(
            output_item_id: int,
            cost: int,
            material_item_ids: list[int],
            material_quantities: list[int],
            quantity: int = 1,
            allow_partial: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that exchanges one collector recipe by direct item ids.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Exchange Collector Item
              Purpose: Issue one collector exchange request with direct offered item and material ids.
              UserDescription: Use this when you want a BT step that exchanges a collector reward with fixed item ids.
              Notes: Validates current ingredient stacks on every tick and progresses one exchange per tick.
            """
            def _exchange(node: BehaviorTree.Node):
                k = min(len(material_item_ids), len(material_quantities))

                if output_item_id <= 0 or k == 0 or quantity <= 0:
                    return BehaviorTree.NodeState.FAILURE

                recipe_item_ids = material_item_ids[:k]
                recipe_quantities = material_quantities[:k]
                state_key = f"{node.id}_collector_exchange_item"
                state = cast(Optional[dict], node.blackboard.get(state_key))

                if state is None:
                    ingredients, available_by_model, resolved = BTItems.Crafting._get_live_direct_ingredients(
                        recipe_item_ids,
                        recipe_quantities,
                    )
                    if not resolved:
                        return BehaviorTree.NodeState.FAILURE

                    exchangeable_now = quantity
                    for ingredient in ingredients:
                        exchangeable_now = min(
                            exchangeable_now,
                            available_by_model.get(ingredient.model_id, 0) // ingredient.required_quantity,
                        )

                    if cost > 0:
                        exchangeable_now = min(exchangeable_now, BTItems.Inventory._get_spendable_gold(allow_withdraw_gold, remaining_storage_gold) // cost)

                    if exchangeable_now < quantity and not allow_partial:
                        return BehaviorTree.NodeState.FAILURE

                    state = {
                        "target_quantity": quantity if not allow_partial else exchangeable_now,
                        "exchanged_quantity": 0,
                    }
                    node.blackboard[state_key] = state

                exchanged_quantity = int(state.get("exchanged_quantity", 0) or 0)
                target_quantity = int(state.get("target_quantity", 0) or 0)

                if exchanged_quantity >= target_quantity:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

                ingredients, available_by_model, resolved = BTItems.Crafting._get_live_direct_ingredients(
                    recipe_item_ids,
                    recipe_quantities,
                )
                if not resolved:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                if BTItems.Crafting._compact_ingredient_stacks([ingredient.model_id for ingredient in ingredients]):
                    return BehaviorTree.NodeState.RUNNING

                ingredients, available_by_model, resolved = BTItems.Crafting._get_live_direct_ingredients(
                    recipe_item_ids,
                    recipe_quantities,
                )
                if not resolved:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                for ingredient in ingredients:
                    if (
                        available_by_model.get(ingredient.model_id, 0) < ingredient.required_quantity
                        or ingredient.available_quantity < ingredient.required_quantity
                        or ingredient.item_id == 0
                    ):
                        node.blackboard.pop(state_key, None)
                        return BehaviorTree.NodeState.FAILURE

                if cost > 0 and Inventory.GetGoldOnCharacter() < cost:
                    if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(cost, remaining_storage_gold) > 0:
                        return BehaviorTree.NodeState.RUNNING
                    node.blackboard.pop(state_key, None)
                    if allow_partial and exchanged_quantity > 0:
                        return BehaviorTree.NodeState.SUCCESS
                    return BehaviorTree.NodeState.FAILURE

                Trading.Collector.ExchangeItem(
                    output_item_id,
                    cost,
                    [ingredient.item_id for ingredient in ingredients],
                    [ingredient.required_quantity for ingredient in ingredients],
                )
                state["exchanged_quantity"] = exchanged_quantity + 1
                node.blackboard[state_key] = state
                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree(
                BehaviorTree.ActionNode(name="Collector.ExchangeItem", action_fn=_exchange, aftercast_ms=aftercast_ms)
            )

        @staticmethod
        def ExchangeItemModelID(
            output_model_id: int,
            trade_model_ids: list[int],
            quantity_list: list[int],
            cost: int = 0,
            quantity: int = 1,
            allow_partial: bool = True,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that exchanges collector items based on the specified output model, trade models, and quantities.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Exchange Collector Item By Model ID
              Purpose: Exchange collector items based on the specified output model, trade models, and quantities.
              UserDescription: Use this when you want to exchange collector items with specific models and quantities.
              Notes: Re-evaluates live inventory state on every tick and supports partial execution when enabled.
            """
            def _exchange_item(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
                k = min(len(trade_model_ids), len(quantity_list))
                if output_model_id <= 0 or k == 0 or quantity <= 0:
                    return BehaviorTree.NodeState.FAILURE

                recipe_model_ids = trade_model_ids[:k]
                recipe_quantities = quantity_list[:k]
                recipe_model_ids, recipe_quantities = BTItems.Crafting._normalize_recipe_ingredients(
                    recipe_model_ids,
                    recipe_quantities,
                )
                if any(required_quantity <= 0 for required_quantity in recipe_quantities):
                    return BehaviorTree.NodeState.FAILURE

                state_key = f"{node.id}_collector_exchange_item_model_id"
                state = cast(Optional[dict], node.blackboard.get(state_key))

                if state is None:
                    exchangeable_now = BTItems.Crafting._get_max_craftable_quantity(
                        quantity,
                        cost,
                        recipe_model_ids,
                        recipe_quantities,
                        available_gold=BTItems.Inventory._get_spendable_gold(allow_withdraw_gold, remaining_storage_gold),
                    )
                    if exchangeable_now <= 0:
                        return BehaviorTree.NodeState.FAILURE

                    if not allow_partial and exchangeable_now < quantity:
                        return BehaviorTree.NodeState.FAILURE

                    state = {
                        "target_quantity": quantity if not allow_partial else exchangeable_now,
                        "exchanged_quantity": 0,
                    }
                    node.blackboard[state_key] = state

                exchanged_quantity = int(state.get("exchanged_quantity", 0) or 0)
                target_quantity = int(state.get("target_quantity", 0) or 0)

                if exchanged_quantity >= target_quantity:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.SUCCESS

                if BTItems.Crafting._compact_ingredient_stacks(recipe_model_ids):
                    return BehaviorTree.NodeState.RUNNING

                offered_item_id = BTItems.Collector._get_output_item_id(output_model_id)
                if offered_item_id == 0:
                    node.blackboard.pop(state_key, None)
                    return BehaviorTree.NodeState.FAILURE

                ingredients, available_by_model = BTItems.Crafting._get_live_ingredients(recipe_model_ids, recipe_quantities)

                for ingredient in ingredients:
                    if (
                        available_by_model.get(ingredient.model_id, 0) < ingredient.required_quantity
                        or ingredient.available_quantity < ingredient.required_quantity
                        or ingredient.item_id == 0
                    ):
                        node.blackboard.pop(state_key, None)
                        if allow_partial and exchanged_quantity > 0:
                            return BehaviorTree.NodeState.SUCCESS
                        return BehaviorTree.NodeState.FAILURE

                if cost > 0 and Inventory.GetGoldOnCharacter() < cost:
                    if allow_withdraw_gold and BTItems.Inventory._withdraw_gold_for_amount(cost, remaining_storage_gold) > 0:
                        return BehaviorTree.NodeState.RUNNING
                    node.blackboard.pop(state_key, None)
                    if allow_partial and exchanged_quantity > 0:
                        return BehaviorTree.NodeState.SUCCESS
                    return BehaviorTree.NodeState.FAILURE

                Trading.Collector.ExchangeItem(
                    offered_item_id,
                    cost,
                    [ingredient.item_id for ingredient in ingredients],
                    [ingredient.required_quantity for ingredient in ingredients],
                )
                state["exchanged_quantity"] = exchanged_quantity + 1
                node.blackboard[state_key] = state
                return BehaviorTree.NodeState.RUNNING

            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name=f"ExchangeCollectorItem({output_model_id})",
                    action_fn=_exchange_item,
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def ExchangeItems(
            recipes: list[tuple[int, int, list[int], list[int], int]],
            allow_partial: bool = False,
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that exchanges multiple collector recipes sequentially by direct item ids.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Exchange Collector Items
              Purpose: Exchange several configured collector rewards in sequence using direct offered item ids.
              UserDescription: Use this when you want to exchange multiple different collector rewards in one BT flow.
              Notes: Runs the single direct-id exchange BT for each recipe entry in order.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Collector.ExchangeItems",
                    children=[
                        BTItems.Collector.ExchangeItem(
                            output_item_id=output_item_id,
                            cost=cost,
                            material_item_ids=material_item_ids,
                            material_quantities=material_quantities,
                            quantity=quantity,
                            allow_partial=allow_partial,
                            allow_withdraw_gold=allow_withdraw_gold,
                            remaining_storage_gold=remaining_storage_gold,
                            aftercast_ms=aftercast_ms,
                        ).root
                        for output_item_id, cost, material_item_ids, material_quantities, quantity in recipes
                    ],
                )
            )

        @staticmethod
        def ExchangeItemsModelID(
            recipes: list[tuple[int, list[int], list[int], int, int, bool]],
            allow_withdraw_gold: bool = False,
            remaining_storage_gold: int = 0,
            aftercast_ms: int = 250,
        ) -> BehaviorTree:
            """
            Build a tree that exchanges multiple collector recipes sequentially by model id.

            Meta:
              Expose: true
              Audience: intermediate
              Display: Exchange Collector Items By Model ID
              Purpose: Exchange several configured collector rewards in sequence using output and ingredient model ids.
              UserDescription: Use this when you want to exchange multiple different collector rewards by model id in one BT flow.
              Notes: Runs the single model-id exchange BT for each recipe entry in order.
            """
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Collector.ExchangeItemsByModelID",
                    children=[
                        BTItems.Collector.ExchangeItemModelID(
                            output_model_id=output_model_id,
                            trade_model_ids=trade_model_ids,
                            quantity_list=quantity_list,
                            cost=cost,
                            quantity=quantity,
                            allow_partial=allow_partial,
                            allow_withdraw_gold=allow_withdraw_gold,
                            remaining_storage_gold=remaining_storage_gold,
                            aftercast_ms=aftercast_ms,
                        ).root
                        for output_model_id, trade_model_ids, quantity_list, cost, quantity, allow_partial in recipes
                    ],
                )
            )
