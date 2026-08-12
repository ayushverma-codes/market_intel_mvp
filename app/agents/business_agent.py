from pathlib import Path

from app.agents.schemas import BusinessOpportunityOutput
from app.config import Settings
from app.llm.client import LLMResult, NIMClient

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "business_agent.txt"


class BusinessOpportunityAgent:
    def __init__(self, settings: Settings):
        self.llm = NIMClient(settings)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, payload: dict) -> LLMResult:
        return self.llm.structured(system_prompt=self.system_prompt, user_payload=payload, schema=BusinessOpportunityOutput)
