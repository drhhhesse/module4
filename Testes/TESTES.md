# Framework de Testes — Módulo 4

Framework configurado conforme **Plano de Testes** (Entrega 4). Pré-requisito da Aula 14.

## Setup

```bash
pip install -r requirements-dev.txt
```

## Executar

```bash
pytest                          # todos os testes
pytest -m unit                  # apenas unidade
pytest -m integration           # apenas integração
pytest -m negative              # apenas casos negativos
pytest --cov=src --cov-report=term-missing   # com cobertura (critério: ≥ 70%)
```

## Estrutura

```
tests/
├── conftest.py            # fixtures: mocks de Ollama, ChromaDB, PDFs de teste
├── test_sanity.py         # verifica que o framework está operacional
├── unit/                  # caixa-branca: PDFExtractor, GoNoGoService
└── integration/           # caixa-cinza: APIs de upload, chat RAG, auth
```

## Rastreabilidade

Cada teste referencia seu Caso de Teste (CT-001 a CT-016) no docstring,
conforme tabela de rastreabilidade do documento de Plano de Testes.
Os esqueletos marcados com `skip` serão implementados na Aula 14.

| Markers | Significado |
|---|---|
| `unit` / `integration` / `system` | Nível da pirâmide de testes |
| `negative` | Casos negativos (mín. 40% — atual: 56%) |
| `boundary` | Análise de valor limite |
