from LootEx import *
from LootEx import Settings
from LootEx import ItemAction
from LootEx import Data
from LootEx import LootCheck
from LootEx import LootItem
from LootEx import Utility
from LootEx.LootFilter import LootFilter
from LootEx.LootProfile import LootProfile
from Py4GWCoreLib import *


import importlib
importlib.reload(Settings)
importlib.reload(Data)
importlib.reload(LootCheck)
importlib.reload(LootItem)
importlib.reload(Utility)

class ItemSelectable:
    def __init__(self, item: Data.Item, selected: bool = False):
        self.ItemInfo = item
        self.IsSelected = selected
        self.Hovered = False

    def __str__(self):
        return f"ItemSelectable(item={self.ItemInfo}, selected={self.IsSelected})"

    def __repr__(self):
        return self.__str__()
    
selected_lootItems : list[ItemSelectable] = []
lootItems_selection_dragging : bool = False
filtered_loot_items : list[ItemSelectable] = [ItemSelectable(item) for item in Data.Items.values()]
selected_Condition : Optional[LootItem.LootItemConditionedActions] = None
condition_Name = ""
item_search = ""
new_name = ""
mod_search = ""
filtered_weapon_mods : dict[str, Data.WeaponMod] = Data.WeaponMods
scroll_bar_visible = False
trader_type = ""
entered_price_threshold = 1000
show_price_check_popup = False
show_add_filter_popup = False
show_add_profile_popup = False
show_delete_profile_popup = False
firstDraw : bool = True
inventory_frame_hash = 291586130
on_screen = True
fullscreen_frame_id = UIManager.GetFrameIDByHash(140452905)
flags = PyImGui.WindowFlags.NoFlag

def DrawInventoryControls():
    coords = Settings.Current.inventory_frame_coords 
    width = 30
    PyImGui.set_next_window_pos(coords.left-(width - 5), coords.top)
    PyImGui.set_next_window_size(width, 0)
    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)

    if PyImGui.begin("Loot Ex Inventory Controls", PyImGui.WindowFlags.NoTitleBar | PyImGui.WindowFlags.NoResize | PyImGui.WindowFlags.NoBackground | PyImGui.WindowFlags.AlwaysAutoResize | PyImGui.WindowFlags.NoCollapse | PyImGui.WindowFlags.NoMove | PyImGui.WindowFlags.NoSavedSettings):
        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(1)

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(0, 255, 0, 255) if Settings.Current.AutomaticInventoryHandling else Utils.RGBToColor(255, 255, 255, 125)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))

        if PyImGui.button(IconsFontAwesome5.ICON_CHECK, width, width):
            Settings.Current.AutomaticInventoryHandling = not Settings.Current.AutomaticInventoryHandling
            ActionQueueManager().ResetQueue("SALVAGE")
            ActionQueueManager().ResetQueue("IDENTIFY")

        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(4)
        
        ImGui.show_tooltip(("Disable" if Settings.Current.AutomaticInventoryHandling else "Enable") + " Inventory Handling")
            
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255) if Settings.Current.ManualWindowVisible else Utils.RGBToColor(255, 255, 255, 125)))        
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))
        if PyImGui.button(IconsFontAwesome5.ICON_COG, width, width):
            Settings.Current.ManualWindowVisible = not Settings.Current.ManualWindowVisible
            Settings.Current.Save()
        
        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(4)
        ImGui.show_tooltip(("Hide" if Settings.Current.ManualWindowVisible else "Show") + " Window")
            
        xunlai_open = Inventory.IsStorageOpen()
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 255) if xunlai_open else Utils.RGBToColor(255, 255, 255, 125)))        
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 125)))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(Utils.RGBToColor(0, 0, 0, 0)))
        if PyImGui.button(IconsFontAwesome5.ICON_BOX_OPEN if xunlai_open else IconsFontAwesome5.ICON_BOX, width, width):
            if xunlai_open:
                # Inventory.CloseStorage()
                pass
            else:
                Inventory.OpenXunlaiWindow()
        
        PyImGui.pop_style_var(1)
        PyImGui.pop_style_color(4)

        ImGui.show_tooltip("Open Xunlai Storage")

        
        PyImGui.end()


    if Settings.Current.ManualWindowVisible:
        Settings.Current.WindowVisible = Settings.Current.ManualWindowVisible

