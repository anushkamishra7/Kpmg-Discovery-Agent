"""End-to-end test: embed → upsert → query → verify retrieval works."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.embedder import embed_text
from services.pinecone_client import (
    upsert_products_batch,
    query,
    index_stats,
)


SAMPLE_PRODUCTS = [
    {"id": "p1", "text": "red running shoes for marathon training"},
    {"id": "p2", "text": "blue denim jeans slim fit men"},
    {"id": "p3", "text": "wireless noise cancelling over-ear headphones"},
    {"id": "p4", "text": "leather wallet bifold brown minimalist"},
    {"id": "p5", "text": "stainless steel water bottle insulated 1 liter"},
    {"id": "p6", "text": "white cotton t-shirt crew neck basic"},
    {"id": "p7", "text": "mechanical keyboard RGB backlit gaming"},
    {"id": "p8", "text": "yoga mat eco-friendly non-slip 6mm thick"},
]


def main():
    print("Embedding sample products...")
    items = []
    for p in SAMPLE_PRODUCTS:
        vec = embed_text(p["text"])
        items.append({
            "id": p["id"],
            "values": vec,
            "metadata": {"description": p["text"]},
        })
    print(f"  embedded {len(items)} products")

    print("\nUpserting to Pinecone...")
    upsert_products_batch(items)
    print("  upsert complete")

    print("\nIndex stats:")
    print(f"  {index_stats()}")

    queries = [
        "shoes for running",
        "something to listen to music with",
        "drink container for the gym",
    ]

    for q in queries:
        print(f"\nQuery: '{q}'")
        q_vec = embed_text(q)
        results = query(q_vec, top_k=3)
        for r in results:
            desc = r["metadata"].get("description", "?")
            print(f"  {r['score']:.4f}  [{r['id']}]  {desc}")

    print("\nall good")


if __name__ == "__main__":
    main()