# Etapa 32 — Hardening inicial e operação local

Implementado:
- CORS configurável por variável de ambiente `CORS_ORIGINS`.
- Guia de instalação local.
- Guia de uso no Android.
- Execução documentada com Uvicorn.
- Testes preservados.

Limitações ainda existentes:
- autenticação não implementada;
- PostgreSQL de produção ainda não configurado;
- deploy público não realizado;
- interface continua protótipo web;
- validação física das fórmulas ainda pendente;
- preços reais ainda não cadastrados.

Próximas evoluções: autenticação/permissões, migrações formais, PostgreSQL de produção, PWA e fluxo de documentos.


## Revisão v5.14
38 testes passando, incluindo execução com deprecation warnings como erros e integração ponta a ponta em SQLite temporário.
