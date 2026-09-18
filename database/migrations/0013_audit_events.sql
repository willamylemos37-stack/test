CREATE TABLE IF NOT EXISTS auditoria_eventos (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NULL REFERENCES empresas(id) ON DELETE SET NULL,
    user_id INTEGER NULL REFERENCES usuarios(id) ON DELETE SET NULL,
    action VARCHAR(80) NOT NULL,
    resource_type VARCHAR(80) NULL,
    resource_id VARCHAR(80) NULL,
    request_id VARCHAR(64) NULL,
    ip_address VARCHAR(64) NULL,
    details JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_auditoria_company_id ON auditoria_eventos(company_id);
CREATE INDEX IF NOT EXISTS ix_auditoria_user_id ON auditoria_eventos(user_id);
CREATE INDEX IF NOT EXISTS ix_auditoria_action ON auditoria_eventos(action);
CREATE INDEX IF NOT EXISTS ix_auditoria_request_id ON auditoria_eventos(request_id);
CREATE INDEX IF NOT EXISTS ix_auditoria_created_at ON auditoria_eventos(created_at);
