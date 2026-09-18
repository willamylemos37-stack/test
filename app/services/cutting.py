from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

@dataclass
class CutBar:
    length_mm: int
    cuts: list[int]
    used_mm: int
    scrap_mm: int

def ffd(cuts: Iterable[int], bar_length_mm: int, kerf_mm: int = 3) -> list[CutBar]:
    pieces=sorted([int(x) for x in cuts], reverse=True)
    if any(x <= 0 or x > bar_length_mm for x in pieces):
        raise ValueError("Há corte inválido para o comprimento da barra.")
    bars: list[CutBar]=[]
    for piece in pieces:
        placed=False
        for bar in bars:
            added=piece + (kerf_mm if bar.cuts else 0)
            if bar.used_mm + added <= bar_length_mm:
                bar.used_mm += added
                bar.cuts.append(piece)
                bar.scrap_mm=bar.length_mm-bar.used_mm
                placed=True
                break
        if not placed:
            bar=CutBar(bar_length_mm,[piece],piece,bar_length_mm-piece)
            bars.append(bar)
    return bars

def optimize_profile(cuts: list[int], price_3000: Decimal | None,
                     price_6000: Decimal | None, kerf_mm: int = 3) -> dict:
    result3=ffd(cuts,3000,kerf_mm)
    result6=ffd(cuts,6000,kerf_mm)
    cost3=(price_3000*len(result3)) if price_3000 is not None else None
    cost6=(price_6000*len(result6)) if price_6000 is not None else None
    if cost3 is not None and cost6 is not None:
        chosen=3000 if cost3 <= cost6 else 6000
    elif cost3 is not None:
        chosen=3000
    elif cost6 is not None:
        chosen=6000
    else:
        chosen=3000 if len(result3) <= len(result6) else 6000
    bars=result3 if chosen==3000 else result6
    return {
        "bar_length_mm":chosen,
        "bars":bars,
        "bar_count":len(bars),
        "cost": cost3 if chosen==3000 else cost6,
        "alternative_3000_bars":len(result3),
        "alternative_6000_bars":len(result6),
        "alternative_3000_cost":cost3,
        "alternative_6000_cost":cost6,
        "kerf_mm":kerf_mm,
    }
