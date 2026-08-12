from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Signal, Source
from app.processing.normalize import content_hash
from app.signals.embeddings import EmbeddingProvider
from app.signals.extractor import SignalExtractor


def build_signals(db: Session, sources: list[Source], extractor: SignalExtractor, embedder: EmbeddingProvider) -> list[Signal]:
    candidates: list[tuple[Source, str, str]] = []
    for source in sources:
        for item in extractor.extract(source.content):
            candidates.append((source, item.topic, content_hash(f"{source.id}:{item.topic}")))

    if not candidates:
        return []

    vectors = embedder.embed([topic for _, topic, _ in candidates])
    created: list[Signal] = []
    for (source, topic, h), vector in zip(candidates, vectors):
        exists = db.scalar(
            select(Signal).where(Signal.source_id == source.id, Signal.content_hash == h)
        )
        if exists:
            continue
        signal = Signal(
            source_id=source.id,
            topic=topic,
            entity=None,
            timestamp=source.timestamp,
            embedding=vector,
        )
        signal.content_hash = h
        db.add(signal)
        created.append(signal)
    db.commit()
    return created
