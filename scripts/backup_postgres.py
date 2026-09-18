"""Create a PostgreSQL backup for the Esquadrias API.
Usage: DATABASE_URL=postgresql://... python scripts/backup_postgres.py [output.dump]
"""
from __future__ import annotations
import os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

def main() -> int:
    url = os.getenv("DATABASE_URL", "")
    if not url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
        print("DATABASE_URL deve apontar para PostgreSQL.", file=sys.stderr); return 2
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("backups") / f"esquadrias_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.dump"
    out.parent.mkdir(parents=True, exist_ok=True)
    # pg_dump does not understand SQLAlchemy's +psycopg scheme.
    dump_url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    cmd = ["pg_dump", "--format=custom", "--no-owner", "--file", str(out), dump_url]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("pg_dump não encontrado no PATH.", file=sys.stderr); return 3
    except subprocess.CalledProcessError as exc:
        print(f"pg_dump falhou com código {exc.returncode}.", file=sys.stderr); return exc.returncode or 4
    print(out)
    return 0

if __name__ == "__main__": raise SystemExit(main())
