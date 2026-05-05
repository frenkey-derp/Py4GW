import json
import math
import os
from collections import Counter

import Py4GW
import PyImGui
from Py4GWCoreLib import (
    Routines,
    Botting,
    ActionQueueManager,
    ConsoleLog,
    GLOBAL_CACHE,
    Agent,
    Utils,
    ImGui,
    Color,
    ColorPalette,
    Party,
)
from Py4GWCoreLib import ThrottledTimer, Map, Player
from Py4GWCoreLib.BuildMgr import BuildMgr
from Py4GWCoreLib.Builds.Assassin.A_Me.SF_Ass_vaettir import SF_Ass_vaettir
from Py4GWCoreLib.Builds.Mesmer.Me_A.SF_Mes_vaettir import SF_Mes_vaettir
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.enums import ModelID, Range, TitleID
from Py4GWCoreLib.enums_src.Item_enums import INVENTORY_BAGS, ItemAction, ItemType
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.BuyConfig import BuyConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.InventoryConfig import InventoryConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig
from Sources.frenkeyLib.ItemHandling.BTNodes import BTNodes
from Sources.frenkeyLib.ItemHandling.InventoryBT import InventoryBT
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions

from typing import Generator, List, Tuple


MODULE_NAME = "YAVB 2.5 - InventoryBT"
MODULE_ICON = "Textures\\Module_Icons\\YAVB 2.0 mascot.png"
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
MERCHANT_XY = (-23110.0, 14942.0)
KEEP_GOLD_ON_CHARACTER = 5000
MAX_STORAGE_GOLD = 1000000
BJORA_TO_JAGA_PATH: List[Tuple[float, float]] = [
    (17810, -17649), (17516, -17270), (17166, -16813), (16862, -16324), (16472, -15934),
    (15929, -15731), (15387, -15521), (14849, -15312), (14311, -15101), (13776, -14882),
    (13249, -14642), (12729, -14386), (12235, -14086), (11748, -13776), (11274, -13450),
    (10839, -13065), (10572, -12590), (10412, -12036), (10238, -11485), (10125, -10918),
    (10029, -10348), (9909, -9778), (9599, -9327), (9121, -9009), (8674, -8645),
    (8215, -8289), (7755, -7945), (7339, -7542), (6962, -7103), (6587, -6666),
    (6210, -6226), (5834, -5788), (5457, -5349), (5081, -4911), (4703, -4470),
    (4379, -3990), (4063, -3507), (3773, -3031), (3452, -2540), (3117, -2070),
    (2678, -1703), (2115, -1593), (1541, -1614), (960, -1563), (388, -1491),
    (-187, -1419), (-770, -1426), (-1343, -1440), (-1922, -1455), (-2496, -1472),
    (-3073, -1535), (-3650, -1607), (-4214, -1712), (-4784, -1759), (-5278, -1492),
    (-5754, -1164), (-6200, -796), (-6632, -419), (-7192, -300), (-7770, -306),
    (-8352, -286), (-8932, -258), (-9504, -226), (-10086, -201), (-10665, -215),
    (-11247, -242), (-11826, -262), (-12400, -247), (-12979, -216), (-13529, -53),
    (-13944, 341), (-14358, 743), (-14727, 1181), (-15109, 1620), (-15539, 2010),
    (-15963, 2380), (-18048, 4223), (-19196, 4986), (-20000, 5595), (-20300, 5600),
]

bot = Botting("YAVB 2.5 - InventoryBT")
stop_bot_after_cleanup = False
AGGRO_BALL_COMPACT_RANGE = Range.Nearby.value
AGGRO_BALL_POLL_MS = 100
AGGRO_BALL_SAFETY_TIMEOUT_MS = 30000
EARLY_LOOT_ENEMY_THRESHOLD = 0
POST_CLEAR_SKILL_SUPPRESSION_RANGE = 1300.0
POST_CLEAR_SKILL_SUPPRESSION_FOE_COUNT = 40
STUCK_MOVEMENT_DELTA = 120.0
STUCK_PROGRESS_DELTA = 80.0
STUCK_PATH_WAYPOINT_REACHED = 180.0
STUCK_HOS_MIN_ENEMIES = 5

active_route_path: list[tuple[float, float]] = []
active_route_label = ""

STARTUP_ROUTING_ANCHOR = "Startup Routing_1"
TOWN_ROUTINES_ANCHOR = "Town Routines_2"
JAGA_ROUTINES_ANCHOR = "Jaga Moraine Farm Routine_7"
LOOT_ITEMS_ANCHOR = "Loot Items_11"
RESET_FARM_ANCHOR = "Reset Farm Loop_12"


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
    items = ItemSnapshot.get_items(INVENTORY_BAGS)
    quantity = 0
    for item in items:
        if entry.model_id is not None and item.model_id != entry.model_id:
            continue
        if entry.item_type is not None and item.item_type != entry.item_type:
            continue
        quantity += item.quantity
    return quantity


def _get_buy_entry_deficit(entry) -> int:
    return max(0, int(entry.quantity) - _current_buy_entry_quantity(entry))


def _needs_buy_restock() -> bool:
    needs_to_purchase = len(_get_missing_buy_entries()) > 0
    if needs_to_purchase:
        ConsoleLog(
            "Inventory Handling",
            "BuyConfig restock needed based on current inventory quantities.",
            Py4GW.Console.MessageType.Info,
        )
        
        for entry in BuyConfig().get_entries():
            if entry.quantity > 0:
                current_quantity = _current_buy_entry_quantity(entry)
                ConsoleLog(
                    "Inventory Handling",
                    f"BuyConfig Entry: model_id={entry.model_id}, item_type={entry.item_type}, desired_quantity={entry.quantity}, current_quantity={current_quantity}",
                    Py4GW.Console.MessageType.Info,
                )
                
    return needs_to_purchase


def _get_missing_buy_entries():
    return [
        entry
        for entry in BuyConfig().get_entries()
        if entry.quantity > 0 and _get_buy_entry_deficit(entry) > 0
    ]


def _has_pending_merchant_sales() -> bool:
    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        entry.action in {ItemAction.Sell_To_Merchant, ItemAction.Sell_To_Trader}
        for entry in preview_entries
    )


def _needs_merchant_visit() -> bool:
    return _has_pending_merchant_sales() or _needs_buy_restock()


def _has_executable_inventory_action(actions: set[ItemAction]) -> bool:
    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        entry.executable and entry.action in actions
        for entry in preview_entries
    )


def _get_processing_slot_reserve() -> int:
    if _has_executable_inventory_action({ItemAction.ExtractUpgrade}):
        return 2
    return 1


def _get_buy_slot_reserve() -> int:
    return len(_get_missing_buy_entries())


def _get_required_free_inventory_slots() -> int:
    return _get_buy_slot_reserve() + _get_processing_slot_reserve()


