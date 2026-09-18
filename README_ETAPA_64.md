# LEIA-ME — Etapa 65 / v5.47

## Correção oficial do MP-309

Data: 17/09/2026

### Regras fechadas
- Janela de 2 folhas: MP-309 = `(L - 105) / 2`; 4 peças por janela.
- Janela de 4 folhas: MP-309 = `(L - 178) / 4`; 8 peças por janela quando o modelo de 4 folhas for ativado.
- O motor não arredonda cortes: se o resultado não for inteiro em mm, a medida é rejeitada.
- Para o MOD-001, que é de 2 folhas, a regra usada pelo cálculo foi corrigida para `L105_2`.
- Vidro do MOD-001: largura = MP-309 - 8 mm; altura = H - 118 mm.

### Exemplo validado
Para 1203 x 1500 mm, 2 folhas:
- MP-309 = (1203 - 105) / 2 = 549 mm
- 4 peças de MP-309 por janela
- vidro = 541 x 1382 mm, 2 peças por janela
- para 30 janelas: 120 peças de MP-309 de 549 mm e 60 vidros de 541 x 1382 mm

### Banco
Migration `0018_mp309_rules_2_4_leaves.sql` cria/atualiza as regras `L105_2` e `L178_4` e atualiza o componente MP-309 do MOD-001 para `L105_2`.

### Testes
Suite local: **108 passed, 1 skipped**.

### Próximo passo
Substituir o projeto local pela v5.47, executar a migration e testar no Swagger `/calcular` o caso 1203 x 1500, quantidade 30. Depois disso, avançar para o motor de otimização de barras 3 m/6 m.
