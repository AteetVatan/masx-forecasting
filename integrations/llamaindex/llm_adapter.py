from __future__ import annotations

from typing import Generator

from llama_index.core.llms import (
    ChatMessage,
    ChatResponse,
    CompletionResponse,
    CustomLLM,
    LLMMetadata,
)

from core.llm.ports import LLMClientPort

_DEFAULT_CONTEXT_WINDOW = 4096
_DEFAULT_NUM_OUTPUT = 1024
_MODEL_NAME = "masx-bridge"


class MasxLLMBridge(CustomLLM):
    """Wraps an existing LLMClientPort as a LlamaIndex CustomLLM.

    This lets LlamaIndex query engines use whatever LLM provider
    the app is already configured with, instead of requiring a
    separate direct OpenAI connection.
    """

    _llm_port: LLMClientPort

    def __init__(self, *, llm_port: LLMClientPort) -> None:
        super().__init__()
        object.__setattr__(self, "_llm_port", llm_port)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=_DEFAULT_CONTEXT_WINDOW,
            num_output=_DEFAULT_NUM_OUTPUT,
            model_name=_MODEL_NAME,
        )

    def complete(
        self,
        prompt: str,
        **kwargs,
    ) -> CompletionResponse:
        text = self._llm_port.call(prompt)
        return CompletionResponse(text=text)

    def stream_complete(
        self,
        prompt: str,
        **kwargs,
    ) -> Generator[CompletionResponse, None, None]:
        text = self._llm_port.call(prompt)
        yield CompletionResponse(text=text, delta=text)

    def chat(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> ChatResponse:
        combined = "\n".join(m.content or "" for m in messages)
        text = self._llm_port.call(combined)
        return ChatResponse(message=ChatMessage(role="assistant", content=text))

    def stream_chat(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> Generator[ChatResponse, None, None]:
        response = self.chat(messages, **kwargs)
        yield response
