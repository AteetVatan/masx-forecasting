from enum import Enum
from typing import Literal


class DoctrineStatus(str, Enum):
    RAW_COLLECTED = "raw_collected"
    CLEANED = "cleaned"
    CHUNKED = "chunked"
    TAGGED = "tagged"


class ResponseType(str, Enum):
    JSON = "json"
    TEXT = "text"


class ForecastStatus(str, Enum):
    OPEN = "open"
    RESOLVED_TRUE = "resolved_true"
    RESOLVED_FALSE = "resolved_false"
    EXPIRED = "expired"


class ScenarioStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"
    REALIZED = "realized"


class DoctrineDomain(str, Enum):
    GEOPOLITICS = "geopolitics"
    ECONOMIC = "economic"
    MILITARY = "military"
    CYBER = "cyber"
    CIVILIZATIONAL = "civilizational"
    DIPLOMATIC = "diplomatic"


class EventCategory(str, Enum):
    """CAMEO-inspired event taxonomy for making the world queryable."""
    VERBAL_COOPERATION = "01"
    APPEAL = "02"
    INTEND_COOPERATION = "03"
    CONSULT = "04"
    DIPLOMATIC_COOPERATION = "05"
    MATERIAL_COOPERATION = "06"
    PROVIDE_AID = "07"
    YIELD = "08"
    INVESTIGATE = "09"
    DEMAND = "10"
    DISAPPROVE = "11"
    REJECT = "12"
    THREATEN = "13"
    PROTEST = "14"
    EXHIBIT_FORCE = "15"
    REDUCE_RELATIONS = "16"
    COERCE = "17"
    ASSAULT = "18"
    FIGHT = "19"
    MASS_VIOLENCE = "20"


SUPPORTED_DOC_EXTENSIONS: frozenset[str] = frozenset({".txt", ".pdf", ".html"})

DEFAULT_MAX_TOKENS: int = 3000
DEFAULT_TEMPERATURE: float = 0.3
DEFAULT_CHUNK_SIZE: int = 1000
DEFAULT_CHUNK_MAX_WORDS: int = 500
ANTHROPIC_API_VERSION: str = "2023-06-01"
CONTENT_TYPE_JSON: str = "application/json"

DEFAULT_SIMILARITY_TOP_K: int = 5
DEFAULT_RAG_RESPONSE_MODE: str = "compact"
