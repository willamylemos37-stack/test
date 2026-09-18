-- Migração aditiva e não destrutiva. Colunas legadas são preservadas para compatibilidade.

ALTER TABLE modelos ADD COLUMN IF NOT EXISTS code VARCHAR(30);
ALTER TABLE modelos ADD COLUMN IF NOT EXISTS name VARCHAR(120);
ALTER TABLE modelos ADD COLUMN IF NOT EXISTS leaves INTEGER;
ALTER TABLE modelos ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'ATIVO';
UPDATE modelos SET code=COALESCE(code,codigo), name=COALESCE(name,nome), leaves=COALESCE(leaves,folhas), status=COALESCE(status,CASE WHEN ativo THEN 'ATIVO' ELSE 'INATIVO' END);
ALTER TABLE modelos ALTER COLUMN code SET NOT NULL;
ALTER TABLE modelos ALTER COLUMN name SET NOT NULL;
ALTER TABLE modelos ALTER COLUMN leaves SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_modelos_code ON modelos(code);

ALTER TABLE regras_tecnicas ADD COLUMN IF NOT EXISTS expression VARCHAR(255);
ALTER TABLE regras_tecnicas ADD COLUMN IF NOT EXISTS description TEXT NOT NULL DEFAULT '';
UPDATE regras_tecnicas SET expression=COALESCE(expression,expressao), description=COALESCE(description,'');
ALTER TABLE regras_tecnicas ALTER COLUMN expression SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_regras_tecnicas_code ON regras_tecnicas(code);

ALTER TABLE modelo_componentes ADD COLUMN IF NOT EXISTS material_code VARCHAR(50);
ALTER TABLE modelo_componentes ADD COLUMN IF NOT EXISTS quantity INTEGER;
ALTER TABLE modelo_componentes ADD COLUMN IF NOT EXISTS cut_rule VARCHAR(50);
ALTER TABLE modelo_componentes ADD COLUMN IF NOT EXISTS notes TEXT NOT NULL DEFAULT '';
UPDATE modelo_componentes SET material_code=COALESCE(material_code,componente), quantity=COALESCE(quantity,ROUND(quantidade_por_unidade)::INTEGER), cut_rule=COALESCE(cut_rule,'LEGACY'), notes=COALESCE(notes,'');
ALTER TABLE modelo_componentes ALTER COLUMN material_code SET NOT NULL;
ALTER TABLE modelo_componentes ALTER COLUMN quantity SET NOT NULL;
ALTER TABLE modelo_componentes ALTER COLUMN cut_rule SET NOT NULL;

ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS code VARCHAR(40);
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS model_code VARCHAR(30);
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS width_mm INTEGER;
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS height_mm INTEGER;
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS quantity INTEGER;
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS total_cost NUMERIC(14,2) NOT NULL DEFAULT 0;
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS sale_price NUMERIC(14,2) NOT NULL DEFAULT 0;
ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
UPDATE orcamentos SET code=COALESCE(code,numero,'LEGACY-'||id::text), model_code=COALESCE(model_code,(SELECT m.code FROM modelos m WHERE m.id=orcamentos.modelo_id),'LEGACY'), width_mm=COALESCE(width_mm,ROUND(largura_mm)::INTEGER), height_mm=COALESCE(height_mm,ROUND(altura_mm)::INTEGER), quantity=COALESCE(quantity,quantidade), total_cost=COALESCE(total_cost,custo_total,0), sale_price=COALESCE(sale_price,venda_total,0);
ALTER TABLE orcamentos ALTER COLUMN code SET NOT NULL;
ALTER TABLE orcamentos ALTER COLUMN model_code SET NOT NULL;
ALTER TABLE orcamentos ALTER COLUMN width_mm SET NOT NULL;
ALTER TABLE orcamentos ALTER COLUMN height_mm SET NOT NULL;
ALTER TABLE orcamentos ALTER COLUMN quantity SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_orcamentos_code ON orcamentos(code);

ALTER TABLE orcamento_itens ADD COLUMN IF NOT EXISTS material_code VARCHAR(50);
ALTER TABLE orcamento_itens ADD COLUMN IF NOT EXISTS cut_type VARCHAR(30);
ALTER TABLE orcamento_itens ADD COLUMN IF NOT EXISTS length_mm INTEGER;
ALTER TABLE orcamento_itens ADD COLUMN IF NOT EXISTS quantity INTEGER;
ALTER TABLE orcamento_itens ADD COLUMN IF NOT EXISTS unit_price NUMERIC(14,4) DEFAULT 0;
ALTER TABLE orcamento_itens ADD COLUMN IF NOT EXISTS total_price NUMERIC(14,2) DEFAULT 0;
UPDATE orcamento_itens SET material_code=COALESCE(material_code,item,'LEGACY'), cut_type=COALESCE(cut_type,'LEGACY'), length_mm=COALESCE(length_mm,1), quantity=COALESCE(quantity,GREATEST(1,ROUND(COALESCE(quantidade,1)))::INTEGER), unit_price=COALESCE(unit_price,preco_unitario,0), total_price=COALESCE(total_price,total,0);
ALTER TABLE orcamento_itens ALTER COLUMN material_code SET NOT NULL;
ALTER TABLE orcamento_itens ALTER COLUMN cut_type SET NOT NULL;
ALTER TABLE orcamento_itens ALTER COLUMN length_mm SET NOT NULL;
ALTER TABLE orcamento_itens ALTER COLUMN quantity SET NOT NULL;

