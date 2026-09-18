# Etapa 60 — manutenção de dependências

## Objetivo
Tornar a instalação do backend reproduzível para ambientes que recebem versões atuais do Starlette/FastAPI.

## Problema observado
A instalação do `requirements.txt` do v5.41 em um ambiente Windows com Python 3.14 concluiu, porém a coleta do pytest falhou porque o `TestClient` do Starlette exigia o pacote opcional `httpx2`.

## Correção
O `httpx2` passou a ser dependência explícita em `requirements.txt`.

## Escopo
Esta manutenção não altera:
- fórmulas técnicas;
- regras de vidro;
- regras de MP-352;
- cálculo de custos;
- PostgreSQL/migrations;
- isolamento multiempresa;
- workflow Orçamento → OP → Reserva → Produção → Consumo;
- contratos funcionais da API.

## Validação
Após instalar `httpx2`, a suíte local apresentou **103 passed, 1 skipped, 1 warning**. O warning é de depreciação do `BlockingPortal` no Starlette e não causou falha.

## Próximo passo técnico
Prosseguir para a validação com PostgreSQL real na máquina local, incluindo migrations e os testes marcados para PostgreSQL.
