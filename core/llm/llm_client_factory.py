"""LLM Client Factory"""
from .openai_llm_client import OpenAILLMClient
from .claude_llm_client import ClaudeLLMClient
from .groq_llm_client import GroqLLMClient
from .gemini_llm_client import GeminiLLMClient
from .cohere_llm_client import CohereLLMClient
from .llm_client import LLMClient
from .enums.llm_provider import LLMProvider
from .enums.llm_model import LLMModel

class LLMClientFactory:
    @staticmethod
    def get_client(provider: str, model: LLMModel, max_tokens: int = 3000, temperature: float = 0.3) -> LLMClient:
        if provider == LLMProvider.OPENAI:
            return OpenAILLMClient(model, max_tokens, temperature)
        elif provider == LLMProvider.CLAUDE:
            return ClaudeLLMClient(model, max_tokens, temperature)
        elif provider == LLMProvider.GROQ:
            return GroqLLMClient(model, max_tokens, temperature)
        elif provider == LLMProvider.GEMINI:
            return GeminiLLMClient(model, max_tokens, temperature)
        elif provider == LLMProvider.COHERE:
            return CohereLLMClient(model, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")