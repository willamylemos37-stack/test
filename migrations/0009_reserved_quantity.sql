ALTER TABLE estoque_itens
ADD COLUMN IF NOT EXISTS reserved_quantity NUMERIC(14,3) NOT NULL DEFAULT 0;

ALTER TABLE estoque_itens
ADD CONSTRAINT ck_estoque_reserved_qty_valid
CHECK (reserved_quantity >= 0 AND reserved_quantity <= quantity);

CREATE INDEX IF NOT EXISTS ix_estoque_available_lookup
ON estoque_itens(company_id, material_code, status, reserved_quantity);
