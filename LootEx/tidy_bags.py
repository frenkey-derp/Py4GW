
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.enums import ItemType


class TidyBag:
    def __init__(self):
        self.enabled: bool = False
        self.allowed_item_types : list[ItemType] = []

class TidyBags(dict[Bag, TidyBag]):
    
    def __init__(self):
        super().__init__()  