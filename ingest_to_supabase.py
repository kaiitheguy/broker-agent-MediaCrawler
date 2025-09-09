import os
import sqlite3
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SQLITE_PATH = os.getenv("XHS_SQLITE_PATH", "schema/sqlite_tables.db")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Need SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
conn = sqlite3.connect(SQLITE_PATH)
cur = conn.cursor()

rows = cur.execute("""
    SELECT note_id, title, desc, liked_count, collected_count, comment_count,
           share_count, ip_location, source_keyword, note_url, time
    FROM xhs_note
    ORDER BY time DESC
    LIMIT 200
""").fetchall()

print(f"Read {len(rows)} rows from {SQLITE_PATH}")

payload = []
for r in rows:
    payload.append({
        "note_id": r[0],
        "title": r[1],
        "desc": r[2],
        "liked_count": int(r[3]) if r[3] else 0,
        "collected_count": int(r[4]) if r[4] else 0,
        "comment_count": int(r[5]) if r[5] else 0,
        "share_count": int(r[6]) if r[6] else 0,
        "ip_location": r[7],
        "source_keyword": r[8],
        "note_url": r[9],
        "time": int(r[10]) if r[10] else None,
    })

if payload:
    resp = supabase.table("xhs_items").upsert(payload, on_conflict="note_id").execute()
    print(f"Upserted {len(payload)} rows to Supabase")
else:
    print("No rows to ingest")
