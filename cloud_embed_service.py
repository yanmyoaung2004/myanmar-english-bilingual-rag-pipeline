"""
Cloud Embedding Service
=======================
Standalone FastAPI service that computes embeddings on a GPU cloud VM.
Supports ANY embedding model — Sentence Transformers, Cohere, OpenAI.

Usage:
    # Start on your GPU VM:
    python cloud_embed_service.py --port 8001

    # Use any model:
    curl -X POST http://localhost:8001/embed \
      -H "Content-Type: application/json" \
      -d '{"texts": ["မြန်မာ"], "model": "sentence-transformers/LaBSE"}'

    curl -X POST http://localhost:8001/embed \
      -H "Content-Type: application/json" \
      -d '{"texts": ["မြန်မာ"], "model": "cohere/embed-multilingual-v3.0",
           "api_key": "co-xxxxx"}'

    curl -X POST http://localhost:8001/embed \
      -H "Content-Type: application/json" \
      -d '{"texts": ["မြန်မာ"], "model": "openai/text-embedding-3-small",
           "api_key": "sk-xxxxx"}'
"""

import argparse
import os
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Cloud Embedding Service")

_sentence_models: dict = {}


class EmbedRequest(BaseModel):
    texts: List[str]
    model: str = "sentence-transformers/LaBSE"
    api_key: Optional[str] = None


class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dimension: int
    time_seconds: float
    backend: str


def _load_sentence_model(model_name: str):
    if model_name not in _sentence_models:
        from sentence_transformers import SentenceTransformer
        print(f"[SentenceTransformer] Loading: {model_name}...")
        _sentence_models[model_name] = SentenceTransformer(model_name)
        dim = _sentence_models[model_name].get_sentence_embedding_dimension()
        print(f"  Model loaded. Dimension: {dim}")
    return _sentence_models[model_name]


def _embed_sentence(texts: List[str], model_name: str) -> List[List[float]]:
    model = _load_sentence_model(model_name)
    return model.encode(texts, show_progress_bar=False).tolist()


def _embed_cohere(texts: List[str], model_name: str, api_key: str) -> List[List[float]]:
    import cohere
    api_key = api_key or os.getenv("COHERE_API_KEY", "")
    if not api_key:
        raise HTTPException(400, "Cohere requires api_key or COHERE_API_KEY env var")
    model = model_name.removeprefix("cohere/")
    client = cohere.ClientV2(api_key=api_key)
    resp = client.embed(texts=texts, model=model, input_type="search_document")
    return [list(r) for r in resp.embeddings]


def _embed_openai(texts: List[str], model_name: str, api_key: str) -> List[List[float]]:
    from openai import OpenAI
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(400, "OpenAI requires api_key or OPENAI_API_KEY env var")
    model = model_name.removeprefix("openai/")
    client = OpenAI(api_key=api_key)
    resp = client.embeddings.create(input=texts, model=model)
    return [r.embedding for r in resp.data]


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest):
    if not req.texts:
        raise HTTPException(400, "texts must be non-empty")

    t0 = time.time()
    model_lower = req.model.lower()

    try:
        if model_lower.startswith("cohere/") or model_lower.startswith("cohere_"):
            embeddings = _embed_cohere(req.texts, req.model, req.api_key or "")
            backend = "cohere"
        elif model_lower.startswith("openai/") or model_lower.startswith("openai_"):
            embeddings = _embed_openai(req.texts, req.model, req.api_key or "")
            backend = "openai"
        else:
            embeddings = _embed_sentence(req.texts, req.model)
            backend = "sentence_transformers"
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Model '{req.model}' failed: {e}")

    elapsed = time.time() - t0

    return EmbedResponse(
        embeddings=embeddings,
        model=req.model,
        dimension=len(embeddings[0]) if embeddings else 0,
        time_seconds=round(elapsed, 3),
        backend=backend,
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "sentence_models_loaded": list(_sentence_models.keys()),
        "supported_backends": ["sentence_transformers", "cohere", "openai"],
    }


@app.get("/models")
async def list_models():
    return {"sentence_models_loaded": list(_sentence_models.keys())}


def main():
    parser = argparse.ArgumentParser(description="Cloud Embedding Service")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--model", default=None,
                        help="Preload a SentenceTransformer model on startup (e.g. sentence-transformers/LaBSE)")
    args = parser.parse_args()

    if args.model:
        _load_sentence_model(args.model)

    print(f"\n{'='*60}")
    print(f"  Cloud Embedding Service")
    print(f"  Listening on {args.host}:{args.port}")
    print(f"{'='*60}")
    print(f"  Supported backends:")
    print(f"    sentence-transformers/...  → local GPU")
    print(f"    cohere/...                 → Cohere API")
    print(f"    openai/...                 → OpenAI API")
    if args.model:
        print(f"  Preloaded: {args.model}")
    print(f"\n  POST /embed  — compute embeddings")
    print(f"  GET  /health — health check")
    print(f"  GET  /models — list loaded models")
    print(f"{'='*60}\n")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
