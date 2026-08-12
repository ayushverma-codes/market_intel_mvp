from pydantic import BaseModel, Field


class TrendAgentOutput(BaseModel):
    trend: str
    trend_strength: float = Field(ge=0.0, le=1.0)
    evidence: list[str]
    supporting_signal_count: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)


class ConsumerAgentOutput(BaseModel):
    consumer_signals: list[str] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: str = "placeholder"


class IngredientAgentOutput(BaseModel):
    ingredients: list[str] = []
    product_formats: list[str] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: str = "placeholder"


class IndiaRelevanceOutput(BaseModel):
    india_relevance: float = Field(ge=0.0, le=1.0)
    reasoning: list[str]
    target_segments: list[str]
    regional_notes: list[str]


class BusinessOpportunity(BaseModel):
    product: str = ""
    marketing: str = ""
    pricing: str = ""
    packaging: str = ""
    positioning: str = ""


class BusinessOpportunityOutput(BaseModel):
    opportunities: list[BusinessOpportunity] = []
    recommendation: str = ""
    business_impact: float = 0.0
    confidence: float = 0.0


class AggregatorOutput(BaseModel):
    meaningful: bool
    confidence: float = Field(ge=0.0, le=1.0)
    business_impact: float = Field(ge=0.0, le=1.0)
    recommendation: str
    evidence_quality: float = Field(ge=0.0, le=1.0)
    conflicts: list[str] = []
    rationale: list[str] = []
