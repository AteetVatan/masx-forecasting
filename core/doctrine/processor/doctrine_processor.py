import re
import json
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import numpy as np
import io
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from core.doctrine.metadata import DoctrineMetadata
from core.config.paths import Paths
from core.doctrine.processor.helpers import ChunkAndEnrich
from core.llm.enums.llm_model import LLMModel
from core.llm.enums.llm_provider import LLMProvider
from core.llm.llm_client_factory import LLMClientFactory
from core.prompts.prompts import Prompts

reader = easyocr.Reader(['en'])  # Initialize OCR reader globally

class DoctrineProcessor:
    def __init__(self, slug: str = None, files: List[str] = None, raw_dir: Path = None):
        self.slug = slug
        self.files = files or []
        self.raw_dir = raw_dir or Paths.RAW_DIR
        self.cleaned_dir = Paths.CLEANED_DIR
        self.chunk_dir = Paths.CHUNK_DIR

    def clean_text(self, text: str) -> str:
        text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        text = text.replace('\ufeff', '').replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, text: str, size: int = 1000) -> List[Dict]:
        words = text.split()
        return [
            {
                "id": f"{self.slug}_{str(i // size + 1).zfill(3)}",
                "section": "AUTO CHUNK",
                "text": ' '.join(words[i:i + size]),
                "meta": {
                    "theme": "unspecified",
                    "region": "unspecified",
                    "use_case": "doctrine_selector",
                    "chunk_index": i // size + 1
                }
            }
            for i in range(0, len(words), size)
        ]

    def process_grouped_files(self):
        combined = ""
        for file in sorted(self.files):
            with open(self.raw_dir / file, "r", encoding="utf-8", errors="ignore") as f:
                combined += "\n\n" + self.clean_text(f.read())

        self.cleaned_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cleaned_dir / f"{self.slug}.md", "w", encoding="utf-8") as f:
            f.write(combined)

        chunks = self.chunk_text(combined)
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        with open(self.chunk_dir / f"{self.slug}_chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        print(f"✅ [TXT] {self.slug} → cleaned + chunked ({len(chunks)} chunks)")

    @classmethod
    def batch_process(cls, raw_dir: Path, cleaned_dir: Path, chunk_dir: Path, chunk_size: int = 1000):
               
        cls.process_raw_pdfs(raw_dir, cleaned_dir)

        existing_chunk_slugs = []
        for file in chunk_dir.glob("*.json"):
            existing_chunk_slugs.append(file.name.replace("_chunks.json", ""))
            
        # Group .txt/.html/.pdf files by slug
        grouped_txt = defaultdict(list)
        for file in raw_dir.iterdir():
            if file.suffix.lower() in [".txt", ".html", ".pdf"]:
                slug = DoctrineMetadata.extract_slug(file.name)
                if slug not in existing_chunk_slugs: # Chunk file exists, skip
                    grouped_txt[slug].append(file.name)  

        for slug, files in grouped_txt.items():           
            
            files = sorted(files)
            processor = cls(slug, files, raw_dir)
            processor.cleaned_dir = Path(cleaned_dir)
            processor.chunk_dir = Path(chunk_dir)

            print(f"\n🚀 Running MASX Doctrine Chunking: {slug}")
            ChunkAndEnrich.chunk_and_enrich_process(
                slug=slug,
                embedded_prompt=Prompts.EMBEDDED_CHUNK_TAGGING_PROMPT,
                system_prompt=Prompts.SYSTEM_ROLE_PROMPT
            )        

            
            
    @classmethod
    def process_raw_pdfs(cls, raw_dir: Path, cleaned_dir: Path):
        """
        Process grouped PDFs and save cleaned and chunked versions.
        """        
        grouped_pdfs = defaultdict(list)
        for file in raw_dir.glob("*.pdf"):
            slug = DoctrineMetadata.extract_slug(file.name)
            grouped_pdfs[slug].append(file)
            
        grouped_pdfs_names = list(grouped_pdfs.keys())        
        cleaned_file_list = list(cleaned_dir.glob("*.md"))
        cleaned_files_names = [file.name.replace(".md", "") for file in cleaned_file_list]        
        # compare grouped_pdfs_names with cleaned_files_names
        missing_files = [file for file in grouped_pdfs_names if file not in cleaned_files_names] 
        
        for slug, pdf_files in grouped_pdfs.items():            
            if slug not in missing_files:
                continue
            
            pdf_files = sorted(pdf_files)
            text = ""
            for pdf in pdf_files:
                doc = fitz.open(pdf)
                for page in doc:
                    page_text = page.get_text().strip()

                    if not page_text:
                        #print(f"📸 OCRing page from {pdf.name} (image-based)")
                        try:
                            pix = page.get_pixmap(dpi=300)
                            img = Image.open(io.BytesIO(pix.tobytes("png")))
                            img_np = np.array(img)
                            ocr_lines = reader.readtext(img_np, detail=0)
                            page_text = ' '.join(ocr_lines)
                        except Exception as e:
                            print(f"⚠️ OCR failed for {pdf.name}: {e}")
                            page_text = ''

                    text += page_text + '\n'

            text = cls.clean_text(text)

            Path(cleaned_dir).mkdir(parents=True, exist_ok=True)
            cleaned_path = Path(cleaned_dir) / f"{slug}.md"
            with open(cleaned_path, "w", encoding="utf-8") as f:
                f.write(text)
                
            print(f"✅ [PDF] {slug} → cleaned")
            
            
            
