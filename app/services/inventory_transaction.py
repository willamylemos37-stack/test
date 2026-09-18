from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .workflow import WorkflowError, require_atomic_stock
@dataclass(frozen=True)
class Allocation:
    item_id:int
    quantity:Decimal
def plan_atomic_reservation(lines:list[tuple[int,Decimal]], availability:dict[int,Decimal])->list[Allocation]:
    # Pure planning step: no mutation occurs unless every requested line is available.
    allocations=[]
    for item_id, qty in lines:
        available=availability.get(item_id, Decimal("0"))
        require_atomic_stock(available, qty)
        allocations.append(Allocation(item_id, qty))
    return allocations
