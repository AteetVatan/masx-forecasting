from __future__ import annotations

from typing import Protocol

from core.domain.models import LLMResponse


class LLMClientPort(Protocol):
    def call(self, prompt: str, system_prompt: str | None = None) -> str: ...

    def call_batch(
        self,
        batch_texts: list[str],
        embedded_prompt: str,
        system_prompt: str | None = None,
    ) -> LLMResponse: ...
