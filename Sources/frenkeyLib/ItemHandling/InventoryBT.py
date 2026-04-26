from __future__ import annotations

from typing import Optional, Sequence, cast

import Py4GW

from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.enums_src.Item_enums import INVENTORY_BAGS, ItemAction
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions
from Sources.frenkeyLib.ItemHandling.BTNodes import BTNodes
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.InventoryConfig import InventoryConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import ExtractUpgradeRule, Rule
from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot
from Sources.frenkeyLib.ItemHandling.Rules.types import SalvageMode


class InventoryBT:
    NodeState = BehaviorTree.NodeState

    _ACTIVE_NODE_KEY = "inventory_bt_active_node"
    _ACTIVE_ACTION_KEY = "inventory_bt_active_action"
    _EXTRACT_WARNING_CACHE_KEY = "inventory_bt_extract_warning_cache"

    ACTION_PRIORITY: tuple[ItemAction, ...] = (
        ItemAction.Destroy,
        ItemAction.Drop,
        ItemAction.Use,
        ItemAction.Identify,
        ItemAction.Stash,
        ItemAction.Sell_To_Trader,
        ItemAction.Sell_To_Merchant,
        ItemAction.Salvage_Rare_Materials,
        ItemAction.Salvage_Common_Materials,
        ItemAction.ExtractUpgrade,
    )

    def __init__(self, config: Optional[InventoryConfig] = None):
        self.config = config or InventoryConfig()
        self.tree = self.Build(self.config)

    def tick(self) -> BehaviorTree.NodeState:
        return self.tree.tick()

    def reset(self) -> None:
        self.tree.reset()
        self.tree.blackboard.pop(self._ACTIVE_NODE_KEY, None)
        self.tree.blackboard.pop(self._ACTIVE_ACTION_KEY, None)
        self.tree.blackboard.pop(self._EXTRACT_WARNING_CACHE_KEY, None)

    @classmethod
    def Build(cls, config: Optional[InventoryConfig] = None) -> BehaviorTree:
        inventory_config = config or InventoryConfig()
        return BehaviorTree(cls._build_root_node(inventory_config))

    @classmethod
    def _build_root_node(cls, config: InventoryConfig) -> BehaviorTree.Node:
        def _tick(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
            active_node = cast(BehaviorTree.Node | None, node.blackboard.get(cls._ACTIVE_NODE_KEY))
            if active_node is not None:
                active_node.blackboard = node.blackboard
                active_state = active_node.tick()

                if active_state == BehaviorTree.NodeState.RUNNING:
                    return BehaviorTree.NodeState.RUNNING

                node.blackboard.pop(cls._ACTIVE_NODE_KEY, None)
                node.blackboard.pop(cls._ACTIVE_ACTION_KEY, None)

                if active_state == BehaviorTree.NodeState.FAILURE:
                    return BehaviorTree.NodeState.FAILURE

            action_batches = cls._collect_action_batches(config, node.blackboard)
            if not action_batches:
                return BehaviorTree.NodeState.SUCCESS

            for action in cls.ACTION_PRIORITY:
                item_ids = action_batches.get(action, [])
                if not item_ids:
                    continue

                action_node = cls._build_action_node(config, action, item_ids, node.blackboard)
                if action_node is None:
                    continue

                Py4GW.Console.Log(
                    "InventoryBT",
                    f"Dispatching {action.name} for {len(item_ids)} item(s).",
                    Py4GW.Console.MessageType.Info,
                )

                node.blackboard[cls._ACTIVE_NODE_KEY] = action_node
                node.blackboard[cls._ACTIVE_ACTION_KEY] = action.name
                action_node.blackboard = node.blackboard
                return action_node.tick()

            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree.ActionNode(name="InventoryBT.ProcessInventory", action_fn=_tick)

    @classmethod
    def _collect_action_batches(cls, config: InventoryConfig, blackboard: Optional[dict] = None) -> dict[ItemAction, list[int]]:
        action_batches: dict[ItemAction, list[int]] = {}

        for item_id in cls._get_inventory_item_ids():
            action = cls._get_action_for_item(config, item_id)
            if action in (None, ItemAction.NONE, ItemAction.Hold):
                continue

            if action == ItemAction.ExtractUpgrade:
                if cls._get_single_extractable_match(config, item_id, blackboard) is None:
                    continue

            action_batches.setdefault(action, []).append(item_id)

        return action_batches

    @staticmethod
    def _get_inventory_item_ids() -> list[int]:
        snapshot = ItemSnapshot.get_bags_snapshot(INVENTORY_BAGS)
        item_ids: list[int] = []

        for bag_items in snapshot.values():
            for item in bag_items.values():
                if item is None or not item.is_valid or not item.is_inventory_item:
                    continue

                item_ids.append(item.id)

        return item_ids

    @classmethod
    def _get_action_for_item(cls, config: InventoryConfig, item_id: int) -> Optional[ItemAction]:
        rule = cls._get_first_matching_rule(config, item_id)
        if rule is None:
            return None

        return rule.action

    @staticmethod
    def _get_first_matching_rule(config: InventoryConfig, item_id: int) -> Optional[Rule]:
        if item_id in config.blacklisted_items:
            return None

        for rule in config:
            if rule.applies(item_id):
                return rule

        return None

    @classmethod
    def _build_action_node(
        cls,
        config: InventoryConfig,
        action: ItemAction,
        item_ids: list[int],
        blackboard: Optional[dict] = None,
    ) -> Optional[BehaviorTree.Node]:
        match action:
            case ItemAction.Identify:
                return BTNodes.Items.IdentifyItems(item_ids)
            
            case ItemAction.Use:
                return BTNodes.Items.UseItems(item_ids)
            
            case ItemAction.Drop:
                if Map.IsExplorable():
                    return BTNodes.Items.DropItems(item_ids)
            
            case ItemAction.Destroy:
                return BTNodes.Items.DestroyItems(item_ids)
            
            case ItemAction.Stash:
                return BTNodes.Items.DepositItems(item_ids)
            
            case ItemAction.Sell_To_Merchant:
                if UIManagerExtensions.IsMerchantWindowOpen():
                    return BTNodes.Merchant.SellItems(item_ids) 
                
            case ItemAction.Sell_To_Trader:
                if UIManagerExtensions.IsMerchantWindowOpen():
                    item_id = cls._get_first_valid_item_id(item_ids)
                    if item_id is not None:
                        return BTNodes.Trader.SellItem(item_id)
            
            case ItemAction.Salvage_Common_Materials:
                item_id = cls._get_first_salvageable_item_id(item_ids)
                if item_id is not None:
                    return BTNodes.Items.SalvageItem(
                        item_id,
                        salvage_mode=SalvageMode.LesserCraftingMaterials,
                        allow_expert_for_common_materials=True,
                    )   
                    
            case ItemAction.Salvage_Rare_Materials: 
                item_id = cls._get_first_salvageable_item_id(item_ids)
                if item_id is not None:
                    return BTNodes.Items.SalvageItem(item_id, salvage_mode=SalvageMode.RareCraftingMaterials)
                
            case ItemAction.ExtractUpgrade:
                item_id, salvage_mode = cls._get_first_extractable_item(config, item_ids, blackboard)
                if item_id is not None and salvage_mode is not None:
                    return BTNodes.Items.SalvageItem(item_id, salvage_mode=salvage_mode)
            
            case _:
                return None

        return None

    @staticmethod
    def _get_first_valid_item_id(item_ids: list[int]) -> Optional[int]:
        for item_id in item_ids:
            item = ItemSnapshot.from_item_id(item_id)
            if item is not None and item.is_valid and item.is_inventory_item:
                return item_id

        return None

    @staticmethod
    def _get_first_salvageable_item_id(item_ids: list[int]) -> Optional[int]:
        for item_id in item_ids:
            item = ItemSnapshot.from_item_id(item_id)
            if item is not None and item.is_valid and item.is_inventory_item and item.is_salvageable:
                return item_id

        return None

    @classmethod
    def _get_first_extractable_item(
        cls,
        config: InventoryConfig,
        item_ids: list[int],
        blackboard: Optional[dict] = None,
    ) -> tuple[Optional[int], Optional[SalvageMode]]:
        for item_id in item_ids:
            item = ItemSnapshot.from_item_id(item_id)
            if item is None or not item.is_valid or not item.is_inventory_item or not item.is_salvageable:
                continue

            match = cls._get_single_extractable_match(config, item_id, blackboard)
            if match is not None:
                _, salvage_mode = match
                return item_id, salvage_mode

        return None, None

    @staticmethod
    def _format_upgrade_match_name(salvage_mode: SalvageMode, item_id: int) -> str:
        item = ItemSnapshot.from_item_id(item_id)
        if item is None:
            return salvage_mode.name

        if salvage_mode == SalvageMode.Prefix and item.prefix is not None:
            return f"{salvage_mode.name}: {type(item.prefix).__name__}"

        if salvage_mode == SalvageMode.Suffix and item.suffix is not None:
            return f"{salvage_mode.name}: {type(item.suffix).__name__}"

        if salvage_mode == SalvageMode.Inscription and item.inscription is not None:
            return f"{salvage_mode.name}: {type(item.inscription).__name__}"

        return salvage_mode.name

    @classmethod
    def _get_single_extractable_match(
        cls,
        config: InventoryConfig,
        item_id: int,
        blackboard: Optional[dict] = None,
    ) -> Optional[tuple[object, SalvageMode]]:
        rule = cls._get_first_matching_rule(config, item_id)
        if not isinstance(rule, ExtractUpgradeRule):
            return None

        matches = rule.get_matching_upgrades(item_id)
        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            cls._log_ambiguous_extract_upgrade(item_id, rule, matches, blackboard)

        return None

    @classmethod
    def _log_ambiguous_extract_upgrade(
        cls,
        item_id: int,
        rule: ExtractUpgradeRule,
        matches: Sequence[tuple[object, SalvageMode]],
        blackboard: Optional[dict],
    ) -> None:
        if blackboard is not None:
            warning_cache = cast(set[int], blackboard.setdefault(cls._EXTRACT_WARNING_CACHE_KEY, set()))
            if item_id in warning_cache:
                return
            warning_cache.add(item_id)

        item = ItemSnapshot.from_item_id(item_id)
        item_name = item.names.plain if item is not None and item.names.plain else f"Item {item_id}"
        match_names = ", ".join(cls._format_upgrade_match_name(salvage_mode, item_id) for _, salvage_mode in matches)

        Py4GW.Console.Log(
            "InventoryBT",
            f"Skipping upgrade extraction for '{item_name}' (ID: {item_id}) because rule '{rule.name or type(rule).__name__}' matched multiple upgrades: {match_names}.",
            Py4GW.Console.MessageType.Warning,
        )


__all__ = ["InventoryBT"]
