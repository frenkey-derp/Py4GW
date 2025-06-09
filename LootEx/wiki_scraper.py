import re
import sys

from LootEx import data, models, module_import
import importlib

from Py4GWCoreLib.Py4GWcorelib import ActionQueueManager, ConsoleLog
from Py4GWCoreLib.enums import ItemType, ServerLanguage

importlib.reload(models)
importlib.reload(module_import)

try:
    module_import.ModuleImporter.prepare_module_import()
    from bs4 import BeautifulSoup
    import requests
    print("Successfully imported BeautifulSoup and requests!")

except ModuleNotFoundError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you have BeautifulSoup and requests installed in your Python environment.")
    sys.exit(1)


class WikiScraper:
    
    @staticmethod
    def get_all_materials() -> dict[str, models.Item]:
        """
        Returns a list of all materials from the items data.
        """
        materials = {}

        for item in data.Items.values():
            if item.item_type == models.ItemType.Materials_Zcoins:
                materials[item.names.get(ServerLanguage.English, item.name).lower()] = item

        return materials
    
    MATERIALS: dict[str, models.Item] = {}
    
    @staticmethod
    def get_material_ids(material_names: list[str]) -> list[int]:
        model_ids = []

        for item in data.Items.values():
            if item.item_type == models.ItemType.Materials_Zcoins:
                name = item.names.get(ServerLanguage.English, None)

                if name:
                    name = name.lower()

                    if any(name in material_name.lower() for material_name in material_names):
                        ConsoleLog(
                            "LootEx", f"Found material: {name} with ID {item.model_id} in the items data."
                        )
                        model_ids.append(item.model_id)

        return model_ids

    @staticmethod
    def extract_materials(td) -> models.SalvageInfoCollection:
        materials : models.SalvageInfoCollection = models.SalvageInfoCollection()
        
        if not td:
            return materials

        tokens = list(td.children)
        current_amount = None

        for token in tokens:
            if isinstance(token, str):
                # Handle amount strings: "1-5", "4", etc.
                stripped = token.strip()
                if stripped:
                    range_match = re.match(r"^(\d+)\s*-\s*(\d+)$", stripped)
                    single_match = re.match(r"^(\d+)$", stripped)
                    if range_match:
                        current_amount = {
                            "min": int(range_match.group(1)),
                            "max": int(range_match.group(2))
                        }
                    elif single_match:
                        current_amount = {
                            "min": int(single_match.group(1)),
                            "max": int(single_match.group(1))
                        }
            elif token.name == "a":
                material_name = token.get("title", token.get_text(strip=True))
                entry = {
                    "name": material_name,
                    "min": -1,
                    "max": -1
                }
                
                if current_amount:
                    entry["min"] = current_amount["min"]
                    entry["max"] = current_amount["max"]
                    current_amount = None
                    
                materials[material_name] = models.SalvageInfo(
                    material_name=material_name,
                    min_amount=entry.get("min", -1) if entry.get("min") != entry.get("max") else -1,
                    max_amount=entry.get("max", -1) if entry.get("min") != entry.get("max") else -1,
                    amount=entry.get("min", -1) if entry.get("min") == entry.get("max") else -1
                )
                
        
        if materials:
            WikiScraper.MATERIALS = WikiScraper.get_all_materials()
            
            for material_name, salvage_info in materials.items():
                lower_name = material_name.lower()
                
                if lower_name in WikiScraper.MATERIALS:
                    salvage_info.material_model_id = WikiScraper.MATERIALS[lower_name].model_id
        
        return materials
    
    @staticmethod
    def scrape_info_from_wiki(item: models.Item):
        url = item.wiki_url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        info_table = soup.find('table')

        if info_table is None:
            return None

        if info_table:
            rows = info_table.find_all('tr')
            scraped = False

            for row in rows:
                th = row.find('th')

                if th:
                    material_names = []                
                    
                    if th.find('a', string="Common salvage"):
                        td = row.find('td')

                        #<td>4-5 <a href="/wiki/Granite_Slab" title="Granite Slab">Granite Slabs</a><br>1-49 <a href="/wiki/Pile_of_Glittering_Dust" title="Pile of Glittering Dust">Piles of Glittering Dust</a></td>    
                        if td:
                            mats = WikiScraper.extract_materials(td)
                            
                            if mats:
                                item.common_salvage = mats
                                scraped = True

                    rare_material_names = []
                    if th.find('a', string="Rare salvage"):
                        td = row.find('td')

                        if td:
                            mats = WikiScraper.extract_materials(td)
                            
                            if mats:
                                item.rare_salvage = mats
                                scraped = True

                    if "Type" in th.get_text():
                        td = row.find('td')
                        
                        if td:
                            text = td.get_text(strip=True)
                            
                            if text:
                                scraped = True          
                                                      
                                if item.item_type == models.ItemType.Unknown:                                
                                    try:
                                        item.item_type = ItemType[text]
                                    except KeyError:
                                        if "upgrade" in text.lower():
                                            item.item_type = ItemType.Rune_Mod
                                        
                                        elif "focus" in text.lower():
                                            item.item_type = ItemType.Offhand
                                            
                                        elif "consumable" in text.lower():
                                            item.item_type = ItemType.Usable
                                            
                                        elif "sweet" in text.lower():
                                            item.item_type = ItemType.Usable
                                            
                                        elif "alcohol" in text.lower():
                                            item.item_type = ItemType.Usable
                                            
                                        else:
                                            item.item_type = ItemType.Unknown
                                            ConsoleLog("LootEx", f"Unknown item type '{text}' for {item.name} ({item.model_id}) in {item.wiki_url}.")
                                    
                                
                    if th.find('a', string="Inventory icon"):
                        td = row.find('td')                        

                        if td:
                            # Extract the image URL
                            img = td.find('img')
                            if img and 'src' in img.attrs:
                                item.inventory_icon = f"https://wiki.guildwars.com{img['src']}"
                                scraped = True

            if not item.inventory_icon or item.inventory_icon == "":
                # Try to find the first image in the table as a fallback

                first_image = info_table.find('img')

                if first_image and 'src' in first_image.attrs:
                    item.inventory_icon = f"https://wiki.guildwars.com{first_image['src']}"      
            
            if item.inventory_icon and "Disambig_icon" in item.inventory_icon:
                # If the icon is a disambiguation icon, set it to None
                item.inventory_icon = None
            
            if scraped and not item.wiki_scraped:
                item.wiki_scraped = True

    @staticmethod
    def scrape_multiple_entries(model_ids: list[int]):
        total = len(model_ids)
        i  = 0
        
        for model_id in model_ids:
            # Skip entries with no wiki_url
            i += 1
            
            def ScrapeEntry(entry: models.Item, i: int):
                ConsoleLog("LootEx", f"Scraping {entry.name} from {entry.wiki_url} | ({i} / {total})...")                
                # Scrape the item information from the wiki
                WikiScraper.scrape_info_from_wiki(entry)
                data.SaveItems(True)
                
                if i >= total:
                    ConsoleLog("LootEx", "Finished scraping all entries.")
                    return

            entry = data.Items.get(model_id)
            if not entry:
                ConsoleLog("LootEx", f"Skipping model ID {model_id} as it does not exist in the items data.")
                continue
            
            try:                
                if not entry.wiki_url:
                    ConsoleLog("LootEx", f"Skipping {entry.name} due to missing wiki URL.")
                    continue
                
                ActionQueueManager().AddAction("ACTION", 
                ScrapeEntry, entry, i)         
                            
            except Exception as e:
                print(f"Error scraping {entry.wiki_url}: {e}")
            

    @staticmethod
    def scrape_missing_entries():                
        items_with_missing_info = [
            item.model_id for item in data.Items.values()
            if item.wiki_url and not item.wiki_scraped
        ]
        
        WikiScraper.scrape_multiple_entries(items_with_missing_info)
