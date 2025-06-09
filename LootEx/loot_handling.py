from datetime import date
from LootEx.enum import SalvageKitOption, SalvageOption, ItemAction
from Py4GWCoreLib import *
from LootEx import data, data_collector, models, settings, utility, ui_manager_extensions, loot_filter

import importlib

importlib.reload(loot_filter)
importlib.reload(settings)
importlib.reload(ui_manager_extensions)

# self.skillbar_action_queue = ActionQueueNode(100)

salvaged = False
deposited = False
capacity_checked = False
material_capacity = 2500

salvage_timer = ThrottledTimer(750)
identification_timer = ThrottledTimer(500)
merchant_timer = ThrottledTimer(1000)
deposit_timer = ThrottledTimer(5000)
inventory_timer = ThrottledTimer(5000)
compact_inventory_timer = ThrottledTimer(250)
indentify_action_queue = ActionQueueNode(250)
salvage_action_queue = ActionQueueNode(150)
merchant_action_queue = ActionQueueNode(750)
queued_items : dict[int, datetime] = {}

salvage_requires_confirmation = False

#TODO: Collect salvage data for items, so we can make better decisions on what to salvage and what not to salvage.

#region Reworked
def IdentifyItems() -> bool:    
    identified_items = False
    id_kit = Inventory.GetFirstIDKit()
    
    if id_kit != 0:        
        remaining_uses = GLOBAL_CACHE.Item.Usage.GetUses(id_kit)
        
        item_array = GLOBAL_CACHE.ItemArray.GetItemArray(
                [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2, Bag.Equipment_Pack])
            
        for item_id in item_array:        
            if not ShouldIdentifyItem(item_id):
                continue   
            
            if remaining_uses > 0:
                remaining_uses -= 1
                identified_items = True
                ConsoleLog("LootEx", f"Identifying item: '{utility.Util.GetItemDataName(item_id)}' {item_id} using kit {utility.Util.GetItemDataName(id_kit)} {id_kit}", Console.MessageType.Info)
                Inventory.IdentifyItem(item_id, id_kit)                   
            
    return identified_items

def ShouldIdentifyItem(item_id) -> bool:
    if not GLOBAL_CACHE.Item.Usage.IsIdentified(item_id):        
        item_type = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])
        
        if utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type): 
            rarity = Rarity(GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)[0])
            value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
                       
            if rarity > Rarity.White or value >= 25:
                return True

    return False

def DepositMaterials(force : bool = False) -> bool:
    global deposited, capacity_checked, material_capacity
    
    if not deposited or force:        
        items : list[int] = GLOBAL_CACHE.ItemArray.GetItemArray(
            [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2])

        items : list[int] = ItemArray.Filter.ByCondition(
            items, lambda item_id: GLOBAL_CACHE.Item.GetItemType(item_id)[0] == ItemType.Materials_Zcoins.value)
        
        material_storage = GLOBAL_CACHE.ItemArray.GetItemArray(
            [Bag.Material_Storage])
        
        model_ids = [GLOBAL_CACHE.Item.GetModelID(i) for i in items]
        
        ## filter the material_storage items to only include those which share the same model_id as the items in the inventory
        material_storage = ItemArray.Filter.ByCondition(
            material_storage, 
            lambda item_id: GLOBAL_CACHE.Item.GetModelID(item_id) in model_ids
        )
        
        deposited = True
        
        for item_id in items:
            model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
            
            if model_id:
                material_storage_item = next(
                    (item_id for item_id in material_storage if GLOBAL_CACHE.Item.GetModelID(item_id) == model_id), None)
                
                max_move_amount = material_capacity - GLOBAL_CACHE.Item.Properties.GetQuantity(material_storage_item) if material_storage_item else material_capacity
                move_amount = min(max_move_amount, GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))
                
                if move_amount <= 0:
                    continue
                
                material_data = data.Materials.get(model_id, None)
                if material_data:
                    ConsoleLog("LootEx", f"Depositing item {move_amount}x '{material_data.name}' ({item_id}) to material storage.", Console.MessageType.Info)
                    Inventory.MoveItem(item_id, Bags.MaterialStorage, material_data.material_storage_slot, move_amount)                    
                    
        return True
                
    elif not capacity_checked:
        ConsoleLog("LootEx", "Checking material storage capacity", Console.MessageType.Info)
        
        material_storage = GLOBAL_CACHE.ItemArray.GetItemArray(
            [Bag.Material_Storage])
        
        max_quantity = max([GLOBAL_CACHE.Item.Properties.GetQuantity(item_id) for item_id in material_storage])
        
        ## calculate the estimated capacity based on the max quantity by rounding it up to the nearest 250 if it is not already a multiple of 250
        
        estimated_capacity = (max_quantity // 250) * 250
        if max_quantity % 250 != 0:
            ## if it is not a multiple of 250, add 250 to the estimated capacity
            ## this ensures that the material storage capacity is always a multiple of 250
            estimated_capacity += 250
        ConsoleLog("LootEx", f"Estimated material storage capacity: {estimated_capacity}", Console.MessageType.Info)

        
        if estimated_capacity != material_capacity:
            material_capacity = estimated_capacity
            ConsoleLog("LootEx", f"Material storage capacity set to {material_capacity}", Console.MessageType.Info)
                 
        capacity_checked = True
    else:
        deposited = False   
        
                        
    return False

def GetSalvageOption(item_id: int, action : ItemAction) -> Optional[SalvageOption]:
    model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
    item_info = data.Items.get(model_id, None)
    
    if action == ItemAction.SALVAGE_SMART:
        if item_info is None:
            return None
        
        if item_info is not None:
            mods = utility.Util.GetMods(item_id)
            is_highly_salvageable = any(mod.identifier == "AQAmCAAeKA==" for mod in mods) if mods else False 
            value = GLOBAL_CACHE.Item.Properties.GetValue(item_id)
                            
            common_salvage = (item_info.common_salvage.get_average_value(is_highly_salvageable) if item_info.common_salvage else 0) - 4
            rare_salvage = ((item_info.rare_salvage.get_average_value(is_highly_salvageable) if item_info.rare_salvage else 0) + common_salvage)  - 12                
            rare_salvage = rare_salvage / max(1, len(item_info.rare_salvage) + len(item_info.common_salvage))
            
            multiplier = 1.5
            # if value >= rare_salvage * multiplier and value >= common_salvage * multiplier:
            #     return None
            # else:
            return SalvageOption.LesserCraftingMaterials if common_salvage > rare_salvage else SalvageOption.RareCraftingMaterials
    else:
        match action:
            case ItemAction.SALVAGE_COMMON_MATERIALS:
                return SalvageOption.LesserCraftingMaterials
            
            case ItemAction.SALVAGE_RARE_MATERIALS:
                return SalvageOption.RareCraftingMaterials    
            
            case ItemAction.SALVAGE_MODS:
                return SalvageOption.Inherent            

def ShouldSalvageItem(item_id: int) -> tuple[bool, ItemAction]:                
    if GLOBAL_CACHE.Item.Usage.IsSalvageable(item_id) and settings.current.loot_profile:   
        model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
        
        item_config = settings.current.loot_profile.items.get(model_id, None)
        if item_config:
            action = item_config.get_action(item_id)

            if action != ItemAction.NONE:
                return action == ItemAction.SALVAGE or action == ItemAction.SALVAGE_SMART or action == ItemAction.SALVAGE_COMMON_MATERIALS or action == ItemAction.SALVAGE_RARE_MATERIALS or action == ItemAction.SALVAGE_SMART, action
            
        for filter in settings.current.loot_profile.filters:
            action = filter.get_action(item_id)
            
            if action != ItemAction.NONE:
                return action == ItemAction.SALVAGE or action == ItemAction.SALVAGE_COMMON_MATERIALS or action == ItemAction.SALVAGE_RARE_MATERIALS or action == ItemAction.SALVAGE_SMART, action
   
    return False, ItemAction.NONE

def ShouldExtractMods(item_id: int) -> bool:
    if GLOBAL_CACHE.Item.Usage.IsSalvageable(item_id):
        item_type = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])
        
        if utility.Util.IsWeaponType(item_type) or utility.Util.IsArmorType(item_type):
            has_mod_to_keep, _, _ = HasModToKeep(item_id)
            
            if has_mod_to_keep:
                return True
            
    return False

