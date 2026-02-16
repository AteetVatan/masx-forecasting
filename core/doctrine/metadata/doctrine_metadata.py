from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from core.config import Paths
from core.domain.constants import SUPPORTED_DOC_EXTENSIONS, DoctrineStatus

logger = logging.getLogger(__name__)


class StrategicCategory(BaseModel):
    military_doctrine: list[str] = Field(default_factory=list)
    geopolitical_strategy: list[str] = Field(default_factory=list)
    national_security: list[str] = Field(default_factory=list)
    diplomatic_posture: list[str] = Field(default_factory=list)
    geostrategic_positioning: list[str] = Field(default_factory=list)


class EconomicCategory(BaseModel):
    development_models: list[str] = Field(default_factory=list)
    resource_strategies: list[str] = Field(default_factory=list)
    trade_tariff_systems: list[str] = Field(default_factory=list)
    economic_warfare: list[str] = Field(default_factory=list)


class CivilizationalCategory(BaseModel):
    cultural_ethos: list[str] = Field(default_factory=list)
    temporal_orientation: list[str] = Field(default_factory=list)
    value_systems: list[str] = Field(default_factory=list)
    historical_memory: list[str] = Field(default_factory=list)
    civilizational_missions: list[str] = Field(default_factory=list)


class InfluenceMap(BaseModel):
    influenced_works: list[str] = Field(default_factory=list)
    modern_applications: list[str] = Field(default_factory=list)


class DoctrineMetadataModel(BaseModel):
    name: str
    slug: str
    type: str = "Unknown"
    source_type: list[str]
    status: str = DoctrineStatus.RAW_COLLECTED.value
    file_path: str
    source_files: list[str]
    license: str = "Unknown"
    language: str = "en"
    origin_civilization: str = "Unknown"
    strategic_category: StrategicCategory = Field(default_factory=StrategicCategory)
    economic_category: EconomicCategory = Field(default_factory=EconomicCategory)
    civilizational_category: CivilizationalCategory = Field(
        default_factory=CivilizationalCategory
    )
    usage_tags: list[str] = Field(default_factory=list)
    influence_map: InfluenceMap = Field(default_factory=InfluenceMap)
    metadata_version: str = "1.1"
    notes: str | None = ""


class DoctrineMetadata:
    STORAGE_DIR = Paths.METADATA_DIR

    def __init__(self, slug: str, files: list[str], raw_dir: Path) -> None:
        self.slug = slug
        self.files = files
        self.raw_dir = raw_dir
        self.data = self._generate_metadata()

    def _generate_metadata(self) -> dict:
        metadata = DoctrineMetadataModel(
            name=self.slug.replace("_", " ").title(),
            slug=self.slug,
            source_type=list(
                {_source_type(f) for f in self.files}
            ),
            file_path=str(self.raw_dir / self.files[0]),
            source_files=self.files,
            notes=f"Grouped from files: {', '.join(self.files)}",
        )
        return metadata.model_dump()

    def validate(self) -> bool:
        try:
            DoctrineMetadataModel(**self.data)
            return True
        except PydanticValidationError as ve:
            logger.error("Pydantic validation error in doctrine '%s': %s", self.slug, ve)
            return False

    def save(self) -> Path:
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        output_path = self.STORAGE_DIR / f"{self.slug}.json"
        output_path.write_text(
            json.dumps(self.data, indent=4), encoding="utf-8"
        )
        return output_path

    def get_metadata(self) -> dict:
        return self.data

    @staticmethod
    def extract_slug(filename: str) -> str:
        return re.sub(r"[-_](\d+)$", "", Path(filename).stem.lower())

    @classmethod
    def bulk_generate(cls, raw_dir: str) -> None:
        raw_path = Path(raw_dir)
        grouped: dict[str, list[str]] = defaultdict(list)
        for file in raw_path.iterdir():
            if file.suffix.lower() in SUPPORTED_DOC_EXTENSIONS:
                slug = cls.extract_slug(file.name)
                grouped[slug].append(file.name)
        for slug, files in grouped.items():
            instance = cls(slug, files, raw_path)
            instance.save()


def _source_type(filename: str) -> str:
    return "pdf" if filename.endswith(".pdf") else "text"
