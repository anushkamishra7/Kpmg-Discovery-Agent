"""
Pinecone client wrapper.
Handles index connection, upsert, and query for the discovery agent.
"""
import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX", "discovery-agent")
PINECONE_NAMESPACE  = os.getenv("PINECONE_NAMESPACE", "asian-paints")

if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY not set in .env")


@lru_cache(maxsize=1)
def _client() -> Pinecone:
    """Singleton Pinecone client."""
    return Pinecone(api_key=PINECONE_API_KEY)


@lru_cache(maxsize=1)
def _index():
    """Singleton handle to the discovery-agent index."""
    return _client().Index(PINECONE_INDEX_NAME)


def upsert_product(
    product_id: str,
    vector: list[float],
    metadata: Optional[dict] = None,
) -> None:
    """Insert or update a single product vector with metadata."""
    _index().upsert(
        vectors=[
            {
                "id": product_id,
                "values": vector,
                "metadata": metadata or {},
            }
        ],
        namespace=PINECONE_NAMESPACE,
    )


def upsert_products_batch(items: list[dict]) -> None:
    """
    Bulk upsert. Each item must have keys: id, values, metadata (optional).
    Use this for seeding the index from a catalog.
    """
    _index().upsert(vectors=items, namespace=PINECONE_NAMESPACE)


def query(
    vector: list[float],
    top_k: int = 5,
    filter: Optional[dict] = None,
) -> list[dict]:
    """
    Query the index with a vector. Returns top-k matches with metadata.
    Optionally filter on metadata fields (e.g. {"category": "shoes"}).
    """
    response = _index().query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter,
        namespace=PINECONE_NAMESPACE,
    )
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match.get("metadata", {}),
        }
        for match in response["matches"]
    ]


def index_stats() -> dict:
    """Return current index stats (vector count, dimensions, etc.)."""
    stats = _index().describe_index_stats()
    return {
        "total_vector_count": stats.get("total_vector_count", 0),
        "dimension": stats.get("dimension"),
        "namespaces": dict(stats.get("namespaces", {})),
    }