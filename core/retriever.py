import os
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

from core.config import settings
from core.embeddings import get_embedding_strategy, EmbeddingStrategy


def _ensure_no_proxy_for_localhost():
    no_proxy = os.environ.get("NO_PROXY", "")
    localhost_entries = {"localhost", "127.0.0.1"}
    existing = {s.strip() for s in no_proxy.replace(";", ",").split(",") if s.strip()}
    missing = localhost_entries - existing
    if missing:
        separator = ";" if ";" in no_proxy else ","
        no_proxy_parts = [no_proxy] if no_proxy else []
        os.environ["NO_PROXY"] = separator.join(no_proxy_parts + sorted(missing))


def get_qdrant_client() -> QdrantClient:
    in_memory = os.getenv("QDRANT_IN_MEMORY", "").lower() == "true"
    if in_memory:
        return QdrantClient(":memory:")

    _ensure_no_proxy_for_localhost()

    kwargs = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantClient(**kwargs)


def _detect_embed_dim(embedding_strategy: EmbeddingStrategy) -> int:
    sample = embedding_strategy.embed_texts(["test"])
    return len(sample[0])


def _get_collection_info(client: QdrantClient):
    try:
        return client.get_collection(settings.collection_name)
    except Exception:
        return None


def ensure_collection(
    client: Optional[QdrantClient] = None,
    embedding_strategy: Optional[EmbeddingStrategy] = None,
):
    client = client or get_qdrant_client()
    try:
        dim = _detect_embed_dim(embedding_strategy) if embedding_strategy else settings.embed_dimension

        existing = _get_collection_info(client)

        if existing:
            current_dim = existing.config.params.vectors.size
            if current_dim == dim:
                return
            print(
                f"[WARN] Collection dimension mismatch: existing={current_dim}, "
                f"embedding={dim}. Recreating collection..."
            )
            client.delete_collection(settings.collection_name)

        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=qmodels.VectorParams(
                size=dim,
                distance=qmodels.Distance.COSINE,
            ),
        )

        client.create_payload_index(
            collection_name=settings.collection_name,
            field_name="page_content",
            field_schema=qmodels.TextIndexParams(
                type=qmodels.TextIndexType.TEXT,
                tokenizer=qmodels.TokenizerType.MULTILINGUAL,
            ),
        )
        print(f"[OK] Collection '{settings.collection_name}' ready (dim={dim})")
    except Exception as e:
        raise ConnectionError(
            f"Cannot connect to Qdrant at {settings.qdrant_url}. "
            f"Make sure Qdrant is running:\n"
            f"  docker run -p 6333:6333 qdrant/qdrant\n"
            f"Or set QDRANT_IN_MEMORY=true for in-memory mode (data lost on restart).\n"
            f"Error: {e}"
        )


def get_vector_store(
    embedding_strategy: Optional[EmbeddingStrategy] = None,
) -> QdrantVectorStore:
    strategy = embedding_strategy or get_embedding_strategy()
    client = get_qdrant_client()
    ensure_collection(client, strategy)

    return QdrantVectorStore(
        client=client,
        collection_name=settings.collection_name,
        embedding=strategy.get_embeddings(),
    )


def add_documents(
    documents: List[Document],
    embedding_strategy: Optional[EmbeddingStrategy] = None,
):
    store = get_vector_store(embedding_strategy)
    store.add_documents(documents)


def get_retriever(
    embedding_strategy: Optional[EmbeddingStrategy] = None,
    top_k: Optional[int] = None,
):
    store = get_vector_store(embedding_strategy)
    return store.as_retriever(
        search_kwargs={"k": top_k or settings.retriever_top_k}
    )
