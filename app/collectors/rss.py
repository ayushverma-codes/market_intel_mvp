from datetime import datetime, timezone

import feedparser

from app.collectors.base import BaseCollector, CollectedRecord


class RSSCollector(BaseCollector):
    def __init__(self, feeds: list[str], credibility: float = 0.75):
        self.feeds = feeds
        self.credibility = credibility

    def collect(self) -> list[CollectedRecord]:
        records: list[CollectedRecord] = []
        for feed_url in self.feeds:
            parsed = feedparser.parse(feed_url)
            feed_name = parsed.feed.get("title", feed_url)
            for entry in parsed.entries:
                content = entry.get("summary") or entry.get("description") or entry.get("title", "")
                url = entry.get("link")
                if not url or not content.strip():
                    continue
                ts = entry.get("published_parsed") or entry.get("updated_parsed")
                timestamp = datetime(*ts[:6], tzinfo=timezone.utc) if ts else datetime.now(timezone.utc)
                records.append(
                    CollectedRecord(
                        source=feed_name,
                        url=url,
                        timestamp=timestamp,
                        content=content,
                        source_type="rss",
                        credibility=self.credibility,
                    )
                )
        return records
