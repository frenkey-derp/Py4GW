
import os

from Py4GWCoreLib.py4gwcorelib_src.IniHandler import IniHandler
from Py4GWCoreLib.py4gwcorelib_src.Console import Console, ConsoleLog
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer


class Settings:
    _instance = None
    _initialized = False    
        
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance
    
    def __init__(self): 
        # guard: only initialize once
        if self.__class__._initialized:
            return
        
        self.__class__._initialized = True
        
        base_path = Console.get_projects_path()
        self.ini_path = os.path.join(base_path, "Widgets", "Config", "PartyQuestLog.ini")
        
        self.save_requested = False        
        if not os.path.exists(self.ini_path):
            ConsoleLog("Party Quest Log", "Settings file not found. Creating default settings...")
            self.save_requested = True  
        
        self.save_throttle_timer = ThrottledTimer(1000)
        self.ini_handler = IniHandler(self.ini_path)
        
        self.LogPosX : float = 0
        self.LogPosY : float = 0
        self.LogPosHeight : float = 800
        self.LogPosWidth : float = 300
            
        self.ShowOnlyInParty : bool = True
        self.ShowOnlyOnLeader : bool = True
            
    def save_settings(self):
        self.save_requested = True
    
    def write_settings(self):               
        if not self.save_requested:
            return
        
        if not self.save_throttle_timer.IsExpired():
            return        
        
        self.save_throttle_timer.Reset()
        self.save_requested = False
        
        self.ini_handler.write_key("Window", "LogPosX", str(self.LogPosX))
        self.ini_handler.write_key("Window", "LogPosY", str(self.LogPosY))
        self.ini_handler.write_key("Window", "LogPosHeight", str(self.LogPosHeight))
        self.ini_handler.write_key("Window", "LogPosWidth", str(self.LogPosWidth))
        
    def load_settings(self):
        self.LogPosX = self.ini_handler.read_float("Window", "LogPosX", self.LogPosX)
        self.LogPosY = self.ini_handler.read_float("Window", "LogPosY", self.LogPosY)
        self.LogPosHeight = self.ini_handler.read_float("Window", "LogPosHeight", self.LogPosHeight)
        self.LogPosWidth = self.ini_handler.read_float("Window", "LogPosWidth", self.LogPosWidth)
        pass