from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import Settings
from app.database.models import AgentEvent
from app.llm.client import LLMResult


def utcnow():
    return datetime.now(timezone.utc)


def record_event(
    db: Session,
    *,
    insight_id: int,
    agent: str,
    started: datetime,
    result: LLMResult | None = None,
    settings: Settings | None = None,
    status: str = "success",
) -> None:
    db.add(
        AgentEvent(
            insight_id=insight_id,
            agent=agent,
            start_time=started,
            end_time=utcnow(),
            tokens=result.total_tokens if result else 0,
            cost=((result.total_tokens / 1000.0) * settings.llm_cost_per_1k_tokens_usd) if result and settings else 0.0,
            status=status,
        )
    )


def estimated_cost(result: LLMResult, settings: Settings) -> float:
    return (result.total_tokens / 1000.0) * settings.llm_cost_per_1k_tokens_usd
