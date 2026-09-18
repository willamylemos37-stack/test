import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.runtime_config import validate_runtime_config, RuntimeConfigError

def test_ready_endpoint():
    r = TestClient(app).get('/ready')
    assert r.status_code == 200
    assert r.json()['status'] == 'ready'

def test_production_rejects_auto_create(monkeypatch):
    monkeypatch.setenv('APP_ENV','production')
    monkeypatch.setenv('DATABASE_URL','postgresql+psycopg://x:y@localhost/x')
    monkeypatch.setenv('APP_SECRET_KEY','a-real-secret')
    monkeypatch.setenv('AUTO_CREATE_SCHEMA','true')
    with pytest.raises(RuntimeConfigError):
        validate_runtime_config()
