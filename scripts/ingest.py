"""
CLI tool for ingesting documents into the RAG pipeline.

Usage:
    uv run python -m scripts.ingest path/to/document.pdf
    uv run python -m scripts.ingest path/to/document.pdf --mode cloud
    uv run python -m scripts.ingest data/doc.pdf --mode cloud --model "cohere/embed-multilingual-v3.0"
    uv run python -m scripts.ingest data/*.pdf
"""

import argparse
from pathlib import Path

from core.config import settings
from core.sanitizer import sanitize_documents
from core.chunker import get_chunker
from core.embeddings import get_embedding_strategy
from core.retriever import add_documents, ensure_collection


def ingest_file(path: str, mode: str = "local", model: str = None):
    path = str(Path(path).resolve())
    ext = Path(path).suffix.lower()

    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(path)
        raw_docs = loader.load()
    elif ext == ".txt":
        from langchain_core.documents import Document
        text = Path(path).read_text(encoding="utf-8")
        raw_docs = [Document(page_content=text, metadata={"source": Path(path).name})]
    else:
        print(f"[SKIP] Unsupported file type: {ext}")
        return 0

    docs = sanitize_documents(raw_docs)
    strategy = get_embedding_strategy(mode, model=model)
    chunker = get_chunker(mode)
    chunks = chunker.split_documents(docs)

    add_documents(chunks, strategy)
    model_label = model or settings.cloud_embed_model if mode == "cloud" else "cohere"
    print(f"[OK] {Path(path).name}: {len(chunks)} chunks indexed ({mode}, {model_label})")
    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG pipeline")
    parser.add_argument("files", nargs="+", help="PDF or TXT files to ingest")
    parser.add_argument("--mode", choices=["local", "cloud"], default="local",
                        help="Embedding mode (default: local)")
    parser.add_argument("--model", default=None,
                        help="Embedding model (cloud mode only). "
                             "Examples: sentence-transformors/LaBSE, cohere/embed-multilingual-v3.0, "
                             "openai/text-embedding-3-small")
    args = parser.parse_args()

    settings.validate()
    ensure_collection()

    total = 0
    for f in args.files:
        if Path(f).is_file():
            total += ingest_file(f, args.mode, args.model)
        else:
            print(f"[WARN] Not a file: {f}")

    print(f"\nDone. {total} total chunks indexed.")


if __name__ == "__main__":
    main()
