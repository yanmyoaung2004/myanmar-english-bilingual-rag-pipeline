"""
Myanmar-English Bilingual RAG Pipeline
======================================
Entry point for CLI mode. Also runnable as: python -m main
"""

import os
import time
import sys
from typing import Optional

from core.config import settings
from core.sanitizer import sanitize_documents
from core.chunker import get_chunker
from core.embeddings import get_embedding_strategy
from core.retriever import add_documents, ensure_collection
from rag.pipeline import build_rag_pipeline


def load_pdf_documents(data_dir: str):
    from langchain_community.document_loaders import PyPDFLoader

    pdf_files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"[WARN] No PDF files found in {data_dir}/")
        return []

    all_docs = []
    for pdf_file in pdf_files:
        file_path = os.path.join(data_dir, pdf_file)
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        all_docs.extend(docs)
        print(f"[OK] Loaded {len(docs)} pages from {pdf_file}")

    return all_docs


def index_documents(docs, strategy, chunker):
    if not docs:
        print("[WARN] No documents to index")
        return

    print(f"  Chunking {len(docs)} documents...")
    chunks = chunker.split_documents(docs)
    print(f"  Created {len(chunks)} chunks")

    print("  Adding to vector store...")
    add_documents(chunks, strategy)
    print(f"[OK] {len(chunks)} chunks indexed")


def interactive_query_loop(pipeline):
    print("\n" + "=" * 60)
    print("INTERACTIVE RAG QUERY MODE")
    print("=" * 60)
    print("Supports Myanmar (Burmese) and English queries.")
    print("Type 'exit' or 'quit' to stop.\n")

    query_count = 0
    while True:
        try:
            user_query = input("\n> Your Question: ").strip()
            if user_query.lower() in ["exit", "quit", "bye"]:
                print("\nGoodbye!")
                break
            if not user_query:
                continue

            query_count += 1
            print(f"[Query #{query_count}] Processing...")

            result = pipeline.invoke(user_query)
            content = ""
            if hasattr(result, "content"):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", str(result))
            else:
                content = str(result)

            print(f"\nAnswer:\n{content}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"[ERR] {e}")


def main():
    print("\n" + "=" * 60)
    print("Myanmar-English Bilingual RAG Pipeline")
    print(f"  Embedding mode: {settings.embedding_mode}")
    print("=" * 60 + "\n")

    settings.validate()
    ensure_collection()

    strategy = get_embedding_strategy()
    chunker = get_chunker(settings.embedding_mode)

    os.makedirs(settings.data_dir, exist_ok=True)

    indexing_mode = os.getenv("INDEX_ON_START", "false").lower() == "true"
    if indexing_mode:
        print("Indexing PDF documents...")
        docs = load_pdf_documents(settings.data_dir)
        index_documents(docs, strategy, chunker)

    print("\nBuilding RAG pipeline...")
    pipeline = build_rag_pipeline(strategy)

    print("\nPipeline ready!")
    interactive_query_loop(pipeline)


if __name__ == "__main__":
    main()
