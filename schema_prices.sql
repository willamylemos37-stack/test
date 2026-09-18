-- Etapa 24: catálogo e histórico de preços
CREATE TABLE IF NOT EXISTS catalogo_precos (
    id SERIAL PRIMARY KEY,
    material_code VARCHAR(50) NOT NULL,
    description VARCHAR(160) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    price NUMERIC(14,4) NOT NULL CHECK (price >= 0),
    supplier VARCHAR(120),
    active VARCHAR(20) NOT NULL DEFAULT 'ATIVO'
);
CREATE INDEX IF NOT EXISTS ix_catalogo_precos_material_code ON catalogo_precos(material_code);

CREATE TABLE IF NOT EXISTS historico_precos (
    id SERIAL PRIMARY KEY,
    material_code VARCHAR(50) NOT NULL,
    price NUMERIC(14,4) NOT NULL CHECK (price >= 0),
    unit VARCHAR(20) NOT NULL,
    supplier VARCHAR(120),
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(120) NOT NULL DEFAULT 'CADASTRO'
);
CREATE INDEX IF NOT EXISTS ix_historico_precos_material_code ON historico_precos(material_code);
