from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import Profession
from Py4GWCoreLib.enums_src.Item_enums import ItemType, Rarity
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Sources.ItemHandling.item_modifiers import DecodedModifier


class Insignia:
    identifier: int
    model_id : int
    model_file_id: int
    inventory_icon : str
    profession : Profession 
    rarity : Rarity
    names: dict[ServerLanguage, str]

    def __init__(self, modifier: DecodedModifier):
        self.modifier = modifier        

    def describe(self) -> str:
        return f"Modifier {self.identifier}"
    
    @property
    def name(self) -> str:
        preference = UIManager.GetIntPreference(NumberPreference.TextLanguage)
        server_language = ServerLanguage(preference)
        return self.names.get(server_language, self.names.get(ServerLanguage.English, self.__class__.__name__))
        
_INSIGNIA_REGISTRY: dict[int, type[Insignia]] = {}
def register_insignia(cls: type[Insignia]) -> type[Insignia]:
    if cls.identifier in _INSIGNIA_REGISTRY:
        raise ValueError(f"Insignia with identifier {cls.identifier} is already registered as {_INSIGNIA_REGISTRY[cls.identifier].__name__}")
    
    _INSIGNIA_REGISTRY[cls.identifier] = cls
    return cls

class BlessedInsignia(Insignia):
    identifier = 489
    model_id = 19135
    model_file_id = 265850
    inventory_icon = "Blessed Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Blessed Insignia",
        ServerLanguage.Spanish: "Insignia con bendición",
        ServerLanguage.Italian: "Insegne della Benedizione",
        ServerLanguage.German: "Segens Befähigung",
        ServerLanguage.Korean: "축복의 휘장",
        ServerLanguage.French: "Insigne de la bénédiction",
        ServerLanguage.TraditionalChinese: "祝福 徽記",
        ServerLanguage.Japanese: "ブレス 記章",
        ServerLanguage.Polish: "Symbol Błogosławieństwa",
        ServerLanguage.Russian: "Blessed Insignia",
        ServerLanguage.BorkBorkBork: "Blessed Inseegneea"
    }
    def describe(self) -> str:
        return f"Armor +10 (while affected by an Enchantment Spell)"
register_insignia(BlessedInsignia)

class BrawlersInsignia(Insignia):
    identifier = 488
    model_id = 19134
    model_file_id = 265849
    inventory_icon = "Brawler's Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Brawler's Insignia",
        ServerLanguage.Spanish: "Insignia del pendenciero",
        ServerLanguage.Italian: "Insegne da Lottatore",
        ServerLanguage.German: "Raufbold- Befähigung",
        ServerLanguage.Korean: "싸움꾼의 휘장",
        ServerLanguage.French: "Insigne de l'agitateur",
        ServerLanguage.TraditionalChinese: "鬥士 徽記",
        ServerLanguage.Japanese: "ブラウラー 記章",
        ServerLanguage.Polish: "Symbol Zapaśnika",
        ServerLanguage.Russian: "Brawler's Insignia",
        ServerLanguage.BorkBorkBork: "Braevler's Inseegneea"
    }
    def describe(self) -> str:
        return f"Armor +10 (while attacking)"
register_insignia(BrawlersInsignia)

class HeraldsInsignia(Insignia):
    identifier = 490
    model_id = 19136
    model_file_id = 265851
    inventory_icon = "Herald's Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Herald's Insignia",
        ServerLanguage.Spanish: "Insignia de heraldo",
        ServerLanguage.Italian: "Insegne da Araldo",
        ServerLanguage.German: "Herold- Befähigung",
        ServerLanguage.Korean: "전령의 휘장",
        ServerLanguage.French: "Insigne de héraut",
        ServerLanguage.TraditionalChinese: "先驅 徽記",
        ServerLanguage.Japanese: "ヘラルド 記章",
        ServerLanguage.Polish: "Symbol Herolda",
        ServerLanguage.Russian: "Herald's Insignia",
        ServerLanguage.BorkBorkBork: "Heraeld's Inseegneea"
    }
    def describe(self) -> str:
        return f"Armor +10 (while holding an item)"
register_insignia(HeraldsInsignia)

class RadiantInsignia(Insignia):
    identifier = 485
    model_id = 19131
    model_file_id = 265846
    inventory_icon = "Radiant Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Radiant Insignia",
        ServerLanguage.Spanish: "Insignia radiante",
        ServerLanguage.Italian: "Insegne Radianti",
        ServerLanguage.German: "Radianten- Befähigung",
        ServerLanguage.Korean: "눈부신 휘장",
        ServerLanguage.French: "Insigne du rayonnement",
        ServerLanguage.TraditionalChinese: "閃耀 徽記",
        ServerLanguage.Japanese: "ラディアント 記章",
        ServerLanguage.Polish: "Symbol Promieni",
        ServerLanguage.Russian: "Radiant Insignia",
        ServerLanguage.BorkBorkBork: "Raedeeunt Inseegneea"
    }
    def describe(self) -> str:
        return f"Energy +3 (on chest armor)\nEnergy +2 (on leg armor)\nEnergy +1 (on other armor)"
register_insignia(RadiantInsignia)

class SentrysInsignia(Insignia):
    identifier = 491
    model_id = 19137
    model_file_id = 265852
    inventory_icon = "Sentry's Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Sentry's Insignia",
        ServerLanguage.Spanish: "Insignia de centinela",
        ServerLanguage.Italian: "Insegne da Sentinella",
        ServerLanguage.German: "Wachposten- Befähigung",
        ServerLanguage.Korean: "보초병의 휘장",
        ServerLanguage.French: "Insigne de factionnaire",
        ServerLanguage.TraditionalChinese: "哨兵 徽記",
        ServerLanguage.Japanese: "セントリー 記章",
        ServerLanguage.Polish: "Symbol Wartownika",
        ServerLanguage.Russian: "Sentry's Insignia",
        ServerLanguage.BorkBorkBork: "Sentry's Inseegneea"
    }
    def describe(self) -> str:
        return f"Armor +10 (while in a stance)"
register_insignia(SentrysInsignia)

class StalwartInsignia(Insignia):
    identifier = 487
    model_id = 19133
    model_file_id = 265848
    inventory_icon = "Stalwart Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Stalwart Insignia",
        ServerLanguage.Spanish: "Insignia firme",
        ServerLanguage.Italian: "Insegne della Robustezza",
        ServerLanguage.German: "Entschlossenheits- Befähigung",
        ServerLanguage.Korean: "튼튼한 휘장",
        ServerLanguage.French: "Insigne robuste",
        ServerLanguage.TraditionalChinese: "健壯 徽記",
        ServerLanguage.Japanese: "スタルウォート 記章",
        ServerLanguage.Polish: "Symbol Stanowczości",
        ServerLanguage.Russian: "Stalwart Insignia",
        ServerLanguage.BorkBorkBork: "Staelvaert Inseegneea"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. physical damage)"