def DrawWindow():    
    global firstDraw, show_add_profile_popup, show_delete_profile_popup, on_screen, flags

    if firstDraw is True:        
        PyImGui.set_next_window_size(Settings.Current.WindowSize[0], Settings.Current.WindowSize[1])
        PyImGui.set_next_window_pos(Settings.Current.WindowPosition[0], Settings.Current.WindowPosition[1])
        PyImGui.set_next_window_collapsed(Settings.Current.WindowCollapsed, 0)
        firstDraw = False

        
    _, _, width, height = UIManager.GetFrameCoords(fullscreen_frame_id)
    # size = PyImGui.get_io().display_size
    # width = size[0]
    # height = size[1]
    
    if(Settings.Current.WindowPosition[0] > width or Settings.Current.WindowPosition[1] > height):
        Settings.Current.WindowPosition = (width / 2, height / 2)
        Settings.Current.WindowSize = (width / 2, height / 2)
        Settings.Current.Save()

        PyImGui.set_next_window_pos(Settings.Current.WindowPosition[0], Settings.Current.WindowPosition[1])
        PyImGui.set_next_window_size(Settings.Current.WindowSize[0], Settings.Current.WindowSize[1])
        PyImGui.set_next_window_collapsed(Settings.Current.WindowCollapsed, 0)
    
    #if dragging and mouse over, set flag to no move
    if PyImGui.begin_with_close("Loot Ex", Settings.Current.WindowVisible, flags) and Settings.Current.LootProfile:        
        flags = PyImGui.WindowFlags.NoTitleBar | PyImGui.WindowFlags.NoMove| PyImGui.WindowFlags.NoResize if PyImGui.is_mouse_down(0) else PyImGui.WindowFlags.NoFlag

        profile_names = [profile.Name for profile in Settings.Current.LootProfiles]
        combo_index = PyImGui.combo("", Settings.Current.ProfileCombo, profile_names)

        if(Settings.Current.ProfileCombo != combo_index): 
            ConsoleLog("LootEx", "Profile changed to " + profile_names[combo_index], Console.MessageType.Info)   
            Settings.Current.ProfileCombo = combo_index       
            Settings.Current.LootProfile = Settings.Current.LootProfiles[Settings.Current.ProfileCombo]
            Settings.Current.Save()

        PyImGui.same_line(0, 5)
        
        if PyImGui.button((IconsFontAwesome5.ICON_PLUS)):
            show_add_profile_popup = not show_add_profile_popup
            if show_add_profile_popup:
                PyImGui.open_popup("Add Profile")
            else:
                PyImGui.close_current_popup()

        ImGui.show_tooltip("Add New Profile")
        PyImGui.same_line(0, 5)

        if PyImGui.button((IconsFontAwesome5.ICON_TRASH)) and len(Settings.Current.LootProfiles) > 1:
            show_delete_profile_popup = not show_delete_profile_popup
            if show_delete_profile_popup:
                PyImGui.open_popup("Delete Profile")
            else:
                PyImGui.close_current_popup()
        
        ImGui.show_tooltip("Delete Profile '" + Settings.Current.LootProfile.Name + "'")
        PyImGui.same_line(0, 5)

        btnColor = Utils.RGBToColor(0, 255, 0, 255) if Settings.Current.AutomaticInventoryHandling else Utils.RGBToColor(255, 0, 0, 125)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(btnColor))

        if PyImGui.button((IconsFontAwesome5.ICON_PLAY_CIRCLE if Settings.Current.AutomaticInventoryHandling else IconsFontAwesome5.ICON_PAUSE_CIRCLE)):
            Settings.Current.AutomaticInventoryHandling = not Settings.Current.AutomaticInventoryHandling
            ActionQueueManager().ResetQueue("SALVAGE")
            ActionQueueManager().ResetQueue("IDENTIFY")

        PyImGui.pop_style_color(1)
        ImGui.show_tooltip(("Disable" if Settings.Current.AutomaticInventoryHandling else "Enable") + " Inventory Handling")
        


        if PyImGui.begin_tab_bar("LootExTabBar"):
            DrawGeneralSettings()
            DrawLootFilters()
            DrawLootItems()
            DrawMods()
            DrawRunes()

        PyImGui.end_tab_bar()

        pos = PyImGui.get_window_pos()
        size = PyImGui.get_window_size()
        
        if Settings.Current.WindowPosition != (pos[0], pos[1]):
            Settings.Current.WindowPosition = (pos[0], pos[1])
            Settings.Current.Save()

        if Settings.Current.WindowSize != (size[0], size[1]):
            Settings.Current.WindowSize = (size[0], size[1])
            Settings.Current.Save()
        
        DrawDeleteProfilePopup()
        DrawProfilesPopup()
        
        PyImGui.end()

    collapsed = PyImGui.is_window_collapsed()

    if  collapsed != Settings.Current.WindowCollapsed:
        Settings.Current.WindowCollapsed = collapsed
        Settings.Current.Save()

def DrawDeleteProfilePopup():
    global show_delete_profile_popup

    if Settings.Current.LootProfile == None:
        return

    if show_delete_profile_popup:
        PyImGui.open_popup("Delete Profile")

    if PyImGui.begin_popup("Delete Profile"):
        PyImGui.text("Are you sure you want to delete " + str(Settings.Current.LootProfile.Name) + " this profile?")
        PyImGui.separator()

        if PyImGui.button("Yes", 100, 0):
            Settings.Current.LootProfiles.pop(Settings.Current.ProfileCombo)
            Settings.Current.ProfileCombo = min(Settings.Current.ProfileCombo, len(Settings.Current.LootProfiles) - 1)
            Settings.Current.LootProfile = Settings.Current.LootProfiles[Settings.Current.ProfileCombo]
            Settings.Current.Save()
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

def DrawProfilesPopup():
    global show_add_profile_popup, new_name

    if show_add_profile_popup:
        PyImGui.open_popup("Add Profile")

    # PyImGui.set_next_window_size(300, 0)
    if PyImGui.begin_popup("Add Profile"):
        PyImGui.text("Please enter a name for the new profile:")
        PyImGui.separator()            

        exists = new_name == "" or any(profile.Name.lower() == new_name.lower() for profile in Settings.Current.LootProfiles)
            
        if exists:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)))

        profile_name = PyImGui.input_text("##NewProfileName", new_name)
        if profile_name != None and profile_name != new_name:
            new_name = profile_name    

        if exists:
            PyImGui.pop_style_color(1)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 120)))
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)))
            
        PyImGui.same_line(0, 5)  

        if PyImGui.button("Create", 100, 0) and not exists:
            if new_name != "" and not exists:
                if Settings.Current.LootProfile:
                    Settings.Current.LootProfile.Save()

                new_profile = LootProfile(new_name)
                Settings.Current.LootProfiles.append(new_profile)
                Settings.Current.ProfileCombo = len(Settings.Current.LootProfiles) - 1
                Settings.Current.LootProfile = new_profile
                Settings.Current.Save()
                Settings.Current.LootProfile.Save()

                new_name = ""
                show_add_profile_popup = False
                PyImGui.close_current_popup()
            else:
                ConsoleLog("LootEx", "Profile name already exists!", Console.MessageType.Error)

        if exists:
            PyImGui.pop_style_color(4)   

            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)))
            PyImGui.text("Profile name already exists!")
            PyImGui.pop_style_color(1)        


        PyImGui.end_popup()

    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_add_profile_popup:
            PyImGui.close_current_popup()
            show_add_profile_popup = False

