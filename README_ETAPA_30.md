# Etapa 30 — Orçamento Completo

Foi criado o endpoint de orquestração `/orcamento-completo`, reunindo em uma única resposta:
1. entrada e normalização de medidas;
2. motor técnico do MOD-001;
3. custo completo;
4. formação de preço;
5. planejamento de chapa de vidro quando o formato da chapa é informado.

A etapa não inventa preços. Sem preços de materiais, o orçamento fica explicitamente provisório.

O endpoint é uma ponte para a interface SMART. Ainda não é a interface final nem substitui a validação física.

Regras preservadas: MOD-001 2 folhas; MP-352 somente 4 folhas; mm inteiro; cm com uma casa decimal; folga de vidro 3,5 mm por lado.
