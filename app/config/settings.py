"""
Central application configuration.

All runtime configuration is loaded from environment variables / a .env file
via pydantic-settings. Nothing in the codebase should hard-code secrets,
model names, or thresholds -- they all flow through this module so behavior
can change without touching code.
"""
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # ---------------------------------------------------------------- app
    app_env: Literal["local", "dev", "staging", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ---------------------------------------------------------- database
    database_url: str = Field(
        default="postgresql+psycopg://cie_user:cie_password@localhost:5432/cie",
        description="SQLAlchemy connection string for PostgreSQL.",
    )
    db_echo: bool = False

    # ---------------------------------------------------- LLM provider(s)
    # The system is designed to be provider-agnostic. Default provider is
    # NVIDIA NIM (OpenAI-compatible /v1/chat/completions API), but this can
    # be swapped (e.g. to "openai" or "anthropic") purely through env vars
    # without touching agent code -- see app/agents/llm_client.py.
    llm_provider: Literal["nvidia_nim", "openai", "anthropic"] = "nvidia_nim"

    # NVIDIA NIM settings (build.nvidia.com or a self-hosted NIM endpoint)
    nvidia_nim_api_key: Optional[str] = Field(default=None, repr=False)
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_nim_chat_model: str = "meta/llama-3.1-70b-instruct"
    nvidia_nim_embedding_model: str = "nvidia/nv-embedqa-e5-v5"

    # Generic LLM behavior knobs (provider-independent)
    llm_temperature: float = 0.2
    llm_max_tokens: int = 1024
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 3

    # Embeddings are configurable independently of the chat model in case a
    # different provider/model is preferred for vectorization.
    embedding_provider: Literal["nvidia_nim", "openai"] = "nvidia_nim"
    embedding_dimensions: int = 1024

    # --------------------------------------------------------- scheduler
    collection_interval_minutes: int = 60

    # ------------------------------------------------------- confidence
    # Thresholds for the Confidence Gate (Section 14). Configurable, never
    # hard-coded in the aggregator/gate logic itself.
    confidence_high_threshold: float = 0.75
    confidence_medium_threshold: float = 0.45

    # ------------------------------------------------------------ slack
    slack_webhook_url: Optional[str] = Field(default=None, repr=False)
    slack_channel: str = "#market-intelligence"

    # ---------------------------------------------------------- sources
    rss_feed_urls: str = ""  # comma-separated list, parsed in collectors
    reddit_client_id: Optional[str] = Field(default=None, repr=False)
    reddit_client_secret: Optional[str] = Field(default=None, repr=False)
    reddit_user_agent: str = "central-consumer-intelligence-engine/0.1"
    reddit_subreddits: str = ""  # comma-separated list

    @model_validator(mode="after")
    def _validate_provider_credentials(self) -> "Settings":
        if self.app_env != "local":
            if self.llm_provider == "nvidia_nim" and not self.nvidia_nim_api_key:
                raise ValueError(
                    "NVIDIA_NIM_API_KEY is required when llm_provider=nvidia_nim "
                    "outside local development."
                )
        return self

    @property
    def rss_feed_url_list(self) -> list[str]:
        return [u.strip() for u in self.rss_feed_urls.split(",") if u.strip()]

    @property
    def reddit_subreddit_list(self) -> list[str]:
        return [s.strip() for s in self.reddit_subreddits.split(",") if s.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor -- import and call this, don't instantiate Settings() directly."""
    return Settings()
