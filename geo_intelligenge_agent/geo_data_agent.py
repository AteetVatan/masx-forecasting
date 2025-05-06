import sys
from pathlib import Path
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

# Add the project root to Python path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from gedlt import GdeltV2Themes
from helpers import JsonFileHelper

class GeoDataAgent:
    def __init__(self):
        self.llm = ChatOllama(model="llama3")
        self.chain = None
        self.known_descriptions = {}

    def load_known_descriptions(self, csv_file):
        df = pd.read_csv(csv_file, usecols=[0,1,2], header=0, names=['Type', 'Name', 'Description'])
        self.known_descriptions = {
            row['Name'].strip().lower(): row['Description'].strip()
            for _, row in df.iterrows()
            if pd.notnull(row['Description'])
        }

    def init_chain(self, masx_categories, with_description=False):
        if with_description:
            prompt_template_str = f"""
            You are an expert classifier.
            Given the GDELT theme code and its description, assign it to the most appropriate MASX AI category.
            Categories: {', '.join(masx_categories)}
            Theme code: {{theme_code}}
            Description: {{description}}
            Respond ONLY with the category name.
            If you are unsure or no category fits, respond with: SKIP
            """
            prompt_template = PromptTemplate(input_variables=["theme_code", "description"], template=prompt_template_str)
        else:
            prompt_template_str = f"""
            You are an expert classifier.
            Given the GDELT theme code, assign it to the most appropriate MASX AI category.
            Categories: {', '.join(masx_categories)}
            Theme code: {{theme_code}}
            Respond ONLY with the category name.
            If you are unsure or no category fits, respond with: SKIP
            """
            prompt_template = PromptTemplate(input_variables=["theme_code"], template=prompt_template_str)

        self.chain = prompt_template | self.llm | StrOutputParser()

    def invoke_chain(self, theme_code, description=None):
        if description:
            result = self.chain.invoke({"theme_code": theme_code, "description": description})
        else:
            result = self.chain.invoke({"theme_code": theme_code})
        return result.strip()

    def run_full_pipeline(self):
        themes = GdeltV2Themes()
        themes.download_gdelt_themes(
            "http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT",
            "v2_themes.txt",
        )

        masx_template = JsonFileHelper.read_data("gedlt/constants/masx_keywords.json")
        masx_categories = self.flatten_masx_categories(masx_template)

        self.load_known_descriptions("gedlt/constants/GDELT-Global_Knowledge_Graph_CategoryList.csv")

        relevant_themes = []
        count = 0
        with open("v2_themes.txt", "r", encoding="utf-8") as f:
            for line in f:
                count += 1
                print(f"Processing line {count}")
                
                # if count > 27:
                #      break
                if line.strip() == "":
                    continue
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue

                theme_code = parts[0].lower()
                description = self.known_descriptions.get(theme_code)

                self.init_chain(masx_categories, with_description=bool(description))

                try:
                    category = self.invoke_chain(theme_code, description)
                    print(f"************     LLM - Category: {category} for theme - {theme_code}      **************")
                    if category.upper() == "SKIP":
                        print(f"⚠ Unknown category for {theme_code}, marking as uncategorized.")
                        relevant_themes.append((theme_code, "uncategorized"))
                    else:
                        if category in masx_categories:
                            relevant_themes.append((theme_code, category))
                        else:
                            print(f"⚠ Unknown category for {theme_code}, marking as uncategorized.")
                            relevant_themes.append((theme_code, "uncategorized"))
                except Exception as e:
                    print(f"❌ LLM error on {theme_code}: {e}")
                    relevant_themes.append((theme_code, "uncategorized"))

        mapped = self.map_themes_to_nested_structure(relevant_themes, masx_template)
        JsonFileHelper.write_data(mapped, "gedlt/constants/masx_theme_map.json")
        return mapped

    def flatten_masx_categories(self, masx_template):
        flat = []
        for main_cat, subcats in masx_template.items():
            if isinstance(subcats, dict):
                flat.extend(subcats.keys())
            elif isinstance(subcats, list):
                flat.append(main_cat)
        return flat

    def map_themes_to_nested_structure(self, relevant_themes, masx_template):
        import copy
        category_map = copy.deepcopy(masx_template)

        for theme_code, category in relevant_themes:
            inserted = False
            for main_cat, subcats in category_map.items():
                if isinstance(subcats, dict):
                    if category in subcats:
                        subcats[category].append(theme_code)
                        inserted = True
                        break
                elif isinstance(subcats, list):
                    if main_cat == category:
                        subcats.append(theme_code)
                        inserted = True
                        break
            if not inserted:
                print(f"⚠ Warning: category '{category}' not found in template — skipping or logging")
        return category_map

if __name__ == "__main__":
    agent = GeoDataAgent()
    mapped = agent.run_full_pipeline()
    print(mapped)
