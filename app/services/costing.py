def calculate_cost(db, calculated):
    """Compatibilidade: custo apenas dos perfis, usando o motor completo."""
    r = calculate_full_cost(db, calculated)
    return {
        "aluminum": r["aluminum"],
        "glass": [],
        "accessories": [],
        "consumables": [],
        "cost_aluminum": r["cost_aluminum"],
        "cost_glass": r["cost_glass"],
        "cost_accessories": r["cost_accessories_consumables"],
        "cost_consumables": Decimal("0"),
        "total_cost": r["total_cost"],
        "missing_prices": r["missing_prices"],
        "status": r["status"],
    }

from decimal import Decimal
from sqlalchemy import select
from app.models.entities import PriceCatalog
from app.services.cutting import optimize_profile
from app.services.pricing import get_current_prices

def _price(db, code, variant="PADRAO"):
    return get_current_prices(db,[code],variant).get(code)

def calculate_full_cost(db, calculated, kerf_mm=3):
    # Aluminum: cut by profile, compare 3m/6m prices.
    aluminum=[]
    total=Decimal("0")
    pending=set()
    for code in sorted(set(p["material_code"] for p in calculated.parts)):
        pieces=[]
        for p in calculated.parts:
            if p["material_code"]==code:
                pieces += [p["length_mm"]]*p["quantity"]
        p3=_price(db,code,"BARRA_3000")
        p6=_price(db,code,"BARRA_6000")
        source3="BARRA_3000" if p3 is not None else None
        source6="BARRA_6000" if p6 is not None else None
        if p3 is None and p6 is None:
            legacy=_price(db,code,"PADRAO")
            if legacy is not None:
                p3=legacy
                source3="PADRAO"
        result=optimize_profile(pieces,p3,p6,kerf_mm)
        cost=result["cost"] or Decimal("0")
        total += cost
        if p3 is None and p6 is None: pending.add(code)
        aluminum.append({
            "material_code":code,
            "bar_length_mm":result["bar_length_mm"],
            "bar_count":result["bar_count"],
            "total_scrap_mm":sum(b.scrap_mm for b in result["bars"]),
            "kerf_mm":kerf_mm,
            "cost":cost,
            "price_3000":p3,
            "price_6000":p6,
            "price_3000_source":source3,
            "price_6000_source":source6
        })

    # Glass: one catalog price per m², using pane area.
    glass_price=_price(db,"VIDRO","M2")
    glass_total=Decimal("0")
    glass=[]
    for pane in calculated.glass:
        area=Decimal(pane["width_mm"]*pane["height_mm"])/Decimal(1_000_000)
        qty=pane["quantity"]
        subtotal=(glass_price or Decimal("0"))*area*qty
        glass_total += subtotal
        glass.append({"pane":pane["pane"],"width_mm":pane["width_mm"],
                      "height_mm":pane["height_mm"],"area_m2":area,
                      "quantity":qty,"unit_price_m2":glass_price,
                      "subtotal":subtotal})
    if glass_price is None: pending.add("VIDRO")

    # Accessory and consumable quantities from the technical motor.
    accessories=[]
    for item in calculated.accessories:
        code=item["item"]
        qty=Decimal(str(item.get("quantity",0)))
        # Linear items are priced per meter; piece items per unit.
        if "length_mm" in item:
            variant="METRO"
            unit_price=_price(db,code,variant)
            base_qty=qty
            meters=Decimal(str(item["length_mm"])) / Decimal(1000) * qty
            subtotal=(unit_price or Decimal("0"))*meters
            measure=meters
        else:
            variant="UNIDADE"
            unit_price=_price(db,code,variant)
            subtotal=(unit_price or Decimal("0"))*qty
            measure=qty
        if unit_price is None: pending.add(code)
        accessories.append({"item":code,"variant":variant,"quantity":measure,
                            "unit_price":unit_price,"subtotal":subtotal})
        total += subtotal

    total += glass_total
    price_snapshots=[]
    for x in aluminum:
        if x["price_3000"] is not None and x["bar_length_mm"] == 3000:
            price_snapshots.append({"material_code":x["material_code"],"variant":x["price_3000_source"],"unit":"barra","unit_price":x["price_3000"]})
        if x["price_6000"] is not None and x["bar_length_mm"] == 6000:
            price_snapshots.append({"material_code":x["material_code"],"variant":x["price_6000_source"],"unit":"barra","unit_price":x["price_6000"]})
    if glass_price is not None:
        price_snapshots.append({"material_code":"VIDRO","variant":"M2","unit":"m2","unit_price":glass_price})
    for item in accessories:
        if item["unit_price"] is not None:
            price_snapshots.append({"material_code":item["item"],"variant":item["variant"],"unit":item["variant"],"unit_price":item["unit_price"]})

    return {
        "cost_aluminum":sum(Decimal(x["cost"]) for x in aluminum),
        "cost_glass":glass_total,
        "cost_accessories_consumables":sum(Decimal(x["subtotal"]) for x in accessories),
        "total_cost":total,
        "aluminum":aluminum,"glass":glass,"accessories_consumables":accessories,
        "missing_prices":sorted(pending),
        "price_snapshots":price_snapshots,
        "status":"PRECO_INCOMPLETO" if pending else "CUSTO_COMPLETO"
    }
