from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://marketintel:marketintel@localhost:5432/marketintel"

    nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nim_api_key: str = Field(default="", repr=False)
    nim_llm_model: str = "meta/llama-3.1-8b-instruct"
    nim_embedding_base_url: str | None = None
    nim_embedding_api_key: str | None = Field(default=None, repr=False)
    nim_embedding_model: str | None = None
    nim_max_tokens: int = 700
    nim_temperature: float = 0.0
    embedding_dimension: int = 384
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    rss_feeds: str = ""
    reddit_subreddits: str = "FoodIndustry,india,IndianFood,HealthyFood"
    reddit_limit: int = 25

    trend_lookback_hours: int = 168
    trend_recent_hours: int = 24
    trend_min_signals: int = 3
    trend_top_k: int = 20
    trend_min_score: float = 0.10

    @property
    def rss_feed_list(self) -> list[str]:
        return [x.strip() for x in self.rss_feeds.split(",") if x.strip()]

    @property
    def reddit_subreddit_list(self) -> list[str]:
        return [x.strip() for x in self.reddit_subreddits.split(",") if x.strip()]

    confidence_high_threshold: float = 0.80
    confidence_medium_threshold: float = 0.55
    minimum_evidence_quality: float = 0.60

    slack_webhook_url: str | None = None
    slack_channel: str | None = None
    hitl_webhook_url: str | None = None

    schedule_interval_minutes: int = 360
    agent_max_signals: int = 50
    llm_cost_per_1k_tokens_usd: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
