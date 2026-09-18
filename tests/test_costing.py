from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models.entities import PriceCatalog
from app.services.calculator import calculate_model_001
from app.services.costing import calculate_cost

def test_cost_uses_registered_prices():
    engine=create_engine("sqlite:///:memory:",future=True)
    Base.metadata.create_all(engine)
    Session=sessionmaker(bind=engine,future=True)
    with Session() as db:
        db.add(PriceCatalog(material_code="MP-357", description="Marco", unit="barra", price=Decimal("100"), active="ATIVO"))
        db.commit()
        result=calculate_cost(db,calculate_model_001(1003,1000,1))
        assert result["cost_aluminum"] == Decimal("100")
        assert "MP-357" not in result["missing_prices"]

def test_cost_reports_missing_prices():
    engine=create_engine("sqlite:///:memory:",future=True)
    Base.metadata.create_all(engine)
    Session=sessionmaker(bind=engine,future=True)
    with Session() as db:
        result=calculate_cost(db,calculate_model_001(1003,1000,1))
        assert result["total_cost"] == Decimal("0")
        assert result["status"] == "PRECO_INCOMPLETO"
        assert len(result["missing_prices"]) > 0
