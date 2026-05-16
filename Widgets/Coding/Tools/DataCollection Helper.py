from dataclasses import dataclass
from dataclasses import field
from datetime import datetime, timedelta
import json
import os
from typing import Optional

import Py4GW
import PyImGui
import PyUIManager


from Py4GWCoreLib import ImGui, Merchant
from Py4GWCoreLib.Agent import Agent
from Py4GWCoreLib.AgentArray import AgentArray
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.ImGui_src.types import Alignment
from Py4GWCoreLib.Map import Map
from Py4GWCoreLib.Player import Player
from Py4GWCoreLib.Py4GWcorelib import Utils
from Py4GWCoreLib.Routines import Routines
from Py4GWCoreLib.UIManager import CrafterWindow, FrameInfo, UIManager, WindowFrame
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.item_data.item_snapshot import ItemSnapshot
from Py4GWCoreLib.item_mods_src.upgrades import Inherent, Inscription, Upgrade, WeaponPrefix, WeaponSuffix
from Py4GWCoreLib.py4gwcorelib_src.Color import Color
from Py4GWCoreLib.py4gwcorelib_src.WidgetManager import get_widget_handler


project_path = Py4GW.Console.get_projects_path()
MODULE_NAME = "Data Collection Helper"
MODULE_ICON = os.path.join("Textures", "Module_Icons", "Research Code.png")
DATA_FILE_PATH = os.path.join(project_path, 'Widgets', 'Data', 'armor_crafters.json')
    
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

@dataclass
class CraftingRequirements:
    materials: dict[ModelID, int] = field(default_factory=dict)
    gold: int = 0
    skill_points: Optional[int] = None    
    
    
@dataclass
class CraftableItem:
    name: str
    item_type : ItemType
    model_id : int
    
    required_materials : CraftingRequirements
    
@dataclass
class CraftableWeapon(CraftableItem):
    requirement : int
    attribute : Attribute
    damage : tuple[int, int] #min, max
    prefix : Upgrade  
    suffix : Upgrade  
    inscription : Upgrade  
    inherent : list[Upgrade]  
    
        
@dataclass
class CraftableArmor(CraftableItem):
    armor_rating: int
    profession : Profession
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'armor_rating': self.armor_rating,
            'item_type': self.item_type.name,
            'model_id': self.model_id,
            'profession': self.profession.name,
        }

    @staticmethod
    def from_dict(data: dict) -> 'CraftableArmor':
        item_type_name = str(data.get('item_type', ItemType.Unknown.name))
        profession_name = str(data.get('profession', Profession._None.name))

        return CraftableArmor(
            name=str(data.get('name', '')),
            armor_rating=int(data.get('armor_rating', 0) or 0),
            item_type=ItemType[item_type_name] if item_type_name in ItemType.__members__ else ItemType.Unknown,
            model_id=int(data.get('model_id', 0) or 0),
            profession=Profession[profession_name] if profession_name in Profession.__members__ else Profession._None,
        )

@dataclass
class Npc:
    name : str = ""
    map_id : int = 0
    position : tuple[float, float] = (0.0, 0.0)
    model_id : int = 0
    encoded_name : bytes = b""
    
@dataclass
class Artisan(Npc):
    items : list[CraftableItem] = field(default_factory=list)

@dataclass
class ConsumableCrafter(Npc):
    consumables : list[CraftableItem] = field(default_factory=list)

@dataclass
class Weaponsmith(Npc):
    weapons : list[CraftableWeapon] = field(default_factory=list)
    