register_insignia(StalwartInsignia)

class SurvivorInsignia(Insignia):
    identifier = 486
    model_id = 19132
    model_file_id = 265847
    inventory_icon = "Survivor Insignia.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Survivor Insignia",
        ServerLanguage.Spanish: "Insignia de superviviente",
        ServerLanguage.Italian: "Insegne del Superstite",
        ServerLanguage.German: "Überlebende Befähigung",
        ServerLanguage.Korean: "생존자의 휘장",
        ServerLanguage.French: "Insigne du survivant",
        ServerLanguage.TraditionalChinese: "生存 徽記",
        ServerLanguage.Japanese: "サバイバー 記章",
        ServerLanguage.Polish: "Symbol Przetrwania",
        ServerLanguage.Russian: "Survivor Insignia",
        ServerLanguage.BorkBorkBork: "Soorfeefur Inseegneea"
    }
    def describe(self) -> str:
        return f"Health +15 (on chest armor)\nHealth +10 (on leg armor)\nHealth +5 (on other armor)"
register_insignia(SurvivorInsignia)

class RuneOfMinorVigor(Insignia):
    identifier = 255
    model_id = 898
    model_file_id = 151852
    inventory_icon = "Rune All Minor.png"
    profession = Profession._None
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Rune of Minor Vigor",
        ServerLanguage.Spanish: "Runa (vigor de grado menor)",
        ServerLanguage.Italian: "Runa Vigore di grado minore",
        ServerLanguage.German: "Rune d. kleineren Lebenskraft",
        ServerLanguage.Korean: "룬(하급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus mineur)",
        ServerLanguage.TraditionalChinese: "初級 活力 符文",
        ServerLanguage.Japanese: "ルーン (マイナー ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru niższego poziomu)",
        ServerLanguage.Russian: "Rune of Minor Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Meenur Feegur"
    }
    def describe(self) -> str:
        return f"Health +30 (Non-stacking)"
register_insignia(RuneOfMinorVigor)

class RuneOfMajorVigor(Insignia):
    identifier = 256
    model_id = 5550
    model_file_id = 151853
    inventory_icon = "Rune All Major.png"
    profession = Profession._None
    rarity = Rarity.Purple
    names = {
        ServerLanguage.English: "Rune of Major Vigor",
        ServerLanguage.Spanish: "Runa (vigor de grado mayor)",
        ServerLanguage.Italian: "Runa Vigore di grado maggiore",
        ServerLanguage.German: "Rune d. hohen Lebenskraft",
        ServerLanguage.Korean: "룬(상급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus majeur)",
        ServerLanguage.TraditionalChinese: "中級 活力 符文",
        ServerLanguage.Japanese: "ルーン (メジャー ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru wyższego poziomu)",
        ServerLanguage.Russian: "Rune of Major Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Maejur Feegur"
    }
    def describe(self) -> str:
        return f"Health +41 (Non-stacking)"
register_insignia(RuneOfMajorVigor)

class RuneOfSuperiorVigor(Insignia):
    identifier = 257
    model_id = 5551
    model_file_id = 151854
    inventory_icon = "Rune All Sup.png"
    profession = Profession._None
    rarity = Rarity.Gold
    names = {
        ServerLanguage.English: "Rune of Superior Vigor",
        ServerLanguage.Spanish: "Runa (vigor de grado excepcional)",
        ServerLanguage.Italian: "Runa Vigore di grado supremo",
        ServerLanguage.German: "Rune d. überlegenen Lebenskraft",
        ServerLanguage.Korean: "룬(고급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus supérieur)",
        ServerLanguage.TraditionalChinese: "高級 活力 符文",
        ServerLanguage.Japanese: "ルーン (スーペリア ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru najwyższego poziomu)",
        ServerLanguage.Russian: "Rune of Superior Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Soopereeur Feegur"
    }
    def describe(self) -> str:
        return f"Health +50 (Non-stacking)"
register_insignia(RuneOfSuperiorVigor)

class DreadnoughtInsignia(Insignia):
    identifier = 506
    model_id = 19155
    model_file_id = 265870
    inventory_icon = "Dreadnought Insignia.png"
    profession = Profession.Warrior
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Dreadnought Insignia [Warrior]",
        ServerLanguage.Spanish: "Insignia [Guerrero] de Dreadnought",
        ServerLanguage.Italian: "Insegne [Guerriero] da Dreadnought",
        ServerLanguage.German: "Panzerschiff- [Krieger]-Befähigung",
        ServerLanguage.Korean: "용자의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] de Dreadnaught",
        ServerLanguage.TraditionalChinese: "無懼 徽記 [戰士]",
        ServerLanguage.Japanese: "ドレッドノート 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Pancernika",
        ServerLanguage.Russian: "Dreadnought Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Dreaednuooght Inseegneea [Vaerreeur]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. elemental damage)"
register_insignia(DreadnoughtInsignia)

class KnightsInsignia(Insignia):
    identifier = 505
    model_id = 19152
    model_file_id = 265867
    inventory_icon = "Knight's Insignia.png"
    profession = Profession.Warrior
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Knight's Insignia [Warrior]",
        ServerLanguage.Spanish: "Insignia [Guerrero] de caballero",
        ServerLanguage.Italian: "Insegne [Guerriero] da Cavaliere",
        ServerLanguage.German: "Ritter- [Krieger]-Befähigung",
        ServerLanguage.Korean: "기사의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] de chevalier",
        ServerLanguage.TraditionalChinese: "騎士 徽記 [戰士]",
        ServerLanguage.Japanese: "ナイト 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Rycerza",
        ServerLanguage.Russian: "Knight's Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Kneeght's Inseegneea [Vaerreeur]"
    }
    def describe(self) -> str:
        return f"Received physical damage -3"
register_insignia(KnightsInsignia)

class LieutenantsInsignia(Insignia):
    identifier = 520
    model_id = 19153
    model_file_id = 265868
    inventory_icon = "Lieutenant's Insignia.png"
    profession = Profession.Warrior
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Lieutenant's Insignia [Warrior]",
        ServerLanguage.Spanish: "Insignia [Guerrero] de teniente",
        ServerLanguage.Italian: "Insegne [Guerriero] da Luogotenente",
        ServerLanguage.German: "Leutnant- [Krieger]-Befähigung",
        ServerLanguage.Korean: "부관의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] du Lieutenant",
        ServerLanguage.TraditionalChinese: "副官 徽記 [戰士]",
        ServerLanguage.Japanese: "ルテナント 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Porucznika",
        ServerLanguage.Russian: "Lieutenant's Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Leeeootenunt's Inseegneea [Vaerreeur]"
    }
    def describe(self) -> str:
        return f"Reduces Hex durations on you by 20% and damage dealt by you by 5% (Non-stacking)\nArmor -20"
