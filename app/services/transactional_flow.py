from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
class TransactionFlowError(ValueError): pass
@dataclass(frozen=True)
class ReservationPlan:
    item_id:int
    quantity:Decimal
def build_atomic_plan(lines:list[tuple[int,Decimal]], availability:dict[int,Decimal])->list[ReservationPlan]:
    plan=[]
    for item_id, qty in lines:
        if qty <= 0: raise TransactionFlowError("Quantidade deve ser positiva.")
        if availability.get(item_id, Decimal("0")) < qty:
            raise TransactionFlowError("Estoque insuficiente; nenhuma linha deve ser reservada.")
        plan.append(ReservationPlan(item_id,qty))
    return plan
def require_same_company(resource_company:int, actor_company:int)->None:
    if resource_company != actor_company: raise TransactionFlowError("Empresa sem acesso ao recurso.")
