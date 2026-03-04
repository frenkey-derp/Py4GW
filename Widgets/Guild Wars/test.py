import Py4GW
import PyImGui

from Py4GWCoreLib.Inventory import Inventory
from Py4GWCoreLib.Item import Bag
from Py4GWCoreLib.ItemArray import ItemArray
from Py4GWCoreLib.enums_src.Item_enums import Rarity
from Py4GWCoreLib.py4gwcorelib_src.BehaviorTree import BehaviorTree
from Py4GWCoreLib.py4gwcorelib_src.Utils import Utils
from Sources.frenkeyLib.ItemHandling.Items.ItemCache import ITEM_CACHE

Utils.ClearSubModules("ItemHandling")
from Sources.frenkeyLib.ItemHandling.BTNodes import BTNodes
from Sources.frenkeyLib.ItemHandling.Rules.types import SalvageMode


MODULE_NAME = "ItemHandling Test"

TESTS = [
    "Identify Hovered",
    "Salvage Hovered",
    "Deposit Hovered",
    "Destroy Hovered (Armed)",
    "Compact Inventory",
    "Sort Inventory",
    "Identify + Salvage Hovered",
    "Identify + Salvage + Deposit Hovered",
    "Compact + Sort Inventory",
    "Trader Buy (single item id)",
    "Trader Sell (single item id)",
    "Merchant Buy (single item id)",
    "Merchant Sell Hovered",
]

SALVAGE_MODES = [m.name for m in SalvageMode]


selected_rarity_idx = 0
selected_test = 0
tree: BehaviorTree | None = None
auto_tick = False
tick_interval_ms = 1
last_tick_at = 0
last_state = "NONE"
last_error = ""

target_item_id = 0
trader_item_id = 0
trader_cost = -1
merchant_item_id = 0
merchant_cost = -1
armed = False
salvage_mode_idx = 0
hovered = 0

def _inventory_item_ids() -> list[int]:
    bags = ItemArray.CreateBagList(Bag.Backpack.value, Bag.Belt_Pouch.value, Bag.Bag_1.value, Bag.Bag_2.value)
    return ItemArray.GetItemArray(bags)


def _build_tree() -> BehaviorTree | None:
    global last_error, hovered
    last_error = ""

    hovered = Inventory.GetHoveredItemID() or hovered
    item_id = target_item_id if target_item_id > 0 else hovered
    salvage_mode = getattr(SalvageMode, SALVAGE_MODES[salvage_mode_idx], SalvageMode.NONE)

    try:
        if TESTS[selected_test] == "Identify Hovered":
            
            return BehaviorTree(BTNodes.Items.IdentifyItems(item_ids=_inventory_item_ids() if item_id <= 0 else [item_id]))

        if TESTS[selected_test] == "Salvage Hovered":
            return BehaviorTree(BTNodes.Items.SalvageItem(item_id=item_id, salvage_mode=salvage_mode))

        if TESTS[selected_test] == "Deposit Hovered":
            return BehaviorTree(BTNodes.Items.DepositItems(item_ids=[item_id]))

        if TESTS[selected_test] == "Destroy Hovered (Armed)":
            if not armed:
                last_error = "Destructive test is not armed."
                return None
            return BehaviorTree(BTNodes.Items.DestroyItems(item_ids=[item_id]))

        if TESTS[selected_test] == "Compact Inventory":
            return BehaviorTree(BTNodes.InventoryOps.CompactInventory())

        if TESTS[selected_test] == "Sort Inventory":
            return BehaviorTree(BTNodes.InventoryOps.SortInventory())

        if TESTS[selected_test] == "Identify + Salvage Hovered":
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Combo.IdentifySalvage",
                    children=[
                        BTNodes.Items.IdentifyItems(item_ids=[item_id]),
                        BTNodes.Items.SalvageItem(item_id=item_id, salvage_mode=salvage_mode),
                    ],
                )
            )

        if TESTS[selected_test] == "Identify + Salvage + Deposit Hovered":
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Combo.IdentifySalvageDeposit",
                    children=[
                        BTNodes.Items.IdentifyItems(item_ids=[item_id]),
                        BTNodes.Items.SalvageItem(item_id=item_id, salvage_mode=salvage_mode),
                        BTNodes.Items.DepositItems(item_ids=[item_id]),
                    ],
                )
            )

        if TESTS[selected_test] == "Compact + Sort Inventory":
            return BehaviorTree(
                BehaviorTree.SequenceNode(
                    name="Combo.CompactSort",
                    children=[
                        BTNodes.InventoryOps.CompactInventory(),
                        BTNodes.InventoryOps.SortInventory(),
                    ],
                )
            )

        if TESTS[selected_test] == "Trader Buy (single item id)":
            if trader_item_id <= 0:
                last_error = "Set trader item id first."
                return None
            costs = [trader_cost] if trader_cost >= 0 else None
            return BehaviorTree(BTNodes.Trader.BuyItems(item_ids=[trader_item_id], costs=costs))

        if TESTS[selected_test] == "Trader Sell (single item id)":
            if trader_item_id <= 0:
                last_error = "Set trader item id first."
                return None
            costs = [trader_cost] if trader_cost >= 0 else None
            return BehaviorTree(BTNodes.Trader.SellItems(item_ids=[trader_item_id], costs=costs))

        if TESTS[selected_test] == "Merchant Buy (single item id)":
            if merchant_item_id <= 0:
                last_error = "Set merchant item id first."
                return None
            costs = [merchant_cost] if merchant_cost >= 0 else None
            return BehaviorTree(BTNodes.Merchant.BuyItems(item_ids=[merchant_item_id], costs=costs))

        if TESTS[selected_test] == "Merchant Sell Hovered":
            return BehaviorTree(BTNodes.Merchant.SellItems(item_ids=[item_id]))

        last_error = "Unknown test selection."
        return None

    except Exception as ex:
        last_error = f"Build error: {ex}"
        return None


