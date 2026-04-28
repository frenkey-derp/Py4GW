import json
import math
import os

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
)
from Py4GWCoreLib import ThrottledTimer, Map, Player
from Py4GWCoreLib.BuildMgr import BuildMgr
from Py4GWCoreLib.Builds.Assassin.A_Me.SF_Ass_vaettir import SF_Ass_vaettir
from Py4GWCoreLib.Builds.Mesmer.Me_A.SF_Mes_vaettir import SF_Mes_vaettir
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.enums import ModelID, Range, TitleID
from Py4GWCoreLib.enums_src.Item_enums import ItemAction, ItemType
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.BuyConfig import BuyConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.InventoryConfig import InventoryConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.LootConfig import LootConfig
from Sources.frenkeyLib.ItemHandling.InventoryBT import InventoryBT
from Sources.frenkeyLib.ItemHandling.UIManagerExtensions import UIManagerExtensions

from typing import List, Tuple


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

bot = Botting("YAVB 2.5 - InventoryBT")
stop_bot_after_cleanup = False


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
        entry.action == ItemAction.Sell_To_Merchant
        for entry in preview_entries
    )


def _needs_merchant_visit() -> bool:
    return _has_pending_merchant_sales() or _needs_buy_restock()


def _needs_inventory_management(bot: Botting) -> bool:
    free_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
    leave_empty_slots = bot.Properties.Get("leave_empty_inventory_slots", "value")

    if free_slots < leave_empty_slots:
        return True

    return _needs_buy_restock()


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


def _can_free_slots_in_town() -> bool:
    town_slot_actions = {
        ItemAction.Stash,
        ItemAction.Sell_To_Merchant,
        ItemAction.Sell_To_Trader,
    }

    preview_entries = InventoryBT.Preview(InventoryConfig())
    return any(
        entry.action in town_slot_actions
        for entry in preview_entries
    )


def _open_xunlai_window(timeout_ms: int = 5000):
    start_time = Utils.GetBaseTimestamp()
    while not Inventory.IsStorageOpen():
        Inventory.OpenXunlaiWindow()
        yield from Routines.Yield.wait(250)
        if Utils.GetBaseTimestamp() - start_time >= timeout_ms:
            break


def _open_merchant_window(timeout_ms: int = 8000):
    yield from Routines.Yield.Movement.FollowPath([MERCHANT_XY], timeout=15000)

    start_time = Utils.GetBaseTimestamp()
    while not UIManagerExtensions.IsMerchantWindowOpen():
        yield from Routines.Yield.Agents.TargetNearestNPCXY(MERCHANT_XY[0], MERCHANT_XY[1], 300)
        if Player.GetTargetID() != 0:
            yield from Routines.Yield.Player.InteractTarget()
        yield from Routines.Yield.wait(500)
        if Utils.GetBaseTimestamp() - start_time >= timeout_ms:
            break


def _run_inventory_pass(*, tolerate_failure: bool = True, max_ticks: int = 80, settle_ticks: int = 3):
    runner = InventoryBT(InventoryConfig())
    success_streak = 0
    
    planned_actions = runner.Preview()
    if not planned_actions or all(entry.action is None or entry.action == ItemAction.NONE for entry in planned_actions):
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
    if not UIManagerExtensions.IsMerchantWindowOpen():
        return

    for entry in BuyConfig().get_entries():
        if entry.quantity <= 0:
            continue

        current_quantity = _current_buy_entry_quantity(entry)
        needed_quantity = max(0, int(entry.quantity) - current_quantity)
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
            yield from Routines.Yield.wait(100)


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
        reserved_slots = 1 if _needs_reserved_salvage_slot() else 0
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

        if not inventory_actions_remaining and not loot_remaining:
            return

        if inventory_actions_remaining:
            _reset_runtime_item_state()
            yield from _run_inventory_pass(tolerate_failure=True, max_ticks=30, settle_ticks=2)

        loot_remaining = _has_loot_available()
        inventory_actions_remaining = _has_explorable_inventory_actions()
        if not inventory_actions_remaining and not loot_remaining:
            return

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

    ConsoleLog("Inventory Handling", "Post-kill loot/inventory loop reached safety limit.", Py4GW.Console.MessageType.Warning)


def HandleSharedInventory(bot: Botting):
    _load_shared_configs()
    _reset_runtime_item_state()

    yield from _open_xunlai_window()
    yield from _run_inventory_pass(tolerate_failure=True)

    if _needs_merchant_visit():
        yield from _open_merchant_window()
        if UIManagerExtensions.IsMerchantWindowOpen():
            yield from _run_inventory_pass(tolerate_failure=True)
            yield from _restock_buy_config()

    yield


