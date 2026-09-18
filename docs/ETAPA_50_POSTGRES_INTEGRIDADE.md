# Etapa 50 — Bateria de concorrência e integridade transacional

## Objetivo
Ampliar a suíte específica de PostgreSQL para os cenários que podem causar dupla reserva, dupla baixa ou saldo inconsistente.

## Cobertura adicionada
- duas reservas simultâneas sobre a mesma unidade;
- dois consumos simultâneos da mesma reserva;
- reserva concorrente com consumo de uma reserva já existente;
- tentativa de reserva de item pertencente a outra empresa.

Todos os cenários usam sessões independentes e `SELECT ... FOR UPDATE` do repositório transacional. O objetivo é validar o comportamento do banco de referência, e não simular concorrência em SQLite.

## Resultado do ambiente desta etapa
A suíte funcional local foi executada sem o marcador `postgres`: **81 passaram e 1 foi ignorado** (o teste específico de PostgreSQL).

O runtime disponível nesta execução não possui servidor PostgreSQL nem driver `psycopg` instalado. Portanto, **a bateria PostgreSQL desta etapa foi preparada, mas não é declarada como executada/validada**.

## Critério de fechamento
A etapa só será considerada validada em ambiente PostgreSQL quando:
1. `DATABASE_URL` apontar para PostgreSQL real;
2. as migrations estiverem aplicadas em banco de teste isolado;
3. os quatro cenários passarem;
4. a suíte completa permanecer verde;
5. não houver saldo físico ou reservado negativo nem sobrescrição entre tenants.

## Versão
`5.32.0`

## Regra técnica preservada
MP-352 continua exclusivo dos modelos de 4 folhas e não pode aparecer no Modelo 001 de 2 folhas.
