import json
import os
from LootEx import models
from LootEx.enum import ModType
from Py4GWCoreLib import UIManager
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import Attribute, Console, NumberPreference, ServerLanguage
from Py4GWCoreLib.enums import ItemType, Rarity, Profession

import importlib
importlib.reload(models)

DamageRanges: dict[ItemType, dict[int, models.IntRange]] = {
    ItemType.Axe: {
        0:  models.IntRange(6, 12),
        1:  models.IntRange(6, 12),
        2:  models.IntRange(6, 14),
        3:  models.IntRange(6, 17),
        4:  models.IntRange(6, 19),
        5:  models.IntRange(6, 22),
        6:  models.IntRange(6, 24),
        7:  models.IntRange(6, 25),
        8:  models.IntRange(6, 27),
        9:  models.IntRange(6, 28),
    },
    ItemType.Bow: {
        0:  models.IntRange(9, 13),
        1:  models.IntRange(9, 14),
        2:  models.IntRange(10, 16),
        3:  models.IntRange(11, 18),
        4:  models.IntRange(12, 20),
        5:  models.IntRange(13, 22),
        6:  models.IntRange(14, 24),
        7:  models.IntRange(14, 25),
        8:  models.IntRange(14, 27),
        9:  models.IntRange(14, 28),
    },

    ItemType.Daggers: {
        0:  models.IntRange(4, 8),
        1:  models.IntRange(4, 8),
        2:  models.IntRange(5, 9),
        3:  models.IntRange(5, 11),
        4:  models.IntRange(6, 12),
        5:  models.IntRange(6, 13),
        6:  models.IntRange(7, 14),
        7:  models.IntRange(7, 15),
        8:  models.IntRange(7, 16),
        9:  models.IntRange(7, 17),
    },

    ItemType.Offhand: {
        0:  models.IntRange(6),
        1:  models.IntRange(6),
        2:  models.IntRange(7),
        3:  models.IntRange(8),
        4:  models.IntRange(9),
        5:  models.IntRange(10),
        6:  models.IntRange(11),
        7:  models.IntRange(11),
        8:  models.IntRange(12),
        9:  models.IntRange(12),
    },

    ItemType.Hammer: {
        0:  models.IntRange(11, 15),
        1:  models.IntRange(11, 16),
        2:  models.IntRange(12, 19),
        3:  models.IntRange(14, 22),
        4:  models.IntRange(15, 24),
        5:  models.IntRange(16, 28),
        6:  models.IntRange(17, 30),
        7:  models.IntRange(18, 32),
        8:  models.IntRange(18, 34),
        9:  models.IntRange(19, 35),
    },

    ItemType.Scythe: {
        0:  models.IntRange(8, 17),
        1:  models.IntRange(8, 18),
        2:  models.IntRange(9, 21),
        3:  models.IntRange(10, 24),
        4:  models.IntRange(10, 28),
        5:  models.IntRange(10, 32),
        6:  models.IntRange(10, 35),
        7:  models.IntRange(10, 36),
        8:  models.IntRange(9, 40),
        9:  models.IntRange(9, 41),
    },

    ItemType.Shield: {
        0:  models.IntRange(8),
        1:  models.IntRange(9),
        2:  models.IntRange(10),
        3:  models.IntRange(11),
        4:  models.IntRange(12),
        5:  models.IntRange(13),
        6:  models.IntRange(14),
        7:  models.IntRange(15),
        8:  models.IntRange(16),
        9:  models.IntRange(16),
    },

    ItemType.Spear: {
        0:  models.IntRange(8, 12),
        1:  models.IntRange(8, 13),
        2:  models.IntRange(10, 15),
        3:  models.IntRange(11, 17),
        4:  models.IntRange(11, 19),
        5:  models.IntRange(12, 21),
        6:  models.IntRange(13, 23),
        7:  models.IntRange(13, 25),
        8:  models.IntRange(14, 26),
        9:  models.IntRange(14, 27),
    },

    ItemType.Staff: {
        0:  models.IntRange(7, 11),
        1:  models.IntRange(7, 11),
        2:  models.IntRange(8, 13),
        3:  models.IntRange(9, 14),
        4:  models.IntRange(10, 16),
        5:  models.IntRange(10, 18),
        6:  models.IntRange(10, 19),
        7:  models.IntRange(11, 20),
        8:  models.IntRange(11, 21),
        9:  models.IntRange(11, 22),
    },

    ItemType.Sword: {
        0:  models.IntRange(8, 10),
        1:  models.IntRange(8, 11),
        2:  models.IntRange(9, 13),
        3:  models.IntRange(11, 14),
        4:  models.IntRange(12, 16),
        5:  models.IntRange(13, 18),
        6:  models.IntRange(14, 19),
        7:  models.IntRange(14, 20),
        8:  models.IntRange(15, 22),
        9:  models.IntRange(15, 22),
    },

    ItemType.Wand: {
        0:  models.IntRange(7, 11),
        1:  models.IntRange(7, 11),
        2:  models.IntRange(8, 13),
        3:  models.IntRange(9, 14),
        4:  models.IntRange(10, 16),
        5:  models.IntRange(10, 18),
        6:  models.IntRange(11, 19),
        7:  models.IntRange(11, 20),
        8:  models.IntRange(11, 21),
        9:  models.IntRange(11, 22),
    },
}