def create_bot_routine(bot: Botting) -> None:
    TownRoutines(bot)
    TraverseBjoraMarches(bot)
    JagaMoraineFarmRoutine(bot)
    ResetFarmLoop(bot)


def InitializeBot(bot: Botting) -> None:
    condition = lambda: on_death(bot)
    bot.Events.OnDeathCallback(condition)
    _load_shared_configs()
    _reset_runtime_item_state()
    bot.States.AddHeader("Initialize Bot")
    bot.Properties.Disable("auto_inventory_management")
    bot.Properties.Disable("auto_loot")
    bot.Properties.Disable("hero_ai")
    bot.Properties.Enable("build_ticker")
    bot.Properties.Disable("pause_on_danger")
    bot.Properties.Enable("halt_on_death")
    bot.Properties.Set("movement_timeout", value=-1)
    bot.Properties.Enable("identify_kits")
    bot.Properties.Enable("salvage_kits")


def TownRoutines(bot: Botting) -> None:
    bot.States.AddHeader("Town Routines")
    bot.Map.Travel(target_map_id=650)
    InitializeBot(bot)
    bot.States.AddCustomState(lambda: EquipSkillBar(bot), "Equip SkillBar")
    HandleInventory(bot)
    bot.States.AddHeader("Exit to Bjora Marches")
    bot.Party.SetHardMode(True)
    bot.Properties.Enable("birthday_cupcake")
    bot.Move.XYAndExitMap(-26375, 16180, target_map_id=482)


