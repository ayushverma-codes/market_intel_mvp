from .base import BaseCollector, CollectedRecord
from .reddit import RedditCollector
from .rss import RSSCollector

__all__ = ["BaseCollector", "CollectedRecord", "RSSCollector", "RedditCollector"]
