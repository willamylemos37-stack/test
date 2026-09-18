# Etapa 29 — Otimização de Vidro / Chapas

## Status
CONCLUÍDA — testes automatizados e compilação passaram.

## Implementado
- Peças de vidro em mm e quantidades.
- Formatos de chapa cadastráveis.
- Kerf configurável.
- Rotação das peças.
- Planejamento heurístico por linhas.
- Quantidade de chapas, área comprada, área utilizada, sobra e aproveitamento.
- Comparação entre formatos.
- Seleção por custo somente quando os preços dos formatos forem fornecidos.
- Sem preço, nenhuma escolha comercial é inventada.

## Limitação
O algoritmo GREEDY_ROW é heurístico e não garante ótimo global 2D. A evolução para um solver mais sofisticado poderá ser feita após testes reais.

## Regras preservadas
MOD-001 = 2 folhas; MP-352 somente em modelos de 4 folhas; mm inteiro; cm com uma casa decimal; vidro com 3,5 mm por lado (7 mm total), pendente de validação física.

## Próxima etapa
Etapa 30 — integrar vidro/chapas ao orçamento e à interface SMART.