ItemType_MetaTypes: dict[ItemType, list[ItemType]] = {
    ItemType.Weapon: [
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Scythe,
        ItemType.Spear,
        ItemType.Staff,
        ItemType.Sword,
        ItemType.Wand
        ],

    ItemType.MartialWeapon: [
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Scythe,
        ItemType.Spear,
        ItemType.Sword
        ],

    ItemType.OffhandOrShield: [
        ItemType.Offhand,
        ItemType.Shield
        ],
    
    ItemType.EquippableItem : [
        ItemType.Axe,
        ItemType.Bow,
        ItemType.Daggers,
        ItemType.Hammer,
        ItemType.Offhand,
        ItemType.Scythe,
        ItemType.Shield,
        ItemType.Spear,
        ItemType.Staff,
        ItemType.Sword,
        ItemType.Wand
    ],

    ItemType.SpellcastingWeapon: [
        ItemType.Offhand,
        ItemType.Staff,
        ItemType.Wand
    ],
}

Caster_Attributes: list[Attribute] = [
    Attribute.FastCasting,
    Attribute.IllusionMagic,
    Attribute.DominationMagic,
    Attribute.InspirationMagic,
    Attribute.BloodMagic,
    Attribute.DeathMagic,
    Attribute.SoulReaping,
    Attribute.Curses,
    Attribute.AirMagic,
    Attribute.EarthMagic,
    Attribute.FireMagic,
    Attribute.WaterMagic,
    Attribute.EnergyStorage,
    Attribute.HealingPrayers,
    Attribute.SmitingPrayers,
    Attribute.ProtectionPrayers,
    Attribute.DivineFavor,
    Attribute.Communing,
    Attribute.RestorationMagic,
    Attribute.ChannelingMagic,
    Attribute.SpawningPower,
]
Shield_Attributes: list[Attribute] = [
    Attribute.Strength,
    Attribute.Tactics,
    Attribute.Command,
    Attribute.Motivation,
    Attribute.Leadership,
]
Item_Attributes: dict[ItemType, list[Attribute]] = {
    ItemType.Axe: [Attribute.AxeMastery],
    ItemType.Bow: [Attribute.Marksmanship],
    ItemType.Daggers: [Attribute.DaggerMastery],
    ItemType.Hammer: [Attribute.HammerMastery],
    ItemType.Scythe: [Attribute.ScytheMastery],
    ItemType.Shield: Shield_Attributes,
    ItemType.Spear: [Attribute.SpearMastery],
    ItemType.Sword: [Attribute.Swordsmanship],
    ItemType.Offhand: Caster_Attributes,
    ItemType.Wand: Caster_Attributes,
    ItemType.Staff: Caster_Attributes,
}