register_insignia(LieutenantsInsignia)

class SentinelsInsignia(Insignia):
    identifier = 507
    model_id = 19156
    model_file_id = 265871
    inventory_icon = "Sentinel's Insignia.png"
    profession = Profession.Warrior
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Sentinel's Insignia [Warrior]",
        ServerLanguage.Spanish: "Insignia [Guerrero] de centinela",
        ServerLanguage.Italian: "Insegne [Guerriero] da Sentinella",
        ServerLanguage.German: "Wächter- [Krieger]-Befähigung",
        ServerLanguage.Korean: "감시병의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] de sentinelle",
        ServerLanguage.TraditionalChinese: "警戒 徽記 [戰士]",
        ServerLanguage.Japanese: "センチネル 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Strażnika",
        ServerLanguage.Russian: "Sentinel's Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Senteenel's Inseegneea [Vaerreeur]"
    }
    def describe(self) -> str:
        return f"Armor +20 (Requires 13 Strength, vs. elemental damage)"
register_insignia(SentinelsInsignia)

class StonefistInsignia(Insignia):
    identifier = 521
    model_id = 19154
    model_file_id = 265869
    inventory_icon = "Stonefist Insignia.png"
    profession = Profession.Warrior
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Stonefist Insignia [Warrior]",
        ServerLanguage.Spanish: "Insignia [Guerrero] de piedra",
        ServerLanguage.Italian: "Insegne [Guerriero] di Pietra",
        ServerLanguage.German: "Steinfaust- [Krieger]-Befähigung",
        ServerLanguage.Korean: "돌주먹의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] Poing-de-fer",
        ServerLanguage.TraditionalChinese: "石拳 徽記 [戰士]",
        ServerLanguage.Japanese: "ストーンフィスト 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Kamiennej Pięści",
        ServerLanguage.Russian: "Stonefist Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Stuneffeest Inseegneea [Vaerreeur]"
    }
    def describe(self) -> str:
        return f"Increases knockdown time on foes by 1 second.\n(Maximum: 3 seconds)"
register_insignia(StonefistInsignia)

class RuneOfMinorAbsorption(Insignia):
    identifier = 252
    model_id = 903
    model_file_id = 23691
    inventory_icon = "Rune Warrior Minor.png"
    profession = Profession.Warrior
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Warrior Rune of Minor Absorption",
        ServerLanguage.Spanish: "Runa de Guerrero (absorción de grado menor)",
        ServerLanguage.Italian: "Runa del Guerriero Assorbimento di grado minore",
        ServerLanguage.German: "Krieger-Rune d. kleineren Absorption",
        ServerLanguage.Korean: "워리어 룬(하급 흡수)",
        ServerLanguage.French: "Rune de Guerrier (Absorption : bonus mineur)",
        ServerLanguage.TraditionalChinese: "初級 吸收 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー アブソープション)",
        ServerLanguage.Polish: "Runa Wojownika (Pochłaniania niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Absorption",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Aebsurpshun"
    }
    def describe(self) -> str:
        return f"Reduces physical damage by 1 (Non-stacking)"
register_insignia(RuneOfMinorAbsorption)

class RuneOfMajorAbsorption(Insignia):
    identifier = 253
    model_id = 5558
    model_file_id = 151883
    inventory_icon = "Rune Warrior Major.png"
    profession = Profession.Warrior
    rarity = Rarity.Purple
    names = {
        ServerLanguage.English: "Warrior Rune of Major Absorption",
        ServerLanguage.Spanish: "Runa de Guerrero (absorción de grado mayor)",
        ServerLanguage.Italian: "Runa del Guerriero Assorbimento di grado maggiore",
        ServerLanguage.German: "Krieger-Rune d. hohen Absorption",
        ServerLanguage.Korean: "워리어 룬(상급 흡수)",
        ServerLanguage.French: "Rune de Guerrier (Absorption : bonus majeur)",
        ServerLanguage.TraditionalChinese: "中級 吸收 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー アブソープション)",
        ServerLanguage.Polish: "Runa Wojownika (Pochłaniania wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Absorption",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Aebsurpshun"
    }
    def describe(self) -> str:
        return f"Reduces physical damage by 2 (Non-stacking)"
register_insignia(RuneOfMajorAbsorption)

class RuneOfSuperiorAbsorption(Insignia):
    identifier = 254
    model_id = 5559
    model_file_id = 151884
    inventory_icon = "Rune Warrior Sup.png"
    profession = Profession.Warrior
    rarity = Rarity.Gold
    names = {
        ServerLanguage.English: "Warrior Rune of Superior Absorption",
        ServerLanguage.Spanish: "Runa de Guerrero (absorción de grado excepcional)",
        ServerLanguage.Italian: "Runa del Guerriero Assorbimento di grado supremo",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Absorption",
        ServerLanguage.Korean: "워리어 룬(고급 흡수)",
        ServerLanguage.French: "Rune de Guerrier (Absorption : bonus supérieur)",
        ServerLanguage.TraditionalChinese: "高級 吸收 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア アブソープション)",
        ServerLanguage.Polish: "Runa Wojownika (Pochłaniania najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Absorption",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Aebsurpshun"
    }
    def describe(self) -> str:
        return f"Reduces physical damage by 3 (Non-stacking)"
register_insignia(RuneOfSuperiorAbsorption)

class BeastmastersInsignia(Insignia):
    identifier = 512
    model_id = 19161
    model_file_id = 265876
    inventory_icon = "Beastmaster's Insignia.png"
    profession = Profession.Ranger
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Beastmaster's Insignia [Ranger]",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de domador",
        ServerLanguage.Italian: "Insegne [Esploratore] da Domatore",
        ServerLanguage.German: "Tierbändiger- [Waldläufer]-Befähigung",
        ServerLanguage.Korean: "조련사의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] de belluaire",
        ServerLanguage.TraditionalChinese: "野獸大師 徽記 [遊俠]",
        ServerLanguage.Japanese: "ビーストマスター 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Władcy Zwierząt",
        ServerLanguage.Russian: "Beastmaster's Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Beaestmaester's Inseegneea [Runger]"
    }
    def describe(self) -> str:
        return f"Armor +10 (while your pet is alive)"
register_insignia(BeastmastersInsignia)

