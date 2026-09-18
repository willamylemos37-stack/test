# Etapa 41 — Fundação transacional

## Objetivo
Preparar o repositório para operações atômicas de reserva e consumo.

## Regra crítica
A validação de disponibilidade feita em memória é apenas planejamento. A implementação PostgreSQL deve, dentro da mesma transação:
1. selecionar os itens necessários;
2. bloquear as linhas com SELECT ... FOR UPDATE;
3. revalidar saldo;
4. gravar reserva;
5. gravar movimentos;
6. confirmar tudo ou fazer rollback.

## Concorrência
Não há garantia de concorrência real no SQLite. A validação definitiva deve ocorrer em PostgreSQL antes de produção.

## Segurança
company_id deve ser obtido do contexto autenticado.
