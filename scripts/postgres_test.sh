#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker não encontrado. Instale Docker/Compose para executar PostgreSQL local."
  exit 2
fi

export POSTGRES_DB="${POSTGRES_DB:-esquadrias}"
export POSTGRES_USER="${POSTGRES_USER:-esquadrias}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-esquadrias_dev_change_me}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}}"

cleanup() { docker compose down >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker compose up -d postgres
python scripts/wait_postgres.py
python scripts/migrate.py
PYTHONPATH=. pytest -q -m postgres
