from decimal import Decimal
from app.db import Base, engine, SessionLocal
from app.models.security_entities import Company, User
from app.models.entities import PriceCatalog
from app.models.audit_entities import AuditEvent
from app.services.pricing import get_current_prices


def setup_module():
    Base.metadata.create_all(bind=engine)


def test_current_price_lookup_is_deterministic_when_legacy_duplicates_exist():
    db = SessionLocal()
    try:
        c = Company(name="Price Determinism")
        db.add(c); db.flush()
        db.add_all([
            PriceCatalog(company_id=c.id, material_code="DUP", description="old", variant="PADRAO", unit="UN", price=Decimal("10"), active="ATIVO"),
            PriceCatalog(company_id=c.id, material_code="DUP", description="new", variant="PADRAO", unit="UN", price=Decimal("20"), active="ATIVO"),
        ])
        db.commit()
        assert get_current_prices(db, ["DUP"], "PADRAO", c.id)["DUP"] == Decimal("20")
    finally:
        db.close()
