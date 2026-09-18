# Auditoria e revisão — v5.14

- 38 testes automatizados: PASSANDO.
- Testes com `DeprecationWarning` tratado como erro: PASSANDO.
- Compilação Python: PASSANDO.
- Integração ponta a ponta em SQLite temporário: PASSANDO.
- CORS com origem configurada: PASSANDO.

## Correções
- FastAPI lifespan no lugar de on_event.
- datetime UTC timezone-aware.
- CORS controlado por `CORS_ORIGINS`.
- Validação de altura em mm corrigida.
- Largura/altura positivas nos schemas.
- Largura que produziria meia folha fracionária rejeitada para evitar truncamento silencioso.
- Snapshots de preços integrados ao orçamento.
- Relacionamentos de snapshots corrigidos.
- Testes de regressão ampliados.

## Pendências
Validação física; preços reais; solver 2D exato; PostgreSQL de produção; autenticação; deploy; PWA/app final; documentos ligados ao fluxo; migrações formais.

A tabela legada `estoque_retals` não foi renomeada silenciosamente para evitar quebra de banco existente.
