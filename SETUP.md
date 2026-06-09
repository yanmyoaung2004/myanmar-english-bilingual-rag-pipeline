# RAG Pipeline Setup & Execution Guide

## What We've Done So Far

1. **Installed Python Dependencies**: langchain, langchain-cohere, langchain-qdrant, qdrant-client, pypdf, cohere, tokenizers
2. **Created AGENTS.md**: Documentation for the project structure and conventions
3. **Started main.py**: Skeleton of the RAG pipeline with:
   - Unicode sanitization for Burmese text
   - Cohere Embeddings v4 integration
   - Qdrant vector store setup
   - Bilingual prompt templates
   - LangChain retrieval chains

## What You Need to Do to Run This Project

### Step 1: Set Up Qdrant Database

Qdrant is an in-memory or persistent vector database. You have two options:

#### Option A: Using Docker (Recommended for Production)
```bash
# Make sure Docker is running
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

#### Option B: Using Qdrant in-memory Client (Development)
```bash
# This is what we'll use for now - no external service needed
# The qdrant-client can work in memory
```

### Step 2: Get Cohere API Key

1. Go to https://cohere.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Store it as an environment variable: `COHERE_API_KEY`

### Step 3: Prepare Your Data

You need to have one or more PDF files with Myanmar and/or English text:
- Place your PDF files in a data directory (e.g., `data/`)
- The pipeline will extract text, clean it, and convert to embeddings

### Step 4: Install Missing Dependencies

```bash
# Additional dependencies we may need
pip install langchain-text-splitters
pip install pypdf
pip install python-dotenv  # for managing env variables
```

### Step 5: Run the Project

```bash
# Activate virtual environment (if using one)
# On Windows:
.venv\Scripts\activate

# Run the project
uv run python main.py
```

## Current Issues in main.py

1. **Missing imports**: QdrantClient, qmodels not imported
2. **Missing function**: `calculated_cohere_token_metric` not defined
3. **Missing import**: PyPDFLoader not imported
4. **Undefined variable**: `client` used before proper initialization
5. **Error handling**: No try-catch blocks
6. **Configuration**: API key hardcoded instead of using environment variables

## Complete Requirements Checklist

- [x] Python 3.13+
- [x] langchain (already installed)
- [x] langchain-cohere (already installed)
- [x] langchain-qdrant (already installed)
- [x] qdrant-client (already installed)
- [x] cohere (already installed)
- [x] pypdf (already installed)
- [x] tokenizers (already installed)
- [ ] COHERE_API_KEY environment variable set
- [ ] .env file with API key
- [ ] Sample PDF files in `data/` directory
- [ ] Qdrant instance running (docker or in-memory)

## Next Steps

1. Fix main.py to handle all imports and errors properly
2. Create a .env file for API keys
3. Create sample data directory
4. Add proper configuration management
5. Test with sample Myanmar + English text
6. Add logging and monitoring
