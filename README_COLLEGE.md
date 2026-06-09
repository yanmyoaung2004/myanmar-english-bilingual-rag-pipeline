# README for College Edition

# Myanmar-English Bilingual RAG Pipeline
## College Edition

A complete, production-ready Retrieval-Augmented Generation (RAG) system with support for Myanmar (Burmese) and English languages.

### 🎯 What is This Project?

A RAG pipeline that:
- **Loads** PDF documents in Myanmar and English
- **Processes** text with Unicode-aware tokenization
- **Embeds** documents using Cohere's multilingual embeddings
- **Stores** vectors in Qdrant for efficient retrieval
- **Retrieves** relevant documents based on queries
- **Generates** responses using custom LLM endpoints

Perfect for learning, research, and production deployment.

### ✨ Key Features

- ✅ **Bilingual Support** - Myanmar (Burmese) + English
- ✅ **Hybrid Search** - Dense vectors + BM25 keyword matching
- ✅ **Multilingual Embeddings** - Cohere Embed v3 (1024 dimensions)
- ✅ **Token-Aware Chunking** - Accurate 350-token chunks with 35-token overlap
- ✅ **Custom LLM Support** - Any OpenAI-compatible endpoint
- ✅ **Interactive Querying** - Built-in query loop
- ✅ **Well-Documented** - 10 comprehensive guides

### 🚀 Quick Start (5 Minutes)

#### 1. Prerequisites
- Python 3.13+ (via `uv` or direct installation)
- Cohere API key (free tier available)
- Qdrant instance (local Docker or cloud)
- Custom LLM endpoint (local or remote)

#### 2. Setup
```bash
# Clone the repository
git clone <repo-url>
cd rag

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - COHERE_API_KEY: Get from https://cohere.com/
# - QDRANT_URL: Local (http://localhost:6333) or cloud
# - LLM_API_BASE: Your LLM endpoint
# - LLM_MODEL: Model name
```

#### 3. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or use pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r pyproject.toml
```

#### 4. Add Sample Documents
```bash
# Place your PDF files in data/ folder
# Supports Myanmar, English, and bilingual PDFs
cp your_documents.pdf data/
```

#### 5. Run the Pipeline
```bash
# Using uv
uv run python main.py

# Or with direct Python
python main.py
```

#### 6. Start Querying
```
> Your Question: What is the main topic?
[Processing] Retrieving documents...
[OK] Response received

[Answer]:
Based on the documents...
```

### 📚 Documentation

| Document | Purpose |
|----------|---------|
| `INDEX.md` | Navigation guide - Start here |
| `QUICK_START.md` | 5-minute setup guide |
| `SETUP.md` | Detailed installation & troubleshooting |
| `EXECUTION_GUIDE.md` | Step-by-step usage instructions |
| `QUERY_GUIDE.md` | Interactive querying guide |
| `plan.md` | Technical architecture & design |
| `SAMPLE_DATA.md` | How to add test documents |
| `CLEANUP_REPORT.md` | Accuracy metrics & cleanup decisions |

### 🏗️ Architecture

```
Your Question
     ↓
[Retriever] Find top 5 relevant chunks from Qdrant
     ↓
[Context Formatter] Prepare retrieved documents
     ↓
[Prompt Builder] Create bilingual prompt
     ↓
[LLM] Send to custom endpoint (OpenAI-compatible)
     ↓
[Response] Language-matched answer
     ↓
Your Answer
```

### 📊 System Specifications

| Component | Details |
|-----------|---------|
| **Embedding Model** | Cohere Embed v3 Multilingual (1024 dimensions) |
| **Vector Database** | Qdrant with multilingual BM25 indexing |
| **Chunk Size** | 350 tokens with 35-token overlap |
| **Top Results** | Top 5 most relevant documents retrieved |
| **Languages** | Myanmar (Burmese) + English |
| **LLM Support** | Any OpenAI-compatible endpoint |
| **Python Version** | 3.13+ |

### 🔧 Configuration

All configuration via `.env` file:

```bash
# Embeddings
COHERE_API_KEY=sk-...

# Vector Database
QDRANT_URL=http://localhost:6333

# Language Model
LLM_API_BASE=http://localhost:8000
LLM_API_KEY=your-key
LLM_MODEL=gpt-3.5-turbo
```

### 📝 Example Queries

```
# English
> What are the key topics?
> Summarize the documents

# Myanmar (Burmese)
> အဲဒီ ឯកសារတွေ၏ အဓိက အကြောင်းအရာက ဘာလဲ?
> အခြင်း အခြင်း အသေးစိတ်ကို ပြောပြပါ

# Mixed
> Tell me about the Myanmar content and English sections
```

### 🛠️ Development

**Project Structure:**
```
rag/
├── main.py                 # Core RAG pipeline
├── test_accuracy.py        # Accuracy testing suite
├── pyproject.toml          # Dependencies
├── .env.example            # Configuration template
├── data/                   # Your PDF documents
└── docs/                   # Documentation
```

**Adding Features:**
1. Modify prompt template in `main.py` (line ~220)
2. Adjust retrieval count (line ~243, `k=5`)
3. Change chunk size (line ~305, `chunk_size=350`)
4. Customize LLM parameters (line ~230, `temperature=0.3`)

### 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines.

### 📖 Learning Resources

- **Cohere Embeddings**: https://docs.cohere.com/
- **Qdrant Vector DB**: https://qdrant.tech/documentation/
- **LangChain Framework**: https://python.langchain.com/
- **RAG Concepts**: https://en.wikipedia.org/wiki/Retrieval-augmented_generation

### ⚠️ Troubleshooting

**Connection Refused Error?**
- Ensure Qdrant is running: `docker run -p 6333:6333 qdrant/qdrant`
- Check LLM endpoint is accessible at `LLM_API_BASE`
- Verify `.env` has correct URLs

**API Key Error?**
- Check `COHERE_API_KEY` in `.env`
- Verify LLM API key format matches your endpoint
- Ensure APIs are not rate-limited

**Low Accuracy?**
- Add more relevant documents to `data/`
- Check document quality and structure
- Run `python test_accuracy.py` to diagnose
- Review `plan.md` for optimization tips

See `SETUP.md` for detailed troubleshooting.

### 📄 License

[Add your license here]

### 👥 Authors

[Add your information here]

### 🎓 Academic Use

This project is designed for educational and research purposes. Ideal for:
- AI/ML coursework
- RAG system learning
- Multilingual NLP research
- Vector database study
- LLM integration projects

### 📞 Support

- Check documentation in `INDEX.md`
- Review troubleshooting in `SETUP.md`
- Test accuracy with `test_accuracy.py`
- See examples in `QUERY_GUIDE.md`

---

**Ready to get started?** Begin with `QUICK_START.md` (5 minutes) or dive deep into `plan.md` for architecture details.
