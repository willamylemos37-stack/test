import os
os.environ["APP_SECRET_KEY"]="test-secret-etapa-44"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models.security_entities import Company, User
from app.security import hash_password
def setup_module():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    if not db.query(Company).filter_by(id=991).first():
        c=Company(id=991,name="Empresa Teste",active=True); db.add(c); db.flush()
        db.add(User(company_id=991,email="teste@empresa.local",password_hash=hash_password("senha-segura-123"),role="ADMIN"))
        db.commit()
    db.close()
def test_login_and_me():
    c=TestClient(app)
    r=c.post("/auth/login",json={"company_id":991,"email":"teste@empresa.local","password":"senha-segura-123"})
    assert r.status_code==200
    token=r.json()["access_token"]
    m=c.get("/auth/me",headers={"Authorization":"Bearer "+token})
    assert m.status_code==200 and m.json()["company_id"]==991
def test_prices_require_token():
    c=TestClient(app)
    r=c.post("/precos",json={"material_code":"X","description":"X","unit":"UN","price":10})
    assert r.status_code==401

def test_protected_quote_requires_token():
    c=TestClient(app)
    r=c.get("/orcamentos/999999")
    assert r.status_code==401
