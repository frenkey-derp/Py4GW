from dataclasses import dataclass
from enum import Enum, IntEnum

class ItemUpgradeClassType(IntEnum):
    Unknown = 0
    Prefix = 1
    Suffix = 2
    Inherent = 3
    UpgradeRune = 4
    AppliesToRune = 5

@dataclass
class ItemUpgradeClass:
    upgrade_id : int
    name : str
    upgrade_type : ItemUpgradeClassType

class ItemUpgrade(Enum):
    Unknown = ItemUpgradeClass(upgrade_id = -1,  name = "Unknown", upgrade_type = ItemUpgradeClassType.Unknown)
    Icy_Axe = ItemUpgradeClass(upgrade_id = 0x0081,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Axe = ItemUpgradeClass(upgrade_id = 0x0082,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Axe = ItemUpgradeClass(upgrade_id = 0x0083,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    Fiery_Axe = ItemUpgradeClass(upgrade_id = 0x0084,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Barbed_Axe = ItemUpgradeClass(upgrade_id = 0x0092,  name = "Barbed", upgrade_type = ItemUpgradeClassType.Prefix)
    Crippling_Axe = ItemUpgradeClass(upgrade_id = 0x0094,  name = "Crippling", upgrade_type = ItemUpgradeClassType.Prefix)
    Cruel_Axe = ItemUpgradeClass(upgrade_id = 0x0096,  name = "Cruel", upgrade_type = ItemUpgradeClassType.Prefix)
    Furious_Axe = ItemUpgradeClass(upgrade_id = 0x0099,  name = "Furious", upgrade_type = ItemUpgradeClassType.Prefix)
    Poisonous_Axe = ItemUpgradeClass(upgrade_id = 0x009E,  name = "Poisonous", upgrade_type = ItemUpgradeClassType.Prefix)
    Heavy_Axe = ItemUpgradeClass(upgrade_id = 0x00A1,  name = "Heavy", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Axe = ItemUpgradeClass(upgrade_id = 0x00A3,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Axe = ItemUpgradeClass(upgrade_id = 0x00A7,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Axe = ItemUpgradeClass(upgrade_id = 0x00AB,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    OfDefense_Axe = ItemUpgradeClass(upgrade_id = 0x00C5,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfWarding_Axe = ItemUpgradeClass(upgrade_id = 0x00C7,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Axe = ItemUpgradeClass(upgrade_id = 0x00CD,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSlaying_Axe = ItemUpgradeClass(upgrade_id = 0x00D4,  name = "of ____slaying", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Axe = ItemUpgradeClass(upgrade_id = 0x00D9,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Axe = ItemUpgradeClass(upgrade_id = 0x00DE,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfAxeMastery = ItemUpgradeClass(upgrade_id = 0x00E8,  name = "of Axe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfTheProfession_Axe = ItemUpgradeClass(upgrade_id = 0x0226,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    Icy_Bow = ItemUpgradeClass(upgrade_id = 0x0085,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Bow = ItemUpgradeClass(upgrade_id = 0x0086,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Bow = ItemUpgradeClass(upgrade_id = 0x0087,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    Fiery_Bow = ItemUpgradeClass(upgrade_id = 0x0088,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Poisonous_Bow = ItemUpgradeClass(upgrade_id = 0x009F,  name = "Poisonous", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Bow = ItemUpgradeClass(upgrade_id = 0x00A5,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Bow = ItemUpgradeClass(upgrade_id = 0x00A9,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Bow = ItemUpgradeClass(upgrade_id = 0x00AD,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    OfDefense_Bow = ItemUpgradeClass(upgrade_id = 0x00C6,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfWarding_Bow = ItemUpgradeClass(upgrade_id = 0x00C8,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Bow = ItemUpgradeClass(upgrade_id = 0x00CE,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSlaying_Bow = ItemUpgradeClass(upgrade_id = 0x00D5,  name = "of _____slaying", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Bow = ItemUpgradeClass(upgrade_id = 0x00DA,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Bow = ItemUpgradeClass(upgrade_id = 0x00DF,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMarksmanship = ItemUpgradeClass(upgrade_id = 0x00E9,  name = "of Marksmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    Barbed_Bow = ItemUpgradeClass(upgrade_id = 0x0147,  name = "Barbed", upgrade_type = ItemUpgradeClassType.Prefix)
    Crippling_Bow = ItemUpgradeClass(upgrade_id = 0x0148,  name = "Crippling", upgrade_type = ItemUpgradeClassType.Prefix)
    Silencing_Bow = ItemUpgradeClass(upgrade_id = 0x0149,  name = "Silencing", upgrade_type = ItemUpgradeClassType.Prefix)
    OfTheProfession_Bow = ItemUpgradeClass(upgrade_id = 0x0227,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    Icy_Daggers = ItemUpgradeClass(upgrade_id = 0x012E,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Daggers = ItemUpgradeClass(upgrade_id = 0x012F,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    Fiery_Daggers = ItemUpgradeClass(upgrade_id = 0x0130,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Daggers = ItemUpgradeClass(upgrade_id = 0x0131,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Daggers = ItemUpgradeClass(upgrade_id = 0x0132,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Daggers = ItemUpgradeClass(upgrade_id = 0x0133,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Daggers = ItemUpgradeClass(upgrade_id = 0x0134,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    Barbed_Daggers = ItemUpgradeClass(upgrade_id = 0x0135,  name = "Barbed", upgrade_type = ItemUpgradeClassType.Prefix)
    Crippling_Daggers = ItemUpgradeClass(upgrade_id = 0x0136,  name = "Crippling", upgrade_type = ItemUpgradeClassType.Prefix)
    Cruel_Daggers = ItemUpgradeClass(upgrade_id = 0x0137,  name = "Cruel", upgrade_type = ItemUpgradeClassType.Prefix)
    Poisonous_Daggers = ItemUpgradeClass(upgrade_id = 0x0138,  name = "Poisonous", upgrade_type = ItemUpgradeClassType.Prefix)
    Silencing_Daggers = ItemUpgradeClass(upgrade_id = 0x0139,  name = "Silencing", upgrade_type = ItemUpgradeClassType.Prefix)
    Furious_Daggers = ItemUpgradeClass(upgrade_id = 0x013A,  name = "Furious", upgrade_type = ItemUpgradeClassType.Prefix)
    OfDefense_Daggers = ItemUpgradeClass(upgrade_id = 0x0141,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfWarding_Daggers = ItemUpgradeClass(upgrade_id = 0x0142,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Daggers = ItemUpgradeClass(upgrade_id = 0x0143,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Daggers = ItemUpgradeClass(upgrade_id = 0x0144,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Daggers = ItemUpgradeClass(upgrade_id = 0x0145,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDaggerMastery = ItemUpgradeClass(upgrade_id = 0x0146,  name = "of Dagger Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfTheProfession_Daggers = ItemUpgradeClass(upgrade_id = 0x0228,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    OfAptitude_Focus = ItemUpgradeClass(upgrade_id = 0x0217,  name = "of Aptitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Focus = ItemUpgradeClass(upgrade_id = 0x0218,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDevotion_Focus = ItemUpgradeClass(upgrade_id = 0x0219,  name = "of Devotion", upgrade_type = ItemUpgradeClassType.Suffix)
    OfValor_Focus = ItemUpgradeClass(upgrade_id = 0x021A,  name = "of Valor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEndurance_Focus = ItemUpgradeClass(upgrade_id = 0x021B,  name = "of Endurance", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSwiftness_Focus = ItemUpgradeClass(upgrade_id = 0x021C,  name = "of Swiftness", upgrade_type = ItemUpgradeClassType.Suffix)
    Icy_Hammer = ItemUpgradeClass(upgrade_id = 0x0089,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Hammer = ItemUpgradeClass(upgrade_id = 0x008A,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Hammer = ItemUpgradeClass(upgrade_id = 0x008B,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    Fiery_Hammer = ItemUpgradeClass(upgrade_id = 0x008C,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Cruel_Hammer = ItemUpgradeClass(upgrade_id = 0x0097,  name = "Cruel", upgrade_type = ItemUpgradeClassType.Prefix)
    Furious_Hammer = ItemUpgradeClass(upgrade_id = 0x009A,  name = "Furious", upgrade_type = ItemUpgradeClassType.Prefix)
    Heavy_Hammer = ItemUpgradeClass(upgrade_id = 0x00A2,  name = "Heavy", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Hammer = ItemUpgradeClass(upgrade_id = 0x00A4,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Hammer = ItemUpgradeClass(upgrade_id = 0x00A8,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Hammer = ItemUpgradeClass(upgrade_id = 0x00AC,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    OfWarding_Hammer = ItemUpgradeClass(upgrade_id = 0x00C9,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDefense_Hammer = ItemUpgradeClass(upgrade_id = 0x00CC,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Hammer = ItemUpgradeClass(upgrade_id = 0x00CF,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSlaying_Hammer = ItemUpgradeClass(upgrade_id = 0x00D6,  name = "of _____slaying", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Hammer = ItemUpgradeClass(upgrade_id = 0x00DB,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Hammer = ItemUpgradeClass(upgrade_id = 0x00E0,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfHammerMastery = ItemUpgradeClass(upgrade_id = 0x00EA,  name = "of Hammer Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfTheProfession_Hammer = ItemUpgradeClass(upgrade_id = 0x0229,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    IHaveThePower = ItemUpgradeClass(upgrade_id = 0x015C,  name = "\"I have the power!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    LetTheMemoryLiveAgain = ItemUpgradeClass(upgrade_id = 0x015E,  name = "\"Let the Memory Live Again!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    TooMuchInformation = ItemUpgradeClass(upgrade_id = 0x0163,  name = "\"Too Much Information\"", upgrade_type = ItemUpgradeClassType.Inherent)
    GuidedByFate = ItemUpgradeClass(upgrade_id = 0x0164,  name = "\"Guided by Fate\"", upgrade_type = ItemUpgradeClassType.Inherent)
    StrengthAndHonor = ItemUpgradeClass(upgrade_id = 0x0165,  name = "\"Strength and Honor\"", upgrade_type = ItemUpgradeClassType.Inherent)
    VengeanceIsMine = ItemUpgradeClass(upgrade_id = 0x0166,  name = "\"Vengeance is Mine\"", upgrade_type = ItemUpgradeClassType.Inherent)
    DontFearTheReaper = ItemUpgradeClass(upgrade_id = 0x0167,  name = "\"Don't Fear the Reaper\"", upgrade_type = ItemUpgradeClassType.Inherent)
    DanceWithDeath = ItemUpgradeClass(upgrade_id = 0x0168,  name = "\"Dance with Death\"", upgrade_type = ItemUpgradeClassType.Inherent)
    BrawnOverBrains = ItemUpgradeClass(upgrade_id = 0x0169,  name = "\"Brawn over Brains\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ToThePain = ItemUpgradeClass(upgrade_id = 0x016A,  name = "\"To The Pain!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    IgnoranceIsBliss = ItemUpgradeClass(upgrade_id = 0x01B6,  name = "\"Ignorance is Bliss\"", upgrade_type = ItemUpgradeClassType.Inherent)
    LifeIsPain = ItemUpgradeClass(upgrade_id = 0x01B7,  name = "\"Life is Pain\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ManForAllSeasons = ItemUpgradeClass(upgrade_id = 0x01B8,  name = "\"Man for All Seasons\"", upgrade_type = ItemUpgradeClassType.Inherent)
    SurvivalOfTheFittest = ItemUpgradeClass(upgrade_id = 0x01B9,  name = "\"Survival of the Fittest\"", upgrade_type = ItemUpgradeClassType.Inherent)
    MightMakesRight = ItemUpgradeClass(upgrade_id = 0x01BA,  name = "\"Might makes Right!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    KnowingIsHalfTheBattle = ItemUpgradeClass(upgrade_id = 0x01BB,  name = "\"Knowing is Half the Battle.\"", upgrade_type = ItemUpgradeClassType.Inherent)
    FaithIsMy = ItemUpgradeClass(upgrade_id = 0x01BC,  name = "\"Faith is My \"", upgrade_type = ItemUpgradeClassType.Inherent)
    DownButNotOut = ItemUpgradeClass(upgrade_id = 0x01BD,  name = "\"Down But Not Out\"", upgrade_type = ItemUpgradeClassType.Inherent)
    HailToTheKing = ItemUpgradeClass(upgrade_id = 0x01BE,  name = "\"Hail to the King\"", upgrade_type = ItemUpgradeClassType.Inherent)
    BeJustAndFearNot = ItemUpgradeClass(upgrade_id = 0x01BF,  name = "\"Be Just and Fear Not\"", upgrade_type = ItemUpgradeClassType.Inherent)
    LiveForToday = ItemUpgradeClass(upgrade_id = 0x01C0,  name = "\"Live for Today\"", upgrade_type = ItemUpgradeClassType.Inherent)
    SerenityNow = ItemUpgradeClass(upgrade_id = 0x01C1,  name = "\"Serenity Now\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ForgetMeNot = ItemUpgradeClass(upgrade_id = 0x01C2,  name = "\"Forget Me Not\"", upgrade_type = ItemUpgradeClassType.Inherent)
    NotTheFace = ItemUpgradeClass(upgrade_id = 0x01C3,  name = "\"Not the face!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    LeafOnTheWind = ItemUpgradeClass(upgrade_id = 0x01C4,  name = "\"Leaf on the Wind\"", upgrade_type = ItemUpgradeClassType.Inherent)
    LikeARollingStone = ItemUpgradeClass(upgrade_id = 0x01C5,  name = "\"Like a Rolling Stone\"", upgrade_type = ItemUpgradeClassType.Inherent)
    RidersOnTheStorm = ItemUpgradeClass(upgrade_id = 0x01C6,  name = "\"Riders on the Storm\"", upgrade_type = ItemUpgradeClassType.Inherent)
    SleepNowInTheFire = ItemUpgradeClass(upgrade_id = 0x01C7,  name = "\"Sleep Now in the Fire\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ThroughThickAndThin = ItemUpgradeClass(upgrade_id = 0x01C8,  name = "\"Through Thick and Thin\"", upgrade_type = ItemUpgradeClassType.Inherent)
    TheRiddleOfSteel = ItemUpgradeClass(upgrade_id = 0x01C9,  name = "\"The Riddle of Steel\"", upgrade_type = ItemUpgradeClassType.Inherent)
    FearCutsDeeper = ItemUpgradeClass(upgrade_id = 0x01CA,  name = "\"Fear Cuts Deeper\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ICanSeeClearlyNow = ItemUpgradeClass(upgrade_id = 0x01CB,  name = "\"I Can See Clearly Now\"", upgrade_type = ItemUpgradeClassType.Inherent)
    SwiftAsTheWind = ItemUpgradeClass(upgrade_id = 0x01CC,  name = "\"Swift as the Wind\"", upgrade_type = ItemUpgradeClassType.Inherent)
    StrengthOfBody = ItemUpgradeClass(upgrade_id = 0x01CD,  name = "\"Strength of Body\"", upgrade_type = ItemUpgradeClassType.Inherent)
    CastOutTheUnclean = ItemUpgradeClass(upgrade_id = 0x01CE,  name = "\"Cast Out the Unclean\"", upgrade_type = ItemUpgradeClassType.Inherent)
    PureOfHeart = ItemUpgradeClass(upgrade_id = 0x01CF,  name = "\"Pure of Heart\"", upgrade_type = ItemUpgradeClassType.Inherent)
    SoundnessOfMind = ItemUpgradeClass(upgrade_id = 0x01D0,  name = "\"Soundness of Mind\"", upgrade_type = ItemUpgradeClassType.Inherent)
    OnlyTheStrongSurvive = ItemUpgradeClass(upgrade_id = 0x01D1,  name = "\"Only the Strong Survive\"", upgrade_type = ItemUpgradeClassType.Inherent)
    LuckOfTheDraw = ItemUpgradeClass(upgrade_id = 0x01D2,  name = "\"Luck of the Draw\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ShelteredByFaith = ItemUpgradeClass(upgrade_id = 0x01D3,  name = "\"Sheltered by Faith\"", upgrade_type = ItemUpgradeClassType.Inherent)
    NothingToFear = ItemUpgradeClass(upgrade_id = 0x01D4,  name = "\"Nothing to Fear\"", upgrade_type = ItemUpgradeClassType.Inherent)
    RunForYourLife = ItemUpgradeClass(upgrade_id = 0x01D5,  name = "\"Run For Your Life!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    MasterOfMyDomain = ItemUpgradeClass(upgrade_id = 0x01D6,  name = "\"Master of My Domain\"", upgrade_type = ItemUpgradeClassType.Inherent)
    AptitudeNotAttitude = ItemUpgradeClass(upgrade_id = 0x01D7,  name = "\"Aptitude not Attitude\"", upgrade_type = ItemUpgradeClassType.Inherent)
    SeizeTheDay = ItemUpgradeClass(upgrade_id = 0x01D8,  name = "\"Seize the Day\"", upgrade_type = ItemUpgradeClassType.Inherent)
    HaveFaith = ItemUpgradeClass(upgrade_id = 0x01D9,  name = "\"Have Faith\"", upgrade_type = ItemUpgradeClassType.Inherent)
    HaleAndHearty = ItemUpgradeClass(upgrade_id = 0x01DA,  name = "\"Hale and Hearty\"", upgrade_type = ItemUpgradeClassType.Inherent)
    DontCallItAComeback = ItemUpgradeClass(upgrade_id = 0x01DB,  name = "\"Don't call it a comeback!\"", upgrade_type = ItemUpgradeClassType.Inherent)
    IAmSorrow = ItemUpgradeClass(upgrade_id = 0x01DC,  name = "\"I am Sorrow.\"", upgrade_type = ItemUpgradeClassType.Inherent)
    DontThinkTwice = ItemUpgradeClass(upgrade_id = 0x01DD,  name = "\"Don't Think Twice\"", upgrade_type = ItemUpgradeClassType.Inherent)
    ShowMeTheMoney = ItemUpgradeClass(upgrade_id = 0x021E,  name = "\"Show me the money\"", upgrade_type = ItemUpgradeClassType.Inherent)
    MeasureForMeasure = ItemUpgradeClass(upgrade_id = 0x021F,  name = "\"Measure for Measure\"", upgrade_type = ItemUpgradeClassType.Inherent)
    Icy_Scythe = ItemUpgradeClass(upgrade_id = 0x016B,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Scythe = ItemUpgradeClass(upgrade_id = 0x016C,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Scythe = ItemUpgradeClass(upgrade_id = 0x016F,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Scythe = ItemUpgradeClass(upgrade_id = 0x0171,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Scythe = ItemUpgradeClass(upgrade_id = 0x0173,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    Barbed_Scythe = ItemUpgradeClass(upgrade_id = 0x0174,  name = "Barbed", upgrade_type = ItemUpgradeClassType.Prefix)
    Crippling_Scythe = ItemUpgradeClass(upgrade_id = 0x0175,  name = "Crippling", upgrade_type = ItemUpgradeClassType.Prefix)
    Cruel_Scythe = ItemUpgradeClass(upgrade_id = 0x0176,  name = "Cruel", upgrade_type = ItemUpgradeClassType.Prefix)
    Poisonous_Scythe = ItemUpgradeClass(upgrade_id = 0x0177,  name = "Poisonous", upgrade_type = ItemUpgradeClassType.Prefix)
    Heavy_Scythe = ItemUpgradeClass(upgrade_id = 0x0178,  name = "Heavy", upgrade_type = ItemUpgradeClassType.Prefix)
    Furious_Scythe = ItemUpgradeClass(upgrade_id = 0x0179,  name = "Furious", upgrade_type = ItemUpgradeClassType.Prefix)
    OfDefense_Scythe = ItemUpgradeClass(upgrade_id = 0x0188,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfWarding_Scythe = ItemUpgradeClass(upgrade_id = 0x0189,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Scythe = ItemUpgradeClass(upgrade_id = 0x018A,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Scythe = ItemUpgradeClass(upgrade_id = 0x018B,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Scythe = ItemUpgradeClass(upgrade_id = 0x018C,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfScytheMastery = ItemUpgradeClass(upgrade_id = 0x018D,  name = "of Scythe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    Fiery_Scythe = ItemUpgradeClass(upgrade_id = 0x020B,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Scythe = ItemUpgradeClass(upgrade_id = 0x020C,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    OfTheProfession_Scythe = ItemUpgradeClass(upgrade_id = 0x022C,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    OfValor_Shield = ItemUpgradeClass(upgrade_id = 0x0151,  name = "of Valor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEndurance_Shield = ItemUpgradeClass(upgrade_id = 0x0152,  name = "of Endurance", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Shield = ItemUpgradeClass(upgrade_id = 0x0161,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDevotion_Shield = ItemUpgradeClass(upgrade_id = 0x0162,  name = "of Devotion", upgrade_type = ItemUpgradeClassType.Suffix)
    Fiery_Spear = ItemUpgradeClass(upgrade_id = 0x016D,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Spear = ItemUpgradeClass(upgrade_id = 0x016E,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Spear = ItemUpgradeClass(upgrade_id = 0x0170,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Spear = ItemUpgradeClass(upgrade_id = 0x0172,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Spear = ItemUpgradeClass(upgrade_id = 0x017A,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    Barbed_Spear = ItemUpgradeClass(upgrade_id = 0x017B,  name = "Barbed", upgrade_type = ItemUpgradeClassType.Prefix)
    Crippling_Spear = ItemUpgradeClass(upgrade_id = 0x017C,  name = "Crippling", upgrade_type = ItemUpgradeClassType.Prefix)
    Cruel_Spear = ItemUpgradeClass(upgrade_id = 0x017D,  name = "Cruel", upgrade_type = ItemUpgradeClassType.Prefix)
    Poisonous_Spear = ItemUpgradeClass(upgrade_id = 0x017E,  name = "Poisonous", upgrade_type = ItemUpgradeClassType.Prefix)
    Silencing_Spear = ItemUpgradeClass(upgrade_id = 0x017F,  name = "Silencing", upgrade_type = ItemUpgradeClassType.Prefix)
    Furious_Spear = ItemUpgradeClass(upgrade_id = 0x0180,  name = "Furious", upgrade_type = ItemUpgradeClassType.Prefix)
    Heavy_Spear = ItemUpgradeClass(upgrade_id = 0x0181,  name = "Heavy", upgrade_type = ItemUpgradeClassType.Prefix)
    OfDefense_Spear = ItemUpgradeClass(upgrade_id = 0x018E,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfWarding_Spear = ItemUpgradeClass(upgrade_id = 0x018F,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Spear = ItemUpgradeClass(upgrade_id = 0x0190,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Spear = ItemUpgradeClass(upgrade_id = 0x0191,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Spear = ItemUpgradeClass(upgrade_id = 0x0192,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSpearMastery = ItemUpgradeClass(upgrade_id = 0x0193,  name = "of Spear Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    Icy_Spear = ItemUpgradeClass(upgrade_id = 0x020D,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Spear = ItemUpgradeClass(upgrade_id = 0x020E,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    OfTheProfession_Spear = ItemUpgradeClass(upgrade_id = 0x022D,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    Defensive_Staff = ItemUpgradeClass(upgrade_id = 0x0091,  name = "Defensive", upgrade_type = ItemUpgradeClassType.Prefix)
    Insightful_Staff = ItemUpgradeClass(upgrade_id = 0x009C,  name = "Insightful", upgrade_type = ItemUpgradeClassType.Prefix)
    Hale_Staff = ItemUpgradeClass(upgrade_id = 0x009D,  name = "Hale", upgrade_type = ItemUpgradeClassType.Prefix)
    OfAttribute_Staff = ItemUpgradeClass(upgrade_id = 0x00C3,  name = "of <Attribute>", upgrade_type = ItemUpgradeClassType.Suffix)
    OfWarding_Staff = ItemUpgradeClass(upgrade_id = 0x00CA,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Staff = ItemUpgradeClass(upgrade_id = 0x00D0,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDefense_Staff = ItemUpgradeClass(upgrade_id = 0x00D2,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSlaying_Staff = ItemUpgradeClass(upgrade_id = 0x00D7,  name = "of _____slaying", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Staff = ItemUpgradeClass(upgrade_id = 0x00DC,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Staff = ItemUpgradeClass(upgrade_id = 0x00E1,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMastery_Staff = ItemUpgradeClass(upgrade_id = 0x0153,  name = "of Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDevotion_Staff = ItemUpgradeClass(upgrade_id = 0x0154,  name = "of Devotion", upgrade_type = ItemUpgradeClassType.Suffix)
    OfValor_Staff = ItemUpgradeClass(upgrade_id = 0x0155,  name = "of Valor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEndurance_Staff = ItemUpgradeClass(upgrade_id = 0x0156,  name = "of Endurance", upgrade_type = ItemUpgradeClassType.Suffix)
    Swift_Staff = ItemUpgradeClass(upgrade_id = 0x020F,  name = "Swift", upgrade_type = ItemUpgradeClassType.Prefix)
    Adept_Staff = ItemUpgradeClass(upgrade_id = 0x0210,  name = "Adept", upgrade_type = ItemUpgradeClassType.Prefix)
    OfTheProfession_Staff = ItemUpgradeClass(upgrade_id = 0x022B,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    Icy_Sword = ItemUpgradeClass(upgrade_id = 0x008D,  name = "Icy", upgrade_type = ItemUpgradeClassType.Prefix)
    Ebon_Sword = ItemUpgradeClass(upgrade_id = 0x008E,  name = "Ebon", upgrade_type = ItemUpgradeClassType.Prefix)
    Shocking_Sword = ItemUpgradeClass(upgrade_id = 0x008F,  name = "Shocking", upgrade_type = ItemUpgradeClassType.Prefix)
    Fiery_Sword = ItemUpgradeClass(upgrade_id = 0x0090,  name = "Fiery", upgrade_type = ItemUpgradeClassType.Prefix)
    Barbed_Sword = ItemUpgradeClass(upgrade_id = 0x0093,  name = "Barbed", upgrade_type = ItemUpgradeClassType.Prefix)
    Crippling_Sword = ItemUpgradeClass(upgrade_id = 0x0095,  name = "Crippling", upgrade_type = ItemUpgradeClassType.Prefix)
    Cruel_Sword = ItemUpgradeClass(upgrade_id = 0x0098,  name = "Cruel", upgrade_type = ItemUpgradeClassType.Prefix)
    Furious_Sword = ItemUpgradeClass(upgrade_id = 0x009B,  name = "Furious", upgrade_type = ItemUpgradeClassType.Prefix)
    Poisonous_Sword = ItemUpgradeClass(upgrade_id = 0x00A0,  name = "Poisonous", upgrade_type = ItemUpgradeClassType.Prefix)
    Zealous_Sword = ItemUpgradeClass(upgrade_id = 0x00A6,  name = "Zealous", upgrade_type = ItemUpgradeClassType.Prefix)
    Vampiric_Sword = ItemUpgradeClass(upgrade_id = 0x00AA,  name = "Vampiric", upgrade_type = ItemUpgradeClassType.Prefix)
    Sundering_Sword = ItemUpgradeClass(upgrade_id = 0x00AE,  name = "Sundering", upgrade_type = ItemUpgradeClassType.Prefix)
    OfWarding_Sword = ItemUpgradeClass(upgrade_id = 0x00CB,  name = "of Warding", upgrade_type = ItemUpgradeClassType.Suffix)
    OfShelter_Sword = ItemUpgradeClass(upgrade_id = 0x00D1,  name = "of Shelter", upgrade_type = ItemUpgradeClassType.Suffix)
    OfDefense_Sword = ItemUpgradeClass(upgrade_id = 0x00D3,  name = "of Defense", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSlaying_Sword = ItemUpgradeClass(upgrade_id = 0x00D8,  name = "of _____slaying", upgrade_type = ItemUpgradeClassType.Suffix)
    OfFortitude_Sword = ItemUpgradeClass(upgrade_id = 0x00DD,  name = "of Fortitude", upgrade_type = ItemUpgradeClassType.Suffix)
    OfEnchanting_Sword = ItemUpgradeClass(upgrade_id = 0x00E2,  name = "of Enchanting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSwordsmanship = ItemUpgradeClass(upgrade_id = 0x00EB,  name = "of Swordsmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfTheProfession_Sword = ItemUpgradeClass(upgrade_id = 0x022E,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMemory_Wand = ItemUpgradeClass(upgrade_id = 0x015F,  name = "of Memory", upgrade_type = ItemUpgradeClassType.Suffix)
    OfQuickening_Wand = ItemUpgradeClass(upgrade_id = 0x0160,  name = "of Quickening", upgrade_type = ItemUpgradeClassType.Suffix)
    OfTheProfession_Wand = ItemUpgradeClass(upgrade_id = 0x022A,  name = "of the Profession", upgrade_type = ItemUpgradeClassType.Suffix)
    Survivor = ItemUpgradeClass(upgrade_id = 0x01E6,  name = "Survivor", upgrade_type = ItemUpgradeClassType.Prefix)
    Radiant = ItemUpgradeClass(upgrade_id = 0x01E5,  name = "Radiant", upgrade_type = ItemUpgradeClassType.Prefix)
    Stalwart = ItemUpgradeClass(upgrade_id = 0x01E7,  name = "Stalwart", upgrade_type = ItemUpgradeClassType.Prefix)
    Brawlers = ItemUpgradeClass(upgrade_id = 0x01E8,  name = "Brawler's", upgrade_type = ItemUpgradeClassType.Prefix)
    Blessed = ItemUpgradeClass(upgrade_id = 0x01E9,  name = "Blessed", upgrade_type = ItemUpgradeClassType.Prefix)
    Heralds = ItemUpgradeClass(upgrade_id = 0x01EA,  name = "Herald's", upgrade_type = ItemUpgradeClassType.Prefix)
    Sentrys = ItemUpgradeClass(upgrade_id = 0x01EB,  name = "Sentry's", upgrade_type = ItemUpgradeClassType.Prefix)
    Knights = ItemUpgradeClass(upgrade_id = 0x01F9,  name = "Knight's", upgrade_type = ItemUpgradeClassType.Prefix)
    Lieutenants = ItemUpgradeClass(upgrade_id = 0x0208,  name = "Lieutenant's", upgrade_type = ItemUpgradeClassType.Prefix)
    Stonefist = ItemUpgradeClass(upgrade_id = 0x0209,  name = "Stonefist", upgrade_type = ItemUpgradeClassType.Prefix)
    Dreadnought = ItemUpgradeClass(upgrade_id = 0x01FA,  name = "Dreadnought", upgrade_type = ItemUpgradeClassType.Prefix)
    Sentinels = ItemUpgradeClass(upgrade_id = 0x01FB,  name = "Sentinel's", upgrade_type = ItemUpgradeClassType.Prefix)
    Frostbound = ItemUpgradeClass(upgrade_id = 0x01FC,  name = "Frostbound", upgrade_type = ItemUpgradeClassType.Prefix)
    Pyrebound = ItemUpgradeClass(upgrade_id = 0x01FE,  name = "Pyrebound", upgrade_type = ItemUpgradeClassType.Prefix)
    Stormbound = ItemUpgradeClass(upgrade_id = 0x01FF,  name = "Stormbound", upgrade_type = ItemUpgradeClassType.Prefix)
    Scouts = ItemUpgradeClass(upgrade_id = 0x0201,  name = "Scout's", upgrade_type = ItemUpgradeClassType.Prefix)
    Earthbound = ItemUpgradeClass(upgrade_id = 0x01FD,  name = "Earthbound", upgrade_type = ItemUpgradeClassType.Prefix)
    Beastmasters = ItemUpgradeClass(upgrade_id = 0x0200,  name = "Beastmaster's", upgrade_type = ItemUpgradeClassType.Prefix)
    Wanderers = ItemUpgradeClass(upgrade_id = 0x01F6,  name = "Wanderer's", upgrade_type = ItemUpgradeClassType.Prefix)
    Disciples = ItemUpgradeClass(upgrade_id = 0x01F7,  name = "Disciple's", upgrade_type = ItemUpgradeClassType.Prefix)
    Anchorites = ItemUpgradeClass(upgrade_id = 0x01F8,  name = "Anchorite's", upgrade_type = ItemUpgradeClassType.Prefix)
    Bloodstained = ItemUpgradeClass(upgrade_id = 0x020A,  name = "Bloodstained", upgrade_type = ItemUpgradeClassType.Prefix)
    Tormentors = ItemUpgradeClass(upgrade_id = 0x01EC,  name = "Tormentor's", upgrade_type = ItemUpgradeClassType.Prefix)
    Bonelace = ItemUpgradeClass(upgrade_id = 0x01EE,  name = "Bonelace", upgrade_type = ItemUpgradeClassType.Prefix)
    MinionMasters = ItemUpgradeClass(upgrade_id = 0x01EF,  name = "Minion Master's", upgrade_type = ItemUpgradeClassType.Prefix)
    Blighters = ItemUpgradeClass(upgrade_id = 0x01F0,  name = "Blighter's", upgrade_type = ItemUpgradeClassType.Prefix)
    Undertakers = ItemUpgradeClass(upgrade_id = 0x01ED,  name = "Undertaker's", upgrade_type = ItemUpgradeClassType.Prefix)
    Virtuosos = ItemUpgradeClass(upgrade_id = 0x01E4,  name = "Virtuoso's", upgrade_type = ItemUpgradeClassType.Prefix)
    Artificers = ItemUpgradeClass(upgrade_id = 0x01E2,  name = "Artificer's", upgrade_type = ItemUpgradeClassType.Prefix)
    Prodigys = ItemUpgradeClass(upgrade_id = 0x01E3,  name = "Prodigy's", upgrade_type = ItemUpgradeClassType.Prefix)
    Hydromancer = ItemUpgradeClass(upgrade_id = 0x01F2,  name = "Hydromancer", upgrade_type = ItemUpgradeClassType.Prefix)
    Geomancer = ItemUpgradeClass(upgrade_id = 0x01F3,  name = "Geomancer", upgrade_type = ItemUpgradeClassType.Prefix)
    Pyromancer = ItemUpgradeClass(upgrade_id = 0x01F4,  name = "Pyromancer", upgrade_type = ItemUpgradeClassType.Prefix)
    Aeromancer = ItemUpgradeClass(upgrade_id = 0x01F5,  name = "Aeromancer", upgrade_type = ItemUpgradeClassType.Prefix)
    Prismatic = ItemUpgradeClass(upgrade_id = 0x01F1,  name = "Prismatic", upgrade_type = ItemUpgradeClassType.Prefix)
    Vanguards = ItemUpgradeClass(upgrade_id = 0x01DE,  name = "Vanguard's", upgrade_type = ItemUpgradeClassType.Prefix)
    Infiltrators = ItemUpgradeClass(upgrade_id = 0x01DF,  name = "Infiltrator's", upgrade_type = ItemUpgradeClassType.Prefix)
    Saboteurs = ItemUpgradeClass(upgrade_id = 0x01E0,  name = "Saboteur's", upgrade_type = ItemUpgradeClassType.Prefix)
    Nightstalkers = ItemUpgradeClass(upgrade_id = 0x01E1,  name = "Nightstalker's", upgrade_type = ItemUpgradeClassType.Prefix)
    Shamans = ItemUpgradeClass(upgrade_id = 0x0204,  name = "Shaman's", upgrade_type = ItemUpgradeClassType.Prefix)
    GhostForge = ItemUpgradeClass(upgrade_id = 0x0205,  name = "Ghost Forge", upgrade_type = ItemUpgradeClassType.Prefix)
    Mystics = ItemUpgradeClass(upgrade_id = 0x0206,  name = "Mystic's", upgrade_type = ItemUpgradeClassType.Prefix)
    Windwalker = ItemUpgradeClass(upgrade_id = 0x0202,  name = "Windwalker", upgrade_type = ItemUpgradeClassType.Prefix)
    Forsaken = ItemUpgradeClass(upgrade_id = 0x0203,  name = "Forsaken", upgrade_type = ItemUpgradeClassType.Prefix)
    Centurions = ItemUpgradeClass(upgrade_id = 0x0207,  name = "Centurion's", upgrade_type = ItemUpgradeClassType.Prefix)
    OfAttunement = ItemUpgradeClass(upgrade_id = 0x0211,  name = "of Attunement", upgrade_type = ItemUpgradeClassType.Suffix)
    OfRecovery = ItemUpgradeClass(upgrade_id = 0x0213,  name = "of Recovery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfRestoration = ItemUpgradeClass(upgrade_id = 0x0214,  name = "of Restoration", upgrade_type = ItemUpgradeClassType.Suffix)
    OfClarity = ItemUpgradeClass(upgrade_id = 0x0215,  name = "of Clarity", upgrade_type = ItemUpgradeClassType.Suffix)
    OfPurity = ItemUpgradeClass(upgrade_id = 0x0216,  name = "of Purity", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorVigor = ItemUpgradeClass(upgrade_id = 0x00FF,  name = "of Minor Vigor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorVigor2 = ItemUpgradeClass(upgrade_id = 0x00C2,  name = "of Minor Vigor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorVigor = ItemUpgradeClass(upgrade_id = 0x0101,  name = "of Superior Vigor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorVigor = ItemUpgradeClass(upgrade_id = 0x0100,  name = "of Major Vigor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfVitae = ItemUpgradeClass(upgrade_id = 0x0212,  name = "of Vitae", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorAbsorption = ItemUpgradeClass(upgrade_id = 0x00FC,  name = "of Minor Absorption", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorTactics = ItemUpgradeClass(upgrade_id = 0x1501,  name = "of Minor Tactics", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorStrength = ItemUpgradeClass(upgrade_id = 0x1101,  name = "of Minor Strength", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorAxeMastery = ItemUpgradeClass(upgrade_id = 0x1201,  name = "of Minor Axe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorHammerMastery = ItemUpgradeClass(upgrade_id = 0x1301,  name = "of Minor Hammer Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorSwordsmanship = ItemUpgradeClass(upgrade_id = 0x1401,  name = "of Minor Swordsmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorAbsorption = ItemUpgradeClass(upgrade_id = 0x00FD,  name = "of Major Absorption", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorTactics = ItemUpgradeClass(upgrade_id = 0x1502,  name = "of Major Tactics", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorStrength = ItemUpgradeClass(upgrade_id = 0x1102,  name = "of Major Strength", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorAxeMastery = ItemUpgradeClass(upgrade_id = 0x1202,  name = "of Major Axe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorHammerMastery = ItemUpgradeClass(upgrade_id = 0x1302,  name = "of Major Hammer Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorSwordsmanship = ItemUpgradeClass(upgrade_id = 0x1402,  name = "of Major Swordsmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorAbsorption = ItemUpgradeClass(upgrade_id = 0x00FE,  name = "of Superior Absorption", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorTactics = ItemUpgradeClass(upgrade_id = 0x1503,  name = "of Superior Tactics", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorStrength = ItemUpgradeClass(upgrade_id = 0x1103,  name = "of Superior Strength", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorAxeMastery = ItemUpgradeClass(upgrade_id = 0x1203,  name = "of Superior Axe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorHammerMastery = ItemUpgradeClass(upgrade_id = 0x1303,  name = "of Superior Hammer Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorSwordsmanship = ItemUpgradeClass(upgrade_id = 0x1403,  name = "of Superior Swordsmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorWildernessSurvival = ItemUpgradeClass(upgrade_id = 0x1801,  name = "of Minor Wilderness Survival", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorExpertise = ItemUpgradeClass(upgrade_id = 0x1701,  name = "of Minor Expertise", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorBeastMastery = ItemUpgradeClass(upgrade_id = 0x1601,  name = "of Minor Beast Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorMarksmanship = ItemUpgradeClass(upgrade_id = 0x1901,  name = "of Minor Marksmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorWildernessSurvival = ItemUpgradeClass(upgrade_id = 0x1802,  name = "of Major Wilderness Survival", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorExpertise = ItemUpgradeClass(upgrade_id = 0x1702,  name = "of Major Expertise", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorBeastMastery = ItemUpgradeClass(upgrade_id = 0x1602,  name = "of Major Beast Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorMarksmanship = ItemUpgradeClass(upgrade_id = 0x1902,  name = "of Major Marksmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorWildernessSurvival = ItemUpgradeClass(upgrade_id = 0x1803,  name = "of Superior Wilderness Survival", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorExpertise = ItemUpgradeClass(upgrade_id = 0x1703,  name = "of Superior Expertise", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorBeastMastery = ItemUpgradeClass(upgrade_id = 0x1603,  name = "of Superior Beast Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorMarksmanship = ItemUpgradeClass(upgrade_id = 0x1903,  name = "of Superior Marksmanship", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorHealingPrayers = ItemUpgradeClass(upgrade_id = 0x0D01,  name = "of Minor Healing Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorSmitingPrayers = ItemUpgradeClass(upgrade_id = 0x0E01,  name = "of Minor Smiting Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorProtectionPrayers = ItemUpgradeClass(upgrade_id = 0x0F01,  name = "of Minor Protection Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorDivineFavor = ItemUpgradeClass(upgrade_id = 0x1001,  name = "of Minor Divine Favor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorHealingPrayers = ItemUpgradeClass(upgrade_id = 0x0D02,  name = "of Major Healing Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorSmitingPrayers = ItemUpgradeClass(upgrade_id = 0x0E02,  name = "of Major Smiting Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorProtectionPrayers = ItemUpgradeClass(upgrade_id = 0x0F02,  name = "of Major Protection Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorDivineFavor = ItemUpgradeClass(upgrade_id = 0x1002,  name = "of Major Divine Favor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorHealingPrayers = ItemUpgradeClass(upgrade_id = 0x0D03,  name = "of Superior Healing Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorSmitingPrayers = ItemUpgradeClass(upgrade_id = 0x0E03,  name = "of Superior Smiting Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorProtectionPrayers = ItemUpgradeClass(upgrade_id = 0x0F03,  name = "of Superior Protection Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorDivineFavor = ItemUpgradeClass(upgrade_id = 0x1003,  name = "of Superior Divine Favor", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorBloodMagic = ItemUpgradeClass(upgrade_id = 0x0401,  name = "of Minor Blood Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorDeathMagic = ItemUpgradeClass(upgrade_id = 0x0501,  name = "of Minor Death Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorCurses = ItemUpgradeClass(upgrade_id = 0x0701,  name = "of Minor Curses", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorSoulReaping = ItemUpgradeClass(upgrade_id = 0x0601,  name = "of Minor Soul Reaping", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorBloodMagic = ItemUpgradeClass(upgrade_id = 0x0402,  name = "of Major Blood Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorDeathMagic = ItemUpgradeClass(upgrade_id = 0x0502,  name = "of Major Death Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorCurses = ItemUpgradeClass(upgrade_id = 0x0702,  name = "of Major Curses", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorSoulReaping = ItemUpgradeClass(upgrade_id = 0x0602,  name = "of Major Soul Reaping", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorBloodMagic = ItemUpgradeClass(upgrade_id = 0x0403,  name = "of Superior Blood Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorDeathMagic = ItemUpgradeClass(upgrade_id = 0x0503,  name = "of Superior Death Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorCurses = ItemUpgradeClass(upgrade_id = 0x0703,  name = "of Superior Curses", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorSoulReaping = ItemUpgradeClass(upgrade_id = 0x0603,  name = "of Superior Soul Reaping", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorFastCasting = ItemUpgradeClass(upgrade_id = 0x0001,  name = "of Minor Fast Casting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorDominationMagic = ItemUpgradeClass(upgrade_id = 0x0201,  name = "of Minor Domination Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorIllusionMagic = ItemUpgradeClass(upgrade_id = 0x0101,  name = "of Minor Illusion Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorInspirationMagic = ItemUpgradeClass(upgrade_id = 0x0301,  name = "of Minor Inspiration Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorFastCasting = ItemUpgradeClass(upgrade_id = 0x0002,  name = "of Major Fast Casting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorDominationMagic = ItemUpgradeClass(upgrade_id = 0x0202,  name = "of Major Domination Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorIllusionMagic = ItemUpgradeClass(upgrade_id = 0x0102,  name = "of Major Illusion Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorInspirationMagic = ItemUpgradeClass(upgrade_id = 0x0302,  name = "of Major Inspiration Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorFastCasting = ItemUpgradeClass(upgrade_id = 0x0003,  name = "of Superior Fast Casting", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorDominationMagic = ItemUpgradeClass(upgrade_id = 0x0203,  name = "of Superior Domination Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorIllusionMagic = ItemUpgradeClass(upgrade_id = 0x0103,  name = "of Superior Illusion Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorInspirationMagic = ItemUpgradeClass(upgrade_id = 0x0303,  name = "of Superior Inspiration Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorEnergyStorage = ItemUpgradeClass(upgrade_id = 0x0C01,  name = "of Minor Energy Storage", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorFireMagic = ItemUpgradeClass(upgrade_id = 0x0A01,  name = "of Minor Fire Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorAirMagic = ItemUpgradeClass(upgrade_id = 0x0801,  name = "of Minor Air Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorEarthMagic = ItemUpgradeClass(upgrade_id = 0x0901,  name = "of Minor Earth Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorWaterMagic = ItemUpgradeClass(upgrade_id = 0x0B01,  name = "of Minor Water Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorEnergyStorage = ItemUpgradeClass(upgrade_id = 0x0C02,  name = "of Major Energy Storage", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorFireMagic = ItemUpgradeClass(upgrade_id = 0x0A02,  name = "of Major Fire Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorAirMagic = ItemUpgradeClass(upgrade_id = 0x0802,  name = "of Major Air Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorEarthMagic = ItemUpgradeClass(upgrade_id = 0x0902,  name = "of Major Earth Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorWaterMagic = ItemUpgradeClass(upgrade_id = 0x0B02,  name = "of Major Water Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorEnergyStorage = ItemUpgradeClass(upgrade_id = 0x0C03,  name = "of Superior Energy Storage", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorFireMagic = ItemUpgradeClass(upgrade_id = 0x0A03,  name = "of Superior Fire Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorAirMagic = ItemUpgradeClass(upgrade_id = 0x0803,  name = "of Superior Air Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorEarthMagic = ItemUpgradeClass(upgrade_id = 0x0903,  name = "of Superior Earth Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorWaterMagic = ItemUpgradeClass(upgrade_id = 0x0B03,  name = "of Superior Water Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorCriticalStrikes = ItemUpgradeClass(upgrade_id = 0x2301,  name = "of Minor Critical Strikes", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorDaggerMastery = ItemUpgradeClass(upgrade_id = 0x1D01,  name = "of Minor Dagger Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorDeadlyArts = ItemUpgradeClass(upgrade_id = 0x1E01,  name = "of Minor Deadly Arts", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorShadowArts = ItemUpgradeClass(upgrade_id = 0x1F01,  name = "of Minor Shadow Arts", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorCriticalStrikes = ItemUpgradeClass(upgrade_id = 0x2302,  name = "of Major Critical Strikes", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorDaggerMastery = ItemUpgradeClass(upgrade_id = 0x1D02,  name = "of Major Dagger Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorDeadlyArts = ItemUpgradeClass(upgrade_id = 0x1E02,  name = "of Major Deadly Arts", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorShadowArts = ItemUpgradeClass(upgrade_id = 0x1F02,  name = "of Major Shadow Arts", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorCriticalStrikes = ItemUpgradeClass(upgrade_id = 0x2303,  name = "of Superior Critical Strikes", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorDaggerMastery = ItemUpgradeClass(upgrade_id = 0x1D03,  name = "of Superior Dagger Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorDeadlyArts = ItemUpgradeClass(upgrade_id = 0x1E03,  name = "of Superior Deadly Arts", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorShadowArts = ItemUpgradeClass(upgrade_id = 0x1F03,  name = "of Superior Shadow Arts", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorChannelingMagic = ItemUpgradeClass(upgrade_id = 0x2201,  name = "of Minor Channeling Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorRestorationMagic = ItemUpgradeClass(upgrade_id = 0x2101,  name = "of Minor Restoration Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorCommuning = ItemUpgradeClass(upgrade_id = 0x2001,  name = "of Minor Communing", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorSpawningPower = ItemUpgradeClass(upgrade_id = 0x2401,  name = "of Minor Spawning Power", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorChannelingMagic = ItemUpgradeClass(upgrade_id = 0x2202,  name = "of Major Channeling Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorRestorationMagic = ItemUpgradeClass(upgrade_id = 0x2102,  name = "of Major Restoration Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorCommuning = ItemUpgradeClass(upgrade_id = 0x2002,  name = "of Major Communing", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorSpawningPower = ItemUpgradeClass(upgrade_id = 0x2402,  name = "of Major Spawning Power", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorChannelingMagic = ItemUpgradeClass(upgrade_id = 0x2203,  name = "of Superior Channeling Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorRestorationMagic = ItemUpgradeClass(upgrade_id = 0x2103,  name = "of Superior Restoration Magic", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorCommuning = ItemUpgradeClass(upgrade_id = 0x2003,  name = "of Superior Communing", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorSpawningPower = ItemUpgradeClass(upgrade_id = 0x2403,  name = "of Superior Spawning Power", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorMysticism = ItemUpgradeClass(upgrade_id = 0x2C01,  name = "of Minor Mysticism", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorEarthPrayers = ItemUpgradeClass(upgrade_id = 0x2B01,  name = "of Minor Earth Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorScytheMastery = ItemUpgradeClass(upgrade_id = 0x2901,  name = "of Minor Scythe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorWindPrayers = ItemUpgradeClass(upgrade_id = 0x2A01,  name = "of Minor Wind Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorMysticism = ItemUpgradeClass(upgrade_id = 0x2C02,  name = "of Major Mysticism", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorEarthPrayers = ItemUpgradeClass(upgrade_id = 0x2B02,  name = "of Major Earth Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorScytheMastery = ItemUpgradeClass(upgrade_id = 0x2902,  name = "of Major Scythe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorWindPrayers = ItemUpgradeClass(upgrade_id = 0x2A02,  name = "of Major Wind Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorMysticism = ItemUpgradeClass(upgrade_id = 0x2C03,  name = "of Superior Mysticism", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorEarthPrayers = ItemUpgradeClass(upgrade_id = 0x2B03,  name = "of Superior Earth Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorScytheMastery = ItemUpgradeClass(upgrade_id = 0x2903,  name = "of Superior Scythe Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorWindPrayers = ItemUpgradeClass(upgrade_id = 0x2A03,  name = "of Superior Wind Prayers", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorLeadership = ItemUpgradeClass(upgrade_id = 0x2801,  name = "of Minor Leadership", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorMotivation = ItemUpgradeClass(upgrade_id = 0x2701,  name = "of Minor Motivation", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorCommand = ItemUpgradeClass(upgrade_id = 0x2601,  name = "of Minor Command", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMinorSpearMastery = ItemUpgradeClass(upgrade_id = 0x2501,  name = "of Minor Spear Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorLeadership = ItemUpgradeClass(upgrade_id = 0x2802,  name = "of Major Leadership", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorMotivation = ItemUpgradeClass(upgrade_id = 0x2702,  name = "of Major Motivation", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorCommand = ItemUpgradeClass(upgrade_id = 0x2602,  name = "of Major Command", upgrade_type = ItemUpgradeClassType.Suffix)
    OfMajorSpearMastery = ItemUpgradeClass(upgrade_id = 0x2502,  name = "of Major Spear Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorLeadership = ItemUpgradeClass(upgrade_id = 0x2803,  name = "of Superior Leadership", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorMotivation = ItemUpgradeClass(upgrade_id = 0x2703,  name = "of Superior Motivation", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorCommand = ItemUpgradeClass(upgrade_id = 0x2603,  name = "of Superior Command", upgrade_type = ItemUpgradeClassType.Suffix)
    OfSuperiorSpearMastery = ItemUpgradeClass(upgrade_id = 0x2503,  name = "of Superior Spear Mastery", upgrade_type = ItemUpgradeClassType.Suffix)
    
    UpgradeMinorRune_Warrior = ItemUpgradeClass(upgrade_id = 0x00B3,  name = "Upgrade warrior minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Warrior = ItemUpgradeClass(upgrade_id = 0x0167,  name = "Applies to warrior minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Warrior = ItemUpgradeClass(upgrade_id = 0x00B9,  name = "Upgrade warrior major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Warrior = ItemUpgradeClass(upgrade_id = 0x0173,  name = "Applies to warrior major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Warrior = ItemUpgradeClass(upgrade_id = 0x00BF,  name = "Upgrade warrior superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Warrior = ItemUpgradeClass(upgrade_id = 0x017F,  name = "Applies to warrior superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Ranger = ItemUpgradeClass(upgrade_id = 0x00B4,  name = "Upgrade ranger minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Ranger = ItemUpgradeClass(upgrade_id = 0x0169,  name = "Applies to ranger minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Ranger = ItemUpgradeClass(upgrade_id = 0x00BA,  name = "Upgrade ranger major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Ranger = ItemUpgradeClass(upgrade_id = 0x0175,  name = "Applies to ranger major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Ranger = ItemUpgradeClass(upgrade_id = 0x00C0,  name = "Upgrade ranger superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Ranger = ItemUpgradeClass(upgrade_id = 0x0181,  name = "Applies to ranger superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Monk = ItemUpgradeClass(upgrade_id = 0x00B2,  name = "Upgrade monk major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Monk = ItemUpgradeClass(upgrade_id = 0x0165,  name = "Applies to monk minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Monk = ItemUpgradeClass(upgrade_id = 0x00B8,  name = "Upgrade monk major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Monk = ItemUpgradeClass(upgrade_id = 0x0171,  name = "Applies to monk major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Monk = ItemUpgradeClass(upgrade_id = 0x00BE,  name = "Upgrade monk superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Monk = ItemUpgradeClass(upgrade_id = 0x017D,  name = "Applies to monk superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Necromancer = ItemUpgradeClass(upgrade_id = 0x00B0,  name = "Upgrade necromancer minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Necromancer = ItemUpgradeClass(upgrade_id = 0x0161,  name = "Applies to necromancer minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Necromancer = ItemUpgradeClass(upgrade_id = 0x00B6,  name = "Upgrade necromancer major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Necromancer = ItemUpgradeClass(upgrade_id = 0x016D,  name = "Applies to necromancer major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Necromancer = ItemUpgradeClass(upgrade_id = 0x00BC,  name = "Upgrade necromancer superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Necromancer = ItemUpgradeClass(upgrade_id = 0x0179,  name = "Applies to necromancer superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Mesmer = ItemUpgradeClass(upgrade_id = 0x00AF,  name = "Upgrade mesmer minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Mesmer = ItemUpgradeClass(upgrade_id = 0x015F,  name = "Applies to mesmer minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Mesmer = ItemUpgradeClass(upgrade_id = 0x00B5,  name = "Upgrade mesmer major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Mesmer = ItemUpgradeClass(upgrade_id = 0x016B,  name = "Applies to mesmer major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Mesmer = ItemUpgradeClass(upgrade_id = 0x00BB,  name = "Upgrade mesmer superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Mesmer = ItemUpgradeClass(upgrade_id = 0x0177,  name = "Applies to mesmer superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Elementalist = ItemUpgradeClass(upgrade_id = 0x00B1,  name = "Upgrade elementalist minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Elementalist = ItemUpgradeClass(upgrade_id = 0x0163,  name = "Applies to elementalist minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Elementalist = ItemUpgradeClass(upgrade_id = 0x00B7,  name = "Upgrade elementalist major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Elementalist = ItemUpgradeClass(upgrade_id = 0x016F,  name = "Applies to elementalist major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Elementalist = ItemUpgradeClass(upgrade_id = 0x00BD,  name = "Upgrade elementalist superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Elementalist = ItemUpgradeClass(upgrade_id = 0x017B,  name = "Applies to elementalist superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Assassin = ItemUpgradeClass(upgrade_id = 0x013B,  name = "Upgrade assassin minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Assassin = ItemUpgradeClass(upgrade_id = 0x0277,  name = "Applies to assassin minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Assassin = ItemUpgradeClass(upgrade_id = 0x014C,  name = "Upgrade assassin major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Assassin = ItemUpgradeClass(upgrade_id = 0x0279,  name = "Applies to assassin major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Assassin = ItemUpgradeClass(upgrade_id = 0x013D,  name = "Upgrade assassin superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Assassin = ItemUpgradeClass(upgrade_id = 0x027B,  name = "Applies to assassin superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Ritualist = ItemUpgradeClass(upgrade_id = 0x013E,  name = "Upgrade ritualist minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Ritualist = ItemUpgradeClass(upgrade_id = 0x027D,  name = "Applies to ritualist minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Ritualist = ItemUpgradeClass(upgrade_id = 0x013F,  name = "Upgrade ritualist major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Ritualist = ItemUpgradeClass(upgrade_id = 0x027F,  name = "Applies to ritualist major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Ritualist = ItemUpgradeClass(upgrade_id = 0x0140,  name = "Upgrade ritualist superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Ritualist = ItemUpgradeClass(upgrade_id = 0x0281,  name = "Applies to ritualist superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Dervish = ItemUpgradeClass(upgrade_id = 0x0182,  name = "Upgrade dervish minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Dervish = ItemUpgradeClass(upgrade_id = 0x0305,  name = "Applies to dervish minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Dervish = ItemUpgradeClass(upgrade_id = 0x0183,  name = "Upgrade dervish major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Dervish = ItemUpgradeClass(upgrade_id = 0x0307,  name = "Applies to dervish major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Dervish = ItemUpgradeClass(upgrade_id = 0x0184,  name = "Upgrade dervish superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Dervish = ItemUpgradeClass(upgrade_id = 0x0309,  name = "Applies to dervish superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Paragon = ItemUpgradeClass(upgrade_id = 0x0185,  name = "Upgrade paragon minor rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Paragon = ItemUpgradeClass(upgrade_id = 0x030B,  name = "Applies to paragon minor rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Paragon = ItemUpgradeClass(upgrade_id = 0x0186,  name = "Upgrade paragon major rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Paragon = ItemUpgradeClass(upgrade_id = 0x030D,  name = "Applies to paragon major rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Paragon = ItemUpgradeClass(upgrade_id = 0x0187,  name = "Upgrade paragon superior rune", upgrade_type = ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Paragon = ItemUpgradeClass(upgrade_id = 0x030F,  name = "Applies to paragon superior rune", upgrade_type = ItemUpgradeClassType.AppliesToRune)

ITEM_UPGRADES_CLASSES = [up.value for up in ItemUpgrade.__members__.values() if isinstance(up.value, ItemUpgradeClass)]  

class ItemUpgradeIdTuple(Enum):
    Unknown = -1
    Icy_Axe = (0x0081, ItemUpgradeClassType.Prefix)
    Ebon_Axe = (0x0082, ItemUpgradeClassType.Prefix)
    Shocking_Axe = (0x0083, ItemUpgradeClassType.Prefix)
    Fiery_Axe = (0x0084, ItemUpgradeClassType.Prefix)
    Barbed_Axe = (0x0092, ItemUpgradeClassType.Prefix)
    Crippling_Axe = (0x0094, ItemUpgradeClassType.Prefix)
    Cruel_Axe = (0x0096, ItemUpgradeClassType.Prefix)
    Furious_Axe = (0x0099, ItemUpgradeClassType.Prefix)
    Poisonous_Axe = (0x009E, ItemUpgradeClassType.Prefix)
    Heavy_Axe = (0x00A1, ItemUpgradeClassType.Prefix)
    Zealous_Axe = (0x00A3, ItemUpgradeClassType.Prefix)
    Vampiric_Axe = (0x00A7, ItemUpgradeClassType.Prefix)
    Sundering_Axe = (0x00AB, ItemUpgradeClassType.Prefix)
    OfDefense_Axe = (0x00C5, ItemUpgradeClassType.Suffix)
    OfWarding_Axe = (0x00C7, ItemUpgradeClassType.Suffix)
    OfShelter_Axe = (0x00CD, ItemUpgradeClassType.Suffix)
    OfSlaying_Axe = (0x00D4, ItemUpgradeClassType.Suffix)
    OfFortitude_Axe = (0x00D9, ItemUpgradeClassType.Suffix)
    OfEnchanting_Axe = (0x00DE, ItemUpgradeClassType.Suffix)
    OfAxeMastery = (0x00E8, ItemUpgradeClassType.Suffix)
    OfTheProfession_Axe = (0x0226, ItemUpgradeClassType.Suffix)
    Icy_Bow = (0x0085, ItemUpgradeClassType.Prefix)
    Ebon_Bow = (0x0086, ItemUpgradeClassType.Prefix)
    Shocking_Bow = (0x0087, ItemUpgradeClassType.Prefix)
    Fiery_Bow = (0x0088, ItemUpgradeClassType.Prefix)
    Poisonous_Bow = (0x009F, ItemUpgradeClassType.Prefix)
    Zealous_Bow = (0x00A5, ItemUpgradeClassType.Prefix)
    Vampiric_Bow = (0x00A9, ItemUpgradeClassType.Prefix)
    Sundering_Bow = (0x00AD, ItemUpgradeClassType.Prefix)
    OfDefense_Bow = (0x00C6, ItemUpgradeClassType.Suffix)
    OfWarding_Bow = (0x00C8, ItemUpgradeClassType.Suffix)
    OfShelter_Bow = (0x00CE, ItemUpgradeClassType.Suffix)
    OfSlaying_Bow = (0x00D5, ItemUpgradeClassType.Suffix)
    OfFortitude_Bow = (0x00DA, ItemUpgradeClassType.Suffix)
    OfEnchanting_Bow = (0x00DF, ItemUpgradeClassType.Suffix)
    OfMarksmanship = (0x00E9, ItemUpgradeClassType.Suffix)
    Barbed_Bow = (0x0147, ItemUpgradeClassType.Prefix)
    Crippling_Bow = (0x0148, ItemUpgradeClassType.Prefix)
    Silencing_Bow = (0x0149, ItemUpgradeClassType.Prefix)
    OfTheProfession_Bow = (0x0227, ItemUpgradeClassType.Suffix)
    Icy_Daggers = (0x012E, ItemUpgradeClassType.Prefix)
    Ebon_Daggers = (0x012F, ItemUpgradeClassType.Prefix)
    Fiery_Daggers = (0x0130, ItemUpgradeClassType.Prefix)
    Shocking_Daggers = (0x0131, ItemUpgradeClassType.Prefix)
    Zealous_Daggers = (0x0132, ItemUpgradeClassType.Prefix)
    Vampiric_Daggers = (0x0133, ItemUpgradeClassType.Prefix)
    Sundering_Daggers = (0x0134, ItemUpgradeClassType.Prefix)
    Barbed_Daggers = (0x0135, ItemUpgradeClassType.Prefix)
    Crippling_Daggers = (0x0136, ItemUpgradeClassType.Prefix)
    Cruel_Daggers = (0x0137, ItemUpgradeClassType.Prefix)
    Poisonous_Daggers = (0x0138, ItemUpgradeClassType.Prefix)
    Silencing_Daggers = (0x0139, ItemUpgradeClassType.Prefix)
    Furious_Daggers = (0x013A, ItemUpgradeClassType.Prefix)
    OfDefense_Daggers = (0x0141, ItemUpgradeClassType.Suffix)
    OfWarding_Daggers = (0x0142, ItemUpgradeClassType.Suffix)
    OfShelter_Daggers = (0x0143, ItemUpgradeClassType.Suffix)
    OfEnchanting_Daggers = (0x0144, ItemUpgradeClassType.Suffix)
    OfFortitude_Daggers = (0x0145, ItemUpgradeClassType.Suffix)
    OfDaggerMastery = (0x0146, ItemUpgradeClassType.Suffix)
    OfTheProfession_Daggers = (0x0228, ItemUpgradeClassType.Suffix)
    OfAptitude_Focus = (0x0217, ItemUpgradeClassType.Suffix)
    OfFortitude_Focus = (0x0218, ItemUpgradeClassType.Suffix)
    OfDevotion_Focus = (0x0219, ItemUpgradeClassType.Suffix)
    OfValor_Focus = (0x021A, ItemUpgradeClassType.Suffix)
    OfEndurance_Focus = (0x021B, ItemUpgradeClassType.Suffix)
    OfSwiftness_Focus = (0x021C, ItemUpgradeClassType.Suffix)
    Icy_Hammer = (0x0089, ItemUpgradeClassType.Prefix)
    Ebon_Hammer = (0x008A, ItemUpgradeClassType.Prefix)
    Shocking_Hammer = (0x008B, ItemUpgradeClassType.Prefix)
    Fiery_Hammer = (0x008C, ItemUpgradeClassType.Prefix)
    Cruel_Hammer = (0x0097, ItemUpgradeClassType.Prefix)
    Furious_Hammer = (0x009A, ItemUpgradeClassType.Prefix)
    Heavy_Hammer = (0x00A2, ItemUpgradeClassType.Prefix)
    Zealous_Hammer = (0x00A4, ItemUpgradeClassType.Prefix)
    Vampiric_Hammer = (0x00A8, ItemUpgradeClassType.Prefix)
    Sundering_Hammer = (0x00AC, ItemUpgradeClassType.Prefix)
    OfWarding_Hammer = (0x00C9, ItemUpgradeClassType.Suffix)
    OfDefense_Hammer = (0x00CC, ItemUpgradeClassType.Suffix)
    OfShelter_Hammer = (0x00CF, ItemUpgradeClassType.Suffix)
    OfSlaying_Hammer = (0x00D6, ItemUpgradeClassType.Suffix)
    OfFortitude_Hammer = (0x00DB, ItemUpgradeClassType.Suffix)
    OfEnchanting_Hammer = (0x00E0, ItemUpgradeClassType.Suffix)
    OfHammerMastery = (0x00EA, ItemUpgradeClassType.Suffix)
    OfTheProfession_Hammer = (0x0229, ItemUpgradeClassType.Suffix)
    
    Icy_Scythe = (0x016B, ItemUpgradeClassType.Prefix)
    Ebon_Scythe = (0x016C, ItemUpgradeClassType.Prefix)
    Zealous_Scythe = (0x016F, ItemUpgradeClassType.Prefix)
    Vampiric_Scythe = (0x0171, ItemUpgradeClassType.Prefix)
    Sundering_Scythe = (0x0173, ItemUpgradeClassType.Prefix)
    Barbed_Scythe = (0x0174, ItemUpgradeClassType.Prefix)
    Crippling_Scythe = (0x0175, ItemUpgradeClassType.Prefix)
    Cruel_Scythe = (0x0176, ItemUpgradeClassType.Prefix)
    Poisonous_Scythe = (0x0177, ItemUpgradeClassType.Prefix)
    Heavy_Scythe = (0x0178, ItemUpgradeClassType.Prefix)
    Furious_Scythe = (0x0179, ItemUpgradeClassType.Prefix)
    OfDefense_Scythe = (0x0188, ItemUpgradeClassType.Suffix)
    OfWarding_Scythe = (0x0189, ItemUpgradeClassType.Suffix)
    OfShelter_Scythe = (0x018A, ItemUpgradeClassType.Suffix)
    OfEnchanting_Scythe = (0x018B, ItemUpgradeClassType.Suffix)
    OfFortitude_Scythe = (0x018C, ItemUpgradeClassType.Suffix)
    OfScytheMastery = (0x018D, ItemUpgradeClassType.Suffix)
    Fiery_Scythe = (0x020B, ItemUpgradeClassType.Prefix)
    Shocking_Scythe = (0x020C, ItemUpgradeClassType.Prefix)
    OfTheProfession_Scythe = (0x022C, ItemUpgradeClassType.Suffix)
    OfValor_Shield = (0x0151, ItemUpgradeClassType.Suffix)
    OfEndurance_Shield = (0x0152, ItemUpgradeClassType.Suffix)
    OfFortitude_Shield = (0x0161, ItemUpgradeClassType.Suffix)
    OfDevotion_Shield = (0x0162, ItemUpgradeClassType.Suffix)
    Fiery_Spear = (0x016D, ItemUpgradeClassType.Prefix)
    Shocking_Spear = (0x016E, ItemUpgradeClassType.Prefix)
    Zealous_Spear = (0x0170, ItemUpgradeClassType.Prefix)
    Vampiric_Spear = (0x0172, ItemUpgradeClassType.Prefix)
    Sundering_Spear = (0x017A, ItemUpgradeClassType.Prefix)
    Barbed_Spear = (0x017B, ItemUpgradeClassType.Prefix)
    Crippling_Spear = (0x017C, ItemUpgradeClassType.Prefix)
    Cruel_Spear = (0x017D, ItemUpgradeClassType.Prefix)
    Poisonous_Spear = (0x017E, ItemUpgradeClassType.Prefix)
    Silencing_Spear = (0x017F, ItemUpgradeClassType.Prefix)
    Furious_Spear = (0x0180, ItemUpgradeClassType.Prefix)
    Heavy_Spear = (0x0181, ItemUpgradeClassType.Prefix)
    OfDefense_Spear = (0x018E, ItemUpgradeClassType.Suffix)
    OfWarding_Spear = (0x018F, ItemUpgradeClassType.Suffix)
    OfShelter_Spear = (0x0190, ItemUpgradeClassType.Suffix)
    OfEnchanting_Spear = (0x0191, ItemUpgradeClassType.Suffix)
    OfFortitude_Spear = (0x0192, ItemUpgradeClassType.Suffix)
    OfSpearMastery = (0x0193, ItemUpgradeClassType.Suffix)
    Icy_Spear = (0x020D, ItemUpgradeClassType.Prefix)
    Ebon_Spear = (0x020E, ItemUpgradeClassType.Prefix)
    OfTheProfession_Spear = (0x022D, ItemUpgradeClassType.Suffix)
    
    Defensive_Staff = (0x0091, ItemUpgradeClassType.Prefix)
    Insightful_Staff = (0x009C, ItemUpgradeClassType.Prefix)
    Hale_Staff = (0x009D, ItemUpgradeClassType.Prefix)
    OfAttribute_Staff = (0x00C3, ItemUpgradeClassType.Suffix)
    OfWarding_Staff = (0x00CA, ItemUpgradeClassType.Suffix)
    OfShelter_Staff = (0x00D0, ItemUpgradeClassType.Suffix)
    OfDefense_Staff = (0x00D2, ItemUpgradeClassType.Suffix)
    OfSlaying_Staff = (0x00D7, ItemUpgradeClassType.Suffix)
    OfFortitude_Staff = (0x00DC, ItemUpgradeClassType.Suffix)
    OfEnchanting_Staff = (0x00E1, ItemUpgradeClassType.Suffix)
    OfMastery_Staff = (0x0153, ItemUpgradeClassType.Suffix)
    OfDevotion_Staff = (0x0154, ItemUpgradeClassType.Suffix)
    OfValor_Staff = (0x0155, ItemUpgradeClassType.Suffix)
    OfEndurance_Staff = (0x0156, ItemUpgradeClassType.Suffix)
    Swift_Staff = (0x020F, ItemUpgradeClassType.Prefix)
    Adept_Staff = (0x0210, ItemUpgradeClassType.Prefix)
    OfTheProfession_Staff = (0x022B, ItemUpgradeClassType.Suffix)
    Icy_Sword = (0x008D, ItemUpgradeClassType.Prefix)
    Ebon_Sword = (0x008E, ItemUpgradeClassType.Prefix)  
    Shocking_Sword = (0x008F, ItemUpgradeClassType.Prefix)
    Fiery_Sword = (0x0090, ItemUpgradeClassType.Prefix)
    Barbed_Sword = (0x0093, ItemUpgradeClassType.Prefix)
    Crippling_Sword = (0x0095, ItemUpgradeClassType.Prefix)
    Cruel_Sword = (0x0098, ItemUpgradeClassType.Prefix)
    Furious_Sword = (0x009B, ItemUpgradeClassType.Prefix)
    Poisonous_Sword = (0x00A0, ItemUpgradeClassType.Prefix)
    Zealous_Sword = (0x00A6, ItemUpgradeClassType.Prefix)
    Vampiric_Sword = (0x00AA, ItemUpgradeClassType.Prefix)
    Sundering_Sword = (0x00AE, ItemUpgradeClassType.Prefix)
    OfWarding_Sword = (0x00CB, ItemUpgradeClassType.Suffix)
    OfShelter_Sword = (0x00D1, ItemUpgradeClassType.Suffix)
    OfDefense_Sword = (0x00D3, ItemUpgradeClassType.Suffix)
    OfSlaying_Sword = (0x00D8, ItemUpgradeClassType.Suffix)
    OfFortitude_Sword = (0x00DD, ItemUpgradeClassType.Suffix)
    OfEnchanting_Sword = (0x00E2, ItemUpgradeClassType.Suffix)
    OfSwordsmanship = (0x00EB, ItemUpgradeClassType.Suffix)
    OfTheProfession_Sword = (0x022E, ItemUpgradeClassType.Suffix)
    OfMemory_Wand = (0x015F, ItemUpgradeClassType.Suffix)
    OfQuickening_Wand = (0x0160, ItemUpgradeClassType.Suffix)
    OfTheProfession_Wand = (0x022A, ItemUpgradeClassType.Suffix)
    
    IHaveThePower = (0x015C, ItemUpgradeClassType.Inherent)
    LetTheMemoryLiveAgain = (0x015E, ItemUpgradeClassType.Inherent)
    TooMuchInformation = (0x0163, ItemUpgradeClassType.Inherent)
    GuidedByFate = (0x0164, ItemUpgradeClassType.Inherent)
    StrengthAndHonor = (0x0165, ItemUpgradeClassType.Inherent)
    VengeanceIsMine = (0x0166, ItemUpgradeClassType.Inherent)
    DontFearTheReaper = (0x0167, ItemUpgradeClassType.Inherent)
    DanceWithDeath = (0x0168, ItemUpgradeClassType.Inherent)
    BrawnOverBrains = (0x0169, ItemUpgradeClassType.Inherent)
    ToThePain = (0x016A, ItemUpgradeClassType.Inherent)
    IgnoranceIsBliss = (0x01B6, ItemUpgradeClassType.Inherent)
    LifeIsPain = (0x01B7, ItemUpgradeClassType.Inherent)
    ManForAllSeasons = (0x01B8, ItemUpgradeClassType.Inherent)
    SurvivalOfTheFittest = (0x01B9, ItemUpgradeClassType.Inherent)
    MightMakesRight = (0x01BA, ItemUpgradeClassType.Inherent)
    KnowingIsHalfTheBattle = (0x01BB, ItemUpgradeClassType.Inherent)
    FaithIsMyShield = (0x01BC, ItemUpgradeClassType.Inherent)
    DownButNotOut = (0x01BD, ItemUpgradeClassType.Inherent)
    HailToTheKing = (0x01BE, ItemUpgradeClassType.Inherent)
    BeJustAndFearNot = (0x01BF, ItemUpgradeClassType.Inherent)
    LiveForToday = (0x01C0, ItemUpgradeClassType.Inherent)
    SerenityNow = (0x01C1, ItemUpgradeClassType.Inherent)
    ForgetMeNot = (0x01C2, ItemUpgradeClassType.Inherent)
    NotTheFace = (0x01C3, ItemUpgradeClassType.Inherent)
    LeafOnTheWind = (0x01C4, ItemUpgradeClassType.Inherent)
    LikeARollingStone = (0x01C5, ItemUpgradeClassType.Inherent)
    RidersOnTheStorm = (0x01C6, ItemUpgradeClassType.Inherent)
    SleepNowInTheFire = (0x01C7, ItemUpgradeClassType.Inherent)
    ThroughThickAndThin = (0x01C8, ItemUpgradeClassType.Inherent)
    TheRiddleOfSteel = (0x01C9, ItemUpgradeClassType.Inherent)
    FearCutsDeeper = (0x01CA, ItemUpgradeClassType.Inherent)
    ICanSeeClearlyNow = (0x01CB, ItemUpgradeClassType.Inherent)
    SwiftAsTheWind = (0x01CC, ItemUpgradeClassType.Inherent)
    StrengthOfBody = (0x01CD, ItemUpgradeClassType.Inherent)
    CastOutTheUnclean = (0x01CE, ItemUpgradeClassType.Inherent)
    PureOfHeart = (0x01CF, ItemUpgradeClassType.Inherent)
    SoundnessOfMind = (0x01D0, ItemUpgradeClassType.Inherent)
    OnlyTheStrongSurvive = (0x01D1, ItemUpgradeClassType.Inherent)
    LuckOfTheDraw = (0x01D2, ItemUpgradeClassType.Inherent)
    ShelteredByFaith = (0x01D3, ItemUpgradeClassType.Inherent)
    NothingToFear = (0x01D4, ItemUpgradeClassType.Inherent)
    RunForYourLife = (0x01D5, ItemUpgradeClassType.Inherent)
    MasterOfMyDomain = (0x01D6, ItemUpgradeClassType.Inherent)
    AptitudeNotAttitude = (0x01D7, ItemUpgradeClassType.Inherent)
    SeizeTheDay = (0x01D8, ItemUpgradeClassType.Inherent)
    HaveFaith = (0x01D9, ItemUpgradeClassType.Inherent)
    HaleAndHearty = (0x01DA, ItemUpgradeClassType.Inherent)
    DontCallItAComeback = (0x01DB, ItemUpgradeClassType.Inherent)
    IAmSorrow = (0x01DC, ItemUpgradeClassType.Inherent)
    DontThinkTwice = (0x01DD, ItemUpgradeClassType.Inherent)
    ShowMeTheMoney = (0x021E, ItemUpgradeClassType.Inherent)
    MeasureForMeasure = (0x021F, ItemUpgradeClassType.Inherent)
    
    Survivor = (0x01E6, ItemUpgradeClassType.Prefix)
    Radiant = (0x01E5, ItemUpgradeClassType.Prefix)
    Stalwart = (0x01E7, ItemUpgradeClassType.Prefix)
    Brawlers = (0x01E8, ItemUpgradeClassType.Prefix)
    Blessed = (0x01E9, ItemUpgradeClassType.Prefix)
    Heralds = (0x01EA, ItemUpgradeClassType.Prefix)
    Sentrys = (0x01EB, ItemUpgradeClassType.Prefix)
    Knights = (0x01F9, ItemUpgradeClassType.Prefix)
    Lieutenants = (0x0208, ItemUpgradeClassType.Prefix)
    Stonefist = (0x0209, ItemUpgradeClassType.Prefix)
    Dreadnought = (0x01FA, ItemUpgradeClassType.Prefix)
    Sentinels = (0x01FB, ItemUpgradeClassType.Prefix)
    Frostbound = (0x01FC, ItemUpgradeClassType.Prefix)
    Pyrebound = (0x01FE, ItemUpgradeClassType.Prefix)
    Stormbound = (0x01FF, ItemUpgradeClassType.Prefix)
    Scouts = (0x0201, ItemUpgradeClassType.Prefix)
    Earthbound = (0x01FD, ItemUpgradeClassType.Prefix)
    Beastmasters = (0x0200, ItemUpgradeClassType.Prefix)
    Wanderers = (0x01F6, ItemUpgradeClassType.Prefix)
    Disciples = (0x01F7, ItemUpgradeClassType.Prefix)
    Anchorites = (0x01F8, ItemUpgradeClassType.Prefix)
    Bloodstained = (0x020A, ItemUpgradeClassType.Prefix)
    Tormentors = (0x01EC, ItemUpgradeClassType.Prefix)
    Bonelace = (0x01EE, ItemUpgradeClassType.Prefix)
    MinionMasters = (0x01EF, ItemUpgradeClassType.Prefix)
    Blighters = (0x01F0, ItemUpgradeClassType.Prefix)
    Undertakers = (0x01ED, ItemUpgradeClassType.Prefix)
    Virtuosos = (0x01E4, ItemUpgradeClassType.Prefix)
    Artificers = (0x01E2, ItemUpgradeClassType.Prefix)
    Prodigys = (0x01E3, ItemUpgradeClassType.Prefix)
    Hydromancer = (0x01F2, ItemUpgradeClassType.Prefix)
    Geomancer = (0x01F3, ItemUpgradeClassType.Prefix)
    Pyromancer = (0x01F4, ItemUpgradeClassType.Prefix)
    Aeromancer = (0x01F5, ItemUpgradeClassType.Prefix)
    Prismatic = (0x01F1, ItemUpgradeClassType.Prefix)
    Vanguards = (0x01DE, ItemUpgradeClassType.Prefix)
    Infiltrators = (0x01DF, ItemUpgradeClassType.Prefix)
    Saboteurs = (0x01E0, ItemUpgradeClassType.Prefix)
    Nightstalkers = (0x01E1, ItemUpgradeClassType.Prefix)
    Shamans = (0x0204, ItemUpgradeClassType.Prefix)
    GhostForge = (0x0205, ItemUpgradeClassType.Prefix)
    Mystics = (0x0206, ItemUpgradeClassType.Prefix)
    Windwalker = (0x0202, ItemUpgradeClassType.Prefix)
    Forsaken = (0x0203, ItemUpgradeClassType.Prefix)
    Centurions = (0x0207, ItemUpgradeClassType.Prefix)
    
    OfAttunement = (0x0211, ItemUpgradeClassType.Suffix)
    OfRecovery = (0x0213, ItemUpgradeClassType.Suffix)
    OfRestoration = (0x0214, ItemUpgradeClassType.Suffix)
    OfClarity = (0x0215, ItemUpgradeClassType.Suffix)
    OfPurity = (0x0216, ItemUpgradeClassType.Suffix)
    OfMinorVigor = (0x00FF, ItemUpgradeClassType.Suffix)
    OfMinorVigor2 = (0x00C2, ItemUpgradeClassType.Suffix)
    OfSuperiorVigor = (0x0101, ItemUpgradeClassType.Suffix)
    OfMajorVigor = (0x0100, ItemUpgradeClassType.Suffix)
    OfVitae = (0x0212, ItemUpgradeClassType.Suffix)
    OfMinorAbsorption = (0x00FC, ItemUpgradeClassType.Suffix)
    OfMinorTactics = (0x1501, ItemUpgradeClassType.Suffix)
    OfMinorStrength = (0x1101, ItemUpgradeClassType.Suffix)
    OfMinorAxeMastery = (0x1201, ItemUpgradeClassType.Suffix)
    OfMinorHammerMastery = (0x1301, ItemUpgradeClassType.Suffix)
    OfMinorSwordsmanship = (0x1401, ItemUpgradeClassType.Suffix)
    OfMajorAbsorption = (0x00FD, ItemUpgradeClassType.Suffix)
    OfMajorTactics = (0x1502, ItemUpgradeClassType.Suffix)
    OfMajorStrength = (0x1102, ItemUpgradeClassType.Suffix)
    OfMajorAxeMastery = (0x1202, ItemUpgradeClassType.Suffix)
    OfMajorHammerMastery = (0x1302, ItemUpgradeClassType.Suffix)
    OfMajorSwordsmanship = (0x1402, ItemUpgradeClassType.Suffix)
    OfSuperiorAbsorption = (0x00FE, ItemUpgradeClassType.Suffix)
    OfSuperiorTactics = (0x1503, ItemUpgradeClassType.Suffix)
    OfSuperiorStrength = (0x1103, ItemUpgradeClassType.Suffix)
    OfSuperiorAxeMastery = (0x1203, ItemUpgradeClassType.Suffix)
    OfSuperiorHammerMastery = (0x1303, ItemUpgradeClassType.Suffix)
    OfSuperiorSwordsmanship = (0x1403, ItemUpgradeClassType.Suffix)
    OfMinorWildernessSurvival = (0x1801, ItemUpgradeClassType.Suffix)
    OfMinorExpertise = (0x1701, ItemUpgradeClassType.Suffix)
    OfMinorBeastMastery = (0x1601, ItemUpgradeClassType.Suffix)
    OfMinorMarksmanship = (0x1901, ItemUpgradeClassType.Suffix)
    OfMajorWildernessSurvival = (0x1802, ItemUpgradeClassType.Suffix)
    OfMajorExpertise = (0x1702, ItemUpgradeClassType.Suffix)
    OfMajorBeastMastery = (0x1602, ItemUpgradeClassType.Suffix)
    OfMajorMarksmanship = (0x1902, ItemUpgradeClassType.Suffix)
    OfSuperiorWildernessSurvival = (0x1803, ItemUpgradeClassType.Suffix)
    OfSuperiorExpertise = (0x1703, ItemUpgradeClassType.Suffix)
    OfSuperiorBeastMastery = (0x1603, ItemUpgradeClassType.Suffix)
    OfSuperiorMarksmanship = (0x1903, ItemUpgradeClassType.Suffix)
    OfMinorHealingPrayers = (0x0D01, ItemUpgradeClassType.Suffix)
    OfMinorSmitingPrayers = (0x0E01, ItemUpgradeClassType.Suffix)
    OfMinorProtectionPrayers = (0x0F01, ItemUpgradeClassType.Suffix)
    OfMinorDivineFavor = (0x1001, ItemUpgradeClassType.Suffix)
    OfMajorHealingPrayers = (0x0D02, ItemUpgradeClassType.Suffix)
    OfMajorSmitingPrayers = (0x0E02, ItemUpgradeClassType.Suffix)
    OfMajorProtectionPrayers = (0x0F02, ItemUpgradeClassType.Suffix)
    OfMajorDivineFavor = (0x1002, ItemUpgradeClassType.Suffix)
    OfSuperiorHealingPrayers = (0x0D03, ItemUpgradeClassType.Suffix)
    OfSuperiorSmitingPrayers = (0x0E03, ItemUpgradeClassType.Suffix)
    OfSuperiorProtectionPrayers = (0x0F03, ItemUpgradeClassType.Suffix)
    OfSuperiorDivineFavor = (0x1003, ItemUpgradeClassType.Suffix)
    OfMinorBloodMagic = (0x0401, ItemUpgradeClassType.Suffix)
    OfMinorDeathMagic = (0x0501, ItemUpgradeClassType.Suffix)
    OfMinorCurses = (0x0701, ItemUpgradeClassType.Suffix)
    OfMinorSoulReaping = (0x0601, ItemUpgradeClassType.Suffix)
    OfMajorBloodMagic = (0x0402, ItemUpgradeClassType.Suffix)
    OfMajorDeathMagic = (0x0502, ItemUpgradeClassType.Suffix)
    OfMajorCurses = (0x0702, ItemUpgradeClassType.Suffix)
    OfMajorSoulReaping = (0x0602, ItemUpgradeClassType.Suffix)
    OfSuperiorBloodMagic = (0x0403, ItemUpgradeClassType.Suffix)
    OfSuperiorDeathMagic = (0x0503, ItemUpgradeClassType.Suffix)
    OfSuperiorCurses = (0x0703, ItemUpgradeClassType.Suffix)
    OfSuperiorSoulReaping = (0x0603, ItemUpgradeClassType.Suffix)
    OfMinorFastCasting = (0x0001, ItemUpgradeClassType.Suffix)
    OfMinorDominationMagic = (0x0201, ItemUpgradeClassType.Suffix)
    OfMinorIllusionMagic = (0x0101, ItemUpgradeClassType.Suffix)
    OfMinorInspirationMagic = (0x0301, ItemUpgradeClassType.Suffix)
    OfMajorFastCasting = (0x0002, ItemUpgradeClassType.Suffix)
    OfMajorDominationMagic = (0x0202, ItemUpgradeClassType.Suffix)
    OfMajorIllusionMagic = (0x0102, ItemUpgradeClassType.Suffix)
    OfMajorInspirationMagic = (0x0302, ItemUpgradeClassType.Suffix)
    OfSuperiorFastCasting = (0x0003, ItemUpgradeClassType.Suffix)
    OfSuperiorDominationMagic = (0x0203, ItemUpgradeClassType.Suffix)
    OfSuperiorIllusionMagic = (0x0103, ItemUpgradeClassType.Suffix)
    OfSuperiorInspirationMagic = (0x0303, ItemUpgradeClassType.Suffix)
    OfMinorEnergyStorage = (0x0C01, ItemUpgradeClassType.Suffix)
    OfMinorFireMagic = (0x0A01, ItemUpgradeClassType.Suffix)
    OfMinorAirMagic = (0x0801, ItemUpgradeClassType.Suffix)
    OfMinorEarthMagic = (0x0901, ItemUpgradeClassType.Suffix)
    OfMinorWaterMagic = (0x0B01, ItemUpgradeClassType.Suffix)
    OfMajorEnergyStorage = (0x0C02, ItemUpgradeClassType.Suffix)
    OfMajorFireMagic = (0x0A02, ItemUpgradeClassType.Suffix)
    OfMajorAirMagic = (0x0802, ItemUpgradeClassType.Suffix)
    OfMajorEarthMagic = (0x0902, ItemUpgradeClassType.Suffix)
    OfMajorWaterMagic = (0x0B02, ItemUpgradeClassType.Suffix)
    OfSuperiorEnergyStorage = (0x0C03, ItemUpgradeClassType.Suffix)
    OfSuperiorFireMagic = (0x0A03, ItemUpgradeClassType.Suffix)
    OfSuperiorAirMagic = (0x0803, ItemUpgradeClassType.Suffix)
    OfSuperiorEarthMagic = (0x0903, ItemUpgradeClassType.Suffix)
    OfSuperiorWaterMagic = (0x0B03, ItemUpgradeClassType.Suffix)
    OfMinorCriticalStrikes = (0x2301, ItemUpgradeClassType.Suffix)
    OfMinorDaggerMastery = (0x1D01, ItemUpgradeClassType.Suffix)
    OfMinorDeadlyArts = (0x1E01, ItemUpgradeClassType.Suffix)
    OfMinorShadowArts = (0x1F01, ItemUpgradeClassType.Suffix)
    OfMajorCriticalStrikes = (0x2302, ItemUpgradeClassType.Suffix)
    OfMajorDaggerMastery = (0x1D02, ItemUpgradeClassType.Suffix)
    OfMajorDeadlyArts = (0x1E02, ItemUpgradeClassType.Suffix)
    OfMajorShadowArts = (0x1F02, ItemUpgradeClassType.Suffix)
    OfSuperiorCriticalStrikes = (0x2303, ItemUpgradeClassType.Suffix)
    OfSuperiorDaggerMastery = (0x1D03, ItemUpgradeClassType.Suffix)
    OfSuperiorDeadlyArts = (0x1E03, ItemUpgradeClassType.Suffix)
    OfSuperiorShadowArts = (0x1F03, ItemUpgradeClassType.Suffix)
    OfMinorChannelingMagic = (0x2201, ItemUpgradeClassType.Suffix)
    OfMinorRestorationMagic = (0x2101, ItemUpgradeClassType.Suffix)
    OfMinorCommuning = (0x2001, ItemUpgradeClassType.Suffix)
    OfMinorSpawningPower = (0x2401, ItemUpgradeClassType.Suffix)
    OfMajorChannelingMagic = (0x2202, ItemUpgradeClassType.Suffix)
    OfMajorRestorationMagic = (0x2102, ItemUpgradeClassType.Suffix)
    OfMajorCommuning = (0x2002, ItemUpgradeClassType.Suffix)
    OfMajorSpawningPower = (0x2402, ItemUpgradeClassType.Suffix)
    OfSuperiorChannelingMagic = (0x2203, ItemUpgradeClassType.Suffix)
    OfSuperiorRestorationMagic = (0x2103, ItemUpgradeClassType.Suffix)
    OfSuperiorCommuning = (0x2003, ItemUpgradeClassType.Suffix)
    OfSuperiorSpawningPower = (0x2403, ItemUpgradeClassType.Suffix)
    OfMinorMysticism = (0x2C01, ItemUpgradeClassType.Suffix)    
    OfMinorEarthPrayers = (0x2B01, ItemUpgradeClassType.Suffix)
    OfMinorScytheMastery = (0x2901, ItemUpgradeClassType.Suffix)
    OfMinorWindPrayers = (0x2A01, ItemUpgradeClassType.Suffix)
    OfMajorMysticism = (0x2C02, ItemUpgradeClassType.Suffix)
    OfMajorEarthPrayers = (0x2B02, ItemUpgradeClassType.Suffix)
    OfMajorScytheMastery = (0x2902, ItemUpgradeClassType.Suffix)
    OfMajorWindPrayers = (0x2A02, ItemUpgradeClassType.Suffix)
    OfSuperiorMysticism = (0x2C03, ItemUpgradeClassType.Suffix)
    OfSuperiorEarthPrayers = (0x2B03, ItemUpgradeClassType.Suffix)
    OfSuperiorScytheMastery = (0x2903, ItemUpgradeClassType.Suffix)
    OfSuperiorWindPrayers = (0x2A03, ItemUpgradeClassType.Suffix)
    OfMinorLeadership = (0x2801, ItemUpgradeClassType.Suffix)
    OfMinorMotivation = (0x2701, ItemUpgradeClassType.Suffix)
    OfMinorCommand = (0x2601, ItemUpgradeClassType.Suffix)
    OfMinorSpearMastery = (0x2501, ItemUpgradeClassType.Suffix)
    OfMajorLeadership = (0x2802, ItemUpgradeClassType.Suffix)
    OfMajorMotivation = (0x2702, ItemUpgradeClassType.Suffix)
    OfMajorCommand = (0x2602, ItemUpgradeClassType.Suffix)
    OfMajorSpearMastery = (0x2502, ItemUpgradeClassType.Suffix)
    OfSuperiorLeadership = (0x2803, ItemUpgradeClassType.Suffix)
    OfSuperiorMotivation = (0x2703, ItemUpgradeClassType.Suffix)
    OfSuperiorCommand = (0x2603, ItemUpgradeClassType.Suffix)
    OfSuperiorSpearMastery = (0x2503, ItemUpgradeClassType.Suffix)
    
    UpgradeMinorRune_Warrior = (0x00B3, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Warrior = (0x0167, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Warrior = (0x00B9, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Warrior = (0x0173, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Warrior = (0x00BF, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Warrior = (0x017F, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Ranger = (0x00B4, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Ranger = (0x0169, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Ranger = (0x00BA, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Ranger = (0x0175, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Ranger = (0x00C0, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Ranger = (0x0181, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Monk = (0x00B2, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Monk = (0x0165, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Monk = (0x00B8, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Monk = (0x0171, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Monk = (0x00BE, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Monk = (0x017D, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Necromancer = (0x00B0, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Necromancer = (0x0161, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Necromancer = (0x00B6, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Necromancer = (0x016D, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Necromancer = (0x00BC, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Necromancer = (0x0179, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Mesmer = (0x00AF, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Mesmer = (0x015F, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Mesmer = (0x00B5, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Mesmer = (0x016B, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Mesmer = (0x00BB, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Mesmer = (0x0177, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Elementalist = (0x00B1, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Elementalist = (0x0163, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Elementalist = (0x00B7, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Elementalist = (0x016F, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Elementalist = (0x00BD, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Elementalist = (0x017B, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Assassin = (0x013B, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Assassin = (0x0277, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Assassin = (0x014C, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Assassin = (0x0279, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Assassin = (0x013D, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Assassin = (0x027B, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Ritualist = (0x013E, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Ritualist = (0x027D, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Ritualist = (0x013F, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Ritualist = (0x027F, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Ritualist = (0x0140, ItemUpgradeClassType.UpgradeRune)  
    AppliesToSuperiorRune_Ritualist = (0x0281, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Dervish = (0x0182, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Dervish = (0x0305, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Dervish = (0x0183, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Dervish = (0x0307, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Dervish = (0x0184, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Dervish = (0x0309, ItemUpgradeClassType.AppliesToRune)
    UpgradeMinorRune_Paragon = (0x0185, ItemUpgradeClassType.UpgradeRune)
    AppliesToMinorRune_Paragon = (0x030B, ItemUpgradeClassType.AppliesToRune)
    UpgradeMajorRune_Paragon = (0x0186, ItemUpgradeClassType.UpgradeRune)
    AppliesToMajorRune_Paragon = (0x030D, ItemUpgradeClassType.AppliesToRune)
    UpgradeSuperiorRune_Paragon = (0x0187, ItemUpgradeClassType.UpgradeRune)
    AppliesToSuperiorRune_Paragon = (0x030F, ItemUpgradeClassType.AppliesToRune)
    
class ItemUpgradeId(Enum):
    Unknown = -1
    Icy_Axe = 0x0081
    Ebon_Axe = 0x0082
    Shocking_Axe = 0x0083
    Fiery_Axe = 0x0084
    Barbed_Axe = 0x0092
    Crippling_Axe = 0x0094
    Cruel_Axe = 0x0096
    Furious_Axe = 0x0099
    Poisonous_Axe = 0x009E
    Heavy_Axe = 0x00A1
    Zealous_Axe = 0x00A3
    Vampiric_Axe = 0x00A7
    Sundering_Axe = 0x00AB
    OfDefense_Axe = 0x00C5
    OfWarding_Axe = 0x00C7
    OfShelter_Axe = 0x00CD
    OfSlaying_Axe = 0x00D4
    OfFortitude_Axe = 0x00D9
    OfEnchanting_Axe = 0x00DE
    OfAxeMastery = 0x00E8
    OfTheProfession_Axe = 0x0226
    Icy_Bow = 0x0085
    Ebon_Bow = 0x0086
    Shocking_Bow = 0x0087
    Fiery_Bow = 0x0088
    Poisonous_Bow = 0x009F
    Zealous_Bow = 0x00A5
    Vampiric_Bow = 0x00A9
    Sundering_Bow = 0x00AD
    OfDefense_Bow = 0x00C6
    OfWarding_Bow = 0x00C8
    OfShelter_Bow = 0x00CE
    OfSlaying_Bow = 0x00D5
    OfFortitude_Bow = 0x00DA
    OfEnchanting_Bow = 0x00DF
    OfMarksmanship = 0x00E9
    Barbed_Bow = 0x0147
    Crippling_Bow = 0x0148
    Silencing_Bow = 0x0149
    OfTheProfession_Bow = 0x0227
    Icy_Daggers = 0x012E
    Ebon_Daggers = 0x012F
    Fiery_Daggers = 0x0130
    Shocking_Daggers = 0x0131
    Zealous_Daggers = 0x0132
    Vampiric_Daggers = 0x0133
    Sundering_Daggers = 0x0134
    Barbed_Daggers = 0x0135
    Crippling_Daggers = 0x0136
    Cruel_Daggers = 0x0137
    Poisonous_Daggers = 0x0138
    Silencing_Daggers = 0x0139
    Furious_Daggers = 0x013A
    OfDefense_Daggers = 0x0141
    OfWarding_Daggers = 0x0142
    OfShelter_Daggers = 0x0143
    OfEnchanting_Daggers = 0x0144
    OfFortitude_Daggers = 0x0145
    OfDaggerMastery = 0x0146
    OfTheProfession_Daggers = 0x0228
    OfAptitude_Focus = 0x0217
    OfFortitude_Focus = 0x0218
    OfDevotion_Focus = 0x0219
    OfValor_Focus = 0x021A
    OfEndurance_Focus = 0x021B
    OfSwiftness_Focus = 0x021C
    Icy_Hammer = 0x0089
    Ebon_Hammer = 0x008A
    Shocking_Hammer = 0x008B
    Fiery_Hammer = 0x008C
    Cruel_Hammer = 0x0097
    Furious_Hammer = 0x009A
    Heavy_Hammer = 0x00A2
    Zealous_Hammer = 0x00A4
    Vampiric_Hammer = 0x00A8
    Sundering_Hammer = 0x00AC
    OfWarding_Hammer = 0x00C9
    OfDefense_Hammer = 0x00CC
    OfShelter_Hammer = 0x00CF
    OfSlaying_Hammer = 0x00D6
    OfFortitude_Hammer = 0x00DB
    OfEnchanting_Hammer = 0x00E0
    OfHammerMastery = 0x00EA
    OfTheProfession_Hammer = 0x0229
    
    IHaveThePower = 0x015C
    LetTheMemoryLiveAgain = 0x015E
    TooMuchInformation = 0x0163
    GuidedByFate = 0x0164
    StrengthAndHonor = 0x0165
    VengeanceIsMine = 0x0166
    DontFearTheReaper = 0x0167
    DanceWithDeath = 0x0168
    BrawnOverBrains = 0x0169
    ToThePain = 0x016A
    IgnoranceIsBliss = 0x01B6
    LifeIsPain = 0x01B7
    ManForAllSeasons = 0x01B8
    SurvivalOfTheFittest = 0x01B9
    MightMakesRight = 0x01BA
    KnowingIsHalfTheBattle = 0x01BB
    FaithIsMyShield = 0x01BC
    DownButNotOut = 0x01BD
    HailToTheKing = 0x01BE
    BeJustAndFearNot = 0x01BF
    LiveForToday = 0x01C0
    SerenityNow = 0x01C1
    ForgetMeNot = 0x01C2
    NotTheFace = 0x01C3
    LeafOnTheWind = 0x01C4
    LikeARollingStone = 0x01C5
    RidersOnTheStorm = 0x01C6
    SleepNowInTheFire = 0x01C7
    ThroughThickAndThin = 0x01C8
    TheRiddleOfSteel = 0x01C9
    FearCutsDeeper = 0x01CA
    ICanSeeClearlyNow = 0x01CB
    SwiftAsTheWind = 0x01CC
    StrengthOfBody = 0x01CD
    CastOutTheUnclean = 0x01CE
    PureOfHeart = 0x01CF
    SoundnessOfMind = 0x01D0
    OnlyTheStrongSurvive = 0x01D1
    LuckOfTheDraw = 0x01D2
    ShelteredByFaith = 0x01D3
    NothingToFear = 0x01D4
    RunForYourLife = 0x01D5
    MasterOfMyDomain = 0x01D6
    AptitudeNotAttitude = 0x01D7
    SeizeTheDay = 0x01D8
    HaveFaith = 0x01D9
    HaleAndHearty = 0x01DA
    DontCallItAComeback = 0x01DB
    IAmSorrow = 0x01DC
    DontThinkTwice = 0x01DD
    ShowMeTheMoney = 0x021E
    MeasureForMeasure = 0x021F
    
    Icy_Scythe = 0x016B
    Ebon_Scythe = 0x016C
    Zealous_Scythe = 0x016F
    Vampiric_Scythe = 0x0171
    Sundering_Scythe = 0x0173
    Barbed_Scythe = 0x0174
    Crippling_Scythe = 0x0175
    Cruel_Scythe = 0x0176
    Poisonous_Scythe = 0x0177
    Heavy_Scythe = 0x0178
    Furious_Scythe = 0x0179
    OfDefense_Scythe = 0x0188
    OfWarding_Scythe = 0x0189
    OfShelter_Scythe = 0x018A
    OfEnchanting_Scythe = 0x018B
    OfFortitude_Scythe = 0x018C
    OfScytheMastery = 0x018D
    Fiery_Scythe = 0x020B
    Shocking_Scythe = 0x020C
    OfTheProfession_Scythe = 0x022C
    OfValor_Shield = 0x0151
    OfEndurance_Shield = 0x0152
    OfFortitude_Shield = 0x0161
    OfDevotion_Shield = 0x0162
    Fiery_Spear = 0x016D
    Shocking_Spear = 0x016E
    Zealous_Spear = 0x0170
    Vampiric_Spear = 0x0172
    Sundering_Spear = 0x017A
    Barbed_Spear = 0x017B
    Crippling_Spear = 0x017C
    Cruel_Spear = 0x017D
    Poisonous_Spear = 0x017E
    Silencing_Spear = 0x017F
    Furious_Spear = 0x0180
    Heavy_Spear = 0x0181
    OfDefense_Spear = 0x018E
    OfWarding_Spear = 0x018F
    OfShelter_Spear = 0x0190
    OfEnchanting_Spear = 0x0191
    OfFortitude_Spear = 0x0192
    OfSpearMastery = 0x0193
    Icy_Spear = 0x020D
    Ebon_Spear = 0x020E
    OfTheProfession_Spear = 0x022D
    
    Defensive_Staff = 0x0091
    Insightful_Staff = 0x009C
    Hale_Staff = 0x009D
    OfAttribute_Staff = 0x00C3
    OfWarding_Staff = 0x00CA
    OfShelter_Staff = 0x00D0
    OfDefense_Staff = 0x00D2
    OfSlaying_Staff = 0x00D7
    OfFortitude_Staff = 0x00DC
    OfEnchanting_Staff = 0x00E1
    OfMastery_Staff = 0x0153
    OfDevotion_Staff = 0x0154
    OfValor_Staff = 0x0155
    OfEndurance_Staff = 0x0156
    Swift_Staff = 0x020F
    Adept_Staff = 0x0210
    OfTheProfession_Staff = 0x022B
    Icy_Sword = 0x008D
    Ebon_Sword = 0x008E
    Shocking_Sword = 0x008F
    Fiery_Sword = 0x0090
    Barbed_Sword = 0x0093
    Crippling_Sword = 0x0095
    Cruel_Sword = 0x0098
    Furious_Sword = 0x009B
    Poisonous_Sword = 0x00A0
    Zealous_Sword = 0x00A6
    Vampiric_Sword = 0x00AA
    Sundering_Sword = 0x00AE
    OfWarding_Sword = 0x00CB
    OfShelter_Sword = 0x00D1
    OfDefense_Sword = 0x00D3
    OfSlaying_Sword = 0x00D8
    OfFortitude_Sword = 0x00DD
    OfEnchanting_Sword = 0x00E2
    OfSwordsmanship = 0x00EB
    OfTheProfession_Sword = 0x022E
    OfMemory_Wand = 0x015F
    OfQuickening_Wand = 0x0160
    OfTheProfession_Wand = 0x022A
    
    Survivor = 0x01E6
    Radiant = 0x01E5
    Stalwart = 0x01E7
    Brawlers = 0x01E8
    Blessed = 0x01E9
    Heralds = 0x01EA
    Sentrys = 0x01EB
    Knights = 0x01F9
    Lieutenants = 0x0208
    Stonefist = 0x0209
    Dreadnought = 0x01FA
    Sentinels = 0x01FB
    Frostbound = 0x01FC
    Pyrebound = 0x01FE
    Stormbound = 0x01FF
    Scouts = 0x0201
    Earthbound = 0x01FD
    Beastmasters = 0x0200
    Wanderers = 0x01F6
    Disciples = 0x01F7
    Anchorites = 0x01F8
    Bloodstained = 0x020A
    Tormentors = 0x01EC
    Bonelace = 0x01EE
    MinionMasters = 0x01EF
    Blighters = 0x01F0
    Undertakers = 0x01ED
    Virtuosos = 0x01E4
    Artificers = 0x01E2
    Prodigys = 0x01E3
    Hydromancer = 0x01F2
    Geomancer = 0x01F3
    Pyromancer = 0x01F4
    Aeromancer = 0x01F5
    Prismatic = 0x01F1
    Vanguards = 0x01DE
    Infiltrators = 0x01DF
    Saboteurs = 0x01E0
    Nightstalkers = 0x01E1
    Shamans = 0x0204
    GhostForge = 0x0205
    Mystics = 0x0206
    Windwalker = 0x0202
    Forsaken = 0x0203
    Centurions = 0x0207
    
    OfAttunement = 0x0211
    OfRecovery = 0x0213
    OfRestoration = 0x0214
    OfClarity = 0x0215
    OfPurity = 0x0216
    OfMinorVigor = 0x00FF
    OfMinorVigor2 = 0x00C2
    OfSuperiorVigor = 0x0101
    OfMajorVigor = 0x0100
    OfVitae = 0x0212
    OfMinorAbsorption = 0x00FC
    OfMinorTactics = 0x1501
    OfMinorStrength = 0x1101
    OfMinorAxeMastery = 0x1201
    OfMinorHammerMastery = 0x1301
    OfMinorSwordsmanship = 0x1401
    OfMajorAbsorption = 0x00FD
    OfMajorTactics = 0x1502
    OfMajorStrength = 0x1102
    OfMajorAxeMastery = 0x1202
    OfMajorHammerMastery = 0x1302
    OfMajorSwordsmanship = 0x1402
    OfSuperiorAbsorption = 0x00FE
    OfSuperiorTactics = 0x1503
    OfSuperiorStrength = 0x1103
    OfSuperiorAxeMastery = 0x1203
    OfSuperiorHammerMastery = 0x1303
    OfSuperiorSwordsmanship = 0x1403
    OfMinorWildernessSurvival = 0x1801
    OfMinorExpertise = 0x1701
    OfMinorBeastMastery = 0x1601
    OfMinorMarksmanship = 0x1901
    OfMajorWildernessSurvival = 0x1802
    OfMajorExpertise = 0x1702
    OfMajorBeastMastery = 0x1602
    OfMajorMarksmanship = 0x1902
    OfSuperiorWildernessSurvival = 0x1803
    OfSuperiorExpertise = 0x1703
    OfSuperiorBeastMastery = 0x1603
    OfSuperiorMarksmanship = 0x1903
    OfMinorHealingPrayers = 0x0D01
    OfMinorSmitingPrayers = 0x0E01
    OfMinorProtectionPrayers = 0x0F01
    OfMinorDivineFavor = 0x1001
    OfMajorHealingPrayers = 0x0D02
    OfMajorSmitingPrayers = 0x0E02
    OfMajorProtectionPrayers = 0x0F02
    OfMajorDivineFavor = 0x1002
    OfSuperiorHealingPrayers = 0x0D03
    OfSuperiorSmitingPrayers = 0x0E03
    OfSuperiorProtectionPrayers = 0x0F03
    OfSuperiorDivineFavor = 0x1003
    OfMinorBloodMagic = 0x0401
    OfMinorDeathMagic = 0x0501
    OfMinorCurses = 0x0701
    OfMinorSoulReaping = 0x0601
    OfMajorBloodMagic = 0x0402
    OfMajorDeathMagic = 0x0502
    OfMajorCurses = 0x0702
    OfMajorSoulReaping = 0x0602
    OfSuperiorBloodMagic = 0x0403
    OfSuperiorDeathMagic = 0x0503
    OfSuperiorCurses = 0x0703
    OfSuperiorSoulReaping = 0x0603
    OfMinorFastCasting = 0x0001
    OfMinorDominationMagic = 0x0201
    OfMinorIllusionMagic = 0x0101
    OfMinorInspirationMagic = 0x0301
    OfMajorFastCasting = 0x0002
    OfMajorDominationMagic = 0x0202
    OfMajorIllusionMagic = 0x0102
    OfMajorInspirationMagic = 0x0302
    OfSuperiorFastCasting = 0x0003
    OfSuperiorDominationMagic = 0x0203
    OfSuperiorIllusionMagic = 0x0103
    OfSuperiorInspirationMagic = 0x0303
    OfMinorEnergyStorage = 0x0C01
    OfMinorFireMagic = 0x0A01
    OfMinorAirMagic = 0x0801
    OfMinorEarthMagic = 0x0901
    OfMinorWaterMagic = 0x0B01
    OfMajorEnergyStorage = 0x0C02
    OfMajorFireMagic = 0x0A02
    OfMajorAirMagic = 0x0802
    OfMajorEarthMagic = 0x0902
    OfMajorWaterMagic = 0x0B02
    OfSuperiorEnergyStorage = 0x0C03
    OfSuperiorFireMagic = 0x0A03
    OfSuperiorAirMagic = 0x0803
    OfSuperiorEarthMagic = 0x0903
    OfSuperiorWaterMagic = 0x0B03
    OfMinorCriticalStrikes = 0x2301
    OfMinorDaggerMastery = 0x1D01
    OfMinorDeadlyArts = 0x1E01
    OfMinorShadowArts = 0x1F01
    OfMajorCriticalStrikes = 0x2302
    OfMajorDaggerMastery = 0x1D02
    OfMajorDeadlyArts = 0x1E02
    OfMajorShadowArts = 0x1F02
    OfSuperiorCriticalStrikes = 0x2303
    OfSuperiorDaggerMastery = 0x1D03
    OfSuperiorDeadlyArts = 0x1E03
    OfSuperiorShadowArts = 0x1F03
    OfMinorChannelingMagic = 0x2201
    OfMinorRestorationMagic = 0x2101
    OfMinorCommuning = 0x2001
    OfMinorSpawningPower = 0x2401
    OfMajorChannelingMagic = 0x2202
    OfMajorRestorationMagic = 0x2102
    OfMajorCommuning = 0x2002
    OfMajorSpawningPower = 0x2402
    OfSuperiorChannelingMagic = 0x2203
    OfSuperiorRestorationMagic = 0x2103
    OfSuperiorCommuning = 0x2003
    OfSuperiorSpawningPower = 0x2403
    OfMinorMysticism = 0x2C01
    OfMinorEarthPrayers = 0x2B01
    OfMinorScytheMastery = 0x2901
    OfMinorWindPrayers = 0x2A01
    OfMajorMysticism = 0x2C02
    OfMajorEarthPrayers = 0x2B02
    OfMajorScytheMastery = 0x2902
    OfMajorWindPrayers = 0x2A02
    OfSuperiorMysticism = 0x2C03
    OfSuperiorEarthPrayers = 0x2B03
    OfSuperiorScytheMastery = 0x2903
    OfSuperiorWindPrayers = 0x2A03
    OfMinorLeadership = 0x2801
    OfMinorMotivation = 0x2701
    OfMinorCommand = 0x2601
    OfMinorSpearMastery = 0x2501
    OfMajorLeadership = 0x2802
    OfMajorMotivation = 0x2702
    OfMajorCommand = 0x2602
    OfMajorSpearMastery = 0x2502
    OfSuperiorLeadership = 0x2803
    OfSuperiorMotivation = 0x2703
    OfSuperiorCommand = 0x2603
    OfSuperiorSpearMastery = 0x2503
    
    UpgradeMinorRune_Warrior = 0x00B3
    AppliesToMinorRune_Warrior = 0x0167
    UpgradeMajorRune_Warrior = 0x00B9
    AppliesToMajorRune_Warrior = 0x0173
    UpgradeSuperiorRune_Warrior = 0x00BF
    AppliesToSuperiorRune_Warrior = 0x017F
    UpgradeMinorRune_Ranger = 0x00B4
    AppliesToMinorRune_Ranger = 0x0169
    UpgradeMajorRune_Ranger = 0x00BA
    AppliesToMajorRune_Ranger = 0x0175
    UpgradeSuperiorRune_Ranger = 0x00C0
    AppliesToSuperiorRune_Ranger = 0x0181
    UpgradeMinorRune_Monk = 0x00B2
    AppliesToMinorRune_Monk = 0x0165
    UpgradeMajorRune_Monk = 0x00B8
    AppliesToMajorRune_Monk = 0x0171
    UpgradeSuperiorRune_Monk = 0x00BE
    AppliesToSuperiorRune_Monk = 0x017D
    UpgradeMinorRune_Necromancer = 0x00B0
    AppliesToMinorRune_Necromancer = 0x0161
    UpgradeMajorRune_Necromancer = 0x00B6
    AppliesToMajorRune_Necromancer = 0x016D
    UpgradeSuperiorRune_Necromancer = 0x00BC
    AppliesToSuperiorRune_Necromancer = 0x0179
    UpgradeMinorRune_Mesmer = 0x00AF
    AppliesToMinorRune_Mesmer = 0x015F
    UpgradeMajorRune_Mesmer = 0x00B5
    AppliesToMajorRune_Mesmer = 0x016B
    UpgradeSuperiorRune_Mesmer = 0x00BB
    AppliesToSuperiorRune_Mesmer = 0x0177
    UpgradeMinorRune_Elementalist = 0x00B1
    AppliesToMinorRune_Elementalist = 0x0163
    UpgradeMajorRune_Elementalist = 0x00B7
    AppliesToMajorRune_Elementalist = 0x016F
    UpgradeSuperiorRune_Elementalist = 0x00BD
    AppliesToSuperiorRune_Elementalist = 0x017B
    UpgradeMinorRune_Assassin = 0x013B
    AppliesToMinorRune_Assassin = 0x0277
    UpgradeMajorRune_Assassin = 0x014C
    AppliesToMajorRune_Assassin = 0x0279
    UpgradeSuperiorRune_Assassin = 0x013D
    AppliesToSuperiorRune_Assassin = 0x027B
    UpgradeMinorRune_Ritualist = 0x013E
    AppliesToMinorRune_Ritualist = 0x027D
    UpgradeMajorRune_Ritualist = 0x013F
    AppliesToMajorRune_Ritualist = 0x027F
    UpgradeSuperiorRune_Ritualist = 0x0140
    AppliesToSuperiorRune_Ritualist = 0x0281
    UpgradeMinorRune_Dervish = 0x0182
    AppliesToMinorRune_Dervish = 0x0305
    UpgradeMajorRune_Dervish = 0x0183
    AppliesToMajorRune_Dervish = 0x0307
    UpgradeSuperiorRune_Dervish = 0x0184
    AppliesToSuperiorRune_Dervish = 0x0309
    UpgradeMinorRune_Paragon = 0x0185
    AppliesToMinorRune_Paragon = 0x030B
    UpgradeMajorRune_Paragon = 0x0186
    AppliesToMajorRune_Paragon = 0x030D
    UpgradeSuperiorRune_Paragon = 0x0187
    AppliesToSuperiorRune_Paragon = 0x030F