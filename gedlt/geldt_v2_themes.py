import requests
import sys
import os
from pathlib import Path

# Add the project root to Python path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from helpers.json_file_helper import JsonFileHelper

class GdeltV2Themes:
    def __init__(self):
        self.themes = []

    # Step 1: download v2 themes txt file
    @staticmethod
    def download_gdelt_themes(url, local_filename):
        response = requests.get(url)
        response.raise_for_status()
        with open(local_filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Downloaded {local_filename}")

    # Step 2: Load and filter themes by relevance
    @staticmethod
    def load_and_filter_themes(filename, keywords):
        relevant_themes = []
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == "":
                    continue
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue
                theme_code = parts[0].lower()
                for category, words in keywords.items():
                    if any(word.lower() in theme_code for word in words):
                        relevant_themes.append((theme_code, category))
                        break
        return relevant_themes

    # Step 3: Map themes to MASX AI categories
    @staticmethod
    def map_themes_to_categories(relevant_themes):
        category_map = {}
        for theme_code, category in relevant_themes:
            if category not in category_map:
                category_map[category] = []
            category_map[category].append({"code": theme_code})
        return category_map


if __name__ == "__main__":
    themes = GdeltV2Themes()
    themes.download_gdelt_themes(
        "http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT",
        "v2_themes.txt",
    )
    
    #test = os.path.exists('constants/masx_keywords.json')
    masx_keywords = JsonFileHelper.read_data("gedlt/constants/masx_keywords.json")
    relevant_themes = themes.load_and_filter_themes("v2_themes.txt", masx_keywords)
    mapped = themes.map_themes_to_categories(relevant_themes)
    JsonFileHelper.write_data(mapped, "constants/masx_theme_map.json")
