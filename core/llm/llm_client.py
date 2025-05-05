"""Abstract Base LLM Client"""
from abc import ABC, abstractmethod
from typing import List


class LLMClient(ABC):
    def __init__(self, model: str, max_tokens: int = 3000, temperature: float = 0.3):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    @abstractmethod
    def call(self, prompt: str) -> str:
        pass

    @abstractmethod
    def call_batch(self, batch_texts: List[str], embedded_prompt: str) -> List[dict]:
        pass