from __future__ import annotations

import json
import os
import time
from collections.abc import Generator
from typing import Any, Callable

import Py4GW
import PyImGui
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.BottingTree import BottingTree
from Py4GWCoreLib.Builds.Assassin.A_Me.SF_Ass_vaettir import SF_Ass_vaettir
from Py4GWCoreLib.Builds.Mesmer.Me_A.SF_Mes_vaettir import SF_Mes_vaettir
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.enums_src.Item_enums import ItemAction, ItemType
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.enums_src.Title_enums import TitleID
from Py4GWCoreLib.native_src.internals.types import Vec2f
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Py4GWCoreLib.py4gwcorelib_src.Color import Color, ColorPalette
from Py4GWCoreLib.routines_src.BehaviourTrees import BT as RoutinesBT
from Sources.ApoSource.ApoBottingLib import wrappers as BT
from Sources.frenkeyLib.ItemHandling.BTNodes import BTNodes
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.BuyConfig import BuyConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.InventoryConfig import InventoryConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig
from Sources.frenkeyLib.ItemHandling.InventoryBT import InventoryBT
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions


MODULE_NAME = "YAVB 3.0"
MODULE_ICON = "Textures\\Module_Icons\\YAVB 2.0 mascot.png"
LONGEYES_LEDGE = 650
BJORA_MARCHES = 482
JAGA_MORAINE = 546
MERCHANT_XY = Vec2f(-23110.0, 14942.0)

SETTINGS_DIR = os.path.join(
    Py4GW.Console.get_projects_path(),
    "Settings",
    "Global",
    "Item & Inventory",
    "Configs",
)
INVENTORY_CONFIG_PATH = os.path.join(SETTINGS_DIR, "inventoryconfig.json")
LOOT_CONFIG_PATH = os.path.join(SETTINGS_DIR, "lootconfig.json")
BUY_CONFIG_PATH = os.path.join(SETTINGS_DIR, "buyconfig.json")

initialized = False
botting_tree: BottingTree | None = None


def _log(message: str, message_type=Py4GW.Console.MessageType.Info) -> None:
    Py4GW.Console.Log(MODULE_NAME, message, message_type)


def _action_tree(
    name: str,
    action_fn: Callable[[BehaviorTree.Node], BehaviorTree.NodeState],
    aftercast_ms: int = 0,
) -> BehaviorTree:
    return BehaviorTree(
        BehaviorTree.ActionNode(
            name=name,
            action_fn=action_fn,
            aftercast_ms=aftercast_ms,
        )
    )


def _load_shared_configs() -> None:
    InventoryConfig.Load(INVENTORY_CONFIG_PATH)
    LootConfig.Load(LOOT_CONFIG_PATH)

    buy_config = BuyConfig()
    if os.path.isfile(BUY_CONFIG_PATH):
        with open(BUY_CONFIG_PATH, "r", encoding="utf-8") as file:
            payload = json.load(file)
        if isinstance(payload, dict):
            buy_config.load_dict(payload)


def _reset_runtime_item_state() -> None:
    InventoryConfig().reset()
    LootConfig().reset()


def _get_runtime_build(blackboard: dict) -> SF_Ass_vaettir | SF_Mes_vaettir | None:
    build = blackboard.get("yavb_build")
    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
        return build
    return None


def _set_build_runtime_flags(
    blackboard: dict,
    *,
    in_killing: bool | None = None,
    finished: bool | None = None,
    stuck_counter: int | None = None,
) -> None:
    build = _get_runtime_build(blackboard)
    if build is None:
        return

    if in_killing is not None:
        build.SetKillingRoutine(in_killing)
    if finished is not None:
        build.SetRoutineFinished(finished)
    if stuck_counter is not None:
        build.SetStuckSignal(stuck_counter)


def _count_inventory_item_type(item_type: ItemType) -> int:
    quantity = 0
    for item_id in GLOBAL_CACHE.Inventory.GetAllInventoryItemIds():
        if item_id == 0:
            continue

        item_type_value, _ = GLOBAL_CACHE.Item.GetItemType(item_id)
        try:
            current_type = ItemType(item_type_value)
        except ValueError:
            continue

        if current_type.matches(item_type):
            quantity += max(1, int(GLOBAL_CACHE.Item.Properties.GetQuantity(item_id) or 1))

    return quantity


def _current_buy_entry_quantity(entry) -> int:
    if entry.model_id is not None:
        return GLOBAL_CACHE.Inventory.GetModelCount(int(entry.model_id))

    if entry.item_type is not None:
        return _count_inventory_item_type(entry.item_type)

    return 0