class EarthboundInsignia(Insignia):
    identifier = 509
    model_id = 19158
    model_file_id = 265873
    inventory_icon = "Earthbound Insignia.png"
    profession = Profession.Ranger
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Earthbound Insignia [Ranger]",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de tierra",
        ServerLanguage.Italian: "Insegne [Esploratore] da Terra",
        ServerLanguage.German: "Erdbindungs- [Waldläufer]-Befähigung",
        ServerLanguage.Korean: "대지결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] terrestre",
        ServerLanguage.TraditionalChinese: "地縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "アースバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Ziemię",
        ServerLanguage.Russian: "Earthbound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Iaerthbuoond Inseegneea [Runger]"
    }
    def describe(self) -> str:
        return f"Armor +15 (vs. Earth damage)"
register_insignia(EarthboundInsignia)

class FrostboundInsignia(Insignia):
    identifier = 508
    model_id = 19157
    model_file_id = 265872
    inventory_icon = "Frostbound Insignia.png"
    profession = Profession.Ranger
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Frostbound Insignia [Ranger]",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de montaña",
        ServerLanguage.Italian: "Insegne [Esploratore] da Ghiaccio",
        ServerLanguage.German: "Permafrost- [Waldläufer]-Befähigung",
        ServerLanguage.Korean: "얼음결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] de givre",
        ServerLanguage.TraditionalChinese: "霜縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "フロストバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Lód",
        ServerLanguage.Russian: "Frostbound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Frustbuoond Inseegneea [Runger]"
    }
    def describe(self) -> str:
        return f"Armor +15 (vs. Cold damage)"
register_insignia(FrostboundInsignia)

class PyreboundInsignia(Insignia):
    identifier = 510
    model_id = 19159
    model_file_id = 265874
    inventory_icon = "Pyrebound Insignia.png"
    profession = Profession.Ranger
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Pyrebound Insignia [Ranger]",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de leñero",
        ServerLanguage.Italian: "Insegne [Esploratore] da Rogo",
        ServerLanguage.German: "Scheiterhaufen- [Waldläufer]-Befähigung",
        ServerLanguage.Korean: "화염결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] du bûcher",
        ServerLanguage.TraditionalChinese: "火縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "パイアーバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Ogień",
        ServerLanguage.Russian: "Pyrebound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Pyrebuoond Inseegneea [Runger]"
    }
    def describe(self) -> str:
        return f"Armor +15 (vs. Fire damage)"
register_insignia(PyreboundInsignia)

class ScoutsInsignia(Insignia):
    identifier = 513
    model_id = 19162
    model_file_id = 265877
    inventory_icon = "Scout's Insignia.png"
    profession = Profession.Ranger
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Scout's Insignia [Ranger]",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de explorador",
        ServerLanguage.Italian: "Insegne [Esploratore] da Perlustratore",
        ServerLanguage.German: "Späher- [Waldläufer]-Befähigung",
        ServerLanguage.Korean: "정찰병의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] d'éclaireur",
        ServerLanguage.TraditionalChinese: "偵查者 徽記 [遊俠]",
        ServerLanguage.Japanese: "スカウト 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Zwiadowcy",
        ServerLanguage.Russian: "Scout's Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Scuoot's Inseegneea [Runger]"
    }
    def describe(self) -> str:
        return f"Armor +10 (while using a Preparation)"
register_insignia(ScoutsInsignia)

class StormboundInsignia(Insignia):
    identifier = 511
    model_id = 19160
    model_file_id = 265875
    inventory_icon = "Stormbound Insignia.png"
    profession = Profession.Ranger
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Stormbound Insignia [Ranger]",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de hidromántico",
        ServerLanguage.Italian: "Insegne [Esploratore] da Bufera",
        ServerLanguage.German: "Unwetter- [Waldläufer]-Befähigung",
        ServerLanguage.Korean: "폭풍결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] de tonnerre",
        ServerLanguage.TraditionalChinese: "風縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "ストームバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Sztorm",
        ServerLanguage.Russian: "Stormbound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Sturmbuoond Inseegneea [Runger]"
    }
    def describe(self) -> str:
        return f"Armor +15 (vs. Lightning damage)"
register_insignia(StormboundInsignia)

class AnchoritesInsignia(Insignia):
    identifier = 504
    model_id = 19151
    model_file_id = 265866
    inventory_icon = "Anchorite's Insignia.png"
    profession = Profession.Monk
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Anchorite's Insignia [Monk]",
        ServerLanguage.Spanish: "Insignia [Monje] de anacoreta",
        ServerLanguage.Italian: "Insegne [Mistico] da Anacoreta",
        ServerLanguage.German: "Einsiedler- [Mönchs]-Befähigung",
        ServerLanguage.Korean: "은둔자의 휘장 [몽크]",
        ServerLanguage.French: "Insigne [Moine] d'anachorète",
        ServerLanguage.TraditionalChinese: "隱士 徽記 [僧侶]",
        ServerLanguage.Japanese: "アンコライト 記章 [モンク]",
        ServerLanguage.Polish: "[Mnich] Symbol Pustelnika",
        ServerLanguage.Russian: "Anchorite's Insignia [Monk]",
        ServerLanguage.BorkBorkBork: "Unchureete-a's Inseegneea [Munk]"
    }
    def describe(self) -> str:
        return f"Armor +5 (while recharging 1 or more skills)\nArmor +5 (while recharging 3 or more skills)\nArmor +5 (while recharging 5 or more skills)"
register_insignia(AnchoritesInsignia)

class DisciplesInsignia(Insignia):
    identifier = 503
    model_id = 19150
    model_file_id = 265865
    inventory_icon = "Disciple's Insignia.png"
    profession = Profession.Monk
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Disciple's Insignia [Monk]",
        ServerLanguage.Spanish: "Insignia [Monje] de discípulo",
        ServerLanguage.Italian: "Insegne [Mistico] da Discepolo",
        ServerLanguage.German: "Jünger- [Mönchs]-Befähigung",
        ServerLanguage.Korean: "사도의 휘장 [몽크]",
        ServerLanguage.French: "Insigne [Moine] de disciple",
        ServerLanguage.TraditionalChinese: "門徒 徽記 [僧侶]",
        ServerLanguage.Japanese: "ディサイプル 記章 [モンク]",
        ServerLanguage.Polish: "[Mnich] Symbol Ucznia",
        ServerLanguage.Russian: "Disciple's Insignia [Monk]",
        ServerLanguage.BorkBorkBork: "Deesceeple-a's Inseegneea [Munk]"
    }
    def describe(self) -> str:
        return f"Armor +15 (while affected by a Condition)"
register_insignia(DisciplesInsignia)

