"""Restore a PostgreSQL custom-format backup.
Usage: DATABASE_URL=postgresql://... python scripts/restore_postgres.py backup.dump
Refuses to run unless RESTORE_CONFIRM=YES is explicitly set.
"""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

def main() -> int:
    if os.getenv("RESTORE_CONFIRM") != "YES":
        print("Restauração bloqueada: defina RESTORE_CONFIRM=YES explicitamente.", file=sys.stderr); return 2
    url = os.getenv("DATABASE_URL", "")
    if not url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
        print("DATABASE_URL deve apontar para PostgreSQL.", file=sys.stderr); return 2
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        print("Informe um arquivo .dump existente.", file=sys.stderr); return 2
    dump_url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    cmd = ["pg_restore", "--clean", "--if-exists", "--no-owner", "--dbname", dump_url, sys.argv[1]]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("pg_restore não encontrado no PATH.", file=sys.stderr); return 3
    except subprocess.CalledProcessError as exc:
        print(f"pg_restore falhou com código {exc.returncode}.", file=sys.stderr); return exc.returncode or 4
    print("Restauração concluída.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