def ShouldSellItemToMerchant(item_id: int) -> bool:
    if not settings.current.loot_profile:
        return False
    
    model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
    ignored_model_ids = [
        ModelID.Salvage_Kit,
        ModelID.Expert_Salvage_Kit,
        ModelID.Superior_Salvage_Kit,
        ModelID.Perfect_Salvage_Kit,
        ModelID.Identification_Kit,
        ModelID.Superior_Identification_Kit,
        ModelID.Lockpick,
        ]
    
    if model_id in ignored_model_ids:
        return False  
    
    ## If the item is a material, we should not sell it to the merchant, instead we should deposit it to the material storage or visit the material trader
    item_type = ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])
    if  item_type == ItemType.Materials_Zcoins:
        return False
    
    ## Runes and Insignias should not be sold to the merchant, instead we should visit the rune trader to sell them
    if item_type == ItemType.Rune_Mod:
        mods = utility.Util.GetMods(item_id)
        if mods and mods[0].identifier in data.Runes:
            return False
        
    if GLOBAL_CACHE.Item.Properties.GetValue(item_id) > 0:
        item_config = settings.current.loot_profile.items.get(model_id, None)
        
        if item_config:
            action = item_config.get_action(item_id)
            return action == ItemAction.SELL_TO_MERCHANT
                        
        for filter in settings.current.loot_profile.filters:
            action = filter.get_action(item_id)
            
            if action != ItemAction.NONE:
                return action == ItemAction.SELL_TO_MERCHANT
    
    return False

def IsVial_Of_DyeToKeep(item_id : int) -> bool:
    lootprofile = settings.current.loot_profile
    
    if lootprofile is None:
        return False
    
    if GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Vial_Of_Dye:
        dye_info = GLOBAL_CACHE.Item.Customization.GetDyeInfo(item_id)
        if dye_info is not None:
            color_id = dye_info.dye1.ToInt() if dye_info.dye1 else -1
            color = DyeColor(color_id) if color_id != -1 else None 
            if color is not None and color in lootprofile.dyes:
                return lootprofile.dyes[color]

    return False

