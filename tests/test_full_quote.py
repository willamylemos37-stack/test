from decimal import Decimal
from app.services.price_formation import form_price

def test_full_quote_price_layer():
    r=form_price(Decimal("100"),labor_total=Decimal("20"),tax_percent=Decimal("10"),margin_percent=Decimal("20"))
    assert r["sale_price"] == Decimal("171.43")

def test_markup_layer():
    r=form_price(Decimal("100"),tax_percent=Decimal("10"),markup_percent=Decimal("30"))
    assert r["sale_price"] == Decimal("144.44")
