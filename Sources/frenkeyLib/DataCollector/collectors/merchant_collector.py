
from Sources.frenkeyLib.DataCollector.collectors.base_collectors import BaseCollector, ListCollector
from Sources.frenkeyLib.DataCollector.data_collector_widget import Merchant


class MerchantCollector(ListCollector[Merchant]):
    def _collect(self):
        pass

MERCHANTS = MerchantCollector(*BaseCollector.get_path_providers("merchants.json"))