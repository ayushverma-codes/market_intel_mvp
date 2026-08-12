from collections import defaultdict
from datetime import datetime, timedelta, timezone
import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Signal, Trend


class TrendDetector:
    def __init__(self, lookback_hours: int = 168, recent_hours: int = 24, min_signals: int = 3, top_k: int = 20):
        self.lookback = timedelta(hours=lookback_hours)
        self.recent = timedelta(hours=recent_hours)
        self.min_signals = min_signals
        self.top_k = top_k

    def detect(self, db: Session, now: datetime | None = None) -> list[Trend]:
        now = now or datetime.now(timezone.utc)
        start = now - self.lookback
        recent_start = now - self.recent
        baseline_window_days = max((self.lookback - self.recent).total_seconds() / self.recent.total_seconds(), 1.0)

        signals = db.scalars(select(Signal).where(Signal.timestamp >= start)).all()
        stats: dict[str, dict] = defaultdict(lambda: {
            "total": 0,
            "recent": 0,
            "first_seen": now,
            "last_seen": start,
            "cred_sum": 0.0,
        })
        for signal in signals:
            key = signal.topic.strip().lower()
            if not key:
                continue
            s = stats[key]
            s["total"] += 1
            if signal.timestamp >= recent_start:
                s["recent"] += 1
            s["first_seen"] = min(s["first_seen"], signal.timestamp)
            s["last_seen"] = max(s["last_seen"], signal.timestamp)
            s["cred_sum"] += signal.source.credibility if signal.source else 0.5

        candidates = []
        max_total = max((x["total"] for x in stats.values()), default=1)
        for topic, s in stats.items():
            if s["total"] < self.min_signals:
                continue
            expected_recent = max((s["total"] - s["recent"]) / baseline_window_days, 0.1)
            growth_rate = (s["recent"] - expected_recent) / expected_recent
            growth_component = 1 / (1 + math.exp(-growth_rate))
            frequency_component = min(s["total"] / max_total, 1.0)
            velocity_component = min(s["recent"] / max(s["total"], 1), 1.0)
            credibility = s["cred_sum"] / s["total"]
            spike_component = min(s["recent"] / max(expected_recent, 1.0), 3.0) / 3.0
            score = (
                0.25 * frequency_component
                + 0.30 * growth_component
                + 0.20 * velocity_component
                + 0.15 * spike_component
                + 0.10 * credibility
            )
            candidates.append((score, topic, growth_rate, s))

        candidates.sort(reverse=True)
        trends: list[Trend] = []
        for score, topic, growth_rate, s in candidates[: self.top_k]:
            trend = db.scalar(select(Trend).where(Trend.topic == topic))
            if trend is None:
                trend = Trend(
                    topic=topic,
                    trend_score=score,
                    growth_rate=growth_rate,
                    first_seen=s["first_seen"],
                    last_seen=s["last_seen"],
                )
                db.add(trend)
            else:
                trend.trend_score = score
                trend.growth_rate = growth_rate
                trend.first_seen = min(trend.first_seen, s["first_seen"])
                trend.last_seen = max(trend.last_seen, s["last_seen"])
            trends.append(trend)

        db.commit()
        return trends