def _needs_inventory_management(bot: Botting) -> bool:
    free_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
    required_free_slots = _get_required_free_inventory_slots()

    if free_slots <= required_free_slots and (_can_free_slots_in_town() or _needs_buy_restock()):
        ConsoleLog(
            "Inventory Handling",
            (
                f"Inventory management needed after cleanup. {free_slots} free slots available, "
                f"required reserve is {required_free_slots} "
                f"(buy reserve={_get_buy_slot_reserve()}, processing reserve={_get_processing_slot_reserve()}). Routing to town."
            ),
            Py4GW.Console.MessageType.Info,
        )
        return True

    return False


def _has_loot_available() -> bool:
    return bool(
        LootConfig().GetfilteredLootArray(
            distance=Range.Earshot.value,
            multibox_loot=True,
            allow_unasigned_loot=False,
        )
    )


def _has_explorable_inventory_actions() -> bool:
    actionable_explorable_actions = {
        ItemAction.Use,
        ItemAction.Drop,
        ItemAction.Identify,
        ItemAction.ExtractUpgrade,
        ItemAction.Salvage_Rare_Materials,
        ItemAction.Salvage_Common_Materials,
        ItemAction.Destroy,
    }

    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        entry.executable and entry.action in actionable_explorable_actions
        for entry in preview_entries
    )


def _has_blocked_explorable_inventory_actions() -> bool:
    actionable_explorable_actions = {
        ItemAction.Use,
        ItemAction.Drop,
        ItemAction.Identify,
        ItemAction.ExtractUpgrade,
        ItemAction.Salvage_Rare_Materials,
        ItemAction.Salvage_Common_Materials,
        ItemAction.Destroy,
    }

    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        not entry.executable and entry.action in actionable_explorable_actions
        for entry in preview_entries
    )


def _get_non_executable_explorable_inventory_entries():
    actionable_explorable_actions = {
        ItemAction.Use,
        ItemAction.Drop,
        ItemAction.Identify,
        ItemAction.ExtractUpgrade,
        ItemAction.Salvage_Rare_Materials,
        ItemAction.Salvage_Common_Materials,
        ItemAction.Destroy,
    }

    preview_entries = InventoryBT.Preview(InventoryConfig())
    return [
        entry
        for entry in preview_entries
        if not entry.executable and entry.action in actionable_explorable_actions
    ]


def _needs_reserved_salvage_slot() -> bool:
    reserve_slot_actions = {
        ItemAction.ExtractUpgrade,
        ItemAction.Salvage_Rare_Materials,
        ItemAction.Salvage_Common_Materials,
    }

    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        entry.executable and entry.action in reserve_slot_actions
        for entry in preview_entries
    )


def _has_pending_inventory_processing() -> bool:
    process_actions = {
        ItemAction.Sell_To_Trader,
        ItemAction.Sell_To_Merchant,
        ItemAction.Identify,
        ItemAction.Salvage_Common_Materials,
        ItemAction.Salvage_Rare_Materials,
        ItemAction.ExtractUpgrade,
        ItemAction.Stash,
        ItemAction.Destroy,
        ItemAction.Drop,
        ItemAction.Use,
    }
    return _has_executable_inventory_action(process_actions)


def _get_inventory_work_signature():
    preview_entries = InventoryBT.Preview(InventoryConfig())
    processing_counts = Counter(
        (
            entry.action.name if entry.action is not None else "NONE",
            bool(entry.executable),
        )
        for entry in preview_entries
        if (
            entry.action is not None
            and entry.action != ItemAction.NONE
            and (
                entry.executable
                or entry.action in {ItemAction.Sell_To_Merchant, ItemAction.Sell_To_Trader}
            )
        )
    )
    buy_deficits = tuple(
        sorted(
            (
                int(entry.model_id) if entry.model_id is not None else -1,
                entry.item_type.name if entry.item_type is not None else "NONE",
                _get_buy_entry_deficit(entry),
            )
            for entry in BuyConfig().get_entries()
            if entry.quantity > 0 and _get_buy_entry_deficit(entry) > 0
        )
    )
    return (
        GLOBAL_CACHE.Inventory.GetFreeSlotCount(),
        tuple(sorted(processing_counts.items())),
        buy_deficits,
    )


def _get_inventory_layout_signature():
    snapshot = ItemSnapshot.get_bags_snapshot(INVENTORY_BAGS)
    return tuple(
        (
            bag.value,
            slot,
            item.id if item is not None and item.is_valid else 0,
            item.quantity if item is not None and item.is_valid else 0,
        )
        for bag in INVENTORY_BAGS
        for slot, item in sorted(snapshot.get(bag, {}).items())
    )


def _can_free_slots_in_town() -> bool:
    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        (
            entry.action in {ItemAction.Sell_To_Merchant, ItemAction.Sell_To_Trader}
            or (entry.action == ItemAction.Stash and entry.executable)
        )
        for entry in preview_entries
    )


def _open_xunlai_window(timeout_ms: int = 5000):
    start_time = Utils.GetBaseTimestamp()
    while not Inventory.IsStorageOpen():
        Inventory.OpenXunlaiWindow()
        yield from Routines.Yield.wait(250)
        if Utils.GetBaseTimestamp() - start_time >= timeout_ms:
            break


def _deposit_town_gold():
    if not Inventory.IsStorageOpen():
        return

    gold_on_character = max(0, int(GLOBAL_CACHE.Inventory.GetGoldOnCharacter() or 0))
    gold_in_storage = max(0, int(GLOBAL_CACHE.Inventory.GetGoldInStorage() or 0))

    if gold_on_character <= KEEP_GOLD_ON_CHARACTER:
        return

    storage_space_left = max(0, MAX_STORAGE_GOLD - gold_in_storage)
    if storage_space_left <= 0:
        return

    gold_to_deposit = min(gold_on_character - KEEP_GOLD_ON_CHARACTER, storage_space_left)
    if gold_to_deposit <= 0:
        return

    GLOBAL_CACHE.Inventory.DepositGold(gold_to_deposit)
    yield from Routines.Yield.wait(250)


def _open_merchant_window(timeout_ms: int = 8000):
    yield from Routines.Yield.Movement.FollowPath([MERCHANT_XY], timeout=15000)

    start_time = Utils.GetBaseTimestamp()
    while not UIManagerExtensions.MerchantWindow.IsOpen():
        yield from Routines.Yield.Agents.TargetNearestNPCXY(MERCHANT_XY[0], MERCHANT_XY[1], 300)
        if Player.GetTargetID() != 0:
            yield from Routines.Yield.Player.InteractTarget()
        yield from Routines.Yield.wait(500)
        if Utils.GetBaseTimestamp() - start_time >= timeout_ms:
            break


