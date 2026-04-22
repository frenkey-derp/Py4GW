from __future__ import annotations

import argparse
from pathlib import Path

from Py4GWCoreLib.enums_src.GameData_enums import PROFESSION_ATTRIBUTES, Attribute, Profession
from Py4GWCoreLib.item_mods_src.types import ItemBaneSpecies
from Py4GWCoreLib.item_mods_src.upgrades import ArmorVsSpeciesUpgrade, HalvesCastingTimeAttributeUpgrade, HalvesRechargeTimeAttributeUpgrade


def camelize_enum_name(name: str) -> str:
    return "".join(part for part in name.replace("_", " ").split())


def render_of_attribute_specializations() -> tuple[str, list[str]]:
    handwritten_attributes = {
        Attribute.AxeMastery,
        Attribute.DaggerMastery,
        Attribute.HammerMastery,
        Attribute.Marksmanship,
        Attribute.ScytheMastery,
        Attribute.SpearMastery,
        Attribute.Swordsmanship,
    }

    generated_names: list[str] = []
    blocks: list[str] = []

    for profession in Profession:
        if profession == Profession._None:
            continue

        for attribute in PROFESSION_ATTRIBUTES.get(profession, []):
            if attribute in handwritten_attributes:
                continue

            class_name = f"Of{camelize_enum_name(attribute.name)}Upgrade"
            generated_names.append(class_name)
            blocks.append(
                f"""@dataclass(eq=False)
class {class_name}(OfAttributeUpgrade):
    attribute = Attribute.{attribute.name}

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute",
            fixed_value=Attribute.{attribute.name},
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.AttributePlusOne,
            target="attribute_level",
            fixed_value=1,
            value_getter=property_value(
                AttributePlusOne,
                lambda prop: prop.attribute_level,
            ),
        ),
    )"""
            )

    return "\n\n".join(blocks), generated_names


def render_of_the_profession_specializations() -> tuple[str, list[str]]:
    generated_names: list[str] = []
    blocks: list[str] = []

    for profession in Profession:
        if profession == Profession._None:
            continue

        attributes = PROFESSION_ATTRIBUTES.get(profession, [])
        if not attributes:
            continue

        primary_attribute = next((attribute for attribute in attributes if attribute.is_primary), attributes[0])
        class_name = f"OfThe{camelize_enum_name(profession.name)}Upgrade"
        generated_names.append(class_name)
        blocks.append(
            f"""@dataclass(eq=False)
class {class_name}(OfTheProfessionUpgrade):
    profession = Profession.{profession.name}
    attribute = Attribute.{primary_attribute.name}

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.OfTheProfession,
            target="attribute",
            fixed_value=Attribute.{primary_attribute.name},
            value_getter=property_value(
                OfTheProfession,
                lambda prop: prop.attribute,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.OfTheProfession,
            target="attribute_level",
            min_value=4,
            max_value=5,
            value_getter=property_value(
                OfTheProfession,
                lambda prop: prop.attribute_level,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.OfTheProfession,
            target="profession",
            fixed_value=Profession.{profession.name},
            value_getter=property_value(
                OfTheProfession,
                lambda prop: prop.profession,
            ),
        ),
    )"""
        )

    return "\n\n".join(blocks), generated_names


def render_slaying_specializations() -> tuple[str, list[str]]:
    generated_names: list[str] = []
    blocks: list[str] = []

    for species in ItemBaneSpecies:
        if species == ItemBaneSpecies.Unknown:
            continue

        class_name = f"Of{camelize_enum_name(species.name)}SlayingUpgrade"
        generated_names.append(class_name)
        blocks.append(
            f"""@dataclass(eq=False)
class {class_name}(OfSlayingUpgrade):
    species = ItemBaneSpecies.{species.name}

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.DamagePlusVsSpecies,
            target="species",
            fixed_value=ItemBaneSpecies.{species.name},
            value_getter=property_value(
                DamagePlusVsSpecies,
                lambda prop: prop.species,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.DamagePlusVsSpecies,
            target="damage_increase",
            min_value=15,
            max_value=20,
            value_getter=property_value(
                DamagePlusVsSpecies,
                lambda prop: prop.damage_increase,
            ),
        ),
    )"""
        )

    return "\n\n".join(blocks), generated_names


def render_vs_species_specializations() -> tuple[str, list[str]]:
    generated_names: list[str] = []
    blocks: list[str] = []

    for species in ItemBaneSpecies:
        if species == ItemBaneSpecies.Unknown:
            continue

        class_name = f"ArmorVs{camelize_enum_name(species.name)}Upgrade"
        generated_names.append(class_name)
        blocks.append(
            f"""@dataclass(eq=False)
class {class_name}(ArmorVsSpeciesUpgrade):
    species = ItemBaneSpecies.{species.name}

    upgrade_info = (
        fixed(
            identifier=ModifierIdentifier.ArmorPlusVsSpecies,
            target="species",
            fixed_value=ItemBaneSpecies.{species.name},
            value_getter=property_value(
                ArmorPlusVsSpecies,
                lambda prop: prop.species,
            ),
        ),
        ranged(
            identifier=ModifierIdentifier.ArmorPlusVsSpecies,
            target="armor",
            min_value=5,
            max_value=10,
            value_getter=property_value(
                ArmorPlusVsSpecies,
                lambda prop: prop.armor,
            ),
        ),
    )"""
        )

    return "\n\n".join(blocks), generated_names