class WanderersInsignia(Insignia):
    identifier = 502
    model_id = 19149
    model_file_id = 265864
    inventory_icon = "Wanderer's Insignia.png"
    profession = Profession.Monk
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Wanderer's Insignia [Monk]",
        ServerLanguage.Spanish: "Insignia [Monje] de trotamundos",
        ServerLanguage.Italian: "Insegne [Mistico] da Vagabondo",
        ServerLanguage.German: "Wanderer- [Mönchs]-Befähigung",
        ServerLanguage.Korean: "방랑자의 휘장 [몽크]",
        ServerLanguage.French: "Insigne [Moine] de vagabond",
        ServerLanguage.TraditionalChinese: "流浪者 徽記 [僧侶]",
        ServerLanguage.Japanese: "ワンダラー 記章 [モンク]",
        ServerLanguage.Polish: "[Mnich] Symbol Wędrowca",
        ServerLanguage.Russian: "Wanderer's Insignia [Monk]",
        ServerLanguage.BorkBorkBork: "Vunderer's Inseegneea [Munk]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. elemental damage)"
register_insignia(WanderersInsignia)

class BlightersInsignia(Insignia):
    identifier = 496
    model_id = 19143
    model_file_id = 265858
    inventory_icon = "Blighter's Insignia.png"
    profession = Profession.Necromancer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Blighter's Insignia [Necromancer]",
        ServerLanguage.Spanish: "Insignia [Nigromante] de malhechor",
        ServerLanguage.Italian: "Insegne [Negromante] da Malfattore",
        ServerLanguage.German: "Verderber- [Nekromanten]-Befähigung",
        ServerLanguage.Korean: "오염자의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de destructeur",
        ServerLanguage.TraditionalChinese: "破壞者 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ブライター 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Złoczyńcy",
        ServerLanguage.Russian: "Blighter's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Bleeghter's Inseegneea [Necrumuncer]"
    }
    def describe(self) -> str:
        return f"Armor +20 (while affected by a Hex Spell)"
register_insignia(BlightersInsignia)

class BloodstainedInsignia(Insignia):
    identifier = 522
    model_id = 19138
    model_file_id = 265853
    inventory_icon = "Bloodstained Insignia.png"
    profession = Profession.Necromancer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Bloodstained Insignia [Necromancer]",
        ServerLanguage.Spanish: "Insignia [Nigromante] con sangre",
        ServerLanguage.Italian: "Insegne [Negromante] di Sangue",
        ServerLanguage.German: "Blutfleck- [Nekromanten]-Befähigung",
        ServerLanguage.Korean: "혈흔의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de Sang",
        ServerLanguage.TraditionalChinese: "血腥 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ブラッドステイン 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Okrwawienia",
        ServerLanguage.Russian: "Bloodstained Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Bluudstaeeened Inseegneea [Necrumuncer]"
    }
    def describe(self) -> str:
        return f"Reduces casting time of spells that exploit corpses by 25% (Non-stacking)"
register_insignia(BloodstainedInsignia)

class BonelaceInsignia(Insignia):
    identifier = 494
    model_id = 19141
    model_file_id = 265856
    inventory_icon = "Bonelace Insignia.png"
    profession = Profession.Necromancer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Bonelace Insignia [Necromancer]",
        ServerLanguage.Spanish: "Insignia [Nigromante] de cordones de hueso",
        ServerLanguage.Italian: "Insegne [Negromante] di Maglia d'Ossa",
        ServerLanguage.German: "Klöppelspitzen- [Nekromanten]-Befähigung",
        ServerLanguage.Korean: "해골장식 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de dentelle",
        ServerLanguage.TraditionalChinese: "骨飾 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ボーンレース 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Kościanej Lancy",
        ServerLanguage.Russian: "Bonelace Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Bunelaece-a Inseegneea [Necrumuncer]"
    }
    def describe(self) -> str:
        return f"Armor +15 (vs. Piercing damage)"
register_insignia(BonelaceInsignia)

class MinionInsignia(Insignia):
    identifier = 495
    model_id = 19142
    model_file_id = 265857
    inventory_icon = "Minion Master's Insignia.png"
    profession = Profession.Necromancer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Minion Master's Insignia [Necromancer]",
        ServerLanguage.Spanish: "Insignia [Nigromante] de maestro de siervos",
        ServerLanguage.Italian: "Insegne [Negromante] da Domasgherri",
        ServerLanguage.German: "Dienermeister- [Nekromanten]-Befähigung",
        ServerLanguage.Korean: "언데드마스터의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] du Maître des serviteurs",
        ServerLanguage.TraditionalChinese: "爪牙大師 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ミニオン マスター 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Władcy Sług",
        ServerLanguage.Russian: "Minion Master's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Meeneeun Maester's Inseegneea [Necrumuncer]"
    }
    def describe(self) -> str:
        return f"Armor +5 (while you control 1 or more minions)\nArmor +5 (while you control 3 or more minions)\nArmor +5 (while you control 5 or more minions)"
register_insignia(MinionInsignia)

class TormentorsInsignia(Insignia):
    identifier = 492
    model_id = 19139
    model_file_id = 265854
    inventory_icon = "Tormentor's Insignia.png"
    profession = Profession.Necromancer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Tormentor's Insignia [Necromancer]",
        ServerLanguage.Spanish: "Insignia [Nigromante] de torturador",
        ServerLanguage.Italian: "Insegne [Negromante] da Tormentatore",
        ServerLanguage.German: "Folterer- [Nekromanten]-Befähigung",
        ServerLanguage.Korean: "고문가의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de persécuteur",
        ServerLanguage.TraditionalChinese: "苦痛者 徽記 [死靈法師]",
        ServerLanguage.Japanese: "トルメンター 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Oprawcy",
        ServerLanguage.Russian: "Tormentor's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Turmentur's Inseegneea [Necrumuncer]"
    }
    def describe(self) -> str:
        return f"Holy damage you receive increased by 6 (on chest armor)\nHoly damage you receive increased by 4 (on leg armor)\nHoly damage you receive increased by 2 (on other armor)\nArmor +10"
register_insignia(TormentorsInsignia)

class UndertakersInsignia(Insignia):
    identifier = 493
    model_id = 19140
    model_file_id = 265855
    inventory_icon = "Undertaker's Insignia.png"
    profession = Profession.Necromancer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Undertaker's Insignia [Necromancer]",
        ServerLanguage.Spanish: "Insignia [Nigromante] de enterrador",
        ServerLanguage.Italian: "Insegne [Negromante] da Becchino",
        ServerLanguage.German: "Leichenbestatter- [Nekromanten]-Befähigung",
        ServerLanguage.Korean: "장의사의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] du fossoyeur",
        ServerLanguage.TraditionalChinese: "承受者 徽記 [死靈法師]",
        ServerLanguage.Japanese: "アンダーテイカー 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Grabarza",
        ServerLanguage.Russian: "Undertaker's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Undertaeker's Inseegneea [Necrumuncer]"
    }
    def describe(self) -> str:
        return f"Armor +5 (while health is below 80%)\nArmor +5 (while health is below 60%)\nArmor +5 (while health is below 40%)\nArmor +5 (while health is below 20%)"
