import logging
import sys
import time

from sqlalchemy import select

from app.agents import TrendAgent
from app.collectors import RedditCollector, RSSCollector
from app.config import get_settings
from app.database import SessionLocal
from app.database.models import Signal, Trend
from app.ingestion import persist_records
from app.orchestration import MarketGraph
from app.processing import deduplicate
from app.signals import NIMEmbeddingProvider, SentenceTransformerProvider, SignalExtractor, build_signals
from app.trends import TrendDetector


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


logger = logging.getLogger(__name__)


def collect_all():
    settings = get_settings()
    collectors = [RSSCollector(settings.rss_feed_list)]
    if settings.reddit_subreddit_list:
        collectors.append(RedditCollector(settings.reddit_subreddit_list, settings.reddit_limit))
    records = []
    for collector in collectors:
        try:
            records.extend(collector.collect())
        except Exception:
            logger.exception("Collector failed: %s", collector.__class__.__name__)
    records = deduplicate(records)
    with SessionLocal() as db:
        return persist_records(db, records)


def run_signal_extraction():
    settings = get_settings()
    with SessionLocal() as db:
        from app.database.models import Source
        sources = db.scalars(select(Source)).all()
        # extractor = SignalExtractor(top_k=5)
        extractor = SignalExtractor(max_signals=5)
        embedder = NIMEmbeddingProvider(settings) if settings.nim_embedding_model else SentenceTransformerProvider(settings.embedding_model_name)
        return build_signals(db, sources, extractor, embedder)


def run_trend_detection():
    settings = get_settings()
    with SessionLocal() as db:
        detector = TrendDetector(
            lookback_hours=settings.trend_lookback_hours,
            recent_hours=settings.trend_recent_hours,
            min_signals=settings.trend_min_signals,
            top_k=settings.trend_top_k,
        )
        return detector.detect(db)


def run_trend_agent(trend_id: int | None = None):
    settings = get_settings()
    agent = TrendAgent(settings)
    with SessionLocal() as db:
        trend = db.get(Trend, trend_id) if trend_id else db.scalar(select(Trend).order_by(Trend.trend_score.desc()))
        if trend is None:
            raise RuntimeError("No trend found. Run trend detection first.")
        signals = db.scalars(select(Signal).where(Signal.topic == trend.topic).order_by(Signal.timestamp.desc()).limit(50)).all()
        evidence = [
            {
                "topic": s.topic,
                "timestamp": s.timestamp.isoformat(),
                "source": s.source.source,
                "source_type": s.source.source_type,
                "credibility": s.source.credibility,
                "url": s.source.url,
                "content": s.source.content[:500],
            }
            for s in signals
        ]
        result = agent.run(trend=trend.topic, trend_score=trend.trend_score, growth_rate=trend.growth_rate, signals=evidence)
        logger.info("Trend Agent output: %s", result.value.model_dump_json(indent=2))
        return result.value


def run_pipeline(trend_id: int | None = None):
    collect_all()
    run_signal_extraction()
    trends = run_trend_detection()
    if not trends:
        logger.warning("No trends detected")
        return None
    selected_id = trend_id or trends[0].id
    result = MarketGraph(get_settings()).run(selected_id)
    logger.info("End-to-end insight completed: %s", result.get("gate_status"))
    return result


def run_scheduler():
    settings = get_settings()
    interval = max(1, settings.schedule_interval_minutes) * 60
    logger.info("Scheduler started; interval=%s minutes", settings.schedule_interval_minutes)
    while True:
        try:
            run_pipeline()
        except Exception:
            logger.exception("Scheduled pipeline failed")
        time.sleep(interval)


def main() -> None:
    configure_logging()
    command = sys.argv[1] if len(sys.argv) > 1 else "all"
    if command == "collect":
        logger.info("Persisted %d new source records", len(collect_all()))
    elif command == "signals":
        logger.info("Created %d signals", len(run_signal_extraction()))
    elif command == "trends":
        logger.info("Updated %d trends", len(run_trend_detection()))
    elif command == "agent":
        run_trend_agent(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif command == "graph":
        trend_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        with SessionLocal() as db:
            trend = db.get(Trend, trend_id) if trend_id else db.scalar(select(Trend).order_by(Trend.trend_score.desc()))
            if not trend:
                raise RuntimeError("No trend found. Run: python -m app.main trends")
            result = MarketGraph(get_settings()).run(trend.id)
            logger.info("Graph finished: %s", result.get("gate_status"))
    elif command == "all":
        run_pipeline()
    elif command == "schedule":
        run_scheduler()
    else:
        raise SystemExit("Usage: python -m app.main [collect|signals|trends|agent [TREND_ID]|graph [TREND_ID]|all|schedule]")


if __name__ == "__main__":
    main()
