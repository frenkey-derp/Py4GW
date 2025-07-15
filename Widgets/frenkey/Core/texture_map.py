from enum import Enum
import os

from Py4GWCoreLib.enums import Profession

core_texture_path = __file__.replace("texture_map.py", "textures/")


class CoreTextures(Enum):
    PROFESSION_ICON_SQUARE = "profession_icon_square_{}.png"
    PROFESSION_ICON_SQUARE_HOVERED = "profession_icon_square_{}_hovered.png"

    @staticmethod
    def get_profession_texture(profession: Profession, hovered: bool = False) -> str:

        if hovered:
            return os.path.join(core_texture_path, CoreTextures.PROFESSION_ICON_SQUARE_HOVERED.value.format(profession.name.lower()))

        return CoreTextures.PROFESSION_ICON_SQUARE.value.format(profession.name.lower())

    Assassin = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Assassin.name.lower()))
    Assassin_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Assassin.name.lower()))
    Elementalist = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Elementalist.name.lower()))
    Elementalist_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Elementalist.name.lower()))
    Mesmer = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Mesmer.name.lower()))
    Mesmer_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Mesmer.name.lower()))
    Monk = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Monk.name.lower()))
    Monk_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Monk.name.lower()))
    Necromancer = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Necromancer.name.lower()))
    Necromancer_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Necromancer.name.lower()))
    Ranger = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Ranger.name.lower()))
    Ranger_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Ranger.name.lower()))
    Ritualist = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Ritualist.name.lower()))
    Ritualist_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Ritualist.name.lower()))
    Paragon = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Paragon.name.lower()))
    Paragon_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Paragon.name.lower()))
    Dervish = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Dervish.name.lower()))
    Dervish_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Dervish.name.lower()))
    Warrior = os.path.join(core_texture_path, PROFESSION_ICON_SQUARE.format(
        Profession.Warrior.name.lower()))
    Warrior_Hovered = os.path.join(
        core_texture_path, PROFESSION_ICON_SQUARE_HOVERED.format(Profession.Warrior.name.lower()))
    UI_Checkmark = os.path.join(core_texture_path, "ui_checkmark.png")
    UI_Checkmark_Hovered = os.path.join(core_texture_path, "ui_checkmark_hovered.png")
    Cancel = os.path.join(core_texture_path, "cancel.png")
    Cog = os.path.join(core_texture_path, "cog.png")
    UI_Cancel = os.path.join(core_texture_path, "ui_cancel.png")
    UI_Cancel_Hovered = os.path.join(core_texture_path, "ui_cancel_hovered.png")
    UI_Reward_Bag = os.path.join(core_texture_path, "ui_reward_bag.png")
    UI_Reward_Bag_Hovered = os.path.join(core_texture_path, "ui_reward_bag_hovered.png")
    UI_Destroy = os.path.join(core_texture_path, "ui_destroy.png")
    UI_Show_Always = os.path.join(core_texture_path, "ui_show_always.png")
    UI_Show_Always_Hovered = os.path.join(core_texture_path, "ui_show_always_hovered.png")
    UI_Show_Explorable = os.path.join(core_texture_path, "ui_show_explorable.png")
    UI_Show_Explorable_Hovered = os.path.join(core_texture_path, "ui_show_explorable_hovered.png")
    UI_Show_Never = os.path.join(core_texture_path, "ui_show_never.png")
    UI_Show_Never_Hovered = os.path.join(core_texture_path, "ui_show_never_hovered.png")
    UI_Show_PvP = os.path.join(core_texture_path, "ui_show_pvp.png")
    UI_Show_PvP_Hovered = os.path.join(core_texture_path, "ui_show_pvp_hovered.png")
    UI_Inventory_Slot = os.path.join(core_texture_path, "ui_inventory_slot_background_ex.png")
    UI_Platinum = os.path.join(core_texture_path, "ui_platinum.png")
    UI_Gold = os.path.join(core_texture_path, "ui_gold.png")
    UI_Up = os.path.join(core_texture_path, "ui_up.png")
    UI_Up_Hovered = os.path.join(core_texture_path, "ui_up_hovered.png")
    UI_Up_Active = os.path.join(core_texture_path, "ui_up_active.png")
    UI_Down = os.path.join(core_texture_path, "ui_down.png")
    UI_Down_Hovered = os.path.join(core_texture_path, "ui_down_hovered.png")
    UI_Down_Active = os.path.join(core_texture_path, "ui_down_active.png")
    UI_Help_Icon = os.path.join(core_texture_path, "ui_help_icon.png")
    UI_Help_Icon_Hovered = os.path.join(core_texture_path, "ui_help_icon_hovered.png")
    UI_Help_Icon_Active = os.path.join(core_texture_path, "ui_help_icon_active.png")
