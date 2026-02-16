import logging
from dataclasses import dataclass

from core.domain.constants import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMClientConfig:
    model: str
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE


class BaseLLMClient:
    def __init__(self, config: LLMClientConfig) -> None:
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
