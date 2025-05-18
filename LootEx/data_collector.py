import json
import os
from LootEx import data, enum, models, settings, utility
from Py4GWCoreLib import Inventory, Item, ItemArray, Map, UIManager
from Py4GWCoreLib import enums
from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog
from Py4GWCoreLib.enums import Attribute, Bags, Console, FlagPreference, ItemType, NumberPreference, Profession, ServerLanguage

import importlib
importlib.reload(settings)
importlib.reload(models)

item_collection_node = ActionQueueNode(5)
queued_items: dict[int, bool] = {}
queued_runes: dict[int, bool] = {}

##TODO: Add either a dictionary for item names per language or check if the game is set to english
class DataCollector:
    def __init__(self):
        self.data: dict[int, models.Item] = {}
        self.runes : dict[int, models.Rune] = {}

    def contains_item(self, model_id: int) -> bool:
        """Check if the data collector contains an item with the given model ID."""
        return model_id in self.data

    def add_item(self, item_id: int, model_id: int) -> bool:
        """Add an item to the data collector."""
        item_type = ItemType[Item.GetItemType(item_id)[1]]

        # ConsoleLog("LootEx", f"Adding item: {model_id} ({item_type})")
        profession = Item.Properties.GetProfession(item_id)
        self.data[model_id] = models.Item(model_id=model_id, item_type=item_type, profession=Profession(profession) if profession < 11 and profession > -1 else Profession._None)
        return True
    
    def add_rune_item(self, item_id: int) -> bool:
        """Add an item to the data collector."""
        item_type = ItemType[Item.GetItemType(item_id)[1]]

        ConsoleLog("LootEx", f"Adding item: {item_id} ({item_type})")
        profession = Item.Properties.GetProfession(item_id)
        self.data[item_id] = models.Item(model_id=item_id, item_type=item_type, profession=Profession(profession) if profession < 11 and profession > -1 else Profession._None)
        
        return True

    def check_and_add_item(self, item_id: int) -> bool:
        model_id = Item.GetModelID(item_id)

        """Check if the item is already in the data collector and add it if not."""
        if self.contains_item(model_id):
            # has_all_names = all(name in self.data[model_id].names for name in ServerLanguage)
            has_all_names = True
            if has_all_names:
                return False
            
            self.add_name_if_ready(item_id, model_id)
            return True
        else:
            if model_id in queued_items:
                return False

            self.add_item(item_id, model_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            queued_items[model_id] = True

            return True

    ##TODO: Add non perfect mods to be extracted, also make sure to handle multiple names like fortitude and hale. While Hale is a prefix, fortitude is a suffix
    def format_item_name(self, item_id: int) -> str:
        name = Item.GetName(item_id)
    
        # Strip upgrade suffixes and prefixes
        mods = utility.Util.GetMods(item_id)
        if mods:
            # ConsoleLog("LootEx", f"Mods: {mods}")
            for mod in mods:
                # ConsoleLog("LootEx", f"Removing Mod: {mod.name}")
                name = name.replace(mod.name, "")

        return (name if name else "Unknown Item").strip()

    def add_name_if_ready(self, item_id: int, model_id: int) -> bool:
        def retry_name_request():                
            Item.RequestName(item_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)            
            queued_items[model_id] = True
            
        """Add the name of the item if it's ready."""
        if Item.IsNameReady(item_id):
            preference = UIManager.GetEnumPreference(NumberPreference.TextLanguage)
            server_language = ServerLanguage(preference)
            # ConsoleLog(
            #     "LootEx", f"Creating item name for: {Item.GetName(item_id)} ({model_id})")
            self.data[model_id].names[server_language] = self.format_item_name(item_id) if self.data[model_id].item_type != ItemType.Rune_Mod else Item.GetName(item_id)
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

            english_name = self.data[model_id].names[ServerLanguage.English]

            if english_name is not None:
                self.data[model_id].wiki_url = f"https://wiki.guildwars.com/wiki/{english_name.replace(' ', '_')}"
                profession = self.data[model_id].profession if self.data[model_id].profession else Profession._None

                if utility.Util.IsArmorType(self.data[model_id].item_type) and self.data[model_id].item_type != ItemType.Salvage and profession:
                    split_name = english_name.split(" ")
                    if len(split_name) > 1:
                        if(split_name[0] == "Elite"):
                            english_name = split_name[0] + " " + split_name[1]
                        else:
                            english_name = split_name[0]

                    self.data[model_id].wiki_url = f"https://wiki.guildwars.com/wiki/{profession.name}_{english_name.replace(' ', '_')}_armor"

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

    def save_item(self, model_id: int) -> bool:
        """Save the item as a file."""
        if model_id in queued_items:
            del queued_items[model_id]

        path = os.path.join(
            settings.current.data_collection_path, f"{model_id}.json")

        with open(path, "w") as file:
            json.dump(self.data[model_id].to_json(), file, indent=4)
            # ConsoleLog("LootEx", f"Saved item: {model_id}")
            return True

        return False

    #region rune merchant

    def rune_check_and_add_item(self, item_id: int) -> bool:

        """Check if the item is already in the data collector and add it if not."""
        if item_id in self.runes:
            # has_all_names = all(name in self.data[model_id].names for name in ServerLanguage)
            has_all_names = True
            
            if has_all_names:
                return False
            
            ConsoleLog("LootEx", f"Missing Languages for item: {item_id} ({Item.GetItemType(item_id)[1]})")
            self.rune_add_name_if_ready(item_id)
            return True
        else:
            if item_id in queued_runes:
                return False

            self.add_rune_item(item_id)

            item_collection_node.add_action(
                self.rune_add_name_if_ready, item_id)
            queued_runes[item_id] = True

            return True

    def rune_add_name_if_ready(self, item_id: int) -> bool:
        def retry_rune_add_name_if_ready():                
            Item.RequestName(item_id)

            item_collection_node.add_action(
                self.rune_add_name_if_ready, item_id)            
            queued_runes[item_id] = True
            
        """Add the name of the item if it's ready."""
        if Item.IsNameReady(item_id):
            preference = UIManager.GetEnumPreference(NumberPreference.TextLanguage)
            server_language = ServerLanguage(preference)

            mods = utility.Util.GetMods(item_id)
            
            if len(mods) == 1:
                mod_index = data.Runes.index(mods[0])
                if mod_index == -1:
                    ConsoleLog(
                        "LootEx", f"Mod not found in runes: {mods[0].name} ({item_id})")
                    return False
                
                data.Runes[mod_index].names[server_language] = Item.GetName(item_id)                               
                
                ConsoleLog(
                    "LootEx", f"Creating item name for: {mods[0].names[server_language]} ({item_id})")
            else:
                ConsoleLog(
                    "LootEx", f"Item '{Item.GetName(item_id)}' has {len(mods)} mods", Console.MessageType.Warning)

            self.data[item_id].names[server_language] = mods[0].names[server_language] if mods and mods[0] and mods[0].names and mods[0].names[server_language] else "None"
            
            if item_id in queued_items:
                del queued_items[item_id]
            
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
            retry_rune_add_name_if_ready()
            return False
    #endregion

    def run(self):
        if item_collection_node.ProcessQueue():
            return
        
        for bag_id in range(Bags.Backpack, Bags.EquippedItems + 1):
            bag_to_check = ItemArray.CreateBagList(bag_id)
            item_array = ItemArray.GetItemArray(bag_to_check)

            for item_id in item_array:                    
                self.check_and_add_item(item_id)    
