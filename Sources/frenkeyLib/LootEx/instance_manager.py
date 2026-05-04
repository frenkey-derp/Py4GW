

from Py4GW import Console
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog

PERSISTENT = True

class InstanceManager:
    _initialized = False
    _instance = None

    def __new__(cls, inventory_handler = None):
        if cls._instance is None:
            cls._instance = super(InstanceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, inventory_handler = None):
        if self._initialized:
            return
        
        from Py4GWCoreLib.py4gwcorelib_src.AutoInventoryHandler import AutoInventoryHandler
        
        if getattr(self, "auto_inventory_handler", None) is None:
            self.auto_inventory_handler = AutoInventoryHandler()
            
    
                  
    