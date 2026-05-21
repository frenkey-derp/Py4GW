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
    
    Py4GW.Console.Log("Test", f"Setting up party with formation: {party_formation}, multibox_invite: {multibox_invite}, timeout_ms: {timeout_ms}, poll_interval_ms: {poll_interval_ms}, aftercast_ms: {aftercast_ms}, log: {log}")
    
    all_accs = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
    own_mail = str(Player.GetAccountEmail() or "")
    own_acc = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(own_mail) if own_mail else None
    party_members = Party.GetPlayers() or []
    
    Py4GW.Console.Log("Test", f"Own account: {own_acc}, Party members: {party_members}")
    
    if not own_acc:
        Py4GW.Console.Log("Test", "Own account data not found in shared memory. Aborting party setup.")
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
    
    def _resolve_current_henchman_id(henchman: Any) -> int:
        for attr_name in ('henchman_id', 'id'):
            resolved_id = int(getattr(henchman, attr_name, 0) or 0)
            if resolved_id > 0:
                return resolved_id

        agent_id = int(getattr(henchman, 'agent_id', 0) or 0)
        if agent_id <= 0:
            return 0
        return int(Agent.GetPlayerNumber(agent_id) or 0)

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
        current_henchmen = [_resolve_current_henchman_id(henchman) for henchman in (Party.GetHenchmen() or [])]
        current_heroes = [(_get_owner_name(hero.owner_player_id), (hero.hero_id.GetID(), "")) for hero in (Party.GetHeroes() or [])]
        local_login_number = int(Player.GetLoginNumber() or 0)
        current_players = [
            (str(Party.Players.GetPlayerNameByLoginNumber(int(getattr(player, "login_number", 0) or 0)) or "").strip(), "")
            for player in (Party.GetPlayers() or [])
            if int(getattr(player, "login_number", 0) or 0) > 0 and int(getattr(player, "login_number", 0) or 0) != local_login_number
        ]
        
        return current_henchmen, current_heroes, current_players
    
    def _kick_unwanted(current : tuple[HenchmenFormation, HeroesFormation, PlayersFormation], desired: tuple[HenchmenFormation, HeroesFormation, PlayersFormation]) -> BehaviorTree:
        current_henchmen, current_heroes, current_players = current
        desired_henchmen, desired_heroes, desired_players = desired
        
        for henchman_id in current_henchmen:
            if henchman_id not in desired_henchmen:
                Party.Henchmen.KickHenchman(henchman_id)
        
        for hero_id in current_heroes:
                # Party.Heroes.KickHero(hero_id)
            pass
                
        for (player_name, _) in current_players:
            if not any(player_name == desired_player_name for (desired_player_name, _) in desired_players):
                Party.Players.KickPlayer(player_name)      
        
        return BehaviorTree(
            BehaviorTree.SucceederNode(name="KickUnwanted")
        )
    
    def _apply_templates(desired: tuple[HenchmenFormation, HeroesFormation, PlayersFormation]) -> BehaviorTree:
        _, desired_heroes, desired_players = desired
        children: list[BehaviorTree | BehaviorTree.Node] = []
        
        player_id = Player.GetPlayerNumber()
        heroes = Party.GetHeroes() or []
        handled_hero_index: set[int] = set()
        skillbar = SkillBar()
        
        for hero_index, (hero_owner, (hero_id, template)) in enumerate(desired_heroes):
            if template:
                if hero_owner == own_acc.AgentData.CharacterName:
                    skillbar.LoadHeroSkillTemplate(hero_id, template)
                else:
                    acc = _get_owner_account(hero_owner)
                    GLOBAL_CACHE.ShMem.SendMessage(own_acc.AgentData.CharacterName, hero_owner, SharedCommandType.LoadSkillTemplateOnHero, (0.0, 0.0, 0.0, 0.0), (hero_id, template, "", ""))
                                        
        for player_name, template in desired_players:
            if template:
                if player_name == own_acc.AgentData.CharacterName:
                    skillbar.LoadSkillTemplate(template)
                
                else:
                    acc = _get_owner_account(player_name)    
                    if acc is not None and str(acc.AccountEmail or "").strip().lower() != own_mail:
                        GLOBAL_CACHE.ShMem.SendMessage(own_mail, acc.AccountEmail, SharedCommandType.LoadSkillTemplate, (0.0, 0.0, 0.0, 0.0), (template, "", "", ""))
        
        return RoutinesBT.Composite.Sequence(*children, name="ApplyTemplates")
    
    
    Py4GW.Console.Log("Test", "Composing current party formation...")
    current_formation = _get_current_formation()
    current_henchmen, current_heroes, current_players = current_formation
    Py4GW.Console.Log("Test", f"Current henchmen: {current_henchmen}, heroes: {current_heroes}, players: {current_players}")
        
    Py4GW.Console.Log("Test", "Parsing desired party formation...")    
    desired_formation = _parse_party_formation(own_acc.AgentData.CharacterName, party_formation)
    desired_henchmen, desired_heroes, desired_players = desired_formation
    Py4GW.Console.Log("Test", f"Desired henchmen: {desired_henchmen}, heroes: {desired_heroes}, players: {desired_players}")
        
    # _kick_tree = _kick_unwanted(current_formation, desired_formation)
    
    Py4GW.Console.Log("Test", "Applying desired party formation...")
    
    return BehaviorTree(
        BehaviorTree.SubtreeNode(
            name="SetupParty",
            subtree_fn=lambda _: BehaviorTree.SucceederNode(name="SetupPartyPlaceholder"),
        )
    )

