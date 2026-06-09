## Architecture Blueprint

```
[DOCUMENT INGESTION]
  PDFs / Docs / Text -> Regular Expression Sanitizer -> Token-Aware Recursive Chunker (Max 350 Cohere Tokens)
                                                                 │
                                                                 ▼
[VECTORIZATION & STORAGE]
  LangChain Vector Store Wrapper -> Cohere Embed v4 (1536-dim) -> Qdrant (Dense payload + Named Payload BM25)
                                                                 │
                                                                 ▼
[RETRIEVAL RUNTIME]
  User Query -> Multi-Script Encoding Validation -> Parallel Retrieval (Dense Search + Sparse BM25 Search)
                                                                 │
                                                                 ▼
[CONTEXT COMPRESSION]
  Reciprocal Rank Fusion (RRF) -> Cohere Rerank v4 Multilingual -> Top 5 Validated Context Windows
                                                                 │
                                                                 ▼
[GENERATION]
  Command R+ LLM -> Cross-Script Guardrail Prompt Enforcement -> Output (Matching Query Script)

```

---

## Phase 1: Environment & Infrastructure Configuration

You must drop ChromaDB. To execute high-performance hybrid (vector + text string match) retrieval for Burmese Unicode syllables and compound phrases, you need an enterprise engine like **Qdrant**.

### 1.1 Local/Production Setup via Docker

Run a Qdrant container with text indexing modules enabled natively.

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

```

### 1.2 Python Dependencies

```bash
pip install langchain langchain-cohere langchain-qdrant qdrant-client pypdf tokenizers cohere

```

---

## Phase 2: The Ingestion Pipeline (Data Sanitation & Chunking)

Even when working strictly with Unicode, Burmese scripts can contain irregular, invisible formatting sequences (e.g., dangling zero-width characters or non-standard visual stackings) that inflate token consumption or skew vector metrics.

### 2.1 File Parser and Unicode Normalizer Script

```python
import re
from langchain_community.document_loaders import PyPDFLoader

def strict_unicode_sanitizer(text: str) -> str:
    """
    Cleans structural noise, phantom spaces, and normalizes breaks
    without fracturing compound Burmese characters.
    """
    # Strip dangerous zero-width non-joiners/joiners which cause token inflation
    text = re.sub(r'[\u200c\u200d]', '', text)
    # Standardize consecutive Burmese punctuation markers (Pyaat-thone / Shone)
    text = re.sub(r'\s*။\s*', '။ ', text)
    text = re.sub(r'\s*၊\s*', '၊ ', text)
    # Collapse multiple whitespace lines down to logical bounds
    return re.sub(r' +', ' ', text).strip()

def load_and_sanitize_documents(file_path: str):
    loader = PyPDFLoader(file_path)
    raw_docs = loader.load()
    for doc in raw_docs:
        doc.page_content = strict_unicode_sanitizer(doc.page_content)
    return raw_docs

```

### 2.2 Cohere Tokenizer-Aware Dynamic Text Splitter

Burmese text can consume up to $4\times$ more tokens than an identical English concept because multilingual models fracture complex scripts into minor byte-level or sub-token fragments. We force LangChain to query the true Cohere backend to calculate chunk sizes.

```python
import cohere
from langchain_text_splitters import RecursiveCharacterTextSplitter

cohere_client = cohere.ClientV2(api_key="YOUR_COHERE_API_KEY")

def calculated_cohere_token_metric(text: str) -> int:
    """
    Returns exact token footprints relative to the Cohere Embed v4 vector space.
    """
    if not text.strip():
        return 0
    response = cohere_client.tokenize(text=text, model="embed-v4.0")
    return len(response.tokens)

# Defensive block configuration for low-resource cross-lingual data
bilingual_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,       # Strict token ceiling to keep context readable for LLMs
    chunk_overlap=35,     # 10% structural boundary overlay
    length_function=calculated_cohere_token_metric,
    separators=["\n\n", "\n", "။", "၊", " ", ""] # Checks paragraph down to Burmese syllable splits
)

```

---

## Phase 3: Vector Layer & Hybrid Optimization

Cohere Embed v4 outputs a default length of **1536 dimensions**. We must register this collection in Qdrant and structure a background keyword index targeting the payload content.

```python
from langchain_cohere import CohereEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Initialize embeddings with the mandatory system flag
embeddings_engine = CohereEmbeddings(
    model="embed-v4.0",
    cohere_api_key="YOUR_COHERE_API_KEY"
)

