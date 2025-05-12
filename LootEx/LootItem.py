from LootEx.Data import IntRange
from LootEx.ItemAction import ItemActions, LootItemMode
from Py4GWCoreLib import *
    
class LootItemConditionedActions:
    def __init__(self, name: str = "New Condition"):
        self.Name : str = name
        self.ItemType : Optional[ItemType] = None
        self.DamageRange : Optional[IntRange] = None
        self.Requirements : Optional[dict[Attribute, IntRange]] = None

        self.PrefixMod : Optional[str] = None
        self.SuffixMod : Optional[str] = None
        self.InherentMod : Optional[str] = None
        self.OldSchoolOnly = False

        self.Rarities = {}
        for rarity in Rarity:
            self.Rarities[rarity] = False

        self.ItemActions : ItemActions = ItemActions()

class LootItem:
    def __init__(self, model_id : ModelID):
        self.ModelId : ModelID = model_id
        default_condition = LootItemConditionedActions("Default")

        self.Conditions : list[LootItemConditionedActions] = [default_condition]        

@staticmethod
def to_dict(data) -> dict:
    return {
        "ModelId": data.ModelId.name if data.ModelId else None,
        "Conditions": [
            {
                "Name": condition.Name,
                "ItemType": condition.ItemType.name if condition.ItemType else None,
                "DamageRange": (condition.DamageRange.Min, condition.DamageRange.Max) if condition.DamageRange else None,
                "PrefixMod": condition.PrefixMod,
                "SuffixMod": condition.SuffixMod,
                "InherentMod": condition.InherentMod,
                "OldSchoolOnly": condition.OldSchoolOnly,
                "Rarities": {rarity.name: value for rarity, value in condition.Rarities.items()},
                "ItemActions": ItemActions.to_dict(condition.ItemActions),
                "Requirements": {attribute.name: (requirement.Min, requirement.Max) for attribute, requirement in condition.Requirements.items()} if condition.Requirements else None

            }
            for condition in data.Conditions
        ]
    }

@staticmethod
def from_dict(data) -> LootItem:
    model_id = ModelID[data["ModelId"]] if data["ModelId"] in ModelID.__members__ else None

    if model_id is None:
        raise ValueError(f"Invalid ModelId: {data['ModelId']}")
    
    item = LootItem(model_id)
    item.Conditions = []

    for condition_data in data["Conditions"]:
        condition = LootItemConditionedActions(condition_data["Name"])
        condition.ItemType = ItemType[condition_data["ItemType"]] if condition_data["ItemType"] in ItemType.__members__ else None
        condition.DamageRange = IntRange(condition_data["DamageRange"][0], condition_data["DamageRange"][1]) if condition_data["DamageRange"] else None
        condition.PrefixMod = condition_data["PrefixMod"]
        condition.SuffixMod = condition_data["SuffixMod"]
        condition.InherentMod = condition_data["InherentMod"]
        condition.OldSchoolOnly = condition_data["OldSchoolOnly"]
        condition.Rarities = {Rarity[rarity]: value for rarity, value in condition_data["Rarities"].items() if rarity in Rarity.__members__}
        condition.ItemActions = ItemActions.from_dict(condition_data["ItemActions"])

        condition.Requirements = {
            Attribute[attribute]: IntRange(requirement[0], requirement[1])
            for attribute, requirement in condition_data["Requirements"].items()
            if attribute in Attribute.__members__
        } if condition_data["Requirements"] else None

        
        item.Conditions.append(condition)        
    return item
