import os
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

        for item in data.Items.get(models.ItemType.Materials_Zcoins, {}).values():
            if item.item_type == models.ItemType.Materials_Zcoins:
                materials[item.names.get(ServerLanguage.English, item.name).lower()] = item

        return materials
    
    MATERIALS: dict[str, models.Item] = {}
    
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
                                item.inventory_icon_url = f"https://wiki.guildwars.com{img['src']}"
                                scraped = True
                
             
            if item.item_type == ItemType.Rune_Mod:
                tr = rows[1]
                td = tr.find('td')   
                name = item.names.get(ServerLanguage.English, item.name).lower()
                image_index = 0 if "minor" in name else 1 if "major" in name else 2 if "superior" in name else -1
                
                if td and image_index >= 0:
                    if "rune" in item.wiki_url.lower():
                        images = td.find_all('img')
                        if not images or image_index >= len(images):
                            print(f"Image at index {image_index} not found.")
                            return ""

                        # Extract and normalize the src
                        img = images[image_index]
                        item.inventory_icon_url = f"https://wiki.guildwars.com{img['src']}"
                        
                    elif "insignia" in item.wiki_url.lower():  
                        # Extract the image URL
                        img = td.find('img')
                        if img and 'src' in img.attrs:
                            item.inventory_icon_url = f"https://wiki.guildwars.com{img['src']}"
                            scraped = True
                            
                        pass            

            if not item.inventory_icon_url or item.inventory_icon_url == "":
                # Try to find the first image in the table as a fallback

                first_image = info_table.find('img')

                if first_image and 'src' in first_image.attrs:
                    item.inventory_icon_url = f"https://wiki.guildwars.com{first_image['src']}"      
            
            if item.inventory_icon_url and "Disambig_icon" in item.inventory_icon_url:
                # If the icon is a disambiguation icon, set it to None
                item.inventory_icon_url = None
            
            if scraped and not item.wiki_scraped:
                item.wiki_scraped = True
    
    @staticmethod            
    def get_image_name(url: str) -> str:
        last_part = url.rsplit('/', 1)[-1]
        #Remove all invalid characters from the filename
        # filename = re.sub(r'[<>:"/\\|?*]', '', last_part)
        return last_part.replace("File:", "")

    @staticmethod
    def download_image(item: models.Item) -> bool:       
        """
        Downloads an image from the given URL and saves it to the item's inventory_icon_url path.
        """
        
        if not item.inventory_icon_url:
            ConsoleLog("LootEx", f"No URL provided for {item.name}. Cannot download image.")
            return False
        filename = WikiScraper.get_image_name(item.inventory_icon_url)
        file_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.join(file_directory, "data")
        path = os.path.join(data_directory, "textures", filename)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
            
        if not os.path.exists(os.path.join(data_directory, "textures")):
            os.makedirs(os.path.join(data_directory, "textures"))
        
        if not filename:
            ConsoleLog("LootEx", f"Invalid filename for {item.name}. Cannot download image.")
            return False    
        
        if os.path.exists(path):
            item.inventory_icon = filename
            data.SaveItems(True)
            return True
        
        try:
            response = requests.get(item.inventory_icon_url)
            response.raise_for_status()  # Raise an error for bad responses                               
            
            # Save the image to the item's inventory_icon_url path
            with open(path, 'wb') as file:
                file.write(response.content)
                item.inventory_icon = filename
                
                
            ConsoleLog("LootEx", f"Downloaded image for {item.name} from {item.inventory_icon_url} to {path}.")
            data.SaveItems(True)
            return True
        
        except requests.RequestException as e:
            ConsoleLog("LootEx", f"Failed to download image for {item.name} from {item.inventory_icon_url}: {e}")            
        return False
    
    @staticmethod
    def scrape_multiple_entries(items: list[models.Item]):
        total = len(items)
        i  = 0
        
        for entry in items:
            # Skip entries with no wiki_url
            i += 1
            
            if not entry:
                continue
            
            def ScrapeEntry(entry: models.Item, i: int):
                ConsoleLog("LootEx", f"Scraping {entry.name} from {entry.wiki_url} | ({i} / {total})...")                
                # Scrape the item information from the wiki
                WikiScraper.scrape_info_from_wiki(entry)
                
                if not entry.inventory_icon_url or not WikiScraper.download_image(entry):
                    data.SaveItems(True)
                    
                
                if i >= total:
                    ConsoleLog("LootEx", "Finished scraping all entries.")
                    return
            
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
        # items_with_missing_info = [
        #     item for subdict in data.Items.values() for item in subdict.values() if not item.wiki_scraped
        # ]
                      
        items_with_missing_info = [
            item for subdict in data.Items.values() for item in subdict.values() if item.inventory_icon_url and not item.inventory_icon
        ]
        
        WikiScraper.scrape_multiple_entries(items_with_missing_info)
