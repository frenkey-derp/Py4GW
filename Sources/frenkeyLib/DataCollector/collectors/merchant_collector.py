
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.UIManager import MerchantWindow
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils

from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Merchant


class MerchantCollector(ListCollector[Merchant]):
    def __init__(self, get_local_path, get_default_path, *, version = '1.0', value_type = None, key_decoder = None, key_encoder = None):
        super().__init__(get_local_path, get_default_path, version=version, value_type=value_type, key_decoder=key_decoder, key_encoder=key_encoder)
        self.map_merchants : set[Merchant] = set()
        
        
    def _collect(self):        
        agent_ids = AgentArray.GetAllyArray()
        map_id = Map.GetBaseMapID()
        
        for agent_id in agent_ids:
            if agent_id in self.checked_ids:
                continue
            
            model_id = Agent.GetModelID(agent_id)
            matching_merchants = [merchant for merchant in self.map_merchants if merchant.model_id == model_id]
            pos = Agent.GetXY(agent_id)
            
            if matching_merchants:
                closest_merchant = min(matching_merchants, key=lambda merchant: Utils.Distance(merchant.position, pos))
                if Utils.Distance(closest_merchant.position, pos) < Range.Earshot.value:  # Threshold for matching
                    continue
            
            name = Agent.GetNameByID(agent_id) or ""
            if not name:
                continue
            
            enc_name = bytes(Agent.GetEncNameByID(agent_id))
            new_merchant = Merchant(name=name, model_id=model_id, encoded_name=enc_name, position=pos, map_id=map_id)
            self.add_merchant(new_merchant)
            
        if self.map_merchants:
            if MerchantWindow.IsOpen():
                for merchant in self.map_merchants:
                    if merchant.CollectData():
                        self.requires_save = True
                
    def add_merchant(self, merchant: Merchant):
        self.map_merchants.add(merchant)
        self.append(merchant)
        self.requires_save = True
    
    def _flush_cache(self):
        super()._flush_cache()
        self.map_merchants.clear()
        self.current_map_id = Map.GetBaseMapID()
        
        map_merchants = [merchant for merchant in self if merchant.map_id == self.current_map_id]
        self.map_merchants.update(map_merchants)

MERCHANTS = MerchantCollector(*BaseCollector.get_path_providers("merchants.json"))