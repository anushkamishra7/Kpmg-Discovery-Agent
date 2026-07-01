import sqlite3
import os
from datetime import datetime

QUEUE_DB = os.path.join(os.path.dirname(__file__), "..", "aem_queue.db")

def init_queue():
    conn = sqlite3.connect(QUEUE_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id   TEXT UNIQUE NOT NULL,
            asset_url  TEXT NOT NULL,
            asset_path TEXT NOT NULL,
            status     TEXT DEFAULT 'pending',
            error      TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def enqueue(asset_id, asset_url, asset_path):
    conn = sqlite3.connect(QUEUE_DB)
    try:
        conn.execute("""
            INSERT OR IGNORE INTO queue (asset_id, asset_url, asset_path, status)
            VALUES (?, ?, ?, 'pending')
        """, (asset_id, asset_url, asset_path))
        conn.commit()
    finally:
        conn.close()

def get_pending(limit=10):
    conn = sqlite3.connect(QUEUE_DB)
    try:
        cur = conn.execute(
            "SELECT asset_id, asset_url, asset_path FROM queue WHERE status='pending' LIMIT ?",
            (limit,)
        )
        return cur.fetchall()
    finally:
        conn.close()

def mark_done(asset_id):
    conn = sqlite3.connect(QUEUE_DB)
    conn.execute(
        "UPDATE queue SET status='done', updated_at=? WHERE asset_id=?",
        (datetime.now().isoformat(), asset_id)
    )
    conn.commit()
    conn.close()

def mark_failed(asset_id, error):
    conn = sqlite3.connect(QUEUE_DB)
    conn.execute(
        "UPDATE queue SET status='failed', error=?, updated_at=? WHERE asset_id=?",
        (str(error)[:500], datetime.now().isoformat(), asset_id)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(QUEUE_DB)
    cur = conn.execute("SELECT status, COUNT(*) FROM queue GROUP BY status")
    stats = dict(cur.fetchall())
    conn.close()
    return {
        "total":   sum(stats.values()),
        "pending": stats.get("pending", 0),
        "done":    stats.get("done", 0),
        "failed":  stats.get("failed", 0),
    }
