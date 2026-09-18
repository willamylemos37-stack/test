import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./esquadrias_dev.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

AUTO_CREATE_SCHEMA = os.getenv("AUTO_CREATE_SCHEMA", "true").lower() == "true"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_dev_schema():
    """Apply additive SQLite dev-only columns when an old local DB predates a model change."""
    if not AUTO_CREATE_SCHEMA or not DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    with engine.begin() as conn:
        if "catalogo_precos" in insp.get_table_names():
            cols={c["name"] for c in inspect(conn).get_columns("catalogo_precos")}
            if "company_id" not in cols:
                conn.execute(text("ALTER TABLE catalogo_precos ADD COLUMN company_id INTEGER"))
        if "historico_precos" in insp.get_table_names():
            cols={c["name"] for c in inspect(conn).get_columns("historico_precos")}
            if "company_id" not in cols:
                conn.execute(text("ALTER TABLE historico_precos ADD COLUMN company_id INTEGER"))
        if "orcamentos" in insp.get_table_names():
            cols={c["name"] for c in inspect(conn).get_columns("orcamentos")}
            if "company_id" not in cols:
                conn.execute(text("ALTER TABLE orcamentos ADD COLUMN company_id INTEGER"))
        if "estoque_itens" in insp.get_table_names():
            cols={c["name"] for c in inspect(conn).get_columns("estoque_itens")}
            if "reserved_quantity" not in cols:
                conn.execute(text("ALTER TABLE estoque_itens ADD COLUMN reserved_quantity NUMERIC(14,3) NOT NULL DEFAULT 0"))
        if "ordens_producao" in insp.get_table_names():
            cols={c["name"] for c in inspect(conn).get_columns("ordens_producao")}
            if "reservation_id" not in cols:
                conn.execute(text("ALTER TABLE ordens_producao ADD COLUMN reservation_id INTEGER"))
