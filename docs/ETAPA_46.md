# Etapa 46 — Fluxo transacional persistido de estoque → produção

- Ordem de produção agora pode apontar para `reservation_id`.
- `POST /producao/{id}/reservar` cria a reserva com alocações explícitas e vincula a OP na mesma transação.
- `POST /producao/{id}/iniciar` exige OP ABERTA + reserva ATIVA da mesma empresa.
- `POST /producao/{id}/concluir` consome a reserva e conclui a OP dentro da mesma transação.
- Todos os recursos são filtrados pelo `company_id` derivado do token.
- PostgreSQL continua sendo o ambiente necessário para validar concorrência real com row locks.
- Não foi implementada alocação automática de barras por comprimento: a reserva recebe `item_id` e quantidade explícitos, evitando inventar uma regra de corte.