def DrawGeneralSettings():
    if(PyImGui.begin_tab_item("General")):
        #Get Size of the tab
        tab_size = PyImGui.get_content_region_avail()
        dye_width = 250

        if (PyImGui.begin_child("GeneralSettingsChild", (tab_size[0] - dye_width - 5, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)):
            PyImGui.text("Merchant Settings")
            PyImGui.separator()
            
            subtab_size = PyImGui.get_content_region_avail()
            
            if(PyImGui.begin_child("generalsettingschild##2", (subtab_size[0], subtab_size[1] - 30), True, PyImGui.WindowFlags.NoBackground)) and Settings.Current.LootProfile:
                amount = PyImGui.input_int("Identification Kits", Settings.Current.LootProfile.IdentificationKits)
                if amount != Settings.Current.LootProfile.IdentificationKits:
                    Settings.Current.LootProfile.IdentificationKits = amount
                    Settings.Current.LootProfile.Save()
                ImGui.show_tooltip("Number of Identification Kits to stock up to when visiting a merchant.")

                amount = PyImGui.input_int("Salvage Kits", Settings.Current.LootProfile.SalvageKits)
                if amount != Settings.Current.LootProfile.SalvageKits:
                    Settings.Current.LootProfile.SalvageKits = amount
                    Settings.Current.LootProfile.Save()
                ImGui.show_tooltip("Number of Salvage Kits to stock up to when visiting a merchant.")

                amount = PyImGui.input_int("Expert Salvage Kits", Settings.Current.LootProfile.ExpertSalvageKits)
                if amount != Settings.Current.LootProfile.ExpertSalvageKits:
                    Settings.Current.LootProfile.ExpertSalvageKits = amount
                    Settings.Current.LootProfile.Save()
                ImGui.show_tooltip("Number of Expert Salvage Kits to stock up to when visiting a merchant.")

                amount = PyImGui.input_int("Lockpicks", Settings.Current.LootProfile.Lockpicks)
                if amount != Settings.Current.LootProfile.Lockpicks:
                    Settings.Current.LootProfile.Lockpicks = amount
                    Settings.Current.LootProfile.Save()                
                ImGui.show_tooltip("Number of Lockpicks to stock up to when visiting a merchant.")

                amount = PyImGui.input_int("Sell Threshold", Settings.Current.LootProfile.SellThreshold)
                if amount != Settings.Current.LootProfile.SellThreshold:
                    Settings.Current.LootProfile.SellThreshold = amount
                    Settings.Current.LootProfile.Save()
                
                ImGui.show_tooltip("Items with a value equal or above " + str(Settings.Current.LootProfile.SellThreshold) +" gold will be sold to a merchant instead of being salvaged.")
                pass

            PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.same_line(0, 5)

        if (PyImGui.begin_child("Dyes", (dye_width, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)) and Settings.Current.LootProfile:
            PyImGui.text("Dyes")
            PyImGui.text_wrapped("Select the dyes you want to pick up and keep.")
            PyImGui.separator()

            if PyImGui.begin_child("DyesSelection", (dye_width - 20, 0), True, PyImGui.WindowFlags.NoFlag | PyImGui.WindowFlags.NoBackground):
                for dye in DyeColor:
                    if dye != DyeColor.NoColor:
                        if dye not in Settings.Current.LootProfile.Dyes:
                            Settings.Current.LootProfile.Dyes[dye] = False
                        
                        color = Utility.Util.GetDyeColor(dye, 205 if Settings.Current.LootProfile.Dyes[dye] else 125)
                        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color))
                        hoverColor = Utility.Util.GetDyeColor(dye)
                        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(hoverColor))
                        selected = PyImGui.checkbox(IconsFontAwesome5.ICON_FLASK + " " + dye.name, Settings.Current.LootProfile.Dyes[dye])

                        if Settings.Current.LootProfile.Dyes[dye] != selected:
                            Settings.Current.LootProfile.Dyes[dye] = selected
                            Settings.Current.LootProfile.Save()

                        PyImGui.pop_style_color(2)
                        ImGui.show_tooltip("Dye: " + dye.name)
                pass

            PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.end_tab_item()

def DrawLootFilters():
    global show_add_filter_popup

    if(PyImGui.begin_tab_item("Filter based Actions")) and Settings.Current.LootProfile:
        #Get Size of the tab
        tab_size = PyImGui.get_content_region_avail()

        if (PyImGui.begin_child("LootFilterSelectionChild", (tab_size[0] * 0.3, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)):
            
            PyImGui.text("Loot Filter Selection")
            PyImGui.separator()
            subtab_size = PyImGui.get_content_region_avail()
            
            if(PyImGui.begin_child("filterselectionchild##1", (subtab_size[0], subtab_size[1] - 30), True, PyImGui.WindowFlags.NoBackground)):
                if Settings.Current.LootProfile and Settings.Current.LootProfile.Filters:
                    for filter in Settings.Current.LootProfile.Filters:
                        if PyImGui.selectable(filter.Name, filter == Settings.Current.SelectedLootFilter, PyImGui.SelectableFlags.NoFlag, (0, 0)):
                            Settings.Current.SelectedLootFilter = filter

            PyImGui.end_child()
            
            if(PyImGui.button("Add Filter", subtab_size[0])):
                show_add_filter_popup = not show_add_filter_popup
                if show_add_filter_popup:
                    PyImGui.open_popup("Add Filter")                

        PyImGui.end_child()

        PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

        if (PyImGui.begin_child("LootFilterChild", (tab_size[0] - (tab_size[0] * 0.3) - 10, tab_size[1]), True, PyImGui.WindowFlags.NoFlag)):
            if(Settings.Current.SelectedLootFilter != None):
                name = PyImGui.input_text("##NameEdit", Settings.Current.SelectedLootFilter.Name)

                if name != None and name != Settings.Current.SelectedLootFilter.Name:
                    Settings.Current.SelectedLootFilter.Name = name
                    Settings.Current.LootProfile.Save()

                PyImGui.same_line(0, 5)

                if PyImGui.button(IconsFontAwesome5.ICON_TRASH):
                    Settings.Current.LootProfile.Filters.remove(Settings.Current.SelectedLootFilter)
                    Settings.Current.LootProfile.Save()
                    Settings.Current.SelectedLootFilter = Settings.Current.LootProfile.Filters[0] if Settings.Current.LootProfile.Filters else None
                    show_add_filter_popup = False
                    PyImGui.close_current_popup()

                # PyImGui.separator()                
                filter = Settings.Current.SelectedLootFilter

                if filter:
                    sub_subtab_size = PyImGui.get_content_region_avail()

                    if PyImGui.begin_child("LootFilterActions##1", (0, 100), True, PyImGui.WindowFlags.NoFlag):
                        PyImGui.text("Actions")
                        PyImGui.separator()

                        if filter.Actions.Explorable != None:
                            names = [action.name for action in ItemAction.ItemAction]
                            explorable = PyImGui.combo("Explorable", names.index(filter.Actions.Explorable.name), names)
                            
                            if explorable != filter.Actions.Explorable:
                                filter.Actions.Explorable = ItemAction.ItemAction[names[explorable]]
                                Settings.Current.LootProfile.Save()

                        if filter.Actions.Outpost != None:
                            names = [action.name for action in ItemAction.ItemAction]
                            outpost = PyImGui.combo("Outpost", names.index(filter.Actions.Outpost.name), names)

                            if outpost != filter.Actions.Outpost:
                                filter.Actions.Outpost = ItemAction.ItemAction[names[outpost]]
                                Settings.Current.LootProfile.Save()
                        pass

                    PyImGui.end_child()
                    
                    sub_subtab_size = PyImGui.get_content_region_avail()

                    if PyImGui.begin_child("LootItemtypesFilterTable", (sub_subtab_size[0] / 3 * 2, 0), True, PyImGui.WindowFlags.NoFlag):
                        PyImGui.begin_table("LootFilterTable", 3, PyImGui.TableFlags.ScrollY)
                        
                        count = 0
                        chunk_size = len(filter.ItemTypes) / 3    
                        PyImGui.table_next_column()            
                       
                        sorted_item_types = sorted(filter.ItemTypes.keys(), key=lambda x: x.name)
                    
                        for item_type in sorted_item_types:
                            count += 1

                            if count > chunk_size:
                                PyImGui.table_next_column()
                                count = 1

                            if(filter.ItemTypes[item_type] == None):
                                continue
                            
                            changed, filter.ItemTypes[item_type] = DrawItemTypeSelectable(item_type, filter.ItemTypes[item_type])
                            if changed:
                                Settings.Current.LootProfile.Save()


                        PyImGui.end_table()
                        pass

                    PyImGui.end_child()
                    PyImGui.same_line(sub_subtab_size[0] / 3 * 2 + 20, 0)
                    
                    if PyImGui.begin_child("LootRarityFilterTable", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                        for rarity in Rarity:
                            if rarity not in filter.Rarities:
                                filter.Rarities[rarity] = False
                                
                            color = Utility.Util.GetRarityColor(rarity)

                            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color["text"]))
                            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color["content"]))
                            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(color["frame"]))
                            label = f"Rarity: {rarity.name}"
                            unique_id = f"##{rarity.value}"
                            rarity_selected = PyImGui.checkbox(IconsFontAwesome5.ICON_SHIELD_ALT + " "  + label + unique_id, filter.Rarities[rarity])

                            if filter.Rarities[rarity] != rarity_selected:
                                filter.Rarities[rarity] = rarity_selected
                                Settings.Current.LootProfile.Save()

                            PyImGui.pop_style_color(3)
                        pass

                    PyImGui.end_child()
                        
        PyImGui.end_child()

        PyImGui.end_tab_item()

        DrawAddLootFilterPopup()

