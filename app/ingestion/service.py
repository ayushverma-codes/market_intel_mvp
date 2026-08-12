from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.base import CollectedRecord
from app.database.models import Source
from app.processing.normalize import normalize_text


def persist_records(db: Session, records: list[CollectedRecord]) -> list[Source]:
    persisted: list[Source] = []
    for record in records:
        url = str(record.url).rstrip("/")
        existing = db.scalar(select(Source).where(Source.url == url))
        if existing:
            continue
        source = Source(
            source=record.source,
            url=url,
            timestamp=record.timestamp,
            content=normalize_text(record.content),
            source_type=record.source_type,
            credibility=record.credibility,
        )
        db.add(source)
        persisted.append(source)
    db.commit()
    return persisted