#TODO: Add a rule for PCons and add a keep in item threshold for them
def ShouldStashItem(item_id: int) -> bool:    
    if settings.current.loot_profile is None:
        return False
        
    item_data = data.Items.get(GLOBAL_CACHE.Item.GetModelID(item_id), None)
    if item_data is not None:
        if item_data.nick_index and item_data.next_nick_week:
            weeks_until = (item_data.next_nick_week - date.today()).days // 7
              
            return weeks_until < settings.current.loot_profile.nick_weeks_to_keep if settings.current.loot_profile else False
    
    if IsVial_Of_DyeToKeep(item_id):
        return True
        
    if utility.Util.IsWeaponType(ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])):
        has_mod_to_keep, mods_to_keep, _ = HasModToKeep(item_id)
        if has_mod_to_keep and len(mods_to_keep) > 1:
            return True
    
    ##TODO: Rule for runes: If the other rune/insignia is worth above a certain threshold, we should not salvage the item as we will risk losing the rune/insignia. This option should be configurable in the loot profile.
    if utility.Util.IsArmorType(ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])):
        has_mod_to_keep, _, runes_to_keep = HasModToKeep(item_id)
        if has_mod_to_keep and len(runes_to_keep) > 1:
            return True
    
    model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
    item_config = settings.current.loot_profile.items.get(model_id, None)
    if item_config:
        action = item_config.get_action(item_id)        
        return action == ItemAction.STASH

    for filter in settings.current.loot_profile.filters:
        action = filter.get_action(item_id)
        
        if action != ItemAction.NONE:
            return action == ItemAction.STASH
        
    return False

def ShouldCollectData(item_id: int) -> bool:
    if not data_collector.instance.is_item_collected(item_id):
        # ConsoleLog("LootEx", f"Item '{utility.Util.GetItemDataName(item_id)}' {item_id} is not collected yet, skipping processing.", Console.MessageType.Warning)
        return True
    
    if data_collector.instance.has_uncollected_mods(item_id):
        # ConsoleLog("LootEx", f"Item '{utility.Util.GetItemDataName(item_id)}' {item_id} has uncollected mods, skipping processing.", Console.MessageType.Warning)
        return True
    
    return False

def GetSalvageKit(option: SalvageKitOption = SalvageKitOption.Lesser) -> int:    
    if option == SalvageKitOption.Lesser:
        return GLOBAL_CACHE.Inventory.GetFirstSalvageKit(True)    
    
    if option == SalvageKitOption.LesserOrExpert:
        salvage_kit = GLOBAL_CACHE.Inventory.GetFirstSalvageKit(True)  
        return GLOBAL_CACHE.Inventory.GetFirstSalvageKit(False) if salvage_kit == 0 else salvage_kit
        
    if option == SalvageKitOption.Expert:
        item_array = GLOBAL_CACHE.ItemArray.GetItemArray([Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2])
        
        for item_id in item_array:
            if GLOBAL_CACHE.Item.Usage.IsExpertSalvageKit(item_id):
                return item_id    
    
    if option == SalvageKitOption.Perfect:
        item_array = GLOBAL_CACHE.ItemArray.GetItemArray([Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2])
        
        for item_id in item_array:
            if GLOBAL_CACHE.Item.GetModelID(item_id) == ModelID.Perfect_Salvage_Kit:
                return item_id
    
    return 0

def GetSalvageKitOption(option : SalvageOption) -> SalvageKitOption:
    match option:        
        case SalvageOption.Prefix:            
            return SalvageKitOption.Expert
        
        case SalvageOption.Suffix:
            return SalvageKitOption.Expert
        
        case SalvageOption.Inherent:
            return SalvageKitOption.Expert
        
        case SalvageOption.LesserCraftingMaterials:
            return SalvageKitOption.Lesser
        
        case SalvageOption.RareCraftingMaterials:
            return SalvageKitOption.Expert
        
        case _:
            # Default to Lesser or Expert for any other option which implies crafting materials
            return SalvageKitOption.LesserOrExpert

def SalvageItem(item_id, option : SalvageOption = SalvageOption.LesserCraftingMaterials):
    global salvage_requires_confirmation
    
    if item_id == 0:
        return False
    
    if option is SalvageOption.None_:
        return False
    
    if not GLOBAL_CACHE.Item.Usage.IsSalvageable(item_id):
        return False
    
    salvage_kit = GetSalvageKit(GetSalvageKitOption(option))
    
    if salvage_kit == 0:
        ConsoleLog("LootEx", "No salvage kit found, cannot salvage item.", Console.MessageType.Warning)
        return False
    
    ConsoleLog("LootEx", f"Salvaging item: '{utility.Util.GetItemDataName(item_id)}' {item_id} using kit {utility.Util.GetItemDataName(salvage_kit)} {salvage_kit}", Console.MessageType.Info)
    Inventory.SalvageItem(item_id, salvage_kit)
    salvage_timer.Reset()
    
    rarity_requires_confirmation = GLOBAL_CACHE.Item.Rarity.GetRarity(item_id)[0] >= Rarity.Blue
    mods_require_confirmation = len(utility.Util.GetMods(item_id)) > 0 and option is not SalvageOption.LesserCraftingMaterials
    
    salvage_requires_confirmation = mods_require_confirmation or rarity_requires_confirmation
    
    if salvage_requires_confirmation:
        ConfirmSalvage(item_id, option)
        
    return True

def ResetSalvageConfirmation():
    global salvage_requires_confirmation
    salvage_requires_confirmation = False

def ConfirmSalvage(item_id : int, option: SalvageOption = SalvageOption.LesserCraftingMaterials) -> bool:    
    global salvage_requires_confirmation
    salvage_action_queue.add_action(lambda : True)
    salvage_action_queue.add_action(_SendConfirmSalvage, item_id, option)  
    
    # salvage_action_queue.add_action(lambda : True)
    salvage_action_queue.add_action(ResetSalvageConfirmation)  
    
    return True