def render_HalvesRechargeTimeAttributeUpgrade() -> tuple[str, list[str]]:
    generated_names: list[str] = []
    blocks: list[str] = []
    
    for profession in Profession:
        if profession not in [Profession.Monk, Profession.Necromancer, Profession.Mesmer, Profession.Elementalist, Profession.Ritualist]:
            continue

        for attribute in PROFESSION_ATTRIBUTES.get(profession, []):
            class_name = f"HalvesRechargeTimeOf{camelize_enum_name(attribute.name)}Upgrade"
            generated_names.append(class_name)
            blocks.append(
                f"""@dataclass(eq=False)
class {class_name}(HalvesRechargeTimeAttributeUpgrade):
    attribute = Attribute.{attribute.name}

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesSkillRechargeAttribute,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                HalvesSkillRechargeAttribute,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.HalvesSkillRechargeAttribute,
            target="attribute",
            fixed_value=Attribute.{attribute.name},
            value_getter=property_value(
                HalvesSkillRechargeAttribute,
                lambda prop: prop.attribute,
            ),
        ),
    )"""
            )
            

    return "\n\n".join(blocks), generated_names
            
def render_HalvesCastingTimeAttributeUpgrade() -> tuple[str, list[str]]:
    generated_names: list[str] = []
    blocks: list[str] = []
    
    for profession in Profession:
        if profession not in [Profession.Monk, Profession.Necromancer, Profession.Mesmer, Profession.Elementalist, Profession.Ritualist]:
            continue

        for attribute in PROFESSION_ATTRIBUTES.get(profession, []):
            class_name = f"HalvesCastingTimeOf{camelize_enum_name(attribute.name)}Upgrade"
            generated_names.append(class_name)
            blocks.append(
                f"""@dataclass(eq=False)
class {class_name}(HalvesCastingTimeAttributeUpgrade):
    attribute = Attribute.{attribute.name}

    upgrade_info = (
        ranged(
            identifier=ModifierIdentifier.HalvesCastingTimeAttribute,
            target="chance",
            min_value=10,
            max_value=20,
            value_getter=property_value(
                HalvesCastingTimeAttribute,
                lambda prop: prop.chance,
            ),
        ),
        fixed(
            identifier=ModifierIdentifier.HalvesCastingTimeAttribute,
            target="attribute",
            fixed_value=Attribute.{attribute.name},
            value_getter=property_value(
                HalvesCastingTimeAttribute,
                lambda prop: prop.attribute,
            ),
        ),
    )"""
            )
            

    return "\n\n".join(blocks), generated_names
            

def build_output() -> str:
    renders = [
        # render_of_attribute_specializations,
        # render_of_the_profession_specializations,
        # render_slaying_specializations,
        render_vs_species_specializations,
        render_HalvesRechargeTimeAttributeUpgrade,
        render_HalvesCastingTimeAttributeUpgrade,
    ]
    
    sections : list[str] = []
    names : list[str] = []
    
    for render in renders:
        block, class_names = render()
        if block:
            sections.append(block)
        
        if class_names:
            names.extend(class_names)
            
    return "\n".join(section for section in sections if section is not None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate hard-coded upgrade specialization classes.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/generated_upgrade_specializations.py"),
        help="File to write the generated code into.",
    )
    args = parser.parse_args()

    imports = """from dataclasses import dataclass
from Py4GWCoreLib.enums_src.GameData_enums import Attribute, Profession
from Py4GWCoreLib.item_mods_src.properties import ArmorPlusVsSpecies, AttributePlusOne, DamagePlusVsSpecies, HalvesCastingTimeAttribute, HalvesSkillRechargeAttribute, OfTheProfession
from Py4GWCoreLib.item_mods_src.types import ItemBaneSpecies, ModifierIdentifier
from Py4GWCoreLib.item_mods_src.upgrades import ArmorVsSpeciesUpgrade, HalvesCastingTimeAttributeUpgrade, HalvesRechargeTimeAttributeUpgrade, OfAttributeUpgrade, OfSlayingUpgrade, OfTheProfessionUpgrade, enum, fixed, property_value, ranged
"""
    
    output_text = build_output()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(imports + "\n\n" + output_text, encoding="utf-8")
    print(f"Wrote generated upgrade specializations to {args.output}")


if __name__ == "__main__":
    main()
