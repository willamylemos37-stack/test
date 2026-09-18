from decimal import Decimal
from typing import Any

SUPPORTED_UNITS = {"mm", "cm"}
def normalize_dimensions(model_code: str, unit: str, width: float, height: float) -> tuple[int, int]:
    if unit not in SUPPORTED_UNITS:
        raise ValueError("Unidade deve ser mm ou cm.")
    if width <= 0 or height <= 0:
        raise ValueError("Largura e altura devem ser maiores que zero.")
    if unit == "mm":
        if width != int(width) or height != int(height):
            raise ValueError("Em mm, use apenas números inteiros.")
        return int(width), int(height)
    # Decimal-safe check without silently rounding an invalid cm value.
    if Decimal(str(width)) * 10 != (Decimal(str(width)) * 10).to_integral_value():
        raise ValueError("Em cm, use no máximo uma casa decimal.")
    if Decimal(str(height)) * 10 != (Decimal(str(height)) * 10).to_integral_value():
        raise ValueError("Em cm, use no máximo uma casa decimal.")
    return int(Decimal(str(width)) * 10), int(Decimal(str(height)) * 10)


def validate_kerf(kerf_mm: int) -> None:
    if kerf_mm < 0:
        raise ValueError("Kerf não pode ser negativo.")


def validate_margin_or_markup(margin_percent: Any, markup_percent: Any) -> None:
    if margin_percent is not None and markup_percent is not None:
        raise ValueError("Informe margem OU markup, não ambos.")