def _SendConfirmSalvage(item_id : int, option: SalvageOption = SalvageOption.LesserCraftingMaterials) -> bool:
    if option is not SalvageOption.LesserCraftingMaterials:
        ConsoleLog("LootEx", f"Confirming salvage option: {option.name} for {utility.Util.GetItemDataName(item_id)}", Console.MessageType.Info)
        ui_manager_extensions.UIManagerExtensions.SelectSalvageOptionAndSalvage(option)
    else:
        ConsoleLog("LootEx", f"Confirming lesser salvage for item: {utility.Util.GetItemDataName(item_id)}", Console.MessageType.Info)
        ui_manager_extensions.UIManagerExtensions.ConfirmLesserSalvage()
            
    return True

def ExtractWantedMods(item_id: int) -> bool:
    global salvage_requires_confirmation
    
    if item_id == 0:
        return False
    
    salvage_kit = GetSalvageKit(SalvageKitOption.Expert)
    
    if salvage_kit == 0:
        ConsoleLog("LootEx", "No expert salvage kit found, cannot extract mods.", Console.MessageType.Warning)
        return False
    
    _, mods, runes = HasModToKeep(item_id)
    
    if not mods and not runes:
        return False
    
    mod_to_extract : Optional[models.ItemMod] = None
    
    if mods:    
        mod_to_extract = mods[0]    
    else:
        mod_to_extract = runes[0]
    
    
    ConsoleLog("LootEx", f"Extracting '{mod_to_extract.name}' from item: '{utility.Util.GetItemDataName(item_id)}' {item_id} using kit {utility.Util.GetItemDataName(salvage_kit)} {salvage_kit}", Console.MessageType.Info)
    Inventory.SalvageItem(item_id, salvage_kit)
    
    salvage_requires_confirmation = True
    ConfirmSalvage(item_id, utility.Util.GetSalvageOptionFromModType(mod_to_extract.mod_type))
    
    return True

def CanSalvage() -> bool:
    global salvage_requires_confirmation, salvaged, salvage_timer
    return not salvage_requires_confirmation and not salvaged and salvage_timer.IsExpired()

