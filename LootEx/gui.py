from datetime import timedelta
import webbrowser
from LootEx import *
from LootEx import settings, item_actions, data, loot_check, item_configuration, utility, enum, cache, ui_manager_extensions, loot_handling, wiki_scraper
from LootEx import models
from LootEx import messaging
from LootEx import data_collector
from LootEx import wiki_scraper
from LootEx.item_configuration import ItemConfiguration, ConfigurationCondition
from LootEx.loot_filter import LootFilter
from LootEx.loot_profile import LootProfile
from LootEx.ui_manager_extensions import UIManagerExtensions
from Py4GWCoreLib import *


import importlib

from Py4GWCoreLib.GlobalCache.SharedMemory import Py4GWSharedMemoryManager
from Widgets import LootManager
importlib.reload(settings)
importlib.reload(data)
importlib.reload(models)
importlib.reload(loot_check)
importlib.reload(item_configuration)
importlib.reload(utility)
importlib.reload(cache)
importlib.reload(ui_manager_extensions)
importlib.reload(loot_handling)
importlib.reload(wiki_scraper)


class SelectableItem:
    """
    Represents an item that can be selected and hovered over in a GUI.
    Attributes:
        item_info (data.Item): The information about the item.
        is_selected (bool): Indicates whether the item is currently selected. Defaults to False.
        is_hovered (bool): Indicates whether the item is currently being hovered over. Defaults to False.
    Methods:
        __str__(): Returns a string representation of the SelectableItem instance.
        __repr__(): Returns a string representation of the SelectableItem instance (same as __str__).
    """

    def __init__(self, item: models.Item, is_selected: bool = False):
        self.item_info: models.Item = item
        self.is_selected: bool = is_selected
        self.is_hovered: bool = False

    def __str__(self):
        return f"SelectableItem(item={self.item_info}, is_selected={self.is_selected})"

    def __repr__(self):
        return self.__str__()


class SelectableWrapper:
    """
    Represents a selectable wrapper for an object, allowing it to be selected and hovered over in a GUI.
    Attributes:
        object (object): The object to be wrapped.
        is_selected (bool): Indicates whether the object is currently selected. Defaults to False.
        is_hovered (bool): Indicates whether the object is currently being hovered over. Defaults to False.
    """

    def __init__(self, object, is_selected: bool = False):
        self.object = object
        self.is_selected: bool = is_selected
        self.is_hovered: bool = False


selected_loot_items: list[SelectableItem] = []
loot_items_selection_dragging: bool = False
filtered_loot_items: list[SelectableItem] = [
    SelectableItem(item) for item in data.Items.values()
]
selected_condition: Optional[ConfigurationCondition] = None
filter_name: str = ""
condition_name: str = ""
item_search: str = ""
new_profile_name: str = ""
mod_search: str = ""
filtered_weapon_mods: list[SelectableWrapper] = []
scroll_bar_visible: bool = False
trader_type: str = ""
entered_price_threshold: int = 1000
show_price_check_popup: bool = False
show_add_filter_popup: bool = False
show_add_profile_popup: bool = False
show_delete_profile_popup: bool = False
first_draw: bool = True
inventory_frame_hash: int = 291586130
on_screen: bool = True
window_flags: int = PyImGui.WindowFlags.NoFlag
weapon_types = [
    ItemType.Axe,
    ItemType.Sword,
    ItemType.Spear,
    ItemType.Wand,
    ItemType.Daggers,
    ItemType.Hammer,
    ItemType.Scythe,
    ItemType.Bow,
    ItemType.Staff,
    ItemType.Offhand,
    ItemType.Shield,
]

prefix_names = ["Any"]
suffix_names = ["Any"]
inherent_names = ["Any"]

mod_heights: dict[str, float] = {}
sharedMemoryManager = Py4GWSharedMemoryManager()
filter_popup = False

class ItemFilter:
    def __init__(self, name: str, lambda_function: Callable):
        self.name: str = name
        self.lambda_function: Callable = lambda_function
        pass
    
    def match(self, item: models.Item) -> bool:
        """
        Checks if the item matches the filter criteria.
        
        Args:
            item (models.Item): The item to check against the filter.
        
        Returns:
            bool: True if the item matches the filter, False otherwise.
        """
        
        return self.lambda_function(item)
    
selected_filter: Optional[ItemFilter] = None
filters : list[ItemFilter] = [
    ItemFilter("All Items", lambda item: True),
    ItemFilter("Weapons", lambda item: item.item_type in weapon_types),
    ItemFilter("Armor", lambda item: item.item_type in [
        ItemType.Chestpiece,
        ItemType.Headpiece,
        ItemType.Leggings,
        ItemType.Boots,
        ItemType.Gloves,
    ]),
    ItemFilter("Upgrades", lambda item: item.item_type == ItemType.Rune_Mod),
    ItemFilter("Consumables", lambda item: item.category == enum.ItemCategory.Alcohol or
                                            item.category == enum.ItemCategory.Sweet or
                                            item.category == enum.ItemCategory.Party or
                                            item.category == enum.ItemCategory.DeathPenaltyRemoval),
    ItemFilter("Alcohol", lambda item: item.category == enum.ItemCategory.Alcohol),
    ItemFilter("Sweets", lambda item: item.category == enum.ItemCategory.Sweet),
    ItemFilter("Party", lambda item: item.category == enum.ItemCategory.Party),
    ItemFilter("Death Penalty Removal", lambda item: item.category == enum.ItemCategory.DeathPenaltyRemoval),
    ItemFilter("Scrolls", lambda item: item.category == enum.ItemCategory.Scroll),
    ItemFilter("Tomes", lambda item: item.category == enum.ItemCategory.Tome),
    ItemFilter("Keys", lambda item: item.category == enum.ItemCategory.Key),
    ItemFilter("Materials", lambda item: item.category == enum.ItemCategory.Material),
    ItemFilter("Trophies", lambda item: item.category == enum.ItemCategory.Trophy),
    ItemFilter("Reward Trophies", lambda item: item.category == enum.ItemCategory.RewardTrophy),
    ItemFilter("Quest Items", lambda item: item.category == enum.ItemCategory.QuestItem),    
]

def draw_vault_controls():    
    if not UIManager.IsWindowVisible(WindowID.WindowID_VaultBox):
        ConsoleLog(
            "LootEx",
            "Vault controls not drawn because the Vault Box window is not visible.",
            Console.MessageType.Warning,
        )
        return
    
    coords = settings.FrameCoords(UIManager.GetFrameIDByHash(2315448754))  # "Xunlai Window" frame hash

    if coords is None:
        ConsoleLog(
            "LootEx",
            "Vault controls not drawn because the Xunlai Window frame coordinates are None.",
            Console.MessageType.Warning,
        )
        return
    
    width = 30
    PyImGui.set_next_window_pos(coords.right - (width) - 20, coords.top + 50)
    PyImGui.set_next_window_size(width, 0)
    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,
                                Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)    
    if PyImGui.begin(
        "Loot Ex Vault Controls",
        PyImGui.WindowFlags.NoTitleBar
        | PyImGui.WindowFlags.NoResize
        | PyImGui.WindowFlags.NoBackground
        | PyImGui.WindowFlags.AlwaysAutoResize
        | PyImGui.WindowFlags.NoCollapse
        | PyImGui.WindowFlags.NoMove
        | PyImGui.WindowFlags.NoSavedSettings,
    ):
        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(1)

        if _draw_transparent_button(IconsFontAwesome5.ICON_TH, True, width, width):
            imgui_io = PyImGui.get_io()
            if imgui_io.key_ctrl:
                # messaging.SendOpenXunlai(imgui_io.key_shift)
                pass
            else:
                loot_handling.CondenseStacks(Bag.Storage_1, Bag.Storage_14)

        ImGui.show_tooltip("Condense items to full stacks" +
                           "\nHold Ctrl to send message to all accounts" +
                           "\nHold Shift to send message to all accounts excluding yourself")

        PyImGui.end()

def draw_inventory_controls():    
    if not UIManager.IsWindowVisible(WindowID.WindowID_InventoryBags):
        return
    
    coords = settings.FrameCoords(UIManager.GetFrameIDByHash(inventory_frame_hash))

    if coords is None:
        return

    width = 30
    PyImGui.set_next_window_pos(coords.left - (width - 5), coords.top)
    PyImGui.set_next_window_size(width, 0)
    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,
                             Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)

    if PyImGui.begin(
        "Loot Ex Inventory Controls",
        PyImGui.WindowFlags.NoTitleBar
        | PyImGui.WindowFlags.NoResize
        | PyImGui.WindowFlags.NoBackground
        | PyImGui.WindowFlags.AlwaysAutoResize
        | PyImGui.WindowFlags.NoCollapse
        | PyImGui.WindowFlags.NoMove
        | PyImGui.WindowFlags.NoSavedSettings,
    ):
        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(1)

        _draw_inventory_toggle_button(width)
        _draw_date_collection_toggle_button(width)
        _draw_manual_window_toggle_button(width)
        _draw_xunlai_storage_button(width)

        PyImGui.end()

    if settings.current.manual_window_visible:
        settings.current.window_visible = settings.current.manual_window_visible


def _draw_transparent_button(text : str, enabled : bool, width: float, height : float) -> bool:
    """
    Draws a transparent button with the specified icon and width.
    
    Args:
        icon (str): The icon to display on the button.
        width (int): The width of the button.
    
    Returns:
        bool: True if the button was clicked, False otherwise.
    """
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
    PyImGui.push_style_color(
        PyImGui.ImGuiCol.Text,
        Utils.ColorToTuple(
            Utils.RGBToColor(255, 255, 255, 255)
            if enabled
            else Utils.RGBToColor(255, 255, 255, 125)
        ),
    )
    PyImGui.push_style_color(PyImGui.ImGuiCol.Button,
                             Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(
        Utils.RGBToColor(0, 0, 0, 125)))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,
                             Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))

    clicked = PyImGui.button(text, width, height)

    PyImGui.pop_style_var(1)
    PyImGui.pop_style_color(4)

    return clicked
    

def _draw_inventory_toggle_button(width):
    if _draw_transparent_button(IconsFontAwesome5.ICON_CHECK, settings.current.automatic_inventory_handling, width, width):
        imgui_io = PyImGui.get_io()

        if imgui_io.key_ctrl:
            if settings.current.automatic_inventory_handling:
                messaging.SendStopLootHandling(imgui_io.key_shift)
                settings.current.save()
            else:
                messaging.SendStartLootHandling(imgui_io.key_shift)
                settings.current.save()

        else:
            settings.current.automatic_inventory_handling = not settings.current.automatic_inventory_handling
            settings.current.save()

    # ImGui.show_tooltip(
    #     ("Disable" if settings.current.automatic_inventory_handling else "Enable") +
    #     " Inventory Handling" +
    #     "\nHold Ctrl to send message to all accounts" +
    #     "\nHold Shift to send message to all accounts excluding yourself"
    # )


