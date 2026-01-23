from enum import IntEnum


class Quest():
    class State(IntEnum):
        INACTIVE = 0
        ACTIVE = 1
        COMPLETED = 2
        FAILED = 3
        
    def __init__(self, quest_id: int):
        self.id : int = quest_id
        self.name : str = ""
        self.description : str = ""
        
        self.state : Quest.State = Quest.State.INACTIVE
        
    pass