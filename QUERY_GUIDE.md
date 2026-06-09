# Interactive RAG Query Guide

## Overview

The updated RAG pipeline now supports interactive querying with your custom OpenAI-compatible LLM endpoint.

## Setup (First Time Only)

### 1. Update `.env` file with your LLM configuration

```bash
# LLM Configuration - Custom OpenAI Compatible Endpoint
LLM_API_BASE=http://localhost:8000        # Your LLM endpoint URL
LLM_API_KEY=your_api_key_here            # Your API key
LLM_MODEL=your-model-name                # Model name (e.g., gpt-3.5-turbo, mistral, etc.)
```

**Example configurations:**

```bash
# Local Ollama
LLM_API_BASE=http://localhost:11434
LLM_API_KEY=ollama
LLM_MODEL=mistral

# Local LM Studio
LLM_API_BASE=http://localhost:1234
LLM_API_KEY=lm-studio
LLM_MODEL=local-model

# Remote API-compatible service
LLM_API_BASE=https://api.example.com/v1
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-3.5-turbo
```

### 2. Ensure your LLM endpoint is running

Before running the pipeline, make sure:
- Your LLM endpoint is accessible at `LLM_API_BASE`
- The endpoint supports OpenAI-compatible API format
- You have a valid API key

## Running the Pipeline

### Start the RAG pipeline:

```bash
uv run python main.py
```

### Expected output:

```
[OK] Configuration loaded successfully

============================================================
Myanmar-English Bilingual RAG Pipeline
============================================================

1. Initializing Cohere Embeddings (v3.0 multilingual)...
[OK] Embeddings engine initialized

2. Initializing Qdrant vector database...
[OK] Qdrant initialized

3. Creating vector store...
[OK] Vector store created

4. Loading and processing documents...
[OK] Loaded X pages from data/...

5. Chunking and embedding documents...
[OK] Created Y chunks from Z documents

6. Setting up RAG pipeline...
[OK] RAG pipeline created successfully

7. RAG Pipeline ready for queries!

============================================================
INTERACTIVE RAG QUERY MODE
============================================================

You can now ask questions about the documents.
Supports Myanmar (Burmese) and English queries.
Type 'exit' or 'quit' to stop.

> Your Question:
```

## Using the Interactive Query Loop

### Ask questions:

```
> Your Question: What is the main topic of the documents?

[Query #1] What is the main topic of the documents?
------------------------------------------------------------
[Processing] Retrieving documents...

[OK] Response received

[Answer]:
Based on the documents, the main topic is...
```

### Supported query types:

1. **English queries** - Will retrieve documents and generate English responses
2. **Myanmar/Burmese queries** - Supports Myanmar Unicode text
3. **Mixed language queries** - Can reference both languages

### Example queries:

```
> What are the key skills mentioned?
> အဲဒီ ឯកសารတွေ၏ အဓိက အကြောင်းအရာက ဘာလဲ?
> Tell me about the experience section
> ပညာရေး အချက်အလက်ကို ပြောပြပါ
```

### Exit the program:

Type any of:
- `exit`
- `quit`
- `bye`

Or press `Ctrl+C` to interrupt

## Troubleshooting

### "Connection refused" error

**Problem:** Pipeline can't reach your LLM endpoint

**Solution:**
1. Verify your endpoint is running at `LLM_API_BASE`
2. Check the .env file has correct URL
3. Test connectivity: `curl http://your-endpoint:port/health` or similar

```bash
# Example: Test Ollama endpoint
curl http://localhost:11434/api/tags

# Example: Test LM Studio endpoint  
curl http://localhost:1234/v1/models
```

### "Unauthorized" or "API key" error

**Problem:** Invalid or missing API key

**Solution:**
1. Check `LLM_API_KEY` in .env is correct
2. Verify your endpoint accepts the key format you're using
3. Try with a test key specific to your endpoint

### "Model not found" error

**Problem:** `LLM_MODEL` doesn't exist on your endpoint

**Solution:**
1. Check what models are available on your endpoint
2. Update `LLM_MODEL` in .env to a valid model name

```bash
# For Ollama
ollama list

# For LM Studio - check the UI or API
curl http://localhost:1234/v1/models
```

### Timeouts or slow responses

**Problem:** LLM endpoint is slow or not responding

**Solution:**
1. Check if your endpoint process is running
2. Try a simpler query first
3. Check endpoint logs for errors
4. Increase retry delay if needed (edit `retry_delay` in code)

## Endpoint Compatibility

The pipeline uses the OpenAI-compatible API format. Compatible endpoints include:

- ✓ OpenAI (gpt-3.5-turbo, gpt-4, etc.)
- ✓ Ollama (local)
- ✓ LM Studio (local)
- ✓ Hugging Face Inference API
- ✓ Together AI
- ✓ Replicate
- ✓ Anthropic Claude (via OpenAI adapter)
- ✓ Any OpenAI-compatible service

## Performance Tips

1. **Batch similar queries together** - The pipeline caches embeddings
2. **Use specific queries** - More specific questions get better results
3. **Verify your documents** - Check that data/ has relevant PDFs
4. **Monitor API usage** - Track your LLM endpoint's rate limits

## What Happens Behind the Scenes

```
Your Question
     ↓
[Retriever] Find relevant chunks in Qdrant
     ↓
[Context] Format top 5 most relevant documents
     ↓
[Prompt] Create bilingual prompt with context
     ↓
[LLM] Send to your custom endpoint
     ↓
[Response] Return generated answer
     ↓
Your Answer
```

## Advanced Configuration

### Adjust retrieval behavior (edit main.py):

```python
# Line ~243: Change number of documents retrieved
retriever = vector_store.as_retriever(search_kwargs={"k": 10})  # Get 10 instead of 5

# Line ~213: Adjust LLM temperature (creativity)
llm_engine = ChatOpenAI(
    ...
    temperature=0.5,  # Higher = more creative, Lower = more factual
)
```

### Custom prompt template (edit main.py):

Modify the `bilingual_prompt_template` in `create_rag_pipeline()` function to customize how responses are generated.

## Support

- Check SETUP.md for environment setup issues
- Review EXECUTION_GUIDE.md for detailed troubleshooting
- See README.md for architecture details

Happy querying! 🚀