def _draw_date_collection_toggle_button(width):
    if _draw_transparent_button(IconsFontAwesome5.ICON_LANGUAGE, settings.current.collect_items, width, width):
        imgui_io = PyImGui.get_io()

        if imgui_io.key_ctrl:
            if settings.current.collect_items:
                messaging.SendPauseDataCollection(imgui_io.key_shift)
                settings.current.save()
            else:
                messaging.SendStartDataCollection(imgui_io.key_shift)
                settings.current.save()

        else:
            if settings.current.collect_items:
                data_collector.instance.stop_collection()
                settings.current.save()
            else:
                data_collector.instance.start_collection()
                settings.current.save()

    ImGui.show_tooltip(
        ("Disable" if settings.current.collect_items else "Enable") +
        " Item Data Collection" +
        "\nHold Ctrl to send message to all accounts" +
        "\nHold Shift to send message to all accounts excluding yourself"
    )


def _draw_manual_window_toggle_button(width):
    if _draw_transparent_button(IconsFontAwesome5.ICON_COG, settings.current.manual_window_visible, width, width):
        imgui_io = PyImGui.get_io()
        if imgui_io.key_ctrl:
            if settings.current.manual_window_visible:
                messaging.SendHideLootExWindow(imgui_io.key_shift)
                settings.current.save()
            else:
                messaging.SendShowLootExWindow(imgui_io.key_shift)
                settings.current.save()
        else:
            settings.current.manual_window_visible = not settings.current.manual_window_visible
            settings.current.save()

    ImGui.show_tooltip(
        ("Hide" if settings.current.manual_window_visible else "Show") + " Window" +
        "\nHold Ctrl to send message to all accounts" +
        "\nHold Shift to send message to all accounts excluding yourself")


def _draw_xunlai_storage_button(width):
    xunlai_open = Inventory.IsStorageOpen()

    if _draw_transparent_button(
        IconsFontAwesome5.ICON_BOX_OPEN if xunlai_open else IconsFontAwesome5.ICON_BOX, xunlai_open, width, width
    ):
        if xunlai_open:
            # Inventory.close_storage()
            pass
        else:
            imgui_io = PyImGui.get_io()

            if imgui_io.key_ctrl:
                messaging.SendOpenXunlai(imgui_io.key_shift)
            else:
                Inventory.OpenXunlaiWindow()

    ImGui.show_tooltip("Open Xunlai Storage" +
                       "\nHold Ctrl to send message to all accounts" +
                       "\nHold Shift to send message to all accounts excluding yourself")


def draw_data_collector_tab():
    if PyImGui.begin_tab_item("Data Collector"):
        tab_size = PyImGui.get_content_region_avail()
        child_width = (tab_size[0] - 10) / 2
        
        if PyImGui.begin_child("DataCollectorChild", (child_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag):
            PyImGui.text("Data Collector")
            PyImGui.separator()

            if PyImGui.begin_table("DataCollectorTable", 2, PyImGui.TableFlags.ScrollY, 250, 100):
                PyImGui.table_setup_column("Data")
                PyImGui.table_setup_column("Amount")

                # PyImGui.table_headers_row()
                PyImGui.table_next_row()

                PyImGui.table_next_column()
                PyImGui.text(f"Items")
                PyImGui.table_next_column()
                PyImGui.text(f"{len(data.Items)}")

                PyImGui.table_next_column()
                PyImGui.text(f"Weapon Mods")
                PyImGui.table_next_column()
                PyImGui.text(f"{len(data.Weapon_Mods)}")

                PyImGui.table_next_column()
                PyImGui.text(f"Runes")
                PyImGui.table_next_column()
                PyImGui.text(f"{len(data.Runes)}")
            PyImGui.end_table()

            if PyImGui.button("Merge Diffs into Data", 200, 50):
                ConsoleLog(
                    "LootEx",
                    "Merging diffs into data...",
                    Console.MessageType.Info,
                )

                messaging.SendMergingMessage()

            ImGui.show_tooltip("Merge all diff files into the data files.")

            PyImGui.same_line(0, 5)

            if PyImGui.button("Test", 300, 50):
                clipboard_text = "```\n"

                # sort weapon mods by mod_type then by name
                mods = sorted(data.Weapon_Mods.values(), key=lambda x: (
                    x.mod_type, x.names.get(ServerLanguage.English, "")))

                for mod in mods:
                    if not mod.upgrade_exists:
                        continue

                    english = mod.names.get(ServerLanguage.English, None)

                    # check if the mod has a value for each language but Unknown in names
                    has_all_languages = all(
                        mod.names.get(
                            lang) is not None or lang == ServerLanguage.Unknown
                        for lang in ServerLanguage
                    )

                    if not has_all_languages and english:
                        clipboard_text += f"\n{english}"

                clipboard_text += "```"
                PyImGui.set_clipboard_text(clipboard_text)
                
                # Load items modelid_drop_data
                file_directory = os.path.dirname(os.path.abspath(__file__))
                data_directory = os.path.join(file_directory, "data")
                path = os.path.join(data_directory, "modelid_drop_data.json")
               
                            
                            
                
                    
            ImGui.show_tooltip("Copy all weapon mods that have an upgrade to the clipboard.")
            

        PyImGui.end_child()
        
        PyImGui.same_line(0, 5)
        
        PyImGui.begin_child("DataCollectorMaterialsChild", (child_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)
        
        remaining_size = PyImGui.get_content_region_avail()
        if PyImGui.button("Get Material Prices", remaining_size[0], 0):
            ConsoleLog(
                "LootEx",
                "Fetching material prices from the wiki...",
                Console.MessageType.Info,
            )
            
            loot_check.LootCheck.get_material_prices_from_trader()
        
        PyImGui.begin_table("DataCollectorMaterialsTable", 2, PyImGui.TableFlags.ScrollY | PyImGui.TableFlags.Borders, 0, 0)
        PyImGui.table_setup_column("Material")
        PyImGui.table_setup_column("Price")
        PyImGui.table_headers_row()
        
        PyImGui.table_next_row()
        for material in data.Materials.values():
            PyImGui.table_next_column()
            PyImGui.text(material.name)
            PyImGui.table_next_column()
            if material.vendor_value is not None:
                PyImGui.text(utility.Util.format_currency(material.vendor_value))
            else:
                PyImGui.text("N/A")
            ImGui.show_tooltip("Last Checked: " + utility.Util.format_time_ago(datetime.now() - material.vendor_updated) if material.vendor_updated else "Never Updated")

        # for material in data.Rare_Materials.values():
        #     PyImGui.table_next_row()
        #     PyImGui.table_next_column()
        #     PyImGui.text(material.name)
        #     PyImGui.table_next_column()
        #     if material.vendor_value is not None:
        #         PyImGui.text(utility.Util.format_currency(material.vendor_value))
        #     else:
        #         PyImGui.text("N/A")
        #     ImGui.show_tooltip("Last Checked: " + utility.Util.format_time_ago(datetime.now() - material.vendor_updated) if material.vendor_updated else "Never Updated")
                
        PyImGui.end_table()
        
        
        PyImGui.end_child()

        PyImGui.end_tab_item()


def draw_window():
    global first_draw, filtered_weapon_mods, show_add_profile_popup, show_delete_profile_popup, on_screen, window_flags

    if first_draw:
        PyImGui.set_next_window_size(
            settings.current.window_size[0], settings.current.window_size[1]
        )
        PyImGui.set_next_window_pos(
            settings.current.window_position[0], settings.current.window_position[1]
        )
        PyImGui.set_next_window_collapsed(settings.current.window_collapsed, 0)

    screen_width = PyImGui.get_io().display_size_x
    screen_height = PyImGui.get_io().display_size_y
    min_remaining_space = 50

    if (
        settings.current.window_position[0] +
            min_remaining_space > screen_width
        or settings.current.window_position[1] + min_remaining_space > screen_height
    ):
        settings.current.window_position = (
            screen_width / 2, screen_height / 2)
        settings.current.window_size = (screen_width / 2, screen_height / 2)
        ConsoleLog(
            "LootEx",
            "Window position or size is out of bounds, resetting to center.",
            Console.MessageType.Warning,
        )
        settings.current.save()

        PyImGui.set_next_window_pos(
            settings.current.window_position[0], settings.current.window_position[1]
        )
        PyImGui.set_next_window_size(
            settings.current.window_size[0], settings.current.window_size[1]
        )
        PyImGui.set_next_window_collapsed(settings.current.window_collapsed, 0)

    expanded, gui_open = PyImGui.begin_with_close(
        "Loot Ex", settings.current.window_visible, window_flags)
    if gui_open and settings.current.loot_profile:
        window_flags = (
            PyImGui.WindowFlags.NoMove if PyImGui.is_mouse_down(
                0) else PyImGui.WindowFlags.NoFlag
        )

        profile_names = [
            profile.name for profile in settings.current.loot_profiles]
        selected_index = PyImGui.combo(
            "", settings.current.profile_combo, profile_names)

        if settings.current.profile_combo != selected_index:
            ConsoleLog(
                "LootEx",
                f"Profile changed to {profile_names[selected_index]}",
                Console.MessageType.Info,
            )
            settings.current.profile_combo = selected_index
            settings.current.loot_profile = settings.current.loot_profiles[selected_index]
            settings.current.save()

        PyImGui.same_line(0, 5)

        if PyImGui.button(IconsFontAwesome5.ICON_PLUS):
            show_add_profile_popup = not show_add_profile_popup
            if show_add_profile_popup:
                PyImGui.open_popup("Add Profile")
            else:
                PyImGui.close_current_popup()

        ImGui.show_tooltip("Add New Profile")
        PyImGui.same_line(0, 5)

        if PyImGui.button((IconsFontAwesome5.ICON_TRASH)) and len(settings.current.loot_profiles) > 1:
            show_delete_profile_popup = not show_delete_profile_popup
            if show_delete_profile_popup:
                PyImGui.open_popup("Delete Profile")
            else:
                PyImGui.close_current_popup()

        ImGui.show_tooltip("Delete Profile '" +
                           settings.current.loot_profile.name + "'")
        PyImGui.same_line(0, 5)

        btnColor = Utils.RGBToColor(
            0, 255, 0, 255) if settings.current.automatic_inventory_handling else Utils.RGBToColor(255, 0, 0, 125)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text, Utils.ColorToTuple(btnColor))

        if PyImGui.button((IconsFontAwesome5.ICON_PLAY_CIRCLE if settings.current.automatic_inventory_handling else
                           IconsFontAwesome5.ICON_PAUSE_CIRCLE)):
            settings.current.automatic_inventory_handling = not settings.current.automatic_inventory_handling
            settings.current.save()
            ActionQueueManager().ResetQueue("SALVAGE")
            ActionQueueManager().ResetQueue("IDENTIFY")

        PyImGui.pop_style_color(1)
        ImGui.show_tooltip(
            ("Disable" if settings.current.automatic_inventory_handling else "Enable") + " Inventory Handling")

        PyImGui.same_line(0, 5)
        btnColor = Utils.RGBToColor(
            0, 255, 0, 255) if settings.current.collect_items else Utils.RGBToColor(255, 255, 255, 125)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text, Utils.ColorToTuple(btnColor))

        if PyImGui.button(IconsFontAwesome5.ICON_LANGUAGE + IconsFontAwesome5.ICON_USER_SHIELD):
            settings.current.collect_items = not settings.current.collect_items
            settings.current.save()

        PyImGui.pop_style_color(1)
        ImGui.show_tooltip("Collect Items")

        PyImGui.same_line(0, 5)
        btnColor = Utils.RGBToColor(
            0, 255, 0, 255) if settings.current.collect_runes else Utils.RGBToColor(255, 255, 255, 125)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text, Utils.ColorToTuple(btnColor))

        if PyImGui.button(IconsFontAwesome5.ICON_LANGUAGE + IconsFontAwesome5.ICON_SHIELD_ALT):
            settings.current.collect_runes = not settings.current.collect_runes
            settings.current.save()

        PyImGui.pop_style_color(1)
        ImGui.show_tooltip("Collect Runes")

        if PyImGui.begin_tab_bar("LootExTabBar"):
            draw_general_settings()
            draw_loot_filters()
            draw_loot_items()
            draw_weapon_mods()
            draw_runes()
            draw_data_collector_tab()

        PyImGui.end_tab_bar()

        pos = PyImGui.get_window_pos()
        size = PyImGui.get_window_size()

        if settings.current.window_position != (pos[0], pos[1]):
            # ConsoleLog(
            #     "LootEx",
            #     f"Window position changed to ({pos[0]}, {pos[1]})",
            #     Console.MessageType.Debug,
            # )
            settings.current.window_position = (pos[0], pos[1])
            settings.current.save()

        if settings.current.window_size != (size[0], size[1]):
            # ConsoleLog(
            #     "LootEx",
            #     f"Window size changed to ({size[0]}, {size[1]})",
            #     Console.MessageType.Debug,
            # )
            mod_heights.clear()
            settings.current.window_size = (size[0], size[1])
            settings.current.save()

        draw_delete_profile_popup()
        draw_profiles_popup()

        PyImGui.end()

    collapsed = not expanded

    if collapsed != settings.current.window_collapsed:
        settings.current.window_collapsed = collapsed
        settings.current.save()

    if gui_open != settings.current.window_visible:
        settings.current.window_visible = gui_open
        settings.current.manual_window_visible = gui_open
        settings.current.save()

    first_draw = False


