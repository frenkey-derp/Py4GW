from typing import Optional

import Py4GW

from Py4GWCoreLib.Merchant import Trading
from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils

Utils.ClearSubModules("ItemHandling")
Utils.ClearSubModules("ItemManager")
Utils.ClearSubModules("frenkeyLib.Core")

from Sources.frenkeyLib.ItemManager.btrees import TraderPriceCheckManager
from Sources.frenkeyLib.ItemManager.config import Config
from Sources.frenkeyLib.ItemManager.ui import UI

MODULE_NAME = "Item Manager"
MODULE_ICON = "Textures\\Module_Icons\\item_manager.png"

MODULE_CONFIG = Config()
MODULE_UI : UI | None = None
def _tick_trader_price_check() -> None:
    previous_kind = TraderPriceCheckManager.get_kind()
    state = TraderPriceCheckManager.tick()
    current_kind = TraderPriceCheckManager.get_kind()

    if current_kind is not None and current_kind != previous_kind:
        Py4GW.Console.Log(
            MODULE_NAME,
            f"Starting trader price check for {current_kind}.",
            Py4GW.Console.MessageType.Info,
        )

    if state is None:
        return

    if state.name == "RUNNING":
        return

    quote_count, failed_count, skipped_count = TraderPriceCheckManager.summary()
    finished_kind = current_kind or previous_kind
    if state.name == "SUCCESS" and finished_kind is not None:
        checked_type = "rune / insignia" if finished_kind == "runes" else "material"
        Py4GW.Console.Log(
            MODULE_NAME,
            f"Finished {checked_type} trader price check. Collected {quote_count} quotes, failed {failed_count}, skipped {skipped_count}.",
            Py4GW.Console.MessageType.Success,
        )
    elif finished_kind is not None:
        Py4GW.Console.Log(
            MODULE_NAME,
            f"Trader price check for {finished_kind} failed.",
            Py4GW.Console.MessageType.Warning,
        )

def tooltip():
    pass


def configure():    
    pass


def main():
    global MODULE_UI
    
    try:
        if not Routines.Checks.Map.MapValid():
            return
        
        if not MODULE_CONFIG._ensure_ini():
            return
        
        if MODULE_UI is None:
            Py4GW.Console.Log(MODULE_NAME, "Initializing UI...", Py4GW.Console.MessageType.Info)
            MODULE_UI = UI(MODULE_CONFIG)
            MODULE_UI.floating_button.load_visibility()
        
        MODULE_UI.floating_button.visible = True
        MODULE_UI.draw()
        _tick_trader_price_check()
    
    except Exception as e:
        Py4GW.Console.Log(MODULE_NAME, f"Error: {e}", Py4GW.Console.MessageType.Error)
        raise

# These functions need to be available at module level
__all__ = ['main', 'configure', 'tooltip']
