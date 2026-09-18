# Etapa 54 — Observabilidade e auditoria operacional

## Objetivo
Adicionar rastreabilidade operacional sem armazenar segredos, senhas ou tokens.

## Entregas
- Entidade `AuditEvent` / tabela `auditoria_eventos`.
- Migration PostgreSQL `0013_audit_events.sql` no diretório canônico e no legado espelhado.
- Registro de `LOGIN_SUCESSO` e `LOGIN_FALHA`.
- Registro de `OP_CRIADA`.
- Eventos associados à empresa e usuário quando conhecidos.
- `request_id` e endereço IP suportados no modelo de auditoria.
- Headers de segurança e `X-Request-ID` mantidos.
- `Cache-Control: no-store` aplicado às respostas da API para evitar cache de dados operacionais.
- Suíte atualizada para a versão 5.36.0.

## Segurança
O evento de login falho registra somente o e-mail informado e metadados operacionais; nunca registra senha, token ou hash de senha.

## Limites conhecidos
A auditoria ainda não é um SIEM e não substitui logs externos/imutáveis. Retenção, rotação e exportação devem ser configuradas na infraestrutura de produção.

## Validação
90 testes passaram e 1 teste foi mantido como skip por depender de PostgreSQL real.
