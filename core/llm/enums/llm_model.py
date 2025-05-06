from enum import Enum


class LLMModel(Enum):
    # OpenAI
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-2024-04-09"
    GPT_35_TURBO = "gpt-3.5-turbo-0125"

    # Claude
    CLAUDE_OPUS = "claude-3-opus-20240229"
    CLAUDE_SONNET_7 = "claude-3-7-sonnet-20250219"
    CLAUDE_SONNET_5 = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-5-haiku-20241022"

    # Groq
    MIXTRAL = "mistral-saba-24b"
    MIXTRAL_8X7B_32768 = "mixtral-8x7b-32768"
    MISTRAL_7B_INSTRUCT = "mistral-7b-instruct"

    # Gemini
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_FLASH = "gemini-1.5-flash"

    # Cohere
    COMMAND_R = "command-r"
    COMMAND_R_PLUS = "command-r-plus"
