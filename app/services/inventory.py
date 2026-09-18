from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class InventoryItem:
    material_code: str
    variant: str
    kind: str
    length_mm: int|None
    quantity: Decimal
    status: str = "DISPONIVEL"

class InventoryError(ValueError): pass

def validate_item(item: InventoryItem) -> None:
    if not item.material_code.strip(): raise InventoryError("material_code obrigatório.")
    if item.kind not in {"BARRA","RETALHO","UNIDADE"}: raise InventoryError("kind inválido.")
    if item.quantity < 0: raise InventoryError("quantity não pode ser negativa.")
    if item.kind in {"BARRA","RETALHO"} and (item.length_mm is None or item.length_mm <= 0):
        raise InventoryError("material linear exige length_mm positivo.")
    if item.status not in {"DISPONIVEL","RESERVADO","CONSUMIDO","BLOQUEADO"}:
        raise InventoryError("status inválido.")

def compatible_scrap(material_code:str, length_mm:int, available: list[InventoryItem]) -> list[InventoryItem]:
    return [x for x in available if x.material_code==material_code and x.kind=="RETALHO"
            and x.status=="DISPONIVEL" and x.length_mm is not None and x.length_mm>=length_mm]
