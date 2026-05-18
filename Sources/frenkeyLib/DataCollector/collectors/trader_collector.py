
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Trader


class TraderCollector(ListCollector[Trader]):
    def _collect(self):
        pass

TRADERS = TraderCollector(*BaseCollector.get_path_providers("traders.json"))