def draw_delete_profile_popup():
    global show_delete_profile_popup

    if settings.current.loot_profile is None:
        return

    if show_delete_profile_popup:
        PyImGui.open_popup("Delete Profile")

    if PyImGui.begin_popup("Delete Profile"):
        PyImGui.text(
            f"Are you sure you want to delete the profile '{settings.current.loot_profile.name}'?")
        PyImGui.separator()

        if PyImGui.button("Yes", 100, 0):
            settings.current.loot_profiles.pop(settings.current.profile_combo)
            settings.current.profile_combo = min(
                settings.current.profile_combo, len(
                    settings.current.loot_profiles) - 1
            )
            settings.current.loot_profile = settings.current.loot_profiles[
                settings.current.profile_combo
            ]
            settings.current.save()
            show_delete_profile_popup = False
            PyImGui.close_current_popup()

        PyImGui.same_line(0, 5)

        if PyImGui.button("No", 100, 0):
            show_delete_profile_popup = False
            PyImGui.close_current_popup()

        PyImGui.end_popup()

    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_delete_profile_popup:
            PyImGui.close_current_popup()
            show_delete_profile_popup = False


def draw_profiles_popup():
    global show_add_profile_popup, new_profile_name

    if show_add_profile_popup:
        PyImGui.open_popup("Add Profile")

    if PyImGui.begin_popup("Add Profile"):
        PyImGui.text("Please enter a name for the new profile:")
        PyImGui.separator()

        profile_exists = new_profile_name == "" or any(
            profile.name.lower() == new_profile_name.lower() for profile in settings.current.loot_profiles
        )

        if profile_exists:
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                    Utils.RGBToColor(255, 0, 0, 255))
            )

        profile_name_input = PyImGui.input_text(
            "##NewProfileName", new_profile_name)
        if profile_name_input is not None and profile_name_input != new_profile_name:
            new_profile_name = profile_name_input

        if profile_exists:
            PyImGui.pop_style_color(1)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                    Utils.RGBToColor(255, 255, 255, 120))
            )
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Button, Utils.ColorToTuple(
                    Utils.RGBToColor(26, 38, 51, 125))
            )
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(
                    Utils.RGBToColor(26, 38, 51, 125))
            )
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(
                    Utils.RGBToColor(26, 38, 51, 125))
            )

        PyImGui.same_line(0, 5)

        if PyImGui.button("Create", 100, 0) and not profile_exists:
            if new_profile_name != "" and not profile_exists:
                if settings.current.loot_profile:
                    settings.current.loot_profile.save()

                new_profile = LootProfile(new_profile_name)
                settings.current.loot_profiles.append(new_profile)
                settings.current.profile_combo = len(
                    settings.current.loot_profiles) - 1
                settings.current.loot_profile = new_profile
                settings.current.save()
                settings.current.loot_profile.save()

                new_profile_name = ""
                show_add_profile_popup = False
                PyImGui.close_current_popup()
            else:
                ConsoleLog("LootEx", "Profile name already exists!",
                           Console.MessageType.Error)

        if profile_exists:
            PyImGui.pop_style_color(4)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                    Utils.RGBToColor(255, 0, 0, 255))
            )
            PyImGui.text("Profile name already exists!")
            PyImGui.pop_style_color(1)

        PyImGui.end_popup()

    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_add_profile_popup:
            PyImGui.close_current_popup()
            show_add_profile_popup = False


def draw_general_settings():
    if PyImGui.begin_tab_item("General"):
        tab_size = PyImGui.get_content_region_avail()
        dye_section_width = 250

        if PyImGui.begin_child("GeneralSettingsChild", (tab_size[0] - dye_section_width - 5, tab_size[1]), True, PyImGui.WindowFlags.NoFlag):
            PyImGui.text("Merchant Settings")
            PyImGui.separator()

            subtab_size = PyImGui.get_content_region_avail()

            if PyImGui.begin_child("GeneralSettingsChildInner", (subtab_size[0], subtab_size[1] - 30), True, PyImGui.WindowFlags.NoBackground) and settings.current.loot_profile:
                _update_merchant_setting(
                    "Identification Kits", settings.current.loot_profile.identification_kits)
                _update_merchant_setting(
                    "Salvage Kits", settings.current.loot_profile.salvage_kits)
                _update_merchant_setting(
                    "Expert Salvage Kits", settings.current.loot_profile.expert_salvage_kits)
                _update_merchant_setting(
                    "Lockpicks", settings.current.loot_profile.lockpicks)
                _update_merchant_setting("Sell Threshold", settings.current.loot_profile.sell_threshold,
                                         tooltip="Items with a value equal or above {value} gold will be sold to a merchant instead of being salvaged.")

            PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.same_line(0, 5)

        if PyImGui.begin_child("Dyes", (dye_section_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag) and settings.current.loot_profile:
            PyImGui.text("Dyes")
            PyImGui.text_wrapped(
                "Select the dyes you want to pick up and keep.")
            PyImGui.separator()

            if PyImGui.begin_child("DyesSelection", (dye_section_width - 20, 0), True, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoBackground):
                for dye in DyeColor:
                    if dye != DyeColor.NoColor:
                        if dye not in settings.current.loot_profile.dyes:
                            settings.current.loot_profile.dyes[dye] = False

                        color = utility.Util.GetDyeColor(
                            dye, 205 if settings.current.loot_profile.dyes[dye] else 125)
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color))
                        hover_color = utility.Util.GetDyeColor(dye)
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(hover_color))
                        selected = PyImGui.checkbox(
                            IconsFontAwesome5.ICON_FLASK + " " + dye.name, settings.current.loot_profile.dyes[dye])

                        if settings.current.loot_profile.dyes[dye] != selected:
                            settings.current.loot_profile.dyes[dye] = selected
                            settings.current.loot_profile.save()

                        PyImGui.pop_style_color(2)
                        ImGui.show_tooltip("Dye: " + dye.name)

            PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.end_tab_item()


def _update_merchant_setting(label, current_value, tooltip=None):
    if settings.current.loot_profile is None:
        return

    new_value = PyImGui.input_int(label, current_value)
    if new_value != current_value:
        setattr(settings.current.loot_profile,
                label.replace(" ", "_").lower(), new_value)
        settings.current.loot_profile.save()

    if tooltip:
        ImGui.show_tooltip(tooltip.format(value=new_value))


