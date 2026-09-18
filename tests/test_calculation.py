import pytest
from app.services.calculator import calculate_model_001

def test_model_001_has_no_mp352():
    result = calculate_model_001(1003,1000,1)
    assert "MP-352" not in [p["material_code"] for p in result.parts]

def test_glass_clearance():
    result = calculate_model_001(1003,1000,1)
    assert result.glass[0]["width_mm"] == 441
    assert result.glass[0]["height_mm"] == 882

def test_multiple_quantity_scales_parts():
    one = calculate_model_001(1003,1000,1)
    six = calculate_model_001(1003,1000,6)
    assert sum(p["quantity"] for p in six.parts) == 6 * sum(p["quantity"] for p in one.parts)

def test_invalid_dimensions():
    with pytest.raises(ValueError):
        calculate_model_001(105,1000,1)
    with pytest.raises(ValueError):
        calculate_model_001(1000,134,1)


def test_odd_width_rejected_for_integer_mm_cuts():
    with pytest.raises(ValueError):
        calculate_model_001(1004, 1000, 1)


def test_reference_six_windows_cut_quantities():
    result = calculate_model_001(1003, 1000, 6)
    by_code = {}
    for part in result.parts:
        by_code.setdefault((part["material_code"], part["cut_type"], part["length_mm"]), 0)
        by_code[(part["material_code"], part["cut_type"], part["length_mm"])] += part["quantity"]
    assert by_code[("MP-357", "PADRAO", 973)] == 6
    assert by_code[("MP-309", "HORIZONTAL", 449)] == 24
    assert by_code[("BG-202", "VERTICAL", 866)] == 24
    assert result.glass[0]["width_mm"] == 441
    assert result.glass[0]["height_mm"] == 882

def test_unknown_model_is_rejected():
    from app.services.calculator import calculate_model
    with pytest.raises(ValueError, match="Modelo não suportado"):
        calculate_model("MOD-999", 1000, 1000, 1)

def test_model_code_is_normalized():
    from app.services.calculator import calculate_model
    result = calculate_model(" mod-001 ", 1003, 1000, 1)
    assert result.model_code == "MOD-001"


def test_glass_height_is_mp300_minus_78():
    result = calculate_model_001(1203, 1500, 1)
    assert result.parts[3]["material_code"] == "MP-300"
    assert result.parts[3]["length_mm"] == 1460
    assert result.glass[0]["width_mm"] == 541
    assert result.glass[0]["height_mm"] == 1382


def test_glass_width_uses_mp309_minus_8():
    result = calculate_model_001(1203, 1500, 1)
    assert result.parts[6]["length_mm"] == 549
    assert result.glass[0]["width_mm"] == 541


def test_mp309_rules_two_and_four_leaves():
    from app.services.calculator import mp309_length
    assert mp309_length(1203, 2) == 549
    assert mp309_length(1202, 4) == 256
    with pytest.raises(ValueError):
        mp309_length(1203, 4)

