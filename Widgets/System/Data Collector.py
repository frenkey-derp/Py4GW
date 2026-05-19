import os

import Py4GW
import PyImGui

from Py4GWCoreLib import ImGui
from Py4GWCoreLib.ImGui_src.types import Alignment
from Py4GWCoreLib.py4gwcorelib_src.Color import Color, ColorPalette

from Sources.frenkeyLib.DataCollector.collectors.base_collectors import ListCollector
from Sources.frenkeyLib.DataCollector.collectors.items_collector import ItemCollector
from Sources.frenkeyLib.DataCollector.data_collector import DataCollectorRuntime

MODULE_NAME = 'Data Collector'
MODULE_ICON = os.path.join(Py4GW.Console.get_projects_path(), 'Textures', 'Module_Icons', 'Data Collector.png')
DATA_COLLECTOR = DataCollectorRuntime(MODULE_NAME, MODULE_ICON)

def on_enable():
    DATA_COLLECTOR.set_collector_enabled(True)


def on_disable():
    DATA_COLLECTOR.set_collector_enabled(False)

GRAY_COLOR = ColorPalette.Gray.color
def configure():
    if not DATA_COLLECTOR.ensure_state():
        return
    
    PyImGui.set_next_window_size((400, 0))
    if PyImGui.begin("Data Collector Settings"):
        for collector_name, collector in DATA_COLLECTOR.collectors.items():
            is_enabled = DATA_COLLECTOR.collecting[collector_name]
            enabled = PyImGui.checkbox(f"Collect {collector_name}", is_enabled)            
            if enabled != is_enabled:
                DATA_COLLECTOR.collecting[collector_name] = enabled
                DATA_COLLECTOR._save_collector_setting(collector_name, enabled)
                
            PyImGui.same_line(0, 5)
            
            collected = 0
            if (isinstance(collector, ListCollector)):
                collected = len(collector)
                
            elif (isinstance(collector, ItemCollector)):
                collected = len(collector.all_items)
                
            ImGui.text_colored(f"({collected} {collector_name} collected)", GRAY_COLOR.color_tuple)
    
    PyImGui.end()
    
    pass

def tooltip():
    PyImGui.set_next_window_size((400, 0))
    PyImGui.begin_tooltip()

    # Title
    title_color = Color(255, 200, 100, 255)
    ImGui.image(MODULE_ICON, (32, 32))
    PyImGui.same_line(0, 10)
    ImGui.push_font("Regular", 20)
    ImGui.text_aligned(MODULE_NAME, alignment=Alignment.MidLeft, color=title_color.color_tuple, height=32)
    ImGui.pop_font()
    PyImGui.spacing()
    PyImGui.spacing()
    PyImGui.separator()

    # Description
    ImGui.text_wrapped("This widget will help you collect data in Guild Wars by providing various tools and utilities to streamline the process.")

    PyImGui.spacing()
    PyImGui.separator()
    PyImGui.spacing()

    # Credits
    PyImGui.text_colored("Credits:", title_color.to_tuple_normalized())
    PyImGui.bullet_text("Developed by frenkey")

    PyImGui.end_tooltip()

def main():
    if not DATA_COLLECTOR.ensure_state():
        return
    
    DATA_COLLECTOR.run()

__all__ = ['main']

if __name__ == '__main__':
    main()