def TraverseBjoraMarches(bot: Botting) -> None:
    bot.States.AddHeader("Traverse Bjora Marches")
    bot.Player.SetTitle(TitleID.Norn.value)
    path_points_to_traverse_bjora_marches: List[Tuple[float, float]] = [
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
    bot.Move.FollowPathAndExitMap(path_points_to_traverse_bjora_marches, target_map_id=546)


def JagaMoraineFarmRoutine(bot: Botting) -> None:
    def _follow_and_wait(path_points: List[Tuple[float, float]], wait_state_name: str, cycle_timeout: int = 150):
        bot.Move.FollowPath(path_points)
        bot.States.AddCustomState(lambda: WaitForBall(bot, wait_state_name, cycle_timeout), f"Wait for {wait_state_name}")

    bot.States.AddHeader("Jaga Moraine Farm Routine")
    InitializeBot(bot)
    bot.Properties.Disable("birthday_cupcake")
    bot.States.AddCustomState(lambda: AssignBuild(bot), "Assign Build")
    bot.Move.XY(13372.44, -20758.50)
    bot.Dialogs.AtXY(13367, -20771, 0x84)
    bot.States.AddManagedCoroutine("HandleStuckJagaMoraine", lambda: HandleStuckJagaMoraine(bot))

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
    bot.Move.FollowPath(path_points_to_killing_spot)
    bot.Properties.ResetTodefault("movement_tolerance", field="value")
    bot.States.AddHeader("Kill Enemies")
    bot.States.AddCustomState(lambda: KillEnemies(bot), "Kill Enemies")
    bot.Properties.Disable("build_ticker")
    bot.States.RemoveManagedCoroutine("HandleStuckJagaMoraine")
    bot.States.AddHeader("Loot Items")
    bot.States.AddCustomState(ProcessLootAndInventory, "Loot And Inventory")
    bot.States.AddCustomState(lambda: NeedsInventoryManagement(bot), "Needs Inventory Management")
    bot.Properties.Disable("birthday_cupcake")
    bot.Move.XYAndExitMap(15850, -20550, target_map_id=482)


def NeedsInventoryManagement(bot: Botting):
    global stop_bot_after_cleanup

    if stop_bot_after_cleanup:
        stop_bot_after_cleanup = False
        bot.Stop()
        yield
        return

    free_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
    salvage_reserve_needed = _needs_reserved_salvage_slot()
    if salvage_reserve_needed and free_slots <= 1:
        Player.SendChatCommand("resign")
        yield from Routines.Yield.wait(500)
        yield
        return

    if _needs_inventory_management(bot):
        Player.SendChatCommand("resign")
        yield from Routines.Yield.wait(500)
    yield


def ResetFarmLoop(bot: Botting) -> None:
    bot.States.AddHeader("Reset Farm Loop")
    bot.Move.XYAndExitMap(-20300, 5600, target_map_id=546)
    bot.States.JumpToStepName("[H]Jaga Moraine Farm Routine_6")


def KillEnemies(bot: Botting):
    global in_killing_routine, finished_routine

    in_killing_routine = True
    finished_routine = False
    build = bot.config.build_handler
    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
        build.SetKillingRoutine(True)
        build.SetRoutineFinished(False)

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

        yield from Routines.Yield.wait(1000)
        enemy_array = Routines.Agents.GetFilteredEnemyArray(player_pos[0], player_pos[1], Range.Spellcast.value)

    in_killing_routine = False
    finished_routine = True
    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
        build.SetKillingRoutine(False)
        build.SetRoutineFinished(True)

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


def HandleInventory(bot: Botting) -> None:
    bot.States.AddHeader("Inventory Handling")
    bot.States.AddCustomState(lambda: HandleSharedInventory(bot), "Shared Inventory Handling")
    bot.Items.Restock.BirthdayCupcake()


def _wait_for_aggro_ball(bot: Botting, side_label: str, cycle_timeout: int = 150):
    global in_waiting_routine

    ConsoleLog(
        f"Waiting for {side_label} Aggro Ball",
        "Waiting for enemies to ball up.",
        Py4GW.Console.MessageType.Info,
    )

    in_waiting_routine = True
    elapsed = 0
    build = bot.config.build_handler

    try:
        while elapsed < cycle_timeout:
            yield from Routines.Yield.wait(100)
            elapsed += 1

            if Agent.IsDead(Player.GetAgentID()):
                ConsoleLog(
                    f"{side_label} Aggro Ball Wait",
                    "Player is dead, exiting wait.",
                    Py4GW.Console.MessageType.Warning,
                )
                yield
                return

            px, py = Player.GetXY()
            enemies_ids = Routines.Agents.GetFilteredEnemyArray(px, py, Range.Earshot.value)

            all_in_adjacent = True
            for enemy_id in enemies_ids:
                enemy = Agent.GetAgentByID(enemy_id)
                if enemy is None:
                    continue
                dx = enemy.pos.x - px
                dy = enemy.pos.y - py
                if dx * dx + dy * dy > (Range.Adjacent.value ** 2):
                    all_in_adjacent = False
                    break

            if all_in_adjacent:
                ConsoleLog(
                    f"{side_label} Aggro Ball Wait",
                    "Enemies balled up successfully.",
                    Py4GW.Console.MessageType.Info,
                )
                break
        else:
            ConsoleLog(
                f"{side_label} Aggro Ball Wait",
                f"Timeout reached {cycle_timeout * 100}ms, exiting without ball.",
                Py4GW.Console.MessageType.Warning,
            )
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
        fsm.jump_to_state_by_name("[H]Reset Farm Loop_1")
    else:
        fsm.jump_to_state_by_name("[H]Town Routines_1")
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


def HandleStuckJagaMoraine(bot: Botting):
    global in_waiting_routine, finished_routine, stuck_counter
    global stuck_timer, movement_check_timer, JAGA_MORAINE
    global old_player_position, in_killing_routine

    log_actions = False
    forced_log = True

    ConsoleLog("Stuck Detection", "Starting Stuck Detection Coroutine.", Py4GW.Console.MessageType.Info, forced_log)

    while True:
        if not Routines.Checks.Map.MapValid():
            ConsoleLog("HandleStuck", "Map is not valid, halting...", Py4GW.Console.MessageType.Debug, forced_log)
            yield from Routines.Yield.wait(1000)
            return

        if Agent.IsDead(Player.GetAgentID()):
            ConsoleLog("HandleStuck", "Player is dead, exiting stuck handler.", Py4GW.Console.MessageType.Debug, forced_log)
            yield from Routines.Yield.wait(1000)
            return

        build: BuildMgr = bot.config.build_handler
        instance_time = Map.GetInstanceUptime() / 1000
        if instance_time > 10 * 60:
            ConsoleLog("HandleStuck", "Instance time exceeded 7 minutes, force resigning.", Py4GW.Console.MessageType.Debug, forced_log)
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
            yield from Routines.Yield.wait(1000)
            continue

        if Map.GetMapID() == JAGA_MORAINE:
            if stuck_timer.IsExpired():
                ConsoleLog("HandleStuck", "Issuing scheduled /stuck command.", Py4GW.Console.MessageType.Debug, log_actions)
                Player.SendChatCommand("stuck")
                stuck_timer.Reset()

            if movement_check_timer.IsExpired():
                current_player_pos = Player.GetXY()
                ConsoleLog(
                    "HandleStuck",
                    f"Checking movement. Old pos: {old_player_position}, Current pos: {current_player_pos}",
                    Py4GW.Console.MessageType.Debug,
                    log_actions,
                )

                if old_player_position == current_player_pos:
                    ConsoleLog("HandleStuck", "Player is stuck, sending /stuck command.", Py4GW.Console.MessageType.Warning, forced_log)
                    Player.SendChatCommand("stuck")
                    stuck_counter += 1
                    if isinstance(build, (SF_Ass_vaettir, SF_Mes_vaettir)):
                        _set_build_stuck_signal(build, stuck_counter)
                    stuck_timer.Reset()
                else:
                    old_player_position = current_player_pos
                    stuck_counter = 0

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
