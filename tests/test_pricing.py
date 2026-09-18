from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.services.pricing import set_price, get_current_prices

def test_price_history_and_current_price():
    engine=create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session=sessionmaker(bind=engine, future=True)
    with Session() as db:
        set_price(db,"MP-357","Marco superior","barra",Decimal("0"),"TESTE")
        assert get_current_prices(db,["MP-357"])["MP-357"] == Decimal("0")
        set_price(db,"MP-357","Marco superior","barra",Decimal("123.45"),"TESTE")
        assert get_current_prices(db,["MP-357"])["MP-357"] == Decimal("123.45")
