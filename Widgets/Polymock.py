
# Reload imports
import importlib
import os
from Widgets.frenkey.Polymock import gui, combat, state

from Py4GWCoreLib import Map, Routines
from Py4GWCoreLib.Py4GWcorelib import ThrottledTimer

importlib.reload(gui)
importlib.reload(combat)
importlib.reload(state)

MODULE_NAME = "Polymock"
throttle_timer = ThrottledTimer(250)
script_directory = os.path.dirname(os.path.abspath(__file__))

combat_handler = combat.Combat()
widget_state = state.WidgetState()
ui = gui.UI()

def configure():
    pass


def main():    
    if not Routines.Checks.Map.MapValid():
        return    
            
    widget_state.update()
    ui.draw()
    
    if not Map.IsExplorable():
        return                    
                     
    if throttle_timer.IsExpired():
        throttle_timer.Reset()
        
        combat_handler.Fight()
        
        
        

__all__ = ['main', 'configure']
