from collections import defaultdict
import json
import os
from enum import IntEnum
import random
import time

import time
import sys
import os
import ctypes
import subprocess

# *******************************************************************************
# *********  Start of manual import of external libraries  ***********************
# *******************************************************************************
# Automatically detect Python installation path


def find_system_python():
    """ Automatically detects the system Python installation path """
    try:
        python_path = subprocess.check_output(
            "where python", shell=True).decode().split("\n")[0].strip()
        if python_path and os.path.exists(python_path):
            return os.path.dirname(python_path)
    except Exception:
        pass

    if sys.prefix and os.path.exists(sys.prefix):
        return sys.prefix

    return None


# Automatically detect Python installation path
system_python_path = find_system_python()

if not system_python_path:
    print("Error: Could not detect system Python!")
    sys.exit(1)

# print("Detected system Python path:", system_python_path)

# Define paths dynamically
site_packages_path = os.path.join(system_python_path, "Lib", "site-packages")
pywin32_system32 = os.path.join(site_packages_path, "pywin32_system32")
win32_path = os.path.join(site_packages_path, "win32")

# Ensure Py4GW has access to the right directories
if site_packages_path not in sys.path:
    sys.path.append(site_packages_path)

if win32_path not in sys.path:
    sys.path.append(win32_path)

if pywin32_system32 not in sys.path:
    sys.path.append(pywin32_system32)

# Manually load `pywintypes` DLL (skipping import)
try:
    ctypes.windll.LoadLibrary(os.path.join(
        pywin32_system32, "pywintypes313.dll"))
    ctypes.windll.LoadLibrary(os.path.join(
        pywin32_system32, "pythoncom313.dll"))
    print("Successfully loaded pywintypes DLL manually!")
except Exception as e:
    print(f"Failed to load pywintypes DLL: {e}")

# Now try importing `win32pipe`
try:
    from bs4 import BeautifulSoup
    import requests
    print("Successfully imported BeautifulSoup and requests!")
except ModuleNotFoundError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you have BeautifulSoup and requests installed in your Python environment.")
    sys.exit(1)


class Campaign(IntEnum):
    None_ = 0
    Core = 1
    Prophecies = 2
    Factions = 3
    Nightfall = 4
    EyeOfTheNorth = 5


class ScrapedData:
    def __init__(self, model_id: int = 0, name: str = "", wiki_url: str = "", common_salvage: list[str] | None = None, rare_salvage: list[str] | None = None, inventory_icon: str = ""):
        if common_salvage is None:
            common_salvage = []

        if rare_salvage is None:
            rare_salvage = []

        self.model_id: int = model_id
        self.name: str = name
        self.wiki_url: str = wiki_url
        self.common_salvage: list[str] = common_salvage
        self.rare_salvage: list[str] = rare_salvage
        self.inventory_icon: str = inventory_icon

    def to_dict(self):
        return {
            "ModelID": self.model_id,
            "Name": self.name,
            "WikiURL": self.wiki_url,
            "Materials": self.common_salvage,
            "RareMaterials": self.rare_salvage,
            "InventoryIcon": self.inventory_icon
        }

    def from_dict(self, data: dict):
        self.model_id = data.get("ModelID", 0)
        self.name = data.get("Name", "")
        self.wiki_url = data.get("WikiURL", "")
        self.common_salvage = data.get("Materials", [])
        self.rare_salvage = data.get("RareMaterials", [])
        self.inventory_icon = data.get("InventoryIcon", "")


