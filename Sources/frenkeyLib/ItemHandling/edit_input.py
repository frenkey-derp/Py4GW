from typing import Optional
import Py4GW
from Py4GWCoreLib.UIManager import UIManager
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, AttributeNames, Profession
from Py4GWCoreLib.enums_src.Item_enums import Rarity
from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Py4GWCoreLib.enums_src.UI_enums import NumberPreference
from Sources.frenkeyLib.ItemHandling.item_modifiers import DecodedModifier
from Sources.frenkeyLib.ItemHandling.item_properties import _PROPERTY_FACTORY, ItemProperty, Upgrade
from Sources.frenkeyLib.ItemHandling.types import ItemUpgradeType, ModifierIdentifier
from Sources.frenkeyLib.ItemHandling.upgrades import ItemUpgradeId

#region Armor Upgrades
class Insignia(Upgrade):
    id : ItemUpgradeId
    mod_type = ItemUpgradeType.Prefix
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    localized_name_format : dict[ServerLanguage, str] = {}

    INSIGNIA_LOCALIZATION = {
        ServerLanguage.English: "Insignia",
        ServerLanguage.Spanish: "Insignia",
        ServerLanguage.Italian: "Insegna",
        ServerLanguage.German: "Befähigung",
        ServerLanguage.Korean: "휘장",
        ServerLanguage.French: "Insigne",
        ServerLanguage.TraditionalChinese: "徽記",
        ServerLanguage.Japanese: "記章",
        ServerLanguage.Polish: "Symbol",
        ServerLanguage.Russian: "Insignia",
        ServerLanguage.BorkBorkBork: "Inseegneea"
    }

    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return cls.id is not None and upgrade_id == cls.id

    @property
    def name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(item_name=Insignia.INSIGNIA_LOCALIZATION.get(language, "Insignia"))

    @classmethod
    def add_to_item_name(cls, item_name: str, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(name=cls.get_name(language), item_name=item_name)

class Rune(Upgrade):
    id : ItemUpgradeId
    mod_type = ItemUpgradeType.Suffix
    inventory_icon : str
    rarity : Rarity = Rarity.Blue
    profession : Profession = Profession._None
    localized_name_format : dict[ServerLanguage, str] = {}

    RANK_LOCALIZATION = {
        Rarity.Blue: {
            ServerLanguage.English: "Minor",
            ServerLanguage.Spanish: "de grado menor",
            ServerLanguage.Italian: "di grado minore",
            ServerLanguage.German: "d. kleineren",
            ServerLanguage.Korean: "하급",
            ServerLanguage.French: "bonus mineur",
            ServerLanguage.TraditionalChinese: "初級",
            ServerLanguage.Japanese: "マイナー",
            ServerLanguage.Polish: "niższego poziomu",
            ServerLanguage.Russian: "Minor",
            ServerLanguage.BorkBorkBork: "Meenur"
        },
        Rarity.Purple: {
            ServerLanguage.English: "Major",
            ServerLanguage.Spanish: "de grado mayor",
            ServerLanguage.Italian: "di grado maggiore",
            ServerLanguage.German: "d. hohen",
            ServerLanguage.Korean: "상급",
            ServerLanguage.French: "bonus majeur",
            ServerLanguage.TraditionalChinese: "中級",
            ServerLanguage.Japanese: "メジャー",
            ServerLanguage.Polish: "wyższego poziomu",
            ServerLanguage.Russian: "Major",
            ServerLanguage.BorkBorkBork: "Maejur"
            },
        Rarity.Gold: {
            ServerLanguage.English: "Superior",
            ServerLanguage.Spanish: "de grado excepcional",
            ServerLanguage.Italian: "di grado supremo",
            ServerLanguage.German: "d. überlegenen",
            ServerLanguage.Korean: "고급",
            ServerLanguage.French: "bonus supérieur",
            ServerLanguage.TraditionalChinese: "高級",
            ServerLanguage.Japanese: "スーペリア",
            ServerLanguage.Polish: "najwyższego poziomu",
            ServerLanguage.Russian: "Superior",
            ServerLanguage.BorkBorkBork: "Soopereeur"
        }
    }

    RUNE_LOCALIZATION = {
        ServerLanguage.English: "Rune",
        ServerLanguage.Spanish: "Runa",
        ServerLanguage.Italian: "Runa",
        ServerLanguage.German: "Rune",
        ServerLanguage.Korean: "룬",
        ServerLanguage.French: "Rune",
        ServerLanguage.TraditionalChinese: "符文",
        ServerLanguage.Japanese: "ルーン",
        ServerLanguage.Polish: "Runa",
        ServerLanguage.Russian: "Rune",
        ServerLanguage.BorkBorkBork: "Roone-a"
    }

    @classmethod
    def has_id(cls, upgrade_id: ItemUpgradeId) -> bool:
        return cls.id is not None and upgrade_id == cls.id

    @property
    def name(self) -> str:
        return self.get_name()

    @classmethod
    def get_name(cls, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(item_name=Insignia.INSIGNIA_LOCALIZATION.get(language, "Insignia"))

    @classmethod
    def add_to_item_name(cls, item_name: str, language : ServerLanguage = ServerLanguage(UIManager.GetIntPreference(NumberPreference.TextLanguage))) -> str:
        format_str = cls.localized_name_format.get(language, "[ABC] {item_name}")
        return format_str.format(name=cls.get_name(language), item_name=item_name)

class AttributeRune(Rune):
    attribute : Attribute
    attribute_level : int

    @classmethod
    def compose_from_modifiers(cls, mod : DecodedModifier, modifiers: list[DecodedModifier]) -> Optional["AttributeRune"]:
        upgrade = cls()
        upgrade.properties = []

        cls.attribute = Attribute(mod.arg1)
        cls.attribute_level = mod.arg2

        for prop_id in upgrade.property_identifiers:
            prop_mod = next((m for m in modifiers if m.identifier == prop_id), None)

            if prop_mod:
                prop = _PROPERTY_FACTORY.get(prop_id, lambda m, _: ItemProperty(modifier=m))(prop_mod, modifiers)
                upgrade.properties.append(prop)
            else:
                Py4GW.Console.Log("ItemHandling", f"Missing modifier for property {prop_id.name} in upgrade {upgrade.__class__.__name__}. Upgrade composition failed.")
                return None

        return upgrade

    @property
    def description(self) -> str:
        parts = [prop.describe() for prop in self.properties if prop.is_valid()]
        return f"+ {self.attribute_level} {AttributeNames.get(self.attribute)}\n" + "\n".join(parts)

#region No Profession

class SurvivorInsignia(Insignia):

    names = {
        ServerLanguage.English: "Survivor Insignia",
        ServerLanguage.Korean: "생존자의 휘장",
        ServerLanguage.French: "Insigne du survivant",
        ServerLanguage.German: "Überlebende Befähigung",
        ServerLanguage.Italian: "Insegne del Superstite",
        ServerLanguage.Spanish: "Insignia de superviviente",
        ServerLanguage.TraditionalChinese: "生存 徽記",
        ServerLanguage.Japanese: "サバイバー 記章",
        ServerLanguage.Polish: "Symbol Przetrwania",
        ServerLanguage.Russian: "Survivor Insignia",
        ServerLanguage.BorkBorkBork: "Soorfeefur Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Survivor

class RadiantInsignia(Insignia):

    names = {
        ServerLanguage.English: "Radiant Insignia",
        ServerLanguage.Korean: "눈부신 휘장",
        ServerLanguage.French: "Insigne du rayonnement",
        ServerLanguage.German: "Radianten- Befähigung",
        ServerLanguage.Italian: "Insegne Radianti",
        ServerLanguage.Spanish: "Insignia radiante",
        ServerLanguage.TraditionalChinese: "閃耀 徽記",
        ServerLanguage.Japanese: "ラディアント 記章",
        ServerLanguage.Polish: "Symbol Promieni",
        ServerLanguage.Russian: "Radiant Insignia",
        ServerLanguage.BorkBorkBork: "Raedeeunt Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Radiant

class StalwartInsignia(Insignia):

    names = {
        ServerLanguage.English: "Stalwart Insignia",
        ServerLanguage.Korean: "튼튼한 휘장",
        ServerLanguage.French: "Insigne robuste",
        ServerLanguage.German: "Entschlossenheits- Befähigung",
        ServerLanguage.Italian: "Insegne della Robustezza",
        ServerLanguage.Spanish: "Insignia firme",
        ServerLanguage.TraditionalChinese: "健壯 徽記",
        ServerLanguage.Japanese: "スタルウォート 記章",
        ServerLanguage.Polish: "Symbol Stanowczości",
        ServerLanguage.Russian: "Stalwart Insignia",
        ServerLanguage.BorkBorkBork: "Staelvaert Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Stalwart
    property_identifiers = [
        ModifierIdentifier.ArmorPlusVsPhysical,
    ]

class BrawlersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Brawler's Insignia",
        ServerLanguage.Korean: "싸움꾼의 휘장",
        ServerLanguage.French: "Insigne de l'agitateur",
        ServerLanguage.German: "Raufbold- Befähigung",
        ServerLanguage.Italian: "Insegne da Lottatore",
        ServerLanguage.Spanish: "Insignia del pendenciero",
        ServerLanguage.TraditionalChinese: "鬥士 徽記",
        ServerLanguage.Japanese: "ブラウラー 記章",
        ServerLanguage.Polish: "Symbol Zapaśnika",
        ServerLanguage.Russian: "Brawler's Insignia",
        ServerLanguage.BorkBorkBork: "Braevler's Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Brawlers

class BlessedInsignia(Insignia):

    names = {
        ServerLanguage.English: "Blessed Insignia",
        ServerLanguage.Korean: "축복의 휘장",
        ServerLanguage.French: "Insigne de la bénédiction",
        ServerLanguage.German: "Segens Befähigung",
        ServerLanguage.Italian: "Insegne della Benedizione",
        ServerLanguage.Spanish: "Insignia con bendición",
        ServerLanguage.TraditionalChinese: "祝福 徽記",
        ServerLanguage.Japanese: "ブレス 記章",
        ServerLanguage.Polish: "Symbol Błogosławieństwa",
        ServerLanguage.Russian: "Blessed Insignia",
        ServerLanguage.BorkBorkBork: "Blessed Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Blessed

class HeraldsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Herald's Insignia",
        ServerLanguage.Korean: "전령의 휘장",
        ServerLanguage.French: "Insigne de héraut",
        ServerLanguage.German: "Herold- Befähigung",
        ServerLanguage.Italian: "Insegne da Araldo",
        ServerLanguage.Spanish: "Insignia de heraldo",
        ServerLanguage.TraditionalChinese: "先驅 徽記",
        ServerLanguage.Japanese: "ヘラルド 記章",
        ServerLanguage.Polish: "Symbol Herolda",
        ServerLanguage.Russian: "Herald's Insignia",
        ServerLanguage.BorkBorkBork: "Heraeld's Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Heralds

class SentrysInsignia(Insignia):

    names = {
        ServerLanguage.English: "Sentry's Insignia",
        ServerLanguage.Korean: "보초병의 휘장",
        ServerLanguage.French: "Insigne de factionnaire",
        ServerLanguage.German: "Wachposten- Befähigung",
        ServerLanguage.Italian: "Insegne da Sentinella",
        ServerLanguage.Spanish: "Insignia de centinela",
        ServerLanguage.TraditionalChinese: "哨兵 徽記",
        ServerLanguage.Japanese: "セントリー 記章",
        ServerLanguage.Polish: "Symbol Wartownika",
        ServerLanguage.Russian: "Sentry's Insignia",
        ServerLanguage.BorkBorkBork: "Sentry's Inseegneea",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Sentrys

class RuneOfMinorVigor(Rune):

    names = {
        ServerLanguage.English: "Rune of Minor Vigor",
        ServerLanguage.Korean: "룬(하급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus mineur)",
        ServerLanguage.German: "Rune d. kleineren Lebenskraft",
        ServerLanguage.Italian: "Runa Vigore di grado minore",
        ServerLanguage.Spanish: "Runa (vigor de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 活力 符文",
        ServerLanguage.Japanese: "ルーン (マイナー ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru niższego poziomu)",
        ServerLanguage.Russian: "Rune of Minor Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Meenur Feegur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorVigor

class RuneOfMinorVigor2(Rune):

    names = {
        ServerLanguage.English: "Rune of Minor Vigor",
        ServerLanguage.Korean: "룬(하급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus mineur)",
        ServerLanguage.German: "Rune d. kleineren Lebenskraft",
        ServerLanguage.Italian: "Runa Vigore di grado minore",
        ServerLanguage.Spanish: "Runa (vigor de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 活力 符文",
        ServerLanguage.Japanese: "ルーン (マイナー ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru niższego poziomu)",
        ServerLanguage.Russian: "Rune of Minor Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Meenur Feegur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorVigor2

class RuneOfVitae(Rune):

    names = {
        ServerLanguage.English: "Rune of Vitae",
        ServerLanguage.Korean: "룬(이력)",
        ServerLanguage.French: "Rune (de la vie)",
        ServerLanguage.German: "Rune d. Lebenskraft",
        ServerLanguage.Italian: "Runa della Vita",
        ServerLanguage.Spanish: "Runa (de vida)",
        ServerLanguage.TraditionalChinese: "生命 符文",
        ServerLanguage.Japanese: "ルーン (ヴィータ)",
        ServerLanguage.Polish: "Runa (Życia)",
        ServerLanguage.Russian: "Rune of Vitae",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Feetaee-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfVitae

class RuneOfAttunement(Rune):

    names = {
        ServerLanguage.English: "Rune of Attunement",
        ServerLanguage.Korean: "룬(조율)",
        ServerLanguage.French: "Rune (d'affinité)",
        ServerLanguage.German: "Rune d. Einstimmung",
        ServerLanguage.Italian: "Runa dell'Armonia",
        ServerLanguage.Spanish: "Runa (de sintonía)",
        ServerLanguage.TraditionalChinese: "調和 符文",
        ServerLanguage.Japanese: "ルーン (アチューン)",
        ServerLanguage.Polish: "Runa (Dostrojenia)",
        ServerLanguage.Russian: "Rune of Attunement",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Aettoonement",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfAttunement

class RuneOfMajorVigor(Rune):

    names = {
        ServerLanguage.English: "Rune of Major Vigor",
        ServerLanguage.Korean: "룬(상급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus majeur)",
        ServerLanguage.German: "Rune d. hohen Lebenskraft",
        ServerLanguage.Italian: "Runa Vigore di grado maggiore",
        ServerLanguage.Spanish: "Runa (vigor de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 活力 符文",
        ServerLanguage.Japanese: "ルーン (メジャー ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru wyższego poziomu)",
        ServerLanguage.Russian: "Rune of Major Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Maejur Feegur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorVigor

class RuneOfRecovery(Rune):

    names = {
        ServerLanguage.English: "Rune of Recovery",
        ServerLanguage.Korean: "룬(회복)",
        ServerLanguage.French: "Rune (de récupération)",
        ServerLanguage.German: "Rune d. Gesundung",
        ServerLanguage.Italian: "Runa della Ripresa",
        ServerLanguage.Spanish: "Runa (de mejoría)",
        ServerLanguage.TraditionalChinese: "恢復 符文",
        ServerLanguage.Japanese: "ルーン (リカバリー)",
        ServerLanguage.Polish: "Runa (Uzdrowienia)",
        ServerLanguage.Russian: "Rune of Recovery",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Recufery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfRecovery
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfRestoration(Rune):

    names = {
        ServerLanguage.English: "Rune of Restoration",
        ServerLanguage.Korean: "룬(복구)",
        ServerLanguage.French: "Rune (de rétablissement)",
        ServerLanguage.German: "Rune d. Wiederherstellung",
        ServerLanguage.Italian: "Runa del Ripristino",
        ServerLanguage.Spanish: "Runa (de restauración)",
        ServerLanguage.TraditionalChinese: "復原 符文",
        ServerLanguage.Japanese: "ルーン (レストレーション)",
        ServerLanguage.Polish: "Runa (Renowacji)",
        ServerLanguage.Russian: "Rune of Restoration",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Resturaeshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfRestoration
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfClarity(Rune):

    names = {
        ServerLanguage.English: "Rune of Clarity",
        ServerLanguage.Korean: "룬(명석)",
        ServerLanguage.French: "Rune (de la clarté)",
        ServerLanguage.German: "Rune d. Klarheit",
        ServerLanguage.Italian: "Runa della Trasparenza",
        ServerLanguage.Spanish: "Runa (de claridad)",
        ServerLanguage.TraditionalChinese: "澄澈 符文",
        ServerLanguage.Japanese: "ルーン (クラリティ)",
        ServerLanguage.Polish: "Runa (Jasności)",
        ServerLanguage.Russian: "Rune of Clarity",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Claereety",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfClarity
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfPurity(Rune):

    names = {
        ServerLanguage.English: "Rune of Purity",
        ServerLanguage.Korean: "룬(순수)",
        ServerLanguage.French: "Rune (de la pureté)",
        ServerLanguage.German: "Rune d. Reinheit",
        ServerLanguage.Italian: "Runa della Purezza",
        ServerLanguage.Spanish: "Runa (de pureza)",
        ServerLanguage.TraditionalChinese: "潔淨 符文",
        ServerLanguage.Japanese: "ルーン (ピュリティ)",
        ServerLanguage.Polish: "Runa (Czystości)",
        ServerLanguage.Russian: "Rune of Purity",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Pooreety",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfPurity
    property_identifiers = [
        ModifierIdentifier.ReduceConditionTupleDuration,
    ]

class RuneOfSuperiorVigor(Rune):

    names = {
        ServerLanguage.English: "Rune of Superior Vigor",
        ServerLanguage.Korean: "룬(고급 활력)",
        ServerLanguage.French: "Rune (Vigueur : bonus supérieur)",
        ServerLanguage.German: "Rune d. überlegenen Lebenskraft",
        ServerLanguage.Italian: "Runa Vigore di grado supremo",
        ServerLanguage.Spanish: "Runa (vigor de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 活力 符文",
        ServerLanguage.Japanese: "ルーン (スーペリア ビガー)",
        ServerLanguage.Polish: "Runa (Wigoru najwyższego poziomu)",
        ServerLanguage.Russian: "Rune of Superior Vigor",
        ServerLanguage.BorkBorkBork: "Roone-a ooff Soopereeur Feegur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorVigor
#endregion No Profession

#region Warrior

class KnightsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Knight's Insignia [Warrior]",
        ServerLanguage.Korean: "기사의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] de chevalier",
        ServerLanguage.German: "Ritter- [Krieger]-Befähigung",
        ServerLanguage.Italian: "Insegne [Guerriero] da Cavaliere",
        ServerLanguage.Spanish: "Insignia [Guerrero] de caballero",
        ServerLanguage.TraditionalChinese: "騎士 徽記 [戰士]",
        ServerLanguage.Japanese: "ナイト 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Rycerza",
        ServerLanguage.Russian: "Knight's Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Kneeght's Inseegneea [Vaerreeur]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Knights

class LieutenantsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Lieutenant's Insignia [Warrior]",
        ServerLanguage.Korean: "부관의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] du Lieutenant",
        ServerLanguage.German: "Leutnant- [Krieger]-Befähigung",
        ServerLanguage.Italian: "Insegne [Guerriero] da Luogotenente",
        ServerLanguage.Spanish: "Insignia [Guerrero] de teniente",
        ServerLanguage.TraditionalChinese: "副官 徽記 [戰士]",
        ServerLanguage.Japanese: "ルテナント 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Porucznika",
        ServerLanguage.Russian: "Lieutenant's Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Leeeootenunt's Inseegneea [Vaerreeur]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Lieutenants

class StonefistInsignia(Insignia):

    names = {
        ServerLanguage.English: "Stonefist Insignia [Warrior]",
        ServerLanguage.Korean: "돌주먹의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] Poing-de-fer",
        ServerLanguage.German: "Steinfaust- [Krieger]-Befähigung",
        ServerLanguage.Italian: "Insegne [Guerriero] di Pietra",
        ServerLanguage.Spanish: "Insignia [Guerrero] de piedra",
        ServerLanguage.TraditionalChinese: "石拳 徽記 [戰士]",
        ServerLanguage.Japanese: "ストーンフィスト 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Kamiennej Pięści",
        ServerLanguage.Russian: "Stonefist Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Stuneffeest Inseegneea [Vaerreeur]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Stonefist

class DreadnoughtInsignia(Insignia):

    names = {
        ServerLanguage.English: "Dreadnought Insignia [Warrior]",
        ServerLanguage.Korean: "용자의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] de Dreadnaught",
        ServerLanguage.German: "Panzerschiff- [Krieger]-Befähigung",
        ServerLanguage.Italian: "Insegne [Guerriero] da Dreadnought",
        ServerLanguage.Spanish: "Insignia [Guerrero] de Dreadnought",
        ServerLanguage.TraditionalChinese: "無懼 徽記 [戰士]",
        ServerLanguage.Japanese: "ドレッドノート 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Pancernika",
        ServerLanguage.Russian: "Dreadnought Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Dreaednuooght Inseegneea [Vaerreeur]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Dreadnought

class SentinelsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Sentinel's Insignia [Warrior]",
        ServerLanguage.Korean: "감시병의 휘장 [워리어]",
        ServerLanguage.French: "Insigne [Guerrier] de sentinelle",
        ServerLanguage.German: "Wächter- [Krieger]-Befähigung",
        ServerLanguage.Italian: "Insegne [Guerriero] da Sentinella",
        ServerLanguage.Spanish: "Insignia [Guerrero] de centinela",
        ServerLanguage.TraditionalChinese: "警戒 徽記 [戰士]",
        ServerLanguage.Japanese: "センチネル 記章 [ウォーリア]",
        ServerLanguage.Polish: "[Wojownik] Symbol Strażnika",
        ServerLanguage.Russian: "Sentinel's Insignia [Warrior]",
        ServerLanguage.BorkBorkBork: "Senteenel's Inseegneea [Vaerreeur]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Sentinels

class WarriorRuneOfMinorAbsorption(Rune):

    names = {
        ServerLanguage.English: "Warrior Rune of Minor Absorption",
        ServerLanguage.Korean: "워리어 룬(하급 흡수)",
        ServerLanguage.French: "Rune de Guerrier (Absorption : bonus mineur)",
        ServerLanguage.German: "Krieger-Rune d. kleineren Absorption",
        ServerLanguage.Italian: "Runa del Guerriero Assorbimento di grado minore",
        ServerLanguage.Spanish: "Runa de Guerrero (absorción de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 吸收 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー アブソープション)",
        ServerLanguage.Polish: "Runa Wojownika (Pochłaniania niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Absorption",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Aebsurpshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorAbsorption

class WarriorRuneOfMinorTactics(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Minor Tactics",
        ServerLanguage.Korean: "워리어 룬(하급 전술)",
        ServerLanguage.French: "Rune de Guerrier (Tactique : bonus mineur)",
        ServerLanguage.German: "Krieger-Rune d. kleineren Taktik",
        ServerLanguage.Italian: "Runa del Guerriero Tattica di grado minore",
        ServerLanguage.Spanish: "Runa de Guerrero (Táctica de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 戰術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー タクティクス)",
        ServerLanguage.Polish: "Runa Wojownika (Taktyka niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Tactics",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Taecteecs",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorTactics

class WarriorRuneOfMinorStrength(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Minor Strength",
        ServerLanguage.Korean: "워리어 룬(하급 강인함)",
        ServerLanguage.French: "Rune de Guerrier (Force : bonus mineur)",
        ServerLanguage.German: "Krieger-Rune d. kleineren Stärke",
        ServerLanguage.Italian: "Runa del Guerriero Forza di grado minore",
        ServerLanguage.Spanish: "Runa de Guerrero (Fuerza de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 力量 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー ストレングス)",
        ServerLanguage.Polish: "Runa Wojownika (Siła niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Strength",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Strengt",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorStrength

class WarriorRuneOfMinorAxeMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Minor Axe Mastery",
        ServerLanguage.Korean: "워리어 룬(하급 도끼술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise de la hache : bonus mineur)",
        ServerLanguage.German: "Krieger-Rune d. kleineren Axtbeherrschung",
        ServerLanguage.Italian: "Runa del Guerriero Abilità con l'Ascia di grado minore",
        ServerLanguage.Spanish: "Runa de Guerrero (Dominio del hacha de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 精通斧術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー アックス マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Toporach niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Axe Mastery",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Aexe-a Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorAxeMastery

class WarriorRuneOfMinorHammerMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Minor Hammer Mastery",
        ServerLanguage.Korean: "워리어 룬(하급 해머술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise du marteau : bonus mineur)",
        ServerLanguage.German: "Krieger-Rune d. kleineren Hammerbeherrschung",
        ServerLanguage.Italian: "Runa del Guerriero Abilità col Martello di grado minore",
        ServerLanguage.Spanish: "Runa de Guerrero (Dominio del martillo de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 精通鎚術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー ハンマー マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Młotach niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Hammer Mastery",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Haemmer Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorHammerMastery

class WarriorRuneOfMinorSwordsmanship(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Minor Swordsmanship",
        ServerLanguage.Korean: "워리어 룬(하급 검술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise de l'épée : bonus mineur)",
        ServerLanguage.German: "Krieger-Rune d. kleineren Schwertkunst",
        ServerLanguage.Italian: "Runa del Guerriero Scherma di grado minore",
        ServerLanguage.Spanish: "Runa de Guerrero (Esgrima de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 精通劍術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (マイナー ソード マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Mieczach niższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Minor Swordsmanship",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Meenur Svurdsmunsheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSwordsmanship

class WarriorRuneOfMajorAbsorption(Rune):

    names = {
        ServerLanguage.English: "Warrior Rune of Major Absorption",
        ServerLanguage.Korean: "워리어 룬(상급 흡수)",
        ServerLanguage.French: "Rune de Guerrier (Absorption : bonus majeur)",
        ServerLanguage.German: "Krieger-Rune d. hohen Absorption",
        ServerLanguage.Italian: "Runa del Guerriero Assorbimento di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guerrero (absorción de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 吸收 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー アブソープション)",
        ServerLanguage.Polish: "Runa Wojownika (Pochłaniania wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Absorption",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Aebsurpshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorAbsorption

class WarriorRuneOfMajorTactics(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Major Tactics",
        ServerLanguage.Korean: "워리어 룬(상급 전술)",
        ServerLanguage.French: "Rune de Guerrier (Tactique : bonus majeur)",
        ServerLanguage.German: "Krieger-Rune d. hohen Taktik",
        ServerLanguage.Italian: "Runa del Guerriero Tattica di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guerrero (Táctica de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 戰術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー タクティクス)",
        ServerLanguage.Polish: "Runa Wojownika (Taktyka wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Tactics",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Taecteecs",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorTactics
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfMajorStrength(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Major Strength",
        ServerLanguage.Korean: "워리어 룬(상급 강인함)",
        ServerLanguage.French: "Rune de Guerrier (Force : bonus majeur)",
        ServerLanguage.German: "Krieger-Rune d. hohen Stärke",
        ServerLanguage.Italian: "Runa del Guerriero Forza di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guerrero (Fuerza de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 力量 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー ストレングス)",
        ServerLanguage.Polish: "Runa Wojownika (Siła wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Strength",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Strengt",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorStrength
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfMajorAxeMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Major Axe Mastery",
        ServerLanguage.Korean: "워리어 룬(상급 도끼술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise de la hache : bonus majeur)",
        ServerLanguage.German: "Krieger-Rune d. hohen Axtbeherrschung",
        ServerLanguage.Italian: "Runa del Guerriero Abilità con l'Ascia di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guerrero (Dominio del hacha de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 精通斧術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー アックス マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Toporach wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Axe Mastery",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Aexe-a Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorAxeMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfMajorHammerMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Major Hammer Mastery",
        ServerLanguage.Korean: "워리어 룬(상급 해머술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise du marteau : bonus majeur)",
        ServerLanguage.German: "Krieger-Rune d. hohen Hammerbeherrschung",
        ServerLanguage.Italian: "Runa del Guerriero Abilità col Martello di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guerrero (Dominio del martillo de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 精通鎚術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー ハンマー マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Młotach wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Hammer Mastery",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Haemmer Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorHammerMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfMajorSwordsmanship(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Major Swordsmanship",
        ServerLanguage.Korean: "워리어 룬(상급 검술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise de l'épée : bonus majeur)",
        ServerLanguage.German: "Krieger-Rune d. hohen Schwertkunst",
        ServerLanguage.Italian: "Runa del Guerriero Scherma di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guerrero (Esgrima de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 精通劍術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (メジャー ソード マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Mieczach wyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Major Swordsmanship",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Maejur Svurdsmunsheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSwordsmanship
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfSuperiorAbsorption(Rune):

    names = {
        ServerLanguage.English: "Warrior Rune of Superior Absorption",
        ServerLanguage.Korean: "워리어 룬(고급 흡수)",
        ServerLanguage.French: "Rune de Guerrier (Absorption : bonus supérieur)",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Absorption",
        ServerLanguage.Italian: "Runa del Guerriero Assorbimento di grado supremo",
        ServerLanguage.Spanish: "Runa de Guerrero (absorción de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 吸收 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア アブソープション)",
        ServerLanguage.Polish: "Runa Wojownika (Pochłaniania najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Absorption",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Aebsurpshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorAbsorption

class WarriorRuneOfSuperiorTactics(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Superior Tactics",
        ServerLanguage.Korean: "워리어 룬(고급 전술)",
        ServerLanguage.French: "Rune de Guerrier (Tactique : bonus supérieur)",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Taktik",
        ServerLanguage.Italian: "Runa del Guerriero Tattica di grado supremo",
        ServerLanguage.Spanish: "Runa de Guerrero (Táctica de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 戰術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア タクティクス)",
        ServerLanguage.Polish: "Runa Wojownika (Taktyka najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Tactics",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Taecteecs",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorTactics
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfSuperiorStrength(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Superior Strength",
        ServerLanguage.Korean: "워리어 룬(고급 강인함)",
        ServerLanguage.French: "Rune de Guerrier (Force : bonus supérieur)",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Stärke",
        ServerLanguage.Italian: "Runa del Guerriero Forza di grado supremo",
        ServerLanguage.Spanish: "Runa de Guerrero (Fuerza de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 力量 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア ストレングス)",
        ServerLanguage.Polish: "Runa Wojownika (Siła najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Strength",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Strengt",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorStrength
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfSuperiorAxeMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Superior Axe Mastery",
        ServerLanguage.Korean: "워리어 룬(고급 도끼술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise de la hache : bonus supérieur)",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Axtbeherrschung",
        ServerLanguage.Italian: "Runa del Guerriero Abilità con l'Ascia di grado supremo",
        ServerLanguage.Spanish: "Runa de Guerrero (Dominio del hacha de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 精通斧術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア アックス マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Toporach najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Axe Mastery",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Aexe-a Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorAxeMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfSuperiorHammerMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Superior Hammer Mastery",
        ServerLanguage.Korean: "워리어 룬(고급 해머술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise du marteau : bonus supérieur)",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Hammerbeherrschung",
        ServerLanguage.Italian: "Runa del Guerriero Abilità col Martello di grado supremo",
        ServerLanguage.Spanish: "Runa de Guerrero (Dominio del martillo de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 精通鎚術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア ハンマー マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Młotach najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Hammer Mastery",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Haemmer Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorHammerMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class WarriorRuneOfSuperiorSwordsmanship(AttributeRune):

    names = {
        ServerLanguage.English: "Warrior Rune of Superior Swordsmanship",
        ServerLanguage.Korean: "워리어 룬(고급 검술)",
        ServerLanguage.French: "Rune de Guerrier (Maîtrise de l'épée : bonus supérieur)",
        ServerLanguage.German: "Krieger-Rune d. überlegenen Schwertkunst",
        ServerLanguage.Italian: "Runa del Guerriero Scherma di grado supremo",
        ServerLanguage.Spanish: "Runa de Guerrero (Esgrima de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 精通劍術 戰士符文",
        ServerLanguage.Japanese: "ウォーリア ルーン (スーペリア ソード マスタリー)",
        ServerLanguage.Polish: "Runa Wojownika (Biegłość w Mieczach najwyższego poziomu)",
        ServerLanguage.Russian: "Warrior Rune of Superior Swordsmanship",
        ServerLanguage.BorkBorkBork: "Vaerreeur Roone-a ooff Soopereeur Svurdsmunsheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSwordsmanship
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Warrior

class UpgradeMajorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Warrior

class UpgradeSuperiorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Warrior

class AppliesToMinorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Warrior

class AppliesToMajorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Warrior

class AppliesToSuperiorRuneWarrior(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Warrior
#endregion Warrior

#region Ranger

class FrostboundInsignia(Insignia):

    names = {
        ServerLanguage.English: "Frostbound Insignia [Ranger]",
        ServerLanguage.Korean: "얼음결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] de givre",
        ServerLanguage.German: "Permafrost- [Waldläufer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Esploratore] da Ghiaccio",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de montaña",
        ServerLanguage.TraditionalChinese: "霜縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "フロストバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Lód",
        ServerLanguage.Russian: "Frostbound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Frustbuoond Inseegneea [Runger]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Frostbound

class PyreboundInsignia(Insignia):

    names = {
        ServerLanguage.English: "Pyrebound Insignia [Ranger]",
        ServerLanguage.Korean: "화염결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] du bûcher",
        ServerLanguage.German: "Scheiterhaufen- [Waldläufer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Esploratore] da Rogo",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de leñero",
        ServerLanguage.TraditionalChinese: "火縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "パイアーバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Ogień",
        ServerLanguage.Russian: "Pyrebound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Pyrebuoond Inseegneea [Runger]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Pyrebound

class StormboundInsignia(Insignia):

    names = {
        ServerLanguage.English: "Stormbound Insignia [Ranger]",
        ServerLanguage.Korean: "폭풍결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] de tonnerre",
        ServerLanguage.German: "Unwetter- [Waldläufer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Esploratore] da Bufera",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de hidromántico",
        ServerLanguage.TraditionalChinese: "風縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "ストームバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Sztorm",
        ServerLanguage.Russian: "Stormbound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Sturmbuoond Inseegneea [Runger]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Stormbound

class ScoutsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Scout's Insignia [Ranger]",
        ServerLanguage.Korean: "정찰병의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] d'éclaireur",
        ServerLanguage.German: "Späher- [Waldläufer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Esploratore] da Perlustratore",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de explorador",
        ServerLanguage.TraditionalChinese: "偵查者 徽記 [遊俠]",
        ServerLanguage.Japanese: "スカウト 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Zwiadowcy",
        ServerLanguage.Russian: "Scout's Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Scuoot's Inseegneea [Runger]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Scouts

class EarthboundInsignia(Insignia):

    names = {
        ServerLanguage.English: "Earthbound Insignia [Ranger]",
        ServerLanguage.Korean: "대지결계의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] terrestre",
        ServerLanguage.German: "Erdbindungs- [Waldläufer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Esploratore] da Terra",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de tierra",
        ServerLanguage.TraditionalChinese: "地縛 徽記 [遊俠]",
        ServerLanguage.Japanese: "アースバウンド 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Spętanego przez Ziemię",
        ServerLanguage.Russian: "Earthbound Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Iaerthbuoond Inseegneea [Runger]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Earthbound

class BeastmastersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Beastmaster's Insignia [Ranger]",
        ServerLanguage.Korean: "조련사의 휘장 [레인저]",
        ServerLanguage.French: "Insigne [Rôdeur] de belluaire",
        ServerLanguage.German: "Tierbändiger- [Waldläufer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Esploratore] da Domatore",
        ServerLanguage.Spanish: "Insignia [Guardabosques] de domador",
        ServerLanguage.TraditionalChinese: "野獸大師 徽記 [遊俠]",
        ServerLanguage.Japanese: "ビーストマスター 記章 [レンジャー]",
        ServerLanguage.Polish: "[Łowca] Symbol Władcy Zwierząt",
        ServerLanguage.Russian: "Beastmaster's Insignia [Ranger]",
        ServerLanguage.BorkBorkBork: "Beaestmaester's Inseegneea [Runger]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Beastmasters

class RangerRuneOfMinorWildernessSurvival(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Minor Wilderness Survival",
        ServerLanguage.Korean: "레인저 룬(하급 생존술)",
        ServerLanguage.French: "Rune de Rôdeur (Survie : bonus mineur)",
        ServerLanguage.German: "Waldläufer-Rune d. kleineren Überleben in der Wildnis",
        ServerLanguage.Italian: "Runa dell'Esploratore Sopravvivenza nella Natura di grado minore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Supervivencia naturaleza de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 求生 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (マイナー サバイバル)",
        ServerLanguage.Polish: "Runa Łowcy (Przetrwanie w Dziczy niższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Minor Wilderness Survival",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Meenur Veelderness Soorfeefael",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorWildernessSurvival

class RangerRuneOfMinorExpertise(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Minor Expertise",
        ServerLanguage.Korean: "레인저 룬(하급 전문성)",
        ServerLanguage.French: "Rune de Rôdeur (Expertise : bonus mineur)",
        ServerLanguage.German: "Waldläufer-Rune d. kleineren Fachkenntnis",
        ServerLanguage.Italian: "Runa dell'Esploratore Esperienza di grado minore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Pericia de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 專精 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (マイナー エキスパーティーズ)",
        ServerLanguage.Polish: "Runa Łowcy (Specjalizacja niższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Minor Expertise",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Meenur Ixperteese-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorExpertise

class RangerRuneOfMinorBeastMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Minor Beast Mastery",
        ServerLanguage.Korean: "레인저 룬(하급 동물 친화)",
        ServerLanguage.French: "Rune de Rôdeur (Domptage : bonus mineur)",
        ServerLanguage.German: "Waldläufer-Rune d. kleineren Tierbeherrschung",
        ServerLanguage.Italian: "Runa dell'Esploratore Potere sulle Belve di grado minore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Dominio de bestias de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 野獸支配 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (マイナー ビースト マスタリー)",
        ServerLanguage.Polish: "Runa Łowcy (Panowanie nad Zwierzętami niższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Minor Beast Mastery",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Meenur Beaest Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorBeastMastery

class RangerRuneOfMinorMarksmanship(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Minor Marksmanship",
        ServerLanguage.Korean: "레인저 룬(하급 궁술)",
        ServerLanguage.French: "Rune de Rôdeur (Adresse au tir : bonus mineur)",
        ServerLanguage.German: "Waldläufer-Rune d. kleineren Treffsicherheit",
        ServerLanguage.Italian: "Runa dell'Esploratore Precisione di grado minore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Puntería de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 弓術精通 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (マイナー ボウ マスタリー)",
        ServerLanguage.Polish: "Runa Łowcy (Umiejętności Strzeleckie niższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Minor Marksmanship",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Meenur Maerksmunsheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorMarksmanship

class RangerRuneOfMajorWildernessSurvival(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Major Wilderness Survival",
        ServerLanguage.Korean: "레인저 룬(상급 생존술)",
        ServerLanguage.French: "Rune de Rôdeur (Survie : bonus majeur)",
        ServerLanguage.German: "Waldläufer-Rune d. hohen Überleben in der Wildnis",
        ServerLanguage.Italian: "Runa dell'Esploratore Sopravvivenza nella Natura di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Supervivencia naturaleza de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 求生 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (メジャー サバイバル)",
        ServerLanguage.Polish: "Runa Łowcy (Przetrwanie w Dziczy wyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Major Wilderness Survival",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Maejur Veelderness Soorfeefael",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorWildernessSurvival
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfMajorExpertise(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Major Expertise",
        ServerLanguage.Korean: "레인저 룬(상급 전문성)",
        ServerLanguage.French: "Rune de Rôdeur (Expertise : bonus majeur)",
        ServerLanguage.German: "Waldläufer-Rune d. hohen Fachkenntnis",
        ServerLanguage.Italian: "Runa dell'Esploratore Esperienza di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Pericia de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 專精 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (メジャー エキスパーティーズ)",
        ServerLanguage.Polish: "Runa Łowcy (Specjalizacja wyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Major Expertise",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Maejur Ixperteese-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorExpertise
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfMajorBeastMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Major Beast Mastery",
        ServerLanguage.Korean: "레인저 룬(상급 동물 친화)",
        ServerLanguage.French: "Rune de Rôdeur (Domptage : bonus majeur)",
        ServerLanguage.German: "Waldläufer-Rune d. hohen Tierbeherrschung",
        ServerLanguage.Italian: "Runa dell'Esploratore Potere sulle Belve di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Dominio de bestias de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 野獸支配 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (メジャー ビースト マスタリー)",
        ServerLanguage.Polish: "Runa Łowcy (Panowanie nad Zwierzętami wyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Major Beast Mastery",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Maejur Beaest Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorBeastMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfMajorMarksmanship(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Major Marksmanship",
        ServerLanguage.Korean: "레인저 룬(상급 궁술)",
        ServerLanguage.French: "Rune de Rôdeur (Adresse au tir : bonus majeur)",
        ServerLanguage.German: "Waldläufer-Rune d. hohen Treffsicherheit",
        ServerLanguage.Italian: "Runa dell'Esploratore Precisione di grado maggiore",
        ServerLanguage.Spanish: "Runa de Guardabosques (Puntería de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 弓術精通 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (メジャー ボウ マスタリー)",
        ServerLanguage.Polish: "Runa Łowcy (Umiejętności Strzeleckie wyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Major Marksmanship",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Maejur Maerksmunsheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorMarksmanship
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfSuperiorWildernessSurvival(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Superior Wilderness Survival",
        ServerLanguage.Korean: "레인저 룬(고급 생존술)",
        ServerLanguage.French: "Rune de Rôdeur (Survie : bonus supérieur)",
        ServerLanguage.German: "Waldläufer-Rune d. überlegenen Überleben in der Wildnis",
        ServerLanguage.Italian: "Runa dell'Esploratore Sopravvivenza nella Natura di grado supremo",
        ServerLanguage.Spanish: "Runa de Guardabosques (Supervivencia naturaleza de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 求生 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (スーペリア サバイバル)",
        ServerLanguage.Polish: "Runa Łowcy (Przetrwanie w Dziczy najwyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Superior Wilderness Survival",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Soopereeur Veelderness Soorfeefael",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorWildernessSurvival
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfSuperiorExpertise(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Superior Expertise",
        ServerLanguage.Korean: "레인저 룬(고급 전문성)",
        ServerLanguage.French: "Rune de Rôdeur (Expertise : bonus supérieur)",
        ServerLanguage.German: "Waldläufer-Rune d. überlegenen Fachkenntnis",
        ServerLanguage.Italian: "Runa dell'Esploratore Esperienza di grado supremo",
        ServerLanguage.Spanish: "Runa de Guardabosques (Pericia de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 專精 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (スーペリア エキスパーティーズ)",
        ServerLanguage.Polish: "Runa Łowcy (Specjalizacja najwyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Superior Expertise",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Soopereeur Ixperteese-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorExpertise
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfSuperiorBeastMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Superior Beast Mastery",
        ServerLanguage.Korean: "레인저 룬(고급 동물 친화)",
        ServerLanguage.French: "Rune de Rôdeur (Domptage : bonus supérieur)",
        ServerLanguage.German: "Waldläufer-Rune d. überlegenen Tierbeherrschung",
        ServerLanguage.Italian: "Runa dell'Esploratore Potere sulle Belve di grado supremo",
        ServerLanguage.Spanish: "Runa de Guardabosques (Dominio de bestias de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 野獸支配 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (スーペリア ビースト マスタリー)",
        ServerLanguage.Polish: "Runa Łowcy (Panowanie nad Zwierzętami najwyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Superior Beast Mastery",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Soopereeur Beaest Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorBeastMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RangerRuneOfSuperiorMarksmanship(AttributeRune):

    names = {
        ServerLanguage.English: "Ranger Rune of Superior Marksmanship",
        ServerLanguage.Korean: "레인저 룬(고급 궁술)",
        ServerLanguage.French: "Rune de Rôdeur (Adresse au tir : bonus supérieur)",
        ServerLanguage.German: "Waldläufer-Rune d. überlegenen Treffsicherheit",
        ServerLanguage.Italian: "Runa dell'Esploratore Precisione di grado supremo",
        ServerLanguage.Spanish: "Runa de Guardabosques (Puntería de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 弓術精通 遊俠符文",
        ServerLanguage.Japanese: "レンジャー ルーン (スーペリア ボウ マスタリー)",
        ServerLanguage.Polish: "Runa Łowcy (Umiejętności Strzeleckie najwyższego poziomu)",
        ServerLanguage.Russian: "Ranger Rune of Superior Marksmanship",
        ServerLanguage.BorkBorkBork: "Runger Roone-a ooff Soopereeur Maerksmunsheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorMarksmanship
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Ranger

class UpgradeMajorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Ranger

class UpgradeSuperiorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Ranger

class AppliesToMinorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Ranger

class AppliesToMajorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Ranger

class AppliesToSuperiorRuneRanger(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Ranger
#endregion Ranger

#region Monk

class WanderersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Wanderer's Insignia [Monk]",
        ServerLanguage.Korean: "방랑자의 휘장 [몽크]",
        ServerLanguage.French: "Insigne [Moine] de vagabond",
        ServerLanguage.German: "Wanderer- [Mönchs]-Befähigung",
        ServerLanguage.Italian: "Insegne [Mistico] da Vagabondo",
        ServerLanguage.Spanish: "Insignia [Monje] de trotamundos",
        ServerLanguage.TraditionalChinese: "流浪者 徽記 [僧侶]",
        ServerLanguage.Japanese: "ワンダラー 記章 [モンク]",
        ServerLanguage.Polish: "[Mnich] Symbol Wędrowca",
        ServerLanguage.Russian: "Wanderer's Insignia [Monk]",
        ServerLanguage.BorkBorkBork: "Vunderer's Inseegneea [Munk]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Wanderers

class DisciplesInsignia(Insignia):

    names = {
        ServerLanguage.English: "Disciple's Insignia [Monk]",
        ServerLanguage.Korean: "사도의 휘장 [몽크]",
        ServerLanguage.French: "Insigne [Moine] de disciple",
        ServerLanguage.German: "Jünger- [Mönchs]-Befähigung",
        ServerLanguage.Italian: "Insegne [Mistico] da Discepolo",
        ServerLanguage.Spanish: "Insignia [Monje] de discípulo",
        ServerLanguage.TraditionalChinese: "門徒 徽記 [僧侶]",
        ServerLanguage.Japanese: "ディサイプル 記章 [モンク]",
        ServerLanguage.Polish: "[Mnich] Symbol Ucznia",
        ServerLanguage.Russian: "Disciple's Insignia [Monk]",
        ServerLanguage.BorkBorkBork: "Deesceeple-a's Inseegneea [Munk]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Disciples

class AnchoritesInsignia(Insignia):

    names = {
        ServerLanguage.English: "Anchorite's Insignia [Monk]",
        ServerLanguage.Korean: "은둔자의 휘장 [몽크]",
        ServerLanguage.French: "Insigne [Moine] d'anachorète",
        ServerLanguage.German: "Einsiedler- [Mönchs]-Befähigung",
        ServerLanguage.Italian: "Insegne [Mistico] da Anacoreta",
        ServerLanguage.Spanish: "Insignia [Monje] de anacoreta",
        ServerLanguage.TraditionalChinese: "隱士 徽記 [僧侶]",
        ServerLanguage.Japanese: "アンコライト 記章 [モンク]",
        ServerLanguage.Polish: "[Mnich] Symbol Pustelnika",
        ServerLanguage.Russian: "Anchorite's Insignia [Monk]",
        ServerLanguage.BorkBorkBork: "Unchureete-a's Inseegneea [Munk]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Anchorites

class MonkRuneOfMinorHealingPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Minor Healing Prayers",
        ServerLanguage.Korean: "몽크 룬(하급 치유)",
        ServerLanguage.French: "Rune de Moine (Prières de guérison : bonus mineur)",
        ServerLanguage.German: "Mönch-Rune d. kleineren Heilgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Curative di grado minore",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias curativas de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 治療祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (マイナー ヒーリング)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Uzdrawiające niższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Minor Healing Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Meenur Heaeleeng Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorHealingPrayers

class MonkRuneOfMinorSmitingPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Minor Smiting Prayers",
        ServerLanguage.Korean: "몽크 룬(하급 천벌)",
        ServerLanguage.French: "Rune de Moine (Prières de châtiment : bonus mineur)",
        ServerLanguage.German: "Mönch-Rune d. kleineren Peinigungsgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Punitive di grado minore",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias de ataque de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 懲戒祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (マイナー ホーリー)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Ofensywne niższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Minor Smiting Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Meenur Smeeteeng Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSmitingPrayers

class MonkRuneOfMinorProtectionPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Minor Protection Prayers",
        ServerLanguage.Korean: "몽크 룬(하급 보호)",
        ServerLanguage.French: "Rune de Moine (Prières de protection : bonus mineur)",
        ServerLanguage.German: "Mönch-Rune d. kleineren Schutzgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Protettive di grado minore",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias de protección de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 防護祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (マイナー プロテクション)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Ochronne niższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Minor Protection Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Meenur Prutecshun Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorProtectionPrayers

class MonkRuneOfMinorDivineFavor(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Minor Divine Favor",
        ServerLanguage.Korean: "몽크 룬(하급 신의 은총)",
        ServerLanguage.French: "Rune de Moine (Faveur divine : bonus mineur)",
        ServerLanguage.German: "Mönch-Rune d. kleineren Gunst der Götter",
        ServerLanguage.Italian: "Runa del Mistico Favore Divino di grado minore",
        ServerLanguage.Spanish: "Runa de Monje (Favor divino de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 神恩 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (マイナー ディヴァイン)",
        ServerLanguage.Polish: "Runa Mnicha (Łaska Bogów niższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Minor Divine Favor",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Meenur Deefeene-a Faefur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDivineFavor

class MonkRuneOfMajorHealingPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Major Healing Prayers",
        ServerLanguage.Korean: "몽크 룬(상급 치유)",
        ServerLanguage.French: "Rune de Moine (Prières de guérison : bonus majeur)",
        ServerLanguage.German: "Mönch-Rune d. hohen Heilgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Curative di grado maggiore",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias curativas de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 治療祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (メジャー ヒーリング)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Uzdrawiające wyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Major Healing Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Maejur Heaeleeng Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorHealingPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfMajorSmitingPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Major Smiting Prayers",
        ServerLanguage.Korean: "몽크 룬(상급 천벌)",
        ServerLanguage.French: "Rune de Moine (Prières de châtiment : bonus majeur)",
        ServerLanguage.German: "Mönch-Rune d. hohen Peinigungsgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Punitive di grado maggiore",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias de ataque de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 懲戒祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (メジャー ホーリー)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Ofensywne wyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Major Smiting Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Maejur Smeeteeng Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSmitingPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfMajorProtectionPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Major Protection Prayers",
        ServerLanguage.Korean: "몽크 룬(상급 보호)",
        ServerLanguage.French: "Rune de Moine (Prières de protection : bonus majeur)",
        ServerLanguage.German: "Mönch-Rune d. hohen Schutzgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Protettive di grado maggiore",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias de protección de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 防護祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (メジャー プロテクション)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Ochronne wyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Major Protection Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Maejur Prutecshun Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorProtectionPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfMajorDivineFavor(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Major Divine Favor",
        ServerLanguage.Korean: "몽크 룬(상급 신의 은총)",
        ServerLanguage.French: "Rune de Moine (Faveur divine : bonus majeur)",
        ServerLanguage.German: "Mönch-Rune d. hohen Gunst der Götter",
        ServerLanguage.Italian: "Runa del Mistico Favore Divino di grado maggiore",
        ServerLanguage.Spanish: "Runa de Monje (Favor divino de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 神恩 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (メジャー ディヴァイン)",
        ServerLanguage.Polish: "Runa Mnicha (Łaska Bogów wyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Major Divine Favor",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Maejur Deefeene-a Faefur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDivineFavor
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfSuperiorHealingPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Superior Healing Prayers",
        ServerLanguage.Korean: "몽크 룬(고급 치유)",
        ServerLanguage.French: "Rune de Moine (Prières de guérison : bonus supérieur)",
        ServerLanguage.German: "Mönch-Rune d. überlegenen Heilgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Curative di grado supremo",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias curativas de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 治療祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (スーペリア ヒーリング)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Uzdrawiające najwyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Superior Healing Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Soopereeur Heaeleeng Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorHealingPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfSuperiorSmitingPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Superior Smiting Prayers",
        ServerLanguage.Korean: "몽크 룬(고급 천벌)",
        ServerLanguage.French: "Rune de Moine (Prières de châtiment : bonus supérieur)",
        ServerLanguage.German: "Mönch-Rune d. überlegenen Peinigungsgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Punitive di grado supremo",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias de ataque de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 懲戒祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (スーペリア ホーリー)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Ofensywne najwyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Superior Smiting Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Soopereeur Smeeteeng Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSmitingPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfSuperiorProtectionPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Superior Protection Prayers",
        ServerLanguage.Korean: "몽크 룬(고급 보호)",
        ServerLanguage.French: "Rune de Moine (Prières de protection : bonus supérieur)",
        ServerLanguage.German: "Mönch-Rune d. überlegenen Schutzgebete",
        ServerLanguage.Italian: "Runa del Mistico Preghiere Protettive di grado supremo",
        ServerLanguage.Spanish: "Runa de Monje (Plegarias de protección de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 防護祈禱 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (スーペリア プロテクション)",
        ServerLanguage.Polish: "Runa Mnicha (Modlitwy Ochronne najwyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Superior Protection Prayers",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Soopereeur Prutecshun Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorProtectionPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MonkRuneOfSuperiorDivineFavor(AttributeRune):

    names = {
        ServerLanguage.English: "Monk Rune of Superior Divine Favor",
        ServerLanguage.Korean: "몽크 룬(고급 신의 은총)",
        ServerLanguage.French: "Rune de Moine (Faveur divine : bonus supérieur)",
        ServerLanguage.German: "Mönch-Rune d. überlegenen Gunst der Götter",
        ServerLanguage.Italian: "Runa del Mistico Favore Divino di grado supremo",
        ServerLanguage.Spanish: "Runa de Monje (Favor divino de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 神恩 僧侶符文",
        ServerLanguage.Japanese: "モンク ルーン (スーペリア ディヴァイン)",
        ServerLanguage.Polish: "Runa Mnicha (Łaska Bogów najwyższego poziomu)",
        ServerLanguage.Russian: "Monk Rune of Superior Divine Favor",
        ServerLanguage.BorkBorkBork: "Munk Roone-a ooff Soopereeur Deefeene-a Faefur",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDivineFavor
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Monk

class UpgradeMajorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Monk

class UpgradeSuperiorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Monk

class AppliesToMinorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Monk

class AppliesToMajorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Monk

class AppliesToSuperiorRuneMonk(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Monk
#endregion Monk

#region Necromancer

class BloodstainedInsignia(Insignia):

    names = {
        ServerLanguage.English: "Bloodstained Insignia [Necromancer]",
        ServerLanguage.Korean: "혈흔의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de Sang",
        ServerLanguage.German: "Blutfleck- [Nekromanten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Negromante] di Sangue",
        ServerLanguage.Spanish: "Insignia [Nigromante] con sangre",
        ServerLanguage.TraditionalChinese: "血腥 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ブラッドステイン 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Okrwawienia",
        ServerLanguage.Russian: "Bloodstained Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Bluudstaeeened Inseegneea [Necrumuncer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Bloodstained

class TormentorsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Tormentor's Insignia [Necromancer]",
        ServerLanguage.Korean: "고문가의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de persécuteur",
        ServerLanguage.German: "Folterer- [Nekromanten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Negromante] da Tormentatore",
        ServerLanguage.Spanish: "Insignia [Nigromante] de torturador",
        ServerLanguage.TraditionalChinese: "苦痛者 徽記 [死靈法師]",
        ServerLanguage.Japanese: "トルメンター 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Oprawcy",
        ServerLanguage.Russian: "Tormentor's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Turmentur's Inseegneea [Necrumuncer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Tormentors

class BonelaceInsignia(Insignia):

    names = {
        ServerLanguage.English: "Bonelace Insignia [Necromancer]",
        ServerLanguage.Korean: "해골장식 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de dentelle",
        ServerLanguage.German: "Klöppelspitzen- [Nekromanten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Negromante] di Maglia d'Ossa",
        ServerLanguage.Spanish: "Insignia [Nigromante] de cordones de hueso",
        ServerLanguage.TraditionalChinese: "骨飾 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ボーンレース 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Kościanej Lancy",
        ServerLanguage.Russian: "Bonelace Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Bunelaece-a Inseegneea [Necrumuncer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Bonelace

class MinionMastersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Minion Master's Insignia [Necromancer]",
        ServerLanguage.Korean: "언데드마스터의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] du Maître des serviteurs",
        ServerLanguage.German: "Dienermeister- [Nekromanten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Negromante] da Domasgherri",
        ServerLanguage.Spanish: "Insignia [Nigromante] de maestro de siervos",
        ServerLanguage.TraditionalChinese: "爪牙大師 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ミニオン マスター 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Władcy Sług",
        ServerLanguage.Russian: "Minion Master's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Meeneeun Maester's Inseegneea [Necrumuncer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.MinionMasters

class BlightersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Blighter's Insignia [Necromancer]",
        ServerLanguage.Korean: "오염자의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] de destructeur",
        ServerLanguage.German: "Verderber- [Nekromanten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Negromante] da Malfattore",
        ServerLanguage.Spanish: "Insignia [Nigromante] de malhechor",
        ServerLanguage.TraditionalChinese: "破壞者 徽記 [死靈法師]",
        ServerLanguage.Japanese: "ブライター 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Złoczyńcy",
        ServerLanguage.Russian: "Blighter's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Bleeghter's Inseegneea [Necrumuncer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Blighters

class UndertakersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Undertaker's Insignia [Necromancer]",
        ServerLanguage.Korean: "장의사의 휘장 [네크로맨서]",
        ServerLanguage.French: "Insigne [Nécromant] du fossoyeur",
        ServerLanguage.German: "Leichenbestatter- [Nekromanten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Negromante] da Becchino",
        ServerLanguage.Spanish: "Insignia [Nigromante] de enterrador",
        ServerLanguage.TraditionalChinese: "承受者 徽記 [死靈法師]",
        ServerLanguage.Japanese: "アンダーテイカー 記章 [ネクロマンサー]",
        ServerLanguage.Polish: "[Nekromanta] Symbol Grabarza",
        ServerLanguage.Russian: "Undertaker's Insignia [Necromancer]",
        ServerLanguage.BorkBorkBork: "Undertaeker's Inseegneea [Necrumuncer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Undertakers

class NecromancerRuneOfMinorBloodMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Minor Blood Magic",
        ServerLanguage.Korean: "네크로맨서 룬(하급 피)",
        ServerLanguage.French: "Rune de Nécromant (Magie du sang : bonus mineur)",
        ServerLanguage.German: "Nekromanten-Rune d. kleineren Blutmagie",
        ServerLanguage.Italian: "Runa del Negromante Magia del Sangue di grado minore",
        ServerLanguage.Spanish: "Runa de Nigromante (Magia de sangre de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 血魔法 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (マイナー ブラッド)",
        ServerLanguage.Polish: "Runa Nekromanty (Magia Krwi niższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Minor Blood Magic",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Meenur Bluud Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorBloodMagic

class NecromancerRuneOfMinorDeathMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Minor Death Magic",
        ServerLanguage.Korean: "네크로맨서 룬(하급 죽음)",
        ServerLanguage.French: "Rune de Nécromant (Magie de la mort : bonus mineur)",
        ServerLanguage.German: "Nekromanten-Rune d. kleineren Todesmagie",
        ServerLanguage.Italian: "Runa del Negromante Magia della Morte di grado minore",
        ServerLanguage.Spanish: "Runa de Nigromante (Magia de muerte de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 死亡魔法 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (マイナー デス)",
        ServerLanguage.Polish: "Runa Nekromanty (Magia Śmierci niższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Minor Death Magic",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Meenur Deaet Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDeathMagic

class NecromancerRuneOfMinorCurses(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Minor Curses",
        ServerLanguage.Korean: "네크로맨서 룬(하급 저주)",
        ServerLanguage.French: "Rune de Nécromant (Malédictions : bonus mineur)",
        ServerLanguage.German: "Nekromanten-Rune d. kleineren Flüche",
        ServerLanguage.Italian: "Runa del Negromante Maledizioni di grado minore",
        ServerLanguage.Spanish: "Runa de Nigromante (Maldiciones de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 詛咒 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (マイナー カース)",
        ServerLanguage.Polish: "Runa Nekromanty (Klątwy niższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Minor Curses",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Meenur Coorses",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCurses

class NecromancerRuneOfMinorSoulReaping(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Minor Soul Reaping",
        ServerLanguage.Korean: "네크로맨서 룬(하급 영혼)",
        ServerLanguage.French: "Rune de Nécromant (Moisson des âmes : bonus mineur)",
        ServerLanguage.German: "Nekromanten-Rune d. kleineren Seelensammlung",
        ServerLanguage.Italian: "Runa del Negromante Sottrazione dell'Anima di grado minore",
        ServerLanguage.Spanish: "Runa de Nigromante (Cosecha de almas de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 靈魂吸取 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (マイナー ソウル リーピング)",
        ServerLanguage.Polish: "Runa Nekromanty (Wydzieranie Duszy niższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Minor Soul Reaping",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Meenur Suool Reaepeeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSoulReaping

class NecromancerRuneOfMajorBloodMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Major Blood Magic",
        ServerLanguage.Korean: "네크로맨서 룬(상급 피)",
        ServerLanguage.French: "Rune de Nécromant (Magie du sang : bonus majeur)",
        ServerLanguage.German: "Nekromanten-Rune d. hohen Blutmagie",
        ServerLanguage.Italian: "Runa del Negromante Magia del Sangue di grado maggiore",
        ServerLanguage.Spanish: "Runa de Nigromante (Magia de sangre de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 血魔法 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (メジャー ブラッド)",
        ServerLanguage.Polish: "Runa Nekromanty (Magia Krwi wyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Major Blood Magic",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Maejur Bluud Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorBloodMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfMajorDeathMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Major Death Magic",
        ServerLanguage.Korean: "네크로맨서 룬(상급 죽음)",
        ServerLanguage.French: "Rune de Nécromant (Magie de la mort : bonus majeur)",
        ServerLanguage.German: "Nekromanten-Rune d. hohen Todesmagie",
        ServerLanguage.Italian: "Runa del Negromante Magia della Morte di grado maggiore",
        ServerLanguage.Spanish: "Runa de Nigromante (Magia de muerte de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 死亡魔法 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (メジャー デス)",
        ServerLanguage.Polish: "Runa Nekromanty (Magia Śmierci wyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Major Death Magic",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Maejur Deaet Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDeathMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfMajorCurses(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Major Curses",
        ServerLanguage.Korean: "네크로맨서 룬(상급 저주)",
        ServerLanguage.French: "Rune de Nécromant (Malédictions : bonus majeur)",
        ServerLanguage.German: "Nekromanten-Rune d. hohen Flüche",
        ServerLanguage.Italian: "Runa del Negromante Maledizioni di grado maggiore",
        ServerLanguage.Spanish: "Runa de Nigromante (Maldiciones de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 詛咒 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (メジャー カース)",
        ServerLanguage.Polish: "Runa Nekromanty (Klątwy wyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Major Curses",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Maejur Coorses",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCurses
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfMajorSoulReaping(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Major Soul Reaping",
        ServerLanguage.Korean: "네크로맨서 룬(상급 영혼)",
        ServerLanguage.French: "Rune de Nécromant (Moisson des âmes : bonus majeur)",
        ServerLanguage.German: "Nekromanten-Rune d. hohen Seelensammlung",
        ServerLanguage.Italian: "Runa del Negromante Sottrazione dell'Anima di grado maggiore",
        ServerLanguage.Spanish: "Runa de Nigromante (Cosecha de almas de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 靈魂吸取 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (メジャー ソウル リーピング)",
        ServerLanguage.Polish: "Runa Nekromanty (Wydzieranie Duszy wyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Major Soul Reaping",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Maejur Suool Reaepeeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSoulReaping
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfSuperiorBloodMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Superior Blood Magic",
        ServerLanguage.Korean: "네크로맨서 룬(고급 피)",
        ServerLanguage.French: "Rune de Nécromant (Magie du sang : bonus supérieur)",
        ServerLanguage.German: "Nekromanten-Rune d. überlegenen Blutmagie",
        ServerLanguage.Italian: "Runa del Negromante Magia del Sangue di grado supremo",
        ServerLanguage.Spanish: "Runa de Nigromante (Magia de sangre de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 血魔法 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (スーペリア ブラッド)",
        ServerLanguage.Polish: "Runa Nekromanty (Magia Krwi najwyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Superior Blood Magic",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Soopereeur Bluud Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorBloodMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfSuperiorDeathMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Superior Death Magic",
        ServerLanguage.Korean: "네크로맨서 룬(고급 죽음)",
        ServerLanguage.French: "Rune de Nécromant (Magie de la mort : bonus supérieur)",
        ServerLanguage.German: "Nekromanten-Rune d. überlegenen Todesmagie",
        ServerLanguage.Italian: "Runa del Negromante Magia della Morte di grado supremo",
        ServerLanguage.Spanish: "Runa de Nigromante (Magia de muerte de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 死亡魔法 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (スーペリア デス)",
        ServerLanguage.Polish: "Runa Nekromanty (Magia Śmierci najwyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Superior Death Magic",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Soopereeur Deaet Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDeathMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfSuperiorCurses(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Superior Curses",
        ServerLanguage.Korean: "네크로맨서 룬(고급 저주)",
        ServerLanguage.French: "Rune de Nécromant (Malédictions : bonus supérieur)",
        ServerLanguage.German: "Nekromanten-Rune d. überlegenen Flüche",
        ServerLanguage.Italian: "Runa del Negromante Maledizioni di grado supremo",
        ServerLanguage.Spanish: "Runa de Nigromante (Maldiciones de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 詛咒 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (スーペリア カース)",
        ServerLanguage.Polish: "Runa Nekromanty (Klątwy najwyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Superior Curses",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Soopereeur Coorses",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCurses
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class NecromancerRuneOfSuperiorSoulReaping(AttributeRune):

    names = {
        ServerLanguage.English: "Necromancer Rune of Superior Soul Reaping",
        ServerLanguage.Korean: "네크로맨서 룬(고급 영혼)",
        ServerLanguage.French: "Rune de Nécromant (Moisson des âmes : bonus supérieur)",
        ServerLanguage.German: "Nekromanten-Rune d. überlegenen Seelensammlung",
        ServerLanguage.Italian: "Runa del Negromante Sottrazione dell'Anima di grado supremo",
        ServerLanguage.Spanish: "Runa de Nigromante (Cosecha de almas de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 靈魂吸取 死靈法師符文",
        ServerLanguage.Japanese: "ネクロマンサー ルーン (スーペリア ソウル リーピング)",
        ServerLanguage.Polish: "Runa Nekromanty (Wydzieranie Duszy najwyższego poziomu)",
        ServerLanguage.Russian: "Necromancer Rune of Superior Soul Reaping",
        ServerLanguage.BorkBorkBork: "Necrumuncer Roone-a ooff Soopereeur Suool Reaepeeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSoulReaping
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Necromancer

class UpgradeMajorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Necromancer

class UpgradeSuperiorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Necromancer

class AppliesToMinorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Necromancer

class AppliesToMajorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Necromancer

class AppliesToSuperiorRuneNecromancer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Necromancer
#endregion Necromancer

#region Mesmer

class VirtuososInsignia(Insignia):

    names = {
        ServerLanguage.English: "Virtuoso's Insignia [Mesmer]",
        ServerLanguage.Korean: "거장의 휘장 [메스머]",
        ServerLanguage.French: "Insigne [Envoûteur] de virtuose",
        ServerLanguage.German: "Virtuosen- [Mesmer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Ipnotizzatore] da Intenditore",
        ServerLanguage.Spanish: "Insignia [Hipnotizador] de virtuoso",
        ServerLanguage.TraditionalChinese: "鑑賞家 徽記 [幻術師]",
        ServerLanguage.Japanese: "ヴァーチュオーソ 記章 [メスマー]",
        ServerLanguage.Polish: "[Mesmer] Symbol Wirtuoza",
        ServerLanguage.Russian: "Virtuoso's Insignia [Mesmer]",
        ServerLanguage.BorkBorkBork: "Furtoousu's Inseegneea [Mesmer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Virtuosos

class ArtificersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Artificer's Insignia [Mesmer]",
        ServerLanguage.Korean: "장인의 휘장 [메스머]",
        ServerLanguage.French: "Insigne [Envoûteur] de l'artisan",
        ServerLanguage.German: "Feuerwerker- [Mesmer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Ipnotizzatore] da Artefice",
        ServerLanguage.Spanish: "Insignia [Hipnotizador] de artífice",
        ServerLanguage.TraditionalChinese: "巧匠 徽記 [幻術師]",
        ServerLanguage.Japanese: "アーティファサー 記章 [メスマー]",
        ServerLanguage.Polish: "[Mesmer] Symbol Rzemieślnika",
        ServerLanguage.Russian: "Artificer's Insignia [Mesmer]",
        ServerLanguage.BorkBorkBork: "Aerteeffeecer's Inseegneea [Mesmer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Artificers

class ProdigysInsignia(Insignia):

    names = {
        ServerLanguage.English: "Prodigy's Insignia [Mesmer]",
        ServerLanguage.Korean: "천재의 휘장 [메스머]",
        ServerLanguage.French: "Insigne [Envoûteur] prodige",
        ServerLanguage.German: "Wunder- [Mesmer]-Befähigung",
        ServerLanguage.Italian: "Insegne [Ipnotizzatore] da Prodigio",
        ServerLanguage.Spanish: "Insignia [Hipnotizador] de prodigio",
        ServerLanguage.TraditionalChinese: "奇蹟 徽記 [幻術師]",
        ServerLanguage.Japanese: "プロディジー 記章 [メスマー]",
        ServerLanguage.Polish: "[Mesmer] Symbol Geniusza",
        ServerLanguage.Russian: "Prodigy's Insignia [Mesmer]",
        ServerLanguage.BorkBorkBork: "Prudeegy's Inseegneea [Mesmer]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Prodigys

class MesmerRuneOfMinorFastCasting(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Minor Fast Casting",
        ServerLanguage.Korean: "메스머 룬(하급 빠른 시전)",
        ServerLanguage.French: "Rune d'Envoûteur (Incantation rapide : bonus mineur)",
        ServerLanguage.German: "Mesmer-Rune d. kleineren Schnellwirkung",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Lancio Rapido di grado minore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Lanzar conjuros rápido de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 快速施法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (マイナー ファスト キャスト)",
        ServerLanguage.Polish: "Runa Mesmera (Szybkie Rzucanie Czarów niższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Minor Fast Casting",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Meenur Faest Caesteeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorFastCasting

class MesmerRuneOfMinorDominationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Minor Domination Magic",
        ServerLanguage.Korean: "메스머 룬(하급 지배)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de domination : bonus mineur)",
        ServerLanguage.German: "Mesmer-Rune d. kleineren Beherrschungsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia del Dominio di grado minore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de dominación de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 支配魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (マイナー ドミネーション)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Dominacji niższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Minor Domination Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Meenur Dumeenaeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDominationMagic

class MesmerRuneOfMinorIllusionMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Minor Illusion Magic",
        ServerLanguage.Korean: "메스머 룬(하급 환상)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de l'illusion : bonus mineur)",
        ServerLanguage.German: "Mesmer-Rune d. kleineren Illusionsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia Illusoria di grado minore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de ilusión de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 幻術魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (マイナー イリュージョン)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Iluzji niższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Minor Illusion Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Meenur Illooseeun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorIllusionMagic

class MesmerRuneOfMinorInspirationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Minor Inspiration Magic",
        ServerLanguage.Korean: "메스머 룬(하급 영감)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de l'inspiration : bonus mineur)",
        ServerLanguage.German: "Mesmer-Rune d. kleineren Inspirationsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia di Ispirazione di grado minore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de inspiración de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 靈感魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (マイナー インスピレーション)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Inspiracji niższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Minor Inspiration Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Meenur Inspuraeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorInspirationMagic

class MesmerRuneOfMajorFastCasting(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Major Fast Casting",
        ServerLanguage.Korean: "메스머 룬(상급 빠른 시전)",
        ServerLanguage.French: "Rune d'Envoûteur (Incantation rapide : bonus majeur)",
        ServerLanguage.German: "Mesmer-Rune d. hohen Schnellwirkung",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Lancio Rapido di grado maggiore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Lanzar conjuros rápido de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 快速施法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (メジャー ファスト キャスト)",
        ServerLanguage.Polish: "Runa Mesmera (Szybkie Rzucanie Czarów wyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Major Fast Casting",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Maejur Faest Caesteeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorFastCasting
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfMajorDominationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Major Domination Magic",
        ServerLanguage.Korean: "메스머 룬(상급 지배)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de domination : bonus majeur)",
        ServerLanguage.German: "Mesmer-Rune d. hohen Beherrschungsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia del Dominio di grado maggiore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de dominación de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 支配魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (メジャー ドミネーション)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Dominacji wyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Major Domination Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Maejur Dumeenaeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDominationMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfMajorIllusionMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Major Illusion Magic",
        ServerLanguage.Korean: "메스머 룬(상급 환상)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de l'illusion : bonus majeur)",
        ServerLanguage.German: "Mesmer-Rune d. hohen Illusionsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia Illusoria di grado maggiore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de ilusión de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 幻術魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (メジャー イリュージョン)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Iluzji wyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Major Illusion Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Maejur Illooseeun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorIllusionMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfMajorInspirationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Major Inspiration Magic",
        ServerLanguage.Korean: "메스머 룬(상급 영감)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de l'inspiration : bonus majeur)",
        ServerLanguage.German: "Mesmer-Rune d. hohen Inspirationsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia di Ispirazione di grado maggiore",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de inspiración de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 靈感魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (メジャー インスピレーション)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Inspiracji wyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Major Inspiration Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Maejur Inspuraeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorInspirationMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfSuperiorFastCasting(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Superior Fast Casting",
        ServerLanguage.Korean: "메스머 룬(고급 빠른 시전)",
        ServerLanguage.French: "Rune d'Envoûteur (Incantation rapide : bonus supérieur)",
        ServerLanguage.German: "Mesmer-Rune d. überlegenen Schnellwirkung",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Lancio Rapido di grado supremo",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Lanzar conjuros rápido de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 快速施法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (スーペリア ファスト キャスト)",
        ServerLanguage.Polish: "Runa Mesmera (Szybkie Rzucanie Czarów najwyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Superior Fast Casting",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Soopereeur Faest Caesteeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorFastCasting
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfSuperiorDominationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Superior Domination Magic",
        ServerLanguage.Korean: "메스머 룬(고급 지배)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de domination : bonus supérieur)",
        ServerLanguage.German: "Mesmer-Rune d. überlegenen Beherrschungsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia del Dominio di grado supremo",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de dominación de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 支配魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (スーペリア ドミネーション)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Dominacji najwyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Superior Domination Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Soopereeur Dumeenaeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDominationMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfSuperiorIllusionMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Superior Illusion Magic",
        ServerLanguage.Korean: "메스머 룬(고급 환상)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de l'illusion : bonus supérieur)",
        ServerLanguage.German: "Mesmer-Rune d. überlegenen Illusionsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia Illusoria di grado supremo",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de ilusión de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 幻術魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (スーペリア イリュージョン)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Iluzji najwyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Superior Illusion Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Soopereeur Illooseeun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorIllusionMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class MesmerRuneOfSuperiorInspirationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Mesmer Rune of Superior Inspiration Magic",
        ServerLanguage.Korean: "메스머 룬(고급 영감)",
        ServerLanguage.French: "Rune d'Envoûteur (Magie de l'inspiration : bonus supérieur)",
        ServerLanguage.German: "Mesmer-Rune d. überlegenen Inspirationsmagie",
        ServerLanguage.Italian: "Runa dell'Ipnotizzatore Magia di Ispirazione di grado supremo",
        ServerLanguage.Spanish: "Runa de Hipnotizador (Magia de inspiración de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 靈感魔法 幻術師符文",
        ServerLanguage.Japanese: "メスマー ルーン (スーペリア インスピレーション)",
        ServerLanguage.Polish: "Runa Mesmera (Magia Inspiracji najwyższego poziomu)",
        ServerLanguage.Russian: "Mesmer Rune of Superior Inspiration Magic",
        ServerLanguage.BorkBorkBork: "Mesmer Roone-a ooff Soopereeur Inspuraeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorInspirationMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Mesmer

class UpgradeMajorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Mesmer

class UpgradeSuperiorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Mesmer

class AppliesToMinorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Mesmer

class AppliesToMajorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Mesmer

class AppliesToSuperiorRuneMesmer(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Mesmer
#endregion Mesmer

#region Elementalist

class HydromancerInsignia(Insignia):

    names = {
        ServerLanguage.English: "Hydromancer Insignia [Elementalist]",
        ServerLanguage.Korean: "물의술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] d'hydromancie",
        ServerLanguage.German: "Hydromanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Italian: "Insegne [Elementalista] da Idromante",
        ServerLanguage.Spanish: "Insignia [Elementalista] de hidromante",
        ServerLanguage.TraditionalChinese: "水法師 徽記 [元素使]",
        ServerLanguage.Japanese: "ハイドロマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Hydromanty",
        ServerLanguage.Russian: "Hydromancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Hydrumuncer Inseegneea [Ilementaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Hydromancer

class GeomancerInsignia(Insignia):

    names = {
        ServerLanguage.English: "Geomancer Insignia [Elementalist]",
        ServerLanguage.Korean: "대지술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] de géomancie",
        ServerLanguage.German: "Geomanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Italian: "Insegne [Elementalista] da Geomante",
        ServerLanguage.Spanish: "Insignia [Elementalista] de geomante",
        ServerLanguage.TraditionalChinese: "地法師 徽記 [元素使]",
        ServerLanguage.Japanese: "ジオマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Geomanty",
        ServerLanguage.Russian: "Geomancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Geumuncer Inseegneea [Ilementaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Geomancer

class PyromancerInsignia(Insignia):

    names = {
        ServerLanguage.English: "Pyromancer Insignia [Elementalist]",
        ServerLanguage.Korean: "화염술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] de pyromancie",
        ServerLanguage.German: "Pyromanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Italian: "Insegne [Elementalista] da Piromante",
        ServerLanguage.Spanish: "Insignia [Elementalista] de piromante",
        ServerLanguage.TraditionalChinese: "火法師 徽記 [元素使]",
        ServerLanguage.Japanese: "パイロマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Piromanty",
        ServerLanguage.Russian: "Pyromancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Pyrumuncer Inseegneea [Ilementaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Pyromancer

class AeromancerInsignia(Insignia):

    names = {
        ServerLanguage.English: "Aeromancer Insignia [Elementalist]",
        ServerLanguage.Korean: "바람술사의 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] d'aéromancie",
        ServerLanguage.German: "Aeromanten- [Elementarmagier]-Befähigung",
        ServerLanguage.Italian: "Insegne [Elementalista] da Aeromante",
        ServerLanguage.Spanish: "Insignia [Elementalista] de aeromante",
        ServerLanguage.TraditionalChinese: "風法師 徽記 [元素使]",
        ServerLanguage.Japanese: "エアロマンサー 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Aeromanty",
        ServerLanguage.Russian: "Aeromancer Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Aeerumuncer Inseegneea [Ilementaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Aeromancer

class PrismaticInsignia(Insignia):

    names = {
        ServerLanguage.English: "Prismatic Insignia [Elementalist]",
        ServerLanguage.Korean: "무지갯빛 휘장 [엘리멘탈리스트]",
        ServerLanguage.French: "Insigne [Elémentaliste] prismatique",
        ServerLanguage.German: "Spektral- [Elementarmagier]-Befähigung",
        ServerLanguage.Italian: "Insegne [Elementalista] a Prisma",
        ServerLanguage.Spanish: "Insignia [Elementalista] de prismático",
        ServerLanguage.TraditionalChinese: "稜鏡 徽記 [元素使]",
        ServerLanguage.Japanese: "プリズマティック 記章 [エレメンタリスト]",
        ServerLanguage.Polish: "[Elementalista] Symbol Pryzmatu",
        ServerLanguage.Russian: "Prismatic Insignia [Elementalist]",
        ServerLanguage.BorkBorkBork: "Preesmaeteec Inseegneea [Ilementaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Prismatic

class ElementalistRuneOfMinorEnergyStorage(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Minor Energy Storage",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(하급 에너지 축적)",
        ServerLanguage.French: "Rune d'Elémentaliste (Conservation d'énergie : bonus mineur)",
        ServerLanguage.German: "Elementarmagier-Rune d. kleineren Energiespeicherung",
        ServerLanguage.Italian: "Runa dell'Elementalista Riserva di Energia di grado minore",
        ServerLanguage.Spanish: "Runa de Elementalista (Almacenamiento energía de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 能量儲存 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (マイナー ストレージ)",
        ServerLanguage.Polish: "Runa Elementalisty (Zapas Energii niższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Minor Energy Storage",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Meenur Inergy Sturaege-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorEnergyStorage

class ElementalistRuneOfMinorFireMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Minor Fire Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(하급 불)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie du feu : bonus mineur)",
        ServerLanguage.German: "Elementarmagier-Rune d. kleineren Feuermagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia del Fuoco di grado minore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de fuego de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 火系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (マイナー ファイア)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Ognia niższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Minor Fire Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Meenur Fure-a Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorFireMagic

class ElementalistRuneOfMinorAirMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Minor Air Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(하급 바람)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de l'air : bonus mineur)",
        ServerLanguage.German: "Elementarmagier-Rune d. kleineren Luftmagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia dell'Aria di grado minore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de aire de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 風系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (マイナー エアー)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Powietrza niższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Minor Air Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Meenur Aeur Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorAirMagic

class ElementalistRuneOfMinorEarthMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Minor Earth Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(하급 대지)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de la terre : bonus mineur)",
        ServerLanguage.German: "Elementarmagier-Rune d. kleineren Erdmagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia della Terra di grado minore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de tierra de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 土系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (マイナー アース)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Ziemi niższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Minor Earth Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Meenur Iaert Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorEarthMagic

class ElementalistRuneOfMinorWaterMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Minor Water Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(하급 물)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de l'eau : bonus mineur)",
        ServerLanguage.German: "Elementarmagier-Rune d. kleineren Wassermagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia dell'Acqua di grado minore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de agua de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 水系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (マイナー ウォーター)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Wody niższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Minor Water Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Meenur Vaeter Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorWaterMagic

class ElementalistRuneOfMajorEnergyStorage(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Major Energy Storage",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(상급 에너지 축적)",
        ServerLanguage.French: "Rune d'Elémentaliste (Conservation d'énergie : bonus majeur)",
        ServerLanguage.German: "Elementarmagier-Rune d. hohen Energiespeicherung",
        ServerLanguage.Italian: "Runa dell'Elementalista Riserva di Energia di grado maggiore",
        ServerLanguage.Spanish: "Runa de Elementalista (Almacenamiento energía de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 能量儲存 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (メジャー ストレージ)",
        ServerLanguage.Polish: "Runa Elementalisty (Zapas Energii wyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Major Energy Storage",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Maejur Inergy Sturaege-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorEnergyStorage
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfMajorFireMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Major Fire Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(상급 불)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie du feu : bonus majeur)",
        ServerLanguage.German: "Elementarmagier-Rune d. hohen Feuermagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia del Fuoco di grado maggiore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de fuego de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 火系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (メジャー ファイア)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Ognia wyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Major Fire Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Maejur Fure-a Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorFireMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfMajorAirMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Major Air Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(상급 바람)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de l'air : bonus majeur)",
        ServerLanguage.German: "Elementarmagier-Rune d. hohen Luftmagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia dell'Aria di grado maggiore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de aire de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 風系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (メジャー エアー)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Powietrza wyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Major Air Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Maejur Aeur Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorAirMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfMajorEarthMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Major Earth Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(상급 대지)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de la terre : bonus majeur)",
        ServerLanguage.German: "Elementarmagier-Rune d. hohen Erdmagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia della Terra di grado maggiore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de tierra de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 土系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (メジャー アース)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Ziemi wyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Major Earth Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Maejur Iaert Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorEarthMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfMajorWaterMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Major Water Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(상급 물)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de l'eau : bonus majeur)",
        ServerLanguage.German: "Elementarmagier-Rune d. hohen Wassermagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia dell'Acqua di grado maggiore",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de agua de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 水系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (メジャー ウォーター)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Wody wyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Major Water Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Maejur Vaeter Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorWaterMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfSuperiorEnergyStorage(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Superior Energy Storage",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(고급 에너지 축적)",
        ServerLanguage.French: "Rune d'Elémentaliste (Conservation d'énergie : bonus supérieur)",
        ServerLanguage.German: "Elementarmagier-Rune d. überlegenen Energiespeicherung",
        ServerLanguage.Italian: "Runa dell'Elementalista Riserva di Energia di grado supremo",
        ServerLanguage.Spanish: "Runa de Elementalista (Almacenamiento energía de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 能量儲存 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (スーペリア ストレージ)",
        ServerLanguage.Polish: "Runa Elementalisty (Zapas Energii najwyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Superior Energy Storage",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Soopereeur Inergy Sturaege-a",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorEnergyStorage
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfSuperiorFireMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Superior Fire Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(고급 불)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie du feu : bonus supérieur)",
        ServerLanguage.German: "Elementarmagier-Rune d. überlegenen Feuermagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia del Fuoco di grado supremo",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de fuego de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 火系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (スーペリア ファイア)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Ognia najwyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Superior Fire Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Soopereeur Fure-a Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorFireMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfSuperiorAirMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Superior Air Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(고급 바람)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de l'air : bonus supérieur)",
        ServerLanguage.German: "Elementarmagier-Rune d. überlegenen Luftmagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia dell'Aria di grado supremo",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de aire de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 風系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (スーペリア エアー)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Powietrza najwyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Superior Air Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Soopereeur Aeur Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorAirMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfSuperiorEarthMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Superior Earth Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(고급 대지)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de la terre : bonus supérieur)",
        ServerLanguage.German: "Elementarmagier-Rune d. überlegenen Erdmagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia della Terra di grado supremo",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de tierra de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 土系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (スーペリア アース)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Ziemi najwyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Superior Earth Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Soopereeur Iaert Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorEarthMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ElementalistRuneOfSuperiorWaterMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Elementalist Rune of Superior Water Magic",
        ServerLanguage.Korean: "엘리멘탈리스트 룬(고급 물)",
        ServerLanguage.French: "Rune d'Elémentaliste (Magie de l'eau : bonus supérieur)",
        ServerLanguage.German: "Elementarmagier-Rune d. überlegenen Wassermagie",
        ServerLanguage.Italian: "Runa dell'Elementalista Magia dell'Acqua di grado supremo",
        ServerLanguage.Spanish: "Runa de Elementalista (Magia de agua de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 水系魔法 元素使符文",
        ServerLanguage.Japanese: "エレメンタリスト ルーン (スーペリア ウォーター)",
        ServerLanguage.Polish: "Runa Elementalisty (Magia Wody najwyższego poziomu)",
        ServerLanguage.Russian: "Elementalist Rune of Superior Water Magic",
        ServerLanguage.BorkBorkBork: "Ilementaeleest Roone-a ooff Soopereeur Vaeter Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorWaterMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Elementalist

class UpgradeMajorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Elementalist

class UpgradeSuperiorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Elementalist

class AppliesToMinorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Elementalist

class AppliesToMajorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Elementalist

class AppliesToSuperiorRuneElementalist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Elementalist
#endregion Elementalist

#region Assassin

class VanguardsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Vanguard's Insignia [Assassin]",
        ServerLanguage.Korean: "선봉대의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de l'avant-garde",
        ServerLanguage.German: "Hauptmann- [Assassinen]-Befähigung",
        ServerLanguage.Italian: "Insegne [Assassino] da Avanguardia",
        ServerLanguage.Spanish: "Insignia [Asesino] de avanzado",
        ServerLanguage.TraditionalChinese: "前鋒 徽記 [暗殺者]",
        ServerLanguage.Japanese: "ヴァンガード 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Awangardy",
        ServerLanguage.Russian: "Vanguard's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Fungooaerd's Inseegneea [Aessaesseen]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Vanguards

class InfiltratorsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Infiltrator's Insignia [Assassin]",
        ServerLanguage.Korean: "침입자의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de l'infiltré",
        ServerLanguage.German: "Eindringlings- [Assassinen]-Befähigung",
        ServerLanguage.Italian: "Insegne [Assassino] da Spia",
        ServerLanguage.Spanish: "Insignia [Asesino] de infiltrado",
        ServerLanguage.TraditionalChinese: "滲透者 徽記 [暗殺者]",
        ServerLanguage.Japanese: "インフィルトレイター 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Infiltratora",
        ServerLanguage.Russian: "Infiltrator's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Inffeeltraetur's Inseegneea [Aessaesseen]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Infiltrators

class SaboteursInsignia(Insignia):

    names = {
        ServerLanguage.English: "Saboteur's Insignia [Assassin]",
        ServerLanguage.Korean: "파괴자의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de saboteur",
        ServerLanguage.German: "Saboteur- [Assassinen]-Befähigung",
        ServerLanguage.Italian: "Insegne [Assassino] da Sabotatore",
        ServerLanguage.Spanish: "Insignia [Asesino] de saboteador",
        ServerLanguage.TraditionalChinese: "破壞者 徽記 [暗殺者]",
        ServerLanguage.Japanese: "サボター 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Sabotażysty",
        ServerLanguage.Russian: "Saboteur's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Saebuteoor's Inseegneea [Aessaesseen]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Saboteurs

class NightstalkersInsignia(Insignia):

    names = {
        ServerLanguage.English: "Nightstalker's Insignia [Assassin]",
        ServerLanguage.Korean: "밤추종자의 휘장 [어새신]",
        ServerLanguage.French: "Insigne [Assassin] de traqueur nocturne",
        ServerLanguage.German: "Nachtpirscher- [Assassinen]-Befähigung",
        ServerLanguage.Italian: "Insegne [Assassino] da Inseguitore Notturno",
        ServerLanguage.Spanish: "Insignia [Asesino] de acechador nocturno",
        ServerLanguage.TraditionalChinese: "夜行者 徽記 [暗殺者]",
        ServerLanguage.Japanese: "ナイトストーカー 記章 [アサシン]",
        ServerLanguage.Polish: "[Zabójca] Symbol Nocnego Tropiciela",
        ServerLanguage.Russian: "Nightstalker's Insignia [Assassin]",
        ServerLanguage.BorkBorkBork: "Neeghtstaelker's Inseegneea [Aessaesseen]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Nightstalkers

class AssassinRuneOfMinorCriticalStrikes(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Minor Critical Strikes",
        ServerLanguage.Korean: "어새신 룬(하급 치명타)",
        ServerLanguage.French: "Rune d'Assassin (Attaques critiques : bonus mineur)",
        ServerLanguage.German: "Assassinen-Rune d. kleineren Kritische Stöße",
        ServerLanguage.Italian: "Runa dell'Assassino Colpi Critici di grado minore",
        ServerLanguage.Spanish: "Runa de Asesino (Impactos críticos de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 致命攻擊 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (マイナー クリティカル ストライク)",
        ServerLanguage.Polish: "Runa Zabójcy (Trafienia Krytyczne niższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Minor Critical Strikes",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Meenur Creeteecael Streekes",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCriticalStrikes

class AssassinRuneOfMinorDaggerMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Minor Dagger Mastery",
        ServerLanguage.Korean: "어새신 룬(하급 단검술)",
        ServerLanguage.French: "Rune d'Assassin (Maîtrise de la dague : bonus mineur)",
        ServerLanguage.German: "Assassinen-Rune d. kleineren Dolchbeherrschung",
        ServerLanguage.Italian: "Runa dell'Assassino Abilità con il Pugnale di grado minore",
        ServerLanguage.Spanish: "Runa de Asesino (Dominio de la daga de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 匕首精通 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (マイナー ダガー マスタリー)",
        ServerLanguage.Polish: "Runa Zabójcy (Biegłość w Sztyletach niższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Minor Dagger Mastery",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Meenur Daegger Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDaggerMastery

class AssassinRuneOfMinorDeadlyArts(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Minor Deadly Arts",
        ServerLanguage.Korean: "어새신 룬(하급 죽음의 기예)",
        ServerLanguage.French: "Rune d'Assassin (Arts létaux : bonus mineur)",
        ServerLanguage.German: "Assassinen-Rune d. kleineren Tödliche Künste",
        ServerLanguage.Italian: "Runa dell'Assassino Arti Letali di grado minore",
        ServerLanguage.Spanish: "Runa de Asesino (Artes mortales de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 暗殺技巧 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (マイナー デッドリー アーツ)",
        ServerLanguage.Polish: "Runa Zabójcy (Sztuka Śmierci niższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Minor Deadly Arts",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Meenur Deaedly Aerts",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorDeadlyArts

class AssassinRuneOfMinorShadowArts(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Minor Shadow Arts",
        ServerLanguage.Korean: "어새신 룬(하급 그림자 기예)",
        ServerLanguage.French: "Rune d'Assassin (Arts des ombres : bonus mineur)",
        ServerLanguage.German: "Assassinen-Rune d. kleineren Schattenkünste",
        ServerLanguage.Italian: "Runa dell'Assassino Arti dell'Ombra di grado minore",
        ServerLanguage.Spanish: "Runa de Asesino (Artes sombrías de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 暗影技巧 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (マイナー シャドウ アーツ)",
        ServerLanguage.Polish: "Runa Zabójcy (Sztuka Cienia niższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Minor Shadow Arts",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Meenur Shaedoo Aerts",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorShadowArts

class AssassinRuneOfMajorCriticalStrikes(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Major Critical Strikes",
        ServerLanguage.Korean: "어새신 룬(상급 치명타)",
        ServerLanguage.French: "Rune d'Assassin (Attaques critiques : bonus majeur)",
        ServerLanguage.German: "Assassinen-Rune d. hohen Kritische Stöße",
        ServerLanguage.Italian: "Runa dell'Assassino Colpi Critici di grado maggiore",
        ServerLanguage.Spanish: "Runa de Asesino (Impactos críticos de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 致命攻擊 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (メジャー クリティカル ストライク)",
        ServerLanguage.Polish: "Runa Zabójcy (Trafienia Krytyczne wyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Major Critical Strikes",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Maejur Creeteecael Streekes",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCriticalStrikes
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfMajorDaggerMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Major Dagger Mastery",
        ServerLanguage.Korean: "어새신 룬(상급 단검술)",
        ServerLanguage.French: "Rune d'Assassin (Maîtrise de la dague : bonus majeur)",
        ServerLanguage.German: "Assassinen-Rune d. hohen Dolchbeherrschung",
        ServerLanguage.Italian: "Runa dell'Assassino Abilità con il Pugnale di grado maggiore",
        ServerLanguage.Spanish: "Runa de Asesino (Dominio de la daga de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 匕首精通 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (メジャー ダガー マスタリー)",
        ServerLanguage.Polish: "Runa Zabójcy (Biegłość w Sztyletach wyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Major Dagger Mastery",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Maejur Daegger Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDaggerMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfMajorDeadlyArts(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Major Deadly Arts",
        ServerLanguage.Korean: "어새신 룬(상급 죽음의 기예)",
        ServerLanguage.French: "Rune d'Assassin (Arts létaux : bonus majeur)",
        ServerLanguage.German: "Assassinen-Rune d. hohen Tödliche Künste",
        ServerLanguage.Italian: "Runa dell'Assassino Arti Letali di grado maggiore",
        ServerLanguage.Spanish: "Runa de Asesino (Artes mortales de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 暗殺技巧 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (メジャー デッドリー アーツ)",
        ServerLanguage.Polish: "Runa Zabójcy (Sztuka Śmierci wyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Major Deadly Arts",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Maejur Deaedly Aerts",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorDeadlyArts
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfMajorShadowArts(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Major Shadow Arts",
        ServerLanguage.Korean: "어새신 룬(상급 그림자 기예)",
        ServerLanguage.French: "Rune d'Assassin (Arts des ombres : bonus majeur)",
        ServerLanguage.German: "Assassinen-Rune d. hohen Schattenkünste",
        ServerLanguage.Italian: "Runa dell'Assassino Arti dell'Ombra di grado maggiore",
        ServerLanguage.Spanish: "Runa de Asesino (Artes sombrías de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 暗影技巧 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (メジャー シャドウ アーツ)",
        ServerLanguage.Polish: "Runa Zabójcy (Sztuka Cienia wyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Major Shadow Arts",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Maejur Shaedoo Aerts",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorShadowArts
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfSuperiorCriticalStrikes(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Superior Critical Strikes",
        ServerLanguage.Korean: "어새신 룬(고급 치명타)",
        ServerLanguage.French: "Rune d'Assassin (Attaques critiques : bonus supérieur)",
        ServerLanguage.German: "Assassinen-Rune d. überlegenen Kritische Stöße",
        ServerLanguage.Italian: "Runa dell'Assassino Colpi Critici di grado supremo",
        ServerLanguage.Spanish: "Runa de Asesino (Impactos críticos de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 致命攻擊 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (スーペリア クリティカル ストライク)",
        ServerLanguage.Polish: "Runa Zabójcy (Trafienia Krytyczne najwyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Superior Critical Strikes",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Soopereeur Creeteecael Streekes",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCriticalStrikes
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfSuperiorDaggerMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Superior Dagger Mastery",
        ServerLanguage.Korean: "어새신 룬(고급 단검술)",
        ServerLanguage.French: "Rune d'Assassin (Maîtrise de la dague : bonus supérieur)",
        ServerLanguage.German: "Assassinen-Rune d. überlegenen Dolchbeherrschung",
        ServerLanguage.Italian: "Runa dell'Assassino Abilità con il Pugnale di grado supremo",
        ServerLanguage.Spanish: "Runa de Asesino (Dominio de la daga de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 匕首精通 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (スーペリア ダガー マスタリー)",
        ServerLanguage.Polish: "Runa Zabójcy (Biegłość w Sztyletach najwyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Superior Dagger Mastery",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Soopereeur Daegger Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDaggerMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfSuperiorDeadlyArts(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Superior Deadly Arts",
        ServerLanguage.Korean: "어새신 룬(고급 죽음의 기예)",
        ServerLanguage.French: "Rune d'Assassin (Arts létaux : bonus supérieur)",
        ServerLanguage.German: "Assassinen-Rune d. überlegenen Tödliche Künste",
        ServerLanguage.Italian: "Runa dell'Assassino Arti Letali di grado supremo",
        ServerLanguage.Spanish: "Runa de Asesino (Artes mortales de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 暗殺技巧 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (スーペリア デッドリー アーツ)",
        ServerLanguage.Polish: "Runa Zabójcy (Sztuka Śmierci najwyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Superior Deadly Arts",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Soopereeur Deaedly Aerts",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorDeadlyArts
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class AssassinRuneOfSuperiorShadowArts(AttributeRune):

    names = {
        ServerLanguage.English: "Assassin Rune of Superior Shadow Arts",
        ServerLanguage.Korean: "어새신 룬(고급 그림자 기예)",
        ServerLanguage.French: "Rune d'Assassin (Arts des ombres : bonus supérieur)",
        ServerLanguage.German: "Assassinen-Rune d. überlegenen Schattenkünste",
        ServerLanguage.Italian: "Runa dell'Assassino Arti dell'Ombra di grado supremo",
        ServerLanguage.Spanish: "Runa de Asesino (Artes sombrías de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 暗影技巧 暗殺者符文",
        ServerLanguage.Japanese: "アサシン ルーン (スーペリア シャドウ アーツ)",
        ServerLanguage.Polish: "Runa Zabójcy (Sztuka Cienia najwyższego poziomu)",
        ServerLanguage.Russian: "Assassin Rune of Superior Shadow Arts",
        ServerLanguage.BorkBorkBork: "Aessaesseen Roone-a ooff Soopereeur Shaedoo Aerts",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorShadowArts
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Assassin

class UpgradeMajorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Assassin

class UpgradeSuperiorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Assassin

class AppliesToMinorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Assassin

class AppliesToMajorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Assassin

class AppliesToSuperiorRuneAssassin(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Assassin
#endregion Assassin

#region Ritualist

class ShamansInsignia(Insignia):

    names = {
        ServerLanguage.English: "Shaman's Insignia [Ritualist]",
        ServerLanguage.Korean: "주술사의 휘장 [리추얼리스트]",
        ServerLanguage.French: "Insigne [Ritualiste] de chaman",
        ServerLanguage.German: "Schamanen- [Ritualisten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Ritualista] da Sciamano",
        ServerLanguage.Spanish: "Insignia [Ritualista] de chamán",
        ServerLanguage.TraditionalChinese: "巫醫 徽記 [祭祀者]",
        ServerLanguage.Japanese: "シャーマン 記章 [リチュアリスト]",
        ServerLanguage.Polish: "[Rytualista] Symbol Szamana",
        ServerLanguage.Russian: "Shaman's Insignia [Ritualist]",
        ServerLanguage.BorkBorkBork: "Shaemun's Inseegneea [Reetooaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Shamans

class GhostForgeInsignia(Insignia):

    names = {
        ServerLanguage.English: "Ghost Forge Insignia [Ritualist]",
        ServerLanguage.Korean: "유령화로의 휘장 [리추얼리스트]",
        ServerLanguage.French: "Insigne [Ritualiste] de la forge du fantôme",
        ServerLanguage.German: "Geisterschmiede- [Ritualisten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Ritualista] della Fucina Spettrale",
        ServerLanguage.Spanish: "Insignia [Ritualista] de fragua fantasma",
        ServerLanguage.TraditionalChinese: "魂鎔 徽記 [祭祀者]",
        ServerLanguage.Japanese: "ゴースト フォージ 記章 [リチュアリスト]",
        ServerLanguage.Polish: "[Rytualista] Symbol Kuźni Duchów",
        ServerLanguage.Russian: "Ghost Forge Insignia [Ritualist]",
        ServerLanguage.BorkBorkBork: "Ghust Furge-a Inseegneea [Reetooaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.GhostForge

class MysticsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Mystic's Insignia [Ritualist]",
        ServerLanguage.Korean: "신비술사의 휘장 [리추얼리스트]",
        ServerLanguage.French: "Insigne [Ritualiste] mystique",
        ServerLanguage.German: "Mystiker- [Ritualisten]-Befähigung",
        ServerLanguage.Italian: "Insegne [Ritualista] del Misticismo",
        ServerLanguage.Spanish: "Insignia [Ritualista] de místico",
        ServerLanguage.TraditionalChinese: "祕法 徽記 [祭祀者]",
        ServerLanguage.Japanese: "ミスティック 記章 [リチュアリスト]",
        ServerLanguage.Polish: "[Rytualista] Symbol Mistyka",
        ServerLanguage.Russian: "Mystic's Insignia [Ritualist]",
        ServerLanguage.BorkBorkBork: "Mysteec's Inseegneea [Reetooaeleest]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Mystics

class RitualistRuneOfMinorChannelingMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Minor Channeling Magic",
        ServerLanguage.Korean: "리추얼리스트 룬(하급 마력 증폭)",
        ServerLanguage.French: "Rune du Ritualiste (Magie de la canalisation : bonus mineur)",
        ServerLanguage.German: "Ritualisten-Rune d. kleineren Kanalisierungsmagie",
        ServerLanguage.Italian: "Runa del Ritualista Magia di Incanalamento di grado minore",
        ServerLanguage.Spanish: "Runa de Ritualista (Magia de canalización de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 導引魔法 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (マイナー チャネリング)",
        ServerLanguage.Polish: "Runa Rytualisty (Magia Połączeń niższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Minor Channeling Magic",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Meenur Chunneleeng Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorChannelingMagic

class RitualistRuneOfMinorRestorationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Minor Restoration Magic",
        ServerLanguage.Korean: "리추얼리스트 룬(하급 마력 회복)",
        ServerLanguage.French: "Rune du Ritualiste (Magie de restauration : bonus mineur)",
        ServerLanguage.German: "Ritualisten-Rune d. kleineren Wiederherstellungsmagie",
        ServerLanguage.Italian: "Runa del Ritualista Magia del Ripristino di grado minore",
        ServerLanguage.Spanish: "Runa de Ritualista (Magia de restauración de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 復原魔法 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (マイナー レストレーション)",
        ServerLanguage.Polish: "Runa Rytualisty (Magia Odnowy niższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Minor Restoration Magic",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Meenur Resturaeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorRestorationMagic

class RitualistRuneOfMinorCommuning(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Minor Communing",
        ServerLanguage.Korean: "리추얼리스트 룬(하급 교감)",
        ServerLanguage.French: "Rune du Ritualiste (Communion : bonus mineur)",
        ServerLanguage.German: "Ritualisten-Rune d. kleineren Zwiesprache",
        ServerLanguage.Italian: "Runa del Ritualista Raccoglimento di grado minore",
        ServerLanguage.Spanish: "Runa de Ritualista (Comunión de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 神諭 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (マイナー コミューン)",
        ServerLanguage.Polish: "Runa Rytualisty (Zjednoczenie niższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Minor Communing",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Meenur Cummooneeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCommuning

class RitualistRuneOfMinorSpawningPower(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Minor Spawning Power",
        ServerLanguage.Korean: "리추얼리스트 룬(하급 생성)",
        ServerLanguage.French: "Rune du Ritualiste (Puissance de l'Invocation : bonus mineur)",
        ServerLanguage.German: "Ritualisten-Rune d. kleineren Macht des Herbeirufens",
        ServerLanguage.Italian: "Runa del Ritualista Riti Sacrificali di grado minore",
        ServerLanguage.Spanish: "Runa de Ritualista (Engendramiento de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 召喚 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (マイナー スポーン パワー)",
        ServerLanguage.Polish: "Runa Rytualisty (Moc Przywoływania niższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Minor Spawning Power",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Meenur Spaevneeng Pooer",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSpawningPower

class RitualistRuneOfMajorChannelingMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Major Channeling Magic",
        ServerLanguage.Korean: "리추얼리스트 룬(상급 마력 증폭)",
        ServerLanguage.French: "Rune du Ritualiste (Magie de la canalisation : bonus majeur)",
        ServerLanguage.German: "Ritualisten-Rune d. hohen Kanalisierungsmagie",
        ServerLanguage.Italian: "Runa del Ritualista Magia di Incanalamento di grado maggiore",
        ServerLanguage.Spanish: "Runa de Ritualista (Magia de canalización de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 導引魔法 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (メジャー チャネリング)",
        ServerLanguage.Polish: "Runa Rytualisty (Magia Połączeń wyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Major Channeling Magic",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Maejur Chunneleeng Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorChannelingMagic

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfMajorRestorationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Major Restoration Magic",
        ServerLanguage.Korean: "리추얼리스트 룬(상급 마력 회복)",
        ServerLanguage.French: "Rune du Ritualiste (Magie de restauration : bonus majeur)",
        ServerLanguage.German: "Ritualisten-Rune d. hohen Wiederherstellungsmagie",
        ServerLanguage.Italian: "Runa del Ritualista Magia del Ripristino di grado maggiore",
        ServerLanguage.Spanish: "Runa de Ritualista (Magia de restauración de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 復原魔法 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (メジャー レストレーション)",
        ServerLanguage.Polish: "Runa Rytualisty (Magia Odnowy wyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Major Restoration Magic",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Maejur Resturaeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorRestorationMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfMajorCommuning(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Major Communing",
        ServerLanguage.Korean: "리추얼리스트 룬(상급 교감)",
        ServerLanguage.French: "Rune du Ritualiste (Communion : bonus majeur)",
        ServerLanguage.German: "Ritualisten-Rune d. hohen Zwiesprache",
        ServerLanguage.Italian: "Runa del Ritualista Raccoglimento di grado maggiore",
        ServerLanguage.Spanish: "Runa de Ritualista (Comunión de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 神諭 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (メジャー コミューン)",
        ServerLanguage.Polish: "Runa Rytualisty (Zjednoczenie wyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Major Communing",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Maejur Cummooneeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCommuning
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfMajorSpawningPower(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Major Spawning Power",
        ServerLanguage.Korean: "리추얼리스트 룬(상급 생성)",
        ServerLanguage.French: "Rune du Ritualiste (Puissance de l'Invocation : bonus majeur)",
        ServerLanguage.German: "Ritualisten-Rune d. hohen Macht des Herbeirufens",
        ServerLanguage.Italian: "Runa del Ritualista Riti Sacrificali di grado maggiore",
        ServerLanguage.Spanish: "Runa de Ritualista (Engendramiento de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 召喚 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (メジャー スポーン パワー)",
        ServerLanguage.Polish: "Runa Rytualisty (Moc Przywoływania wyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Major Spawning Power",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Maejur Spaevneeng Pooer",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSpawningPower
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfSuperiorChannelingMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Superior Channeling Magic",
        ServerLanguage.Korean: "리추얼리스트 룬(고급 마력 증폭)",
        ServerLanguage.French: "Rune du Ritualiste (Magie de la canalisation : bonus supérieur)",
        ServerLanguage.German: "Ritualisten-Rune d. überlegenen Kanalisierungsmagie",
        ServerLanguage.Italian: "Runa del Ritualista Magia di Incanalamento di grado supremo",
        ServerLanguage.Spanish: "Runa de Ritualista (Magia de canalización de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 導引魔法 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (スーペリア チャネリング)",
        ServerLanguage.Polish: "Runa Rytualisty (Magia Połączeń najwyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Superior Channeling Magic",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Soopereeur Chunneleeng Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorChannelingMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfSuperiorRestorationMagic(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Superior Restoration Magic",
        ServerLanguage.Korean: "리추얼리스트 룬(고급 마력 회복)",
        ServerLanguage.French: "Rune du Ritualiste (Magie de restauration : bonus supérieur)",
        ServerLanguage.German: "Ritualisten-Rune d. überlegenen Wiederherstellungsmagie",
        ServerLanguage.Italian: "Runa del Ritualista Magia del Ripristino di grado supremo",
        ServerLanguage.Spanish: "Runa de Ritualista (Magia de restauración de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 復原魔法 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (スーペリア レストレーション)",
        ServerLanguage.Polish: "Runa Rytualisty (Magia Odnowy najwyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Superior Restoration Magic",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Soopereeur Resturaeshun Maegeec",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorRestorationMagic
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfSuperiorCommuning(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Superior Communing",
        ServerLanguage.Korean: "리추얼리스트 룬(고급 교감)",
        ServerLanguage.French: "Rune du Ritualiste (Communion : bonus supérieur)",
        ServerLanguage.German: "Ritualisten-Rune d. überlegenen Zwiesprache",
        ServerLanguage.Italian: "Runa del Ritualista Raccoglimento di grado supremo",
        ServerLanguage.Spanish: "Runa de Ritualista (Comunión de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 神諭 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (スーペリア コミューン)",
        ServerLanguage.Polish: "Runa Rytualisty (Zjednoczenie najwyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Superior Communing",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Soopereeur Cummooneeng",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCommuning
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class RitualistRuneOfSuperiorSpawningPower(AttributeRune):

    names = {
        ServerLanguage.English: "Ritualist Rune of Superior Spawning Power",
        ServerLanguage.Korean: "리추얼리스트 룬(고급 생성)",
        ServerLanguage.French: "Rune du Ritualiste (Puissance de l'Invocation : bonus supérieur)",
        ServerLanguage.German: "Ritualisten-Rune d. überlegenen Macht des Herbeirufens",
        ServerLanguage.Italian: "Runa del Ritualista Riti Sacrificali di grado supremo",
        ServerLanguage.Spanish: "Runa de Ritualista (Engendramiento de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 召喚 祭祀者符文",
        ServerLanguage.Japanese: "リチュアリスト ルーン (スーペリア スポーン パワー)",
        ServerLanguage.Polish: "Runa Rytualisty (Moc Przywoływania najwyższego poziomu)",
        ServerLanguage.Russian: "Ritualist Rune of Superior Spawning Power",
        ServerLanguage.BorkBorkBork: "Reetooaeleest Roone-a ooff Soopereeur Spaevneeng Pooer",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSpawningPower
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Ritualist

class UpgradeMajorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Ritualist

class UpgradeSuperiorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Ritualist

class AppliesToMinorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Ritualist

class AppliesToMajorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Ritualist

class AppliesToSuperiorRuneRitualist(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Ritualist
#endregion Ritualist

#region Dervish

class WindwalkerInsignia(Insignia):

    names = {
        ServerLanguage.English: "Windwalker Insignia [Dervish]",
        ServerLanguage.Korean: "여행가의 휘장 [더비시]",
        ServerLanguage.French: "Insigne [Derviche] du Marche-vent",
        ServerLanguage.German: "Windläufer- [Derwisch]-Befähigung",
        ServerLanguage.Italian: "Insegne [Derviscio] da Camminatore nel Vento",
        ServerLanguage.Spanish: "Insignia [Derviche] de caminante del viento",
        ServerLanguage.TraditionalChinese: "風行者 徽記 [神喚使]",
        ServerLanguage.Japanese: "ウインドウォーカー 記章 [ダルウィーシュ]",
        ServerLanguage.Polish: "[Derwisz] Symbol Włóczywiatru",
        ServerLanguage.Russian: "Windwalker Insignia [Dervish]",
        ServerLanguage.BorkBorkBork: "Veendvaelker Inseegneea [Derfeesh]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Windwalker

class ForsakenInsignia(Insignia):

    names = {
        ServerLanguage.English: "Forsaken Insignia [Dervish]",
        ServerLanguage.Korean: "고독한 휘장 [더비시]",
        ServerLanguage.French: "Insigne [Derviche] de l'oubli",
        ServerLanguage.German: "Verlassenen- [Derwisch]-Befähigung",
        ServerLanguage.Italian: "Insegne [Derviscio] da Abbandonato",
        ServerLanguage.Spanish: "Insignia [Derviche] de abandonado",
        ServerLanguage.TraditionalChinese: "背離 徽記 [神喚使]",
        ServerLanguage.Japanese: "フォーセイク 記章 [ダルウィーシュ]",
        ServerLanguage.Polish: "[Derwisz] Symbol Zapomnienia",
        ServerLanguage.Russian: "Forsaken Insignia [Dervish]",
        ServerLanguage.BorkBorkBork: "Fursaekee Inseegneea [Derfeesh]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Forsaken

class DervishRuneOfMinorMysticism(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Minor Mysticism",
        ServerLanguage.Korean: "더비시 룬(하급 신비주의)",
        ServerLanguage.French: "Rune de Derviche (Mysticisme : bonus mineur)",
        ServerLanguage.German: "Derwisch-Rune d. kleineren Mystik",
        ServerLanguage.Italian: "Runa del Derviscio Misticismo di grado minore",
        ServerLanguage.Spanish: "Runa para Derviche (Misticismo de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 祕法 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (マイナー ミスティシズム)",
        ServerLanguage.Polish: "Runa Derwisza (Mistycyzm niższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Minor Mysticism",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Meenur Mysteeceesm",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorMysticism

class DervishRuneOfMinorEarthPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Minor Earth Prayers",
        ServerLanguage.Korean: "더비시 룬(하급 대지의 기도)",
        ServerLanguage.French: "Rune de Derviche (Prières de la Terre : bonus mineur)",
        ServerLanguage.German: "Derwisch-Rune d. kleineren Erdgebete",
        ServerLanguage.Italian: "Runa del Derviscio Preghiere della Terra di grado minore",
        ServerLanguage.Spanish: "Runa para Derviche (Plegarias de tierra de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 地之祈禱 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (マイナー アース プレイヤー)",
        ServerLanguage.Polish: "Runa Derwisza (Modlitwy Ziemi niższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Minor Earth Prayers",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Meenur Iaert Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorEarthPrayers

class DervishRuneOfMinorScytheMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Minor Scythe Mastery",
        ServerLanguage.Korean: "더비시 룬(하급 사이드술)",
        ServerLanguage.French: "Rune de Derviche (Maîtrise de la faux : bonus mineur)",
        ServerLanguage.German: "Derwisch-Rune d. kleineren Sensenbeherrschung",
        ServerLanguage.Italian: "Runa del Derviscio Abilità con la Falce di grado minore",
        ServerLanguage.Spanish: "Runa para Derviche (Dominio de la guadaña de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 鐮刀精通 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (マイナー サイズ マスタリー)",
        ServerLanguage.Polish: "Runa Derwisza (Biegłość w Kosach niższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Minor Scythe Mastery",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Meenur Scyzee Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorScytheMastery

class DervishRuneOfMinorWindPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Minor Wind Prayers",
        ServerLanguage.Korean: "더비시 룬(하급 바람의 기도)",
        ServerLanguage.French: "Rune de Derviche (Prières du Vent : bonus mineur)",
        ServerLanguage.German: "Derwisch-Rune d. kleineren Windgebete",
        ServerLanguage.Italian: "Runa del Derviscio Preghiere del Vento di grado minore",
        ServerLanguage.Spanish: "Runa para Derviche (Plegarias de viento de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 風之祈禱 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (マイナー ウインド プレイヤー)",
        ServerLanguage.Polish: "Runa Derwisza (Modlitwy Wiatru niższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Minor Wind Prayers",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Meenur Veend Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorWindPrayers

class DervishRuneOfMajorMysticism(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Major Mysticism",
        ServerLanguage.Korean: "더비시 룬(상급 신비주의)",
        ServerLanguage.French: "Rune de Derviche (Mysticisme : bonus majeur)",
        ServerLanguage.German: "Derwisch-Rune d. hohen Mystik",
        ServerLanguage.Italian: "Runa del Derviscio Misticismo di grado maggiore",
        ServerLanguage.Spanish: "Runa para Derviche (Misticismo de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 祕法 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (メジャー ミスティシズム)",
        ServerLanguage.Polish: "Runa Derwisza (Mistycyzm wyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Major Mysticism",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Maejur Mysteeceesm",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorMysticism
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfMajorEarthPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Major Earth Prayers",
        ServerLanguage.Korean: "더비시 룬(상급 대지의 기도)",
        ServerLanguage.French: "Rune de Derviche (Prières de la Terre : bonus majeur)",
        ServerLanguage.German: "Derwisch-Rune d. hohen Erdgebete",
        ServerLanguage.Italian: "Runa del Derviscio Preghiere della Terra di grado maggiore",
        ServerLanguage.Spanish: "Runa para Derviche (Plegarias de tierra de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 地之祈禱 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (メジャー アース プレイヤー)",
        ServerLanguage.Polish: "Runa Derwisza (Modlitwy Ziemi wyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Major Earth Prayers",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Maejur Iaert Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorEarthPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfMajorScytheMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Major Scythe Mastery",
        ServerLanguage.Korean: "더비시 룬(상급 사이드술)",
        ServerLanguage.French: "Rune de Derviche (Maîtrise de la faux : bonus majeur)",
        ServerLanguage.German: "Derwisch-Rune d. hohen Sensenbeherrschung",
        ServerLanguage.Italian: "Runa del Derviscio Abilità con la Falce di grado maggiore",
        ServerLanguage.Spanish: "Runa para Derviche (Dominio de la guadaña de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 鐮刀精通 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (メジャー サイズ マスタリー)",
        ServerLanguage.Polish: "Runa Derwisza (Biegłość w Kosach wyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Major Scythe Mastery",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Maejur Scyzee Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorScytheMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfMajorWindPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Major Wind Prayers",
        ServerLanguage.Korean: "더비시 룬(상급 바람의 기도)",
        ServerLanguage.French: "Rune de Derviche (Prières du Vent : bonus majeur)",
        ServerLanguage.German: "Derwisch-Rune d. hohen Windgebete",
        ServerLanguage.Italian: "Runa del Derviscio Preghiere del Vento di grado maggiore",
        ServerLanguage.Spanish: "Runa para Derviche (Plegarias de viento de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 風之祈禱 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (メジャー ウインド プレイヤー)",
        ServerLanguage.Polish: "Runa Derwisza (Modlitwy Wiatru wyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Major Wind Prayers",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Maejur Veend Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorWindPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfSuperiorMysticism(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Superior Mysticism",
        ServerLanguage.Korean: "더비시 룬(고급 신비주의)",
        ServerLanguage.French: "Rune de Derviche (Mysticisme : bonus supérieur)",
        ServerLanguage.German: "Derwisch-Rune d. überlegenen Mystik",
        ServerLanguage.Italian: "Runa del Derviscio Misticismo di grado supremo",
        ServerLanguage.Spanish: "Runa para Derviche (Misticismo de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 祕法 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (スーペリア ミスティシズム)",
        ServerLanguage.Polish: "Runa Derwisza (Mistycyzm najwyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Superior Mysticism",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Soopereeur Mysteeceesm",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorMysticism
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfSuperiorEarthPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Superior Earth Prayers",
        ServerLanguage.Korean: "더비시 룬(고급 대지의 기도)",
        ServerLanguage.French: "Rune de Derviche (Prières de la Terre : bonus supérieur)",
        ServerLanguage.German: "Derwisch-Rune d. überlegenen Erdgebete",
        ServerLanguage.Italian: "Runa del Derviscio Preghiere della Terra di grado supremo",
        ServerLanguage.Spanish: "Runa para Derviche (Plegarias de tierra de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 地之祈禱 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (スーペリア アース プレイヤー)",
        ServerLanguage.Polish: "Runa Derwisza (Modlitwy Ziemi najwyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Superior Earth Prayers",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Soopereeur Iaert Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorEarthPrayers
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfSuperiorScytheMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Superior Scythe Mastery",
        ServerLanguage.Korean: "더비시 룬(고급 사이드술)",
        ServerLanguage.French: "Rune de Derviche (Maîtrise de la faux : bonus supérieur)",
        ServerLanguage.German: "Derwisch-Rune d. überlegenen Sensenbeherrschung",
        ServerLanguage.Italian: "Runa del Derviscio Abilità con la Falce di grado supremo",
        ServerLanguage.Spanish: "Runa para Derviche (Dominio de la guadaña de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 鐮刀精通 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (スーペリア サイズ マスタリー)",
        ServerLanguage.Polish: "Runa Derwisza (Biegłość w Kosach najwyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Superior Scythe Mastery",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Soopereeur Scyzee Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorScytheMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class DervishRuneOfSuperiorWindPrayers(AttributeRune):

    names = {
        ServerLanguage.English: "Dervish Rune of Superior Wind Prayers",
        ServerLanguage.Korean: "더비시 룬(고급 바람의 기도)",
        ServerLanguage.French: "Rune de Derviche (Prières du Vent : bonus supérieur)",
        ServerLanguage.German: "Derwisch-Rune d. überlegenen Windgebete",
        ServerLanguage.Italian: "Runa del Derviscio Preghiere del Vento di grado supremo",
        ServerLanguage.Spanish: "Runa para Derviche (Plegarias de viento de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 風之祈禱 神喚使符文",
        ServerLanguage.Japanese: "ダルウィーシュ ルーン (スーペリア ウインド プレイヤー)",
        ServerLanguage.Polish: "Runa Derwisza (Modlitwy Wiatru najwyższego poziomu)",
        ServerLanguage.Russian: "Dervish Rune of Superior Wind Prayers",
        ServerLanguage.BorkBorkBork: "Derfeesh Roone-a ooff Soopereeur Veend Praeyers",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorWindPrayers

    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Dervish

class UpgradeMajorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Dervish

class UpgradeSuperiorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Dervish

class AppliesToMinorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Dervish

class AppliesToMajorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Dervish

class AppliesToSuperiorRuneDervish(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Dervish
#endregion Dervish

#region Paragon

class CenturionsInsignia(Insignia):

    names = {
        ServerLanguage.English: "Centurion's Insignia [Paragon]",
        ServerLanguage.Korean: "백부장의 휘장 [파라곤]",
        ServerLanguage.French: "Insigne [Parangon] du centurion",
        ServerLanguage.German: "Zenturio- [Paragon]-Befähigung",
        ServerLanguage.Italian: "Insegne [Paragon] da Centurione",
        ServerLanguage.Spanish: "Insignia [Paragón] de centurión",
        ServerLanguage.TraditionalChinese: "百夫長 徽記 [聖言者]",
        ServerLanguage.Japanese: "センチュリオン 記章 [パラゴン]",
        ServerLanguage.Polish: "[Patron] Symbol Centuriona",
        ServerLanguage.Russian: "Centurion's Insignia [Paragon]",
        ServerLanguage.BorkBorkBork: "Centooreeun's Inseegneea [Paeraegun]",
    }
    mod_type = ItemUpgradeType.Prefix
    id = ItemUpgradeId.Centurions

class ParagonRuneOfMinorLeadership(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Minor Leadership",
        ServerLanguage.Korean: "파라곤 룬(하급 리더십)",
        ServerLanguage.French: "Rune de Parangon (Charisme : bonus mineur)",
        ServerLanguage.German: "Paragon-Rune d. kleineren Führung",
        ServerLanguage.Italian: "Runa del Paragon Leadership di grado minore",
        ServerLanguage.Spanish: "Runa de Paragón (Liderazgo de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 領導 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (マイナー リーダーシップ)",
        ServerLanguage.Polish: "Runa Patrona (Przywództwo niższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Minor Leadership",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Meenur Leaedersheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorLeadership

class ParagonRuneOfMinorMotivation(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Minor Motivation",
        ServerLanguage.Korean: "파라곤 룬(하급 격려)",
        ServerLanguage.French: "Rune de Parangon (Motivation : bonus mineur)",
        ServerLanguage.German: "Paragon-Rune d. kleineren Motivation",
        ServerLanguage.Italian: "Runa del Paragon Motivazione di grado minore",
        ServerLanguage.Spanish: "Runa de Paragón (Motivación de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 激勵 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (マイナー モチベーション)",
        ServerLanguage.Polish: "Runa Patrona (Motywacja niższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Minor Motivation",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Meenur Muteefaeshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorMotivation

class ParagonRuneOfMinorCommand(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Minor Command",
        ServerLanguage.Korean: "파라곤 룬(하급 통솔)",
        ServerLanguage.French: "Rune de Parangon (Commandement : bonus mineur)",
        ServerLanguage.German: "Paragon-Rune d. kleineren Befehlsgewalt",
        ServerLanguage.Italian: "Runa del Paragon Comando di grado minore",
        ServerLanguage.Spanish: "Runa de Paragón (Mando de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 命令 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (マイナー コマンド)",
        ServerLanguage.Polish: "Runa Patrona (Rozkazy niższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Minor Command",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Meenur Cummund",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorCommand

class ParagonRuneOfMinorSpearMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Minor Spear Mastery",
        ServerLanguage.Korean: "파라곤 룬(하급 창술)",
        ServerLanguage.French: "Rune de Parangon (Maîtrise du javelot : bonus mineur)",
        ServerLanguage.German: "Paragon-Rune d. kleineren Speerbeherrschung",
        ServerLanguage.Italian: "Runa del Paragon Abilità con la Lancia di grado minore",
        ServerLanguage.Spanish: "Runa de Paragón (Dominio de la lanza de grado menor)",
        ServerLanguage.TraditionalChinese: "初級 矛術精通 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (マイナー スピア マスタリー)",
        ServerLanguage.Polish: "Runa Patrona (Biegłość we Włóczniach niższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Minor Spear Mastery",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Meenur Speaer Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Blue
    id = ItemUpgradeId.OfMinorSpearMastery

class ParagonRuneOfMajorLeadership(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Major Leadership",
        ServerLanguage.Korean: "파라곤 룬(상급 리더십)",
        ServerLanguage.French: "Rune de Parangon (Charisme : bonus majeur)",
        ServerLanguage.German: "Paragon-Rune d. hohen Führung",
        ServerLanguage.Italian: "Runa del Paragon Leadership di grado maggiore",
        ServerLanguage.Spanish: "Runa de Paragón (Liderazgo de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 領導 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (メジャー リーダーシップ)",
        ServerLanguage.Polish: "Runa Patrona (Przywództwo wyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Major Leadership",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Maejur Leaedersheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorLeadership
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfMajorMotivation(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Major Motivation",
        ServerLanguage.Korean: "파라곤 룬(상급 격려)",
        ServerLanguage.French: "Rune de Parangon (Motivation : bonus majeur)",
        ServerLanguage.German: "Paragon-Rune d. hohen Motivation",
        ServerLanguage.Italian: "Runa del Paragon Motivazione di grado maggiore",
        ServerLanguage.Spanish: "Runa de Paragón (Motivación de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 激勵 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (メジャー モチベーション)",
        ServerLanguage.Polish: "Runa Patrona (Motywacja wyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Major Motivation",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Maejur Muteefaeshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorMotivation
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfMajorCommand(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Major Command",
        ServerLanguage.Korean: "파라곤 룬(상급 통솔)",
        ServerLanguage.French: "Rune de Parangon (Commandement : bonus majeur)",
        ServerLanguage.German: "Paragon-Rune d. hohen Befehlsgewalt",
        ServerLanguage.Italian: "Runa del Paragon Comando di grado maggiore",
        ServerLanguage.Spanish: "Runa de Paragón (Mando de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 命令 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (メジャー コマンド)",
        ServerLanguage.Polish: "Runa Patrona (Rozkazy wyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Major Command",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Maejur Cummund",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorCommand
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfMajorSpearMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Major Spear Mastery",
        ServerLanguage.Korean: "파라곤 룬(상급 창술)",
        ServerLanguage.French: "Rune de Parangon (Maîtrise du javelot : bonus majeur)",
        ServerLanguage.German: "Paragon-Rune d. hohen Speerbeherrschung",
        ServerLanguage.Italian: "Runa del Paragon Abilità con la Lancia di grado maggiore",
        ServerLanguage.Spanish: "Runa de Paragón (Dominio de la lanza de grado mayor)",
        ServerLanguage.TraditionalChinese: "中級 矛術精通 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (メジャー スピア マスタリー)",
        ServerLanguage.Polish: "Runa Patrona (Biegłość we Włóczniach wyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Major Spear Mastery",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Maejur Speaer Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Purple
    id = ItemUpgradeId.OfMajorSpearMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfSuperiorLeadership(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Superior Leadership",
        ServerLanguage.Korean: "파라곤 룬(고급 리더십)",
        ServerLanguage.French: "Rune de Parangon (Charisme : bonus supérieur)",
        ServerLanguage.German: "Paragon-Rune d. überlegenen Führung",
        ServerLanguage.Italian: "Runa del Paragon Leadership di grado supremo",
        ServerLanguage.Spanish: "Runa de Paragón (Liderazgo de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 領導 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (スーペリア リーダーシップ)",
        ServerLanguage.Polish: "Runa Patrona (Przywództwo najwyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Superior Leadership",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Soopereeur Leaedersheep",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorLeadership
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfSuperiorMotivation(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Superior Motivation",
        ServerLanguage.Korean: "파라곤 룬(고급 격려)",
        ServerLanguage.French: "Rune de Parangon (Motivation : bonus supérieur)",
        ServerLanguage.German: "Paragon-Rune d. überlegenen Motivation",
        ServerLanguage.Italian: "Runa del Paragon Motivazione di grado supremo",
        ServerLanguage.Spanish: "Runa de Paragón (Motivación de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 激勵 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (スーペリア モチベーション)",
        ServerLanguage.Polish: "Runa Patrona (Motywacja najwyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Superior Motivation",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Soopereeur Muteefaeshun",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorMotivation
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfSuperiorCommand(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Superior Command",
        ServerLanguage.Korean: "파라곤 룬(고급 통솔)",
        ServerLanguage.French: "Rune de Parangon (Commandement : bonus supérieur)",
        ServerLanguage.German: "Paragon-Rune d. überlegenen Befehlsgewalt",
        ServerLanguage.Italian: "Runa del Paragon Comando di grado supremo",
        ServerLanguage.Spanish: "Runa de Paragón (Mando de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 命令 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (スーペリア コマンド)",
        ServerLanguage.Polish: "Runa Patrona (Rozkazy najwyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Superior Command",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Soopereeur Cummund",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorCommand
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class ParagonRuneOfSuperiorSpearMastery(AttributeRune):

    names = {
        ServerLanguage.English: "Paragon Rune of Superior Spear Mastery",
        ServerLanguage.Korean: "파라곤 룬(고급 창술)",
        ServerLanguage.French: "Rune de Parangon (Maîtrise du javelot : bonus supérieur)",
        ServerLanguage.German: "Paragon-Rune d. überlegenen Speerbeherrschung",
        ServerLanguage.Italian: "Runa del Paragon Abilità con la Lancia di grado supremo",
        ServerLanguage.Spanish: "Runa de Paragón (Dominio de la lanza de grado excepcional)",
        ServerLanguage.TraditionalChinese: "高級 矛術精通 聖言者符文",
        ServerLanguage.Japanese: "パラゴン ルーン (スーペリア スピア マスタリー)",
        ServerLanguage.Polish: "Runa Patrona (Biegłość we Włóczniach najwyższego poziomu)",
        ServerLanguage.Russian: "Paragon Rune of Superior Spear Mastery",
        ServerLanguage.BorkBorkBork: "Paeraegun Roone-a ooff Soopereeur Speaer Maestery",
    }
    mod_type = ItemUpgradeType.Suffix
    rarity = Rarity.Gold
    id = ItemUpgradeId.OfSuperiorSpearMastery
    property_identifiers = [
        ModifierIdentifier.HealthMinus
    ]

class UpgradeMinorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMinorRune_Paragon

class UpgradeMajorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeMajorRune_Paragon

class UpgradeSuperiorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.UpgradeRune
    id = ItemUpgradeId.UpgradeSuperiorRune_Paragon

class AppliesToMinorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMinorRune_Paragon

class AppliesToMajorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToMajorRune_Paragon

class AppliesToSuperiorRuneParagon(Upgrade):
    mod_type = ItemUpgradeType.AppliesToRune
    id = ItemUpgradeId.AppliesToSuperiorRune_Paragon
#endregion Paragon

#endregion Armor Upgrades
