# Complete RAG Pipeline Execution Guide

## What We've Done So Far

### 1. ✅ Project Setup
- Created virtual environment with Python 3.13
- Installed all dependencies (langchain, qdrant, cohere, etc.)
- Fixed import issues and module compatibility
- Created main.py with full RAG pipeline implementation

### 2. ✅ Infrastructure
- Installed Qdrant client (for vector database)
- Installed Cohere SDK (for embeddings and LLM)
- Installed LangChain ecosystem packages

### 3. ✅ Code Implementation
- **Text Sanitization**: Handles Burmese Unicode cleaning
- **Tokenization**: Cohere-aware token counting
- **Document Chunking**: Recursive splitting with Burmese punctuation awareness
- **Vector Embeddings**: Cohere Embed v4 (1536 dimensions)
- **Vector Storage**: Qdrant with multilingual BM25 indexing
- **Retrieval**: Hybrid search (dense + sparse)
- **Generation**: Bilingual LLM with guardrails

---

## Complete Step-by-Step Execution

### Step 1: Get Cohere API Key (**REQUIRED**)

1. Visit https://cohere.com/
2. Sign up for a free account (no credit card needed for free tier)
3. After login, go to Dashboard → API Keys
4. Copy your API key (looks like: `co-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
5. Edit the `.env` file and paste your key:
   ```
   COHERE_API_KEY=co-your-actual-key-here
   QDRANT_URL=http://localhost:6333
   ```

**⚠️ Important**: Without this step, the pipeline cannot run!

### Step 2: Start Qdrant Database

You have 3 options:

#### Option A: Docker (Recommended for Development)
```powershell
# If Docker Desktop is not running, start it first
# Then run Qdrant in a separate terminal:

docker run -p 6333:6333 -p 6334:6334 `
    -v ${PWD}/qdrant_storage:/qdrant/storage `
    qdrant/qdrant

# You should see: "Qdrant started on 0.0.0.0:6333"
```

#### Option B: Qdrant Cloud (Production)
1. Go to https://qdrant.tech/cloud/
2. Create a cluster
3. Get your API URL and key
4. Update `.env`:
   ```
   QDRANT_URL=https://your-instance.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key_here
   ```

#### Option C: In-Memory (Development Only - No Persistence)
- Skip Docker, run directly
- Data will be lost when pipeline stops

### Step 3: Prepare Your Data

Create a `data/` directory with PDF files:

```
project_root/
├── data/
│   ├── document1.pdf      # Myanmar text
│   ├── document2.pdf      # English text
│   └── document3.pdf      # Bilingual content
├── main.py
├── .env
└── ...
```

To test without real data, create a simple text file:
```
data/
├── sample.txt  # Content: "This is a test document in English."
```

### Step 4: Activate Virtual Environment

```powershell
# Windows
.venv\Scripts\Activate.ps1

# Or using CMD
.venv\Scripts\activate.bat

# You should see "(.venv)" in your terminal
```

### Step 5: Run the Pipeline

```powershell
# Option A: Using uv (recommended)
uv run python main.py

# Option B: After activating venv
python main.py
```

---

## Expected Output

When you run `uv run python main.py`, you should see:

```
============================================================
Myanmar-English Bilingual RAG Pipeline
============================================================

1. Initializing Cohere Embeddings (v4)...
✓ Embeddings engine initialized

2. Initializing Qdrant vector database...
✓ Collection 'myanmar_english_knowledge_corp' already exists

3. Creating vector store...
✓ Vector store created

4. Loading and processing documents...
✓ Created data directory. Please add PDF files here.
⚠ No PDF files found in data/ directory
To use this pipeline, add PDF files to the data/ directory

6. Setting up RAG pipeline...
✓ RAG pipeline created successfully

7. Testing RAG pipeline...

============================================================
✓ RAG Pipeline setup complete!
============================================================
```

---

## Troubleshooting Errors

### ❌ "COHERE_API_KEY not found in environment variables"
**Solution:**
- Make sure `.env` file exists in project root
- Check that the key starts with `co-`
- Verify there are no extra spaces around the key
```
✓ COHERE_API_KEY=co-xxxxx
✗ COHERE_API_KEY = co-xxxxx  (spaces!)
```

### ❌ "Could not connect to Qdrant"
**Solution:**
- Start Docker and run Qdrant container (see Step 2)
- Or verify QDRANT_URL in `.env` is correct
- Check if port 6333 is already in use:
  ```powershell
  netstat -ano | findstr :6333
  ```

### ❌ "No module named 'XXX'"
**Solution:**
- Reinstall dependencies:
  ```powershell
  uv pip install langchain langchain-cohere langchain-qdrant qdrant-client python-dotenv
  ```

### ❌ "No PDF files found in data/"
**Solution:**
- Create `data/` directory if it doesn't exist:
  ```powershell
  mkdir data
  ```
- Add at least one PDF file to `data/`
- Re-run the pipeline

### ❌ "Connection refused" or "connection timed out"
**Solution:**
- Make sure Qdrant is running:
  ```powershell
  docker ps  # Should show qdrant container
  ```
- If not running, start it again:
  ```powershell
  docker run -p 6333:6333 qdrant/qdrant
  ```

---

## File Structure After Setup

```
rag/
├── main.py                      # Main RAG pipeline ✓
├── README.md                    # Project documentation ✓
├── AGENTS.md                    # Agent instructions ✓
├── SETUP.md                     # Setup guide ✓
├── plan.md                      # Architecture blueprint ✓
├── .env                         # Environment variables (created by you)
├── .env.example                 # Template for .env ✓
├── .python-version              # Python version spec ✓
├── pyproject.toml               # Project config ✓
├── data/                        # Your PDF files (create yourself)
│   ├── document1.pdf
│   └── document2.pdf
├── qdrant_storage/              # Vector DB storage (created by Docker)
└── .venv/                       # Virtual environment
    └── Scripts/
        ├── python.exe
        ├── pip.exe
        └── ...
```

---

## Quick Start Commands

```powershell
# 1. Get API key (https://cohere.com/)
# 2. Edit .env with your key
# 3. In one terminal: Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 4. In another terminal: Run the pipeline
uv run python main.py

# 5. To query the pipeline (after it's running):
python -c "
from main import rag_pipeline
result = rag_pipeline.invoke('Your question here')
print(result)
"
```

---

## Next Steps After Initial Run

1. **Add Real Data**: Place actual Myanmar/English PDFs in `data/`
2. **Test Queries**: Modify test queries in `main()` function
3. **Monitor Performance**: Check retrieval quality and generation
4. **Fine-tune Parameters**:
   - `chunk_size=350` - Increase for larger contexts
   - `chunk_overlap=35` - Adjust overlap percentage
   - `search_kwargs={"k": 5}` - Number of documents to retrieve
   - `temperature=0.3` - Lower = more consistent, higher = more creative

---

## Architecture Recap

```
PDFs in data/ 
    ↓
[Unicode Sanitizer] - Removes zero-width chars
    ↓
[Cohere Tokenizer] - Counts exact tokens
    ↓
[Recursive Chunker] - Splits at 350 tokens with 35 overlap
    ↓
[Cohere Embed v4] - Creates 1536-dim vectors
    ↓
[Qdrant Storage] - Stores vectors + BM25 index
    ↓
[Hybrid Retrieval] - Dense + Sparse search
    ↓
[Cohere Command R+] - Generates bilingual response
    ↓
Output (Myanmar or English based on input language)
```

---

## Important Notes

- **Language Detection**: The system matches output language to input language
- **Token Limits**: Max 350 tokens per chunk ensures LLM can process
- **Multilingual**: Qdrant's multilingual tokenizer handles both Myanmar and English
- **No Hallucination**: Prompt includes guardrails to prevent making up answers
- **Burmese Support**: All regex patterns respect Burmese script (။, ၊)

---

## Support & Help

If you encounter issues:
1. Check this file for troubleshooting
2. Review README.md for architecture details
3. Check AGENTS.md for project conventions
4. Verify all 5 steps above are completed

**Get help:**
- Cohere docs: https://docs.cohere.com/
- Qdrant docs: https://qdrant.tech/documentation/
- LangChain docs: https://python.langchain.com/
