# Etapa 61 — Correção da cadeia de migrations PostgreSQL

A v5.44 corrige dois problemas encontrados na primeira instalação PostgreSQL limpa:

1. A baseline agora cria `empresas` e `usuarios` antes das migrations que possuem chaves estrangeiras para essas tabelas.
2. A migration `0008_transactional_workflow.sql` passa a indexar `estoque_movimentos.created_at`, coluna existente no schema, em vez de uma coluna `timestamp` inexistente.

A migration legada `0002_upgrade_legacy_v4_6_to_v5_15.sql` continua sendo ignorada somente quando o banco é identificado como schema novo.

## Estado
Esta etapa deve ser validada em banco PostgreSQL novo, desde a criação do banco até a última migration.
