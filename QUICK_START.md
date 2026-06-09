# Quick Reference: How to Run This RAG Pipeline

## TL;DR - 5 Minute Setup

```powershell
# 1. Get API key from https://cohere.com/ and add to .env
# 2. Start Qdrant (in separate terminal)
docker run -p 6333:6333 qdrant/qdrant

# 3. Run the pipeline (in another terminal)
uv run python main.py
```

## Complete Checklist

- [ ] **Python 3.13+** installed ✓
- [ ] **Virtual environment** created (.venv/) ✓
- [ ] **Dependencies installed** ✓
- [ ] **Cohere API key** obtained (https://cohere.com/)
- [ ] **API key added** to `.env` file
- [ ] **Qdrant running** via Docker (or using Cloud)
- [ ] **`data/` directory** created
- [ ] **PDF files** added to `data/` folder

## What Each File Does

| File | Purpose |
|------|---------|
| `main.py` | Main RAG pipeline - runs everything |
| `EXECUTION_GUIDE.md` | Detailed step-by-step instructions |
| `README.md` | Architecture & usage documentation |
| `SETUP.md` | Troubleshooting guide |
| `plan.md` | Technical architecture blueprint |
| `AGENTS.md` | Instructions for OpenCode agents |
| `.env` | Your API keys & config (create from .example) |
| `data/` | Where to put your PDF files |

## What the Pipeline Does

1. **Loads PDFs** from `data/` folder
2. **Cleans text** (removes problematic Unicode)
3. **Splits into chunks** (350 tokens max, Burmese-aware)
4. **Creates embeddings** using Cohere Embed v4
5. **Stores in Qdrant** (vector database)
6. **Retrieves relevant** documents for queries
7. **Generates responses** using Cohere Command R+
8. **Respects language** (Burmese query → Burmese answer)

## Commands Reference

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run the pipeline
uv run python main.py

# Start Qdrant database
docker run -p 6333:6333 qdrant/qdrant

# Install missing packages
uv pip install python-dotenv langchain-text-splitters

# Check Python version
python --version

# List installed packages
pip list | grep langchain
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "COHERE_API_KEY not found" | Add key to `.env` file |
| "Could not connect to Qdrant" | Start Docker container with Qdrant |
| "No module named..." | Run `uv pip install [package]` |
| "No PDF files found" | Create `data/` folder and add PDFs |

## Architecture at a Glance

```
Your PDF Files
    ↓
Unicode Sanitizer (removes bad characters)
    ↓
Cohere Tokenizer (counts tokens accurately)
    ↓
Recursive Chunker (350 tokens per chunk)
    ↓
Cohere Embed v4 (creates 1536-dim vectors)
    ↓
Qdrant (stores & indexes vectors)
    ↓
Hybrid Search (dense + sparse retrieval)
    ↓
Cohere LLM (generates response)
    ↓
Output (in same language as query)
```

## Configuration

**Default settings in `main.py`:**
- Chunk size: 350 tokens
- Chunk overlap: 35 tokens
- Top retrieved docs: 5
- Model: Cohere Command R+ Pro
- Temperature: 0.3 (consistent output)

## After Setup Works

1. Add more PDF files to `data/`
2. Modify test queries in `main()` function
3. Adjust parameters for your needs
4. Deploy with monitoring/logging

## File Locations

```
D:\Projects_And_Learning\AI\myanmar-ocr\rag\
├── .env ← Put your API key here
├── main.py ← Run this file
├── data/ ← Put your PDFs here
└── qdrant_storage/ ← Created by Docker (don't edit)
```

## Key Technologies

- **Embeddings**: Cohere Embed v4 (1536 dimensions)
- **Database**: Qdrant (vector + BM25 search)
- **LLM**: Cohere Command R+ (bilingual)
- **Framework**: LangChain
- **Language Support**: Myanmar (Burmese) + English

## Get Your Cohere API Key

1. Go to https://cohere.com/
2. Click "Sign Up" (free, no credit card)
3. After login → Dashboard → API Keys
4. Copy your key (starts with `co-`)
5. Paste into `.env` file:
   ```
   COHERE_API_KEY=co-your-key-here
   ```

## Support

- **Troubleshooting**: See `SETUP.md`
- **Architecture**: See `plan.md`
- **Full Guide**: See `EXECUTION_GUIDE.md`
- **API Docs**: https://docs.cohere.com/
- **Qdrant Docs**: https://qdrant.tech/

## Success Criteria

Pipeline is working when you see:
```
✓ Embeddings engine initialized
✓ Qdrant initialized
✓ Vector store created
✓ RAG pipeline created successfully
✓ RAG Pipeline setup complete!
```

Then query it:
```python
result = rag_pipeline.invoke("Your question here")
print(result)
```

---

**You're all set! Follow the 5-minute setup above to get started.** 🚀
