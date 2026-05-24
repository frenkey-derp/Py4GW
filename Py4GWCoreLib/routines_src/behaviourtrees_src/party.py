"""
BT routines file notes
======================

This file is both:
- part of the public BT grouped routine surface
- a discovery source for higher-level tooling
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple, Optional

from PyParty import HenchmanPartyMember, HeroPartyMember

from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.shared_memory_src.AccountStruct import AccountStruct
from Py4GWCoreLib.Skillbar import SkillBar
from Py4GWCoreLib.enums_src.Hero_enums import HeroType
from Py4GWCoreLib.enums_src.Multiboxing_enums import SharedCommandType
from Py4GWCoreLib.native_src.context.AgentContext import AgentLivingStruct

from ...Map import Map
from ...Party import Party
from ...Player import Player
from ...Py4GWcorelib import ConsoleLog, Console
from ...py4gwcorelib_src.BehaviorTree import BehaviorTree
from .composite import BTComposite


def _log(source: str, message: str, *, log: bool = False, message_type=Console.MessageType.Info) -> None:
    ConsoleLog(source, message, message_type, log=log)


def _fail_log(source: str, message: str, message_type=Console.MessageType.Warning) -> None:
    ConsoleLog(source, message, message_type, log=True)


def _normalized(name : str) -> str:
    return str(name or '').strip().lower().split('[')[0].strip()

HenchmanEntry = NamedTuple("HenchmanEntry", [
    ("agent_id", int),
    ("primary", int),
    ("level", int),
    ("name", str),
    ("name_normalized", str),
]) 

HeroeEntry = NamedTuple("HeroEntry", [
    ("hero_id", HeroType),
    ("template", str),
    ("name", str),
    ("name_normalized", str),
])

PlayerEntry = NamedTuple("PlayerEntry", [
    ("character_name", str),
    ("character_name_normalized", str),
    ("account_email", str),
    ("account", Optional[AccountStruct]),
    ("template", Optional[str]),
    ("is_on_same_map", bool),
    ("login_number", Optional[int]),
])

class BTParty:
    """
    Public BT helper group for party-management routines.

    Meta:
      Expose: true
      Audience: advanced
      Display: Party
      Purpose: Group public BT routines related to party composition and party control.
      UserDescription: Built-in BT helper group for party-management actions.
      Notes: Public `PascalCase` methods in this class are discovery candidates when marked exposed.
    """

    @staticmethod
    def IsPartyLeader(log: bool = False) -> BehaviorTree:
        """
        Build a condition tree that succeeds when the local player is party leader.

        Meta:
          Expose: true
          Audience: beginner
          Display: Is Party Leader
          Purpose: Check whether the local player currently leads the party.
          UserDescription: Use this when a step should only run for the party leader.
          Notes: Returns failure when not party leader.
        """

        def _is_party_leader() -> bool:
            result = bool(Party.IsPartyLeader())
            _log("BTParty.IsPartyLeader", f"is_party_leader={result}", log=log)
            return result

        return BehaviorTree(
            BehaviorTree.ConditionNode(
                name="IsPartyLeader",
                condition_fn=_is_party_leader,
            )
        )

    @staticmethod
    def LeaveParty(log: bool = False, aftercast_ms: int = 250) -> BehaviorTree:
        """
        Build an action tree that leaves the current party.

        Meta:
          Expose: true
          Audience: beginner
          Display: Leave Party
          Purpose: Leave the current party.
          UserDescription: Use this when you want to leave party immediately.
          Notes: Executes instantly and returns success once dispatched.
        """

        def _leave_party() -> BehaviorTree.NodeState:
            Party.LeaveParty()
            _log("BTParty.LeaveParty", "LeaveParty dispatched.", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="LeaveParty",
                action_fn=_leave_party,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def FlagHero(hero_position: int, x: float, y: float, log: bool = False, aftercast_ms: int = 125) -> BehaviorTree:
        """
        Build an action tree that flags one hero at a world coordinate.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Flag Hero
          Purpose: Flag a single local hero at a given position.
          UserDescription: Use this when you need to place one hero at a specific flag position.
          Notes: The hero selector uses party position and resolves to the current hero agent id at runtime.
        """

        def _flag_hero() -> BehaviorTree.NodeState:
            resolved_position = int(hero_position)
            if resolved_position <= 0:
                _fail_log(
                    "BTParty.FlagHero",
                    f"Failed to flag hero: invalid party position {resolved_position}.",
                )
                return BehaviorTree.NodeState.FAILURE

            hero_agent_id = int(Party.Heroes.GetHeroAgentIDByPartyPosition(resolved_position) or 0)
            if hero_agent_id <= 0:
                _fail_log(
                    "BTParty.FlagHero",
                    f"Failed to flag hero: no hero found at party position {resolved_position}.",
                )
                return BehaviorTree.NodeState.FAILURE

            Party.Heroes.FlagHero(hero_agent_id, float(x), float(y))
            _log(
                "BTParty.FlagHero",
                f"FlagHero party_position={resolved_position}, agent_id={hero_agent_id}, x={x:.2f}, y={y:.2f}",
                log=log,
            )
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="FlagHero",
                action_fn=_flag_hero,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def FlagAllHeroes(x: float, y: float, log: bool = False, aftercast_ms: int = 125) -> BehaviorTree:
        """
        Build an action tree that flags all heroes at a world coordinate.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Flag All Heroes
          Purpose: Flag all local heroes at a given position.
          UserDescription: Use this when you need to place all heroes at one flag position.
          Notes: Operates on local party heroes only.
        """

        def _flag_all_heroes() -> BehaviorTree.NodeState:
            Party.Heroes.FlagAllHeroes(float(x), float(y))
            _log("BTParty.FlagAllHeroes", f"FlagAllHeroes x={x:.2f}, y={y:.2f}", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="FlagAllHeroes",
                action_fn=_flag_all_heroes,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def FlagHeroesFromList(
        hero_positions: Sequence[int | str] | None,
        x: float,
        y: float,
        flag_all: bool = False,
        log: bool = False,
        aftercast_ms: int = 125,
    ) -> BehaviorTree:
        """
        Build a composite tree that flags selected heroes at a world coordinate.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Flag Heroes From List
          Purpose: Flag several local heroes in sequence using party positions, or all heroes with an explicit flag.
          UserDescription: Use this when a step should flag one hero, many heroes, or all heroes through one shared entrypoint.
          Notes: When `flag_all` is true, the composite collapses to the all-heroes flag routine and ignores `hero_positions`.
        """
        normalized_positions: list[int] = []
        if flag_all:
            return BTParty.FlagAllHeroes(x=float(x), y=float(y), log=log, aftercast_ms=aftercast_ms)

        for raw_value in hero_positions or []:
            if isinstance(raw_value, str):
                stripped_value = raw_value.strip()
                if not stripped_value:
                    continue
                try:
                    resolved_position = int(stripped_value)
                except ValueError as exc:
                    raise ValueError(f"Invalid hero position value {raw_value!r}; expected positive integer.") from exc
            else:
                resolved_position = int(raw_value)

            if resolved_position <= 0:
                raise ValueError(f"Invalid hero position value {raw_value!r}; expected positive integer.")
            normalized_positions.append(resolved_position)

        if not normalized_positions:
            raise ValueError("FlagHeroesFromList requires at least one hero position unless flag_all is true.")

        return BTComposite.Sequence(
            *[
                BTParty.FlagHero(
                    hero_position=hero_position,
                    x=float(x),
                    y=float(y),
                    log=log,
                    aftercast_ms=aftercast_ms,
                )
                for hero_position in normalized_positions
            ],
            name="FlagHeroesFromList",
        )

    @staticmethod
    def UnflagAllHeroes(log: bool = False, aftercast_ms: int = 125) -> BehaviorTree:
        """
        Build an action tree that clears all local hero flags.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Unflag All Heroes
          Purpose: Remove all local hero flags.
          UserDescription: Use this to clear hero flags and resume default behavior.
          Notes: Operates on local party heroes only.
        """

        def _unflag_all_heroes() -> BehaviorTree.NodeState:
            Party.Heroes.UnflagAllHeroes()
            _log("BTParty.UnflagAllHeroes", "UnflagAllHeroes dispatched.", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="UnflagAllHeroes",
                action_fn=_unflag_all_heroes,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def SetupParty(
        henchmen : Optional[Sequence[int | str]] = None,
        heroes : Optional[Sequence[int | HeroType | str | tuple[int | HeroType | str, Optional[str]]]] = None,
        players : Optional[Sequence[str | int | tuple[str | int, Optional[str]]]] = None,
        account_heroes : Optional[Sequence[tuple[str, Sequence[tuple[int | HeroType | str, Optional[str]]]]]] = None,
        require_outpost: bool = True,
        leave_if_no_leader: bool = True,
        timeout_ms: int = 15000,
        poll_interval_ms: int = 100,
        aftercast_ms: int = 150,
        log: bool = False,
        ) -> BehaviorTree:

            children: list[BehaviorTree | BehaviorTree.Node] = []
                        
            if not Party.IsPartyLeader():
                if leave_if_no_leader:
                    children.append(
                        BehaviorTree.ActionNode(
                            name="LeavePartyIfNotLeader",
                            action_fn=lambda _node=None: (
                                ConsoleLog("BTParty.LoadParty", "Local player is not party leader, leaving party.", log=log),
                                Party.LeaveParty(),
                                BehaviorTree.NodeState.SUCCESS,
                            )[-1],
                        )
                    )
                else:
                    children.append(
                        BehaviorTree.FailerNode(
                            name="FailIfNotLeader"
                        )
                    )
                    
            if require_outpost and not Map.IsOutpost():
                children.append(
                    BehaviorTree.FailerNode(
                        name="FailIfNotInOutpost",
                    )
                )
            
            
            if henchmen:
                ConsoleLog("SetupPartyFormation", f'Setting up henchmen: {henchmen}', log=log)
                children.append(BTParty.Henchmen.SetupHenchmen(henchmen, log=log))
            else:
                ConsoleLog("SetupPartyFormation", 'No henchmen to set up.', log=log)
                
            if heroes:
                ConsoleLog("SetupPartyFormation", f'Setting up heroes: {heroes}', log=log)
                children.append(BTParty.Heroes.SetupHeroes(heroes, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupPartyFormation", 'No heroes to set up.', log=log)
                
            if players:
                ConsoleLog("SetupPartyFormation", f'Setting up players: {players}', log=log)
                children.append(BTParty.Multiboxing.SetupPlayers(players, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupPartyFormation", 'No players to set up.', log=log)
                
            if account_heroes:
                for account_email, account_hero_list in account_heroes:
                    ConsoleLog("SetupPartyFormation", f'Setting up heroes for account {account_email}: {account_hero_list}', log=log)
                    children.append(BTParty.Multiboxing.RequestHeroSetup(account_email, account_hero_list, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="SetupPartyFormation",
                    children=children
                )
            )

    @staticmethod
    def WaitForPartyLoaded(
        expected_heroes: int = 0,
        expected_henchmen: int = 0,
        timeout_ms: int = 10000,
        poll_interval_ms: int = 200,
        require_party_loaded_flag: bool = True,
        log: bool = False,
    ) -> BehaviorTree:
        """
        Build a wait tree that blocks until the party reaches expected counts.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Wait For Party Loaded
          Purpose: Wait until party-load state and expected hero/henchman counts are reached.
          UserDescription: Use this to wait after party composition changes.
          Notes: Returns failure on timeout.
        """

        expected_heroes = max(0, int(expected_heroes))
        expected_henchmen = max(0, int(expected_henchmen))
        timeout_ms = max(0, int(timeout_ms))
        poll_interval_ms = max(10, int(poll_interval_ms))

        state = {"started": False}

        def _is_loaded() -> bool:
            heroes = int(Party.GetHeroCount() or 0)
            henchmen = int(Party.GetHenchmanCount() or 0)
            loaded_flag = bool(Party.IsPartyLoaded()) if require_party_loaded_flag else True
            result = loaded_flag and heroes >= expected_heroes and henchmen >= expected_henchmen
            if result:
                _log(
                    "BTParty.WaitForPartyLoaded",
                    f"Party ready heroes={heroes}/{expected_heroes}, henchmen={henchmen}/{expected_henchmen}",
                    log=log,
                )
            elif not state["started"]:
                state["started"] = True
            return result

        return BehaviorTree(
            BehaviorTree.WaitUntilNode(
                name="WaitForPartyLoaded",
                condition_fn=_is_loaded,
                throttle_interval_ms=poll_interval_ms,
                timeout_ms=timeout_ms,
            )
        )

    @staticmethod
    def Resign(log: bool = False, aftercast_ms: int = 250) -> BehaviorTree:
        """
        Build an action tree that sends resign command.

        Meta:
          Expose: true
          Audience: beginner
          Display: Resign
          Purpose: Trigger resign command for the local player.
          UserDescription: Use this when you want to resign the current run.
          Notes: This routine dispatches the command and returns success.
        """

        def _resign() -> BehaviorTree.NodeState:
            Player.SendChatCommand("resign")
            _log("BTParty.Resign", "Resign dispatched.", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="Resign",
                action_fn=_resign,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def SetTitle(title_id: int, log: bool = False, aftercast_ms: int = 250) -> BehaviorTree:
        """
        Build an action tree that sets the local player's active title.

        Meta:
          Expose: true
          Audience: beginner
          Display: Set Title
          Purpose: Set the active player title by title id.
          UserDescription: Use this when a route or setup needs a specific title active.
          Notes: Dispatches the title change and returns success immediately.
        """

        def _set_title() -> BehaviorTree.NodeState:
            Player.SetActiveTitle(int(title_id))
            _log("BTParty.SetTitle", f"Set title id={int(title_id)}.", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="SetTitle",
                action_fn=_set_title,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def ForceHeroState(behavior: int, log: bool = False, aftercast_ms: int = 125) -> BehaviorTree:
        """
        Build an action tree that sets every current hero to a behavior mode.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Force Hero State
          Purpose: Set all local heroes to fight, guard, or avoid behavior.
          UserDescription: Use this when you want to force the whole hero party into one behavior mode.
          Notes: Behavior values are the native hero behavior ids 0, 1, and 2.
        """

        def _force_hero_state() -> BehaviorTree.NodeState:
            behavior_value = int(behavior)
            if behavior_value not in (0, 1, 2):
                _fail_log("BTParty.ForceHeroState", f"Failed to update hero behavior: invalid behavior value {behavior_value}.")
                return BehaviorTree.NodeState.FAILURE
            used = 0
            for hero in Party.GetHeroes():
                hero_agent_id = getattr(hero, "agent_id", 0)
                if hero_agent_id:
                    Party.Heroes.SetHeroBehavior(hero_agent_id, behavior_value)
                    used += 1
            _log("BTParty.ForceHeroState", f"Updated {used} hero behavior(s).", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="ForceHeroState",
                action_fn=_force_hero_state,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def DropBundle(log: bool = False) -> BehaviorTree:
        """
        Build an action tree that drops the currently held bundle.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Drop Bundle
          Purpose: Press the configured drop-item control action used to drop a held bundle.
          UserDescription: Use this when a route needs to release a bundle before continuing.
          Notes: Uses the native drop-item keybind action instead of raw function keys.
        """
        from ...UIManager import UIManager
        from ...enums_src.UI_enums import ControlAction

        def _keydown() -> BehaviorTree.NodeState:
            UIManager.Keydown(ControlAction.ControlAction_DropItem.value, 0)
            _log("BTParty.DropBundle", "Pressed drop-item control action.", log=log)
            return BehaviorTree.NodeState.SUCCESS

        def _keyup() -> BehaviorTree.NodeState:
            UIManager.Keyup(ControlAction.ControlAction_DropItem.value, 0)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name="DropBundle",
                children=[
                    BehaviorTree.ActionNode(
                        name="DropBundleKeyDown",
                        action_fn=_keydown,
                        aftercast_ms=75,
                    ),
                    BehaviorTree.ActionNode(
                        name="DropBundleKeyUp",
                        action_fn=_keyup,
                        aftercast_ms=50,
                    ),
                ],
            )
        )

    @staticmethod
    def AbandonQuest(quest_id: int, log: bool = False, aftercast_ms: int = 250) -> BehaviorTree:
        """
        Build an action tree that abandons a quest by id.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Abandon Quest
          Purpose: Abandon a quest by quest id.
          UserDescription: Use this when a route needs to reset or clear a specific quest.
          Notes: Fails when the quest id is not positive.
        """

        def _abandon_quest() -> BehaviorTree.NodeState:
            qid = int(quest_id)
            if qid <= 0:
                _fail_log("BTParty.AbandonQuest", f"Failed to abandon quest: invalid quest id {qid}.")
                return BehaviorTree.NodeState.FAILURE
            from ...Quest import Quest

            Quest.AbandonQuest(qid)
            _log("BTParty.AbandonQuest", f"Abandoned quest id={qid}.", log=log)
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name="AbandonQuest",
                action_fn=_abandon_quest,
                aftercast_ms=max(0, int(aftercast_ms)),
            )
        )

    @staticmethod
    def WaitForActiveQuest(quest_id: int, timeout_ms: int = 10000, throttle_interval_ms: int = 250, log: bool = False) -> BehaviorTree:
        """
        Build a tree that waits until the requested quest becomes the active quest.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Wait For Active Quest
          Purpose: Wait until a specific quest id is the active quest.
          UserDescription: Use this when a dialog or interaction should be confirmed by checking the active quest id.
          Notes: Succeeds only when the requested quest becomes active before timeout.
        """

        def _wait_for_active_quest() -> BehaviorTree.NodeState:
            from ...Quest import Quest

            if int(Quest.GetActiveQuest() or 0) == int(quest_id):
                _log("BTParty.WaitForActiveQuest", f"Quest {int(quest_id)} is now active.", log=log)
                return BehaviorTree.NodeState.SUCCESS
            return BehaviorTree.NodeState.RUNNING

        return BehaviorTree(
            BehaviorTree.WaitUntilNode(
                name=f"WaitForActiveQuest({int(quest_id)})",
                condition_fn=_wait_for_active_quest,
                throttle_interval_ms=max(1, int(throttle_interval_ms)),
                timeout_ms=max(0, int(timeout_ms)),
            )
        )

    @staticmethod
    def WaitForActiveQuestCleared(quest_id: int, timeout_ms: int = 10000, throttle_interval_ms: int = 250, log: bool = False) -> BehaviorTree:
        """
        Build a tree that waits until the requested quest is no longer the active quest.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Wait For Active Quest Cleared
          Purpose: Wait until a specific quest id is no longer active.
          UserDescription: Use this when quest completion or abandonment should be confirmed by checking that the active quest changed away.
          Notes: Succeeds when the active quest differs from the requested quest before timeout.
        """

        def _wait_for_quest_cleared() -> BehaviorTree.NodeState:
            from ...Quest import Quest

            if int(Quest.GetActiveQuest() or 0) != int(quest_id):
                _log("BTParty.WaitForQuestCleared", f"Quest {int(quest_id)} is no longer active.", log=log)
                return BehaviorTree.NodeState.SUCCESS
            return BehaviorTree.NodeState.RUNNING

        return BehaviorTree(
            BehaviorTree.WaitUntilNode(
                name=f"WaitForQuestCleared({int(quest_id)})",
                condition_fn=_wait_for_quest_cleared,
                throttle_interval_ms=max(1, int(throttle_interval_ms)),
                timeout_ms=max(0, int(timeout_ms)),
            )
        )

    @staticmethod
    def IsQuestInLog(quest_id: int, log: bool = False) -> BehaviorTree:
        """
        Build a condition tree that succeeds when the requested quest id is present in the quest log.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Is Quest In Log
          Purpose: Check whether a specific quest id is currently present in the quest log.
          UserDescription: Use this when a route needs a direct condition check for whether a quest is currently in the quest log.
          Notes: Returns failure when the quest id is not found in the quest log ids.
        """

        def _is_quest_in_log() -> bool:
            from ...Quest import Quest


            quest_log_ids = [int(qid) for qid in (Quest.GetQuestLogIds() or [])]
            result = int(quest_id) in quest_log_ids
            _log("BTParty.IsQuestInLog", f"quest_id={int(quest_id)} in_log={result}", log=log)
            return result

        return BehaviorTree(
            BehaviorTree.ConditionNode(
                name=f"IsQuestInLog({int(quest_id)})",
                condition_fn=_is_quest_in_log,
            )
        )

    @staticmethod
    def IsQuestAbsentFromLog(quest_id: int, log: bool = False) -> BehaviorTree:
        """
        Build a condition tree that succeeds when the requested quest id is absent from the quest log.

        Meta:
          Expose: true
          Audience: intermediate
          Display: Is Quest Absent From Log
          Purpose: Check whether a specific quest id is currently absent from the quest log.
          UserDescription: Use this when a route needs a direct condition check for whether a quest is currently not in the quest log.
          Notes: Returns failure when the quest id is still found in the quest log ids.
        """

        def _is_quest_absent_from_log() -> bool:
            from ...Quest import Quest

            quest_log_ids = [int(qid) for qid in (Quest.GetQuestLogIds() or [])]
            result = int(quest_id) not in quest_log_ids
            _log("BTParty.IsQuestAbsentFromLog", f"quest_id={int(quest_id)} absent_from_log={result}", log=log)
            return result

        return BehaviorTree(
            BehaviorTree.ConditionNode(
                name=f"IsQuestAbsentFromLog({int(quest_id)})",
                condition_fn=_is_quest_absent_from_log,
            )
        )

    
    class Henchmen:
        @staticmethod
        def _get_henchman_entry(agent_or_henchman : AgentLivingStruct | HenchmanPartyMember) -> Optional[HenchmanEntry]:
            name = Agent.GetNameByID(agent_or_henchman.agent_id) or ''
            
            return HenchmanEntry(
                agent_id=agent_or_henchman.agent_id,
                primary=agent_or_henchman.primary if isinstance(agent_or_henchman, AgentLivingStruct) else agent_or_henchman.profession.ToInt(),
                level=agent_or_henchman.level,
                name=name,
                name_normalized=_normalized(name),
            ) if name else None
                
        @staticmethod
        def _get_available_henchmen() -> list[HenchmanEntry]:
            henchmen: list[HenchmanEntry] = []
            for henchman_id in AgentArray.GetAllyArray():
                if Agent.CanBeViewedInPartyWindow(henchman_id) and not Agent.IsPlayer(henchman_id):
                    if (agent := Agent.GetAgentByID(henchman_id)) and (living_agent := agent.GetAsAgentLiving()) and living_agent is not None:
                        if entry := BTParty.Henchmen._get_henchman_entry(living_agent):
                            henchmen.append(entry)
            return henchmen

        @staticmethod
        def _get_henchman(identifier : int | str | Sequence[int], available_henchmen: Sequence[HenchmanEntry]) -> Optional[HenchmanEntry]:        
            if isinstance(identifier, str):
                for henchman in available_henchmen:
                    if henchman.name_normalized == _normalized(identifier):
                        return henchman
            
            if isinstance(identifier, int):
                if (agent := Agent.GetAgentByID(identifier)) and (living_agent := agent.GetAsAgentLiving()) and living_agent is not None:
                    return BTParty.Henchmen._get_henchman_entry(living_agent) 
            
            return None
            
        @staticmethod
        def InviteHenchmen(henchman_ids: Sequence[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _invite() -> BehaviorTree.NodeState:
                available_henchmen = BTParty.Henchmen._get_available_henchmen()
                in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := BTParty.Henchmen._get_henchman_entry(party_henchman)) is not None]
                desired_henchmen: list[HenchmanEntry] = [henchman for identifier in henchman_ids if (henchman := BTParty.Henchmen._get_henchman(identifier, available_henchmen)) is not None]
                
                if len(desired_henchmen) != len(henchman_ids):
                    missing_identifiers = [id for id in henchman_ids if not any((henchman.agent_id == id if isinstance(id, int) else henchman.name_normalized == _normalized(id)) for henchman in desired_henchmen)]
                    ConsoleLog("InviteHenchmen", f'Missing henchmen for identifiers: {missing_identifiers}', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                for henchman in desired_henchmen:
                    if not any(available.agent_id == henchman.agent_id for available in available_henchmen):
                        ConsoleLog("InviteHenchmen", f'Henchman not available to invite, skipping: {henchman.name} (ID: {henchman.agent_id})', log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    if any(henchman.agent_id == party_henchman.agent_id for party_henchman in in_party_henchmen or []):
                        ConsoleLog("InviteHenchmen", f'Henchman already in party, skipping: {henchman.name} (ID: {henchman.agent_id})', log=log)
                        continue
                    
                    else:
                        ConsoleLog("InviteHenchmen", f'Inviting henchman: {henchman.name} (ID: {henchman.agent_id})', log=log)
                        Party.Henchmen.AddHenchman(henchman.agent_id)
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="InviteHenchmen",
                    action_fn=_invite,
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def KickHenchmen(henchman_ids: Sequence[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _kick() -> BehaviorTree.NodeState:
                if len(henchman_ids) == 0:
                    ConsoleLog("KickHenchmen", 'No henchmen specified to kick.', log=log)
                    return BehaviorTree.NodeState.SUCCESS
                
                in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := BTParty.Henchmen._get_henchman_entry(party_henchman)) is not None]
                desired_kick_henchmen: list[HenchmanEntry] = [henchman for identifier in henchman_ids if (henchman := BTParty.Henchmen._get_henchman(identifier, in_party_henchmen)) is not None]
                
                if len(desired_kick_henchmen) != len(henchman_ids):
                    missing_identifiers = [id for id in henchman_ids if not any((henchman.agent_id == id if isinstance(id, int) else henchman.name_normalized == _normalized(id)) for henchman in desired_kick_henchmen)]
                    ConsoleLog("KickHenchmen", f'Missing henchmen for identifiers: {missing_identifiers}', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                for henchman in desired_kick_henchmen:
                    ConsoleLog("KickHenchmen", f'Kicking henchman: {henchman.name} (ID: {henchman.agent_id})', log=log)
                    Party.Henchmen.KickHenchman(henchman.agent_id)
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="KickHenchmen",
                    action_fn=_kick,
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def SetupHenchmen(henchmen : Sequence[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            available_henchmen = BTParty.Henchmen._get_available_henchmen()
            desired_henchmen: list[HenchmanEntry] = [henchman for identifier in henchmen if (henchman := BTParty.Henchmen._get_henchman(identifier, available_henchmen)) is not None]
            
            if len(desired_henchmen) != len(henchmen):
                missing_identifiers = [id for id in henchmen if not any((henchman.agent_id == id if isinstance(id, int) else henchman.name_normalized == _normalized(id)) for henchman in desired_henchmen)]
                ConsoleLog("SetupHenchmen", f'Missing henchmen for identifiers: {missing_identifiers}', log=log)
                return BehaviorTree(
                    BehaviorTree.ActionNode(
                        name="SetupHenchmen",
                        action_fn=lambda _node=None: BehaviorTree.NodeState.FAILURE,
                        aftercast_ms=aftercast_ms,
                    )
                )
            
            in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := BTParty.Henchmen._get_henchman_entry(party_henchman)) is not None]
            henchmen_to_kick: list[int | str] = [henchman.agent_id for henchman in in_party_henchmen if not any(henchman.agent_id == desired.agent_id for desired in desired_henchmen)]
            henchmen_to_add: list[int | str] = [henchman.agent_id for henchman in desired_henchmen if not any(henchman.agent_id == party.agent_id for party in in_party_henchmen)]
            
            
            children: list[BehaviorTree | BehaviorTree.Node] = []
            if henchmen_to_kick:
                ConsoleLog("SetupHenchmen", f'Henchmen to kick: {henchmen_to_kick}', log=log)
                children.append(BTParty.Henchmen.KickHenchmen(henchmen_to_kick, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupHenchmen", 'No henchmen to kick.', log=log)
            
            if henchmen_to_add:
                ConsoleLog("SetupHenchmen", f'Henchmen to add: {henchmen_to_add}', log=log)
                children.append(BTParty.Henchmen.InviteHenchmen(henchmen_to_add, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupHenchmen", 'No henchmen to add.', log=log)

            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="InviteHeroesAndLoadTemplates",
                    children=children,
                )
            )

    class Heroes:
        @staticmethod
        def _get_hero_type(identifier : int | HeroType | str) -> Optional[HeroType]:
            if isinstance(identifier, HeroType):
                return identifier
            
            if isinstance(identifier, int):
                try:
                    return HeroType(identifier)
                except ValueError:
                    return None
            
            if isinstance(identifier, str):
                for hero in HeroType:
                    if _normalized(hero.name) == _normalized(identifier):
                        return hero
            
            return None

        @staticmethod
        def _get_hero_map(heroes : Sequence[int | HeroType | str], log: bool = False) -> list[HeroeEntry]:
            mapped_heroes: list[HeroeEntry] = []
            for hero_identifier in heroes:
                hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                
                if hero_type is not None and BTParty.Heroes._is_hero_available(hero_type):
                    mapped_heroes.append(HeroeEntry(
                        hero_id=hero_type,
                        template='',
                        name=hero_type.name,
                        name_normalized=_normalized(hero_type.name),
                    ))
                else:
                    ConsoleLog("InviteHeroes", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                    return []
                        
            return mapped_heroes

        @staticmethod
        def _is_hero_available(hero_id: HeroType) -> bool:
            # We don't have a way yet to check hero availability before inviting, but we keep this so we can implement it later if we find a way
            return True

        @staticmethod
        def _get_hero_entry(hero : HeroPartyMember) -> Optional[HeroeEntry]:
            hero_id = HeroType(hero.hero_id.GetID() or 0)
            
            return HeroeEntry(
                hero_id=hero_id,
                template='',
                name=hero_id.name,
                name_normalized=_normalized(hero_id.name),
            ) if hero_id else None

        @staticmethod
        def _get_party_heroes(login_number: int) -> list[HeroeEntry]:
            party_heroes: list[HeroeEntry] = []
            for party_hero in Party.GetHeroes() or []:
                if party_hero.owner_player_id == login_number:
                    if (hero_entry := BTParty.Heroes._get_hero_entry(party_hero)) is not None:
                        party_heroes.append(hero_entry)

            return party_heroes
            
        @staticmethod
        def InviteHeroes(heroes : Sequence[int | HeroType | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _invite() -> BehaviorTree.NodeState:
                mapped_heroes = BTParty.Heroes._get_hero_map(heroes, log=log)
                if not mapped_heroes:
                    return BehaviorTree.NodeState.FAILURE
                        
                in_party_heroes =  BTParty.Heroes._get_party_heroes(Player.GetLoginNumber())
                for hero_entry in mapped_heroes:
                    if any(hero_entry.hero_id == party_hero.hero_id for party_hero in in_party_heroes):
                        ConsoleLog("InviteHeroes", f'Hero already in party, skipping: {hero_entry.name} (ID: {hero_entry.hero_id})', log=log)
                        continue
                    else:
                        ConsoleLog("InviteHeroes", f'Inviting hero: {hero_entry.name} (ID: {hero_entry.hero_id})', log=log)
                        Party.Heroes.AddHero(int(hero_entry.hero_id))
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="InviteHeroes",
                    action_fn=lambda _node=None: _invite(),
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def LoadHeroTemplates(heroes : Sequence[tuple[int | HeroType | str, str]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _load_templates() -> BehaviorTree.NodeState:
                for hero_identifier, template in heroes:
                    hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                    
                    if hero_type is None:
                        ConsoleLog("LoadHeroTemplates", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    in_party_heroes =  BTParty.Heroes._get_party_heroes(Player.GetLoginNumber())
                    if not any(hero_type == party_hero.hero_id for party_hero in in_party_heroes):
                        ConsoleLog("LoadHeroTemplates", f'Hero not in party, skipping template load: {hero_type.name} (ID: {hero_type})', log=log)
                        continue
                        
                    ConsoleLog("LoadHeroTemplates", f'Find hero index for template load: {hero_type.name} (ID: {hero_type})', log=log)
                    hero_index = Party.GetHeroIndex(hero_type)
                    
                    if hero_index > 0:
                        ConsoleLog("LoadHeroTemplates", f'Loading template \'{template}\' for hero at index {hero_index}: {hero_type.name} (ID: {hero_type})', log=log)
                        SkillBar.LoadHeroSkillTemplate(hero_index, template)
                        
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="LoadHeroTemplates",
                    action_fn=lambda _node=None: _load_templates(),
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def InviteHeroesAndLoadTemplates(heroes : Sequence[int | HeroType | str | tuple[int | HeroType | str, str]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            heroes_to_invite: list[int | HeroType | str] = []
            heroes_to_load_templates: list[tuple[int | HeroType | str, str]] = []
            
            for hero in heroes:
                if isinstance(hero, tuple) and len(hero) == 2:
                    hero_identifier, template = hero
                    heroes_to_invite.append(hero_identifier)
                    heroes_to_load_templates.append((hero_identifier, template))
                    
                else:
                    heroes_to_invite.append(hero)
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="InviteHeroesAndLoadTemplates",
                    children=[
                        BTParty.Heroes.InviteHeroes(heroes_to_invite, aftercast_ms=aftercast_ms, log=log),
                        BTParty.Heroes.LoadHeroTemplates(heroes_to_load_templates, aftercast_ms=aftercast_ms, log=log),
                    ]
                )
            )

        @staticmethod
        def KickHeroes(heroes : Sequence[int | HeroType | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _kick() -> BehaviorTree.NodeState:
                if len(heroes) == 0:
                    ConsoleLog("KickHeroes", 'No heroes specified to kick.', log=log)
                    return BehaviorTree.NodeState.SUCCESS
                
                mapped_heroes = BTParty.Heroes._get_hero_map(heroes, log=log)
                if not mapped_heroes:
                    return BehaviorTree.NodeState.FAILURE
                        
                in_party_heroes =  BTParty.Heroes._get_party_heroes(Player.GetLoginNumber())
                for hero_entry in mapped_heroes:
                    if any(hero_entry.hero_id == party_hero.hero_id for party_hero in in_party_heroes):
                        ConsoleLog("KickHeroes", f'Kicking hero: {hero_entry.name} (ID: {hero_entry.hero_id})', log=log)
                        Party.Heroes.KickHero(int(hero_entry.hero_id))
                    else:
                        ConsoleLog("KickHeroes", f'Hero not in party, skipping kick: {hero_entry.name} (ID: {hero_entry.hero_id})', log=log)
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="KickHeroes",
                    action_fn=lambda _node=None: _kick(),
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def SetupHeroes(heroes : Sequence[int | HeroType | str | tuple[int | HeroType | str, Optional[str]]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            heroes_to_invite: list[int | HeroType | str] = []
            heroes_to_load_templates: list[tuple[int | HeroType | str, str]] = []
            heroes_to_kick: list[int | HeroType | str] = []
            
            for hero in heroes:
                if isinstance(hero, tuple) and len(hero) == 2:
                    hero_identifier, template = hero
                    heroes_to_invite.append(hero_identifier)
                    if template:
                        heroes_to_load_templates.append((hero_identifier, template))
                    
                else:
                    heroes_to_invite.append(hero)
            
            party_heroes = BTParty.Heroes._get_party_heroes(Player.GetLoginNumber())
            for party_hero in party_heroes:
                if not any(
                    (party_hero.hero_id == BTParty.Heroes._get_hero_type(hero) if not isinstance(hero, tuple) else party_hero.hero_id == BTParty.Heroes._get_hero_type(hero[0]))
                    for hero in heroes
                ):
                    heroes_to_kick.append(party_hero.hero_id)
            
            children: list[BehaviorTree | BehaviorTree.Node] = []
            if heroes_to_kick:
                ConsoleLog("SetupHeroes", f'Heroes to kick: {heroes_to_kick}', log=log)
                children.append(BTParty.Heroes.KickHeroes(heroes_to_kick, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupHeroes", 'No heroes to kick.', log=log)
                
            
            if heroes_to_invite:
                ConsoleLog("SetupHeroes", f'Heroes to invite: {heroes_to_invite}', log=log)
                children.append(BTParty.Heroes.InviteHeroes(heroes_to_invite, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupHeroes", 'No heroes to invite.', log=log)
                
            if heroes_to_load_templates:
                ConsoleLog("SetupHeroes", f'Heroes to load templates for: {heroes_to_load_templates}', log=log)
                children.append(BTParty.Heroes.LoadHeroTemplates(heroes_to_load_templates, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupHeroes", 'No heroes to load templates for.', log=log)
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="SetupHeroes",
                    children=children
                )
            )

    class Multiboxing:
        @staticmethod
        def _get_player_entry(identifier : str | int) -> Optional[PlayerEntry]:
            shared_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
            
            def _get_owner_account(character_name: str) -> Optional[AccountStruct]:
                for acc in shared_accounts:
                    if _normalized(character_name) == _normalized(acc.AgentData.CharacterName):
                        return acc
                return None
            
            if isinstance(identifier, int):
                agent = Agent.GetAgentByID(identifier)
                if agent and Agent.IsPlayer(identifier):
                    character_name = str(Agent.GetNameByID(identifier) or '').strip()
                    account = _get_owner_account(character_name)
                
                    if account is None:
                        return PlayerEntry(
                            character_name=character_name,
                            character_name_normalized=_normalized(character_name),
                            account_email='',    
                            account=None,
                            template=None,
                            is_on_same_map=True,
                            login_number=Agent.GetLoginNumber(identifier),
                        )
                    else:
                        identifier = account.AgentData.CharacterName
            
            if isinstance(identifier, str):
                account = _get_owner_account(identifier) or next((acc for acc in shared_accounts if _normalized(identifier) == _normalized(acc.AccountEmail)), None)
                
                if account is not None:
                    mapid = Map.GetMapID() or 0
                    region = Map.GetRegion() or 0
                    district = Map.GetDistrict() or 0
                    language = Map.GetLanguage() or 0
                    on_same_map = account.AgentData.Map.MapID == mapid and account.AgentData.Map.Region == region and account.AgentData.Map.District == district and account.AgentData.Map.Language == language
                    
                    if account is not None:
                        return PlayerEntry(
                            character_name=account.AgentData.CharacterName,
                            character_name_normalized=_normalized(account.AgentData.CharacterName),
                            account_email=str(account.AccountEmail or '').strip(),
                            account=account,
                            template=None,
                            is_on_same_map=on_same_map,
                            login_number=account.AgentData.LoginNumber,
                        )
                else:
                    players = [agent for agent_id in AgentArray.GetAllyArray() if (agent := Agent.GetAgentByID(agent_id)) and Agent.IsPlayer(agent_id)]
                    for player in players:
                        character_name = str(Agent.GetNameByID(player.agent_id) or '').strip()
                        
                        if _normalized(character_name) == _normalized(identifier):
                            return PlayerEntry(
                                character_name=character_name,
                                character_name_normalized=_normalized(character_name),
                                account_email='',
                                account=None,
                                template=None,
                                is_on_same_map=True,
                                login_number=Agent.GetLoginNumber(player.agent_id),
                            )
            
            return None

        @staticmethod
        def _get_current_player_entries() -> list[PlayerEntry]:
            players = [agent for agent_id in AgentArray.GetAllyArray() if (agent := Agent.GetAgentByID(agent_id)) and Agent.IsPlayer(agent_id)]
            player_entries: list[PlayerEntry] = []
            
            for member in Party.GetPlayers():
                agent = next((agent for agent in players if Agent.GetLoginNumber(agent.agent_id) == member.login_number), None)
                
                if agent and (entry := BTParty.Multiboxing._get_player_entry(agent.agent_id)) is not None:
                    player_entries.append(entry)
                    
            return player_entries

        @staticmethod
        def InvitePlayers(players : Sequence[str | int], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def invite_players(
                players: Sequence[str | int],
                timeout_ms: int = 15000,
                poll_interval_ms: int = 100,
                aftercast_ms: int = 150,
                log: bool = False,
            ) -> BehaviorTree:
                childs: list[BehaviorTree | BehaviorTree.Node] = []
                from Sources.ApoSource.ApoBottingLib.wrappers import InviteAccountByEmail, SummonAccountByEmail

                for identifier in players:
                    entry = BTParty.Multiboxing._get_player_entry(identifier)
                    if entry is None:
                        ConsoleLog("InvitePlayers", f'Could not resolve player entry for identifier: {identifier}', log=log)
                        return BehaviorTree(
                            BehaviorTree.FailerNode(
                                name="InvitePlayers",
                            )
                        )

                    if entry.is_on_same_map:
                        if entry.account_email:
                            ConsoleLog("InvitePlayers", f'Invite multiboxing account by email: {entry.character_name} ({entry.account_email})', log=log)
                            childs.append(InviteAccountByEmail(entry.account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))

                        else:
                            ConsoleLog("InvitePlayers", f'Invite unknown player by character name: {entry.character_name}', log=log)
                            childs.append(
                                BehaviorTree.ActionNode(
                                    name=f'DispatchInvitePlayer({entry.character_name})',
                                    action_fn=lambda _node=None, player_name=entry.character_name: (
                                        ConsoleLog("InvitePlayers", f'Dispatch direct invite by name: {player_name}', log=log),
                                        Party.Players.InvitePlayer(str(player_name)),
                                        BehaviorTree.NodeState.SUCCESS,
                                    )[1],
                                    aftercast_ms=aftercast_ms,
                                ))

                            childs.append(
                                BehaviorTree.WaitUntilNode(
                                    name=f'WaitForInvitedPlayer({entry.character_name})',
                                    condition_fn=lambda player_name=entry.character_name: any(
                                        _normalized(player.character_name) == _normalized(player_name)
                                        for player in BTParty.Multiboxing._get_current_player_entries()
                                    ),
                                    throttle_interval_ms=poll_interval_ms,
                                    timeout_ms=timeout_ms,
                                ),
                            )

                    elif entry.account_email:
                        ConsoleLog("InvitePlayers", f'Summon and Invite multiboxing account by email: {entry.character_name} ({entry.account_email})', log=log)
                        childs.append(SummonAccountByEmail(entry.account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
                        childs.append(InviteAccountByEmail(entry.account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))

                    else:
                        ConsoleLog("InvitePlayers", f'Cannot invite player, no valid invitation method: {entry.character_name}', log=log)
                        return BehaviorTree(
                            BehaviorTree.FailerNode(
                                name="InvitePlayers",
                            )
                        )

                return BehaviorTree(
                    BehaviorTree.SequenceNode(
                        name="InvitePlayers",
                        children=childs,
                    )
                )

            return BehaviorTree(
                BehaviorTree.SubtreeNode(
                    name="InvitePlayers",
                    subtree_fn=lambda _node=None: invite_players(
                        players=players,
                        timeout_ms=timeout_ms,
                        poll_interval_ms=poll_interval_ms,
                        aftercast_ms=aftercast_ms,
                        log=log,
                    ),
                )
            )

        @staticmethod
        def SendTemplateRequestToPlayers(players : Sequence[tuple[str | int, str]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _send_template_request() -> BehaviorTree.NodeState:
                for identifier, template in players:
                    if not template:
                        continue 
                    
                    entry = BTParty.Multiboxing._get_player_entry(identifier)
                    
                    if entry is None:
                        ConsoleLog("SendTemplateRequestToPlayers", f'Could not resolve player entry for identifier: {identifier}', log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    if entry.account_email:
                        ConsoleLog("SendTemplateRequestToPlayers", f'Sending template request to multiboxing account by email: {entry.character_name} ({entry.account_email})', log=log)
                        GLOBAL_CACHE.ShMem.SendMessage(
                            sender_email=Player.GetAccountEmail(),
                            receiver_email=entry.account_email,
                            command=SharedCommandType.LoadSkillTemplate,
                            ExtraData=(template, '', '', ''),
                        )
                    else:
                        ConsoleLog("SendTemplateRequestToPlayers", f'Cannot send template request to player, no valid method: {entry.character_name}', log=log)
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="SendTemplateRequestToPlayers",
                    action_fn=lambda _node=None: _send_template_request(),
                    aftercast_ms=aftercast_ms,
                )
            )

        @staticmethod
        def InvitePlayersAndSendTemplateRequest(players_and_templates : Sequence[tuple[str | int, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            players = [identifier for identifier, _ in players_and_templates]
            templates = [(identifier, template) for identifier, template in players_and_templates if template]
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="InvitePlayersAndSendTemplateRequest",
                    children=[
                        BTParty.Multiboxing.InvitePlayers(players, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log),
                        BTParty.Multiboxing.SendTemplateRequestToPlayers(templates, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log),
                    ]
                )
            )

        @staticmethod
        def KickPlayers(players : Sequence[str | int], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _kick() -> BehaviorTree.NodeState:
                current_party = BTParty.Multiboxing._get_current_player_entries()
                for identifier in players:
                    entry = BTParty.Multiboxing._get_player_entry(identifier)
                    
                    if entry is None:
                        continue
                    
                    if entry.login_number is None:
                        ConsoleLog("KickPlayers", f'Cannot kick player with unknown login number, skipping: {entry.character_name}', log=log)
                        continue
                    
                    ConsoleLog("KickPlayers", f'Kicking player: {entry.character_name}', log=log)
                    Party.Players.KickPlayer(entry.login_number)
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.ActionNode(
                    name="KickPlayers",
                    action_fn=lambda _node=None: _kick(),
                    aftercast_ms=aftercast_ms,
                )
            )
            
        @staticmethod
        def SetupPlayers(players : Sequence[str | int | tuple[str | int, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            players_to_invite: list[str | int] = []
            players_to_send_template: list[tuple[str | int, str]] = []
            players_to_kick: list[str | int] = []
            
            current_party = BTParty.Multiboxing._get_current_player_entries()
            
            for player in players:
                if isinstance(player, tuple) and len(player) == 2:
                    player_identifier, template = player
                    players_to_invite.append(player_identifier)
                    if template:
                        players_to_send_template.append((player_identifier, template))
                    
                else:
                    players_to_invite.append(player)

            desired_entries = [player for identifier in players_to_invite if (player := BTParty.Multiboxing._get_player_entry(identifier)) is not None]
                    
            for party_member in current_party:
                if not any(party_member.character_name_normalized == entry.character_name_normalized for entry in desired_entries):
                    if party_member.character_name != Player.GetName():
                        players_to_kick.append(party_member.character_name)
                        
            children: list[BehaviorTree | BehaviorTree.Node] = []
            if players_to_kick:
                ConsoleLog("SetupPlayers", f'Players to kick: {players_to_kick}', log=log)
                children.append(BTParty.Multiboxing.KickPlayers(players_to_kick, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupPlayers", 'No players to kick.', log=log)
                
            if players_to_invite:
                ConsoleLog("SetupPlayers", f'Players to invite: {players_to_invite}', log=log)
                children.append(BTParty.Multiboxing.InvitePlayers(players_to_invite, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupPlayers", 'No players to invite.', log=log)
                
            if players_to_send_template:
                ConsoleLog("SetupPlayers", f'Players to send template request to: {players_to_send_template}', log=log)
                children.append(BTParty.Multiboxing.SendTemplateRequestToPlayers(players_to_send_template, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("SetupPlayers", 'No players to send template request to.', log=log)
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="SetupPlayers",
                    children=children
                )
            )
            
        @staticmethod
        def RequestAddHero(account_email : str, heroes : Sequence[int | HeroType | str], template: str, timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _request() -> BehaviorTree.NodeState:        
                available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
                account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
                
                if account is None:
                    ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                current_party_players = BTParty.Multiboxing._get_current_player_entries()
                if not any(player.account_email == account_email for player in current_party_players):
                    ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                current_heroes = BTParty.Heroes._get_party_heroes(account.AgentData.LoginNumber)
                heroes_to_add = [hero_identifier for hero_identifier in heroes if not any(hero.hero_id == BTParty.Heroes._get_hero_type(hero_identifier) for hero in current_heroes)]
                if not heroes_to_add:
                    ConsoleLog("RequestHeroFromAccount", f'All requested heroes are already in the party for account {account_email}.', log=log)
                    return BehaviorTree.NodeState.SUCCESS
                
                for hero_identifier in heroes:
                    hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                    
                    if hero_type is None:
                        ConsoleLog("RequestHero", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    GLOBAL_CACHE.ShMem.SendMessage(
                        sender_email=Player.GetAccountEmail(),
                        receiver_email=account_email,
                        command=SharedCommandType.AddHero,
                        params=(hero_type, 0, 0, 0),
                    )
                
                return BehaviorTree.NodeState.SUCCESS
            
            def _wait_for_heroes() -> bool:
                available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
                account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
                
                if account is None:
                    ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                    return True
                
                current_party_players = BTParty.Multiboxing._get_current_player_entries()
                if not any(player.account_email == account_email for player in current_party_players):
                    ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                    return True
                
                current_heroes = BTParty.Heroes._get_party_heroes(account.AgentData.LoginNumber)
                heroes_to_add = [hero_identifier for hero_identifier in heroes if not any(hero.hero_id == BTParty.Heroes._get_hero_type(hero_identifier) for hero in current_heroes)]
                if not heroes_to_add:
                    ConsoleLog("RequestHeroFromAccount", f'All requested heroes are already in the party for account {account_email}.', log=log)
                    return True
                
                for hero_identifier in heroes:
                    hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                    
                    if hero_type is None:
                        ConsoleLog("RequestHero", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                        return False
                    
                    if not any(hero.hero_id == hero_type for hero in current_heroes):
                        ConsoleLog("RequestHeroFromAccount", f'Waiting for hero {hero_type.name} (ID: {hero_type}) to be added to the party for account {account_email}.', log=log)
                        return False
                
                return True
                    
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="RequestHeroFromAccount",
                    children=[
                        BehaviorTree.ActionNode(
                            name="RequestHero",
                            action_fn=lambda _node=None: _request(),
                            aftercast_ms=aftercast_ms,
                        ),
                        
                        BehaviorTree.WaitUntilNode(
                            name=f'WaitForRequestedHeroes({account_email})',
                            condition_fn=_wait_for_heroes,
                            throttle_interval_ms=poll_interval_ms,
                            timeout_ms=timeout_ms,
                        ),
                    ],
                )
            )

        @staticmethod
        def RequestLoadHeroTemplate(account_email : str, heroes : Sequence[tuple[int | HeroType | str, str]], template: str, timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            from Sources.ApoSource.ApoBottingLib.wrappers import Wait

            def _request() -> BehaviorTree.NodeState:        
                for hero_identifier, template in heroes:
                    hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                    
                    if hero_type is None:
                        ConsoleLog("RequestLoadHeroTemplate", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    GLOBAL_CACHE.ShMem.SendMessage(
                        sender_email=Player.GetAccountEmail(),
                        receiver_email=account_email,
                        command=SharedCommandType.LoadSkillTemplateOnHero,
                        params=(hero_type, 0, 0, 0),
                        ExtraData=(template, '', '', '', ''),
                    )
                
                return BehaviorTree.NodeState.SUCCESS
            
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="RequestLoadHeroTemplate",
                    children=[
                        BehaviorTree.ActionNode(
                            name="RequestLoadHeroTemplate",
                            action_fn=lambda _node=None: _request(),
                            aftercast_ms=aftercast_ms,
                        ),
                        Wait(250)
                    ],
                )
            )

        @staticmethod
        def RequestKickHero(account_email : str, heroes : Sequence[int | HeroType | str], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _request() -> BehaviorTree.NodeState:  
                available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
                account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
                
                if account is None:
                    ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                current_party_players = BTParty.Multiboxing._get_current_player_entries()
                if not any(player.account_email == account_email for player in current_party_players):
                    ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                current_heroes = BTParty.Heroes._get_party_heroes(account.AgentData.LoginNumber)      
                for hero_identifier in heroes:
                    hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                    
                    if hero_type is None:
                        ConsoleLog("RequestKickHero", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                        return BehaviorTree.NodeState.FAILURE
                    
                    if not any(hero_type == hero.hero_id for hero in current_heroes):
                        ConsoleLog("RequestKickHero", f'Hero {hero_type.name} (ID: {hero_type}) is not currently in the party for account {account_email}, skipping kick request.', log=log)
                        continue
                    
                    GLOBAL_CACHE.ShMem.SendMessage(
                        sender_email=Player.GetAccountEmail(),
                        receiver_email=account_email,
                        command=SharedCommandType.KickHero,
                        params=(hero_type, 0, 0, 0),
                    )
                
                return BehaviorTree.NodeState.SUCCESS
            
            def _wait_for_kick() -> bool:
                available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
                account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
                
                if account is None:
                    ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                    return True
                
                current_party_players = BTParty.Multiboxing._get_current_player_entries()
                if not any(player.account_email == account_email for player in current_party_players):
                    ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                    return True
                
                current_heroes = BTParty.Heroes._get_party_heroes(account.AgentData.LoginNumber)      
                for hero_identifier in heroes:
                    hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                    
                    if hero_type is None:
                        ConsoleLog("RequestKickHero", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                        return False
                    
                    if any(hero_type == hero.hero_id for hero in current_heroes):
                        ConsoleLog("RequestKickHero", f'Hero {hero_type.name} (ID: {hero_type}) is still in the party for account {account_email}.', log=log)
                        return False
                
                ConsoleLog("RequestKickHero", f'All requested heroes have been kicked for account {account_email}.', log=log)
                return True
                
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="RequestKickHero",
                    children=[
                        BehaviorTree.ActionNode(
                            name="RequestKickHero",
                            action_fn=lambda _node=None: _request(),
                            aftercast_ms=aftercast_ms,
                        ),
                        
                        BehaviorTree.WaitUntilNode(
                            name=f'WaitForKickedHeroes({account_email})',
                            condition_fn=_wait_for_kick,
                            throttle_interval_ms=poll_interval_ms,
                            timeout_ms=timeout_ms,
                        ),
                    ]
                )
            )

        @staticmethod
        def RequestHeroSetup(account_email : str, heroes : Sequence[tuple[int | HeroType | str, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
            def _build_request_hero_setup_tree(
                account_email: str,
                heroes: Sequence[tuple[int | HeroType | str, Optional[str]]],
                timeout_ms: int = 15000,
                poll_interval_ms: int = 100,
                aftercast_ms: int = 150,
                log: bool = False,
            ) -> BehaviorTree:
                available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
                account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)

                if account is None:
                    ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                    return BehaviorTree(
                        BehaviorTree.FailerNode(
                            name="RequestHeroSetup",
                        )
                    )

                current_party_players = BTParty.Multiboxing._get_current_player_entries()
                if not any(player.account_email == account_email for player in current_party_players):
                    ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                    return BehaviorTree(
                        BehaviorTree.FailerNode(
                            name="RequestHeroSetup",
                        )
                    )

                current_heroes = BTParty.Heroes._get_party_heroes(account.AgentData.LoginNumber)
                heroes_to_kick = [hero for hero in current_heroes if not any(hero.hero_id == BTParty.Heroes._get_hero_type(hero_identifier) for hero_identifier, _ in heroes)]
                heroes_to_add = [hero_identifier for hero_identifier, _ in heroes if not any(hero.hero_id == BTParty.Heroes._get_hero_type(hero_identifier) for hero in current_heroes)]

                children: list[BehaviorTree | BehaviorTree.Node] = []
                if heroes_to_kick:
                    ConsoleLog("RequestHeroFromAccount", f'Heroes to kick from account {account_email}: {[hero.name for hero in heroes_to_kick]}', log=log)
                    for hero in heroes_to_kick:
                        children.append(BTParty.Multiboxing.RequestKickHero(account_email, [hero.hero_id], timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
                else:
                    ConsoleLog("RequestHeroFromAccount", f'No heroes to kick from account {account_email}.', log=log)

                if heroes_to_add:
                    ConsoleLog("RequestHeroFromAccount", f'Heroes to add from account {account_email}: {heroes_to_add}', log=log)
                    children.append(BTParty.Multiboxing.RequestAddHero(account_email, heroes_to_add, template='', timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
                else:
                    ConsoleLog("RequestHeroFromAccount", f'No heroes to add from account {account_email}.', log=log)
                    
                for hero_identifier, template in heroes:
                    if template:
                        hero_type = BTParty.Heroes._get_hero_type(hero_identifier)
                        if hero_type is not None:
                            ConsoleLog("RequestHeroFromAccount", f'Will request to load template for hero {hero_type.name} (ID: {hero_type}) on account {account_email}.', log=log)
                            children.append(BTParty.Multiboxing.RequestLoadHeroTemplate(account_email, [(hero_identifier, template)], template, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
                        else:
                            ConsoleLog("RequestHeroFromAccount", f'Could not resolve hero identifier for template loading: {hero_identifier}', log=log)

                return BehaviorTree(
                    BehaviorTree.SequenceNode(
                        name="RequestHeroSetup",
                        children=children
                    )
                )

            return BehaviorTree(
                BehaviorTree.SubtreeNode(
                    name="RequestHeroSetup",
                    subtree_fn=lambda _node=None: _build_request_hero_setup_tree(
                        account_email=account_email,
                        heroes=heroes,
                        timeout_ms=timeout_ms,
                        poll_interval_ms=poll_interval_ms,
                        aftercast_ms=aftercast_ms,
                        log=log,
                    ),
                )
            )
