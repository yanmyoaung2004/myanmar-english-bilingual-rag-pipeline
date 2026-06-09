# Cloud Embedding Setup Guide

## Overview

Two embedding modes:

| Mode | Where embeddings run | Models |
|------|---------------------|--------|
| **local** (default) | Your laptop via Cohere API | Cohere only |
| **cloud** | GPU VM (or API passthrough) | **Any model** — SentenceTransformers, Cohere, OpenAI, etc. |

Switch via `EMBEDDING_MODE=cloud` in `.env`.

> **You can use ANY model in cloud mode.** The cloud embedding service is a
> generic embedding proxy — it supports three backends:
> - `sentence-transformers/...` — HuggingFace models loaded on the cloud GPU
> - `cohere/...` — Cohere API called from the cloud VM
> - `openai/...` — OpenAI API called from the cloud VM

---

## Architecture

```
Your Laptop                           Cloud VM (GPU or API proxy)
┌─────────────────────┐               ┌──────────────────────────────────┐
│  main.py            │               │  cloud_embed_service.py          │
│  api/main.py        │ ── POST ──►   │                                  │
│  scripts/ingest.py  │   /embed      │  ┌─ SentenceTransformer (GPU) ─┐ │
│                     │ ◄───────     │  ├─ Cohere API ────────────────┤ │
│  Qdrant (vector DB) │               │  └─ OpenAI API ────────────────┘ │
└─────────────────────┘               └──────────────────────────────────┘
```

---

## Quick Start (5 minutes)

### 1. Set up `.env`

```env
# Switch to cloud mode
EMBEDDING_MODE=cloud

# Point to your cloud service
CLOUD_EMBED_URL=http://<YOUR_VM_IP>:8001
CLOUD_EMBED_API_KEY=your-secret-key

# Embedding model on the cloud VM
CLOUD_EMBED_MODEL=sentence-transformers/LaBSE

# Embedding dimension must match the model output
EMBED_DIMENSION=768
```

### 2. Deploy the cloud service

On your GPU cloud VM (e.g., GCP, AWS, Lambda Labs, RunPod):

```bash
# Install
pip install fastapi uvicorn sentence-transformers torch requests

# Start the service
python cloud_embed_service.py --port 8001 --model sentence-transformers/LaBSE
```

Your service will listen on `0.0.0.0:8001`.

### 3. Test it

```bash
curl -X POST http://<YOUR_VM_IP>:8001/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["မြန်မာနိုင်ငံ", "hello world"], "model": "sentence-transformers/LaBSE"}'
```

### 4. Use from your laptop

```bash
# Ingest using cloud embeddings (SentenceTransformer model on cloud GPU)
uv run python -m scripts.ingest data/myanmar_text.pdf --mode cloud

# Use Cohere API through the cloud service
uv run python -m scripts.ingest data/doc.pdf --mode cloud --model "cohere/embed-multilingual-v3.0"

# Use OpenAI through the cloud service
uv run python -m scripts.ingest data/doc.pdf --mode cloud --model "openai/text-embedding-3-small"

# Or set mode + model permanently in .env
# EMBEDDING_MODE=cloud
# CLOUD_EMBED_MODEL=cohere/embed-multilingual-v3.0
```

### Troubleshooting: Qdrant not running?

If you see `Connection refused` on Qdrant (port 6333), you have two options:

**Option A: Start Qdrant via Docker**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Option B: Use in-memory mode** (data lost on restart)
```env
QDRANT_IN_MEMORY=true
```

| Provider | GPU | Cost (approx) | Best for |
|----------|-----|--------------|----------|
| **Lambda Labs** | A10G / A100 | $0.50–$1.50/hr | Simple, fast setup |
| **RunPod** | RTX 3090 / A40 | $0.30–$0.80/hr | Cheapest |
| **GCP (Vertex AI)** | T4 / L4 | $0.50–$1.00/hr | Enterprise |
| **AWS SageMaker** | T4 / A10G | $1.00–$2.00/hr | Managed endpoint |
| **Hugging Face (Inference Endpoints)** | T4 / A10G | $0.60–$1.50/hr | Easiest deployment |

