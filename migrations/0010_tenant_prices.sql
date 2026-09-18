-- Etapa 45: isolamento de catálogo de preços por empresa.
ALTER TABLE catalogo_precos ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE;
ALTER TABLE historico_precos ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS ix_catalogo_precos_company_id ON catalogo_precos(company_id);
CREATE INDEX IF NOT EXISTS ix_historico_precos_company_id ON historico_precos(company_id);
