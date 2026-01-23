import PyImGui
from HeroAI.ui import get_display_name
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.GlobalCache.SharedMemory import AccountData
from Py4GWCoreLib.ImGui_src.ImGuisrc import ImGui
from Py4GWCoreLib.ImGui_src.Textures import TextureState, ThemeTextures
from Py4GWCoreLib.ImGui_src.WindowModule import WindowModule
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Quest import Quest
from Py4GWCoreLib.Quest import Quest
from Py4GWCoreLib.enums_src.GameData_enums import ProfessionShort
from Py4GWCoreLib.enums_src.Multiboxing_enums import SharedCommandType
from Py4GWCoreLib.py4gwcorelib_src.Color import Color, ColorPalette
from Py4GWCoreLib.py4gwcorelib_src.Console import ConsoleLog
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Widgets.PartyQuestLog.settings import Settings
from account_data_src.quest_data_src import QuestData, QuestNode

class UI():
    COLOR_MAP: dict[str, tuple[float, float, float, float]] = {
        "@warning": ColorPalette.GetColor("red").to_tuple_normalized(),
        "@Warning": ColorPalette.GetColor("red").to_tuple_normalized(),
        "@Quest":   ColorPalette.GetColor("bright_green").to_tuple_normalized(),
        "@quest":   ColorPalette.GetColor("bright_green").to_tuple_normalized(),
        "@completed":   ColorPalette.GetColor("creme").to_tuple_normalized(),
        "Header":  ColorPalette.GetColor("creme").to_tuple_normalized(),   
    }
    
    QUEST_STATE_COLOR_MAP: dict[str, Color] = {
        "Completed": ColorPalette.GetColor("bright_green").opacify(0.6),
        "Active": ColorPalette.GetColor("white").opacify(0.6),
        "Inactive": ColorPalette.GetColor("light_gray").opacify(0.3),
    }
    gray_color = Color(150, 150, 150, 255)
    
    Settings : "Settings" = Settings()
    QuestLogWindow : WindowModule = WindowModule("Party Quest Log", "Party Quest Log", window_size=(Settings.LogPosWidth, Settings.LogPosHeight), window_pos=(Settings.LogPosX, Settings.LogPosY), can_close=True)
    ActiveQuest : QuestNode | None = None
    
    @staticmethod
    def draw_log(quest_data : QuestData, accounts: dict[int, AccountData]):
        open = UI.QuestLogWindow.begin()
        if open:
            style = ImGui.get_style()
            grouped_quests : dict[str, list[QuestNode]] = {}
            avail = PyImGui.get_content_region_avail()
            _, height = avail[0], avail[1] / 2
            
            if quest_data.mission_map_quest is not None:
                grouped_quests.setdefault(quest_data.mission_map_quest.quest_location, []).append(quest_data.mission_map_quest)
            
            for quest in quest_data.quest_log.values():
                if quest.is_primary:
                    grouped_quests.setdefault("Primary", []).append(quest)
                else:
                    grouped_quests.setdefault(quest.quest_location, []).append(quest)
            
            # Sort quests by name for each location
            for location, quests in grouped_quests.items():
                sorted_quests = sorted(quests, key=lambda q: q.name)
                grouped_quests[location] = sorted_quests
            
            style.WindowPadding.push_style_var(2, 8)
            ImGui.begin_child("QuestLogChild", (0, height), border=True)
            style.WindowPadding.pop_style_var()
                        
            width = PyImGui.get_content_region_avail()[0]
            og_item_spacing = style.ItemSpacing.get_current()
            
            for location, quests in grouped_quests.items():
                ImGui.push_font("Regular", 16)
                location_open = ImGui.tree_node(f"{location}")
                ImGui.pop_font()
                                
                if location_open:                    
                    style.ItemSpacing.push_style_var(4, 0)
                    
                    for quest in quests:  
                        max_width = max(1, width - (len(accounts) * 10) - 30)
                        tokenized_lines = Utils.TokenizeMarkupText(f"{quest.name}{(" <c=@completed>(Completed)</c>") if quest.is_completed else ""}", max_width=max_width)     
                                 
                        posY = PyImGui.get_cursor_pos_y()               
                        cursor = PyImGui.get_cursor_screen_pos()
                        height_selectable = len(tokenized_lines) * PyImGui.get_text_line_height() + 4
                        computed_rect = (cursor[0], cursor[1], width, height_selectable)
                        color = Color(200, 200, 200, 40) if quest == UI.ActiveQuest else \
                                Color(200, 200, 200, 20) if ImGui.is_mouse_in_rect(computed_rect) else \
                                None
                                
                        if color:
                            style.ChildBg.push_color(color.rgb_tuple)                        
                            
                        style.Border.push_color(color.opacify(0.1).rgb_tuple if color else (0,0,0,0))
                        style.WindowPadding.push_style_var(4, 4)
                        ImGui.begin_child(f"QuestSelectable_{quest.quest_id}", (0, height_selectable), border=True, flags=PyImGui.WindowFlags.NoScrollbar | PyImGui.WindowFlags.NoScrollWithMouse)      
                        ImGui.render_tokenized_markup(tokenized_lines, max_width=max_width, COLOR_MAP=UI.COLOR_MAP)
                        ImGui.end_child()
                        style.WindowPadding.pop_style_var()
                                     
                        style.Border.pop_color()
                        
                        if color:
                            style.ChildBg.pop_color()                        
                            
                        if PyImGui.is_item_clicked(0):
                            if PyImGui.is_mouse_double_clicked(0):
                                if Map.IsMapUnlocked(quest.map_to):
                                    ConsoleLog("Party Quest Log", f"Traveling to map '{Map.GetMapName(quest.map_to)}' ({quest.map_to}) for quest '{quest.name}'...")
                                    Map.Travel(quest.map_to)
                                else:
                                    ConsoleLog("Party Quest Log", f"Cannot travel to locked map '{Map.GetMapName(quest.map_to)}' ({quest.map_to}).")
                            else:
                                UI.ActiveQuest = quest
                            
                        if PyImGui.is_item_hovered():
                            if accounts: 
                                style.ItemSpacing.push_style_var(og_item_spacing.value1, og_item_spacing.value2)   
                                ImGui.begin_tooltip()
                                
                                bullet_col_width = PyImGui.get_text_line_height()
                                ImGui.begin_table("QuestStatusTable", 3, PyImGui.TableFlags.NoBordersInBody)
                                PyImGui.table_setup_column("bullet", PyImGui.TableColumnFlags.WidthFixed, bullet_col_width)
                                PyImGui.table_setup_column("professions", PyImGui.TableColumnFlags.WidthFixed, bullet_col_width * 2.5)
                                PyImGui.table_setup_column("text", PyImGui.TableColumnFlags.WidthStretch)
                                
                                for acc in accounts.values():
                                    name = get_display_name(acc)
                                    acc_quest = next((q for q in acc.PlayerData.QuestsData.Quests if q.QuestID == quest.quest_id), None)
                                    
                                    active = acc_quest is not None
                                    completed = acc_quest and acc_quest.IsCompleted
                                    
                                    color = UI.QUEST_STATE_COLOR_MAP["Completed"] if completed else (UI.QUEST_STATE_COLOR_MAP["Active"] if active else UI.QUEST_STATE_COLOR_MAP["Inactive"])
                                                        
                                    PyImGui.table_next_row()
                                    PyImGui.table_set_column_index(0)
                                    style.Text.push_color(color.rgb_tuple)  
                                    PyImGui.bullet_text("")
                                    style.Text.pop_color()
                                                                    
                                    prof_primary, prof_secondary = "", ""
                                    prof_primary = ProfessionShort(
                                        acc.PlayerProfession[0]).name if acc.PlayerProfession[0] != 0 else ""
                                    prof_secondary = ProfessionShort(
                                        acc.PlayerProfession[1]).name if acc.PlayerProfession[1] != 0 else ""
                                    PyImGui.table_next_column()
                                    ImGui.text(f"{prof_primary}{('/' if prof_secondary else '')}{prof_secondary}")
                                    
                                    PyImGui.table_next_column()
                                    ImGui.text(name)
                                
                                ImGui.end_table()   
                                
                                ImGui.separator()
                                ImGui.push_font("Regular", 12)
                                for name, col in UI.QUEST_STATE_COLOR_MAP.items():
                                    style.Text.push_color(col.rgb_tuple)  
                                    PyImGui.bullet_text("")
                                    style.Text.pop_color()
                                    
                                    PyImGui.same_line(0, 5)
                                    ImGui.text(f"{name}")
                                    PyImGui.same_line(0, 5)
                                    
                                ImGui.pop_font()
                                ImGui.end_tooltip()
                                style.ItemSpacing.pop_style_var() 
                        
                        after_y = PyImGui.get_cursor_pos_y()
                        for i, acc in enumerate(accounts.values()):
                            PyImGui.set_cursor_pos(width - (i * 10) - 20, posY + 2)
                            ## chek if quest.quest_id is in active quests (.QuestID) 
                            acc_quest = next((q for q in acc.PlayerData.QuestsData.Quests if q.QuestID == quest.quest_id), None)
                            
                            active = acc_quest is not None
                            completed = acc_quest and acc_quest.IsCompleted
                            
                            color = UI.QUEST_STATE_COLOR_MAP["Completed"] if completed else (UI.QUEST_STATE_COLOR_MAP["Active"] if active else UI.QUEST_STATE_COLOR_MAP["Inactive"])

                            style.Text.push_color(color.rgb_tuple)                              
                            PyImGui.bullet_text("")
                            style.Text.pop_color()
                        
                        PyImGui.set_cursor_pos_y(after_y + 4)
                            
                        # ImGui.show_tooltip(f"{acc.AccountEmail} | {acc.CharacterName} | {("Completed" if completed else "Active" if active else "Not Active")} " )
                        # ImGui.show_tooltip(f"{name.lower().replace(" ", "_")}@gmail.com | {name} | {("Completed" if completed else "Active" if active else "Not Active")} " )
                        
                    style.ItemSpacing.pop_style_var()
                    ImGui.tree_pop()
                    
                pass
            
            ImGui.end_child()
            
            ImGui.begin_child("QuestDetailsChild", (0, height - 10), border=False)
            if UI.ActiveQuest is not None:
                UI.draw_quest_details(UI.ActiveQuest, accounts)
            ImGui.end_child()
            
            
            UI.QuestLogWindow.process_window()
            if UI.QuestLogWindow.changed:
                
                pos = UI.QuestLogWindow.end_pos
                UI.Settings.LogPosX = pos[0]
                UI.Settings.LogPosY = pos[1]
                
                size = UI.QuestLogWindow.window_size
                UI.Settings.LogPosWidth = size[0]
                UI.Settings.LogPosHeight = size[1]
                
                UI.Settings.save_settings()
        
        UI.QuestLogWindow.end()
        
    
    @staticmethod
    def draw_quest_details(quest: QuestNode, accounts: dict[int, AccountData]):
        child_width = PyImGui.get_content_region_avail()[0]
        text_clip = child_width - 120
        cursor_pos = PyImGui.get_cursor_screen_pos()
        
        PyImGui.push_clip_rect(cursor_pos[0], cursor_pos[1], text_clip, 50, True)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, UI.COLOR_MAP["Header"])
        ImGui.text("Quest Summary", font_size=16)
        PyImGui.pop_style_color(1)
        PyImGui.pop_clip_rect()
        
        PyImGui.same_line(child_width - 110, 0)
        if ImGui.button("Abandon", 100, 20):
            if PyImGui.get_io().key_ctrl:
                ConsoleLog("Party Quest Log", f"Requesting to abandon quest '{quest.name}'...")
                Quest.AbandonQuest(quest.quest_id)
                
                for _, acc in accounts.items():                
                    GLOBAL_CACHE.ShMem.SendMessage(Player.GetAccountEmail(), acc.AccountEmail, SharedCommandType.AbandonQuest, (quest.quest_id,0,0,0))
        
        if PyImGui.is_item_hovered():
            ImGui.begin_tooltip()
            ImGui.text_colored("Ctrl + Click to abandon the quest on all party members.", UI.gray_color.color_tuple)    
            ImGui.end_tooltip()
        
        PyImGui.spacing()
                                                
        
        tokens = Utils.TokenizeMarkupText(quest.objectives, max_width=child_width)
        ImGui.render_tokenized_markup(tokens, max_width=child_width, COLOR_MAP=UI.COLOR_MAP)

        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, UI.COLOR_MAP["Header"])
        PyImGui.text_wrapped(f"{quest.npc_quest_giver}")
        PyImGui.pop_style_color(1)

        tokens = Utils.TokenizeMarkupText(quest.description, max_width=child_width)
        ImGui.render_tokenized_markup(tokens, max_width=child_width, COLOR_MAP=UI.COLOR_MAP)

        PyImGui.separator()
        PyImGui.text(f"From: {Map.GetMapName(quest.map_from)}")
        PyImGui.text(f"To: {Map.GetMapName(quest.map_to)}")
        PyImGui.text(f"Marker X,Y: ({quest.quest_marker[0]}, {quest.quest_marker[1]})")
        PyImGui.end_child()

    @staticmethod
    def draw_modal():
        pass