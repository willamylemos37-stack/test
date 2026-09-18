# Etapa 45 — Isolamento do catálogo de preços

- `/precos` e consulta de preços agora exigem autenticação.
- Preços cadastrados por API recebem `company_id` derivado do token.
- `PriceCatalog` e `PriceHistory` ganharam `company_id`.
- Migração PostgreSQL: `0010_tenant_prices.sql`.
- Registros legados permanecem com `company_id = NULL`; não são atribuídos automaticamente a uma empresa.
- Compatibilidade aditiva para banco SQLite de desenvolvimento foi incluída.
- O fluxo de cálculo sem persistência continua disponível; a proteção dos endpoints persistidos será ampliada gradualmente.