@dataclass
class Armorer(Npc):
    professions_armor_rating : dict[Profession, int] = field(default_factory=dict)
    armors : dict[Profession, list[CraftableArmor]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'encoded_name': list(self.encoded_name),
            'model_id': self.model_id,
            'map_id': self.map_id,
            'position': [self.position[0], self.position[1]],
            'professions_armor_rating': {
                profession.name: armor_rating
                for profession, armor_rating in self.professions_armor_rating.items()
            },
            'armors': {
                profession.name: [armor.to_dict() for armor in armors]
                for profession, armors in self.armors.items()
            },
        }

    @staticmethod
    def from_dict(data: dict) -> 'Armorer':
        professions_armor_rating: dict[Profession, int] = {}
        for profession_name, armor_rating in dict(data.get('professions_armor_rating', {})).items():
            if profession_name not in Profession.__members__:
                continue
            professions_armor_rating[Profession[profession_name]] = int(armor_rating or 0)

        armors: dict[Profession, list[CraftableArmor]] = {}
        for profession_name, entries in dict(data.get('armors', {})).items():
            if profession_name not in Profession.__members__:
                continue
            profession = Profession[profession_name]
            armors[profession] = [CraftableArmor.from_dict(entry) for entry in list(entries or [])]

        position_data = list(data.get('position', [0.0, 0.0]))
        position = (
            float(position_data[0]) if len(position_data) > 0 else 0.0,
            float(position_data[1]) if len(position_data) > 1 else 0.0,
        )

        return Armorer(
            name=str(data.get('name', '')),
            encoded_name=bytes(data.get('encoded_name', [])),
            model_id=int(data.get('model_id', 0) or 0),
            map_id=int(data.get('map_id', 0) or 0),
            position=position,
            professions_armor_rating=professions_armor_rating,
            armors=armors,
        )

    def HasMapUnlocked(self) -> bool:
        return Map.IsMapUnlocked(self.map_id)
    
    def GetAgentId(self) -> int:
        if not Routines.Checks.Map.IsMapReady():
            return 0
        
        if self.position == (0.0, 0.0):
            return 0
        
        agents = AgentArray.GetAgentArray()
        agents = AgentArray.Filter.ByDistance(agents, self.position, 300.0, False)
        
        for agent_id in agents:
            if agent_id is not None and Agent.GetModelID(agent_id) == self.model_id:
                return agent_id
        
        return 0
    
    def MoveTo(self):
        if not Routines.Checks.Map.IsMapReady():
            return
        
        if Map.GetBaseMapID() != Map.GetBaseMapID(self.map_id):
            if Map.IsMapUnlocked(self.map_id):
                Map.Travel(self.map_id)
                return
            else:
                Py4GW.Console.Log(MODULE_NAME, f"Map '{Map.GetMapName(self.map_id)}' is not unlocked yet.", Py4GW.Console.MessageType.Warning)
                return
        
        Player.Move(self.position[0], self.position[1])
        
        if (agent_id := self.GetAgentId()) != 0:
            Player.ChangeTarget(agent_id)
            Player.Interact(agent_id)
        
    def IsCrafterOpen(self) -> bool:
        if not Routines.Checks.Map.IsMapReady():
            return False
        
        if Map.GetBaseMapID() != Map.GetBaseMapID(self.map_id):
            return False
        
        agent_id = self.GetAgentId()
        if agent_id == 0:
            return False
        
        player_target_id = Player.GetTargetID()
        if player_target_id != agent_id:
            return False
        
        return CrafterWindow.IsOpen()
    
    def CollectData(self) -> bool:
        if not self.IsCrafterOpen():
            Py4GW.Console.Log(MODULE_NAME, f"Crafter '{self.name}' is not open. Please move to the crafter and open their crafting window before collecting data.", Py4GW.Console.MessageType.Warning)
            return False
        
        offered_items = Merchant.Trading.Crafter.GetOfferedItems()
        items = [ItemSnapshot.from_item_id(item_id) for item_id in offered_items]
        collected_count = 0

        pending_name_update = False
        for item in items:
            if item is None or not item.is_valid or not item.is_armor:
                continue

            profession = item.profession if item.profession not in (None, Profession._None) else _get_current_profession()
            if profession in (None, Profession._None):
                continue

            armor_name = item.name
            if not armor_name:
                pending_name_update = True
                continue
            
            armor = CraftableArmor(
                name=armor_name,
                armor_rating=int(self.professions_armor_rating.get(profession, 0) or 0),
                item_type=item.item_type,
                model_id=item.model_id,
                profession=profession,
            )
            
            if self._upsert_craftable_armor(armor):
                collected_count += 1

        if collected_count > 0:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"Collected {collected_count} craftable armor entries from '{self.name}'.",
                Py4GW.Console.MessageType.Success,
            )
        else:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"No new craftable armor entries were found for '{self.name}'.",
                Py4GW.Console.MessageType.Warning,
            )

        return not pending_name_update and collected_count > 0

    def _upsert_craftable_armor(self, armor: CraftableArmor) -> bool:
        entries = self.armors.setdefault(armor.profession, [])
        existing_index = next(
            (
                index for index, existing in enumerate(entries)
                if existing.model_id == armor.model_id and existing.item_type == armor.item_type
            ),
            -1,
        )

        if existing_index >= 0:
            existing = entries[existing_index]
            if (
                existing.name == armor.name
                and existing.armor_rating == armor.armor_rating
                and existing.profession == armor.profession
            ):
                return False
            entries[existing_index] = armor
        else:
            entries.append(armor)

        entries.sort(key=lambda entry: (entry.item_type.name, entry.name))
        return True
        
    def CloseCrafter(self):
        if self.IsCrafterOpen():
            CrafterWindow.Close()
            
        
    def Save(self):
        save_crafters_to_json()
        
P = Profession

PROPH_ARMOR_35 = {
    P.Warrior: 35,
    P.Ranger: 25,
    P.Monk: 15,
    P.Necromancer: 15,
    P.Mesmer: 15,
    P.Elementalist: 15,
}
PROPH_ARMOR_50 = {
    P.Warrior: 50,
    P.Ranger: 40,
    P.Monk: 30,
    P.Necromancer: 30,
    P.Mesmer: 30,
    P.Elementalist: 30,
}
PROPH_ARMOR_59 = {
    P.Warrior: 59,
    P.Ranger: 49,
    P.Monk: 39,
    P.Necromancer: 39,
    P.Mesmer: 39,
    P.Elementalist: 39,
}
PROPH_ARMOR_65 = {
    P.Warrior: 65,
    P.Ranger: 55,
    P.Monk: 45,
    P.Necromancer: 45,
    P.Mesmer: 45,
    P.Elementalist: 45,
}
PROPH_ARMOR_71 = {
    P.Warrior: 71,
    P.Ranger: 61,
    P.Monk: 51,
    P.Necromancer: 51,
    P.Mesmer: 51,
    P.Elementalist: 51,
}
PROPH_ARMOR_80 = {
    P.Warrior: 80,
    P.Ranger: 70,
    P.Monk: 60,
    P.Necromancer: 60,
    P.Mesmer: 60,
    P.Elementalist: 60,
}
FACTIONS_ARMOR_35 = {
    P.Warrior: 35,
    P.Ranger: 25,
    P.Monk: 15,
    P.Necromancer: 15,
    P.Mesmer: 15,
    P.Elementalist: 15,
    P.Assassin: 25,
    P.Ritualist: 15,
}
FACTIONS_ARMOR_50 = {
    P.Warrior: 50,
    P.Ranger: 40,
    P.Monk: 30,
    P.Necromancer: 30,
    P.Mesmer: 30,
    P.Elementalist: 30,
    P.Assassin: 40,
    P.Ritualist: 30,
}
FACTIONS_ARMOR_65 = {
    P.Warrior: 65,
    P.Ranger: 55,
    P.Monk: 45,
    P.Necromancer: 45,
    P.Mesmer: 45,
    P.Elementalist: 45,
    P.Assassin: 55,
    P.Ritualist: 45,
}
FACTIONS_ARMOR_80 = {
    P.Warrior: 80,
    P.Ranger: 70,
    P.Monk: 60,
    P.Necromancer: 60,
    P.Mesmer: 60,
    P.Elementalist: 60,
    P.Assassin: 70,
    P.Ritualist: 60,
}
FULL_ARMOR_80 = {
    P.Warrior: 80,
    P.Ranger: 70,
    P.Monk: 60,
    P.Necromancer: 60,
    P.Mesmer: 60,
    P.Elementalist: 60,
    P.Assassin: 70,
    P.Ritualist: 60,
    P.Paragon: 80,
    P.Dervish: 70,
}
NIGHTFALL_ARMOR_35 = {
    P.Warrior: 35,
    P.Ranger: 25,
    P.Monk: 15,
    P.Necromancer: 15,
    P.Mesmer: 15,
    P.Elementalist: 15,
    P.Paragon: 35,
    P.Dervish: 25,
}
NIGHTFALL_ARMOR_50 = {
    P.Warrior: 50,
    P.Ranger: 40,
    P.Monk: 30,
    P.Necromancer: 30,
    P.Mesmer: 30,
    P.Elementalist: 30,
    P.Paragon: 50,
    P.Dervish: 40,
}
NIGHTFALL_ARMOR_65 = {
    P.Warrior: 65,
    P.Ranger: 55,
    P.Monk: 45,
    P.Necromancer: 45,
    P.Mesmer: 45,
    P.Elementalist: 45,
    P.Paragon: 65,
    P.Dervish: 55,
}

