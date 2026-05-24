from typing import NamedTuple, Optional
from collections.abc import Sequence as SequenceABC

from PyParty import HenchmanPartyMember, HeroPartyMember

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
from Py4GWCoreLib.native_src.context.AgentContext import AgentLivingStruct
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Sources.ApoSource.ApoBottingLib.wrappers import InviteAccountByEmail, SummonAccountByEmail, Wait

def _normalized(name : str) -> str:
    return str(name or '').strip().lower().split('[')[0].strip()

HenchmanEntry = NamedTuple("HenchmanEntry", [
    ("agent_id", int),
    ("primary", int),
    ("level", int),
    ("name", str),
    ("name_normalized", str),
]) 

class Henchmen:
    @staticmethod
    def _get_henchman_entry(agent_or_henchman : AgentLivingStruct |HenchmanPartyMember) -> Optional[HenchmanEntry]:
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
                    if entry := Henchmen._get_henchman_entry(living_agent):
                        henchmen.append(entry)
        return henchmen

    @staticmethod
    def _get_henchman(identifier : int | str | SequenceABC[int], available_henchmen: SequenceABC[HenchmanEntry]) -> Optional[HenchmanEntry]:        
        if isinstance(identifier, str):
            for henchman in available_henchmen:
                if henchman.name_normalized == _normalized(identifier):
                    return henchman
        
        if isinstance(identifier, int):
            if (agent := Agent.GetAgentByID(identifier)) and (living_agent := agent.GetAsAgentLiving()) and living_agent is not None:
                return Henchmen._get_henchman_entry(living_agent) 
        
        return None
        
    @staticmethod
    def InviteHenchmen(henchman_ids: SequenceABC[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _invite() -> BehaviorTree.NodeState:
            available_henchmen = Henchmen._get_available_henchmen()
            in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := Henchmen._get_henchman_entry(party_henchman)) is not None]
            desired_henchmen: list[HenchmanEntry] = [henchman for identifier in henchman_ids if (henchman := Henchmen._get_henchman(identifier, available_henchmen)) is not None]
            
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
    def KickHenchmen(henchman_ids: SequenceABC[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _kick() -> BehaviorTree.NodeState:
            if len(henchman_ids) == 0:
                ConsoleLog("KickHenchmen", 'No henchmen specified to kick.', log=log)
                return BehaviorTree.NodeState.SUCCESS
            
            in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := Henchmen._get_henchman_entry(party_henchman)) is not None]
            desired_kick_henchmen: list[HenchmanEntry] = [henchman for identifier in henchman_ids if (henchman := Henchmen._get_henchman(identifier, in_party_henchmen)) is not None]
            
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
    def SetupHenchmen(henchmen : SequenceABC[int | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        available_henchmen = Henchmen._get_available_henchmen()
        desired_henchmen: list[HenchmanEntry] = [henchman for identifier in henchmen if (henchman := Henchmen._get_henchman(identifier, available_henchmen)) is not None]
        
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
        
        in_party_henchmen = [henchman for party_henchman in (Party.GetHenchmen() or []) if (henchman := Henchmen._get_henchman_entry(party_henchman)) is not None]
        henchmen_to_kick: list[int | str] = [henchman.agent_id for henchman in in_party_henchmen if not any(henchman.agent_id == desired.agent_id for desired in desired_henchmen)]
        henchmen_to_add: list[int | str] = [henchman.agent_id for henchman in desired_henchmen if not any(henchman.agent_id == party.agent_id for party in in_party_henchmen)]
        
        
        children: list[BehaviorTree | BehaviorTree.Node] = []
        if henchmen_to_kick:
            ConsoleLog("SetupHenchmen", f'Henchmen to kick: {henchmen_to_kick}', log=log)
            children.append(Henchmen.KickHenchmen(henchmen_to_kick, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupHenchmen", 'No henchmen to kick.', log=log)
        
        if henchmen_to_add:
            ConsoleLog("SetupHenchmen", f'Henchmen to add: {henchmen_to_add}', log=log)
            children.append(Henchmen.InviteHenchmen(henchmen_to_add, aftercast_ms=aftercast_ms, log=log))
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
    def _get_hero_map(heroes : SequenceABC[int | HeroType | str], log: bool = False) -> list[HeroeEntry]:
        mapped_heroes: list[HeroeEntry] = []
        for hero_identifier in heroes:
            hero_type = Heroes._get_hero_type(hero_identifier)
            
            if hero_type is not None and Heroes._is_hero_available(hero_type):
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
                if (hero_entry := Heroes._get_hero_entry(party_hero)) is not None:
                    party_heroes.append(hero_entry)

        return party_heroes
        
    @staticmethod
    def InviteHeroes(heroes : SequenceABC[int | HeroType | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _invite() -> BehaviorTree.NodeState:
            mapped_heroes = Heroes._get_hero_map(heroes, log=log)
            if not mapped_heroes:
                return BehaviorTree.NodeState.FAILURE
                    
            in_party_heroes =  Heroes._get_party_heroes(Player.GetLoginNumber())
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
    def LoadHeroTemplates(heroes : SequenceABC[tuple[int | HeroType | str, str]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _load_templates() -> BehaviorTree.NodeState:
            for hero_identifier, template in heroes:
                hero_type = Heroes._get_hero_type(hero_identifier)
                
                if hero_type is None:
                    ConsoleLog("LoadHeroTemplates", f'Could not resolve hero identifier: {hero_identifier}', log=log)
                    return BehaviorTree.NodeState.FAILURE
                
                in_party_heroes =  Heroes._get_party_heroes(Player.GetLoginNumber())
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
    def InviteHeroesAndLoadTemplates(heroes : SequenceABC[int | HeroType | str | tuple[int | HeroType | str, str]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
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
                    Heroes.InviteHeroes(heroes_to_invite, aftercast_ms=aftercast_ms, log=log),
                    Heroes.LoadHeroTemplates(heroes_to_load_templates, aftercast_ms=aftercast_ms, log=log),
                ]
            )
        )

    @staticmethod
    def KickHeroes(heroes : SequenceABC[int | HeroType | str], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _kick() -> BehaviorTree.NodeState:
            if len(heroes) == 0:
                ConsoleLog("KickHeroes", 'No heroes specified to kick.', log=log)
                return BehaviorTree.NodeState.SUCCESS
            
            mapped_heroes = Heroes._get_hero_map(heroes, log=log)
            if not mapped_heroes:
                return BehaviorTree.NodeState.FAILURE
                    
            in_party_heroes =  Heroes._get_party_heroes(Player.GetLoginNumber())
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
    def SetupHeroes(heroes : SequenceABC[int | HeroType | str | tuple[int | HeroType | str, Optional[str]]], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
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
        
        party_heroes = Heroes._get_party_heroes(Player.GetLoginNumber())
        for party_hero in party_heroes:
            if not any(
                (party_hero.hero_id == Heroes._get_hero_type(hero) if not isinstance(hero, tuple) else party_hero.hero_id == Heroes._get_hero_type(hero[0]))
                for hero in heroes
            ):
                heroes_to_kick.append(party_hero.hero_id)
        
        children: list[BehaviorTree | BehaviorTree.Node] = []
        if heroes_to_kick:
            ConsoleLog("SetupHeroes", f'Heroes to kick: {heroes_to_kick}', log=log)
            children.append(Heroes.KickHeroes(heroes_to_kick, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupHeroes", 'No heroes to kick.', log=log)
            
        
        if heroes_to_invite:
            ConsoleLog("SetupHeroes", f'Heroes to invite: {heroes_to_invite}', log=log)
            children.append(Heroes.InviteHeroes(heroes_to_invite, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupHeroes", 'No heroes to invite.', log=log)
            
        if heroes_to_load_templates:
            ConsoleLog("SetupHeroes", f'Heroes to load templates for: {heroes_to_load_templates}', log=log)
            children.append(Heroes.LoadHeroTemplates(heroes_to_load_templates, aftercast_ms=aftercast_ms, log=log))
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
            
            if agent and (entry := Multiboxing._get_player_entry(agent.agent_id)) is not None:
                player_entries.append(entry)
                
        return player_entries

    @staticmethod
    def InvitePlayers(players : SequenceABC[str | int], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def invite_players(
            players: SequenceABC[str | int],
            timeout_ms: int = 15000,
            poll_interval_ms: int = 100,
            aftercast_ms: int = 150,
            log: bool = False,
        ) -> BehaviorTree:
            childs: list[BehaviorTree | BehaviorTree.Node] = []

            for identifier in players:
                entry = Multiboxing._get_player_entry(identifier)
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
                                    for player in Multiboxing._get_current_player_entries()
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
    def SendTemplateRequestToPlayers(players : SequenceABC[tuple[str | int, str]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _send_template_request() -> BehaviorTree.NodeState:
            for identifier, template in players:
                if not template:
                    continue 
                
                entry = Multiboxing._get_player_entry(identifier)
                
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
    def InvitePlayersAndSendTemplateRequest(players_and_templates : SequenceABC[tuple[str | int, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        players = [identifier for identifier, _ in players_and_templates]
        templates = [(identifier, template) for identifier, template in players_and_templates if template]
        
        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name="InvitePlayersAndSendTemplateRequest",
                children=[
                    Multiboxing.InvitePlayers(players, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log),
                    Multiboxing.SendTemplateRequestToPlayers(templates, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log),
                ]
            )
        )

    @staticmethod
    def KickPlayers(players : SequenceABC[str | int], aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _kick() -> BehaviorTree.NodeState:
            current_party = Multiboxing._get_current_player_entries()
            for identifier in players:
                entry = Multiboxing._get_player_entry(identifier)
                
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
    def SetupPlayers(players : SequenceABC[str | int | tuple[str | int, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        players_to_invite: list[str | int] = []
        players_to_send_template: list[tuple[str | int, str]] = []
        players_to_kick: list[str | int] = []
        
        current_party = Multiboxing._get_current_player_entries()
        
        for player in players:
            if isinstance(player, tuple) and len(player) == 2:
                player_identifier, template = player
                players_to_invite.append(player_identifier)
                if template:
                    players_to_send_template.append((player_identifier, template))
                
            else:
                players_to_invite.append(player)

        desired_entries = [player for identifier in players_to_invite if (player := Multiboxing._get_player_entry(identifier)) is not None]
                
        for party_member in current_party:
            if not any(party_member.character_name_normalized == entry.character_name_normalized for entry in desired_entries):
                if party_member.character_name != Player.GetName():
                    players_to_kick.append(party_member.character_name)
                    
        children: list[BehaviorTree | BehaviorTree.Node] = []
        if players_to_kick:
            ConsoleLog("SetupPlayers", f'Players to kick: {players_to_kick}', log=log)
            children.append(Multiboxing.KickPlayers(players_to_kick, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupPlayers", 'No players to kick.', log=log)
            
        if players_to_invite:
            ConsoleLog("SetupPlayers", f'Players to invite: {players_to_invite}', log=log)
            children.append(Multiboxing.InvitePlayers(players_to_invite, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupPlayers", 'No players to invite.', log=log)
            
        if players_to_send_template:
            ConsoleLog("SetupPlayers", f'Players to send template request to: {players_to_send_template}', log=log)
            children.append(Multiboxing.SendTemplateRequestToPlayers(players_to_send_template, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupPlayers", 'No players to send template request to.', log=log)
        
        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name="SetupPlayers",
                children=children
            )
        )
        
    @staticmethod
    def RequestAddHero(account_email : str, heroes : SequenceABC[int | HeroType | str], template: str, timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _request() -> BehaviorTree.NodeState:        
            available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
            account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
            
            if account is None:
                ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                return BehaviorTree.NodeState.FAILURE
            
            current_party_players = Multiboxing._get_current_player_entries()
            if not any(player.account_email == account_email for player in current_party_players):
                ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                return BehaviorTree.NodeState.FAILURE
            
            current_heroes = Heroes._get_party_heroes(account.AgentData.LoginNumber)
            heroes_to_add = [hero_identifier for hero_identifier in heroes if not any(hero.hero_id == Heroes._get_hero_type(hero_identifier) for hero in current_heroes)]
            if not heroes_to_add:
                ConsoleLog("RequestHeroFromAccount", f'All requested heroes are already in the party for account {account_email}.', log=log)
                return BehaviorTree.NodeState.SUCCESS
            
            for hero_identifier in heroes:
                hero_type = Heroes._get_hero_type(hero_identifier)
                
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
            
            current_party_players = Multiboxing._get_current_player_entries()
            if not any(player.account_email == account_email for player in current_party_players):
                ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                return True
            
            current_heroes = Heroes._get_party_heroes(account.AgentData.LoginNumber)
            heroes_to_add = [hero_identifier for hero_identifier in heroes if not any(hero.hero_id == Heroes._get_hero_type(hero_identifier) for hero in current_heroes)]
            if not heroes_to_add:
                ConsoleLog("RequestHeroFromAccount", f'All requested heroes are already in the party for account {account_email}.', log=log)
                return True
            
            for hero_identifier in heroes:
                hero_type = Heroes._get_hero_type(hero_identifier)
                
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
    def RequestLoadHeroTemplate(account_email : str, heroes : SequenceABC[tuple[int | HeroType | str, str]], template: str, timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _request() -> BehaviorTree.NodeState:        
            for hero_identifier, template in heroes:
                hero_type = Heroes._get_hero_type(hero_identifier)
                
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
    def RequestKickHero(account_email : str, heroes : SequenceABC[int | HeroType | str], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _request() -> BehaviorTree.NodeState:  
            available_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData() or []
            account = next((entry for entry in available_accounts if entry.AccountEmail == account_email), None)
            
            if account is None:
                ConsoleLog("RequestHeroFromAccount", f'No available account found with email: {account_email}', log=log)
                return BehaviorTree.NodeState.FAILURE
            
            current_party_players = Multiboxing._get_current_player_entries()
            if not any(player.account_email == account_email for player in current_party_players):
                ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                return BehaviorTree.NodeState.FAILURE
            
            current_heroes = Heroes._get_party_heroes(account.AgentData.LoginNumber)      
            for hero_identifier in heroes:
                hero_type = Heroes._get_hero_type(hero_identifier)
                
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
            
            current_party_players = Multiboxing._get_current_player_entries()
            if not any(player.account_email == account_email for player in current_party_players):
                ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                return True
            
            current_heroes = Heroes._get_party_heroes(account.AgentData.LoginNumber)      
            for hero_identifier in heroes:
                hero_type = Heroes._get_hero_type(hero_identifier)
                
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
    def RequestHeroSetup(account_email : str, heroes : SequenceABC[tuple[int | HeroType | str, Optional[str]]], timeout_ms: int = 15000, poll_interval_ms: int = 100, aftercast_ms: int = 150, log: bool = False) -> BehaviorTree:
        def _build_request_hero_setup_tree(
            account_email: str,
            heroes: SequenceABC[tuple[int | HeroType | str, Optional[str]]],
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

            current_party_players = Multiboxing._get_current_player_entries()
            if not any(player.account_email == account_email for player in current_party_players):
                ConsoleLog("RequestHeroFromAccount", f'Account with email {account_email} is not currently in the party, cannot request hero.', log=log)
                return BehaviorTree(
                    BehaviorTree.FailerNode(
                        name="RequestHeroSetup",
                    )
                )

            current_heroes = Heroes._get_party_heroes(account.AgentData.LoginNumber)
            heroes_to_kick = [hero for hero in current_heroes if not any(hero.hero_id == Heroes._get_hero_type(hero_identifier) for hero_identifier, _ in heroes)]
            heroes_to_add = [hero_identifier for hero_identifier, _ in heroes if not any(hero.hero_id == Heroes._get_hero_type(hero_identifier) for hero in current_heroes)]

            children: list[BehaviorTree | BehaviorTree.Node] = []
            if heroes_to_kick:
                ConsoleLog("RequestHeroFromAccount", f'Heroes to kick from account {account_email}: {[hero.name for hero in heroes_to_kick]}', log=log)
                for hero in heroes_to_kick:
                    children.append(Multiboxing.RequestKickHero(account_email, [hero.hero_id], timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("RequestHeroFromAccount", f'No heroes to kick from account {account_email}.', log=log)

            if heroes_to_add:
                ConsoleLog("RequestHeroFromAccount", f'Heroes to add from account {account_email}: {heroes_to_add}', log=log)
                children.append(Multiboxing.RequestAddHero(account_email, heroes_to_add, template='', timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
            else:
                ConsoleLog("RequestHeroFromAccount", f'No heroes to add from account {account_email}.', log=log)
                
            for hero_identifier, template in heroes:
                if template:
                    hero_type = Heroes._get_hero_type(hero_identifier)
                    if hero_type is not None:
                        ConsoleLog("RequestHeroFromAccount", f'Will request to load template for hero {hero_type.name} (ID: {hero_type}) on account {account_email}.', log=log)
                        children.append(Multiboxing.RequestLoadHeroTemplate(account_email, [(hero_identifier, template)], template, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
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

def SetupPartyFormation(
    henchmen : SequenceABC[int | str],
    heroes : SequenceABC[int | HeroType | str | tuple[int | HeroType | str, Optional[str]]],
    players : SequenceABC[str | int | tuple[str | int, Optional[str]]],
    account_heroes : SequenceABC[tuple[str, SequenceABC[tuple[int | HeroType | str, Optional[str]]]]],
    timeout_ms: int = 15000,
    poll_interval_ms: int = 100,
    aftercast_ms: int = 150,
    log: bool = False,
    ) -> BehaviorTree:

        children: list[BehaviorTree | BehaviorTree.Node] = []
        if henchmen:
            ConsoleLog("SetupPartyFormation", f'Setting up henchmen: {henchmen}', log=log)
            children.append(Henchmen.SetupHenchmen(henchmen, log=log))
        else:
            ConsoleLog("SetupPartyFormation", 'No henchmen to set up.', log=log)
            
        if heroes:
            ConsoleLog("SetupPartyFormation", f'Setting up heroes: {heroes}', log=log)
            children.append(Heroes.SetupHeroes(heroes, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupPartyFormation", 'No heroes to set up.', log=log)
            
        if players:
            ConsoleLog("SetupPartyFormation", f'Setting up players: {players}', log=log)
            children.append(Multiboxing.SetupPlayers(players, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
        else:
            ConsoleLog("SetupPartyFormation", 'No players to set up.', log=log)
            
        for account_email, account_hero_list in account_heroes:
            ConsoleLog("SetupPartyFormation", f'Setting up heroes for account {account_email}: {account_hero_list}', log=log)
            children.append(Multiboxing.RequestHeroSetup(account_email, account_hero_list, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms, aftercast_ms=aftercast_ms, log=log))
        
        return BehaviorTree(
            BehaviorTree.SequenceNode(
                name="SetupPartyFormation",
                children=children
            )
        )
