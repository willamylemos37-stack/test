from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def _pct(value) -> Decimal:
    value = Decimal(str(value))
    if value < 0:
        raise ValueError("Percentual não pode ser negativo.")
    return value / Decimal("100")


def form_price(
    material_cost: Decimal,
    labor_total: Decimal = Decimal("0"),
    indirect_percent: Decimal = Decimal("0"),
    indirect_fixed: Decimal = Decimal("0"),
    freight: Decimal = Decimal("0"),
    tax_percent: Decimal = Decimal("0"),
    margin_percent: Decimal | None = None,
    markup_percent: Decimal | None = None,
):
    """Forma preço de venda sem alterar dados.

    Base de custo = material + mão de obra + despesas indiretas + frete.
    Indiretos percentuais incidem sobre material + mão de obra.
    Imposto é percentual do preço de venda.
    Método margem: margem-alvo é percentual do preço de venda.
    Método markup: acréscimo é percentual sobre a base de custo, antes do imposto.
    """
    material_cost = Decimal(material_cost)
    labor_total = Decimal(labor_total)
    indirect_fixed = Decimal(indirect_fixed)
    freight = Decimal(freight)
    indirect_percent = Decimal(indirect_percent)
    tax_percent = Decimal(tax_percent)

    if min(material_cost, labor_total, indirect_fixed, freight,
           indirect_percent, tax_percent) < 0:
        raise ValueError("Valores de custo e percentuais não podem ser negativos.")
    if margin_percent is not None and markup_percent is not None:
        raise ValueError("Informe margem OU markup, não ambos.")

    indirect_variable = (material_cost + labor_total) * _pct(indirect_percent)
    base_cost = material_cost + labor_total + indirect_variable + indirect_fixed + freight

    tax = _pct(tax_percent)

    if margin_percent is not None:
        margin = Decimal(margin_percent)
        if margin < 0 or margin >= 100:
            raise ValueError("Margem deve estar entre 0 e 100%.")
        denominator = Decimal("1") - tax - _pct(margin)
        if denominator <= 0:
            raise ValueError("Imposto + margem devem ser menores que 100%.")
        sale = base_cost / denominator
        method = "MARGEM"
    elif markup_percent is not None:
        markup = Decimal(markup_percent)
        if markup < 0:
            raise ValueError("Markup não pode ser negativo.")
        if tax >= 100:
            raise ValueError("Imposto deve ser menor que 100%.")
        sale = (base_cost * (Decimal("1") + _pct(markup))) / (Decimal("1") - tax)
        method = "MARKUP"
    else:
        # Sem meta comercial: apenas custo-base, sem imposto embutido.
        sale = base_cost
        method = "CUSTO"

    sale = money(sale)
    tax_amount = money(sale * tax)
    profit = money(sale - base_cost - tax_amount)
    effective_margin = money((profit / sale * Decimal("100")) if sale else Decimal("0"))
    effective_markup = money((profit / base_cost * Decimal("100")) if base_cost else Decimal("0"))

    return {
        "method": method,
        "material_cost": money(material_cost),
        "labor_total": money(labor_total),
        "indirect_variable": money(indirect_variable),
        "indirect_fixed": money(indirect_fixed),
        "freight": money(freight),
        "base_cost": money(base_cost),
        "tax_percent": money(tax_percent),
        "tax_amount": tax_amount,
        "target_margin_percent": money(margin_percent) if margin_percent is not None else None,
        "target_markup_percent": money(markup_percent) if markup_percent is not None else None,
        "sale_price": sale,
        "profit": profit,
        "effective_margin_percent": effective_margin,
        "effective_markup_percent": effective_markup,
    }
