import os
from Py4GW import Console
from Py4GWCoreLib import Item
from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Widgets.ItemHandlersRework.ItemCache import ItemView
from Widgets.ItemHandlersRework.Rules import RuleInterface
from Widgets.ItemHandlersRework.types import ItemAction

class DestroyConfig:    
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DestroyConfig, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
        self.config_path = os.path.join(Console.get_projects_path(), "Widgets", "Config", "DestroyConfig.json")
        self.enabled: bool = False
        self.rules: list[RuleInterface] = []
    
    def add_rule(self, rule: RuleInterface):
        if rule.action != ItemAction.Destroy:
            ConsoleLog("DestroyConfig", f"Attempted to add a rule with action {rule.action.name} to DestroyConfig. Only rules with action Destroy are allowed.", Console.MessageType.Error)
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
                
                if rule.action == ItemAction.Destroy:
                    self.rules.append(rule)
        except Exception as e:
            ConsoleLog("DestroyConfig", f"Failed to load DestroyConfig: {e}", Console.MessageType.Error)

class DestroyHandler:
    __instance = None
    __initialized = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DestroyHandler, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if self.__initialized:
            return
        
        self.__initialized = True
        self.config = DestroyConfig()
    
    def Run(self, items : list[ItemView]):
        ''' Method to run the Destroy handler logic. Processing the generator. '''
        
        if not self.config.enabled:
            return  
        
        sorted_rules = sorted(self.config.rules, key=lambda r: r.RULE_TYPE.value)
        
        for item in items:
            for rule in sorted_rules:
                if rule.IsMatch(item):
                    ConsoleLog(f"DestroyHandler", f"Destroying item {item.derived.data.name if item.derived and item.derived.data else 'Unknown'} (ID: {item.id}) as per rule '{rule.name}'.")
                    # Inventory.DestroyItem(item.id)
                    break  # Stop processing further rules for this item
        
        pass