def _run_inventory_pass(*, tolerate_failure: bool = True, max_ticks: int = 80, settle_ticks: int = 3):
    config = InventoryConfig()
    runner = InventoryBT(config)
    success_streak = 0
    
    if not runner.HasExecuteableInventoryActions(config):
        return

    for _ in range(max_ticks):
        result = runner.tick()

        if result == runner.NodeState.RUNNING:
            success_streak = 0
            yield from Routines.Yield.wait(100)
            continue

        if result == runner.NodeState.FAILURE:
            return

        success_streak += 1
        if success_streak >= settle_ticks:
            return

        yield from Routines.Yield.wait(100)

    if not tolerate_failure:
        ConsoleLog("Inventory Handling", "InventoryBT pass timed out.", Py4GW.Console.MessageType.Warning)


def _restock_buy_config():
    if not UIManagerExtensions.MerchantWindow.IsOpen():
        return False

    purchased_any = False
    for entry in BuyConfig().get_entries():
        if entry.quantity <= 0:
            continue

        needed_quantity = _get_buy_entry_deficit(entry)
        if needed_quantity <= 0:
            continue

        offered_items = list(GLOBAL_CACHE.Trading.Merchant.GetOfferedItems() or [])
        matched_item_id = 0
        for offered_item_id in offered_items:
            offered_model_id = int(GLOBAL_CACHE.Item.GetModelID(offered_item_id) or 0)
            offered_type_value, _ = GLOBAL_CACHE.Item.GetItemType(offered_item_id)

            if entry.model_id is not None and offered_model_id == int(entry.model_id):
                matched_item_id = offered_item_id
                break

            if entry.model_id is None and entry.item_type is not None:
                try:
                    offered_type = ItemType(offered_type_value)
                except ValueError:
                    continue
                if offered_type.matches(entry.item_type):
                    matched_item_id = offered_item_id
                    break

        if matched_item_id == 0:
            continue

        item_value = max(0, int(GLOBAL_CACHE.Item.Properties.GetValue(matched_item_id) or 0))
        if item_value <= 0:
            continue

        buy_price = item_value * 2
        affordable_quantity = int(GLOBAL_CACHE.Inventory.GetGoldOnCharacter() or 0) // buy_price
        purchase_count = min(needed_quantity, affordable_quantity)
        for _ in range(purchase_count):
            GLOBAL_CACHE.Trading.Merchant.BuyItem(matched_item_id, buy_price)
            purchased_any = True
            yield from Routines.Yield.wait(100)
    return purchased_any


def _set_active_route_path(path_points: List[Tuple[float, float]], label: str = "") -> None:
    global active_route_path, active_route_label
    active_route_path = list(path_points)
    active_route_label = label


def _clear_active_route_path() -> None:
    global active_route_path, active_route_label
    active_route_path = []
    active_route_label = ""


def _get_expected_build() -> BuildMgr | None:
    profession, _ = Agent.GetProfessionNames(Player.GetAgentID())
    match profession:
        case "Assassin":
            return SF_Ass_vaettir()
        case "Mesmer":
            return SF_Mes_vaettir()
        case _:
            return None


def _has_correct_vaettir_build() -> bool:
    expected_build = _get_expected_build()
    if expected_build is None:
        return False
    return expected_build.ScoreMatch() >= expected_build.minimum_required_match


def _should_force_town_start() -> bool:
    if not _has_correct_vaettir_build():
        return True
    if not Party.IsHardMode():
        return True
    return _needs_inventory_management(bot)


def _get_nearest_path_index(path_points: List[Tuple[float, float]]) -> int:
    if not path_points:
        return 0

    player_pos = Player.GetXY()
    return min(range(len(path_points)), key=lambda index: Utils.Distance(player_pos, path_points[index]))


def _jump_to_state(bot: Botting, state_name: str):
    fsm = bot.config.FSM
    fsm.pause()
    fsm.jump_to_state_by_name(state_name)
    fsm.resume()
    yield


def _anchor_step():
    yield


def _get_aggro_enemy_ids(scan_range: float = Range.Earshot.value) -> list[int]:
    px, py = Player.GetXY()
    return [
        enemy_id
        for enemy_id in Routines.Agents.GetFilteredEnemyArray(px, py, scan_range)
        if enemy_id and not Agent.IsDead(enemy_id)
    ]


def _should_suppress_post_clear_skills() -> bool:
    if Map.GetMapID() != JAGA_MORAINE:
        return False

    if Map.GetFoesKilled() <= POST_CLEAR_SKILL_SUPPRESSION_FOE_COUNT:
        return False

    return len(_get_aggro_enemy_ids(POST_CLEAR_SKILL_SUPPRESSION_RANGE)) == 0


def _all_aggro_enemies_within_range(required_range: float) -> bool:
    px, py = Player.GetXY()
    for enemy_id in _get_aggro_enemy_ids():
        ex, ey = Agent.GetXY(enemy_id)
        if Utils.Distance((px, py), (ex, ey)) > required_range:
            return False
    return True


def _get_next_route_waypoint() -> Tuple[float, float] | None:
    if not active_route_path:
        return None

    player_pos = Player.GetXY()
    for waypoint in active_route_path:
        if Utils.Distance(player_pos, waypoint) > STUCK_PATH_WAYPOINT_REACHED:
            return waypoint

    return active_route_path[-1] if active_route_path else None


def _find_heart_of_shadow_escape_target(goal_point: Tuple[float, float] | None) -> int:
    player_pos = Player.GetXY()
    enemy_ids = _get_aggro_enemy_ids(Range.Spellcast.value)
    if not enemy_ids:
        return 0

    if goal_point is None:
        return enemy_ids[0]

    to_goal = (goal_point[0] - player_pos[0], goal_point[1] - player_pos[1])
    goal_mag = math.hypot(*to_goal)
    if goal_mag <= 0:
        return enemy_ids[0]

    best_enemy_id = 0
    best_score = 2.0
    for enemy_id in enemy_ids:
        ex, ey = Agent.GetXY(enemy_id)
        to_enemy = (ex - player_pos[0], ey - player_pos[1])
        enemy_mag = math.hypot(*to_enemy)
        if enemy_mag <= 0:
            continue

        score = ((to_goal[0] * to_enemy[0]) + (to_goal[1] * to_enemy[1])) / (goal_mag * enemy_mag)
        if score < best_score:
            best_score = score
            best_enemy_id = enemy_id

    return best_enemy_id