def DrawAddLootFilterPopup():
    global show_add_filter_popup, new_name

    if Settings.Current.LootProfile == None:
        return

    if show_add_filter_popup:
        PyImGui.open_popup("Add Filter")

    # PyImGui.set_next_window_size(300, 0)
    if PyImGui.begin_popup("Add Filter"):
        PyImGui.text("Please enter a name for the new filter:")
        PyImGui.separator()            

        exists = new_name == "" or any(filter.Name.lower() == new_name.lower() for filter in Settings.Current.LootProfile.Filters)
            
        if exists:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)))

        filter_name = PyImGui.input_text("##NewFilterName", new_name)
        if filter_name != None and filter_name != new_name:
            new_name = filter_name    

        if exists:
            PyImGui.pop_style_color(1)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 120)))
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(Utils.RGBToColor(26, 38, 51, 125)))
            
        PyImGui.same_line(0, 5)  

        if PyImGui.button("Create", 100, 0) and not exists:
            if new_name != "" and not exists:
                Settings.Current.LootProfile.Filters.append(LootFilter(new_name))
                Settings.Current.LootProfile.Save()

                new_name = ""
                show_add_filter_popup = False
                PyImGui.close_current_popup()
            else:
                ConsoleLog("LootEx", "Filter name already exists!", Console.MessageType.Error)

        if exists:
            PyImGui.pop_style_color(4)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)))
            PyImGui.text("Filter name already exists!")
            PyImGui.pop_style_color(1)
        PyImGui.end_popup()
        
    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_add_filter_popup:
            PyImGui.close_current_popup()
            show_add_filter_popup = False

