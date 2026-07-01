import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import services.embedder as embedder
from services.pinecone_client import query as pinecone_query

router = APIRouter(prefix="/search", tags=["Image Search"])

class ImageSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)

class ImageResult(BaseModel):
    asset_path: str
    asset_url: str
    score: float
    metadata: Optional[dict] = None

class ImageSearchResponse(BaseModel):
    query: str
    count: int
    latency_ms: float
    results: list[ImageResult]

@router.post("/images", response_model=ImageSearchResponse)
async def search_images(body: ImageSearchRequest):
    t0 = time.perf_counter()
    try:
        query_vector = embedder.embed_text(body.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    try:
        matches = pinecone_query(vector=query_vector, top_k=body.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    results = [
        ImageResult(
            asset_path=m["id"],
            asset_url=m.get("metadata", {}).get("asset_url", ""),
            score=round(float(m["score"]), 4),
            metadata=m.get("metadata", {})
        )
        for m in matches
        if float(m["score"]) >= body.score_threshold
    ]
    return ImageSearchResponse(query=body.query, count=len(results),
                               latency_ms=latency_ms, results=results)
