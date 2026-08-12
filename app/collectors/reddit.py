from datetime import datetime, timezone

import httpx

from app.collectors.base import BaseCollector, CollectedRecord


class RedditCollector(BaseCollector):
    """Lightweight public JSON adapter; OAuth can replace this without changing the interface."""

    def __init__(self, subreddits: list[str], limit: int = 25, credibility: float = 0.55):
        self.subreddits = subreddits
        self.limit = limit
        self.credibility = credibility

    def collect(self) -> list[CollectedRecord]:
        records: list[CollectedRecord] = []
        headers = {"User-Agent": "market-intelligence-mvp/0.1"}
        with httpx.Client(timeout=15, headers=headers, follow_redirects=True) as client:
            for subreddit in self.subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                try:
                    response = client.get(url, params={"limit": self.limit})
                    response.raise_for_status()
                    children = response.json().get("data", {}).get("children", [])
                except (httpx.HTTPError, ValueError):
                    continue

                for child in children:
                    data = child.get("data", {})
                    title = data.get("title", "").strip()
                    body = data.get("selftext", "").strip()
                    content = f"{title}\n{body}".strip()
                    permalink = data.get("permalink")
                    if not content or not permalink:
                        continue
                    created = data.get("created_utc")
                    timestamp = datetime.fromtimestamp(created, tz=timezone.utc) if created else datetime.now(timezone.utc)
                    records.append(
                        CollectedRecord(
                            source=f"reddit:r/{subreddit}",
                            url=f"https://www.reddit.com{permalink}",
                            timestamp=timestamp,
                            content=content,
                            source_type="reddit",
                            credibility=self.credibility,
                        )
                    )
        return records