def draw_loot_filters():
    global show_add_filter_popup

    if PyImGui.begin_tab_item("Filter Based Actions") and settings.current.loot_profile:
        # Get size of the tab
        tab_size = PyImGui.get_content_region_avail()

        # Left panel: Loot Filter Selection
        if PyImGui.begin_child("loot_filter_selection_child", (tab_size[0] * 0.3, tab_size[1]), True, PyImGui.WindowFlags.NoFlag):
            PyImGui.text("Loot Filter Selection")
            PyImGui.separator()
            subtab_size = PyImGui.get_content_region_avail()

            if PyImGui.begin_child("filter_selection_child", (subtab_size[0], subtab_size[1] - 30), True, PyImGui.WindowFlags.NoBackground):
                if settings.current.loot_profile and settings.current.loot_profile.filters:
                    for loot_filter in settings.current.loot_profile.filters:
                        if PyImGui.selectable(loot_filter.name, loot_filter == settings.current.selected_loot_filter, PyImGui.SelectableFlags.NoFlag, (0, 0)):
                            settings.current.selected_loot_filter = loot_filter

            PyImGui.end_child()

            if PyImGui.button("Add Filter", subtab_size[0]):
                show_add_filter_popup = not show_add_filter_popup
                if show_add_filter_popup:
                    PyImGui.open_popup("Add Filter")

        PyImGui.end_child()

        PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

        # Right panel: Loot Filter Details
        if PyImGui.begin_child("loot_filter_child", (tab_size[0] - (tab_size[0] * 0.3) - 10, tab_size[1]), True, PyImGui.WindowFlags.NoFlag):
            if settings.current.selected_loot_filter:
                loot_filter = settings.current.selected_loot_filter

                # Edit filter name
                name = PyImGui.input_text(
                    "##name_edit", loot_filter.name)
                if name and name != loot_filter.name:
                    loot_filter.name = name
                    settings.current.loot_profile.save()

                PyImGui.same_line(0, 5)

                # Delete filter button
                if PyImGui.button(IconsFontAwesome5.ICON_TRASH):
                    settings.current.loot_profile.filters.remove(
                        loot_filter)
                    settings.current.loot_profile.save()
                    settings.current.selected_loot_filter = settings.current.loot_profile.filters[
                        0] if settings.current.loot_profile.filters else None
                    show_add_filter_popup = False
                    PyImGui.close_current_popup()

                # Filter actions
                if PyImGui.begin_child("loot_filter_actions", (0, 100), True, PyImGui.WindowFlags.NoFlag):
                    PyImGui.text("Actions")
                    PyImGui.separator()

                    if loot_filter.actions.explorable:
                        action_names = [
                            action.name for action in item_actions.ItemAction]
                        selected_action = PyImGui.combo("Explorable", action_names.index(
                            loot_filter.actions.explorable.name), action_names)
                        if selected_action != loot_filter.actions.explorable:
                            loot_filter.actions.explorable = item_actions.ItemAction[
                                action_names[selected_action]]
                            settings.current.loot_profile.save()

                    if loot_filter.actions.outpost:
                        action_names = [
                            action.name for action in item_actions.ItemAction]
                        selected_action = PyImGui.combo("Outpost", action_names.index(
                            loot_filter.actions.outpost.name), action_names)
                        if selected_action != loot_filter.actions.outpost:
                            loot_filter.actions.outpost = item_actions.ItemAction[
                                action_names[selected_action]]
                            settings.current.loot_profile.save()

                PyImGui.end_child()

                # Filter item types
                sub_subtab_size = PyImGui.get_content_region_avail()
                if PyImGui.begin_child("loot_item_types_filter_table", (sub_subtab_size[0] / 3 * 2, 0), True, PyImGui.WindowFlags.NoFlag):
                    PyImGui.begin_table(
                        "loot_filter_table", 3, PyImGui.TableFlags.ScrollY)

                    count = 0
                    chunk_size = len(loot_filter.item_types) / 3
                    PyImGui.table_next_column()

                    sorted_item_types = sorted(
                        ItemType, key=lambda x: x.name)

                    for item_type in sorted_item_types:
                        count += 1

                        if count > chunk_size:
                            PyImGui.table_next_column()
                            count = 1

                        if loot_filter.item_types[item_type] is None:
                            continue

                        changed, loot_filter.item_types[item_type] = draw_item_type_selectable(
                            item_type, loot_filter.item_types[item_type])
                        if changed:
                            settings.current.loot_profile.save()

                    PyImGui.end_table()

                PyImGui.end_child()

                PyImGui.same_line(sub_subtab_size[0] / 3 * 2 + 20, 0)

                # Filter rarities
                if PyImGui.begin_child("loot_rarity_filter_table", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                    for rarity in Rarity:
                        if rarity not in loot_filter.rarities:
                            loot_filter.rarities[rarity] = False

                        color = utility.Util.GetRarityColor(rarity)

                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color["text"]))
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color["content"]))
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(color["frame"]))

                        label = f"Rarity: {rarity.name}"
                        unique_id = f"##{rarity.value}"
                        rarity_selected = PyImGui.checkbox(
                            IconsFontAwesome5.ICON_SHIELD_ALT + " " + label + unique_id, loot_filter.rarities[rarity])

                        if loot_filter.rarities[rarity] != rarity_selected:
                            loot_filter.rarities[rarity] = rarity_selected
                            settings.current.loot_profile.save()

                        PyImGui.pop_style_color(3)

                PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.end_tab_item()

        draw_add_loot_filter_popup()


def draw_add_loot_filter_popup():
    global show_add_filter_popup, filter_name

    if settings.current.loot_profile is None:
        return

    if show_add_filter_popup:
        PyImGui.open_popup("Add Filter")

    if PyImGui.begin_popup("Add Filter"):
        PyImGui.text("Please enter a name for the new filter:")
        PyImGui.separator()

        filter_exists = filter_name == "" or any(
            loot_filter.name.lower() == filter_name.lower()
            for loot_filter in settings.current.loot_profile.filters
        )

        if filter_exists:
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)),
            )

        filter_name_input = PyImGui.input_text("##NewFilterName", filter_name)
        if filter_name_input is not None and filter_name_input != filter_name:
            filter_name = filter_name_input

        if filter_exists:
            PyImGui.pop_style_color(1)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 120)),
            )
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Button,
                Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)),
            )
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ButtonHovered,
                Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)),
            )
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.ButtonActive,
                Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)),
            )

        PyImGui.same_line(0, 5)

        if PyImGui.button("Create", 100, 0) and not filter_exists:
            if filter_name != "" and not filter_exists:
                settings.current.loot_profile.filters.append(
                    LootFilter(filter_name))
                settings.current.loot_profile.save()

                filter_name = ""
                show_add_filter_popup = False
                PyImGui.close_current_popup()
            else:
                ConsoleLog(
                    "LootEx",
                    "Filter name already exists!",
                    Console.MessageType.Error,
                )

        if filter_exists:
            PyImGui.pop_style_color(4)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)),
            )
            PyImGui.text("Filter name already exists!")
            PyImGui.pop_style_color(1)

        PyImGui.end_popup()

    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_add_filter_popup:
            PyImGui.close_current_popup()
            show_add_filter_popup = False

def draw_filter_popup():
    global item_search, filtered_loot_items, filter_popup, filters, selected_filter

    if filter_popup:
        PyImGui.open_popup("Filter Loot Items")

    if PyImGui.begin_popup("Filter Loot Items"):
        
        remaining_size = PyImGui.get_content_region_avail()
        
        for filter in filters:
            if filter:
                if PyImGui.selectable(filter.name, selected_filter == filter, PyImGui.SelectableFlags.NoFlag, (remaining_size[0], 0)):
                    selected_filter = filter
                    filter_items(item_search)
                    
                    filter_popup = False
                    PyImGui.close_current_popup()
    
        PyImGui.end_popup()
    
    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if filter_popup:
            PyImGui.close_current_popup()
            filter_popup = False        
    

