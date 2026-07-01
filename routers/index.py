from fastapi import APIRouter, HTTPException, Request
from models.schemas import CampaignIndexRequest, CampaignIndexResponse

router = APIRouter(prefix="/index", tags=["Indexing"])

@router.post("", response_model=CampaignIndexResponse)
async def index_campaign(body: CampaignIndexRequest, request: Request):
    embedder = request.app.state.embedder
    pc_client = request.app.state.pinecone_client
    text_to_embed = f"{body.title}. {body.description}"
    try:
        vector = embedder.embed_text(text_to_embed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    metadata = {k: v for k, v in {
        "title": body.title, "description": body.description,
        "category": body.category, "url": body.url, "image_url": body.image_url,
    }.items() if v is not None}
    try:
        pc_client.upsert(vectors=[{"id": body.id, "values": vector, "metadata": metadata}])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone upsert failed: {str(e)}")
    return CampaignIndexResponse(success=True, campaign_id=body.id,
                                  message=f"Campaign indexed successfully.")
