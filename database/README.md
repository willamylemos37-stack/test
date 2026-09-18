# Banco de dados — Etapa 34

## Estratégia
- PostgreSQL é o banco alvo de produção.
- O schema é versionado por migrações SQL ordenadas.
- Cada migração é transacional e registrada em `schema_migrations` com SHA-256.
- Não editar uma migração já aplicada; criar outra migração.
- O `Base.metadata.create_all()` fica reservado ao ambiente de desenvolvimento/testes via `AUTO_CREATE_SCHEMA=true`.
- Preços reais nunca entram nas migrações.

## Migrações
- `0001_baseline_v5_15.sql`: schema canônico para instalação nova.
- `0002_upgrade_legacy_v4_6_to_v5_15.sql`: extensão não destrutiva para bancos derivados do schema antigo.
- `0003_seed_model_001.sql`: cadastro técnico inicial do MOD-001, sem MP-352.

## Execução
Defina `DATABASE_URL` para PostgreSQL e execute:

```bash
python scripts/migrate.py
```

Para um banco novo, a sequência cria o schema, índices, constraints e cadastro técnico inicial.

## Compatibilidade
A tabela legada `estoque_retals` é mantida deliberadamente nesta etapa. A padronização do nome será feita somente em uma migração futura que também altere o ORM, evitando quebra silenciosa.