def draw_loot_items():
    global first_draw, selected_loot_items, filtered_loot_items, item_search, condition_name, selected_condition, loot_items_selection_dragging, filter_popup

    if first_draw:
        ConsoleLog(
            "LootEx",
            "Loading Loot Items...",
            Console.MessageType.Info,
        )
        for mod in data.Weapon_Mods.values():
            if mod.mod_type == enum.ModType.Prefix:
                prefix_names.append(mod.name)

            elif mod.mod_type == enum.ModType.Suffix:
                suffix_names.append(mod.name)

            elif mod.mod_type == enum.ModType.Inherent:
                inherent_names.append(mod.name)

        filtered_loot_items = [
            SelectableItem(item) for item in data.Items.values()
        ]

    if PyImGui.begin_tab_item("Item Actions") and settings.current.loot_profile:
        # Get size of the tab
        tab_size = PyImGui.get_content_region_avail()

        # Left panel: Loot Items Selection
        if PyImGui.begin_child("loot_items_selection_child", (tab_size[0] * 0.3, tab_size[1]), False, PyImGui.WindowFlags.NoFlag):
            child_size = PyImGui.get_content_region_avail()

            PyImGui.push_item_width(child_size[0] - 35)
            search = PyImGui.input_text("##search_item", item_search)
            search_active = PyImGui.is_item_active()

            PyImGui.same_line(0, 5)
            if PyImGui.button(IconsFontAwesome5.ICON_FILTER):
                filter_popup = not filter_popup
                if filter_popup:
                    PyImGui.open_popup("Filter Loot Items")
                pass
            
            if (search is None or search == "") and not search_active:
                PyImGui.same_line(5, 0)
                PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                    Utils.RGBToColor(255, 255, 255, 125)))
                PyImGui.text(IconsFontAwesome5.ICON_SEARCH +
                             " Search for Item Name or Model ID...")
                PyImGui.pop_style_color(1)

            if search is not None and search != item_search:
                filter_items(search)

            
            if PyImGui.begin_child("selectable_items", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                for item in filtered_loot_items:
                    if item:
                        if PyImGui.is_rect_visible(1, 20):
                            draw_selectable_item(item)
                        else:
                            PyImGui.dummy(0, 20)

            PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

        # Right panel: Loot Item Details
        if PyImGui.begin_child("loot_item_child", (tab_size[0] - (tab_size[0] * 0.3) - 10, tab_size[1]), False, PyImGui.WindowFlags.NoFlag):
            selected_loot_item = selected_loot_items[0] if selected_loot_items and len(
                selected_loot_items) == 1 else None

            if selected_loot_item:
                has_settings = selected_loot_item.item_info.model_id and selected_loot_item.item_info.model_id in settings.current.loot_profile.items
                details_height = 130
                posX, posY = PyImGui.get_cursor_screen_pos()
                
                if PyImGui.begin_child("item_info", (0, details_height), True, PyImGui.WindowFlags.NoFlag):
                    
                
                    if PyImGui.begin_child("item_texture", (details_height, 0), False, PyImGui.WindowFlags.NoFlag):
                                                                        
                        remaining_size = PyImGui.get_content_region_avail()
                        if is_mouse_in_rect((posX + 10, posY + 10, details_height - 20, details_height - 20)):                                
                            if PyImGui.button(IconsFontAwesome5.ICON_GLOBE, details_height - 20, details_height - 20) and selected_loot_item.item_info.wiki_url:
                                Player.SendChatCommand(
                                    "wiki " + selected_loot_item.item_info.name)

                                # start the url in the default browser
                                webbrowser.open(
                                    selected_loot_item.item_info.wiki_url)

                            ImGui.show_tooltip(
                                "Open the wiki page for this item.\n" +
                                "If the item is not found, it will search for the item name in the wiki." if selected_loot_item.item_info.wiki_url else "This item does not have a wiki page set yet."
                            )
                        else:
                            color = Utils.RGBToColor(64, 64, 64, 255)
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.Button, Utils.ColorToTuple(color))
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(color))
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(color))
                            PyImGui.button(IconsFontAwesome5.ICON_SHIELD_ALT + "##" + str(
                                selected_loot_item.item_info.model_id), details_height - 20, details_height - 20)
                            PyImGui.pop_style_color(3)
                        
                        
                    PyImGui.end_child()

                    PyImGui.same_line(0, 5)

                    if PyImGui.begin_child("item_details", (0, 0), False, PyImGui.WindowFlags.NoFlag):
                        PyImGui.text(
                            "Name: " + selected_loot_item.item_info.name)

                        PyImGui.text("Model ID: " +
                                     str(selected_loot_item.item_info.model_id))
                        PyImGui.text(
                            "Type: " + utility.Util.GetItemType(selected_loot_item.item_info.item_type).name)
                        
                        if selected_loot_item.item_info.common_salvage:
                            summaries = [salvage_info.summary for salvage_info in selected_loot_item.item_info.common_salvage.values()]                        
                            PyImGui.text("Salvage: " + ", ".join(summaries))
                        
                        if selected_loot_item.item_info.rare_salvage:
                            summaries = [salvage_info.summary for salvage_info in selected_loot_item.item_info.rare_salvage.values()]   
                            PyImGui.text("Rare Salvage: " + ", ".join(summaries))

                    PyImGui.end_child()

                PyImGui.end_child()

                if PyImGui.begin_child("item_settings", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                    if has_settings:
                        loot_item = settings.current.loot_profile.items.get(
                            selected_loot_item.item_info.model_id)

                        if PyImGui.begin_tab_bar("item_conditions") and loot_item:
                            for condition in loot_item.conditions:
                                if PyImGui.begin_tab_item(condition.name) and condition and selected_loot_item:
                                    if selected_condition != condition:
                                        selected_condition = condition
                                        condition_name = condition.name

                                    remaining_size = PyImGui.get_content_region_avail()

                                    PyImGui.begin_child(
                                        "item_condition_details", (0, remaining_size[1] - 32), False, PyImGui.WindowFlags.NoFlag)
                                    condition_name = PyImGui.input_text(
                                        "##name_edit", condition_name)
                                    PyImGui.same_line(0, 5)
                                    if PyImGui.button("Rename") and condition_name and condition_name != condition.name:
                                        condition.name = condition_name
                                        settings.current.loot_profile.save()

                                    PyImGui.separator()

                                    # Get the action names, replace underscores with spaces, split at space, all lowercase and first letter to upper case
                                    action_names = [
                                        utility.Util.GetActionName(action) for action in item_actions.ItemAction]
                                    actions = [
                                        action for action in item_actions.ItemAction]
                                    explorable = PyImGui.combo("Explorable", action_names.index(
                                        utility.Util.GetActionName(condition.item_actions.explorable)), action_names)

                                    if actions[explorable] != condition.item_actions.explorable:
                                        condition.item_actions.explorable = actions[explorable]
                                        settings.current.loot_profile.save()

                                    outpost = PyImGui.combo("Outpost", action_names.index(
                                        utility.Util.GetActionName(condition.item_actions.outpost)), action_names)

                                    if outpost != condition.item_actions.outpost:
                                        condition.item_actions.outpost = actions[outpost]
                                        settings.current.loot_profile.save()

                                    if loot_item:
                                        label_spacing = 120
                                        item_data = utility.Util.GetDataItem(
                                            loot_item.model_id)
                                        item_type = item_data.item_type if item_data else None

                                        if (utility.Util.IsArmor(loot_item)):
                                            PyImGui.text(
                                                "IsArmor Type: " + str(True))

                                        elif utility.Util.IsWeapon(loot_item):
                                            PyImGui.text("")
                                            PyImGui.text("Item Stats")
                                            PyImGui.separator()

                                            available_attributes = selected_loot_item.item_info.attributes if selected_loot_item.item_info.attributes else utility.Util.GetAttributes(
                                                selected_loot_item.item_info.item_type)
                                            if len(available_attributes) > 1:
                                                available_attributes.insert(
                                                    0, Attribute.None_)

                                            if not condition.requirements:
                                                condition.requirements = {attribute: models.IntRange(
                                                    0, 13) for attribute in available_attributes}

                                            min_requirement = min(
                                                [attribute.min for attribute in condition.requirements.values()])
                                            max_requirement = max(
                                                [attribute.max for attribute in condition.requirements.values()])

                                            min_damage_in_requirements = utility.Util.GetMaxDamage(
                                                min_requirement, selected_loot_item.item_info.item_type).min
                                            max_damage_in_requirements = utility.Util.GetMaxDamage(
                                                max_requirement, selected_loot_item.item_info.item_type).max

                                            if not condition.damage_range:
                                                condition.damage_range = models.IntRange(
                                                    min_damage_in_requirements, max_damage_in_requirements)

                                            draw_vertical_centered_text(
                                                "Damage Range", label_spacing)
                                            remaining_size = PyImGui.get_content_region_avail()
                                            item_width = (
                                                remaining_size[0] - 10) / 2

                                            if condition.damage_range.max > max_damage_in_requirements:
                                                condition.damage_range.max = max_damage_in_requirements
                                                settings.current.loot_profile.save()

                                            PyImGui.push_item_width(item_width)
                                            value = PyImGui.slider_int(
                                                "##MinDamage", condition.damage_range.min, 0, min_damage_in_requirements)
                                            if value > condition.damage_range.max:
                                                condition.damage_range.max = value
                                                settings.current.loot_profile.save()
                                            elif value != condition.damage_range.min:
                                                condition.damage_range.min = value
                                                settings.current.loot_profile.save()

                                            PyImGui.same_line(0, 5)
                                            PyImGui.push_item_width(item_width)
                                            value = PyImGui.slider_int(
                                                "##MaxDamage", condition.damage_range.max, min_damage_in_requirements, max_damage_in_requirements)
                                            if value < condition.damage_range.min:
                                                condition.damage_range.min = value
                                                settings.current.loot_profile.save()

                                            elif value != condition.damage_range.max:
                                                condition.damage_range.max = value
                                                settings.current.loot_profile.save()

                                            draw_vertical_centered_text(
                                                "Prefix|Suffix", label_spacing)
                                            prefix_name = utility.Util.GetWeaponModName(
                                                condition.prefix_mod) if condition.prefix_mod else ""
                                            PyImGui.push_item_width(item_width)
                                            mod = PyImGui.combo("##Prefix", prefix_names.index(
                                                prefix_name) if condition.prefix_mod else 0, prefix_names)
                                            if (prefix_names[mod] != prefix_name and mod > 0) or (condition.prefix_mod and mod == 0):
                                                modname = prefix_names[mod]
                                                if modname != None and modname != "Any":
                                                    # Get the mod struct from data.WeaponMods
                                                    for weapon_mod in data.Weapon_Mods.values():
                                                        if weapon_mod.name == modname:
                                                            condition.prefix_mod = weapon_mod.identifier
                                                            settings.current.loot_profile.save()
                                                            break
                                                elif condition.prefix_mod and mod == 0:
                                                    condition.prefix_mod = None
                                                    settings.current.loot_profile.save()

                                            PyImGui.same_line(0, 5)
                                            suffix_name = utility.Util.GetWeaponModName(
                                                condition.suffix_mod) if condition.suffix_mod else ""
                                            PyImGui.push_item_width(item_width)
                                            mod = PyImGui.combo("##Suffix", suffix_names.index(
                                                suffix_name) if condition.suffix_mod else 0, suffix_names)
                                            if suffix_names[mod] != suffix_names and mod > 0 or (condition.suffix_mod and mod == 0):
                                                modname = suffix_names[mod]
                                                if modname != None and modname != "Any":
                                                    # Get the mod struct from data.WeaponMods
                                                    for weapon_mod in data.Weapon_Mods.values():
                                                        if weapon_mod.name == modname:
                                                            condition.suffix_mod = weapon_mod.identifier
                                                            settings.current.loot_profile.save()
                                                            break
                                                elif condition.suffix_mod and mod == 0:
                                                    condition.suffix_mod = None
                                                    settings.current.loot_profile.save()

                                            draw_vertical_centered_text(
                                                "Inherent", label_spacing)
                                            inherent_name = utility.Util.GetWeaponModName(
                                                condition.inherent_mod) if condition.inherent_mod else ""
                                            PyImGui.push_item_width(item_width)
                                            mod = PyImGui.combo("##Inherent", inherent_names.index(utility.Util.GetWeaponModName(
                                                condition.inherent_mod)) if condition.inherent_mod else 0, inherent_names)
                                            if inherent_names[mod] != inherent_name and mod > 0 or (condition.inherent_mod and mod == 0):
                                                modname = inherent_names[mod]
                                                if modname != None and modname != "Any":
                                                    # Get the mod struct from data.WeaponMods
                                                    for weapon_mod in data.Weapon_Mods.values():
                                                        if weapon_mod.name == modname:
                                                            condition.inherent_mod = weapon_mod.identifier
                                                            settings.current.loot_profile.save()
                                                            break
                                                elif condition.inherent_mod and mod == 0:
                                                    condition.inherent_mod = None
                                                    settings.current.loot_profile.save()

                                            PyImGui.same_line(0, 5)
                                            PyImGui.push_item_width(item_width)
                                            checked = PyImGui.checkbox(
                                                "Old School Only", condition.old_school_only)
                                            if condition.old_school_only != checked:
                                                condition.old_school_only = checked
                                                settings.current.loot_profile.save()

                                            PyImGui.text("")
                                            PyImGui.text("Attribute Ranges")
                                            PyImGui.separator()

                                            for attribute, requirement in condition.requirements.items():
                                                if requirement == None:
                                                    continue

                                                draw_vertical_centered_text(
                                                    utility.Util.GetAttributeName(attribute) if attribute != Attribute.None_ else "Any", label_spacing)

                                                remaining_size = PyImGui.get_content_region_avail()
                                                item_width = (
                                                    remaining_size[0] - 10) / 2

                                                PyImGui.push_item_width(
                                                    item_width)
                                                value = PyImGui.slider_int(
                                                    "##MinRequirement", requirement.min, 0, 13)
                                                if value > requirement.max:
                                                    requirement.max = value
                                                    settings.current.loot_profile.save()

                                                elif value != requirement.min:
                                                    requirement.min = value
                                                    settings.current.loot_profile.save()

                                                PyImGui.same_line(0, 5)
                                                PyImGui.push_item_width(
                                                    item_width)
                                                value = PyImGui.slider_int(
                                                    "##MaxRequirement", requirement.max, 0, 13)
                                                if value < requirement.min:
                                                    requirement.min = value
                                                    settings.current.loot_profile.save()

                                                elif value != requirement.max:
                                                    requirement.max = value
                                                    settings.current.loot_profile.save()

                                    PyImGui.end_child()

                                    remaining_size = PyImGui.get_content_region_avail()
                                    width = remaining_size[0] / 2

                                    if PyImGui.button(IconsFontAwesome5.ICON_TRASH, width, 25):
                                        if  len(loot_item.conditions) > 1:
                                            loot_item.conditions.remove(condition)
                                            settings.current.loot_profile.save()
                                        else:
                                            del settings.current.loot_profile.items[loot_item.model_id]
                                            selected_loot_item = None
                                            
                                    ImGui.show_tooltip("Delete Condition")

                                    PyImGui.same_line(0, 5)

                                    if PyImGui.button(IconsFontAwesome5.ICON_PLUS, width, 25):
                                        loot_item.conditions.append(
                                            ConfigurationCondition("New Condition"))
                                        settings.current.loot_profile.save()
                                    ImGui.show_tooltip("Add Condition")

                                    PyImGui.end_tab_item()
                            PyImGui.end_tab_bar()

                    else:
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(
                            Utils.RGBToColor(255, 0, 0, 255)))
                        PyImGui.text_wrapped("Item is not yet configured.")
                        PyImGui.pop_style_color(1)

                        if PyImGui.button(IconsFontAwesome5.ICON_PLUS + " Add to Profile", 0, 25) and selected_loot_item and selected_loot_item.item_info.model_id not in settings.current.loot_profile.items:
                            settings.current.loot_profile.items[selected_loot_item.item_info.model_id] = ItemConfiguration(
                                selected_loot_item.item_info.model_id)
                            settings.current.loot_profile.save()

                PyImGui.end_child()

            elif selected_loot_items and len(selected_loot_items) > 1:
                PyImGui.begin_child("multiple_items_selected",
                                    (0, 0), True, PyImGui.WindowFlags.NoFlag)

                PyImGui.text("Multiple Items Selected")
                PyImGui.separator()
                PyImGui.text_wrapped(
                    "You can create the default rule to stash them for all of them or delete all rules for these items.")

                if PyImGui.button(IconsFontAwesome5.ICON_PLUS + " Create Default Rule", 0, 25):
                    for item in selected_loot_items:
                        if item and item.item_info.model_id and item.item_info.model_id not in settings.current.loot_profile.items:
                            settings.current.loot_profile.items[item.item_info.model_id] = ItemConfiguration(
                                item.item_info.model_id)
                            settings.current.loot_profile.save()

                if PyImGui.button(IconsFontAwesome5.ICON_TRASH + " Delete All Rules", 0, 25):
                    for item in selected_loot_items:
                        if item and item.item_info.model_id and item.item_info.model_id in settings.current.loot_profile.items:
                            settings.current.loot_profile.items.pop(
                                item.item_info.model_id, None)
                            settings.current.loot_profile.save()

                PyImGui.end_child()
            else:
                PyImGui.text("No Item Selected")

        PyImGui.end_child()

        draw_filter_popup()
        PyImGui.end_tab_item()

