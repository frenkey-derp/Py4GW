from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import unquote

from bs4 import BeautifulSoup
from bs4 import Tag


REPO_ROOT = Path(__file__).resolve().parents[2]
PAGES_DIR = Path(r'F:\Programmieren\Frenkey\scraped_wiki\pages')
ITEMS_JSON_PATH = REPO_ROOT / 'Py4GWCoreLib' / 'item_data' / 'items.json'
MAP_ENUMS_PATH = REPO_ROOT / 'Py4GWCoreLib' / 'enums_src' / 'Map_enums.py'
LEGACY_ARMORERS_PATH = Path(__file__).resolve().with_name('armor_crafters.json')
OUTPUT_PATH = Path(__file__).resolve().with_name('crafter_catalog.json')
OUTPUT_DIRECTORY_PATH = Path(__file__).resolve().with_name('npc_catalog')
CATEGORY_KEYS = [
    'armorers',
    'artisans',
    'consumable_crafters',
    'weaponsmiths',
    'collectors',
    'merchants',
    'traders',
    'allies',
    'foes',
]

PROFESSIONS = [
    'Warrior',
    'Ranger',
    'Monk',
    'Necromancer',
    'Mesmer',
    'Elementalist',
    'Assassin',
    'Ritualist',
    'Paragon',
    'Dervish',
]
PROFESSION_SET = set(PROFESSIONS)

ATTRIBUTES = {
    'fast casting': 'FastCasting',
    'illusion magic': 'IllusionMagic',
    'domination magic': 'DominationMagic',
    'inspiration magic': 'InspirationMagic',
    'blood magic': 'BloodMagic',
    'death magic': 'DeathMagic',
    'soul reaping': 'SoulReaping',
    'curses': 'Curses',
    'air magic': 'AirMagic',
    'earth magic': 'EarthMagic',
    'fire magic': 'FireMagic',
    'water magic': 'WaterMagic',
    'energy storage': 'EnergyStorage',
    'healing prayers': 'HealingPrayers',
    'smiting prayers': 'SmitingPrayers',
    'protection prayers': 'ProtectionPrayers',
    'divine favor': 'DivineFavor',
    'strength': 'Strength',
    'axe mastery': 'AxeMastery',
    'hammer mastery': 'HammerMastery',
    'swordsmanship': 'Swordsmanship',
    'tactics': 'Tactics',
    'beast mastery': 'BeastMastery',
    'expertise': 'Expertise',
    'wilderness survival': 'WildernessSurvival',
    'marksmanship': 'Marksmanship',
    'dagger mastery': 'DaggerMastery',
    'deadly arts': 'DeadlyArts',
    'shadow arts': 'ShadowArts',
    'communing': 'Communing',
    'restoration magic': 'RestorationMagic',
    'channeling magic': 'ChannelingMagic',
    'critical strikes': 'CriticalStrikes',
    'spawning power': 'SpawningPower',
    'spear mastery': 'SpearMastery',
    'command': 'Command',
    'motivation': 'Motivation',
    'leadership': 'Leadership',
    'scythe mastery': 'ScytheMastery',
    'wind prayers': 'WindPrayers',
    'earth prayers': 'EarthPrayers',
    'mysticism': 'Mysticism',
}

ARMOR_HEADER_TO_ITEM_TYPE = {
    'helm': 'Headpiece',
    'mask': 'Headpiece',
    'headpiece': 'Headpiece',
    'headgear': 'Headpiece',
    'headwrap': 'Headpiece',
    'bandana': 'Headpiece',
    'crown': 'Headpiece',
    'scalp design': 'Headpiece',
    'chest design': 'Chestpiece',
    'arm design': 'Gloves',
    'leg design': 'Leggings',
    'foot design': 'Boots',
    'hauberk': 'Chestpiece',
    'vest': 'Chestpiece',
    'vestments': 'Chestpiece',
    'jacket': 'Chestpiece',
    'tunic': 'Chestpiece',
    'coat': 'Chestpiece',
    'breastplate': 'Chestpiece',
    'robes': 'Chestpiece',
    'robe': 'Chestpiece',
    'raiment': 'Chestpiece',
    'cuirass': 'Chestpiece',
    'guise': 'Chestpiece',
    'attire': 'Chestpiece',
    'gloves': 'Gloves',
    'gauntlets': 'Gloves',
    'bangles': 'Gloves',
    'handwraps': 'Gloves',
    'leggings': 'Leggings',
    'pants': 'Leggings',
    'hose': 'Leggings',
    'boots': 'Boots',
    'footwear': 'Boots',
    'shoes': 'Boots',
    'sandals': 'Boots',
}

SERVICE_ALIASES = {
    'armorer': 'armorers',
    'weaponsmith': 'weaponsmiths',
    'artisan': 'artisans',
    'consumable crafter': 'consumable_crafters',
    'collector': 'collectors',
}

ITEM_TYPE_FALLBACKS = [
    ('scythe', 'Scythe'),
    ('dagger', 'Daggers'),
    ('spear', 'Spear'),
    ('staff', 'Staff'),
    ('wand', 'Wand'),
    ('shield', 'Shield'),
    ('focus', 'Offhand'),
    ('cesta', 'Offhand'),
    ('chakram', 'Offhand'),
    ('totem', 'Offhand'),
    ('idol', 'Offhand'),
    ('sword', 'Sword'),
    ('hammer', 'Hammer'),
    ('axe', 'Axe'),
    ('bow', 'Bow'),
    ('kit', 'Kit'),
    ('scroll', 'Scroll'),
]

