from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.config import settings
from api.routes import query, ingest, export

app = FastAPI(
    title="Myanmar-English Bilingual RAG API",
    version="0.2.0",
    description="Retrieval-Augmented Generation for Myanmar and English text",
)

app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(export.router)


@app.get("/")
async def root():
    return {
        "service": "myanmar-rag",
        "embedding_mode": settings.embedding_mode,
        "collection": settings.collection_name,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
