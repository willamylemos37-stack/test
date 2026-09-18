from decimal import Decimal
import pytest
from app.services.workflow import *
from app.services.inventory_transaction import plan_atomic_reservation
def test_approval_only_sent():
    assert approve_quote("ENVIADO")=="APROVADO"
    with pytest.raises(WorkflowError): approve_quote("RASCUNHO")
def test_atomic_shortage():
    with pytest.raises(WorkflowError): plan_atomic_reservation([(1,Decimal("2"))],{1:Decimal("1")})
def test_all_lines_planned():
    r=plan_atomic_reservation([(1,Decimal("2")),(2,Decimal("1"))],{1:Decimal("2"),2:Decimal("1")})
    assert len(r)==2
def test_consume_only_active():
    assert consume_reservation("ATIVA")=="CONSUMIDA"
    with pytest.raises(WorkflowError): consume_reservation("CANCELADA")