def filter_items(search):
    global item_search, filtered_loot_items
    item_search = search
    
    filtered_loot_items = [
                    SelectableItem(item) for item in data.Items.values()
                    if item and item.name and (item.name.lower().find(item_search.lower()) != -1 or str(item.model_id).find(item_search.lower()) != -1) and (selected_filter is None or selected_filter.match(item))
                ]

def _calc_mod_description_height(mod, tab_width: float) -> float:
    base_height = 48
    weapon_types_height = 32
    text_size_x, text_size_y = PyImGui.calc_text_size(mod.description)

    lines_of_text = math.ceil(text_size_x / (tab_width - 60))
    required_text_height = (lines_of_text * text_size_y)

    height = base_height + required_text_height + weapon_types_height
    return height


def mouse_within_rect(mouse_x, mouse_y, x, y, width, height):
    return (x <= mouse_x <= x + width) and (y <= mouse_y <= y + height)


def filter_weapon_mods():
    global mod_search, filtered_weapon_mods, mod_heights

    if mod_search == "":
        filtered_weapon_mods = [SelectableWrapper(
            v) for k, v in data.Weapon_Mods.items() if v]

    else:
        filtered_weapon_mods = []
        for mod in data.Weapon_Mods.values():
            if mod and mod.name and (mod.name.lower().find(mod_search.lower()) != -1 or mod.description.lower().find(mod_search.lower()) != -1 or str(mod.identifier).find(mod_search.lower()) != -1):
                filtered_weapon_mods.append(SelectableWrapper(mod))


def draw_weapon_mods():
    global mod_search, filtered_weapon_mods, scroll_bar_visible, mod_heights, first_draw

    if first_draw:
        filter_weapon_mods()

    tab_name = "Weapon Mods"
    if PyImGui.begin_tab_item(tab_name) and settings.current.loot_profile:
        # Get size of the tab
        tab_size = PyImGui.get_content_region_avail()

        # Search bar for weapon mods
        PyImGui.push_item_width(tab_size[0] - 20)
        search_input = PyImGui.input_text("##Search", mod_search)
        if (search_input is None or search_input == "") and not PyImGui.is_item_active():
            PyImGui.same_line(15, 0)
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 125)),
            )
            PyImGui.text(IconsFontAwesome5.ICON_SEARCH +
                         " Search for Mod Name, Description or Mod Struct...")
            PyImGui.pop_style_color(1)

        if search_input is not None and search_input != mod_search:
            mod_search = search_input
            filter_weapon_mods()

        selection_width = tab_size[0]  # max(255, tab_size[0] * 0.3)
        edit_width = tab_size[0] - selection_width - 20

        PyImGui.begin_child(
            "ModSelectionsChild", (selection_width, 0), True, PyImGui.WindowFlags.NoFlag)
        first_mod = False
        last_mod = False
        selected_weapon_mod = None

        for selectable in filtered_weapon_mods:
            m: models.WeaponMod = selectable.object
            selected_weapon_mod = m if selectable.is_selected else selected_weapon_mod

            if not m.identifier in mod_heights:
                mod_heights[m.identifier] = _calc_mod_description_height(
                    m, selection_width)

            first_mod = PyImGui.is_rect_visible(
                1, mod_heights[m.identifier]) if not first_mod else first_mod

            if not first_mod or last_mod:
                PyImGui.dummy(0, int(mod_heights[m.identifier]))
                continue

            last_mod = (first_mod and not PyImGui.is_rect_visible(
                1, mod_heights[m.identifier])) if not last_mod else last_mod

            is_in_profile = settings.current.loot_profile.contains_weapon_mod(
                m.identifier) if settings.current.loot_profile else None

            def get_frame_color():
                base_color = (255, 255, 255, 255) if not is_in_profile else (
                    255, 204, 85, 255)
                return Utils.RGBToColor(base_color[0], base_color[1], base_color[2], 150)

            if is_in_profile:
                color = Utils.RGBToColor(255, 204, 85, 255)
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.Text,
                    Utils.ColorToTuple(color),
                )

            color = get_frame_color()
            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Border,
                Utils.ColorToTuple(color),
            )

            if selectable.is_hovered:
                color = Utils.RGBToColor(255, 255, 255, 15)
                PyImGui.push_style_color(
                    PyImGui.ImGuiCol.ChildBg,
                    Utils.ColorToTuple(color),
                )

            PyImGui.begin_child(
                id=f"ModSelectable{m.identifier}", size=(0.0, mod_heights[m.identifier]), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse)

            draw_vertical_centered_text(
                IconsFontAwesome5.ICON_SHIELD_ALT, 35, 24)
            draw_vertical_centered_text(m.applied_name, None, 24)

            if is_in_profile:
                PyImGui.pop_style_color(1)

            PyImGui.pop_style_color(1)

            if selectable.is_hovered:
                PyImGui.pop_style_color(1)

            PyImGui.separator()

            # PyImGui.dummy(0, 0)
            # PyImGui.same_line(0, 28)

            PyImGui.push_style_color(
                PyImGui.ImGuiCol.Text,
                (1, 1, 1, 0.75),
            )
            PyImGui.text_wrapped(m.description)
            PyImGui.pop_style_color(1)

            is_tooltip_visible = False
            if settings.current.loot_profile:
                for weapon_type in ItemType:
                    if not m.has_item_type(weapon_type) or weapon_type >= ItemType.Weapon:
                        continue

                    is_selected = m.identifier in settings.current.loot_profile.weapon_mods and weapon_type.name in settings.current.loot_profile.weapon_mods[
                        m.identifier] and settings.current.loot_profile.weapon_mods[m.identifier][weapon_type.name] or False

                    selected = toggle_button(
                        label = f"{utility.Util.reformat_string(weapon_type.name)}##{m.identifier}{weapon_type.name}", v = is_selected, width= 100, height= 20,
                        default_color=Utils.ColorToTuple(Utils.RGBToColor(255, 204, 85, 155)),
                        hover_color=Utils.ColorToTuple(Utils.RGBToColor(255, 204, 85, 180)),
                        active_color=Utils.ColorToTuple(Utils.RGBToColor(2255, 204, 85, 180))
                        )
                    if selected != is_selected:
                        if not settings.current.loot_profile.weapon_mods.get(m.identifier, None):
                            settings.current.loot_profile.weapon_mods[m.identifier] = {
                            }

                        if PyImGui.get_io().key_ctrl:
                            for weapon_type in ItemType:
                                settings.current.loot_profile.weapon_mods[
                                    m.identifier][weapon_type.name] = selected
                        else:
                            settings.current.loot_profile.weapon_mods[m.identifier][weapon_type.name] = selected

                        settings.current.loot_profile.save()
                        filter_weapon_mods()

                    is_tooltip_visible = is_tooltip_visible or PyImGui.is_item_hovered()

                    ImGui.show_tooltip(
                        f"Toggle {utility.Util.reformat_string(weapon_type.name)} for this mod.\n" +
                        "If selected, the mod will be picked up and stored when found." +
                        "\nHold CTRL to toggle all weapon types at once."
                    )

                    PyImGui.same_line(0, 5)

            PyImGui.end_child()
            selectable.is_hovered = PyImGui.is_item_hovered()

            if PyImGui.is_item_clicked(0) and settings.current.loot_profile:
                selectable.is_selected = not selectable.is_selected
                for s in filtered_weapon_mods:
                    if s != selectable:
                        s.is_selected = False

            if is_in_profile:
                PyImGui.pop_style_color(2)

            if not is_tooltip_visible:
                draw_weapon_mod_tooltip(m)

        PyImGui.end_child()

        # PyImGui.same_line(0, 5)

        # PyImGui.begin_child(
        #     "ModEditChild", (edit_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)

        # PyImGui.text("Mod Details")
        # PyImGui.separator()

        # PyImGui.text("Selected Mod: " + (selected_weapon_mod.name if selected_weapon_mod else "None"))

        # PyImGui.end_child()

        if False:
            # Table headers
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.ChildBorderSize, 0)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.CellPadding, 2, 2)
            if PyImGui.begin_child(
                f"{tab_name}TableHeaders#1",
                (tab_size[0] - 20 if scroll_bar_visible else 0, 20),
                True,
                PyImGui.WindowFlags.NoBackground,
            ):
                PyImGui.begin_table(
                    "Weapon Mods Table",
                    len(weapon_types) + 4,
                    PyImGui.TableFlags.NoFlag,
                )
                PyImGui.table_setup_column(
                    "##Texture", PyImGui.TableColumnFlags.WidthFixed, 50)
                PyImGui.table_setup_column(
                    "Name", PyImGui.TableColumnFlags.WidthFixed, 150)

                PyImGui.table_setup_column(
                    "Description", PyImGui.TableColumnFlags.WidthFixed, 250)

                PyImGui.table_setup_column(
                    "Inscription", PyImGui.TableColumnFlags.WidthFixed, 50
                )

                for weapon_type in weapon_types:
                    PyImGui.table_setup_column(
                        weapon_type.name, PyImGui.TableColumnFlags.WidthFixed, 50
                    )

                PyImGui.table_headers_row()
                PyImGui.end_table()

            PyImGui.end_child()

            # Table content
            scroll_bar_visible = False
            if PyImGui.begin_child(
                f"{tab_name}#1", (0, 0), True, PyImGui.WindowFlags.NoBackground
            ):
                PyImGui.begin_table(
                    "Weapon Mods Table",
                    len(weapon_types) + 4,
                    PyImGui.TableFlags.RowBg | PyImGui.TableFlags.BordersInnerH | PyImGui.TableFlags.ScrollY,
                )
                PyImGui.table_setup_column(
                    "##Texture", PyImGui.TableColumnFlags.WidthFixed, 50)
                PyImGui.table_setup_column(
                    "Name", PyImGui.TableColumnFlags.WidthFixed, 150)

                PyImGui.table_setup_column(
                    "Description", PyImGui.TableColumnFlags.WidthFixed, 250)

                PyImGui.table_setup_column(
                    "Inscription", PyImGui.TableColumnFlags.WidthFixed, 50
                )

                for weapon_type in weapon_types:
                    PyImGui.table_setup_column(
                        weapon_type.name, PyImGui.TableColumnFlags.WidthFixed, 50
                    )

                server_language = utility.Util.get_server_language()
                for mod in filtered_weapon_mods.values():
                    if not mod or not mod.identifier:
                        continue

                    keep = settings.current.loot_profile.weapon_mods.get(
                        mod.identifier, None) if settings.current.loot_profile else None

                    if keep:
                        color = utility.Util.GetRarityColor(Rarity.Gold)[
                            "text"]
                        PyImGui.push_style_color(
                            PyImGui.ImGuiCol.Text,
                            Utils.ColorToTuple(color),
                        )

                    PyImGui.table_next_row()
                    # Mod texture
                    PyImGui.table_next_column()
                    PyImGui.push_style_color(
                        PyImGui.ImGuiCol.Button, Utils.ColorToTuple(
                            Utils.RGBToColor(255, 255, 255, 0))
                    )
                    PyImGui.push_style_color(
                        PyImGui.ImGuiCol.ButtonHovered,
                        Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)),
                    )
                    PyImGui.push_style_color(
                        PyImGui.ImGuiCol.ButtonActive,
                        Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)),
                    )
                    PyImGui.push_style_var2(
                        ImGui.ImGuiStyleVar.FramePadding, 5, 8)
                    PyImGui.button(
                        IconsFontAwesome5.ICON_SHIELD_ALT + f"##{mod.identifier}")
                    PyImGui.pop_style_color(3)
                    PyImGui.pop_style_var(1)

                    # Mod name
                    PyImGui.table_next_column()
                    color = utility.Util.GetRarityColor(Rarity.Green)[
                        "text"] if not server_language in mod.names else utility.Util.GetRarityColor(Rarity.White)["text"]
                    # PyImGui.push_style_color(
                    #     PyImGui.ImGuiCol.Text,
                    #     Utils.ColorToTuple(color),
                    # )
                    PyImGui.text_wrapped(mod.applied_name)
                    # PyImGui.pop_style_color(1)
                    draw_weapon_mod_tooltip(mod)
                    # ImGui.show_tooltip(
                    #     f"Mod: {mod.name}\nIdentifier: {mod.identifier}"
                    # )

                    # Mod name
                    PyImGui.table_next_column()
                    PyImGui.text_wrapped(mod.description)
                    draw_weapon_mod_tooltip(mod)
                    # ImGui.show_tooltip(
                    #     f"Mod: {mod.description}\nIdentifier: {mod.identifier}"
                    # )
                    if keep:
                        PyImGui.pop_style_color(1)

                    PyImGui.table_next_column()
                    inscription = "Inscription"

                    if mod.is_inscription:
                        unique_id = f"##{mod.identifier}{inscription}"
                        PyImGui.push_style_var2(
                            ImGui.ImGuiStyleVar.FramePadding, 0, 8)

                        is_selected = (
                            mod.identifier in settings.current.loot_profile.weapon_mods
                            and inscription
                            in settings.current.loot_profile.weapon_mods[mod.identifier]
                            and settings.current.loot_profile.weapon_mods[mod.identifier][inscription]
                        )
                        mod_selected = PyImGui.checkbox(unique_id, is_selected)

                        PyImGui.pop_style_var(1)
                        ImGui.show_tooltip(
                            f"{'Keep' if is_selected else 'Ignore'} {mod.name}"
                        )

                        if is_selected != mod_selected:
                            if mod_selected:
                                if mod.identifier not in settings.current.loot_profile.weapon_mods:
                                    settings.current.loot_profile.weapon_mods[mod.identifier] = {
                                    }
                                settings.current.loot_profile.weapon_mods[mod.identifier][
                                    inscription
                                ] = True
                            else:
                                settings.current.loot_profile.weapon_mods[mod.identifier].pop(
                                    inscription, None
                                )
                                if not settings.current.loot_profile.weapon_mods[mod.identifier]:
                                    settings.current.loot_profile.weapon_mods.pop(
                                        mod.identifier, None)

                            settings.current.loot_profile.save()

                    # Weapon type checkboxes
                    for weapon_type in weapon_types:
                        PyImGui.table_next_column()

                        if not mod.is_inscription:
                            hasWeaponType = mod.has_item_type(weapon_type)

                            if hasWeaponType:
                                unique_id = f"##{mod.identifier}{weapon_type}"
                                PyImGui.push_style_var2(
                                    ImGui.ImGuiStyleVar.FramePadding, 0, 8)

                                is_selected = (
                                    mod.identifier in settings.current.loot_profile.weapon_mods
                                    and weapon_type.name
                                    in settings.current.loot_profile.weapon_mods[mod.identifier]
                                    and settings.current.loot_profile.weapon_mods[mod.identifier][weapon_type.name]
                                )
                                mod_selected = PyImGui.checkbox(
                                    unique_id, is_selected)

                                PyImGui.pop_style_var(1)
                                ImGui.show_tooltip(
                                    f"{'Keep' if is_selected else 'Ignore'} {mod.name} for {weapon_type.name}"
                                )

                                if is_selected != mod_selected:
                                    if mod_selected:
                                        if mod.identifier not in settings.current.loot_profile.weapon_mods:
                                            settings.current.loot_profile.weapon_mods[mod.identifier] = {
                                            }
                                        settings.current.loot_profile.weapon_mods[mod.identifier][
                                            weapon_type.name
                                        ] = True
                                    else:
                                        settings.current.loot_profile.weapon_mods[mod.identifier].pop(
                                            weapon_type.name, None
                                        )
                                        if not settings.current.loot_profile.weapon_mods[mod.identifier]:
                                            settings.current.loot_profile.weapon_mods.pop(
                                                mod.identifier, None)

                                    settings.current.loot_profile.save()

                    scroll_bar_visible = scroll_bar_visible or PyImGui.get_scroll_max_y() > 0

            PyImGui.pop_style_var(2)
            PyImGui.end_table()
            PyImGui.end_child()

        PyImGui.end_tab_item()


