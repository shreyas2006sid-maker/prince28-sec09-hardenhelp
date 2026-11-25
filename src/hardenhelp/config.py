"""All settings come from environment variables (or a local .env file)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from hardenhelp.db.url import to_asyncpg_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "hardenhelp"
    app_env: Literal["local", "ci", "production"]
    git_sha: str = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    data_file: Path = Path("data/sample_records.json")
    prompts_dir: Path = Path("prompts")
    database_url: str = "postgresql://localhost:5432/hardenhelp"

    # Primary LLM: Gemini
    llm_primary_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_api_key: str = ""
    llm_primary_model: str = "gemini-3.5-flash"

    # Fallback LLM: Groq
    llm_fallback_base_url: str = "https://api.groq.com/openai/v1"
    groq_api_key: str = ""
    llm_fallback_model: str = "openai/gpt-oss-20b"

    # Shared LLM settings
    llm_timeout_seconds: float = 30.0
    usd_inr: float = 85.0

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        return to_asyncpg_url(value)


@lru_cache
def get_settings() -> Settings:
    """Build the settings once and reuse them."""
    return Settings()
