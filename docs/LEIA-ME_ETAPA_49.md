# Sistema de Esquadrias — Etapa 49 / v5.31

## Estado
Preparação formal para validação PostgreSQL real e concorrência.

## Marco desta etapa
O mecanismo transacional já utiliza bloqueio pessimista por linha (`SELECT ... FOR UPDATE`) quando executado em PostgreSQL. Nesta etapa foi criado um teste concorrente real, mas ele só executa quando `DATABASE_URL` aponta para PostgreSQL.

## Evidência disponível
- Suíte funcional local anterior: 81/81 testes.
- Novo teste PostgreSQL: condicionado à disponibilidade de PostgreSQL real.
- No ambiente atual, PostgreSQL não está disponível; portanto não há alegação de teste concorrente executado.

## Regra de segurança
Não considerar SQLite como prova de concorrência PostgreSQL.

## Continuidade técnica
O próximo passo é executar o teste em um PostgreSQL real e, depois, revisar isolamento transacional, índices e constraints observados no banco real.

## Regras técnicas preservadas
- Dimensões internas em mm.
- Entrada em cm: uma casa decimal.
- Entrada em mm: inteiro.
- MOD-001: 2 folhas.
- MP-352: somente modelos de 4 folhas; não pertence ao MOD-001.
- BG-202: cadastro único com regras horizontal/vertical distintas.
- Folga do vidro: 3,5 mm por lado, provisória e ajustável.
