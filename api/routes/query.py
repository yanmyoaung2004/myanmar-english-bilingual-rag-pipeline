from fastapi import APIRouter, HTTPException

from api.schemas import QueryRequest, QueryResponse
from rag.pipeline import build_rag_pipeline
from core.embeddings import get_embedding_strategy
from core.config import settings

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    try:
        strategy = get_embedding_strategy()
        pipeline = build_rag_pipeline(strategy, req.top_k)
        result = pipeline.invoke(req.question)

        content = ""
        if hasattr(result, "content"):
            content = result.content
        elif isinstance(result, dict):
            content = result.get("content", str(result))
        else:
            content = str(result)

        return QueryResponse(answer=content, sources=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "ok", "embedding_mode": settings.embedding_mode}
