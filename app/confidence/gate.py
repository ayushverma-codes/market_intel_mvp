from dataclasses import dataclass

from app.config import Settings


@dataclass(frozen=True)
class GateDecision:
    status: str
    confidence: float


def decide(*, confidence: float, meaningful: bool, evidence_quality: float, settings: Settings) -> GateDecision:
    if not meaningful or evidence_quality < settings.minimum_evidence_quality:
        return GateDecision("low", confidence)
    if confidence >= settings.confidence_high_threshold:
        return GateDecision("high", confidence)
    if confidence >= settings.confidence_medium_threshold:
        return GateDecision("medium", confidence)
    return GateDecision("low", confidence)
