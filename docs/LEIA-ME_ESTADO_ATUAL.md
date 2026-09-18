# Estado atual do projeto — v5.44.0

## Etapa 61 — PostgreSQL
A cadeia de migrations foi revisada para instalação limpa: a baseline cria `empresas`/`usuarios` antes das tabelas multiempresa e o índice transacional usa `created_at`. A validação final em PostgreSQL real ainda deve ser executada.


## Marco
Etapa 48 — fluxo persistido Orçamento → OP → Reserva → Produção.

## Núcleo
MOD-001 (2 folhas) ativo. MP-352 permanece exclusivo de modelos de 4 folhas. Dimensões normalizadas internamente em mm; cm aceita uma casa decimal; mm somente inteiros.

## Estoque
Itens, movimentos, retalhos, reservas e consumo modelados. `reserved_quantity` separa saldo físico de saldo reservado.

## Transação
Reserva e consumo possuem revalidação dentro do escopo transacional e `SELECT ... FOR UPDATE` quando executados em PostgreSQL. Se já existir uma transação no chamador, o serviço usa SAVEPOINT.

## Limitações
Concorrência real ainda depende de PostgreSQL executável. Validação física das fórmulas ainda pendente. Sistema ainda não deve ser exposto publicamente sem completar autenticação/autorização, HTTPS, backup, observabilidade e revisão dos endpoints.

## Etapa 48
Orçamento persistido e OP agora formam um fluxo mais completo: a OP pode nascer de um orçamento do mesmo tenant, recebe snapshot técnico completo e pode ser consultada de forma autenticada. O ciclo de reserva, início e conclusão permanece transacional. A suíte desta etapa fecha em 81/81 testes.

## Etapa 51
O ambiente PostgreSQL foi tornado reproduzível: Compose local, healthcheck, arquivo de ambiente de exemplo, diretório canônico de migrações 0001–0012 e script único para subir banco, migrar e executar os testes de concorrência.

## Limitação atual
Este ambiente de desenvolvimento não possui Docker executável; portanto a bateria `postgres` continua pendente de execução real. Isso não é tratado como aprovação automática.
