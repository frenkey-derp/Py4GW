
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import ConsumableCrafter


class ConsumableCraftersCollector(ListCollector[ConsumableCrafter]):
    def _collect(self):
        pass

CONSUMABLE_CRAFTERS = ConsumableCraftersCollector(*BaseCollector.get_path_providers("consumable_crafters.json"))