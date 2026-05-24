import re
from typing import Any, NamedTuple, Optional, cast
from typing import Mapping
from typing import TypedDict
from typing import TypeVar
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC

import Py4GW
from PyParty import HenchmanPartyMember, HeroPartyMember
from PySkillbar import Skillbar

from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.shared_memory_src.AccountStruct import AccountStruct
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Party import Party
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Skillbar import SkillBar
from Py4GWCoreLib.enums_src.Hero_enums import HeroType
from Py4GWCoreLib.enums_src.Multiboxing_enums import SharedCommandType
from Py4GWCoreLib.native_src.context.AgentContext import AgentLivingStruct, AgentStruct
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Py4GWCoreLib.routines_src.yield_src import player
from Sources.ApoSource.ApoBottingLib.wrappers import InviteAccountByEmail, LeaveParty, LoadSkillbar, SummonAccountByEmail, Wait
from Py4GWCoreLib.routines_src.BehaviourTrees import BT as RoutinesBT


class _PartyPlayerEntry(TypedDict):
    spec: str
    shared_account: Any | None
    email: str
    character_name: str
    template: str


class _CurrentHenchmanEntry(TypedDict):
    resolved_id: int
    agent_id: int


TValue = TypeVar('TValue')
"""
List of:
- int (henchman ID)
- HeroType (hero ID)
- str (player name)
- Mapping[HeroType | int, str] (hero ID to template)
- Mapping[str, str] (player name to template)
- Mapping[tuple[str,  str], list[Mapping[HeroType | int, str]]] ((player name and template) to list of hero ID to template)
""" 
HeroTemplateEntry = tuple[HeroType | int, str]
PlayerTemplateEntry = tuple[str, str]
FollowerHeroSpec = HeroType | int | HeroTemplateEntry | Mapping[HeroType | int, str]
FollowerPlayerEntry = tuple[PlayerTemplateEntry, list[FollowerHeroSpec]]
PartyFormationEntry = int | HeroType | str | HeroTemplateEntry | PlayerTemplateEntry | Mapping[object, object] | FollowerPlayerEntry
PartyFormation = list[PartyFormationEntry]

HenchmenFormation = SequenceABC[int]
HeroesFormation = SequenceABC[tuple[str, tuple[int, str]]]
PlayersFormation = SequenceABC[tuple[str, str]]