ALTER TABLE orcamento_regras_snapshot ADD COLUMN IF NOT EXISTS expression_snapshot VARCHAR(255);
ALTER TABLE orcamento_regras_snapshot ADD COLUMN IF NOT EXISTS value_snapshot VARCHAR(255);
UPDATE orcamento_regras_snapshot SET expression_snapshot=COALESCE(expression_snapshot,expressao), value_snapshot=COALESCE(value_snapshot,valor_aplicado);
ALTER TABLE orcamento_regras_snapshot ALTER COLUMN expression_snapshot SET NOT NULL;
ALTER TABLE orcamento_regras_snapshot ALTER COLUMN value_snapshot SET NOT NULL;

ALTER TABLE estoque_retals ADD COLUMN IF NOT EXISTS material_code VARCHAR(50);
ALTER TABLE estoque_retals ADD COLUMN IF NOT EXISTS length_mm INTEGER;
ALTER TABLE estoque_retals ADD COLUMN IF NOT EXISTS quantity INTEGER NOT NULL DEFAULT 1;
ALTER TABLE estoque_retals ADD COLUMN IF NOT EXISTS source_quote_code VARCHAR(40);
ALTER TABLE estoque_retals ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
UPDATE estoque_retals SET material_code=COALESCE(material_code,perfil,'LEGACY'), length_mm=COALESCE(length_mm,ROUND(comprimento_mm)::INTEGER), source_quote_code=COALESCE(source_quote_code,(SELECT o.code FROM orcamentos o WHERE o.id=estoque_retals.origem_orcamento_id));
ALTER TABLE estoque_retals ALTER COLUMN material_code SET NOT NULL;
ALTER TABLE estoque_retals ALTER COLUMN length_mm SET NOT NULL;

CREATE TABLE IF NOT EXISTS catalogo_precos (id BIGSERIAL PRIMARY KEY, material_code VARCHAR(50) NOT NULL, description VARCHAR(160) NOT NULL, variant VARCHAR(40) NOT NULL DEFAULT 'PADRAO', unit VARCHAR(20) NOT NULL, price NUMERIC(14,4) NOT NULL DEFAULT 0 CHECK(price>=0), supplier VARCHAR(120), active VARCHAR(20) NOT NULL DEFAULT 'ATIVO');
ALTER TABLE catalogo_precos ADD COLUMN IF NOT EXISTS variant VARCHAR(40) NOT NULL DEFAULT 'PADRAO';
CREATE TABLE IF NOT EXISTS historico_precos (id BIGSERIAL PRIMARY KEY, material_code VARCHAR(50) NOT NULL, variant VARCHAR(40) NOT NULL DEFAULT 'PADRAO', price NUMERIC(14,4) NOT NULL CHECK(price>=0), unit VARCHAR(20) NOT NULL, supplier VARCHAR(120), valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(), source VARCHAR(120) NOT NULL DEFAULT 'CADASTRO');
ALTER TABLE historico_precos ADD COLUMN IF NOT EXISTS variant VARCHAR(40) NOT NULL DEFAULT 'PADRAO';

CREATE TABLE IF NOT EXISTS orcamento_precos_snapshot (id BIGSERIAL PRIMARY KEY, quote_id BIGINT NOT NULL REFERENCES orcamentos(id) ON DELETE CASCADE, material_code VARCHAR(50) NOT NULL, variant VARCHAR(40) NOT NULL, unit VARCHAR(20) NOT NULL, unit_price NUMERIC(14,4) NOT NULL DEFAULT 0, supplier VARCHAR(120));
CREATE TABLE IF NOT EXISTS orcamento_formacao_preco_snapshot (id BIGSERIAL PRIMARY KEY, quote_id BIGINT NOT NULL REFERENCES orcamentos(id) ON DELETE CASCADE, method VARCHAR(20) NOT NULL, material_cost NUMERIC(14,2) NOT NULL DEFAULT 0, labor_total NUMERIC(14,2) NOT NULL DEFAULT 0, indirect_variable NUMERIC(14,2) NOT NULL DEFAULT 0, indirect_fixed NUMERIC(14,2) NOT NULL DEFAULT 0, freight NUMERIC(14,2) NOT NULL DEFAULT 0, tax_percent NUMERIC(8,4) NOT NULL DEFAULT 0, tax_amount NUMERIC(14,2) NOT NULL DEFAULT 0, target_margin_percent NUMERIC(8,4), target_markup_percent NUMERIC(8,4), base_cost NUMERIC(14,2) NOT NULL DEFAULT 0, sale_price NUMERIC(14,2) NOT NULL DEFAULT 0, profit NUMERIC(14,2) NOT NULL DEFAULT 0, effective_margin_percent NUMERIC(8,4) NOT NULL DEFAULT 0, effective_markup_percent NUMERIC(8,4) NOT NULL DEFAULT 0);

CREATE INDEX IF NOT EXISTS idx_orcamentos_model_code ON orcamentos(model_code);
CREATE INDEX IF NOT EXISTS idx_quote_items_quote ON orcamento_itens(orcamento_id);
CREATE INDEX IF NOT EXISTS idx_quote_rules_quote ON orcamento_regras_snapshot(orcamento_id);
CREATE INDEX IF NOT EXISTS idx_retals_material_status ON estoque_retals(material_code,status);
CREATE INDEX IF NOT EXISTS idx_price_catalog_material_variant ON catalogo_precos(material_code,variant);
CREATE INDEX IF NOT EXISTS idx_price_history_material_variant ON historico_precos(material_code,variant,valid_from DESC);
CREATE INDEX IF NOT EXISTS idx_quote_price_snapshot_quote ON orcamento_precos_snapshot(quote_id);
CREATE INDEX IF NOT EXISTS idx_quote_pricing_snapshot_quote ON orcamento_formacao_preco_snapshot(quote_id);
