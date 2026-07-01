import os
import httpx
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import services.embedder as embedder
from agents.queue_manager import get_pending, mark_done, mark_failed, get_stats
from services.pinecone_client import upsert_product

load_dotenv()

AEM_BASE = os.getenv("AEM_BASE_URL", "http://13.127.20.49:4503")
BEARER = os.getenv("AEM_BEARER_TOKEN", "")
N_WORKERS = int(os.getenv("N_WORKERS", 4))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))

def _process_one(item):
    asset_id, asset_url, asset_path = item
    try:
        with httpx.Client(headers={"Authorization": f"Bearer {BEARER}"}, follow_redirects=True, timeout=20) as client:
            r = client.get(asset_url)
            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code}")
            img = Image.open(BytesIO(r.content)).convert("RGB")

        vector = embedder.embed_image(img)
        filename = asset_path.split("/")[-1]
        metadata = {"filename": filename, "aem_path": asset_path, "asset_url": asset_url, "client": "asian-paints"}
        upsert_product(asset_id, vector, metadata)
        mark_done(asset_id)
        return True, asset_id
    except Exception as e:
        mark_failed(asset_id, e)
        return False, f"{asset_id}: {e}"

def run_workers():
    print("Starting embed workers...")
    total_done = 0
    total_failed = 0

    while True:
        batch = get_pending(BATCH_SIZE)
        if not batch:
            break

        with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
            results = list(pool.map(_process_one, batch))

        for ok, info in results:
            if ok:
                total_done += 1
            else:
                total_failed += 1
                print(f"  FAILED: {info}")

        stats = get_stats()
        print(f"Progress — done: {stats['done']} / total: {stats['total']} | failed: {stats['failed']}")

    print(f"Workers finished. Done: {total_done} | Failed: {total_failed}")
    return {"done": total_done, "failed": total_failed}