register_insignia(UndertakersInsignia)

class ArtificersInsignia(Insignia):
    identifier = 482
    model_id = 19128
    model_file_id = 265843
    inventory_icon = "Artificer's Insignia.png"
    profession = Profession.Mesmer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Artificer's Insignia [Mesmer]",
        ServerLanguage.Spanish: "Insignia [Hipnotizador] de artífice",
        ServerLanguage.Italian: "Insegne [Ipnotizzatore] da Artefice",
        ServerLanguage.German: "Feuerwerker- [Mesmer]-Befähigung",
        ServerLanguage.Korean: "장인의 휘장 [메스머]",
        ServerLanguage.French: "Insigne [Envoûteur] de l'artisan",
        ServerLanguage.TraditionalChinese: "巧匠 徽記 [幻術師]",
        ServerLanguage.Japanese: "アーティファサー 記章 [メスマー]",
        ServerLanguage.Polish: "[Mesmer] Symbol Rzemieślnika",
        ServerLanguage.Russian: "Artificer's Insignia [Mesmer]",
        ServerLanguage.BorkBorkBork: "Aerteeffeecer's Inseegneea [Mesmer]"
    }
    def describe(self) -> str:
        return f"Armor +3 (for each equipped Signet)"
register_insignia(ArtificersInsignia)

class ProdigysInsignia(Insignia):
    identifier = 483
    model_id = 19129
    model_file_id = 265844
    inventory_icon = "Prodigy's Insignia.png"
    profession = Profession.Mesmer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Prodigy's Insignia [Mesmer]",
        ServerLanguage.Spanish: "Insignia [Hipnotizador] de prodigio",
        ServerLanguage.Italian: "Insegne [Ipnotizzatore] da Prodigio",
        ServerLanguage.German: "Wunder- [Mesmer]-Befähigung",
        ServerLanguage.Korean: "천재의 휘장 [메스머]",
        ServerLanguage.French: "Insigne [Envoûteur] prodige",
        ServerLanguage.TraditionalChinese: "奇蹟 徽記 [幻術師]",
        ServerLanguage.Japanese: "プロディジー 記章 [メスマー]",
        ServerLanguage.Polish: "[Mesmer] Symbol Geniusza",
        ServerLanguage.Russian: "Prodigy's Insignia [Mesmer]",
        ServerLanguage.BorkBorkBork: "Prudeegy's Inseegneea [Mesmer]"
    }
    def describe(self) -> str:
        return f"Armor +5 (while recharging 1 or more skills)\nArmor +5 (while recharging 3 or more skills)\nArmor +5 (while recharging 5 or more skills)"
register_insignia(ProdigysInsignia)

class VirtuososInsignia(Insignia):
    identifier = 484
    model_id = 19130
    model_file_id = 265845
    inventory_icon = "Virtuoso's Insignia.png"
    profession = Profession.Mesmer
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Virtuoso's Insignia [Mesmer]",
        ServerLanguage.Spanish: "Insignia [Hipnotizador] de virtuoso",
        ServerLanguage.Italian: "Insegne [Ipnotizzatore] da Intenditore",
        ServerLanguage.German: "Virtuosen- [Mesmer]-Befähigung",
        ServerLanguage.Korean: "거장의 휘장 [메스머]",
        ServerLanguage.French: "Insigne [Envoûteur] de virtuose",
        ServerLanguage.TraditionalChinese: "鑑賞家 徽記 [幻術師]",
        ServerLanguage.Japanese: "ヴァーチュオーソ 記章 [メスマー]",
        ServerLanguage.Polish: "[Mesmer] Symbol Wirtuoza",
        ServerLanguage.Russian: "Virtuoso's Insignia [Mesmer]",
        ServerLanguage.BorkBorkBork: "Furtoousu's Inseegneea [Mesmer]"
    }
    def describe(self) -> str:
        return f"Armor +15 (while activating skills)"
register_insignia(VirtuososInsignia)

class AeromancerInsignia(Insignia):
    identifier = 501
    model_id = 19148
    model_file_id = 265863
    inventory_icon = "Aeromancer Insignia.png"
    profession = Profession.Elementalist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Aeromancer Insignia [Elementalist]",
        ServerLanguage.Spanish: "Insignia [Elementalista] de aeromante",
        ServerLanguage.Italian: "Insegne [Elementalista] da Aeromante",
        ServerLanguage.German: "Aeromanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Korean: "바람술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] d'aéromancie",
        ServerLanguage.TraditionalChinese: "風法師 徽記 [元素使]",
        ServerLanguage.Japanese: "エアロマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Aeromanty",
        ServerLanguage.Russian: "Aeromancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Aeerumuncer Inseegneea [Ilementaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. elemental damage)\nArmor +10 (vs. Lightning damage)"
register_insignia(AeromancerInsignia)

class GeomancerInsignia(Insignia):
    identifier = 499
    model_id = 19146
    model_file_id = 265861
    inventory_icon = "Geomancer Insignia.png"
    profession = Profession.Elementalist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Geomancer Insignia [Elementalist]",
        ServerLanguage.Spanish: "Insignia [Elementalista] de geomante",
        ServerLanguage.Italian: "Insegne [Elementalista] da Geomante",
        ServerLanguage.German: "Geomanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Korean: "대지술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] de géomancie",
        ServerLanguage.TraditionalChinese: "地法師 徽記 [元素使]",
        ServerLanguage.Japanese: "ジオマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Geomanty",
        ServerLanguage.Russian: "Geomancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Geumuncer Inseegneea [Ilementaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. elemental damage)\nArmor +10 (vs. Earth damage)"
register_insignia(GeomancerInsignia)

class HydromancerInsignia(Insignia):
    identifier = 498
    model_id = 19145
    model_file_id = 265860
    inventory_icon = "Hydromancer Insignia.png"
    profession = Profession.Elementalist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Hydromancer Insignia [Elementalist]",
        ServerLanguage.Spanish: "Insignia [Elementalista] de hidromante",
        ServerLanguage.Italian: "Insegne [Elementalista] da Idromante",
        ServerLanguage.German: "Hydromanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Korean: "물의술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] d'hydromancie",
        ServerLanguage.TraditionalChinese: "水法師 徽記 [元素使]",
        ServerLanguage.Japanese: "ハイドロマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Hydromanty",
        ServerLanguage.Russian: "Hydromancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Hydrumuncer Inseegneea [Ilementaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. elemental damage)\nArmor +10 (vs. Cold damage)"
register_insignia(HydromancerInsignia)

