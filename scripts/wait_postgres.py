"""Wait for the configured PostgreSQL database to accept connections."""
from __future__ import annotations
import os
import time
import psycopg

url = os.getenv("DATABASE_URL", "")
if not url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
    raise SystemExit("DATABASE_URL deve apontar para PostgreSQL.")
url = url.replace("postgresql+psycopg://", "postgresql://", 1)
last = None
for _ in range(30):
    try:
        with psycopg.connect(url, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        print("PostgreSQL disponível.")
        raise SystemExit(0)
    except Exception as exc:
        last = exc
        time.sleep(1)
raise SystemExit(f"PostgreSQL não ficou disponível: {last}")
