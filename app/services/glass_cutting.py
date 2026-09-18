from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class GlassPiece:
    width_mm: int
    height_mm: int
    quantity: int = 1

@dataclass(frozen=True)
class GlassSheet:
    width_mm: int
    height_mm: int
    kerf_mm: int = 3

def expand_pieces(pieces: Iterable[GlassPiece]):
    out=[]
    for p in pieces:
        if p.width_mm <= 0 or p.height_mm <= 0 or p.quantity <= 0:
            raise ValueError("Dimensões e quantidades devem ser positivas.")
        out += [(p.width_mm,p.height_mm)] * p.quantity
    return out

def greedy_sheets(pieces, sheet: GlassSheet):
    items=sorted(expand_pieces(pieces), key=lambda p:p[0]*p[1], reverse=True)
    sheets=[]
    for pw,ph in items:
        placed=False
        for s in sheets:
            for row in s["rows"]:
                for rw,rh in ((pw,ph),(ph,pw)):
                    extra=sheet.kerf_mm if row["pieces"] else 0
                    if rw <= sheet.width_mm and rh <= row["height"] and row["used_width"]+extra+rw <= sheet.width_mm:
                        row["used_width"] += extra+rw
                        row["pieces"].append((pw,ph,rw,rh))
                        placed=True; break
                if placed: break
            if placed: break
            for rw,rh in ((pw,ph),(ph,pw)):
                extra=sheet.kerf_mm if s["rows"] else 0
                if rw <= sheet.width_mm and s["used_height"]+extra+rh <= sheet.height_mm:
                    s["rows"].append({"height":rh,"used_width":rw,"pieces":[(pw,ph,rw,rh)]})
                    s["used_height"] += extra+rh
                    placed=True; break
            if placed: break
        if not placed:
            if not any(rw <= sheet.width_mm and rh <= sheet.height_mm for rw,rh in ((pw,ph),(ph,pw))):
                raise ValueError(f"Peça {pw}x{ph} não cabe na chapa.")
            rw,rh=min(((pw,ph),(ph,pw)), key=lambda x:(x[1],x[0]))
            sheets.append({"used_height":rh,"rows":[{"height":rh,"used_width":rw,"pieces":[(pw,ph,rw,rh)]}]})
    area=sum(p[0]*p[1] for s in sheets for r in s["rows"] for p in r["pieces"])
    purchased=sheet.width_mm*sheet.height_mm*len(sheets)
    return {"sheet_count":len(sheets),"sheet_width_mm":sheet.width_mm,"sheet_height_mm":sheet.height_mm,
            "kerf_mm":sheet.kerf_mm,"piece_area_mm2":area,"purchased_area_mm2":purchased,
            "scrap_area_mm2":purchased-area,
            "utilization_percent":round(area/purchased*100,2) if purchased else 0,
            "layout":sheets,"method":"GREEDY_ROW","optimality":"HEURISTIC"}

def optimize_glass(pieces, sheets):
    sheets=list(sheets)
    if not sheets: raise ValueError("Cadastre pelo menos um formato de chapa.")
    return [greedy_sheets(pieces,s) for s in sheets]

def choose_by_cost(results, price_by_size=None):
    if not price_by_size: return None
    candidates=[]
    for r in results:
        key=(r["sheet_width_mm"],r["sheet_height_mm"])
        if key in price_by_size: candidates.append((r["sheet_count"]*float(price_by_size[key]),r))
    return min(candidates,key=lambda x:x[0])[1] if candidates else None