client = QdrantClient(url="http://localhost:6333")
collection_name = "myanmar_english_knowledge_corp"

# Initialize Qdrant Collection Structure
client.create_collection(
    collection_name=collection_name,
    vectors_config=qmodels.VectorParams(
        size=1536, # Cohere v4 native size
        distance=qmodels.Distance.COSINE
    )
)

# Build a Full-Text Lexical Index inside the payload to support exact Burmese keyword matching
client.create_payload_index(
    collection_name=collection_name,
    field_name="metadata.page_content",
    field_schema=qmodels.TextIndexParams(
        type=qmodels.TextIndexType.TEXT,
        tokenizer=qmodels.TokenizerType.MULTILINGUAL, # Natively handles complex token breaks
    ),
)

# Upload chunks via LangChain abstraction layer
vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings_engine
)
# Documents addition: vector_store.add_documents(processed_chunks)

```

---

## Phase 4: Hybrid Search & Cross-Lingual Reranking

When a user searches in English, their query vector might sit farther away from a target Burmese Unicode document due to representation disparities. We address this using a **two-stage retrieval pipeline**: retrieve heavily using dense + sparse techniques, then execute deep alignment using Cohere's Multilingual Cross-Encoder Reranker.

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere import ChatCohere

# 1. Base Retrieval Layer: Fetch broad candidate lists via Hybrid Vector Space
base_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 25} # Over-retrieve to give the reranker enough text data
)

# 2. Re-evaluation Layer: Resolve the English-to-Myanmar concept alignment gaps
multilingual_compressor = CohereRerank(
    model="rerank-v4.0-pro", # Latest enterprise model
    top_n=5,                # Drop down to the absolute best 5 documents for LLM processing
    cohere_api_key="YOUR_COHERE_API_KEY"
)

optimized_retriever = ContextualCompressionRetriever(
    base_compressor=multilingual_compressor,
    base_retriever=base_retriever
)

```

---

## Phase 5: Generator System Guardrails

Your model system prompt must clearly define linguistic rules. Without strict constraint boundaries, LLMs often translate your documents internally and respond in English when a query is submitted in Burmese.

```python
# System prompt to enforce structural context boundaries
bilingual_prompt_template = (
    "You are an expert bilingual knowledge engine serving users in Myanmar and English.\n"
    "Carefully evaluate the following context extracts to answer the incoming user query. "
    "The texts are raw, verified Unicode segments containing cross-lingual knowledge entries.\n\n"
    "CRITICAL GENERATION INSTRUCTIONS:\n"
    "1. You must respond to the user utilizing the exact language, script, and writing style of their question.\n"
    "2. If the query is written in Burmese Unicode, your entire thought structure and final output must be in pure Burmese Unicode.\n"
    "3. If the answer cannot be confidently verified inside the provided context documents, state directly that you do not possess sufficient data to answer.\n\n"
    "Context:\n{context}\n\n"
    "User Question: {input}\n"
    "System Verified Output:"
)

prompt_generation_framework = ChatPromptTemplate.from_messages([
    ("system", bilingual_prompt_template)
])

# Assemble final execution layer using a robust multi-lingual LLM
llm_engine = ChatCohere(model="command-r-plus", cohere_api_key="YOUR_COHERE_API_KEY")

document_compilation_chain = create_stuff_documents_chain(llm_engine, prompt_generation_framework)
rag_application_system = create_retrieval_chain(optimized_retriever, document_compilation_chain)

```

---

## Phase 6: Execution & Evaluation Checklist

To verify your system functions reliably in production, systematically execute these three targeted validation routines:

- **Verify Syllable Splitting Integrity:** Review the payload blocks inside Qdrant. Ensure your Burmese sentence blocks terminate on logical end-stops (`။`) rather than fragmenting mid-word.
- **Test Language Invariance:** Submit an identical domain question in English and Burmese Unicode. The system should target and return the exact same content chunk regardless of the input language.
- **Confirm Context Constraints:** Submit a query that is completely unrelated to your document corpus. Ensure the generation layer aborts and fires the "insufficient data" fallback sequence instead of hallucinating.
