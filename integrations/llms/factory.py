import logging
from typing import TYPE_CHECKING

from core.domain.constants import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from core.domain.exceptions import ConfigurationError
from core.llm.enums.llm_provider import LLMProvider
from .base import LLMClientConfig

if TYPE_CHECKING:
    from core.llm.ports import LLMClientPort

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, type] = {}


def _ensure_registry() -> None:
    if _REGISTRY:
        return
    from .openai_client import OpenAILLMClient
    from .claude_client import ClaudeLLMClient
    from .groq_client import GroqLLMClient
    from .gemini_client import GeminiLLMClient
    from .cohere_client import CohereLLMClient

    _REGISTRY.update(
        {
            LLMProvider.OPENAI.value: OpenAILLMClient,
            LLMProvider.CLAUDE.value: ClaudeLLMClient,
            LLMProvider.GROQ.value: GroqLLMClient,
            LLMProvider.GEMINI.value: GeminiLLMClient,
            LLMProvider.COHERE.value: CohereLLMClient,
        }
    )


class LLMClientFactory:
    @staticmethod
    def get_client(
        provider: str | LLMProvider,
        *,
        model: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> "LLMClientPort":
        _ensure_registry()

        provider_key = provider.value if isinstance(provider, LLMProvider) else provider
        client_cls = _REGISTRY.get(provider_key)
        if client_cls is None:
            raise ConfigurationError(
                f"Unknown LLM provider: {provider_key}. "
                f"Available: {list(_REGISTRY.keys())}"
            )

        config = LLMClientConfig(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return client_cls(config)