def DrawLootItems():    
    global selected_lootItems, filtered_loot_items, item_search, condition_Name, selected_Condition, lootItems_selection_dragging
    if(PyImGui.begin_tab_item("Item Actions")) and Settings.Current.LootProfile:
        #Get Size of the tab
        tab_size = PyImGui.get_content_region_avail()

        if (PyImGui.begin_child("LootItemsSelectionChild", (tab_size[0] * 0.3, tab_size[1]), False, PyImGui.WindowFlags.NoFlag)):
            
            c_size = PyImGui.get_content_region_avail()
            
            PyImGui.push_item_width(c_size[0])
            search = PyImGui.input_text("##search_item", item_search)

            if(search == None or search == "") and not PyImGui.is_item_active():
                PyImGui.same_line(5, 0)
                PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 125)))
                PyImGui.text(IconsFontAwesome5.ICON_SEARCH + " Search for Item Name or Model ID...")
                PyImGui.pop_style_color(1)

            if search != None and search != item_search:
                item_search = search
                filtered_loot_items = []
                for item in Data.Items.values():
                    if item == None or item.Name == "":
                        continue

                    if item.Name.lower().find(item_search.lower()) != -1 or str(item.ModelID).find(item_search.lower()) != -1:
                        filtered_loot_items.append(ItemSelectable(item))
            
            if (PyImGui.begin_child("ItemSelectables", (0, 0), True, PyImGui.WindowFlags.NoFlag)):
                is_dragging = PyImGui.is_mouse_dragging(0, 0.5)
                if is_dragging:
                    ConsoleLog("LootEx", "Dragging Item: " + item_search, Console.MessageType.Info)

                for item in filtered_loot_items:
                    if item == None:
                        continue

                    DrawItemSelectable(item)

                    # has_Settings = item.ItemInfo.ModelID.name in Settings.Current.LootProfile.Items
                    
                    # color = Utility.Util.GetRarityColor(Rarity.Gold)["text"] if has_Settings else Utils.RGBToColor(255, 255, 255, 255)

                    # PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color))

                    # attributes = [Utility.Util.GetAttributeName(a) + ", " for a in item.ItemInfo.Attributes] if item.ItemInfo.Attributes else []
                    # item_name = item.ItemInfo.Name if not item.ItemInfo.Attributes else item.ItemInfo.Name + " (" + "".join(attributes).removesuffix(",") + ")" if len(item.ItemInfo.Attributes) > 1 else item.ItemInfo.Name + " (" + Utility.Util.GetAttributeName(item.ItemInfo.Attributes[0]) + ")"
                    # if PyImGui.selectable(item_name, item in selected_lootItems, PyImGui.SelectableFlags.AllowDoubleClick, (0, 0)):
                    #     selected_lootItems = [item]
                    
                    # if(is_dragging) and PyImGui.is_item_hovered():
                    #     ConsoleLog("LootEx", "Dragging Item: " + item.ItemInfo.Name, Console.MessageType.Info)

                    # if(PyImGui.is_item_hovered() and is_dragging):
                    #     if item not in selected_lootItems:
                    #         selected_lootItems.append(item)
                    # elif len(selected_lootItems) > 1 and item in selected_lootItems and not is_dragging:
                    #     selected_lootItems.remove(item)                       

                    # PyImGui.pop_style_color(1)

                    # ImGui.show_tooltip(item_name)

            PyImGui.end_child()

        PyImGui.end_child()

        PyImGui.same_line(tab_size[0] * 0.3 + 20, 0)

        if (PyImGui.begin_child("LootItemChild", (tab_size[0] - (tab_size[0] * 0.3) - 10, tab_size[1]), False, PyImGui.WindowFlags.NoFlag)): 
            selected_lootItem = selected_lootItems[0] if selected_lootItems else None

            if selected_lootItem != None:                
                has_Settings = selected_lootItem.ItemInfo.ModelID and selected_lootItem.ItemInfo.ModelID.name in Settings.Current.LootProfile.Items
                details_height = 130

                if PyImGui.begin_child("ItemInfo", (0, details_height), True, PyImGui.WindowFlags.NoFlag):
                    if PyImGui.begin_child("ItemTexture", (details_height, 0), False, PyImGui.WindowFlags.NoFlag):
                        color = Utils.RGBToColor(64, 64 ,64 ,255)
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(color))
                        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(color))
                        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(color))
                        PyImGui.button(IconsFontAwesome5.ICON_SHIELD_ALT + "##" + str(selected_lootItem.ItemInfo.ModelID), details_height - 20, details_height - 20)
                        PyImGui.pop_style_color(3)
                    PyImGui.end_child()

                    PyImGui.same_line(0, 5)

                    if PyImGui.begin_child("ItemDetails", (0, 0), False, PyImGui.WindowFlags.NoFlag):                    
                        PyImGui.text("Name: " + selected_lootItem.ItemInfo.Name)

                        remaining_size = PyImGui.get_content_region_avail()
                        PyImGui.same_line(remaining_size[0] - 30, 0)

                        if(PyImGui.button(IconsFontAwesome5.ICON_GLOBE, 0, 0)): 
                            Player.SendChatCommand("wiki " + selected_lootItem.ItemInfo.Name)

                        PyImGui.text("Model ID: " + str(selected_lootItem.ItemInfo.ModelID))
                        PyImGui.text("Type: " + Utility.Util.GetItemType(selected_lootItem.ItemInfo.ItemType).name)
                        PyImGui.text_wrapped("Drop Info: " + selected_lootItem.ItemInfo.DropInfo)

                    PyImGui.end_child()

                PyImGui.end_child()

                if PyImGui.begin_child("ItemSettings", (0, 0), True, PyImGui.WindowFlags.NoFlag):
                    if has_Settings:
                        lootItem = Settings.Current.LootProfile.Items[selected_lootItem.ItemInfo.ModelID.name] if selected_lootItem.ItemInfo.ModelID and selected_lootItem.ItemInfo.ModelID.name in Settings.Current.LootProfile.Items else None
          

                        if PyImGui.begin_tab_bar("ItemConditions") and lootItem:
                            for condition in lootItem.Conditions:
                                if PyImGui.begin_tab_item(condition.Name) and condition:
                                    if selected_Condition != condition:
                                        selected_Condition = condition
                                        condition_Name = condition.Name

                                    remaining_size = PyImGui.get_content_region_avail()

                                    PyImGui.begin_child("ItemConditionDetails", (0, remaining_size[1] - 32), False, PyImGui.WindowFlags.NoFlag)
                                    condition_Name = PyImGui.input_text("##NameEdit", condition_Name)
                                    PyImGui.same_line(0, 5)
                                    if(PyImGui.button("Save")) and condition_Name != None and condition_Name != condition.Name:
                                        condition.Name = condition_Name
                                        Settings.Current.LootProfile.Save()
  

                                    PyImGui.separator()

                                    if condition.ItemActions.Explorable != None:
                                        names = [action.name for action in ItemAction.ItemAction]
                                        explorable = PyImGui.combo("Explorable", names.index(condition.ItemActions.Explorable.name), names)
                                        
                                        if explorable != condition.ItemActions.Explorable:
                                            condition.ItemActions.Explorable = ItemAction.ItemAction[names[explorable]]
                                            Settings.Current.LootProfile.Save()

                                    if condition.ItemActions.Outpost != None:
                                        names = [action.name for action in ItemAction.ItemAction]
                                        outpost = PyImGui.combo("Outpost", names.index(condition.ItemActions.Outpost.name), names)

                                        if outpost != condition.ItemActions.Outpost:
                                            condition.ItemActions.Outpost = ItemAction.ItemAction[names[outpost]]
                                            Settings.Current.LootProfile.Save()

                                    if lootItem:
                                        label_spacing = 120

                                        if(Utility.Util.IsArmor(lootItem)):
                                            PyImGui.text("IsArmor Type: " + str(True))     

                                        elif Utility.Util.IsWeapon(lootItem):
                                            PyImGui.text("")
                                            PyImGui.text("Item Stats")
                                            PyImGui.separator()
                                            mod_names = ["Any"]
                                            for mod in Data.WeaponMods.values():
                                                if mod == None or mod.Struct == "":
                                                    continue
                                                mod_names.append(mod.Name)

                                                
                                            available_attributes = selected_lootItem.ItemInfo.Attributes if selected_lootItem.ItemInfo.Attributes else Utility.Util.GetAttributes(selected_lootItem.ItemInfo.ItemType)
                                            if len(available_attributes) > 1:
                                                available_attributes.insert(0, Attribute.None_)

                                            if not condition.Requirements:
                                                condition.Requirements = {attribute: LootItem.IntRange(0, 13) for attribute in available_attributes}

                                            min_requirement = min([attribute.Min for attribute in condition.Requirements.values()])
                                            max_requirement = max([attribute.Max for attribute in condition.Requirements.values()])

                                            min_damage_in_requirements = Utility.Util.GetMaxDamage(min_requirement, selected_lootItem.ItemInfo.ItemType).Min
                                            max_damage_in_requirements = Utility.Util.GetMaxDamage(max_requirement, selected_lootItem.ItemInfo.ItemType).Max

                                            if not condition.DamageRange:
                                                condition.DamageRange = Data.IntRange(min_damage_in_requirements, max_damage_in_requirements)


                                            VerticalCenteredText("Damage Range", label_spacing)
                                            remaining_size = PyImGui.get_content_region_avail()
                                            item_width = (remaining_size[0] - 10) / 2

                                            if condition.DamageRange.Max > max_damage_in_requirements:
                                                condition.DamageRange.Max = max_damage_in_requirements
                                                Settings.Current.LootProfile.Save()
                                            
                                            PyImGui.push_item_width(item_width)
                                            value = PyImGui.slider_int("##MinDamage", condition.DamageRange.Min, 0, min_damage_in_requirements)
                                            if value > condition.DamageRange.Max:
                                                condition.DamageRange.Max = value
                                                Settings.Current.LootProfile.Save()
                                            elif value != condition.DamageRange.Min:
                                                condition.DamageRange.Min = value
                                                Settings.Current.LootProfile.Save()

                                            PyImGui.same_line(0, 5)
                                            PyImGui.push_item_width(item_width)
                                            value = PyImGui.slider_int("##MaxDamage", condition.DamageRange.Max, min_damage_in_requirements, max_damage_in_requirements)
                                            if value < condition.DamageRange.Min:
                                                condition.DamageRange.Min = value
                                                Settings.Current.LootProfile.Save()
                                                
                                            elif value != condition.DamageRange.Max:
                                                condition.DamageRange.Max = value
                                                Settings.Current.LootProfile.Save()

                                            VerticalCenteredText("Prefix|Suffix", label_spacing)
                                            prefix_name = Data.GetWeaponModName(condition.PrefixMod) if condition.PrefixMod else ""
                                            PyImGui.push_item_width(item_width)
                                            mod = PyImGui.combo("##Prefix", mod_names.index(prefix_name) if condition.PrefixMod else 0, mod_names)
                                            if (mod_names[mod] != prefix_name and mod > 0) or (condition.PrefixMod and mod == 0):
                                                modname = mod_names[mod]
                                                if modname != None and modname != "Any":
                                                    ## Get the mod struct from Data.WeaponMods
                                                    for weapon_mod in Data.WeaponMods.values():
                                                        if weapon_mod.Name == modname:
                                                            condition.PrefixMod = weapon_mod.Struct
                                                            Settings.Current.LootProfile.Save()
                                                            break
                                                elif condition.PrefixMod and mod == 0:
                                                    condition.PrefixMod = None
                                                    Settings.Current.LootProfile.Save()                                                                  

                                            PyImGui.same_line(0, 5)
                                            suffix_name = Data.GetWeaponModName(condition.SuffixMod) if condition.SuffixMod else ""
                                            PyImGui.push_item_width(item_width)
                                            mod = PyImGui.combo("##Suffix", mod_names.index(suffix_name) if condition.SuffixMod else 0, mod_names)
                                            if mod_names[mod] != suffix_name and mod > 0 or (condition.SuffixMod and mod == 0):
                                                modname = mod_names[mod]
                                                if modname != None and modname != "Any":
                                                    ## Get the mod struct from Data.WeaponMods
                                                    for weapon_mod in Data.WeaponMods.values():
                                                        if weapon_mod.Name == modname:
                                                            condition.SuffixMod = weapon_mod.Struct
                                                            Settings.Current.LootProfile.Save()
                                                            break
                                                elif condition.SuffixMod and mod == 0:
                                                    condition.SuffixMod = None
                                                    Settings.Current.LootProfile.Save()   

                                            
                                            VerticalCenteredText("Inherent", label_spacing)
                                            inherent_name = Data.GetWeaponModName(condition.InherentMod) if condition.InherentMod else ""
                                            PyImGui.push_item_width(item_width)
                                            mod = PyImGui.combo("##Inherent", mod_names.index(Data.GetWeaponModName(condition.InherentMod)) if condition.InherentMod else 0, mod_names)
                                            if mod_names[mod] != inherent_name and mod > 0 or (condition.InherentMod and mod == 0):
                                                modname = mod_names[mod]
                                                if modname != None and modname != "Any":
                                                    ## Get the mod struct from Data.WeaponMods
                                                    for weapon_mod in Data.WeaponMods.values():
                                                        if weapon_mod.Name == modname:
                                                            condition.InherentMod = weapon_mod.Struct
                                                            Settings.Current.LootProfile.Save()
                                                            break
                                                elif condition.InherentMod and mod == 0:
                                                    condition.InherentMod = None
                                                    Settings.Current.LootProfile.Save()

                                            PyImGui.same_line(0, 5)
                                            PyImGui.push_item_width(item_width)
                                            checked = PyImGui.checkbox("Old School Only", condition.OldSchoolOnly)
                                            if condition.OldSchoolOnly != checked:
                                                condition.OldSchoolOnly = checked
                                                Settings.Current.LootProfile.Save()

                                            PyImGui.text("")
                                            PyImGui.text("Attribute Ranges")
                                            PyImGui.separator()

                                            for attribute, requirement in condition.Requirements.items():
                                                if requirement == None:
                                                    continue

                                                VerticalCenteredText(attribute.name if attribute != Attribute.None_ else "Any", label_spacing)

                                                remaining_size = PyImGui.get_content_region_avail()
                                                item_width = (remaining_size[0] - 10) / 2
                                                
                                                PyImGui.push_item_width(item_width)
                                                value = PyImGui.slider_int("##MinRequirement", requirement.Min, 0, 13)
                                                if value > requirement.Max:
                                                    requirement.Max = value
                                                    Settings.Current.LootProfile.Save()

                                                elif value != requirement.Min:
                                                    requirement.Min = value
                                                    Settings.Current.LootProfile.Save()

                                                PyImGui.same_line(0, 5)
                                                PyImGui.push_item_width(item_width)
                                                value = PyImGui.slider_int("##MaxRequirement", requirement.Max, 0, 13)
                                                if value < requirement.Min:
                                                    requirement.Min = value
                                                    Settings.Current.LootProfile.Save()

                                                elif value != requirement.Max:
                                                    requirement.Max = value                                                
                                                    Settings.Current.LootProfile.Save()



                                            
                                                        
                                    PyImGui.end_child()

                                    width = (remaining_size[0]) / 2

                                    if PyImGui.button(IconsFontAwesome5.ICON_TRASH, width, 25) and len(lootItem.Conditions) > 1:
                                        Settings.Current.LootProfile.Items[selected_lootItem.ItemInfo.ModelID.name].Conditions.remove(condition)
                                        Settings.Current.LootProfile.Save()
                                    ImGui.show_tooltip("Delete Condition")

                                    PyImGui.same_line(0, 5)

                                    if PyImGui.button(IconsFontAwesome5.ICON_PLUS, width, 25):
                                        Settings.Current.LootProfile.Items[selected_lootItem.ItemInfo.ModelID.name].Conditions.append(LootItem.LootItemConditionedActions("New Condition (" + str(len(Settings.Current.LootProfile.Items[selected_lootItem.ItemInfo.ModelID.name].Conditions)) + ")"))
                                        Settings.Current.LootProfile.Save()
                                    ImGui.show_tooltip("Add Condition")

                                    PyImGui.end_tab_item()                                    
                            PyImGui.end_tab_bar()
                       
    
                    else:
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 0, 0, 255)))
                        PyImGui.text_wrapped("Item is not yet configured.")
                        PyImGui.pop_style_color(1)

                        if PyImGui.button(IconsFontAwesome5.ICON_PLUS + " Add to Profile", 0, 25) and selected_lootItem != None and not selected_lootItem.ItemInfo.ModelID in Settings.Current.LootProfile.Items:
                            Settings.Current.LootProfile.Items[selected_lootItem.ItemInfo.ModelID.name] = LootItem.LootItem(selected_lootItem.ItemInfo.ModelID)
                            Settings.Current.LootProfile.Save()                           

                PyImGui.end_child()

            else:
                PyImGui.text("No Item Selected")

        PyImGui.end_child()

        PyImGui.end_tab_item()

