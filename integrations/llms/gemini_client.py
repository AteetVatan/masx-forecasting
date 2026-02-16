import logging

import google.generativeai as genai

from core.config.settings import get_settings
from core.domain.constants import ResponseType
from core.domain.exceptions import LLMClientError
from core.domain.models import LLMResponse
from core.llm.json_extraction import extract_json_array
from .base import BaseLLMClient, LLMClientConfig

logger = logging.getLogger(__name__)


class GeminiLLMClient(BaseLLMClient):
    def __init__(self, config: LLMClientConfig) -> None:
        super().__init__(config)
        genai.configure(api_key=get_settings().gemini_api_key)
        self._model = genai.GenerativeModel(self.model)

    def call(self, prompt: str, system_prompt: str | None = None) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            response = self._model.generate_content(full_prompt)
            return response.text or ""
        except Exception as e:
            raise LLMClientError(f"Gemini call failed: {e}") from e

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
                logger.warning("Failed to parse JSON from Gemini response")
        return LLMResponse(response_type=ResponseType.JSON, content=results)
