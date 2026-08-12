from collections.abc import Iterable

from app.collectors.base import CollectedRecord
from app.processing.normalize import content_hash


def deduplicate(records: Iterable[CollectedRecord]) -> list[CollectedRecord]:
    seen_urls: set[str] = set()
    seen_content: set[str] = set()
    unique: list[CollectedRecord] = []
    for record in records:
        url = str(record.url).rstrip("/")
        h = content_hash(record.content)
        if url in seen_urls or h in seen_content:
            continue
        seen_urls.add(url)
        seen_content.add(h)
        unique.append(record.model_copy(update={"content": record.content.strip()}))
    return unique
