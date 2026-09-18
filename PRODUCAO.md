# Operação de produção — Esquadrias API v5.35

## Variáveis obrigatórias
- `APP_ENV=production`
- `DATABASE_URL=postgresql+psycopg://...`
- `APP_SECRET_KEY=<segredo forte e exclusivo>`
- `AUTO_CREATE_SCHEMA=false`
- `CORS_ORIGINS=https://seu-dominio.example`

## Banco
1. Suba PostgreSQL.
2. Execute `python scripts/migrate.py`.
3. Verifique `GET /ready`.

## Execução
`uvicorn app.main:app --host 0.0.0.0 --port 8000`

Em produção, TLS deve ser terminado no proxy/reverse proxy. O proxy também deve aplicar rate limit global, limites de corpo, timeout e logs de acesso.

## Health
- `/health`: processo responde.
- `/ready`: processo responde e consegue consultar o banco.

## Segurança
- Documentação OpenAPI fica desabilitada em produção por padrão.
- Headers de segurança são adicionados pela API.
- `X-Request-ID` permite correlacionar logs.
- Login possui limite local de proteção; para múltiplas réplicas, o limite deve ser aplicado no gateway/WAF.
