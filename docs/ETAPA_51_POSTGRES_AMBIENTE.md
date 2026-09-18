# Etapa 51 — Ambiente PostgreSQL reproduzível

## Objetivo
Preparar uma execução reproduzível do PostgreSQL real para a bateria de concorrência da Etapa 50, sem substituir os testes funcionais em SQLite.

## Entregas
- `docker-compose.yml` com PostgreSQL 16 Alpine e healthcheck.
- `.env.postgres.example` com configuração de teste local.
- diretório canônico `database/migrations/` contendo as migrações 0001–0012.
- `scripts/wait_postgres.py` para aguardar o banco.
- `scripts/postgres_test.sh` para subir banco, aplicar migrações e executar testes marcados `postgres`.
- teste estrutural que garante a sequência completa das migrações.
- versão 5.33.0.

## Execução
1. Copie `.env.postgres.example` para `.env` e troque a senha.
2. Execute `docker compose up -d postgres`.
3. Defina `DATABASE_URL` conforme o `.env`.
4. Execute `python scripts/migrate.py`.
5. Execute `PYTHONPATH=. pytest -q -m postgres`.

Ou use `scripts/postgres_test.sh` para automatizar a sequência.

## Segurança
As credenciais do exemplo são somente para desenvolvimento local. Não reutilizar a senha do exemplo em produção. Em produção, usar segredo externo/gerenciador de segredos, TLS, backup e política de acesso de rede.

## Critério de validação
A concorrência real só é considerada validada quando os testes `postgres` forem executados contra um servidor PostgreSQL efetivo. A existência do Compose e dos testes não é evidência de concorrência já executada.
