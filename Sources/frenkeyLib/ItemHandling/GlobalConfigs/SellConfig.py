from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.ItemArray import ItemArray
from Py4GWCoreLib.Routines import Routines

from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig
from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot

class SellConfig(RuleConfig):    
    def EvaluateItem(self, item_id):
        item : ItemSnapshot = ItemSnapshot.from_item_id(item_id)
        return item.value > 0 and super().EvaluateItem(item_id)
    
    def GetItemsToSell(self, bags : list[Bag]) -> list[int]:                        
        if not Routines.Checks.Map.MapValid():
            return []
            
        item_ids = ItemArray.GetItemArray(ItemArray.CreateBagList(*bags))        
        filtered_array = []

        for item_id in item_ids[:]:  # Iterate over a copy to avoid modifying while iterating
            if not self.EvaluateItem(item_id):
                continue
            
            filtered_array.append(item_id)
            
        return filtered_array
