from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

client = TestClient(app)

def test_calcular_mm():
    r = client.post("/calcular", json={
        "model_code":"MOD-001","unit":"mm","width":1003,"height":1000,"quantity":1
    })
    assert r.status_code == 200
    assert r.json()["width_mm"] == 1003

def test_mm_rejects_decimal():
    r = client.post("/calcular", json={
        "model_code":"MOD-001","unit":"mm","width":1000.5,"height":1000,"quantity":1
    })
    assert r.status_code == 400

def test_cm_normalizes():
    r = client.post("/calcular", json={
        "model_code":"MOD-001","unit":"cm","width":150.3,"height":120.0,"quantity":1
    })
    assert r.status_code == 200
    assert r.json()["width_mm"] == 1503
    assert r.json()["height_mm"] == 1200

def test_cm_rejects_more_than_one_decimal():
    r = client.post("/calcular", json={
        "model_code":"MOD-001","unit":"cm","width":150.05,"height":120.0,"quantity":1
    })
    assert r.status_code == 400


def test_height_decimal_rejected_in_mm():
    r = client.post("/calcular", json={"model_code":"MOD-001","unit":"mm","width":1003,"height":1000.5,"quantity":1})
    assert r.status_code == 400

def test_health_version():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["version"] == "5.51.0"


def test_full_quote_endpoint_provisional_with_glass_sheet():
    Base.metadata.create_all(bind=engine)
    r = client.post("/orcamento-completo", json={
        "model_code":"MOD-001","unit":"mm","width":1003,"height":1000,"quantity":1,
        "allow_provisional":True,"glass_sheet_width_mm":3210,"glass_sheet_height_mm":2200
    })
    assert r.status_code == 200
    data = r.json()
    assert data["input"]["width_mm"] == 1003
    assert data["status"] == "PROVISORIO"
    assert data["glass_sheets"]["sheet_count"] >= 1

def test_full_quote_rejects_mm_height_decimal():
    r = client.post("/orcamento-completo", json={
        "model_code":"MOD-001","unit":"mm","width":1003,"height":1000.5,"quantity":1
    })
    assert r.status_code == 400

def test_fractional_half_leaf_rejected_at_api_boundary():
    r = client.post("/calcular", json={
        "model_code": "MOD-001", "unit": "mm", "width": 1002, "height": 1000, "quantity": 1
    })
    assert r.status_code == 400
    assert "MP-309 inteiros" in r.json()["detail"]


def test_negative_kerf_rejected():
    r = client.post("/custo-completo?kerf_mm=-1", json={
        "model_code": "MOD-001", "unit": "mm", "width": 1003, "height": 1000, "quantity": 1
    })
    assert r.status_code == 400


def test_health_version_v515():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["version"] == "5.51.0"

def test_unknown_model_rejected_at_api_boundary():
    r = client.post("/calcular", json={
        "model_code":"MOD-999","unit":"mm","width":1003,"height":1000,"quantity":1
    })
    assert r.status_code == 400
    assert "Modelo não suportado" in r.json()["detail"]


def test_public_catalog_is_safe_and_marks_future_sections():
    r = client.get("/catalogo/publico")
    assert r.status_code == 200
    by_code = {item["code"]: item for item in r.json()}
    assert by_code["PORTAO"]["status"] == "EM_BREVE"
    assert by_code["GRADE"]["status"] == "EM_BREVE"
    assert by_code["BOX"]["status"] == "EM_BREVE"
    assert all(set(item) == {"code", "name", "status"} for item in r.json())
