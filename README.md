## v5.44 — Etapa 61
Correção da cadeia de migrations para PostgreSQL novo: baseline de empresas/usuários e correção do índice de movimentos.

# Smart Esquadrias Backend — v5.51.0

Backend do sistema Smart Esquadrias: cálculo técnico, custos, formação de preço, orçamento persistido, estoque, reservas, ordens de produção, auditoria e preparação para PostgreSQL.

## Estado atual

## Etapa 61 — compatibilidade de migration PostgreSQL (v5.43)
- Corrigido o runner de migrations para bancos PostgreSQL novos: a migration legada `0002_upgrade_legacy_v4_6_to_v5_15.sql` é marcada como aplicada sem execução quando a estrutura nova da `0001` já está presente.
- Em bancos legados que ainda possuem as colunas da estrutura v4.6, a `0002` continua sendo executada normalmente.
- Nenhuma regra técnica, cálculo, preço, workflow ou contrato de API foi alterado.
- Objetivo: permitir a instalação limpa da estrutura canônica atual sem tentar executar uma migração de compatibilidade sobre tabelas já modernas.


## Etapa 62 — consolidação técnica do MOD-001 e PostgreSQL (v5.45)
- Incluído `httpx2` no `requirements.txt`, necessário para o `TestClient` da versão atual do Starlette.
- A mudança corrige a instalação limpa em ambientes que recebem as dependências atuais sem depender de instalação manual posterior.
- Nenhuma regra de cálculo, banco, workflow ou contrato de API foi alterada nesta etapa.
- Validação local: suíte funcional aprovada após a instalação de `httpx2`.

- Python + FastAPI + SQLAlchemy + PostgreSQL como banco de referência.
- SQLite permitido apenas para desenvolvimento/testes funcionais.
- Multiempresa por `company_id` em preços, orçamentos, estoque, reservas e produção.
- Fluxo persistido: **Orçamento → OP → Reserva → Produção → Consumo**.
- Snapshots técnicos preservam o estado usado na criação da OP/orçamento.
- Auditoria operacional e `X-Request-ID`.
- Migrations canônicas em `database/migrations`.
- Concorrência real requer execução contra PostgreSQL.

## Executar testes
```bash
pip install -r requirements.txt
pytest -q
```

O `pytest.ini` já define `pythonpath = .`, portanto o teste é reproduzível independentemente do `PYTHONPATH` herdado do ambiente.

## PostgreSQL local
```bash
./scripts/postgres_test.sh
```

O script sobe PostgreSQL, aguarda disponibilidade, aplica migrations e executa os testes marcados como `postgres`.

## Produção
Defina `APP_ENV=production`, `DATABASE_URL` apontando para PostgreSQL, `APP_SECRET_KEY` forte e `AUTO_CREATE_SCHEMA=false`. Aplique as migrations antes de iniciar a API.

## Segurança
- Senhas com PBKDF2-HMAC-SHA256.
- Tokens HMAC-SHA256 com expiração.
- Isolamento por empresa derivado do token, nunca do payload.
- Rate limit básico de login por processo; em produção, complemente com proxy/WAF ou mecanismo distribuído.
- Headers de segurança e documentação OpenAPI desabilitada em produção.
- Auditoria não grava senhas, tokens ou hashes.

## Regra técnica crítica
**MP-352 é exclusivo dos modelos de 4 folhas e não pode aparecer no Modelo 001 de 2 folhas.**

## Limites conhecidos
- A concorrência PostgreSQL ainda precisa ser executada em um servidor PostgreSQL real.
- Alocação automática de barras por comprimento não foi inventada; a reserva usa `item_id` e quantidade explícitos.
- Modelos e regras técnicas ainda são globais; a parametrização completa de modelos é uma próxima camada do produto.


## Etapa 56 — Motor de modelos e validação (v5.38)
- O cálculo agora passa por um registro de modelos (`calculate_model`).
- O código do modelo é normalizado e modelos não cadastrados são rejeitados pelo motor.
- `calculate_model_001` permanece como compatibilidade explícita do MOD-001.
- A validação dimensional não mantém uma segunda lista manual de modelos, evitando divergência entre validação e motor.
- O orçamento persistido grava o `model_code` efetivamente calculado.
- Regra crítica preservada: MP-352 não pertence ao MOD-001 de 2 folhas.
- Suíte: 98 testes passaram; 1 teste PostgreSQL foi ignorado por ausência de PostgreSQL real.


## Etapa 57 — famílias e expansão futura
- O catálogo possui seções para Esquadrias, Portões, Grades, Boxes, Guarda-corpos, Fechamentos, Corrimãos e Outros.
- Apenas as famílias atualmente desenvolvidas devem ser tratadas como ativas; as demais ficam `EM_BREVE`, sem regras técnicas ou preços inventados.
- Endpoint `/catalogo/publico` foi preparado para uma futura vitrine pública e expõe somente código, nome e status.
- A futura vitrine poderá permitir ao cliente escolher modelo, informar medidas e receber somente o valor final; essa experiência não foi ativada nem expõe custos internos nesta etapa.
- A primeira validação comercial deverá usar somente os modelos tecnicamente comprovados (2 e 4 folhas quando ambos estiverem formalmente cadastrados).


## Etapa 59 — Regra definitiva do vidro

Para os dois modelos atualmente validados, o vidro segue a regra técnica confirmada:
- largura do vidro = comprimento do MP-309 − 8 mm;
- altura do vidro = comprimento do MP-300 − 78 mm;
- os 78 mm da altura correspondem a 35 mm de cada MP-309 + 8 mm de folga total.

A regra foi registrada como `VIDRO78` e permanece separada do cálculo de preço.


## v5.48 — Correção oficial do MP-309
- MOD-001 (2 folhas): MP-309 = `(L - 105) / 2`, 4 peças por janela.
- Regra para 4 folhas cadastrada: MP-309 = `(L - 178) / 4`, 8 peças por janela quando o modelo de 4 folhas for ativado.
- O motor rejeita larguras que produzam fração de milímetro; não arredonda.
- O vidro de 2 folhas continua usando largura = MP-309 - 8 mm e altura = H - 118 mm.

## v5.48 — MOD-002 4 folhas

- Cadastro inicial do MOD-002 — Janela Módulo Prático 4 Folhas.
- MP-309: `(L - 178) / 4`, 8 peças.
- MP-352: `H - 40`, exclusivo do MOD-002.
- BG-202 segue as regras dimensionais definidas.
- Cortes fracionados em milímetros são rejeitados.
- O cálculo do vidro segue a regra consolidada do projeto.
- Quantidades estruturais do MOD-002 foram cadastradas simetricamente como base de teste e permanecem sujeitas à confirmação física antes de uso comercial.

## v5.50 — Escovas ajustadas
- Escova 5 mm: 2 folhas = 1 altura + 4 larguras; 4 folhas = 2 alturas + 4 larguras.
- Escova 7 mm: 2 alturas em ambos os modelos, vinculadas aos 2 MP-360.
- Nenhuma migration adicional: alteração exclusiva do motor de cálculo.
