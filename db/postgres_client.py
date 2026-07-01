import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    register_vector(conn)
    return conn

def upsert_embedding(asset_id, asset_path, asset_url, embedding, metadata=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO asset_embeddings (asset_id, asset_path, asset_url, embedding, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (asset_id) DO UPDATE SET
                asset_path = EXCLUDED.asset_path,
                asset_url  = EXCLUDED.asset_url,
                embedding  = EXCLUDED.embedding,
                metadata   = EXCLUDED.metadata,
                updated_at = NOW()
        """, (asset_id, asset_path, asset_url, embedding, psycopg2.extras.Json(metadata or {})))
        conn.commit()
    finally:
        conn.close()

def search_similar(query_vector, top_k=10):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT asset_id, asset_path, asset_url, metadata,
                   1 - (embedding <=> %s::vector) AS score
            FROM asset_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_vector, query_vector, top_k))
        return cur.fetchall()
    finally:
        conn.close()

def get_stats():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM asset_embeddings")
        total = cur.fetchone()[0]
        return {"total_indexed": total}
    finally:
        conn.close()
