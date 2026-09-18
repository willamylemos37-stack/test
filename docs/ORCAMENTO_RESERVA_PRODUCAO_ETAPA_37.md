# Etapa 37 — Orçamento, reserva e produção

## Fundação
- reservas pertencem a uma empresa;
- uma reserva possui linhas ligadas a itens de estoque;
- status: ATIVA, CANCELADA, CONSUMIDA;
- transições são explícitas;
- linhas não podem repetir o mesmo item na mesma reserva;
- quantidade reservada precisa ser positiva;
- acesso entre empresas é rejeitado.

## Regra operacional futura
A baixa definitiva deve ocorrer em transação de banco com bloqueio apropriado (ex.: SELECT ... FOR UPDATE), revalidando saldo no momento da reserva/consumo. O serviço atual fornece as regras de domínio; a operação concorrente real será implementada no repositório.

## Fluxo
Orçamento -> aprovação -> reserva -> ordem de produção -> consumo -> retalhos.