def _cast_stuck_recovery_heart_of_shadow(bot: Botting) -> Generator[None, None, bool]:
    build = bot.config.build_handler
    if not isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
        return False

    enemy_ids = _get_aggro_enemy_ids(Range.Area.value)
    if len(enemy_ids) < STUCK_HOS_MIN_ENEMIES:
        return False

    goal_point = _get_next_route_waypoint()
    target_enemy_id = _find_heart_of_shadow_escape_target(goal_point)
    if target_enemy_id <= 0:
        return False

    Player.ChangeTarget(target_enemy_id)
    yield from Routines.Yield.wait(75)

    if not (yield from Routines.Yield.Skills.IsSkillIDUsable(build.heart_of_shadow)):
        return False

    if goal_point is not None:
        ConsoleLog(
            "HandleStuck",
            f"Casting Heart of Shadow toward route recovery. Goal={goal_point}, target={target_enemy_id}, path='{active_route_label}'.",
            Py4GW.Console.MessageType.Warning,
            True,
        )
    else:
        ConsoleLog(
            "HandleStuck",
            f"Casting Heart of Shadow toward fallback target {target_enemy_id}.",
            Py4GW.Console.MessageType.Warning,
            True,
        )

    if (yield from build._CastSkillID(build.heart_of_shadow, log=False, aftercast_delay=350)):
        build.SetStuckSignal(0)
        return True

    return False


def LootItemsWithSharedConfig():
    item_timeout_ms = 10000
    last_loot_seen_ms = Utils.GetBaseTimestamp()
    last_interact_ms = 0
    consecutive_empty_polls = 0
    settle_after_empty_ms = 1250
    min_post_interact_ms = 900
    current_item_agent_id = 0
    current_item_seen_ms = 0

    while True:
        now_ms = Utils.GetBaseTimestamp()
        free_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
        reserved_slots = max(
            _get_required_free_inventory_slots(),
            1 if _needs_reserved_salvage_slot() else 0,
        )
        if free_slots <= reserved_slots:
            return

        loot_array = LootConfig().GetfilteredLootArray(
            distance=Range.Earshot.value,
            multibox_loot=True,
            allow_unasigned_loot=False,
        )
        if not loot_array:
            consecutive_empty_polls += 1

            current_target = Player.GetTargetID()
            target_is_item = current_target > 0 and Agent.IsValid(current_target) and Agent.IsItem(current_target)
            last_activity_ms = max(last_loot_seen_ms, last_interact_ms)

            if target_is_item and now_ms - last_interact_ms < min_post_interact_ms:
                yield from Routines.Yield.wait(200)
                continue

            if now_ms - last_activity_ms < settle_after_empty_ms:
                yield from Routines.Yield.wait(200)
                continue

            if consecutive_empty_polls < 3:
                yield from Routines.Yield.wait(200)
                continue

            return

        consecutive_empty_polls = 0
        last_loot_seen_ms = now_ms

        item_agent_id = loot_array[0]
        if item_agent_id != current_item_agent_id:
            current_item_agent_id = item_agent_id
            current_item_seen_ms = now_ms
        elif now_ms - current_item_seen_ms >= item_timeout_ms:
            item_data = Agent.GetItemAgentByID(item_agent_id)
            if item_data is not None:
                LootConfig().blacklisted_items.append(item_data.item_id)
            current_item_agent_id = 0
            current_item_seen_ms = 0
            yield from Routines.Yield.wait(100)
            continue

        if Player.GetTargetID() != item_agent_id:
            Player.ChangeTarget(item_agent_id)
            yield from Routines.Yield.wait(100)
        Player.Interact(item_agent_id, False)
        last_interact_ms = Utils.GetBaseTimestamp()
        yield from Routines.Yield.wait(500)


def ProcessLootAndInventory():
    global stop_bot_after_cleanup

    stop_bot_after_cleanup = False
    for _ in range(12):
        yield from LootItemsWithSharedConfig()

        loot_remaining = _has_loot_available()
        inventory_actions_remaining = _has_explorable_inventory_actions()
        blocked_preview_entries = _get_non_executable_explorable_inventory_entries()
        blocked_inventory_actions_remaining = len(blocked_preview_entries) > 0

        if not inventory_actions_remaining and not loot_remaining:
            return

        if blocked_inventory_actions_remaining and inventory_actions_remaining:
            ConsoleLog(
                "Inventory Handling",
                "Ignoring non-executable explorable preview entries and continuing with executable cleanup.",
                Py4GW.Console.MessageType.Info,
            )

        if inventory_actions_remaining:
            _reset_runtime_item_state()
            yield from _run_inventory_pass(tolerate_failure=True, max_ticks=30, settle_ticks=2)

        loot_remaining = _has_loot_available()
        inventory_actions_remaining = _has_explorable_inventory_actions()
        blocked_preview_entries = _get_non_executable_explorable_inventory_entries()
        blocked_inventory_actions_remaining = len(blocked_preview_entries) > 0
        if not inventory_actions_remaining and not loot_remaining:
            return

        if blocked_inventory_actions_remaining and inventory_actions_remaining:
            ConsoleLog(
                "Inventory Handling",
                "Non-executable explorable preview entries remain after cleanup, but they are not treated as fatal here.",
                Py4GW.Console.MessageType.Info,
            )

        if loot_remaining and GLOBAL_CACHE.Inventory.GetFreeSlotCount() <= 0 and not inventory_actions_remaining:
            if _can_free_slots_in_town():
                return

            stop_bot_after_cleanup = True
            ConsoleLog(
                "Inventory Handling",
                "Inventory is full, loot remains on the ground, and town cannot free slots. Stopping bot.",
                Py4GW.Console.MessageType.Warning,
            )
            return

    ConsoleLog(
        "Inventory Handling",
        "Post-kill loot/inventory loop reached safety limit. Resigning to town for recovery.",
        Py4GW.Console.MessageType.Warning,
    )
    Player.SendChatCommand("resign")
    yield from Routines.Yield.wait(500)

def RunInventoryBT(bt : InventoryBT, config: InventoryConfig, max_ticks: int = 80, settle_ticks: int = 3, tolerate_failure: bool = True):
    success_streak = 0
    
    for _ in range(max_ticks):
        result = bt.tick()
        
        if result == bt.NodeState.RUNNING:
            success_streak = 0
            yield from Routines.Yield.wait(100)
            continue

        if result == bt.NodeState.FAILURE:
            Py4GW.Console.Log("Inventory Handling", "InventoryBT pass failed.", Py4GW.Console.MessageType.Warning)
            return

        success_streak += 1
        if success_streak >= settle_ticks:
            Py4GW.Console.Log("Inventory Handling", "InventoryBT pass completed successfully.", Py4GW.Console.MessageType.Info)
            return

        yield from Routines.Yield.wait(100)

    if not tolerate_failure:
        Py4GW.Console.Log("Inventory Handling", "InventoryBT pass timed out.", Py4GW.Console.MessageType.Warning)