CRAFTERS = [
    
    Armorer(name='Sol Pyrrhus', map_id=63, professions_armor_rating=PROPH_ARMOR_71.copy()),
    
    Armorer(name='Oroku', map_id=240, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Voldo the Exotic', map_id=239, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Koumei', map_id=351, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Maiya', map_id=351, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    Armorer(name='Wei Qi', map_id=351, professions_armor_rating=FACTIONS_ARMOR_80.copy()),
    
    Armorer(name='Eternal Forgemaster', map_id=34, professions_armor_rating=FULL_ARMOR_80.copy()),
    Armorer(name='Keeper of Armor', map_id=503, professions_armor_rating=FULL_ARMOR_80.copy()),
    
    Armorer(name='Mehinu', map_id=449, professions_armor_rating=NIGHTFALL_ARMOR_35, position=(-11202.0, 9346.0), model_id=4774, encoded_name=bytes([0x1, 0x81, 0x54, 0x20, 0x38, 0x91, 0xB6, 0x9C, 0x44, 0x3E, 0x0, 0x0])),
    Armorer(name='Pasu', map_id=491, professions_armor_rating=NIGHTFALL_ARMOR_50, position=(3944.0, 2378.0), model_id=4773, encoded_name=bytes([0x1, 0x81, 0xC5, 0x3F, 0x6F, 0xBC, 0xCB, 0xD4, 0x5B, 0x6D, 0x0, 0x0])),
    Armorer(name='Sulee', map_id=492, professions_armor_rating=NIGHTFALL_ARMOR_65, position=(607.0, 2710.0), model_id=4774, encoded_name=bytes([0x1, 0x81, 0xBE, 0x3F, 0xB7, 0xB0, 0x2A, 0x98, 0x1F, 0x2, 0x0, 0x0])),
    Armorer(name='Mateneh', map_id=414, professions_armor_rating=FULL_ARMOR_80, position=(-1805.0, -4050.0), model_id=5718, encoded_name=bytes([0x1, 0x81, 0x9A, 0x21, 0x2B, 0xFB, 0x48, 0xDA, 0x4D, 0x7B, 0x0, 0x0])),
    Armorer(name='Burreh', map_id=436, professions_armor_rating=FULL_ARMOR_80, position=(-4916.0, 8985.0), model_id=5437, encoded_name=bytes([0x1, 0x81, 0xC6, 0x21, 0x2F, 0xE7, 0xF0, 0xC4, 0x6C, 0x7C, 0x0, 0x0])),
    Armorer(name='Ahamid', map_id=436, professions_armor_rating=FULL_ARMOR_80, position=(-5870.0, 8255.0), model_id=4792, encoded_name=bytes([0x1, 0x81, 0x1, 0x57, 0xF0, 0xF4, 0xA9, 0x81, 0xA, 0x2A, 0x0, 0x0])),
    Armorer(name='Palmod', map_id=438, professions_armor_rating=FULL_ARMOR_80, position=(-14036.0, 8632.0), model_id=5674, encoded_name=bytes([0x1, 0x81, 0x96, 0x2D, 0xA3, 0xE0, 0xD5, 0x9B, 0x23, 0x44, 0x0, 0x0])),
    Armorer(name='Vatundo', map_id=493, professions_armor_rating=FULL_ARMOR_80, position=(-3164.0, 16472.0), model_id=4773, encoded_name=bytes([0x1, 0x81, 0x3A, 0x53, 0x95, 0x8B, 0xE7, 0xF1, 0x4A, 0x51, 0x0, 0x0])),
    Armorer(name='Klub', map_id=640, professions_armor_rating=FULL_ARMOR_80, position=(12781.0, 16732.0), model_id=6810, encoded_name=bytes([0x2, 0x81, 0x9D, 0x1E, 0x36, 0x82, 0xCC, 0xBF, 0xD2, 0x7C, 0x0, 0x0])),
    Armorer(name='Brett', map_id=642, professions_armor_rating=FULL_ARMOR_80, position=(-552.0, 1250.0), model_id=6101, encoded_name=bytes([0x2, 0x81, 0xAC, 0x1E, 0x4F, 0x8B, 0x7F, 0xFE, 0xDA, 0x14, 0x0, 0x0])),
    Armorer(name='Radi', map_id=644, professions_armor_rating=FULL_ARMOR_80, position=(18894.0, -3806.0), model_id=6436, encoded_name=bytes([0x2, 0x81, 0xBC, 0x1E, 0xC1, 0xE2, 0x11, 0xA5, 0xBC, 0x65, 0x0, 0x0])),
    Armorer(name='Gobrech Stonefoot', map_id=652, professions_armor_rating=FULL_ARMOR_80, position=(1860.0, 1681.0), model_id=6287, encoded_name=bytes([0x2, 0x81, 0xDB, 0x25, 0xA7, 0xE4, 0x25, 0xBB, 0x53, 0x5D, 0x0, 0x0])),
    Armorer(name='Jolvor Stoneforge', map_id=675, professions_armor_rating=FULL_ARMOR_80, position=(5419.0, -27343.0), model_id=1553, encoded_name=bytes([0x2, 0x81, 0x42, 0x39, 0x6C, 0xCE, 0x9E, 0x95, 0x50, 0x65, 0x0, 0x0])),
    
    Armorer(name='Kambei', map_id=242, professions_armor_rating=FACTIONS_ARMOR_35, position=(-7260.0, 12622.0), model_id=3323, encoded_name=bytes([0x24, 0x57, 0x9A, 0x9F, 0x67, 0xBC, 0xA4, 0x3B, 0x0, 0x0])),
    Armorer(name='Moon Ahn', map_id=242, professions_armor_rating=FACTIONS_ARMOR_35, position=(-7115.0, 12636.0), model_id=3324, encoded_name=bytes([0x23, 0x57, 0xB5, 0xB9, 0xA5, 0xE7, 0xB5, 0x18, 0x0, 0x0])),
    Armorer(name='Nu Leng', map_id=242, professions_armor_rating=FACTIONS_ARMOR_35, position=(-6614.0, 12465.0), model_id=3323, encoded_name=bytes([0x22, 0x57, 0xC2, 0xCC, 0x6C, 0xB0, 0xCC, 0x8, 0x0, 0x0])),
    Armorer(name='Maeko', map_id=251, professions_armor_rating=FACTIONS_ARMOR_50, position=(16647.0, 16881.0), model_id=3324, encoded_name=bytes([0x19, 0x57, 0x3B, 0x8D, 0x9, 0x8E, 0x27, 0x31, 0x0, 0x0])),
    Armorer(name='Seiji', map_id=251, professions_armor_rating=FACTIONS_ARMOR_50, position=(16656.0, 17055.0), model_id=3323, encoded_name=bytes([0x1A, 0x57, 0x4B, 0xC7, 0xCC, 0x8F, 0x91, 0x21, 0x0, 0x0])),
    Armorer(name='Taura', map_id=251, professions_armor_rating=FACTIONS_ARMOR_50, position=(16425.0, 17446.0), model_id=3332, encoded_name=bytes([0x1B, 0x57, 0x80, 0xD2, 0x9F, 0xDF, 0xE1, 0x7B, 0x0, 0x0])),
    Armorer(name='Fugui Ge', map_id=250, professions_armor_rating=FACTIONS_ARMOR_65, position=(20381.0, 9576.0), model_id=3323, encoded_name=bytes([0xE, 0x57, 0x35, 0xB7, 0x51, 0x89, 0x8, 0x77, 0x0, 0x0])),
    Armorer(name='Lain', map_id=250, professions_armor_rating=FACTIONS_ARMOR_65, position=(20508.0, 9497.0), model_id=3324, encoded_name=bytes([0xF, 0x57, 0x3A, 0xBC, 0xD2, 0x85, 0x8, 0x1F, 0x0, 0x0])),
    Armorer(name='Tsukare', map_id=250, professions_armor_rating=FACTIONS_ARMOR_65, position=(19709.0, 9444.0), model_id=3331, encoded_name=bytes([0x10, 0x57, 0xE0, 0xFF, 0x2A, 0xBF, 0x5D, 0x48, 0x0, 0x0])),
    Armorer(name='Morbach', map_id=77, professions_armor_rating=FACTIONS_ARMOR_80, position=(6961.0, -1537.0), model_id=3454, encoded_name=bytes([0x9C, 0x6D, 0xA7, 0x89, 0x9F, 0xEE, 0xF1, 0x67, 0x0, 0x0])),
    Armorer(name='Giygas', map_id=130, professions_armor_rating=FACTIONS_ARMOR_80, position=(23180.0, 11879.0), model_id=3454, encoded_name=bytes([0x93, 0x6D, 0xB0, 0xB1, 0x8F, 0xEE, 0xC7, 0x31, 0x0, 0x0])),
    Armorer(name='Tateos', map_id=193, professions_armor_rating=FACTIONS_ARMOR_80, position=(4785.0, 798.0), model_id=3670, encoded_name=bytes([0xC4, 0x6D, 0x8E, 0xEC, 0xFC, 0xF0, 0x8A, 0x3F, 0x0, 0x0])),
    Armorer(name='Kakumei', map_id=194, professions_armor_rating=FACTIONS_ARMOR_80, position=(-700.0, -5156.0), model_id=3323, encoded_name=bytes([0xF5, 0x6D, 0xDC, 0xCE, 0xC8, 0xB1, 0x43, 0x4A, 0x0, 0x0])),
    Armorer(name='Suki', map_id=194, professions_armor_rating=FACTIONS_ARMOR_80, position=(-891.0, -5382.0), model_id=3324, encoded_name=bytes([0xF6, 0x6D, 0x2, 0xE8, 0x35, 0x8D, 0x50, 0x22, 0x0, 0x0])),
    Armorer(name='Ryoko', map_id=194, professions_armor_rating=FACTIONS_ARMOR_80, position=(-1682.0, -3970.0), model_id=3324, encoded_name=bytes([0xF7, 0x6D, 0x88, 0x9F, 0xC, 0xAE, 0x6A, 0x2B, 0x0, 0x0])),
    Armorer(name='Mikolas', map_id=279, professions_armor_rating=FACTIONS_ARMOR_80, position=(13037.0, -21167.0), model_id=3670, encoded_name=bytes([0x1F, 0x7B, 0x85, 0x8A, 0xB5, 0xD8, 0x94, 0x61, 0x0, 0x0])),
    
    Armorer(name='Samuka', map_id=55, professions_armor_rating=PROPH_ARMOR_50, position=(2343.0, 6843.0), model_id=2008, encoded_name=bytes([0x56, 0x2D, 0x98, 0xC2, 0x8E, 0x9E, 0x8D, 0x55, 0x0, 0x0])),
    Armorer(name='Shada', map_id=136, professions_armor_rating=PROPH_ARMOR_59, position=(20437.0, -10959.0), model_id=2008, encoded_name=bytes([0x4F, 0x2D, 0xC6, 0xB5, 0xA2, 0x86, 0x7C, 0x3A, 0x0, 0x0])),
    Armorer(name='Hagen', map_id=156, professions_armor_rating=PROPH_ARMOR_80, position=(-12914.0, 18003.0), model_id=1559, encoded_name=bytes([0xB0, 0x2D, 0x1A, 0xB6, 0xAF, 0xA5, 0x5A, 0x7C, 0x0, 0x0])),
    Armorer(name='Karl', map_id=157, professions_armor_rating=PROPH_ARMOR_80, position=(5184.0, -14389.0), model_id=1559, encoded_name=bytes([0xB3, 0x2D, 0x22, 0xA9, 0xBF, 0xD0, 0x53, 0x79, 0x0, 0x0])),
    
    Armorer(name='Banoit', map_id=81, professions_armor_rating=PROPH_ARMOR_35, position=(1545.0, 5585.0), model_id=2118, encoded_name=bytes([0x9B, 0x2D, 0x83, 0xEA, 0xD5, 0xAE, 0xAA, 0x18, 0x0, 0x0])),
    Armorer(name='Corwen', map_id=81, professions_armor_rating=PROPH_ARMOR_50, position=(1905.0, 6218.0), model_id=2120, encoded_name=bytes([0x9C, 0x2D, 0x9D, 0xA4, 0xC8, 0x89, 0x27, 0x8, 0x0, 0x0])),
    Armorer(name='Harlan', map_id=40, professions_armor_rating=PROPH_ARMOR_35, position=(22887.0, 10033.0), model_id=2118, encoded_name=bytes([0x8E, 0x2D, 0x56, 0xA0, 0x24, 0x8F, 0x6D, 0x2F, 0x0, 0x0])),
    Armorer(name='Breyshaw', map_id=134, professions_armor_rating=PROPH_ARMOR_50, position=(6561.0, 5157.0), model_id=2118, encoded_name=bytes([0xC6, 0x2D, 0x19, 0xC0, 0x7E, 0xE7, 0x2, 0x6E, 0x0, 0x0])),
    Armorer(name='Kathir', map_id=109, professions_armor_rating=PROPH_ARMOR_71, position=(1889.0, 1637.0), model_id=2046, encoded_name=bytes([0x6A, 0x2D, 0xA6, 0xFB, 0x33, 0xD5, 0xD2, 0x55, 0x0, 0x0])),
    Armorer(name='Morgren', map_id=20, professions_armor_rating=PROPH_ARMOR_80, position=(814.0, 4651.0), model_id=1558, encoded_name=bytes([0xBA, 0x2D, 0x4D, 0x87, 0x1D, 0xE3, 0xD3, 0xD, 0x0, 0x0])),
    Armorer(name='Seifred', map_id=20, professions_armor_rating=PROPH_ARMOR_80, position=(1742.0, 5162.0), model_id=1558, encoded_name=bytes([0xB9, 0x2D, 0xB8, 0xFE, 0xFE, 0xC8, 0x84, 0x51, 0x0, 0x0])),
    Armorer(name='Alemeth', map_id=49, professions_armor_rating=PROPH_ARMOR_65, position=(6016.0, -8406.0), model_id=2089, encoded_name=bytes([0x82, 0x2D, 0x91, 0xA0, 0x1C, 0x8C, 0xB7, 0x3, 0x0, 0x0])),
    Armorer(name='Kailan', map_id=57, professions_armor_rating=PROPH_ARMOR_59, position=(17558.0, -18033.0), model_id=2028, encoded_name=bytes([0x49, 0x2D, 0x55, 0xD1, 0x8, 0xE6, 0x23, 0x53, 0x0, 0x0])),
    Armorer(name='Hanita', map_id=139, professions_armor_rating=PROPH_ARMOR_65, position=(-14449.0, 2275.0), model_id=2016, encoded_name=bytes([0x79, 0x2D, 0x55, 0xFA, 0xE0, 0x86, 0x4C, 0x62, 0x0, 0x0])),
    Armorer(name='Saphir', map_id=142, professions_armor_rating=PROPH_ARMOR_59, position=(173.0, -4431.0), model_id=1544, encoded_name=bytes([0x7F, 0x2D, 0xEC, 0xB6, 0x23, 0xEC, 0xCA, 0x31, 0x0, 0x0])),
]

RAW_CRAFTERS = CRAFTERS.copy()
PROFESSION_ORDER = [
    Profession.Warrior,
    Profession.Ranger,
    Profession.Monk,
    Profession.Necromancer,
    Profession.Mesmer,
    Profession.Elementalist,
    Profession.Assassin,
    Profession.Ritualist,
    Profession.Paragon,
    Profession.Dervish,
]

PROFESSION_LABELS = {
    Profession.Warrior: 'W',
    Profession.Ranger: 'R',
    Profession.Monk: 'Mo',
    Profession.Necromancer: 'N',
    Profession.Mesmer: 'Me',
    Profession.Elementalist: 'E',
    Profession.Assassin: 'A',
    Profession.Ritualist: 'Rt',
    Profession.Paragon: 'P',
    Profession.Dervish: 'D',
}

search_query = ''
show_unlocked_only = False
out_posts = Map.GetOutpostIDs()
sweep_stop_requested = False
sweep_is_running = False
sweep_status = 'Idle'
sweep_current_name = ''
sweep_current_index = 0
sweep_total = 0


def _get_current_profession() -> Profession:
    agent = Agent.GetAgentByID(Player.GetAgentID())
    living_agent = agent.GetAsAgentLiving() if agent is not None else None

    if living_agent is None:
        return Profession._None

    try:
        return Profession(living_agent.primary)
    except Exception:
        return Profession._None


def save_crafters_to_json(path: str = DATA_FILE_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        'version': 1,
        'saved_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'crafters': [crafter.to_dict() for crafter in CRAFTERS],
    }

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)

    Py4GW.Console.Log(
        MODULE_NAME,
        f"Saved {len(CRAFTERS)} crafters to '{path}'.",
        Py4GW.Console.MessageType.Success,
    )


