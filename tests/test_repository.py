from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models.entities import Quote
from app.repositories.quote_repository import QuoteRepository
from app.services.calculator import calculate_model_001

def test_repository_create_get():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    with Session() as db:
        result = calculate_model_001(1003,1000,2)
        quote = Quote(code="TEST-001", model_code="MOD-001", width_mm=1000,
                      height_mm=1000, quantity=2, status="RASCUNHO")
        repo = QuoteRepository(db)
        repo.add_calculated_items(quote, result)
        saved = repo.create(quote)
        loaded = repo.get(saved.id)
        assert loaded is not None
        assert loaded.code == "TEST-001"
        assert len(loaded.items) == len(result.parts)
        assert len(loaded.snapshots) == len(result.rule_snapshots)
