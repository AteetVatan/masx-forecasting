import logging

import cohere

from core.config.settings import get_settings
from core.domain.constants import ResponseType
from core.domain.exceptions import LLMClientError
from core.domain.models import LLMResponse
from core.llm.json_extraction import extract_json_array
from .base import BaseLLMClient, LLMClientConfig

logger = logging.getLogger(__name__)


class CohereLLMClient(BaseLLMClient):
    def __init__(self, config: LLMClientConfig) -> None:
        super().__init__(config)
        self._client = cohere.Client(api_key=get_settings().cohere_api_key)

    def call(self, prompt: str, system_prompt: str | None = None) -> str:
        try:
            response = self._client.chat(
                message=prompt,
                model=self.model,
                preamble=system_prompt or "",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.text or ""
        except Exception as e:
            raise LLMClientError(f"Cohere call failed: {e}") from e

    def call_batch(
        self,
        batch_texts: list[str],
        embedded_prompt: str,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        results: list[dict] = []
        for text in batch_texts:
            prompt = f"{embedded_prompt}\n\n{text}"
            raw = self.call(prompt, system_prompt=system_prompt)
            parsed = extract_json_array(raw)
            if parsed:
                results.extend(parsed)
            else:
                logger.warning("Failed to parse JSON from Cohere response")
        return LLMResponse(response_type=ResponseType.JSON, content=results)
