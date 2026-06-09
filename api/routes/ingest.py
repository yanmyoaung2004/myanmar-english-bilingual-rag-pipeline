import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from api.schemas import IngestResponse
from core.config import settings
from core.sanitizer import sanitize_documents
from core.chunker import get_chunker
from core.embeddings import get_embedding_strategy
from core.retriever import add_documents

router = APIRouter(prefix="/ingest", tags=["ingest"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".jpg", ".jpeg", ".png"}


@router.post("", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    os.makedirs(settings.data_dir, exist_ok=True)
    save_path = os.path.join(settings.data_dir, f"{uuid.uuid4()}{ext}")
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(save_path)
        raw_docs = loader.load()
    elif ext == ".txt":
        from langchain_core.documents import Document
        text = Path(save_path).read_text(encoding="utf-8")
        raw_docs = [Document(page_content=text, metadata={"source": file.filename})]
    else:
        raise HTTPException(400, "Image OCR not supported yet — use PDF or TXT")

    docs = sanitize_documents(raw_docs)

    strategy = get_embedding_strategy()
    chunker = get_chunker(settings.embedding_mode)
    chunks = chunker.split_documents(docs)

    add_documents(chunks, strategy)

    return IngestResponse(
        status="ok",
        file=file.filename,
        chunks_added=len(chunks),
        embedding_mode=settings.embedding_mode,
    )
