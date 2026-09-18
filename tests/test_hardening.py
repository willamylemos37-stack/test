import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.runtime_config import validate_runtime_config, RuntimeConfigError


def test_request_id_is_returned_and_invalid_value_is_replaced():
    c = TestClient(app)
    valid = c.get('/health', headers={'X-Request-ID': 'audit-123_ABC'})
    assert valid.headers['X-Request-ID'] == 'audit-123_ABC'
    invalid = c.get('/health', headers={'X-Request-ID': 'bad value\nlog-injection'})
    rid = invalid.headers['X-Request-ID']
    assert rid != 'bad value\nlog-injection'
    assert len(rid) <= 64 and all(ch.isalnum() or ch in '-_' for ch in rid)


def test_production_rejects_sqlite(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///./x.db')
    monkeypatch.setenv('APP_SECRET_KEY', 'a-long-production-secret')
    monkeypatch.setenv('AUTO_CREATE_SCHEMA', 'false')
    monkeypatch.setenv('CORS_ORIGINS', 'https://app.example.com')
    with pytest.raises(RuntimeConfigError, match='SQLite'):
        validate_runtime_config()


def test_production_rejects_localhost_cors(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('DATABASE_URL', 'postgresql+psycopg://x:y@db/app')
    monkeypatch.setenv('APP_SECRET_KEY', 'a-long-production-secret')
    monkeypatch.setenv('AUTO_CREATE_SCHEMA', 'false')
    monkeypatch.setenv('CORS_ORIGINS', 'https://app.example.com,http://localhost:3000')
    with pytest.raises(RuntimeConfigError, match='CORS'):
        validate_runtime_config()