def SetupParty(
    hero_ids: list[int] | None = None,
    henchman_ids: list[int] | None = None,
    player_names: list[str] | None = None,
    hero_templates: Mapping[int, str] | SequenceABC[str] | None = None,
    player_templates: Mapping[str, str] | None = None,
    multibox_invite: bool = False,
    timeout_ms: int = 15000,
    poll_interval_ms: int = 100,
    aftercast_ms: int = 250,
    log: bool = False,
) -> BehaviorTree:
    desired_hero_ids = [int(hero_id) for hero_id in (hero_ids or []) if int(hero_id) > 0]
    desired_henchman_ids = [int(henchman_id) for henchman_id in (henchman_ids or []) if int(henchman_id) > 0]
    desired_player_specs = [str(player_name or "").strip() for player_name in (player_names or []) if str(player_name or "").strip()]

    normalized_hero_templates: dict[int, str] = {}
    if isinstance(hero_templates, Mapping):
        for hero_id, template_code in hero_templates.items():
            resolved_hero_id = int(hero_id)
            resolved_template = str(template_code or "").strip()
            if resolved_hero_id > 0 and resolved_template:
                normalized_hero_templates[resolved_hero_id] = resolved_template
    elif hero_templates is not None:
        for hero_id, template_code in zip(desired_hero_ids, hero_templates):
            resolved_template = str(template_code or "").strip()
            if resolved_template:
                normalized_hero_templates[int(hero_id)] = resolved_template

    normalized_player_templates = {
        str(key or "").strip().lower(): str(value or "").strip()
        for key, value in (player_templates or {}).items()
        if str(key or "").strip() and str(value or "").strip()
    }

    def _normalized(value: object) -> str:
        return str(value or "").strip().lower()

    def _shared_accounts() -> list[Any]:
        return [
            account
            for account in (GLOBAL_CACHE.ShMem.GetAllAccountData() or [])
            if bool(getattr(account, "IsSlotActive", True)) and bool(getattr(account, "IsAccount", True))
        ]

    def _account_email(account: Any) -> str:
        return str(getattr(account, "AccountEmail", "") or "").strip()

    def _account_character_name(account: Any) -> str:
        return str(
            getattr(account, "CharacterName", "")
            or getattr(getattr(account, "AgentData", None), "CharacterName", "")
            or ""
        ).strip()

    def _account_is_in_local_party(account: Any) -> bool:
        if not Party.IsPartyLoaded():
            return False
        local_party_id = int(Party.GetPartyID() or 0)
        if local_party_id <= 0:
            return False
        return int(getattr(getattr(account, "AgentPartyData", None), "PartyID", 0) or 0) == local_party_id

    def _resolve_shared_account(player_spec: str) -> Any | None:
        wanted = _normalized(player_spec)
        if not wanted:
            return None
        for account in _shared_accounts():
            if wanted in {_normalized(_account_email(account)), _normalized(_account_character_name(account))}:
                return account
        return None

    def _resolve_player_template(raw_spec: str, shared_account: Any | None, character_name: str) -> str:
        lookup_keys = [_normalized(raw_spec), _normalized(character_name)]
        if shared_account is not None:
            lookup_keys.insert(1, _normalized(_account_email(shared_account)))
        for lookup_key in lookup_keys:
            if lookup_key and lookup_key in normalized_player_templates:
                return normalized_player_templates[lookup_key]
        return ""

    local_email = str(Player.GetAccountEmail() or "").strip()
    local_name = str(Player.GetName() or "").strip()
    local_name_key = _normalized(local_name)
    local_email_key = _normalized(local_email)

    desired_party_players: list[_PartyPlayerEntry] = []
    local_player_template = ""
    seen_player_keys: set[str] = set()
    source_player_specs = desired_player_specs or (
        [_account_email(account) for account in _shared_accounts() if _normalized(_account_email(account)) != local_email_key]
        if multibox_invite else
        []
    )

    for raw_spec in source_player_specs:
        shared_account = _resolve_shared_account(raw_spec)
        resolved_name = _account_character_name(shared_account) if shared_account is not None else str(raw_spec).strip()
        resolved_email = _account_email(shared_account) if shared_account is not None else ""
        template_code = _resolve_player_template(raw_spec, shared_account, resolved_name)

        if (shared_account is not None and _normalized(resolved_email) == local_email_key) or _normalized(resolved_name) == local_name_key:
            if template_code:
                local_player_template = template_code
            continue

        dedupe_key = _normalized(resolved_email or resolved_name)
        if not dedupe_key or dedupe_key in seen_player_keys:
            continue
        seen_player_keys.add(dedupe_key)
        desired_party_players.append({
            "spec": str(raw_spec),
            "shared_account": shared_account,
            "email": resolved_email,
            "character_name": resolved_name,
            "template": template_code,
        })

    def _current_other_player_names() -> list[str]:
        local_login_number = int(Player.GetLoginNumber() or 0)
        names: list[str] = []
        for player in (Party.GetPlayers() or []):
            login_number = int(getattr(player, "login_number", 0) or 0)
            if login_number <= 0 or login_number == local_login_number:
                continue
            name = str(Party.Players.GetPlayerNameByLoginNumber(login_number) or "").strip()
            if name:
                names.append(name)
        return names

    def _desired_other_player_names() -> list[str]:
        return [str(entry["character_name"] or "").strip() for entry in desired_party_players if str(entry["character_name"] or "").strip()]

    def _current_hero_ids() -> list[int]:
        return [int(hero.hero_id.GetID()) for hero in (Party.GetHeroes() or [])]

    def _current_other_player_name_keys() -> list[str]:
        return [_normalized(name) for name in _current_other_player_names() if _normalized(name)]

    def _resolve_current_henchman_id(henchman: Any) -> int:
        for attr_name in ('henchman_id', 'id'):
            resolved_id = int(getattr(henchman, attr_name, 0) or 0)
            if resolved_id > 0:
                return resolved_id

        agent_id = int(getattr(henchman, 'agent_id', 0) or 0)
        if agent_id <= 0:
            return 0
        return int(Agent.GetPlayerNumber(agent_id) or 0)

    def _current_henchman_entries() -> list[_CurrentHenchmanEntry]:
        entries: list[_CurrentHenchmanEntry] = []
        for henchman in (Party.GetHenchmen() or []):
            agent_id = int(getattr(henchman, 'agent_id', 0) or 0)
            entries.append({
                'resolved_id': _resolve_current_henchman_id(henchman),
                'agent_id': agent_id,
            })
        return entries

    def _current_henchman_ids() -> list[int]:
        return [entry['resolved_id'] for entry in _current_henchman_entries()]

    def _lcs_keep_indices(current_values: list[TValue], desired_values: list[TValue]) -> set[int]:
        rows = len(current_values)
        cols = len(desired_values)
        dp = [[0] * (cols + 1) for _ in range(rows + 1)]

        for row in range(rows - 1, -1, -1):
            for col in range(cols - 1, -1, -1):
                if current_values[row] == desired_values[col]:
                    dp[row][col] = dp[row + 1][col + 1] + 1
                else:
                    dp[row][col] = max(dp[row + 1][col], dp[row][col + 1])

        keep_indices: set[int] = set()
        row = 0
        col = 0
        while row < rows and col < cols:
            if current_values[row] == desired_values[col]:
                keep_indices.add(row)
                row += 1
                col += 1
            elif dp[row + 1][col] >= dp[row][col + 1]:
                row += 1
            else:
                col += 1

        return keep_indices

    def _build_desired_additions(current_values: list[TValue], desired_values: list[TValue]) -> list[TValue]:
        additions: list[TValue] = []
        current_index = 0
        current_len = len(current_values)

        for desired_value in desired_values:
            while current_index < current_len and current_values[current_index] != desired_value:
                current_index += 1
            if current_index < current_len:
                current_index += 1
                continue
            additions.append(desired_value)

        return additions

    def _party_matches_target() -> bool:
        if not (Map.IsMapReady() and Map.IsOutpost() and Party.IsPartyLoaded()):
            return False
        return (
            _current_hero_ids() == desired_hero_ids
            and _current_henchman_ids() == desired_henchman_ids
            and _current_other_player_name_keys() == [_normalized(name) for name in _desired_other_player_names() if _normalized(name)]
        )

    def _kick_player_by_name(player_name: str) -> BehaviorTree:
        return BehaviorTree(
            BehaviorTree.ActionNode(
                name=f"KickPlayer({player_name})",
                action_fn=lambda: (GLOBAL_CACHE.Party.Players.KickPlayer(str(player_name)), BehaviorTree.NodeState.SUCCESS)[1],
                aftercast_ms=aftercast_ms,
            )
        )

    def _invite_player_by_name(player_name: str) -> BehaviorTree:
        normalized_name = _normalized(player_name)
        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name=f"InvitePlayer({player_name})",
                children=[
                    BehaviorTree.ActionNode(
                        name=f"DispatchInvitePlayer({player_name})",
                        action_fn=lambda: (GLOBAL_CACHE.Party.Players.InvitePlayer(str(player_name)), BehaviorTree.NodeState.SUCCESS)[1],
                        aftercast_ms=aftercast_ms,
                    ),
                    BehaviorTree.WaitUntilNode(
                        name=f"WaitForInvitedPlayer({player_name})",
                        condition_fn=lambda: normalized_name in {_normalized(name) for name in _current_other_player_names()},
                        throttle_interval_ms=poll_interval_ms,
                        timeout_ms=timeout_ms,
                    ),
                ],
            )
        )

    def _send_skill_template_to_account(account_email: str, template_code: str) -> BehaviorTree:
        def _send() -> BehaviorTree.NodeState:
            sender_email = str(Player.GetAccountEmail() or "").strip()
            if not sender_email or not account_email or not template_code:
                return BehaviorTree.NodeState.FAILURE
            GLOBAL_CACHE.ShMem.SendMessage(
                sender_email,
                str(account_email),
                SharedCommandType.LoadSkillTemplate,
                (0.0, 0.0, 0.0, 0.0),
                (str(template_code), "", "", ""),
            )
            return BehaviorTree.NodeState.SUCCESS

        return BehaviorTree(
            BehaviorTree.ActionNode(
                name=f"LoadAccountSkillTemplate({account_email})",
                action_fn=_send,
                aftercast_ms=max(250, int(aftercast_ms)),
            )
        )

    def _template_actions() -> list[BehaviorTree | BehaviorTree.Node]:
        actions: list[BehaviorTree | BehaviorTree.Node] = []
        if local_player_template:
            actions.append(LoadSkillbar(local_player_template, log=log))
        for hero_index, hero_id in enumerate(desired_hero_ids, start=1):
            template_code = normalized_hero_templates.get(int(hero_id), "")
            if template_code:
                actions.append(RoutinesBT.Skills.LoadHeroSkillbar(hero_index=hero_index, template=template_code, log=log))
        for entry in desired_party_players:
            shared_account = entry["shared_account"]
            template_code = str(entry["template"] or "").strip()
            account_email = str(entry["email"] or "").strip()
            if shared_account is None or not template_code or not account_email or _normalized(account_email) == local_email_key:
                continue
            actions.append(_send_skill_template_to_account(account_email, template_code))
        return actions

    def _build_setup_party_subtree(_: BehaviorTree.Node) -> BehaviorTree | BehaviorTree.Node:
        if _party_matches_target():
            template_children = _template_actions()
            if not template_children:
                return BehaviorTree.SucceederNode(name="SetupPartyAlreadyMatches")
            return RoutinesBT.Composite.Sequence(*template_children, name="SetupPartyApplyTemplates")

        current_other_names = _current_other_player_names()
        if not Party.IsPartyLeader():
            if not desired_party_players and current_other_names:
                return BehaviorTree.SequenceNode(
                    name="SetupPartyLeaveUnexpectedPlayers",
                    children=[
                        LeaveParty().root,
                        BehaviorTree.SubtreeNode(
                            name="RetrySetupPartyAfterLeave",
                            subtree_fn=_build_setup_party_subtree,
                        ),
                    ],
                )
            return BehaviorTree.FailerNode(name="SetupPartyNotLeader")

        children: list[BehaviorTree | BehaviorTree.Node] = []

        desired_name_keys = [_normalized(name) for name in _desired_other_player_names() if _normalized(name)]
        keep_player_indices = _lcs_keep_indices(_current_other_player_name_keys(), desired_name_keys)
        for idx, current_name in enumerate(current_other_names):
            if idx in keep_player_indices:
                continue
            if _normalized(current_name) not in desired_name_keys or idx not in keep_player_indices:
                children.append(_kick_player_by_name(current_name))

        current_hero_ids = _current_hero_ids()
        keep_hero_indices = _lcs_keep_indices(current_hero_ids, desired_hero_ids)
        for idx, hero_id in enumerate(current_hero_ids):
            if idx in keep_hero_indices:
                continue

            def _make_kick_hero_action(resolved_hero_id: int):
                def _kick_hero_action() -> BehaviorTree.NodeState:
                    Party.Heroes.KickHero(resolved_hero_id)
                    return BehaviorTree.NodeState.SUCCESS
                return _kick_hero_action

            children.append(
                BehaviorTree.ActionNode(
                    name=f"KickHero({hero_id})",
                    action_fn=_make_kick_hero_action(hero_id),
                    aftercast_ms=aftercast_ms,
                )
            )

        current_henchman_entries = _current_henchman_entries()
        current_henchman_ids = [entry['resolved_id'] for entry in current_henchman_entries]
        if len(current_henchman_ids) != len(Party.GetHenchmen() or []):
            return BehaviorTree.FailerNode(name='SetupPartyUnresolvedHenchmen')

        keep_henchman_indices = _lcs_keep_indices(current_henchman_ids, desired_henchman_ids)
        for idx, current_henchman_entry in enumerate(current_henchman_entries):
            current_henchman_id = int(current_henchman_entry['resolved_id'])
            if idx in keep_henchman_indices or current_henchman_id <= 0:
                continue

            def _make_kick_henchman_action(resolved_henchman_id: int, agent_id: int):
                def _kick_henchman_action() -> BehaviorTree.NodeState:
                    candidate_ids: list[int] = []
                    for candidate_id in (resolved_henchman_id, agent_id):
                        candidate_id = int(candidate_id)
                        if candidate_id > 0 and candidate_id not in candidate_ids:
                            candidate_ids.append(candidate_id)
                    for candidate_id in candidate_ids:
                        Party.Henchmen.KickHenchman(candidate_id)
                    return BehaviorTree.NodeState.SUCCESS

                return _kick_henchman_action

            children.append(
                BehaviorTree.ActionNode(
                    name=f"KickHenchman({current_henchman_id})",
                    action_fn=_make_kick_henchman_action(current_henchman_id, int(current_henchman_entry['agent_id'])),
                    aftercast_ms=aftercast_ms,
                )
            )

        for hero_id in _build_desired_additions(current_hero_ids, desired_hero_ids):
            def _make_add_hero_action(resolved_hero_id: int):
                def _add_hero_action() -> BehaviorTree.NodeState:
                    Party.Heroes.AddHero(resolved_hero_id)
                    return BehaviorTree.NodeState.SUCCESS
                return _add_hero_action

            children.append(
                BehaviorTree.ActionNode(
                    name=f"AddHero({hero_id})",
                    action_fn=_make_add_hero_action(int(hero_id)),
                    aftercast_ms=aftercast_ms,
                )
            )

        for henchman_id in _build_desired_additions(current_henchman_ids, desired_henchman_ids):
            def _make_add_henchman_action(resolved_henchman_id: int):
                def _add_henchman_action() -> BehaviorTree.NodeState:
                    Party.Henchmen.AddHenchman(resolved_henchman_id)
                    return BehaviorTree.NodeState.SUCCESS

                return _add_henchman_action

            children.append(
                BehaviorTree.ActionNode(
                    name=f"AddHenchman({henchman_id})",
                    action_fn=_make_add_henchman_action(int(henchman_id)),
                    aftercast_ms=aftercast_ms,
                )
            )

        current_name_keys = _current_other_player_name_keys()
        desired_player_entries_by_name = {
            _normalized(str(entry["character_name"] or "").strip()): entry
            for entry in desired_party_players
            if _normalized(str(entry["character_name"] or "").strip())
        }
        for desired_name_key in _build_desired_additions(current_name_keys, desired_name_keys):
            entry = desired_player_entries_by_name.get(str(desired_name_key), None)
            if entry is None:
                continue

            character_name = str(entry["character_name"] or "").strip()
            shared_account = entry["shared_account"]
            account_email = str(entry["email"] or "").strip()
            if shared_account is not None and multibox_invite and account_email:
                children.append(SummonAccountByEmail(account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
                children.append(InviteAccountByEmail(account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
            elif shared_account is not None and account_email:
                children.append(InviteAccountByEmail(account_email, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, log=log))
            else:
                children.append(_invite_player_by_name(character_name))

        if children:
            children.append(
                BehaviorTree.WaitUntilNode(
                    name="WaitForSetupPartyMatch",
                    condition_fn=_party_matches_target,
                    throttle_interval_ms=poll_interval_ms,
                    timeout_ms=timeout_ms,
                )
            )

        children.extend(_template_actions())

        if not children:
            return BehaviorTree.SucceederNode(name="SetupPartyEmpty")

        return RoutinesBT.Composite.Sequence(*children, name="SetupPartyReconcile")

    return BehaviorTree(
        BehaviorTree.SubtreeNode(
            name="SetupParty",
            subtree_fn=_build_setup_party_subtree,
        )
    )
