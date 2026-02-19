from dataclasses import dataclass
from enum import Enum, IntEnum, auto

from Py4GWCoreLib.enums_src.Region_enums import ServerLanguage
from Sources.frenkeyLib.ItemHandling.upgrades import ItemUpgradeClassType
class ItemBaneSpecies(IntEnum):
    Undead = 0
    Charr = 1
    Trolls = 2
    Plants = 3
    Skeletons = 4
    Giants = 5
    Dwarves = 6
    Tengus = 7
    Demons = 8
    Dragons = 9
    Ogres = 10
    Unknown = -1
    
class ModifierIdentifier(IntEnum):
    Armor1 = 0x27b
    Armor2 = 0x23c
    ArmorEnergyRegen = 0x22e
    ArmorMinusAttacking = 0x201
    ArmorPenetration = 0x23f
    ArmorPlus = 0x210
    ArmorPlusAttacking = 0x217
    ArmorPlusCasting = 0x218
    ArmorPlusEnchanted = 0x219
    ArmorPlusHexed = 0x21c
    ArmorPlusAbove = 0x21a
    ArmorPlusVsDamage = 0x211
    ArmorPlusVsElemental = 0x212
    ArmorPlusVsPhysical = 0x215
    ArmorPlusVsPhysical2 = 0x216
    ArmorPlusVsSpecies = 0x214
    ArmorPlusWhileDown = 0x21b
    AttributePlusOne = 0x241
    AttributePlusOneItem = 0x283
    AttributeRequirement = 0x279
    BaneSpecies = 0x8
    Damage = 0x27a
    Damage2 = 0x248
    DamageCustomized = 0x249
    DamagePlusEnchanted = 0x226
    DamagePlusHexed = 0x229
    DamagePlusPercent = 0x223
    DamagePlusStance = 0x22a
    DamagePlusVsHexed = 0x225
    DamagePlusVsSpecies = 0x224
    DamagePlusWhileDown = 0x228
    DamagePlusWhileUp = 0x227
    DamageTypeProperty = 0x24b
    Energy = 0x27c
    Energy2 = 0x22c
    EnergyDegen = 0x20c
    EnergyGainOnHit = 0x251
    EnergyMinus = 0x20b
    EnergyPlus = 0x22d
    EnergyPlusEnchanted = 0x22f
    EnergyPlusHexed = 0x232
    EnergyPlusWhileBelow = 0x231
    Furious = 0x23b
    HalvesCastingTimeAttribute = 0x221
    HalvesCastingTimeGeneral = 0x220
    HalvesCastingTimeItemAttribute = 0x280
    HalvesSkillRechargeAttribute = 0x239
    HalvesSkillRechargeGeneral = 0x23a
    HalvesSkillRechargeItemAttribute = 0x282
    HeadpieceAttribute = 0x21f
    HeadpieceGenericAttribute = 0x284
    HealthDegen = 0x20e
    HealthMinus = 0x20d
    HealthPlus = 0x234
    HealthPlus2 = 0x289
    HealthPlusEnchanted = 0x236
    HealthPlusHexed = 0x237
    HealthPlusStance = 0x238
    EnergyPlusWhileDown = 0x230
    HealthStealOnHit = 0x252
    HighlySalvageable = 0x260
    IncreaseConditionDuration = 0x246
    IncreaseEnchantmentDuration = 0x22b
    IncreasedSaleValue = 0x25f
    Infused = 0x262
    OfTheProfession = 0x28a
    ReceiveLessDamage = 0x207
    ReceiveLessPhysDamageEnchanted = 0x208
    ReceiveLessPhysDamageHexed = 0x209
    ReceiveLessPhysDamageStance = 0x20a
    ReduceConditionDuration = 0x285
    ReduceConditionTupleDuration = 0x277
    ReducesDiseaseDuration = 0x247
    TargetItemType = 0x25b
    TooltipDescription = 0x253
    AttributeRune = 0x21e
    Insignia_RuneOfAbsorption = 0x240

class ItemModifierParam(IntEnum):
    LabelInName = 0x0
    Description = 0x8
    
class ItemUpgradeType(IntEnum):    
    Unknown = 0
    Prefix = 1
    Suffix = 2
    Inscription = 3
    UpgradeRune = 4
    AppliesToRune = 5

        
@dataclass
class Upgrade():
    names: dict[ServerLanguage, str]
    descriptions: dict[ServerLanguage, str]
    upgrade_type : ItemUpgradeClassType
    
