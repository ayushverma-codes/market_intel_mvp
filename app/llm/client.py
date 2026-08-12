import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.config import Settings

T = TypeVar("T", bound=BaseModel)


@dataclass
class LLMResult:
    value: BaseModel
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0

    @property
    def estimated_cost_usd(self) -> float:
        return 0.0


class NIMClient:
    """Small provider wrapper. NVIDIA NIM exposes an OpenAI-compatible API."""

    def __init__(self, settings: Settings):
        if not settings.nim_api_key:
            raise ValueError("NIM_API_KEY is required")
        self.client = OpenAI(api_key=settings.nim_api_key, base_url=settings.nim_base_url)
        self.model = settings.nim_llm_model
        self.max_tokens = settings.nim_max_tokens
        self.temperature = settings.nim_temperature

    def structured(self, *, system_prompt: str, user_payload: dict[str, Any], schema: type[T]) -> LLMResult:
        started = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, default=str)},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        try:
            value = schema.model_validate_json(content)
        except ValidationError as exc:
            raise ValueError(f"NIM returned invalid {schema.__name__}: {content}") from exc
        usage = response.usage
        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0
        return LLMResult(
            value=value,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=round((time.perf_counter() - started) * 1000),
        )
