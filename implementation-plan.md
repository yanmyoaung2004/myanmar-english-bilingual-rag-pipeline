# Implementation Plan for rag Project

This document serves as an executable blueprint for building the Retrieval‑Augmented Generation (RAG) pipeline. It pulls together the design intent outlined in `dev/plan.md`, the current code layout, and the operational tools (uv, ruff, mypy, pytest) that the team uses.

## 1. Core Roles
| Role | Responsibility | Rough Entry point |
|------|----------------|------------------|
| **Environment** | Manage virtual‑env (`.venv`), dependency lock (`uv.lock`), and global pyproject configuration | `uv sync` / `uv run` |
| **Parser / Tokeniser** | Break queries into tokens that feed into the embedding engine | `rag/text.py` (stub) |
| **Vectoriser** | Convert documents or query fragments into embeddings | `rag/vector.py` |
| **Store** | Persist embeddings and metadata. Uses SQLite by default; can swap to Postgres or a vector‑DB in the future | Implemented in `rag/store.py` |
| **Retriever** | Perform similarity search over stored vectors | `rag/retriever.py` |
| **LLM Wrapper** | Interface with external LLM back‑ends (Gemini, Together, etc.) | `rag/llm.py` |
| **Orchestrator** | Glue all the pieces together: receive request → tokenise → vectorise → retrieve → prompt LLM → aggregate → response | `rag/main.py` – `main()` |
| **CLI / API** | Expose a simple command‑line interface and a placeholder HTTP API for future extension | `rag/cli.py` (to be added) |

## 2. Flow Diagram (textual)
```
[Client] → [CLI/HTTP] → [Orchestrator] →
   ├─[Tokenizer] → [Vectoriser] → [Store] →
   └─[Retriever] → [LLM] → [Response Builder]
```

## 3. Development Workflow
1. **Setup** – `uv sync` creates the virtual‑env and installs dependencies.
2. **Lint** – `uv run ruff check .`
3. **Type‑check** – `uv run mypy .`
4. **Test** – `uv run pytest -q`
5. **Run** – `uv run python -m rag.main` or `uv run python main.py`

### Branching Convention
- Feature branches off `dev`. Merge back into `dev` with a PR. Each PR must pass all lint, type, and tests locally before review.
- Release candidates are branched from `dev` named `release/vX.Y`.

## 4. Testing Strategy
- Unit tests: placed under `tests/` and cover individual functions.
- Integration tests: reside in `tests/integration/`; require LLM API keys set as environment variables (`OPENAI_API_KEY`, `TOGETHERAI_API_KEY`, etc.).
- Skipping expensive tests: use `pytest -k <tag>` e.g. `-k slow`.

## 5. Deployment & CI (to be added)
- CI should mirror the local dev sequence:
  1. `uv sync`
  2. `ruff check .`
  3. `mypy .`
  4. `pytest`
- Packaging: `uv build` for source distribution; `uv publish` when ready.
- Docker container: Dockerfile will use `python:3.13-slim` and copy the repo, run `uv sync --no-dev`, then expose a simple API.

## 6. Extensibility Points
- **Vector Store Swap** – Implement `rag/store.py` as a protocol; new back‑ends can be injected.
- **LLM Adapter Layer** – `rag/llm.py` defines a simple interface; new providers only need to implement `generate()`.
- **Retrieval Enhancements** – current naive similarity search can be upgraded to k‑NN libraries (FAISS, Milvus) without altering orchestrator.

## 7. Documentation & Resources
- `dev/plan.md` – detailed architectural narrative.
- `README.md` – quick start.
- `pyproject.toml` – dependency definitions.
- `tests/` – concrete examples of how to call the system with various back‑ends.

---
**Note**: This plan is iterative. As new requirements emerge (e.g., scaling, multi‑tenant support, monitoring), sections will be expanded. Keep the `implementation-plan.md` in sync with the evolving codebase.