class WikiScraper:
    @staticmethod
    def scrape_wiki_page(data: ScrapedData) -> ScrapedData | None:
        url = data.wiki_url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        info_table = soup.find('table')

        if info_table is None:
            return None

        if info_table:
            rows = info_table.find_all('tr')

            for row in rows:
                th = row.find('th')

                if th:
                    if th.find('a', string="Common salvage"):
                        td = row.find('td')

                        if td:
                            common_salvage = td.get_text(
                                strip=True, separator="|")

                            if common_salvage:
                                print(
                                    "LootEx", f"Common salvage: {common_salvage} for {url}")

                                # the response looks like <a href="/wiki/Iron_Ingot" title="Iron Ingot">Iron Ingots</a><br /><a href="/wiki/Wood_Plank" title="Wood Plank">Wood Planks</a>

                                materials = common_salvage.split("|")
                                data.common_salvage.extend(
                                    [material.strip() for material in materials if material.strip()])

                    if th.find('a', string="Rare salvage"):
                        td = row.find('td')

                        if td:
                            rare_salvage = td.get_text(
                                strip=True, separator="|")

                            if rare_salvage:
                                print(
                                    "LootEx", f"Rare salvage: {rare_salvage} for {url}")
                                # split by "br" to handle multiple materials
                                materials = rare_salvage.split("|")
                                data.rare_salvage.extend(
                                    [material.strip() for material in materials if material.strip()])

                    if th.find('a', string="Inventory icon"):
                        td = row.find('td')

                        if td:
                            # Extract the image URL
                            img = td.find('img')
                            if img and 'src' in img.attrs:
                                data.inventory_icon = f"https://wiki.guildwars.com{img['src']}"
                                print(
                                    "LootEx", f"Found inventory icon: {data.inventory_icon} for {url}")

            if not data.inventory_icon or data.inventory_icon == "":
                # Try to find the first image in the table as a fallback

                first_image = info_table.find('img')

                if first_image and 'src' in first_image.attrs:
                    data.inventory_icon = f"https://wiki.guildwars.com{first_image['src']}"
                    print(
                        "LootEx", f"Found inventory icon fallback: {data.inventory_icon} for {url}")

        return data

    @staticmethod
    def extract_acquisition_data(soup: BeautifulSoup) -> dict[Campaign, dict[str, list[str]]]:
        # Find the Acquisition headline
        acquisition_header = soup.find("span", id="Acquisition")
        if not acquisition_header:
            return {}

        acquisition_data = {}
        current = acquisition_header.find_parent("h2")

        # Collect all tags until the next h2 (end of section)
        tags = []
        while current and (current := current.find_next_sibling()):
            if current.name == "h2":
                break
            tags.append(current)

        i = 0
        while i < len(tags):
            tag = tags[i]

            # Find Campaign (in <dl>)
            if tag.name == "dl":
                campaign_link = tag.find("a")
                campaign_name = campaign_link.get_text(
                    strip=True) if campaign_link else "Unknown Campaign"

                campaigns = WikiScraper.GetCampaignsFromString(campaign_name)

                # Prepare a nested dict of {location: [enemies]}
                campaign_locations = defaultdict(list)

                # Advance and parse all <ul> after this <dl>
                i += 1
                while i < len(tags) and tags[i].name == "ul":
                    # if the next item on the list is "Random drop" or "Random drops", then set the location to "All Campaign" and the enemies will be "Random drop"

                    if tags[i].get_text(strip=True) in ["Random drop", "Random drops"]:
                        location_name = "All Campaign"
                        enemies = ["Random drop"]
                        campaign_locations[location_name] = enemies
                        i += 1
                        continue

                    location_ul = tags[i]
                    for li in location_ul.find_all("li", recursive=False):
                        location_link = li.find("a")
                        location_name = location_link.get_text(
                            strip=True) if location_link else "Unknown Location"

                        # Get nested enemies/items <ul>
                        nested_ul = li.find("ul")
                        enemies = []
                        if nested_ul:
                            for enemy_li in nested_ul.find_all("li", recursive=False):
                                enemy_link = enemy_li.find("a")
                                if enemy_link:
                                    enemies.append(
                                        enemy_link.get_text(strip=True))

                        campaign_locations[location_name] = enemies
                    i += 1

                for campaign in campaigns:
                    acquisition_data[campaign] = campaign_locations

            else:
                i += 1

        return acquisition_data

    @staticmethod
    def GetCampaignsFromString(campaign_name: str) -> list[Campaign]:
        campaigns = []
        campaign_name = campaign_name.lower()
        if "core" in campaign_name:
            campaigns.append(Campaign.Core)

        if "prophecies" in campaign_name or "prophecy" in campaign_name:
            campaigns.append(Campaign.Prophecies)

        if "factions" in campaign_name:
            campaigns.append(Campaign.Factions)

        if "nightfall" in campaign_name:
            campaigns.append(Campaign.Nightfall)

        if "eye of the north" in campaign_name or "eotn" in campaign_name:
            campaigns.append(Campaign.EyeOfTheNorth)

        return campaigns

    @staticmethod
    def scrape_multiple_entries(entries: dict[int, ScrapedData]):
        result_path = os.path.join(os.path.dirname(
            __file__), "data", "scraper_result.json")

        for key, entry in entries.items():
            # Skip entries with no wiki_url

            try:
                # Scrape the page
                WikiScraper.scrape_wiki_page(entry)

                with open(result_path, 'w', encoding='utf-8') as file:
                    json.dump({k: v.to_dict() for k, v in scrape_entries.items(
                    )}, file, indent=4, ensure_ascii=False)

            except Exception as e:
                print(f"Error scraping {entry.wiki_url}: {e}")

            # Throttle requests with a random delay
            delay = random.uniform(0.75, 2)
            print(
                f"Waiting for {delay:.2f} seconds before the next request...")
            time.sleep(delay)

        with open(result_path, 'w', encoding='utf-8') as file:
            json.dump({k: v.to_dict() for k, v in scrape_entries.items()},
                      file, indent=4, ensure_ascii=False)

        print("Scraping completed.")

    @staticmethod
    def scrape_all_entries():
        path = os.path.join(os.path.dirname(__file__), "data", "items.json")

        scrape_entries: dict[int, ScrapedData] = {}

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for entry in data.values():
                    scraped_data = ScrapedData()
                    scraped_data.from_dict(entry)
                    scrape_entries[scraped_data.model_id] = scraped_data

        WikiScraper.scrape_multiple_entries(scrape_entries)