def draw_runes():
    global show_price_check_popup, trader_type

    tab_name = "Runes"
    if PyImGui.begin_tab_item(tab_name) and settings.current.loot_profile:
        if PyImGui.begin_child(f"{tab_name}#1", (0, 0), True, PyImGui.WindowFlags.NoFlag):
            PyImGui.text("Rune Selection")

            remaining_space = PyImGui.get_content_region_avail()
            PyImGui.same_line(remaining_space[0] - 255, 5)
            if PyImGui.button("Get Expensive Runes from Merchant", 250, 0):
                if settings.current.loot_profile:
                    show_price_check_popup = not show_price_check_popup
                    if show_price_check_popup:
                        trader_type = "RUNES"
                        PyImGui.open_popup("Get Expensive Runes from Merchant")
                    else:
                        PyImGui.close_current_popup()

            PyImGui.separator()

            if PyImGui.begin_tab_bar("RunesTabBar"):
                for profession, runes in data.Runes_by_Profession.items():

                    if not runes:
                        continue

                    profession_name = "Common" if profession == Profession._None else profession.name

                    if not PyImGui.begin_tab_item(profession_name):
                        continue

                    if PyImGui.begin_child("RunesSelection#1", (0, 0), True, PyImGui.WindowFlags.NoBackground):
                        for rune in runes.values():
                            if not rune or not rune.identifier:
                                continue

                            if not PyImGui.is_rect_visible(0, 20):
                                PyImGui.dummy(0, 20)
                                continue

                            color = utility.Util.GetRarityColor(
                                rune.rarity.value)
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color["text"]))
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color["content"]))
                            PyImGui.push_style_color(
                                PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(color["frame"]))

                            label = f"{rune.full_name}"
                            unique_id = f"##{rune.identifier}"
                            rune_selected = PyImGui.checkbox(
                                IconsFontAwesome5.ICON_SHIELD_ALT + " " + label + unique_id,
                                rune.identifier in settings.current.loot_profile.runes and settings.current.loot_profile.runes[
                                    rune.identifier]
                            )

                            is_selected = rune.identifier in settings.current.loot_profile.runes and settings.current.loot_profile.runes[
                                rune.identifier]

                            if is_selected != rune_selected:
                                if rune_selected:
                                    settings.current.loot_profile.runes[rune.identifier] = True

                                elif rune.identifier in settings.current.loot_profile.runes:
                                    del settings.current.loot_profile.runes[rune.identifier]

                                settings.current.loot_profile.save()

                            PyImGui.pop_style_color(3)                            
                            draw_rune_tooltip(rune)
                            
                            PyImGui.same_line(0, 5)
                            PyImGui.text_colored(utility.Util.format_currency(rune.vendor_value), Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 125)))

                        PyImGui.end_child()

                    PyImGui.end_tab_item()

                PyImGui.end_tab_bar()

        PyImGui.end_child()

        draw_price_check_popup()
        PyImGui.end_tab_item()


def draw_price_check_popup():
    global show_price_check_popup, entered_price_threshold

    if settings.current.loot_profile is None:
        return

    if show_price_check_popup:
        PyImGui.open_popup("Get Expensive Runes from Merchant")

    if PyImGui.begin_popup("Get Expensive Runes from Merchant"):
        PyImGui.text("Please enter a price threshold:")
        PyImGui.separator()

        price_input = PyImGui.input_int(
            "##PriceThreshold", entered_price_threshold)
        if price_input is not None and price_input != entered_price_threshold:
            entered_price_threshold = price_input

        PyImGui.same_line(0, 5)

        if PyImGui.button("Check Prices", 100, 0):
            if trader_type == "RUNES":
                if entered_price_threshold is not None and entered_price_threshold > 0:
                    ConsoleLog(
                        "LootEx",
                        f"Checking for expensive runes from merchant with price threshold: {entered_price_threshold}",
                        Console.MessageType.Info,
                    )
                    loot_check.LootCheck.get_expensive_runes_from_merchant(
                        entered_price_threshold)
                else:
                    ConsoleLog(
                        "LootEx",
                        "Price threshold must be greater than 0!",
                        Console.MessageType.Error,
                    )

            show_price_check_popup = False
            PyImGui.close_current_popup()

        PyImGui.end_popup()

    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_price_check_popup:
            PyImGui.close_current_popup()
            show_price_check_popup = False


