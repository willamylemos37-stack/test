from __future__ import annotations
from dataclasses import dataclass
from .workflow import approve_quote, consume_reservation, WorkflowError
from .production import validate_transition

@dataclass(frozen=True)
class WorkflowCommandResult:
    quote_status: str
    reservation_status: str
    production_status: str

def approve_and_prepare(quote_status: str, reservation_status: str | None = None) -> WorkflowCommandResult:
    q = approve_quote(quote_status)
    return WorkflowCommandResult(q, reservation_status or "PENDENTE", "ABERTA")

def start_production(production_status: str, reservation_status: str) -> WorkflowCommandResult:
    if reservation_status != "ATIVA":
        raise WorkflowError("Produção exige reserva ATIVA.")
    validate_transition(production_status, "EM_PRODUCAO")
    return WorkflowCommandResult("APROVADO", "ATIVA", "EM_PRODUCAO")

def finish_production(production_status: str, reservation_status: str) -> WorkflowCommandResult:
    if reservation_status != "ATIVA":
        raise WorkflowError("Conclusão exige reserva ATIVA.")
    validate_transition(production_status, "CONCLUIDA")
    return WorkflowCommandResult("APROVADO", "CONSUMIDA", "CONCLUIDA")