def DrawMods():    
    global mod_search, filtered_weapon_mods, scroll_bar_visible

    tab_name = "Weapon Mods"
    if(PyImGui.begin_tab_item(tab_name)) and Settings.Current.LootProfile:
        #Get Size of the tab
        tab_size = PyImGui.get_content_region_avail()

        PyImGui.push_item_width(tab_size[0] - 20)
        search = PyImGui.input_text("##Search", mod_search)
        if(search == None or search == "") and not PyImGui.is_item_active():
            PyImGui.same_line(15, 0)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 125)))
            PyImGui.text(IconsFontAwesome5.ICON_SEARCH + " Search for Mod Name or Mod Struct...")
            PyImGui.pop_style_color(1)

        if search != None and search != mod_search:
            mod_search = search
            filtered_weapon_mods = {}
            for mod in Data.WeaponMods.values():
                if mod == None or mod.Struct == "":
                    continue

                if mod.Name.lower().find(mod_search.lower()) != -1 or mod.Struct.lower().find(mod_search.lower()) != -1:
                    filtered_weapon_mods[mod.Struct] = mod
            
        PyImGui.push_style_var(ImGui.ImGuiStyleVar.ChildBorderSize, 0)
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.CellPadding, 2, 2)
        if (PyImGui.begin_child(tab_name + "TableHeaders#1", (tab_size[0] - 20 if scroll_bar_visible else 0, 20), True, PyImGui.WindowFlags.NoBackground)):

            PyImGui.begin_table("Weapon Mods Table", len(Data.WeaponType) + 2, PyImGui.TableFlags.ScrollY )
            PyImGui.table_setup_column("##Texture", PyImGui.TableColumnFlags.WidthFixed, 50)
            PyImGui.table_setup_column("Name", PyImGui.TableColumnFlags.WidthStretch)

            for weaponType in Data.WeaponType:                
                PyImGui.table_setup_column(weaponType.name, PyImGui.TableColumnFlags.WidthFixed, 50)
            
            PyImGui.table_headers_row()
            PyImGui.end_table()
            
        PyImGui.end_child()
        
        scroll_bar_visible = False
        if (PyImGui.begin_child(tab_name + "#1", (0, 0), True, PyImGui.WindowFlags.NoBackground)):
            

            PyImGui.begin_table("Weapon Mods Table", len(Data.WeaponType) + 2, PyImGui.TableFlags.RowBg | PyImGui.TableFlags.BordersInnerH)
            PyImGui.table_setup_column("##Texture", PyImGui.TableColumnFlags.WidthFixed, 50)
            PyImGui.table_setup_column("Name", PyImGui.TableColumnFlags.WidthStretch)

            for weaponType in Data.WeaponType:                
                PyImGui.table_setup_column(weaponType.name, PyImGui.TableColumnFlags.WidthFixed, 50)
            
            count = 0            
            for mod in filtered_weapon_mods.values():
                count += 1
                row_background_color = Utils.RGBToColor(36, 36, 36, 125) if count % 2 == 0 else Utils.RGBToColor(0, 0, 0, 125)
                PyImGui.push_style_color(PyImGui.ImGuiCol.TableRowBg, Utils.ColorToTuple(row_background_color))
  
                if mod == None or mod.Struct == "":
                    continue

                PyImGui.table_next_row()


                label = f"{mod.Name}"
                
                PyImGui.table_next_column()
                PyImGui.push_style_color(PyImGui.ImGuiCol.Button, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, Utils.ColorToTuple(Utils.RGBToColor(255, 255, 255, 0)))
                PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 5, 8)

                PyImGui.button(IconsFontAwesome5.ICON_SHIELD_ALT + "##" + mod.Struct)

                PyImGui.table_next_column()
                PyImGui.button(label, 0, 25)
                ImGui.show_tooltip("Mod: " + mod.Name  + "\n" + "Struct: " + mod.Struct + "\n" + "Identifier: " + str(mod.Identifier) + "\n" + "Args: " + str(mod.Arg1) + "|" + str(mod.Arg2))
                
                PyImGui.pop_style_color(3)
                PyImGui.pop_style_var(1)

                PyImGui.table_next_column()

                for weaponType in Data.WeaponType:
                    unique_id = f"##{mod.Struct}{weaponType}"
                    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0,8)

                    is_selected = mod.Struct in Settings.Current.LootProfile.WeaponMods and weaponType.name in Settings.Current.LootProfile.WeaponMods[mod.Struct] and Settings.Current.LootProfile.WeaponMods[mod.Struct][weaponType.name] == True
                    mod_selected = PyImGui.checkbox(unique_id, is_selected)

                    PyImGui.pop_style_var(1)
                    ImGui.show_tooltip("Keep " if is_selected else "Ignore " + mod.Name + " for " + weaponType.name)

                    if is_selected != mod_selected:
                        if mod_selected:
                            if mod.Struct not in Settings.Current.LootProfile.WeaponMods:
                                Settings.Current.LootProfile.WeaponMods[mod.Struct] = {}

                            Settings.Current.LootProfile.WeaponMods[mod.Struct][weaponType.name] = True
                        else:
                            Settings.Current.LootProfile.WeaponMods[mod.Struct].pop(weaponType.name, None)  

                        if len(Settings.Current.LootProfile.WeaponMods[mod.Struct]) == 0:
                            Settings.Current.LootProfile.WeaponMods.pop(mod.Struct, None)

                        Settings.Current.LootProfile.Save()
                    
                    PyImGui.table_next_column()

                    PyImGui.pop_style_color(1)

                scroll_bar_visible = scroll_bar_visible or PyImGui.get_scroll_max_y() > 0            
                PyImGui.pop_style_color(2)

        PyImGui.pop_style_var(2)

        
        PyImGui.end_table()
        PyImGui.end_child()


        PyImGui.end_tab_item()

