from __future__ import annotations
import os

class RuntimeConfigError(ValueError):
    pass

def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

def is_production() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() in {"production", "prod"}

def validate_runtime_config() -> None:
    if not is_production():
        return
    required = ["DATABASE_URL", "APP_SECRET_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeConfigError("Configuração de produção incompleta: " + ", ".join(missing))
    if env_bool("AUTO_CREATE_SCHEMA", False):
        raise RuntimeConfigError("AUTO_CREATE_SCHEMA deve ser false em produção; use migrations.")
    database_url = os.getenv("DATABASE_URL", "").lower()
    if database_url.startswith("sqlite"):
        raise RuntimeConfigError("SQLite não é permitido em produção; use PostgreSQL.")
    cors = [x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()]
    if any("localhost" in x or "127.0.0.1" in x for x in cors):
        raise RuntimeConfigError("CORS de desenvolvimento não é permitido em produção.")
    if os.getenv("APP_SECRET_KEY", "").strip() in {"change-me", "test-secret-etapa-44", "esquadrias_dev_change_me"}:
        raise RuntimeConfigError("APP_SECRET_KEY insegura para produção.")