class Upgrades(Enum):
    Unknown = Upgrade(names={ServerLanguage.English: "Unknown"}, descriptions={ServerLanguage.English: ""}, upgrade_type=ItemUpgradeClassType.Unknown)
    AptitudeNotAttitude = Upgrade(
        names = {
        ServerLanguage.German: "\"Gut gewirkt ist halb gewonnen\"",
            ServerLanguage.English: "\"Aptitude not Attitude\"",
            ServerLanguage.Korean: "마력석: 특성이 아니라 재능이다",
            ServerLanguage.French: "\"Les compétences prévalent\"",
            ServerLanguage.Italian: "\"Inclinazione non Finzione\"",
            ServerLanguage.Spanish: "\"Aptitud, no actitud\"",
            ServerLanguage.TraditionalChinese: "\"能力而非態度\"",
            ServerLanguage.Japanese: "アプティテュード ノット アティテュード",
            ServerLanguage.Polish: "\"Talent a nie nastawienie\"",
            ServerLanguage.Russian: "\"Главное -способности, а не отношение к делу\"",
            ServerLanguage.BorkBorkBork: "\"Aepteetoode-a nut Aetteetoode-a\""},
        descriptions = {
        ServerLanguage.English: "Halves casting time on spells of item's attribute (Chance: {arg1[10248]}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    BeJustAndFearNot = Upgrade(
        names = {
        ServerLanguage.English: "\"Be Just and Fear Not\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (while Hexed)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    BrawnOverBrains = Upgrade(
        names = {
        ServerLanguage.German: "\"Körper über Geist\"",
            ServerLanguage.English: "\"Brawn over Brains\"",
            ServerLanguage.Korean: "힘보다는 머리",
            ServerLanguage.French: "\"Tout en muscles\"",
            ServerLanguage.Italian: "\"Più Muscoli che Cervello\"",
            ServerLanguage.Spanish: "\"Más vale maña que fuerza\"",
            ServerLanguage.TraditionalChinese: "\"有勇無謀\"",
            ServerLanguage.Japanese: "ブローン オーバー ブレイン",
            ServerLanguage.Polish: "\"Siła ponad umysł\"",
            ServerLanguage.Russian: "\"Сила есть -ума не надо\"",
            ServerLanguage.BorkBorkBork: "\"Braevn oofer Braeeens\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2[8760]}%\nEnergy -{arg2[8376]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    CastOutTheUnclean = Upgrade(
        names = {
        ServerLanguage.German: "\"Gute Besserung!\"",
            ServerLanguage.English: "\"Cast Out the Unclean\"",
            ServerLanguage.Korean: "불결한 건 가랏!",
            ServerLanguage.French: "\"Au rebut les impurs\"",
            ServerLanguage.Italian: "\"Esorcizza l'Eresia\"",
            ServerLanguage.Spanish: "\"Desterremos a los impuros\"",
            ServerLanguage.TraditionalChinese: "\"驅除不潔\"",
            ServerLanguage.Japanese: "キャスト アウト ザ アンクリーン",
            ServerLanguage.Polish: "\"Wyrzuć nieczystych\"",
            ServerLanguage.Russian: "\"Изгнать нечистых\"",
            ServerLanguage.BorkBorkBork: "\"Caest Oooot zee Uncleun\""},
        descriptions = {
        ServerLanguage.English: "Reduces Disease duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DanceWithDeath = Upgrade(
        names = {
        ServerLanguage.German: "\"Tanz mit dem Tod\"",
            ServerLanguage.English: "\"Dance with Death\"",
            ServerLanguage.Korean: "마력석: 죽음과 함께 춤을",
            ServerLanguage.French: "\"Danse avec la mort\"",
            ServerLanguage.Italian: "\"Balla coi Lutti\"",
            ServerLanguage.Spanish: "\"Baila con la muerte\"",
            ServerLanguage.TraditionalChinese: "\"與死亡共舞\"",
            ServerLanguage.Japanese: "ダンス ウィズ デス",
            ServerLanguage.Polish: "\"Taniec ze śmiercią\"",
            ServerLanguage.Russian: "\"Танец со смертью\"",
            ServerLanguage.BorkBorkBork: "\"Dunce-a veet Deaet\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2}% (while in a Stance)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DontFearTheReaper = Upgrade(
        names = {
        ServerLanguage.German: "\"Keine Angst vorm Sensenmann\"",
            ServerLanguage.English: "\"Don't Fear the Reaper\"",
            ServerLanguage.Korean: "사신을 두려워하지 마라",
            ServerLanguage.French: "\"Ne craignez pas le Faucheur\"",
            ServerLanguage.Italian: "\"Non Temere la Falce\"",
            ServerLanguage.Spanish: "\"No temas la guadaña\"",
            ServerLanguage.TraditionalChinese: "\"無懼死亡\"",
            ServerLanguage.Japanese: "ドント フィアー ザ リーパー",
            ServerLanguage.Polish: "\"Nie bój się żniwiarza\"",
            ServerLanguage.Russian: "\"Не бойся жнеца\"",
            ServerLanguage.BorkBorkBork: "\"Dun't Feaer zee Reaeper\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2}% (while Hexed)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DontThinkTwice = Upgrade(
        names = {
        ServerLanguage.German: "\"Zauderei ist keine Zier\"",
            ServerLanguage.English: "\"Don't Think Twice\"",
            ServerLanguage.Korean: "두 번 생각하지 마라",
            ServerLanguage.French: "\"Pas le temps de réfléchir\"",
            ServerLanguage.Italian: "\"Non Pensarci Due Volte\"",
            ServerLanguage.Spanish: "\"No te lo pienses\"",
            ServerLanguage.TraditionalChinese: "\"別再考慮\"",
            ServerLanguage.Japanese: "ドント シンク トゥワイス",
            ServerLanguage.Polish: "\"Nie zastanawiaj się\"",
            ServerLanguage.Russian: "\"А что тут думать?\"",
            ServerLanguage.BorkBorkBork: "\"Dun't Theenk Tveece-a\""},
        descriptions = {
        ServerLanguage.English: "Halves casting time of spells (Chance: +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DontCallItAComback = Upgrade(
        names = {
        ServerLanguage.German: "\"Sie kehren niemals wieder\"",
            ServerLanguage.English: "\"Don't call it a comeback!\"",
            ServerLanguage.Korean: "단순한 회복이 아니다!",
            ServerLanguage.French: "\"Aucun recours !\"",
            ServerLanguage.Italian: "\"Non Consideratelo un Ritorno!\"",
            ServerLanguage.Spanish: "\"¡No será la última palabra!\"",
            ServerLanguage.TraditionalChinese: "\"別說我不行！\"",
            ServerLanguage.Japanese: "ドント コール イット ア カムバック！",
            ServerLanguage.Polish: "\"Nie nazywaj tego powrotem!\"",
            ServerLanguage.Russian: "\"Не считай это местью!\"",
            ServerLanguage.BorkBorkBork: "\"Dun't caell it a cumebaeck!\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2} (while Health is below +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DownButNotOut = Upgrade(
        names = {
        ServerLanguage.English: "\"Down But Not Out\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (while Health is below +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    FaithIsMyShield = Upgrade(
        names = {
        ServerLanguage.German: "\"Der Glaube ist mein Schild!\"",
            ServerLanguage.English: "\"Faith is My Shield\"",
            ServerLanguage.Korean: "신념은 나의 방패다",
            ServerLanguage.French: "\"La foi est mon bouclier\"",
            ServerLanguage.Italian: "\"La Fede è il Mio Scudo\"",
            ServerLanguage.Spanish: "\"La fe es mi escudo\"",
            ServerLanguage.TraditionalChinese: "\"信念是盾\"",
            ServerLanguage.Japanese: "フェイス イズ マイ シールド",
            ServerLanguage.Polish: "\"Wiara jest mą tarczą\"",
            ServerLanguage.Russian: "\"Вера послужит мне щитом\"",
            ServerLanguage.BorkBorkBork: "\"Faeeet is My Sheeeld\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (while Enchanted)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    FearCutsDeeper = Upgrade(
        names = {
        ServerLanguage.German: "\"Die Furcht schneidet tiefer\"",
            ServerLanguage.English: "\"Fear Cuts Deeper\"",
            ServerLanguage.Korean: "공포는 더 깊은 상처를 낸다",
            ServerLanguage.French: "\"La peur fait plus de mal\"",
            ServerLanguage.Italian: "\"Il Timore Trafigge\"",
            ServerLanguage.Spanish: "\"El miedo hace más daño\"",
            ServerLanguage.TraditionalChinese: "\"戒除恐懼\"",
            ServerLanguage.Japanese: "フィアー カッツ ディーパー",
            ServerLanguage.Polish: "\"Strach rani głęboko\"",
            ServerLanguage.Russian: "\"Страх острее бритвы\"",
            ServerLanguage.BorkBorkBork: "\"Feaer Coots Deeper\""},
        descriptions = {
        ServerLanguage.English: "Reduces Bleeding duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ForgetMeNot = Upgrade(
        names = {
        ServerLanguage.German: "\"Vergesst mein nicht!\"",
            ServerLanguage.English: "\"Forget Me Not\"",
            ServerLanguage.Korean: "물망초",
            ServerLanguage.French: "\"Souvenir gravé à jamais\"",
            ServerLanguage.Italian: "\"Non Ti Scordar di Me\"",
            ServerLanguage.Spanish: "\"No me olvides\"",
            ServerLanguage.TraditionalChinese: "\"勿忘我\"",
            ServerLanguage.Japanese: "フォーゲット ミー ノット",
            ServerLanguage.Polish: "\"Nie zapomnij mnie\"",
            ServerLanguage.Russian: "\"Незабудка\"",
            ServerLanguage.BorkBorkBork: "\"Furget Me-a Nut\""},
        descriptions = {
        ServerLanguage.English: "Halves skill recharge of item's attribute spells (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    GuidedByFate = Upgrade(
        names = {
        ServerLanguage.German: "\"Wink des Schicksals\"",
            ServerLanguage.English: "\"Guided by Fate\"",
            ServerLanguage.Korean: "마력석: 운명의 이끌림",
            ServerLanguage.French: "\"Soyez maître de votre destin\"",
            ServerLanguage.Italian: "\"Guidato dal Fato\"",
            ServerLanguage.Spanish: "\"Guiado por el destino\"",
            ServerLanguage.TraditionalChinese: "\"命運\"",
            ServerLanguage.Japanese: "ガイデッド バイ フェイト",
            ServerLanguage.Polish: "\"Prowadzi mnie przeznaczenie\"",
            ServerLanguage.Russian: "\"Ведомый роком\"",
            ServerLanguage.BorkBorkBork: "\"Gooeeded by Faete-a\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2}% (while Enchanted)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    HailToTheKing = Upgrade(
        names = {
        ServerLanguage.German: "\"Gelobt sei der König\"",
            ServerLanguage.English: "\"Hail to the King\"",
            ServerLanguage.Korean: "국왕 폐하 만세",
            ServerLanguage.French: "\"Longue vie au roi\"",
            ServerLanguage.Italian: "\"Viva il Re\"",
            ServerLanguage.Spanish: "\"Viva el rey\"",
            ServerLanguage.TraditionalChinese: "\"與王致敬\"",
            ServerLanguage.Japanese: "ヘイル トゥ ザ キング",
            ServerLanguage.Polish: "\"Niech żyje król\"",
            ServerLanguage.Russian: "\"Да здравствует король!\"",
            ServerLanguage.BorkBorkBork: "\"Haeeel tu zee Keeng\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (while Health is above +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    HaleAndHearty = Upgrade(
        names = {
        ServerLanguage.German: "\"Gesund und munter\"",
            ServerLanguage.English: "\"Hale and Hearty\"",
            ServerLanguage.Korean: "마력석: 원기왕성하게!",
            ServerLanguage.French: "\"En pleine santé\"",
            ServerLanguage.Italian: "\"Vivo e Vegeto\"",
            ServerLanguage.Spanish: "\"Viejo pero joven\"",
            ServerLanguage.TraditionalChinese: "\"健壯的\"",
            ServerLanguage.Japanese: "ヘイル アンド ハーティー",
            ServerLanguage.Polish: "\"Zdrowy i krzepki\"",
            ServerLanguage.Russian: "\"Сильный и здоровый\"",
            ServerLanguage.BorkBorkBork: "\"Haele-a und Heaerty\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2} (while health is above +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    HaveFaith = Upgrade(
        names = {
        ServerLanguage.German: "\"Habt Vertrauen\"",
            ServerLanguage.English: "\"Have Faith\"",
            ServerLanguage.Korean: "신념을 가져라",
            ServerLanguage.French: "\"Ayez la foi\"",
            ServerLanguage.Italian: "\"Abbi Fede\"",
            ServerLanguage.Spanish: "\"Tened fe\"",
            ServerLanguage.TraditionalChinese: "\"信念\"",
            ServerLanguage.Japanese: "ハブ フェイス",
            ServerLanguage.Polish: "\"Miej wiarę\"",
            ServerLanguage.Russian: "\"Не теряй веру\"",
            ServerLanguage.BorkBorkBork: "\"Haefe-a Faeeet\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2} (while Enchanted)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ICanSeeClearlyNow = Upgrade(
        names = {
        ServerLanguage.German: "\"Klar wie Morgentau\"",
            ServerLanguage.English: "\"I Can See Clearly Now\"",
            ServerLanguage.Korean: "마력석: 모든 게 뚜렷하게 보인다",
            ServerLanguage.French: "\"Je vois clair à présent\"",
            ServerLanguage.Italian: "\"Chiara Come Un'Alba\"",
            ServerLanguage.Spanish: "\"He abierto los ojos\"",
            ServerLanguage.TraditionalChinese: "\"光明再現\"",
            ServerLanguage.Japanese: "アイ キャン シー クリアリー ナウ",
            ServerLanguage.Polish: "\"Widzę to teraz wyraźnie\"",
            ServerLanguage.Russian: "\"Теперь я ясно вижу\"",
            ServerLanguage.BorkBorkBork: "\"I Cun See-a Cleaerly Noo\""},
        descriptions = {
        ServerLanguage.English: "Reduces Blind duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    IAmSorrow = Upgrade(
        names = {
        ServerLanguage.German: "\"Ich bin es Leid\"",
            ServerLanguage.English: "\"I am Sorrow.\"",
            ServerLanguage.Korean: "너무 슬프군",
            ServerLanguage.French: "\"Je suis la douleur\"",
            ServerLanguage.Italian: "\"Io Sono la Sofferenza\"",
            ServerLanguage.Spanish: "\"Un mar de lágrimas\"",
            ServerLanguage.TraditionalChinese: "\"倍感憂傷\"",
            ServerLanguage.Japanese: "アイ アム ソロウ",
            ServerLanguage.Polish: "\"Jestem smutkiem.\"",
            ServerLanguage.Russian: "\"Я -воплощение скорби\"",
            ServerLanguage.BorkBorkBork: "\"I aem Surroo.\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2} (while hexed)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    IHaveThePower = Upgrade(
        names = {
        ServerLanguage.German: "\"Ich habe die Kraft!\"",
            ServerLanguage.English: "\"I have the power!\"",
            ServerLanguage.Korean: "마력석: 내겐 에너지가 있다!",
            ServerLanguage.French: "\"Je détiens le pouvoir !\"",
            ServerLanguage.Italian: "\"A Me Il Potere!\"",
            ServerLanguage.Spanish: "\"¡Tengo el poder!\"",
            ServerLanguage.TraditionalChinese: "\"充滿力量！\"",
            ServerLanguage.Japanese: "アイ ハブ ザ パワー！",
            ServerLanguage.Polish: "\"Mam moc!\"",
            ServerLanguage.Russian: "\"Сила в моих руках!\"",
            ServerLanguage.BorkBorkBork: "\"I haefe-a zee pooer!\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    IgnoranceIsBliss = Upgrade(
        names = {
        ServerLanguage.German: "\"Was ich nicht weiß ...\"",
            ServerLanguage.English: "\"Ignorance is Bliss\"",
            ServerLanguage.Korean: "모르는 게 약이다",
            ServerLanguage.French: "\"Il vaut mieux ne pas savoir\"",
            ServerLanguage.Italian: "\"Benedetta Ignoranza\"",
            ServerLanguage.Spanish: "\"La ignorancia es felicidad\"",
            ServerLanguage.TraditionalChinese: "\"傻人有傻福\"",
            ServerLanguage.Japanese: "イグノーランス イズ ブリス",
            ServerLanguage.Polish: "\"Ignorancja jest błogosławieństwem\"",
            ServerLanguage.Russian: "\"Счастлив в неведении\"",
            ServerLanguage.BorkBorkBork: "\"Ignurunce-a is Bleess\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2[8456]}\nEnergy -{arg2[8376]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    KnowingIsHalfTheBattle = Upgrade(
        names = {
        ServerLanguage.English: "\"Knowing is Half the Battle\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (while casting)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    LeafOnTheWind = Upgrade(
        names = {
        ServerLanguage.German: "\"Grashalm im Wind\"",
            ServerLanguage.English: "\"Leaf on the Wind\"",
            ServerLanguage.Korean: "바람에 떠다니는 나뭇잎",
            ServerLanguage.French: "\"La feuille portée par le vent\"",
            ServerLanguage.Italian: "\"Foglia nel Vento\"",
            ServerLanguage.Spanish: "\"Hoja en el viento\"",
            ServerLanguage.TraditionalChinese: "\"風中之葉\"",
            ServerLanguage.Japanese: "リーフ オン ザ ウインド",
            ServerLanguage.Polish: "\"Liść na wietrze\"",
            ServerLanguage.Russian: "\"Лист на ветру\"",
            ServerLanguage.BorkBorkBork: "\"Leaeff oon zee Veend\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Cold damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    LetTheMemoryLiveAgain = Upgrade(
        names = {
        ServerLanguage.German: "\"Auf die Erinnerung!\"",
            ServerLanguage.English: "\"Let the Memory Live Again\"",
            ServerLanguage.Korean: "기억이여, 되살아나라",
            ServerLanguage.French: "\"Vers l'infini et au-delà\"",
            ServerLanguage.Italian: "\"Facciamo Rivivere i Ricordi\"",
            ServerLanguage.Spanish: "\"Que vuelvan los recuerdos\"",
            ServerLanguage.TraditionalChinese: "\"記憶復甦\"",
            ServerLanguage.Japanese: "レット ザ メモリー リブ アゲイン",
            ServerLanguage.Polish: "\"Niech pamięć ponownie ożyje\"",
            ServerLanguage.Russian: "\"Пусть оживут воспоминания\"",
            ServerLanguage.BorkBorkBork: "\"Let zee Memury Leefe-a Aegaeeen\""},
        descriptions = {
        ServerLanguage.English: "Halves skill recharge of spells (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    LifeIsPain = Upgrade(
        names = {
        ServerLanguage.English: "\"Life is Pain\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2[8456]}\nHealth -{arg2[8408]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    LikeARollingStone = Upgrade(
        names = {
        ServerLanguage.German: "\"Marmor, Stein und Erde bricht\"",
            ServerLanguage.English: "\"Like a Rolling Stone\"",
            ServerLanguage.Korean: "구르는 돌처럼",
            ServerLanguage.French: "\"Solide comme le roc\"",
            ServerLanguage.Italian: "\"Come Una Pietra Scalciata\"",
            ServerLanguage.Spanish: "\"Like a Rolling Stone\"",
            ServerLanguage.TraditionalChinese: "\"漂泊者\"",
            ServerLanguage.Japanese: "ライク ア ローリング ストーン",
            ServerLanguage.Polish: "\"Jak wędrowiec\"",
            ServerLanguage.Russian: "\"Как перекати-поле\"",
            ServerLanguage.BorkBorkBork: "\"Leeke-a a Rulleeng Stune-a\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Earth damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    LiveForToday = Upgrade(
        names = {
        ServerLanguage.German: "\"Lebt den Tag\"",
            ServerLanguage.English: "\"Live for Today\"",
            ServerLanguage.Korean: "오늘을 위해 최선을",
            ServerLanguage.French: "\"Aujourd'hui, la vie\"",
            ServerLanguage.Italian: "\"Vivi alla Giornata\"",
            ServerLanguage.Spanish: "\"Vive el presente\"",
            ServerLanguage.TraditionalChinese: "\"活在當下\"",
            ServerLanguage.Japanese: "リブ フォー トゥデイ",
            ServerLanguage.Polish: "\"Żyj dniem dzisiejszym\"",
            ServerLanguage.Russian: "\"Живи сегодняшним днем\"",
            ServerLanguage.BorkBorkBork: "\"Leefe-a fur Tudaey\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2[8920]}\nEnergy regeneration -{arg2[8392]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    LuckOfTheDraw = Upgrade(
        names = {
        ServerLanguage.German: "\"Glück im Spiel ...\"",
            ServerLanguage.English: "\"Luck of the Draw\"",
            ServerLanguage.Korean: "비김의 행운",
            ServerLanguage.French: "\"Une question de chance\"",
            ServerLanguage.Italian: "\"La Fortuna è Cieca\"",
            ServerLanguage.Spanish: "\"La suerte del apostante\"",
            ServerLanguage.TraditionalChinese: "\"全憑運氣\"",
            ServerLanguage.Japanese: "ラック オブ ザ ドロー",
            ServerLanguage.Polish: "\"Szczęśliwe rozdanie\"",
            ServerLanguage.Russian: "\"Счастливый жребий\"",
            ServerLanguage.BorkBorkBork: "\"Loock ooff zee Draev\""},
        descriptions = {
        ServerLanguage.English: "Received physical damage -{arg2} (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ManForAllSeasons = Upgrade(
        names = {
        ServerLanguage.English: "\"Man for All Seasons\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Elemental damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    MasterOfMyDomain = Upgrade(
        names = {
        ServerLanguage.German: "\"Herr in meinem Haus\"",
            ServerLanguage.English: "\"Master of My Domain!\"",
            ServerLanguage.Korean: "마력석: 내 공간의 지배자",
            ServerLanguage.French: "\"Maître du Domaine\"",
            ServerLanguage.Italian: "\"Padrone in Casa Mia\"",
            ServerLanguage.Spanish: "\"Amo de mi reino\"",
            ServerLanguage.TraditionalChinese: "\"這是我的地盤！\"",
            ServerLanguage.Japanese: "マスター オブ マイ ドメイン",
            ServerLanguage.Polish: "\"Pan mego królestwa\"",
            ServerLanguage.Russian: "\"Я сам себе хозяин\"",
            ServerLanguage.BorkBorkBork: "\"Maester ooff My Dumaeeen\""},
        descriptions = {
        ServerLanguage.English: "Item's attribute +1 (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    MeasureForMeasure = Upgrade(
        names = {
        ServerLanguage.German: "\"Maß für Maß\"",
            ServerLanguage.English: "\"Measure for Measure\"",
            ServerLanguage.Korean: "다다익선",
            ServerLanguage.French: "\"Mesure pour mesure.\"",
            ServerLanguage.Italian: "\"Occhio per Occhio\"",
            ServerLanguage.Spanish: "\"Ojo por ojo\"",
            ServerLanguage.TraditionalChinese: "\"以牙還牙\"",
            ServerLanguage.Japanese: "メジャー フォー メジャー",
            ServerLanguage.Polish: "\"Miarka za miarkę\"",
            ServerLanguage.Russian: "\"Око за око\"",
            ServerLanguage.BorkBorkBork: "\"Meaesoore-a fur Meaesoore-a\""},
        descriptions = {
        ServerLanguage.English: "Highly salvageable"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    MightMakesRight = Upgrade(
        names = {
        ServerLanguage.English: "\"Might Makes Right\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (while attacking)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    NotTheFace = Upgrade(
        names = {
        ServerLanguage.German: "\"Nicht das Gesicht!\"",
            ServerLanguage.English: "\"Not the Face!\"",
            ServerLanguage.Korean: "얼굴은 안 돼!",
            ServerLanguage.French: "\"Pas le visage !\"",
            ServerLanguage.Italian: "\"Non al Volto!\"",
            ServerLanguage.Spanish: "\"¡En la cara no!\"",
            ServerLanguage.TraditionalChinese: "\"不要打臉！\"",
            ServerLanguage.Japanese: "ノット ザ フェース！",
            ServerLanguage.Polish: "\"Nie po twarzy!\"",
            ServerLanguage.Russian: "\"Только не в лицо!\"",
            ServerLanguage.BorkBorkBork: "\"Nut zee faece-a!\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Blunt damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    NothingToFear = Upgrade(
        names = {
        ServerLanguage.German: "\"Nichts zu befürchten\"",
            ServerLanguage.English: "\"Nothing to Fear\"",
            ServerLanguage.Korean: "두려울 건 없다",
            ServerLanguage.French: "\"Rien à craindre\"",
            ServerLanguage.Italian: "\"Niente Paura\"",
            ServerLanguage.Spanish: "\"Nada que temer\"",
            ServerLanguage.TraditionalChinese: "\"無畏無懼\"",
            ServerLanguage.Japanese: "ナッシング トゥ フィアー",
            ServerLanguage.Polish: "\"Nieulękły\"",
            ServerLanguage.Russian: "\"Нечего бояться\"",
            ServerLanguage.BorkBorkBork: "\"Nutheeng tu Feaer\""},
        descriptions = {
        ServerLanguage.English: "Received physical damage -{arg2} (while Hexed)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    OnlyTheStrongSurvive = Upgrade(
        names = {
        ServerLanguage.German: "\"Nur die Stärksten überleben!\"",
            ServerLanguage.English: "\"Only the Strong Survive\"",
            ServerLanguage.Korean: "강자만이 살아남는다",
            ServerLanguage.French: "\"Seuls les plus forts survivent\"",
            ServerLanguage.Italian: "\"Superstite è soltanto il Forte\"",
            ServerLanguage.Spanish: "\"Sólo sobreviven los más fuertes\"",
            ServerLanguage.TraditionalChinese: "\"強者生存\"",
            ServerLanguage.Japanese: "オンリー ザ ストロング サバイブ",
            ServerLanguage.Polish: "\"Tylko silni przetrwają\"",
            ServerLanguage.Russian: "\"Выживает сильнейший\"",
            ServerLanguage.BorkBorkBork: "\"Oonly zee Strung Soorfeefe-a\""},
        descriptions = {
        ServerLanguage.English: "Reduces Weakness duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    PureOfHeart = Upgrade(
        names = {
        ServerLanguage.German: "\"Mein Herz ist rein\"",
            ServerLanguage.English: "\"Pure of Heart\"",
            ServerLanguage.Korean: "심장의 깨끗함",
            ServerLanguage.French: "\"Pureté du coeur\"",
            ServerLanguage.Italian: "\"Purezza di Cuore\"",
            ServerLanguage.Spanish: "\"Puro de corazón\"",
            ServerLanguage.TraditionalChinese: "\"純淨之心\"",
            ServerLanguage.Japanese: "ピュア オブ ハート",
            ServerLanguage.Polish: "\"Czystość serca\"",
            ServerLanguage.Russian: "\"Чистые сердцем\"",
            ServerLanguage.BorkBorkBork: "\"Poore-a ooff Heaert\""},
        descriptions = {
        ServerLanguage.English: "Reduces Poison duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    RidersOnTheStorm = Upgrade(
        names = {
        ServerLanguage.German: "\"Geblitzt wird nicht!\"",
            ServerLanguage.English: "\"Riders on the Storm\"",
            ServerLanguage.Korean: "폭풍의 기수",
            ServerLanguage.French: "\"Les chevaliers du ciel\"",
            ServerLanguage.Italian: "\"Viaggiatori nella Burrasca\"",
            ServerLanguage.Spanish: "\"Jinetes de la tormenta\"",
            ServerLanguage.TraditionalChinese: "\"暴風騎士\"",
            ServerLanguage.Japanese: "ライダー オン ザ ストーム",
            ServerLanguage.Polish: "\"Jeźdźcy burzy\"",
            ServerLanguage.Russian: "\"Всадники бури\"",
            ServerLanguage.BorkBorkBork: "\"Reeders oon zee Sturm\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Lightning damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    RunForYourLife = Upgrade(
        names = {
        ServerLanguage.German: "\"Rennt um Euer Leben!\"",
            ServerLanguage.English: "\"Run For Your Life!\"",
            ServerLanguage.Korean: "살기 위해 달려라!",
            ServerLanguage.French: "\"Sauve-qui-peut !\"",
            ServerLanguage.Italian: "\"Gambe in Spalla!\"",
            ServerLanguage.Spanish: "\"¡Ponte a salvo!\"",
            ServerLanguage.TraditionalChinese: "\"逃命\"",
            ServerLanguage.Japanese: "ラン フォー ユア ライフ！",
            ServerLanguage.Polish: "\"Ratuj się kto może!\"",
            ServerLanguage.Russian: "\"Спасайся, кто может!\"",
            ServerLanguage.BorkBorkBork: "\"Roon Fur Yuoor Leeffe-a!\""},
        descriptions = {
        ServerLanguage.English: "Received physical damage -{arg2} (while in a Stance)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SeizeTheDay = Upgrade(
        names = {
        ServerLanguage.German: "\"Lebt den Tag\"",
            ServerLanguage.English: "\"Seize the Day\"",
            ServerLanguage.Korean: "오늘을 위해 최선을",
            ServerLanguage.French: "\"Aujourd'hui, la vie\"",
            ServerLanguage.Italian: "\"Vivi alla Giornata\"",
            ServerLanguage.Spanish: "\"Vive el presente\"",
            ServerLanguage.TraditionalChinese: "\"活在當下\"",
            ServerLanguage.Japanese: "リブ フォー トゥデイ",
            ServerLanguage.Polish: "\"Żyj dniem dzisiejszym\"",
            ServerLanguage.Russian: "\"Живи сегодняшним днем\"",
            ServerLanguage.BorkBorkBork: "\"Leefe-a fur Tudaey\""},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2[8920]}\nEnergy regeneration -{arg2[8392]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SerenityNow = Upgrade(
        names = {
        ServerLanguage.German: "\"Auf die Gelassenheit\"",
            ServerLanguage.English: "\"Serenity Now\"",
            ServerLanguage.Korean: "평정을 찾아라",
            ServerLanguage.French: "\"Un peu de sérénité\"",
            ServerLanguage.Italian: "\"Serenità Immediata\"",
            ServerLanguage.Spanish: "\"Calma ahora\"",
            ServerLanguage.TraditionalChinese: "\"平靜\"",
            ServerLanguage.Japanese: "セレニティ ナウ",
            ServerLanguage.Polish: "\"Niech nastanie spokój\"",
            ServerLanguage.Russian: "\"Спокойствие, только спокойствие!\"",
            ServerLanguage.BorkBorkBork: "\"Sereneety Noo\""},
        descriptions = {
        ServerLanguage.English: "Halves skill recharge of spells (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ShelteredByFaith = Upgrade(
        names = {
        ServerLanguage.German: "\"Vertrauen ist gut\"",
            ServerLanguage.English: "\"Sheltered by Faith\"",
            ServerLanguage.Korean: "신념의 보호",
            ServerLanguage.French: "\"Protégé par la Foi\"",
            ServerLanguage.Italian: "\"Rifugio della Speranza\"",
            ServerLanguage.Spanish: "\"Fe ciega\"",
            ServerLanguage.TraditionalChinese: "\"信念守護\"",
            ServerLanguage.Japanese: "シェルター バイ フェイス",
            ServerLanguage.Polish: "\"Chroniony przez wiarę\"",
            ServerLanguage.Russian: "\"Под защитой веры\"",
            ServerLanguage.BorkBorkBork: "\"Sheltered by Faeeet\""},
        descriptions = {
        ServerLanguage.English: "Received physical damage -{arg2} (while Enchanted)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ShowMeTheMoney = Upgrade(
        names = {
        ServerLanguage.German: "\"Geld macht glücklich!\"",
            ServerLanguage.English: "\"Show me the money!\"",
            ServerLanguage.Korean: "돈이다!",
            ServerLanguage.French: "\"Par ici la monnaie !\"",
            ServerLanguage.Italian: "\"Mostrami la Grana!\"",
            ServerLanguage.Spanish: "\"¡Enséñame la pasta!\"",
            ServerLanguage.TraditionalChinese: "\"給我錢！\"",
            ServerLanguage.Japanese: "ショー ミー ザ マネー！",
            ServerLanguage.Polish: "\"Pokaż pieniądze!\"",
            ServerLanguage.Russian: "\"Покажи мне деньги!\"",
            ServerLanguage.BorkBorkBork: "\"Shoo me-a zee muney!\""},
        descriptions = {
        ServerLanguage.English: "Improved sale value"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SleepNowInTheFire = Upgrade(
        names = {
        ServerLanguage.German: "\"Geborgenheit im Feuer\"",
            ServerLanguage.English: "\"Sleep Now in the Fire\"",
            ServerLanguage.Korean: "화염 속에 잠들라",
            ServerLanguage.French: "\"Faisons la lumière sur les ténèbres\"",
            ServerLanguage.Italian: "\"Dormi Ardentemente\"",
            ServerLanguage.Spanish: "\"Descansa en la hoguera\"",
            ServerLanguage.TraditionalChinese: "\"烈焰中歇息\"",
            ServerLanguage.Japanese: "スリープ ナウ イン ザ ファイア",
            ServerLanguage.Polish: "\"Zaśnij w ogniu\"",
            ServerLanguage.Russian: "\"Покойся в пламени\"",
            ServerLanguage.BorkBorkBork: "\"Sleep Noo in zee Fure-a\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Fire damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SoundnessOfMind = Upgrade(
        names = {
        ServerLanguage.German: "\"Ein gesunder Geist ...\"",
            ServerLanguage.English: "\"Soundness of Mind\"",
            ServerLanguage.Korean: "마음의 소리",
            ServerLanguage.French: "\"Bon sens\"",
            ServerLanguage.Italian: "\"Mente Sana\"",
            ServerLanguage.Spanish: "\"Sano juicio\"",
            ServerLanguage.TraditionalChinese: "\"堅定意念\"",
            ServerLanguage.Japanese: "サウンドネス オブ マインド",
            ServerLanguage.Polish: "\"Mądrość umysłu\"",
            ServerLanguage.Russian: "\"Здравый рассудок\"",
            ServerLanguage.BorkBorkBork: "\"Suoondness ooff Meend\""},
        descriptions = {
        ServerLanguage.English: "Reduces Dazed duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    StrengthAndHonor = Upgrade(
        names = {
        ServerLanguage.German: "\"Stärke und Ehre\"",
            ServerLanguage.English: "\"Strength and Honor\"",
            ServerLanguage.Korean: "마력석: 힘과 명예",
            ServerLanguage.French: "\"Force et honneur\"",
            ServerLanguage.Italian: "\"Forza e Onore\"",
            ServerLanguage.Spanish: "\"Fuerza y honor\"",
            ServerLanguage.TraditionalChinese: "\"力與榮耀\"",
            ServerLanguage.Japanese: "ストレングス アンド オナー",
            ServerLanguage.Polish: "\"Siła i honor\"",
            ServerLanguage.Russian: "\"Сила и честь\"",
            ServerLanguage.BorkBorkBork: "\"Strengt und Hunur\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2}% (while Health is above +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    StrengthOfBody = Upgrade(
        names = {
        ServerLanguage.German: "\"Hart im Nehmen\"",
            ServerLanguage.English: "\"Strength of Body\"",
            ServerLanguage.Korean: "육체의 힘",
            ServerLanguage.French: "\"La Force réside du corps\"",
            ServerLanguage.Italian: "\"Corpo Gagliardo\"",
            ServerLanguage.Spanish: "\"Fuerza bruta\"",
            ServerLanguage.TraditionalChinese: "\"力貫全身\"",
            ServerLanguage.Japanese: "ストレングス オブ ボディ",
            ServerLanguage.Polish: "\"Siła ciała\"",
            ServerLanguage.Russian: "\"Сила тела\"",
            ServerLanguage.BorkBorkBork: "\"Strengt ooff Budy\""},
        descriptions = {
        ServerLanguage.English: "Reduces Deep Wound duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SurvivalOfTheFittest = Upgrade(
        names = {
        ServerLanguage.German: "\"Hart wie Stahl\"",
            ServerLanguage.English: "\"Survival of the Fittest\"",
            ServerLanguage.Korean: "적자생존",
            ServerLanguage.French: "\"La survie du plus fort\"",
            ServerLanguage.Italian: "\"Sopravvivenza Integrale\"",
            ServerLanguage.Spanish: "\"Supervivencia del más fuerte\"",
            ServerLanguage.TraditionalChinese: "\"適者生存\"",
            ServerLanguage.Japanese: "サバイバル オブ ザ フィッテスト",
            ServerLanguage.Polish: "\"Przetrwają najsilniejsi\"",
            ServerLanguage.Russian: "\"Естественный отбор\"",
            ServerLanguage.BorkBorkBork: "\"Soorfeefael ooff zee Feettest\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Physical damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SwiftAsTheWind = Upgrade(
        names = {
        ServerLanguage.German: "\"Schnell wie der Wind\"",
            ServerLanguage.English: "\"Swift as the Wind\"",
            ServerLanguage.Korean: "바람처럼 빠르게",
            ServerLanguage.French: "\"Rapide comme le vent\"",
            ServerLanguage.Italian: "\"Raffica di Bora\"",
            ServerLanguage.Spanish: "\"Veloz como el viento\"",
            ServerLanguage.TraditionalChinese: "\"迅捷如風\"",
            ServerLanguage.Japanese: "スウィフト アズ ザ ウインド",
            ServerLanguage.Polish: "\"Szybki niczym wiatr\"",
            ServerLanguage.Russian: "\"Быстрый как ветер\"",
            ServerLanguage.BorkBorkBork: "\"Sveefft aes zee Veend\""},
        descriptions = {
        ServerLanguage.English: "Reduces Crippled duration on you by 20%"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    TheRiddleOfSteel = Upgrade(
        names = {
        ServerLanguage.German: "\"Hieb-und stahlfest\"",
            ServerLanguage.English: "\"The Riddle of Steel\"",
            ServerLanguage.Korean: "강철의 수수께끼",
            ServerLanguage.French: "\"L'énigme de l'acier\"",
            ServerLanguage.Italian: "\"Enigma d'Acciaio\"",
            ServerLanguage.Spanish: "\"El enigma de acero\"",
            ServerLanguage.TraditionalChinese: "\"鋼鐵之謎\"",
            ServerLanguage.Japanese: "ザ リドル オブ スチール",
            ServerLanguage.Polish: "\"Zagadka stali\"",
            ServerLanguage.Russian: "\"Стальной щит\"",
            ServerLanguage.BorkBorkBork: "\"Zee Reeddle-a ooff Steel\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Slashing damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ThroughThickAndThin = Upgrade(
        names = {
        ServerLanguage.German: "\"Durch Dick und Dünn\"",
            ServerLanguage.English: "\"Through Thick and Thin\"",
            ServerLanguage.Korean: "무엇이든 막아내리",
            ServerLanguage.French: "\"Contre vents et marées\"",
            ServerLanguage.Italian: "\"Nella Buona e nella Cattiva Sorte\"",
            ServerLanguage.Spanish: "\"En lo bueno y en lo malo\"",
            ServerLanguage.TraditionalChinese: "\"同甘共苦\"",
            ServerLanguage.Japanese: "スルー シック アンド シン",
            ServerLanguage.Polish: "\"Poprzez gąszcz\"",
            ServerLanguage.Russian: "\"Сквозь огонь и воду\"",
            ServerLanguage.BorkBorkBork: "\"Thruoogh Theeck und Theen\""},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} (vs. Piercing damage)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ToThePain = Upgrade(
        names = {
        ServerLanguage.German: "\"Fühlt den Schmerz!\"",
            ServerLanguage.English: "\"To the Pain!\"",
            ServerLanguage.Korean: "오직 공격뿐!",
            ServerLanguage.French: "\"Vive la douleur !\"",
            ServerLanguage.Italian: "\"Patisci!\"",
            ServerLanguage.Spanish: "\"¡A que duele!\"",
            ServerLanguage.TraditionalChinese: "\"受死吧！\"",
            ServerLanguage.Japanese: "トゥ ザ ペイン！",
            ServerLanguage.Polish: "\"Niech żyje ból!\"",
            ServerLanguage.Russian: "\"Боль!\"",
            ServerLanguage.BorkBorkBork: "\"Tu zee Paeeen!\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2[8760]}%\nArmor -{arg2[8216]} (while attacking)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    TooMuchInformation = Upgrade(
        names = {
        ServerLanguage.German: "\"Zuviel Information\"",
            ServerLanguage.English: "\"Too Much Information\"",
            ServerLanguage.Korean: "너무 많은 정보",
            ServerLanguage.French: "\"Trop de détails\"",
            ServerLanguage.Italian: "\"Troppe Informazioni\"",
            ServerLanguage.Spanish: "\"Demasiada información\"",
            ServerLanguage.TraditionalChinese: "\"多說無益\"",
            ServerLanguage.Japanese: "トゥー マッチ インフォメーション",
            ServerLanguage.Polish: "\"Za dużo informacji\"",
            ServerLanguage.Russian: "\"Слишком много информации\"",
            ServerLanguage.BorkBorkBork: "\"Tuu Mooch Inffurmaeshun\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2}% (vs. Hexed Foes)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    VengeanceIsMine = Upgrade(
        names = {
        ServerLanguage.German: "\"Die Rache ist mein\"",
            ServerLanguage.English: "\"Vengeance is Mine\"",
            ServerLanguage.Korean: "복수는 나의 것",
            ServerLanguage.French: "\"La vengeance sera mienne\"",
            ServerLanguage.Italian: "\"La Vendetta è Mia\"",
            ServerLanguage.Spanish: "\"La venganza será mía\"",
            ServerLanguage.TraditionalChinese: "\"我要報仇\"",
            ServerLanguage.Japanese: "ヴェンジャンス イズ マイン",
            ServerLanguage.Polish: "\"Zemsta należy do mnie\"",
            ServerLanguage.Russian: "\"Аз воздам\"",
            ServerLanguage.BorkBorkBork: "\"Fengeunce-a is Meene-a\""},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2}% (while Health is below +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    AirMagic = Upgrade(
        names = {
        ServerLanguage.English: "Air Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    BloodMagic = Upgrade(
        names = {
        ServerLanguage.English: "Blood Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ChannelingMagic = Upgrade(
        names = {
        ServerLanguage.English: "Channeling Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    Communing = Upgrade(
        names = {
        ServerLanguage.English: "Communing +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    Curses = Upgrade(
        names = {
        ServerLanguage.English: "Curses +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DeathMagic = Upgrade(
        names = {
        ServerLanguage.English: "Death Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DivineFavor = Upgrade(
        names = {
        ServerLanguage.English: "Divine Favor +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    DominationMagic = Upgrade(
        names = {
        ServerLanguage.English: "Domination Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    EarthMagic = Upgrade(
        names = {
        ServerLanguage.English: "Earth Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    FireMagic = Upgrade(
        names = {
        ServerLanguage.English: "Fire Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    HealingPrayers = Upgrade(
        names = {
        ServerLanguage.English: "Healing Prayers +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    IllusionMagic = Upgrade(
        names = {
        ServerLanguage.English: "Illusion Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    InspirationMagic = Upgrade(
        names = {
        ServerLanguage.English: "Inspiration Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ProtectionPrayers = Upgrade(
        names = {
        ServerLanguage.English: "Protection Prayers +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ReducesDiseaseOS = Upgrade(
        names = {
        ServerLanguage.English: "Reduces Disease duration on you by 20%"},
        descriptions = {
        ServerLanguage.English: "Reduces Disease duration on you by 20%\n[Old School] Shield, Staff or Offhand"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    RestorationMagic = Upgrade(
        names = {
        ServerLanguage.English: "Restoration Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SmitingPrayers = Upgrade(
        names = {
        ServerLanguage.English: "Smiting Prayers +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SoulReaping = Upgrade(
        names = {
        ServerLanguage.English: "Soul Reaping +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    SpawningPower = Upgrade(
        names = {
        ServerLanguage.English: "Spawning Power +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    VampiricStrength = Upgrade(
        names = {
        ServerLanguage.English: "Vampiric Strength"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2[8760]}%\nHealth regeneration -{arg2[8424]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    WaterMagic = Upgrade(
        names = {
        ServerLanguage.English: "Water Magic +1"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ZealousStrength = Upgrade(
        names = {
        ServerLanguage.English: "Zealous Strength"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg2[8760]}%\nEnergy regeneration -{arg2[8392]}"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsBluntdamage = Upgrade(
        names = {
        ServerLanguage.English: "vs. Blunt damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Blunt damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsCharr = Upgrade(
        names = {
        ServerLanguage.English: "vs. Charr"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Charr"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsCold = Upgrade(
        names = {
        ServerLanguage.English: "vs. Cold damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Cold damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsDemons = Upgrade(
        names = {
        ServerLanguage.English: "vs. Demons"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Demons"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsDragons = Upgrade(
        names = {
        ServerLanguage.English: "vs. Dragons"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Dragons"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsDwarves = Upgrade(
        names = {
        ServerLanguage.English: "vs. Dwarves"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Dwarves"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsEarth = Upgrade(
        names = {
        ServerLanguage.English: "vs. Earth damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Earth damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsFire = Upgrade(
        names = {
        ServerLanguage.English: "vs. Fire damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Fire damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsGiants = Upgrade(
        names = {
        ServerLanguage.English: "vs. Giants"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Giants"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsLightning = Upgrade(
        names = {
        ServerLanguage.English: "vs. Lightning damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Lightning damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsOgres = Upgrade(
        names = {
        ServerLanguage.English: "vs. Ogres"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Ogres"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsPiercing = Upgrade(
        names = {
        ServerLanguage.English: "vs. Piercing damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Piercing damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsPlants = Upgrade(
        names = {
        ServerLanguage.English: "vs. Plants"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Plants"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsSkeletons = Upgrade(
        names = {
        ServerLanguage.English: "vs. Skeletons"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Skeletons"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsSlashing = Upgrade(
        names = {
        ServerLanguage.English: "vs. Slashing damage"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Slashing damage"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsTengu = Upgrade(
        names = {
        ServerLanguage.English: "vs. Tengu"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Tengu"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsTrolls = Upgrade(
        names = {
        ServerLanguage.English: "vs. Trolls"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Trolls"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    ArmorVsUndead = Upgrade(
        names = {
        ServerLanguage.English: "vs. Undead"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2} vs. Undead"},
        upgrade_type = ItemUpgradeClassType.Inherent
    )

    Adept = Upgrade(
        names = {
        ServerLanguage.German: "Experten-",
            ServerLanguage.English: "Adept",
            ServerLanguage.Korean: "숙련된",
            ServerLanguage.French: "d'adepte",
            ServerLanguage.Italian: "da Adepto",
            ServerLanguage.Spanish: "de adepto",
            ServerLanguage.TraditionalChinese: "行家",
            ServerLanguage.Japanese: "アデプト",
            ServerLanguage.Polish: "Adepta",
            ServerLanguage.Russian: "Adept",
            ServerLanguage.BorkBorkBork: "Aedept"},
        descriptions = {
        ServerLanguage.English: "Halves casting time of spells of item's attribute (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Barbed = Upgrade(
        names = {
        ServerLanguage.German: "Stachel-",
            ServerLanguage.English: "Barbed",
            ServerLanguage.Korean: "가시 박힌",
            ServerLanguage.French: "à pointes",
            ServerLanguage.Italian: "a Punta",
            ServerLanguage.Spanish: "con espinas",
            ServerLanguage.TraditionalChinese: "荊棘",
            ServerLanguage.Japanese: "バーブ",
            ServerLanguage.Polish: "Kolców",
            ServerLanguage.Russian: "Barbed",
            ServerLanguage.BorkBorkBork: "Baerbed"},
        descriptions = {
        ServerLanguage.English: "Lengthens Bleeding duration on foes by 33%"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Crippling = Upgrade(
        names = {
        ServerLanguage.German: "Verkrüppelungs-",
            ServerLanguage.English: "Crippling",
            ServerLanguage.Korean: "치명적인",
            ServerLanguage.French: "d'infirmité",
            ServerLanguage.Italian: "Azzoppante",
            ServerLanguage.Spanish: "letal",
            ServerLanguage.TraditionalChinese: "致殘",
            ServerLanguage.Japanese: "クリップル",
            ServerLanguage.Polish: "Kaleczenia",
            ServerLanguage.Russian: "Crippling",
            ServerLanguage.BorkBorkBork: "Creeppleeng"},
        descriptions = {
        ServerLanguage.English: "Lengthens Crippled duration on foes by 33%"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Cruel = Upgrade(
        names = {
        ServerLanguage.German: "Grausamkeits-",
            ServerLanguage.English: "Cruel",
            ServerLanguage.Korean: "잔인한",
            ServerLanguage.French: "atroce",
            ServerLanguage.Italian: "Crudele",
            ServerLanguage.Spanish: "cruel",
            ServerLanguage.TraditionalChinese: "殘酷",
            ServerLanguage.Japanese: "クルーエル",
            ServerLanguage.Polish: "Okrucieństwa",
            ServerLanguage.Russian: "Cruel",
            ServerLanguage.BorkBorkBork: "Crooel"},
        descriptions = {
        ServerLanguage.English: "Lengthens Deep Wound duration on foes by 33%"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Defensive = Upgrade(
        names = {
        ServerLanguage.German: "Verteidigungs-",
            ServerLanguage.English: "Defensive",
            ServerLanguage.Korean: "방어적인",
            ServerLanguage.French: "défensif",
            ServerLanguage.Italian: "da Difesa",
            ServerLanguage.Spanish: "de defensa",
            ServerLanguage.TraditionalChinese: "防衛",
            ServerLanguage.Japanese: "ディフェンス",
            ServerLanguage.Polish: "Obrony",
            ServerLanguage.Russian: "Defensive",
            ServerLanguage.BorkBorkBork: "Deffenseefe-a"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Ebon = Upgrade(
        names = {
        ServerLanguage.German: "Ebon-",
            ServerLanguage.English: "Ebon",
            ServerLanguage.Korean: "흑단",
            ServerLanguage.French: "terrestre",
            ServerLanguage.Italian: "per danno d'ebano",
            ServerLanguage.Spanish: "con daño de granito",
            ServerLanguage.TraditionalChinese: "黑檀",
            ServerLanguage.Japanese: "エボン",
            ServerLanguage.Polish: "z Hebanu",
            ServerLanguage.Russian: "Ebon",
            ServerLanguage.BorkBorkBork: "Ibun"},
        descriptions = {
        ServerLanguage.English: "Changes Damage to {arg1}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Fiery = Upgrade(
        names = {
        ServerLanguage.German: "Hitze-",
            ServerLanguage.English: "Fiery",
            ServerLanguage.Korean: "화염의",
            ServerLanguage.French: "incendiaire",
            ServerLanguage.Italian: "per danno da fuoco",
            ServerLanguage.Spanish: "con daño ardiente",
            ServerLanguage.TraditionalChinese: "火焰",
            ServerLanguage.Japanese: "ファイア",
            ServerLanguage.Polish: "Ognia",
            ServerLanguage.Russian: "Fiery",
            ServerLanguage.BorkBorkBork: "Feeery"},
        descriptions = {
        ServerLanguage.English: "Changes Damage to {arg1}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Furious = Upgrade(
        names = {
        ServerLanguage.German: "Zorn-",
            ServerLanguage.English: "Furious",
            ServerLanguage.Korean: "격노한",
            ServerLanguage.French: "de fureur",
            ServerLanguage.Italian: "della Furia",
            ServerLanguage.Spanish: "de furor",
            ServerLanguage.TraditionalChinese: "狂怒",
            ServerLanguage.Japanese: "フューリアス",
            ServerLanguage.Polish: "Wściekłości",
            ServerLanguage.Russian: "Furious",
            ServerLanguage.BorkBorkBork: "Fooreeuoos"},
        descriptions = {
        ServerLanguage.English: "Double Adrenaline on hit (Chance: +{arg2}%)"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Hale = Upgrade(
        names = {
        ServerLanguage.German: "Rüstigkeits-",
            ServerLanguage.English: "Hale",
            ServerLanguage.Korean: "단단한",
            ServerLanguage.French: "de vigueur",
            ServerLanguage.Italian: "del Vigore",
            ServerLanguage.Spanish: "de robustez",
            ServerLanguage.TraditionalChinese: "健壯",
            ServerLanguage.Japanese: "ヘイル",
            ServerLanguage.Polish: "Wigoru",
            ServerLanguage.Russian: "Hale",
            ServerLanguage.BorkBorkBork: "Haele-a"},
        descriptions = {
        ServerLanguage.English: "+{arg1} Health"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Heavy = Upgrade(
        names = {
        ServerLanguage.German: "Schwergewichts-",
            ServerLanguage.English: "Heavy",
            ServerLanguage.Korean: "무거운",
            ServerLanguage.French: "de poids",
            ServerLanguage.Italian: "Pesante",
            ServerLanguage.Spanish: "fuerte",
            ServerLanguage.TraditionalChinese: "沉重",
            ServerLanguage.Japanese: "ヘヴィー",
            ServerLanguage.Polish: "Ciężaru",
            ServerLanguage.Russian: "Heavy",
            ServerLanguage.BorkBorkBork: "Heaefy"},
        descriptions = {
        ServerLanguage.English: "Lengthens Weakness duration on foes by 33%"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Icy = Upgrade(
        names = {
        ServerLanguage.German: "Eis-",
            ServerLanguage.English: "Icy",
            ServerLanguage.Korean: "냉기",
            ServerLanguage.French: "polaire",
            ServerLanguage.Italian: "per danno da ghiaccio",
            ServerLanguage.Spanish: "con daño frío",
            ServerLanguage.TraditionalChinese: "冰凍",
            ServerLanguage.Japanese: "アイス",
            ServerLanguage.Polish: "Lodu",
            ServerLanguage.Russian: "Icy",
            ServerLanguage.BorkBorkBork: "Icy"},
        descriptions = {
        ServerLanguage.English: "Changes Damage to {arg1}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Insightful = Upgrade(
        names = {
        ServerLanguage.German: "Einblick-",
            ServerLanguage.English: "Insightful",
            ServerLanguage.Korean: "통찰력의",
            ServerLanguage.French: "de vision",
            ServerLanguage.Italian: "dell'Astuzia",
            ServerLanguage.Spanish: "de visión",
            ServerLanguage.TraditionalChinese: "洞察",
            ServerLanguage.Japanese: "インサイト",
            ServerLanguage.Polish: "Przenikliwości",
            ServerLanguage.Russian: "Insightful",
            ServerLanguage.BorkBorkBork: "Inseeghtffool"},
        descriptions = {
        ServerLanguage.English: "Energy +{arg2}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Poisonous = Upgrade(
        names = {
        ServerLanguage.German: "Gift-",
            ServerLanguage.English: "Poisonous",
            ServerLanguage.Korean: "맹독의",
            ServerLanguage.French: "de poison",
            ServerLanguage.Italian: "del Veleno",
            ServerLanguage.Spanish: "con veneno",
            ServerLanguage.TraditionalChinese: "淬毒",
            ServerLanguage.Japanese: "ポイズン",
            ServerLanguage.Polish: "Zatrucia",
            ServerLanguage.Russian: "Poisonous",
            ServerLanguage.BorkBorkBork: "Pueesunuoos"},
        descriptions = {
        ServerLanguage.English: "Lengthens Poison duration on foes by 33%"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Shocking = Upgrade(
        names = {
        ServerLanguage.German: "Schock-",
            ServerLanguage.English: "Shocking",
            ServerLanguage.Korean: "충격의",
            ServerLanguage.French: "de foudre",
            ServerLanguage.Italian: "per danno da shock",
            ServerLanguage.Spanish: "con daño de descarga",
            ServerLanguage.TraditionalChinese: "電擊",
            ServerLanguage.Japanese: "ショック",
            ServerLanguage.Polish: "Porażenia",
            ServerLanguage.Russian: "Shocking",
            ServerLanguage.BorkBorkBork: "Shuckeeng"},
        descriptions = {
        ServerLanguage.English: "Changes Damage to {arg1}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Silencing = Upgrade(
        names = {
        ServerLanguage.German: "Dämpfungs-",
            ServerLanguage.English: "Silencing",
            ServerLanguage.Korean: "침묵의",
            ServerLanguage.French: "de silence",
            ServerLanguage.Italian: "del Silenzio",
            ServerLanguage.Spanish: "de silencio",
            ServerLanguage.TraditionalChinese: "沈默",
            ServerLanguage.Japanese: "サイレンス",
            ServerLanguage.Polish: "Uciszenia",
            ServerLanguage.Russian: "Silencing",
            ServerLanguage.BorkBorkBork: "Seelenceeng"},
        descriptions = {
        ServerLanguage.English: "Lengthens Dazed duration on foes by 33%"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Sundering = Upgrade(
        names = {
        ServerLanguage.German: "Trenn-",
            ServerLanguage.English: "Sundering",
            ServerLanguage.Korean: "날카로운",
            ServerLanguage.French: "de fractionnement",
            ServerLanguage.Italian: "della Separazione",
            ServerLanguage.Spanish: "de penetración",
            ServerLanguage.TraditionalChinese: "分離",
            ServerLanguage.Japanese: "サンダリング",
            ServerLanguage.Polish: "Rozdzierania",
            ServerLanguage.Russian: "Sundering",
            ServerLanguage.BorkBorkBork: "Soondereeng"},
        descriptions = {
        ServerLanguage.English: "Armor penetration +20% (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Swift = Upgrade(
        names = {
        ServerLanguage.German: "Schnelligkeits-",
            ServerLanguage.English: "Swift",
            ServerLanguage.Korean: "재빠른",
            ServerLanguage.French: "rapide",
            ServerLanguage.Italian: "della Rapidità",
            ServerLanguage.Spanish: "veloz",
            ServerLanguage.TraditionalChinese: "迅速",
            ServerLanguage.Japanese: "スウィフト",
            ServerLanguage.Polish: "Szybkości",
            ServerLanguage.Russian: "Swift",
            ServerLanguage.BorkBorkBork: "Sveefft"},
        descriptions = {
        ServerLanguage.English: "Halves casting time of spells (Chance: +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Vampiric = Upgrade(
        names = {
        ServerLanguage.German: "Vampir-",
            ServerLanguage.English: "Vampiric",
            ServerLanguage.Korean: "흡혈의 단검자루",
            ServerLanguage.French: "vampirique",
            ServerLanguage.Italian: "del Vampiro",
            ServerLanguage.Spanish: "de vampiro",
            ServerLanguage.TraditionalChinese: "吸血鬼 匕首刃",
            ServerLanguage.Japanese: "ヴァンピリック ダガーのグリップ",
            ServerLanguage.Polish: "Wampiryzmu",
            ServerLanguage.Russian: "Vampiric",
            ServerLanguage.BorkBorkBork: "Faempureec"},
        descriptions = {
        ServerLanguage.English: "Vampiric +{arg1[9512]}\nHealth regeneration -{arg2[8424]}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    Zealous = Upgrade(
        names = {
        ServerLanguage.German: "Eifer-",
            ServerLanguage.English: "Zealous",
            ServerLanguage.Korean: "광신도의",
            ServerLanguage.French: "de zèle",
            ServerLanguage.Italian: "Zelante",
            ServerLanguage.Spanish: "de afán",
            ServerLanguage.TraditionalChinese: "熱望",
            ServerLanguage.Japanese: "ゼラス",
            ServerLanguage.Polish: "Fanatyzmu",
            ServerLanguage.Russian: "Zealous",
            ServerLanguage.BorkBorkBork: "Zeaeluoos"},
        descriptions = {
        ServerLanguage.English: "Zeal +{arg2[9496]}\n    Energy regeneration -{arg2[8392]}"},
        upgrade_type = ItemUpgradeClassType.Prefix
    )

    OfAttribute = Upgrade(
        names = {
        ServerLanguage.German: "d. {arg1}",
            ServerLanguage.English: "of Attribute",
            ServerLanguage.Korean: "(속성)",
            ServerLanguage.French: "(d'attribut)",
            ServerLanguage.Italian: "dell'Attributo",
            ServerLanguage.Spanish: "(de atributo)",
            ServerLanguage.TraditionalChinese: "屬性",
            ServerLanguage.Japanese: "(アトリビュート)",
            ServerLanguage.Polish: "(Atrybutu)",
            ServerLanguage.Russian: "of Attribute",
            ServerLanguage.BorkBorkBork: "ooff Aetreeboot"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )
    
    OfAirMagic = Upgrade(
        names = {
        ServerLanguage.German: "d. Luftmagie",
            ServerLanguage.English: "of Air Magic",
            ServerLanguage.Korean: "(바람)",
            ServerLanguage.French: "(Magie de l'air)",
            ServerLanguage.Italian: "dell'Aria",
            ServerLanguage.Spanish: "(Magia de aire)",
            ServerLanguage.TraditionalChinese: "風系魔法",
            ServerLanguage.Japanese: "(エアー)",
            ServerLanguage.Polish: "(Magia Powietrza)",
            ServerLanguage.Russian: "of Air Magic",
            ServerLanguage.BorkBorkBork: "ooff Aeur Maegeec"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfAptitude = Upgrade(
        names = {
        ServerLanguage.German: "d. Begabung",
            ServerLanguage.English: "of Aptitude",
            ServerLanguage.Korean: "(총명)",
            ServerLanguage.French: "(d'aptitude)",
            ServerLanguage.Italian: "della Perspicacia",
            ServerLanguage.Spanish: "(de aptitud)",
            ServerLanguage.TraditionalChinese: "天賦",
            ServerLanguage.Japanese: "(アプティテュード)",
            ServerLanguage.Polish: "(Uzdolnienia)",
            ServerLanguage.Russian: "of Aptitude",
            ServerLanguage.BorkBorkBork: "ooff Aepteetoode-a"},
        descriptions = {
        ServerLanguage.English: "Halves casting time on spells of item's attribute (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfAxeMastery = Upgrade(
        names = {
        ServerLanguage.German: "d. Axtbeherrschung",
            ServerLanguage.English: "of Axe Mastery",
            ServerLanguage.Korean: "(도끼술)",
            ServerLanguage.French: "(Maîtrise de la hache)",
            ServerLanguage.Italian: "Abilità con l'Ascia",
            ServerLanguage.Spanish: "(Dominio del hacha)",
            ServerLanguage.TraditionalChinese: "精通斧術",
            ServerLanguage.Japanese: "(アックス マスタリー)",
            ServerLanguage.Polish: "(Biegłość w Toporach)",
            ServerLanguage.Russian: "of Axe Mastery",
            ServerLanguage.BorkBorkBork: "ooff Aexe-a Maestery"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfBloodMagic = Upgrade(
        names = {
        ServerLanguage.English: "of Blood Magic"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfChannelingMagic = Upgrade(
        names = {
        ServerLanguage.German: "d. Kanalisierungsmagie",
            ServerLanguage.English: "of Channeling Magic",
            ServerLanguage.Korean: "(마력 증폭)",
            ServerLanguage.French: "(Magie de la canalisation)",
            ServerLanguage.Italian: "del bastone Magia di Incanalamento",
            ServerLanguage.Spanish: "(Magia de canalización)",
            ServerLanguage.TraditionalChinese: "導引魔法",
            ServerLanguage.Japanese: "(チャネリング)",
            ServerLanguage.Polish: "(Magia Połączeń)",
            ServerLanguage.Russian: "of Channeling Magic",
            ServerLanguage.BorkBorkBork: "ooff Chunneleeng Maegeec"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfCharrslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Charrslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfCommuning = Upgrade(
        names = {
        ServerLanguage.English: "of Communing"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfCurses = Upgrade(
        names = {
        ServerLanguage.English: "of Curses"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDaggerMastery = Upgrade(
        names = {
        ServerLanguage.German: "d. Dolchbeherrschung",
            ServerLanguage.English: "of Dagger Mastery",
            ServerLanguage.Korean: "(단검술)",
            ServerLanguage.French: "(Maîtrise de la dague)",
            ServerLanguage.Italian: "Abilità con il Pugnale",
            ServerLanguage.Spanish: "(Dominio de la daga)",
            ServerLanguage.TraditionalChinese: "匕首精通",
            ServerLanguage.Japanese: "(ダガー マスタリー)",
            ServerLanguage.Polish: "(Biegłość w Sztyletach)",
            ServerLanguage.Russian: "of Dagger Mastery",
            ServerLanguage.BorkBorkBork: "ooff Daegger Maestery"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDeathMagic = Upgrade(
        names = {
        ServerLanguage.English: "of Death Magic"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDeathbane = Upgrade(
        names = {
        ServerLanguage.German: "d. Todesfluches",
            ServerLanguage.English: "of Deathbane",
            ServerLanguage.Korean: "(언데드 상대 무기)",
            ServerLanguage.French: "(anti-mort)",
            ServerLanguage.Italian: "del Flagello Mortale",
            ServerLanguage.Spanish: "(matamuertos)",
            ServerLanguage.TraditionalChinese: "不死族剋星",
            ServerLanguage.Japanese: "(デスベイン)",
            ServerLanguage.Polish: "(Zabijania Nieumarłych)",
            ServerLanguage.Russian: "of Deathbane",
            ServerLanguage.BorkBorkBork: "ooff Deaethbune-a"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDefense = Upgrade(
        names = {
        ServerLanguage.German: "d. Verteidigung",
            ServerLanguage.English: "of Defense",
            ServerLanguage.Korean: "(방어)",
            ServerLanguage.French: "(de Défense)",
            ServerLanguage.Italian: "di Difesa",
            ServerLanguage.Spanish: "(de protección)",
            ServerLanguage.TraditionalChinese: "防衛",
            ServerLanguage.Japanese: "(ディフェンス)",
            ServerLanguage.Polish: "(Obrony)",
            ServerLanguage.Russian: "of Defense",
            ServerLanguage.BorkBorkBork: "ooff Deffense-a"},
        descriptions = {
        ServerLanguage.English: "Armor +{arg2}"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDemonslaying = Upgrade(
        names = {
        ServerLanguage.German: "d. Dämonentötung",
            ServerLanguage.English: "of Demonslaying",
            ServerLanguage.Korean: "(데몬 상대 무기)",
            ServerLanguage.French: "(anti-démons)",
            ServerLanguage.Italian: "dell'arco Ammazza-demoni",
            ServerLanguage.Spanish: "(matademonios)",
            ServerLanguage.TraditionalChinese: "惡魔殺手",
            ServerLanguage.Japanese: "(デーモン キラー)",
            ServerLanguage.Polish: "(Zabijania Demonów)",
            ServerLanguage.Russian: "of Demonslaying",
            ServerLanguage.BorkBorkBork: "ooff Demunslaeyeeng"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDevotion = Upgrade(
        names = {
        ServerLanguage.German: "d. Hingabe",
            ServerLanguage.English: "of Devotion",
            ServerLanguage.Korean: "(헌신)",
            ServerLanguage.French: "(de dévotion)",
            ServerLanguage.Italian: "della Devozione",
            ServerLanguage.Spanish: "(de devoción)",
            ServerLanguage.TraditionalChinese: "奉獻",
            ServerLanguage.Japanese: "(ディボーション)",
            ServerLanguage.Polish: "(Oddania)",
            ServerLanguage.Russian: "of Devotion",
            ServerLanguage.BorkBorkBork: "ooff Defushun"},
        descriptions = {
        ServerLanguage.English: "+{arg1} Health while Enchanted"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDivineFavor = Upgrade(
        names = {
        ServerLanguage.English: "of Divine Favor"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDominationMagic = Upgrade(
        names = {
        ServerLanguage.English: "of Domination Magic"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDragonslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Dragonslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfDwarfslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Dwarfslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfEarthMagic = Upgrade(
        names = {
        ServerLanguage.English: "of Earth Magic"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfEnchanting = Upgrade(
        names = {
        ServerLanguage.German: "d. Verzauberung",
            ServerLanguage.English: "of Enchanting",
            ServerLanguage.Korean: "(강화)",
            ServerLanguage.French: "(d'Enchantement)",
            ServerLanguage.Italian: "dell'Incantesimo",
            ServerLanguage.Spanish: "(de encantamientos)",
            ServerLanguage.TraditionalChinese: "附魔",
            ServerLanguage.Japanese: "(エンチャント)",
            ServerLanguage.Polish: "(Zaklinania)",
            ServerLanguage.Russian: "of Enchanting",
            ServerLanguage.BorkBorkBork: "ooff Inchunteeng"},
        descriptions = {
        ServerLanguage.English: "+{arg2}% Enchantment Duration"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfEndurance = Upgrade(
        names = {
        ServerLanguage.German: "d. Ausdauer",
            ServerLanguage.English: "of Endurance",
            ServerLanguage.Korean: "(인내)",
            ServerLanguage.French: "(d'endurance)",
            ServerLanguage.Italian: "della Resistenza",
            ServerLanguage.Spanish: "(de resistencia)",
            ServerLanguage.TraditionalChinese: "忍耐",
            ServerLanguage.Japanese: "(インデュランス)",
            ServerLanguage.Polish: "(Wytrzymałości)",
            ServerLanguage.Russian: "of Endurance",
            ServerLanguage.BorkBorkBork: "ooff Indoorunce-a"},
        descriptions = {
        ServerLanguage.English: "+{arg1} Health while in a Stance"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfFireMagic = Upgrade(
        names = {
        ServerLanguage.German: "d. Feuermagie",
            ServerLanguage.English: "of Fire Magic",
            ServerLanguage.Korean: "(불)",
            ServerLanguage.French: "(Magie du feu)",
            ServerLanguage.Italian: "del Fuoco",
            ServerLanguage.Spanish: "(Magia de fuego)",
            ServerLanguage.TraditionalChinese: "火系魔法",
            ServerLanguage.Japanese: "(ファイア)",
            ServerLanguage.Polish: "(Magia Ognia)",
            ServerLanguage.Russian: "of Fire Magic",
            ServerLanguage.BorkBorkBork: "ooff Fure-a Maegeec"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfFortitude = Upgrade(
        names = {
        ServerLanguage.German: "d. Tapferkeit",
            ServerLanguage.English: "of Fortitude",
            ServerLanguage.Korean: "(견고)",
            ServerLanguage.French: "(de Courage)",
            ServerLanguage.Italian: "del Coraggio",
            ServerLanguage.Spanish: "(con poder)",
            ServerLanguage.TraditionalChinese: "堅忍",
            ServerLanguage.Japanese: "(フォーティチュード)",
            ServerLanguage.Polish: "(Wytrwałości)",
            ServerLanguage.Russian: "of Fortitude",
            ServerLanguage.BorkBorkBork: "ooff Furteetoode-a"},
        descriptions = {
        ServerLanguage.English: "+{arg1} Health"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfGiantslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Giantslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfHammerMastery = Upgrade(
        names = {
        ServerLanguage.German: "d. Hammerbeherrschung",
            ServerLanguage.English: "of Hammer Mastery",
            ServerLanguage.Korean: "(해머술)",
            ServerLanguage.French: "(Maîtrise du marteau)",
            ServerLanguage.Italian: "Abilità col Martello",
            ServerLanguage.Spanish: "(Dominio del martillo)",
            ServerLanguage.TraditionalChinese: "精通鎚術",
            ServerLanguage.Japanese: "(ハンマー マスタリー)",
            ServerLanguage.Polish: "(Biegłość w Młotach)",
            ServerLanguage.Russian: "of Hammer Mastery",
            ServerLanguage.BorkBorkBork: "ooff Haemmer Maestery"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfHealingPrayers = Upgrade(
        names = {
        ServerLanguage.English: "of Healing Prayers"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfIllusionMagic = Upgrade(
        names = {
        ServerLanguage.English: "of Illusion Magic"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfInspirationMagic = Upgrade(
        names = {
        ServerLanguage.German: "d. Inspirationsmagie",
            ServerLanguage.English: "of Inspiration Magic",
            ServerLanguage.Korean: "(영감)",
            ServerLanguage.French: "(Magie de l'inspiration)",
            ServerLanguage.Italian: "del bastone Magia di Ispirazione",
            ServerLanguage.Spanish: "(Magia de inspiración)",
            ServerLanguage.TraditionalChinese: "靈感魔法",
            ServerLanguage.Japanese: "(インスピレーション)",
            ServerLanguage.Polish: "(Magia Inspiracji)",
            ServerLanguage.Russian: "of Inspiration Magic",
            ServerLanguage.BorkBorkBork: "ooff Inspuraeshun Maegeec"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfMarksmanship = Upgrade(
        names = {
        ServerLanguage.German: "d. Treffsicherheit",
            ServerLanguage.English: "of Marksmanship",
            ServerLanguage.Korean: "(궁술)",
            ServerLanguage.French: "(Adresse au tir)",
            ServerLanguage.Italian: "Precisione",
            ServerLanguage.Spanish: "(Puntería)",
            ServerLanguage.TraditionalChinese: "弓術精通",
            ServerLanguage.Japanese: "(ボウ マスタリー)",
            ServerLanguage.Polish: "(Umiejętności Strzeleckie)",
            ServerLanguage.Russian: "of Marksmanship",
            ServerLanguage.BorkBorkBork: "ooff Maerksmunsheep"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfMastery = Upgrade(
        names = {
        ServerLanguage.German: "d. Beherrschung",
            ServerLanguage.English: "of Mastery",
            ServerLanguage.Korean: "(지배)",
            ServerLanguage.French: "(de maîtrise)",
            ServerLanguage.Italian: "della Destrezza da Difesa",
            ServerLanguage.Spanish: "(de maestría)",
            ServerLanguage.TraditionalChinese: "支配",
            ServerLanguage.Japanese: "(マスタリー)",
            ServerLanguage.Polish: "(Mistrzostwa)",
            ServerLanguage.Russian: "of Mastery",
            ServerLanguage.BorkBorkBork: "ooff Maestery"},
        descriptions = {
        ServerLanguage.English: "Item's attribute +1 (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfMemory = Upgrade(
        names = {
        ServerLanguage.German: "d. Erinnerung",
            ServerLanguage.English: "of Memory",
            ServerLanguage.Korean: "(기억)",
            ServerLanguage.French: "(de mémoire)",
            ServerLanguage.Italian: "della Memoria",
            ServerLanguage.Spanish: "(de memoria)",
            ServerLanguage.TraditionalChinese: "記憶",
            ServerLanguage.Japanese: "(メモリー)",
            ServerLanguage.Polish: "(Pamięci)",
            ServerLanguage.Russian: "of Memory",
            ServerLanguage.BorkBorkBork: "ooff Memury"},
        descriptions = {
        ServerLanguage.English: "Halves skill recharge of item's attribute spells (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfOgreslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Ogreslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfProtectionPrayers = Upgrade(
        names = {
        ServerLanguage.English: "of Protection Prayers"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfPruning = Upgrade(
        names = {
        ServerLanguage.German: "d. Pflanzentötung",
            ServerLanguage.English: "of Pruning",
            ServerLanguage.Korean: "(식물 상대 무기)",
            ServerLanguage.French: "(anti-plantes)",
            ServerLanguage.Italian: "del martello da Sfoltimento",
            ServerLanguage.Spanish: "(mataplantas)",
            ServerLanguage.TraditionalChinese: "枝葉修整",
            ServerLanguage.Japanese: "(プルーニング)",
            ServerLanguage.Polish: "(Obcinania)",
            ServerLanguage.Russian: "of Pruning",
            ServerLanguage.BorkBorkBork: "ooff Prooneeng"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfQuickening = Upgrade(
        names = {
        ServerLanguage.German: "d. Beschleunigung",
            ServerLanguage.English: "of Quickening",
            ServerLanguage.Korean: "(활기)",
            ServerLanguage.French: "(de rapidité)",
            ServerLanguage.Italian: "dell'Accelerazione",
            ServerLanguage.Spanish: "(de aceleración)",
            ServerLanguage.TraditionalChinese: "復甦",
            ServerLanguage.Japanese: "(クイックニング)",
            ServerLanguage.Polish: "(Przyspieszenia)",
            ServerLanguage.Russian: "of Quickening",
            ServerLanguage.BorkBorkBork: "ooff Qooeeckeneeng"},
        descriptions = {
        ServerLanguage.English: "Halves skill recharge of spells (Chance: {arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfRestorationMagic = Upgrade(
        names = {
        ServerLanguage.German: "d. Wiederherstellungsmagie",
            ServerLanguage.English: "of Restoration Magic",
            ServerLanguage.Korean: "(마력 회복)",
            ServerLanguage.French: "(Magie de restauration)",
            ServerLanguage.Italian: "del Ripristino",
            ServerLanguage.Spanish: "(Magia de restauración)",
            ServerLanguage.TraditionalChinese: "復原魔法",
            ServerLanguage.Japanese: "(レストレーション)",
            ServerLanguage.Polish: "(Magia Odnowy)",
            ServerLanguage.Russian: "of Restoration Magic",
            ServerLanguage.BorkBorkBork: "ooff Resturaeshun Maegeec"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfScytheMastery = Upgrade(
        names = {
        ServerLanguage.German: "d. Sensenbeherrschung",
            ServerLanguage.English: "of Scythe Mastery",
            ServerLanguage.Korean: "(사이드술)",
            ServerLanguage.French: "(Maîtrise de la faux)",
            ServerLanguage.Italian: "Abilità con la Falce",
            ServerLanguage.Spanish: "(Dominio de la guadaña)",
            ServerLanguage.TraditionalChinese: "鐮刀精通",
            ServerLanguage.Japanese: "(サイズ マスタリー)",
            ServerLanguage.Polish: "(Biegłość w Kosach)",
            ServerLanguage.Russian: "of Scythe Mastery",
            ServerLanguage.BorkBorkBork: "ooff Scyzee Maestery"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfShelter = Upgrade(
        names = {
        ServerLanguage.German: "d. Zuflucht",
            ServerLanguage.English: "of Shelter",
            ServerLanguage.Korean: "(보호)",
            ServerLanguage.French: "(de Refuge)",
            ServerLanguage.Italian: "del Riparo",
            ServerLanguage.Spanish: "(de refugio)",
            ServerLanguage.TraditionalChinese: "庇護",
            ServerLanguage.Japanese: "(シェルター)",
            ServerLanguage.Polish: "(Ochrony)",
            ServerLanguage.Russian: "of Shelter",
            ServerLanguage.BorkBorkBork: "ooff Shelter"},
        descriptions = {
        ServerLanguage.English: "+{arg2} Armor vs Physical"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSkeletonslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Skeletonslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSmitingPrayers = Upgrade(
        names = {
        ServerLanguage.German: "d. Peinigungsgebete",
            ServerLanguage.English: "of Smiting Prayers",
            ServerLanguage.Korean: "(천벌)",
            ServerLanguage.French: "(Prières de châtiment)",
            ServerLanguage.Italian: "del bastone Preghiere Punitive",
            ServerLanguage.Spanish: "(Plegarias de ataque)",
            ServerLanguage.TraditionalChinese: "懲戒祈禱",
            ServerLanguage.Japanese: "(ホーリー)",
            ServerLanguage.Polish: "(Modlitwy Ofensywne)",
            ServerLanguage.Russian: "of Smiting Prayers",
            ServerLanguage.BorkBorkBork: "ooff Smeeteeng Praeyers"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSoulReaping = Upgrade(
        names = {
        ServerLanguage.English: "of Soul Reaping"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSpawningPower = Upgrade(
        names = {
        ServerLanguage.German: "d. Macht des Herbeirufens",
            ServerLanguage.English: "of Spawning Power",
            ServerLanguage.Korean: "(생성)",
            ServerLanguage.French: "(Puissance de l'Invocation)",
            ServerLanguage.Italian: "del bastone Riti Sacrificali",
            ServerLanguage.Spanish: "(Engendramiento)",
            ServerLanguage.TraditionalChinese: "召喚",
            ServerLanguage.Japanese: "(スポーン パワー)",
            ServerLanguage.Polish: "(Moc Przywoływania)",
            ServerLanguage.Russian: "of Spawning Power",
            ServerLanguage.BorkBorkBork: "ooff Spaevneeng Pooer"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSpearMastery = Upgrade(
        names = {
        ServerLanguage.German: "d. Speerbeherrschung",
            ServerLanguage.English: "of Spear Mastery",
            ServerLanguage.Korean: "(창술)",
            ServerLanguage.French: "(Maîtrise du javelot)",
            ServerLanguage.Italian: "Abilità con la Lancia",
            ServerLanguage.Spanish: "(Dominio de la lanza)",
            ServerLanguage.TraditionalChinese: "矛術精通",
            ServerLanguage.Japanese: "(スピア マスタリー)",
            ServerLanguage.Polish: "(Biegłość we Włóczniach)",
            ServerLanguage.Russian: "of Spear Mastery",
            ServerLanguage.BorkBorkBork: "ooff Speaer Maestery"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSwiftness = Upgrade(
        names = {
        ServerLanguage.German: "d. Eile",
            ServerLanguage.English: "of Swiftness",
            ServerLanguage.Korean: "(신속)",
            ServerLanguage.French: "(de Rapidité)",
            ServerLanguage.Italian: "della Rapidità",
            ServerLanguage.Spanish: "(de rapidez)",
            ServerLanguage.TraditionalChinese: "迅捷",
            ServerLanguage.Japanese: "(スウィフトネス)",
            ServerLanguage.Polish: "(Szybkości)",
            ServerLanguage.Russian: "of Swiftness",
            ServerLanguage.BorkBorkBork: "ooff Sveefftness"},
        descriptions = {
        ServerLanguage.English: "Halves casting time of spells (Chance: +{arg1}%)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSwordsmanship = Upgrade(
        names = {
        ServerLanguage.German: "d. Schwertkunst",
            ServerLanguage.English: "of Swordsmanship",
            ServerLanguage.Korean: "(검술)",
            ServerLanguage.French: "(Maîtrise de l'épée)",
            ServerLanguage.Italian: "Scherma",
            ServerLanguage.Spanish: "(Esgrima)",
            ServerLanguage.TraditionalChinese: "精通劍術",
            ServerLanguage.Japanese: "(ソード マスタリー)",
            ServerLanguage.Polish: "(Biegłość w Mieczach)",
            ServerLanguage.Russian: "of Swordsmanship",
            ServerLanguage.BorkBorkBork: "ooff Svurdsmunsheep"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTenguslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Tenguslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTrollslaying = Upgrade(
        names = {
        ServerLanguage.English: "of Trollslaying"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfValor = Upgrade(
        names = {
        ServerLanguage.German: "d. Wertschätzung",
            ServerLanguage.English: "of Valor",
            ServerLanguage.Korean: "(용맹)",
            ServerLanguage.French: "(de valeur)",
            ServerLanguage.Italian: "del Valore",
            ServerLanguage.Spanish: "(de valor)",
            ServerLanguage.TraditionalChinese: "英勇",
            ServerLanguage.Japanese: "(ヴァラー)",
            ServerLanguage.Polish: "(Odwagi)",
            ServerLanguage.Russian: "of Valor",
            ServerLanguage.BorkBorkBork: "ooff Faelur"},
        descriptions = {
        ServerLanguage.English: "+{arg1} Health while Hexed"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfWarding = Upgrade(
        names = {
        ServerLanguage.German: "d. Abwehr",
            ServerLanguage.English: "of Warding",
            ServerLanguage.Korean: "(결계)",
            ServerLanguage.French: "(du Protecteur)",
            ServerLanguage.Italian: "della Protezione",
            ServerLanguage.Spanish: "(de guardia)",
            ServerLanguage.TraditionalChinese: "結界",
            ServerLanguage.Japanese: "(ウォーディング)",
            ServerLanguage.Polish: "(Zapobiegliwości)",
            ServerLanguage.Russian: "of Warding",
            ServerLanguage.BorkBorkBork: "ooff Vaerdeeng"},
        descriptions = {
        ServerLanguage.English: "+{arg2} Armor vs Elemental"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfWaterMagic = Upgrade(
        names = {
        ServerLanguage.English: "of Water Magic"},
        descriptions = {
        ServerLanguage.English: "{arg1} +1 ({arg2}% chance while using skills)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheAssassin = Upgrade(
        names = {
        ServerLanguage.German: "d. des Assassinen",
            ServerLanguage.English: "of the Assassin",
            ServerLanguage.Korean: "(어새신)",
            ServerLanguage.French: "(l'Assassin)",
            ServerLanguage.Italian: "dell'arco l'assassino",
            ServerLanguage.Spanish: "(el asesino)",
            ServerLanguage.TraditionalChinese: "the",
            ServerLanguage.Japanese: "(アサシン)",
            ServerLanguage.Polish: "(Zabójcy)",
            ServerLanguage.Russian: "of ассасин",
            ServerLanguage.BorkBorkBork: "ooff zee Aessaesseen"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheDervish = Upgrade(
        names = {
        ServerLanguage.German: "d. des Derwischs",
            ServerLanguage.English: "of the Dervish",
            ServerLanguage.Korean: "(더비시)",
            ServerLanguage.French: "(le Derviche)",
            ServerLanguage.Italian: "dell'arco il derviscio",
            ServerLanguage.Spanish: "(el derviche)",
            ServerLanguage.TraditionalChinese: "the",
            ServerLanguage.Japanese: "(ダルウィーシュ)",
            ServerLanguage.Polish: "(Derwisza)",
            ServerLanguage.Russian: "of дервиш",
            ServerLanguage.BorkBorkBork: "ooff zee Derfeesh"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheElementalist = Upgrade(
        names = {
        ServerLanguage.English: "of the Elementalist"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheMesmer = Upgrade(
        names = {
        ServerLanguage.German: "d. des Mesmers",
            ServerLanguage.English: "of the Mesmer",
            ServerLanguage.Korean: "(メスマー)",
            ServerLanguage.French: "(l'Envoûteur)",
            ServerLanguage.Italian: "il mesmerista",
            ServerLanguage.Spanish: "(el hipnotizador)",
            ServerLanguage.TraditionalChinese: "the Mesmer",
            ServerLanguage.Japanese: "(メスマー)",
            ServerLanguage.Polish: "(Mesmera)",
            ServerLanguage.Russian: "of месмер",
            ServerLanguage.BorkBorkBork: "ooff zee Mesmer"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheMonk = Upgrade(
        names = {
        ServerLanguage.German: "d. des Mönchs",
            ServerLanguage.English: "of the Monk",
            ServerLanguage.Korean: "(몽크)",
            ServerLanguage.French: "(le Moine)",
            ServerLanguage.Italian: "della Falce il monaco",
            ServerLanguage.Spanish: "(el monje)",
            ServerLanguage.TraditionalChinese: "the Monk",
            ServerLanguage.Japanese: "(モンク)",
            ServerLanguage.Polish: "(Mnicha)",
            ServerLanguage.Russian: "of монах",
            ServerLanguage.BorkBorkBork: "ooff zee Munk"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheNecromancer = Upgrade(
        names = {
        ServerLanguage.German: "d. des Nekromanten",
            ServerLanguage.English: "of the Necromancer",
            ServerLanguage.Korean: "(ネクロマンサー)",
            ServerLanguage.French: "(le Nécromant)",
            ServerLanguage.Italian: "il negromante",
            ServerLanguage.Spanish: "(el nigromante)",
            ServerLanguage.TraditionalChinese: "the Necromancer",
            ServerLanguage.Japanese: "(ネクロマンサー)",
            ServerLanguage.Polish: "(Nekromanty)",
            ServerLanguage.Russian: "of некромант",
            ServerLanguage.BorkBorkBork: "ooff zee Necrumuncer"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheParagon = Upgrade(
        names = {
        ServerLanguage.German: "d. des Paragons",
            ServerLanguage.English: "of the Paragon",
            ServerLanguage.Korean: "(파라곤)",
            ServerLanguage.French: "(le Parangon)",
            ServerLanguage.Italian: "del bastone il campione",
            ServerLanguage.Spanish: "(el paragón)",
            ServerLanguage.TraditionalChinese: "the Paragon",
            ServerLanguage.Japanese: "(パラゴン)",
            ServerLanguage.Polish: "(Patrona)",
            ServerLanguage.Russian: "of парагон",
            ServerLanguage.BorkBorkBork: "ooff zee Paeraegun"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheRanger = Upgrade(
        names = {
        ServerLanguage.German: "d. des Waldläufers",
            ServerLanguage.English: "of the Ranger",
            ServerLanguage.Korean: "(레인저)",
            ServerLanguage.French: "(le Rôdeur)",
            ServerLanguage.Italian: "della Bacchetta il ranger",
            ServerLanguage.Spanish: "(el guardabosques)",
            ServerLanguage.TraditionalChinese: "the",
            ServerLanguage.Japanese: "(レンジャー)",
            ServerLanguage.Polish: "(Łowcy)",
            ServerLanguage.Russian: "of рейнджер",
            ServerLanguage.BorkBorkBork: "ooff zee Runger"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheRitualist = Upgrade(
        names = {
        ServerLanguage.German: "d. des Ritualisten",
            ServerLanguage.English: "of the Ritualist",
            ServerLanguage.Korean: "(リチュアリスト)",
            ServerLanguage.French: "(le Ritualiste)",
            ServerLanguage.Italian: "il ritualista",
            ServerLanguage.Spanish: "(el ritualista)",
            ServerLanguage.TraditionalChinese: "the Ritualist",
            ServerLanguage.Japanese: "(リチュアリスト)",
            ServerLanguage.Polish: "(Rytualisty)",
            ServerLanguage.Russian: "of ритуалист",
            ServerLanguage.BorkBorkBork: "ooff zee Reetooaeleest"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfTheWarrior = Upgrade(
        names = {
        ServerLanguage.German: "d. des Kriegers",
            ServerLanguage.English: "of the Warrior",
            ServerLanguage.Korean: "(ウォーリア)",
            ServerLanguage.French: "(le Guerrier)",
            ServerLanguage.Italian: "il guerriero",
            ServerLanguage.Spanish: "(el guerrero)",
            ServerLanguage.TraditionalChinese: "the Warrior",
            ServerLanguage.Japanese: "(ウォーリア)",
            ServerLanguage.Polish: "(Wojownika)",
            ServerLanguage.Russian: "of воин",
            ServerLanguage.BorkBorkBork: "ooff zee Vaerreeur"},
        descriptions = {
        ServerLanguage.English: "{arg1}: {arg2} (if your rank is lower. No effects in PvP.)"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )

    OfSlaying = Upgrade(
        names = {
        ServerLanguage.German: "d. Tötung",
            ServerLanguage.English: "of Slaying",
            ServerLanguage.Korean: "(상대 무기)",
            ServerLanguage.French: "(anti-)",
            ServerLanguage.Italian: "del martello da Uccisione",
            ServerLanguage.Spanish: "(matador)",
            ServerLanguage.TraditionalChinese: "殺戮",
            ServerLanguage.Japanese: "(スレイング)",
            ServerLanguage.Polish: "(Zabijania)",
            ServerLanguage.Russian: "of Slaying",
            ServerLanguage.BorkBorkBork: "ooff Slaeyeeng"},
        descriptions = {
        ServerLanguage.English: "Damage +{arg1[41544]}% (vs. {arg1[32896]})"},
        upgrade_type = ItemUpgradeClassType.Suffix
    )