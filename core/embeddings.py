import os
from abc import ABC, abstractmethod
from typing import List, Optional

import requests
from langchain_cohere import CohereEmbeddings
from langchain_core.embeddings import Embeddings

from core.config import settings


class EmbeddingStrategy(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass


class LocalEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self):
        self._embeddings: Optional[CohereEmbeddings] = None

    def get_embeddings(self) -> CohereEmbeddings:
        if self._embeddings is None:
            self._embeddings = CohereEmbeddings(
                model="embed-multilingual-v3.0",
                cohere_api_key=settings.cohere_api_key,
            )
        return self._embeddings

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        emb = self.get_embeddings()
        return emb.embed_documents(texts)


class CloudEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self, model: Optional[str] = None):
        self.api_url = settings.cloud_embed_url.rstrip("/") + "/embed"
        self.api_key = settings.cloud_embed_api_key
        self.model = model or settings.cloud_embed_model

    def get_embeddings(self) -> Embeddings:
        return _CloudEmbeddingProxy(self)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"texts": texts, "model": self.model}
        if self.api_key:
            payload["api_key"] = self.api_key

        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["embeddings"]


class _CloudEmbeddingProxy(Embeddings):
    def __init__(self, strategy: CloudEmbeddingStrategy):
        self._strategy = strategy

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._strategy.embed_texts(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._strategy.embed_texts([text])[0]


def get_embedding_strategy(
    mode: Optional[str] = None,
    model: Optional[str] = None,
) -> EmbeddingStrategy:
    mode = mode or settings.embedding_mode
    if mode == "cloud":
        if not settings.cloud_embed_url:
            raise ValueError(
                "CLOUD_EMBED_URL must be set when EMBEDDING_MODE=cloud"
            )
        return CloudEmbeddingStrategy(model=model)
    if mode == "local":
        return LocalEmbeddingStrategy()
    raise ValueError(f"Unknown embedding mode: {mode}")
