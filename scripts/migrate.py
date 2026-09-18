"""Simple transactional PostgreSQL migration runner for the Esquadrias project."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import psycopg


def psycopg_url(url: str) -> str:
    return url.replace("postgresql+psycopg://", "postgresql://", 1)

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "migrations"

def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def is_new_schema_without_legacy_columns(conn) -> bool:
    rows = conn.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'modelos'
          AND column_name IN ('code', 'codigo')
        """
    ).fetchall()
    columns = {row[0] for row in rows}
    return 'code' in columns and 'codigo' not in columns

def main() -> None:
    url = os.getenv("DATABASE_URL")
    if not url or not url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
        raise SystemExit("DATABASE_URL deve apontar para PostgreSQL.")
    url = psycopg_url(url)
    files = sorted(MIGRATIONS.glob("*.sql"))
    if not files:
        raise SystemExit("Nenhuma migração encontrada.")
    with psycopg.connect(url) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(100) PRIMARY KEY,
                checksum VARCHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        rows = dict(conn.execute("SELECT version, checksum FROM schema_migrations").fetchall())
        for path in files:
            version = path.name
            digest = checksum(path)
            if version in rows:
                if rows[version] != digest:
                    raise SystemExit(f"Checksum divergente para migração já aplicada: {version}")
                print(f"OK {version} (já aplicada)")
                continue
            if version == "0002_upgrade_legacy_v4_6_to_v5_15.sql" and is_new_schema_without_legacy_columns(conn):
                with conn.transaction():
                    conn.execute(
                        "INSERT INTO schema_migrations(version, checksum) VALUES (%s, %s)",
                        (version, digest),
                    )
                print(f"IGNORADA {version} (banco novo; migration legada não necessária)")
                continue

            print(f"APLICANDO {version}")
            sql = path.read_text(encoding="utf-8")
            with conn.transaction():
                conn.execute(sql)
                conn.execute(
                    "INSERT INTO schema_migrations(version, checksum) VALUES (%s, %s)",
                    (version, digest),
                )
            print(f"OK {version}")

if __name__ == "__main__":
    main()
