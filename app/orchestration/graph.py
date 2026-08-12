import logging
from datetime import datetime, timezone

from langgraph.graph import END, START, StateGraph
from sqlalchemy import select

from app.agents.aggregator_agent import AggregatorAgent
from app.agents.business_agent import BusinessOpportunityAgent
from app.agents.consumer_agent import run_placeholder as consumer_placeholder
from app.agents.ingredient_agent import run_placeholder as ingredient_placeholder
from app.agents.india_agent import IndiaRelevanceAgent
from app.agents.trend_agent import TrendAgent
from app.config import Settings
from app.confidence.gate import decide
from app.database.models import Insight, Signal, Trend
from app.database.session import SessionLocal
from app.notifications.slack import send_hitl, send_slack
from app.orchestration.events import record_event
from app.orchestration.state import MarketState

logger = logging.getLogger(__name__)


def utcnow():
    return datetime.now(timezone.utc)


class MarketGraph:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.trend_agent = TrendAgent(settings)
        self.india_agent = IndiaRelevanceAgent(settings)
        self.business_agent = BusinessOpportunityAgent(settings)
        self.aggregator_agent = AggregatorAgent(settings)

    def _load_context(self, trend_id: int) -> tuple[dict, list[dict]]:
        with SessionLocal() as db:
            trend = db.get(Trend, trend_id)
            if trend is None:
                raise ValueError(f"Trend {trend_id} not found")
            signals = db.scalars(
                select(Signal)
                .where(Signal.topic == trend.topic)
                .order_by(Signal.timestamp.desc())
                .limit(self.settings.agent_max_signals)
            ).all()
            trend_data = {
                "id": trend.id,
                "topic": trend.topic,
                "trend_score": trend.trend_score,
                "growth_rate": trend.growth_rate,
                "first_seen": trend.first_seen.isoformat(),
                "last_seen": trend.last_seen.isoformat(),
            }
            signal_data = [
                {
                    "id": s.id,
                    "topic": s.topic,
                    "entity": s.entity,
                    "timestamp": s.timestamp.isoformat(),
                    "source": s.source.source,
                    "source_type": s.source.source_type,
                    "credibility": s.source.credibility,
                    "url": s.source.url,
                    "content": s.source.content[:700],
                }
                for s in signals
            ]
            return trend_data, signal_data

    def _create_draft(self, trend_id: int) -> int:
        with SessionLocal() as db:
            insight = Insight(
                trend_id=trend_id,
                recommendation="Processing",
                status="processing",
                evidence={},
            )
            db.add(insight)
            db.commit()
            db.refresh(insight)
            return insight.id

    def build(self):
        graph = StateGraph(MarketState)
        graph.add_node("prepare", self.prepare)
        graph.add_node("trend_agent", self.trend_agent_node)
        graph.add_node("consumer_agent", self.consumer_agent_node)
        graph.add_node("ingredient_agent", self.ingredient_agent_node)
        graph.add_node("india_relevance", self.india_node)
        graph.add_node("business_opportunity", self.business_node)
        graph.add_node("aggregator", self.aggregator_node)
        graph.add_node("confidence_gate", self.gate_node)
        graph.add_node("notification", self.notification_node)

        graph.add_edge(START, "prepare")
        # Parallel specialist stage.
        graph.add_edge("prepare", "trend_agent")
        graph.add_edge("prepare", "consumer_agent")
        graph.add_edge("prepare", "ingredient_agent")
        # Fan-in after all specialist nodes complete.
        graph.add_edge("trend_agent", "india_relevance")
        graph.add_edge("consumer_agent", "india_relevance")
        graph.add_edge("ingredient_agent", "india_relevance")
        graph.add_edge("india_relevance", "business_opportunity")
        graph.add_edge("business_opportunity", "aggregator")
        graph.add_edge("aggregator", "confidence_gate")
        graph.add_edge("confidence_gate", "notification")
        graph.add_edge("notification", END)
        return graph.compile()

    def prepare(self, state: MarketState) -> dict:
        trend, signals = self._load_context(state["trend_id"])
        return {"trend": trend, "signals": signals}

    def trend_agent_node(self, state: MarketState) -> dict:
        started = utcnow()
        with SessionLocal() as db:
            try:
                result = self.trend_agent.run(
                    trend=state["trend"]["topic"],
                    trend_score=state["trend"]["trend_score"],
                    growth_rate=state["trend"]["growth_rate"],
                    signals=state["signals"],
                )
                record_event(db, insight_id=state["insight_id"], agent="trend_agent", started=started, result=result, settings=self.settings)
                db.commit()
                return {"trend_agent": result.value.model_dump()}
            except Exception:
                record_event(db, insight_id=state["insight_id"], agent="trend_agent", started=started, status="failed")
                db.commit()
                raise

    def consumer_agent_node(self, state: MarketState) -> dict:
        started = utcnow()
        result = consumer_placeholder(trend=state["trend"]["topic"], signals=state["signals"])
        with SessionLocal() as db:
            record_event(db, insight_id=state["insight_id"], agent="consumer_agent", started=started, status="placeholder")
            db.commit()
        return {"consumer_agent": result.model_dump()}

    def ingredient_agent_node(self, state: MarketState) -> dict:
        started = utcnow()
        result = ingredient_placeholder(trend=state["trend"]["topic"], signals=state["signals"])
        with SessionLocal() as db:
            record_event(db, insight_id=state["insight_id"], agent="ingredient_agent", started=started, status="placeholder")
            db.commit()
        return {"ingredient_agent": result.model_dump()}

    def india_node(self, state: MarketState) -> dict:
        started = utcnow()
        payload = {
            "trend": state["trend"],
            "trend_agent": state["trend_agent"],
            "consumer_agent": state["consumer_agent"],
            "ingredient_agent": state["ingredient_agent"],
            "signals": state["signals"],
        }
        with SessionLocal() as db:
            try:
                result = self.india_agent.run(payload)
                record_event(db, insight_id=state["insight_id"], agent="india_relevance_agent", started=started, result=result, settings=self.settings)
                db.commit()
                return {"india_relevance": result.value.model_dump()}
            except Exception:
                record_event(db, insight_id=state["insight_id"], agent="india_relevance_agent", started=started, status="failed")
                db.commit()
                raise

    def business_node(self, state: MarketState) -> dict:
        started = utcnow()
        payload = {
            "trend": state["trend"],
            "trend_agent": state["trend_agent"],
            "consumer_agent": state["consumer_agent"],
            "ingredient_agent": state["ingredient_agent"],
            "india_relevance": state["india_relevance"],
            "signals": state["signals"],
        }
        with SessionLocal() as db:
            try:
                result = self.business_agent.run(payload)
                record_event(db, insight_id=state["insight_id"], agent="business_opportunity_agent", started=started, result=result, settings=self.settings)
                db.commit()
                return {"business_opportunity": result.value.model_dump()}
            except Exception:
                record_event(db, insight_id=state["insight_id"], agent="business_opportunity_agent", started=started, status="failed")
                db.commit()
                raise

    def aggregator_node(self, state: MarketState) -> dict:
        started = utcnow()
        payload = {
            "trend": state["trend"],
            "trend_agent": state["trend_agent"],
            "consumer_agent": state["consumer_agent"],
            "ingredient_agent": state["ingredient_agent"],
            "india_relevance": state["india_relevance"],
            "business_opportunity": state["business_opportunity"],
            "signals": state["signals"],
        }
        with SessionLocal() as db:
            try:
                result = self.aggregator_agent.run(payload)
                record_event(db, insight_id=state["insight_id"], agent="aggregator_agent", started=started, result=result, settings=self.settings)
                db.commit()
                return {"aggregation": result.value.model_dump()}
            except Exception:
                record_event(db, insight_id=state["insight_id"], agent="aggregator_agent", started=started, status="failed")
                db.commit()
                raise

    def gate_node(self, state: MarketState) -> dict:
        aggregation = state["aggregation"]
        decision = decide(
            confidence=aggregation["confidence"],
            meaningful=aggregation["meaningful"],
            evidence_quality=aggregation["evidence_quality"],
            settings=self.settings,
        )
        with SessionLocal() as db:
            insight = db.get(Insight, state["insight_id"])
            assert insight is not None
            insight.india_relevance = state["india_relevance"]["india_relevance"]
            insight.business_impact = aggregation["business_impact"]
            insight.confidence = aggregation["confidence"]
            insight.recommendation = aggregation["recommendation"]
            insight.status = decision.status
            insight.evidence = {
                "trend": state["trend_agent"],
                "india_relevance": state["india_relevance"],
                "business_opportunity": state["business_opportunity"],
                "aggregation": aggregation,
            }
            db.commit()
        return {"gate_status": decision.status}

    def notification_node(self, state: MarketState) -> dict:
        status = state["gate_status"]
        with SessionLocal() as db:
            insight = db.get(Insight, state["insight_id"])
            assert insight is not None
            message = (
                f"*Market Intelligence — {status.upper()}*\n"
                f"Trend: {state['trend']['topic']}\n"
                f"Confidence: {state['aggregation']['confidence']:.2f}\n"
                f"India relevance: {state['india_relevance']['india_relevance']:.2f}\n"
                f"Recommendation: {state['aggregation']['recommendation']}"
            )
            try:
                if status == "high":
                    send_slack(message, self.settings)
                elif status == "medium":
                    send_hitl(
                        {
                            "insight_id": insight.id,
                            "status": "pending_review",
                            "trend": state["trend"]["topic"],
                            "confidence": state["aggregation"]["confidence"],
                            "recommendation": state["aggregation"]["recommendation"],
                        },
                        self.settings,
                    )
                    insight.status = "pending_review"
                    db.commit()
            except Exception:
                logger.exception("Notification failed for insight %s", insight.id)
        return {}

    def run(self, trend_id: int) -> dict:
        insight_id = self._create_draft(trend_id)
        graph = self.build()
        try:
            return graph.invoke({"trend_id": trend_id, "insight_id": insight_id})
        except Exception:
            with SessionLocal() as db:
                insight = db.get(Insight, insight_id)
                if insight:
                    insight.status = "failed"
                    db.commit()
            raise
