# Etapa 53 — Operação, backup e erros

## Objetivo
Preparar a API para operação controlada, sem confundir backup com disponibilidade.

## Backup PostgreSQL
`python scripts/backup_postgres.py [arquivo.dump]`

O script usa `pg_dump` em formato custom, adequado para restauração seletiva e automação.
O arquivo de saída não deve ser colocado no repositório.

## Restauração
`RESTORE_CONFIRM=YES python scripts/restore_postgres.py arquivo.dump`

A confirmação explícita existe porque a restauração pode sobrescrever dados. Faça teste de restauração em ambiente separado antes de considerar o backup válido.

## Migrações
`python scripts/migrate.py` aplica apenas migrações ausentes e verifica SHA-256 das já aplicadas.

## Erros
A API mantém mensagens de negócio específicas em HTTPException e registra exceções não tratadas com `X-Request-ID`. Não expor stack trace ou segredos ao cliente.

## Checklist de produção
- PostgreSQL com backup automatizado e retenção definida.
- Teste periódico de restauração.
- `AUTO_CREATE_SCHEMA=false`.
- `APP_SECRET_KEY` forte e fora do código.
- TLS no proxy.
- Rate limit global no gateway/WAF.
- Monitorar `/health` e `/ready`.
- Guardar logs sem senhas, tokens ou dados sensíveis.
