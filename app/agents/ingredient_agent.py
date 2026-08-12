from app.agents.schemas import IngredientAgentOutput


def run_placeholder(*, trend: str, signals: list[dict]) -> IngredientAgentOutput:
    """Reserved interface for the future Ingredient/Product Agent."""
    return IngredientAgentOutput(status="placeholder", ingredients=[], product_formats=[], confidence=0.0)