---

## Python Code (standalone client)

```python
"""
cloud_embed_client.py — Use this in your own scripts
"""

import requests
from typing import List


class CloudEmbeddingClient:
    def __init__(self, api_url: str, api_key: str = "", model: str = "sentence-transformers/LaBSE"):
        self.api_url = api_url.rstrip("/") + "/embed"
        self.api_key = api_key
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"texts": texts, "model": self.model}
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()["embeddings"]


# Usage
client = CloudEmbeddingClient(
    api_url="http://<YOUR_VM_IP>:8001",
    api_key="your-secret-key",
    model="sentence-transformers/LaBSE",
)

texts = ["မြန်မာနိုင်ငံသည် အရှေ့တောင်အာရှတွင် တည်ရှိသည်။", "Myanmar is in Southeast Asia."]
embeddings = client.embed(texts)
print(f"Got {len(embeddings)} embeddings, dim={len(embeddings[0])}")
```

---

## Jupyter Notebook

Create `cloud_embed_demo.ipynb`:

```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# Cloud Embedding Demo\n\nCompute embeddings on a GPU cloud VM and use them locally."]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "import numpy as np\n",
    "from typing import List\n",
    "\n",
    "# ── Config ──────────────────────────────────────────\n",
    "CLOUD_EMBED_URL = \"http://<YOUR_VM_IP>:8001\"\n",
    "CLOUD_EMBED_MODEL = \"sentence-transformers/LaBSE\"\n",
    "# ────────────────────────────────────────────────────\n",
    "\n",
    "class CloudEmbeddingClient:\n",
    "    def __init__(self, api_url: str, model: str = \"sentence-transformers/LaBSE\"):\n",
    "        self.api_url = api_url.rstrip(\"/\") + \"/embed\"\n",
    "        self.model = model\n",
    "\n",
    "    def embed(self, texts: List[str]) -> List[List[float]]:\n",
    "        resp = requests.post(\n",
    "            self.api_url,\n",
    "            json={\"texts\": texts, \"model\": self.model},\n",
    "            timeout=120,\n",
    "        )\n",
    "        resp.raise_for_status()\n",
    "        return resp.json()[\"embeddings\"]\n",
    "\n",
    "client = CloudEmbeddingClient(CLOUD_EMBED_URL, CLOUD_EMBED_MODEL)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Test with Myanmar text\n",
    "texts = [\n",
    "    \"မြန်မာနိုင်ငံသည် အရှေ့တောင်အာရှတွင် တည်ရှိသည်။\",\n",
    "    \"နေပြည်တော်သည် မြန်မာနိုင်ငံ၏ မြို့တော်ဖြစ်သည်။\",\n",
    "    \"Myanmar is a country in Southeast Asia.\",\n",
    "    \"Bagan is known for its ancient temples and pagodas.\",\n",
    "]\n",
    "\n",
    "embeddings = client.embed(texts)\n",
    "emb_array = np.array(embeddings)\n",
    "\n",
    "print(f\"Embeddings shape: {emb_array.shape}\")\n",
    "print(f\"Dimension: {emb_array.shape[1]}\")\n",
    "\n",
    "# Cosine similarity\n",
    "sim_matrix = np.dot(emb_array, emb_array.T) / (\n",
    "    np.linalg.norm(emb_array, axis=1, keepdims=True) *\n",
    "    np.linalg.norm(emb_array, axis=1, keepdims=True).T\n",
    ")\n",
    "\n",
    "print(\"\\nSimilarity matrix:\")\n",
    "for i, t1 in enumerate(texts):\n",
    "    for j, t2 in enumerate(texts):\n",
    "        print(f\"  [{i},{j}] {sim_matrix[i][j]:.3f}  {t1[:30]}... vs {t2[:30]}...\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Batch benchmark\n",
    "import time\n",
    "\n",
    "batch_sizes = [1, 10, 50, 100, 200]\n",
    "for n in batch_sizes:\n",
    "    batch = [\"မြန်မာ\"] * n\n",
    "    t0 = time.time()\n",
    "    client.embed(batch)\n",
    "    elapsed = time.time() - t0\n",
    "    print(f\"Batch size {n:4d}: {elapsed:.3f}s ({n/elapsed:.0f} texts/sec)\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["---\n\n## Integration with RAG pipeline\n\nSet `EMBEDDING_MODE=cloud` in `.env` and the pipeline will call this service automatically."]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.13.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
```

