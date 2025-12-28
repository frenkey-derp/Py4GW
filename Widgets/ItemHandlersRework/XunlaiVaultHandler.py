import os
from Py4GW import Console
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Widgets.ItemHandlersRework.Rules import RuleInterface
from Widgets.ItemHandlersRework.types import ItemAction

class XunlaiVaultConfig:
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(XunlaiVaultConfig, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
        self.config_path = os.path.join(Console.get_projects_path(), "Widgets", "Config", "XunlaiVaultConfig.json")
        self.enabled: bool = False
        self.rules: list[RuleInterface] = []
    
    def add_rule(self, rule: RuleInterface):
        if rule.action != ItemAction.Stash:
            ConsoleLog("XunlaiVaultConfig", f"Attempted to add a rule with action {rule.action.name} to XunlaiVaultConfig. Only rules with action Stash are allowed.", Console.MessageType.Error)
            return
        
        if rule not in self.rules:
            self.rules.append(rule)
    
    def remove_rule(self, rule: RuleInterface):
        if rule in self.rules:
            self.rules.remove(rule)
    
    def save_config(self):
        data = {
            "enabled": self.enabled,
            "rules": [rule.to_dict() for rule in self.rules]
        }
        
        with open(self.config_path, 'w') as f:
            import json
            json.dump(data, f, indent=4)
    
    def load_config(self):
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, 'r') as f:
                import json
                data = json.load(f)
            
            self.enabled = data.get("enabled", False)
            self.rules = []
            
            for rule_data in data.get("rules", []):
                rule = RuleInterface.from_dict(rule_data)
                
                if rule.action == ItemAction.Stash:
                    self.rules.append(rule)
        except Exception as e:
            ConsoleLog("XunlaiVaultConfig", f"Failed to load config: {e}", Console.MessageType.Error)

class XunlaiVaultHandler:
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(XunlaiVaultHandler, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
    
    def Run(self):
        ''' Method to run the Xunlai Vault handler logic. Processing the generator. '''
        
        ConsoleLog(str(self.__class__.__name__), "Running ...")
        pass