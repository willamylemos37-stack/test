# Etapa 43 — Contexto autenticado e isolamento por empresa

## Implementado
- contexto de usuário/empresa centralizado;
- validação obrigatória de ator;
- verificação de empresa do recurso;
- adaptador inicial para FastAPI.

## Importante
Os cabeçalhos do adaptador são apenas uma ponte de desenvolvimento e NÃO são uma autenticação segura. O endpoint público deverá extrair o contexto de um token assinado validado pelo sistema, e nunca confiar em `X-User-Id`/`X-Company-Id` enviados livremente pelo cliente.

## Próximo
Conectar o contexto ao token assinado existente e aos endpoints de orçamento, reserva e produção.