def HandleSharedInventory(bot: Botting):
    _load_shared_configs()
    _reset_runtime_item_state()

    yield from _open_xunlai_window()
    yield from _deposit_town_gold()

    bt = InventoryBT()
    config = InventoryConfig()
    stalled_iterations = 0
    attempted_forced_sort = False
    
    
    while True:
        before_work_signature = _get_inventory_work_signature()
        before_layout_signature = _get_inventory_layout_signature()

        if bt.HasExecuteableInventoryActions(config):            
            yield from RunInventoryBT(bt, config, tolerate_failure=False, max_ticks=30, settle_ticks=2)
            
        if _needs_merchant_visit():
            yield from _open_merchant_window()
            
            if UIManagerExtensions.MerchantWindow.IsOpen():
                if _needs_buy_restock():
                    yield from _restock_buy_config()

        after_work_signature = _get_inventory_work_signature()
        after_layout_signature = _get_inventory_layout_signature()

        if before_work_signature == after_work_signature and before_layout_signature == after_layout_signature:
            stalled_iterations += 1
        else:
            stalled_iterations = 0

        if stalled_iterations >= 1:
            if not attempted_forced_sort and InventoryBT._needs_inventory_sorting():
                attempted_forced_sort = True
                ConsoleLog(
                    "Inventory Handling",
                    "InventoryBT made no town progress. Forcing one inventory sort pass before continuing.",
                    Py4GW.Console.MessageType.Info,
                )
                BTNodes.Bags.SortBags(INVENTORY_BAGS).tick()
                yield from Routines.Yield.wait(250)
                stalled_iterations = 0
                continue

            ConsoleLog(
                "Inventory Handling",
                "No further inventory progress is possible in town. Continuing with remaining non-stashable items.",
                Py4GW.Console.MessageType.Info,
            )
            break

        if not bt.HasExecuteableInventoryActions(config):
            break

    yield


def StartupRouting(bot: Botting):
    _apply_bot_runtime_defaults(bot)

    current_map_id = Map.GetMapID()
    # enemy_count_in_compass = len(_get_aggro_enemy_ids(Range.Compass.value))
    killed_foes = Map.GetFoesKilled()
    has_loot = _has_loot_available()

    if _should_force_town_start():
        ConsoleLog(
            "Startup Routing",
            "Routing to town because the build is wrong, hard mode is off, or inventory requires a merchant.",
            Py4GW.Console.MessageType.Info,
        )
        yield from _jump_to_state(bot, TOWN_ROUTINES_ANCHOR)
        return

    if current_map_id == JAGA_MORAINE:
        ConsoleLog(
            "Startup Routing",
            f"Detected Jaga Moraine start with {killed_foes} killed foes and {("available loot" if has_loot else "no loot available")}.",
            Py4GW.Console.MessageType.Info,
        )

        yield from AssignBuild(bot)

        if killed_foes <= 10:
            yield from _jump_to_state(bot, JAGA_ROUTINES_ANCHOR)
            return

        if has_loot:
            yield from ProcessLootAndInventory()

            if stop_bot_after_cleanup:
                bot.Stop()
                yield
                return

            if _needs_inventory_management(bot):
                ConsoleLog(
                    "Startup Routing",
                    "Inventory management needed after loot in Jaga Moraine. Routing to town.",
                    Py4GW.Console.MessageType.Info,
                )
                yield from _jump_to_state(bot, TOWN_ROUTINES_ANCHOR)
                return

        yield from _jump_to_state(bot, LOOT_ITEMS_ANCHOR)
        return

    if current_map_id == BJORA_MARCHES:
        nearest_index = _get_nearest_path_index(BJORA_TO_JAGA_PATH)
        remaining_path = BJORA_TO_JAGA_PATH[nearest_index:]

        ConsoleLog(
            "Startup Routing",
            f"Detected Bjora Marches start. Resuming route from waypoint {nearest_index + 1}/{len(BJORA_TO_JAGA_PATH)}.",
            Py4GW.Console.MessageType.Info,
        )

        _set_active_route_path(remaining_path, "Startup Bjora Resume")
        reached_exit = yield from Routines.Yield.Movement.FollowPath(
            remaining_path,
            timeout=180000,
            map_transition_exit_success=True,
        )
        _clear_active_route_path()

        if reached_exit and Map.GetMapID() == JAGA_MORAINE:
            yield from _jump_to_state(bot, JAGA_ROUTINES_ANCHOR)
            return

        ConsoleLog(
            "Startup Routing",
            "Failed to resume from Bjora Marches cleanly, routing to town.",
            Py4GW.Console.MessageType.Warning,
        )
        yield from _jump_to_state(bot, TOWN_ROUTINES_ANCHOR)
        return

    ConsoleLog(
        "Startup Routing",
        "No resumable map detected, routing to town.",
        Py4GW.Console.MessageType.Info,
    )
    yield from _jump_to_state(bot, TOWN_ROUTINES_ANCHOR)


def create_bot_routine(bot: Botting) -> None:
    bot.States.AddCustomState(_anchor_step, STARTUP_ROUTING_ANCHOR)
    bot.States.AddHeader("Startup Routing")
    bot.States.AddCustomState(lambda: StartupRouting(bot), "Startup Routing")
    TownRoutines(bot)
    TraverseBjoraMarches(bot)
    JagaMoraineFarmRoutine(bot)
    ResetFarmLoop(bot)


def _apply_bot_runtime_defaults(bot: Botting) -> None:
    condition = lambda: on_death(bot)
    bot.Events.OnDeathCallback(condition)
    _load_shared_configs()
    _reset_runtime_item_state()
    bot.Properties.Disable("auto_inventory_management")
    bot.Properties.Disable("auto_loot")
    bot.Properties.Disable("hero_ai")
    bot.Properties.Enable("build_ticker")
    bot.Properties.Disable("pause_on_danger")
    bot.Properties.Enable("halt_on_death")
    bot.Properties.Set("movement_timeout", value=-1)
    bot.Properties.Enable("identify_kits")
    bot.Properties.Enable("salvage_kits")
    bot.Properties.Disable("birthday_cupcake")


def InitializeBot(bot: Botting) -> None:
    bot.States.AddHeader("Initialize Bot")
    _apply_bot_runtime_defaults(bot)


def TownRoutines(bot: Botting) -> None:
    bot.States.AddCustomState(_anchor_step, TOWN_ROUTINES_ANCHOR)
    bot.States.AddHeader("Town Routines")
    bot.Map.Travel(target_map_id=650)
    InitializeBot(bot)
    bot.States.AddCustomState(lambda: EquipSkillBar(bot), "Equip SkillBar")
    HandleInventory(bot)
    bot.States.AddHeader("Exit to Bjora Marches")
    bot.Party.SetHardMode(True)
    # bot.Properties.Enable("birthday_cupcake")
    bot.Move.XYAndExitMap(-26375, 16180, target_map_id=482)


