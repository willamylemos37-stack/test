# Etapa 39 — Workflow transacional

## Fluxo formal
ENVIADO -> APROVADO -> reserva ATIVA -> produção -> consumo -> CONSUMIDA.

## Atomicidade
O planejador verifica todas as linhas antes de qualquer mutação. Se uma linha não tiver saldo suficiente, nenhuma reserva deve ser efetivada.

## PostgreSQL
Na implementação de persistência, a reserva deverá usar uma única transação e bloqueio das linhas de estoque (`SELECT ... FOR UPDATE`) antes da revalidação do saldo. O planejamento puro desta etapa não substitui o bloqueio do banco.

## Regra de segurança
company_id deve vir do contexto autenticado no endpoint, nunca de um campo confiado enviado pelo cliente.
