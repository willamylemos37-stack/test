# Auditoria e revisão — v5.14

## Resultado
- 38 testes automatizados: PASSANDO.
- Suíte com `-W error::DeprecationWarning`: PASSANDO.
- Compilação Python: PASSANDO.
- Teste de integração em SQLite temporário: PASSANDO.
- CORS testado com origem configurada: PASSANDO.

## Correções realizadas
1. Migração de FastAPI `on_event` para `lifespan`.
2. Datas SQLAlchemy migradas de `datetime.utcnow()` para datetime UTC com timezone.
3. CORS deixou de usar `*` e passou a ser controlado por `CORS_ORIGINS`.
4. Validação de altura em mm corrigida nos endpoints.
5. Campos de largura/altura dos schemas passaram a exigir valores positivos.
6. MOD-001 rejeita larguras que produziriam meia folha fracionária em mm, evitando truncamento silencioso.
7. Snapshot de preços passou a ser produzido pelo cálculo de custo e gravado ao formar preço do orçamento.
8. Relacionamentos de snapshots foram ajustados com `back_populates`.
9. Endpoint integrado `/orcamento-completo` foi testado de ponta a ponta.
10. Testes de regressão do Modelo 001 foram ampliados.

## Arquitetura atual
Entrada → validação → cálculo técnico → perfis/cortes → vidro → acessórios → custo → formação de preço → orçamento/histórico → interface SMART.

## Pontos ainda não considerados encerrados
- validação física na bancada;
- cadastro de preços reais;
- solver 2D exato para chapas de vidro;
- uso de PostgreSQL de produção;
- autenticação e autorização;
- deploy público;
- PWA/app final;
- documentos automáticos ligados ao fluxo final;
- migrações formais para evolução de schema.

## Observação importante
A tabela histórica `estoque_retals` possui nome legado. Não foi renomeada silenciosamente para evitar quebrar bancos existentes. Uma migração futura poderá padronizar o nome.

## Estado
O backend está em condição de protótipo técnico integrado e significativamente mais robusto, mas ainda não deve ser tratado como software de produção sem as pendências acima.
