from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import PriceCatalog, PriceHistory

def get_current_prices(db: Session, material_codes: list[str], variant: str = "PADRAO", company_id: int | None = None) -> dict[str, Decimal]:
    rows=db.execute(select(PriceCatalog).where(
        PriceCatalog.material_code.in_(material_codes),
        PriceCatalog.variant == variant,
        PriceCatalog.active == "ATIVO",
        *([PriceCatalog.company_id == company_id] if company_id is not None else [])
    ).order_by(PriceCatalog.id.desc())).scalars().all()
    result = {}
    for row in rows:
        result.setdefault(row.material_code, Decimal(row.price))
    return result

def set_price(db: Session, material_code: str, description: str, unit: str,
              price: Decimal, supplier: str | None = None,
              variant: str = "PADRAO", company_id: int | None = None) -> PriceCatalog:
    previous=db.execute(select(PriceCatalog).where(
        PriceCatalog.material_code==material_code,
        PriceCatalog.variant==variant,
        PriceCatalog.active=="ATIVO",
        *([PriceCatalog.company_id == company_id] if company_id is not None else [])
    )).scalars().all()
    for row in previous: row.active="INATIVO"
    current=PriceCatalog(company_id=company_id,material_code=material_code,description=description,
        variant=variant,unit=unit,price=price,supplier=supplier,active="ATIVO")
    db.add(current)
    db.add(PriceHistory(company_id=company_id,material_code=material_code,variant=variant,price=price,
        unit=unit,supplier=supplier,source="CADASTRO"))
    db.commit(); db.refresh(current)
    return current