def _needs_buy_restock() -> bool:
    return any(
        entry.quantity > 0 and _current_buy_entry_quantity(entry) < entry.quantity
        for entry in BuyConfig().get_entries()
    )


def _has_pending_merchant_sales() -> bool:
    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        entry.action == ItemAction.Sell_To_Merchant and entry.executable
        for entry in preview_entries
    )


def _needs_merchant_visit() -> bool:
    return _has_pending_merchant_sales() or _needs_buy_restock()


def _needs_town_after_run() -> bool:
    if GLOBAL_CACHE.Inventory.GetFreeSlotCount() <= 0:
        return True
    return _needs_buy_restock()


def _restock_buy_entry(entry) -> BehaviorTree.Node:
    def _restock(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        if entry.quantity <= 0:
            return BehaviorTree.NodeState.SUCCESS

        if not UIManagerExtensions.MerchantWindow.IsOpen():
            return BehaviorTree.NodeState.FAILURE

        current_quantity = _current_buy_entry_quantity(entry)
        if current_quantity >= entry.quantity:
            return BehaviorTree.NodeState.SUCCESS

        if entry.model_id is not None and entry.item_type is not None:
            return BTNodes.Merchant.Restock(
                model_id=int(entry.model_id),
                item_type=entry.item_type,
                quantity=entry.quantity,
            ).tick()

        if entry.item_type is None:
            return BehaviorTree.NodeState.FAILURE

        offered_items = list(GLOBAL_CACHE.Trading.Merchant.GetOfferedItems() or [])
        for offered_item_id in offered_items:
            offered_type_value, _ = GLOBAL_CACHE.Item.GetItemType(offered_item_id)
            try:
                offered_type = ItemType(offered_type_value)
            except ValueError:
                continue

            if not offered_type.matches(entry.item_type):
                continue

            price = max(0, int(GLOBAL_CACHE.Item.Properties.GetValue(offered_item_id) or 0) * 2)
            if price <= 0:
                return BehaviorTree.NodeState.FAILURE

            needed = max(0, int(entry.quantity) - current_quantity)
            affordable = int(GLOBAL_CACHE.Inventory.GetGoldOnCharacter() or 0) // price
            count = min(needed, affordable)
            if count <= 0:
                return BehaviorTree.NodeState.FAILURE

            for _ in range(count):
                GLOBAL_CACHE.Trading.Merchant.BuyItem(offered_item_id, price)

            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree.NodeState.FAILURE

    return BehaviorTree.ActionNode(
        name=f"RestockBuyEntry({entry.key})",
        action_fn=_restock,
        aftercast_ms=200,
    )


def LoadSharedConfigs() -> BehaviorTree:
    def _load(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        _load_shared_configs()
        _reset_runtime_item_state()
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("LoadSharedConfigs", _load)


def ResetRunFlags() -> BehaviorTree:
    def _reset(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        now_ms = time.monotonic() * 1000.0
        node.blackboard["yavb_waiting_for_ball"] = False
        node.blackboard["yavb_finished_routine"] = False
        node.blackboard["yavb_in_killing_routine"] = False
        node.blackboard["yavb_stuck_counter"] = 0
        node.blackboard["yavb_old_player_position"] = Player.GetXY()
        node.blackboard["yavb_last_stuck_ms"] = now_ms
        node.blackboard["yavb_last_move_check_ms"] = now_ms
        _set_build_runtime_flags(node.blackboard, in_killing=False, finished=False, stuck_counter=0)
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("ResetRunFlags", _reset)


def AssignBuild() -> BehaviorTree:
    def _assign(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        profession, _ = Agent.GetProfessionNames(Player.GetAgentID())
        if profession == "Assassin":
            build = SF_Ass_vaettir()
        elif profession == "Mesmer":
            build = SF_Mes_vaettir()
        else:
            _log(f"Unsupported profession '{profession}'.", Py4GW.Console.MessageType.Error)
            return BehaviorTree.NodeState.FAILURE

        node.blackboard["yavb_build"] = build
        _set_build_runtime_flags(node.blackboard, in_killing=False, finished=False, stuck_counter=0)
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("AssignBuild", _assign)


def EquipSkillBar() -> BehaviorTree:
    state: dict[str, Generator[Any, Any, None] | None] = {"generator": None}

    def _equip(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        build = _get_runtime_build(node.blackboard)
        if build is None:
            return BehaviorTree.NodeState.FAILURE

        if state["generator"] is None:
            state["generator"] = build.LoadSkillBar()

        try:
            next(state["generator"])
            return BehaviorTree.NodeState.RUNNING
        except StopIteration:
            state["generator"] = None
            return BehaviorTree.NodeState.SUCCESS

    return _action_tree("EquipSkillBar", _equip)


def SetNornTitle() -> BehaviorTree:
    def _set_title(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        Player.SetActiveTitle(TitleID.Norn.value)
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("SetNornTitle", _set_title, aftercast_ms=100)


def SetHardMode() -> BehaviorTree:
    def _set_hard_mode(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        GLOBAL_CACHE.Party.SetHardMode()
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("SetHardMode", _set_hard_mode, aftercast_ms=250)


def MoveTo(
    pos: Vec2f,
    *,
    tolerance: float = 150.0,
    timeout_ms: int = 30000,
    pause_on_combat: bool = False,
) -> BehaviorTree:
    return RoutinesBT.Player.Move(
        x=pos.x,
        y=pos.y,
        tolerance=tolerance,
        timeout_ms=timeout_ms,
        pause_on_combat=pause_on_combat,
        log=False,
    )


def MovePath(
    path_points: list[Vec2f],
    *,
    tolerance: float = 150.0,
    timeout_ms: int = 30000,
    pause_on_combat: bool = False,
) -> BehaviorTree:
    return RoutinesBT.Player.MoveDirect(
        path_points=path_points,
        tolerance=tolerance,
        timeout_ms=timeout_ms,
        pause_on_combat=pause_on_combat,
        log=False,
    )


def OpenXunlai() -> BehaviorTree:
    def _open(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        if Inventory.IsStorageOpen():
            return BehaviorTree.NodeState.SUCCESS
        Inventory.OpenXunlaiWindow()
        return BehaviorTree.NodeState.RUNNING

    return BehaviorTree(
        BehaviorTree.WaitUntilNode(
            name="OpenXunlai",
            condition_fn=_open,
            throttle_interval_ms=250,
            timeout_ms=5000,
        )
    )


def RunInventoryPass(name: str, tolerate_failure: bool = True) -> BehaviorTree:
    state = {"runner": None, "ticks": 0, "success_streak": 0}

    def _run(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        if state["runner"] is None:
            state["runner"] = InventoryBT(InventoryConfig())
            state["ticks"] = 0
            state["success_streak"] = 0

        result = state["runner"].tick()
        state["ticks"] += 1

        if result == BehaviorTree.NodeState.RUNNING:
            state["success_streak"] = 0
            return BehaviorTree.NodeState.RUNNING

        if result == BehaviorTree.NodeState.FAILURE:
            state["runner"] = None
            state["ticks"] = 0
            state["success_streak"] = 0
            return BehaviorTree.NodeState.SUCCESS if tolerate_failure else BehaviorTree.NodeState.FAILURE

        state["success_streak"] += 1
        if state["success_streak"] < 3 and state["ticks"] < 50:
            return BehaviorTree.NodeState.RUNNING

        state["runner"] = None
        state["ticks"] = 0
        state["success_streak"] = 0
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree(name, _run)


def RestockBuyConfig() -> BehaviorTree:
    entries = [
        _restock_buy_entry(entry)
        for entry in BuyConfig().get_entries()
        if entry.quantity > 0
    ]

    if not entries:
        return BehaviorTree(BehaviorTree.SucceederNode(name="RestockBuyConfigEmpty"))

    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="RestockBuyConfig",
            children=entries,
        )
    )


def OptionalMerchantRoutine() -> BehaviorTree:
    def _needs_merchant(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        return BehaviorTree.NodeState.SUCCESS if _needs_merchant_visit() else BehaviorTree.NodeState.FAILURE

    return BehaviorTree(
        BehaviorTree.SelectorNode(
            name="OptionalMerchantRoutine",
            children=[
                BehaviorTree.SequenceNode(
                    name="MerchantRoutine",
                    children=[
                        BehaviorTree.ActionNode(
                            name="NeedsMerchantVisit",
                            action_fn=_needs_merchant,
                            aftercast_ms=0,
                        ),
                        BT.MoveAndInteract(MERCHANT_XY).root,
                        BT.Wait(500).root,
                        RunInventoryPass("RunMerchantInventoryPass").root,
                        RestockBuyConfig().root,
                    ],
                ),
                BehaviorTree.SucceederNode(name="SkipMerchantRoutine"),
            ],
        )
    )


def TownRoutines() -> BehaviorTree:
    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="Town Routines",
            children=[
                BT.TravelToOutpost(LONGEYES_LEDGE).root,
                LoadSharedConfigs().root,
                ResetRunFlags().root,
                AssignBuild().root,
                EquipSkillBar().root,
                OpenXunlai().root,
                RunInventoryPass("RunStorageInventoryPass").root,
                OptionalMerchantRoutine().root,
                SetHardMode().root,
                MoveTo(Vec2f(-26375.0, 16180.0), tolerance=175.0, timeout_ms=30000).root,
                BT.WaitForMapLoad(BJORA_MARCHES).root,
            ],
        )
    )


def TraverseBjoraMarches() -> BehaviorTree:
    path = [
        Vec2f(17810, -17649), Vec2f(17516, -17270), Vec2f(17166, -16813), Vec2f(16862, -16324),
        Vec2f(16472, -15934), Vec2f(15929, -15731), Vec2f(15387, -15521), Vec2f(14849, -15312),
        Vec2f(14311, -15101), Vec2f(13776, -14882), Vec2f(13249, -14642), Vec2f(12729, -14386),
        Vec2f(12235, -14086), Vec2f(11748, -13776), Vec2f(11274, -13450), Vec2f(10839, -13065),
        Vec2f(10572, -12590), Vec2f(10412, -12036), Vec2f(10238, -11485), Vec2f(10125, -10918),
        Vec2f(10029, -10348), Vec2f(9909, -9778), Vec2f(9599, -9327), Vec2f(9121, -9009),
        Vec2f(8674, -8645), Vec2f(8215, -8289), Vec2f(7755, -7945), Vec2f(7339, -7542),
        Vec2f(6962, -7103), Vec2f(6587, -6666), Vec2f(6210, -6226), Vec2f(5834, -5788),
        Vec2f(5457, -5349), Vec2f(5081, -4911), Vec2f(4703, -4470), Vec2f(4379, -3990),
        Vec2f(4063, -3507), Vec2f(3773, -3031), Vec2f(3452, -2540), Vec2f(3117, -2070),
        Vec2f(2678, -1703), Vec2f(2115, -1593), Vec2f(1541, -1614), Vec2f(960, -1563),
        Vec2f(388, -1491), Vec2f(-187, -1419), Vec2f(-770, -1426), Vec2f(-1343, -1440),
        Vec2f(-1922, -1455), Vec2f(-2496, -1472), Vec2f(-3073, -1535), Vec2f(-3650, -1607),
        Vec2f(-4214, -1712), Vec2f(-4784, -1759), Vec2f(-5278, -1492), Vec2f(-5754, -1164),
        Vec2f(-6200, -796), Vec2f(-6632, -419), Vec2f(-7192, -300), Vec2f(-7770, -306),
        Vec2f(-8352, -286), Vec2f(-8932, -258), Vec2f(-9504, -226), Vec2f(-10086, -201),
        Vec2f(-10665, -215), Vec2f(-11247, -242), Vec2f(-11826, -262), Vec2f(-12400, -247),
        Vec2f(-12979, -216), Vec2f(-13529, -53), Vec2f(-13944, 341), Vec2f(-14358, 743),
        Vec2f(-14727, 1181), Vec2f(-15109, 1620), Vec2f(-15539, 2010), Vec2f(-15963, 2380),
        Vec2f(-18048, 4223), Vec2f(-19196, 4986), Vec2f(-20000, 5595), Vec2f(-20300, 5600),
    ]

    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="Traverse Bjora Marches",
            children=[
                SetNornTitle().root,
                MovePath(path, tolerance=175.0, timeout_ms=30000).root,
                BT.WaitForMapLoad(JAGA_MORAINE).root,
            ],
        )
    )


def WaitForBall(side_label: str, cycle_timeout: int = 150) -> BehaviorTree:
    started = False
    elapsed = 0
    cleanup_generator: Generator[Any, Any, None] | None = None

    def _wait(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        nonlocal started, elapsed, cleanup_generator
        build = _get_runtime_build(node.blackboard)

        if not started:
            started = True
            elapsed = 0
            cleanup_generator = None
            node.blackboard["yavb_waiting_for_ball"] = True

        if cleanup_generator is not None:
            try:
                next(cleanup_generator)
                return BehaviorTree.NodeState.RUNNING
            except StopIteration:
                cleanup_generator = None
                started = False
                return BehaviorTree.NodeState.SUCCESS

        if Agent.IsDead(Player.GetAgentID()):
            node.blackboard["yavb_waiting_for_ball"] = False
            started = False
            cleanup_generator = None
            return BehaviorTree.NodeState.FAILURE

        px, py = Player.GetXY()
        enemies = Routines.Agents.GetFilteredEnemyArray(px, py, Range.Earshot.value)
        all_in_adjacent = True
        for enemy_id in enemies:
            enemy = Agent.GetAgentByID(enemy_id)
            if enemy is None:
                continue
            dx = enemy.pos.x - px
            dy = enemy.pos.y - py
            if dx * dx + dy * dy > Range.Adjacent.value ** 2:
                all_in_adjacent = False
                break

        elapsed += 1
        if all_in_adjacent or elapsed >= cycle_timeout:
            node.blackboard["yavb_waiting_for_ball"] = False
            if build is not None:
                cleanup_generator = build.CastHeartOfShadow()
                return BehaviorTree.NodeState.RUNNING
            started = False
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree.NodeState.RUNNING

    return _action_tree(f"WaitForBall({side_label})", _wait, aftercast_ms=100)


def PrepareForKillRoutine() -> BehaviorTree:
    def _prepare(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        node.blackboard["yavb_waiting_for_ball"] = False
        node.blackboard["yavb_in_killing_routine"] = True
        node.blackboard["yavb_finished_routine"] = False
        _set_build_runtime_flags(node.blackboard, in_killing=True, finished=False)
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("PrepareForKillRoutine", _prepare)


def KillEnemies() -> BehaviorTree:
    state = {"started_at_ms": 0.0}

    def _kill(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        build = _get_runtime_build(node.blackboard)
        if build is None:
            return BehaviorTree.NodeState.FAILURE

        if state["started_at_ms"] == 0.0:
            state["started_at_ms"] = time.monotonic() * 1000.0
            node.blackboard["yavb_in_killing_routine"] = True
            node.blackboard["yavb_finished_routine"] = False
            _set_build_runtime_flags(node.blackboard, in_killing=True, finished=False)

        if Agent.IsDead(Player.GetAgentID()):
            state["started_at_ms"] = 0.0
            node.blackboard["yavb_in_killing_routine"] = False
            _set_build_runtime_flags(node.blackboard, in_killing=False)
            return BehaviorTree.NodeState.FAILURE

        if (time.monotonic() * 1000.0) - state["started_at_ms"] > 120000.0:
            _log("Kill routine timed out, resigning.", Py4GW.Console.MessageType.Warning)
            Player.SendChatCommand("resign")
            state["started_at_ms"] = 0.0
            node.blackboard["yavb_in_killing_routine"] = False
            _set_build_runtime_flags(node.blackboard, in_killing=False)
            return BehaviorTree.NodeState.FAILURE

        px, py = Player.GetXY()
        enemies = Routines.Agents.GetFilteredEnemyArray(px, py, Range.Spellcast.value)
        if enemies:
            return BehaviorTree.NodeState.RUNNING

        state["started_at_ms"] = 0.0
        node.blackboard["yavb_in_killing_routine"] = False
        node.blackboard["yavb_finished_routine"] = True
        _set_build_runtime_flags(node.blackboard, in_killing=False, finished=True)
        return BehaviorTree.NodeState.SUCCESS

    return _action_tree("KillEnemies", _kill, aftercast_ms=250)


def LootItemsWithConfig(distance: float = Range.Earshot.value, timeout_ms: int = 10000) -> BehaviorTree:
    state = {"started_at_ms": 0.0}

    def _loot(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        if state["started_at_ms"] == 0.0:
            state["started_at_ms"] = time.monotonic() * 1000.0

        if GLOBAL_CACHE.Inventory.GetFreeSlotCount() <= 0:
            state["started_at_ms"] = 0.0
            return BehaviorTree.NodeState.SUCCESS

        loot_array = LootConfig().GetfilteredLootArray(
            distance=distance,
            multibox_loot=True,
            allow_unasigned_loot=False,
        )
        if not loot_array:
            state["started_at_ms"] = 0.0
            return BehaviorTree.NodeState.SUCCESS

        if (time.monotonic() * 1000.0) - state["started_at_ms"] >= timeout_ms:
            state["started_at_ms"] = 0.0
            return BehaviorTree.NodeState.SUCCESS

        item_agent_id = loot_array[0]
        Player.ChangeTarget(item_agent_id)
        Player.Interact(item_agent_id, False)
        return BehaviorTree.NodeState.RUNNING

    return _action_tree("LootItemsWithConfig", _loot, aftercast_ms=500)


def HandlePostRunTransition() -> BehaviorTree:
    state = {"started": False, "branch_tree": None}

    def _handle(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        if not state["started"]:
            state["started"] = True
            if _needs_town_after_run():
                state["branch_tree"] = BehaviorTree(
                    BehaviorTree.SequenceNode(
                        name="ReturnToTown",
                        children=[
                            BehaviorTree.ActionNode(
                                name="SendResign",
                                action_fn=lambda _: (Player.SendChatCommand("resign") or BehaviorTree.NodeState.SUCCESS),
                                aftercast_ms=250,
                            ),
                            BT.WaitForMapLoad(LONGEYES_LEDGE).root,
                            BehaviorTree.FailerNode(name="StopFarmLoop"),
                        ],
                    )
                )
            else:
                state["branch_tree"] = BehaviorTree(
                    BehaviorTree.SequenceNode(
                        name="RepeatFarmCycle",
                        children=[
                            MoveTo(Vec2f(15850.0, -20550.0), tolerance=175.0, timeout_ms=30000).root,
                            BT.WaitForMapLoad(BJORA_MARCHES).root,
                            MoveTo(Vec2f(-20300.0, 5600.0), tolerance=175.0, timeout_ms=30000).root,
                            BT.WaitForMapLoad(JAGA_MORAINE).root,
                        ],
                    )
                )

        branch_tree = state["branch_tree"]
        if branch_tree is None:
            return BehaviorTree.NodeState.FAILURE

        branch_tree.blackboard = node.blackboard
        result = branch_tree.tick()
        if result == BehaviorTree.NodeState.RUNNING:
            return BehaviorTree.NodeState.RUNNING

        state["started"] = False
        state["branch_tree"] = None
        node.blackboard["yavb_finished_routine"] = False
        _set_build_runtime_flags(node.blackboard, finished=False)
        return result

    return _action_tree("HandlePostRunTransition", _handle, aftercast_ms=250)


def SingleFarmCycle() -> BehaviorTree:
    first_pull = [
        Vec2f(13367.0, -20771.0),
        Vec2f(11375.0, -22761.0),
        Vec2f(10925.0, -23466.0),
        Vec2f(10917.0, -24311.0),
        Vec2f(10280.0, -24620.0),
        Vec2f(10280.0, -24620.0),
        Vec2f(9640.0, -23175.0),
        Vec2f(7815.0, -23200.0),
        Vec2f(6626.51, -23167.24),
    ]
    left_ball = [
        Vec2f(7765.0, -22940.0),
        Vec2f(8213.0, -22829.0),
        Vec2f(8740.0, -22475.0),
        Vec2f(8880.0, -21384.0),
        Vec2f(8684.0, -20833.0),
        Vec2f(8982.0, -20576.0),
    ]
    log_side = [
        Vec2f(10196.0, -20124.0),
        Vec2f(10123.0, -19529.0),
        Vec2f(10049.0, -18933.0),
    ]
    big_pack = [
        Vec2f(9976.0, -18338.0),
        Vec2f(11316.0, -18056.0),
        Vec2f(10392.0, -17512.0),
        Vec2f(10114.0, -16948.0),
    ]
    right_ball = [
        Vec2f(10729.0, -16273.0),
        Vec2f(10505.0, -14750.0),
        Vec2f(10815.0, -14790.0),
        Vec2f(11090.0, -15345.0),
        Vec2f(11670.0, -15457.0),
        Vec2f(12604.0, -15320.0),
        Vec2f(12450.0, -14800.0),
        Vec2f(12725.0, -14850.0),
        Vec2f(12476.0, -16157.0),
    ]
    kill_spot = [
        Vec2f(13070.0, -16911.0),
        Vec2f(12938.0, -17081.0),
        Vec2f(12790.0, -17201.0),
        Vec2f(12747.0, -17220.0),
        Vec2f(12703.0, -17239.0),
        Vec2f(12684.0, -17184.0),
        Vec2f(12485.18, -17260.41),
    ]

    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="SingleFarmCycle",
            children=[
                ResetRunFlags().root,
                MoveTo(Vec2f(13372.44, -20758.50), tolerance=175.0, timeout_ms=30000).root,
                BT.DialogAtXY(Vec2f(13367.0, -20771.0), dialog_id=0x84).root,
                MovePath(first_pull, tolerance=175.0, timeout_ms=30000).root,
                WaitForBall("Inner Packs", cycle_timeout=75).root,
                MovePath(left_ball, tolerance=175.0, timeout_ms=30000).root,
                WaitForBall("Left Aggro Ball").root,
                MovePath(log_side, tolerance=175.0, timeout_ms=30000).root,
                WaitForBall("Log Side Packs", cycle_timeout=75).root,
                MovePath(big_pack, tolerance=175.0, timeout_ms=30000).root,
                WaitForBall("Big Pack").root,
                MovePath(right_ball, tolerance=175.0, timeout_ms=30000).root,
                WaitForBall("Right Aggro Ball").root,
                PrepareForKillRoutine().root,
                MovePath(kill_spot, tolerance=80.0, timeout_ms=30000).root,
                KillEnemies().root,
                LootItemsWithConfig(distance=Range.Earshot.value, timeout_ms=10000).root,
                RunInventoryPass("RunExplorableInventoryPass").root,
                HandlePostRunTransition().root,
            ],
        )
    )


def FarmLoop() -> BehaviorTree:
    return BehaviorTree(
        BehaviorTree.RepeaterUntilFailureNode(
            child=SingleFarmCycle().root,
            timeout_ms=0,
            name="FarmLoop",
        )
    )


def BuildService() -> BehaviorTree:
    state = {"last_tick_ms": 0.0}

    def _tick(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        build = _get_runtime_build(node.blackboard)
        if build is None:
            return BehaviorTree.NodeState.RUNNING

        if not Routines.Checks.Map.MapValid() or not Map.IsExplorable() or Map.IsMapLoading():
            return BehaviorTree.NodeState.RUNNING

        now_ms = time.monotonic() * 1000.0
        if now_ms - state["last_tick_ms"] < 125.0:
            return BehaviorTree.NodeState.RUNNING

        state["last_tick_ms"] = now_ms
        try:
            if Routines.Checks.Agents.InDanger(Range.Earshot):
                next(build.ProcessCombat(), None)
            else:
                next(build.ProcessOOC(), None)
        except Exception as exc:
            _log(f"BuildService error: {exc}", Py4GW.Console.MessageType.Error)

        return BehaviorTree.NodeState.RUNNING

    return _action_tree("BuildService", _tick)


def RuntimeResetService() -> BehaviorTree:
    state = {"last_map_id": 0}

    def _tick(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        current_map_id = Map.GetMapID() if Routines.Checks.Map.MapValid() else 0
        if current_map_id != state["last_map_id"]:
            _reset_runtime_item_state()
            state["last_map_id"] = current_map_id
        return BehaviorTree.NodeState.RUNNING

    return _action_tree("RuntimeResetService", _tick)


def StuckDetectionService() -> BehaviorTree:
    def _tick(node: BehaviorTree.Node) -> BehaviorTree.NodeState:
        if not Routines.Checks.Map.MapValid() or Agent.IsDead(Player.GetAgentID()):
            return BehaviorTree.NodeState.RUNNING

        if Map.GetMapID() != JAGA_MORAINE:
            return BehaviorTree.NodeState.RUNNING

        if bool(node.blackboard.get("yavb_waiting_for_ball")) or bool(node.blackboard.get("yavb_finished_routine")) or bool(node.blackboard.get("yavb_in_killing_routine")):
            now_ms = time.monotonic() * 1000.0
            node.blackboard["yavb_stuck_counter"] = 0
            node.blackboard["yavb_old_player_position"] = Player.GetXY()
            node.blackboard["yavb_last_stuck_ms"] = now_ms
            node.blackboard["yavb_last_move_check_ms"] = now_ms
            _set_build_runtime_flags(node.blackboard, stuck_counter=0)
            return BehaviorTree.NodeState.RUNNING

        now_ms = time.monotonic() * 1000.0
        last_stuck_ms = float(node.blackboard.get("yavb_last_stuck_ms", now_ms))
        last_move_check_ms = float(node.blackboard.get("yavb_last_move_check_ms", now_ms))

        if Map.GetInstanceUptime() / 1000.0 > 7 * 60:
            Player.SendChatCommand("resign")
            node.blackboard["yavb_stuck_counter"] = 0
            _set_build_runtime_flags(node.blackboard, stuck_counter=0)
            return BehaviorTree.NodeState.RUNNING

        if now_ms - last_stuck_ms >= 5000.0:
            Player.SendChatCommand("stuck")
            node.blackboard["yavb_last_stuck_ms"] = now_ms

        if now_ms - last_move_check_ms >= 3000.0:
            current_pos = Player.GetXY()
            old_pos = node.blackboard.get("yavb_old_player_position", current_pos)
            if old_pos == current_pos:
                Player.SendChatCommand("stuck")
                stuck_counter = int(node.blackboard.get("yavb_stuck_counter", 0)) + 1
                node.blackboard["yavb_stuck_counter"] = stuck_counter
                node.blackboard["yavb_last_stuck_ms"] = now_ms
                _set_build_runtime_flags(node.blackboard, stuck_counter=stuck_counter)
                if stuck_counter >= 10:
                    Player.SendChatCommand("resign")
                    node.blackboard["yavb_stuck_counter"] = 0
                    _set_build_runtime_flags(node.blackboard, stuck_counter=0)
            else:
                node.blackboard["yavb_old_player_position"] = current_pos
                node.blackboard["yavb_stuck_counter"] = 0
                _set_build_runtime_flags(node.blackboard, stuck_counter=0)

            node.blackboard["yavb_last_move_check_ms"] = now_ms

        return BehaviorTree.NodeState.RUNNING

    return _action_tree("StuckDetectionService", _tick)


def InitializeBot() -> BehaviorTree:
    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="Initialize Bot",
            children=[
                LoadSharedConfigs().root,
                ResetRunFlags().root,
                BT.ResetActionQueues().root,
            ],
        )
    )


def get_execution_steps() -> list[tuple[str, Callable[[], BehaviorTree]]]:
    return [
        ("Initialize Bot", InitializeBot),
        ("Town Routines", TownRoutines),
        ("Traverse Bjora Marches", TraverseBjoraMarches),
        ("Farm Loop", FarmLoop),
    ]


def configure_upkeep_trees(tree: BottingTree) -> BottingTree:
    tree.DisableLooting()
    tree.DisableHeadlessHeroAI(reset_runtime=False)
    tree.pause_on_combat = False
    tree.SetRestoreIsolationOnStop(True)
    tree.SetUpkeepTrees([
        ("RuntimeResetService", RuntimeResetService),
        ("BuildService", BuildService),
        ("StuckDetectionService", StuckDetectionService),
    ])
    tree.AddPartyWipeRecoveryService(default_step_name=get_execution_steps()[0][0])
    return tree


def ensure_botting_tree() -> BottingTree:
    global botting_tree

    if botting_tree is None:
        botting_tree = configure_upkeep_trees(BottingTree(MODULE_NAME, pause_on_combat=False))
        botting_tree.SetMainRoutine(
            get_execution_steps(),
            name="YAVB Sequence",
            repeat=True,
            reset=False,
        )

    return botting_tree


def tooltip() -> None:
    PyImGui.begin_tooltip()

    title_color = Color(255, 200, 100, 255)
    ImGui.push_font("Regular", 20)
    PyImGui.text_colored("Yet Another Vaettir Bot (Y.A.V.B) 3.0", title_color.to_tuple_normalized())
    ImGui.pop_font()
    PyImGui.spacing()
    PyImGui.separator()

    PyImGui.text("A BottingTree port of the Vaettir farm route.")
    PyImGui.spacing()

    PyImGui.text_colored("Features:", title_color.to_tuple_normalized())
    PyImGui.bullet_text("Preserves the original YAVB 2.0 route and combat flow")
    PyImGui.bullet_text("Uses shared LootConfig, InventoryConfig, and BuyConfig")
    PyImGui.bullet_text("Loops in Jaga until inventory or supplies require town")
    PyImGui.bullet_text("Includes build and stuck watcher services")
    PyImGui.bullet_text("Supports")
    PyImGui.same_line(0, -1)

    assassin_color = ColorPalette.GetColor("gw_assassin")
    mesmer_color = ColorPalette.GetColor("gw_mesmer")
    PyImGui.text_colored("Assassin", assassin_color.to_tuple_normalized())
    PyImGui.same_line(0, -1)
    PyImGui.text(" and ")
    PyImGui.same_line(0, -1)
    PyImGui.text_colored("Mesmer", mesmer_color.to_tuple_normalized())
    PyImGui.same_line(0, -1)
    PyImGui.text(" professions")

    PyImGui.end_tooltip()


def main() -> None:
    global initialized

    if not initialized:
        ensure_botting_tree()
        initialized = True

    tree = ensure_botting_tree()
    tree.tick()
    tree.UI.draw_window()


if __name__ == "__main__":
    main()