def load_crafters_from_json(path: str = DATA_FILE_PATH):
    if not os.path.exists(path):
        Py4GW.Console.Log(
            MODULE_NAME,
            f"Crafter data file '{path}' does not exist yet.",
            Py4GW.Console.MessageType.Warning,
        )
        return False

    with open(path, 'r', encoding='utf-8') as file:
        payload = json.load(file)

    loaded_crafters = [Armorer.from_dict(entry) for entry in list(payload.get('crafters', []))]
    if not loaded_crafters:
        Py4GW.Console.Log(
            MODULE_NAME,
            f"No crafter entries were found in '{path}'.",
            Py4GW.Console.MessageType.Warning,
        )
        return False

    CRAFTERS[:] = loaded_crafters
    Py4GW.Console.Log(
        MODULE_NAME,
        f"Loaded {len(CRAFTERS)} crafters from '{path}'.",
        Py4GW.Console.MessageType.Success,
    )
    
    updated = False
    for crafter in CRAFTERS:
        if not _is_position_collected(crafter) or not crafter.encoded_name:
            #Check RAW_CRAFTERS for position data
            raw_match = next((raw for raw in RAW_CRAFTERS if raw.name == crafter.name and raw.map_id == crafter.map_id), None)
            if raw_match:
                crafter.position = raw_match.position
                crafter.model_id = raw_match.model_id
                crafter.encoded_name = raw_match.encoded_name
                updated = True
                
    if updated:
        save_crafters_to_json()
        
    return True


