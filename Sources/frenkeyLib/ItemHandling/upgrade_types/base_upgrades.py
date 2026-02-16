from dataclasses import dataclass

from Sources.frenkeyLib.ItemHandling.upgrades import ItemUpgradeClassType


@dataclass
class ItemUpgrade:
    upgrade_type : ItemUpgradeClassType
    pass

class Prefix(ItemUpgrade):
    upgrade_type = ItemUpgradeClassType.Prefix
    pass

class Suffix(ItemUpgrade):
    upgrade_type = ItemUpgradeClassType.Suffix
    pass
