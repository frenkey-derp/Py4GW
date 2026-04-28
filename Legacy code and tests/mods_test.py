
from PyItem import PyItem

from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Item
from Py4GWCoreLib.item_mods_src.upgrades import *

from Py4GWCoreLib.native_src.internals.encoded_strings import GWStringEncoded
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer

throttle = ThrottledTimer(500)  # 1 second throttle

def main():
    if not throttle.IsExpired():
        return
    
    throttle.Reset()
    
    try:
        item_id = Inventory.GetHoveredItemID()
        if item_id is not None and item_id > 0:
            item_name_enc = GWStringEncoded(bytes(PyItem.GetCompleteNameEnc(item_id)) or bytes(), "Unknown Item")
            item_name = item_name_enc.plain
            print(f"Currently hovered item: '{item_name}' ({item_id})")
        
            if Item.Customization.HasUpgradeType(item_id, OfFortitudeUpgrade):
                print(f"Item '{item_name}' ({item_id}) has a fortitude upgrade.")
                
                if (fortitude_upgrade := Item.Customization.GetUpgrade(item_id, OfFortitudeUpgrade)) is not None:
                    print(f"Item '{item_name}' ({item_id}) has a fortitude upgrade ({fortitude_upgrade.health} health).")
                    
            
            if (fortitude_upgrade := Item.Customization.GetUpgrade(item_id, OfFortitudeUpgrade(health=29))) is not None:
                print(f"Item '{item_name}' ({item_id}) has a specific fortitude upgrade ({fortitude_upgrade.health} health).")
                
            prefix, suffix, inscription, inherents = Item.Customization.GetUpgrades(item_id)
            upgrades_dic = {"prefix": prefix, "suffix": suffix, "inscription": inscription, "inherents": (inherents or [])}
            upgrades = [prefix, suffix, inscription] + (inherents or [])

            for upgrade_type, upgrade in upgrades_dic.items():
                if upgrade is not None:
                    if isinstance(upgrade, list):
                        for u in upgrade:
                            print(f"Item '{item_name}' ({item_id}) has an {upgrade_type} upgrade: {u.display_summary}.")
                    else:
                        print(f"Item '{item_name}' ({item_id}) has an {upgrade_type} upgrade: {upgrade.display_summary}.")

            desired_upgrade = OfFortitudeUpgrade(health=29)
            if Item.Customization.HasUpgrade(item_id, desired_upgrade):
                print(f"Item '{item_name}' ({item_id}) has the desired upgrade: {desired_upgrade.display_summary}.")
            else:
                print(f"Item '{item_name}' ({item_id}) does not have the desired upgrade: {desired_upgrade.display_summary}.")
                
            for upgrade in upgrades:
                if upgrade and upgrade.matches(desired_upgrade):
                    break
            
    except Exception as e:
        print(f"An error occurred while evaluating the hovered item: {e}")
        
if __name__ == "__main__":
    main()