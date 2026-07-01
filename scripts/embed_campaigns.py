"""
Embed scraped campaigns into Pinecone.
Reads unembedded campaigns from SQLite, embeds with CLIP, upserts to Pinecone.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.database import get_unembedded, mark_embedded
from services.embedder import embed_text
from services.pinecone_client import upsert_product


def build_embed_text(campaign: dict) -> str:
    """
    Combine campaign fields into a single string for embedding.
    More context = better semantic matching.
    """
    parts = [
        campaign.get("name", ""),
        campaign.get("offer_text", "")[:500],  # first 500 chars of offer
        campaign.get("promo_codes", ""),
    ]
    return " | ".join(p for p in parts if p)


def main():
    campaigns = get_unembedded()
    print(f"Found {len(campaigns)} unembedded campaigns")

    if not campaigns:
        print("Nothing to embed. Run scripts/scrape_campaigns.py first.")
        return

    for i, campaign in enumerate(campaigns):
        print(f"[{i+1}/{len(campaigns)}] Embedding: {campaign['name'][:60]}")
        text = build_embed_text(campaign)
        vector = embed_text(text)

        upsert_product(
            product_id=campaign["id"],
            vector=vector,
            metadata={
                "name": campaign["name"],
                "url": campaign["url"],
                "promo_codes": campaign.get("promo_codes", ""),
                "offer_preview": campaign.get("offer_text", "")[:200],
            }
        )
        mark_embedded(campaign["id"])
        print(f"  embedded and upserted")

    print(f"\nDone. {len(campaigns)} campaigns now searchable in Pinecone.")


if __name__ == "__main__":
    main()