# core/config/paths.py
from pathlib import Path

class Paths:
    BASE_DATA_DIR = Path("data/doctrines")
    RAW_DIR = BASE_DATA_DIR / "raw"
    METADATA_DIR = BASE_DATA_DIR / "metadata"
    CLEANED_DIR = BASE_DATA_DIR / "cleaned"
    CHUNK_DIR = BASE_DATA_DIR / "chunks"
    VECTOR_DIR = BASE_DATA_DIR / "vector"    
    TEMPLATE_DIR = Path("templates/doctrines")
    
    @classmethod
    def mkdir_all(cls):
        for path in [cls.RAW_DIR, cls.METADATA_DIR, cls.CLEANED_DIR, cls.CHUNK_DIR, cls.VECTOR_DIR]:
            path.mkdir(parents=True, exist_ok=True)
