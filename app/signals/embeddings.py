from abc import ABC, abstractmethod

from openai import OpenAI
from sentence_transformers import SentenceTransformer

from app.config import Settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class NIMEmbeddingProvider(EmbeddingProvider):
    def __init__(self, settings: Settings):
        self.client = OpenAI(
            api_key=settings.nim_embedding_api_key or settings.nim_api_key,
            base_url=settings.nim_embedding_base_url or settings.nim_base_url,
        )
        if not settings.nim_embedding_model:
            raise ValueError("NIM_EMBEDDING_MODEL is required for NIM embeddings")
        self.model = settings.nim_embedding_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()
