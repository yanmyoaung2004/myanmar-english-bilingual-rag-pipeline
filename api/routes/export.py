import os
from fastapi import APIRouter, HTTPException

from api.schemas import ExportResponse
from exporters.corpus_exporter import export_corpus

router = APIRouter(prefix="/export", tags=["export"])


@router.get("", response_model=ExportResponse)
async def export_endpoint(version: str = "v0.1.0"):
    try:
        result = export_corpus(version)
        return ExportResponse(
            status="ok",
            version=version,
            pages=result["pages"],
            characters=result["characters"],
            path=result["path"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
