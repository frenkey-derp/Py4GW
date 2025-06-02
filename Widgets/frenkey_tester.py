from Py4GWCoreLib import *

MODULE_NAME = "frenkey_tester"

# "3613855137": "merchant window",
# "3613855137,0": "merchant window inner",
# "3068881268": "merchant window your funds",
# "1532320307": "merchant window buy button"

# "684387150": "Salvage Window",
# "684387150,1": "Salvage Window.Cancel Button",
# "684387150,2": "Salvage Window.Salvage Button",
# "684387150,3": "Salvage Window,Salvage Details",
# "684387150,4": "Salvage Window.Header Label",

# "684387150,5": "Salvage Window.Options",
# "684387150,5,0": "Salvage Window.Options.Option1",
# "684387150,5,1": "Salvage Window.Options.Option2",
# "684387150,5,2": "Salvage Window.Options.Option3"
# "684387150,5,3": "Salvage Window.Options.Materials",

# "140452905,6,98": "Salvage Materials Dialog",
# "140452905,6,98,4": "Salvage Materials Dialog.No Button",
# "140452905,6,98,6": "Salvage Materials Dialog.Yes Button",

def color_bool_text(label: str, value: bool):
    color = Utils.RGBToNormal(0, 255, 0, 255) if value else Utils.RGBToNormal(255, 0, 0, 255)
    PyImGui.text(f"{label}: ")
    PyImGui.same_line(0,-1)
    PyImGui.text_colored(str(value), color)

def is_visible(frame_id):
    return isinstance(frame_id, int) and frame_id > 0

#sometimes is window visible is false positive annoying
def is_visible_test(frame_id):
    return isinstance(frame_id, int) and frame_id > 0 and not UIManager.IsWindowVisible(frame_id)

