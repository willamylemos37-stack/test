# Etapa 28 — Formação de Preço

## Objetivo
Transformar o custo técnico completo em preço de venda configurável, sem inventar preços reais.

## Fórmulas
- Base de custo = materiais + mão de obra + indiretos variáveis + indiretos fixos + frete.
- Margem-alvo: `Preço = Base / (1 - imposto - margem)`.
- Markup: `Preço = Base × (1 + markup) / (1 - imposto)`.
- Lucro = preço - base - imposto.
- Margem efetiva = lucro / preço.
- Markup efetivo = lucro / base.

## Regras
- Margem e markup são alternativas; não podem ser informados simultaneamente.
- Imposto é tratado como percentual do preço de venda.
- Mão de obra pode ser informada por unidade.
- Despesa indireta pode ter percentual e valor fixo.
- Frete pode ser informado como valor.
- Se houver preços faltantes, a formação final é bloqueada por padrão.
- `allow_provisional=true` permite apenas uma simulação provisória.
- Todos os valores monetários são arredondados para centavos.
- Nenhum preço de mercado foi inventado.

## Novos endpoints
- `POST /formar-preco` — simula/formaliza a formação para uma medida.
- `POST /orcamentos/{quote_id}/formar-preco` — grava custo/preço no orçamento e cria snapshot.
- `GET /orcamentos/{quote_id}/formacao-preco` — consulta snapshots da formação.

## Banco
Foi adicionada a migração `schema_pricing.sql` com:
- `orcamento_precos_snapshot`
- `orcamento_formacao_preco_snapshot`

## Validação
Testes específicos da formação de preço cobrem margem, markup, imposto, mão de obra, indiretos, frete, arredondamento e proteções matemáticas.

## Pendências
- Custos reais ainda dependem de cotações do usuário.
- A validação física das regras técnicas continua pendente.
- Otimização de vidro em chapas e plano de compra ficam para etapa posterior.
- Deprecações de FastAPI/SQLAlchemy serão limpas em etapa de hardening.
