from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.ItemArray import ItemArray
from Py4GWCoreLib.Routines import Routines

from Sources.frenkeyLib.ItemHandling.GlobalConfigs.GlobalConfig import GlobalConfig

class BagSorting:
    def __init__(self, bag_id: Bag):
        self.bag_id = bag_id
    
class SortingConfig(GlobalConfig):
    def __init__(self):              
        if self._initialized:
            return
        
        super().__init__()
        
        self.BagSortings : list[BagSorting] = []