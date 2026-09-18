from decimal import Decimal
import pytest
from app.services.price_formation import form_price


def test_margin_formula_with_tax():
    r = form_price(
        Decimal("100"),
        tax_percent=Decimal("10"),
        margin_percent=Decimal("20"),
    )
    assert r["sale_price"] == Decimal("142.86")
    assert r["profit"] == Decimal("28.57")
    assert r["effective_margin_percent"] == Decimal("20.00")


def test_markup_formula_with_tax():
    r = form_price(
        Decimal("100"),
        tax_percent=Decimal("10"),
        markup_percent=Decimal("30"),
    )
    assert r["sale_price"] == Decimal("144.44")
    assert r["profit"] == Decimal("30.00")
    assert r["effective_markup_percent"] == Decimal("30.00")


def test_labor_indirect_fixed_and_freight():
    r = form_price(
        Decimal("100"),
        labor_total=Decimal("20"),
        indirect_percent=Decimal("10"),
        indirect_fixed=Decimal("5"),
        freight=Decimal("10"),
    )
    assert r["base_cost"] == Decimal("147.00")
    assert r["sale_price"] == Decimal("147.00")


def test_margin_and_markup_cannot_be_used_together():
    with pytest.raises(ValueError):
        form_price(Decimal("100"), margin_percent=Decimal("20"), markup_percent=Decimal("20"))


def test_margin_denominator_guard():
    with pytest.raises(ValueError):
        form_price(Decimal("100"), tax_percent=Decimal("50"), margin_percent=Decimal("50"))


def test_zero_rates():
    r = form_price(Decimal("250"))
    assert r["sale_price"] == Decimal("250.00")
    assert r["profit"] == Decimal("0.00")
