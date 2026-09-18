from app.services.calculator import calculate_model, mp309_length
import pytest


def test_mp309_four_leaves_exact_integer():
    assert mp309_length(1178, 4) == 250


def test_mp309_four_leaves_rejects_fraction():
    with pytest.raises(ValueError):
        mp309_length(1203, 4)


def test_model_002_calculation():
    r = calculate_model('MOD-002', 1178, 1500, 30)
    assert r.model_code == 'MOD-002'
    p = {(x['material_code'], x['cut_type']): x for x in r.parts}
    assert p[('MP-309','HORIZONTAL')] == {'material_code':'MP-309','cut_type':'HORIZONTAL','length_mm':250,'quantity':240}
    assert p[('MP-352','PADRAO')]['length_mm'] == 1460
    assert p[('MP-352','PADRAO')]['quantity'] == 60
    assert len(r.glass) == 4
    assert all(x['width_mm'] == 242 and x['height_mm'] == 1382 and x['quantity'] == 30 for x in r.glass)
    assert 'MP-352' in [x['material_code'] for x in r.parts]
    accessories = {x['item']: x for x in r.accessories}
    assert accessories['ESCOVA_5MM'] == {'item':'ESCOVA_5MM','length_mm':4000,'quantity':30}
    assert accessories['ESCOVA_7MM'] == {'item':'ESCOVA_7MM','length_mm':1500,'quantity':60}
    assert accessories['BORRACHA_VEDACAO'] == {'item':'BORRACHA_VEDACAO','length_mm':12992,'quantity':30}
    assert r.rule_snapshots[3]['rule_code'] == 'L178_4'
