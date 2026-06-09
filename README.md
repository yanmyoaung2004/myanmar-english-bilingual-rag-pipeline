# Myanmar-English Bilingual RAG Pipeline

A Retrieval-Augmented Generation (RAG) system that processes Myanmar (Burmese) and English text using advanced NLP techniques.

## Architecture Overview

```
[DOCUMENT INGESTION]
  PDFs / Docs / Text → Regex Unicode Sanitizer → Token-Aware Recursive Chunker (Max 350 Cohere Tokens)
                                                              │
                                                              ▼
[VECTORIZATION & STORAGE]
  LangChain Vector Store → Cohere Embed v4 (1536-dim) → Qdrant (Dense + BM25)
                                                              │
                                                              ▼
[RETRIEVAL RUNTIME]
  User Query → Multi-Script Encoding Validation → Parallel Retrieval (Dense + Sparse BM25)
                                                              │
                                                              ▼
[CONTEXT COMPRESSION]
  Reciprocal Rank Fusion (RRF) → Cohere Rerank v4 → Top 5 Validated Context Windows
                                                              │
                                                              ▼
[GENERATION]
  Command R+ LLM → Cross-Script Guardrail Prompt → Output (Matching Query Script)
```

## Prerequisites

- **Python 3.13+** (via uv)
- **Docker** (optional, for Qdrant)
- **Cohere API Key** (free tier available at https://cohere.com)

## Installation

### 1. Clone and Setup

```bash
cd D:\Projects_And_Learning\AI\myanmar-ocr\rag
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv .venv

# Activate on Windows
.venv\Scripts\activate

# Or manually with Python
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

All dependencies are already installed from the previous setup:
- langchain, langchain-cohere, langchain-qdrant
- qdrant-client, pypdf, cohere, tokenizers

Additional dependencies for this version:

```bash
pip install python-dotenv langchain-text-splitters
```

Or using uv:

```bash
uv pip install python-dotenv langchain-text-splitters
```

### 4. Setup Qdrant Database

**Option A: Using Docker (Recommended)**

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

**Option B: Using Python Client (In-Memory)**

The code automatically connects to Qdrant. If Qdrant is not running, the pipeline will fail. You can either:
- Start Qdrant with Docker (Option A)
- Use Qdrant Cloud (https://qdrant.tech/cloud/)

### 5. Setup Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from example
copy .env.example .env

# Edit .env with your Cohere API Key
COHERE_API_KEY=your_actual_api_key_here
QDRANT_URL=http://localhost:6333
```

To get your Cohere API Key:
1. Go to https://cohere.com/
2. Sign up (free tier available)
3. Create an API key in your dashboard
4. Add it to `.env`

### 6. Prepare Your Data

Create a `data/` directory and add PDF files:

```
project_root/
├── data/
│   ├── myanmar_text.pdf
│   ├── english_text.pdf
│   └── bilingual_content.pdf
├── main.py
├── .env
└── ...
```

## Running the Pipeline

### Start Qdrant (if using Docker)

In a separate terminal:

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Run the Pipeline

```bash
# Using uv
uv run python main.py

# Or with activated venv
python main.py
```

## Expected Output

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
✓ Loaded 10 pages from data/sample.pdf

5. Chunking and embedding documents...
✓ Created 45 chunks from 10 documents
✓ Documents added to vector store

6. Setting up RAG pipeline...
✓ RAG pipeline created successfully

7. Testing RAG pipeline...

Query: What is the main topic of the documents?
------------------------------------------------------------
Answer: Based on the provided documents, the main topic is...

============================================================
✓ RAG Pipeline setup complete!
============================================================
```

## How It Works

### 1. **Document Ingestion & Sanitization**
- Loads PDF files from `data/` directory
- Removes zero-width characters that inflate token count
- Standardizes Burmese punctuation (။ and ၊)
- Removes excessive whitespace

### 2. **Tokenization & Chunking**
- Uses Cohere's tokenizer to measure token count accurately
- Splits documents into 350-token chunks with 35-token overlap
- Respects Burmese syllable boundaries (။ and ၊)

### 3. **Embedding & Vectorization**
- Uses Cohere Embed v4 model (1536 dimensions)
- Generates dense vector representations for semantic search
- Stores vectors in Qdrant with multilingual BM25 indexing

### 4. **Hybrid Retrieval**
- **Dense Search**: Semantic similarity using vector embeddings
- **Sparse Search**: Exact keyword matching using BM25
- Returns top 5 most relevant context windows

### 5. **Generation**
- Uses Cohere's Command R+ LLM
- Enforces language matching (Burmese queries get Burmese responses)
- Includes guardrails to prevent hallucination

## Querying the System

After the pipeline is running, you can query it with:

```python
# English query
query = "What are the main findings?"
result = rag_pipeline.invoke({"input": query})
print(result["output"])

# Myanmar query
query = "အဓိက ရလဒ်များ သည် အဘယ်နည်း။"
result = rag_pipeline.invoke({"input": query})
print(result["output"])
```

## Troubleshooting

### Error: "COHERE_API_KEY not found"
- Make sure `.env` file exists in project root
- Verify the API key is set correctly
- The key should start with `co-`

### Error: "Could not connect to Qdrant"
- Start Qdrant with Docker: `docker run -p 6333:6333 qdrant/qdrant`
- Or change `QDRANT_URL` in `.env` to use Qdrant Cloud

### Error: "No PDF files found in data/"
- Create the `data/` directory
- Add at least one PDF file with Myanmar or English text
- Re-run the pipeline

### Error: "ModuleNotFoundError"
- Install missing dependencies: `pip install -r requirements.txt`
- Or use: `uv pip install langchain langchain-cohere langchain-qdrant qdrant-client`

## Project Structure

```
rag/
├── main.py              # Main RAG pipeline
├── AGENTS.md            # Agent instructions for OpenCode
├── SETUP.md             # Detailed setup guide
├── README.md            # This file
├── plan.md              # Architecture blueprint
├── .env.example         # Environment template
├── .env                 # Environment variables (create from .example)
├── data/                # PDF documents go here
├── qdrant_storage/      # Qdrant persistent storage (created by Docker)
└── .venv/               # Python virtual environment
```

## Configuration

Key settings in `main.py`:

```python
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "myanmar_english_knowledge_corp"
```

Text splitting configuration:

```python
chunk_size=350              # Max tokens per chunk
chunk_overlap=35            # 10% overlap between chunks
separators=["\n\n", "\n", "။", "၊", " ", ""]  # Split points (Burmese-aware)
```

## Validation Checklist

Before running, ensure:

- [ ] Python 3.13+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with COHERE_API_KEY
- [ ] Qdrant running (Docker or Cloud)
- [ ] `data/` directory created
- [ ] At least one PDF file in `data/`
- [ ] Network connection (for Cohere API calls)

## Next Steps

1. **Add More Documents**: Place additional PDFs in `data/`
2. **Fine-tune Parameters**: Adjust chunk_size, overlap, or model settings
3. **Implement Web UI**: Create a Streamlit or FastAPI interface
4. **Deploy**: Push to production with proper monitoring
5. **Evaluate**: Test quality with benchmark datasets

## References

- [Cohere API Documentation](https://docs.cohere.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain Documentation](https://python.langchain.com/)
- [Plan Documentation](./plan.md) - Technical architecture details

## Support

For issues or questions:
1. Check SETUP.md for detailed troubleshooting
2. Review AGENTS.md for project conventions
3. Consult plan.md for architecture details