def _find_current_open_crafter() -> Armorer | None:
    current_map_id = Map.GetBaseMapID()
    for crafter in CRAFTERS:
        if Map.GetBaseMapID(crafter.map_id) != current_map_id:
            continue
        
        if crafter.IsCrafterOpen():
            return crafter
    return None


def _collect_current_open_crafter():
    crafter = _find_current_open_crafter()
    if crafter is None:
        Py4GW.Console.Log(
            MODULE_NAME,
            'No known crafter window is currently open on this map.',
            Py4GW.Console.MessageType.Warning,
        )
        return

    collected_count = crafter.CollectData()
    if collected_count > 0:
        save_crafters_to_json()

def _format_armor_ratings(crafter: Armorer) -> str:
    return '  '.join(
        f'{PROFESSION_LABELS[profession]}:{crafter.professions_armor_rating[profession]}'
        for profession in PROFESSION_ORDER
        if profession in crafter.professions_armor_rating
    )


def _matches_search(crafter: Armorer, query: str) -> bool:
    if not query:
        return True

    query = query.lower()
    map_name = Map.GetMapName(crafter.map_id).lower()
    return query in crafter.name.lower() or query in map_name


def _get_visible_crafters() -> list[Armorer]:
    visible: list[Armorer] = []
    for crafter in CRAFTERS:
        if show_unlocked_only and not crafter.HasMapUnlocked():
            continue
        if not _matches_search(crafter, search_query.strip()):
            continue
        visible.append(crafter)
    return visible


