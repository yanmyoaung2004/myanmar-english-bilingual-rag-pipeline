# Adding Sample Data to the RAG Pipeline

This guide explains how to add documents to test and improve the RAG pipeline.

## Quick Start

1. **Create sample documents**
   - PDF files with clear, structured content
   - Both Myanmar and English supported

2. **Place in `data/` folder**
   ```
   rag/
   └── data/
       ├── README.md (this file)
       ├── document1.pdf
       ├── document2.pdf
       └── document3.pdf
   ```

3. **Re-run the pipeline**
   ```bash
   uv run python main.py
   ```

4. **Start querying**
   ```
   > Your Question: What are the topics?
   ```

## Document Quality Tips

### ✅ Good Documents
- Technical documentation with clear sections
- FAQ documents with Q&A format
- Research papers with structured content
- Manuals with indexed topics
- Articles with clear headings

### ❌ Poor Documents
- Generic, unstructured text
- Documents with minimal content
- Images with OCR'd text
- Corrupted or scrambled PDFs
- Very long documents without sections

## Recommended Sample Documents

### For Testing
1. **Tech FAQ** - Q&A format with clear answers
2. **Wikipedia Article** - Well-structured content
3. **Python Documentation** - Clear sections and examples
4. **Research Paper** - Abstract, sections, references

### For Myanmar Language
1. **Myanmar Wikipedia excerpts** - Structured Myanmar text
2. **Burmese news articles** - Clear Myanmar writing
3. **Technical glossary** - Myanmar + English terms
4. **Cultural documents** - Myanmar content samples

### For Bilingual Testing
1. **Translation pairs** - Same content in both languages
2. **Glossaries** - Term definitions in both languages
3. **Bilingual FAQs** - Q&A in Myanmar and English

## Supported File Formats

| Format | Status | Notes |
|--------|--------|-------|
| PDF | ✅ Supported | Best option |
| TXT | ❌ Not yet | Need to implement |
| DOCX | ❌ Not yet | Need to add support |
| Images | ❌ Not yet | No OCR integration |

## How to Find Good Sample Documents

### Free Sources
1. **Project Gutenberg** - https://www.gutenberg.org/
   - Free books and texts
   - Both English and various languages

2. **Wikipedia** - Save articles as PDF
   - Well-structured content
   - Multiple languages available

3. **Academic Papers** - arXiv, ResearchGate
   - Technical content
   - Clear structure

4. **Documentation**
   - Python docs
   - Technical guides
   - API documentation

### Myanmar Specific Sources
1. **Myanmar Unicode resources**
2. **Local news websites** (if available in PDF)
3. **Educational materials**
4. **Cultural documents**

## Testing Your Documents

### 1. Check File Integrity
```bash
# Verify PDF can be read
python -c "from pypdf import PdfReader; PdfReader('data/your_file.pdf').pages[0].extract_text()"
```

### 2. Test Document Loading
```bash
# Check if pipeline loads your documents
uv run python main.py
# Look for: "[OK] Loaded X pages from data/your_file.pdf"
```

### 3. Manual Query Testing
```bash
# When prompted:
> Your Question: [Type a question about your document content]
# Should retrieve relevant chunks
```

## Testing Your Documents

Successfully loaded documents should:

### 1. Document Selection
- Choose content with clear structure
- Prefer documents > 1 MB (more content)
- Ensure content is relevant to your domain

### 2. Chunk Optimization
- Default: 350 tokens with 35-token overlap
- For short documents: Reduce to 200 tokens
- For long documents: Increase to 500 tokens

Edit `main.py` line ~305:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,        # Adjust this
    chunk_overlap=35,      # And this
    length_function=calculated_cohere_token_metric,
    separators=["\n\n", "\n", "။", "၊", " ", ""]
)
```

### 3. Query Formulation
- Use specific, clear questions
- Include domain keywords
- For Myanmar: Use proper Unicode characters

## Troubleshooting

### Problem: No documents loaded
**Solution:**
- Check PDFs are in `data/` folder
- Verify PDF file integrity
- Check file permissions

### Problem: Low accuracy scores
**Solution:**
- Add more relevant documents
- Use better quality PDFs
- Check document content matches queries
- Increase chunk size for better context

### Problem: Unicode errors (Myanmar text)
**Solution:**
- Ensure PDFs use UTF-8 encoding
- Verify Myanmar Unicode characters are properly formed
- Test with simple queries first

### Problem: Slow processing
**Solution:**
- Remove large PDFs (> 50 MB)
- Reduce number of documents
- Increase chunk size to reduce chunks
- Use local vector database (not cloud)

## Adding Documents Programmatically

For automation, you can modify `main.py`:

```python
# In main() function, before Step 4:
document_sources = [
    "data/file1.pdf",
    "data/file2.pdf",
    "data/file3.pdf",
]

for pdf_path in document_sources:
    if os.path.exists(pdf_path):
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        # Continue with processing...
```

## Evaluating Document Quality

Score each document:

| Criterion | Score | Notes |
|-----------|-------|-------|
| Relevance | 0-10 | How relevant to your domain |
| Structure | 0-10 | Clear sections/headings |
| Clarity | 0-10 | Easy to understand content |
| Completeness | 0-10 | All necessary information |
| Quality | 0-10 | No corruption/errors |
| **Total** | **0-50** | Target: > 35 |

**Score > 35** = Good document for RAG

## Next Steps

1. ✅ Add 3-5 good quality PDFs to `data/`
2. ✅ Run pipeline: `uv run python main.py`
3. ✅ Test with queries related to document content
4. ✅ Refine document selection based on results

## Questions?

- See `QUICK_START.md` for setup help
- Check `QUERY_GUIDE.md` for querying
- Consult `plan.md` for technical details

---

**Happy document loading! 🚀**