def TraverseBjoraMarches(bot: Botting) -> None:
    bot.States.AddHeader("Traverse Bjora Marches")
    bot.Player.SetTitle(TitleID.Norn.value)
    bot.Move.FollowPathAndExitMap(BJORA_TO_JAGA_PATH, target_map_id=546)


def JagaMoraineFarmRoutine(bot: Botting) -> None:
    def _follow_and_wait(path_points: List[Tuple[float, float]], wait_state_name: str, cycle_timeout: int = 150):
        _set_active_route_path(path_points, wait_state_name)
        bot.Move.FollowPath(path_points)
        bot.States.AddCustomState(lambda: WaitForBall(bot, wait_state_name, cycle_timeout), f"Wait for {wait_state_name}")

    bot.States.AddCustomState(_anchor_step, JAGA_ROUTINES_ANCHOR)
    bot.States.AddHeader("Jaga Moraine Farm Routine")
    InitializeBot(bot)
    # bot.Properties.Disable("birthday_cupcake")
    bot.States.AddCustomState(lambda: AssignBuild(bot), "Assign Build")
    _set_active_route_path([(13372.44, -20758.50)], "Jaga Shrine")
    bot.Move.XY(13372.44, -20758.50)
    bot.Dialogs.AtXY(13367, -20771, 0x84)
    bot.States.AddManagedCoroutine("HandleStuckJagaMoraine", lambda: HandleStuckJagaMoraine(bot))
    bot.States.AddManagedCoroutine("ManagePostClearSkillUsage", lambda: ManagePostClearSkillUsage(bot))

    path: List[Tuple[float, float]] = [
        (13367, -20771),
        (11375, -22761), (10925, -23466), (10917, -24311), (10280, -24620),
        (10280, -24620), (9640, -23175), (7815, -23200), (6626.51, -23167.24),
    ]
    _follow_and_wait(path, "Inner Packs", cycle_timeout=75)

    path = [(7765, -22940), (8213, -22829), (8740, -22475), (8880, -21384), (8684, -20833), (8982, -20576)]
    bot.States.AddHeader("Wait for Left Aggro Ball")
    _follow_and_wait(path, "Left Aggro Ball")

    path = [(10196, -20124), (10123, -19529), (10049, -18933)]
    _follow_and_wait(path, "log side packs", cycle_timeout=75)

    path = [(9976, -18338), (11316, -18056), (10392, -17512), (10114, -16948)]
    _follow_and_wait(path, "Big Pack")

    path = [
        (10729, -16273), (10505, -14750), (10815, -14790), (11090, -15345),
        (11670, -15457), (12604, -15320), (12450, -14800), (12725, -14850), (12476, -16157),
    ]
    _follow_and_wait(path, "Right Aggro Ball")

    bot.Properties.Set("movement_tolerance", value=25)
    path_points_to_killing_spot: List[Tuple[float, float]] = [
        (13070, -16911), (12938, -17081), (12790, -17201), (12747, -17220),
        (12703, -17239), (12684, -17184), (12485.18, -17260.41),
    ]
    _set_active_route_path(path_points_to_killing_spot, "Kill Spot")
    bot.Move.FollowPath(path_points_to_killing_spot)
    bot.Properties.ResetTodefault("movement_tolerance", field="value")
    bot.States.AddHeader("Kill Enemies")
    bot.States.AddCustomState(lambda: KillEnemies(bot), "Kill Enemies")
    bot.States.RemoveManagedCoroutine("HandleStuckJagaMoraine")
    _clear_active_route_path()
    bot.States.AddCustomState(_anchor_step, LOOT_ITEMS_ANCHOR)
    bot.States.AddHeader("Loot Items")
    bot.States.AddCustomState(ProcessLootAndInventory, "Loot And Inventory")
    bot.States.AddCustomState(lambda: NeedsInventoryManagement(bot), "Needs Inventory Management")
    # bot.Properties.Disable("birthday_cupcake")
    path_to_portal: List[Tuple[float, float]] = [
        (13182, -16901), (14502, -17841), (14258, -19639), (14767, -20241), 
    ]
    
    closest_point = min(path_to_portal, key=lambda point: Utils.Distance(Player.GetXY(), point))
    point_index = path_to_portal.index(closest_point) + 1
    final_path = path_to_portal[point_index:] if point_index < len(path_to_portal) else [path_to_portal[len(path_to_portal) - 1]]
    
    _set_active_route_path(final_path, "Exit Jaga")
    bot.Move.FollowPath(final_path)
    
    bot.Move.XYAndExitMap(15850, -20550, target_map_id=482)


def NeedsInventoryManagement(bot: Botting):
    global stop_bot_after_cleanup

    if stop_bot_after_cleanup:
        stop_bot_after_cleanup = False
        bot.Stop()
        yield
        return

    free_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
    required_free_slots = max(
        _get_required_free_inventory_slots(),
        1 if _needs_reserved_salvage_slot() else 0,
    )

    if _needs_inventory_management(bot):
        Py4GW.Console.Log(
            "Inventory Handling",
            (
                f"Inventory management is needed after cleanup. {free_slots} free slots available, "
                f"but {required_free_slots} are reserved for processing and missing buy stock."
            ),
            Py4GW.Console.MessageType.Info,
        )
        Player.SendChatCommand("resign")
        yield from Routines.Yield.wait(500)
    yield


def ResetFarmLoop(bot: Botting) -> None:
    bot.States.AddCustomState(_anchor_step, RESET_FARM_ANCHOR)
    bot.States.AddHeader("Reset Farm Loop")
    _set_active_route_path([(-20300, 5600)], "Reset to Bjora")
    bot.Move.XYAndExitMap(-20300, 5600, target_map_id=546)
    bot.States.JumpToStepName("[H]Jaga Moraine Farm Routine_7")


def KillEnemies(bot: Botting):
    _set_build_routine_state(bot, in_killing=True, routine_finished=False)

    player_pos = Player.GetXY()
    enemy_array = Routines.Agents.GetFilteredEnemyArray(player_pos[0], player_pos[1], Range.Spellcast.value)

    start_time = Utils.GetBaseTimestamp()
    timeout = 120000

    while len(enemy_array) > 0:
        if Utils.GetBaseTimestamp() - start_time > timeout and timeout > 0:
            ConsoleLog("Killing Routine", "Timeout reached, restarting.", Py4GW.Console.MessageType.Error)
            Player.SendChatCommand("resign")
            yield from Routines.Yield.wait(500)
            return

        if Agent.IsDead(Player.GetAgentID()):
            ConsoleLog("Killing Routine", "Player is dead, restarting.", Py4GW.Console.MessageType.Warning)
            yield from Routines.Yield.wait(500)
            return

        if len(enemy_array) <= EARLY_LOOT_ENEMY_THRESHOLD:
            ConsoleLog(
                "Killing Routine",
                f"Only {len(enemy_array)} enemies remain, switching to loot cleanup while keeping buffs active.",
                Py4GW.Console.MessageType.Info,
            )
            _set_build_routine_state(bot, in_killing=False, routine_finished=False)
            return

        yield from Routines.Yield.wait(1000)
        enemy_array = Routines.Agents.GetFilteredEnemyArray(player_pos[0], player_pos[1], Range.Spellcast.value)

    _set_build_routine_state(bot, in_killing=False, routine_finished=False)

    ConsoleLog("Killing Routine", "Finished Killing Routine", Py4GW.Console.MessageType.Info)
    yield from Routines.Yield.wait(1000)


