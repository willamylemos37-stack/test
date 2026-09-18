# Guia rápido — Android

## O que o Android consegue abrir
- `SMART_ESQUADRIAS_APP_v5_12_ETAPA_31.html`: abrir no navegador para visualizar a interface.
- `.pdf`: abrir normalmente.
- `.zip`: extrair pelo aplicativo de arquivos.

## Para usar a interface SMART com a API
O HTML precisa alcançar uma API HTTP. Abrir o HTML no celular, sozinho, não executa o backend Python.

Fluxo recomendado:
1. Rodar o backend Python em um computador/servidor.
2. Descobrir o endereço IP local desse computador.
3. Configurar no campo API do HTML algo como `http://IP_DO_SERVIDOR:8000`.
4. Garantir que o firewall permita a porta 8000 na rede local.
5. Manter CORS configurado com `CORS_ORIGINS`.

## Importante
O projeto ainda não é um aplicativo Android nativo. A interface atual é um protótipo web. O próximo passo de produto é colocar a API em um servidor acessível e transformar a interface em PWA/app.