def _is_position_collected(crafter: Armorer) -> bool:
    return (
        crafter.position != (0.0, 0.0)
        and crafter.model_id != 0
    )
    
def _is_auto_reachable_crafter(crafter: Armorer) -> bool:
    return (
        crafter.HasMapUnlocked()
        and crafter.map_id in out_posts
        and crafter.position != (0.0, 0.0)
        and crafter.model_id != 0
    )


def _get_auto_reachable_crafters() -> list[Armorer]:
    profession = _get_current_profession()   
     
    def armor_collected(armor : CraftableArmor) -> bool:
        return not armor.name.startswith('Model')
    
    def armors_collected(crafter: Armorer) -> bool:
        return all(
            armor_collected(armor)
            for armor in crafter.armors.get(profession, [])
        ) 
    
    crafters = [crafter for crafter in CRAFTERS if _is_auto_reachable_crafter(crafter) and profession in crafter.professions_armor_rating and (not profession in crafter.armors or not armors_collected(crafter))]
    sorted_by_map = sorted(crafters, key=lambda c: (c.professions_armor_rating.get(profession, -1) if profession is not None else 0, c.map_id), reverse=False)
    
    return sorted_by_map


def _set_sweep_status(status: str, crafter_name: str = '', current_index: int = 0, total: int = 0):
    global sweep_status
    global sweep_current_name
    global sweep_current_index
    global sweep_total

    sweep_status = status
    sweep_current_name = crafter_name
    sweep_current_index = current_index
    sweep_total = total


def _finish_sweep(status: str):
    global sweep_is_running
    global sweep_stop_requested

    sweep_is_running = False
    sweep_stop_requested = False
    _set_sweep_status(status)


def _start_crafter_sweep():
    global sweep_is_running
    global sweep_stop_requested

    if sweep_is_running:
        return

    reachable_crafters = _get_auto_reachable_crafters()
    if not reachable_crafters:
        _set_sweep_status('No unlocked auto-reachable crafters found.')
        return

    sweep_is_running = True
    sweep_stop_requested = False
    _set_sweep_status('Starting crafter sweep...', total=len(reachable_crafters))
    GLOBAL_CACHE.Coroutines.append(_run_crafter_sweep(reachable_crafters))