def AssignBuild(bot: Botting):
    profession, _ = Agent.GetProfessionNames(Player.GetAgentID())
    match profession:
        case "Assassin":
            bot.OverrideBuild(SF_Ass_vaettir())
        case "Mesmer":
            bot.OverrideBuild(SF_Mes_vaettir())
        case _:
            ConsoleLog(
                "Unsupported Profession",
                f"The profession '{profession}' is not supported by this bot.",
                Py4GW.Console.MessageType.Error,
                True,
            )
            bot.Stop()
            return
    yield


def EquipSkillBar(bot: Botting):
    yield from AssignBuild(bot)
    yield from bot.config.build_handler.LoadSkillBar()


def _set_build_stuck_signal(build: BuildMgr, stuck_counter: int) -> None:
    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
        build.SetStuckSignal(stuck_counter)


def _set_build_routine_state(bot: Botting, *, in_killing: bool, routine_finished: bool) -> None:
    global in_killing_routine, finished_routine

    in_killing_routine = in_killing
    finished_routine = routine_finished

    build = bot.config.build_handler
    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
        build.SetKillingRoutine(in_killing)
        build.SetRoutineFinished(routine_finished)


def HandleInventory(bot: Botting) -> None:
    bot.States.AddHeader("Inventory Handling")
    bot.States.AddCustomState(lambda: HandleSharedInventory(bot), "Shared Inventory Handling")
    # bot.Items.Restock.BirthdayCupcake()


def ManagePostClearSkillUsage(bot: Botting):
    skills_suppressed = False

    while True:
        if Map.GetMapID() != JAGA_MORAINE:
            if skills_suppressed:
                bot.Properties.Enable("build_ticker")
            return

        should_suppress = _should_suppress_post_clear_skills()
        if should_suppress and not skills_suppressed:
            bot.Properties.Disable("build_ticker")
            skills_suppressed = True
            ConsoleLog(
                "Skill Usage",
                f"Suppressing skills after {Map.GetFoesKilled()} kills because no enemies are within {POST_CLEAR_SKILL_SUPPRESSION_RANGE:.0f} units.",
                Py4GW.Console.MessageType.Info,
            )
        elif not should_suppress and skills_suppressed:
            bot.Properties.Enable("build_ticker")
            skills_suppressed = False
            ConsoleLog(
                "Skill Usage",
                "Enemies re-entered range, re-enabling build skills.",
                Py4GW.Console.MessageType.Info,
            )

        yield from Routines.Yield.wait(250)


def _wait_for_aggro_ball(bot: Botting, side_label: str, cycle_timeout: int = 150):
    global in_waiting_routine

    ConsoleLog(
        f"Waiting for {side_label} Aggro Ball",
        f"Waiting until all aggroed enemies are within {AGGRO_BALL_COMPACT_RANGE:.0f} range.",
        Py4GW.Console.MessageType.Info,
    )

    in_waiting_routine = True
    build = bot.config.build_handler
    started_at = Utils.GetBaseTimestamp()
    safety_timeout_ms = max(cycle_timeout * 100, AGGRO_BALL_SAFETY_TIMEOUT_MS)

    try:
        while True:
            yield from Routines.Yield.wait(AGGRO_BALL_POLL_MS)

            if Agent.IsDead(Player.GetAgentID()):
                ConsoleLog(
                    f"{side_label} Aggro Ball Wait",
                    "Player is dead, exiting wait.",
                    Py4GW.Console.MessageType.Warning,
                )
                yield
                return

            if _all_aggro_enemies_within_range(AGGRO_BALL_COMPACT_RANGE):
                ConsoleLog(
                    f"{side_label} Aggro Ball Wait",
                    "Enemies balled up successfully.",
                    Py4GW.Console.MessageType.Info,
                )
                break

            if Utils.GetBaseTimestamp() - started_at >= safety_timeout_ms:
                enemy_count = len(_get_aggro_enemy_ids())
                ConsoleLog(
                    f"{side_label} Aggro Ball Wait",
                    f"Safety timeout reached after {safety_timeout_ms}ms with {enemy_count} aggroed enemies still spread. Continuing anyway.",
                    Py4GW.Console.MessageType.Warning,
                )
                break
    finally:
        in_waiting_routine = False
        if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
            yield from build.CastHeartOfShadow()


def WaitForBall(bot: Botting, side_label: str, cycle_timeout: int = 150):
    yield from _wait_for_aggro_ball(bot, side_label, cycle_timeout)


def _on_death(bot: Botting):
    yield from Routines.Yield.wait(10000)
    fsm = bot.config.FSM
    if Map.GetMapID() == JAGA_MORAINE:
        fsm.jump_to_state_by_name("[H]Reset Farm Loop_12")
    else:
        fsm.jump_to_state_by_name("[H]Town Routines_2")
    fsm.resume()
    yield


def on_death(bot: Botting):
    ConsoleLog("Death detected", "Player Died - Run Failed, Restarting...", Py4GW.Console.MessageType.Notice)
    ActionQueueManager().ResetAllQueues()
    fsm = bot.config.FSM
    fsm.pause()
    fsm.AddManagedCoroutine("OnDeath", _on_death(bot))


in_waiting_routine = False
finished_routine = False
stuck_counter = 0
stuck_timer = ThrottledTimer(5000)
stuck_timer.Start()
BJORA_MARCHES = Map.GetMapIDByName("Bjora Marches")
JAGA_MORAINE = Map.GetMapIDByName("Jaga Moraine")
movement_check_timer = ThrottledTimer(3000)
old_player_position = (0, 0)
in_killing_routine = False
last_waypoint_distance = 0.0
last_header_signature: tuple[int, str] | None = None
last_header_change_ms = 0


def _get_current_header_signature(bot: Botting) -> tuple[int, str] | None:
    fsm = bot.config.FSM
    current_state_number = fsm.get_current_state_number()
    if current_state_number <= 0:
        return None

    state_names = fsm.get_state_names()
    current_index = current_state_number - 1
    if current_index < 0 or current_index >= len(state_names):
        return None

    for index in range(current_index, -1, -1):
        state_name = state_names[index]
        if state_name.startswith("[H]"):
            return index, state_name

    return None


