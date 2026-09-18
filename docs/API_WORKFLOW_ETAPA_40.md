# Etapa 40 — API do workflow

Endpoints de domínio expostos:
- POST /workflow/aprovar
- POST /workflow/iniciar-producao
- POST /workflow/concluir-producao

## Estado
Esta etapa expõe o fluxo na API para testes e integração futura. A persistência transacional de reserva/consumo ainda deve ser ligada ao repositório PostgreSQL.

## Regra
Não considerar estes endpoints como produção pública antes da autenticação/autorização por empresa e da transação com bloqueio de estoque.