def _request_stop_crafter_sweep():
    global sweep_stop_requested

    GLOBAL_CACHE.Coroutines.clear()  # Clear any pending steps to expedite stopping
    if not sweep_is_running:
        return

    sweep_stop_requested = True
    _set_sweep_status('Stopping after current step...', sweep_current_name, sweep_current_index, sweep_total)


def _run_crafter_sweep(crafters: list[Armorer]):
    total = len(crafters)
    closed_count = 0

    for index, crafter in enumerate(crafters, start=1):
        if sweep_stop_requested:
            _finish_sweep(f'Sweep stopped ({closed_count}/{total} completed).')
            return

        map_name = Map.GetMapName(crafter.map_id)
        _set_sweep_status(f'Traveling to {map_name}...', crafter.name, index, total)

        if Map.GetBaseMapID() != Map.GetBaseMapID(crafter.map_id):
            travel_success = yield from Routines.Yield.Map.TravelToOutpost(crafter.map_id, timeout=20000, log=False)
            if not travel_success:
                Py4GW.Console.Log(
                    MODULE_NAME,
                    f"Skipping '{crafter.name}' because travel to '{map_name}' failed.",
                    Py4GW.Console.MessageType.Warning,
                )
                continue

            yield from Routines.Yield.wait(500, break_on_map_transition=True)

        if sweep_stop_requested:
            _finish_sweep(f'Sweep stopped ({closed_count}/{total} completed).')
            return

        _set_sweep_status('Walking to crafter...', crafter.name, index, total)
        distance_to_crafter = Utils.Distance(Player.GetXY(), crafter.position)
        Py4GW.Console.Log(
            MODULE_NAME,
            f"Distance to '{crafter.name}' is {distance_to_crafter:.1f}. Allowing up to {int(distance_to_crafter * 10)} ms for movement.",
            Py4GW.Console.MessageType.Info,
        )
        
        move_success = yield from Routines.Yield.Movement.FollowPath([crafter.position], tolerance=200, timeout=int(distance_to_crafter * 50), log=False)
        if not move_success:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"Skipping '{crafter.name}' because movement to the stored position failed.",
                Py4GW.Console.MessageType.Warning,
            )
            continue

        _set_sweep_status('Opening crafter window...', crafter.name, index, total)
        window_opened = yield from _open_crafter_window(crafter)
        if not window_opened:
            Py4GW.Console.Log(
                MODULE_NAME,
                f"Skipping '{crafter.name}' because the crafter window did not open.",
                Py4GW.Console.MessageType.Warning,
            )
            continue

        _set_sweep_status('Collecting visible craftable armor...', crafter.name, index, total)
        crafter.CollectData()
        save_crafters_to_json()

        _set_sweep_status('Crafter window open, waiting 2 seconds...', crafter.name, index, total)
        yield from Routines.Yield.wait(2000)
        CrafterWindow.Close()
        yield from Routines.Yield.wait(500)
        closed_count += 1

    _finish_sweep(f'Sweep complete ({closed_count}/{total} windows opened).')


def _open_crafter_window(crafter: Armorer, timeout_ms: int = 1500):
    elapsed = 0
    retry_interval = 250
    reissue_interval = 1000
    since_reissue = reissue_interval

    while elapsed <= timeout_ms:
        if sweep_stop_requested:
            return False

        if CrafterWindow.IsOpen():
            return True

        agent_id = crafter.GetAgentId()
        if agent_id == 0:
            yield from Routines.Yield.wait(retry_interval)
            elapsed += retry_interval
            since_reissue += retry_interval
            continue

        if since_reissue >= reissue_interval:
            yield from Routines.Yield.Agents.ChangeTarget(agent_id)
            yield from Routines.Yield.Agents.InteractAgent(agent_id)
            since_reissue = 0

        player_distance = Utils.Distance(Player.GetXY(), Agent.GetXY(agent_id))
        if player_distance > 220.0:
            yield from Routines.Yield.Movement.FollowPath([crafter.position], tolerance=150, timeout=5000, log=False)
        else:
            yield from Routines.Yield.wait(retry_interval)

        elapsed += retry_interval
        since_reissue += retry_interval

    return CrafterWindow.IsOpen()


def get_armor_rating_as_constant_name(crafter: Armorer) -> str:
    for constant_name, armor_dict in globals().items():
        if isinstance(armor_dict, dict) and all(
            profession in armor_dict and armor_dict[profession] == crafter.professions_armor_rating.get(profession, -1)
            for profession in crafter.professions_armor_rating
        ):
            return constant_name
        
    return "CUSTOM"

