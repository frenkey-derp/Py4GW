
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Chest


class ChestsCollector(ListCollector[Chest]):
    def __init__(self, get_local_path, get_default_path, *, version = '1.0', value_type = None, key_decoder = None, key_encoder = None):
        super().__init__(get_local_path, get_default_path, version=version, value_type=value_type, key_decoder=key_decoder, key_encoder=key_encoder)
        self.map_chests : list[Chest] = []

    @staticmethod
    def _identity_key(*, model_id: int, encoded_name: bytes, name: str) -> tuple[str, object]:
        if model_id != 0:
            return ('model_id', model_id)

        if encoded_name:
            return ('encoded_name', encoded_name)

        return ('name', name.strip().lower())
        
    def _collect(self):        
        agent_ids = AgentArray.GetGadgetArray()
        map_id = Map.GetBaseMapID()
        collected_matching_chests : dict[tuple[str, object], list[Chest]] = {}
        
        for agent_id in agent_ids:
            if agent_id in self.checked_ids:
                continue
            
            name = Agent.GetNameByID(agent_id) or ''
            if not name:
                continue

            if 'chest' not in name.lower():
                self.mark_id_as_checked(agent_id)
                continue

            model_id = Agent.GetModelID(agent_id)
            enc_name = bytes(Agent.GetEncNameByID(agent_id))
            identity_key = self._identity_key(model_id=model_id, encoded_name=enc_name, name=name)

            if identity_key not in collected_matching_chests:
                collected_matching_chests[identity_key] = [
                    chest
                    for chest in self.map_chests
                    if self._identity_key(model_id=chest.model_id, encoded_name=chest.encoded_name, name=chest.name) == identity_key
                ]

            matching_chests = collected_matching_chests.get(identity_key, [])
            pos = Agent.GetXY(agent_id)
            
            if matching_chests:
                closest_chest = min(matching_chests, key=lambda chest: min(Utils.Distance(spawn, pos) for spawns in chest.spawns.values() for spawn in spawns))                
                if min(Utils.Distance(spawn, pos) for spawns in closest_chest.spawns.values() for spawn in spawns) < Range.Earshot.value:  # Threshold for matching
                    self.mark_id_as_checked(agent_id)
                    continue
                else:
                    if map_id not in closest_chest.spawns:
                        closest_chest.spawns[map_id] = []
                    
                    closest_chest.spawns[map_id].append(pos)
                    self.requires_save = True
                
                self.mark_id_as_checked(agent_id)
                continue

            new_chest = Chest(name=name, model_id=model_id, encoded_name=enc_name, spawns={map_id: [pos]}) 
            self.add_chest(new_chest)
            collected_matching_chests.setdefault(identity_key, []).append(new_chest)
            self.mark_id_as_checked(agent_id)
            
    def add_chest(self, chest: Chest):
        self.map_chests.append(chest)
        self.append(chest)
        self.requires_save = True
        
    def _flush_cache(self):
        super()._flush_cache()
        self.map_chests.clear()
        self.current_map_id = Map.GetBaseMapID()
        
        map_chests = [chest for chest in self if self.current_map_id in chest.spawns]
        self.map_chests.extend(map_chests)
        
CHESTS = ChestsCollector(*BaseCollector.get_path_providers("chests.json"))
