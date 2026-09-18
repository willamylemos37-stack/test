from decimal import Decimal
import pytest
from app.services.transactional_flow import *
def test_all_or_nothing_plan():
    with pytest.raises(TransactionFlowError):
        build_atomic_plan([(1,Decimal("2")),(2,Decimal("2"))],{1:Decimal("2"),2:Decimal("1")})
def test_plan_success():
    p=build_atomic_plan([(1,Decimal("2"))],{1:Decimal("3")})
    assert p[0].quantity==Decimal("2")
def test_company_isolation():
    require_same_company(5,5)
    with pytest.raises(TransactionFlowError): require_same_company(5,6)
