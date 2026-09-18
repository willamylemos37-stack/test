import pytest
from app.services.production_workflow import *
from app.services.workflow import WorkflowError
def test_approve():
    r=approve_and_prepare("ENVIADO")
    assert r.quote_status=="APROVADO" and r.production_status=="ABERTA"
def test_start_requires_reservation():
    with pytest.raises(WorkflowError): start_production("ABERTA","PENDENTE")
    assert start_production("ABERTA","ATIVA").production_status=="EM_PRODUCAO"
def test_finish_consumes():
    r=finish_production("EM_PRODUCAO","ATIVA")
    assert r.reservation_status=="CONSUMIDA" and r.production_status=="CONCLUIDA"
