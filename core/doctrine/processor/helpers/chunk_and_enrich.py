"""Chunk and Enrich"""
import json
import os
from openai import OpenAI
from collections import Counter, defaultdict
from core.config.paths import Paths
from tiktoken import get_encoding
from typing import List
import time
import httpx
from core.llm.claude_llm_client import ClaudeLLMClient
from core.prompts.prompts import Prompts
from core.llm.enums.llm_model import LLMModel
from core.llm.enums.llm_provider import LLMProvider
from core.llm.llm_client_factory import LLMClientFactory
from core.llm.llm_client_factory import LLMClient
from pathlib import Path
import re

# Cost tracking
COST_LOG_PATH = Paths.CHUNK_DIR / "cost_log.json"

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChunkAndEnrich:
    """
    This class is used to create chunks and enrich the metadata of a given doctrine.
    """
    CHUNCK_AND_ENRICH_PROMPT = """
    You are a highly trained geopolitical doctrine analyst embedded within the MASX AI strategic intelligence system. 
    Your knowledge spans classical military strategy, 21st-century hybrid warfare, Cold War deterrence theory, post-colonial statecraft, 
    economic coercion, and civilizational alignment frameworks. You are fluent in interpreting doctrinal texts from both traditional and 
    modern sources — including Mahabharat, Arthashastra, Sun Tzu, NATO, Chinese Unrestricted Warfare, and contemporary psyops manuals. 
    Your core objective is to extract and classify operational insights that will guide AI agents in geopolitical simulation,
    alliance prediction, and asymmetric threat modeling.

    Your job is to:
    1. Split the given doctrine text into coherent semantic chunks. Each chunk should contain one core idea or argument, not exceeding 500 words.
    2. For each chunk, assign the following:
    
    - `section`: A short, human-readable title summarizing the chunk (e.g., "Deception in War", "Cyber Influence Operations", "Cultural Assimilation Doctrine")

    - `theme`: The core strategic theme of the chunk. Use precise and domain-specific labels like , add more if needed:
        • "cyberwarfare"
        • "espionage and counterintelligence"
        • "psychological operations"
        • "non-alignment strategy"
        • "doctrine of deterrence"
        • "influence warfare"
        • "economic subversion"
        • "post-colonial realignment"
        • "civilizational soft power"
        • "Kautilyan statecraft"
        • "warrior ethics"
        • "hybrid warfare"
        • "supply chain domination"

    - `region`: The most relevant geopolitical region or scope:
        • "India", "China", "Russia", "Europe", "USA"
        • "Middle East", "Africa", "South Asia"
        • "Cyber", "Global", "Oceanic", "Space", "Post-colonial Africa"

    - `use_case`: The MASX AI use-case or simulation module this chunk should influence , add more if needed:
        • "doctrine_selector" - used to help MASX match strategic doctrines to nations, policies, or risks
        • "proxy_predictor" - used to simulate shadow wars or indirect engagements
        • "risk_analyzer" - used to identify internal/external vulnerabilities
        • "civilizational_alignment" - used to model ideological and cultural compatibility
        • "alliance_modeler" - used to predict diplomatic configurations
        • "psyops_engine" - used to train MASX psyops agent modules
        • "defense_simulator" - used to simulate conventional or hybrid war scenarios
        • "influence_network_mapper" - for detecting influence campaigns
        • "economic_shock_predictor" - for resource, debt, or trade-based conflicts

    Return a JSON array with the following structure:

    [
    {
        "section": "...",
        "text": "...",
        "meta": {
        "theme": "...",
        "region": "...",
        "use_case": "..."
        }
    },
    ...
    ]
    """

    @classmethod
    def _call_openai_api(cls, model: str, messages: list, temperature: float = 0.3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            return response
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            raise



    @classmethod
    def _call_claude_opus(cls, prompt: str, model: str = "claude-3-opus-20240229", max_tokens: int = 3000):
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": os.getenv("CLAUDE_API_KEY"),  # From .env or secrets manager
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            response = httpx.post(url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Claude API error [{model}]: {e}")
            raise
   

    #ChunkAndEnrich.chunk_and_enrich_process(slug="deep_state", model="claude-3-opus", provider="claude")
    #ChunkAndEnrich.chunk_and_enrich_process(slug="sun_tzu", model="gpt-4", provider="openai")

    @classmethod
    def chunk_and_enrich_process(cls, slug: str, embedded_prompt: str, system_prompt: str):       

        cleaned_path = Paths.CLEANED_DIR / f"{slug}.md"
        chunk_path = Paths.CHUNK_DIR / f"{slug}_chunks.json"
        meta_path = Paths.METADATA_DIR / f"{slug}.json"        

        # with open(Paths.CHUNK_DIR / "artofwar_chunks.json", "r", encoding="utf-8") as f:
        #     all_chunks = json.load(f)

        # cls.enrich_metadata( Paths.METADATA_DIR / "artofwar.json", all_chunks)
         
         
        if chunk_path.exists():
            print(f"⏩ Skipping {slug} – already chunked.")
            return

        with open(cleaned_path, "r", encoding="utf-8") as f:
            full_text = f.read()

        segments = cls.split_text_for_gpt(full_text, max_tokens=1000)
        segment_batches = [segments[i:i + 3] for i in range(0, len(segments), 3)]

        providers_to_test = [                
                (LLMProvider.GEMINI, LLMModel.GEMINI_PRO),
                (LLMProvider.COHERE, LLMModel.COMMAND_R_PLUS),
                (LLMProvider.OPENAI, LLMModel.GPT_4_TURBO),
                (LLMProvider.CLAUDE, LLMModel.CLAUDE_SONNET_5),
                (LLMProvider.GROQ, LLMModel.MIXTRAL)
            ]
            
        providers = [                    
            (LLMProvider.GEMINI, LLMModel.GEMINI_PRO),      
            (LLMProvider.OPENAI, LLMModel.GPT_4_TURBO),                            
            (LLMProvider.CLAUDE, LLMModel.CLAUDE_SONNET_5),
            (LLMProvider.COHERE, LLMModel.COMMAND_R_PLUS)
        ]
        
        clients = []
        for provider, model in providers:
            client = LLMClientFactory.get_client(provider=provider, model=model)               
            clients.append(client)

        llm_client_index = 0       
        all_chunks = []
        for batch_index, batch in enumerate(segment_batches):
            for llm_client_index in range(len(clients)):
                try:
                    print(f"{providers[llm_client_index][0].value} - {providers[llm_client_index][1].value}")
                    #print(f"✅ [{slug}] Processed batch {batch_index + 1}/{len(segment_batches)}")
                    print(f"✅ [{slug}] Processed batch {batch_index + 1}/{len(segment_batches)}")
                    
                    response = clients[llm_client_index].call_batch(batch_texts=batch, embedded_prompt=embedded_prompt, system_prompt=system_prompt)
                    
                    if response["type"] == "json":
                        chunks = response["response"]
                    else:
                        chunks = cls.convert_doctrine_text_to_json(response["response"])                                        
                    
                    if len(chunks) == 0:
                        raise Exception("No chunks returned")
                    all_chunks.extend(chunks)
                    
                    #print(f"✅ [{slug}] Processed batch {batch_index + 1}/{len(segment_batches)} (attempt {attempt})")
                  
                    
                    #Wait for 30 seconds before next batch as most llm providers have a rate limit
                    time.sleep(5)
                    break
                    
                except Exception as e:
                    print(f"⚠️ Failed to process batch {batch_index + 1} : {e}")
                    #print(f"⚠️ Failed to process batch {batch_index + 1} : {e}")                
                    if llm_client_index == len(clients) - 1:
                        print(f"❌ Skipping batch {batch_index + 1} after all LLM failed attempts.")

        for idx, chunk in enumerate(all_chunks):
            chunk['id'] = f"{slug}_{str(idx + 1).zfill(3)}"
            chunk['meta']['chunk_index'] = idx + 1

        with open(chunk_path, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)

        # Enrich metadata
        #cls.enrich_metadata(meta_path, all_chunks)

        # cost_per_chunk = 0.0105 # Modify cost based on model
        # total_cost = round(len(all_chunks) * cost_per_chunk, 4)
        # from core.config.paths import COST_LOG_PATH
        # COST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        # if COST_LOG_PATH.exists():
        #     with open(COST_LOG_PATH, "r") as f:
        #         log = json.load(f)
        # else:
        #     log = {}
        # log[slug] = {"chunks": len(all_chunks), "estimated_cost_usd": total_cost}
        # with open(COST_LOG_PATH, "w") as f:
        #     json.dump(log, f, indent=2)

        # print(f"✅ [{slug}] {len(all_chunks)} AI chunks tagged and metadata enriched. Est. cost: ${total_cost}")




    @classmethod
    def split_text_for_gpt(cls, text: str, max_tokens: int = 3000) -> List[str]:
        enc = get_encoding("cl100k_base")
        tokens = enc.encode(text)
        chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
        return [enc.decode(chunk) for chunk in chunks]
    

    @classmethod
    def enrich_metadata(cls, meta_path: Path, all_chunks: List[dict]):
        """
        Enrich the metadata of the given doctrine.
        """
        doctrine_meta = {}
        with open(meta_path, "r", encoding="utf-8") as f:
            doctrine_meta = json.load(f)

        # Initialize aggregators
        strategic = defaultdict(set)
        economic = defaultdict(set)
        civilizational = defaultdict(set)
        influenced_works = set()
        modern_apps = set()
        usage_tags = set()
        regions = set()

        for chunk in all_chunks:
            meta = chunk.get("meta", {})

            regions.add(meta.get("region", ""))
            usage_tags.add(meta.get("use_case", ""))

            strategic["strategic_category"].update(meta.get("strategic_category", {}))
            economic["economic_category"].update(meta.get("economic_category", {}))
            civilizational["civilizational_category"].update(meta.get("civilizational_category", {}))


            if "influence_map" in meta and isinstance(meta["influence_map"], dict):
                influence = meta.get("influence_map", {})                
                influenced_works.update(influence.get("influenced_works", []))
                modern_apps.update(influence.get("modern_applications", []))                    


        doctrine_meta["strategic_category"] = list(set().union(*strategic.values()))
        doctrine_meta["economic_category"] = list(set().union(*economic.values()))
        doctrine_meta["civilizational_category"] = list(set().union(*civilizational.values()))
        doctrine_meta["usage_tags"] = list(usage_tags)
        doctrine_meta["origin_civilization"] = list(regions)
        doctrine_meta["influence_map"] = {
            "influenced_works": list(influenced_works),
            "modern_applications": list(modern_apps)
        }
        doctrine_meta["status"] = "tagged"

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(doctrine_meta, f, indent=2, ensure_ascii=False)
            
    
    @classmethod
    def convert_doctrine_text_to_json(cls, raw_text: str):
        """
        Converts raw LLM response into MASX-style chunk JSON.
        Supports both:
        - JSON-formatted chunks (Claude, Gemini, etc.)
        - Markdown-style "**Section:** ... **Text:** ..."

        Always returns fully structured chunk dicts with all MASX meta fields.
        """
        
        chunks = []
        # 1️⃣ Try parsing JSON block
        json_block_match = re.search(r'\{[\s\n]*"section"\s*:[\s\S]+?\}', raw_text, re.DOTALL)
        if json_block_match:
            try:
                parsed = ChunkAndEnrich.safe_parse_llm_chunk(json_block_match.group())
                if parsed:
                    chunks.append(ChunkAndEnrich.normalize_chunk(parsed, idx=1))
                    return chunks
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e} — falling back to markdown")

        # 2️⃣ Fallback: markdown style
        pattern = r"\*\*Section:\*\* (.*?)\n\*\*Text:\*\*\n(.*?)(?=\n###|$)"
        matches = re.findall(pattern, raw_text, re.DOTALL)

        for idx, (section, text) in enumerate(matches, 1):
            chunks.append({
                "id": f"chunk_{idx:03}",
                "section": section.strip(),
                "text": text.strip(),
                "meta": {
                    "theme": "unspecified",
                    "region": "unspecified",
                    "use_case": "doctrine_selector",
                    "strategic_category": {},
                    "economic_category": {},
                    "civilizational_category": {},
                    "usage_tags": [],
                    "influence_map": {
                        "influenced_works": [],
                        "modern_applications": []
                    },
                    "chunk_index": idx
                }
            })

        return chunks


    @staticmethod
    def normalize_chunk(parsed: dict, idx: int):
            """Ensure all required MASX fields exist"""
            return {
                "id": f"chunk_{idx:03}",
                "section": str(parsed.get("section", "")).strip(),
                "text": str(parsed.get("text", "")).strip(),
                "meta": {
                    "theme": parsed.get("meta", {}).get("theme", "unspecified"),
                    "region": parsed.get("meta", {}).get("region", "unspecified"),
                    "use_case": parsed.get("meta", {}).get("use_case", "doctrine_selector"),
                    "strategic_category": parsed.get("meta", {}).get("strategic_category", {}),
                    "economic_category": parsed.get("meta", {}).get("economic_category", {}),
                    "civilizational_category": parsed.get("meta", {}).get("civilizational_category", {}),
                    "usage_tags": parsed.get("meta", {}).get("usage_tags", []),
                    "influence_map": parsed.get("meta", {}).get("influence_map", {
                        "influenced_works": [],
                        "modern_applications": []
                    }),
                    "chunk_index": idx
                }
            }
            
    @staticmethod        
    def safe_parse_llm_chunk(raw_json_str: str):
        """
        Try to safely parse a JSON chunk from LLM.
        Handles various LLM response formats and common JSON issues.
        """
        if not raw_json_str:
            return None

        # Step 1: Clean the input
        raw = raw_json_str.strip()
        
        # Remove any markdown code block markers
        raw = re.sub(r'```json\s*|\s*```', '', raw)
        
        # Remove any leading/trailing non-JSON content
        raw = re.sub(r'^[^{]*', '', raw)  # Remove everything before first {
        raw = re.sub(r'[^}]*$', '', raw)  # Remove everything after last }
        
        # Step 2: Fix common JSON issues
        # Remove trailing commas
        raw = re.sub(r',\s*([}\]])', r'\1', raw)
        
        # Fix missing quotes around keys
        raw = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', raw)
        
        # Fix single quotes to double quotes
        raw = re.sub(r"'", '"', raw)
        
        # Step 3: Balance braces
        open_braces = raw.count('{')
        close_braces = raw.count('}')
        if close_braces < open_braces:
            raw += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            raw = '{' * (close_braces - open_braces) + raw

        # Step 4: Try parsing with increasing levels of leniency
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            try:
                # Try parsing as a list of chunks
                if not raw.startswith('['):
                    raw = f'[{raw}]'
                return json.loads(raw)[0]  # Take first chunk if it's a list
            except json.JSONDecodeError:
                try:
                    # Try extracting just the content part
                    content_match = re.search(r'"text"\s*:\s*"([^"]*)"', raw)
                    if content_match:
                        return {
                            "section": "Extracted Content",
                            "text": content_match.group(1),
                            "meta": {
                                "theme": "unspecified",
                                "region": "unspecified",
                                "use_case": "doctrine_selector"
                            }
                        }
                except Exception:
                    pass
                
        return None
