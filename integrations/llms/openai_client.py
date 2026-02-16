import logging

from openai import OpenAI

from core.config.settings import get_settings
from core.domain.constants import ResponseType
from core.domain.exceptions import LLMClientError, LLMResponseParseError
from core.domain.models import LLMResponse
from core.llm.json_extraction import extract_json_array
from .base import BaseLLMClient, LLMClientConfig

logger = logging.getLogger(__name__)


class OpenAILLMClient(BaseLLMClient):
    def __init__(self, config: LLMClientConfig) -> None:
        super().__init__(config)
        self._client = OpenAI(api_key=get_settings().openai_api_key)

    def call(self, prompt: str, system_prompt: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMClientError(f"OpenAI call failed: {e}") from e

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
                logger.warning("Failed to parse JSON from OpenAI response")
        return LLMResponse(response_type=ResponseType.JSON, content=results)
