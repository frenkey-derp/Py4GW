from Sources.frenkeyLib.ItemHandling.GlobalConfigs.GlobalConfig import GlobalConfig
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.Rule import ExtractUpgradeRule, Rule
from Sources.frenkeyLib.ItemHandling.GlobalConfigs.RuleConfig import RuleConfig

class InventoryConfig(RuleConfig, GlobalConfig):    
    def __init__(self):          
        if self._initialized:
            return
        
        super().__init__()
        
