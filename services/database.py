"""
SQLite database for storing scraped IndiGo campaign data.
"""
import os
from pathlib import Path
from datetime import datetime

from sqlite_utils import Database

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campaigns.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db() -> Database:
    return Database(DB_PATH)


def init_db() -> None:
    db = get_db()
    if "campaigns" not in db.table_names():
        db["campaigns"].create({
            "id": str,
            "name": str,
            "url": str,
            "offer_text": str,
            "promo_codes": str,
            "scraped_at": str,
            "embedded": int,
        }, pk="id")
        print("  created campaigns table")
    else:
        print("  campaigns table already exists")


def upsert_campaign(campaign: dict) -> None:
    db = get_db()
    campaign["scraped_at"] = datetime.utcnow().isoformat()
    campaign["embedded"] = 0
    db["campaigns"].upsert(campaign, pk="id")


def get_unembedded() -> list[dict]:
    db = get_db()
    return list(db["campaigns"].rows_where("embedded = 0"))


def mark_embedded(campaign_id: str) -> None:
    db = get_db()
    db["campaigns"].update(campaign_id, {"embedded": 1})


def all_campaigns() -> list[dict]:
    db = get_db()
    return list(db["campaigns"].rows)


def campaign_count() -> int:
    db = get_db()
    if "campaigns" not in db.table_names():
        return 0
    return db["campaigns"].count