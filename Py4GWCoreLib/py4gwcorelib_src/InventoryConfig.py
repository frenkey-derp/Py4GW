class ItemAction(IntEnum):
    NONE = 0
    SalvageCommonMaterial = 1 #Salvage the item for common materials (with lesser kit)
    SalvageRareMaterial = 2 #Salvage the item for rare materials (with expert kit)
    ExtractPrefix = 3 #Extract the prefix mod of the item
    ExtractInherent = 4 #Extract the inherent/inscription mod of the item
    ExtractSuffix = 5 #Extract the suffix mod of the item
    Hold = 6 #Do nothing but keep the item in place
    Sell = 7 #Sell the item
    Deposit = 8 #Deposit the item in the xunlai stash
    Destroy = 9 #Destory the item

    ##... Whatever else we need

## This way allows endless widgets and bots to register addtional checks to whitelist items
class InventoryConfig:
    def __init__(self):
        self.item_checks : list[Callable[[int], ItemAction]] = []

    def GetItemAction(self, item_id: int) -> ItemAction:
        for check in self.item_checks:
            action = check(item_id)

            if action != ItemAction.NONE:
                return action

        return ItemAction.NONE

    # LootEx, Inventory+ or any other widget or bot can register their own item check with this method if they are loaded 
    def AddItemCheck(self, action_func: Callable[[int], ItemAction]):
        self.item_checks.append(action_func)

    # LootEx, Inventory+ or any other widget or bot can unregister their own item check with this method if they are unloaded
    def RemoveItemCheck(self, action_func: Callable[[int], ItemAction]):
        self.item_checks.remove(action_func)