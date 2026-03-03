from Sources.frenkeyLib.ItemHandling.Items.item_snapshot import ItemSnapshot


class ItemCache:
    def __init__(self):
        self.items : dict[int, ItemSnapshot] = {}
    
    def get_item_snapshot(self, item_id: int) -> ItemSnapshot:
        if item_id not in self.items:
            self.items[item_id] = ItemSnapshot(item_id)
        # else:
        #     self.items[item_id].update()
            
        return self.items[item_id]
    

ITEM_CACHE = ItemCache()