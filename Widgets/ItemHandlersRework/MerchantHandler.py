import os
from Py4GW import Console
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Widgets.ItemHandlersRework.Rules import RuleInterface
from Widgets.ItemHandlersRework.types import ItemAction

class MerchantConfig:    
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(MerchantConfig, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
        self.config_path = os.path.join(Console.get_projects_path(), "Widgets", "Config", "MerchantConfig.json")
        self.enabled: bool = False
        self.rules: list[RuleInterface] = []
    
    def add_rule(self, rule: RuleInterface):
        if rule.action != ItemAction.Sell_To_Merchant:
            ConsoleLog("MerchantConfig", f"Attempted to add a rule with action {rule.action.name} to MerchantConfig. Only rules with action Sell_To_Merchant are allowed.", Console.MessageType.Error)
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
                
                if rule.action == ItemAction.Sell_To_Merchant:
                    self.rules.append(rule)
        except Exception as e:
            ConsoleLog("MerchantConfig", f"Failed to load MerchantConfig: {e}", Console.MessageType.Error)


class MerchantHandler:
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(MerchantHandler, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
    
    def Run(self):
        ''' Method to run the Xunlai Vault handler logic. Processing the generator. '''
        
        ConsoleLog(str(self.__class__.__name__), "Running ...")
        pass