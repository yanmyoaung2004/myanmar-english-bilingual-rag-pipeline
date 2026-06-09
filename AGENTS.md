## Project structure
Monorepo `myanmar-ocr/` with three sibling directories:
| Path | Purpose |
|-------|----------------------------------|
| `rag/`| Retrieval-Augmented Generation |
| `test/`| OCR benchmarking |
| `dev/` | Plan / reference implementation |

## Environment
- Python 3.13 via `uv` (v0.8.15). Virtual env is `.venv/`.
- Run: `uv run python main.py` (or activate `.venv\Scripts\activate` on Windows).
- No dependencies declared yet. Add to `[project] dependencies` in `pyproject.toml`.

## Entrypoint
`main.py` exports `main()`. Invoked via `if __name__ == "__main__"` guard.

## Current status
Scaffold only. No linting, typechecking, tests, or CI configured yet. README is empty.

## Conventions
- `dev/plan.md` is the source of truth for the intended design — consult it before implementing.
- The `test/` sibling has working OCR scripts against multiple backends (Google Gemini, OpenRouter, Together AI, NVIDIA, Lightning AI). Reference those when adding OCR support to `rag/`.