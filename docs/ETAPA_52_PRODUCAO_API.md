# Etapa 52 — Preparação da API para produção

Versão: 5.34.0

- Configuração explícita de ambiente de produção.
- Bloqueio de `AUTO_CREATE_SCHEMA` em produção.
- Exigência de `DATABASE_URL` e `APP_SECRET_KEY` em produção.
- OpenAPI/Swagger/ReDoc desabilitados em produção por padrão.
- Middleware de headers de segurança.
- `X-Request-ID` e logging estruturado básico por requisição.
- Endpoint `/ready` para readiness com consulta real ao banco.
- Proteção local de tentativas de login; limitação global continua responsabilidade do proxy/WAF em múltiplas réplicas.
- Guia `PRODUCAO.md` incluído no pacote.
