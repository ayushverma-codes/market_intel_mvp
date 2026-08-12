from pathlib import Path

from app.agents.schemas import AggregatorOutput
from app.config import Settings
from app.llm.client import LLMResult, NIMClient

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "aggregator_agent.txt"


class AggregatorAgent:
    def __init__(self, settings: Settings):
        self.llm = NIMClient(settings)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, payload: dict) -> LLMResult:
        return self.llm.structured(system_prompt=self.system_prompt, user_payload=payload, schema=AggregatorOutput)
