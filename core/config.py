import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    collection_name: str = os.getenv("COLLECTION_NAME", "myanmar_english_knowledge_corp")

    llm_api_base: str = os.getenv("LLM_API_BASE", "http://localhost:8000")
    llm_api_key: str = os.getenv("LLM_API_KEY", "sk-default-key")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    use_custom_llm: bool = os.getenv("USE_CUSTOM_LLM", "false").lower() == "true"

    embedding_mode: str = os.getenv("EMBEDDING_MODE", "local")
    cloud_embed_url: str = os.getenv("CLOUD_EMBED_URL", "")
    cloud_embed_api_key: str = os.getenv("CLOUD_EMBED_API_KEY", "")
    cloud_embed_model: str = os.getenv("CLOUD_EMBED_MODEL", "sentence-transformers/LaBSE")

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "350"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "35"))
    retriever_top_k: int = int(os.getenv("RETRIEVER_TOP_K", "5"))

    data_dir: str = os.getenv("DATA_DIR", "data")
    corpus_releases_dir: str = os.getenv("CORPUS_RELEASES_DIR", "corpus/releases")
    embed_dimension: int = int(os.getenv("EMBED_DIMENSION", "1024"))

    def validate(self):
        if not self.cohere_api_key and self.embedding_mode == "local":
            raise ValueError(
                "COHERE_API_KEY is required when EMBEDDING_MODE=local. "
                "Set it in .env or switch to EMBEDDING_MODE=cloud."
            )


settings = Settings()