def SetupPartyFormation(
    party_formation: PartyFormation,
    multibox_invite: bool = False,
    timeout_ms: int = 15000,
    poll_interval_ms: int = 100,
    aftercast_ms: int = 250,
    log: bool = False,
) -> BehaviorTree:
    def _debug(message: str) -> None:
        if log:
            Py4GW.Console.Log('SetupPartyFormation', message)

    _debug(
        f'Setting up party with formation: {party_formation}, multibox_invite: {multibox_invite}, '
        f'timeout_ms: {timeout_ms}, poll_interval_ms: {poll_interval_ms}, aftercast_ms: {aftercast_ms}, log: {log}'
    )
    
    all_accs = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
    own_mail = str(Player.GetAccountEmail() or "")
    own_acc = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(own_mail) if own_mail else None
    
    if not own_acc:
        _debug('Own account data not found in shared memory. Aborting party setup.')
        return BehaviorTree(
            BehaviorTree.FailerNode(name="SetupPartyFormationNoAccountData")
        )
    
    def _get_player_name(name_or_email: str) -> str:
        if "@" in name_or_email:
            acc = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(name_or_email.strip())
            if acc is not None:
                return str(acc.AgentData.CharacterName or "").strip()
            
        return name_or_email.strip()
    
    def _get_owner_name(login_number : int) -> str:
        return Party.Players.GetPlayerNameByLoginNumber(login_number)
    
    def _get_owner_account(character_name : str) -> AccountStruct | None:
        return next((acc for acc in all_accs if str(acc.AgentData.CharacterName or "").strip() == character_name), None)
    
    def _compose_follower_party_formation(heroes_list : SequenceABC[FollowerHeroSpec]) -> PartyFormation:
        formation: PartyFormation = []
        for entry in heroes_list:
            if isinstance(entry, HeroType):
                if entry.value > 0:
                    formation.append(entry)
                
            elif isinstance(entry, int):
                if entry > 0:
                    formation.append(HeroType(entry))
                
            elif isinstance(entry, tuple) and len(entry) == 2:
                hero_spec, template = entry
                resolved_template = str(template or '').strip()
                if not resolved_template:
                    continue

                if isinstance(hero_spec, HeroType) and hero_spec.value > 0:
                    formation.append((hero_spec, resolved_template))
                elif isinstance(hero_spec, int) and hero_spec > 0:
                    formation.append((HeroType(hero_spec), resolved_template))
                
            elif isinstance(entry, MappingABC):
                for key, value in entry.items():
                    if isinstance(key, int) and key > 0 and isinstance(value, str) and value.strip():
                        formation.append((HeroType(key), value.strip()))
                        
                    elif isinstance(key, HeroType) and key.value > 0 and isinstance(value, str) and value.strip():
                        formation.append((key, value.strip()))
                        
        return formation
    
    def _parse_party_formation(character_name : str, formation: PartyFormation) -> tuple[HenchmenFormation, HeroesFormation, PlayersFormation]:
        henchmen: HenchmenFormation = []
        
        #We map player name to hero id and hero template
        heroes: HeroesFormation = []
        
        #We map player name to player template
        players: PlayersFormation = []
        
        for entry in formation:
            #Hero, no build template
            if isinstance(entry, HeroType):
                if entry.value > 0:
                    heroes.append((character_name, (entry.value, '')))

            #Henchman
            elif isinstance(entry, int):
                if entry > 0:
                    henchmen.append(entry)
                
            #Player, no build template    
            elif isinstance(entry, str):
                if entry.strip():
                    players.append((entry.strip(), ''))

            elif isinstance(entry, tuple) and len(entry) == 2:
                key, value = entry

                if isinstance(key, HeroType) and key.value > 0 and isinstance(value, str) and value.strip():
                    heroes.append((character_name, (key.value, value.strip())))

                elif isinstance(key, int) and key > 0 and isinstance(value, str) and value.strip():
                    heroes.append((character_name, (key, value.strip())))

                elif isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip():
                    players.append((_get_player_name(key), value.strip()))

                elif isinstance(key, tuple) and len(key) == 2 and isinstance(value, list):
                    member_name = _get_player_name(str(key[0] or ''))
                    template = str(key[1] or '').strip()

                    if member_name:
                        _, acc_heroes, _ = _parse_party_formation(
                            member_name,
                            _compose_follower_party_formation(value),
                        )
                        if acc_heroes:
                            heroes.extend(
                                [
                                    (member_name, (hero_id, hero_template))
                                    for _, (hero_id, hero_template) in acc_heroes
                                ]
                            )

                    if member_name and template:
                        players.append((member_name, template))
                    
            elif isinstance(entry, MappingABC):
                for key, value in entry.items():
                    #Hero with build template using int as key
                    if isinstance(key, int) and key > 0 and isinstance(value, str) and value.strip():
                        heroes.append((character_name, (key, value.strip())))
                        
                    #Hero with build template using HeroType as key
                    elif isinstance(key, (HeroType)) and key.value > 0 and isinstance(value, str) and value.strip():
                        heroes.append((character_name, (key.value, value.strip())))
                    
                    #Player with build template using player name as key, we also support using email as key if it contains an @ and can be resolved to a character name in shared memory
                    elif isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip():
                        member_name = _get_player_name(key)
                        players.append((member_name, value.strip()))
                    
                    elif isinstance(key, tuple) and len(key) == 2 and isinstance(value, list):
                        member_name = _get_player_name(str(key[0] or ''))
                        template = str(key[1] or '').strip()
                        
                        if member_name:
                            _, acc_heroes, _ = _parse_party_formation(
                                member_name,
                                _compose_follower_party_formation(value),
                            )
                            if acc_heroes:
                                heroes.extend(
                                    [
                                        (member_name, (hero_id, hero_template))
                                        for _, (hero_id, hero_template) in acc_heroes
                                    ]
                                )
                        
                        if member_name and template:
                            players.append((member_name, template))
                            
                        
            
                                
        return henchmen, heroes, players
            
    def _get_current_formation() -> tuple[HenchmenFormation, HeroesFormation, PlayersFormation]:
        current_henchmen = [henchman.agent_id for henchman in (Party.GetHenchmen() or [])]
        current_heroes = [(_get_owner_name(hero.owner_player_id), (hero.hero_id.GetID(), "")) for hero in (Party.GetHeroes() or [])]
        local_login_number = int(Player.GetLoginNumber() or 0)
        current_players = [
            (str(Party.Players.GetPlayerNameByLoginNumber(int(getattr(player, "login_number", 0) or 0)) or "").strip(), "")
            for player in (Party.GetPlayers() or [])
            if int(getattr(player, "login_number", 0) or 0) > 0 and int(getattr(player, "login_number", 0) or 0) != local_login_number
        ]
        
        return current_henchmen, current_heroes, current_players
    
    def _apply_templates(desired: tuple[HenchmenFormation, HeroesFormation, PlayersFormation]) -> BehaviorTree:
        _, desired_heroes, desired_players = desired
        children: list[BehaviorTree | BehaviorTree.Node] = []

        local_hero_index = 0

        for hero_owner, (hero_id, template) in desired_heroes:
            if template:
                if hero_owner == own_acc.AgentData.CharacterName:
                    hero_index = Party.GetHeroIndex(hero_id)
                    if hero_index > 0:
                        SkillBar.LoadHeroSkillTemplate(hero_index, template)
                    
                else:
                    acc = _get_owner_account(hero_owner)
                    if acc is not None and str(acc.AccountEmail or '').strip():
                        recipient_email = str(acc.AccountEmail or '').strip()
                        _debug(f'Queue remote hero template load: owner={hero_owner}, hero_id={hero_id}, recipient={recipient_email}')
                        def _dispatch_remote_hero_template(
                            _node: BehaviorTree.Node | None = None,
                            *,
                            hero_owner: str = hero_owner,
                            recipient_email: str = recipient_email,
                            hero_id: int = hero_id,
                            template: str = template,
                        ) -> BehaviorTree.NodeState:
                            _debug(
                                f'Dispatch remote hero template load: owner={hero_owner}, recipient={recipient_email}, hero_id={hero_id}'
                            )
                            send_result = GLOBAL_CACHE.ShMem.SendMessage(
                                own_mail,
                                recipient_email,
                                SharedCommandType.LoadSkillTemplateOnHero,
                                (hero_id, 0.0, 0.0, 0.0),
                                (template, '', '', ''),
                            )
                            _debug(
                                f'Remote hero template message queued: owner={hero_owner}, hero_id={hero_id}, '
                                f'recipient={recipient_email}, send_result={send_result}'
                            )
                            return BehaviorTree.NodeState.SUCCESS

                        children.append(
                            BehaviorTree.ActionNode(
                                name=f'LoadHeroTemplateRemote({hero_owner}:{hero_id})',
                                action_fn=_dispatch_remote_hero_template,
                                aftercast_ms=max(250, int(aftercast_ms)),
                            )
                        )

        for player_name, template in desired_players:
            if template:
                if player_name == own_acc.AgentData.CharacterName:
                    _debug(f'Queue local player template load: player={player_name}')
                    SkillBar.LoadSkillTemplate(template)
                else:
                    acc = _get_owner_account(player_name)
                    if acc is not None and str(acc.AccountEmail or "").strip().lower() != own_mail:
                        recipient_email = str(acc.AccountEmail or '').strip()
                        _debug(f'Queue remote player template load: player={player_name}, recipient={recipient_email}')
                        def _dispatch_remote_player_template(
                            _node: BehaviorTree.Node | None = None,
                            *,
                            player_name: str = player_name,
                            recipient_email: str = recipient_email,
                            template: str = template,
                        ) -> BehaviorTree.NodeState:
                            _debug(f'Dispatch remote player template load: player={player_name}, recipient={recipient_email}')
                            send_result = GLOBAL_CACHE.ShMem.SendMessage(
                                own_mail,
                                recipient_email,
                                SharedCommandType.LoadSkillTemplate,
                                (0.0, 0.0, 0.0, 0.0),
                                (template, '', '', ''),
                            )
                            _debug(
                                f'Remote player template message queued: player={player_name}, recipient={recipient_email}, '
                                f'send_result={send_result}'
                            )
                            return BehaviorTree.NodeState.SUCCESS

                        children.append(
                            BehaviorTree.ActionNode(
                                name=f'LoadPlayerTemplateRemote({player_name})',
                                action_fn=_dispatch_remote_player_template,
                                aftercast_ms=max(250, int(aftercast_ms)),
                            )
                        )

        return RoutinesBT.Composite.Sequence(*children, name="ApplyTemplates")

    def _normalized(value: object) -> str:
        return str(value or '').strip().lower()

    local_name = str(own_acc.AgentData.CharacterName or '').strip()
    local_name_key = _normalized(local_name)
    local_email_key = _normalized(own_mail)

    desired_henchmen, desired_heroes, desired_players = _parse_party_formation(local_name, party_formation)
    _debug(f'Parsed desired formation: henchmen={list(desired_henchmen)}, heroes={list(desired_heroes)}, players={list(desired_players)}')

    desired_party_players: list[_PartyPlayerEntry] = []
    seen_player_keys: set[str] = set()

    for player_name, template in desired_players:
        resolved_name = str(player_name or '').strip()
        if not resolved_name:
            continue

        shared_account = _get_owner_account(resolved_name)
        resolved_email = str(shared_account.AccountEmail or '').strip() if shared_account is not None else ''
        template_code = str(template or '').strip()

        if _normalized(resolved_name) == local_name_key or (resolved_email and _normalized(resolved_email) == local_email_key):
            if template_code:
                local_player_template = template_code
            continue

        dedupe_key = _normalized(resolved_email or resolved_name)
        if not dedupe_key or dedupe_key in seen_player_keys:
            continue
        seen_player_keys.add(dedupe_key)
        desired_party_players.append({
            'spec': resolved_name,
            'shared_account': shared_account,
            'email': resolved_email,
            'character_name': resolved_name,
            'template': template_code,
        })
        _debug(
            f"Resolved desired remote player: name={resolved_name}, email={resolved_email or '<none>'}, "
            f"shared_account={'yes' if shared_account is not None else 'no'}, template={'yes' if bool(template_code) else 'no'}"
        )

    def _current_other_player_names() -> list[str]:
        return [player_name for player_name, _ in _get_current_formation()[2] if str(player_name or '').strip()]

    def _current_other_player_name_keys() -> list[str]:
        return [_normalized(name) for name in _current_other_player_names() if _normalized(name)]

    def _desired_other_player_names() -> list[str]:
        return [str(entry['character_name'] or '').strip() for entry in desired_party_players if str(entry['character_name'] or '').strip()]

    def _account_map_tuple(account: AccountStruct | None) -> tuple[int, int, int, int]:
        return (
            account.AgentData.Map.MapID,
            account.AgentData.Map.Region,
            account.AgentData.Map.District,
            account.AgentData.Map.Language,
        ) if account is not None else (0, 0, 0, 0)

    def _local_map_tuple() -> tuple[int, int, int, int]:
        return (
            int(Map.GetMapID() or 0),
            int(Map.GetRegion()[0] or 0),
            int(Map.GetDistrict() or 0),
            int(Map.GetLanguage()[0] or 0),
        )

    def _account_needs_summon(account: Any | None) -> bool:
        if account is None:
            return False
        local_tuple = _account_map_tuple(own_acc) if own_acc is not None else _local_map_tuple()
        target_tuple = _account_map_tuple(account)
        needs_summon = target_tuple != local_tuple
        _debug(f'Account map comparison: local={local_tuple}, target={target_tuple}, needs_summon={needs_summon}')
        return needs_summon

    def _current_hero_ids() -> list[int]:
        return [int(hero_id) for _, (hero_id, _) in _get_current_formation()[1]]

    def _current_local_hero_ids() -> list[int]:
        return [
            int(hero_id)
            for hero_owner, (hero_id, _) in _get_current_formation()[1]
            if _normalized(hero_owner) == local_name_key
        ]

    def _desired_local_hero_ids() -> list[int]:
        return [int(hero_id) for hero_owner, (hero_id, _) in desired_heroes if _normalized(hero_owner) == local_name_key]

    def _current_henchman_entries() -> list[_CurrentHenchmanEntry]:
        entries: list[_CurrentHenchmanEntry] = []
        for henchman in (Party.GetHenchmen() or []):
            entries.append({
                'resolved_id': henchman.agent_id,
                'agent_id': int(getattr(henchman, 'agent_id', 0) or 0),
            })
        return entries

    def _send_command_action(
        name: str,
        recipient_email: str,
        command: SharedCommandType,
        params: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
        extra: tuple[Any, Any, Any, Any] = ('', '', '', ''),
    ) -> BehaviorTree.Node:
        def _send(_node: BehaviorTree.Node | None = None) -> BehaviorTree.NodeState:
            if not own_mail or not recipient_email:
                _debug(f'{name} failed before dispatch: sender={own_mail or "<empty>"}, recipient={recipient_email or "<empty>"}')
                return BehaviorTree.NodeState.FAILURE
            _debug(f'Dispatch shared-memory command: name={name}, recipient={recipient_email}, command={command.name}, params={params}, extra={extra}')
            GLOBAL_CACHE.ShMem.SendMessage(
                own_mail,
                recipient_email,
                command,
                params,
                extra,
            )
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree.ActionNode(
            name=name,
            action_fn=_send,
            aftercast_ms=max(250, int(aftercast_ms)),
        )

    def _kick_player_by_name(player_name: str) -> BehaviorTree.Node:
        return BehaviorTree.ActionNode(
            name=f'KickPlayer({player_name})',
            action_fn=lambda _node=None, player_name=player_name: (
                _debug(f'Dispatch kick player: {player_name}'),
                GLOBAL_CACHE.Party.Players.KickPlayer(str(player_name)),
                BehaviorTree.NodeState.SUCCESS,
            )[1],
            aftercast_ms=aftercast_ms,
        )

    def _invite_player_by_name(player_name: str) -> BehaviorTree:
        normalized_name = _normalized(player_name)
        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name=f'InvitePlayer({player_name})',
                children=[
                    BehaviorTree.ActionNode(
                        name=f'DispatchInvitePlayer({player_name})',
                        action_fn=lambda _node=None, player_name=player_name: (
                            _debug(f'Dispatch direct invite by name: {player_name}'),
                            GLOBAL_CACHE.Party.Players.InvitePlayer(str(player_name)),
                            BehaviorTree.NodeState.SUCCESS,
                        )[1],
                        aftercast_ms=aftercast_ms,
                    ),
                    BehaviorTree.WaitUntilNode(
                        name=f'WaitForInvitedPlayer({player_name})',
                        condition_fn=lambda normalized_name=normalized_name: normalized_name in {
                            _normalized(name) for name in _current_other_player_names()
                        },
                        throttle_interval_ms=poll_interval_ms,
                        timeout_ms=timeout_ms,
                    ),
                ],
            )
        )

    def _party_matches_target() -> bool:
        if not (Map.IsMapReady() and Map.IsOutpost() and Party.IsPartyLoaded()):
            _debug(
                f'Party match blocked: map_ready={Map.IsMapReady()}, outpost={Map.IsOutpost()}, '
                f'party_loaded={Party.IsPartyLoaded()}'
            )
            return False

        current_henchmen, current_heroes, current_players = _get_current_formation()
        normalized_current_heroes = [(_normalized(owner), int(hero_id)) for owner, (hero_id, _) in current_heroes]
        normalized_desired_heroes = [(_normalized(owner), int(hero_id)) for owner, (hero_id, _) in desired_heroes]
        normalized_current_players = [_normalized(name) for name, _ in current_players if _normalized(name)]
        normalized_desired_players = [_normalized(name) for name in _desired_other_player_names() if _normalized(name)]
        match = (
            list(current_henchmen) == list(desired_henchmen)
            and normalized_current_heroes == normalized_desired_heroes
            and normalized_current_players == normalized_desired_players
        )
        _debug(
            f'Party match check: match={match}, current_henchmen={list(current_henchmen)}, desired_henchmen={list(desired_henchmen)}, '
            f'current_heroes={normalized_current_heroes}, desired_heroes={normalized_desired_heroes}, '
            f'current_players={normalized_current_players}, desired_players={normalized_desired_players}'
        )
        return match

    def _template_actions() -> list[BehaviorTree | BehaviorTree.Node]:
        actions: list[BehaviorTree | BehaviorTree.Node] = []
        template_tree = _apply_templates((desired_henchmen, desired_heroes, desired_players))
        if getattr(template_tree.root, 'children', None):
            actions.append(template_tree)
        return actions

    def _build_setup_party_formation_subtree(node: BehaviorTree.Node) -> BehaviorTree | BehaviorTree.Node:
        retry_count = int(node.blackboard.get('setup_party_retry_count', 0) or 0)
        _debug(f'Entering setup subtree: retry_count={retry_count}')

        if _party_matches_target():
            template_children = _template_actions()
            if not template_children:
                _debug('Party already matches target and there are no template actions to run.')
                return BehaviorTree.SucceederNode(name='SetupPartyFormationAlreadyMatches')
            _debug(f'Party already matches target. Running {len(template_children)} template action(s).')
            return RoutinesBT.Composite.Sequence(*template_children, name='SetupPartyFormationApplyTemplates')

        current_other_names = _current_other_player_names()
        current_other_name_keys = _current_other_player_name_keys()
        desired_other_name_keys = [_normalized(name) for name in _desired_other_player_names() if _normalized(name)]
        _debug(
            f'Current remote players={current_other_names}, desired remote players={_desired_other_player_names()}, '
            f'is_party_leader={Party.IsPartyLeader()}'
        )

        if not Party.IsPartyLeader():
            if retry_count >= 1:
                _debug('Not party leader after retry. Returning failure.')
                return BehaviorTree.FailerNode(name='SetupPartyFormationNotLeaderAfterRetry')
            node.blackboard['setup_party_retry_count'] = retry_count + 1
            _debug('Not party leader. Leaving party and retrying once.')
            return BehaviorTree.SequenceNode(
                name='SetupPartyFormationLeaveAndRetry',
                children=[
                    LeaveParty().root,
                    BehaviorTree.SubtreeNode(
                        name='RetrySetupPartyFormationAfterLeave',
                        subtree_fn=_build_setup_party_formation_subtree,
                    ),
                ],
            )

        desired_player_entries_by_name = {
            _normalized(str(entry['character_name'] or '').strip()): entry
            for entry in desired_party_players
            if _normalized(str(entry['character_name'] or '').strip())
        }
        desired_player_name_keys_with_local = set(desired_other_name_keys)
        desired_player_name_keys_with_local.add(local_name_key)

        current_henchman_entries = _current_henchman_entries()
        current_henchman_ids = [entry['resolved_id'] for entry in current_henchman_entries]
        if len(current_henchman_ids) != len(Party.GetHenchmen() or []):
            _debug(f'Unresolved henchmen state: entries={current_henchman_entries}')
            return BehaviorTree.FailerNode(name='SetupPartyFormationUnresolvedHenchmen')

        current_henchmen_set = set(current_henchman_ids)
        desired_henchmen_set = {int(henchman_id) for henchman_id in desired_henchmen}
        current_local_hero_ids = _current_local_hero_ids()
        current_local_hero_set = set(current_local_hero_ids)
        desired_local_hero_ids = _desired_local_hero_ids()
        current_heroes = list(_get_current_formation()[1])
        desired_remote_hero_specs = [
            (hero_owner, int(hero_id), str(template or '').strip())
            for hero_owner, (hero_id, template) in desired_heroes
            if _normalized(hero_owner) != local_name_key
        ]
        _debug(
            f'Current snapshot: henchmen={current_henchman_ids}, heroes={current_heroes}, '
            f'local_hero_ids={current_local_hero_ids}, desired_local_hero_ids={desired_local_hero_ids}, '
            f'desired_remote_hero_specs={desired_remote_hero_specs}'
        )

        children: list[BehaviorTree | BehaviorTree.Node] = []

        def _kick_unwanted_members(player_name: str) -> BehaviorTree.Node:
            def _kick(_node: BehaviorTree.Node | None = None) -> BehaviorTree.NodeState:
                for henchman_id in current_henchman_ids:
                    if henchman_id not in desired_henchmen_set:
                        _debug(f'Bulk henchman kick dispatch: player={player_name}, henchman_id={henchman_id}')
                        Party.Henchmen.KickHenchman(henchman_id)
                    else:
                        _debug(f'Bulk henchman keep: player={player_name}, henchman_id={henchman_id}')
                
                
                for hero_owner, (hero_id, _) in current_heroes:
                    hero_id = HeroType(hero_id)
                    
                    normalized_owner = _normalized(hero_owner)
                    if (normalized_owner, int(hero_id)) not in {(_normalized(owner), int(hero_id)) for owner, (hero_id, _) in desired_heroes}:
                        if normalized_owner == local_name_key:
                            _debug(f'Queue kick for unwanted local hero during unwanted kick: hero_id={hero_id.name}')
                            Party.Heroes.KickHero(int(hero_id))
                        else:
                            _debug(f'Unexpected remote hero owner encountered during unwanted kick: owner={hero_owner}, hero_id={hero_id.name}')
                            return BehaviorTree.NodeState.FAILURE
                
                for current_name in current_other_names:
                    if _normalized(current_name) not in set(desired_other_name_keys):
                        _debug(f'Queue kick for unwanted remote player during henchman kick: {current_name}')
                        Party.Players.KickPlayer(str(current_name))
            
                return BehaviorTree.NodeState.SUCCESS
                                        
            return BehaviorTree.ActionNode(
                name=f'KickUnwantedMembers({player_name})',
                action_fn=_kick,
                aftercast_ms=aftercast_ms,
                )
        
        def _add_own_heroes_and_henchmen(player_name: str) -> BehaviorTree.Node:
            def _add(_node: BehaviorTree.Node | None = None) -> BehaviorTree.NodeState:
                for henchman_id in desired_henchmen_set:
                    if henchman_id not in current_henchman_ids:
                        _debug(f'Bulk henchman add dispatch: player={player_name}, henchman_id={henchman_id}')
                        Party.Henchmen.AddHenchman(henchman_id)
                    else:
                        _debug(f'Bulk henchman keep: player={player_name}, henchman_id={henchman_id}')
                    
                
                for hero_owner, (hero_id, _) in desired_heroes:
                    hero_id = HeroType(hero_id)
                    normalized_owner = _normalized(hero_owner)
                    
                    if (normalized_owner, int(hero_id)) not in {(_normalized(owner), int(hero_id)) for owner, (hero_id, _) in current_heroes}:
                        if normalized_owner == local_name_key:
                            _debug(f'Add missing local hero during hero and henchman add: hero_id={hero_id.name}')
                            Party.Heroes.AddHero(int(hero_id))
                        else:
                            continue
                
                return BehaviorTree.NodeState.SUCCESS
                                        
            return BehaviorTree.ActionNode(
                name=f'AddHenchman({player_name})',
                action_fn=_add,
                aftercast_ms=aftercast_ms,
                )
        
        def _has_unwanted_members() -> bool:
            return any(current_henchman_id not in desired_henchmen_set for current_henchman_id in current_henchman_ids) or \
                any(current_local_hero_id not in desired_local_hero_ids for current_local_hero_id in current_local_hero_ids) or \
                any(_normalized(current_name) not in set(desired_player_name_keys_with_local) for current_name in current_other_names)

        def _has_missing_own_heroes_or_henchmen() -> bool:
            return any(desired_henchman_id not in current_henchman_ids for desired_henchman_id in desired_henchmen_set) or \
                any(desired_local_hero_id not in current_local_hero_ids for desired_local_hero_id in desired_local_hero_ids)

        if _has_unwanted_members():
            _debug(
                f'Current henchmen do not match desired set. current={current_henchman_ids}, desired={list(desired_henchmen)}. '
                f'Queueing bulk henchman kick.'
            )
            children.append(_kick_unwanted_members(local_name))

        if _has_missing_own_heroes_or_henchmen():
            _debug(
                f'Current henchmen do not match desired set. current={current_henchman_ids}, desired={list(desired_henchmen)}. '
                f'Queueing bulk henchman add.'
            )
            children.append(_add_own_heroes_and_henchmen(local_name))
        

        for desired_name_key in desired_other_name_keys:
            if desired_name_key in current_other_name_keys:
                continue
            entry = desired_player_entries_by_name.get(desired_name_key)
            if entry is None:
                _debug(f'Could not resolve desired remote player entry for key={desired_name_key}')
                continue

            character_name = str(entry['character_name'] or '').strip()
            shared_account = entry['shared_account']
            account_email = str(entry['email'] or '').strip()
            should_summon_first = shared_account is not None and account_email and _account_needs_summon(shared_account)
            if should_summon_first:
                _debug(
                    f'Queue summon+invite for remote account: player={character_name}, email={account_email}, '
                    f'multibox_invite={multibox_invite}'
                )
                
                children.append(_send_command_action(
                    name=f'LeavePartyCommandBeforeInvite({character_name})',
                    recipient_email=account_email,
                    command=SharedCommandType.LeaveParty,
                ))
                children.append(SummonAccountByEmail(account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
                children.append(InviteAccountByEmail(account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
            elif shared_account is not None and account_email:
                _debug(f'Queue invite for remote account already on same map: player={character_name}, email={account_email}')
                
                #send leave party command
                children.append(_send_command_action(
                    name=f'LeavePartyCommandBeforeInvite({character_name})',
                    recipient_email=account_email,
                    command=SharedCommandType.LeaveParty,
                ))                
                
                children.append(InviteAccountByEmail(account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
            else:
                _debug(f'Queue direct invite by name for non-shared account: player={character_name}')
                children.append(_invite_player_by_name(character_name))

        for hero_owner, hero_id, template in desired_remote_hero_specs:
            hero_id = HeroType(hero_id)
            
            normalized_owner = _normalized(hero_owner)
            if normalized_owner not in set(desired_other_name_keys):
                _debug(f'Remote hero owner not present in desired remote party: owner={hero_owner}, hero_id={hero_id}')
                return BehaviorTree.FailerNode(name=f'SetupPartyFormationMissingRemotePartyOwner({hero_owner})')

            if (normalized_owner, hero_id) in [(_normalized(owner), int(current_hero_id)) for owner, (current_hero_id, _) in current_heroes]:
                _debug(f'Remote hero already present, skipping add: owner={hero_owner}, hero_id={hero_id}')
                continue

            owner_acc = _get_owner_account(hero_owner)
            owner_email = str(owner_acc.AccountEmail or '').strip() if owner_acc is not None else ''
            if not owner_email:
                _debug(f'Missing owner email for remote hero add: owner={hero_owner}, hero_id={hero_id}')
                return BehaviorTree.FailerNode(name=f'SetupPartyFormationMissingRemoteOwnerAccount({hero_owner})')

            _debug(f'Queue remote hero add: owner={hero_owner}, email={owner_email}, hero_id={hero_id}, has_template={bool(template)}')
            children.append(
                _send_command_action(
                    name=f'RemoteAddHero({hero_owner}:{hero_id.name})',
                    recipient_email=owner_email,
                    command=SharedCommandType.AddHero,
                    params=(hero_id, 0, 0, 0),
                    extra=(template, '', '', ''),
                )
            )

        if children:
            _debug(f'Built reconcile action list with {len(children)} action(s) before wait/template steps.')
            children.append(
                BehaviorTree.WaitUntilNode(
                    name='WaitForSetupPartyFormationMatch',
                    condition_fn=_party_matches_target,
                    throttle_interval_ms=poll_interval_ms,
                    timeout_ms=timeout_ms,
                )
            )

        children.extend(_template_actions())
        _debug(f'Final action list size including template actions: {len(children)}')

        if not children:
            _debug('No reconcile actions queued. Returning success.')
            return BehaviorTree.SucceederNode(name='SetupPartyFormationEmpty')

        return RoutinesBT.Composite.Sequence(*children, name='SetupPartyFormationReconcile')

    return BehaviorTree(
        BehaviorTree.SubtreeNode(
            name="SetupParty",
            subtree_fn=_build_setup_party_formation_subtree,
        )
    )


HenchmanEntry = NamedTuple("HenchmanEntry", [
    ("agent_id", int),
    ("primary", int),
    ("level", int),
    ("name", str),
    ("name_normalized", str),
]) 

def _normalized(name : str) -> str:
    return str(name or '').strip().lower().split('[')[0].strip()

def _get_henchman_entry(agent_or_henchman : AgentLivingStruct |HenchmanPartyMember) -> Optional[HenchmanEntry]:
    name = Agent.GetNameByID(agent_or_henchman.agent_id) or ''
    
    return HenchmanEntry(
        agent_id=agent_or_henchman.agent_id,
        primary=agent_or_henchman.primary if isinstance(agent_or_henchman, AgentLivingStruct) else agent_or_henchman.profession.ToInt(),
        level=agent_or_henchman.level,
        name=name,
        name_normalized=_normalized(name),
    ) if name else None
        
def _get_available_henchmen() -> list[HenchmanEntry]:
    henchmen: list[HenchmanEntry] = []
    for henchman_id in AgentArray.GetAllyArray():
        if Agent.CanBeViewedInPartyWindow(henchman_id) and not Agent.IsPlayer(henchman_id):
            if (agent := Agent.GetAgentByID(henchman_id)) and (living_agent := agent.GetAsAgentLiving()) and living_agent is not None:
                if entry := _get_henchman_entry(living_agent):
                    henchmen.append(entry)
    return henchmen

def _get_henchman(identifier : int | str | list[int], available_henchmen: list[HenchmanEntry]) -> Optional[HenchmanEntry]:        
    if isinstance(identifier, str):
        for henchman in available_henchmen:
            if henchman.name_normalized == _normalized(identifier):
                return henchman
    
    if isinstance(identifier, int):
        if (agent := Agent.GetAgentByID(identifier)) and (living_agent := agent.GetAsAgentLiving()) and living_agent is not None:
            return _get_henchman_entry(living_agent) 
    
    return None
    
def InviteHenchmen(henchman_ids: list[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _invite() -> BehaviorTree.NodeState:
        available_henchmen = _get_available_henchmen()
        in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := _get_henchman_entry(party_henchman)) is not None]
        desired_henchmen: list[HenchmanEntry] = [henchman for identifier in henchman_ids if (henchman := _get_henchman(identifier, available_henchmen)) is not None]
        
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

def KickHenchmen(henchman_ids: list[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _kick() -> BehaviorTree.NodeState:
        if len(henchman_ids) == 0:
            ConsoleLog("KickHenchmen", 'No henchmen specified to kick.', log=log)
            return BehaviorTree.NodeState.SUCCESS
        
        in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := _get_henchman_entry(party_henchman)) is not None]
        desired_kick_henchmen: list[HenchmanEntry] = [henchman for identifier in henchman_ids if (henchman := _get_henchman(identifier, in_party_henchmen)) is not None]
        
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

def SetupHenchmen(henchmen : list[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    available_henchmen = _get_available_henchmen()
    desired_henchmen: list[HenchmanEntry] = [henchman for identifier in henchmen if (henchman := _get_henchman(identifier, available_henchmen)) is not None]
    
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
    
    in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := _get_henchman_entry(party_henchman)) is not None]
    henchmen_to_kick: list[int | str] = [henchman.agent_id for henchman in in_party_henchmen if not any(henchman.agent_id == desired.agent_id for desired in desired_henchmen)]
    henchmen_to_add: list[int | str] = [henchman.agent_id for henchman in desired_henchmen if not any(henchman.agent_id == party.agent_id for party in in_party_henchmen)]
    
    
    children: list[BehaviorTree | BehaviorTree.Node] = []
    if henchmen_to_kick:
        ConsoleLog("SetupHenchmen", f'Henchmen to kick: {henchmen_to_kick}', log=log)
        children.append(KickHenchmen(henchmen_to_kick, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupHenchmen", 'No henchmen to kick.', log=log)
    
    if henchmen_to_add:
        ConsoleLog("SetupHenchmen", f'Henchmen to add: {henchmen_to_add}', log=log)
    else:
        ConsoleLog("SetupHenchmen", 'No henchmen to add.', log=log)

    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="InviteHeroesAndLoadTemplates",
            children=children,
        )
    )

HeroeEntry = NamedTuple("HeroEntry", [
    ("hero_id", HeroType),
    ("template", str),
    ("name", str),
    ("name_normalized", str),
])

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

def _get_hero_map(heroes : list[int | HeroType | str], log: bool = False) -> list[HeroeEntry]:
    mapped_heroes: list[HeroeEntry] = []
    for hero_identifier in heroes:
        hero_type = _get_hero_type(hero_identifier)
        
        if hero_type is not None and _is_hero_available(hero_type):
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

def _is_hero_available(hero_id: HeroType) -> bool:
    # We don't have a way yet to check hero availability before inviting, but we keep this so we can implement it later if we find a way
    return True

def _get_hero_entry(hero : HeroPartyMember) -> Optional[HeroeEntry]:
    hero_id = HeroType(hero.hero_id.GetID() or 0)
    
    return HeroeEntry(
        hero_id=hero_id,
        template='',
        name=hero_id.name,
        name_normalized=_normalized(hero_id.name),
    ) if hero_id else None

def _get_party_heroes(login_number: int) -> list[HeroeEntry]:
    party_heroes: list[HeroeEntry] = []
    for party_hero in Party.GetHeroes() or []:
        if party_hero.owner_player_id == login_number:
            if (hero_entry := _get_hero_entry(party_hero)) is not None:
                party_heroes.append(hero_entry)

    return party_heroes
    
def InviteHeroes(heroes : list[int | HeroType | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _invite() -> BehaviorTree.NodeState:
        mapped_heroes = _get_hero_map(heroes, log=log)
        if not mapped_heroes:
            return BehaviorTree.NodeState.FAILURE
                
        in_party_heroes =  _get_party_heroes(Player.GetLoginNumber())
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

def LoadHeroTemplates(heroes : list[tuple[int | HeroType | str, str]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _load_templates() -> BehaviorTree.NodeState:
        for hero_identifier, template in heroes:
            hero_type = _get_hero_type(hero_identifier)
            
            if hero_type is None:
                ConsoleLog("LoadHeroTemplates", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                return BehaviorTree.NodeState.FAILURE
            
            in_party_heroes =  _get_party_heroes(Player.GetLoginNumber())
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

def InviteHeroesAndLoadTemplates(heroes : list[int | HeroType | str | tuple[int | HeroType | str, str]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
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
                InviteHeroes(heroes_to_invite, aftercast_ms=aftercast_ms, log=log),
                LoadHeroTemplates(heroes_to_load_templates, aftercast_ms=aftercast_ms, log=log),
            ]
        )
    )

def KickHeroes(heroes : list[int | HeroType | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _kick() -> BehaviorTree.NodeState:
        if len(heroes) == 0:
            ConsoleLog("KickHeroes", 'No heroes specified to kick.', log=log)
            return BehaviorTree.NodeState.SUCCESS
        
        mapped_heroes = _get_hero_map(heroes, log=log)
        if not mapped_heroes:
            return BehaviorTree.NodeState.FAILURE
                
        in_party_heroes =  _get_party_heroes(Player.GetLoginNumber())
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

def SetupHeroes(heroes : list[int | HeroType | str | tuple[int | HeroType | str, Optional[str]]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
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
    
    party_heroes = _get_party_heroes(Player.GetLoginNumber())
    for party_hero in party_heroes:
        if not any(
            (party_hero.hero_id == _get_hero_type(hero) if not isinstance(hero, tuple) else party_hero.hero_id == _get_hero_type(hero[0]))
            for hero in heroes
        ):
            heroes_to_kick.append(party_hero.hero_id)
    
    children: list[BehaviorTree | BehaviorTree.Node] = []
    if heroes_to_kick:
        ConsoleLog("SetupHeroes", f'Heroes to kick: {heroes_to_kick}', log=log)
        children.append(KickHeroes(heroes_to_kick, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupHeroes", 'No heroes to kick.', log=log)
        
    
    if heroes_to_invite:
        ConsoleLog("SetupHeroes", f'Heroes to invite: {heroes_to_invite}', log=log)
        children.append(InviteHeroes(heroes_to_invite, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupHeroes", 'No heroes to invite.', log=log)
        
    if heroes_to_load_templates:
        ConsoleLog("SetupHeroes", f'Heroes to load templates for: {heroes_to_load_templates}', log=log)
        children.append(LoadHeroTemplates(heroes_to_load_templates, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupHeroes", 'No heroes to load templates for.', log=log)
    
    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="SetupHeroes",
            children=children
        )
    )

PlayerEntry = NamedTuple("PlayerEntry", [
    ("character_name", str),
    ("character_name_normalized", str),
    ("account_email", str),
    ("account", Optional[AccountStruct]),
    ("template", Optional[str]),
    ("is_on_same_map", bool),
    ("login_number", Optional[int]),
])

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
                identifier = account.AccountEmail
    
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
                    login_number=account.AgentData.LoginNumber if on_same_map else None,
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

def _is_player_available(identifier: str | int) -> bool:
    return _get_player_entry(identifier) is not None

def _get_current_player_entries() -> list[PlayerEntry]:
    players = [agent for agent_id in AgentArray.GetAllyArray() if (agent := Agent.GetAgentByID(agent_id)) and Agent.IsPlayer(agent_id)]
    player_entries: list[PlayerEntry] = []
    
    for member in Party.GetPlayers():
        agent = next((agent for agent in players if Agent.GetLoginNumber(agent.agent_id) == member.login_number), None)
        
        if agent and (entry := _get_player_entry(agent.agent_id)) is not None:
            player_entries.append(entry)
            
    return player_entries

def InvitePlayers(players : list[str | int], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _invite() -> BehaviorTree.NodeState:
        children: list[BehaviorTree | BehaviorTree.Node] = []
        
        for identifier in players:
            entry = _get_player_entry(identifier)
            if entry is None:
                ConsoleLog("InvitePlayers", f'Could not resolve player entry for identifier: {identifier}', log=log)
                return BehaviorTree.NodeState.FAILURE
            
            if entry.is_on_same_map:
                if entry.account_email:
                    ConsoleLog("InvitePlayers", f'Invite multiboxing account by email: {entry.character_name} ({entry.account_email})', log=log)
                    children.append(InviteAccountByEmail(entry.account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
                    
                else:
                    ConsoleLog("InvitePlayers", f'Invite unknown player by character name: {entry.character_name}', log=log)
                    children.append(
                        BehaviorTree.ActionNode(
                            name=f'DispatchInvitePlayer({entry.character_name})',
                            action_fn=lambda _node=None, player_name=entry.character_name: (
                                ConsoleLog("InvitePlayers", f'Dispatch direct invite by name: {player_name}', log=log),
                                Party.Players.InvitePlayer(str(player_name)),
                                BehaviorTree.NodeState.SUCCESS,
                            )[1],
                            aftercast_ms=aftercast_ms,
                        ))
                    
                    children.append(
                        BehaviorTree.WaitUntilNode(
                            name=f'WaitForInvitedPlayer({entry.character_name})',
                            condition_fn= lambda player_name=entry.character_name: any(_normalized(player.character_name) == _normalized(player_name) for player in _get_current_player_entries()),
                            throttle_interval_ms=poll_interval_ms,
                            timeout_ms=timeout_ms,
                        ),
                    )
                                
                
            elif entry.account_email:
                ConsoleLog("InvitePlayers", f'Summon and Invite multiboxing account by email: {entry.character_name} ({entry.account_email})', log=log)
                children.append(SummonAccountByEmail(entry.account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
                children.append(InviteAccountByEmail(entry.account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
                
            else:
                ConsoleLog("InvitePlayers", f'Cannot invite player, no valid invitation method: {entry.character_name}', log=log)
                return BehaviorTree.NodeState.FAILURE
        
        return BehaviorTree.NodeState.SUCCESS
    
    return BehaviorTree(
        BehaviorTree.ActionNode(
            name="InvitePlayers",
            action_fn=lambda _node=None: _invite(),
            aftercast_ms=aftercast_ms,
        )
    )

def SendTemplateRequestToPlayers(players : list[tuple[str | int, str]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _send_template_request() -> BehaviorTree.NodeState:
        for identifier, template in players:
            if not template:
                continue 
            
            entry = _get_player_entry(identifier)
            
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

def InvitePlayersAndSendTemplateRequest(players_and_templates : list[tuple[str | int, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    players = [identifier for identifier, _ in players_and_templates]
    templates = [(identifier, template) for identifier, template in players_and_templates if template]
    
    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="InvitePlayersAndSendTemplateRequest",
            children=[
                InvitePlayers(players, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log),
                SendTemplateRequestToPlayers(templates, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log),
            ]
        )
    )

def KickPlayers(players : list[str | int], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _kick() -> BehaviorTree.NodeState:
        current_party = _get_current_player_entries()
        for identifier in players:
            entry = _get_player_entry(identifier)
            
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
    
def SetupPlayers(players : list[str | int | tuple[str | int, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    players_to_invite: list[str | int] = []
    players_to_send_template: list[tuple[str | int, str]] = []
    players_to_kick: list[str | int] = []
    
    current_party = _get_current_player_entries()
            
    desired_entries = [player for identifier in players_to_invite if (player := _get_player_entry(identifier)) is not None]
    
    
    for player in players:
        if isinstance(player, tuple) and len(player) == 2:
            player_identifier, template = player
            players_to_invite.append(player_identifier)
            if template:
                players_to_send_template.append((player_identifier, template))
            
        else:
            players_to_invite.append(player)
            
    for party_member in current_party:
        if not any(party_member.character_name_normalized == entry.character_name_normalized for entry in desired_entries):
            players_to_kick.append(party_member.character_name)
                
    children: list[BehaviorTree | BehaviorTree.Node] = []
    if players_to_kick:
        ConsoleLog("SetupPlayers", f'Players to kick: {players_to_kick}', log=log)
        children.append(KickPlayers(players_to_kick, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupPlayers", 'No players to kick.', log=log)
        
    if players_to_invite:
        ConsoleLog("SetupPlayers", f'Players to invite: {players_to_invite}', log=log)
        children.append(InvitePlayers(players_to_invite, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupPlayers", 'No players to invite.', log=log)
        
    if players_to_send_template:
        ConsoleLog("SetupPlayers", f'Players to send template request to: {players_to_send_template}', log=log)
        children.append(SendTemplateRequestToPlayers(players_to_send_template, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupPlayers", 'No players to send template request to.', log=log)
    
    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="SetupPlayers",
            children=children
        )
    )
    
def RequestAddHero(account_email : str, heroes : list[int | HeroType | str], template: str, timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _request() -> BehaviorTree.NodeState:        
        available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
        account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
        
        if account is None:
            ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
            return BehaviorTree.NodeState.FAILURE
        
        current_party_players = _get_current_player_entries()
        if not any(player.account_email == account_email for player in current_party_players):
            ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
            return BehaviorTree.NodeState.FAILURE
        
        current_heroes = _get_party_heroes(account.AgentData.LoginNumber)
        heroes_to_add = [hero_identifier for hero_identifier in heroes if not any(hero.hero_id == _get_hero_type(hero_identifier) for hero in current_heroes)]
        if not heroes_to_add:
            ConsoleLog("RequestHeroFromAccount", f'All requested heroes are already in the party for account {account_email}.', log=log)
            return BehaviorTree.NodeState.SUCCESS
        
        for hero_identifier in heroes:
            hero_type = _get_hero_type(hero_identifier)
            
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
        
        current_party_players = _get_current_player_entries()
        if not any(player.account_email == account_email for player in current_party_players):
            ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
            return True
        
        current_heroes = _get_party_heroes(account.AgentData.LoginNumber)
        heroes_to_add = [hero_identifier for hero_identifier in heroes if not any(hero.hero_id == _get_hero_type(hero_identifier) for hero in current_heroes)]
        if not heroes_to_add:
            ConsoleLog("RequestHeroFromAccount", f'All requested heroes are already in the party for account {account_email}.', log=log)
            return True
        
        for hero_identifier in heroes:
            hero_type = _get_hero_type(hero_identifier)
            
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

def RequestLoadHeroTemplate(account_email : str, heroes : list[tuple[int | HeroType | str, str]], template: str, timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _request() -> BehaviorTree.NodeState:        
        for hero_identifier, template in heroes:
            hero_type = _get_hero_type(hero_identifier)
            
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

def RequestKickHero(account_email : str, heroes : list[int | HeroType | str], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    def _request() -> BehaviorTree.NodeState:  
        available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
        account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
        
        if account is None:
            ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
            return BehaviorTree.NodeState.FAILURE
        
        current_party_players = _get_current_player_entries()
        if not any(player.account_email == account_email for player in current_party_players):
            ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
            return BehaviorTree.NodeState.FAILURE
        
        current_heroes = _get_party_heroes(account.AgentData.LoginNumber)      
        for hero_identifier in heroes:
            hero_type = _get_hero_type(hero_identifier)
            
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
        
        current_party_players = _get_current_player_entries()
        if not any(player.account_email == account_email for player in current_party_players):
            ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
            return True
        
        current_heroes = _get_party_heroes(account.AgentData.LoginNumber)      
        for hero_identifier in heroes:
            hero_type = _get_hero_type(hero_identifier)
            
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

def RequestHeroSetup(account_email : str, heroes : list[tuple[int | HeroType | str, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
    available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
    account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
    
    if account is not None:
        ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
        current_party_players = _get_current_player_entries()
        
        
        if any(player.account_email == account_email for player in current_party_players):
            ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
            
            current_heroes = _get_party_heroes(account.AgentData.LoginNumber)
            heroes_to_kick = [hero for hero in current_heroes if not any(hero.hero_id == _get_hero_type(hero_identifier) for hero_identifier, _ in heroes)]
            heroes_to_add = [hero_identifier for hero_identifier, _ in heroes if not any(hero.hero_id == _get_hero_type(hero_identifier) for hero in current_heroes)]
            
            children: list[BehaviorTree | BehaviorTree.Node] = []
            if heroes_to_kick:
                ConsoleLog("RequestHeroFromAccount", f'Heroes to kick from account {account_email}: {[hero.name for hero in heroes_to_kick]}', log=log)
                for hero in heroes_to_kick:
                    children.append(RequestKickHero(account_email, [hero.hero_id], timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("RequestHeroFromAccount", f'No heroes to kick from account {account_email}.', log=log)
                
            if heroes_to_add:
                ConsoleLog("RequestHeroFromAccount", f'Heroes to add from account {account_email}: {heroes_to_add}', log=log)
                children.append(RequestAddHero(account_email, heroes_to_add, template='', timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("RequestHeroFromAccount", f'No heroes to add from account {account_email}.', log=log)
        
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="RequestHeroSetup",
                    children=children
                )
            )
    
    return BehaviorTree(
        BehaviorTree.FailerNode(
            name="RequestHeroSetup",
        )
    )
    
def SetupPartyFormation_NEW(
    henchmen : list[int | str],
    heroes : list[int | HeroType | str | tuple[int | HeroType | str, Optional[str]]],
    players : list[str | int | tuple[str | int, Optional[str]]],
    account_heroes : list[tuple[str, list[tuple[int | HeroType | str, Optional[str]]]]],
    timeout_ms: int = 15000,
    poll_interval_ms: int = 100,
    aftercast_ms: int = 150,
    log: bool = False,
    ) -> BehaviorTree:
    
    children: list[BehaviorTree | BehaviorTree.Node] = []
    if henchmen:
        ConsoleLog("SetupPartyFormation", f'Setting up henchmen: {henchmen}', log=log)
        children.append(SetupHenchmen(henchmen, log=log))
    else:
        ConsoleLog("SetupPartyFormation", 'No henchmen to set up.', log=log)
        
    if heroes:
        ConsoleLog("SetupPartyFormation", f'Setting up heroes: {heroes}', log=log)
        children.append(SetupHeroes(heroes, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupPartyFormation", 'No heroes to set up.', log=log)
        
    if players:
        ConsoleLog("SetupPartyFormation", f'Setting up players: {players}', log=log)
        children.append(SetupPlayers(players, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
    else:
        ConsoleLog("SetupPartyFormation", 'No players to set up.', log=log)
        
    for account_email, account_hero_list in account_heroes:
        ConsoleLog("SetupPartyFormation", f'Setting up heroes for account {account_email}: {account_hero_list}', log=log)
        children.append(RequestHeroSetup(account_email, account_hero_list, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
    
    return BehaviorTree(
        BehaviorTree.SequenceNode(
            name="SetupPartyFormation",
            children=children
        )
    )
