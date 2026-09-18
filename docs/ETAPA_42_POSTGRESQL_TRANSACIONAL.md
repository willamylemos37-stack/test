# Etapa 42 — PostgreSQL transacional real

## Implementação
Foi criado o repositório transacional de estoque com:
- `with_for_update()` para PostgreSQL;
- revalidação do saldo dentro da transação;
- reserva atômica;
- consumo atômico;
- rollback integral em caso de insuficiência/inconsistência;
- isolamento por `company_id`;
- quantidade total separada de `reserved_quantity`.

## Importante
SQLite é usado somente para testes funcionais. `with_for_update()` não oferece a mesma semântica no SQLite. A concorrência real deve ser testada no PostgreSQL antes da abertura pública.

## Auditoria
Movimentos de RESERVA registram quantidade reservada; movimentos de CONSUMO registram a baixa física.

## Próximo
Integração do repositório com endpoints autenticados e testes de concorrência em PostgreSQL.
