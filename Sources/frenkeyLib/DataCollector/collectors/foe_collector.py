
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Foe


class FoesCollector(ListCollector[Foe]):
    def __init__(self, get_local_path, get_default_path, *, version = '1.0', value_type = None, key_decoder = None, key_encoder = None):
        super().__init__(get_local_path, get_default_path, version=version, value_type=value_type, key_decoder=key_decoder, key_encoder=key_encoder)
        self.map_foes : set[Foe] = set()
        
    def _collect(self):        
        agent_ids = AgentArray.GetEnemyArray()
        map_id = Map.GetBaseMapID()
        collected_matching_foes : dict[int, list[Foe]] = {}
        
        for agent_id in agent_ids:
            if agent_id in self.checked_ids:
                continue
            
            model_id = Agent.GetModelID(agent_id)
            if model_id not in collected_matching_foes:
                collected_matching_foes[model_id] = [foe for foe in self.map_foes if foe.model_id == model_id]
                
            matching_foes = collected_matching_foes.get(model_id, [])            
            pos = Agent.GetXY(agent_id)
            
            if matching_foes:
                closest_foe = min(matching_foes, key=lambda foe: min(Utils.Distance(spawn, pos) for spawns in foe.spawns.values() for spawn in spawns))                
                if min(Utils.Distance(spawn, pos) for spawns in closest_foe.spawns.values() for spawn in spawns) < Range.Earshot.value:  # Threshold for matching
                    continue
                else:
                    if map_id not in closest_foe.spawns:
                        closest_foe.spawns[map_id] = []
                        
                    closest_foe.spawns[map_id].append(pos)
                    self.requires_save = True
                
            name = Agent.GetNameByID(agent_id) or ""
            if not name:
                continue
            
            enc_name = bytes(Agent.GetEncNameByID(agent_id))
            new_foe = Foe(name=name, model_id=model_id, encoded_name=enc_name, spawns={map_id: [pos]}) 
            self.add_foe(new_foe)
            
    def add_foe(self, foe: Foe):
        self.map_foes.add(foe)
        self.append(foe)
        self.requires_save = True
        
    def _flush_cache(self):
        super()._flush_cache()
        self.map_foes.clear()
        self.current_map_id = Map.GetBaseMapID()
        
        map_foes = [foe for foe in self if self.current_map_id in foe.spawns]
        self.map_foes.update(map_foes)
        
FOES = FoesCollector(*BaseCollector.get_path_providers("foes.json"))