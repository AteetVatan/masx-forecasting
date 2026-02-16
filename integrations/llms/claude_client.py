import logging

import httpx

from core.config.settings import get_settings
from core.domain.constants import (
    ANTHROPIC_API_VERSION,
    CONTENT_TYPE_JSON,
    ResponseType,
)
from core.domain.exceptions import LLMClientError
from core.domain.models import LLMResponse
from core.llm.json_extraction import extract_json_array
from .base import BaseLLMClient, LLMClientConfig

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 120.0


class ClaudeLLMClient(BaseLLMClient):
    def __init__(self, config: LLMClientConfig) -> None:
        super().__init__(config)
        settings = get_settings()
        self._api_key = settings.claude_api_key
        self._url = settings.claude_url

    def _build_headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._api_key,
            "content-type": CONTENT_TYPE_JSON,
            "anthropic-version": ANTHROPIC_API_VERSION,
        }

    def _build_payload(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict:
        payload: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
        return payload

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
            return data["content"][0]["text"]
        except httpx.HTTPError as e:
            raise LLMClientError(f"Claude API call failed: {e}") from e

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
                logger.warning("Failed to parse JSON from Claude response")
        return LLMResponse(response_type=ResponseType.JSON, content=results)
