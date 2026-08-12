from pathlib import Path

from app.agents.schemas import TrendAgentOutput
from app.config import Settings
from app.llm.client import LLMResult, NIMClient

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "trend_agent.txt"


class TrendAgent:
    def __init__(self, settings: Settings):
        self.llm = NIMClient(settings)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, *, trend: str, trend_score: float, growth_rate: float, signals: list[dict]) -> LLMResult:
        payload = {
            "trend": trend,
            "trend_score": round(trend_score, 4),
            "growth_rate": round(growth_rate, 4),
            "signal_count": len(signals),
            "signals": signals,
        }
        return self.llm.structured(system_prompt=self.system_prompt, user_payload=payload, schema=TrendAgentOutput)
