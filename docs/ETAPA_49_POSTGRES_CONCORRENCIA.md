# Etapa 49 — PostgreSQL real e concorrência

## Objetivo
Preparar e registrar a validação do mecanismo transacional de estoque em PostgreSQL real.

## O que foi feito
- Mantido `SELECT ... FOR UPDATE` no repositório transacional de estoque.
- Criado teste de concorrência específico para PostgreSQL em `tests/test_postgres_concurrency.py`.
- O teste inicia duas sessões independentes tentando reservar simultaneamente a mesma unidade física.
- Critério de aprovação: exatamente uma reserva é confirmada e a outra falha, sem ultrapassar o estoque disponível.
- O teste é deliberadamente marcado como `skip` quando `DATABASE_URL` não aponta para PostgreSQL, evitando declarar uma validação que não ocorreu.

## Resultado no ambiente atual
A suíte funcional local permanece verde. O ambiente desta etapa não possui servidor PostgreSQL nem driver `psycopg` instalado no runtime de execução, portanto a concorrência real **não foi declarada como validada**.

## Procedimento quando PostgreSQL estiver disponível
1. Criar banco isolado de teste.
2. Definir `DATABASE_URL=postgresql+psycopg://...`.
3. Aplicar as migrations.
4. Executar `PYTHONPATH=. pytest -q tests/test_postgres_concurrency.py`.
5. Executar a suíte completa.
6. Registrar o resultado sem substituir a evidência por teste SQLite.

## Decisão arquitetural
SQLite continua aceito para desenvolvimento/testes funcionais. PostgreSQL é o banco de referência para concorrência, bloqueio de linhas e ambiente multiusuário.
