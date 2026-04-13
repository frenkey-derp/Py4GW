import os

import Py4GW

from Py4GWCoreLib.IniManager import IniManager


class Config:
    instance = None
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance.__init__()
        return cls.instance
    
    def __init__(self):
        if hasattr(self, 'initialized') and self.initialized:
            return
        
        self.initialized = False
        self.ini_path = "Widgets/Guild Wars/Items & Loot/Item Manager"
        self.main_ini_key = ""
        self.floating_ini_key = ""
        
        self.icon_path = os.path.join(Py4GW.Console.get_projects_path(), "Textures", "Module_Icons", "item_manager.png")
        
        pass
    
    def _ensure_ini(self) -> bool:
        if self.initialized:
            return True

        self.main_ini_key = IniManager().ensure_key(self.ini_path, "ItemManager.ini")
        self.floating_ini_key = IniManager().ensure_key(self.ini_path, "ItemManager_FloatingIcon.ini")
        if not self.main_ini_key or not self.floating_ini_key:
            return False

        IniManager().load_once(self.main_ini_key)
        IniManager().load_once(self.floating_ini_key)

        self.initialized = True
        return True