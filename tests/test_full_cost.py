from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models.entities import PriceCatalog
from app.services.calculator import calculate_model_001
from app.services.costing import calculate_full_cost

def session():
    e=create_engine("sqlite:///:memory:",future=True)
    Base.metadata.create_all(e)
    return sessionmaker(bind=e,future=True)()

def test_full_cost_flags_missing_prices():
    db=session()
    r=calculate_full_cost(db,calculate_model_001(1003,1000,1))
    assert r["status"]=="PRECO_INCOMPLETO"
    assert "VIDRO" in r["missing_prices"]
    db.close()

def test_full_cost_with_zero_prices_is_complete_when_all_registered():
    db=session()
    for code in ["MP-357","MP-358","MP-360","MP-300","MP-302","MP-321","MP-309","BG-202"]:
        for variant in ["BARRA_3000","BARRA_6000"]:
            db.add(PriceCatalog(material_code=code,description=code,variant=variant,unit="barra",price=Decimal("0"),active="ATIVO"))
    db.add(PriceCatalog(material_code="VIDRO",description="Vidro",variant="M2",unit="m2",price=Decimal("0"),active="ATIVO"))
    for code in ["ROLDANA","FECHO","GUIA_TRAVA","PARAFUSO","CALCO"]:
        db.add(PriceCatalog(material_code=code,description=code,variant="UNIDADE",unit="un",price=Decimal("0"),active="ATIVO"))
    for code in ["ESCOVA_5MM","ESCOVA_7MM","BORRACHA_VEDACAO"]:
        db.add(PriceCatalog(material_code=code,description=code,variant="METRO",unit="m",price=Decimal("0"),active="ATIVO"))
    db.add(PriceCatalog(material_code="SILICONE_SELANTE",description="Silicone",variant="UNIDADE",unit="un",price=Decimal("0"),active="ATIVO"))
    db.commit()
    r=calculate_full_cost(db,calculate_model_001(1003,1000,1))
    assert r["status"]=="CUSTO_COMPLETO"
    assert r["total_cost"]==Decimal("0")
    db.close()


def test_full_cost_exposes_price_snapshots_when_prices_exist():
    db=session()
    for code in ["MP-357","MP-358","MP-360","MP-300","MP-302","MP-321","MP-309","BG-202"]:
        db.add(PriceCatalog(material_code=code,description=code,variant="BARRA_3000",unit="barra",price=Decimal("10"),active="ATIVO"))
        db.add(PriceCatalog(material_code=code,description=code,variant="BARRA_6000",unit="barra",price=Decimal("20"),active="ATIVO"))
    db.add(PriceCatalog(material_code="VIDRO",description="Vidro",variant="M2",unit="m2",price=Decimal("30"),active="ATIVO"))
    for code in ["ROLDANA","FECHO","GUIA_TRAVA","PARAFUSO","CALCO"]:
        db.add(PriceCatalog(material_code=code,description=code,variant="UNIDADE",unit="un",price=Decimal("1"),active="ATIVO"))
    for code in ["ESCOVA_5MM","ESCOVA_7MM","BORRACHA_VEDACAO"]:
        db.add(PriceCatalog(material_code=code,description=code,variant="METRO",unit="m",price=Decimal("1"),active="ATIVO"))
    db.add(PriceCatalog(material_code="SILICONE_SELANTE",description="Silicone",variant="UNIDADE",unit="un",price=Decimal("1"),active="ATIVO"))
    db.commit()
    r=calculate_full_cost(db,calculate_model_001(1003,1000,1))
    assert r["status"]=="CUSTO_COMPLETO"
    assert r["price_snapshots"]
    db.close()
