CREATE INDEX IF NOT EXISTS ix_movimentos_item_time ON estoque_movimentos(item_id,timestamp);
CREATE INDEX IF NOT EXISTS ix_reserva_itens_reservation ON estoque_reserva_itens(reservation_id);
