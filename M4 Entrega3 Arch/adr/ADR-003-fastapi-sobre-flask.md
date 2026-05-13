# ADR-003: FastAPI em vez de Flask

**Status:** Aceito  
**Data:** 12/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

O Módulo 4 precisa de um framework web Python para expor endpoints REST para upload de PDF, execução de análise, chat RAG e recomendações Go/No-Go. Os dois principais candidatos são Flask e FastAPI.

Chamadas de inferência LLM (Mistral via Ollama) levam de 5 a 30 segundos por requisição. O framework deve lidar com requisições concorrentes sem bloquear — múltiplos usuários podem enviar editais ou fazer perguntas simultaneamente.

## Decisão

Utilizar FastAPI como framework backend.

## Consequências

**Positivas:**
- Suporte nativo a async — chamadas de inferência LLM rodam concorrentemente sem bloquear outras requisições
- Documentação OpenAPI automática (Swagger UI em /docs) — útil para integração entre módulos
- Validação de requisições integrada via modelos Pydantic — detecta input malformado antes do processamento
- Type hints em todo o código — melhor suporte da IDE e menos erros em tempo de execução
- Performance superior ao Flask para cargas I/O-bound (que é o caso da inferência LLM)

**Negativas:**
- Curva de aprendizado ligeiramente mais íngreme que Flask para membros da equipe não familiarizados com async
- Algumas bibliotecas (ex: pdfplumber) são síncronas e precisam ser encapsuladas com run_in_executor

**Neutras:**
- Ambos os frameworks são Python, usam os mesmos padrões de deploy (uvicorn/gunicorn) e integram com as mesmas bibliotecas
- Migração do protótipo Flask anterior foi mínima — a estrutura de endpoints é similar
