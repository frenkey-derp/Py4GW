
import Py4GW
import PyInventory

import Py4GWCoreLib
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Bag, Item
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE
from Sources.frenkeyLib.ItemHandling.Rules.profile import RuleProfile
from Sources.frenkeyLib.ItemHandling.Rules.types import ItemAction

@staticmethod
def GetZeroFilledBags(start_bag: Bag, end_bag: Bag) -> tuple[list[int], dict[Bag, int]]:
    inventory = []
    bag_sizes = {}

    bags = list(range(start_bag.value, end_bag.value + 1))
    for bag_id in bags:
        if bag_id is None:
            continue
        
        bag_enum = Py4GWCoreLib.Bag(bag_id)
        if bag_enum is None:
            continue
        
        bag = PyInventory.Bag(bag_enum.value, bag_enum.name)
        if bag is None:
            continue
        
        bag.GetContext()
        
        bag_sizes[bag_enum] = bag.GetSize() if bag else 0     
        slots = [0] * bag_sizes[bag_enum]
        
        for item in bag.GetItems():
            if 0 <= item.slot < bag_sizes[bag_enum]:
                slots[item.slot] = item.item_id
                
                
        inventory.extend(slots)
    return inventory, bag_sizes