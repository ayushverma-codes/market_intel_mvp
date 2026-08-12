"""Shared exception hierarchy so every layer of the pipeline fails predictably."""


class CIEError(Exception):
    """Base class for all application-raised errors."""


class ConfigurationError(CIEError):
    """Raised when required configuration/env vars are missing or invalid."""


class CollectorError(CIEError):
    """Raised when a data collector fails to fetch/parse a source."""


class IngestionError(CIEError):
    """Raised during normalization/deduplication of raw records."""


class SignalExtractionError(CIEError):
    """Raised when signal extraction or embedding generation fails."""


class TrendDetectionError(CIEError):
    """Raised when trend scoring fails."""


class LLMProviderError(CIEError):
    """Raised when a call to the configured LLM provider fails."""


class AgentError(CIEError):
    """Raised when a LangGraph agent node fails to produce valid structured output."""


class AggregationError(CIEError):
    """Raised when the Aggregator Agent cannot reconcile agent outputs."""


class NotificationError(CIEError):
    """Raised when pushing a final insight (e.g. to Slack) fails."""
