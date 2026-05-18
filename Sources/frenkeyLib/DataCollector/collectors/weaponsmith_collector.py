
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Weaponsmith


    
class WeaponsmithCollector(ListCollector[Weaponsmith]):
    def _collect(self):
        pass
    
WEAPONSMITHS = WeaponsmithCollector(*BaseCollector.get_path_providers("weaponsmiths.json"))