from typing import ClassVar

from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.ItemArray import ItemArray
from Py4GWCoreLib.Routines import Routines

from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import ExtractModRule, Rule
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig

class UpgradesConfig(RuleConfig):    
    allowed_rule_types: ClassVar[tuple[type[Rule], ...] | None] = (ExtractModRule,)
    
    def GetUpgradesToExtract(self, bags : list[Bag]) -> list[int]:                        
        if not Routines.Checks.Map.MapValid():
            return []
            
        item_ids = ItemArray.GetItemArray(ItemArray.CreateBagList(*bags))        
        filtered_array = []

        for item_id in item_ids[:]:  # Iterate over a copy to avoid modifying while iterating
            if not self.EvaluateItem(item_id):
                continue
            
            filtered_array.append(item_id)
            
        return filtered_array
