from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class CalculatedQuote:
    model_code: str
    width_mm: int
    height_mm: int
    quantity: int
    parts: list[dict[str, Any]]
    glass: list[dict[str, Any]]
    accessories: list[dict[str, Any]]
    rule_snapshots: list[dict[str, str]]

@dataclass(frozen=True)
class ModelDefinition:
    code: str
    calculator: Callable[[int, int, int], CalculatedQuote]


def mp309_length(width_mm: int, leaf_count: int) -> int:
    """Calcula o corte do MP-309 conforme a quantidade de folhas."""
    if width_mm <= 0:
        raise ValueError("A largura deve ser positiva.")
    if leaf_count == 2:
        offset, divisor = 105, 2
    elif leaf_count == 4:
        offset, divisor = 178, 4
    else:
        raise ValueError("O MP-309 aceita somente modelos de 2 ou 4 folhas.")
    numerator = width_mm - offset
    if numerator <= 0 or numerator % divisor != 0:
        raise ValueError("A largura deve produzir um corte inteiro do MP-309 em milímetros.")
    return numerator // divisor


def _common_validation(width_mm: int, height_mm: int, quantity: int) -> None:
    if width_mm <= 0 or height_mm <= 0 or quantity <= 0:
        raise ValueError("Dimensões e quantidade devem ser positivas.")


def _calculate_model_001(width_mm: int, height_mm: int, quantity: int) -> CalculatedQuote:
    _common_validation(width_mm, height_mm, quantity)
    if width_mm <= 105 or height_mm <= 134:
        raise ValueError("Dimensões insuficientes para as regras técnicas do MOD-001.")
    try:
        leaf_width = mp309_length(width_mm, 2)
    except ValueError:
        raise ValueError("A largura do MOD-001 deve produzir cortes do MP-309 inteiros em milímetros.")
    if leaf_width <= 0:
        raise ValueError("Largura insuficiente para a regra do modelo.")
    parts = [
        {"material_code":"MP-357","cut_type":"PADRAO","length_mm":width_mm-30,"quantity":quantity},
        {"material_code":"MP-358","cut_type":"PADRAO","length_mm":width_mm-30,"quantity":quantity},
        {"material_code":"MP-360","cut_type":"PADRAO","length_mm":height_mm,"quantity":2*quantity},
        {"material_code":"MP-300","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":2*quantity},
        {"material_code":"MP-302","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":quantity},
        {"material_code":"MP-321","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":quantity},
        {"material_code":"MP-309","cut_type":"HORIZONTAL","length_mm":leaf_width,"quantity":4*quantity},
        {"material_code":"BG-202","cut_type":"HORIZONTAL","length_mm":leaf_width,"quantity":4*quantity},
        {"material_code":"BG-202","cut_type":"VERTICAL","length_mm":height_mm-134,"quantity":4*quantity},
    ]
    glass = [{"pane":i+1,"width_mm":leaf_width-8,"height_mm":height_mm-118,"quantity":quantity} for i in range(2)]
    accessories = [
        {"item":"ROLDANA","quantity":4*quantity},
        {"item":"FECHO","quantity":quantity},
        {"item":"GUIA_TRAVA","quantity":4*quantity},
        {"item":"PARAFUSO","quantity":16*quantity},
        {"item":"CALCO","quantity":0},
        {"item":"ESCOVA_5MM","length_mm":height_mm + leaf_width*4,"quantity":quantity},
        {"item":"ESCOVA_7MM","length_mm":height_mm,"quantity":2*quantity},
        {"item":"BORRACHA_VEDACAO","length_mm":2*((leaf_width-8)+(height_mm-118))*2,"quantity":quantity},
        {"item":"SILICONE_SELANTE","quantity":quantity/3},
    ]
    snapshots = [
        {"rule_code":"L30","expression_snapshot":"L - 30","value_snapshot":str(width_mm-30)},
        {"rule_code":"H","expression_snapshot":"H","value_snapshot":str(height_mm)},
        {"rule_code":"H40","expression_snapshot":"H - 40","value_snapshot":str(height_mm-40)},
        {"rule_code":"L105_2","expression_snapshot":"(L - 105) / 2","value_snapshot":str(leaf_width)},
        {"rule_code":"H134","expression_snapshot":"H - 134","value_snapshot":str(height_mm-134)},
        {"rule_code":"VIDRO78","expression_snapshot":"largura = MP-309 - 8 mm; altura = MP-300 - 78 mm","value_snapshot":"8 mm na largura; 78 mm na altura; vidro = H - 118 mm"},
    ]
    return CalculatedQuote("MOD-001", width_mm, height_mm, quantity, parts, glass, accessories, snapshots)


