from decimal import Decimal
import pytest
from app.services.reservations import *
def test_access():
    with pytest.raises(ReservationError): validate_company_access(1,2)
def test_available():
    ensure_quantity_available(Decimal("3"),Decimal("2"))
    with pytest.raises(ReservationError): ensure_quantity_available(Decimal("1"),Decimal("2"))
def test_transition():
    validate_transition("ATIVA","CONSUMIDA")
    with pytest.raises(ReservationError): validate_transition("CONSUMIDA","ATIVA")
def test_positive():
    with pytest.raises(ReservationError): ensure_quantity_available(Decimal("5"),Decimal("0"))
