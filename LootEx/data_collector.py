import datetime
import json
import os
import re
from typing import Any, Callable, Optional
from LootEx import data, enum, models, settings, utility
from Py4GWCoreLib import AgentArray, GlobalCache, Item, Routines, UIManager
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog, ThrottledTimer
from Py4GWCoreLib.enums import Bags, Console, ItemType, NumberPreference, Profession, ServerLanguage


import importlib
importlib.reload(settings)
importlib.reload(models)
importlib.reload(GlobalCache)

GLOBAL_CACHE = GlobalCache.GLOBAL_CACHE

item_collection_node = ActionQueueNode(5)
rune_collection_node = ActionQueueNode(5)
queued_mods: dict[int, bool] = {}
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
    server_language: ServerLanguage = ServerLanguage.Unknown
    xunlai_checked: bool = False

    def __init__(self):
        self.cache: dict[int, dict] = {}
        self.queue: dict[int, Callable[[int], Any]] = {}
        self.action_queue = ActionQueueNode(5)
        self.server_language = self.get_server_language()

        self.data: dict[int, models.Item] = {}
        self.items: dict[int, models.Item] = {
            item.model_id: item for item in data.Items.values()}
        self.runes: dict[str, models.Rune] = {
            rune.identifier: rune for rune in data.Runes}
        # self.load_test_item()

    def clear(self):
        self.cache = {}
        self.queue = {}
        self.action_queue.clear()
        GLOBAL_CACHE._reset()

    def get(self, item_id, key: str, action: Callable[[int], Any]):
        """Get an item from the data collector."""
        if not item_id in self.cache:
            self.cache[item_id] = {}

        if not key in self.cache[item_id]:
            self.cache[item_id][key] = action(item_id)

        return self.cache[item_id][key]

    def get_model_id(self, item_id: int) -> int:
        return self.get(item_id, "model_id", lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id))

    def get_item_type(self, item_id: int) -> ItemType:
        return self.get(item_id, "item_type", lambda item_id: ItemType[GLOBAL_CACHE.Item.GetItemType(item_id)[1]])

    def is_complete(self, item_id: int) -> bool:
        if item_id not in self.cache:
            self.cache[item_id] = {"completed": False}

        if "completed" in self.cache[item_id] and self.cache[item_id]["completed"]:
            return True
        
        model_id = self.get_model_id(item_id)
        
        if not model_id in data.Items:
            return False

        item = data.Items[model_id]
        if item.names is None or len(item.names) == 0:
            return False

        if self.server_language not in item.names or item.names[self.server_language] is None:
            return False

        mods = self.get_mods(item_id)
        if len(mods) == 0:
            self.cache[item_id]["completed"] = True
            return True

        for mod in mods:
            if mod.names is None or len(mod.names) == 0:
                return False

            if self.server_language not in mod.names or mod.names[self.server_language] is None:
                return False

        return self.cache[item_id]["completed"]

    def is_fully_completed(self, item_id: int) -> bool:
        if item_id not in self.cache:
            self.cache[item_id] = {"fully_completed": False}

        if "fully_completed" in self.cache[item_id] and self.cache[item_id]["fully_completed"]:
            return True

        model_id = self.get_model_id(item_id)
        if not model_id in data.Items:
            return False

        item = data.Items[model_id]
        if item.names is None or len(item.names) == 0:
            return False

        for lang in ServerLanguage:
            if lang not in item.names or item.names[lang] is None:
                return False

        mods = self.get_mods(item_id)
        if len(mods) == 0:
            self.cache[item_id]["fully_completed"] = True
            return True

        for mod in mods:
            if mod.names is None or len(mod.names) == 0:
                return False

            for lang in ServerLanguage:
                if lang not in mod.names or mod.names[lang] is None:
                    return False

        return self.cache[item_id]["fully_completed"]

    def get_mods(self, item_id: int):
        return self.get(item_id, "mods", lambda item_id: utility.Util.GetMods(item_id))

    def get_requirements(self, item_id: int):
        return self.get(item_id, "requirements", lambda item_id: utility.Util.GetItemRequirements(item_id))
    
    def request_name(self, item_id: int):
        if not (self.get(item_id, "name_requested", lambda item_id: GLOBAL_CACHE.Item.RequestName(item_id) is False)):
            self.cache[item_id]["name_requested"] = True
            return True

        return False
    
    def can_cleanup(self, item_id: int) -> bool:
        item_type = self.get_item_type(item_id)
        
        if item_type == ItemType.Rune_Mod:
            return False
        
        if utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type):
            mods = self.get_mods(item_id)
            
            if len(mods) > 0:
                for mod in mods:
                    if mod.mod_type == enum.ModType.Inherent:
                        ## If the mod is inherent, we don't need to cleanup the item name as its not affected by the mod
                        continue
                    
                    if mod.names is None or self.server_language not in mod.names or mod.names[self.server_language] is None:
                        return False
        
        return True
    
    def reset_name(self, item_id: int):
        """Reset the item name in the cache."""
        if item_id in self.cache:
            if "item_name" in self.cache[item_id]:
                del self.cache[item_id]["item_name"]
                
            if "name_requested" in self.cache[item_id]:
                del self.cache[item_id]["name_requested"]        
    
    def get_item_name(self, item_id: int) -> str:
        name = self.get(item_id, "item_name", lambda item_id: GLOBAL_CACHE.Item.GetName(item_id) if GLOBAL_CACHE.Item.IsNameReady(item_id) else None)
        
        if name is None or name == "":
            self.reset_name(item_id)
        
        return name
    
    def get_quantity(self, item_id: int) -> int:
        return self.get(item_id, "quantity", lambda item_id: GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))
    
    def get_cleaned_item_name(self, item_id: int):
        item_name = self.get_item_name(item_id)
        
        if item_name is None or item_name == "":
            return ""
                
        item_type = self.get_item_type(item_id)
        quantity = self.get_quantity(item_id)
                
        if utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type):
            mods = self.get_mods(item_id)
            
            if len(mods) > 0:
                for mod in mods:
                    if mod.mod_type == enum.ModType.Inherent:
                        ## If the mod is inherent, we don't need to cleanup the item name as its not affected by the mod
                        continue
                    
                    item_name = item_name.replace(mod.applied_name, "").strip()        
        
        if quantity > 1:
            item_name = item_name.replace(str(quantity), "").strip()
        
        return item_name
    
    def get_mods_names(self, item_id: int):
        global save_weapon_mods
        
        def extract_mod_name(mod_type: enum.ModType = enum.ModType.None_) -> Optional[str]:            
            patterns = {}

            match mod_type:
                case enum.ModType.Prefix:
                    patterns = {}

                case enum.ModType.Inherent:
                    patterns = {
                        ServerLanguage.English: r"Inscription: ",
                        ServerLanguage.German: r"Inschrift: ",
                        ServerLanguage.French: r"Inscription : ",
                        ServerLanguage.Spanish: r"Inscripción: ",
                        ServerLanguage.Italian: r"Iscrizione: ",
                        ServerLanguage.TraditionalChinese: r"鑄印：",
                        ServerLanguage.Korean: r"마력석:",
                        ServerLanguage.Japanese: r"刻印：",
                        ServerLanguage.Polish: r"Inskrypcja: ",
                        ServerLanguage.Russian: r"Надпись: ",
                        ServerLanguage.BorkBorkBork: r"Inscreepshun: "
                    }

                case enum.ModType.Suffix:
                    patterns = {
                        ServerLanguage.English: r"^.*?(?= of)",
                        ServerLanguage.German: r"^.*(?= d\.)",
                        ServerLanguage.French: r"^.*?(?= \()",
                        ServerLanguage.Spanish: r"^.*?(?= \()",
                        ServerLanguage.Italian: r"^.*(?= del)",
                        ServerLanguage.TraditionalChinese: r" .*$",
                        ServerLanguage.Japanese: r"^.*?(?= \()",
                        ServerLanguage.Korean: r"^.*?(?= \()",
                        ServerLanguage.Polish: r"^.*?(?= \()",
                        ServerLanguage.Russian: r"^.*?(?= of)",
                        ServerLanguage.BorkBorkBork: r"^.*?(?= ooff)",
                    }

            pattern = patterns.get(self.server_language, None)
            name = self.get_item_name(item_id)
            
            if name is None or name == "" or pattern is None:
                return None

            if pattern:
                name = re.sub(pattern, '', name)

            return name.strip()
               
        item_type = self.get_item_type(item_id)
        model_id = self.get_model_id(item_id)
                
        if item_type == ItemType.Rune_Mod:
            mods = self.get_mods(item_id)
            
            if len(mods) > 0:
                for mod in mods:
                    index = data.Weapon_Mods.index(mod)
                     
                    if index == -1:
                        continue

                    if not data.Weapon_Mods[index].names:
                        data.Weapon_Mods[index].names = {}
                    
                    mod_name = extract_mod_name(mod.mod_type)
                    if mod_name == "" or mod_name is None:                        
                        continue
                    
                    if utility.Util.is_inscription_model_item(model_id) != (mod.mod_type == enum.ModType.Inherent):
                        continue

                    item_type = utility.Util.get_target_item_type_from_mod(
                        item_id) if item_type == ItemType.Rune_Mod else item_type
                    
                    if item_type == None:
                        continue

                    item_type_match = any(utility.Util.IsMatchingItemType(
                        item_type, target_type) for target_type in mod.target_types) if mod.target_types else True

                    if item_type_match is False:
                        continue                    
                        
                    if self.server_language in data.Weapon_Mods[index].names and data.Weapon_Mods[index].names[self.server_language] is not None:
                        # ConsoleLog(
                        #     "LootEx", f"Mod name already exists for {self.server_language.name}: {data.Weapon_Mods[index].names[self.server_language]} ({item_id})", Console.MessageType.Debug)
                        continue                
                    
                    if mod.mod_type == enum.ModType.Prefix:
                        ## There is no way to gurantee to get the correct prefix name without knowing the item name                    
                        continue
                    
                    if mod.mod_type == enum.ModType.Inherent:
                        ConsoleLog(
                            "LootEx", f"Setting Inherent mod name for: {data.Weapon_Mods[index].applied_name} to {mod_name}", Console.MessageType.Debug)
                        data.Weapon_Mods[index].names[self.server_language] = mod_name
                        data.Weapon_Mods[index].update_language(self.server_language)
                        save_weapon_mods = True
                        continue
                    
                    if mod.mod_type == enum.ModType.Suffix:
                        ConsoleLog(
                            "LootEx", f"Setting Suffix mod name for: {data.Weapon_Mods[index].applied_name} to {mod_name}", Console.MessageType.Debug)
                        data.Weapon_Mods[index].names[self.server_language] = mod_name
                        data.Weapon_Mods[index].update_language(self.server_language)
                        save_weapon_mods = True
                        continue                    
        
    def collect_names(self, item_id: int):
        global save_items      
        model_id = self.get_model_id(item_id)
        item_name = self.get_cleaned_item_name(item_id)
        
        if model_id in data.Items and item_name is not None and item_name != "":
            data.Items[model_id].names[self.server_language] = item_name
            save_items = True        

    def check(self, item_id: int):
        def retry_check():
            self.action_queue.add_action(
                self.check, item_id)

        if self.request_name(item_id):
            return retry_check()

        if not GLOBAL_CACHE.Item.IsNameReady(item_id):
            return retry_check()

        model_id = self.get_model_id(item_id)
        item_type = self.get_item_type(item_id)
        profession = GLOBAL_CACHE.Item.Properties.GetProfession(item_id)
        
        # ConsoleLog(
        #     "LootEx", f"Checking item: {self.get_item_name(item_id)} | {item_id} ({model_id}) - Type: {item_type} - Profession: {profession}", Console.MessageType.Debug)
        
        if model_id not in data.Items:
            data.Items[model_id] = models.Item(model_id=model_id, item_type=item_type, profession=Profession(
                profession) if profession < 11 and profession > -1 else Profession._None)
        
        if item_type == ItemType.Rune_Mod:
            self.get_mods_names(item_id)
        
        if not self.can_cleanup(item_id):
            # ConsoleLog(
            #     "LootEx", f"Item {item_id} ({model_id}) cannot be cleaned up, skipping.", Console.MessageType.Debug)
            return retry_check()
        
        self.collect_names(item_id)
        pass

    def run_v2(self):
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
        
        """Run the data collector."""
        if settings.current.collect_items:
            if not Routines.Checks.Map.MapValid():
                self.clear()
                return


            current_language = self.get_server_language()
            if self.server_language != current_language:
                ConsoleLog(
                    "LootEx", f"Language changed from {self.server_language.name} to {current_language.name}")
                self.clear()
                self.server_language = current_language
                return
            
            
            if self.action_queue.ProcessQueue():
                return

            bags = []
            for bag_id in range(Bags.Backpack, Bags.EquippedItems + 1):
                bags.append(Bags(bag_id))
            
            for bag_id in bags:
                item_array = GLOBAL_CACHE.ItemArray.GetItemArray(bags)

                for item_id in item_array:
                    if self.is_complete(item_id):
                        continue

                    if not item_id in self.queue:
                        self.queue[item_id] = self.check
                        self.action_queue.add_action(
                            self.check, item_id)

    def contains_item(self, model_id: int) -> bool:
        """Check if the data collector contains an item with the given model ID."""
        return model_id in self.data

    def add_item(self, item_id: int, model_id: int) -> bool:

        # ConsoleLog("LootEx", f"Item.GetItemType: {Item.GetItemType(item_id)}")
        # ConsoleLog("LootEx", f"Item.GetItemType: {Item.GetItemType(item_id)}")
        """Add an item to the data collector."""
        item_type = ItemType[Item.GetItemType(item_id)[1]]

        # ConsoleLog("LootEx", f"Adding item: {model_id} ({item_type})")
        profession = Item.Properties.GetProfession(item_id)
        self.data[model_id] = models.Item(model_id=model_id, item_type=item_type, profession=Profession(
            profession) if profession < 11 and profession > -1 else Profession._None)
        return True

    def add_rune_item(self, item_id: int) -> bool:
        """Add an item to the data collector."""
        item_type = ItemType[Item.GetItemType(item_id)[1]]

        ConsoleLog("LootEx", f"Adding item: {item_id} ({item_type})")
        profession = Item.Properties.GetProfession(item_id)
        self.data[item_id] = models.Item(model_id=item_id, item_type=item_type, profession=Profession(
            profession) if profession < 11 and profession > -1 else Profession._None)

        return True

    def get_mod_name(self, item_id, mod_type: enum.ModType = enum.ModType.None_) -> str:
        server_language = self.get_server_language()
        patterns = {}

        match mod_type:
            case enum.ModType.Prefix:
                patterns = {}

            case enum.ModType.Inherent:
                patterns = {
                    ServerLanguage.English: r"Inscription: ",
                    ServerLanguage.German: r"Inschrift: ",
                    ServerLanguage.French: r"Inscription : ",
                    ServerLanguage.Spanish: r"Inscripción: ",
                    ServerLanguage.Italian: r"Iscrizione: ",
                    ServerLanguage.Korean: r"마력석:",
                    ServerLanguage.TraditionalChinese: r"鑄印：",
                    ServerLanguage.Japanese: r"刻印：",
                    ServerLanguage.Polish: r"Inskrypcja: ",
                    ServerLanguage.Russian: r"Надпись: ",
                    ServerLanguage.BorkBorkBork: r"Inscreepshun: "
                }

            case enum.ModType.Suffix:
                patterns = {
                    ServerLanguage.English: r"^[^of]+",
                    ServerLanguage.German: r"^.*(?=d\.)",
                    ServerLanguage.French: r"^[^\(]+",
                    ServerLanguage.Spanish: r"^[^\(]+",
                    ServerLanguage.Italian: r"^.*(?=della)",
                    ServerLanguage.TraditionalChinese: r" .*$",
                    ServerLanguage.Korean: r"^[^\(]+",
                    ServerLanguage.Japanese: r"^[^\(]+",
                    ServerLanguage.Polish: r"^[^\(]+",
                    ServerLanguage.Russian: r"of \w. *",
                    ServerLanguage.BorkBorkBork: r"ooff \w. *",
                }

        name = Item.GetName(item_id)
        pattern = patterns.get(server_language, None)

        if pattern:
            name = re.sub(pattern, '', name)
        else:
            ConsoleLog(
                "LootEx", f"Pattern not found for {server_language.name} ({item_id})", Console.MessageType.Warning)

        return name.strip()

    def check_and_add_item(self, item_id: int) -> bool:
        model_id = Item.GetModelID(item_id)

        # If item has mods (item type weapons, armor, salvage or rune_mods)
        # if the mods are not yet collected, keep the item so we can collect the mods
        # if the mods are already collected or an item has no mods, remove them from the item name so we can save the item
        server_language = self.get_server_language()
        mods = self.get_mods(item_id)

        if len(mods) > 0:
            hasAllModNames = all(
                mod.names is not None and server_language in mod.names for mod in mods)

            if not hasAllModNames:
                # ConsoleLog(
                #     "LootEx", f"Item has mods but not all names are ready: {item_id} ({model_id})", Console.MessageType.Debug)
                item_type = ItemType[Item.GetItemType(item_id)[1]]
                if item_type == ItemType.Rune_Mod:
                    # Its the mod item, so we can collect the mod name from it
                    ConsoleLog(
                        "LootEx", f"Item is a rune mod: {item_id} ({model_id})", Console.MessageType.Debug)
                    self.update_mod_name(item_id)
                    pass

                elif item_type == ItemType.Salvage or utility.Util.IsArmorType(item_type):
                    pass

                elif utility.Util.IsWeaponType(item_type):
                    self.update_mod_name(item_id)

            for mod in mods:
                if mod.names is None or server_language not in mod.names:
                    # We can remove the mod name from the item name so we can't save it
                    return True

        else:
            # no mods, so we can collect the item name
            pass

        if not server_language in DataCollector.item_ids:
            DataCollector.item_ids[server_language] = []

        if not item_id in DataCollector.item_ids[server_language]:
            DataCollector.item_ids[server_language].append(item_id)

        if self.contains_item(model_id):
            server_language = self.get_server_language()

            if self.data[model_id].names.get(server_language) is not None:
                ConsoleLog(
                    "LootEx", f"Item name already exists for {server_language}: {self.data[model_id].names[server_language]} ({model_id})")
                return False

            Item.RequestName(item_id)
            self.add_name_if_ready(item_id, model_id)
            return True
        else:
            if model_id in queued_items:
                return False

            Item.RequestName(item_id)
            self.add_item(item_id, model_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            queued_items[model_id] = True

            return True

    def update_mod_name(self, item_id: int):
        global save_weapon_mods, queued_mods

        if not item_id in queued_mods:
            ConsoleLog(
                "LootEx", f"Queueing update for mod name for: {item_id} {Item.GetName(item_id)}", Console.MessageType.Debug)
            queued_mods[item_id] = True
            Item.RequestName(item_id)
            item_collection_node.add_action(
                self.update_mod_name, item_id)
            return False

        # ConsoleLog(
        #     "LootEx", f"Updating mod name for: {item_id} {Item.GetName(item_id)}", Console.MessageType.Debug)

        if Item.IsNameReady(item_id):
            server_language = self.get_server_language()
            name = Item.GetName(item_id)
            model_id = Item.GetModelID(item_id)
            item_type = ItemType[Item.GetItemType(item_id)[1]]

            names = self.data[model_id].names if model_id in self.data else None

            core_name = names.get(server_language, None) if names else None
            upgrade_name = name
            if core_name is None and item_type != ItemType.Rune_Mod:
                ConsoleLog(
                    "LootEx", f"Core name not found for {server_language.name} ({item_id})", Console.MessageType.Warning)

                if item_id in queued_mods:
                    del queued_mods[item_id]
            elif core_name is not None:
                upgrade_name = name.replace(core_name, '').strip()
                if item_id in queued_mods:
                    del queued_mods[item_id]

            mods = self.get_mods(item_id)

            # ConsoleLog(
            #     "LootEx", f"Item has {len(mods)} mods: {item_id} ({model_id})", Console.MessageType.Debug)
            if mods:
                for mod in mods:
                    mod_name = self.get_mod_name(
                        item_id, mod.mod_type) if item_type == ItemType.Rune_Mod else upgrade_name

                    if utility.Util.is_inscription_model_item(model_id) != (mod.mod_type == enum.ModType.Inherent):
                        continue

                    item_type = utility.Util.get_target_item_type_from_mod(
                        item_id) if item_type == ItemType.Rune_Mod else item_type
                    if item_type == None:
                        continue

                    item_type_match = any(utility.Util.IsMatchingItemType(
                        item_type, target_type) for target_type in mod.target_types) if mod.target_types else True

                    if item_type_match is False:
                        continue

                    ConsoleLog(
                        "LootEx", f"Found Mod: {mod.applied_name} ({item_id})", Console.MessageType.Debug)

                    if (mod_name != ""):
                        index = data.Weapon_Mods.index(mod)

                        if index == -1:
                            ConsoleLog(
                                "LootEx", f"Mod not found in weapon mods: {mod_name} ({item_id})", Console.MessageType.Warning)

                        if not data.Weapon_Mods[index].names:
                            data.Weapon_Mods[index].names = {}

                        data.Weapon_Mods[index].names[server_language] = mod_name
                        data.Weapon_Mods[index].update_language(
                            server_language)
                        save_weapon_mods = True
                        ConsoleLog(
                            "LootEx", f"Set Mod name from item {item_id} for: {data.Weapon_Mods[index].names.get(ServerLanguage.English, "N/A")} to {mod_name}", Console.MessageType.Debug)

            if item_id in queued_mods:
                del queued_mods[item_id]
                return False
        else:
            if item_id in queued_mods:
                ConsoleLog(
                    "LootEx", f"Mod name already requested for {item_id} ({item_id})", Console.MessageType.Debug)
                return False

            Item.RequestName(item_id)
            queued_mods[item_id] = True
            item_collection_node.add_action(
                self.update_mod_name, item_id)
            return False

    def format_item_name(self, item_id: int) -> str:
        global save_weapon_mods
        server_language = self.get_server_language()
        name = Item.GetName(item_id)
        qty = Item.Properties.GetQuantity(item_id)

        name = name.replace(str(qty), "xxx")
        # Strip upgrade suffixes and prefixes
        mods = self.get_mods(item_id)
        if mods:
            for mod in mods:
                # ConsoleLog(
                #     "LootEx", f"Removing Mod: {mod.applied_name} ({item_id})", Console.MessageType.Debug)
                name = name.replace(mod.applied_name, "")

        return (name if name else "Unknown Item").strip()

    def add_name_if_ready(self, item_id: int, model_id: int) -> bool:
        def retry_name_request():
            Item.RequestName(item_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            queued_items[model_id] = True

        """Add the name of the item if it's ready."""
        if Item.IsNameReady(item_id):
            server_language = self.get_server_language()
            # ConsoleLog(
            #     "LootEx", f"Creating item name for: {Item.GetName(item_id)} ({model_id})")
            self.data[model_id].names[server_language] = self.format_item_name(
                item_id) if self.data[model_id].item_type != ItemType.Rune_Mod else Item.GetName(item_id)
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

            if english_name is not None and Item.Properties.GetQuantity(item_id) == 1:
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
            if model_id not in [item.model_id for item in data.Items.values()]:
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
                for item in data.Items.values():
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

        item_type = ItemType[Item.GetItemType(item_id)[1]]
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
                Item.RequestName(item_id)

                rune_collection_node.add_action(
                    self.rune_add_name_if_ready, item_id)
                queued_runes[item_id] = True
                return True
        return False

    def rune_add_name_if_ready(self, item_id: int) -> bool:
        global save_runes

        def retry_rune_add_name_if_ready():
            Item.RequestName(item_id)

            rune_collection_node.add_action(
                self.rune_add_name_if_ready, item_id)
            queued_runes[item_id] = True

        """Add the name of the item if it's ready."""
        if Item.IsNameReady(item_id):
            server_language = self.get_server_language()

            mods = self.get_mods(item_id)

            if len(mods) == 1:
                mod_index = data.Runes.index(mods[0])
                if mod_index == -1:
                    ConsoleLog(
                        "LootEx", f"Mod not found in runes: {mods[0].name} ({item_id})")
                    return False

                data.Runes[mod_index].names[server_language] = Item.GetName(
                    item_id)
                save_runes = True
                ConsoleLog(
                    "LootEx", f"Creating item name for: {mods[0].names[server_language]} ({item_id})")
            else:
                ConsoleLog(
                    "LootEx", f"Item '{Item.GetName(item_id)}' has {len(mods)} mods", Console.MessageType.Warning)

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

        if DataCollector.server_language != server_language:
            GLOBAL_CACHE._reset()

            ConsoleLog(
                "LootEx", f"Language changed from {DataCollector.server_language.name} to {server_language.name}")

            # for item in DataCollector.item_ids[server_language] if server_language in DataCollector.item_ids else []:
            #     ConsoleLog(
            #         "LootEx", f"Requesting item name for: {item} ({server_language.name})", Console.MessageType.Notice)
            #     Item.RequestName(item)

            # for item in DataCollector.item_ids[DataCollector.server_language] if DataCollector.server_language in DataCollector.item_ids else []:
            #     ConsoleLog(
            #         "LootEx", f"Requesting item name for: {item} ({server_language.name})", Console.MessageType.Notice)
            #     Item.RequestName(item)

            queued_runes = {}
            queued_items = {}
            item_collection_node.clear()
            rune_collection_node.clear()
            DataCollector.server_language = server_language
            return

        if settings.current.collect_runes:
            if DataCollector.checked_runes != server_language:
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
            # bags = range(Bags.EquippedItems, Bags.EquippedItems + 1)
            DataCollector.first_check = False

            GLOBAL_CACHE.ItemArray.GetRawItemArray(
                [Bags.NoBag, Bags.EquippedItems])

            # DataCollector.item_ids[server_language] = []
            # self.data = {}
            # manual_item_id = 16837
            # self.check_and_add_item(manual_item_id)

            bags = []
            for bag_id in range(Bags.Backpack, Bags.EquippedItems + 1):
                bags.append(Bags(bag_id))
                
            for bag_id in bags:
                item_array = GLOBAL_CACHE.ItemArray.GetItemArray([bag_id])

                for item_id in item_array:
                    slot = Item.GetSlot(item_id)

                    if item_id == 0 or (server_language in DataCollector.item_ids and item_id in DataCollector.item_ids[server_language]):
                        continue

                    if Item.GetItemType(item_id)[0] != ItemType.Rune_Mod.value:
                        # ConsoleLog(
                        #     "LootEx", f"Item is a rune mod: {item_id} ({slot}|{bag_id})", Console.MessageType.Debug)
                        continue

                    # if slot != 0:
                    #     continue

                    # ConsoleLog(s
                    #     "LootEx", f"Checking item: {item_id}  ({slot}|{bag_id})", Console.MessageType.Debug)
                    self.check_and_add_item(item_id)
                    self.update_mod_name(item_id)

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