def _calculate_model_002(width_mm: int, height_mm: int, quantity: int) -> CalculatedQuote:
    """Janela Módulo Prático 4 Folhas.

    Regras fechadas nesta etapa: MP-309=(L-178)/4, 8 peças;
    MP-352=H-40, exclusivo deste modelo; BG-202 mantém as regras de
    baguete horizontal/vertical já estabelecidas.
    """
    _common_validation(width_mm, height_mm, quantity)
    if width_mm <= 178 or height_mm <= 134:
        raise ValueError("Dimensões insuficientes para as regras técnicas do MOD-002.")
    try:
        leaf_width = mp309_length(width_mm, 4)
    except ValueError:
        raise ValueError("A largura do MOD-002 deve produzir cortes do MP-309 inteiros em milímetros.")
    if leaf_width <= 0:
        raise ValueError("Largura insuficiente para a regra do modelo.")

    # Estrutura simétrica de 4 folhas: 2 marcos laterais, 4 montantes de folha,
    # 2 conjuntos de encontro (MP-302/MP-321) e 2 batentes MP-352 no centro.
    parts = [
        {"material_code":"MP-357","cut_type":"PADRAO","length_mm":width_mm-30,"quantity":quantity},
        {"material_code":"MP-358","cut_type":"PADRAO","length_mm":width_mm-30,"quantity":quantity},
        {"material_code":"MP-360","cut_type":"PADRAO","length_mm":height_mm,"quantity":2*quantity},
        {"material_code":"MP-300","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":4*quantity},
        {"material_code":"MP-302","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":2*quantity},
        {"material_code":"MP-321","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":2*quantity},
        {"material_code":"MP-352","cut_type":"PADRAO","length_mm":height_mm-40,"quantity":2*quantity},
        {"material_code":"MP-309","cut_type":"HORIZONTAL","length_mm":leaf_width,"quantity":8*quantity},
        {"material_code":"BG-202","cut_type":"HORIZONTAL","length_mm":leaf_width,"quantity":8*quantity},
        {"material_code":"BG-202","cut_type":"VERTICAL","length_mm":height_mm-134,"quantity":8*quantity},
    ]
    glass = [{"pane":i+1,"width_mm":leaf_width-8,"height_mm":height_mm-118,"quantity":quantity} for i in range(4)]
    accessories = [
        {"item":"ROLDANA","quantity":8*quantity},
        {"item":"FECHO","quantity":2*quantity},
        {"item":"GUIA_TRAVA","quantity":8*quantity},
        {"item":"PARAFUSO","quantity":32*quantity},
        {"item":"CALCO","quantity":0},
        {"item":"ESCOVA_5MM","length_mm":(2*height_mm) + leaf_width*4,"quantity":quantity},
        {"item":"ESCOVA_7MM","length_mm":height_mm,"quantity":2*quantity},
        {"item":"BORRACHA_VEDACAO","length_mm":2*((leaf_width-8)+(height_mm-118))*4,"quantity":quantity},
        {"item":"SILICONE_SELANTE","quantity":quantity/3},
    ]
    snapshots = [
        {"rule_code":"L30","expression_snapshot":"L - 30","value_snapshot":str(width_mm-30)},
        {"rule_code":"H","expression_snapshot":"H","value_snapshot":str(height_mm)},
        {"rule_code":"H40","expression_snapshot":"H - 40","value_snapshot":str(height_mm-40)},
        {"rule_code":"L178_4","expression_snapshot":"(L - 178) / 4","value_snapshot":str(leaf_width)},
        {"rule_code":"H134","expression_snapshot":"H - 134","value_snapshot":str(height_mm-134)},
        {"rule_code":"VIDRO78","expression_snapshot":"largura = MP-309 - 8 mm; altura = MP-300 - 78 mm","value_snapshot":"8 mm na largura; 78 mm na altura; vidro = H - 118 mm"},
    ]
    return CalculatedQuote("MOD-002", width_mm, height_mm, quantity, parts, glass, accessories, snapshots)


_MODEL_REGISTRY: dict[str, ModelDefinition] = {
    "MOD-001": ModelDefinition("MOD-001", _calculate_model_001),
    "MOD-002": ModelDefinition("MOD-002", _calculate_model_002),
}


def supported_models() -> tuple[str, ...]:
    return tuple(sorted(_MODEL_REGISTRY))


def calculate_model(model_code: str, width_mm: int, height_mm: int, quantity: int) -> CalculatedQuote:
    code = (model_code or "").strip().upper()
    definition = _MODEL_REGISTRY.get(code)
    if definition is None:
        raise ValueError(f"Modelo não suportado: {model_code}.")
    return definition.calculator(width_mm, height_mm, quantity)


def calculate_model_001(width_mm: int, height_mm: int, quantity: int) -> CalculatedQuote:
    return _calculate_model_001(width_mm, height_mm, quantity)
