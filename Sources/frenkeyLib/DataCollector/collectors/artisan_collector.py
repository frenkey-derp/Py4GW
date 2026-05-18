
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Artisan


class ArtisanCollector(ListCollector[Artisan]):
    def _collect(self):
        pass
        
ARTISANS = ArtisanCollector(*BaseCollector.get_path_providers("artisans.json"))