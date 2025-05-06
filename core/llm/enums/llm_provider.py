""" """

from enum import Enum


class LLMProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GROQ = "groq"
    GEMINI = "gemini"
    COHERE = "cohere"