class PrismaticInsignia(Insignia):
    identifier = 497
    model_id = 19144
    model_file_id = 265859
    inventory_icon = "Prismatic Insignia.png"
    profession = Profession.Elementalist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Prismatic Insignia [Elementalist]",
        ServerLanguage.Spanish: "Insignia [Elementalista] de prismático",
        ServerLanguage.Italian: "Insegne [Elementalista] a Prisma",
        ServerLanguage.German: "Spektral- [Elementarmagier]-Befähigung",
        ServerLanguage.Korean: "무지갯빛 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] prismatique",
        ServerLanguage.TraditionalChinese: "稜鏡 徽記 [元素使]",
        ServerLanguage.Japanese: "プリズマティック 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Pryzmatu",
        ServerLanguage.Russian: "Prismatic Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Preesmaeteec Inseegneea [Ilementaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +5 (requires 9 Air Magic)\nArmor +5 (requires 9 Earth Magic)\nArmor +5 (requires 9 Fire Magic)\nArmor +5 (requires 9 Water Magic)"
register_insignia(PrismaticInsignia)

class PyromancerInsignia(Insignia):
    identifier = 500
    model_id = 19147
    model_file_id = 265862
    inventory_icon = "Pyromancer Insignia.png"
    profession = Profession.Elementalist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Pyromancer Insignia [Elementalist]",
        ServerLanguage.Spanish: "Insignia [Elementalista] de piromante",
        ServerLanguage.Italian: "Insegne [Elementalista] da Piromante",
        ServerLanguage.German: "Pyromanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Korean: "화염술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] de pyromancie",
        ServerLanguage.TraditionalChinese: "火法師 徽記 [元素使]",
        ServerLanguage.Japanese: "パイロマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Piromanty",
        ServerLanguage.Russian: "Pyromancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Pyrumuncer Inseegneea [Ilementaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. elemental damage)\nArmor +10 (vs. Fire damage)"
register_insignia(PyromancerInsignia)

class InfiltratorsInsignia(Insignia):
    identifier = 479
    model_id = 19125
    model_file_id = 265840
    inventory_icon = "Infiltrator's Insignia.png"
    profession = Profession.Assassin
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Infiltrator's Insignia [Assassin]",
        ServerLanguage.Spanish: "Insignia [Asesino] de infiltrado",
        ServerLanguage.Italian: "Insegne [Assassino] da Spia",
        ServerLanguage.German: "Eindringlings- [Assassinen]-Befähigung",
        ServerLanguage.Korean: "침입자의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de l'infiltré",
        ServerLanguage.TraditionalChinese: "滲透者 徽記 [暗殺者]",
        ServerLanguage.Japanese: "インフィルトレイター 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Infiltratora",
        ServerLanguage.Russian: "Infiltrator's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Inffeeltraetur's Inseegneea [Aessaesseen]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. physical damage)\nArmor +10 (vs. Piercing damage)"
register_insignia(InfiltratorsInsignia)

class NightstalkersInsignia(Insignia):
    identifier = 481
    model_id = 19127
    model_file_id = 265842
    inventory_icon = "Nightstalker's Insignia.png"
    profession = Profession.Assassin
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Nightstalker's Insignia [Assassin]",
        ServerLanguage.Spanish: "Insignia [Asesino] de acechador nocturno",
        ServerLanguage.Italian: "Insegne [Assassino] da Inseguitore Notturno",
        ServerLanguage.German: "Nachtpirscher- [Assassinen]-Befähigung",
        ServerLanguage.Korean: "밤추종자의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de traqueur nocturne",
        ServerLanguage.TraditionalChinese: "夜行者 徽記 [暗殺者]",
        ServerLanguage.Japanese: "ナイトストーカー 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Nocnego Tropiciela",
        ServerLanguage.Russian: "Nightstalker's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Neeghtstaelker's Inseegneea [Aessaesseen]"
    }
    def describe(self) -> str:
        return f"Armor +15 (while attacking)"
register_insignia(NightstalkersInsignia)

class SaboteursInsignia(Insignia):
    identifier = 480
    model_id = 19126
    model_file_id = 265841
    inventory_icon = "Saboteur's Insignia.png"
    profession = Profession.Assassin
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Saboteur's Insignia [Assassin]",
        ServerLanguage.Spanish: "Insignia [Asesino] de saboteador",
        ServerLanguage.Italian: "Insegne [Assassino] da Sabotatore",
        ServerLanguage.German: "Saboteur- [Assassinen]-Befähigung",
        ServerLanguage.Korean: "파괴자의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de saboteur",
        ServerLanguage.TraditionalChinese: "破壞者 徽記 [暗殺者]",
        ServerLanguage.Japanese: "サボター 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Sabotażysty",
        ServerLanguage.Russian: "Saboteur's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Saebuteoor's Inseegneea [Aessaesseen]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. physical damage)\nArmor +10 (vs. Slashing damage)"
register_insignia(SaboteursInsignia)

class VanguardsInsignia(Insignia):
    identifier = 478
    model_id = 19124
    model_file_id = 265839
    inventory_icon = "Vanguard's Insignia.png"
    profession = Profession.Assassin
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Vanguard's Insignia [Assassin]",
        ServerLanguage.Spanish: "Insignia [Asesino] de avanzado",
        ServerLanguage.Italian: "Insegne [Assassino] da Avanguardia",
        ServerLanguage.German: "Hauptmann- [Assassinen]-Befähigung",
        ServerLanguage.Korean: "선봉대의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de l'avant-garde",
        ServerLanguage.TraditionalChinese: "前鋒 徽記 [暗殺者]",
        ServerLanguage.Japanese: "ヴァンガード 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Awangardy",
        ServerLanguage.Russian: "Vanguard's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Fungooaerd's Inseegneea [Aessaesseen]"
    }
    def describe(self) -> str:
        return f"Armor +10 (vs. physical damage)\nArmor +10 (vs. Blunt damage)"
register_insignia(VanguardsInsignia)

class GhostInsignia(Insignia):
    identifier = 517
    model_id = 19166
    model_file_id = 265881
    inventory_icon = "Ghost Forge Insignia.png"
    profession = Profession.Ritualist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Ghost Forge Insignia [Ritualist]",
        ServerLanguage.Spanish: "Insignia [Ritualista] de fragua fantasma",
        ServerLanguage.Italian: "Insegne [Ritualista] della Fucina Spettrale",
        ServerLanguage.German: "Geisterschmiede- [Ritualisten]-Befähigung",
        ServerLanguage.Korean: "유령화로의 휘장 [리추얼리스트]",
        ServerLanguage.French: "Insigne [Ritualiste] de la forge du fantôme",
        ServerLanguage.TraditionalChinese: "魂鎔 徽記 [祭祀者]",
        ServerLanguage.Japanese: "ゴースト フォージ 記章 [リチュアリスト]",
        ServerLanguage.Polish: "[Rytualista] Symbol Kuźni Duchów",
        ServerLanguage.Russian: "Ghost Forge Insignia [Ritualist]",
        ServerLanguage.BorkBorkBork: "Ghust Furge-a Inseegneea [Reetooaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +15 (while affected by a Weapon Spell)"
