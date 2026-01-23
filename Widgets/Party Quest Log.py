import sys

from HeroAI.utils import SameMapAsAccount
from Py4GWCoreLib import Quest
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import AccountData
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Widgets.PartyQuestLog.ui import UI
from Widgets.PartyQuestLog.settings import Settings
from account_data_src.quest_data_src import QuestData, QuestNode


MODULE_NAME = "Party Quest Log"


for module in list(sys.modules):
    if MODULE_NAME.replace(" ", "") in module:
        del sys.modules[module]
        
settings = Settings()
settings.load_settings()

UI.QuestLogWindow.window_pos = (settings.LogPosX, settings.LogPosY)
UI.QuestLogWindow.window_size = (settings.LogPosWidth, settings.LogPosHeight)

fetch_and_handle_quests = True
quest_data : QuestData = QuestData()
previous_quest_log : list[int] = []

def configure():
    pass

def create_quest_node_generator(fresh_ids: list[int]):
    for qid in fresh_ids:            
        quest_node = QuestNode(qid)
        quest_data.quest_log[qid] = quest_node
        yield from quest_node.coro_initialize()
        
def fetch_new_quests(fresh_ids: list[int]):
    GLOBAL_CACHE.Coroutines.append(create_quest_node_generator(fresh_ids))

def main():
    global quest_data
    
    if not Map.IsMapReady():
        return
    
    shmem_accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
    party_id = GLOBAL_CACHE.Party.GetPartyID()
    accounts : dict[int, AccountData] = {}
    quest_log = Quest.GetQuestLog()
    acc_mail = Player.GetAccountEmail()
    new_quest_ids = [q.quest_id for q in quest_log]
    
    if previous_quest_log != new_quest_ids:
        ConsoleLog(MODULE_NAME, "Quest log changed, updating UI.")
        deleted_ids = [qid for qid in previous_quest_log if qid not in new_quest_ids]
        fresh_ids = [qid for qid in new_quest_ids if qid not in previous_quest_log]
            
        for qid in deleted_ids:        
            quest_data.quest_log.pop(qid, None)
            
        if fresh_ids:
            fetch_new_quests(fresh_ids)
        
        previous_quest_log.clear()
        previous_quest_log.extend(new_quest_ids)
        
    for acc in shmem_accounts:
        if acc.AccountEmail != acc_mail and acc.IsSlotActive and acc.PartyID == party_id and SameMapAsAccount(acc):
            accounts[acc.PlayerID] = acc               

    if fetch_and_handle_quests:    
        quest_data.update()
        
    UI.draw_log(quest_data, accounts)
    settings.write_settings()            
    

__all__ = ['main', 'configure']