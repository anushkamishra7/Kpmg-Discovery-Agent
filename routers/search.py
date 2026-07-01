import time
from fastapi import APIRouter, HTTPException, Request
from models.schemas import SearchRequest, SearchResponse, CampaignResult

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
async def search_campaigns(body: SearchRequest, request: Request):
    embedder = request.app.state.embedder
    pc_client = request.app.state.pinecone_client
    t0 = time.perf_counter()
    try:
        query_vector = embedder.embed_text(body.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    try:
        raw_results = pc_client.query(vector=query_vector, top_k=body.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone query failed: {str(e)}")
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    results = []
    for match in raw_results:
        score = match.get("score", 0.0)
        if score < body.score_threshold:
            continue
        meta = match.get("metadata", {})
        results.append(CampaignResult(
            id=match["id"], score=round(score, 4),
            title=meta.get("title"), description=meta.get("description"),
            category=meta.get("category"), url=meta.get("url"),
            image_url=meta.get("image_url"),
        ))
    return SearchResponse(query=body.query, top_k=body.top_k,
                          count=len(results), latency_ms=latency_ms, results=results)
