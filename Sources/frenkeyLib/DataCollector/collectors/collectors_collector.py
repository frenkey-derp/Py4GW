
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Collector


class CollectorsCollector(ListCollector[Collector]):
    def _collect(self):
        pass


COLLECTORS = CollectorsCollector(*BaseCollector.get_path_providers("collectors.json"))