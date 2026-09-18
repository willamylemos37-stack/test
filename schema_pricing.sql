-- Etapa 28: formação de preço e snapshots comerciais.
CREATE TABLE IF NOT EXISTS orcamento_precos_snapshot (
    id SERIAL PRIMARY KEY,
    quote_id INTEGER NOT NULL REFERENCES orcamentos(id),
    material_code VARCHAR(50) NOT NULL,
    variant VARCHAR(40) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    unit_price NUMERIC(14,4) NOT NULL DEFAULT 0,
    supplier VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS orcamento_formacao_preco_snapshot (
    id SERIAL PRIMARY KEY,
    quote_id INTEGER NOT NULL REFERENCES orcamentos(id),
    method VARCHAR(20) NOT NULL,
    material_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    labor_total NUMERIC(14,2) NOT NULL DEFAULT 0,
    indirect_variable NUMERIC(14,2) NOT NULL DEFAULT 0,
    indirect_fixed NUMERIC(14,2) NOT NULL DEFAULT 0,
    freight NUMERIC(14,2) NOT NULL DEFAULT 0,
    tax_percent NUMERIC(8,4) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    target_margin_percent NUMERIC(8,4),
    target_markup_percent NUMERIC(8,4),
    base_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    sale_price NUMERIC(14,2) NOT NULL DEFAULT 0,
    profit NUMERIC(14,2) NOT NULL DEFAULT 0,
    effective_margin_percent NUMERIC(8,4) NOT NULL DEFAULT 0,
    effective_markup_percent NUMERIC(8,4) NOT NULL DEFAULT 0
);
