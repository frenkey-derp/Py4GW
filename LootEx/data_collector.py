import datetime
import json
import os
import re
from typing import Any, Callable, Optional, OrderedDict

from PyInventory import Bag
from LootEx import data, enum, models, settings, utility
from Py4GWCoreLib import AgentArray, GlobalCache, Item, Routines, UIManager
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog, ThrottledTimer
from Py4GWCoreLib.enums import Bags, Console, ItemType, NumberPreference, Profession, Rarity, ServerLanguage
from Py4GWCoreLib.GlobalCache.ItemCache import Bag_enum


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

global_timer = ThrottledTimer(250)
save_timer = ThrottledTimer(2500)
save_items: bool = False
save_runes: bool = False
save_weapon_mods: bool = False

ignored_model_ids = {
 35, # Abbot's Robes and Bag sharing the same model ID
}

class inventory_item:
    def __init__(self, item_id: int, model_id: int):
        self.item_id = item_id
        self.model_id = model_id
        self.quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)


class DataCollector:
    AllBags = GLOBAL_CACHE.ItemArray.CreateBagList(*range(Bag_enum.Backpack.value, Bag_enum.Max.value))
    XunlaiStorage = GLOBAL_CACHE.ItemArray.CreateBagList(*range(Bag_enum.Storage_1.value, Bag_enum.Storage_14.value))
    CharacterInventory = GLOBAL_CACHE.ItemArray.CreateBagList(*range(Bag_enum.Backpack.value, Bag_enum.Equipment_Pack.value), Bag_enum.Equipped_Items.value)
    
    def __init__(self):
        self.modified_items: dict[int, models.Item] = {}
        self.modified_weapon_mods: dict[str, models.WeaponMod] = {}
        self.modified_runes: dict[str, models.Rune] = {}
        
        self.cache: dict[int, dict] = {}
        self.queue: dict[int, bool] = {}
        self.action_queue = ActionQueueNode(5)
        self.server_language = self.get_server_language()        

        self.load_account_files()
        self.clear()

    def load_account_files(self):            
        file_directory = os.path.dirname(os.path.abspath(__file__))
        account_directory = os.path.join(file_directory, "data", "diffs", GLOBAL_CACHE.Player.GetAccountEmail())            
        account_items_file = os.path.join(account_directory, "items.json")
        account_weapon_mods_file = os.path.join(account_directory, "weapon_mods.json")
        
        if os.path.exists(account_items_file):
            with open(account_items_file, 'r', encoding='utf-8') as file:
                items = json.load(file)

                if self.modified_items:
                    self.modified_items.clear()
                
                for value in items.values():
                    item = models.Item.from_json(value)
                    if item.model_id not in self.modified_items:
                        self.modified_items[item.model_id] = item
                        
        if os.path.exists(account_weapon_mods_file):
            with open(account_weapon_mods_file, 'r', encoding='utf-8') as file:
                weapon_mods = json.load(file)
                
                if self.modified_weapon_mods:
                    self.modified_weapon_mods.clear()
                
                for value in weapon_mods:
                    mod = models.WeaponMod.from_json(value)
                    if mod.identifier not in self.modified_weapon_mods:
                        self.modified_weapon_mods[mod.identifier] = mod
                        
    def is_running(self) -> bool:
        return not self.action_queue.is_empty()
    
    def clear(self):
        self.name_requested = {}
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

    def get_rarity(self, item_id: int) -> Rarity:
        return self.get(item_id, "rarity", lambda item_id: Rarity(GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)[0]))
    
    def get_server_language(self):
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return server_language

    def get_model_id(self, item_id: int) -> int:
        return self.get(item_id, "model_id", lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id))

    def get_item_type(self, item_id: int) -> ItemType:
        return self.get(item_id, "item_type", lambda item_id: ItemType[GLOBAL_CACHE.Item.GetItemType(item_id)[1]])

    def get_profession(self, item_id: int) -> Optional[Profession]:
        return self.get(item_id, "profession", lambda item_id: Profession(GLOBAL_CACHE.Item.Properties.GetProfession(item_id)) if GLOBAL_CACHE.Item.Properties.GetProfession(item_id) < 11 and GLOBAL_CACHE.Item.Properties.GetProfession(item_id) > 0 else None)

    def is_identified_or_unnecessary_to_identify(self, item_id: int) -> bool:
        item_type = self.get_item_type(item_id)
        rarity = GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)

        return not GLOBAL_CACHE.Item.Usage.IsIdentified(item_id) and (utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type)) and (rarity != Rarity.Green and rarity != Rarity.White)

    def has_uncollected_mods(self, item_id: int) -> bool:
        mods = self.get_mods(item_id)
        
        if len(mods) == 0:
            return False
                
        for mod in mods:
            if not mod.upgrade_exists:
                continue

            if mod.names is None or len(mod.names) == 0:
                return True        
            
            for server_language in ServerLanguage:
                if server_language is ServerLanguage.Unknown:
                    continue
                
                if server_language not in mod.names or mod.names[server_language] is None:
                    return True
                
        return False
    
    def is_item_collected(self, item_id: int) -> bool:
        if item_id not in self.cache:
            self.cache[item_id] = {"collected": False}

        if "collected" in self.cache[item_id] and self.cache[item_id]["collected"]:
            return True

        model_id = self.get_model_id(item_id)

        if model_id not in data.Items:
            return False

        item = data.Items[model_id]
        if item.names is None or len(item.names) == 0:
            return False
    
        for server_language in ServerLanguage:
            if server_language is ServerLanguage.Unknown:
                continue
            
            if server_language not in item.names or item.names[server_language] is None:
                return False

        if item.contains_amount:
            return False

        model_id = self.get_model_id(item_id)
        item_type = self.get_item_type(item_id)
        profession = self.get_profession(item_id)
        rarity = GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)
        is_identified = GLOBAL_CACHE.Item.Usage.IsIdentified(item_id)

        if item.wiki_url is None or item.wiki_url == "":
            return False

        if item.item_type != item_type:
            return False

        if profession != item.profession:
            return False

        if utility.Util.IsWeaponType(item_type):
            requirements = utility.Util.GetItemRequirements(item_id)
            if requirements is not None:
                attribute, _ = requirements

                if (attribute is not None and attribute not in item.attributes):
                    return False

        if rarity == Rarity.Green:
            self.cache[item_id]["collected"] = True
            return True

        if not is_identified and (utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type)):
            self.cache[item_id]["collected"] = True
            return True

        self.cache[item_id]["collected"] = True
        return self.cache[item_id]["collected"]
    
    def is_complete(self, item_id: int) -> bool:
        if item_id not in self.cache:
            self.cache[item_id] = {"completed": False}

        if "completed" in self.cache[item_id] and self.cache[item_id]["completed"]:
            return True

        model_id = self.get_model_id(item_id)

        if model_id not in data.Items:
            # ConsoleLog(
            #     "LootEx", f"Model ID {model_id} not found in data.Items for item {item_id}", Console.MessageType.Warning)
            return False

        item = data.Items[model_id]
        if item.names is None or len(item.names) == 0:
            # ConsoleLog(
            #     "LootEx", f"Item names are empty for item {item_id} ({model_id})", Console.MessageType.Warning)
            return False

        if self.server_language not in item.names or item.names[self.server_language] is None:
            # ConsoleLog(
            #     "LootEx", f"Item name not found for {self.server_language.name} in item {item_id} ({model_id})", Console.MessageType.Warning)
            return False

        if item.contains_amount:
            # if self.get_quantity(item_id) == 1:
                # ConsoleLog(
                #     "LootEx", f"Item {item_id} ({model_id}) has a quantity of 1 but the name contains an amount.", Console.MessageType.Warning)
            return False

        model_id = self.get_model_id(item_id)
        item_type = self.get_item_type(item_id)
        profession = self.get_profession(item_id)
        rarity = GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)
        is_inscribeable = GLOBAL_CACHE.Item.Customization.IsInscribable(
            item_id)
        is_identified = GLOBAL_CACHE.Item.Usage.IsIdentified(item_id)

        # ConsoleLog(
        #     "LootEx", f"Checking item: {self.get_item_name(item_id)} | {item_id} ({model_id}) - Type: {item_type} - Profession: {profession}", Console.MessageType.Debug)

        if item.wiki_url is None or item.wiki_url == "":
            # ConsoleLog(
            #     "LootEx", f"Item {item_id} ({model_id}) has no wiki URL, skipping completion check.", Console.MessageType.Debug)
            return False

        if item.item_type != item_type:
            # ConsoleLog(
            #     "LootEx", f"Item type mismatch for item {item_id} ({model_id}): {item.item_type} != {item_type}", Console.MessageType.Warning)
            return False

        if profession != item.profession:
            # ConsoleLog(
            #     "LootEx", f"Profession mismatch for item {item_id} ({model_id}): {profession} (ITEM) != {item.profession} (DATA)", Console.MessageType.Warning)
            return False

        if utility.Util.IsWeaponType(item_type):
            requirements = utility.Util.GetItemRequirements(item_id)
            if requirements is not None:
                attribute, _ = requirements

                if (attribute is not None and attribute not in item.attributes):
                    # ConsoleLog(
                    #     "LootEx", f"Item {item_id} ({model_id}) is missing attribute: {attribute.name}", Console.MessageType.Warning)
                    return False

        mods = self.get_mods(item_id)
        if len(mods) == 0:
            self.cache[item_id]["completed"] = True
            return True

        if rarity == Rarity.Green:
            # ConsoleLog(
            #     "LootEx", f"Item {item_id} ({model_id}) is a green item, skipping mod checks.", Console.MessageType.Debug)
            self.cache[item_id]["completed"] = True
            return True

        if not is_identified and (utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type)):
            self.cache[item_id]["completed"] = True
            return True

        for mod in mods:
            if mod.upgrade_exists:
                if item_type == ItemType.Rune_Mod:
                    target_item_type = utility.Util.get_target_item_type_from_mod(
                        item_id)

                    if target_item_type is not None:
                        item_type_match = any(utility.Util.IsMatchingItemType(
                            target_item_type, target_type) for target_type in mod.target_types) if mod.target_types else True

                        # ConsoleLog(
                        #     "LootEx", f"Checking item type match for mod {mod.applied_name} on item {item_id} ({model_id}): {target_item_type.name} - Match: {item_type_match}", Console.MessageType.Debug)

                        if item_type_match is False:
                            continue

                if item_type != ItemType.Rune_Mod and not is_inscribeable:
                    # Oldschool mod items don't have inscriptions, so we skip them
                    continue

                if mod.names is None or len(mod.names) == 0:
                    # ConsoleLog(
                    #     "LootEx", f"Mod names are empty for mod {mod.applied_name} ({mod.mod_id}) in item {item_id} ({model_id})", Console.MessageType.Warning)
                    return False

                if self.server_language not in mod.names or mod.names[self.server_language] is None:
                    # ConsoleLog(
                    #     "LootEx", f"{self.server_language.name} Mod name not found for {mod.applied_name} ({mod.identifier}) on item {self.get_item_name(item_id)} {item_id} ({model_id})", Console.MessageType.Warning)
                    return False

        self.cache[item_id]["completed"] = True
        return self.cache[item_id]["completed"]

    def get_mods(self, item_id: int):
        return self.get(item_id, "mods", lambda item_id: utility.Util.GetMods(item_id))

    def get_requirements(self, item_id: int):
        return self.get(item_id, "requirements", lambda item_id: utility.Util.GetItemRequirements(item_id))

    def request_name(self, item_id: int):
        if not (self.get(item_id, "name_requested", lambda item_id: GLOBAL_CACHE.Item.RequestName(item_id) is False)):
            self.cache[item_id]["name_requested"] = datetime.datetime.now()
            return True

        return False

    def can_cleanup(self, item_id: int) -> bool:
        item_type = self.get_item_type(item_id)

        if item_type == ItemType.Rune_Mod:
            return True

        if utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type):
            mods = self.get_mods(item_id)

            if len(mods) > 0:
                for mod in mods:
                    if mod.mod_type == enum.ModType.Inherent:
                        # If the mod is inherent, we don't need to cleanup the item name as its not affected by the mod
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
                # time since the name was requested
                time_since_requested = datetime.datetime.now(
                ) - self.cache[item_id]["name_requested"]
                if time_since_requested.total_seconds() > 10:
                    del self.cache[item_id]["name_requested"]

    def get_item_name(self, item_id: int) -> str:
        name = self.get(item_id, "item_name", lambda item_id: GLOBAL_CACHE.Item.GetName(
            item_id) if GLOBAL_CACHE.Item.IsNameReady(item_id) else None)

        if name is None or name == "" or name == "No Item":
            self.reset_name(item_id)

        return name

    def get_quantity(self, item_id: int) -> int:
        return self.get(item_id, "quantity", lambda item_id: GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))

    def reformat_string(self, item_name: str) -> str:
        # split on uppercase letters
        item_name = re.sub(r"([a-z])([A-Z])", r"\1 \2", item_name)

        # replace underscores with spaces
        item_name = item_name.replace("_", " ")

        # replace multiple spaces with a single space
        item_name = re.sub(r"\s+", " ", item_name)

        # strip leading and trailing spaces
        item_name = item_name.strip()

        return item_name

    def get_cleaned_item_name(self, item_id: int):
        item_name = self.get_item_name(item_id)

        if item_name is None or item_name == "":
            return ""

        if self.get_rarity(item_id) == Rarity.Green:
            # If the item is a green item, we don't need to cleanup the item name
            return item_name.strip()
        
        item_type = self.get_item_type(item_id)
        quantity = self.get_quantity(item_id)

        if utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type) or item_type == ItemType.Rune_Mod:
            mods = self.get_mods(item_id)
            is_identified = GLOBAL_CACHE.Item.Usage.IsIdentified(item_id)

            if not is_identified and not GLOBAL_CACHE.Item.Properties.IsCustomized(item_id) and (utility.Util.IsWeaponType(item_type) or item_type == ItemType.Salvage):
                return item_name.strip()

            if len(mods) > 0:
                for mod in mods:
                    if mod.mod_type == enum.ModType.Inherent:
                        # If the mod is inherent, we don't need to cleanup the item name as its not affected by the mod
                        continue

                    # ConsoleLog(
                    #     "LootEx", f"Cleaning up item name for mod: {mod.applied_name} on item {item_name} ({self.get_model_id(item_id)})", Console.MessageType.Debug)
                    
                    if self.server_language == ServerLanguage.Italian:
                        ## Get all gender versions of the mod name and replace them
                        for c in ("o", "a", "i", "e"):
                            ## replace the last chacter with the current character
                            mod_name = mod.applied_name[:-1] + c
                            item_name = item_name.replace(mod_name, "").strip()
                    
                    item_name = item_name.replace(mod.applied_name, "").strip()
                    
                    if item_name.startswith("-"):
                        item_name = item_name[1:].strip()

            if item_type == ItemType.Rune_Mod:
                if utility.Util.is_inscription_model_item(self.get_model_id(item_id)):
                    inscription = {
                        ServerLanguage.English: r"Inscription",
                        ServerLanguage.German: r"Inschrift",
                        ServerLanguage.French: r"Inscription",
                        ServerLanguage.Spanish: r"Inscripción",
                        ServerLanguage.Italian: r"Iscrizione",
                        ServerLanguage.TraditionalChinese: r"鑄印",
                        ServerLanguage.Korean: r"마력석",
                        ServerLanguage.Japanese: r"刻印",
                        ServerLanguage.Polish: r"Inskrypcja",
                        ServerLanguage.Russian: r"Надпись",
                        ServerLanguage.BorkBorkBork: r"Inscreepshun"
                    }

                    target_item_type = utility.Util.get_target_item_type_from_mod(
                        item_id)
                    # If the item is an inscription model item, we don't need to cleanup the item name
                    return f"{inscription.get(self.server_language, 'Inscription')}: {self.reformat_string(target_item_type.name) if target_item_type else ''}".strip()

        if quantity > 1:
            item_name = item_name.replace(str(quantity), "250").strip()

        return item_name

    def item_name_contains_amount(self, item_name: Optional[str]) -> bool:
        pattern = r"^\s*\d+\s+|(\d+個)$"

        if item_name is None or item_name == "":
            return False

        return bool(re.match(pattern, item_name))

    def get_wiki_url(self, item_id: int) -> str:        
        model_id = self.get_model_id(item_id)

        item = data.Items.get(model_id, None)
        if item is None:
            return ""

        if item.wiki_url is not None and item.wiki_url != "":
            # If the item already has a wiki URL, we can return it
            return item.wiki_url

        english_name = item.names.get(
            ServerLanguage.English, None)

        if english_name is not None:
            if self.item_name_contains_amount(english_name):
                # If the name starts with a number, we can't use it for the wiki URL
                # This is usually the case for items that have a quantity > 1
                return ""

            wiki_url = f"https://wiki.guildwars.com/wiki/{english_name.replace(' ', '_')}"

            profession = item.profession if item.profession else Profession._None

            if utility.Util.IsArmorType(item.item_type) and item.item_type != ItemType.Salvage and profession:
                split_name = english_name.split(" ")
                # remove the last part of the name as it indicates the armor slot e.g. ("Headpiece", "Chestpiece", etc.)
                if len(split_name) > 1:
                    split_name = split_name[:-1]

                # join the parts of the name together separated by a space
                english_name = " ".join(split_name)

                wiki_url = f"https://wiki.guildwars.com/wiki/{profession.name}_{english_name.replace(' ', '_')}_armor"

            return wiki_url

        return ""

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

        is_identified = GLOBAL_CACHE.Item.Usage.IsIdentified(item_id)
        if not is_identified and item_type != ItemType.Rune_Mod:
            return

        if item_type == ItemType.Rune_Mod:
            mods = self.get_mods(item_id)

            if len(mods) > 0:
                for mod in mods:
                    if not mod.identifier in data.Weapon_Mods:
                        continue

                    if not data.Weapon_Mods[mod.identifier].names:
                        data.Weapon_Mods[mod.identifier].names = {}

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

                    if self.server_language in data.Weapon_Mods[mod.identifier].names and data.Weapon_Mods[mod.identifier].names[self.server_language] is not None:
                        # ConsoleLog(
                        #     "LootEx", f"Mod name already exists for {self.server_language.name}: {data.Weapon_Mods[index].names[self.server_language]} ({item_id})", Console.MessageType.Debug)
                        continue

                    if mod.mod_type == enum.ModType.Prefix:
                        # There is no way to gurantee to get the correct prefix name without knowing the item name
                        continue

                    if mod.mod_type == enum.ModType.Inherent:
                        ConsoleLog(
                            "LootEx", f"Setting Inherent mod name for: {data.Weapon_Mods[mod.identifier].applied_name} to {mod_name}", Console.MessageType.Debug)
                        data.Weapon_Mods[mod.identifier].set_name(
                            mod_name, self.server_language)
                        save_weapon_mods = True
                        self.modified_weapon_mods[mod.identifier] = data.Weapon_Mods[mod.identifier]
                        continue

                    if mod.mod_type == enum.ModType.Suffix:
                        ConsoleLog(
                            "LootEx", f"Setting Suffix mod name for: {data.Weapon_Mods[mod.identifier].applied_name} to {mod_name}", Console.MessageType.Debug)
                        data.Weapon_Mods[mod.identifier].set_name(
                            mod_name, self.server_language)
                        save_weapon_mods = True
                        self.modified_weapon_mods[mod.identifier] = data.Weapon_Mods[mod.identifier]
                        continue

    def create_item_name(self, item_id: int) -> Optional[str]:
        global save_items
        model_id = self.get_model_id(item_id)
        item_name = self.get_cleaned_item_name(item_id)
        quantity = self.get_quantity(item_id)

        # ConsoleLog(
        #     "LootEx", f"Collecting names for item: {item_id} ({model_id}) - Name: {item_name}", Console.MessageType.Debug)

        if model_id in data.Items and item_name is not None and item_name != "":
            item = data.Items.get(model_id, None)

            if item is not None and item.names is not None and quantity == 1:
                if self.server_language in item.names and item.names[self.server_language] is not None:

                    if item.contains_amount:
                        return item_name

        return item_name

    def check(self, item_id: int):
        global save_items

        def retry_check():
            if not self.is_complete(item_id):
                # ConsoleLog(
                #     "LootEx", f"Retrying check for item: {item_id} ({self.get_model_id(item_id)})", Console.MessageType.Debug)
                self.action_queue.add_action(
                    self.check, item_id)

        if self.request_name(item_id):
            # ConsoleLog(
            #     "LootEx", f"Requesting name for item: {item_id} ({self.get_model_id(item_id)})", Console.MessageType.Debug)
            return retry_check()

        if not GLOBAL_CACHE.Item.IsNameReady(item_id):
            # ConsoleLog(
            #     "LootEx", f"Item name not ready: {item_id} ({self.get_model_id(item_id)})", Console.MessageType.Debug)
            return retry_check()

        model_id = self.get_model_id(item_id)
        item_type = self.get_item_type(item_id)
        profession = self.get_profession(item_id)

        if not self.can_cleanup(item_id):
            # ConsoleLog(
            #     "LootEx", f"Item {self.get_item_name(item_id)} {item_id} ({model_id}) cannot be cleaned up, skipping.", Console.MessageType.Debug)
            del self.queue[item_id]
            # self.reset_name(item_id)
            return 

        # ConsoleLog(
        #     "LootEx", f"Checking item: {self.get_item_name(item_id)} | {item_id} ({model_id}) - Type: {item_type} - Profession: {profession}", Console.MessageType.Debug)

        if item_type == ItemType.Rune_Mod:
            # ConsoleLog(
            #     "LootEx", f"Collecting rune mod names for item: {item_id} ({model_id})", Console.MessageType.Debug)
            self.get_mods_names(item_id)

        item_name = self.create_item_name(item_id)
        
        if not self.is_complete(item_id):            
            if item_name:
                if model_id not in data.Items:
                    data.Items[model_id] = models.Item(model_id=model_id)

                if self.server_language not in data.Items[model_id].names or data.Items[model_id].names[self.server_language] is None:
                    data.Items[model_id].set_name(
                        item_name, self.server_language)
                    save_items = True
                    self.modified_items[model_id] = data.Items[model_id]

                if data.Items[model_id].contains_amount and self.get_quantity(item_id) == 1:
                    data.Items[model_id].set_name(
                        item_name, self.server_language)                    
                    self.modified_items[model_id] = data.Items[model_id]
                    save_items = True

            else:
                # ConsoleLog(
                #     "LootEx", f"Item name for item '{self.get_item_name(item_id)}' {item_id} ({model_id}) is empty or None, skipping.", Console.MessageType.Debug)
                return retry_check()

        if model_id in data.Items:
            save_items = save_items or data.Items[model_id].item_type != item_type
            data.Items[model_id].item_type = item_type

            save_items = save_items or data.Items[model_id].profession != profession
            data.Items[model_id].profession = profession

            if utility.Util.IsWeaponType(item_type):
                requirements = utility.Util.GetItemRequirements(item_id)
                if requirements is not None:
                    attribute, _ = requirements

                    if (attribute is not None and attribute not in data.Items[model_id].attributes):
                        data.Items[model_id].attributes.append(attribute)
                        self.modified_items[model_id] = data.Items[model_id]
                        save_items = True

            wiki_url = self.get_wiki_url(item_id)
            save_items = save_items or data.Items[model_id].wiki_url != wiki_url
            data.Items[model_id].wiki_url = wiki_url

            if save_items:
                self.modified_items[model_id] = data.Items[model_id]

                ConsoleLog(
                    "LootEx", f"Collected item: {data.Items[model_id].names.get(self.server_language, 'Unknown')} ({model_id}) from item '{self.get_item_name(item_id)}' with id ({item_id})", Console.MessageType.Debug)
                return

    def get_sorted_items(self) -> tuple[dict[int, inventory_item], dict[int, inventory_item], dict[int, inventory_item]]:
        """Get a sorted list of items in the inventory."""
        items: dict[int, inventory_item] = {}
        single_items: dict[int, inventory_item] = {}
        stacked_items: dict[int, inventory_item] = {}
        
        item_array = GLOBAL_CACHE.ItemArray.GetItemArray(DataCollector.AllBags)

        for item_id in item_array:
            model_id = self.get_model_id(item_id)
            if not item_id in items:
                items[item_id] = inventory_item(item_id, model_id)
                
                if items[item_id].quantity == 1:
                    single_items[model_id] = items[item_id]
                else:
                    stacked_items[model_id] = items[item_id] if (model_id in stacked_items) and (items[item_id].quantity < stacked_items[model_id].quantity) or not model_id in stacked_items else items[item_id] 

        # Sort items by model_id and then by quantity
        sorted_items = dict(
            sorted(items.items(), key=lambda x: (x[1].model_id, x[1].quantity)))
        sorted_dict = OrderedDict(sorted_items)

        return (sorted_dict, single_items, stacked_items)

    def requires_item_split(self, item_id: int, single_items : dict[int, inventory_item] ) -> bool:
        quantity = self.get_quantity(item_id)
        
        if quantity > 0:
            model_id = self.get_model_id(item_id)
            single_item = single_items.get(model_id, None)
            item = data.Items.get(model_id, None)
            
            if item is not None and (item.contains_amount or not item.has_name(self.server_language)):
                # If the item contains an amount, we need to split it
                return single_item is None
            
        return False
    
    def run_v2(self):
        global save_items, save_runes, queued_runes, save_weapon_mods

        if save_timer.IsExpired():
            save_timer.Reset()
            saved = False

            if save_items:
                save_items = False
                data.SaveItems(shared_file=False, items=self.modified_items)
                saved = True

            if save_runes:
                save_runes = False
                data.SaveRunes(items=self.modified_runes)
                saved = True

            if save_weapon_mods:
                save_weapon_mods = False
                data.SaveWeaponMods(items=self.modified_weapon_mods)
                saved = True

            if saved:
                return

        if not Routines.Checks.Map.MapValid():
            self.clear()
            return
        
        """Run the data collector."""
        if settings.current.collect_items:

            current_language = self.get_server_language()
            if self.server_language != current_language:
                ConsoleLog(
                    "LootEx", f"Language changed from {self.server_language.name} to {current_language.name}")
                self.clear()
                self.server_language = current_language
                return

            if self.action_queue.ProcessQueue():
                # ConsoleLog(
                #     "LootEx", "Processing action queue", Console.MessageType.Debug)
                return

            if global_timer.IsExpired():
                global_timer.Reset()                
                
                # ConsoleLog(
                #     "LootEx", "Running data collector", Console.MessageType.Debug)

                item_array, single_items, stacked_items = self.get_sorted_items()

                for item_id in item_array:
                    model_id = self.get_model_id(item_id)
                    
                    if model_id in ignored_model_ids:
                        # ConsoleLog(
                        #     "LootEx", f"Item {item_id} ({model_id}) is ignored, skipping.", Console.MessageType.Debug)
                        continue
                    
                    if self.is_complete(item_id):
                        continue
                    
                    if self.requires_item_split(item_id, single_items):
                        model_id = self.get_model_id(item_id)
                        
                        if model_id in stacked_items:
                            # ConsoleLog(
                            #     "LootEx", f"Item {item_id} requires splitting.", Console.MessageType.Debug)                            
                            continue                                        

                    if not item_id in self.queue:
                        # ConsoleLog(
                        #     "LootEx", f"Adding item {item_id} to queue for checking.", Console.MessageType.Debug)
                        self.queue[item_id] = True
                        self.action_queue.add_action(
                            self.check, item_id)

    def stop_collection(self):
        global save_items, save_runes, save_weapon_mods
        
        """Stop the data collection. And save any pending changes."""
        settings.current.collect_items = False
        save_items = False
        save_runes = False
        save_weapon_mods = False
        
        ConsoleLog("LootEx", "Data collection stopped.")
        data.SaveItems(shared_file=False, items=self.modified_items)
        data.SaveWeaponMods(shared_file=False, items=self.modified_weapon_mods)
        
        
    def start_collection(self):
        """Start the data collection."""
        
        self.clear()
        
        self.load_account_files()
        
        settings.current.collect_items = True
        
        ConsoleLog("LootEx", "Data collection started.")
        
instance = DataCollector()