def draw_visible():
    #Merchant
    merchant_window_frame_id = UIManager.GetFrameIDByHash(3613855137)
    merchant_window_frame_inner_id = UIManager.GetChildFrameID(3613855137, [0])
    merchant_window_funds_id = UIManager.GetFrameIDByHash(3068881268)
    merchant_window_buy_button_id = UIManager.GetFrameIDByHash(1532320307)

    #Salvage
    salvage_window_frame_id = UIManager.GetFrameIDByHash(684387150)
    salvage_window_salvage_button_id = UIManager.GetChildFrameID(684387150, [2])
    salvage_window_cancel_button_id = UIManager.GetChildFrameID(684387150, [1])

    salvage_window_mod_one_id = UIManager.GetChildFrameID(684387150, [5,0])
    salvage_window_mod_two_id = UIManager.GetChildFrameID(684387150, [5,1])
    salvage_window_mod_three_id = UIManager.GetChildFrameID(684387150, [5,2])

    salvage_window_materials_id = UIManager.GetChildFrameID(684387150, [5,3])

    salvage_lower_kit_id = UIManager.GetChildFrameID(140452905, [6,98])
    salvage_lower_kit_yes_button_id = UIManager.GetChildFrameID(140452905, [6,98,6])
    salvage_lower_kit_no_button_id = UIManager.GetChildFrameID(140452905, [6,98,4])


    if PyImGui.begin("frenkey UIManager tester", PyImGui.WindowFlags.AlwaysAutoResize):
        if PyImGui.collapsing_header("Merchant Window Info"):
            PyImGui.spacing()
            PyImGui.text(f"Merchant Window Frame ID: {merchant_window_frame_id}")
            color_bool_text("Merchant Window .IsVisible", UIManager.IsVisible(merchant_window_frame_id))
            color_bool_text("Merchant Window .IsWindowVisible", UIManager.IsWindowVisible(merchant_window_frame_id))
            color_bool_text("Merchant Window is_visible", is_visible(merchant_window_frame_id))
            color_bool_text("Merchant Window is_visible_test", is_visible_test(merchant_window_frame_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Merchant Window Inner Frame ID: {merchant_window_frame_inner_id}")
            color_bool_text("Merchant Window Inner .IsVisible", UIManager.IsVisible(merchant_window_frame_inner_id))
            color_bool_text("Merchant Window Inner .IsWindowVisible", UIManager.IsWindowVisible(merchant_window_frame_inner_id))
            color_bool_text("Merchant Window Inner is_visible", is_visible(merchant_window_frame_inner_id))
            color_bool_text("Merchant Window Inner is_visible_test", is_visible_test(merchant_window_frame_inner_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Merchant Window Funds Frame ID: {merchant_window_funds_id}")
            color_bool_text("Merchant Window Funds .IsVisible", UIManager.IsVisible(merchant_window_funds_id))
            color_bool_text("Merchant Window Funds .IsWindowVisible", UIManager.IsWindowVisible(merchant_window_funds_id))
            color_bool_text("Merchant Window Funds is_visible", is_visible(merchant_window_funds_id))
            color_bool_text("Merchant Window Funds is_visible_test", is_visible_test(merchant_window_funds_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Merchant Window Buy Button Frame ID: {merchant_window_buy_button_id}")
            color_bool_text("Merchant Window Buy Button .IsVisible", UIManager.IsVisible(merchant_window_buy_button_id))
            color_bool_text("Merchant Window Buy Button .IsWindowVisible", UIManager.IsWindowVisible(merchant_window_buy_button_id))
            color_bool_text("Merchant Window Buy Button is_visible", is_visible(merchant_window_buy_button_id))
            color_bool_text("Merchant Window Buy Button is_visible_test", is_visible_test(merchant_window_buy_button_id))
            PyImGui.spacing()
        if PyImGui.collapsing_header("Salvage Window Info"):
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Frame ID: {salvage_window_frame_id}")
            color_bool_text("Salvage Window .IsVisible", UIManager.IsVisible(salvage_window_frame_id))
            color_bool_text("Salvage Window .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_frame_id))
            color_bool_text("Salvage Window is_visible", is_visible(salvage_window_frame_id))
            color_bool_text("Salvage Window is_visible_test", is_visible_test(salvage_window_frame_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window salvage button Frame ID: {salvage_window_salvage_button_id}")
            color_bool_text("Salvage Window salvage button .IsVisible", UIManager.IsVisible(salvage_window_salvage_button_id))
            color_bool_text("Salvage Window salvage button .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_salvage_button_id))
            color_bool_text("Salvage Window salvage button is_visible", is_visible(salvage_window_salvage_button_id))
            color_bool_text("Salvage Window salvage button is_visible_test", is_visible_test(salvage_window_salvage_button_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window cancel button Frame ID: {salvage_window_cancel_button_id}")
            color_bool_text("Salvage Window cancel button .IsVisible", UIManager.IsVisible(salvage_window_cancel_button_id))
            color_bool_text("Salvage Window cancel button .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_cancel_button_id))
            color_bool_text("Salvage Window cancel button is_visible", is_visible(salvage_window_cancel_button_id))
            color_bool_text("Salvage Window cancel button is_visible_test", is_visible_test(salvage_window_cancel_button_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Mod One Frame ID: {salvage_window_mod_one_id}")
            color_bool_text("Salvage Window Mod One .IsVisible", UIManager.IsVisible(salvage_window_mod_one_id))
            color_bool_text("Salvage Window Mod One .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_mod_one_id))
            color_bool_text("Salvage Window Mod One is_visible", is_visible(salvage_window_mod_one_id))
            color_bool_text("Salvage Window Mod One is_visible_test", is_visible_test(salvage_window_mod_one_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Mod Two Frame ID: {salvage_window_mod_two_id}")
            color_bool_text("Salvage Window Mod Two .IsVisible", UIManager.IsVisible(salvage_window_mod_two_id))
            color_bool_text("Salvage Window Mod Two .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_mod_two_id))
            color_bool_text("Salvage Window Mod Two is_visible", is_visible(salvage_window_mod_two_id))
            color_bool_text("Salvage Window Mod Two is_visible_test", is_visible_test(salvage_window_mod_two_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Mod Three Frame ID: {salvage_window_mod_three_id}")
            color_bool_text("Salvage Window Mod Three .IsVisible", UIManager.IsVisible(salvage_window_mod_three_id))
            color_bool_text("Salvage Window Mod Three .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_mod_three_id))
            color_bool_text("Salvage Window Mod Three is_visible", is_visible(salvage_window_mod_three_id))
            color_bool_text("Salvage Window Mod Three is_visible_test", is_visible_test(salvage_window_mod_three_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Materials Frame ID: {salvage_window_materials_id}")
            color_bool_text("Salvage Window Materials .IsVisible", UIManager.IsVisible(salvage_window_materials_id))
            color_bool_text("Salvage Window Materials .IsWindowVisible", UIManager.IsWindowVisible(salvage_window_materials_id))
            color_bool_text("Salvage Window Materials is_visible", is_visible(salvage_window_materials_id))
            color_bool_text("Salvage Window Materials is_visible_test", is_visible_test(salvage_window_materials_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Lower Kit Frame ID: {salvage_lower_kit_id}")
            color_bool_text("Salvage Window Lower Kit .IsVisible", UIManager.IsVisible(salvage_lower_kit_id))
            color_bool_text("Salvage Window Lower Kit .IsWindowVisible", UIManager.IsWindowVisible(salvage_lower_kit_id))
            color_bool_text("Salvage Window Lower Kit is_visible", is_visible(salvage_lower_kit_id))
            color_bool_text("Salvage Window Lower Kit is_visible_test", is_visible_test(salvage_lower_kit_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Lower Kit Yes Button Frame ID: {salvage_lower_kit_yes_button_id}")
            color_bool_text("Salvage Window Lower Kit Yes Button .IsVisible", UIManager.IsVisible(salvage_lower_kit_yes_button_id))
            color_bool_text("Salvage Window Lower Kit Yes Button .IsWindowVisible", UIManager.IsWindowVisible(salvage_lower_kit_yes_button_id))
            color_bool_text("Salvage Window Lower Kit Yes Button is_visible", is_visible(salvage_lower_kit_yes_button_id))
            color_bool_text("Salvage Window Lower Kit Yes Button is_visible_test", is_visible_test(salvage_lower_kit_yes_button_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
            PyImGui.text(f"Salvage Window Lower Kit No Button Frame ID: {salvage_lower_kit_no_button_id}")
            color_bool_text("Salvage Window Lower Kit No Button .IsVisible", UIManager.IsVisible(salvage_lower_kit_no_button_id))
            color_bool_text("Salvage Window Lower Kit No Button .IsWindowVisible", UIManager.IsWindowVisible(salvage_lower_kit_no_button_id))
            color_bool_text("Salvage Window Lower Kit No Button is_visible", is_visible(salvage_lower_kit_no_button_id))
            color_bool_text("Salvage Window Lower Kit No Button is_visible_test", is_visible_test(salvage_lower_kit_no_button_id))
            PyImGui.spacing()
            PyImGui.separator()
            PyImGui.spacing()
    
        PyImGui.text("Summary:")
        color_bool_text("Is the Merchant Window Visible?", is_visible(merchant_window_frame_id))
        color_bool_text("Is the Salvage Window Visible?", is_visible(salvage_window_frame_id))
        
        color_bool_text("Mod 1", is_visible(salvage_window_mod_one_id))
        color_bool_text("Mod 2", is_visible(salvage_window_mod_two_id))
        color_bool_text("Mod 3", is_visible(salvage_window_mod_three_id))
        color_bool_text("Materials", is_visible(salvage_window_materials_id))
        
        mods_visible = sum(is_visible(fid) for fid in [
            salvage_window_mod_one_id,
            salvage_window_mod_two_id,
            salvage_window_mod_three_id
        ])
        PyImGui.text(f"How many mods are salvagable: {mods_visible}")
        color_bool_text("Are materials available in the salvage?", is_visible(salvage_window_materials_id))
        color_bool_text("Using a lower kit?", is_visible(salvage_lower_kit_id))


    PyImGui.end()

def configure():
    pass
     
def main():
    draw_visible()
    
    
__all__ = ['main', 'configure']