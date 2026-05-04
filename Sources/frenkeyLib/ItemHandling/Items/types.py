
import datetime
from enum import IntEnum

from Py4GWCoreLib.enums_src.Item_enums import Bags

class MaterialType(IntEnum):
    None_ = 0
    Common = 1
    Rare = 2
    
NICK_CYCLE_START_DATE = datetime.datetime(2009, 4, 20)
NICK_CYCLE_COUNT = 137