def DrawRunes():   
    global show_price_check_popup, trader_type

    tab_name = "Runes"
    if(PyImGui.begin_tab_item(tab_name)) and Settings.Current.LootProfile:
        if (PyImGui.begin_child(tab_name + "#1", (0, 0), True, PyImGui.WindowFlags.NoFlag)):
            PyImGui.text("Rune Selection")

            remaining_space = PyImGui.get_content_region_avail()
            PyImGui.same_line(remaining_space[0] - 255, 5)
            if PyImGui.button("Get Expensive Runes from Merchant", 250, 0):
                if Settings.Current.LootProfile:
                    show_price_check_popup = not show_price_check_popup
                    if show_price_check_popup:
                        trader_type = "RUNES"
                        PyImGui.open_popup("Get Expensive Runes from Merchant")
                    else:
                        PyImGui.close_current_popup()                
            
            PyImGui.separator()

            PyImGui.begin_tab_bar("RunesTabBar")

            for profession, runes in Data.RunesByProfession.items():
                if runes == None:
                    continue

                profession_name = profession.name
                profession_name = "Common" if profession == Profession._None else profession_name

                if not PyImGui.begin_tab_item(profession_name):
                    continue
                
                PyImGui.begin_child("RunesSelection#1", (0, 0), True, PyImGui.WindowFlags.NoBackground)
                for rune in runes:
                    #Check if rune is an actual Rune
                    if rune == None or rune.Struct == "":
                        continue                    

                    color = Utility.Util.GetRarityColor(rune.Rarity.value)
                    PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color["text"]))
                    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg, Utils.ColorToTuple(color["content"]))
                    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, Utils.ColorToTuple(color["frame"]))
                    label = f"{rune.Name}"
                    unique_id = f"##{rune.Struct}"
                    rune_selected = PyImGui.checkbox(IconsFontAwesome5.ICON_SHIELD_ALT + " "  + label + unique_id, rune.Struct in Settings.Current.LootProfile.Runes and Settings.Current.LootProfile.Runes[rune.Struct] == True)
                    if rune.Struct in Settings.Current.LootProfile.Runes and Settings.Current.LootProfile.Runes[rune.Struct] != rune_selected:
                        Settings.Current.LootProfile.Runes[rune.Struct] = rune_selected
                        Settings.Current.LootProfile.Save()

                    PyImGui.pop_style_color(3)
                    ImGui.show_tooltip("Rune: " + rune.Name  + "\n" + "Struct: " + rune.Struct)
                
                PyImGui.end_child()
                PyImGui.end_tab_item()
            
            PyImGui.end_tab_bar()

        PyImGui.end_child()

        DrawPriceCheckPopup()
        PyImGui.end_tab_item()

