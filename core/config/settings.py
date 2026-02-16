from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    claude_api_key: str = Field(alias="CLAUDE_API_KEY")
    claude_url: str = Field(alias="CLAUDE_URL")
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    groq_url: str = Field(alias="GROQ_URL")
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")
    cohere_api_key: str = Field(alias="COHERE_API_KEY")

    llamaindex_embed_model: str = Field(
        default="text-embedding-3-small",
        alias="LLAMAINDEX_EMBED_MODEL",
    )
    llamaindex_chunk_size: int = Field(default=512, alias="LLAMAINDEX_CHUNK_SIZE")
    llamaindex_chunk_overlap: int = Field(default=64, alias="LLAMAINDEX_CHUNK_OVERLAP")


_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings
