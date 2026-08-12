from abc import ABC, abstractmethod
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class CollectedRecord(BaseModel):
    source: str
    url: HttpUrl
    timestamp: datetime
    content: str
    source_type: str
    credibility: float = Field(ge=0.0, le=1.0)


class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> list[CollectedRecord]:
        raise NotImplementedError
