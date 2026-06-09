import json
import os
from datetime import datetime
from typing import List, Dict

import requests
from qdrant_client import QdrantClient

from core.config import settings


def get_qdrant_client() -> QdrantClient:
    kwargs = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantClient(**kwargs)


def export_corpus(version: str = "v0.1.0") -> Dict:
    client = get_qdrant_client()
    release_dir = os.path.join(settings.corpus_releases_dir, version)
    os.makedirs(release_dir, exist_ok=True)

    corpus_path = os.path.join(release_dir, "corpus.jsonl")
    card_path = os.path.join(release_dir, "dataset_card.md")

    scroll = client.scroll(
        collection_name=settings.collection_name,
        limit=10000,
        with_payload=True,
        with_vectors=False,
    )

    points = scroll[0]
    total_chars = 0
    domain_counts = {}

    with open(corpus_path, "w", encoding="utf-8") as f:
        for point in points:
            payload = point.payload or {}
            text = payload.get("page_content", "")
            if not text:
                text = payload.get("text", "")
            if not text:
                continue

            record = {
                "id": str(point.id),
                "text": text,
                "metadata": {
                    "source": payload.get("source", "unknown"),
                    "domain": payload.get("domain", "unknown"),
                    "doc_id": payload.get("doc_id", ""),
                    "corpus_version": version,
                },
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

            total_chars += len(text)
            domain = payload.get("domain", "unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

    with open(card_path, "w", encoding="utf-8") as f:
        f.write(
            f"""# Myanmar NLP Corpus — {version}

## Overview
- **Version**: {version}
- **Release date**: {datetime.now().strftime('%Y-%m-%d')}
- **Total records**: {len(points)}
- **Total characters**: {total_chars:,}
- **Language**: Myanmar (my) / English (en)

## Domain Distribution
"""
        )
        for domain, count in sorted(domain_counts.items()):
            f.write(f"- {domain}: {count} records\n")
        f.write(
            f"""
## Files
- `corpus.jsonl` — main corpus, one JSON record per chunk
- `dataset_card.md` — this file
"""
        )

    print(f"\nCorpus exported to {release_dir}")
    print(f"  Records: {len(points)}")
    print(f"  Characters: {total_chars:,}")
    print(f"  Domains: {domain_counts}")

    return {
        "pages": len(points),
        "characters": total_chars,
        "path": release_dir,
    }
