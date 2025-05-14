import json
import os

from LootEx import Data, enum, settings, utility
from Py4GWCoreLib import Inventory, Item, ItemArray
from Py4GWCoreLib.Py4GWcorelib import ActionQueueNode, ConsoleLog
from Py4GWCoreLib.enums import Bags, ItemType

item_collection_node = ActionQueueNode(5)
queued_items: dict[int, bool] = {}


class DataCollector:
    def __init__(self):
        self.data: dict[int, Data.Item] = {}

    def contains_item(self, model_id: int) -> bool:
        """Check if the data collector contains an item with the given model ID."""
        return model_id in self.data

    def add_item(self, item_id: int, model_id: int) -> bool:
        """Add an item to the data collector."""
        name = ""
        item_type = ItemType[Item.GetItemType(item_id)[1]]

        ConsoleLog("LootEx", f"Adding item: {model_id} ({item_type})")
        self.data[model_id] = Data.Item(model_id, name, item_type)
        return True

    def check_and_add_item(self, item_id: int) -> bool:
        model_id = Item.GetModelID(item_id)

        """Check if the item is already in the data collector and add it if not."""
        if self.contains_item(model_id):
            return False
        else:
            if model_id in queued_items:
                return False

            self.add_item(item_id, model_id)

            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            queued_items[model_id] = True

            return True

    def format_item_name(self, item_id: int) -> str:
        name = Item.GetName(item_id)
        qty = Item.Properties.GetQuantity(item_id)

        if qty > 1:
            # Remove the quantity from the name
            name = name.replace(f"{qty} ", "")

            if (" of " in name):
                # Remove the quantity from the name
                parts = name.split(" of ")

                if len(parts) > 1 and parts[0].endswith("s"):
                    # Remove the plural form
                    parts[0] = parts[0][:-1]

            # Convert the plural name to singular
            elif name.endswith("s"):
                name = name[:-1]
        
        # Strip upgrade suffixes and prefixes
        #TODO: Implement the mod types
        mods = utility.Util.GetMods(item_id)
        if mods is not None:
            for mod in mods:
                if mod.mod_type == enum.ModType.Prefix:
                    name = name.replace(mod.name, "")
                    
                elif mod.mod_type == enum.ModType.Suffix:
                    name = name.replace(mod.name, "")

        return name if name else "Unknown Item"

    def add_name_if_ready(self, item_id: int, model_id: int) -> bool:
        """Add the name of the item if it's ready."""
        if Item.IsNameReady(item_id):
            self.data[model_id].name = self.format_item_name(item_id)

            requirements = utility.Util.GetItemRequirements(item_id)
            if requirements is not None:
                attribute, _ = requirements

                if (attribute is not None and attribute not in self.data[model_id].attributes):
                    self.data[model_id].attributes.append(attribute)
                    ConsoleLog(
                        "LootEx", f"Added attribute: {attribute.name} ({model_id})")

            if model_id in queued_items:
                del queued_items[model_id]

            ConsoleLog(
                "LootEx", f"Added item: {self.data[model_id].name} ({model_id})")

            self.save_item(model_id)

            return True
        else:
            Item.RequestName(item_id)
            ConsoleLog(
                "LootEx", f"Item name not ready '{Item.GetName(item_id)}': {model_id} ({item_id})")
            item_collection_node.add_action(
                self.add_name_if_ready, item_id, model_id)
            return False

    def save_item(self, model_id: int) -> bool:
        """Save the item as a file."""
        if model_id in queued_items:
            del queued_items[model_id]

        path = os.path.join(
            settings.current.data_collection_path, f"{model_id}.json")

        if not os.path.exists(path):
            with open(path, "w") as file:
                json.dump(self.data[model_id].to_json(), file, indent=4)
                ConsoleLog("LootEx", f"Saved item: {model_id}")
                return True

        return False

    def run(self):
        for bag_id in range(Bags.Backpack, Bags.Bag2 + 1):
            bag_to_check = ItemArray.CreateBagList(bag_id)
            item_array = ItemArray.GetItemArray(bag_to_check)

            for item_id in item_array:
                self.check_and_add_item(item_id)

        item_collection_node.ProcessQueue()
