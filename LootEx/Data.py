from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Optional
from LootEx.enum import EnemyType, ModType
from Py4GWCoreLib import ModelID
from Py4GWCoreLib.enums import Attribute, DamageType
from Py4GWCoreLib.enums import ItemType, Rarity, Profession

class IntRange:
    def __init__(self, min: int = 0, max: Optional[int] = None):
        self.min : int = min
        self.max : int = max if max is not None else min

    def __str__(self) -> str:
        return f"{self.min} - {self.max}"

    def __repr__(self) -> str:
        return f"IntRange({self.min}, {self.max})"

    def __eq__(self, other):
        if isinstance(other, IntRange):
            return self.min == other.min and self.max == other.max
        return False

class Rune():
    def __init__(self, struct, name, profession: Profession, rarity: Rarity = Rarity.White):        
        self.Struct = struct
        self.Name = name
        if len(struct) != 8:
            raise ValueError("Invalid mod string length")

        b = bytes.fromhex(struct)
        self.Identifier = int.from_bytes(b[2:], byteorder='little')
        self.Arg1 = b[1]
        self.Arg2 = b[0]
        self.Args = (self.Arg1 << 8) | self.Arg2

        self.Profession : Profession = profession
        self.Rarity : Rarity = rarity
    
#TODO: Implement the mod types
Runes : dict[str, Rune] = (
    {
        # Warrior
        '240801F9' : Rune('240801F9', "Knight's Insignia", Profession.Warrior, Rarity.Blue),
        '24080208' : Rune('24080208', "Lieutenant's Insignia", Profession.Warrior, Rarity.Blue),
        '24080209' : Rune('24080209', "Stonefist Insignia", Profession.Warrior, Rarity.Blue),
        '240801FA' : Rune('240801FA', "Dreadnought Insignia", Profession.Warrior, Rarity.Blue),
        '240801FB' : Rune('240801FB', "Sentinel's Insignia", Profession.Warrior, Rarity.Blue),
        '240800FC' : Rune('240800FC', "Rune of Minor Absorption", Profession.Warrior, Rarity.Blue),
        '21E81501' : Rune('21E81501', "Rune of Minor Tactics", Profession.Warrior, Rarity.Blue),
        '21E81101' : Rune('21E81101', "Rune of Minor Strength", Profession.Warrior, Rarity.Blue),
        '21E81201' : Rune('21E81201', "Rune of Minor Axe Mastery", Profession.Warrior, Rarity.Blue),
        '21E81301' : Rune('21E81301', "Rune of Minor Hammer Mastery", Profession.Warrior, Rarity.Blue),
        '21E81401' : Rune('21E81401', "Rune of Minor Swordsmanship", Profession.Warrior, Rarity.Blue),
        '240800FD' : Rune('240800FD', "Rune of Major Absorption", Profession.Warrior, Rarity.Purple),
        '21E81502' : Rune('21E81502', "Rune of Major Tactics", Profession.Warrior, Rarity.Purple),
        '21E81102' : Rune('21E81102', "Rune of Major Strength", Profession.Warrior, Rarity.Purple),
        '21E81202' : Rune('21E81202', "Rune of Major Axe Mastery", Profession.Warrior, Rarity.Purple),
        '21E81302' : Rune('21E81302', "Rune of Major Hammer Mastery", Profession.Warrior, Rarity.Purple),
        '21E81402' : Rune('21E81402', "Rune of Major Swordsmanship", Profession.Warrior, Rarity.Purple),
        '240800FE' : Rune('240800FE', "Rune of Superior Absorption", Profession.Warrior, Rarity.Gold),
        '21E81503' : Rune('21E81503', "Rune of Superior Tactics", Profession.Warrior, Rarity.Gold),
        '21E81103' : Rune('21E81103', "Rune of Superior Strength", Profession.Warrior, Rarity.Gold),
        '21E81203' : Rune('21E81203', "Rune of Superior Axe Mastery", Profession.Warrior, Rarity.Gold),
        '21E81303' : Rune('21E81303', "Rune of Superior Hammer Mastery", Profession.Warrior, Rarity.Gold),
        '21E81403' : Rune('21E81403', "Rune of Superior Swordsmanship", Profession.Warrior, Rarity.Gold),

        # Ranger
        '240801FC' : Rune('240801FC', "Frostbound Insignia", Profession.Ranger, Rarity.Blue),
        '240801FE' : Rune('240801FE', "Pyrebound Insignia", Profession.Ranger, Rarity.Blue),
        '240801FF' : Rune('240801FF', "Stormbound Insignia", Profession.Ranger, Rarity.Blue),
        '24080201' : Rune('24080201', "Scout's Insignia", Profession.Ranger, Rarity.Blue),
        '240801FD' : Rune('240801FD', "Earthbound Insignia", Profession.Ranger, Rarity.Blue),
        '24080200' : Rune('24080200', "Beastmaster's Insignia", Profession.Ranger, Rarity.Blue),
        '21E81801' : Rune('21E81801', "Rune of Minor Wilderness Survival", Profession.Ranger, Rarity.Blue),
        '21E81701' : Rune('21E81701', "Rune of Minor Expertise", Profession.Ranger, Rarity.Blue),
        '21E81601' : Rune('21E81601', "Rune of Minor Beast Mastery", Profession.Ranger, Rarity.Blue),
        '21E81901' : Rune('21E81901', "Rune of Minor Marksmanship", Profession.Ranger, Rarity.Blue),
        '21E81802' : Rune('21E81802', "Rune of Major Wilderness Survival", Profession.Ranger, Rarity.Purple),
        '21E81702' : Rune('21E81702', "Rune of Major Expertise", Profession.Ranger, Rarity.Purple),
        '21E81602' : Rune('21E81602', "Rune of Major Beast Mastery", Profession.Ranger, Rarity.Purple),
        '21E81902' : Rune('21E81902', "Rune of Major Marksmanship", Profession.Ranger, Rarity.Purple),
        '21E81803' : Rune('21E81803', "Rune of Superior Wilderness Survival", Profession.Ranger, Rarity.Gold),
        '21E81703' : Rune('21E81703', "Rune of Superior Expertise", Profession.Ranger, Rarity.Gold),
        '21E81603' : Rune('21E81603', "Rune of Superior Beast Mastery", Profession.Ranger, Rarity.Gold),
        '21E81903' : Rune('21E81903', "Rune of Superior Marksmanship", Profession.Ranger, Rarity.Gold),

        # Monk
        '240801F6' : Rune('240801F6', "Wanderer's Insignia", Profession.Monk, Rarity.Blue),
        '240801F7' : Rune('240801F7', "Disciple's Insignia", Profession.Monk, Rarity.Blue),
        '240801F8' : Rune('240801F8', "Anchorite's Insignia", Profession.Monk, Rarity.Blue),
        '21E80D01' : Rune('21E80D01', "Rune of Minor Healing Prayers", Profession.Monk, Rarity.Blue),
        '21E80E01' : Rune('21E80E01', "Rune of Minor Smiting Prayers", Profession.Monk, Rarity.Blue),
        '21E80F01' : Rune('21E80F01', "Rune of Minor Protection Prayers", Profession.Monk, Rarity.Blue),
        '21E81001' : Rune('21E81001', "Rune of Minor Divine Favor", Profession.Monk, Rarity.Blue),
        '21E80D02' : Rune('21E80D02', "Rune of Major Healing Prayers", Profession.Monk, Rarity.Purple),
        '21E80E02' : Rune('21E80E02', "Rune of Major Smiting Prayers", Profession.Monk, Rarity.Purple),
        '21E80F02' : Rune('21E80F02', "Rune of Major Protection Prayers", Profession.Monk, Rarity.Purple),
        '21E81002' : Rune('21E81002', "Rune of Major Divine Favor", Profession.Monk, Rarity.Purple),
        '21E80D03' : Rune('21E80D03', "Rune of Superior Healing Prayers", Profession.Monk, Rarity.Gold),
        '21E80E03' : Rune('21E80E03', "Rune of Superior Smiting Prayers", Profession.Monk, Rarity.Gold),
        '21E80F03' : Rune('21E80F03', "Rune of Superior Protection Prayers", Profession.Monk, Rarity.Gold),
        '21E81003' : Rune('21E81003', "Rune of Superior Divine Favor", Profession.Monk, Rarity.Gold),

        # Necromancer
        '2408020A' : Rune('2408020A', "Bloodstained Insignia", Profession.Necromancer, Rarity.Blue),
        '240801EC' : Rune('240801EC', "Tormentor's Insignia", Profession.Necromancer, Rarity.Blue),
        '240801EE' : Rune('240801EE', "Bonelace Insignia", Profession.Necromancer, Rarity.Blue),
        '240801EF' : Rune('240801EF', "Minion Master's Insignia", Profession.Necromancer, Rarity.Blue),
        '240801F0' : Rune('240801F0', "Blighter's Insignia", Profession.Necromancer, Rarity.Blue),
        '240801ED' : Rune('240801ED', "Undertaker's Insignia", Profession.Necromancer, Rarity.Blue),
        '21E80401' : Rune('21E80401', "Rune of Minor Blood Magic", Profession.Necromancer, Rarity.Blue),
        '21E80501' : Rune('21E80501', "Rune of Minor Death Magic", Profession.Necromancer, Rarity.Blue),
        '21E80701' : Rune('21E80701', "Rune of Minor Curses", Profession.Necromancer, Rarity.Blue),
        '21E80601' : Rune('21E80601', "Rune of Minor Soul Reaping", Profession.Necromancer, Rarity.Blue),
        '21E80402' : Rune('21E80402', "Rune of Major Blood Magic", Profession.Necromancer, Rarity.Purple),
        '21E80502' : Rune('21E80502', "Rune of Major Death Magic", Profession.Necromancer, Rarity.Purple),
        '21E80702' : Rune('21E80702', "Rune of Major Curses", Profession.Necromancer, Rarity.Purple),
        '21E80602' : Rune('21E80602', "Rune of Major Soul Reaping", Profession.Necromancer, Rarity.Purple),
        '21E80403' : Rune('21E80403', "Rune of Superior Blood Magic", Profession.Necromancer, Rarity.Gold),
        '21E80503' : Rune('21E80503', "Rune of Superior Death Magic", Profession.Necromancer, Rarity.Gold),
        '21E80703' : Rune('21E80703', "Rune of Superior Curses", Profession.Necromancer, Rarity.Gold),
        '21E80603' : Rune('21E80603', "Rune of Superior Soul Reaping", Profession.Necromancer, Rarity.Gold),

        # Mesmer
        '240801E4' : Rune('240801E4', "Virtuoso's Insignia", Profession.Mesmer, Rarity.Blue),
        '240801E2' : Rune('240801E2', "Artificer's Insignia", Profession.Mesmer, Rarity.Blue),
        '240801E3' : Rune('240801E3', "Prodigy's Insignia", Profession.Mesmer, Rarity.Blue),
        '21E80001' : Rune('21E80001', "Rune of Minor Fast Casting", Profession.Mesmer, Rarity.Blue),
        '21E80201' : Rune('21E80201', "Rune of Minor Domination Magic", Profession.Mesmer, Rarity.Blue),
        '21E80101' : Rune('21E80101', "Rune of Minor Illusion Magic", Profession.Mesmer, Rarity.Blue),
        '21E80301' : Rune('21E80301', "Rune of Minor Inspiration Magic", Profession.Mesmer, Rarity.Blue),
        '21E80002' : Rune('21E80002', "Rune of Major Fast Casting", Profession.Mesmer, Rarity.Purple),
        '21E80202' : Rune('21E80202', "Rune of Major Domination Magic", Profession.Mesmer, Rarity.Purple),
        '21E80102' : Rune('21E80102', "Rune of Major Illusion Magic", Profession.Mesmer, Rarity.Purple),
        '21E80302' : Rune('21E80302', "Rune of Major Inspiration Magic", Profession.Mesmer, Rarity.Purple),
        '21E80003' : Rune('21E80003', "Rune of Superior Fast Casting", Profession.Mesmer, Rarity.Gold),
        '21E80203' : Rune('21E80203', "Rune of Superior Domination Magic", Profession.Mesmer, Rarity.Gold),
        '21E80103' : Rune('21E80103', "Rune of Superior Illusion Magic", Profession.Mesmer, Rarity.Gold),
        '21E80303' : Rune('21E80303', "Rune of Superior Inspiration Magic", Profession.Mesmer, Rarity.Gold),

        # Elementalist
        '240801F2' : Rune('240801F2', "Hydromancer Insignia", Profession.Elementalist, Rarity.Blue),
        '240801F3' : Rune('240801F3', "Geomancer Insignia", Profession.Elementalist, Rarity.Blue),
        '240801F4' : Rune('240801F4', "Pyromancer Insignia", Profession.Elementalist, Rarity.Blue),
        '240801F5' : Rune('240801F5', "Aeromancer Insignia", Profession.Elementalist, Rarity.Blue),
        '240801F1' : Rune('240801F1', "Prismatic Insignia", Profession.Elementalist, Rarity.Blue),
        '21E80C01' : Rune('21E80C01', "Rune of Minor Energy Storage", Profession.Elementalist, Rarity.Blue),
        '21E80A01' : Rune('21E80A01', "Rune of Minor Fire Magic", Profession.Elementalist, Rarity.Blue),
        '21E80801' : Rune('21E80801', "Rune of Minor Air Magic", Profession.Elementalist, Rarity.Blue),
        '21E80901' : Rune('21E80901', "Rune of Minor Earth Magic", Profession.Elementalist, Rarity.Blue),
        '21E80B01' : Rune('21E80B01', "Rune of Minor Water Magic", Profession.Elementalist, Rarity.Blue),
        '21E80C02' : Rune('21E80C02', "Rune of Major Energy Storage", Profession.Elementalist, Rarity.Purple),
        '21E80A02' : Rune('21E80A02', "Rune of Major Fire Magic", Profession.Elementalist, Rarity.Purple),
        '21E80802' : Rune('21E80802', "Rune of Major Air Magic", Profession.Elementalist, Rarity.Purple),
        '21E80902' : Rune('21E80902', "Rune of Major Earth Magic", Profession.Elementalist, Rarity.Purple),
        '21E80B02' : Rune('21E80B02', "Rune of Major Water Magic", Profession.Elementalist, Rarity.Purple),
        '21E80C03' : Rune('21E80C03', "Rune of Superior Energy Storage", Profession.Elementalist, Rarity.Gold),
        '21E80A03' : Rune('21E80A03', "Rune of Superior Fire Magic", Profession.Elementalist, Rarity.Gold),
        '21E80803' : Rune('21E80803', "Rune of Superior Air Magic", Profession.Elementalist, Rarity.Gold),
        '21E80903' : Rune('21E80903', "Rune of Superior Earth Magic", Profession.Elementalist, Rarity.Gold),
        '21E80B03' : Rune('21E80B03', "Rune of Superior Water Magic", Profession.Elementalist, Rarity.Gold),

        # Assassin
        '240801DE' : Rune('240801DE', "Vanguard's Insignia", Profession.Assassin, Rarity.Blue),
        '240801DF' : Rune('240801DF', "Infiltrator's Insignia", Profession.Assassin, Rarity.Blue),
        '240801E0' : Rune('240801E0', "Saboteur's Insignia", Profession.Assassin, Rarity.Blue),
        '240801E1' : Rune('240801E1', "Nightstalker's Insignia", Profession.Assassin, Rarity.Blue),
        '21E82301' : Rune('21E82301', "Rune of Minor Critical Strikes", Profession.Assassin, Rarity.Blue),
        '21E81D01' : Rune('21E81D01', "Rune of Minor Dagger Mastery", Profession.Assassin, Rarity.Blue),
        '21E81E01' : Rune('21E81E01', "Rune of Minor Deadly Arts", Profession.Assassin, Rarity.Blue),
        '21E81F01' : Rune('21E81F01', "Rune of Minor Shadow Arts", Profession.Assassin, Rarity.Blue),
        '21E82302' : Rune('21E82302', "Rune of Major Critical Strikes", Profession.Assassin, Rarity.Purple),
        '21E81D02' : Rune('21E81D02', "Rune of Major Dagger Mastery", Profession.Assassin, Rarity.Purple),
        '21E81E02' : Rune('21E81E02', "Rune of Major Deadly Arts", Profession.Assassin, Rarity.Purple),
        '21E81F02' : Rune('21E81F02', "Rune of Major Shadow Arts", Profession.Assassin, Rarity.Purple),
        '21E82303' : Rune('21E82303', "Rune of Superior Critical Strikes", Profession.Assassin, Rarity.Gold),
        '21E81D03' : Rune('21E81D03', "Rune of Superior Dagger Mastery", Profession.Assassin, Rarity.Gold),
        '21E81E03' : Rune('21E81E03', "Rune of Superior Deadly Arts", Profession.Assassin, Rarity.Gold),
        '21E81F03' : Rune('21E81F03', "Rune of Superior Shadow Arts", Profession.Assassin, Rarity.Gold),

        # Ritualist
        '24080204' : Rune('24080204', "Shaman's Insignia", Profession.Ritualist, Rarity.Blue),
        '24080205' : Rune('24080205', "Ghost Forge Insignia", Profession.Ritualist, Rarity.Blue),
        '24080206' : Rune('24080206', "Mystic's Insignia", Profession.Ritualist, Rarity.Blue),
        '21E82201' : Rune('21E82201', "Rune of Minor Channeling Magic", Profession.Ritualist, Rarity.Blue),
        '21E82101' : Rune('21E82101', "Rune of Minor Restoration Magic", Profession.Ritualist, Rarity.Blue),
        '21E82001' : Rune('21E82001', "Rune of Minor Communing", Profession.Ritualist, Rarity.Blue),
        '21E82401' : Rune('21E82401', "Rune of Minor Spawning Power", Profession.Ritualist, Rarity.Blue),
        '21E82202' : Rune('21E82202', "Rune of Major Channeling Magic", Profession.Ritualist, Rarity.Purple),
        '21E82102' : Rune('21E82102', "Rune of Major Restoration Magic", Profession.Ritualist, Rarity.Purple),
        '21E82002' : Rune('21E82002', "Rune of Major Communing", Profession.Ritualist, Rarity.Purple),
        '21E82402' : Rune('21E82402', "Rune of Major Spawning Power", Profession.Ritualist, Rarity.Purple),
        '21E82203' : Rune('21E82203', "Rune of Superior Channeling Magic", Profession.Ritualist, Rarity.Gold),
        '21E82103' : Rune('21E82103', "Rune of Superior Restoration Magic", Profession.Ritualist, Rarity.Gold),
        '21E82003' : Rune('21E82003', "Rune of Superior Communing", Profession.Ritualist, Rarity.Gold),
        '21E82403' : Rune('21E82403', "Rune of Superior Spawning Power", Profession.Ritualist, Rarity.Gold),

        # Dervish
        '24080202' : Rune('24080202', "Windwalker Insignia", Profession.Dervish, Rarity.Blue),
        '24080203' : Rune('24080203', "Forsaken Insignia", Profession.Dervish, Rarity.Blue),
        '21E82C01' : Rune('21E82C01', "Rune of Minor Mysticism", Profession.Dervish, Rarity.Blue),
        '21E82B01' : Rune('21E82B01', "Rune of Minor Earth Prayers", Profession.Dervish, Rarity.Blue),
        '21E82901' : Rune('21E82901', "Rune of Minor Scythe Mastery", Profession.Dervish, Rarity.Blue),
        '21E82A01' : Rune('21E82A01', "Rune of Minor Wind Prayers", Profession.Dervish, Rarity.Blue),
        '21E82C02' : Rune('21E82C02', "Rune of Major Mysticism", Profession.Dervish, Rarity.Purple),
        '21E82B02' : Rune('21E82B02', "Rune of Major Earth Prayers", Profession.Dervish, Rarity.Purple),
        '21E82902' : Rune('21E82902', "Rune of Major Scythe Mastery", Profession.Dervish, Rarity.Purple),
        '21E82A02' : Rune('21E82A02', "Rune of Major Wind Prayers", Profession.Dervish, Rarity.Purple),
        '21E82C03' : Rune('21E82C03', "Rune of Superior Mysticism", Profession.Dervish, Rarity.Gold),
        '21E82B03' : Rune('21E82B03', "Rune of Superior Earth Prayers", Profession.Dervish, Rarity.Gold),
        '21E82903' : Rune('21E82903', "Rune of Superior Scythe Mastery", Profession.Dervish, Rarity.Gold),
        '21E82A03' : Rune('21E82A03', "Rune of Superior Wind Prayers", Profession.Dervish, Rarity.Gold),

        # Paragon
        '24080207' : Rune('24080207', "Centurion's Insignia", Profession.Paragon, Rarity.Blue),
        '21E82801' : Rune('21E82801', "Rune of Minor Leadership", Profession.Paragon, Rarity.Blue),
        '21E82701' : Rune('21E82701', "Rune of Minor Motivation", Profession.Paragon, Rarity.Blue),
        '21E82601' : Rune('21E82601', "Rune of Minor Command", Profession.Paragon, Rarity.Blue),
        '21E82501' : Rune('21E82501', "Rune of Minor Spear Mastery", Profession.Paragon, Rarity.Blue),
        '21E82802' : Rune('21E82802', "Rune of Major Leadership", Profession.Paragon, Rarity.Purple),
        '21E82702' : Rune('21E82702', "Rune of Major Motivation", Profession.Paragon, Rarity.Purple),
        '21E82602' : Rune('21E82602', "Rune of Major Command", Profession.Paragon, Rarity.Purple),
        '21E82502' : Rune('21E82502', "Rune of Major Spear Mastery", Profession.Paragon, Rarity.Purple),
        '21E82803' : Rune('21E82803', "Rune of Superior Leadership", Profession.Paragon, Rarity.Gold),
        '21E82703' : Rune('21E82703', "Rune of Superior Motivation", Profession.Paragon, Rarity.Gold),
        '21E82603' : Rune('21E82603', "Rune of Superior Command", Profession.Paragon, Rarity.Gold),
        '21E82503' : Rune('21E82503', "Rune of Superior Spear Mastery", Profession.Paragon, Rarity.Gold),

        # NoProfession
        '240801E6' : Rune('240801E6', "Survivor Insignia", Profession._None, Rarity.Blue),
        '240801E5' : Rune('240801E5', "Radiant Insignia", Profession._None, Rarity.Blue),
        '240801E7' : Rune('240801E7', "Stalwart Insignia", Profession._None, Rarity.Blue),
        '240801E8' : Rune('240801E8', "Brawler's Insignia", Profession._None, Rarity.Blue),
        '240801E9' : Rune('240801E9', "Blessed Insignia", Profession._None, Rarity.Blue),
        '240801EA' : Rune('240801EA', "Herald's Insignia", Profession._None, Rarity.Blue),
        '240801EB' : Rune('240801EB', "Sentry's Insignia", Profession._None, Rarity.Blue),
        '24080211' : Rune('24080211', "Rune of Attunement", Profession._None,Rarity.Purple),
        '24080212' : Rune('24080212', "Rune of Vitae", Profession._None,Rarity.Blue),
        '24080213' : Rune('24080213', "Rune of Recovery", Profession._None,Rarity.Purple),
        '24080214' : Rune('24080214', "Rune of Restoration", Profession._None,Rarity.Purple),
        '24080215' : Rune('24080215', "Rune of Clarity", Profession._None,Rarity.Purple),
        '24080216' : Rune('24080216', "Rune of Purity", Profession._None,Rarity.Purple),
        '240800FF' : Rune('240800FF', "Rune of Minor Vigor", Profession._None, Rarity.Blue),
        '240800C2' : Rune('240800C2', "Rune of Minor Vigor", Profession._None, Rarity.Blue),
        '24080100' : Rune('24080100', "Rune of Major Vigor", Profession._None, Rarity.Purple),     
        '24080101' : Rune('24080101', "Rune of Superior Vigor", Profession._None, Rarity.Gold),       
})

