
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Foe


class FoesCollector(ListCollector[Foe]):
    def _collect(self):
        pass

FOES = FoesCollector(*BaseCollector.get_path_providers("foes.json"))