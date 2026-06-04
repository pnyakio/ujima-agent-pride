from enum import Enum
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class ProviderName(str, Enum):
    COHERE = "Cohere"
    GEMINI = "Gemini"
    CEREBRAS = "Cerebras"


class LLMConfig(BaseSettings):
    cohere_api_key: str = Field("", env="COHERE_API_KEY")
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
    cerebras_api_key: str = Field("", env="CEREBRAS_API_KEY")
    cohere_model: str = Field("xlarge", env="COHERE_MODEL")
    gemini_model: str = Field("gemini-1.0-mini", env="GEMINI_MODEL")
    cerebras_model: str = Field("cerebras-standard", env="CEREBRAS_MODEL")
    default_provider: ProviderName = Field(ProviderName.COHERE, env="LLM_DEFAULT_PROVIDER")
    enable_local_fallback: bool = Field(True, env="ENABLE_LOCAL_FALLBACK")

    @validator("default_provider", pre=True)
    def normalize_provider(cls, value: str) -> ProviderName:
        if isinstance(value, str):
            normalized = value.strip().capitalize()
            return ProviderName(normalized)
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


llm_config = LLMConfig()
