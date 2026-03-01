from Py4GWCoreLib.Item import Item
from Sources.frenkeyLib.ItemHandling.item_modifier_parser import ItemModifierParser
from Sources.frenkeyLib.ItemHandling.item_properties import InscriptionProperty, PrefixProperty, SuffixProperty, Upgrade
from Sources.frenkeyLib.ItemHandling.types import ItemUpgradeType


class ItemMod:
    @staticmethod
    def get_item_upgrades(item_id : int) -> tuple[Upgrade | None, Upgrade | None, Upgrade | None]:
        runtime_modifiers = Item.Customization.Modifiers.GetModifiers(item_id)
        parser = ItemModifierParser(runtime_modifiers)
        properties = parser.get_properties()
        
        prefix = next((p for p in properties if isinstance(p, PrefixProperty) and p.upgrade.mod_type == ItemUpgradeType.Prefix), None)
        suffix = next((s for s in properties if isinstance(s, SuffixProperty) and s.upgrade.mod_type == ItemUpgradeType.Suffix), None)
        inscription = next((i for i in properties if isinstance(i, InscriptionProperty) and i.upgrade.mod_type == ItemUpgradeType.Inscription), None)

        return prefix.upgrade if prefix else None, suffix.upgrade if suffix else None, inscription.upgrade if inscription else None