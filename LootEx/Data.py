import datetime
import json
import os
from typing import Optional
from LootEx import models, utility
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.Py4GWcorelib import ConsoleLog
from Py4GWCoreLib.enums import Attribute, Console, ServerLanguage
from Py4GWCoreLib.enums import ItemType, Profession

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

    ItemType.EquippableItem: [
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

Items: dict[int, models.Item] = {}
Items_By_Type: dict[ItemType, dict[int, models.Item]] = {}

Runes: dict[str, models.Rune] = {}
Runes_by_Profession: dict[Profession, dict[str, models.Rune]] = {}

# Change to be a dictionary of dictionaries per identifier so we can handle mods like "Fortitude" (Suffix) and "Hale" (Prefix) which share the same identifier
# We should also be able to get mods with non perfect stats like a +29 health Fortitude mod
# We need to iterate from the mod with the most modifiers to the least modifiers, specialized to less specialized
Weapon_Mods: dict[str, models.WeaponMod] = {}

Nick_Cycle_Start_Date = datetime.datetime(2009, 4, 20)
Nick_Cycle_Count = 137

Materials: dict[int, models.Material] = {}
Common_Materials: dict[int, models.Material] = {}
Rare_Materials: dict[int, models.Material] = {}


def UpdateLanguage(server_language: ServerLanguage):
    global Items, Runes, Weapon_Mods

    for item in Items.values():
        item.update_language(server_language)

    for rune in Runes.values():
        rune.update_language(server_language)

    for weapon_mod in Weapon_Mods.values():
        weapon_mod.update_language(server_language)


def __init__(self):
    pass


@staticmethod
def Reload():
    global Runes, Weapon_Mods, Items, Runes_by_Profession, Items_By_Type
    
    Runes.clear()
    Runes_by_Profession.clear()
    # Load the runes
    LoadRunes()

    Weapon_Mods.clear()
    # Load the weapon mods
    LoadWeaponMods()

    Items.clear()
    Items_By_Type.clear()
    # Load the items
    LoadItems()
    
@staticmethod
def Load():
    # Load the runes
    LoadRunes()

    # Load the weapon mods
    LoadWeaponMods()

    # Load the items
    LoadItems()
    
    #Load the materials
    LoadMaterials()


@staticmethod
def LoadMaterials():
    global Materials, Common_Materials, Rare_Materials

    # Load materials from data/materials.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "materials.json")

    ConsoleLog(
        "LootEx", f"Loading materials...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        materials = json.load(file)

        for value in materials.values():
            material = models.Material.from_json(value)
            Materials[material.model_id] = material

    Materials = dict(sorted(Materials.items(), key=lambda item: (item[1].name)))
    
    Common_Materials = {
        model_id: material for model_id, material in Materials.items() if material.material_type == models.MaterialType.Common}
    
    Rare_Materials = {
        model_id: material for model_id, material in Materials.items() if material.material_type == models.MaterialType.Rare}
    
@staticmethod
def SaveMaterials():
    global Materials

    # Save materials to data/materials.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "materials.json")

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    with open(path, 'w', encoding='utf-8') as file:
        ConsoleLog(
            "LootEx", f"Saving materials ...", Console.MessageType.Debug)
        json.dump({material.model_id: material.to_json()
                  for material in Materials.values()}, file, indent=4, ensure_ascii=False)

@staticmethod
def LoadWeaponMods():
    global Weapon_Mods
    # Load weapon mods from data/weapon_mods.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "weapon_mods.json")

    ConsoleLog(
        "LootEx", f"Loading weapon mods from {path}...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        weapon_mods = json.load(file)

        if weapon_mods:  
            for value in weapon_mods.values():
                mod = models.WeaponMod.from_json(value)
                
                if not mod.identifier in Weapon_Mods:
                    Weapon_Mods[mod.identifier] = mod

    account_file = os.path.join(
        file_directory, "data", "diffs", GLOBAL_CACHE.Player.GetAccountEmail(), "weapon_mods.json")
    if os.path.exists(account_file):
        with open(account_file, 'r', encoding='utf-8') as file:
            weapon_mods = json.load(file)
            
            if weapon_mods:               
                for value in weapon_mods.values():
                    mod = models.WeaponMod.from_json(value)
                    
                    if not mod.identifier in Weapon_Mods:
                        Weapon_Mods[mod.identifier] = mod
                    else:
                        # If the mod already exists, we can update it
                        Weapon_Mods[mod.identifier].update(mod)

    # sort the weapon mods by mod.mod_type, then by name
    Weapon_Mods = dict(sorted(Weapon_Mods.items(), key=lambda item: (item[1].mod_type, item[1].name)))


@staticmethod
def SaveWeaponMods(shared_file: bool = False, mods: Optional[dict[str, models.WeaponMod]] = None):
    global Weapon_Mods

    # Save weapon mods to data/weapon_mods.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")

    if not shared_file:
        account_name = GLOBAL_CACHE.Player.GetAccountEmail()
        data_directory = os.path.join(
            file_directory, "data", "diffs", account_name)

    path = os.path.join(data_directory, "weapon_mods.json")


    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not shared_file:
        if mods is not None:
            mods = dict(sorted(mods.items(), key=lambda item: item[0]))
    else:
        mods = Weapon_Mods

    if mods is None:
        ConsoleLog(
            "LootEx", "No weapon mods to save.", Console.MessageType.Warning)
        return
    
    with open(path, 'w', encoding='utf-8') as file:
        ConsoleLog(
            "LootEx", f"Saving weapon mods ...", Console.MessageType.Debug)
        json.dump({mod.identifier: mod.to_json()
                  for mod in mods.values()}, file, indent=4, ensure_ascii=False)


@staticmethod
def LoadRunes():
    global Runes

    # Load runes from data/runes.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "runes.json")

    ConsoleLog(
        "LootEx", f"Loading runes ...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        runes = json.load(file)

        for value in runes.values():
            rune = models.Rune.from_json(value)
            Runes[rune.identifier] = rune
    
    Runes = dict(sorted(Runes.items(), key=lambda item: (item[1].profession, item[1].mod_type, item[1].rarity.value, item[1].name)))

    for rune in Runes.values():
        if rune.profession not in Runes_by_Profession:
            Runes_by_Profession[rune.profession] = {}

        Runes_by_Profession[rune.profession][rune.identifier] = rune

    for profession in Runes_by_Profession:
        Runes_by_Profession[profession] = dict(sorted(Runes_by_Profession[profession].items(), key=lambda item: (item[1].mod_type, item[1].rarity.value, item[1].name)))


@staticmethod
def SaveRunes():
    global Runes

    # Save runes to data/runes.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")    
    path = os.path.join(data_directory, "runes.json")


    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    with open(path, 'w', encoding='utf-8') as file:
        ConsoleLog(
            "LootEx", f"Saving runes ...", Console.MessageType.Debug)
        json.dump({rune.identifier: rune.to_json() for rune in Runes.values()}, file, indent=4, ensure_ascii=False)


@staticmethod
def LoadItems():
    global Items

    # Load items from data/items.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "items.json")

    ConsoleLog(
        "LootEx", f"Loading items...", Console.MessageType.Debug)

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as file:
            file.write('{}')

    with open(path, 'r', encoding='utf-8') as file:
        items = json.load(file)

        for value in items.values():
            item = models.Item.from_json(value)
            Items[item.model_id] = item

    account_file = os.path.join(
        file_directory, "data", "diffs", GLOBAL_CACHE.Player.GetAccountEmail(), "items.json")
    if os.path.exists(account_file):
        with open(account_file, 'r', encoding='utf-8') as file:
            items = json.load(file)

            for value in items.values():
                item = models.Item.from_json(value)
                if item.model_id not in Items:
                    Items[item.model_id] = item
                else:
                    # If the item already exists, we can update it
                    Items[item.model_id].update(item)

    Items = dict(sorted(Items.items(), key=lambda item: (item[1].name, item[1].model_id)))
    
    for item in Items.values():
        if item.item_type not in Items_By_Type:
            Items_By_Type[item.item_type] = {}

        Items_By_Type[item.item_type][item.model_id] = item


@staticmethod
def SaveItems(shared_file: bool = False, items: Optional[dict[int, models.Item]] = None):
    global Items

    # Save items to data/items.json
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")

    if not shared_file:
        account_name = GLOBAL_CACHE.Player.GetAccountEmail()
        data_directory = os.path.join(
            file_directory, "data", "diffs", account_name)

    path = os.path.join(data_directory, "items.json")

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not shared_file:
        if items is not None:
            items = dict(sorted(items.items(), key=lambda item: item[0]))

    else:
        items = dict(sorted(Items.items(), key=lambda item: item[0]))

    if items is None:
        return


    with open(path, 'w', encoding='utf-8') as file:
        ConsoleLog(
            "LootEx", f"Saving items ...", Console.MessageType.Debug)
        json.dump({item.model_id: item.to_json()
                  for item in items.values()}, file, indent=4, ensure_ascii=False)

@staticmethod
def MergeDiffItems():
    global Items

    file_directory = os.path.dirname(os.path.abspath(__file__))
    diffs_directory = os.path.join(file_directory, "data", "diffs")
    
    dirs = os.listdir(diffs_directory)
    for dir_name in dirs:
        file_path = os.path.join(diffs_directory, dir_name, "items.json")
        
        if os.path.exists(file_path):            
            with open(file_path, 'r', encoding='utf-8') as file:
                ConsoleLog(
                    "LootEx", f"Merging diff items from {file_path}...", Console.MessageType.Debug)
                
                items = json.load(file)

                for value in items.values():
                    item = models.Item.from_json(value)
                    if item.model_id not in Items:
                        Items[item.model_id] = item
                    else:
                        # If the item already exists, we can update it
                        Items[item.model_id].update(item)
        
            # Delete the diff file after merging
            os.remove(file_path)
    
    SaveItems(shared_file=True, items=Items)
    
    
    for dir_name in dirs:
        file_path = os.path.join(diffs_directory, dir_name, "weapon_mods.json")
        
        if os.path.exists(file_path):            
            with open(file_path, 'r', encoding='utf-8') as file:
                ConsoleLog(
                    "LootEx", f"Merging diff items from {file_path}...", Console.MessageType.Debug)
                
                mods = json.load(file)

                for value in mods.values():
                    mod = models.WeaponMod.from_json(value)
                    
                    if mod.identifier not in Weapon_Mods:
                        Weapon_Mods[mod.identifier] = mod
                    else:
                        # If the item already exists, we can update it
                        Weapon_Mods[mod.identifier].update(mod)
        
            # Delete the diff file after merging
            os.remove(file_path)
    
    SaveWeaponMods(shared_file=True, mods=Weapon_Mods)
    
    
@staticmethod
def GetScraperFile():
    file_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(file_directory, "data")
    path = os.path.join(data_directory, "scraper.json")

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    scrapedata = {}
    
    for item in Items.values():
        if item.contains_amount:
            continue
        
        if item.wiki_url is None or item.wiki_url == "" and ServerLanguage.English in item.names:
            item.wiki_url = f"https://wiki.guildwars.com/wiki/{item.names[ServerLanguage.English].replace(' ', '_')}"
            
        if item.wiki_url is None or item.wiki_url == "":
            continue
        
        if utility.Util.IsArmorType(item.item_type) or utility.Util.IsWeaponType(item.item_type):
            scrapedata[item.model_id] = {
            "ModelID": item.model_id,
            "Name": item.name,
            "WikiURL": item.wiki_url
        }
    
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(scrapedata, file, indent=4, ensure_ascii=False)

    return path