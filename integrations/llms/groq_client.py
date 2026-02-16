import logging

import httpx

from core.config.settings import get_settings
from core.domain.constants import CONTENT_TYPE_JSON, ResponseType
from core.domain.exceptions import LLMClientError
from core.domain.models import LLMResponse
from core.llm.json_extraction import extract_json_array
from .base import BaseLLMClient, LLMClientConfig

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 120.0


class GroqLLMClient(BaseLLMClient):
    def __init__(self, config: LLMClientConfig) -> None:
        super().__init__(config)
        settings = get_settings()
        self._api_key = settings.groq_api_key
        self._url = settings.groq_url

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": CONTENT_TYPE_JSON,
        }

    def _build_payload(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    def call(self, prompt: str, system_prompt: str | None = None) -> str:
        payload = self._build_payload(prompt, system_prompt)
        try:
            resp = httpx.post(
                self._url,
                headers=self._build_headers(),
                json=payload,
                timeout=_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise LLMClientError(f"Groq API call failed: {e}") from e

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
                logger.warning("Failed to parse JSON from Groq response")
        return LLMResponse(response_type=ResponseType.JSON, content=results)
