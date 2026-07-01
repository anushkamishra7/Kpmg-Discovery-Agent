"""
AEM Crawler — KPMG Discoverability Agent
Client: Asian Paints
Source: AEM as a Cloud Service (Bearer token auth)
DAM path: /content/dam/eds-asian-paints
"""
import os
import httpx
from dotenv import load_dotenv
from agents.queue_manager import init_queue, enqueue, get_stats

load_dotenv()

AEM_BASE    = os.getenv("AEM_BASE_URL", "https://author-p110016-e1074395.adobeaemcloud.com")
AEM_PATH    = os.getenv("AEM_DAM_PATH", "/content/dam/eds-asian-paints")
BEARER      = os.getenv("AEM_BEARER_TOKEN", "")
CLIENT      = os.getenv("CLIENT", "asian-paints")

SUPPORTED   = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg",
               ".mp4", ".mov", ".pdf"}

def _headers():
    return {"Authorization": f"Bearer {BEARER}", "Accept": "application/json"}

def _asset_type(name: str) -> str:
    ext = os.path.splitext(name)[1].lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}:
        return "image"
    if ext in {".mp4", ".mov"}:
        return "video"
    if ext == ".pdf":
        return "pdf"
    return "other"

def _is_supported(name: str) -> bool:
    return os.path.splitext(name)[1].lower() in SUPPORTED

def _crawl_node(folder_path: str, client: httpx.Client, depth: int = 0):
    """Recursively crawl using AEM Assets HTTP API."""
    if depth > 10:
        return

    # AEM Assets HTTP API endpoint for folder listing
    api_path = folder_path.replace("/content/dam/", "")
    url = f"{AEM_BASE}/api/assets/{api_path}.json"

    try:
        r = client.get(url, headers=_headers(), timeout=20)
        if r.status_code != 200:
            print(f"  ⚠️  {r.status_code} at {url}")
            return
        data = r.json()
    except Exception as e:
        print(f"  crawl error {folder_path}: {e}")
        return

    entities = data.get("entities", [])
    for entity in entities:
        props = entity.get("properties", {})
        name  = props.get("name", entity.get("name", ""))
        cls   = entity.get("class", [])

        if "assets/folder" in cls or "assets/collection" in cls:
            _crawl_node(f"{folder_path}/{name}", client, depth + 1)

        elif "assets/asset" in cls and _is_supported(name):
            asset_path = f"{folder_path}/{name}"
            asset_url  = f"{AEM_BASE}/content/dam/{api_path}/{name}"
            metadata   = {
                "title":       props.get("dc:title", ""),
                "description": props.get("dc:description", ""),
                "alt_text":    props.get("dc:altText", ""),
                "campaign":    props.get("dam:campaignName", ""),
                "tags":        str(props.get("cq:tags", [])),
                "created_at":  props.get("jcr:created", ""),
                "modified_at": props.get("jcr:lastModified", ""),
                "asset_type":  _asset_type(name),
                "client":      CLIENT,
            }
            enqueue(asset_path, asset_url, asset_path)
            print(f"  ✅ {_asset_type(name).upper()}: {name}")

def crawl():
    if not BEARER:
        print("❌ AEM_BEARER_TOKEN is not set in .env")
        print("   Grab it from browser DevTools → Network tab → Authorization header")
        return

    init_queue()
    print(f"🚀 KPMG Discoverability Agent — AEM Crawler")
    print(f"   Client : {CLIENT}")
    print(f"   Source : {AEM_BASE}{AEM_PATH}")
    print()

    with httpx.Client(follow_redirects=True) as client:
        _crawl_node(AEM_PATH, client)

    stats = get_stats()
    print(f"\n✅ Crawl complete. Queue stats: {stats}")
    return stats
