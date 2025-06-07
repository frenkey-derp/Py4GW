from typing import Callable
from Py4GWCoreLib import IconsFontAwesome5
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Py4GWCoreLib.enums import SharedCommandType


class Command:
    def __init__(self, name: str, action: Callable, icon: str = IconsFontAwesome5.ICON_PLAY):
        self.name : str = name
        self.action : Callable = action
        self.icon : str = icon
        
class Commands:
    instance = None
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Commands, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self):
        if self._initialized:
            return
        
        self.sharedMemoryManager = Py4GWSharedMemoryManager()
        self._initialized = True
        self.current_account = GLOBAL_CACHE.Player.GetAccountEmail()
        self.commands : list[Command] = [
            Command("Resign", self.resign_command, IconsFontAwesome5.ICON_FLAG),
            Command("Stack on me", self.stack_on_me, IconsFontAwesome5.ICON_RUNNING),
            Command("Leave party", self.leave_party, IconsFontAwesome5.ICON_DOOR_OPEN),
            Command("Interact with Target", self.interact_with_taget, IconsFontAwesome5.ICON_HAND_POINT_LEFT),
            Command("Reload", self.reload, IconsFontAwesome5.ICON_SYNC),
        ]
        
    def resign_command(self, exclude_self: bool = False):
        for acc in self.sharedMemoryManager.GetAllAccountData():
            if exclude_self and acc.AccountEmail == self.current_account:
                continue
            
            self.sharedMemoryManager.SendMessage(
                self.current_account, acc.AccountEmail, SharedCommandType.Resign)            
        
            
    def interact_with_taget(self):
        target = GLOBAL_CACHE.Player.GetTargetID()
        if target == 0:
            return
        
        self_account = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(self.current_account)
        if not self_account:
            return
        
        accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
        sender_email = self.current_account
        
        for account in accounts:
            if self_account.AccountEmail == account.AccountEmail:
                continue
            GLOBAL_CACHE.ShMem.SendMessage(sender_email, account.AccountEmail, SharedCommandType.InteractWithTarget, (target,0,0,0))
        
    def reload(self, exclude_self: bool = True):
        for acc in self.sharedMemoryManager.GetAllAccountData():
            if exclude_self and acc.AccountEmail == self.current_account:
                continue

        self.sharedMemoryManager.SendMessage(
            self.current_account, self.current_account, SharedCommandType.LootEx, (10,0,0,0))
        
    def leave_party(self, exclude_self: bool = True):
        for acc in self.sharedMemoryManager.GetAllAccountData():
            if exclude_self and acc.AccountEmail == self.current_account:
                continue

            self.sharedMemoryManager.SendMessage(
                self.current_account, acc.AccountEmail, SharedCommandType.LeaveParty)
            
    def stack_on_me(self):
        for acc in self.sharedMemoryManager.GetAllAccountData():
            if acc.AccountEmail == self.current_account:
                continue
            
            agent = GLOBAL_CACHE.Player.GetAgent()
            self.sharedMemoryManager.SendMessage(
                self.current_account, acc.AccountEmail, SharedCommandType.PixelStack, (agent.x, agent.y, 0, 0))
