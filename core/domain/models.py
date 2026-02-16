from __future__ import annotations

from pydantic import BaseModel, Field

from core.domain.constants import ResponseType


class ChunkMeta(BaseModel):
    theme: str = "unspecified"
    region: str = "unspecified"
    use_case: str = "doctrine_selector"
    strategic_category: dict[str, list[str]] = Field(default_factory=dict)
    economic_category: dict[str, list[str]] = Field(default_factory=dict)
    civilizational_category: dict[str, list[str]] = Field(default_factory=dict)
    usage_tags: list[str] = Field(default_factory=list)
    influence_map: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "influenced_works": [],
            "modern_applications": [],
        }
    )
    chunk_index: int = 0


class DoctrineChunk(BaseModel):
    id: str = ""
    section: str = ""
    text: str = ""
    meta: ChunkMeta = Field(default_factory=ChunkMeta)


class LLMResponse(BaseModel):
    response_type: ResponseType
    content: list[dict] | str
