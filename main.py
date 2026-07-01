from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search, index, image_search
import services.embedder as embedder_module
import services.pinecone_client as pc_module

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.embedder = embedder_module
    app.state.pinecone_client = pc_module
    try:
        embedder_module.embed_text("warmup")
    except Exception:
        pass
    yield

app = FastAPI(title="KPMG Discoverability Agent", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(search.router)
app.include_router(index.router)
app.include_router(image_search.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "KPMG Discoverability Agent", "docs": "/docs"}

@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
async def search_ui():
    index_path = os.path.join(os.path.dirname(__file__), "frontend", "dist", "index.html")
    with open(index_path) as f:
        return f.read()

app.mount("/assets", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend", "dist", "assets")), name="assets")
app.mount("/models", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend", "dist", "models")), name="models")

import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
load_dotenv()

@app.get("/proxy-image")
async def proxy_image(url: str):
    token = os.getenv("AEM_BEARER_TOKEN")
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
        return StreamingResponse(
            iter([r.content]),
            media_type=r.headers.get("content-type", "image/png")
        )
