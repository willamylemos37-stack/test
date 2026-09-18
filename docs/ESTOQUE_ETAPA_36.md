# Etapa 36 — Estoque transacional

O estoque passa a representar itens/lotes individuais, permitindo barras e retalhos com comprimento em mm, além de unidades.

## Princípios
- isolamento por `company_id`;
- movimentações históricas não são apagadas;
- status: DISPONIVEL, RESERVADO, CONSUMIDO, BLOQUEADO;
- retalho só é compatível quando pertence ao mesmo material e tem comprimento suficiente;
- quantidade e comprimento possuem constraints no banco.

## Próximo refinamento
Reserva transacional ligada a orçamento/ordem de produção, com baixa atômica e prevenção de dupla reserva.
