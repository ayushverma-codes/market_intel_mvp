from typing import Any, TypedDict


class MarketState(TypedDict, total=False):
    trend_id: int
    insight_id: int
    trend: dict[str, Any]
    signals: list[dict[str, Any]]
    trend_agent: dict[str, Any]
    consumer_agent: dict[str, Any]
    ingredient_agent: dict[str, Any]
    india_relevance: dict[str, Any]
    business_opportunity: dict[str, Any]
    aggregation: dict[str, Any]
    gate_status: str
