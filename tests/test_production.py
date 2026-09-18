import pytest
from app.services.production import *
def test_transitions():
    validate_transition("ABERTA","EM_PRODUCAO")
    validate_transition("EM_PRODUCAO","CONCLUIDA")
    with pytest.raises(ProductionError): validate_transition("CONCLUIDA","ABERTA")
def test_company():
    validate_company_access(1,1)
    with pytest.raises(ProductionError): validate_company_access(1,2)
def test_snapshots():
    validate_snapshot('{"w":1000}',"input_snapshot")
    with pytest.raises(ProductionError): validate_snapshot("","technical_snapshot")
