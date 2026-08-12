from app.agents.schemas import ConsumerAgentOutput


def run_placeholder(*, trend: str, signals: list[dict]) -> ConsumerAgentOutput:
    """Reserved interface for the future Consumer Agent."""
    return ConsumerAgentOutput(status="placeholder", consumer_signals=[], confidence=0.0)
