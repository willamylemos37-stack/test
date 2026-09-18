from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
class ReservationError(ValueError): pass
@dataclass(frozen=True)
class ReservationLine:
    item_id:int
    quantity:Decimal
@dataclass(frozen=True)
class Reservation:
    id:int
    company_id:int
    reference:str
    status:str="ATIVA"
def validate_company_access(reservation_company_id:int, actor_company_id:int)->None:
    if reservation_company_id != actor_company_id:
        raise ReservationError("Recurso pertence a outra empresa.")
def validate_transition(current:str, target:str)->None:
    allowed={"ATIVA":{"CANCELADA","CONSUMIDA"},"CANCELADA":set(),"CONSUMIDA":set()}
    if target not in allowed.get(current,set()):
        raise ReservationError(f"Transição inválida: {current} -> {target}.")
def ensure_quantity_available(available:Decimal, requested:Decimal)->None:
    if requested <= 0: raise ReservationError("Quantidade da reserva deve ser positiva.")
    if requested > available: raise ReservationError("Estoque insuficiente para reserva.")
