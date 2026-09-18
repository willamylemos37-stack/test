-- Etapa 46: vincula ordem de produção à reserva de estoque.
ALTER TABLE ordens_producao ADD COLUMN IF NOT EXISTS reservation_id BIGINT REFERENCES estoque_reservas(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS ix_ordens_producao_reservation_id ON ordens_producao(reservation_id);
