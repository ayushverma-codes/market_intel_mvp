from app.config import Settings
from app.confidence.gate import decide


def test_high_confidence():
    settings = Settings(confidence_high_threshold=0.8, confidence_medium_threshold=0.55, minimum_evidence_quality=0.6)
    assert decide(confidence=0.9, meaningful=True, evidence_quality=0.9, settings=settings).status == "high"


def test_medium_confidence():
    settings = Settings(confidence_high_threshold=0.8, confidence_medium_threshold=0.55, minimum_evidence_quality=0.6)
    assert decide(confidence=0.7, meaningful=True, evidence_quality=0.8, settings=settings).status == "medium"


def test_low_for_weak_evidence():
    settings = Settings(confidence_high_threshold=0.8, confidence_medium_threshold=0.55, minimum_evidence_quality=0.6)
    assert decide(confidence=0.95, meaningful=True, evidence_quality=0.3, settings=settings).status == "low"


def test_low_for_non_meaningful():
    settings = Settings()
    assert decide(confidence=0.95, meaningful=False, evidence_quality=0.95, settings=settings).status == "low"
