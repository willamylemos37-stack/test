# Etapa 62 — consolidação das regras técnicas e PostgreSQL

O teste no PostgreSQL novo confirmou que a estrutura foi criada, mas o seed técnico do MOD-001 ainda refletia regras históricas. Esta etapa adiciona uma migration incremental e atualiza o motor de cálculo para as regras técnicas vigentes.

- MP-309: `(L - 103) / 4`
- BG-202 horizontal: `(L - 103) / 4`
- BG-202 vertical: `H - 134`
- Vidro: largura `MP-309 - 8 mm`; altura `MP-300 - 78 mm`
- MP-352 permanece fora do MOD-001 (2 folhas).
- Como as dimensões são inteiras em mm, larguras que não produzam corte horizontal inteiro são rejeitadas.

A migration `0016_model_001_technical_rules.sql` corrige bancos que já chegaram até a `0015` sem alterar migrations históricas.
