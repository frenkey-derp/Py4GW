
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
        self.map_chests : set[Chest] = set()
        
    def _collect(self):        
        agent_ids = AgentArray.GetGadgetArray()
        map_id = Map.GetBaseMapID()
        collected_matching_chests : dict[int, list[Chest]] = {}
        
        for agent_id in agent_ids:
            if agent_id in self.checked_ids:
                continue
            
            model_id = Agent.GetModelID(agent_id)
            if model_id not in collected_matching_chests:
                collected_matching_chests[model_id] = [chest for chest in self.map_chests if chest.model_id == model_id]
                
            matching_chests = collected_matching_chests.get(model_id, [])            
            pos = Agent.GetXY(agent_id)
            
            if matching_chests:
                closest_chest = min(matching_chests, key=lambda chest: min(Utils.Distance(spawn, pos) for spawns in chest.spawns.values() for spawn in spawns))                
                if min(Utils.Distance(spawn, pos) for spawns in closest_chest.spawns.values() for spawn in spawns) < Range.Earshot.value:  # Threshold for matching
                    continue
                else:
                    if map_id not in closest_chest.spawns:
                        closest_chest.spawns[map_id] = []
                        
                    closest_chest.spawns[map_id].append(pos)
                    self.requires_save = True
                
            name = Agent.GetNameByID(agent_id) or ""
            if not name:
                continue
            
            enc_name = bytes(Agent.GetEncNameByID(agent_id))
            new_chest = Chest(name=name, model_id=model_id, encoded_name=enc_name, spawns={map_id: [pos]}) 
            self.add_chest(new_chest)
            
    def add_chest(self, chest: Chest):
        self.map_chests.add(chest)
        self.append(chest)
        self.requires_save = True
        
    def _flush_cache(self):
        super()._flush_cache()
        self.map_chests.clear()
        self.current_map_id = Map.GetBaseMapID()
        
        map_chests = [chest for chest in self if self.current_map_id in chest.spawns]
        self.map_chests.update(map_chests)
        
CHESTS = ChestsCollector(*BaseCollector.get_path_providers("chests.json"))