def draw_window():
    global search_query
    global show_unlocked_only

    current_map_id = Map.GetBaseMapID()
    current_map_name = Map.GetMapName(current_map_id)
    current_profession = _get_current_profession()
    if current_profession == Profession._None:
        current_profession = Profession.Warrior
    visible_crafters = _get_visible_crafters()
    # visible_crafters = [crafter for crafter in visible_crafters if current_profession is None or current_profession in crafter.professions_armor_rating]
    sorted_by_map = sorted(visible_crafters, key=lambda c: (c.professions_armor_rating.get(current_profession, -1) if current_profession is not None else 0, c.map_id), reverse=False)
    unlocked_count = sum(1 for crafter in CRAFTERS if crafter.HasMapUnlocked())
    auto_reachable_count = len(_get_auto_reachable_crafters())
    collected_armor_count = sum(len(entries) for crafter in CRAFTERS for entries in crafter.armors.values())

    PyImGui.text(f'Current map: {current_map_name} ({current_map_id})')
    PyImGui.text(f'Armorers: {len(visible_crafters)} shown / {len(CRAFTERS)} total / {unlocked_count} unlocked')
    PyImGui.text(f'Auto-reachable sweep targets: {auto_reachable_count}')
    PyImGui.text(f'Collected craftable armor entries: {collected_armor_count}')
    PyImGui.text(f'JSON path: {DATA_FILE_PATH}')
    PyImGui.text('Collection note: automatic collection records the currently visible crafter page; run it on each profession to fill the full set.')
    PyImGui.text(f'Sweep status: {sweep_status}')
    if sweep_current_name:
        PyImGui.text(f'Current sweep target: {sweep_current_name} ({sweep_current_index}/{sweep_total})')
    if ImGui.button('Collect open crafter##crafter_collect_open', width=150):
        _collect_current_open_crafter()
    PyImGui.same_line(0, 10)
    if ImGui.button('Save JSON##crafter_save_json', width=100):
        save_crafters_to_json()
    PyImGui.same_line(0, 10)
    if ImGui.button('Load JSON##crafter_load_json', width=100):
        load_crafters_from_json()
    if ImGui.button('Sweep + collect reachable##crafter_sweep_start', width=180, disabled=sweep_is_running):
        _start_crafter_sweep()
    PyImGui.same_line(0, 10)
    if ImGui.button('Stop sweep##crafter_sweep_stop', width=100, disabled=not sweep_is_running):
        _request_stop_crafter_sweep()
    PyImGui.separator()

    PyImGui.set_next_item_width(260)
    search_query = PyImGui.input_text('Search##crafter_search', search_query, 128)
    PyImGui.same_line(0, 10)
    show_unlocked_only = PyImGui.checkbox('Unlocked only', show_unlocked_only)
    PyImGui.separator()

    style = ImGui.get_style()
    
    table_flags = (
        PyImGui.TableFlags.Borders
        | PyImGui.TableFlags.RowBg
        | PyImGui.TableFlags.ScrollY
        | PyImGui.TableFlags.Resizable
        | PyImGui.TableFlags.SizingStretchSame
    )
    if PyImGui.begin_table('##armor_crafters_table', 7, table_flags):
        PyImGui.table_setup_column('Name', PyImGui.TableColumnFlags.WidthStretch, 140)
        PyImGui.table_setup_column('Map', PyImGui.TableColumnFlags.WidthStretch, 170)
        PyImGui.table_setup_column('Unlocked', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_setup_column('Armor', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_setup_column('Action', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_setup_column('Copy', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_setup_column('Collected', PyImGui.TableColumnFlags.WidthFixed, 70)
        PyImGui.table_headers_row()

        for crafter in sorted_by_map:
            pos_collected = _is_position_collected(crafter)
            if not pos_collected:
                style.Text.push_color_direct((255, 100, 100, 255))
            
            map_name = Map.GetMapName(crafter.map_id)
            is_unlocked = crafter.HasMapUnlocked()
            is_outpost = crafter.map_id in out_posts
            is_here = current_map_id == Map.GetBaseMapID(crafter.map_id)

            PyImGui.table_next_row()

            PyImGui.table_set_column_index(0)
            PyImGui.text(crafter.name)

            PyImGui.table_set_column_index(1)
            PyImGui.text(f'{map_name} ({crafter.map_id})')

            PyImGui.table_set_column_index(2)
            PyImGui.text('Yes' if is_unlocked else 'No')

            PyImGui.table_set_column_index(3)
            PyImGui.text(str(crafter.professions_armor_rating.get(current_profession, 'N/A')))

            PyImGui.table_set_column_index(4)
            button_label = 'Move' if (crafter.position != (0, 0) and is_here) else 'Here' if is_here else 'Travel' if is_outpost else 'Manual'
            button_disabled = (crafter.position == (0, 0) and is_here) or not is_unlocked or not is_outpost
            if ImGui.button(f'{button_label}##crafter_move_{crafter.name}', width=-1, disabled=button_disabled):
                crafter.MoveTo()
                
            PyImGui.table_set_column_index(5)
            copy_label = f'Copy'
            if ImGui.button(f'{copy_label}##crafter_copy_{crafter.name}', width=-1):
                crafter.CloseCrafter()  # Ensure the window is closed to avoid clipboard issues
                target_id = Player.GetTargetID()
                if target_id != 0:
                    target = Agent.GetAgentByID(target_id)
                    if target is not None:
                        enc_name_bytes = bytes(Agent.GetEncNameByID(target_id))
                        enc_name = ', '.join(f'0x{b:X}' for b in enc_name_bytes)
                        
                        pos = Agent.GetXY(target_id)
                        model_id = Agent.GetModelID(target_id)
                        armor_rating_code = get_armor_rating_as_constant_name(crafter)
                        
                        clipboard_text = (
                            f"ArmorCrafter(name='{crafter.name}', "
                            f"map_id={crafter.map_id}, "
                            f"professions_armor_rating={armor_rating_code}, "
                            f"position=({pos[0]:.1f}, {pos[1]:.1f}), "
                            f"model_id={model_id}, "
                            f"encoded_name=bytes([{enc_name}])"
                            f"),"
                        )
                        PyImGui.set_clipboard_text(clipboard_text)

            PyImGui.table_set_column_index(6)
            collected_count = sum(len(entries) for entries in crafter.armors.values())
            PyImGui.text(str(collected_count))
            
            if not pos_collected:
                style.Text.pop_color()
            
        PyImGui.end_table()


def main():
    if not Routines.Checks.Map.IsMapReady():
        return
    
    PyImGui.set_next_window_size((800, 400), PyImGui.ImGuiCond.FirstUseEver)
    if PyImGui.begin(MODULE_NAME, PyImGui.WindowFlags.NoFlag):
        draw_window()
    PyImGui.end()

GLOBAL_CACHE.Coroutines.clear()
load_crafters_from_json()
if __name__ == "__main__":
    main()
