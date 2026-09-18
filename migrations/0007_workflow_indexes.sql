CREATE INDEX IF NOT EXISTS ix_reserva_status_company ON estoque_reservas(company_id,status);
CREATE INDEX IF NOT EXISTS ix_op_company_model_status ON ordens_producao(company_id,model_code,status);
