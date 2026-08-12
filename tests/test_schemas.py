from app.agents.schemas import AggregatorOutput, IndiaRelevanceOutput, TrendAgentOutput


def test_trend_schema():
    item = TrendAgentOutput(
        trend="high-protein snacks",
        trend_strength=0.87,
        evidence=["25 supporting signals"],
        supporting_signal_count=25,
        confidence=0.84,
    )
    assert item.confidence == 0.84


def test_downstream_schemas():
    IndiaRelevanceOutput(india_relevance=0.8, reasoning=[], target_segments=[], regional_notes=[])
    AggregatorOutput(
        meaningful=True,
        confidence=0.8,
        business_impact=0.7,
        recommendation="Test the opportunity",
        evidence_quality=0.8,
    )
