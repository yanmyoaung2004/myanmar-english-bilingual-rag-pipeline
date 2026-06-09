from typing import List, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = None


class IngestResponse(BaseModel):
    status: str
    file: str
    chunks_added: int
    embedding_mode: str


class ExportResponse(BaseModel):
    status: str
    version: str
    pages: int
    characters: int
    path: str


class ErrorResponse(BaseModel):
    detail: str
