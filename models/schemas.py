from pydantic import BaseModel, Field
from typing import Optional

class CampaignIndexRequest(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    category: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None

class CampaignIndexResponse(BaseModel):
    success: bool
    campaign_id: str
    message: str

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)

class CampaignResult(BaseModel):
    id: str
    score: float
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    top_k: int
    count: int
    latency_ms: float
    results: list[CampaignResult]