SOUP_CACHE: dict[Path, BeautifulSoup] = {}


def normalize_name(value: str) -> str:
    value = unquote(value or '').replace('_', ' ')
    value = value.replace('(s)', '')
    value = value.replace("'", '')
    value = re.sub(r'[^0-9a-zA-Z]+', ' ', value.strip().lower())
    value = re.sub(r'\s+', ' ', value)
    return value


def add_alias(mapping: dict[str, Any], name: str, value: Any):
    candidates = {
        name,
        name.replace('(outpost)', '').strip(),
        name.replace('outpost', '').strip(),
        name.replace('(pre-Searing)', '').replace('(pre searing)', '').strip(),
        name.replace('Pre-Searing:', '').strip(),
    }
    for candidate in list(candidates):
        if '(' in candidate:
            candidates.add(re.sub(r'\s*\([^)]*\)', '', candidate).strip())
    for candidate in candidates:
        normalized = normalize_name(candidate)
        if normalized:
            mapping.setdefault(normalized, value)


def load_items_index() -> dict[str, dict[str, Any]]:
    with ITEMS_JSON_PATH.open('r', encoding='utf-8') as handle:
        payload = json.load(handle)

    by_name: dict[str, dict[str, Any]] = {}
    for item_type_name, entries in payload.items():
        for entry in entries.values():
            record = {
                'name': entry.get('name', ''),
                'item_type': entry.get('item_type', item_type_name),
                'model_id': int(entry.get('model_id', 0) or 0),
                'profession': entry.get('profession'),
                'wiki_url': entry.get('wiki_url', ''),
            }
            add_alias(by_name, record['name'], record)
            wiki_slug = record['wiki_url'].split('/wiki/')[-1] if '/wiki/' in record['wiki_url'] else ''
            if wiki_slug:
                add_alias(by_name, wiki_slug, record)

    return by_name


def load_map_index() -> dict[str, int]:
    text = MAP_ENUMS_PATH.read_text(encoding='utf-8')
    index: dict[str, int] = {}
    for map_id, name in re.findall(r'(\d+): "([^"]+)"', text):
        add_alias(index, name, int(map_id))
    add_alias(index, 'Ascalon City (pre-Searing)', 81)
    add_alias(index, 'Ascalon (pre-Searing)', 81)
    return index


def load_legacy_armorer_index() -> dict[tuple[str, int], dict[str, Any]]:
    if not LEGACY_ARMORERS_PATH.exists():
        return {}

    with LEGACY_ARMORERS_PATH.open('r', encoding='utf-8') as handle:
        payload = json.load(handle)

    index: dict[tuple[str, int], dict[str, Any]] = {}
    for entry in payload.get('crafters', []):
        key = (entry.get('name', ''), int(entry.get('map_id', 0) or 0))
        index[key] = entry
    return index


def resolve_local_page(href: str) -> Path | None:
    if not href or '/wiki/' not in href:
        return None

    slug = href.split('/wiki/', 1)[1]
    slug = slug.split('#', 1)[0]
    slug = slug.split('?', 1)[0]
    candidates = [
        unquote(slug),
        slug,
        unquote(slug).replace('%27', "'"),
    ]
    for candidate in candidates:
        path = PAGES_DIR / f'{candidate}.html'
        if path.exists():
            return path
    return None


def clean_text(value: str) -> str:
    return re.sub(r'\s+', ' ', value.replace('\xa0', ' ').strip())


def extract_service(soup: BeautifulSoup) -> str | None:
    infobox = soup.find('table', class_='infobox')
    if infobox is None:
        return None

    for row in infobox.find_all('tr'):
        header = row.find('th')
        value = row.find('td')
        if header is None or value is None:
            continue
        if clean_text(header.get_text(' ', strip=True)) == 'Service':
            service = clean_text(value.get_text(' ', strip=True)).lower()
            return SERVICE_ALIASES.get(service)
    return None


