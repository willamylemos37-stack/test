from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
class WorkflowError(ValueError): pass
@dataclass(frozen=True)
class ApprovalResult:
    quote_status:str
    reservation_status:str
    production_status:str
def approve_quote(quote_status:str)->str:
    if quote_status != "ENVIADO":
        raise WorkflowError("Somente orçamento ENVIADO pode ser aprovado.")
    return "APROVADO"
def require_atomic_stock(available:Decimal, requested:Decimal)->None:
    if requested <= 0: raise WorkflowError("Quantidade solicitada deve ser positiva.")
    if available < requested: raise WorkflowError("Estoque insuficiente; operação deve ser revertida integralmente.")
def consume_reservation(status:str)->str:
    if status != "ATIVA": raise WorkflowError("Somente reserva ATIVA pode ser consumida.")
    return "CONSUMIDA"
