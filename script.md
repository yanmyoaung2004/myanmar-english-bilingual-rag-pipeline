# Myanmar-English Bilingual RAG Pipeline
## Presentation Script

---

## Slide 1: The Problem

**"How do you make a computer understand documents in two completely different scripts?"**

Myanmar (Burmese) and English are nothing alike:
- Different alphabets (Myanmar script vs Latin)
- Different word boundaries (English uses spaces, Burmese doesn't)
- Different NLP tools available

Most RAG systems are built for English-only. If you throw Myanmar text at them, they break.

---

## Slide 2: What This Project Does

A **RAG** (Retrieval-Augmented Generation) system that:

1. Takes PDF documents in **Myanmar or English**
2. Lets you **ask questions** in either language
3. **Retrieves the relevant passages** from the documents
4. **Generates an answer** in the **same language** you asked in

> Ask in Myanmar → Get answer in Myanmar
> Ask in English → Get answer in English

---

## Slide 3: Big Picture Architecture

```
                    ╔══════════════════════════════════════╗
                    ║       STEP 1: DOCUMENT INGESTION     ║
                    ║  PDF → Clean Unicode → Split into   ║
                    ║  350-token chunks (Burmese-aware)   ║
                    ╚══════════════════════╤═══════════════╝
                                           │
                    ╔══════════════════════▼═══════════════╗
                    ║       STEP 2: VECTORIZATION          ║
                    ║  Each chunk → Embedding (1536 nums)  ║
                    ║  Store in Qdrant (dense + BM25)      ║
                    ╚══════════════════════╤═══════════════╝
                                           │
                    ╔══════════════════════▼═══════════════╗
                    ║       STEP 3: RETRIEVAL              ║
                    ║  Your question → Hybrid search       ║
                    ║  → Top 5 most relevant chunks        ║
                    ╚══════════════════════╤═══════════════╝
                                           │
                    ╔══════════════════════▼═══════════════╗
                    ║       STEP 4: GENERATION             ║
                    ║  LLM reads chunks + question         ║
                    ║  → Generates answer in same script   ║
                    ╚══════════════════════════════════════╝
```

Straight line. Four steps. Simple.

---

## Slide 4: Step 1 — Document Ingestion (The Cleanup)

**What happens when you give the system a PDF?**

```
Raw PDF text → [1] Strip zero-width characters → [2] Fix Burmese punctuation
→ [3] Remove extra whitespace → [4] Split into chunks
```

### Why this matters for Myanmar text

Burmese documents often have **invisible characters** (zero-width joiners/non-joiners) that:
- Inflate token counts (you pay for tokens you can't see)
- Break embedding quality

The sanitizer strips them out before anything else happens.

### Burmese-aware chunking

The chunker is told: **"Split at these points in this order"**

```
First try:    paragraph breaks (\n\n)
Then try:     line breaks (\n)
Then try:     Burmese period (။)
Then try:     Burmese comma (၊)
Then try:     spaces
Last resort:  any character
```

This means a chunk never breaks in the middle of a Burmese word — it breaks at natural punctuation points instead.

---

## Slide 5: Step 2 — Vectorization (Turning Words Into Numbers)

**Computers don't understand words. They understand numbers.**

Each chunk of text gets converted into a **list of 1,536 numbers** — an "embedding."

### The technology: Cohere Embed v4

- Model: `embed-multilingual-v3.0`
- Output: 1,536 floating-point numbers per chunk
- Why Cohere? It's optimized for **multilingual** text — one of the few embedding models that handles Myanmar script well

```
"မြန်မာစာ ကောင်းသည်"  →  [0.234, -0.567, 0.891, ..., 0.123]
                                      (1,536 numbers)
```

### The storage: Qdrant Vector Database

Qdrant stores:
1. **The 1,536-number vector** (for semantic similarity search)
2. **A BM25 text index** (for keyword search — like Google for exact words)

Two search methods = better results.

---

## Slide 6: Step 3 — Retrieval (Finding The Answer)

**User asks:** "What is the main topic of the documents?"

### What happens behind the scenes

```
User's question
        │
        ▼
[1] Convert question to embedding (same 1,536-number format)
        │
        ▼
[2] Search Qdrant two ways:
    ┌─────────────────────┐
    │ DENSE: Find chunks  │  ← Semantic meaning
    │ with similar vectors │     ("main topic" ~ "primary subject")
    ├─────────────────────┤
    │ SPARSE: Find chunks │  ← Exact words
    │ with the same words │     (matches "topic" literally)
    └─────────────────────┘
        │
        ▼
[3] Take top 5 most relevant chunks
        │
        ▼
[4] Send them to the LLM
```

**Top 5 chunks** is the sweet spot — enough context for a good answer, not so much that it overwhelms the model.

---

## Slide 7: Step 4 — Generation (The Answer)

The LLM receives:

```
CONTEXT: [5 relevant chunks]
QUESTION: "What is the main topic?"

INSTRUCTION:
- Answer in the SAME language as the question
- If Myanmar → answer in Myanmar Unicode
- If English → answer in English
- Don't make things up
- If you don't know, say so
```

### The LLM options

| Option | How it works |
|---|---|
| **Default** | Uses an OpenAI-compatible endpoint (localhost:8000) |
| **Custom LLM** | Point it at any API that speaks the OpenAI format |
| **Cohere Command R+** | Just swap the endpoint |

The prompt has **guardrails** — explicit instructions to:
- Match the query script (no mixing languages)
- Refuse to hallucinate (no making stuff up)

---

## Slide 8: Technology Stack (At a Glance)

```
┌─────────────────────────────────────────────────────┐
│                     APPLICATION                      │
│  Python 3.13  │  LangChain  │  Main.py (orchestrator)│
├─────────────────────────────────────────────────────┤
│                    EMBEDDINGS                        │
│         Cohere Embed v4 (multilingual-v3.0)          │
│          Output: 1,536-dim vectors per chunk         │
├─────────────────────────────────────────────────────┤
│                   VECTOR DATABASE                    │
│  Qdrant  │  Dense (cosine similarity)               │
│          │  + Sparse (BM25 text index)              │
├─────────────────────────────────────────────────────┤
│                    LLM LAYER                         │
│  OpenAI-compatible endpoint  │  Configurable model   │
│  (Cohere / GPT / Llama / any)                       │
├─────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE                     │
│  Docker (Qdrant container)  │  uv (Python package)   │
└─────────────────────────────────────────────────────┘
```

---

## Slide 9: Interactive Demo (What You'll See)

Run the pipeline and you get an interactive CLI:

```
> Your Question: What is the main topic?
────────────────────────────────────────────────
[Answer]:
The documents discuss climate change impacts on
coastal communities in Myanmar...

> Your Question: အဓိက အကြောင်းအရာက ဘာလဲ။
────────────────────────────────────────────────
[Answer]:
ရာသီဥတုပြောင်းလဲမှုသည် မြန်မာနိုင်ငံရှိ ကမ်းရိုးတန်း
ဒေသများအပေါ် သက်ရောက်မှုများအကြောင်း...
```

Same question. Two languages. Correct answers in both.

---

## Slide 10: Key Design Decisions

### Why Qdrant instead of Pinecone/Weaviate?

| Requirement | Qdrant | Others |
|---|---|---|
| Runs locally (no cloud) | ✅ Free, Docker | ❌ Often cloud-only |
| BM25 built-in | ✅ Yes | ❌ Extra setup |
| Multilingual tokenizer | ✅ Yes | Varies |

### Why Cohere instead of OpenAI embeddings?

Cohere's `embed-multilingual-v3.0` is specifically trained on multilingual data. For Myanmar text, it dramatically outperforms OpenAI's `text-embedding-ada-002`.

### Why 350 tokens per chunk?

Small enough that the LLM can process multiple chunks. Large enough that each chunk carries meaningful context. 35-token overlap (10%) ensures no information is lost at boundaries.

---

## Slide 11: Running It (Live Demo Ready)

```bash
# Terminal 1: Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: Run the pipeline
uv run python main.py
```

That's it. Two commands.

The pipeline will:
1. Load PDFs from `data/`
2. Sanitize and chunk them
3. Embed and store them
4. Drop you into interactive query mode

---

## Slide 12: What's Next (Roadmap)

Near-term additions:

- **Zawgyi→Unicode converter** — Myanmar text comes in two encodings (Zawgyi and Unicode). The pipeline currently handles Unicode only. Adding Zawgyi detection + conversion will cover 100% of Myanmar digital text.

- **Web UI** — Instead of a terminal, upload PDFs and ask questions in a browser (Streamlit or FastAPI).

- **One-command startup** — Docker Compose that starts everything together.

- **Quality scoring** — Automatically measure how good a retrieval or answer is.

---

## Q&A

**Q: Can it handle mixed Myanmar-English documents?**
Yes. The chunker and embedder both handle mixed script content.

**Q: What if the LLM doesn't know the answer?**
The prompt explicitly tells it to say "I don't have enough information" rather than hallucinate.

**Q: Can I use a different LLM?**
Yes. Set `LLM_API_BASE`, `LLM_API_KEY`, and `LLM_MODEL` in `.env` to point at any OpenAI-compatible endpoint.

**Q: How many documents can it handle?**
Limited only by your Qdrant storage. 10,000+ pages is easily feasible on a laptop.

---

*End of script*
