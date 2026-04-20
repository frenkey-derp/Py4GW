from typing import ClassVar, NamedTuple

from Py4GWCoreLib import Merchant
from Py4GWCoreLib.Routines import Routines

from Py4GWCoreLib.enums_src.Item_enums import INVENTORY_BAGS, STORAGE_BAGS, Bags
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import Rule, StockRule
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig

BuyInstruction = NamedTuple("BuyInstruction", [("item_id", int), ("quantity", int)])

class BuyConfig(RuleConfig):
    allowed_rule_types: ClassVar[tuple[type[Rule], ...] | None] = (StockRule,)

    def GetItemsToBuy(self, include_storage : bool = True) -> list[BuyInstruction]:                        
        if not Routines.Checks.Map.MapValid():
            return []
            
        bags : list[Bags] = [*INVENTORY_BAGS]
        if include_storage:
            bags.extend(STORAGE_BAGS)
            
        item_ids = Merchant.Trading.Merchant.GetOfferedItems()
        filtered_array : list[BuyInstruction] = []

        for item_id in item_ids[:]:  # Iterate over a copy to avoid modifying while iterating
            if not self.EvaluateItem(item_id):
                continue
            
            filtered_array.append(BuyInstruction(item_id, 1))
            
        return filtered_array