RunesByProfession : dict[Profession, list[Rune]] = {}
for rune in Runes.values():
    if rune.Profession not in RunesByProfession:
        RunesByProfession[rune.Profession] = []
    RunesByProfession[rune.Profession].append(rune)
    
for profession in RunesByProfession:
    RunesByProfession[profession].sort(key=lambda x: x.Rarity.value)


DamageRanges = {
    ItemType.Axe: {
        0 :  IntRange(6, 12),
        1 :  IntRange(6, 12),
        2 :  IntRange(6, 14),
        3 :  IntRange(6, 17),
        4 :  IntRange(6, 19),
        5 :  IntRange(6, 22),
        6 :  IntRange(6, 24),
        7 :  IntRange(6, 25),
        8 :  IntRange(6, 27),
        9 :  IntRange(6, 28),                
    },
    ItemType.Bow: {
        0 :  IntRange(9, 13),
        1 :  IntRange(9, 14),
        2 :  IntRange(10, 16),
        3 :  IntRange(11, 18),
        4 :  IntRange(12, 20),
        5 :  IntRange(13, 22),
        6 :  IntRange(14, 24),
        7 :  IntRange(14, 25),
        8 :  IntRange(14, 27),
        9 :  IntRange(14, 28),                
    },
    
    ItemType.Daggers: {
        0 :  IntRange(4, 8),
        1 :  IntRange(4, 8),
        2 :  IntRange(5, 9),
        3 :  IntRange(5, 11),
        4 :  IntRange(6, 12),
        5 :  IntRange(6, 13),
        6 :  IntRange(7, 14),
        7 :  IntRange(7, 15),
        8 :  IntRange(7, 16),
        9 :  IntRange(7, 17),                
    },
    
    ItemType.Offhand: {
        0 :  IntRange(6),
        1 :  IntRange(6),
        2 :  IntRange(7),
        3 :  IntRange(8),
        4 :  IntRange(9),
        5 :  IntRange(10),
        6 :  IntRange(11),
        7 :  IntRange(11),
        8 :  IntRange(12),
        9 :  IntRange(12),                
    },    
    
    ItemType.Hammer: {
        0 :  IntRange(11, 15),
        1 :  IntRange(11, 16),
        2 :  IntRange(12, 19),
        3 :  IntRange(14, 22),
        4 :  IntRange(15, 24),
        5 :  IntRange(16, 28),
        6 :  IntRange(17, 30),
        7 :  IntRange(18, 32),
        8 :  IntRange(18, 34),
        9 :  IntRange(19, 35),                
    },
    
    ItemType.Scythe: {
        0 :  IntRange(8, 17),
        1 :  IntRange(8, 18),
        2 :  IntRange(9, 21),
        3 :  IntRange(10, 24),
        4 :  IntRange(10, 28),
        5 :  IntRange(10, 32),
        6 :  IntRange(10, 35),
        7 :  IntRange(10, 36),
        8 :  IntRange(9, 40),
        9 :  IntRange(9, 41),          
    },
    
    ItemType.Shield: {
        0 :  IntRange(8),
        1 :  IntRange(9),
        2 :  IntRange(10),
        3 :  IntRange(11),
        4 :  IntRange(12),
        5 :  IntRange(13),
        6 :  IntRange(14),
        7 :  IntRange(15),
        8 :  IntRange(16),
        9 :  IntRange(16),
    },
    
    ItemType.Spear: {
        0 :  IntRange(8, 12),
        1 :  IntRange(8, 13),
        2 :  IntRange(10, 15),
        3 :  IntRange(11, 17),
        4 :  IntRange(11, 19),
        5 :  IntRange(12, 21),
        6 :  IntRange(13, 23),
        7 :  IntRange(13, 25),
        8 :  IntRange(14, 26),
        9 :  IntRange(14, 27),         
    },

   ItemType.Staff: {
        0 :  IntRange(7, 11),
        1 :  IntRange(7, 11),
        2 :  IntRange(8, 13),
        3 :  IntRange(9, 14),
        4 :  IntRange(10, 16),
        5 :  IntRange(10, 18),
        6 :  IntRange(10, 19),
        7 :  IntRange(11, 20),
        8 :  IntRange(11, 21),
        9 :  IntRange(11, 22),                             
    },

    ItemType.Sword: {
        0 :  IntRange(8, 10),
        1 :  IntRange(8, 11),
        2 :  IntRange(9, 13),
        3 :  IntRange(11, 14),
        4 :  IntRange(12, 16),
        5 :  IntRange(13, 18),
        6 :  IntRange(14, 19),
        7 :  IntRange(14, 20),
        8 :  IntRange(15, 22),
        9 :  IntRange(15, 22),                
    },

    ItemType.Wand: {
        0 :  IntRange(7, 11),
        1 :  IntRange(7, 11),
        2 :  IntRange(8, 13),
        3 :  IntRange(9, 14),
        4 :  IntRange(10, 16),
        5 :  IntRange(10, 18),
        6 :  IntRange(11, 19),
        7 :  IntRange(11, 20),
        8 :  IntRange(11, 21),
        9 :  IntRange(11, 22),                               
    },
}