def _tick_tree():
    global tree, last_state, last_error, auto_tick
    if tree is None:
        last_error = "No tree built."
        return

    try:
        state = tree.tick()
        last_state = state.name
        
    except Exception as ex:
        last_error = f"Tick error: {ex}"
        tree = None

def _create_tree() -> BehaviorTree:
    # Create tree to identify and salvage to materials all white items in inventory, then deposit them into the bank
    inventory = ITEM_CACHE.get_inventory_snapshot(Bag.Backpack, Bag.Bag_2)
    rarity = Rarity(selected_rarity_idx)
    items = [item for bag in inventory.values() for item in bag.values() if item is not None and item.is_valid and item.rarity == rarity and item.is_salvageable]
    item_ids = [item.id for item in items]
    Py4GW.Console.Log(MODULE_NAME, f"Creating tree for {len(items)} {rarity.name} salvageable items in inventory", Py4GW.Console.MessageType.Info)
    
    node = BehaviorTree.SequenceNode(
            name="IdentifySalvageAllWhite",
            children=[
                BTNodes.Items.IdentifyItems(item_ids=item_ids),
            ],
        )
    
    
    for item in items:
        if item is not None:
            salvage_mode = SalvageMode.LesserCraftingMaterials
            
            if rarity == Rarity.Gold:
                if item.suffix is not None:
                    salvage_mode = SalvageMode.Suffix
                    
                elif item.prefix is not None:
                    salvage_mode = SalvageMode.Prefix
                    
                elif item.inscription is not None:
                    salvage_mode = SalvageMode.Inherent
                    
                else:
                    salvage_mode = SalvageMode.LesserCraftingMaterials
                
            n = BTNodes.Items.SalvageItem(item_id=item.id, salvage_mode=salvage_mode)
            node.children.append(n)

    return BehaviorTree(node)

def main():
    global selected_test, tree, auto_tick, tick_interval_ms, last_tick_at, last_state, last_error
    global target_item_id, trader_item_id, trader_cost, merchant_item_id, merchant_cost, armed
    global salvage_mode_idx, hovered, selected_rarity_idx
    
    ITEM_CACHE.reset()
    
    hovered = Inventory.GetHoveredItemID() or hovered
    inventory_items = _inventory_item_ids()

    if PyImGui.begin(MODULE_NAME):
        PyImGui.text(f"Hovered item id: {hovered}")
        PyImGui.text(f"Inventory items: {len(inventory_items)}")
        PyImGui.separator()
        
        rarity = Rarity(selected_rarity_idx)
        if PyImGui.button(f"Identify + Salvage + Deposit All Items of {rarity.name} ({selected_rarity_idx}) in Inventory"):
            tree = _create_tree()
            auto_tick = True
        
        selected_rarity_idx = PyImGui.combo("Rarity for batch salvage/identify", selected_rarity_idx, [r.name for r in Rarity])
            
        selected_test = PyImGui.combo("Test", selected_test, TESTS)
        target_item_id = PyImGui.input_int("Target item id (0=hovered)", int(target_item_id))
        armed = PyImGui.checkbox("Arm destructive actions", armed)
        salvage_mode_idx = PyImGui.combo("Salvage mode", salvage_mode_idx, SALVAGE_MODES)

        PyImGui.separator()
        PyImGui.text("Trader test fields")
        trader_item_id = PyImGui.input_int("Trader item id", int(trader_item_id))
        trader_cost = PyImGui.input_int("Trader cost (-1 = auto quote)", int(trader_cost))

        PyImGui.text("Merchant test fields")
        merchant_item_id = PyImGui.input_int("Merchant item id", int(merchant_item_id))
        merchant_cost = PyImGui.input_int("Merchant cost (-1 = auto)", int(merchant_cost))

        PyImGui.separator()
        if PyImGui.button("Build Test Tree"):
            tree = _build_tree()
            last_state = "NONE"
            if tree is not None:
                Py4GW.Console.Log(MODULE_NAME, f"Built test tree: {TESTS[selected_test]}", Py4GW.Console.MessageType.Info)
            else:
                Py4GW.Console.Log(MODULE_NAME, f"Failed to build tree: {last_error}", Py4GW.Console.MessageType.Error)

        PyImGui.same_line(0, -1)
        if PyImGui.button("Tick Once"):
            _tick_tree()

        PyImGui.same_line(0, -1)
        if PyImGui.button("Stop Tree"):
            tree = None
            auto_tick = False

        auto_tick = PyImGui.checkbox("Auto tick", auto_tick)
        tick_interval_ms = PyImGui.input_int("Tick interval (ms)", int(tick_interval_ms))
        tick_interval_ms = max(25, tick_interval_ms)

        if auto_tick and tree is not None:
            now = Utils.GetBaseTimestamp()
            if now - last_tick_at >= tick_interval_ms:
                _tick_tree()
                last_tick_at = now

        PyImGui.separator()
        PyImGui.text(f"Tree active: {tree is not None}")
        PyImGui.text(f"Last state: {last_state}")
        if last_error:
            PyImGui.text(f"Last error: {last_error}")

    PyImGui.end()
