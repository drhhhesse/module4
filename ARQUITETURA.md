# Documento de Arquitetura - Módulo 4: Análise Inteligente de Editais

> **Projeto:** LicitaSoluções  
> **Módulo:** 4 - Análise Inteligente de Editais  
> **Disciplina:** Engenharia de Software - Prof. Kurt - UNISC 2026/1  
> **Autor:** Henrique Hayes Hesse | Scrum of Scrums + Arquitetura + LLM  
> **Versão:** 2.1 | Data: 13/05/2026

---

## 1. Introdução

Este documento descreve a arquitetura do Módulo 4 do sistema LicitaSoluções - o componente responsável pela análise inteligente de editais de licitação. O módulo recebe documentos PDF do Módulo 1, processa automaticamente via LLM local, e disponibiliza resumos estruturados, chat RAG, e recomendações Go/No-Go para o Analista de Licitação.

### 1.1 Escopo

O Módulo 4 cobre:
- Processamento automático de editais (trigger-based, sem intervenção humana)
- Extração estruturada via LLM (resumo jurídico, documentos, preços, datas)
- Chat RAG ("Pergunte ao Edital")
- Recomendação Go/No-Go (matching de itens e requisitos)

O Módulo 4 **não** cobre:
- Busca e download de editais (Módulo 1)
- Cadastro de fornecedores e catálogo de produtos (Módulo 2)
- Interface administrativa global (Módulo 3)

### 1.2 Definições

| Termo | Definição |
|-------|-----------|
| **Edital** | Documento PDF de licitação pública com requisitos, preços e prazos |
| **RAG** | Retrieval-Augmented Generation - perguntas respondidas com base no documento |
| **Embedding** | Vetor numérico (768 dimensões) representando o significado semântico de um texto |
| **Go/No-Go** | Recomendação binária: participar ou não de uma licitação |
| **Gate/Regra** | Etapa do pipeline que processa e valida um aspecto do edital |

---

## 2. Padrão Arquitetural

### Padrão: Pipeline de Regras em Cascata

O Módulo 4 adota o padrão de **pipeline de regras em cascata** - cada regra de análise é um gate independente executado sequencialmente, com resultados armazenados após cada etapa.

**Justificativa (ver [ADR-004](adr/ADR-004-pipeline-regras-cascata.md)):**
- Prompts focados por regra = maior precisão de extração
- Falha parcial não perde trabalho anterior
- Extensível - adicionar regras não altera as existentes
- Padrão comprovado em sistemas de produção (validação em cascata)

### Regras do Pipeline

| # | Regra | Tipo | Tecnologia |
|---|-------|------|-----------|
| R1 | Resumo Jurídico | Extração LLM | Mistral via Ollama |
| R2 | Documentos Necessários | Extração LLM | Mistral via Ollama |
| R3 | Faixa de Preços | Extração LLM | Mistral via Ollama |
| R4 | Datas Importantes | Extração LLM | Mistral via Ollama |
| R5 | Embedding + RAG Index | Embedding | nomic-embed-text + ChromaDB |
| R6 | Go/No-Go | Lógica de negócio | Python puro (sem LLM) |

---

## 3. Diagramas

### 3.1 Diagrama de Componentes