def DrawPriceCheckPopup():
    global show_price_check_popup, entered_price_threshold

    if Settings.Current.LootProfile == None:
        return

    if show_price_check_popup:
        PyImGui.open_popup("Get Expensive Runes from Merchant")

    if PyImGui.begin_popup("Get Expensive Runes from Merchant"):
        PyImGui.text("Please enter a price threshold:")
        PyImGui.separator()            

        price = PyImGui.input_int("##PriceThreshold", entered_price_threshold)
        if price != None and price != entered_price_threshold:
            entered_price_threshold = price    

        PyImGui.same_line(0, 5)  

        if PyImGui.button("Check Prices", 100, 0):
            if(trader_type == "RUNES"):
                if entered_price_threshold != None and entered_price_threshold > 0:
                    ConsoleLog("LootEx", "Checking for expensive runes from merchant with price threshold: " + str(entered_price_threshold), Console.MessageType.Info)
                    LootCheck.LootCheck.GetExpensiveRunesFromMerchant(entered_price_threshold)
                else:
                    ConsoleLog("LootEx", "Price threshold must be greater than 0!", Console.MessageType.Error)
                    
            show_price_check_popup = False
            PyImGui.close_current_popup()

        PyImGui.end_popup()
        
    if PyImGui.is_mouse_clicked(0) and not PyImGui.is_item_hovered():
        if show_price_check_popup:
            PyImGui.close_current_popup()
            show_price_check_popup = False

def DrawItemTypeSelectable(item_type, is_selected) -> tuple[bool, bool]:
    if Settings.Current.LootProfile == None:
        return False, False
    
    color = Utils.RGBToColor(255, 255, 255, 255) if is_selected else Utils.RGBToColor(255, 255, 255, 125)

    PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color))
    selected = PyImGui.checkbox(IconsFontAwesome5.ICON_BUG + " " + item_type.name, is_selected)
    PyImGui.pop_style_color(1)
    
    return is_selected != selected, selected

def VerticalCenteredText(text: str, sameline_spacing : Optional[float] = None, desired_height: int = 24) -> float:
    textSize = PyImGui.calc_text_size(text)
    textOffset = (desired_height - textSize[1]) / 2
     
    cursorY = PyImGui.get_cursor_pos_y()
    cusorX = PyImGui.get_cursor_pos_x()

    if textOffset > 0:
        PyImGui.set_cursor_pos_y(cursorY + textOffset)

    PyImGui.text(text)

    
    if sameline_spacing:
        if textOffset > 0:
            PyImGui.set_cursor_pos_y(cursorY)

        # PyImGui.set_cursor_pos_x(cusorX + textSize[0] + sameline_spacing)
        PyImGui.set_cursor_pos_x(sameline_spacing)
    
    return textSize[0]

def DrawItemSelectable(item : ItemSelectable):
    global selected_lootItems, filtered_loot_items
    if Settings.Current.LootProfile == None:
        return False, False

    if item.IsSelected:
        color = Utility.Util.GetRarityColor(Rarity.Blue)
        PyImGui.push_style_color(PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(color["content"]))
    
    if item.Hovered:
        color = Utility.Util.GetRarityColor(Rarity.Purple)
        PyImGui.push_style_color(PyImGui.ImGuiCol.ChildBg, Utils.ColorToTuple(color["frame"]))

    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
    PyImGui.begin_child("ItemSelectable" + str(item.ItemInfo.ModelID), (0, 20), False, PyImGui.WindowFlags.NoFlag)

    attributes = [Utility.Util.GetAttributeName(a) + ", " for a in item.ItemInfo.Attributes] if item.ItemInfo.Attributes else []
    item_name = item.ItemInfo.Name if not item.ItemInfo.Attributes else item.ItemInfo.Name + " (" + "".join(attributes).removesuffix(",") + ")" if len(item.ItemInfo.Attributes) > 1 else item.ItemInfo.Name + " (" + Utility.Util.GetAttributeName(item.ItemInfo.Attributes[0]) + ")"
    
    has_Settings = item.ItemInfo.ModelID.name in Settings.Current.LootProfile.Items
    color = Utility.Util.GetRarityColor(Rarity.Gold)["text"] if has_Settings else Utils.RGBToColor(255, 255, 255, 255)
    PyImGui.push_style_color(PyImGui.ImGuiCol.Text, Utils.ColorToTuple(color))
    VerticalCenteredText(item_name)
    PyImGui.pop_style_color(1)

    PyImGui.end_child()
    PyImGui.pop_style_var(1)

    ImGui.show_tooltip(item_name)

    if item.IsSelected:
        PyImGui.pop_style_color(1)

    if item.Hovered:
        PyImGui.pop_style_color(1)
        
    item.Hovered = PyImGui.is_item_hovered()
    PyImGui.is_item_active()

    if PyImGui.is_mouse_clicked(0) and item.Hovered:        
        selected_lootItems = [item]

        for other_item in filtered_loot_items:
            other_item.IsSelected = False
        
        item.IsSelected = True

