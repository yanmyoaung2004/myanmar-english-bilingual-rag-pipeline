# Myanmar-English Bilingual RAG Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Cohere](https://img.shields.io/badge/powered%20by-Cohere-3952FF.svg)](https://cohere.com)
[![Qdrant](https://img.shields.io/badge/vector%20db-Qdrant-red.svg)](https://qdrant.tech)
[![LangChain](https://img.shields.io/badge/%F0%9F%A7%A1LangChain-informational)](https://python.langchain.com)

A production-ready Retrieval-Augmented Generation (RAG) system designed for **Myanmar (Burmese)** and **English** bilingual document understanding. Built with Cohere embeddings, Qdrant vector storage, and LangChain orchestration.

---

## Features

- **Bilingual by Design** — Detects query language and responds in the same script (Myanmar Unicode or English)
- **Burmese-Aware Chunking** — Respects Myanmar punctuation (။၊) as natural split boundaries
- **Hybrid Search** — Dense semantic vectors + BM25 sparse keyword matching for maximum recall
- **Unicode Sanitization** — Strips zero-width characters that inflate token counts
- **Interactive Query Mode** — Ask questions in either language via CLI
- **Custom LLM Support** — Bring your own OpenAI-compatible endpoint

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │          DOCUMENT INGESTION              │
                    │  PDF/Docs → Unicode Sanitizer → Chunker  │
                    │            (350-token windows)           │
                    └────────────────┬─────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────────┐
                    │       VECTORIZATION & STORAGE            │
                    │  Cohere Embed v4 (1536-dim) → Qdrant     │
                    │         (Dense + BM25 Index)             │
                    └────────────────┬─────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────────┐
                    │          RETRIEVAL RUNTIME               │
                    │  Query → Hybrid Search → Top-5 Contexts  │
                    └────────────────┬─────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────────┐
                    │              GENERATION                  │
                    │  LLM → Cross-Script Guardrail → Output   │
                    │    (matches query script)                │
                    └──────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.13+ (via `uv`)
- Docker (for Qdrant)
- [Cohere API key](https://cohere.com) (free tier available)

### Setup

```bash
# 1. Clone
git clone https://github.com/yanmyoaung2004/myanmar-english-bilingual-rag-pipeline.git
cd myanmar-english-bilingual-rag-pipeline/rag

# 2. Create venv & install
uv venv .venv
.venv\Scripts\activate
uv pip install -r requirements.txt   # or `uv sync`

# 3. Configure
cp .env.example .env
# Edit .env → set COHERE_API_KEY

# 4. Start Qdrant (Docker)
docker run -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_storage:/qdrant/storage qdrant/qdrant

# 5. Add PDFs to data/ and run
uv run python main.py
```

> **Windows users**: Use `.venv\Scripts\activate` and `%PWD%` or absolute paths for Docker volumes.

## How It Works

### 1. Document Ingestion & Sanitization

PDFs loaded from `data/` are passed through a Unicode sanitizer that removes zero-width joiners, normalizes Burmese punctuation (။, ၊), and collapses excessive whitespace — preventing token inflation before embedding.

### 2. Tokenization & Chunking

Uses Cohere's tokenizer to count exact tokens for the `embed-multilingual-v3.0` model. Documents are split into **350-token chunks** with **35-token overlap**, respecting sentence and Burmese punctuation boundaries.

### 3. Embedding & Vector Storage

Each chunk is embedded into a **1536-dimensional vector** via Cohere Embed v4 and stored in **Qdrant** alongside a multilingual BM25 full-text index for hybrid retrieval.

### 4. Retrieval

Queries execute both:

- **Dense search** — semantic similarity over vector embeddings
- **Sparse search** — exact BM25 keyword matching

Results are combined and the top 5 contexts are passed to the LLM.

### 5. Generation

The LLM (default: OpenAI-compatible endpoint, configurable for Cohere Command R+) generates a response in the **same language as the query** — Myanmar Unicode queries produce Myanmar responses, English queries produce English responses.

## Query Examples

```python
# English
result = rag_pipeline.invoke("What are the main findings?")
print(result.content)

# Myanmar
result = rag_pipeline.invoke("အဓိက ရလဒ်များ သည် အဘယ်နည်း။")
print(result.content)
```

The pipeline also includes an **interactive CLI mode** where you can type questions conversationally until you enter `exit`.

## Configuration

| Variable          | Default                          | Description                   |
| ----------------- | -------------------------------- | ----------------------------- |
| `COHERE_API_KEY`  | —                                | Cohere API key for embeddings |
| `QDRANT_URL`      | `http://localhost:6333`          | Qdrant server URL             |
| `COLLECTION_NAME` | `myanmar_english_knowledge_corp` | Qdrant collection name        |
| `LLM_API_BASE`    | `http://localhost:8000`          | Custom LLM endpoint           |
| `LLM_API_KEY`     | `sk-default-key`                 | Custom LLM auth key           |
| `LLM_MODEL`       | `gpt-3.5-turbo`                  | Custom LLM model name         |
| `USE_CUSTOM_LLM`  | `false`                          | Toggle custom LLM             |

### Chunking Parameters (in `main.py`)

| Parameter       | Value                               | Description                        |
| --------------- | ----------------------------------- | ---------------------------------- |
| `chunk_size`    | 350                                 | Max tokens per chunk               |
| `chunk_overlap` | 35                                  | Token overlap between chunks (10%) |
| `separators`    | `["\n\n", "\n", "။", "၊", " ", ""]` | Split priority (Burmese-aware)     |

## Project Layout

```
rag/
├── main.py              # Pipeline entrypoint
├── pyproject.toml       # Project metadata & dependencies
├── AGENTS.md            # Agent/IDE instructions
├── .env.example         # Environment template
├── data/                # PDF documents (create + populate)
├── docs/
│   └── EXECUTION_GUIDE.md   # Detailed walkthrough
├── qdrant_storage/      # Qdrant data (Docker volume)
└── .venv/               # Python virtual environment
```

## Troubleshooting

| Error                         | Likely Cause                  | Fix                                                                        |
| ----------------------------- | ----------------------------- | -------------------------------------------------------------------------- |
| `COHERE_API_KEY not found`    | Missing `.env` or invalid key | Create `.env` from `.env.example` with a valid `co-*` key                  |
| `Could not connect to Qdrant` | Qdrant not running            | `docker run -p 6333:6333 qdrant/qdrant`                                    |
| `No PDF files found in data/` | Empty `data/`                 | Add PDFs to `data/`                                                        |
| `Connection refused`          | LLM endpoint down             | Start your LLM server or set `USE_CUSTOM_LLM=false`                        |
| `ModuleNotFoundError`         | Missing deps                  | `uv pip install langchain langchain-cohere langchain-qdrant qdrant-client` |

## Roadmap

- [ ] **Web UI** — Streamlit or FastAPI frontend for uploads & queries
- [ ] **Zawgyi→Unicode** — Automatic Zawgyi detection and conversion in the ingestion pipeline
- [ ] **Benchmarking** — CER/ROUGE evaluation suite against reference corpora
- [ ] **PDF Batch Ingestion** — Watch folder for automatic processing
- [ ] **Docker Compose** — One-command startup for the full stack

## Tech Stack

- **Embeddings**: [Cohere Embed v4](https://docs.cohere.com/docs/cohere-embed) (multilingual-v3.0, 1536-dim)
- **Vector Store**: [Qdrant](https://qdrant.tech) (dense + BM25 indexing)
- **Orchestration**: [LangChain](https://python.langchain.com)
- **LLM**: OpenAI-compatible endpoints (Cohere Command R+, GPT, Llama, etc.)
- **Documents**: PyPDFLoader via `pypdf`

## License

MIT © [Yan Myo Aung](https://github.com/yanmyoaung2004)
