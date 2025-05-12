from LootEx import Data
from LootEx import Settings
from Py4GWCoreLib import Item, Merchant, Console
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog

trader_queue = ActionQueueNode(175)
checked_items : list[str] = []


class LootCheck:
    @staticmethod
    def GetExpensiveRunesFromMerchant(threshold : int = 1000, profession : int = 0) -> None:        
        def format_currency(value: int) -> str:
            platinum = value // 1000
            gold = value % 1000

            parts = []
            if platinum > 0:
                parts.append(f"{platinum} platinum")
            if gold > 0 or platinum == 0:
                parts.append(f"{gold} gold")

            return " ".join(parts)
        
        if Settings.Current.LootProfile is None:
            ConsoleLog("LootEx", "No loot profile selected, skipping item check.", Console.MessageType.Debug)
            return

        if not trader_queue.action_queue.is_empty():
            trader_queue.clear()
            ConsoleLog("LootEx", "Trader queue is not empty, skipping item check.", Console.MessageType.Debug)
            return
        
        checked_items.clear()        
        items = Merchant.Trading.Trader.GetOfferedItems()
        if items is None:
            ConsoleLog("LootEx", "No items found in merchant's inventory.", Console.MessageType.Debug)
            return
        
        Settings.Current.LootProfile.Runes.clear()
        if(profession != None):
            ConsoleLog("LootEx", "Checking for runes and insignias for profession "+ str(profession) + "...", Console.MessageType.Debug)
            items = [item for item in items if Item.Properties.GetProfession(item) == int(profession)] if profession else items

        ConsoleLog("LootEx", "Checking "+ str(len(items)) +" runes and insignias from the merchant's inventory for expensive runes...", Console.MessageType.Debug)
        ConsoleLog("LootEx", "This will take about " + str(round(len(items) * 175 / 1000)) + " seconds.", Console.MessageType.Debug)
        
        for item in items: 
            def CreateQuotesForItem(item):        
                for modifier in Item.Customization.Modifiers.GetModifiers(item):                            
                    mod_hex = f'{modifier.GetIdentifier():04x}{modifier.GetArg():04x}'.upper()
                    
                    # ConsoleLog("LootEx", "Checking " + str(mod_hex) + " for expensive runes...", Console.MessageType.Debug)
                    if mod_hex and mod_hex in Data.Runes:
                        def RequestQuoteForItem(item):  
                            Merchant.Trading.Trader.RequestQuote(item)

                        def GetQuoteForItem(item):                
                            price = Merchant.Trading.Trader.GetQuotedValue()

                            if price is not None:           
                                for modifier in Item.Customization.Modifiers.GetModifiers(item):                            
                                    mod_hex = f'{modifier.GetIdentifier():04x}{modifier.GetArg():04x}'.upper()
                                    
                                    if mod_hex and mod_hex in Data.Runes and Settings.Current.LootProfile:
                                        checked_items.append(mod_hex)
                                                            
                                        if price >= threshold:
                                            ConsoleLog("LootEx", str(Data.Runes[mod_hex].Name) + " is currently quoted at " + format_currency(price) + ". Marking it as valuable.", Console.MessageType.Debug)
                                            Settings.Current.LootProfile.Runes[mod_hex] = True  
                                            Settings.Current.LootProfile.Save()

                                trader_queue.execute_next()                                   
                                return price
                        
                        trader_queue.add_action(RequestQuoteForItem, item)
                        trader_queue.add_action(GetQuoteForItem, item)
                        return
                    
            CreateQuotesForItem(item)

        
        def CheckForMissingRunes():
            for rune in Data.Runes:                     
                profession_match = profession != None and Data.Runes[rune].Profession == profession

                if rune not in checked_items and Settings.Current.LootProfile and profession_match:
                    ConsoleLog("LootEx", str(Data.Runes[rune].Name) + " is currently not available. Marking it as valuable.", Console.MessageType.Debug)
                    Settings.Current.LootProfile.Runes[rune] = True
                    Settings.Current.LootProfile.Save()
            ConsoleLog("LootEx", "Finished checking for runes and insignias.", Console.MessageType.Debug)

        trader_queue.add_action(CheckForMissingRunes)
                    
        pass

    @staticmethod
    def ProcessTraderQueue() -> bool:
        trader_queue.ProcessQueue()
        return not trader_queue.action_queue.is_empty()