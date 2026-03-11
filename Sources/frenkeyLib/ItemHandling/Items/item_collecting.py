from typing import NamedTuple

import Py4GW

from Py4GWCoreLib import Merchant
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Sources.frenkeyLib.Core.encoded_names import ItemName
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE

def encoded_to_hex_string(int_list: list[int] | bytes) -> str:
    try:
        return " ".join(f"0x{v:X}" for v in int_list)
    except Exception as e:
        return ""
    
def hex_string_to_bytes(s: str) -> bytes:
    return bytes(int(x, 16) for x in s.split())

class EncodedItemNameTuple(NamedTuple):    
    singular_encoded : bytes
    prefix_encoded : bytes
    suffix_encoded : bytes
    
    singular : str = ""
    prefix : str = ""
    suffix : str = ""
    
    def to_dict(self):
        return {
            "singular_encoded": encoded_to_hex_string(self.singular_encoded),
            "prefix_encoded": encoded_to_hex_string(self.prefix_encoded),
            "suffix_encoded": encoded_to_hex_string(self.suffix_encoded),
            "singular": self.singular,
            "prefix": self.prefix,
            "suffix": self.suffix
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> "EncodedItemNameTuple":
        singular_encoded_str = data.get("singular_encoded", "")
        singular_encoded = [int(x, 16) for x in singular_encoded_str.split()] if singular_encoded_str else []
        prefix_encoded_str = data.get("prefix_encoded", "")
        prefix_encoded = [int(x, 16) for x in prefix_encoded_str.split()] if prefix_encoded_str else []
        suffix_encoded_str = data.get("suffix_encoded", "")
        suffix_encoded = [int(x, 16) for x in suffix_encoded_str.split()] if suffix_encoded_str else []
        return cls(
            singular_encoded=bytes(singular_encoded),
            prefix_encoded=bytes(prefix_encoded),
            suffix_encoded=bytes(suffix_encoded),
            singular=data.get("singular", ""),
            prefix=data.get("prefix", ""),
            suffix=data.get("suffix", "")
        )

class ItemCollector():
    PATH = "Sources\\frenkeyLib\\ItemHandling\\Items\\collected_items.json"
    STRING_PATH = "Sources\\frenkeyLib\\ItemHandling\\Items\\collected_strings.json"
    
    def __init__(self):
        self.collected_items: dict[ItemType, dict[int, EncodedItemNameTuple]] = {}
        self.string_table : dict[bytes, str] = {}
        
        self.requires_saving = False
        
        self.save_throttle = ThrottledTimer(500)
        self.run_throttle = ThrottledTimer(250)
    
    def run(self):  
        if not self.run_throttle.IsExpired():
            return
        
        self.run_throttle.Reset()
        
        snapshot = ITEM_CACHE.get_bags_snapshot([Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2, Bag.Equipment_Pack, Bag.Equipped_Items])
        # snapshot = ITEM_CACHE.get_inventory_snapshot(Bag.Backpack, Bag.Max)
        items = [i for bag in snapshot.values() for i in bag.values() if i is not None]
        offered_items = Merchant.Trading.Trader.GetOfferedItems()
        items = [ITEM_CACHE.get_item_snapshot(i) for i in offered_items if i is not None]
        for item in items:
            if item is None:
                continue
            
            if item.item_type not in self.collected_items:
                self.collected_items[item.item_type] = {}
                
            if item.model_id not in self.collected_items[item.item_type]:
                
                if len( item.complete_name_enc or [] ) == 0:
                    continue
                
                try:
                    parts = ItemName.decode_parts(bytes(item.complete_name_enc or []))
                    encoded_parts = ItemName.encoded_parts(bytes(item.complete_name_enc or []))
                except Exception as e:
                    Py4GW.Console.Log("ItemCollector", f"Error decoding item name for ModelID={item.model_id}, Type={item.item_type}: {e}", Py4GW.Console.MessageType.Error)
                    continue
                
                if parts is None or not parts.singular:
                    continue
                
                self.collected_items[item.item_type][item.model_id] = EncodedItemNameTuple(
                    singular_encoded=encoded_parts.singular if encoded_parts and encoded_parts.singular else bytes([]),
                    prefix_encoded=encoded_parts.prefix if encoded_parts and encoded_parts.prefix else bytes([]),
                    suffix_encoded=encoded_parts.suffix if encoded_parts and encoded_parts.suffix else bytes([]),
                    
                    singular=parts.singular,
                    prefix=parts.prefix or "",
                    suffix=parts.suffix or ""
                )
                self.requires_saving = True
        
        for item in items:
            if item is None:
                continue
            
            if not item.complete_name_enc:
                continue
            
            decoded = ItemName.decode_parts(bytes(item.complete_name_enc))
            encoded = ItemName.encoded_parts(bytes(item.complete_name_enc))
            inspected = ItemName.inspect_decoded(bytes(item.complete_name_enc))
            
            for substring in inspected.substrings:
                 if substring.decoded and substring.encoded:
                    if substring.encoded not in self.string_table:
                        self.string_table[substring.encoded] = substring.decoded
                        self.requires_saving = True
            
            if not decoded or not decoded.singular:
                continue
            
            if not encoded or not encoded.singular:
                continue
            
            props = ["prefix", "singular", "suffix"]
            for prop in props:
                enc_value = getattr(encoded, prop, None)
                dec_value = getattr(decoded, prop, None)
                
                if enc_value and dec_value:
                    if enc_value not in self.string_table:
                        self.string_table[enc_value] = dec_value
                        self.requires_saving = True
            
        
        if self.requires_saving and self.save_throttle.IsExpired():
            self.save()
            self.requires_saving = False
            self.save_throttle.Reset()
        
    
    def save(self):
        import json
        with open(self.PATH, "w", encoding="utf-8") as f:
            data = {str(k.name): {str(ik): iv.to_dict() for ik, iv in v.items()} for k, v in self.collected_items.items()}
            sorted_data = {item_type: dict(sorted(items.items())) for item_type, items in data.items()}
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)
            
        with open(self.STRING_PATH, "w", encoding="utf-8") as f:
            data = {v: encoded_to_hex_string(k).replace(" ", ", ") for k, v in self.string_table.items()}
            sorted_data = dict(sorted(data.items(), key=lambda item: item[0]))  # sort by hex string
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)
            
    def load(self):
        import json
        try:
            with open(self.PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.collected_items = {ItemType[k]: {int(ik): EncodedItemNameTuple.from_dict(iv) for ik, iv in v.items()} for k, v in data.items()}
                
                for string, hex_string in json.load(open(self.STRING_PATH, "r", encoding="utf-8")).items():
                    self.string_table[hex_string_to_bytes(hex_string.replace(", ", " "))] = string
                
        except FileNotFoundError:
            self.collected_items = {}
            self.string_table = {}