> Ver: [Diagrama de Componentes com Interfaces](LicitaSolucoes_M4_Diagramas_UML.md#8-diagrama-de-componentes)

Componentes internos:
- **API Controller** (FastAPI) - expõe endpoints REST, orquestra serviços
- **EditalService** - orquestra as regras R1-R5 para cada edital
- **ChatService** - busca por similaridade no ChromaDB + geração de resposta via Mistral
- **GoNoGoService** - matching determinístico sem LLM (documentos, preço, região, qualificações)
- **AnalysisRules** - padrão Strategy: 5 regras implementam a interface `AnalysisRule`
- **PDFExtractor** - adaptador para pdfplumber

Componentes externos:
- **Ollama** (localhost:11434) - runtime LLM local: Mistral (geração) + nomic-embed-text (embeddings)
- **Supabase** (cloud) - PostgreSQL compartilhado entre módulos
- **ChromaDB** (local) - banco vetorial para RAG e matching de catálogo
- **Módulo 1** - insere editais no Supabase (trigger dispara processamento)
- **Módulo 2** - insere perfil e catálogo do fornecedor no Supabase

Interfaces:
- Frontend ↔ API: `HTTP/JSON` (porta 8400)
- API ↔ Ollama: `HTTP/JSON` (localhost:11434)
- API ↔ Supabase: `HTTPS` (supabase-py client)
- API ↔ ChromaDB: `Python API` (local filesystem)
- Trigger → API: `HTTP POST` (on INSERT automático)

### 3.2 Diagrama de Implantação

> Ver: [Diagrama de Implantação](LicitaSolucoes_M4_Diagramas_UML.md#diagrama-de-implantação)

| Nó | Componente | Hospedagem |
|----|-----------|-----------|
| **Navegador** | Frontend (Vue.js SPA) | Build estático servido pelo FastAPI ou Nginx |
| **Servidor Local** | FastAPI, Ollama (Mistral + nomic), ChromaDB, PDFs | Zora Server: i5-12400, RTX 3060 12GB, 48GB DDR4, Ubuntu 24.04 |
| **Supabase Cloud** | PostgreSQL + PostgREST + Auth + Trigger | supabase.co (tier gratuito, 500MB) |
| **Módulo 1 / Módulo 2** | Inserção de dados | Servidores próprios dos outros grupos |
| **Portais Gov** | ComprasNet, PNCP, BNC | APIs públicas (consumidas pelo Módulo 1) |

**Protocolos de comunicação:**
- Frontend ↔ Backend: HTTP/JSON (porta 8400, rede local)
- Backend ↔ Ollama: HTTP/JSON (localhost:11434, loopback)
- Backend ↔ ChromaDB: Python API (filesystem local)
- Backend ↔ Supabase: HTTPS (TLS 1.3, internet)
- Trigger → Backend: HTTP POST (Supabase → servidor via internet)
- Módulos 1/2 → Supabase: HTTPS (supabase-py client)

### 3.3 Outros Diagramas

Todos os diagramas estão em Mermaid e renderizam nativamente no GitHub:

- [Diagrama de Casos de Uso](LicitaSolucoes_M4_Diagramas_UML.md#1-diagrama-de-casos-de-uso)
- [Diagrama de Classes](LicitaSolucoes_M4_Diagramas_UML.md#2-diagrama-de-classes)
- [Diagrama de Sequência - Processamento Automático](LicitaSolucoes_M4_Diagramas_UML.md#3-diagrama-de-sequência--processamento-automático-trigger)
- [Diagrama de Sequência - Chat RAG](LicitaSolucoes_M4_Diagramas_UML.md#4-diagrama-de-sequência--chat-rag)
- [Diagrama de Sequência - Go/No-Go](LicitaSolucoes_M4_Diagramas_UML.md#5-diagrama-de-sequência--gono-go-r6)
- [Diagrama ER](LicitaSolucoes_M4_Diagramas_UML.md#6-diagrama-er-entidade-relacionamento)
- [Diagrama de Atividades](LicitaSolucoes_M4_Diagramas_UML.md#7-diagrama-de-atividades--pipeline-completo)

---

## 4. Decisões Arquiteturais (ADRs)

| ADR | Decisão | Status |
|-----|---------|--------|
| [ADR-001](adr/ADR-001-chromadb-supabase-hibrido.md) | Abordagem híbrida: ChromaDB (RAG local) + Supabase (dados compartilhados) | Aceito |
| [ADR-002](adr/ADR-002-mistral-local-sobre-api-nuvem.md) | Mistral local (Ollama) em vez de APIs de LLM na nuvem | Aceito |
| [ADR-003](adr/ADR-003-fastapi-sobre-flask.md) | FastAPI em vez de Flask | Aceito |
| [ADR-004](adr/ADR-004-pipeline-regras-cascata.md) | Pipeline de regras em cascata para análise de editais | Aceito |
| [ADR-005](adr/ADR-005-nomic-embed-text-embeddings.md) | nomic-embed-text para geração de embeddings | Aceito |
| [ADR-006](adr/ADR-006-pdfplumber-extracao-pdf.md) | pdfplumber para extração de texto de PDFs | Aceito |
| [ADR-007](adr/ADR-007-trigger-processamento-automatico.md) | Processamento automático via trigger PostgreSQL | Aceito |
| [ADR-008](adr/ADR-008-go-no-go-matching-sem-llm.md) | Go/No-Go sem LLM - lógica de negócio pura | Aceito |
| [ADR-009](adr/ADR-009-matching-itens-embeddings.md) | Matching de itens edital vs catálogo via embeddings | Aceito |

---

## 5. Atributos de Qualidade (RNFs) e Como a Arquitetura os Suporta

### RNF01 - Desempenho: Tempo de resposta < 3s para consultas RAG

**Como a arquitetura suporta:**
- ChromaDB local = busca vetorial sem latência de rede (~50ms para top-5)
- Mistral rodando em GPU local (RTX 3060) = geração em ~2-5s
- Embeddings via nomic-embed-text em CPU = ~100ms por consulta
- Total estimado: ~3-5s por consulta RAG (dentro do aceitável para análise de documentos longos)

### RNF02 - Capacidade: Suportar editais de até 200 páginas

**Como a arquitetura suporta:**
- pdfplumber processa página por página - memória controlada ([ADR-006](adr/ADR-006-pdfplumber-extracao-pdf.md))
- Chunking com sobreposição (3200 chars, 800 overlap) fragmenta documentos grandes em pedaços gerenciáveis
- ChromaDB suporta milhões de vetores - 200 páginas geram ~200-400 chunks
- R1-R4 recebem o texto completo - Mistral 7B suporta contexto de 32K tokens (~50 páginas). Editais maiores podem requerer sumarização prévia por seções

### RNF03 - Privacidade: Dados nunca saem da rede local (LLM)

**Como a arquitetura suporta:**
- Mistral e nomic-embed-text rodam localmente via Ollama ([ADR-002](adr/ADR-002-mistral-local-sobre-api-nuvem.md))
- Nenhuma chamada a APIs de LLM na nuvem
- ChromaDB é local (filesystem)
- Supabase recebe apenas resumos estruturados (JSON), não o texto bruto completo do edital
- O texto bruto pode ser armazenado apenas localmente se necessário

### RNF04 - Disponibilidade: Sistema funciona sem internet (para LLM)

**Como a arquitetura suporta:**
- Ollama + ChromaDB são 100% locais
- Sem internet: R1-R5 e Chat RAG funcionam normalmente
- Sem internet: Supabase fica inacessível - R6 (Go/No-Go) não funciona pois depende do perfil do fornecedor
- Mitigação: cache local do perfil do fornecedor para operação offline

### RNF05 - Escalabilidade: Processamento automático de múltiplos editais

**Como a arquitetura suporta:**
- Trigger PostgreSQL dispara processamento automaticamente ([ADR-007](adr/ADR-007-trigger-processamento-automatico.md))
- FastAPI async permite processar múltiplos editais concorrentemente
- Fila implícita via campo `status` (pending → processing → done → error)
- Cron de fallback para editais que falharam no trigger

### RNF06 - Manutenibilidade: Regras de análise extensíveis

**Como a arquitetura suporta:**
- Padrão Strategy: cada regra implementa a interface `AnalysisRule` ([ADR-004](adr/ADR-004-pipeline-regras-cascata.md))
- Adicionar R7 (ex: critérios de sustentabilidade) requer apenas uma nova classe e um novo prompt
- Regras são independentes - alterar R3 não afeta R1, R2, R4
- ADRs documentam cada decisão para facilitar onboarding de novos desenvolvedores

---

## 6. Stack Tecnológico

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Frontend | Vue.js (SPA) | Framework reativo, componentizado, SPA servido pelo FastAPI ou build estático |
| Backend | FastAPI (Python 3.11+) | Async nativo para chamadas LLM ([ADR-003](adr/ADR-003-fastapi-sobre-flask.md)) |
| LLM (Geração) | Mistral 7B via Ollama | Local, gratuito, privacidade ([ADR-002](adr/ADR-002-mistral-local-sobre-api-nuvem.md)) |
| LLM (Embeddings) | nomic-embed-text via Ollama | 768d, local, zero custo ([ADR-005](adr/ADR-005-nomic-embed-text-embeddings.md)) |
| Banco vetorial | ChromaDB (local) | RAG + matching de catálogo ([ADR-001](adr/ADR-001-chromadb-supabase-hibrido.md)) |
| Banco relacional | Supabase (PostgreSQL) | Dados compartilhados entre módulos ([ADR-001](adr/ADR-001-chromadb-supabase-hibrido.md)) |
| PDF Parser | pdfplumber | Layout complexo + tabelas ([ADR-006](adr/ADR-006-pdfplumber-extracao-pdf.md)) |
| Trigger | PostgreSQL AFTER INSERT | Processamento automático ([ADR-007](adr/ADR-007-trigger-processamento-automatico.md)) |

---

## Referências

- [Diagramas UML completos](LicitaSolucoes_M4_Diagramas_UML.md)
- [Pasta de ADRs](adr/)
- [Arquitetura detalhada (docx)](LicitaSolucoes_Modulo4_Arquitetura_v2.docx)

---

*Módulo 4 - Documento de Arquitetura v2.1 - UNISC 2026/1 - Henrique Hayes Hesse*
