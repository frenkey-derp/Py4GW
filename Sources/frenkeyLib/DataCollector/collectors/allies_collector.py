
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Ally


class AlliesCollector(ListCollector[Ally]):
    def _collect(self):
        pass

ALLIES = AlliesCollector(*BaseCollector.get_path_providers("allies.json"))