CasterAttributes = [
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
ShieldAttributes = [
    Attribute.Strength,
    Attribute.Tactics,
    Attribute.Command,
    Attribute.Motivation,
    Attribute.Leadership,
]
AttributeRequirements = {    
    ItemType.Axe: [Attribute.AxeMastery],
    ItemType.Bow: [Attribute.Marksmanship],
    ItemType.Daggers: [Attribute.DaggerMastery],
    ItemType.Hammer: [Attribute.HammerMastery],
    ItemType.Scythe: [Attribute.ScytheMastery],
    ItemType.Shield: ShieldAttributes,
    ItemType.Spear: [Attribute.SpearMastery],
    ItemType.Sword: [Attribute.Swordsmanship],
    ItemType.Offhand: CasterAttributes,
    ItemType.Wand: CasterAttributes,
    ItemType.Staff: CasterAttributes,
}

class WeaponMod():
    def __init__(self, struct, name, modType=ModType.None_):        
        self.Struct = struct
        self.name_format = name

        b = bytes.fromhex(struct)
        self.Identifier = int.from_bytes(b[2:], byteorder='little')
        self.Arg1 = b[1]
        self.Arg2 = b[0]
        self.Args = (self.Arg1 << 8) | self.Arg2
        self.ModType = modType
        
    @property
    def Name(self) -> str:
        # 20% Chance for +1 of Attribute
        if(self.Identifier == 9240):
            attributeName = Attribute(self.Arg1).name
            attributeName = ''.join([' ' + i if i.isupper() else i for i in attributeName]).strip()

            return self.name_format.format(
            arg1=attributeName,
            arg2=self.Arg2,
        )

        # Change Damagetype
        if(self.Identifier == 9400):
            damageType = DamageType(self.Arg1).name
            damageType = ''.join([' ' + i if i.isupper() else i for i in damageType]).strip()

            return self.name_format.format(
                arg1=damageType,
                arg2=self.Arg2,
            )
        
        # Armor versus EnemyType
        if(self.Identifier == 8520):
            enemyType = EnemyType(self.Arg1).name
            enemyType = ''.join([' ' + i if i.isupper() else i for i in enemyType]).strip()

            return self.name_format.format(
                arg1=enemyType,
                arg2=self.Arg2,
            )
        
        # Damage versus EnemyType
        if(self.Identifier == 32896):
            enemyType = EnemyType(self.Arg1).name
            enemyType = ''.join([' ' + i if i.isupper() else i for i in enemyType]).strip()

            return self.name_format.format(
                arg1=enemyType,
                arg2=self.Arg2,
            )

        # Armor versus DamageType
        if(self.Identifier == 41240):
            damageType = DamageType(self.Arg1).name
            damageType = ''.join([' ' + i if i.isupper() else i for i in damageType]).strip()

            return self.name_format.format(
                arg1=damageType,
                arg2=self.Arg2,
            )

        # +5 Profession Primary
        if(self.Identifier == 10408):
            damageType = Attribute(self.Arg1).name
            damageType = ''.join([' ' + i if i.isupper() else i for i in damageType]).strip()

            return self.name_format.format(
                arg1=damageType,
                arg2=self.Arg2,
            )

        return self.name_format.format(
            arg1=self.Arg1,
            arg2=self.Arg2,
        )


#TODO: Implement the mod types
WeaponMods : dict[str, WeaponMod] = (
    {
        '1400B822' : WeaponMod('1400B822', "+{arg2}% Enchantment Duration"),
        '001E4823' : WeaponMod('001E4823', "+{arg1} Health"),
        '002D6823' : WeaponMod('002D6823', "+{arg1} Health while Enchanted"),
        '002D8823' : WeaponMod('002D8823', "+{arg1} Health while in a Stance"),
        '003C7823' : WeaponMod('003C7823', "+{arg1} Health while Hexed"),
        '07002821' : WeaponMod('07002821', "+{arg2} Armor vs Elemental"),
        '07005821' : WeaponMod('07005821', "+{arg2} Armor vs Physical"),
        '14081824' : WeaponMod('14081824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '0A0018A1' : WeaponMod('0A0018A1', "Armor +{arg2} (vs Blunt damage)"),
        '0A0318A1' : WeaponMod('0A0318A1', "Armor +{arg2} (vs Cold damage)"),
        '0A0B18A1' : WeaponMod('0A0B18A1', "Armor +{arg2} (vs Earth damage)"),
        '0A0518A1' : WeaponMod('0A0518A1', "Armor +{arg2} (vs Fire damage)"),
        '0A0418A1' : WeaponMod('0A0418A1', "Armor +{arg2} (vs Lightning damage)"),
        '0A0118A1' : WeaponMod('0A0118A1', "Armor +{arg2} (vs Piercing damage)"),
        '0A0218A1' : WeaponMod('0A0218A1', "Armor +{arg2} (vs Slashing damage)"),
        '0A32B821' : WeaponMod('0A32B821', "Armor +{arg2} (while Health is below +50%)"),
        '0A00C821' : WeaponMod('0A00C821', "Armor +{arg2} (while Hexed)"),
        '0A014821' : WeaponMod('0A014821', "Armor +{arg2} vs Charr"),
        '0A084821' : WeaponMod('0A084821', "Armor +{arg2} vs Demons"),
        '0A094821' : WeaponMod('0A094821', "Armor +{arg2} vs Dragons"),
        '0A064821' : WeaponMod('0A064821', "Armor +{arg2} vs Dwarves"),
        '0A054821' : WeaponMod('0A054821', "Armor +{arg2} vs Giants"),
        '0A0A4821' : WeaponMod('0A0A4821', "Armor +{arg2} vs Ogres"),
        '0A034821' : WeaponMod('0A034821', "Armor +{arg2} vs Plants"),
        '0A044821' : WeaponMod('0A044821', "Armor +{arg2} vs Skeletons"),
        '0A074821' : WeaponMod('0A074821', "Armor +{arg2} vs Tengu"),
        '0A024821' : WeaponMod('0A024821', "Armor +{arg2} vs Trolls"),
        '0A004821' : WeaponMod('0A004821', "Armor +{arg2} vs Undead"),
        '05000821' : WeaponMod('05000821', "Armor +{arg2}"),
        '05002821' : WeaponMod('05002821', "Armor +{arg2} (vs Elemental damage)"),
        '05005821' : WeaponMod('05005821', "Armor +{arg2} (vs Physical damage)"),
        '05007821' : WeaponMod('05007821', "Armor +{arg2} (while attacking)"),
        '05008821' : WeaponMod('05008821', "Armor +{arg2} (while casting)"),
        '05009821' : WeaponMod('05009821', "Armor +{arg2} (while Enchanted)"),
        '0532A821' : WeaponMod('0532A821', "Armor +{arg2} (while Health is above +{arg1}%)"),
        '14121824' : WeaponMod('14121824', "{arg1} +1 ({arg2}% chance while using skills)"),
        'DE016824' : WeaponMod('DE016824', "Barbed 33% Bleed"),
        '14041824' : WeaponMod('14041824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '0003B824' : WeaponMod('0003B824', "Changes Damage to {arg1}"),
        '000BB824' : WeaponMod('000BB824', "Changes Damage to {arg1}"),
        '0005B824' : WeaponMod('0005B824', "Changes Damage to {arg1}"),
        '0004B824' : WeaponMod('0004B824', "Changes Damage to {arg1}"),
        '14221824' : WeaponMod('14221824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14201824' : WeaponMod('14201824', "{arg1} +1 ({arg2}% chance while using skills)"),
        'E1016824' : WeaponMod('E1016824', "Crippling 33% Cripple"),
        'E2016824' : WeaponMod('E2016824', "Cruel 33% Deep Wound"),
        '14071824' : WeaponMod('14071824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '141D1824' : WeaponMod('141D1824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '0F003822' : WeaponMod('0F003822', "Damage +{arg2}%"),
        '0F005822' : WeaponMod('0F005822', "Damage +{arg2}% (vs Hexed Foes)"),
        '0F006822' : WeaponMod('0F006822', "Damage +{arg2}% (while Enchanted)"),
        '0F327822' : WeaponMod('0F327822', "Damage +{arg2}% (while Health is above +{arg1}%)"),
        '0F00A822' : WeaponMod('0F00A822', "Damage +{arg2}% (while in a Stance)"),
        '0A001820' : WeaponMod('0A001820', "Damage +15% And Armor -{arg2} (while attacking)"),
        # TODO: Check if this is correct
        # '0500B820' : WeaponMod('0500B820', "Damage +{arg1}% And Energy -5"),
        '14328822' : WeaponMod('14328822', "Damage {arg2}% (while Health is below +{arg1}%)"),
        '14009822' : WeaponMod('14009822', "Damage {arg2}% (while Hexed)"),
        '00018080' : WeaponMod('00018080', "Damge 20% (vs {arg1})"),
        '00088080' : WeaponMod('00088080', "Damge 20% (vs {arg1})"),
        '00098080' : WeaponMod('00098080', "Damge 20% (vs {arg1})"),
        '00068080' : WeaponMod('00068080', "Damge 20% (vs {arg1})"),
        '00058080' : WeaponMod('00058080', "Damge 20% (vs {arg1})"),
        '000A8080' : WeaponMod('000A8080', "Damge 20% (vs {arg1})"),
        '00038080' : WeaponMod('00038080', "Damge 20% (vs {arg1})"),
        '00048080' : WeaponMod('00048080', "Damge 20% (vs {arg1})"),
        '00078080' : WeaponMod('00078080', "Damge 20% (vs {arg1})"),
        '00028080' : WeaponMod('00028080', "Damge 20% (vs {arg1})"),
        '00008080' : WeaponMod('00008080', "Damge 20% (vs {arg1})"),
        '14051824' : WeaponMod('14051824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14101824' : WeaponMod('14101824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14021824' : WeaponMod('14021824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14091824' : WeaponMod('14091824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '0F00D822' : WeaponMod('0F00D822', "Energy +{arg2}"),
        '0500D822' : WeaponMod('0500D822', "Energy +{arg2}"),
        '0500F822' : WeaponMod('0500F822', "Energy +{arg2} (while Enchanted)"),
        '05320823' : WeaponMod('05320823', "Energy +{arg2} (while health is above +{arg1}%)"),
        '07321823' : WeaponMod('07321823', "Energy +{arg2} (while Health is below +{arg1}%)"),
        '07002823' : WeaponMod('07002823', "Energy +{arg2} (while hexed)"),
        # TODO: Check if this is correct
        # '0500B820' : WeaponMod('0500B820', "Energy -5"),
        '0100C820' : WeaponMod('0100C820', "Energy regeneration -{arg2}"),
        '140A1824' : WeaponMod('140A1824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '0A00B823' : WeaponMod('0A00B823', "Furious +{arg2}% double Adrenalin"),
        '000A0822' : WeaponMod('000A0822', "Halves casting time of spells (Chance: +{arg1}%)"),
        '00140828' : WeaponMod('00140828', "Halves casting time of spells of item's attribute (Chance: {arg1}%)"),
        '000AA823' : WeaponMod('000AA823', "Halves skill recharge of spells (Chance: +{arg1}%)"),
        '00142828' : WeaponMod('00142828', "Halves skill recharge of spells (Chance: {arg1}%)"),
        '14131824' : WeaponMod('14131824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '140D1824' : WeaponMod('140D1824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '1400D820' : WeaponMod('1400D820', "Health -{arg2}"),
        '0100E820' : WeaponMod('0100E820', "Health regeneration -{arg2}"),
        # TODO: Check if this is correct
        # 'E601824' : WeaponMod('E601824', "Heavy 33% Weakness"),
        '32000826' : WeaponMod('32000826', "Highly salvageable"),
        '14011824' : WeaponMod('14011824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '3200F805' : WeaponMod('3200F805', "Improved sale value"),
        '14031824' : WeaponMod('14031824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '00143828' : WeaponMod('00143828', "Item's attribute +1 (Chance: {arg1}%)"),
        '14191824' : WeaponMod('14191824', "{arg1} +1 ({arg2}% chance while using skills)"),
        'E4016824' : WeaponMod('E4016824', "Poisonous 33% Poison"),
        '140F1824' : WeaponMod('140F1824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '02008820' : WeaponMod('02008820', "Received physical damage -{arg2} (while Enchanted)"),
        '0200A820' : WeaponMod('0200A820', "Received physical damage -{arg2} (while in a Stance)"),
        '03009820' : WeaponMod('03009820', "Received physical damage -{arg2} (while Heed)"),
        '05147820' : WeaponMod('05147820', "Received physical damage -{arg2} (Chance: 20%)"),
        '00005828' : WeaponMod('00005828', "Reduces Bleeding duration on you by 20%"),
        '00015828' : WeaponMod('00015828', "Reduces Blind duration on you by 20%"),
        '00035828' : WeaponMod('00035828', "Reduces Crippled duration on you by 20%"),
        '00075828' : WeaponMod('00075828', "Reduces Dazed duration on you by 20%"),
        '00045828' : WeaponMod('00045828', "Reduces Deep Wound duration on you by 20%"),
        '00055828' : WeaponMod('00055828', "Reduces Disease duration on you by 20% ; Inscribable"),
        'E3017824' : WeaponMod('E3017824', "Reduces Disease duration on you by 20% ; OS shield/staff/offhand"),
        '00065828' : WeaponMod('00065828', "Reduces Poison duration on you by 20%"),
        '00085828' : WeaponMod('00085828', "Reduces Weakness duration on you by 20%"),
        '14211824' : WeaponMod('14211824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14291824' : WeaponMod('14291824', "{arg1} +1 ({arg2}% chance while using skills)"),
        'E5016824' : WeaponMod('E5016824', "Silencing 33% Dazed"),
        '140E1824' : WeaponMod('140E1824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14061824' : WeaponMod('14061824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14241824' : WeaponMod('14241824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '14251824' : WeaponMod('14251824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '1414F823' : WeaponMod('1414F823', "Sundering 20% Armor Penetration"),
        '14141824' : WeaponMod('14141824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '00032825' : WeaponMod('00032825', "Vampiric +{arg1}/-1"),
        '00052825' : WeaponMod('00052825', "Vampiric +{arg1}/-1"),
        '140B1824' : WeaponMod('140B1824', "{arg1} +1 ({arg2}% chance while using skills)"),
        '01001825' : WeaponMod('01001825', "Zeal +{arg2}/-1"),
        '0511A828' : WeaponMod('0511A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0517A828' : WeaponMod('0517A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0506A828' : WeaponMod('0506A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0500A828' : WeaponMod('0500A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '050CA828' : WeaponMod('050CA828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0510A828' : WeaponMod('0510A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0524A828' : WeaponMod('0524A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0523A828' : WeaponMod('0523A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '0528A828' : WeaponMod('0528A828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
        '052CA828' : WeaponMod('052CA828', "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"),
    })

#Sort the Weapon Mods by their Name
WeaponMods = dict(sorted(WeaponMods.items(), key=lambda item: item[1].Name))

def GetWeaponModName(struct : str) -> str:
    if struct in WeaponMods:
        return WeaponMods[struct].Name
    else:
        return "Unknown Weapon Mod"

@dataclass
class Item():        
    model_id : int
    name : str
    item_type : ItemType
    drop_info : str = ""
    attributes: List[Attribute] = field(default_factory=list)
    wiki_url : str = ""
    materials : List[int] = field(default_factory=list)
    rare_materials : List[int] = field(default_factory=list)
    is_nick_item : bool = False
    
    def to_json(self) -> dict:
        return {
            "ModelID" : self.model_id,
            "Name" : self.name,
            "ItemType" : self.item_type.name,
            "DropInfo" : self.drop_info,
            "Attributes" : [attribute.name for attribute in self.attributes],
            "WikiURL" : self.wiki_url,
            "Materials" : self.materials,
            "RareMaterials" : self.rare_materials,
            "IsNickItem" : self.is_nick_item,
        }
        
    
    def from_json(self, json : dict):
        self.model_id = json["ModelID"]
        self.name = json["Name"]
        self.item_type = ItemType[json["ItemType"]]
        self.drop_info = json["DropInfo"]
        self.attributes = [Attribute[attribute] for attribute in json["Attributes"]]
        self.wiki_url = json["WikiURL"]
        self.materials = json["Materials"]
        self.rare_materials = json["RareMaterials"]
        self.is_nick_item = json["IsNickItem"]

Items : dict[int, Item] = {
    ModelID.Abnormal_Seed : Item(
        model_id     =   ModelID.Abnormal_Seed, 
        name        =   "Abnormal Seed", 
        item_type    =   ItemType.Unknown, 
        drop_info    =  "Dropped by Ancient Oakhearts, Entangling Roots, Large- and Spined Aloe, Oakhearts, Reed Stalkers in the Kryta."),

    ModelID.Aged_Dwarven_Ale : Item(
        model_id     =   ModelID.Aged_Dwarven_Ale,
        name        =   "Aged Dwarven Ale",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Irontoe's Chest"),

    ModelID.Alpine_Seed : Item(
        model_id     =   ModelID.Alpine_Seed, 
        name        =   "Alpine Seed", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Ancient Oakhearts, Entangling Roots, Large- and Spined Aloe, Oakhearts, Reed Stalkers in the Kryta"),

    ModelID.Amber_Chunk : Item(
        model_id     =   ModelID.Amber_Chunk, 
        name        =   "Amber Chunk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Amphibian_Tongue : Item(
        model_id     =   ModelID.Amphibian_Tongue, 
        name        =   "Amphibian Tongue", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Heket enemies in the Maguuma Jungle"),

    ModelID.Ancient_Elonian_Key : Item(
        model_id     =   ModelID.Ancient_Elonian_Key, 
        name        =   "Ancient Elonian Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes The Desolation"),

    ModelID.Ancient_Eye : Item(
        model_id     =   ModelID.Ancient_Eye, 
        name        =   "Ancient Eye", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "MODELID NOT AQUIRED!!! Dropped by Wind Riders in Maguuma Jungle"),

    ModelID.Ancient_Kappa_Shell : Item(
        model_id     =   ModelID.Ancient_Kappa_Shell, 
        name        =   "Ancient Kappa Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "MODELID NOT AQUIRED!!! Dropped by Ancient Kappa in The Undercity, Kaineng City"),

    ModelID.Animal_Hide : Item(
        model_id     =   ModelID.Animal_Hide, 
        name        =   "Animal Hide", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "MODELID NOT AQUIRED!!!"),

    ModelID.Archaic_Kappa_Shell : Item(
        model_id     =   ModelID.Archaic_Kappa_Shell, 
        name        =   "Archaic Kappa Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Kappa in the Shenzun Tunnels, Factions"),

    ModelID.Arachnis_Scythe : Item(
        model_id     =   ModelID.Arachnis_Scythe,
        name        =   "Arachni's Scythe",
        item_type    =   ItemType.Scythe,
        drop_info    =   "Arachni's Scythe is a unique scythe obtained from the Arachni's Spoils chest that spawns after killing Arachni in Arachni's Haunt."),            

    ModelID.Ascalonian_Key : Item(
        model_id     =   ModelID.Ascalonian_Key, 
        name        =   "Ascalonian Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Ascalon"),

    ModelID.Ashen_Wurm_Husk : Item(
        model_id     =   ModelID.Ashen_Wurm_Husk, 
        name        =   "Ashen Wurm Husk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "MODELID NOT AQUIRED!!!"),

    ModelID.Assassin_Elitetome : Item(
        model_id     =   ModelID.Assassin_Elitetome, 
        name        =   "Assassin Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),
        
    ModelID.Assassin_Tome : Item(
        model_id     =   ModelID.Assassin_Tome, 
        name        =   "Assassin Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),
        
    ModelID.Augmented_Flesh : Item(
        model_id     =   ModelID.Augmented_Flesh, 
        name        =   "Augmented Flesh", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by afflicted in Sing Jea Island"),
        
    ModelID.Azure_Crest : Item(
        model_id     =   ModelID.Azure_Crest, 
        name        =   "Azure Crest", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Rockhide and Saltspray Dragons in The Jade Sea"),
        
    ModelID.Azure_Remains : Item(
        model_id     =   ModelID.Azure_Remains, 
        name        =   "Azure Remains", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Azure Shadows in Southern Shiverpeaks"),
        
    ModelID.Baked_Husk : Item(
        model_id     =   ModelID.Baked_Husk, 
        name        =   "Baked Husk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Plague Worm, Worm Queen in Lakeside County - Ascalon (pre-Searing)"),
        
    ModelID.Battle_Isle_Iced_Tea : Item(
        model_id     =   ModelID.Battle_Isle_Iced_Tea, 
        name        =   "Battle Isle Iced Tea", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration"),
        
    ModelID.Beetle_Egg : Item(
        model_id     =   ModelID.Beetle_Egg, 
        name        =   "Beetle Egg", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Ghosteater Beetle, Thorn Beetle, Thorn Beetle Queen in Depths of Tyria - EOTN"),
        
    ModelID.Behemoth_Hide : Item(
        model_id     =   ModelID.Behemoth_Hide, 
        name        =   "Behemoth Hide", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Behemoth Gravebane, Scytheclaw Behemoth in Vabii - Nightfall"),
        
    ModelID.Behemoth_Jaw : Item(
        model_id     =   ModelID.Behemoth_Jaw, 
        name        =   "Behemoth Jaw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Henge Guardian, Root Begemoth in Maguuma Jungle - Prophecies"),
        
    ModelID.Berserker_Horn : Item(
        model_id     =   ModelID.Berserker_Horn, 
        name        =   "Berserker Horn", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Berserking Creatures in Far Shiverpeaks - EOTN"),
        
    ModelID.Birthday_Cupcake : Item(
        model_id     =   ModelID.Birthday_Cupcake, 
        name        =   "Birthday Cupcake", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebrations & Dragon Festival & Canthan New Year"),
        
    ModelID.Black_Pearl : Item(
        model_id     =   ModelID.Black_Pearl, 
        name        =   "Black Pearl", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Creeping Carp, Irukandji, Scuttle Fish - The Jade Sea"),
        
    ModelID.Bleached_Carapace : Item(
        model_id     =   ModelID.Bleached_Carapace, 
        name        =   "Bleached Carapace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Rockshot Devourer in Crystal Desert - Prophecies & Dalada Uplands - EOTN"),
        
    ModelID.Bleached_Shell : Item(
        model_id     =   ModelID.Bleached_Shell, 
        name        =   "Bleached Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "MODELID NOT AQUIRED!!! Dropped by Sand Wurm, Siege Wurm in Crystal Desert - Prophecies"),
        
    ModelID.Blessing_Of_War : Item(
        model_id     =   ModelID.Blessing_Of_War, 
        name        =   "Blessing Of War", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped after every 25 Zaishen Keys are used to open the Zaishen Chest"),
        
    ModelID.Blob_Of_Ooze : Item(
        model_id     =   ModelID.Blob_Of_Ooze, 
        name        =   "Blob Of Ooze", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by Ooze in Depths of Tyria & Magma Blister in Charr Homelands - EOTN"),
        
    ModelID.Blood_Drinker_Pelt : Item(
        model_id     =   ModelID.Blood_Drinker_Pelt, 
        name        =   "Blood Drinker Pelt", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "MODELID NOT AQUIRED!!! Dropped by Blood Drinker, Rhythm Drinker in Echovald Forest - Factions"),
        
    ModelID.Bolt_Of_Cloth : Item(
        model_id     =   ModelID.Bolt_Of_Cloth, 
        name        =   "Bolt Of Cloth", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),
        
    ModelID.Bolt_Of_Damask : Item(
        model_id     =   ModelID.Bolt_Of_Damask, 
        name        =   "Bolt Of Damask", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),
        
    ModelID.Bolt_Of_Linen : Item(
        model_id     =   ModelID.Bolt_Of_Linen, 
        name        =   "Bolt Of Linen", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),
        
    ModelID.Bolt_Of_Silk : Item(
        model_id     =   ModelID.Bolt_Of_Silk, 
        name        =   "Bolt Of Silk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),
        
    ModelID.Bone : Item(
        model_id     =   ModelID.Bone, 
        name        =   "Bone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),
        
    ModelID.Bottle_Of_Grog : Item(
        model_id     =   ModelID.Bottle_Of_Grog, 
        name        =   "Bottle Of Grog", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Pirate Week"),
        
    ModelID.Bottle_Of_Rice_Wine : Item(
        model_id     =   ModelID.Bottle_Of_Rice_Wine, 
        name        =   "Bottle Of Rice Wine", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Jarimiya the Unmerciful"),
        
    ModelID.Bottle_Of_Vabbian_Wine : Item(
        model_id     =   ModelID.Bottle_Of_Vabbian_Wine, 
        name        =   "Bottle Of Vabbian Wine", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Jarimiya the Unmerciful"),
        
    ModelID.Bottle_Rocket : Item(
        model_id     =   ModelID.Bottle_Rocket, 
        name        =   "Bottle Rocket", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration & Wayfarer's Reverie"),
        
    ModelID.Canthan_Key : Item(
        model_id     =   ModelID.Canthan_Key, 
        name        =   "Canthan Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Kaineng City"),
        
    ModelID.Cc_Shard : Item(
        model_id     =   ModelID.Cc_Shard, 
        name        =   "Cc Shard", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped during Wintersday, randomly dropped by PvE foes"),
        
    ModelID.Celestial_Essence : Item(
        model_id     =   ModelID.Celestial_Essence, 
        name        =   "Celestial Essence", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Champagne_Popper : Item(
        model_id     =   ModelID.Champagne_Popper, 
        name        =   "Champagne Popper", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration & Wayfarer's Reverie"),
        
    ModelID.Charr_Carving : Item(
        model_id     =   ModelID.Charr_Carving, 
        name        =   "Charr Carving", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Chitin_Fragment : Item(
        model_id     =   ModelID.Chitin_Fragment, 
        name        =   "Chitin Fragment", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),
        
    ModelID.Chocolate_Bunny : Item(
        model_id     =   ModelID.Chocolate_Bunny, 
        name        =   "Chocolate Bunny", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Sweet Treats Week"),
        
    ModelID.Chromatic_Scale : Item(
        model_id     =   ModelID.Chromatic_Scale, 
        name        =   "Chromatic Scale", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Chunk_Of_Drake_Flesh : Item(
        model_id     =   ModelID.Chunk_Of_Drake_Flesh, 
        name        =   "Chunk Of Drake Flesh", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Cloth_Of_The_Brotherhood : Item(
        model_id     =   ModelID.Cloth_Of_The_Brotherhood, 
        name        =   "Cloth Of The Brotherhood", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped from Chest of the Brotherhood"),

    ModelID.Cobalt_Talon : Item(
        model_id     =   ModelID.Cobalt_Talon, 
        name        =   "Cobalt Talon", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Confessors_Orders : Item(
        model_id     =   ModelID.Confessors_Orders, 
        name        =   "Confessors Orders", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by the White Mantle & Peacekeepers"),

    ModelID.Copper_Chrimson_Skull_Coin : Item(
        model_id     =   ModelID.Copper_Chrimson_Skull_Coin, 
        name        =   "Copper Chrimson Skull Coin", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Copper_Shilling : Item(
        model_id     =   ModelID.Copper_Shilling, 
        name        =   "Copper Shilling", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Corrosive_Spider_Leg : Item(
        model_id     =   ModelID.Corrosive_Spider_Leg, 
        name        =   "Corrosive Spider Leg", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Creme_Brulee : Item(
        model_id     =   ModelID.Creme_Brulee, 
        name        =   "Creme Brulee", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration & Dragon Festival"),

    ModelID.Curved_Mintaur_Horn : Item(
        model_id     =   ModelID.Curved_Mintaur_Horn, 
        name        =   "Curved Mintaur Horn", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dark_Claw : Item(
        model_id     =   ModelID.Dark_Claw, 
        name        =   "Dark Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dark_Flame_Fang : Item(
        model_id     =   ModelID.Dark_Flame_Fang, 
        name        =   "Dark Flame Fang", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dark_Remains : Item(
        model_id     =   ModelID.Dark_Remains, 
        name        =   "Dark Remains", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Darkstone_Key : Item(
        model_id     =   ModelID.Darkstone_Key, 
        name        =   "Darkstone Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Ring Of Fire Island Chain"),

    ModelID.Decayed_Orr_Emblem : Item(
        model_id     =   ModelID.Decayed_Orr_Emblem, 
        name        =   "Decayed Orr Emblem", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Deep_Jade_Key : Item(
        model_id     =   ModelID.Deep_Jade_Key, 
        name        =   "Deep Jade Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes The Deep"),

    ModelID.Deldrimor_Armor_Remnant : Item(
        model_id     =   ModelID.Deldrimor_Armor_Remnant, 
        name        =   "Deldrimor Armor Remnant", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped from Hierophant's Chest"),

    ModelID.Deldrimor_Steel_Ingot : Item(
        model_id     =   ModelID.Deldrimor_Steel_Ingot, 
        name        =   "Deldrimor Steel Ingot", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Delicious_Cake : Item(
        model_id     =   ModelID.Delicious_Cake, 
        name        =   "Delicious Cake", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration"),

    ModelID.Demonic_Fang : Item(
        model_id     =   ModelID.Demonic_Fang, 
        name        =   "Demonic Fang", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Demonic_Key : Item(
        model_id     =   ModelID.Demonic_Key, 
        name        =   "Demonic Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Domain Of Anguish"),

    ModelID.Demonic_Relic : Item(
        model_id     =   ModelID.Demonic_Relic, 
        name        =   "Demonic Relic", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Demonic_Remains : Item(
        model_id     =   ModelID.Demonic_Remains, 
        name        =   "Demonic Remains", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dervish_Elitetome : Item(
        model_id     =   ModelID.Dervish_Elitetome, 
        name        =   "Dervish Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Dervish_Tome : Item(
        model_id     =   ModelID.Dervish_Tome, 
        name        =   "Dervish Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Dessicated_Hydra_Claw : Item(
        model_id     =   ModelID.Dessicated_Hydra_Claw, 
        name        =   "Dessicated Hydra Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Destroyer_Core : Item(
        model_id     =   ModelID.Destroyer_Core, 
        name        =   "Destroyer Core", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Diamond : Item(
        model_id     =   ModelID.Diamond, 
        name        =   "Diamond", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Diamond_Djinn_Essence : Item(
        model_id     =   ModelID.Diamond_Djinn_Essence, 
        name        =   "Diamond Djinn Essence", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Diessa_Chalice : Item(
        model_id     =   ModelID.Diessa_Chalice, 
        name        =   "Diessa Chalice", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes in the Cathedral of Flames during the Temple of the Damned quest"),

    ModelID.Dragon_Root : Item(
        model_id     =   ModelID.Dragon_Root, 
        name        =   "Dragon Root", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dredge_Incisor : Item(
        model_id     =   ModelID.Dredge_Incisor, 
        name        =   "Dredge Incisor", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dregde_Charm : Item(
        model_id     =   ModelID.Dregde_Charm, 
        name        =   "Dregde Charm", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dregde_Manifesto : Item(
        model_id     =   ModelID.Dregde_Manifesto, 
        name        =   "Dregde Manifesto", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dryder_Web : Item(
        model_id     =   ModelID.Dryder_Web, 
        name        =   "Dryder Web", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dull_Carapace : Item(
        model_id     =   ModelID.Dull_Carapace, 
        name        =   "Dull Carapace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dune_Burrower_Jaw : Item(
        model_id     =   ModelID.Dune_Burrower_Jaw, 
        name        =   "Dune Burrower Jaw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dusty_Insect_Carapace : Item(
        model_id     =   ModelID.Dusty_Insect_Carapace, 
        name        =   "Dusty Insect Carapace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Dwarven_Ale : Item(
        model_id     =   ModelID.Dwarven_Ale, 
        name        =   "Dwarven Ale", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Irontoe's Chest"),

    ModelID.Ebon_Spider_Leg : Item(
        model_id     =   ModelID.Ebon_Spider_Leg, 
        name        =   "Ebon Spider Leg", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Eggnog : Item(
        model_id     =   ModelID.Eggnog, 
        name        =   "Eggnog", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),
        
    ModelID.El_Mischievious_Tonic : Item(
        model_id     =   ModelID.El_Mischievious_Tonic, 
        name        =   "El Mischievious Tonic", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday"),
        
    ModelID.El_Yuletide_Tonic : Item(
        model_id     =   ModelID.El_Yuletide_Tonic, 
        name        =   "El Yuletide Tonic", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),
        
    ModelID.Elder_Kappa_Shell : Item(
        model_id     =   ModelID.Elder_Kappa_Shell, 
        name        =   "Elder Kappa Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Elementalist_Elitetome : Item(
        model_id     =   ModelID.Elementalist_Elitetome, 
        name        =   "Elementalist Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),
        
    ModelID.Elementalist_Tome : Item(
        model_id     =   ModelID.Elementalist_Tome, 
        name        =   "Elementalist Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),
        
    ModelID.Elonian_Key : Item(
        model_id     =   ModelID.Elonian_Key, 
        name        =   "Elonian Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Crystal Desert"),
        
    ModelID.Elonian_Leather_Square : Item(
        model_id     =   ModelID.Elonian_Leather_Square, 
        name        =   "Elonian Leather Square", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),
        
    ModelID.Enchanted_Lodestone : Item(
        model_id     =   ModelID.Enchanted_Lodestone, 
        name        =   "Enchanted Lodestone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Enchanted_Vine : Item(
        model_id     =   ModelID.Enchanted_Vine, 
        name        =   "Enchanted Vine", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Encrusted_Lodestone : Item(
        model_id     =   ModelID.Encrusted_Lodestone, 
        name        =   "Encrusted Lodestone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Enslavement_Stone : Item(
        model_id     =   ModelID.Enslavement_Stone, 
        name        =   "Enslavement Stone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Feather : Item(
        model_id     =   ModelID.Feather, 
        name        =   "Feather", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),
        
    ModelID.Feathered_Avicara_Scalp : Item(
        model_id     =   ModelID.Feathered_Avicara_Scalp, 
        name        =   "Feathered Avicara Scalp", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Feathered_Caromi_Scalp : Item(
        model_id     =   ModelID.Feathered_Caromi_Scalp, 
        name        =   "Feathered Caromi Scalp", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Feathered_Crest : Item(
        model_id     =   ModelID.Feathered_Crest, 
        name        =   "Feathered Crest", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Feathered_Scalp : Item(
        model_id     =   ModelID.Feathered_Scalp, 
        name        =   "Feathered Scalp", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Fetid_Carapace : Item(
        model_id     =   ModelID.Fetid_Carapace, 
        name        =   "Fetid Carapace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Fibrous_Mandragor_Root : Item(
        model_id     =   ModelID.Fibrous_Mandragor_Root, 
        name        =   "Fibrous Mandragor Root", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Fiery_Crest : Item(
        model_id     =   ModelID.Fiery_Crest, 
        name        =   "Fiery Crest", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Fledglin_Skree_Wing : Item(
        model_id     =   ModelID.Fledglin_Skree_Wing, 
        name        =   "Fledglin Skree Wing", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Flesh_Reaver_Morsel : Item(
        model_id     =   ModelID.Flesh_Reaver_Morsel, 
        name        =   "Flesh Reaver Morsel", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Forbidden_Key : Item(
        model_id     =   ModelID.Forbidden_Key, 
        name        =   "Forbidden Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Raisu Palace"),
        
    ModelID.Forest_Minotaur_Horn : Item(
        model_id     =   ModelID.Forest_Minotaur_Horn, 
        name        =   "Forest Minotaur Horn", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Forgotten_Seal : Item(
        model_id     =   ModelID.Forgotten_Seal, 
        name        =   "Forgotten Seal", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Forgotten_Trinket_Box : Item(
        model_id     =   ModelID.Forgotten_Trinket_Box, 
        name        =   "Forgotten Trinket Box", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Four_Leaf_Clover : Item(
        model_id     =   ModelID.Four_Leaf_Clover, 
        name        =   "Four Leaf Clover", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Lucky Treats Week"),
        
    ModelID.Frigid_Heart : Item(
        model_id     =   ModelID.Frigid_Heart, 
        name        =   "Frigid Heart", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Frigid_Mandragor_Husk : Item(
        model_id     =   ModelID.Frigid_Mandragor_Husk, 
        name        =   "Frigid Mandragor Husk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Frosted_Griffon_Wing : Item(
        model_id     =   ModelID.Frosted_Griffon_Wing, 
        name        =   "Frosted Griffon Wing", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Frostfire_Fang : Item(
        model_id     =   ModelID.Frostfire_Fang, 
        name        =   "Frostfire Fang", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Frozen_Remnant : Item(
        model_id     =   ModelID.Frozen_Remnant, 
        name        =   "Frozen Remnant", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Frozen_Shell : Item(
        model_id     =   ModelID.Frozen_Shell, 
        name        =   "Frozen Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Frozen_Wurm_Husk : Item(
        model_id     =   ModelID.Frozen_Wurm_Husk, 
        name        =   "Frozen Wurm Husk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Fruitcake : Item(
        model_id     =   ModelID.Fruitcake, 
        name        =   "Fruitcake", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),
        
    ModelID.Fungal_Root : Item(
        model_id     =   ModelID.Fungal_Root, 
        name        =   "Fungal Root", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),
        
    ModelID.Fur_Square : Item(
        model_id     =   ModelID.Fur_Square, 
        name        =   "Fur Square", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),
        
    ModelID.Gargantuan_Jawbone: Item(
        model_id     =   ModelID.Gargantuan_Jawbone,
        name        =   "Gargantuan Jawbone",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Gargoyle_Skull: Item(
        model_id     =   ModelID.Gargoyle_Skull,
        name        =   "Gargoyle Skull",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Geode: Item(
        model_id     =   ModelID.Geode,
        name        =   "Geode",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Ghostly_Remains: Item(
        model_id     =   ModelID.Ghostly_Remains,
        name        =   "Ghostly Remains",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Giant_Tusk: Item(
        model_id     =   ModelID.Giant_Tusk,
        name        =   "Giant Tusk",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Glacial_Stone: Item(
        model_id     =   ModelID.Glacial_Stone,
        name        =   "Glacial Stone",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Glob_Of_Ectoplasm: Item(
        model_id     =   ModelID.Glob_Of_Ectoplasm,
        name        =   "Glob Of Ectoplasm",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Rare Material",
    ),

    ModelID.Glob_Of_Frozen_Ectoplasm: Item(
        model_id     =   ModelID.Glob_Of_Frozen_Ectoplasm,
        name        =   "Glob Of Frozen Ectoplasm",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped during In Grenth's Defense and You're a Mean One, Mr. Grenth",
    ),

    ModelID.Gloom_Seed: Item(
        model_id     =   ModelID.Gloom_Seed,
        name        =   "Gloom Seed",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Glowing_Heart: Item(
        model_id     =   ModelID.Glowing_Heart,
        name        =   "Glowing Heart",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Gold_Crimson_Skull_Coin: Item(
        model_id     =   ModelID.Gold_Crimson_Skull_Coin,
        name        =   "Gold Crimson Skull Coin",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Gold_Doubloon: Item(
        model_id     =   ModelID.Gold_Doubloon,
        name        =   "Gold Doubloon",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Golden_Egg: Item(
        model_id     =   ModelID.Golden_Egg,
        name        =   "Golden Egg",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Sweet Treats Week",
    ),

    ModelID.Golden_Rin_Relic: Item(
        model_id     =   ModelID.Golden_Rin_Relic,
        name        =   "Golden Rin Relic",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),
    
    ModelID.Golem_Runestone: Item(
        model_id     =   ModelID.Golem_Runestone,
        name        =   "Golem Runestone",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Granite_Slab: Item(
        model_id     =   ModelID.Granite_Slab,
        name        =   "Granite Slab",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Common Material",
    ),

    ModelID.Grawl_Necklace: Item(
        model_id     =   ModelID.Grawl_Necklace,
        name        =   "Grawl Necklace",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Gruesome_Ribcage: Item(
        model_id     =   ModelID.Gruesome_Ribcage,
        name        =   "Gruesome Ribcage",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Gruesome_Sternum: Item(
        model_id     =   ModelID.Gruesome_Sternum,
        name        =   "Gruesome Sternum",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Guardian_Moss: Item(
        model_id     =   ModelID.Guardian_Moss,
        name        =   "Guardian Moss",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Hard_Apple_Cider: Item(
        model_id     =   ModelID.Hard_Apple_Cider,
        name        =   "Hard Apple Cider",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Special Treats Week & Anniversary Celebration",
    ),

    ModelID.Hardened_Hump: Item(
        model_id     =   ModelID.Hardened_Hump,
        name        =   "Hardened Hump",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Heket_Tongue: Item(
        model_id     =   ModelID.Heket_Tongue,
        name        =   "Heket Tongue",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),
    
    ModelID.Honeycomb: Item(
        model_id     =   ModelID.Honeycomb,
        name        =   "Honeycomb",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Anniversary Celebrations & April Fools Day",
    ),

    ModelID.Huge_Jawbone: Item(
        model_id     =   ModelID.Huge_Jawbone,
        name        =   "Huge Jawbone",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),
    
    ModelID.Hunters_Ale: Item(
        model_id     =   ModelID.Hunters_Ale,
        name        =   "Hunters Ale",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Anniversary Celebration",
    ),

    ModelID.Hunting_Minotaur_Horn: Item(
        model_id     =   ModelID.Hunting_Minotaur_Horn,
        name        =   "Hunting Minotaur Horn",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Iboga_Petal: Item(
        model_id     =   ModelID.Iboga_Petal,
        name        =   "Iboga Petal",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Icy_Hump: Item(
        model_id     =   ModelID.Icy_Hump,
        name        =   "Icy Hump",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Icy_Lodestone: Item(
        model_id     =   ModelID.Icy_Lodestone,
        name        =   "Icy Lodestone",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Igneous_Hump: Item(
        model_id     =   ModelID.Igneous_Hump,
        name        =   "Igneous Hump",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Igneous_Spider_leg: Item(
        model_id     =   ModelID.Igneous_Spider_leg,
        name        =   "Igneous Spider Leg",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Igneous_Spider_Leg: Item(
        model_id     =   ModelID.Igneous_Spider_Leg,
        name        =   "Igneous Spider Leg 2",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Immolated_Djinn_Essence: Item(
        model_id     =   ModelID.Immolated_Djinn_Essence,
        name        =   "Immolated Djinn Essence",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Incubus_Wing: Item(
        model_id     =   ModelID.Incubus_Wing,
        name        =   "Incubus Wing",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Inscribed_Shard: Item(
        model_id     =   ModelID.Inscribed_Shard,
        name        =   "Inscribed Shard",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Insect_Appendage: Item(
        model_id     =   ModelID.Insect_Appendage,
        name        =   "Insect Appendage",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Insect_Carapace: Item(
        model_id     =   ModelID.Insect_Carapace,
        name        =   "Insect Carapace",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Intricate_Grawl_Necklace: Item(
        model_id     =   ModelID.Intricate_Grawl_Necklace,
        name        =   "Intricate Grawl Necklace",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added",
    ),

    ModelID.Skree_Wing : Item(
        model_id     =   ModelID.Skree_Wing, 
        name        =   "Skree Wing", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Iridescant_Griffon_Wing : Item(
        model_id     =   ModelID.Iridescant_Griffon_Wing, 
        name        =   "Iridescent Griffon Wing", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Iron_Ingot : Item(
        model_id     =   ModelID.Iron_Ingot, 
        name        =   "Iron Ingot", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),

    ModelID.Istani_Key : Item(
        model_id     =   ModelID.Istani_Key, 
        name        =   "Istani Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Istan"),

    ModelID.Ivory_Troll_Tusk : Item(
        model_id     =   ModelID.Ivory_Troll_Tusk, 
        name        =   "Ivory Troll Tusk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Jade_Bracelet : Item(
        model_id     =   ModelID.Jade_Bracelet, 
        name        =   "Jade Bracelet", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Jade_Mandible : Item(
        model_id     =   ModelID.Jade_Mandible, 
        name        =   "Jade Mandible", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Jade_Orb : Item(
        model_id     =   ModelID.Jade_Orb, 
        name        =   "Jade Orb", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Jadeite_Shard : Item(
        model_id     =   ModelID.Jadeite_Shard, 
        name        =   "Jadeite Shard", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Jotun_Pelt : Item(
        model_id     =   ModelID.Jotun_Pelt, 
        name        =   "Jotun Pelt", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Jungle_Skale_Fin : Item(
        model_id     =   ModelID.Jungle_Skale_Fin, 
        name        =   "Jungle Skale Fin", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Jungle_Troll_Tusk : Item(
        model_id     =   ModelID.Jungle_Troll_Tusk, 
        name        =   "Jungle Troll Tusk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Juvenile_Termite_Leg : Item(
        model_id     =   ModelID.Juvenile_Termite_Leg, 
        name        =   "Juvenile Termite Leg", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Kappa_Hatchling_Shell : Item(
        model_id     =   ModelID.Kappa_Hatchling_Shell, 
        name        =   "Kappa Hatchling Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Kappa_Shell : Item(
        model_id     =   ModelID.Kappa_Shell, 
        name        =   "Kappa Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Keen_Oni_Claw : Item(
        model_id     =   ModelID.Keen_Oni_Claw, 
        name        =   "Keen Oni Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Keen_Oni_Talon : Item(
        model_id     =   ModelID.Keen_Oni_Talon, 
        name        =   "Keen Oni Talon", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Kirin_Horn : Item(
        model_id     =   ModelID.Kirin_Horn, 
        name        =   "Kirin Horn", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Kournan_Key : Item(
        model_id     =   ModelID.Kournan_Key, 
        name        =   "Kournan Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Kourna"),

    ModelID.Kournan_Pendant : Item(
        model_id     =   ModelID.Kournan_Pendant, 
        name        =   "Kournan Pendant", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Krait_Skin : Item(
        model_id     =   ModelID.Krait_Skin, 
        name        =   "Krait Skin", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Kraken_Eye : Item(
        model_id     =   ModelID.Kraken_Eye, 
        name        =   "Kraken Eye", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Krytan_Brandy : Item(
        model_id     =   ModelID.Krytan_Brandy, 
        name        =   "Krytan Brandy", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration"),

    ModelID.Krytan_Key : Item(
        model_id     =   ModelID.Krytan_Key, 
        name        =   "Krytan Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Kryta"),

    ModelID.Kurzick_Bauble : Item(
        model_id     =   ModelID.Kurzick_Bauble, 
        name        =   "Kurzick Bauble", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Kurzick_Key : Item(
        model_id     =   ModelID.Kurzick_Key, 
        name        =   "Kurzick Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Echovald Forest"),

    ModelID.Kuskale_Claw : Item(
        model_id     =   ModelID.Kuskale_Claw, 
        name        =   "Kuskale Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Lavastrider_Appendage : Item(
        model_id     =   ModelID.Lavastrider_Appendage, 
        name        =   "Lavastrider Appendage", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Leather_Belt : Item(
        model_id     =   ModelID.Leather_Belt, 
        name        =   "Leather Belt", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Leather_Square : Item(
        model_id     =   ModelID.Leather_Square, 
        name        =   "Leather Square", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Leathery_Claw : Item(
        model_id     =   ModelID.Leathery_Claw, 
        name        =   "Leathery Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Lockpick : Item(
        model_id     =   ModelID.Lockpick, 
        name        =   "Lockpick", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes All Regions Hard Mode"),

    ModelID.Losaru_Mane : Item(
        model_id     =   ModelID.Losaru_Mane, 
        name        =   "Losaru Mane", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Lump_Of_Charcoal : Item(
        model_id     =   ModelID.Lump_Of_Charcoal, 
        name        =   "Lump Of Charcoal", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Lunar_Token : Item(
        model_id     =   ModelID.Lunar_Token, 
        name        =   "Lunar Token", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped during Canthan New Year - Random drop by foes"),

    ModelID.Luxon_Key : Item(
        model_id     =   ModelID.Luxon_Key, 
        name        =   "Luxon Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Jade Sea"),

    ModelID.Luxon_Pendant : Item(
        model_id     =   ModelID.Luxon_Pendant, 
        name        =   "Luxon Pendant", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Maguuma_Key : Item(
        model_id     =   ModelID.Maguuma_Key, 
        name        =   "Maguuma Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Maguuma Jungle"),

    ModelID.Maguuma_Mane : Item(
        model_id     =   ModelID.Maguuma_Mane, 
        name        =   "Maguuma Mane", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mahgo_Claw : Item(
        model_id     =   ModelID.Mahgo_Claw, 
        name        =   "Mahgo Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mandragor_Carapace : Item(
        model_id     =   ModelID.Mandragor_Carapace, 
        name        =   "Mandragor Carapace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mandragor_Husk : Item(
        model_id     =   ModelID.Mandragor_Husk, 
        name        =   "Mandragor Husk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mandragor_Root : Item(
        model_id     =   ModelID.Mandragor_Root, 
        name        =   "Mandragor Root", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mandragor_Swamproot : Item(
        model_id     =   ModelID.Mandragor_Swamproot, 
        name        =   "Mandragor Swamproot", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mantid_Pincer : Item(
        model_id     =   ModelID.Mantid_Pincer, 
        name        =   "Mantid Pincer", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mantid_Ungula : Item(
        model_id     =   ModelID.Mantid_Ungula, 
        name        =   "Mantid Ungula", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mantis_Pincer : Item(
        model_id     =   ModelID.Mantis_Pincer, 
        name        =   "Mantis Pincer", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Map_Piece_Bl : Item(
        model_id     =   ModelID.Map_Piece_Bl, 
        name        =   "Map Piece (Bottom-Left)", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Map_Piece_Br : Item(
        model_id     =   ModelID.Map_Piece_Br, 
        name        =   "Map Piece (Bottom-Right)", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Map_Piece_Tl : Item(
        model_id     =   ModelID.Map_Piece_Tl, 
        name        =   "Map Piece (Top-Left)", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Map_Piece_Tr : Item(
        model_id     =   ModelID.Map_Piece_Tr, 
        name        =   "Map Piece (Top-Right)", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Margonite_Gemstone : Item(
        model_id     =   ModelID.Margonite_Gemstone, 
        name        =   "Margonite Gemstone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped in Domain of Anguish (DOA)"),

    ModelID.Margonite_Key : Item(
        model_id     =   ModelID.Margonite_Key, 
        name        =   "Margonite Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Realm Of Terror"),

    ModelID.Margonite_Mask : Item(
        model_id     =   ModelID.Margonite_Mask, 
        name        =   "Margonite Mask", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Massive_Jawbone : Item(
        model_id     =   ModelID.Massive_Jawbone, 
        name        =   "Massive Jawbone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mergoyle_Skull : Item(
        model_id     =   ModelID.Mergoyle_Skull, 
        name        =   "Mergoyle Skull", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Mesmer_Elitetome : Item(
        model_id     =   ModelID.Mesmer_Elitetome, 
        name        =   "Mesmer Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Mesmer_Tome : Item(
        model_id     =   ModelID.Mesmer_Tome, 
        name        =   "Mesmer Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Miners_Key : Item(
        model_id     =   ModelID.Miners_Key, 
        name        =   "Miners Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Sorrows Furnace"),

    ModelID.Ministerial_Commendation : Item(
        model_id     =   ModelID.Ministerial_Commendation, 
        name        =   "Ministerial Commendation", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Random drop from members of the Ministry of Purity"),

    ModelID.Minotaur_Horn : Item(
        model_id     =   ModelID.Minotaur_Horn, 
        name        =   "Minotaur Horn", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Modnir_Mane : Item(
        model_id     =   ModelID.Modnir_Mane, 
        name        =   "Modnir Mane", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Molten_Claw : Item(
        model_id     =   ModelID.Molten_Claw, 
        name        =   "Molten Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Molten_Eye : Item(
        model_id     =   ModelID.Molten_Eye, 
        name        =   "Molten Eye", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Molten_Heart : Item(
        model_id     =   ModelID.Molten_Heart, 
        name        =   "Molten Heart", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Monk_Elitetome : Item(
        model_id     =   ModelID.Monk_Elitetome, 
        name        =   "Monk Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Monk_Tome : Item(
        model_id     =   ModelID.Monk_Tome, 
        name        =   "Monk Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Monstrous_Claw : Item(
        model_id     =   ModelID.Monstrous_Claw, 
        name        =   "Monstrous Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Monstrous_Eye : Item(
        model_id     =   ModelID.Monstrous_Eye, 
        name        =   "Monstrous Eye", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Monstrous_Fang : Item(
        model_id     =   ModelID.Monstrous_Fang, 
        name        =   "Monstrous Fang", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Moon_Shell : Item(
        model_id     =   ModelID.Moon_Shell, 
        name        =   "Moon Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Naga_Hide : Item(
        model_id     =   ModelID.Naga_Hide, 
        name        =   "Naga Hide", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Naga_Pelt : Item(
        model_id     =   ModelID.Naga_Pelt, 
        name        =   "Naga Pelt", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Naga_Skin : Item(
        model_id     =   ModelID.Naga_Skin, 
        name        =   "Naga Skin", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Necromancer_Elitetome : Item(
        model_id     =   ModelID.Necromancer_Elitetome, 
        name        =   "Necromancer Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Necromancer_Tome : Item(
        model_id     =   ModelID.Necromancer_Tome, 
        name        =   "Necromancer Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Obsidian_Burrower_Jaw : Item(
        model_id     =   ModelID.Obsidian_Burrower_Jaw, 
        name        =   "Obsidian Burrower Jaw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Obsidian_Key : Item(
        model_id     =   ModelID.Obsidian_Key, 
        name        =   "Obsidian Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Fissure of Woe"),

    ModelID.Obsidian_Shard : Item(
        model_id     =   ModelID.Obsidian_Shard, 
        name        =   "Obsidian Shard", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Oni_Claw : Item(
        model_id     =   ModelID.Oni_Claw, 
        name        =   "Oni Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Oni_Taloon : Item(
        model_id     =   ModelID.Oni_Taloon, 
        name        =   "Oni Taloon", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Onyx_Gemstone : Item(
        model_id     =   ModelID.Onyx_Gemstone, 
        name        =   "Onyx Gemstone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Ornate_Grawl_Necklace : Item(
        model_id     =   ModelID.Ornate_Grawl_Necklace, 
        name        =   "Ornate Grawl Necklace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Paragon_Elitetome : Item(
        model_id     =   ModelID.Paragon_Elitetome, 
        name        =   "Paragon Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Paragon_Tome : Item(
        model_id     =   ModelID.Paragon_Tome, 
        name        =   "Paragon Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Party_Beacon : Item(
        model_id     =   ModelID.Party_Beacon, 
        name        =   "Party Beacon", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration"),

    ModelID.Passage_Scroll_Deep : Item(
        model_id     =   ModelID.Passage_Scroll_Deep, 
        name        =   "Passage Scroll Deep", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses HM & Foes The Deep"),

    ModelID.Passage_Scroll_Fow : Item(
        model_id     =   ModelID.Passage_Scroll_Fow, 
        name        =   "Passage Scroll Fow", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses HM & Foes Fow"),

    ModelID.Passage_Scroll_Urgoz : Item(
        model_id     =   ModelID.Passage_Scroll_Urgoz, 
        name        =   "Passage Scroll Urgoz", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses HM & Foes Urgoz"),

    ModelID.Passage_Scroll_Uw : Item(
        model_id     =   ModelID.Passage_Scroll_Uw, 
        name        =   "Passage Scroll Uw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses HM & Foes The Uw"),

    ModelID.Patch_Of_Simian_Fur : Item(
        model_id     =   ModelID.Patch_Of_Simian_Fur, 
        name        =   "Patch Of Simian Fur", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Peppermint_Cc : Item(
        model_id     =   ModelID.Peppermint_Cc, 
        name        =   "Peppermint Cc", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),

    ModelID.Phantom_Key : Item(
        model_id     =   ModelID.Phantom_Key, 
        name        =   "Phantom Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes The Underworld"),

    ModelID.Phantom_Residue : Item(
        model_id     =   ModelID.Phantom_Residue, 
        name        =   "Phantom Residue", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Pile_Of_Elemental_Dust : Item(
        model_id     =   ModelID.Pile_Of_Elemental_Dust, 
        name        =   "Pile Of Elemental Dust", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Pile_Of_Glittering_Dust : Item(
        model_id     =   ModelID.Pile_Of_Glittering_Dust, 
        name        =   "Pile Of Glittering Dust", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),

    ModelID.Plant_Fiber : Item(
        model_id     =   ModelID.Plant_Fiber, 
        name        =   "Plant Fiber", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),

    ModelID.Plauge_Idol : Item(
        model_id     =   ModelID.Plauge_Idol, 
        name        =   "Plague Idol", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Pulsating_Growth : Item(
        model_id     =   ModelID.Pulsating_Growth, 
        name        =   "Pulsating Growth", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Putrid_Cyst : Item(
        model_id     =   ModelID.Putrid_Cyst, 
        name        =   "Putrid Cyst", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Quetzal_Crest : Item(
        model_id     =   ModelID.Quetzal_Crest, 
        name        =   "Quetzal Crest", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Rainbow_Cc : Item(
        model_id     =   ModelID.Rainbow_Cc, 
        name        =   "Rainbow Cc", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),

    ModelID.Ranger_Elitetome : Item(
        model_id     =   ModelID.Ranger_Elitetome, 
        name        =   "Ranger Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Ranger_Tome : Item(
        model_id     =   ModelID.Ranger_Tome, 
        name        =   "Ranger Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Rawhide_Belt : Item(
        model_id     =   ModelID.Rawhide_Belt, 
        name        =   "Rawhide Belt", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Red_Bean_Cake : Item(
        model_id     =   ModelID.Red_Bean_Cake, 
        name        =   "Red Bean Cake", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration & Dragon Festival"),

    ModelID.Red_Iris_Flower : Item(
        model_id     =   ModelID.Red_Iris_Flower, 
        name        =   "Red Iris Flower", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Rinkhal_Talon : Item(
        model_id     =   ModelID.Rinkhal_Talon, 
        name        =   "Rinkhal Talon", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Ritualist_Elitetome : Item(
        model_id     =   ModelID.Ritualist_Elitetome, 
        name        =   "Ritualist Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Ritualist_Tome : Item(
        model_id     =   ModelID.Ritualist_Tome, 
        name        =   "Ritualist Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),
                    
    ModelID.Ritualist_Elitetome : Item(
        model_id     =   ModelID.Ritualist_Elitetome, 
        name        =   "Ritualist Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Ritualist_Tome : Item(
        model_id     =   ModelID.Ritualist_Tome, 
        name        =   "Ritualist Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Roaring_Ether_Claw : Item(
        model_id     =   ModelID.Roaring_Ether_Claw, 
        name        =   "Roaring Ether Claw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Roll_Of_Parchment : Item(
        model_id     =   ModelID.Roll_Of_Parchment, 
        name        =   "Roll Of Parchment", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Roll_Of_Vellum : Item(
        model_id     =   ModelID.Roll_Of_Vellum, 
        name        =   "Roll Of Vellum", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Rot_Wallow_Tusk : Item(
        model_id     =   ModelID.Rot_Wallow_Tusk, 
        name        =   "Rot Wallow Tusk", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Ruby : Item(
        model_id     =   ModelID.Ruby, 
        name        =   "Ruby", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Ruby_Djinn_Essence : Item(
        model_id     =   ModelID.Ruby_Djinn_Essence, 
        name        =   "Ruby Djinn Essence", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sandblasted_Lodestone : Item(
        model_id     =   ModelID.Sandblasted_Lodestone, 
        name        =   "Sandblasted Lodestone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sapphire : Item(
        model_id     =   ModelID.Sapphire, 
        name        =   "Sapphire", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Sapphire_Djinn_Essence : Item(
        model_id     =   ModelID.Sapphire_Djinn_Essence, 
        name        =   "Sapphire Djinn Essence", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Saurian_Bone : Item(
        model_id     =   ModelID.Saurian_Bone, 
        name        =   "Saurian Bone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Scale : Item(
        model_id     =   ModelID.Scale, 
        name        =   "Scale", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),

    ModelID.Scar_Behemoth_Jaw : Item(
        model_id     =   ModelID.Scar_Behemoth_Jaw, 
        name        =   "Scar Behemoth Jaw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Scorched_Lodestone : Item(
        model_id     =   ModelID.Scorched_Lodestone, 
        name        =   "Scorched Lodestone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Scorched_Seed : Item(
        model_id     =   ModelID.Scorched_Seed, 
        name        =   "Scorched Seed", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Scroll_Of_Adventurers_Insight : Item(
        model_id     =   ModelID.Scroll_Of_Adventurers_Insight, 
        name        =   "Scroll Of Adventurers Insight", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses NM & HM"),

    ModelID.Scroll_Of_Berserkers_Insight : Item(
        model_id     =   ModelID.Scroll_Of_Berserkers_Insight, 
        name        =   "Scroll Of Berserkers Insight", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses NM & HM"),

    ModelID.Scroll_Of_Heros_Insight : Item(
        model_id     =   ModelID.Scroll_Of_Heros_Insight, 
        name        =   "Scroll Of Heros Insight", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses NM & HM"),

    ModelID.Scroll_Of_Hunters_Insight : Item(
        model_id     =   ModelID.Scroll_Of_Hunters_Insight, 
        name        =   "Scroll Of Hunters Insight", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses NM & HM"),

    ModelID.Scroll_Of_Rampagers_Insight : Item(
        model_id     =   ModelID.Scroll_Of_Rampagers_Insight, 
        name        =   "Scroll Of Rampagers Insight", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses NM & HM"),

    ModelID.Searing_Burrower_Jaw : Item(
        model_id     =   ModelID.Searing_Burrower_Jaw, 
        name        =   "Searing Burrower Jaw", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Searing_Ribcage : Item(
        model_id     =   ModelID.Searing_Ribcage, 
        name        =   "Searing Ribcage", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sentient_Lodestone : Item(
        model_id     =   ModelID.Sentient_Lodestone, 
        name        =   "Sentient Lodestone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sentient_Root : Item(
        model_id     =   ModelID.Sentient_Root, 
        name        =   "Sentient Root", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sentient_Seed : Item(
        model_id     =   ModelID.Sentient_Seed, 
        name        =   "Sentient Seed", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sentient_Spore : Item(
        model_id     =   ModelID.Sentient_Spore, 
        name        =   "Sentient Spore", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Sentient_Vine : Item(
        model_id     =   ModelID.Sentient_Vine, 
        name        =   "Sentient Vine", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Shadowy_Crest : Item(
        model_id     =   ModelID.Shadowy_Crest, 
        name        =   "Shadowy Crest", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Shamrock_Ale : Item(
        model_id     =   ModelID.Shamrock_Ale, 
        name        =   "Shamrock Ale", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Lucky Treats Week"),

    ModelID.Shing_Jea_Key : Item(
        model_id     =   ModelID.Shing_Jea_Key, 
        name        =   "Shing Jea Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Shing Jea Island"),

    ModelID.Shiverpeak_Key : Item(
        model_id     =   ModelID.Shiverpeak_Key, 
        name        =   "Shiverpeak Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Southern Shiverpeaks"),

    ModelID.Slayers_Insight_Scroll : Item(
        model_id     =   ModelID.Slayers_Insight_Scroll, 
        name        =   "Slayers Insight Scroll", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses NM & HM"),

    ModelID.Slice_Of_Pumpkin_Pie : Item(
        model_id     =   ModelID.Slice_Of_Pumpkin_Pie, 
        name        =   "Slice Of Pumpkin Pie", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Special Treats Week"),

    ModelID.Snowman_Summoner : Item(
        model_id     =   ModelID.Snowman_Summoner, 
        name        =   "Snowman Summoner", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),

    ModelID.Sparkler : Item(
        model_id     =   ModelID.Sparkler, 
        name        =   "Sparkler", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebration & Wayfarer's Reverie"),

    ModelID.Spiked_Eggnog : Item(
        model_id     =   ModelID.Spiked_Eggnog, 
        name        =   "Spiked Eggnog", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Wintersday & Chest of Wintersday Past"),

    ModelID.Spiritwood_Plank : Item(
        model_id     =   ModelID.Spiritwood_Plank, 
        name        =   "Spiritwood Plank", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),


    ModelID.Spiritwood_Plank : Item(
        model_id     =   ModelID.Spiritwood_Plank, 
        name        =   "Spiritwood Plank", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Steel_Ingot : Item(
        model_id     =   ModelID.Steel_Ingot, 
        name        =   "Steel Ingot", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Steel_Key : Item(
        model_id     =   ModelID.Steel_Key, 
        name        =   "Steel Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Northern Silverpeaks"),

    ModelID.Stoneroot_Key : Item(
        model_id     =   ModelID.Stoneroot_Key, 
        name        =   "Stoneroot Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Urgoz Warren"),

    ModelID.Stygian_Gemstone : Item(
        model_id     =   ModelID.Stygian_Gemstone, 
        name        =   "Stygian Gemstone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped in Domain of Anguish (DOA)"),

    ModelID.Sugary_Blue_Drink : Item(
        model_id     =   ModelID.Sugary_Blue_Drink, 
        name        =   "Sugary Blue Drink", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Anniversary Celebrations & Wayfarer's Reverie & Dragon Festival & Canthan New Year"),

    ModelID.Superior_Charr_Carving : Item(
        model_id     =   ModelID.Superior_Charr_Carving, 
        name        =   "Superior Charr Carving", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Tangled_Seed : Item(
        model_id     =   ModelID.Tangled_Seed, 
        name        =   "Tangled Seed", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Tanned_Hide_Square : Item(
        model_id     =   ModelID.Tanned_Hide_Square, 
        name        =   "Tanned Hide Square", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Common Material"),

    ModelID.Tempered_Glass_Vial : Item(
        model_id     =   ModelID.Tempered_Glass_Vial, 
        name        =   "Tempered Glass Vial", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Thorny_Carapace : Item(
        model_id     =   ModelID.Thorny_Carapace, 
        name        =   "Thorny Carapace", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Titan_Gemstone : Item(
        model_id     =   ModelID.Titan_Gemstone, 
        name        =   "Titan Gemstone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped in Domain of Anguish (DOA)"),

    ModelID.Topaz_Crest : Item(
        model_id     =   ModelID.Topaz_Crest, 
        name        =   "Topaz Crest", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Torment_Gemstone : Item(
        model_id     =   ModelID.Torment_Gemstone, 
        name        =   "Torment Gemstone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped in Domain of Anguish (DOA)"),

    ModelID.Truffle : Item(
        model_id     =   ModelID.Truffle, 
        name        =   "Truffle", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Umbral_Eye : Item(
        model_id     =   ModelID.Umbral_Eye, 
        name        =   "Umbral Eye", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Umbral_Shell : Item(
        model_id     =   ModelID.Umbral_Shell, 
        name        =   "Umbral Shell", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Umbral_Skeletal_Limb : Item(
        model_id     =   ModelID.Umbral_Skeletal_Limb, 
        name        =   "Umbral Skeletal Limb", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Unctuous_Remains : Item(
        model_id     =   ModelID.Unctuous_Remains, 
        name        =   "Unctuous Remains", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Undead_Bone : Item(
        model_id     =   ModelID.Undead_Bone, 
        name        =   "Undead Bone", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Unnatural_Seed : Item(
        model_id     =   ModelID.Unnatural_Seed, 
        name        =   "Unnatural Seed", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Vabbian_Key : Item(
        model_id     =   ModelID.Vabbian_Key, 
        name        =   "Vabbian Key", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes Vabbi"),

    ModelID.Vaettir_Essence : Item(
        model_id     =   ModelID.Vaettir_Essence, 
        name        =   "Vaettir Essence", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Vampiric_Fang : Item(
        model_id     =   ModelID.Vampiric_Fang, 
        name        =   "Vampiric Fang", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped in Urgoz's Warren by Hopping Vampire & Thought Stealer"),

    ModelID.Venerable_Mantid_Pincer : Item(
        model_id     =   ModelID.Venerable_Mantid_Pincer, 
        name        =   "Venerable Mantid Pincer", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Vermin_Hide : Item(
        model_id     =   ModelID.Vermin_Hide, 
        name        =   "Vermin Hide", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Vial_Of_Absinthe : Item(
        model_id     =   ModelID.Vial_Of_Absinthe, 
        name        =   "Vial Of Absinthe", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Halloween"),

    ModelID.Vial_Of_Ink : Item(
        model_id     =   ModelID.Vial_Of_Ink, 
        name        =   "Vial Of Ink", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Rare Material"),

    ModelID.Victory_Token : Item(
        model_id     =   ModelID.Victory_Token, 
        name        =   "Victory Token", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped during Anniversary & Dragon Festival - Randomly dropped by PvE foes"),

    ModelID.War_Supplies : Item(
        model_id     =   ModelID.War_Supplies, 
        name        =   "War Supplies", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Warden_Horn : Item(
        model_id     =   ModelID.Warden_Horn, 
        name        =   "Warden Horn", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Warrior_Elitetome : Item(
        model_id     =   ModelID.Warrior_Elitetome, 
        name        =   "Warrior Elitetome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Bosses & Chests in Hard Mode"),

    ModelID.Warrior_Tome : Item(
        model_id     =   ModelID.Warrior_Tome, 
        name        =   "Warrior Tome", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Foes & Chests in Hard Mode"),

    ModelID.Water_Djinn_Essence : Item(
        model_id     =   ModelID.Water_Djinn_Essence, 
        name        =   "Water Djinn Essence", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Wayfarer_Mark : Item(
        model_id     =   ModelID.Wayfarer_Mark, 
        name        =   "Wayfarer Mark", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped during Wayfarer's Reverie, randomly dropped by PvE foes"),

    ModelID.Weaver_Leg : Item(
        model_id     =   ModelID.Weaver_Leg, 
        name        =   "Weaver Leg", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.White_Mantle_Badge : Item(
        model_id     =   ModelID.White_Mantle_Badge, 
        name        =   "White Mantle Badge", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.White_Mantle_Emblem : Item(
        model_id     =   ModelID.White_Mantle_Emblem, 
        name        =   "White Mantle Emblem", 
        item_type    =   ItemType.Unknown, 
        drop_info    =   "Dropped by data to be added"),

    ModelID.Wintergreen_Cc : Item(
        model_id     =   ModelID.Wintergreen_Cc,
        name        =   "Wintergreen Cc",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Wintersday & Chest of Wintersday Past"),
    
    ModelID.Witchs_Brew : Item(
        model_id     =   ModelID.Witchs_Brew,
        name        =   "Witchs Brew",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Halloween"),

    ModelID.Wood_Plank : Item(
        model_id     =   ModelID.Wood_Plank,
        name        =   "Wood Plank",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Common Material"),

    ModelID.Worn_Belt : Item(
        model_id     =   ModelID.Worn_Belt,
        name        =   "Worn Belt",
        item_type    =   ItemType.Unknown,
        drop_info    =   "Dropped by data to be added"),

    ModelID.Zehtukas_Jug : Item(
        model_id     =   ModelID.Zehtukas_Jug,
        name        =   "Zehtukas Jug",
        item_type    =   ItemType.Unknown,
        drop_info    =   "The Desolation"),
    
    ModelID.Bds_Air : Item(
        model_id     =   ModelID.Bds_Air,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.AirMagic]),

    
    ModelID.Bds_Blood : Item(
        model_id     =   ModelID.Bds_Blood,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.BloodMagic]),
    
    ModelID.Bds_Channeling : Item(
        model_id     =   ModelID.Bds_Channeling,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.ChannelingMagic]),

    ModelID.Bds_Communing : Item(
        model_id     =   ModelID.Bds_Communing,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.Communing]),

    ModelID.Bds_Curses : Item(
        model_id     =   ModelID.Bds_Curses,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.Curses]),

    ModelID.Bds_Death : Item(
        model_id     =   ModelID.Bds_Death,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.DeathMagic]),

    ModelID.Bds_Divine : Item(
        model_id     =   ModelID.Bds_Divine,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.DivineFavor]),

    ModelID.Bds_Domination : Item(
        model_id     =   ModelID.Bds_Domination,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.DominationMagic]),

    ModelID.Bds_Earth : Item(
        model_id     =   ModelID.Bds_Earth,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.EarthMagic]),

    ModelID.Bds_Energy_Storage : Item(
        model_id     =   ModelID.Bds_Energy_Storage,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.EnergyStorage]),

    ModelID.Bds_Fast_Casting : Item(
        model_id     =   ModelID.Bds_Fast_Casting,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.FastCasting]),

    ModelID.Bds_Fire : Item(
        model_id     =   ModelID.Bds_Fire,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.FireMagic]),

    ModelID.Bds_Healing : Item(
        model_id     =   ModelID.Bds_Healing,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.HealingPrayers]),

    ModelID.Bds_Illusion : Item(
        model_id     =   ModelID.Bds_Illusion,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.IllusionMagic]),

    ModelID.Bds_Inspiration : Item(
        model_id     =   ModelID.Bds_Inspiration,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.InspirationMagic]),

    ModelID.Bds_Protection : Item(
        model_id     =   ModelID.Bds_Protection,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.ProtectionPrayers]),

    ModelID.Bds_Restoration : Item(
        model_id     =   ModelID.Bds_Restoration,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.RestorationMagic]),

    ModelID.Bds_Smiting : Item(
        model_id     =   ModelID.Bds_Smiting,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.SmitingPrayers]),

    ModelID.Bds_Soul_Reaping : Item(
        model_id     =   ModelID.Bds_Soul_Reaping,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.SoulReaping]),

    ModelID.Bds_Spawning : Item(
        model_id     =   ModelID.Bds_Spawning,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.SpawningPower]),

    ModelID.Bds_Water : Item(
        model_id     =   ModelID.Bds_Water,
        name        =   "Bone Dragon Staff",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Bone Dragon Staff is a rare staff which drops only from Fendi's Chest, after completing the Shards of Orr dungeon.",
        attributes  =   [Attribute.WaterMagic]),

    ModelID.Froggy_Air : Item(
        model_id     =   ModelID.Froggy_Air,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.AirMagic]),

    ModelID.Froggy_Blood: Item(
        model_id     =   ModelID.Froggy_Blood,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.BloodMagic]),

    ModelID.Froggy_Channeling: Item(
        model_id     =   ModelID.Froggy_Channeling,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.ChannelingMagic]),

    ModelID.Froggy_Communing: Item(
        model_id     =   ModelID.Froggy_Communing,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.Communing]),

    ModelID.Froggy_Curses: Item(
        model_id     =   ModelID.Froggy_Curses,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.Curses]),

    ModelID.Froggy_Death: Item(
        model_id     =   ModelID.Froggy_Death,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.DeathMagic]),

    ModelID.Froggy_Divine: Item(
        model_id     =   ModelID.Froggy_Divine,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.DivineFavor]),

    ModelID.Froggy_Domination: Item(
        model_id     =   ModelID.Froggy_Domination,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.DominationMagic]),

    ModelID.Froggy_Earth: Item(
        model_id     =   ModelID.Froggy_Earth,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.EarthMagic]),

    ModelID.Froggy_Energy_Storage: Item(
        model_id     =   ModelID.Froggy_Energy_Storage,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.EnergyStorage]),

    ModelID.Froggy_Fast_Casting: Item(
        model_id     =   ModelID.Froggy_Fast_Casting,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.FastCasting]),

    ModelID.Froggy_Fire: Item(
        model_id     =   ModelID.Froggy_Fire,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.FireMagic]),

    ModelID.Froggy_Healing: Item(
        model_id     =   ModelID.Froggy_Healing,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.HealingPrayers]),

    ModelID.Froggy_Illusion: Item(
        model_id     =   ModelID.Froggy_Illusion,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.IllusionMagic]),

    ModelID.Froggy_Inspiration: Item(
        model_id     =   ModelID.Froggy_Inspiration,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.InspirationMagic]),

    ModelID.Froggy_Protection: Item(
        model_id     =   ModelID.Froggy_Protection,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.ProtectionPrayers]),

    ModelID.Froggy_Restoration: Item(
        model_id     =   ModelID.Froggy_Restoration,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.RestorationMagic]),

    ModelID.Froggy_Smiting: Item(
        model_id     =   ModelID.Froggy_Smiting,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.SmitingPrayers]),

    ModelID.Froggy_Soul_Reaping: Item(
        model_id     =   ModelID.Froggy_Soul_Reaping,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.SoulReaping]),

    ModelID.Froggy_Spawning: Item(
        model_id     =   ModelID.Froggy_Spawning,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.SpawningPower]),

    ModelID.Froggy_Water: Item(
        model_id     =   ModelID.Froggy_Water,
        name        =   "Frog Scepter",
        item_type    =   ItemType.Staff,
        drop_info    =   "The Frog Scepter is a rare scepter which drops only from Bogroot Chest, after completing the Bogroot Growths dungeon.",
        attributes  =   [Attribute.WaterMagic]),
}

# For each ModelID that is not in the dictionary, create an Item object
for model_id in ModelID:
    if model_id not in Items:
        name = model_id.name
        # Replace all underscores with spaces
        name = name.replace("_", " ")

        Items[model_id] = Item(
            model_id     =   model_id, 
            name        =   name, 
            item_type    =   ItemType.Unknown, 
            drop_info    =   "No data added yet")
        

#Sort the items by name
Items = dict(sorted(Items.items(), key=lambda x: x[1].name))

# Grouped by type
ItemsByType = {}
for item in Items.values():
    if item.item_type not in ItemsByType:
        ItemsByType[item.item_type] = []
    ItemsByType[item.item_type].append(item)

# Sort each group by name
for item_type in ItemsByType:
    ItemsByType[item_type].sort(key=lambda x: x.name)