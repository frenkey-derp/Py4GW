from LootEx import settings, data, utility
from Py4GWCoreLib import Item, Merchant, Console
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog

trader_queue = ActionQueueNode(175)
checked_items: list[str] = []


class LootCheck:
    @staticmethod
    def get_expensive_runes_from_merchant(threshold: int = 1000, profession: int = 0) -> None:
        def format_currency(value: int) -> str:
            platinum = value // 1000
            gold = value % 1000

            parts = []
            if platinum > 0:
                parts.append(f"{platinum} platinum")
            if gold > 0 or platinum == 0:
                parts.append(f"{gold} gold")

            return " ".join(parts)

        if settings.current.loot_profile is None:
            ConsoleLog(
                "LootEx", "No loot profile selected, skipping item check.", Console.MessageType.Error)
            return

        if not trader_queue.action_queue.is_empty():
            trader_queue.clear()
            ConsoleLog(
                "LootEx", "Trader queue is not empty, skipping item check.", Console.MessageType.Error)
            return

        checked_items.clear()
        items = Merchant.Trading.Trader.GetOfferedItems()
        if items is None:
            ConsoleLog(
                "LootEx", "No items found in merchant's inventory.", Console.MessageType.Error)
            return

        settings.current.loot_profile.runes.clear()
        if profession is not None and profession != 0:
            ConsoleLog(
                "LootEx", f"Checking for runes and insignias for profession {profession}...", Console.MessageType.Info)
            items = [item for item in items if Item.Properties.GetProfession(
                item) == int(profession)] if profession else items

        ConsoleLog(
            "LootEx", f"Checking {len(items)} runes and insignias from the merchant's inventory for expensive runes...", Console.MessageType.Info)
        ConsoleLog(
            "LootEx", f"This will take about {round(len(items) * 175 / 1000)} seconds.", Console.MessageType.Info)

        for item in items:
            Item.RequestName(item)
            
            def create_quotes_for_item(item):
                mods = utility.Util.GetMods(item)
                
                if mods is None or len(mods) != 1:
                    ConsoleLog(
                        "LootEx", f"{Item.GetName(item)} has {len(mods)} mods. Skipping...", Console.MessageType.Info)
                    return
                
                mod = mods[0]
                # ConsoleLog("LootEx", f"Checking {mod.full_name}...", Console.MessageType.Info)

                def request_quote_for_item(item):
                    Merchant.Trading.Trader.RequestQuote(item)

                def get_quote_for_item(item):
                    price = Merchant.Trading.Trader.GetQuotedValue()

                    if price is not None:
                        if mod.identifier and settings.current.loot_profile:
                            checked_items.append(mod.identifier)

                            if price >= threshold:
                                ConsoleLog(
                                    "LootEx",
                                    f"{mod.full_name} is currently quoted at {format_currency(price)}. Marking it as valuable.",
                                    Console.MessageType.Info,
                                )
                                settings.current.loot_profile.runes[mod.identifier] = True
                                settings.current.loot_profile.save()

                        trader_queue.execute_next()
                        return price

                trader_queue.add_action(request_quote_for_item, item)
                trader_queue.add_action(get_quote_for_item, item)

            create_quotes_for_item(item)

        def check_for_missing_runes():
            for rune in data.Runes:
                profession_match = profession is not None and rune.profession == profession

                if rune.identifier not in checked_items and settings.current.loot_profile and profession_match:
                    ConsoleLog(
                        "LootEx",
                        f"{rune.full_name} is currently not available. Marking it as valuable.",
                        Console.MessageType.Info,
                    )
                    settings.current.loot_profile.runes[rune.identifier] = True
                    settings.current.loot_profile.save()
            ConsoleLog(
                "LootEx", "Finished checking for runes and insignias.", Console.MessageType.Success)

        trader_queue.add_action(check_for_missing_runes)

    @staticmethod
    def process_trader_queue() -> bool:
        trader_queue.ProcessQueue()
        return not trader_queue.action_queue.is_empty()
