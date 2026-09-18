# Etapa 48 — Fluxo persistido Orçamento → OP → Reserva → Produção

## Objetivo
Consolidar o fluxo operacional persistido e tornar a Ordem de Produção independente do estado futuro do orçamento por meio de snapshots técnicos completos.

## Alterações
- API versionada em `5.30.0`.
- `GET /producao/{production_id}` consulta OP somente dentro da empresa autenticada.
- Ao criar OP a partir de orçamento, `technical_snapshot` passa a guardar:
  - identificação do orçamento;
  - peças técnicas do orçamento;
  - snapshots das regras técnicas.
- `QuoteResponse` expõe `company_id` quando disponível.
- Mantida a regra de derivar `company_id` do token, nunca do cliente.
- Mantida a reserva explícita por `item_id` + quantidade; nenhuma alocação automática por comprimento foi inventada.

## Fluxo validado
1. Empresa A cria orçamento.
2. Empresa B não acessa o orçamento.
3. Empresa A cria OP a partir do orçamento.
4. OP recebe snapshot técnico.
5. OP recebe reserva explícita.
6. OP inicia produção somente com reserva ATIVA.
7. OP conclui produção e consome a reserva na mesma transação.
8. Empresa B não consegue acessar a OP nem seus recursos vinculados.

## Integridade
- O vínculo entre OP e orçamento respeita `company_id`.
- O vínculo entre OP e reserva respeita `company_id`.
- Operações de reserva/consumo usam o repositório transacional.
- PostgreSQL continua sendo o ambiente necessário para validação real de concorrência com `FOR UPDATE`.
