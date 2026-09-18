-- Etapa 57: domínio de produtos para permitir expansão além de esquadrias.
ALTER TABLE modelos ADD COLUMN IF NOT EXISTS product_type VARCHAR(30) NOT NULL DEFAULT 'ESQUADRIA';
CREATE INDEX IF NOT EXISTS ix_modelos_product_type ON modelos(product_type);