def load_soup(path: Path) -> BeautifulSoup:
    cached = SOUP_CACHE.get(path)
    if cached is not None:
        return cached

    soup = BeautifulSoup(path.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
    SOUP_CACHE[path] = soup
    return soup


def find_section_table(soup: BeautifulSoup, section_id: str) -> Tag | None:
    header = soup.find(id=section_id)
    if header is None:
        return None

    node = header.parent
    start_level = int(node.name[1]) if node.name and re.fullmatch(r'h[1-6]', node.name) else None
    while node is not None:
        node = node.find_next_sibling()
        if node is None:
            return None
        if node.name and re.fullmatch(r'h[1-6]', node.name):
            next_level = int(node.name[1])
            if start_level is None or next_level <= start_level:
                return None
        if node.name == 'table':
            return node
    return None


def find_section_block(soup: BeautifulSoup, section_id: str) -> list[Tag]:
    header = soup.find(id=section_id)
    if header is None:
        return []

    blocks: list[Tag] = []
    node = header.parent
    start_level = int(node.name[1]) if node.name and re.fullmatch(r'h[1-6]', node.name) else None
    while node is not None:
        node = node.find_next_sibling()
        if node is None:
            break
        if node.name and re.fullmatch(r'h[1-6]', node.name):
            next_level = int(node.name[1])
            if start_level is None or next_level <= start_level:
                break
        if isinstance(node, Tag):
            blocks.append(node)
    return blocks


def parse_location_name(soup: BeautifulSoup) -> str:
    blocks = find_section_block(soup, 'Locations')
    if not blocks:
        blocks = find_section_block(soup, 'Location')
    if blocks:
        blocks = [blocks[0]]
    for block in blocks:
        if block.name == 'ul':
            nested_items = block.find_all('li')
            if nested_items:
                anchor = nested_items[-1].find('a', href=True)
                if anchor is not None:
                    return clean_text(anchor.get('title') or anchor.get_text(' ', strip=True))

    links: list[str] = []
    for block in blocks:
        for anchor in block.find_all('a', href=True):
            title = clean_text(anchor.get('title') or anchor.get_text(' ', strip=True))
            if title:
                links.append(title)
    return links[-1] if links else ''


def resolve_map_id(map_name: str, map_index: dict[str, int]) -> int:
    if not map_name:
        return 0
    normalized = normalize_name(map_name)
    if normalized in map_index:
        return map_index[normalized]
    simplified = re.sub(r'\s*\([^)]*\)', '', map_name).strip()
    return map_index.get(normalize_name(simplified), 0)


def table_to_grid(table: Tag) -> list[list[Tag | None]]:
    grid: list[list[Tag | None]] = []
    spans: dict[int, tuple[Tag, int]] = {}

    for tr in table.find_all('tr'):
        row: list[Tag | None] = []
        col = 0

        def fill_spans():
            nonlocal col
            while col in spans:
                cell, remaining = spans[col]
                row.append(cell)
                if remaining <= 1:
                    spans.pop(col)
                else:
                    spans[col] = (cell, remaining - 1)
                col += 1

        fill_spans()
        for cell in tr.find_all(['th', 'td'], recursive=False):
            fill_spans()
            rowspan = int(cell.get('rowspan', 1) or 1)
            colspan = int(cell.get('colspan', 1) or 1)
            for offset in range(colspan):
                row.append(cell)
                if rowspan > 1:
                    spans[col + offset] = (cell, rowspan - 1)
            col += colspan
        fill_spans()
        grid.append(row)

    return grid


def parse_gold_cost(cell: Tag) -> int:
    html = str(cell)
    gold = 0
    for amount, currency in re.findall(r'(\d+)\s*<a[^>]+title="([^"]+)"', html):
        if currency == 'Gold':
            gold += int(amount)
        elif currency == 'Platinum':
            gold += int(amount) * 1000

    if gold == 0:
        text = clean_text(cell.get_text(' ', strip=True))
        match = re.search(r'\d+', text)
        if match:
            gold = int(match.group(0))
    return gold


def resolve_item_record(name: str, items_index: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    normalized = normalize_name(name)
    candidates = [normalized]

    if normalized.endswith('s'):
        candidates.append(normalized[:-1])

    if ' of ' in normalized:
        first, rest = normalized.split(' of ', 1)
        if first.endswith('s'):
            candidates.append(f'{first[:-1]} of {rest}')

    for candidate in candidates:
        record = items_index.get(candidate)
        if record is not None:
            return record

    return None


def resolve_item_type(name: str, record: dict[str, Any] | None, default: str = 'Unknown') -> str:
    if record is not None:
        return str(record.get('item_type', default) or default)

    normalized = normalize_name(name)
    for needle, item_type in ITEM_TYPE_FALLBACKS:
        if needle in normalized:
            return item_type
    return default


def resolve_material_title(title: str) -> str:
    title = clean_text(title)
    title = title.removesuffix('(s)').strip()
    if title.endswith('s') and title[:-1].endswith(')'):
        title = title[:-1]
    return title


def parse_material_requirements(cell: Tag, items_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    html = str(cell)
    materials: dict[str, int] = defaultdict(int)
    unresolved: list[str] = []
    skill_points = 0

    for amount in re.findall(r'(\d+)\s*<a[^>]+title="Skill Point"', html):
        skill_points += int(amount)

    for amount, title in re.findall(r'(\d+)\s*<a[^>]+title="([^"]+)"', html):
        if title in {'Skill Point', 'Gold', 'Platinum', 'Currency'}:
            continue
        item_record = resolve_item_record(resolve_material_title(title), items_index)
        if item_record is None:
            unresolved.append(resolve_material_title(title))
            continue
        materials[str(int(item_record['model_id']))] += int(amount)

    payload: dict[str, Any] = {
        'materials': dict(sorted(materials.items(), key=lambda entry: int(entry[0]))),
        'gold': 0,
        'skill_points': skill_points or None,
    }
    if unresolved:
        payload['_unresolved_materials'] = sorted(set(unresolved))
    return payload


def parse_profession(cell: Tag) -> str | None:
    for tag in cell.find_all(['a', 'img']):
        title = tag.get('title') or tag.get('alt')
        if title in PROFESSION_SET:
            return title
    text = clean_text(cell.get_text(' ', strip=True))
    return text if text in PROFESSION_SET else None


def parse_requirement(cell: Tag) -> tuple[int, str]:
    match = re.search(r'(\d+)\s*<a[^>]+title="([^"]+)"', str(cell))
    if match is None:
        return 0, 'None_'
    attribute = ATTRIBUTES.get(normalize_name(match.group(2)), 'None_')
    return int(match.group(1)), attribute


def parse_damage_range(cell: Tag) -> tuple[int, int]:
    match = re.search(r'(\d+)\s*-\s*(\d+)', clean_text(cell.get_text(' ', strip=True)))
    if match is None:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def parse_profession_text(value: str) -> str | None:
    cleaned = clean_text(value)
    if cleaned in PROFESSION_SET:
        return cleaned
    return None


def parse_item_page_profession(page_path: Path | None) -> str | None:
    if page_path is None or not page_path.exists():
        return None

    soup = load_soup(page_path)
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            header = row.find('th')
            value = row.find('td')
            if header is None or value is None:
                continue
            if clean_text(header.get_text(' ', strip=True)) != 'Profession':
                continue
            profession = parse_profession(value)
            if profession is not None:
                return profession
            text_value = clean_text(value.get_text(' ', strip=True))
            if text_value == 'Any':
                return 'Any'
            return parse_profession_text(text_value)
    return None


def resolve_armor_item_type(name: str) -> str:
    normalized = normalize_name(name)
    for header_text, item_type in ARMOR_HEADER_TO_ITEM_TYPE.items():
        if normalize_name(header_text) in normalized:
            return item_type
    return 'Unknown'


def armor_rating_for_profession(profession: str | None) -> int:
    if profession in {'Warrior', 'Paragon'}:
        return 80
    if profession in {'Ranger', 'Assassin', 'Dervish'}:
        return 70
    if profession in {'Monk', 'Necromancer', 'Mesmer', 'Elementalist', 'Ritualist'}:
        return 60
    return 0




def parse_item_anchor(cell: Tag) -> tuple[str, str]:
    for anchor in cell.find_all('a', href=True):
        text = clean_text(anchor.get_text(' ', strip=True))
        if not text:
            continue
        href = anchor.get('href', '')
        if href.startswith('/wiki/File:'):
            continue
        return text, anchor.get('title') or text
    return clean_text(cell.get_text(' ', strip=True)), clean_text(cell.get_text(' ', strip=True))


def parse_simple_item_table(
    soup: BeautifulSoup,
    section_id: str,
    item_field_name: str,
    items_index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    table = find_section_table(soup, section_id)
    if table is None:
        return []

    rows = table.find_all('tr')
    items: list[dict[str, Any]] = []
    for row in rows[1:]:
        cells = row.find_all('td', recursive=False)
        if len(cells) < 3:
            continue
        item_name, _ = parse_item_anchor(cells[0])
        record = resolve_item_record(item_name, items_index)
        requirements = parse_material_requirements(cells[1], items_index)
        requirements['gold'] = parse_gold_cost(cells[2])
        items.append(
            {
                'name': item_name,
                'item_type': resolve_item_type(item_name, record),
                'model_id': 0 if record is None else int(record['model_id']),
                'required_materials': requirements,
            }
        )
    return items


def parse_weaponsmith_items(soup: BeautifulSoup, items_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    table = find_section_table(soup, 'Weapons_offered')
    if table is None:
        return []

    weapons: list[dict[str, Any]] = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td', recursive=False)
        if len(cells) < 7:
            continue
        profession = parse_profession(cells[0]) or 'None'
        item_name, _ = parse_item_anchor(cells[1])
        record = resolve_item_record(item_name, items_index)
        requirements = parse_material_requirements(cells[5], items_index)
        requirements['gold'] = parse_gold_cost(cells[6])
        requirement, attribute = parse_requirement(cells[3])
        weapons.append(
            {
                'name': item_name,
                'item_type': resolve_item_type(item_name, record, default='Weapon'),
                'model_id': 0 if record is None else int(record['model_id']),
                'required_materials': requirements,
                'requirement': requirement,
                'attribute': attribute,
                'damage': list(parse_damage_range(cells[2])),
                'prefix': None,
                'suffix': None,
                'inscription': None,
                'inherent': [],
                '_profession': profession,
            }
        )
    return weapons


def parse_collector_items(soup: BeautifulSoup, items_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    blocks = find_section_block(soup, 'Collector_items')
    if not blocks:
        return []

    requirement_text = ''
    table: Tag | None = None
    for block in blocks:
        if block.name == 'p' and 'Collecting:' in block.get_text(' ', strip=True):
            requirement_text = clean_text(block.get_text(' ', strip=True))
        if block.name == 'table':
            table = block
            break

    shared_collectible: tuple[int, int] | None = None
    unresolved_collectible_name: str | None = None
    match = re.search(r'Collecting:\s*(?:(\d+)\s+)?(.+)$', requirement_text)
    if match:
        collectible_amount = int(match.group(1) or 1)
        collectible_name = clean_text(match.group(2))
        trophy_record = resolve_item_record(collectible_name, items_index)
        if trophy_record is not None:
            shared_collectible = (int(trophy_record['model_id']), collectible_amount)
        else:
            shared_collectible = (0, collectible_amount)
            unresolved_collectible_name = collectible_name

    if table is None:
        return []

    header_cells = table.find_all('tr')[0].find_all(['th', 'td'], recursive=False) if table.find('tr') is not None else []
    header_texts = [clean_text(cell.get_text(' ', strip=True)) for cell in header_cells]
    is_weapon_table = 'Requirement' in header_texts and 'Stats' in header_texts
    is_armor_table = 'AR' in header_texts and 'Item' in header_texts

    items: list[dict[str, Any]] = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td', recursive=False)
        if len(cells) < 1:
            continue
        item_name, _ = parse_item_anchor(cells[0 if is_weapon_table else 0 if not is_armor_table else 2])
        record = resolve_item_record(item_name, items_index)
        item_page_path = None
        anchor_cell = cells[0 if is_weapon_table else 0 if not is_armor_table else 2]
        anchor = anchor_cell.find('a', href=True)
        if anchor is not None:
            item_page_path = resolve_local_page(anchor.get('href', ''))
        entry = {
            'kind': 'collector_item',
            'name': item_name,
            'item_type': resolve_item_type(item_name, record),
            'model_id': 0 if record is None else int(record['model_id']),
            'required_collectible': list(shared_collectible) if shared_collectible is not None else None,
        }

        if is_weapon_table and len(cells) >= 3:
            requirement, attribute = parse_requirement(cells[2])
            entry.update(
                {
                    'kind': 'collectible_weapon',
                    'requirement': requirement,
                    'attribute': attribute,
                    'damage': list(parse_damage_range(cells[1])),
                    'prefix': None,
                    'suffix': None,
                    'inscription': None,
                    'inherent': [],
                }
            )
        elif is_armor_table and len(cells) >= 4:
            profession = parse_profession(cells[0])
            if profession is None and record is not None:
                profession = str(record.get('profession') or '') or None
            if profession is None:
                profession = parse_item_page_profession(item_page_path)

            armor_rating_text = clean_text(cells[3].get_text(' ', strip=True)) if len(cells) >= 4 else ''
            armor_rating_match = re.search(r'\d+', armor_rating_text)
            armor_rating = int(armor_rating_match.group(0)) if armor_rating_match is not None else armor_rating_for_profession(profession)

            entry.update(
                {
                    'kind': 'collectible_armor',
                    'item_type': resolve_item_type(item_name, record, default=resolve_armor_item_type(item_name)),
                    'profession': profession if profession in PROFESSION_SET else 'Any' if profession == 'Any' else 'None',
                    'armor_rating': armor_rating,
                }
            )

        if unresolved_collectible_name is not None:
            entry['_required_collectible_name'] = unresolved_collectible_name
        items.append(entry)
    return items


def build_placeholder_armor_name(profession: str, armor_page_title: str, item_type: str) -> str:
    base_name = armor_page_title.removeprefix(f'{profession} ').removesuffix(' armor').strip()
    if not base_name:
        base_name = armor_page_title
    return f'{base_name} {item_type}'


def _legacy_name_matches_placeholder(placeholder_name: str, legacy_name: str) -> bool:
    placeholder_normalized = normalize_name(placeholder_name)
    legacy_normalized = normalize_name(legacy_name)
    if not placeholder_normalized or not legacy_normalized:
        return False
    if placeholder_normalized == legacy_normalized:
        return True
    return placeholder_normalized in legacy_normalized or legacy_normalized in placeholder_normalized


def extract_armor_slot_columns(header_row: list[Tag | None]) -> list[tuple[int, str]]:
    slot_columns: list[tuple[int, str]] = []
    for index, cell in enumerate(header_row):
        if cell is None or index < 4:
            continue
        header_text = clean_text(cell.get_text(' ', strip=True))
        if not header_text:
            continue
        item_type = ARMOR_HEADER_TO_ITEM_TYPE.get(header_text.lower())
        if item_type is None:
            continue
        slot_columns.append((index, item_type))
    return slot_columns


def _cell_has_item_requirement(cell: Tag) -> bool:
    text = clean_text(cell.get_text(' ', strip=True))
    if not text:
        return False

    if cell.find('a', href=True) is not None:
        return True

    return bool(re.search(r'\d', text))


def parse_profession_columns(row: list[Tag | None], start_index: int = 1) -> list[tuple[int, str]]:
    columns: list[tuple[int, str]] = []
    for index, cell in enumerate(row[start_index:], start=start_index):
        if cell is None:
            continue
        profession = parse_profession(cell)
        if profession is None:
            continue
        columns.append((index, profession))
    return columns


def parse_npc_armor_ratings(soup: BeautifulSoup) -> dict[str, int]:
    table = find_section_table(soup, 'Armor_rating')
    if table is None:
        return {}

    rows = table_to_grid(table)
    if len(rows) < 2:
        return {}

    profession_columns = parse_profession_columns(rows[0], start_index=1)
    if not profession_columns:
        return {}

    ratings: dict[str, int] = {}
    rating_row = rows[1]
    for column_index, profession in profession_columns:
        if column_index >= len(rating_row) or rating_row[column_index] is None:
            continue
        match = re.search(r'\d+', clean_text(rating_row[column_index].get_text(' ', strip=True)))
        if match is None:
            continue
        ratings[profession] = int(match.group(0))
    return ratings


def build_direct_armor_page_specs(soup: BeautifulSoup) -> list[tuple[str, Path, list[str]]]:
    specs: list[tuple[str, Path, list[str]]] = []

    for section_id in ['Armor_sets', 'Body_armor']:
        table = find_section_table(soup, section_id)
        if table is None:
            continue

        rows = table_to_grid(table)
        if len(rows) < 3:
            continue

        profession_columns = parse_profession_columns(rows[0], start_index=2)
        if len(rows) > 1:
            alternative_columns = parse_profession_columns(rows[1], start_index=2)
            if len(alternative_columns) > len(profession_columns):
                profession_columns = alternative_columns
        if not profession_columns:
            continue

        for row in rows[2:]:
            if len(row) < 3 or row[0] is None:
                continue

            style_anchor = row[0].find('a', href=True)
            if style_anchor is None:
                continue

            page_path = resolve_local_page(style_anchor.get('href', ''))
            if page_path is None:
                continue

            offered_professions: list[str] = []
            profession_cell_has_links = False
            for column_index, profession in profession_columns:
                if column_index >= len(row):
                    continue
                cell = row[column_index]
                if cell is None:
                    continue
                for anchor in cell.find_all('a', href=True):
                    title = clean_text(anchor.get('title') or '')
                    if re.match(rf"^({'|'.join(PROFESSIONS)}) .+ armor$", title):
                        profession_cell_has_links = True
                        break
                text = clean_text(cell.get_text(' ', strip=True))
                if not text or text == '-':
                    continue
                offered_professions.append(profession)

            # If profession cells already link to profession-specific pages, the
            # regular armorer parser will pick them up from the NPC page.
            if profession_cell_has_links:
                continue

            title = clean_text(style_anchor.get('title') or style_anchor.get_text(' ', strip=True))
            if not title or not offered_professions:
                continue
            specs.append((title, page_path, offered_professions))

    return specs


def build_armor_name_from_page_title(armor_page_title: str, profession: str, item_type: str, slot_count: int) -> str:
    if armor_page_title.startswith(f'{profession} ') and armor_page_title.endswith(' armor'):
        return build_placeholder_armor_name(profession, armor_page_title, item_type)
    if slot_count == 1:
        return armor_page_title
    if armor_page_title.endswith(' armor'):
        base_name = armor_page_title.removesuffix(' armor').strip()
        return f'{base_name} {item_type}'
    return armor_page_title


def append_armor_entry(
    armors: dict[str, list[dict[str, Any]]],
    legacy_armors: dict[tuple[str, str], dict[str, Any]],
    profession: str,
    armor_rating: int,
    item_type: str,
    armor_name: str,
    requirements: dict[str, Any],
):
    legacy_match = legacy_armors.get((profession, item_type))
    model_id = 0
    if legacy_match is not None and _legacy_name_matches_placeholder(armor_name, str(legacy_match.get('name', ''))):
        armor_name = legacy_match.get('name', armor_name)
        model_id = int(legacy_match.get('model_id', 0) or 0)

    armors[profession].append(
        {
            'name': armor_name,
            'armor_rating': armor_rating,
            'item_type': item_type,
            'model_id': model_id,
            'profession': profession,
            'required_materials': requirements,
        }
    )


def parse_armorer_armor_page(
    armor_page_title: str,
    armor_page_path: Path,
    professions_hint: list[str] | None,
    crafter_name: str,
    map_name: str,
    items_index: dict[str, dict[str, Any]],
    legacy_armors: dict[tuple[str, str], dict[str, Any]],
    npc_profession_ratings: dict[str, int],
    armors: dict[str, list[dict[str, Any]]],
    professions_armor_rating: dict[str, int],
    visited_pages: set[Path],
):
    if armor_page_path in visited_pages:
        return
    visited_pages.add(armor_page_path)

    armor_soup = load_soup(armor_page_path)
    table = None
    for candidate in armor_soup.find_all('table'):
        header = candidate.find('th')
        if header and clean_text(header.get_text(' ', strip=True)).startswith('Crafting'):
            table = candidate
            break

    if table is None:
        followed_child_page = False
        for anchor in armor_soup.find_all('a', href=True):
            title = clean_text(anchor.get('title') or '')
            match = re.match(rf"^({'|'.join(PROFESSIONS)}) .+ armor$", title)
            if match is None:
                continue
            profession = match.group(1)
            if professions_hint is not None and profession not in professions_hint:
                continue
            child_path = resolve_local_page(anchor.get('href', ''))
            if child_path is None:
                continue
            followed_child_page = True
            parse_armorer_armor_page(
                title,
                child_path,
                [profession],
                crafter_name,
                map_name,
                items_index,
                legacy_armors,
                npc_profession_ratings,
                armors,
                professions_armor_rating,
                visited_pages,
            )
        if followed_child_page:
            return

        for paragraph in armor_soup.find_all('p'):
            if 'made up of the following pieces' not in clean_text(paragraph.get_text(' ', strip=True)).lower():
                continue
            bullet_list = paragraph.find_next_sibling('ul')
            if bullet_list is None:
                continue
            for anchor in bullet_list.find_all('a', href=True):
                title = clean_text(anchor.get('title') or anchor.get_text(' ', strip=True))
                if not title or title in PROFESSION_SET:
                    continue
                child_path = resolve_local_page(anchor.get('href', ''))
                if child_path is None:
                    continue
                parse_armorer_armor_page(
                    title,
                    child_path,
                    professions_hint,
                    crafter_name,
                    map_name,
                    items_index,
                    legacy_armors,
                    npc_profession_ratings,
                    armors,
                    professions_armor_rating,
                    visited_pages,
                )
            break
        return

    rows = table_to_grid(table)
    if len(rows) < 2:
        return

    slot_columns = extract_armor_slot_columns(rows[1])
    if not slot_columns:
        return

    if professions_hint is not None:
        target_professions = list(professions_hint)
    elif armor_page_title.split(' ', 1)[0] in PROFESSION_SET:
        target_professions = [armor_page_title.split(' ', 1)[0]]
    else:
        target_professions = []

    for row in rows:
        if len(row) < 5 or row[0] is None or row[1] is None:
            continue

        location_text = clean_text(row[0].get_text(' ', strip=True))
        armorer_text = clean_text(row[1].get_text(' ', strip=True))
        if location_text != map_name or armorer_text != crafter_name:
            continue

        row_rating = 0
        if row[2] is not None:
            armor_rating_match = re.search(r'\d+', clean_text(row[2].get_text(' ', strip=True)))
            if armor_rating_match is not None:
                row_rating = int(armor_rating_match.group(0))
        if row_rating == 0 and not target_professions:
            continue

        gold_per_piece = parse_gold_cost(row[3]) if row[3] is not None else 0

        for profession in target_professions:
            armor_rating = npc_profession_ratings.get(profession, row_rating)
            if armor_rating:
                professions_armor_rating[profession] = armor_rating

            for column_index, item_type in slot_columns:
                if column_index >= len(row):
                    continue
                cell = row[column_index]
                if cell is None or not _cell_has_item_requirement(cell):
                    continue

                requirements = parse_material_requirements(cell, items_index)
                requirements['gold'] = gold_per_piece
                armor_name = build_armor_name_from_page_title(
                    armor_page_title,
                    profession,
                    item_type,
                    len(slot_columns),
                )
                append_armor_entry(
                    armors,
                    legacy_armors,
                    profession,
                    armor_rating,
                    item_type,
                    armor_name,
                    requirements,
                )


def parse_armorer_armors(
    soup: BeautifulSoup,
    crafter_name: str,
    map_name: str,
    map_id: int,
    items_index: dict[str, dict[str, Any]],
    legacy_entry: dict[str, Any] | None,
) -> tuple[dict[str, int], dict[str, list[dict[str, Any]]]]:
    professions_armor_rating: dict[str, int] = parse_npc_armor_ratings(soup)
    armors: dict[str, list[dict[str, Any]]] = defaultdict(list)

    legacy_armors: dict[tuple[str, str], dict[str, Any]] = {}
    if legacy_entry is not None:
        for profession_name, entries in legacy_entry.get('armors', {}).items():
            for entry in entries:
                legacy_armors[(profession_name, entry.get('item_type', 'Unknown'))] = entry

    candidate_links: dict[str, tuple[Path, list[str] | None]] = {}
    for anchor in soup.find_all('a', href=True):
        title = clean_text(anchor.get('title') or '')
        if not re.match(rf"^({'|'.join(PROFESSIONS)}) .+ armor$", title):
            continue
        page_path = resolve_local_page(anchor['href'])
        if page_path is not None:
            candidate_links[title] = (page_path, [title.split(' ', 1)[0]])

    for title, page_path, professions_hint in build_direct_armor_page_specs(soup):
        candidate_links.setdefault(title, (page_path, professions_hint))

    visited_pages: set[Path] = set()
    for armor_page_title, (armor_page_path, professions_hint) in sorted(candidate_links.items()):
        parse_armorer_armor_page(
            armor_page_title,
            armor_page_path,
            professions_hint,
            crafter_name,
            map_name,
            items_index,
            legacy_armors,
            professions_armor_rating,
            armors,
            professions_armor_rating,
            visited_pages,
        )

    for profession, entries in list(armors.items()):
        deduped: dict[tuple[str, str], dict[str, Any]] = {}
        for entry in entries:
            deduped[(entry['item_type'], entry['name'])] = entry
        sorted_entries = sorted(deduped.values(), key=lambda entry: (entry['item_type'], entry['name']))
        armors[profession] = sorted_entries

    return professions_armor_rating, dict(armors)


def parse_crafter_page(
    page_path: Path,
    service_key: str,
    items_index: dict[str, dict[str, Any]],
    map_index: dict[str, int],
    legacy_armorers: dict[tuple[str, int], dict[str, Any]],
) -> dict[str, Any]:
    soup = load_soup(page_path)
    title = clean_text(soup.find('h1').get_text(' ', strip=True))
    map_name = parse_location_name(soup)
    map_id = resolve_map_id(map_name, map_index)

    entry: dict[str, Any] = {
        'name': title,
        'map_id': map_id,
        'position': [0.0, 0.0],
        'model_id': 0,
        'encoded_name': [],
    }

    if service_key == 'artisans':
        entry['items'] = parse_simple_item_table(soup, 'Rare_crafting_materials_offered', 'items', items_index)
    elif service_key == 'consumable_crafters':
        entry['consumables'] = parse_simple_item_table(soup, 'Consumables_offered', 'consumables', items_index)
    elif service_key == 'weaponsmiths':
        entry['weapons'] = parse_weaponsmith_items(soup, items_index)
    elif service_key == 'collectors':
        entry['items'] = parse_collector_items(soup, items_index)
    elif service_key == 'armorers':
        legacy_entry = legacy_armorers.get((title, map_id))
        if legacy_entry is not None:
            entry['position'] = legacy_entry.get('position', [0.0, 0.0])
            entry['model_id'] = int(legacy_entry.get('model_id', 0) or 0)
            entry['encoded_name'] = list(legacy_entry.get('encoded_name', []))
        professions_armor_rating, armors = parse_armorer_armors(
            soup,
            title,
            map_name,
            map_id,
            items_index,
            legacy_entry,
        )
        entry['professions_armor_rating'] = professions_armor_rating
        entry['armors'] = armors

    if map_name:
        entry['_map_name'] = map_name
    if map_id == 0:
        entry['_map_unresolved'] = map_name

    return entry


def build_dataset() -> dict[str, Any]:
    items_index = load_items_index()
    map_index = load_map_index()
    legacy_armorers = load_legacy_armorer_index()

    dataset: dict[str, Any] = {
        'version': 3,
        'saved_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'armorers': [],
        'artisans': [],
        'consumable_crafters': [],
        'weaponsmiths': [],
        'collectors': [],
        'merchants': [],
        'traders': [],
        'allies': [],
        'foes': [],
    }

    targets = discover_target_pages()
    for service_key, page_paths in targets.items():
        for page_path in sorted(page_paths):
            dataset[service_key].append(parse_crafter_page(page_path, service_key, items_index, map_index, legacy_armorers))

    for key in CATEGORY_KEYS:
        dataset[key].sort(key=lambda entry: (entry.get('map_id', 0), entry.get('name', '')))

    return dataset


def iter_local_link_paths(page_path: Path) -> list[Path]:
    soup = load_soup(page_path)
    paths: list[Path] = []
    seen: set[Path] = set()
    for anchor in soup.find_all('a', href=True):
        resolved = resolve_local_page(anchor['href'])
        if resolved is None or resolved in seen:
            continue
        seen.add(resolved)
        paths.append(resolved)
    return paths


def filter_service_pages(candidates: set[Path], service_key: str) -> set[Path]:
    results: set[Path] = set()
    for path in candidates:
        try:
            if extract_service(load_soup(path)) == service_key:
                results.add(path)
        except Exception:
            continue
    return results


def discover_target_pages() -> dict[str, set[Path]]:
    armorers_page = PAGES_DIR / 'Armorer.html'
    artisans_page = PAGES_DIR / 'Artisan.html'
    consumables_page = PAGES_DIR / 'Consumable_crafter.html'
    weaponsmiths_page = PAGES_DIR / 'Weaponsmith.html'
    collectors_page = PAGES_DIR / 'Collector.html'
    list_of_collectors_page = PAGES_DIR / 'List_of_collectors.html'

    targets: dict[str, set[Path]] = {
        'armorers': set(),
        'artisans': set(),
        'consumable_crafters': set(),
        'weaponsmiths': set(),
        'collectors': set(),
    }

    if armorers_page.exists():
        targets['armorers'] = filter_service_pages(set(iter_local_link_paths(armorers_page)), 'armorers')

    if artisans_page.exists():
        targets['artisans'] = filter_service_pages(set(iter_local_link_paths(artisans_page)), 'artisans')

    if consumables_page.exists():
        targets['consumable_crafters'] = filter_service_pages(set(iter_local_link_paths(consumables_page)), 'consumable_crafters')

    if weaponsmiths_page.exists():
        weaponsmith_list_pages = {
            path for path in iter_local_link_paths(weaponsmiths_page)
            if path.stem.startswith('List_of_')
        }
        weaponsmith_candidates: set[Path] = set()
        for list_page in weaponsmith_list_pages:
            weaponsmith_candidates.update(iter_local_link_paths(list_page))
        targets['weaponsmiths'] = filter_service_pages(weaponsmith_candidates, 'weaponsmiths')

    if collectors_page.exists() and list_of_collectors_page.exists():
        collector_list_pages = {
            path for path in iter_local_link_paths(list_of_collectors_page)
            if path.stem.startswith('List_of_')
        }
        collector_candidates: set[Path] = set()
        for list_page in collector_list_pages:
            collector_candidates.update(iter_local_link_paths(list_page))
        targets['collectors'] = filter_service_pages(collector_candidates, 'collectors')

    return targets


def main():
    dataset = build_dataset()
    OUTPUT_PATH.write_text(json.dumps(dataset, indent=4, ensure_ascii=False), encoding='utf-8')
    OUTPUT_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

    for key in CATEGORY_KEYS:
        (OUTPUT_DIRECTORY_PATH / f'{key}.json').write_text(
            json.dumps(
                {
                    'version': dataset['version'],
                    'saved_at': dataset['saved_at'],
                    'category': key,
                    'entries': dataset[key],
                },
                indent=4,
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )

    counts = {key: len(dataset[key]) for key in CATEGORY_KEYS}
    print(f'Wrote {OUTPUT_PATH}')
    print(f'Wrote split category files to {OUTPUT_DIRECTORY_PATH}')
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
