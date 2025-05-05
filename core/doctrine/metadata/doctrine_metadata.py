"""Module for DoctrineMetadata"""
import json
import re
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from typing import List, Dict, Optional
from collections import defaultdict
from core.config import Paths

class StrategicCategory(BaseModel):
    military_doctrine: List[str] = []
    geopolitical_strategy: List[str] = []
    national_security: List[str] = []
    diplomatic_posture: List[str] = []
    geostrategic_positioning: List[str] = []

class EconomicCategory(BaseModel):
    development_models: List[str] = []
    resource_strategies: List[str] = []
    trade_tariff_systems: List[str] = []
    economic_warfare: List[str] = []

class CivilizationalCategory(BaseModel):
    cultural_ethos: List[str] = []
    temporal_orientation: List[str] = []
    value_systems: List[str] = []
    historical_memory: List[str] = []
    civilizational_missions: List[str] = []

class InfluenceMap(BaseModel):
    influenced_works: List[str] = []
    modern_applications: List[str] = []

class DoctrineMetadataModel(BaseModel):
    name: str
    slug: str
    type: str = "Unknown"
    source_type: List[str]
    status: str = "raw_collected"
    file_path: str
    source_files: List[str]
    license: str = "Unknown"
    language: str = "en"
    origin_civilization: str = "Unknown"
    strategic_category: StrategicCategory = StrategicCategory()
    economic_category: EconomicCategory = EconomicCategory()
    civilizational_category: CivilizationalCategory = CivilizationalCategory()
    usage_tags: List[str] = []
    influence_map: InfluenceMap = InfluenceMap()
    metadata_version: str = "1.1"
    notes: Optional[str] = ""

class DoctrineMetadata:
    STORAGE_DIR = Paths.METADATA_DIR

    def __init__(self, slug: str, files: List[str], raw_dir: Path):
        self.slug = slug
        self.files = files
        self.raw_dir = raw_dir
        self.data = self._generate_metadata()

    def _generate_metadata(self) -> Dict:
        metadata = DoctrineMetadataModel(
            name=self.slug.replace("_", " ").title(),
            slug=self.slug,
            source_type=list(set(["pdf" if f.endswith(".pdf") else "text" for f in self.files])),
            file_path=str(self.raw_dir / self.files[0]),
            source_files=self.files,
            notes=f"Grouped from files: {', '.join(self.files)}"
        )
        return metadata.dict()

    def validate(self) -> bool:
        try:
            DoctrineMetadataModel(**self.data)
            return True
        except PydanticValidationError as ve:
            print(f"Pydantic validation error in doctrine '{self.slug}':\n{ve}")
            return False

    def save(self) -> Path:
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        output_path = self.STORAGE_DIR / f"{self.slug}.json"

        with open(output_path, "w", encoding="utf-8") as outfile:
            json.dump(self.data, outfile, indent=4)

        return output_path

    def get_metadata(self) -> Dict:
        return self.data

    @staticmethod
    def extract_slug(filename: str) -> str:
        return re.sub(r'[-_](\d+)$', '', Path(filename).stem.lower())

    @classmethod
    def bulk_generate(cls, raw_dir: str, metadata_dir: Optional[str] = None):
        raw_path = Path(raw_dir)
        grouped = defaultdict(list)

        for file in raw_path.iterdir():
            if file.suffix.lower() in [".txt", ".pdf", ".html"]:
                slug = cls.extract_slug(file.name)
                grouped[slug].append(file.name)

        for slug, files in grouped.items():
            instance = cls(slug, files, raw_path)
            instance.save()