Items: list[models.Item] = []
Items_By_Type: dict[ItemType, list[models.Item]] = {}

Runes : list[models.Rune] = []
Runes_by_Profession: dict[Profession, list[models.Rune]] = {}

# Change to be a dictionary of dictionaries per identifier so we can handle mods like "Fortitude" (Suffix) and "Hale" (Prefix) which share the same identifier
# We should also be able to get mods with non perfect stats like a +29 health Fortitude mod
# We need to iterate from the mod with the most modifiers to the least modifiers, specialized to less specialized
Weapon_Mods : list[models.WeaponMod] = []

def UpdateLanguage(server_language : ServerLanguage):
    global Items, Runes, Weapon_Mods
    
    for item in Items:
        item.update_language(server_language)
        
    for rune in Runes:
        rune.update_language(server_language)
        
    for weapon_mod in Weapon_Mods:
        weapon_mod.update_language(server_language)

def __init__(self):
    pass
    
@staticmethod
def Load():
    # Load the runes
    LoadRunes()
    
    # Load the weapon mods
    LoadWeaponMods()

    # Load the items
    LoadItems()
    
@staticmethod
def LoadWeaponMods():
    global Weapon_Mods
    #Load weapon mods from data/weapon_mods.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "weapon_mods.json")

    ConsoleLog("LootEx", f"Loading weapon mods from {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        weapon_mods = json.load(file)
        
        for value in weapon_mods:
            mod = models.WeaponMod.from_json(value)
            if not mod in Weapon_Mods:
                Weapon_Mods.append(mod)

    Weapon_Mods = sorted(Weapon_Mods, key=lambda x: x.name)

@staticmethod
def SaveWeaponMods():
    global Weapon_Mods

    #Save weapon mods to data/weapon_mods.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "weapon_mods.json")

    ConsoleLog("LootEx", f"Saving weapon mods to {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    with open(path, 'w', encoding='utf-8') as file:
        json.dump([mod.to_json() for mod in Weapon_Mods], file, indent=4, ensure_ascii=False)

@staticmethod
def LoadRunes():
    global Runes

    #Load runes from data/runes.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "runes.json")

    ConsoleLog("LootEx", f"Loading runes from {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        runes = json.load(file)
        
        for value in runes:          
            Runes.append(models.Rune.from_json(value))
    
    Runes = sorted(Runes, key=lambda x: x.name)

    for rune in Runes:
        if rune.profession not in Runes_by_Profession:
            Runes_by_Profession[rune.profession] = []

        Runes_by_Profession[rune.profession].append(rune)
                            
    for profession in Runes_by_Profession:
        Runes_by_Profession[profession].sort(key=lambda x: (x.mod_type, x.rarity.value, x.name))  

@staticmethod
def SaveRunes():
    global Runes

    #Save runes to data/runes.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "runes.json")

    ConsoleLog("LootEx", f"Saving runes to {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        
    with open(path, 'w', encoding='utf-8') as file:
        json.dump([rune.to_json() for rune in Runes], file, indent=4, ensure_ascii=False)

@staticmethod
def LoadItems():
    global Items

    #Load items from data/items.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "items.json")

    ConsoleLog("LootEx", f"Loading items from {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        items = json.load(file)
        
        for value in items:
            Items.append(models.Item.from_json(value))
        
    Items = sorted(Items, key=lambda x: (x.name))  

    for item in Items:
        if item.item_type not in Items_By_Type:
            Items_By_Type[item.item_type] = []

        Items_By_Type[item.item_type].append(item)
        
@staticmethod
def SaveItems():
    global Items

    #Save items to data/items.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "items.json")

    ConsoleLog("LootEx", f"Saving items to {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    with open(path, 'w', encoding='utf-8') as file:
        json.dump([item.to_json() for item in Items], file, indent=4, ensure_ascii=False)