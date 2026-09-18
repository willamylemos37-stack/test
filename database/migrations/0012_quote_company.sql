-- Etapa 47: isolamento multiempresa de orçamentos.
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS company_id BIGINT REFERENCES empresas(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS ix_orcamentos_company_id ON orcamentos(company_id);
