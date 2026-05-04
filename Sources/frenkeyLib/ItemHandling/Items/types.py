
from enum import IntEnum

from Py4GWCoreLib.enums_src.Item_enums import Bags


INVENTORY_BAGS = [Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2]
STORAGE_BAGS = [Bags.Storage1, Bags.Storage2, Bags.Storage3, Bags.Storage4, Bags.Storage5, Bags.Storage6, Bags.Storage7, Bags.Storage8, Bags.Storage9, Bags.Storage10, Bags.Storage11, Bags.Storage12, Bags.Storage13, Bags.Storage14]


class MaterialType(IntEnum):
    None_ = 0
    Common = 1
    Rare = 2