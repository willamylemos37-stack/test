import pytest
from app.security import hash_password,verify_password,create_token,decode_token,SecurityError
def test_password():
    h=hash_password("SenhaSegura123"); assert verify_password("SenhaSegura123",h); assert not verify_password("errada",h)
def test_short(): 
    with pytest.raises(SecurityError): hash_password("1234567")
def test_token(monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY","test-secret-key")
    d=decode_token(create_token("7","3","ADMIN")); assert d["sub"]=="7" and d["company_id"]=="3" and d["role"]=="ADMIN"
def test_tamper(monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY","test-secret-key"); b,s=create_token("7","3","ADMIN").split(".")
    with pytest.raises(SecurityError): decode_token(b+"x."+s)
