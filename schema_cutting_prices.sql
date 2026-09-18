-- Etapa 26: variantes de barra
ALTER TABLE catalogo_precos ADD COLUMN IF NOT EXISTS variant VARCHAR(40) NOT NULL DEFAULT 'PADRAO';
ALTER TABLE historico_precos ADD COLUMN IF NOT EXISTS variant VARCHAR(40) NOT NULL DEFAULT 'PADRAO';
CREATE INDEX IF NOT EXISTS ix_catalogo_precos_material_variant ON catalogo_precos(material_code, variant);
