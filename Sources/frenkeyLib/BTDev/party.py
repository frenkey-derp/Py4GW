from typing import Any, Optional, cast
from typing import Mapping
from typing import TypedDict
from typing import TypeVar
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC

import Py4GW
from PySkillbar import Skillbar

from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.shared_memory_src.AccountStruct import AccountStruct
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Party import Party
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Skillbar import SkillBar
from Py4GWCoreLib.enums_src.Hero_enums import HeroType
from Py4GWCoreLib.enums_src.Multiboxing_enums import SharedCommandType
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Py4GWCoreLib.routines_src.yield_src import player
from Sources.ApoSource.ApoBottingLib.wrappers import InviteAccountByEmail, LeaveParty, LoadSkillbar, SummonAccountByEmail
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
