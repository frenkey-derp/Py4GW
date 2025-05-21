import datetime
import json
import os
from LootEx import data, enum, models, settings, utility
from Py4GWCoreLib import AgentArray, GlobalCache, Inventory, Item, ItemArray, Map, Routines, UIManager
from Py4GWCoreLib import enums
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog, ThrottledTimer
from Py4GWCoreLib.enums import Attribute, Bags, Console, FlagPreference, ItemType, NumberPreference, Profession, ServerLanguage


import importlib
importlib.reload(settings)
importlib.reload(models)
importlib.reload(GlobalCache)

GLOBAL_CACHE = GlobalCache.GLOBAL_CACHE

item_collection_node = ActionQueueNode(5)
rune_collection_node = ActionQueueNode(5)
queued_items: dict[int, bool] = {}
queued_runes: dict[int, bool] = {}

global_timer = ThrottledTimer(2500)
save_timer = ThrottledTimer(2500)
save_items: bool = False
save_runes: bool = False
save_weapon_mods: bool = False

# TODO: Add either a dictionary for item names per language or check if the game is set to english


class DataCollector:
    item_mods: dict[int, list] = {}
    item_ids: dict[ServerLanguage, list[int]] = {}
    first_check: bool = True
    checked_runes: ServerLanguage = ServerLanguage.Unknown
    xunlai_checked: bool = False

    def __init__(self):
        self.data: dict[int, models.Item] = {}
        self.items: dict[int, models.Item] = {
            item.model_id: item for item in data.Items}
        self.runes: dict[str, models.Rune] = {
            rune.identifier: rune for rune in data.Runes}

    def get_mods(self, item_id: int):
        """Get the mods of an item."""
        if item_id in DataCollector.item_mods:
            return DataCollector.item_mods[item_id]

        mods = utility.Util.GetMods(item_id)

        if mods is not None:
            DataCollector.item_mods[item_id] = mods
            return mods
        else:
            DataCollector.item_mods[item_id] = []

        return []

    def contains_item(self, model_id: int) -> bool:
        """Check if the data collector contains an item with the given model ID."""
        return model_id in self.data

    def add_item(self, item_id: int, model_id: int) -> bool:
        
        ConsoleLog("LootEx", f"Item.GetItemType: {Item.GetItemType(item_id)}")
        ConsoleLog("LootEx", f"GLOBAL_CACHE.Item.GetItemType: {GLOBAL_CACHE.Item.GetItemType(item_id)}")
        
        """Add an item to the data collector."""
        item_type = ItemType[GLOBAL_CACHE.Item.GetItemType(item_id)[1]]

        # ConsoleLog("LootEx", f"Adding item: {model_id} ({item_type})")
        profession = GLOBAL_CACHE.Item.Properties.GetProfession(item_id)
        self.data[model_id] = models.Item(model_id=model_id, item_type=item_type, profession=Profession(
            profession) if profession < 11 and profession > -1 else Profession._None)
        return True

    def add_rune_item(self, item_id: int) -> bool:
        """Add an item to the data collector."""
        item_type = ItemType[GLOBAL_CACHE.Item.GetItemType(item_id)[1]]

        ConsoleLog("LootEx", f"Adding item: {item_id} ({item_type})")
        profession = GLOBAL_CACHE.Item.Properties.GetProfession(item_id)
        self.data[item_id] = models.Item(model_id=item_id, item_type=item_type, profession=Profession(
            profession) if profession < 11 and profession > -1 else Profession._None)

        return True

    def check_and_add_item(self, item_id: int) -> bool:
        model_id = GLOBAL_CACHE.Item.GetModelID(item_id)

        """Check if the item is already in the data collector and add it if not."""
        if self.contains_item(model_id):
            server_language = self.get_server_language()

            if self.data[model_id].names.get(server_language) is not None:
                return False

            GLOBAL_CACHE.Item.RequestName(item_id)
            self.add_name_if_ready(item_id, model_id)
            return True
        else:
            if model_id in queued_items:
                return False

            GLOBAL_CACHE.Item.RequestName(item_id)
            self.add_item(item_id, model_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            queued_items[model_id] = True

            return True

    def format_item_name(self, item_id: int) -> str:
        global save_weapon_mods
        name = GLOBAL_CACHE.Item.GetName(item_id)
        qty = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)
        core_name = "PvP-Axt"

        upgrade_ame = name.replace(core_name, '').strip()

        name = name.replace(str(qty), "xxx")
        # Strip upgrade suffixes and prefixes
        mods = self.get_mods(item_id)
        if mods:
            for mod in mods:
                # ConsoleLog(
                #     "LootEx", f"Removing Mod: {mod.applied_name} ({item_id})", Console.MessageType.Debug)
                name = name.replace(mod.applied_name, "")

                server_language = self.get_server_language()

                if (upgrade_ame != ""):
                    index = data.Weapon_Mods.index(mod)

                    if index == -1:
                        ConsoleLog(
                            "LootEx", f"Mod not found in weapon mods: {mod.applied_name} ({item_id})", Console.MessageType.Warning)
                        return name

                    if not data.Weapon_Mods[index].names:
                        data.Weapon_Mods[index].names = {}

                    data.Weapon_Mods[index].names[server_language] = upgrade_ame
                    data.Weapon_Mods[index].update_language(server_language)
                    save_weapon_mods = True
                    ConsoleLog(
                        "LootEx", f"Set Mod name for: {upgrade_ame} ({item_id})", Console.MessageType.Debug)

        return (name if name else "Unknown Item").strip()

    def add_name_if_ready(self, item_id: int, model_id: int) -> bool:
        def retry_name_request():
            GLOBAL_CACHE.Item.RequestName(item_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            queued_items[model_id] = True

        """Add the name of the item if it's ready."""
        if GLOBAL_CACHE.Item.IsNameReady(item_id):
            server_language = self.get_server_language()
            # ConsoleLog(
            #     "LootEx", f"Creating item name for: {GLOBAL_CACHE.Item.GetName(item_id)} ({model_id})")
            self.data[model_id].names[server_language] = self.format_item_name(
                item_id) if self.data[model_id].item_type != ItemType.Rune_Mod else GLOBAL_CACHE.Item.GetName(item_id)
            ConsoleLog(
                "LootEx", f"Added name: {self.data[model_id].names[server_language]} ({model_id})")

            requirements = utility.Util.GetItemRequirements(item_id)
            if requirements is not None:
                attribute, _ = requirements

                if (attribute is not None and attribute not in self.data[model_id].attributes):
                    self.data[model_id].attributes.append(attribute)
                    # ConsoleLog(
                    #     "LootEx", f"Added attribute: {attribute.name} ({model_id})")

            if model_id in queued_items:
                del queued_items[model_id]

            # ConsoleLog(
            #     "LootEx", f"Added item: {self.data[model_id].name} ({model_id})")

            english_name = self.data[model_id].names.get(
                ServerLanguage.English, None)

            if english_name is not None and GLOBAL_CACHE.Item.Properties.GetQuantity(item_id) == 1:
                self.data[
                    model_id].wiki_url = f"https://wiki.guildwars.com/wiki/{english_name.replace(' ', '_')}"
                profession = self.data[model_id].profession if self.data[model_id].profession else Profession._None

                if utility.Util.IsArmorType(self.data[model_id].item_type) and self.data[model_id].item_type != ItemType.Salvage and profession:
                    split_name = english_name.split(" ")
                    if len(split_name) > 1:
                        if (split_name[0] == "Elite"):
                            english_name = split_name[0] + " " + split_name[1]
                        else:
                            english_name = split_name[0]

                    self.data[
                        model_id].wiki_url = f"https://wiki.guildwars.com/wiki/{profession.name}_{english_name.replace(' ', '_')}_armor"

            # Add the item to data.Items if not already present or update it if the current language is not in the names
            if model_id not in [item.model_id for item in data.Items]:
                self.items[model_id] = models.Item(
                    model_id=model_id,
                    item_type=self.data[model_id].item_type,
                    profession=self.data[model_id].profession,
                    names=self.data[model_id].names,
                    attributes=self.data[model_id].attributes,
                    wiki_url=self.data[model_id].wiki_url,
                )

                # data.Items.append(self.items[model_id])
            else:
                for item in data.Items:
                    if item.model_id == model_id:
                        for lang in self.data[model_id].names:
                            if lang not in item.names:
                                item.names[lang] = self.data[model_id].names[lang]

                        for attr in self.data[model_id].attributes:
                            if attr not in item.attributes:
                                item.attributes.append(attr)

                        item.wiki_url = self.data[model_id].wiki_url
                        break

            self.save_item(model_id)
            return True

            # If any language is missing set the game language to it and request the name again
            for lang in ServerLanguage:
                if lang not in self.data[model_id].names:
                    ConsoleLog(
                        "LootEx", f"Missing name for {lang.name} ({model_id})")
                    UIManager.SetEnumPreference(
                        NumberPreference.TextLanguage, lang.value)

                    retry_name_request()
                    return False

            return True
        else:
            retry_name_request()
            return False

    def save_item(self, model_id: int):
        global save_items
        save_items = True

    # region rune merchant
    def rune_check_and_add_item(self, item_id: int) -> bool:
        if item_id in queued_runes:
            return False

        item_type = ItemType[GLOBAL_CACHE.Item.GetItemType(item_id)[1]]
        if item_type != ItemType.Rune_Mod:
            return False

        mods = self.get_mods(item_id)
        if len(mods) == 0:
            return False

        mod = mods[0]
        if mod is None:
            return False

        server_language = self.get_server_language()

        if not mod in data.Runes:
            return False

        else:
            if not server_language in mod.names or mod.names[server_language] is None:
                GLOBAL_CACHE.Item.RequestName(item_id)

                rune_collection_node.add_action(
                    self.rune_add_name_if_ready, item_id)
                queued_runes[item_id] = True
                return True
        return False

    def rune_add_name_if_ready(self, item_id: int) -> bool:
        global save_runes

        def retry_rune_add_name_if_ready():
            GLOBAL_CACHE.Item.RequestName(item_id)

            rune_collection_node.add_action(
                self.rune_add_name_if_ready, item_id)
            queued_runes[item_id] = True

        """Add the name of the item if it's ready."""
        if GLOBAL_CACHE.Item.IsNameReady(item_id):
            server_language = self.get_server_language()

            mods = self.get_mods(item_id)

            if len(mods) == 1:
                mod_index = data.Runes.index(mods[0])
                if mod_index == -1:
                    ConsoleLog(
                        "LootEx", f"Mod not found in runes: {mods[0].name} ({item_id})")
                    return False

                data.Runes[mod_index].names[server_language] = GLOBAL_CACHE.Item.GetName(
                    item_id)
                save_runes = True
                ConsoleLog(
                    "LootEx", f"Creating item name for: {mods[0].names[server_language]} ({item_id})")
            else:
                ConsoleLog(
                    "LootEx", f"Item '{GLOBAL_CACHE.Item.GetName(item_id)}' has {len(mods)} mods", Console.MessageType.Warning)

            if item_id in queued_items:
                del queued_items[item_id]

            return True
        else:
            retry_rune_add_name_if_ready()
            return False

    def get_server_language(self):
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return server_language
    # endregion

    def run(self):
        global save_items, save_runes, queued_runes, save_weapon_mods

        if save_timer.IsExpired():
            save_timer.Reset()
            saved = False

            if save_items:
                save_items = False
                self.save_test_item()
                # data.SaveItems()

                saved = True

            if save_runes:
                save_runes = False

                data.SaveRunes()
                saved = True

            if save_weapon_mods:
                save_weapon_mods = False

                data.SaveWeaponMods()
                saved = True

            if saved:
                return

        if not Routines.Checks.Map.MapValid():
            self.item_mods = {}
            return

        if settings.current.collect_runes:
            if rune_collection_node.ProcessQueue():
                return

        if settings.current.collect_items:
            if item_collection_node.ProcessQueue():
                return

        if global_timer.IsExpired():
            global_timer.Reset()
        else:
            return

        server_language = self.get_server_language()

        if server_language and server_language not in DataCollector.item_ids:
            DataCollector.item_ids[server_language] = []

        if server_language is None or DataCollector.item_ids is None:
            ConsoleLog(
                "LootEx", f"Server language not set: {server_language}", Console.MessageType.Warning)
            return

        if settings.current.collect_runes:
            if DataCollector.checked_runes != server_language:
                queued_runes = {}
                rune_collection_node.clear()

                for item_id in Trading.Trader.GetOfferedItems():
                    if DataCollector.checked_runes != server_language:
                        DataCollector.checked_runes = server_language
                        ConsoleLog(
                            "LootEx", f"Rune language changed to {server_language.name}")

                    if item_id == 0 or item_id in DataCollector.item_ids[server_language]:
                        continue

                    self.rune_check_and_add_item(item_id)

        if settings.current.collect_items:
            xunlai_checked = (datetime.datetime.now(
            ) - settings.current.last_xunlai_check).total_seconds() < 300

            bags = range(Bags.Backpack, Bags.EquippedItems +
                         1) if not xunlai_checked else range(Bags.Backpack, Bags.EquippedItems + 1)
            bags = range(Bags.EquippedItems, Bags.EquippedItems + 1)
            DataCollector.first_check = False

            GLOBAL_CACHE.ItemArray.GetRawItemArray([Bags.NoBag, Bags.EquippedItems])  

            DataCollector.item_ids[server_language] = []
            self.data = {}
            manual_item_id = 5020               
            self.check_and_add_item(manual_item_id)
            
            
            for bag_id in bags:
                item_array = GLOBAL_CACHE.ItemArray.GetItemArray([bag_id])

                for item_id in item_array:                            
                    slot = GLOBAL_CACHE.Item.GetSlot(item_id)
                                                    
                    if item_id == 0 or item_id in DataCollector.item_ids[server_language]:
                        continue
                    
                    if slot != 0:
                        continue

                    # ConsoleLog(s
                    #     "LootEx", f"Checking item: {item_id}  ({slot}|{bag_id})", Console.MessageType.Debug)
                    self.check_and_add_item(item_id)

            items = AgentArray.GetItemArray()
            for item_id in items:
                if item_id == 0 or item_id in DataCollector.item_ids[server_language]:
                    continue

                # self.check_and_add_item(item_id)

            if not xunlai_checked:
                settings.current.last_xunlai_check = datetime.datetime.now()
                settings.current.save()

    def load_test_item(self):
        file_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.join(file_directory, "data")
        path = os.path.join(data_directory, "item_test.json")

        if not os.path.exists(path):
            return

        with open(path, 'r', encoding='utf-8') as file:
            items = json.load(file)

            for item in items:
                self.data[item["ModelID"]] = models.Item.from_json(item)

    def save_test_item(self):
        file_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.join(file_directory, "data")
        path = os.path.join(data_directory, "item_test.json")

        with open(path, 'w', encoding='utf-8') as file:
            json.dump([item.to_json() for _, item in self.data.items()],
                      file, ensure_ascii=False, indent=4)