register_insignia(GhostInsignia)

class MysticsInsignia(Insignia):
    identifier = 518
    model_id = 19167
    model_file_id = 265882
    inventory_icon = "Mystic's Insignia.png"
    profession = Profession.Ritualist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Mystic's Insignia [Ritualist]",
        ServerLanguage.Spanish: "Insignia [Ritualista] de místico",
        ServerLanguage.Italian: "Insegne [Ritualista] del Misticismo",
        ServerLanguage.German: "Mystiker- [Ritualisten]-Befähigung",
        ServerLanguage.Korean: "신비술사의 휘장 [리추얼리스트]",
        ServerLanguage.French: "Insigne [Ritualiste] mystique",
        ServerLanguage.TraditionalChinese: "祕法 徽記 [祭祀者]",
        ServerLanguage.Japanese: "ミスティック 記章 [リチュアリスト]",
        ServerLanguage.Polish: "[Rytualista] Symbol Mistyka",
        ServerLanguage.Russian: "Mystic's Insignia [Ritualist]",
        ServerLanguage.BorkBorkBork: "Mysteec's Inseegneea [Reetooaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +15 (while activating skills)"
register_insignia(MysticsInsignia)

class ShamansInsignia(Insignia):
    identifier = 516
    model_id = 19165
    model_file_id = 265880
    inventory_icon = "Shaman's Insignia.png"
    profession = Profession.Ritualist
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Shaman's Insignia [Ritualist]",
        ServerLanguage.Spanish: "Insignia [Ritualista] de chamán",
        ServerLanguage.Italian: "Insegne [Ritualista] da Sciamano",
        ServerLanguage.German: "Schamanen- [Ritualisten]-Befähigung",
        ServerLanguage.Korean: "주술사의 휘장 [리추얼리스트]",
        ServerLanguage.French: "Insigne [Ritualiste] de chaman",
        ServerLanguage.TraditionalChinese: "巫醫 徽記 [祭祀者]",
        ServerLanguage.Japanese: "シャーマン 記章 [リチュアリスト]",
        ServerLanguage.Polish: "[Rytualista] Symbol Szamana",
        ServerLanguage.Russian: "Shaman's Insignia [Ritualist]",
        ServerLanguage.BorkBorkBork: "Shaemun's Inseegneea [Reetooaeleest]"
    }
    def describe(self) -> str:
        return f"Armor +5 (while you control 1 or more Spirits)\nArmor +5 (while you control 2 or more Spirits)\nArmor +5 (while you control 3 or more Spirits)"
register_insignia(ShamansInsignia)

class CenturionsInsignia(Insignia):
    identifier = 519
    model_id = 19168
    model_file_id = 265883
    inventory_icon = "Centurion's Insignia.png"
    profession = Profession.Paragon
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Centurion's Insignia [Paragon]",
        ServerLanguage.Spanish: "Insignia [Paragón] de centurión",
        ServerLanguage.Italian: "Insegne [Paragon] da Centurione",
        ServerLanguage.German: "Zenturio- [Paragon]-Befähigung",
        ServerLanguage.Korean: "백부장의 휘장 [파라곤]",
        ServerLanguage.French: "Insigne [Parangon] du centurion",
        ServerLanguage.TraditionalChinese: "百夫長 徽記 [聖言者]",
        ServerLanguage.Japanese: "センチュリオン 記章 [パラゴン]",
        ServerLanguage.Polish: "[Patron] Symbol Centuriona",
        ServerLanguage.Russian: "Centurion's Insignia [Paragon]",
        ServerLanguage.BorkBorkBork: "Centooreeun's Inseegneea [Paeraegun]"
    }
    def describe(self) -> str:
        return f"Armor +10 (while affected by a Shout, Echo, or Chant)"
register_insignia(CenturionsInsignia)

class ForsakenInsignia(Insignia):
    identifier = 515
    model_id = 19164
    model_file_id = 265879
    inventory_icon = "Forsaken Insignia.png"
    profession = Profession.Dervish
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Forsaken Insignia [Dervish]",
        ServerLanguage.Spanish: "Insignia [Derviche] de abandonado",
        ServerLanguage.Italian: "Insegne [Derviscio] da Abbandonato",
        ServerLanguage.German: "Verlassenen- [Derwisch]-Befähigung",
        ServerLanguage.Korean: "고독한 휘장 [더비시]",
        ServerLanguage.French: "Insigne [Derviche] de l'oubli",
        ServerLanguage.TraditionalChinese: "背離 徽記 [神喚使]",
        ServerLanguage.Japanese: "フォーセイク 記章 [ダルウィーシュ]",
        ServerLanguage.Polish: "[Derwisz] Symbol Zapomnienia",
        ServerLanguage.Russian: "Forsaken Insignia [Dervish]",
        ServerLanguage.BorkBorkBork: "Fursaekee Inseegneea [Derfeesh]"
    }
    def describe(self) -> str:
        return f"Armor +10 (while not affected by an Enchantment Spell)"
register_insignia(ForsakenInsignia)

class WindwalkerInsignia(Insignia):
    identifier = 514
    model_id = 19163
    model_file_id = 265878
    inventory_icon = "Windwalker Insignia.png"
    profession = Profession.Dervish
    rarity = Rarity.Blue
    names = {
        ServerLanguage.English: "Windwalker Insignia [Dervish]",
        ServerLanguage.Spanish: "Insignia [Derviche] de caminante del viento",
        ServerLanguage.Italian: "Insegne [Derviscio] da Camminatore nel Vento",
        ServerLanguage.German: "Windläufer- [Derwisch]-Befähigung",
        ServerLanguage.Korean: "여행가의 휘장 [더비시]",
        ServerLanguage.French: "Insigne [Derviche] du Marche-vent",
        ServerLanguage.TraditionalChinese: "風行者 徽記 [神喚使]",
        ServerLanguage.Japanese: "ウインドウォーカー 記章 [ダルウィーシュ]",
        ServerLanguage.Polish: "[Derwisz] Symbol Włóczywiatru",
        ServerLanguage.Russian: "Windwalker Insignia [Dervish]",
        ServerLanguage.BorkBorkBork: "Veendvaelker Inseegneea [Derfeesh]"
    }
    def describe(self) -> str:
        return f"Armor +5 (while affected by 1 or more Enchantment Spells)\nArmor +5 (while affected by 2 or more Enchantment Spells)\nArmor +5 (while affected by 3 or more Enchantment Spells)\nArmor +5 (while affected by 4 or more Enchantment Spells)"
register_insignia(WindwalkerInsignia)