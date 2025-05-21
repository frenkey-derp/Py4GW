from types import FunctionType
import inspect

from Py4GWCoreLib import Item
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog


class FRENKEY_CACHE:
    def __init__(self):
        self.Item : _Item = _Item()


class _Item:
    def __init__(self):        
        self.cached : dict = {}
                
        for k, v in _Item.__dict__.items():
            if "function" in str(v):
                ConsoleLog("FRENKEY_CACHE", f"Registering {k}")
                self.cached[k] = dict()
            
    def GetItemType(self, item_id: int):
        method_name = inspect.stack(0)[0][3]
        
        ConsoleLog("FRENKEY_CACHE", f"GetItemType | {method_name}")
            
        if item_id not in self.cached[method_name]:
            ConsoleLog("FRENKEY_CACHE", f"GetItemType({item_id})")
            self.cached[method_name][item_id] = Item.GetItemType(item_id)
        else:
            ConsoleLog("FRENKEY_CACHE", f"GetItemType({item_id}) - Cached")
            
        return self.cached[method_name][item_id]
        
    def GetModelID(self, item_id: int) -> int:
        method_name = inspect.stack(0)[1][3]
        
        if method_name not in self.cached:
            self.cached[method_name] = dict()
            
        if item_id not in self.cached[method_name]:
            self.cached[method_name][item_id] = Item.GetModelID(item_id)
            
        return self.cached[method_name][item_id]
    
    def GetSlot(self, item_id: int) -> int:
        method_name = inspect.stack(0)[1][3]
        
        if method_name not in self.cached:
            self.cached[method_name] = dict()
            
        if item_id not in self.cached[method_name]:
            self.cached[method_name][item_id] = Item.GetSlot(item_id)
            
        return self.cached[method_name][item_id]