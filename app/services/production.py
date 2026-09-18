from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
class ProductionError(ValueError): pass
class ProductionStatus(StrEnum):
    ABERTA="ABERTA"; EM_PRODUCAO="EM_PRODUCAO"; CONCLUIDA="CONCLUIDA"; CANCELADA="CANCELADA"
@dataclass(frozen=True)
class ProductionOrderInput:
    company_id:int
    reference:str
    model_code:str
    input_snapshot:str
    technical_snapshot:str
    quote_id:int|None=None
def validate_transition(current:str,target:str)->None:
    allowed={"ABERTA":{"EM_PRODUCAO","CANCELADA"},
              "EM_PRODUCAO":{"CONCLUIDA","CANCELADA"},
              "CONCLUIDA":set(),"CANCELADA":set()}
    if target not in allowed.get(current,set()):
        raise ProductionError(f"Transição inválida: {current} -> {target}.")
def validate_company_access(order_company_id:int,actor_company_id:int)->None:
    if order_company_id != actor_company_id:
        raise ProductionError("Ordem pertence a outra empresa.")
def validate_snapshot(value:str,name:str)->None:
    if not value or not value.strip(): raise ProductionError(f"{name} obrigatório.")
