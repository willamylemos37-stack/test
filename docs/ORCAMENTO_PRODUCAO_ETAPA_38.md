# Etapa 38 — Persistência e Ordem de Produção

## Princípio
O orçamento e a ordem de produção devem preservar snapshots do cálculo, evitando que alterações futuras de regras/preços modifiquem documentos históricos.

## Ordem de produção
Campos-base: empresa, orçamento de origem, referência, modelo, snapshot de entrada e snapshot técnico.

## Estados
ABERTA -> EM_PRODUCAO -> CONCLUIDA
ABERTA -> CANCELADA
EM_PRODUCAO -> CANCELADA

## Segurança
A empresa do recurso deve ser conferida contra a empresa do usuário autenticado. O cliente não deve poder escolher livremente company_id.

## Próximo passo
Implementar os endpoints transacionais de criação/aprovação/reserva e consumo, com vínculo entre orçamento, ordem de produção e reserva.