def _refresh_header_progress_timer(bot: Botting) -> None:
    global last_header_signature, last_header_change_ms

    current_signature = _get_current_header_signature(bot)
    now_ms = Utils.GetBaseTimestamp()

    if current_signature != last_header_signature:
        last_header_signature = current_signature
        last_header_change_ms = now_ms


def _get_ms_since_last_header_change(bot: Botting) -> int:
    _refresh_header_progress_timer(bot)
    if last_header_change_ms <= 0:
        return 0
    return max(0, Utils.GetBaseTimestamp() - last_header_change_ms)


def HandleStuckJagaMoraine(bot: Botting):
    global in_waiting_routine, finished_routine, stuck_counter
    global stuck_timer, movement_check_timer, JAGA_MORAINE
    global old_player_position, in_killing_routine, last_waypoint_distance
    global last_header_signature, last_header_change_ms

    log_actions = False
    forced_log = True

    ConsoleLog("Stuck Detection", "Starting Stuck Detection Coroutine.", Py4GW.Console.MessageType.Info, forced_log)
    last_header_signature = None
    last_header_change_ms = 0
    _refresh_header_progress_timer(bot)
    old_player_position = Player.GetXY()
    next_waypoint = _get_next_route_waypoint()
    last_waypoint_distance = Utils.Distance(old_player_position, next_waypoint) if next_waypoint else 0.0

    while True:
        _refresh_header_progress_timer(bot)

        if not Routines.Checks.Map.MapValid():
            ConsoleLog("HandleStuck", "Map is not valid, halting...", Py4GW.Console.MessageType.Debug, forced_log)
            yield from Routines.Yield.wait(1000)
            return

        if Agent.IsDead(Player.GetAgentID()):
            ConsoleLog("HandleStuck", "Player is dead, exiting stuck handler.", Py4GW.Console.MessageType.Debug, forced_log)
            yield from Routines.Yield.wait(1000)
            return

        build: BuildMgr = bot.config.build_handler
        ms_since_last_header_change = _get_ms_since_last_header_change(bot)
        if ms_since_last_header_change > 10 * 60 * 1000:
            ConsoleLog(
                "HandleStuck",
                "No header progress for more than 10 minutes, force resigning.",
                Py4GW.Console.MessageType.Debug,
                forced_log,
            )
            stuck_counter = 0
            if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
                _set_build_stuck_signal(build, stuck_counter)
            Player.SendChatCommand("resign")
            yield from Routines.Yield.wait(500)
            return

        if in_waiting_routine or finished_routine or in_killing_routine:
            stuck_counter = 0
            if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
                _set_build_stuck_signal(build, stuck_counter)
            stuck_timer.Reset()
            old_player_position = Player.GetXY()
            next_waypoint = _get_next_route_waypoint()
            last_waypoint_distance = Utils.Distance(old_player_position, next_waypoint) if next_waypoint else 0.0
            yield from Routines.Yield.wait(1000)
            continue

        if Map.GetMapID() == JAGA_MORAINE:
            if movement_check_timer.IsExpired():
                current_player_pos = Player.GetXY()
                next_waypoint = _get_next_route_waypoint()
                waypoint_distance = Utils.Distance(current_player_pos, next_waypoint) if next_waypoint else 0.0
                moved_distance = Utils.Distance(old_player_position, current_player_pos)
                made_waypoint_progress = (
                    next_waypoint is not None and last_waypoint_distance > 0 and waypoint_distance <= (last_waypoint_distance - STUCK_PROGRESS_DELTA)
                )

                ConsoleLog(
                    "HandleStuck",
                    (
                        f"Checking movement. Old pos: {old_player_position}, Current pos: {current_player_pos}, "
                        f"Moved: {moved_distance:.1f}, Next waypoint: {next_waypoint}, "
                        f"Waypoint distance: {waypoint_distance:.1f}, Last waypoint distance: {last_waypoint_distance:.1f}"
                    ),
                    Py4GW.Console.MessageType.Debug,
                    log_actions,
                )

                if moved_distance < STUCK_MOVEMENT_DELTA and not made_waypoint_progress:
                    stuck_counter += 1
                    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
                        _set_build_stuck_signal(build, stuck_counter)

                    recovered_with_hos = False
                    if len(_get_aggro_enemy_ids(Range.Spellcast.value)) > 0:
                        recovered_with_hos = bool((yield from _cast_stuck_recovery_heart_of_shadow(bot)))

                    if not recovered_with_hos and stuck_timer.IsExpired():
                        ConsoleLog("HandleStuck", "Player is stuck, sending /stuck command.", Py4GW.Console.MessageType.Warning, forced_log)
                        Player.SendChatCommand("stuck")
                        stuck_timer.Reset()
                else:
                    stuck_counter = 0
                    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
                        _set_build_stuck_signal(build, stuck_counter)

                old_player_position = current_player_pos
                last_waypoint_distance = waypoint_distance
                movement_check_timer.Reset()

            if stuck_counter >= 10:
                ConsoleLog("HandleStuck", "Unrecoverable stuck detected, force resigning.", Py4GW.Console.MessageType.Error, forced_log)
                stuck_counter = 0
                if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
                    _set_build_stuck_signal(build, stuck_counter)
                Player.SendChatCommand("resign")
                yield from Routines.Yield.wait(500)
                return
        else:
            ConsoleLog("HandleStuck", "Not in Jaga Moraine, halting.", Py4GW.Console.MessageType.Info, forced_log)
            yield from Routines.Yield.wait(1000)
            return

        yield from Routines.Yield.wait(500)


bot.SetMainRoutine(create_bot_routine)


def tooltip():
    PyImGui.begin_tooltip()

    title_color = Color(255, 200, 100, 255)
    ImGui.push_font("Regular", 20)
    PyImGui.text_colored("Yet Another Vaettir Bot (Y.A.V.B) 2.5", title_color.to_tuple_normalized())
    ImGui.pop_font()
    PyImGui.spacing()
    PyImGui.separator()

    PyImGui.text("YAVB 2.0 with shared inventory handling wired in.")
    PyImGui.spacing()

    PyImGui.text_colored("Features:", title_color.to_tuple_normalized())
    PyImGui.bullet_text("Preserves the original 2.0 Botting FSM and route")
    PyImGui.bullet_text("Uses LootConfig, InventoryConfig, and BuyConfig")
    PyImGui.bullet_text("Merchant visit is only done when needed")
    PyImGui.bullet_text("Keeps birthday cupcake restock in town")
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


def main():
    bot.Update()
    projects_path = Py4GW.Console.get_projects_path()
    widgets_path = projects_path + "\\Widgets\\Config\\textures\\"
    bot.UI.draw_window(icon_path=widgets_path + "YAVB 2.0 mascot.png")


if __name__ == "__main__":
    main()
