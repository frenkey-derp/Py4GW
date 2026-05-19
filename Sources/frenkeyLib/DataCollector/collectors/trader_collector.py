
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Trader


class TraderCollector(ListCollector[Trader]):
    def __init__(self, get_local_path, get_default_path, *, version = '1.0', value_type = None, key_decoder = None, key_encoder = None):
        super().__init__(get_local_path, get_default_path, version=version, value_type=value_type, key_decoder=key_decoder, key_encoder=key_encoder)
        self.map_traders : set[Trader] = set()
        
    def _collect(self):        
        agent_ids = AgentArray.GetAllyArray()
        map_id = Map.GetBaseMapID()
        
        for agent_id in agent_ids:
            if agent_id in self.checked_ids:
                continue
            
            model_id = Agent.GetModelID(agent_id)
            matching_traders = [trader for trader in self.map_traders if trader.model_id == model_id]
            pos = Agent.GetXY(agent_id)
            
            if matching_traders:
                closest_trader = min(matching_traders, key=lambda trader: Utils.Distance(trader.position, pos))
                if Utils.Distance(closest_trader.position, pos) < Range.Earshot.value:  # Threshold for matching
                    continue
            
            name = Agent.GetNameByID(agent_id) or ""
            if not name:
                continue
            
            enc_name = bytes(Agent.GetEncNameByID(agent_id))
            new_trader = Trader(name=name, model_id=model_id, encoded_name=enc_name, position=pos, map_id=map_id)
            self.add_trader(new_trader)
            
    def add_trader(self, trader: Trader):
        self.map_traders.add(trader)
        self.append(trader)
        self.requires_save = True
    
    def _flush_cache(self):
        super()._flush_cache()
        self.map_traders.clear()
        self.current_map_id = Map.GetBaseMapID()
        
        map_traders = [trader for trader in self if trader.map_id == self.current_map_id]
        self.map_traders.update(map_traders)

TRADERS = TraderCollector(*BaseCollector.get_path_providers("traders.json"))
