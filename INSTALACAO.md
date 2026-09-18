# Instalação local

## Requisitos
Python 3.11+ recomendado.

## Ambiente
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testar
```bash
pytest -q
```

## CORS
Defina `CORS_ORIGINS` com os endereços que realmente usarão a API, separados por vírgula.
Exemplo local:
`CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5500`

Não usar `*` em ambiente com autenticação/credenciais.
