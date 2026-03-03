
from enum import IntEnum, auto


class ItemAction(IntEnum):
    NONE = 0
    
    Collect_Data = auto() # Basically do nothing but collect data about the item for our item database. This is for items we don't want to interact with yet but want to have data about for future rules.
    PickUp = auto() # Pick up the item and put it in the inventory.
    Drop = auto() # Drop the item to the floor the inventory.
    
    Hold = auto()
    Stash = auto()
    
    # Item processing actions:
    Identify = auto()
    Salvage_Mods = auto()
    Salvage_Rare_Materials = auto()
    Salvage_Common_Materials = auto()
    Destroy = auto()
    Deposit_Material = auto()
    
    # Merchant interactions:
    Sell_To_Merchant = auto()
    Buy_From_Merchant = auto()
    
    Sell_To_Trader = auto()
    Buy_From_Trader = auto() 
    
    Use = auto() # Use the item. The target or context should be specified in the rule's parameters.
    
    ## Some stuff we might be able to implement at some point in the future, but not a priority right now:
    TradeToPlayer = auto() # Open the trade window with a specific player and offer the item. The player name should be specified in the rule's parameters.


ACTION_LIMITS_PER_FRAME = [
    # These are actions which we have to handle yield based, 
    # we would also want to always continue with the previous item if its not finished processing
    ItemAction.Salvage_Common_Materials,
    ItemAction.Salvage_Rare_Materials,
    ItemAction.Salvage_Mods,
    ItemAction.Sell_To_Trader,
    ItemAction.Buy_From_Trader,
]