
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Armorer

class ArmorerCollector(ListCollector[Armorer]):
    def _collect(self):
        pass    
        
ARMORERS = ArmorerCollector(*BaseCollector.get_path_providers("armorers.json"))