def StashItem(item_id: int) -> bool:
    if item_id == 0 or not settings.current.loot_profile:
        return False
                
    stash = GLOBAL_CACHE.Inventory.GetZeroFilledStorageArray()
    model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
    
    if GLOBAL_CACHE.Item.Customization.IsStackable(item_id):
        item_config = settings.current.loot_profile.items.get(model_id, None)
        config_condition = item_config.get_condition(item_id) if item_config else None
        keep_amount = config_condition.keep_in_inventory if config_condition else 0
        
        amount = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id) - keep_amount
        color = utility.Util.get_color(item_id)
        
        sorted_stash = stash.copy()
        sorted_stash.sort(key=lambda x: (x == 0, GLOBAL_CACHE.Item.Properties.GetQuantity(x) if x != 0 else 0), reverse=True)
        
        slot = -1
        for id in sorted_stash:
            slot = stash.index(id)
            storage_index = Bag.Storage_1.value + math.floor(slot / 25)
            storage_slot =  slot % 25
            
            if id == 0:
                continue
            
            slot_model_id = GLOBAL_CACHE.Item.GetModelID(id)
            if slot_model_id == model_id:
                slot_quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(id)
                
                if slot_quantity == 250:
                    continue
                
                if slot_model_id == ModelID.Vial_Of_Dye:
                    if utility.Util.get_color(id) == color:
                        move_amount = min(250 - slot_quantity, amount)
                        ConsoleLog("LootEx", f"Stashing item  {move_amount} '{utility.Util.GetItemDataName(item_id)}' {item_id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)
                        Inventory.MoveItem(item_id, storage_index, storage_slot, move_amount)                        
                        amount -= move_amount
                        
                        if amount <= 0:
                            break
                
                else:
                    name = utility.Util.GetItemDataName(item_id)
                    move_amount = min(250 - slot_quantity, amount)
                    ConsoleLog("LootEx", f"Stashing item {move_amount}'{name}' {item_id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)
                    Inventory.MoveItem(item_id, storage_index, storage_slot, move_amount)                        
                    amount -= move_amount
                    
                    if amount <= 0:
                        break
                    
            
        if amount > 0:
            first_zero_slot = stash.index(0) if 0 in stash else None
            if first_zero_slot is None:
                ConsoleLog("LootEx", "No empty slot found in stash, cannot stash item.", Console.MessageType.Warning)
                return False
            
            storage_index = Bag.Storage_1.value + math.floor(first_zero_slot / 25)
            storage_slot = first_zero_slot % 25
            move_amount = min(250, amount)
            ConsoleLog("LootEx", f"Stashing item {move_amount} '{utility.Util.GetItemDataName(item_id)}' {item_id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)
            Inventory.MoveItem(item_id, storage_index, storage_slot, move_amount)
            
        pass
    
    else:
        # find an empty slot in the stash
        first_zero_slot = stash.index(0) if 0 in stash else None
        
        if first_zero_slot is None:
            ConsoleLog("LootEx", "No empty slot found in stash, cannot stash item.", Console.MessageType.Warning)
            return False
        
        storage_index = Bag.Storage_1.value + math.floor(first_zero_slot / 25)        
        storage_slot = first_zero_slot % 25
        
        ConsoleLog("LootEx", f"Stashing item '{utility.Util.GetItemDataName(item_id)}' {item_id} to storage {Bag(storage_index)} slot {storage_slot}", Console.MessageType.Info)        
        Inventory.MoveItem(item_id, storage_index, storage_slot, GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))
    
    
    return True    

def ShouldDestroyItem(item_id: int) -> bool:
    if not settings.current.loot_profile:
        return False
    
    model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
    if settings.current.loot_profile.is_blacklisted(model_id):
        return False
    
    item_config = settings.current.loot_profile.items.get(model_id, None)
    
    if item_config:
        action = item_config.get_action(item_id)
        return action == ItemAction.DESTROY
    
    for filter in settings.current.loot_profile.filters:
        action = filter.get_action(item_id)
        
        if action != ItemAction.NONE:
            return action == ItemAction.DESTROY
        
    return False

def GetItemAction(item_id: int) -> ItemAction:    
    if ShouldCollectData(item_id):
        return ItemAction.COLLECT_DATA
    
    if ShouldIdentifyItem(item_id):
        return ItemAction.IDENTIFY
    
    if ShouldStashItem(item_id):
        return ItemAction.STASH
    
    if ShouldExtractMods(item_id):
        return ItemAction.SALVAGE_MODS
    
    should_salvage, action = ShouldSalvageItem(item_id)
    if should_salvage:
        return action
    
    if ShouldSellItemToMerchant(item_id):
        return ItemAction.SELL_TO_MERCHANT    
    
    if ShouldDestroyItem(item_id):
        return ItemAction.DESTROY
    
    return ItemAction.NONE

def Run():
    global salvaged, deposited, capacity_checked, material_capacity
    is_outpost = GLOBAL_CACHE.Map.IsOutpost()
    
    if is_outpost:
        if deposit_timer.IsExpired() or not capacity_checked:
            deposit_timer.Reset()
            
            DepositMaterials()
    
    if data_collector.instance.is_running():
        return
    
    if not settings.current.automatic_inventory_handling:
        return
    
    if identification_timer.IsExpired():
        identification_timer.Reset()
        
        if IdentifyItems():
            return
    
    if not salvage_action_queue.is_empty():
        salvage_action_queue.ProcessQueue()
        return
    
    if merchant_timer.IsExpired():
        merchant_timer.Reset()
        
        items_to_buy = GetMissingItems()        
        if items_to_buy:
            if is_outpost and not GetItemsFromStorage(items_to_buy):
                if ui_manager_extensions.UIManagerExtensions.IsMerchantWindowOpen():
                    BuyItemsFromMerchant(items_to_buy)
    
    if inventory_timer.IsExpired():
        inventory_timer.Reset()
        
        merchant_open = ui_manager_extensions.UIManagerExtensions.IsMerchantWindowOpen()
        empty_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
        salvaged = False
        
        for item_id in GLOBAL_CACHE.ItemArray.GetItemArray([Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2]):
            action = GetItemAction(item_id)
            if item_id == -1:
                ConsoleLog("LootEx", f"Processing item: '{utility.Util.GetItemDataName(item_id)}' {item_id} with action: {action.name}", Console.MessageType.Debug)        
                        
            if action == ItemAction.SALVAGE_SMART or action == ItemAction.SALVAGE or action == ItemAction.SALVAGE_COMMON_MATERIALS or action == ItemAction.SALVAGE_RARE_MATERIALS:
                if CanSalvage():                    
                    if empty_slots > 0:
                        salvage_option = GetSalvageOption(item_id, action)
                        
                        # ConsoleLog("LootEx", f"Salvage option for item {item_id} is {salvage_option.name if salvage_option else 'None'}", Console.MessageType.Debug)
                        if salvage_option is None:
                            continue
                        
                        salvage_kit = GetSalvageKit(GetSalvageKitOption(salvage_option))
                        
                        if salvage_kit == 0:
                            continue
                        
                        salvaged = True
                        SalvageItem(item_id, salvage_option if salvage_option else SalvageOption.LesserCraftingMaterials)
                    
            if action == ItemAction.SALVAGE_MODS:
                if CanSalvage():                    
                    if empty_slots > 0:
                        salvage_option = GetSalvageOption(item_id, action)
                        
                        if salvage_option is None:
                            continue
                        
                        salvage_kit = GetSalvageKit(SalvageKitOption.Expert)
                        
                        if salvage_kit == 0:
                            continue
                        
                        salvaged = True
                        ExtractWantedMods(item_id)
                
            if action == ItemAction.STASH:
                if is_outpost:
                    StashItem(item_id)
                    pass
            
            if action == ItemAction.SELL_TO_MERCHANT:
                if merchant_open:
                    ConsoleLog("LootEx", f"Selling item: '{utility.Util.GetItemDataName(item_id)}' {item_id}", Console.MessageType.Info)
                    Trading.Merchant.SellItem(item_id, GLOBAL_CACHE.Item.Properties.GetQuantity(item_id) * GLOBAL_CACHE.Item.Properties.GetValue(item_id))
            
            if action == ItemAction.DESTROY:
                ConsoleLog("LootEx", f"Destroying item: '{utility.Util.GetItemDataName(item_id)}' {item_id}", Console.MessageType.Info)
                # Inventory.DestroyItem(item_id)
                    
            if action == ItemAction.SELL_TO_TRADER:
                pass
                    
                
    if compact_inventory_timer.IsExpired():
        compact_inventory_timer.Reset()
        CompactInventory()       

def GetItemsFromStorage(items: dict[int, int]) -> bool:
    withdrawn_items = False
    
    if not items:
        return False
    
    storage_items = GLOBAL_CACHE.ItemArray.GetItemArray([Bag.Storage_1, Bag.Storage_14])
    
    for model_id, quantity in items.items():
        item_id = next((item for item in storage_items if GLOBAL_CACHE.Item.GetModelID(item) == model_id), None)
        
        if not item_id:
            continue
        
        item_array, bag_sizes = utility.Util.GetZeroFilledBags(Bag.Backpack, Bag.Bag_2)   
        inventory_slot = next((i for i, item in enumerate(item_array) if item == 0), None)
        
        if GLOBAL_CACHE.Item.Customization.IsStackable(item_id):
            existing_item_id = next((item for item in item_array if GLOBAL_CACHE.Item.GetModelID(item) == model_id and GLOBAL_CACHE.Item.Properties.GetQuantity(item) + quantity <= 250), None)
            
            if existing_item_id:
                inventory_slot = item_array.index(existing_item_id)
        
        if inventory_slot is None:
            continue
        
        bag, slot = GetBagFromSlot(inventory_slot, bag_sizes)
        item_data = data.Items.get(GLOBAL_CACHE.Item.GetModelID(item_id), None)        
        item_name = item_data.name if item_data else "Item Name Unavailable"
        
        ConsoleLog("LootEx", f"Withdrawing {quantity}x '{item_name}' ({item_id})", Console.MessageType.Info)  
        Inventory.MoveItem(item_id, bag.value, slot, quantity)
        withdrawn_items = True
    
    return withdrawn_items

def CompactStash() -> bool:
    return CondenseStacks(Bag.Storage_1, Bag.Storage_14) or SortBags(Bag.Storage_1, Bag.Storage_10) 

def GetBagFromSlot(slot: int, bag_sizes : dict[Bag, int]) -> tuple[Bag, int]:
    offset = 0
    
    for bag, size in bag_sizes.items():
        if slot < offset + size:
            return bag, slot - offset
        offset += size
        
    return Bag.NoBag, -1

def CondenseStacks(bag_start : Bag, bag_end : Bag) -> bool:
    if bag_end.value < bag_start.value:
        return False
    
    class SlotInfo:
        def __init__(self, item_id: int, bag: Bag, slot: int):
            self.item_id = item_id
            self.bag = bag
            self.slot = slot
            self.model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
            self.stackable = GLOBAL_CACHE.Item.Customization.IsStackable(item_id)
            self.quantity = GLOBAL_CACHE.Item.Properties.GetQuantity(item_id)
            self.color = utility.Util.get_color(item_id)
                         
    inventory_array, bag_sizes = utility.Util.GetZeroFilledBags(bag_start, bag_end) 
    
    slot_infos = [
        SlotInfo(item_id, bag, local_slot)
        for index, item_id in enumerate(inventory_array)
        for bag, local_slot in [GetBagFromSlot(index, bag_sizes)]
    ]
        
    condensed = False
    slot_infos.sort(key=lambda x: (x.model_id, x.quantity, x.bag.value, x.slot))
    
    for slot_info in slot_infos:
        if slot_info.stackable and slot_info.quantity < 250:
            
            #get the next slot_info with the highest quantity of the same model_id and quantity less than 250
            copy = slot_infos.copy()
            copy = [
                x for x in copy if x.stackable and x.quantity < 250 and x.model_id == slot_info.model_id and (x.model_id != ModelID.Vial_Of_Dye or x.color == slot_info.color)
            ]
            copy.sort(key=lambda x: x.quantity, reverse=True)
            
            for next_slot_info in copy:
                if next_slot_info.item_id == slot_info.item_id or next_slot_info.item_id == 0:
                    continue
                
                if next_slot_info.quantity >= 250:
                    continue
                
                if next_slot_info.bag == slot_info.bag and next_slot_info.slot == slot_info.slot:
                    continue
                
                # Check if the next slot info is not the same item
                if next_slot_info.item_id != slot_info.item_id:
                    move_amount = min(250 - next_slot_info.quantity, slot_info.quantity)
                    next_slot_info.quantity += move_amount
                    slot_info.quantity -= move_amount
                    
                    Inventory.MoveItem(slot_info.item_id, next_slot_info.bag.value, next_slot_info.slot, move_amount)
                    condensed = True
                    
                    if slot_info.quantity <= 0:
                        slot_info.item_id = 0
                        break
    
    return condensed    
    
def CompactInventory() -> bool:  
    return CondenseStacks(Bag.Backpack, Bag.Bag_2) or SortBags(Bag.Backpack, Bag.Bag_2)
    
def SortBags(bag_start : Bag, bag_end : Bag) -> bool:
    if bag_end.value < bag_start.value:
        return False
        
    # Sort the inventory and comapct it
    # We sort in the following order:
    item_typeOrder = [
        int(ItemType.Kit),
        int(ItemType.Key),
        int(ItemType.Usable),
        int(ItemType.Trophy),
        int(ItemType.Quest_Item),
        int(ItemType.Materials_Zcoins)
    ]

    # then everything else
    item_typeOrder += [int(item)
                       for item in ItemType if int(item) not in item_typeOrder]
    
    item_array, bag_sizes = utility.Util.GetZeroFilledBags(bag_start, bag_end)
    
    desired_item_array = sorted(
        item_array,
        key=lambda item_id: (
            item_id == 0,
            item_typeOrder.index(
                GLOBAL_CACHE.Item.GetItemType(item_id)[0]),
            - GLOBAL_CACHE.Item.Properties.GetValue(item_id),
            GLOBAL_CACHE.Item.GetModelID(item_id),
            -GLOBAL_CACHE.Item.Properties.GetQuantity(item_id),
            item_id
        )
    )
        
    for bag_id in bag_sizes.keys():
        item_ids = GLOBAL_CACHE.ItemArray.GetItemArray([bag_id])
        
        if not item_ids:
            continue
        
        for item_id in item_ids:            
            if item_id not in desired_item_array or item_id == 0:
                continue
            
            ## get the index of the item by its item_id
            target_slot = next(
                (i for i, it in enumerate(desired_item_array) if it == item_id), None)
            
            if target_slot is not None:
                bag, slot = GetBagFromSlot(target_slot, bag_sizes)
                
                Inventory.MoveItem(item_id, bag.value, slot, 
                                   GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))

    return False

def CompactItemsX(bag_start : Bag, bag_end : Bag) -> bool:
    if bag_end.value < bag_start.value:
        return False
    
    bag_list = [Bag(i) for i in range(bag_start.value, bag_end.value + 1)]  
    
    # Sort the inventory and comapct it
    # We sort in the following order:
    item_typeOrder = [
        int(ItemType.Kit),
        int(ItemType.Key),
        int(ItemType.Materials_Zcoins)
    ]

    # then everything else
    item_typeOrder += [int(item)
                       for item in ItemType if int(item) not in item_typeOrder]

    desired_item_array = sorted(
        GLOBAL_CACHE.ItemArray.GetItemArray(bag_list),
        key=lambda item_id: (
            item_typeOrder.index(
                GLOBAL_CACHE.Item.GetItemType(item_id)[0]),
            - GLOBAL_CACHE.Item.Properties.GetValue(item_id),
            GLOBAL_CACHE.Item.GetModelID(item_id),
            -GLOBAL_CACHE.Item.Properties.GetQuantity(item_id),
            item_id
        )
    )

    def GetBagFromSlot(slot: int) -> tuple[Bag, int]:        
        backpack_size = PyInventory.Bag(
            Bags.Backpack.value, Bags.Backpack.name).GetSize()
        belt_pouch_size = PyInventory.Bag(
            Bags.BeltPouch.value, Bags.BeltPouch.name).GetSize()
        bag1_size = PyInventory.Bag(Bags.Bag1.value, Bags.Bag1.name).GetSize()
        bag2_size = PyInventory.Bag(Bags.Bag2.value, Bags.Bag2.name).GetSize()

        if slot < backpack_size:
            return Bag.Backpack, slot - 0

        elif slot < backpack_size + belt_pouch_size:
            return Bag.Belt_Pouch, slot - backpack_size

        elif slot < backpack_size + belt_pouch_size + bag1_size:
            return Bag.Bag_1, slot - backpack_size - belt_pouch_size

        elif slot < backpack_size + belt_pouch_size + bag1_size + bag2_size:
            return Bag.Bag_2, slot - backpack_size - belt_pouch_size - bag1_size

        return Bag.NoBag, -1
   
    bag_ids = [Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2]
    
    for bag_id in bag_ids:
        item_ids = GLOBAL_CACHE.ItemArray.GetItemArray([bag_id])
        
        if not item_ids:
            continue
        
        for item_id in item_ids:
            if item_id not in desired_item_array:
                continue
            
            ## get the index of the item by its item_id
            target_slot = next(
                (i for i, it in enumerate(desired_item_array) if it == item_id), None)
            
            if target_slot is not None:
                bag, slot = GetBagFromSlot(target_slot)
                
                Inventory.MoveItem(item_id, bag.value, slot, 
                                   GLOBAL_CACHE.Item.Properties.GetQuantity(item_id))

    return False

def StopLootHandling():
    global salvaged, deposited, capacity_checked, material_capacity

    ConsoleLog("LootEx", "Stopping loot handling", Console.MessageType.Info)
    
    indentify_action_queue.clear()
    salvage_action_queue.clear()
    merchant_action_queue.clear()

    settings.current.automatic_inventory_handling = False
    
    return True

def StartLootHandling() -> bool:
    global salvaged, deposited, capacity_checked, material_capacity

    ConsoleLog("LootEx", "Starting loot handling", Console.MessageType.Info)
    settings.current.automatic_inventory_handling = True

    return True

def HasModToKeep(item_id: int) -> tuple[bool, list[models.WeaponMod], list[models.Rune]]:
    mods = utility.Util.GetMods(item_id, True)
    _, item_type = GLOBAL_CACHE.Item.GetItemType(item_id)
    runes_to_keep : list[models.Rune] = []
    mods_to_keep : list[models.WeaponMod] = []
    
    if settings.current.loot_profile is not None and settings.current.loot_profile.weapon_mods is not None:

        for mod in mods:
            if mod.identifier in settings.current.loot_profile.weapon_mods:
                if settings.current.loot_profile.weapon_mods[mod.identifier].get(item_type, False):
                    if isinstance(mod, models.WeaponMod):
                        mods_to_keep.append(mod)
            
            if mod.identifier in settings.current.loot_profile.runes:
                if settings.current.loot_profile.runes[mod.identifier]:
                    if isinstance(mod, models.Rune):
                        runes_to_keep.append(mod)
        
    return True if runes_to_keep or mods_to_keep else False, mods_to_keep, runes_to_keep

def CanProcessItem(item_id: int) -> bool:
    model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
    
    if settings.current.loot_profile and settings.current.loot_profile.is_blacklisted(model_id):
        return False
    
    if GLOBAL_CACHE.Item.Properties.IsCustomized(item_id):
        # ConsoleLog("LootEx", f"Item '{utility.Util.GetItemDataName(item_id)}' {item_id} is customized, skipping processing.", Console.MessageType.Warning)
        return False
    
    if utility.Util.IsWeaponType(ItemType(GLOBAL_CACHE.Item.GetItemType(item_id)[0])):
        has_mod_to_keep, mods_to_keep, _ = HasModToKeep(item_id)
        if has_mod_to_keep and len(mods_to_keep) > 1:
            return False
    
    ## Add here checks from the loot profile
    
    return True

def HasItemToSalvage() -> tuple[bool, int]:
    if settings.current.loot_profile is None:
        return False, -1
    
    empty_slots = GLOBAL_CACHE.Inventory.GetFreeSlotCount()
    if empty_slots == 0:
        return False, -1
    
    salvage_kit = GLOBAL_CACHE.Inventory.GetFirstSalvageKit(True)
    if salvage_kit == 0:
        ConsoleLog("LootEx", "No salvage kit found, cannot salvage items.", Console.MessageType.Warning)
        return False, -1

    item_array = GLOBAL_CACHE.ItemArray.GetItemArray([
        Bag.Backpack, Bag.Belt_Pouch, Bag.Bag_1, Bag.Bag_2])
    
    for item_id in item_array:
        if item_id in queued_items:
            continue
        
        if not CanProcessItem(item_id):
            continue
        
        if not GLOBAL_CACHE.Item.Usage.IsSalvageable(item_id):            
            continue

        if ShouldIdentifyItem(item_id):
            continue

        if GLOBAL_CACHE.Item.GetItemType(item_id) == ItemType.Materials_Zcoins:
            continue

        has_mod_to_keep, mods_to_keep, runes_to_keep = HasModToKeep(item_id)
        
        if has_mod_to_keep:
            mod_names = [mod.name for mod in mods_to_keep] if mods_to_keep else []
            rune_names = [rune.name for rune in runes_to_keep] if runes_to_keep else []
            
            # ConsoleLog("LootEx", "Item has mods to keep: " + utility.Util.GetItemDataName(item_id) +
            #            " (Id: " + str(item_id) + ")" + 
            #               f" | Mods: {', '.join(mod_names)} | Runes: {', '.join(rune_names)}", Console.MessageType.Info)
            continue

        if GLOBAL_CACHE.Item.Properties.GetValue(item_id) > settings.current.loot_profile.sell_threshold:
            continue
        
        return True, item_id
    
    return False, -1

def GetMissingItems() -> dict[int, int]:
    if settings.current.loot_profile is None:
        return {}

    missing_items = {}
    
    if settings.current.loot_profile.identification_kits > 0:
        identificationKits = Inventory.GetModelCount(
            ModelID.Superior_Identification_Kit)
        identificationKits += Inventory.GetModelCount(ModelID.Identification_Kit)
        if identificationKits < settings.current.loot_profile.identification_kits:
            missing_items[ModelID.Superior_Identification_Kit] = settings.current.loot_profile.identification_kits - identificationKits

    if settings.current.loot_profile.salvage_kits > 0:
        salvageKits = Inventory.GetModelCount(ModelID.Salvage_Kit)
        if salvageKits < settings.current.loot_profile.salvage_kits:
            missing_items[ModelID.Salvage_Kit] = settings.current.loot_profile.salvage_kits - salvageKits

    if settings.current.loot_profile.expert_salvage_kits > 0:
        expertSalvageKits = Inventory.GetModelCount(ModelID.Expert_Salvage_Kit)
        expertSalvageKits += Inventory.GetModelCount(ModelID.Superior_Salvage_Kit)
        if expertSalvageKits < settings.current.loot_profile.expert_salvage_kits:
            missing_items[ModelID.Expert_Salvage_Kit] = settings.current.loot_profile.expert_salvage_kits - expertSalvageKits

    if settings.current.loot_profile.lockpicks > 0:
        lockpicks = Inventory.GetModelCount(ModelID.Lockpick)
        if lockpicks < settings.current.loot_profile.lockpicks:
            missing_items[ModelID.Lockpick] = settings.current.loot_profile.lockpicks - lockpicks

    return missing_items

def BuyItemsFromMerchant(items_to_buy: dict[int, int]):
    global merchant_action_queue
    
    if not ui_manager_extensions.UIManagerExtensions.IsMerchantWindowOpen():
        ConsoleLog("LootEx", "Merchant window is not open, cannot buy items.", Console.MessageType.Warning)
        return

    merchant_item_list = Trading.Merchant.GetOfferedItems()
    gold_on_character = Inventory.GetGoldOnCharacter()

    for model_id, amount in items_to_buy.items():
        item_id = next((
            item for item in merchant_item_list if GLOBAL_CACHE.Item.GetModelID(item) == model_id), None)
        
        if item_id is None:
            continue
        
        value = GLOBAL_CACHE.Item.Properties.GetValue(item_id) * 2
        item_data = data.Items.get(GLOBAL_CACHE.Item.GetModelID(item_id), None)        
        item_name = item_data.name if item_data else "Item Name Unavailable"
        ConsoleLog  ("LootEx", f"Buying {amount}x '{item_name}' ({item_id}) from merchant for {utility.Util.format_currency(value * amount)}.", Console.MessageType.Info)
        
        for i in range(amount):
            if value <= gold_on_character:
                gold_on_character -= value
                Trading.Merchant.BuyItem(item_id, value)
            
            if gold_on_character <= 0:
                break                
            

        if gold_on_character <= 0:
            break

#endregion