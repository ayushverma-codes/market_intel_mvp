"""
Entry point.

At this stage (Step 1) this only proves the project boots: settings load
from .env, logging is configured, and the NVIDIA NIM provider config is
readable. The actual scheduler -> collectors -> ... -> Slack pipeline gets
wired in here incrementally in later steps (see project README).
"""
from app.config.logging_config import get_logger
from app.config.settings import get_settings

logger = get_logger(__name__)


def main() -> None:
    settings = get_settings()

    logger.info("Central Consumer Intelligence Engine -- booting (env=%s)", settings.app_env)
    logger.info("LLM provider: %s (chat_model=%s)", settings.llm_provider, settings.nvidia_nim_chat_model)
    logger.info("Embedding provider: %s (model=%s)", settings.embedding_provider, settings.nvidia_nim_embedding_model)
    logger.info(
        "Confidence gate thresholds: high>=%.2f, medium>=%.2f",
        settings.confidence_high_threshold,
        settings.confidence_medium_threshold,
    )

    if not settings.nvidia_nim_api_key:
        logger.warning(
            "NVIDIA_NIM_API_KEY is not set. LLM-backed agents (Trend, India Relevance, "
            "Business Opportunity, Aggregator) will fail until it is configured in .env."
        )

    logger.info("Step 1 complete: configuration and logging are working. Pipeline stages are not wired yet.")


if __name__ == "__main__":
    main()