---

## Model Recommendations

> **You can use ANY model.** The cloud service supports three backends.
> Prefix determines the backend automatically.

### Sentence Transformers (HuggingFace, runs on cloud GPU)

| Model | Dimension | Quality | Speed | Size |
|-------|-----------|---------|-------|------|
| `sentence-transformers/LaBSE` | 768 | ★★★★☆ | ★★★☆☆ | 1.8 GB |
| `intfloat/multilingual-e5-small` | 384 | ★★★★☆ | ★★★★★ | 470 MB |
| `intfloat/multilingual-e5-base` | 768 | ★★★★★ | ★★★★☆ | 1.1 GB |
| `intfloat/multilingual-e5-large` | 1024 | ★★★★★★ | ★★★☆☆ | 2.2 GB |
| `BAAI/bge-m3` | 1024 | ★★★★★ | ★★★☆☆ | 3.0 GB |

### Cohere (via API, called from the cloud VM)

| Model | Dimension | Quality |
|-------|-----------|---------|
| `cohere/embed-multilingual-v3.0` | 1024 | ★★★★★ |
| `cohere/embed-english-v3.0` | 1024 | ★★★★★ |

### OpenAI (via API, called from the cloud VM)

| Model | Dimension | Quality |
|-------|-----------|---------|
| `openai/text-embedding-3-small` | 512 | ★★★★☆ |
| `openai/text-embedding-3-large` | 3072 | ★★★★★★ |
| `openai/text-embedding-ada-002` | 1536 | ★★★★☆ |

> **Important:** When using `cohere/` or `openai/` models, the cloud service
> calls those APIs using the `api_key` you provide. This is useful when your
> laptop has restricted network access but the cloud VM does not.

For Myanmar text specifically, **LaBSE** or **multilingual-e5-base** give the best balance of quality and speed on GPU. Use **cohere/embed-multilingual-v3.0** for highest quality without a GPU.

---

## Production Deployment

### Option A: systemd service (Linux VM)

```ini
# /etc/systemd/system/cloud-embed.service
[Unit]
Description=Cloud Embedding Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rag
ExecStart=/home/ubuntu/rag/.venv/bin/python cloud_embed_service.py --port 8001 --model sentence-transformers/LaBSE
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cloud-embed
sudo systemctl start cloud-embed
sudo systemctl status cloud-embed
```

### Option B: Docker

```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

RUN pip install fastapi uvicorn sentence-transformers

COPY cloud_embed_service.py /app/
WORKDIR /app

EXPOSE 8001

CMD ["python", "cloud_embed_service.py", "--port", "8001", "--model", "sentence-transformers/LaBSE"]
```

### Option C: Hugging Face Inference Endpoints

1. Go to https://ui.endpoints.huggingface.co/
2. Create new endpoint → model: `sentence-transformers/LaBSE`
3. Select GPU (T4 mini is sufficient)
4. Deploy → get the endpoint URL
5. Use it in `CLOUD_EMBED_URL` with a thin wrapper

---

## Performance Expectations

| Batch size | LaBSE (T4 GPU) | LaBSE (CPU) | Speedup |
|-----------|---------------|-------------|---------|
| 1 | 0.05s | 0.50s | 10× |
| 50 | 0.15s | 8.00s | 53× |
| 200 | 0.40s | 32.00s | 80× |
| 1000 | 1.80s | 180.00s | 100× |

---

## Security

- Deploy the cloud embedding service **inside your VPC** or use a VPN
- Use `CLOUD_EMBED_API_KEY` as a shared secret (passed via `Authorization: Bearer` header)
- The service only accepts `POST /embed` — no data persistence
- No logs of embedded text content are kept