def draw_item_type_selectable(item_type, is_selected) -> tuple[bool, bool]:
    """
    Draws a selectable checkbox for an item type in the GUI.

    Args:
        item_type: The item type to display.
        is_selected: Whether the item type is currently selected.

    Returns:
        A tuple containing:
        - A boolean indicating if the selection state has changed.
        - A boolean indicating the new selection state.
    """
    if settings.current.loot_profile is None:
        return False, False

    text_color = Utils.RGBToColor(
        255, 255, 255, 255) if is_selected else Utils.RGBToColor(255, 255, 255, 125)
    PyImGui.push_style_color(PyImGui.ImGuiCol.Text,
                             Utils.ColorToTuple(text_color))

    is_now_selected = PyImGui.checkbox(
        f"{IconsFontAwesome5.ICON_BUG} {item_type.name}", is_selected
    )
    PyImGui.pop_style_color(1)

    return is_selected != is_now_selected, is_now_selected


def draw_vertical_centered_text(text: str, same_line_spacing: Optional[float] = None, desired_height: int = 24) -> float:
    """
    Draws text vertically centered within a specified height.

    Args:
        text (str): The text to display.
        same_line_spacing (Optional[float]): Spacing to apply if the text is on the same line.
        desired_height (int): The height within which the text should be centered.

    Returns:
        float: The width of the rendered text.
    """
    # text_size = PyImGui.calc_text_size(text)
    # text_offset = (desired_height - text_size[1]) / 2

    # cursor_y = PyImGui.get_cursor_pos_y()

    # if text_offset > 0:
    #     PyImGui.set_cursor_pos_y(cursor_y + text_offset)

    # PyImGui.text(text)

    # if same_line_spacing:
    #     if text_offset > 0:
    #         PyImGui.set_cursor_pos_y(cursor_y)

    #     PyImGui.set_cursor_pos_x(
    #         PyImGui.get_cursor_pos_x() + text_size[0] + same_line_spacing)

    # return text_size[0]

    textSize = PyImGui.calc_text_size(text)
    textOffset = (desired_height - textSize[1]) / 2

    cursorY = PyImGui.get_cursor_pos_y()
    cusorX = PyImGui.get_cursor_pos_x()

    if textOffset > 0:
        PyImGui.set_cursor_pos_y(cursorY + textOffset)

    PyImGui.text(text)

    if same_line_spacing:
        if textOffset > 0:
            PyImGui.set_cursor_pos_y(cursorY)

        # PyImGui.set_cursor_pos_x(cusorX + textSize[0] + sameline_spacing)
        PyImGui.set_cursor_pos_x(same_line_spacing)

    return textSize[0]


def draw_weapon_mod_tooltip(mod: models.WeaponMod):
    if PyImGui.is_item_hovered():
        PyImGui.begin_tooltip()

        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text,
            Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255)),
        )
        PyImGui.text(f"{mod.name}")
        PyImGui.text(f"{mod.description}")

        PyImGui.separator()

        # PyImGui.begin_child(
        #     f"WeaponModTooltip{mod.identifier}",
        #     (400, 0),
        #     True,
        #     PyImGui.WindowFlags.NoBackground,
        # )
        if PyImGui.begin_table(mod.identifier, 2, PyImGui.TableFlags.Borders):
            PyImGui.table_setup_column(
                "Property", PyImGui.TableColumnFlags.WidthFixed, 150)
            PyImGui.table_setup_column(
                "Value", PyImGui.TableColumnFlags.WidthStretch)
            PyImGui.table_headers_row()

            PyImGui.table_next_row()

            PyImGui.table_next_column()
            PyImGui.text(f"Id (internal)")

            PyImGui.table_next_column()
            PyImGui.text(f"{mod.identifier}")

            PyImGui.table_next_column()
            PyImGui.text(f"Mod Type")

            PyImGui.table_next_column()
            PyImGui.text(f"{mod.mod_type.name}")

            PyImGui.table_next_column()
            PyImGui.text(f"Applied to Item Types")

            PyImGui.table_next_column()
            for item_type in mod.target_types:
                PyImGui.text(f"{item_type.name}")

        PyImGui.end_table()

        PyImGui.pop_style_color(1)
        # PyImGui.end_child()
        PyImGui.end_tooltip()


def draw_rune_tooltip(mod: models.Rune):
    if PyImGui.is_item_hovered():
        PyImGui.begin_tooltip()

        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Text,
            Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255)),
        )
        PyImGui.text(f"{mod.name}")
        PyImGui.text(f"{mod.description}")

        PyImGui.separator()

        # PyImGui.begin_child(
        #     f"WeaponModTooltip{mod.identifier}",
        #     (400, 0),
        #     True,
        #     PyImGui.WindowFlags.NoBackground,
        # )
        if PyImGui.begin_table(mod.identifier, 2, PyImGui.TableFlags.Borders):
            PyImGui.table_setup_column(
                "Property", PyImGui.TableColumnFlags.WidthFixed, 150)
            PyImGui.table_setup_column(
                "Value", PyImGui.TableColumnFlags.WidthStretch)
            PyImGui.table_headers_row()

            PyImGui.table_next_row()

            PyImGui.table_next_column()
            PyImGui.text(f"Id (internal)")

            PyImGui.table_next_column()
            PyImGui.text(f"{mod.identifier}")

            PyImGui.table_next_column()
            PyImGui.text(f"Mod Type")

            PyImGui.table_next_column()
            PyImGui.text(f"{mod.mod_type.name}")

            PyImGui.table_next_column()
            PyImGui.text(f"Applied")

            PyImGui.table_next_column()            
            PyImGui.text(f"{mod.applied_name}")
            
            PyImGui.table_next_column()
            PyImGui.text(f"Vendor Value")
            
            PyImGui.table_next_column()
            PyImGui.text(utility.Util.format_currency(mod.vendor_value))
                        
            PyImGui.table_next_column()
            PyImGui.text(f"Last Checked")
            PyImGui.table_next_column()
            time_ago = f"{utility.Util.format_time_ago(datetime.now() - mod.vendor_updated)}\n" if mod.vendor_updated else ""
            PyImGui.text(f"{time_ago}")
            
        PyImGui.end_table()

        PyImGui.pop_style_color(1)
        # PyImGui.end_child()
        PyImGui.end_tooltip()


def draw_selectable_item(item: SelectableItem):
    """
    Draws a selectable item in the GUI.

    Args:
        item (SelectableItem): The item to be displayed.
    """
    global selected_loot_items, filtered_loot_items

    if settings.current.loot_profile is None:
        return

    # Apply background color for selected or hovered items
    if item.is_selected:
        selected_color = Utils.RGBToColor(34, 34, 34, 255)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(selected_color))

    if item.is_hovered:
        hovered_color = Utils.RGBToColor(63, 63, 63, 255)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(hovered_color))

    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
    PyImGui.begin_child(
        f"SelectableItem{item.item_info.model_id}",
        (0, 20),
        False,
        PyImGui.WindowFlags.NoFlag,
    )

    # Construct item name with attributes if available
    attributes = (
        [utility.Util.GetAttributeName(
            attr) + ", " for attr in item.item_info.attributes]
        if item.item_info.attributes
        else []
    )
    
    profession = utility.Util.GetProfessionName(item.item_info.profession) if item.item_info.profession else ""

    item_name = item.item_info.name
    
        
    if item.item_info.attributes and len(item.item_info.attributes) > 0:
        item_name = (
            f"{item_name} ({''.join(attributes).removesuffix(',')})"
            if len(item.item_info.attributes) > 1
            else f"{item_name} ({utility.Util.GetAttributeName(item.item_info.attributes[0])})"
        )
    elif item.item_info.attributes and len(item.item_info.attributes) == 1:
        item_name = f"{item_name} ({utility.Util.GetAttributeName(item.item_info.attributes[0])})"

    elif profession:
        item_name = f"{item_name} ({profession})"
        
    # Determine text color based on whether the item has settings
    has_settings = item.item_info.model_id in settings.current.loot_profile.items
    text_color = (
        utility.Util.GetRarityColor(Rarity.Gold)["text"]
        if has_settings
        else Utils.RGBToColor(255, 255, 255, 255)
    )
    PyImGui.push_style_color(PyImGui.ImGuiCol.Text,
                             Utils.ColorToTuple(text_color))

    # Draw item name with vertical centering
    PyImGui.set_cursor_pos_x(PyImGui.get_cursor_pos_x() + 5)
    draw_vertical_centered_text(item_name, None, 20)
    PyImGui.pop_style_color(1)

    PyImGui.end_child()
    PyImGui.pop_style_var(1)

    # Show tooltip with item name
    ImGui.show_tooltip(item_name)

    # Pop background color styles if applied
    if item.is_selected:
        PyImGui.pop_style_color(1)

    if item.is_hovered:
        PyImGui.pop_style_color(1)

    # Update hover and selection states
    item.is_hovered = PyImGui.is_item_hovered()

    if PyImGui.is_mouse_clicked(0) and item.is_hovered:
        if PyImGui.get_io().key_shift:
            start = min(filtered_loot_items.index(item),
                        filtered_loot_items.index(selected_loot_items[0]))
            end = max(filtered_loot_items.index(item),
                      filtered_loot_items.index(selected_loot_items[0]))
            selected_loot_items = filtered_loot_items[start:end + 1]

            for other_item in filtered_loot_items:
                other_item.is_selected = False

            for selected_item in selected_loot_items:
                selected_item.is_selected = True
        else:
            selected_loot_items = [item]

            for other_item in filtered_loot_items:
                other_item.is_selected = False

            item.is_selected = True

def is_mouse_in_rect(rect: tuple[float, float, float, float]) -> bool:
    """
    Checks if the mouse is within a specified rectangle.

    Args:
        rect (tuple[float, float, float, float]): The rectangle defined by (x, y, width, height).

    Returns:
        bool: True if the mouse is within the rectangle, False otherwise.
    """
    pyimgui_io = PyImGui.get_io()
    mouse_pos = (pyimgui_io.mouse_pos_x, pyimgui_io.mouse_pos_y)
    
    return (rect[0] <= mouse_pos[0] <= rect[0] + rect[2] and
            rect[1] <= mouse_pos[1] <= rect[1] + rect[3])

# region general ui elements


@staticmethod
def toggle_button(label: str, v: bool, width=0, height=0,
                  default_color: tuple[float, float, float, float] = (
                      0.153, 0.318, 0.929, 1.0),
                  hover_color: tuple[float, float, float,
                                     float] = (0.6, 0.6, 0.9, 1.0),
                  active_color: tuple[float, float,
                                      float, float] = (0.6, 0.6, 0.6, 1.0)
                  ) -> bool:
    """
    Purpose: Create a toggle button that changes its state and color based on the current state.
    Args:
        label (str): The label of the button.
        v (bool): The current toggle state (True for on, False for off).
    Returns: bool: The new state of the button after being clicked.
    """
    clicked = False

    if v:
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.Button, default_color)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.ButtonHovered, hover_color)
        PyImGui.push_style_color(
            PyImGui.ImGuiCol.ButtonActive, active_color)
        if width != 0 and height != 0:
            clicked = PyImGui.button(label, width, height)
        else:
            clicked = PyImGui.button(label)
        PyImGui.pop_style_color(3)
    else:
        if width != 0 and height != 0:
            clicked = PyImGui.button(label, width, height)
        else:
            clicked = PyImGui.button(label)

    if clicked:
        v = not v

    return v

# endregion
