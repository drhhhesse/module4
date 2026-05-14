** Módulo 4**

Arquitetura do Módulo de Análise Inteligente de Editais

RAG Pipeline + Analysis Rules + ChromaDB + Supabase

*Engenharia de Software --- Prof. Kurt \| UNISC 2026/1*

*Henrique Hayes Hesse \| Arquitetura + LLM*

**1. VISÃO GERAL**

Módulo 4 é o componente de análise inteligente de editais da plataforma. Recebe documentos PDF de licitações públicas (editais) do Módulo 1, processa com LLM local (Mistral/Ollama), e produz:

-   Resumo jurídico --- exigências legais, cláusulas de conformidade, certificações obrigatórias

-   Documentos necessários --- lista completa de documentos exigidos para habilitação

-   Faixa de preços --- valores estimados, teto orçamentário, preços unitários por lote

-   Datas importantes --- prazo de submissão, abertura, visita técnica, esclarecimentos, recursos

-   Chat RAG --- "Pergunte ao Edital" --- perguntas em linguagem natural com respostas baseadas no documento

-   Recomendação Go/No-Go --- cruzamento com perfil do fornecedor (Módulo 2)

**2. ARQUITETURA GLOBAL**

**2.1 Pipeline de Processamento**

O pipeline segue o padrão de cascata de regras (inspirado no ConeRod gate architecture): cada regra de análise é um gate independente que processa o edital e produz um resultado estruturado. As regras são executadas em sequência, com a mais barata primeiro.

  -------- ---------------------------- ------------------------------------------------------------------------------------------------------------------------------------ ------------------------
  **\#**   **Regra**                    **Descrição**                                                                                                                        **Output**

  **R1**   **Resumo Jurídico**          Extrair e resumir exigências legais, conformidade, certificações, penalidades, regime de execução                                    legal_summary: text

  **R2**   **Documentos Necessários**   Lista completa: certidões negativas, atestados de capacidade técnica, balanço patrimonial, registro no CREA/CRM, etc.                required_docs: jsonb

  **R3**   **Faixa de Preços**          Valor estimado total, preço máximo por lote, preços unitários de referência, critério de julgamento (menor preço, técnica e preço)   price_range: jsonb

  **R4**   **Datas Importantes**        Prazo de entrega de propostas, data de abertura, período de esclarecimentos, prazo de recursos, visita técnica                       important_dates: jsonb

  **R5**   **Embedding + RAG Index**    Chunking (3200 chars, 800 overlap) + embedding via nomic-embed-text + armazenamento em ChromaDB local                             embedding: vector(768)

  **R6**   **Go/No-Go**                 Cruzamento com perfil do fornecedor (Módulo 2): documentos faltantes, preço abaixo do piso, região de entrega, incompatibilidades    recommendation: jsonb
  -------- ---------------------------- ------------------------------------------------------------------------------------------------------------------------------------ ------------------------

*R1-R4 são regras de extração (LLM prompt-based). R5 é embedding + indexação. R6 é lógica de negócio.*

**2.2 Fluxo de Dados**

**Módulo 1 (busca) → INSERT na tabela editais no Supabase → Trigger PostgreSQL dispara automaticamente → Módulo 4 processa:**

1.  Trigger PostgreSQL detecta novo INSERT na tabela editais → chama HTTP POST /api/analyze/{edital_id}

2.  pdfplumber extrai texto

3.  Texto enviado para Mistral (Ollama local) com prompt específico para cada regra (R1-R4)

4.  Resultados estruturados escritos no Supabase Postgres (tabela edital_analysis)

5.  Texto dividido em chunks, embeddings gerados via nomic-embed-text, armazenados em ChromaDB local

6.  Usuário faz perguntas via chat → embedding da pergunta → ChromaDB busca top 5 chunks → Mistral gera resposta

7.  Go/No-Go cruza R1-R4 com perfil do fornecedor (Módulo 2) e produz recomendação

**3. STACK TECNOLÓGICO**

**3.1 Abordagem Hibrida: ChromaDB (local) + Supabase (dados compartilhados)**

O Modulo 4 utiliza ChromaDB como banco vetorial local para RAG e matching de catalogo. A busca vetorial roda localmente (SQLite + HNSW) com latencia minima e sem dependencia de rede. O Supabase serve como camada de dados compartilhada entre todos os modulos para dados estruturados (editais, analises, perfis de fornecedores).

**3.2 Componentes**

  -------------------- --------------------------- ----------------------------------------------------------
  **Componente**       **Tecnologia**              **Função**

  **Backend**          FastAPI (Python 3.11+)      REST API, orquestração do pipeline, endpoints de análise

  **PDF Parser**       pdfplumber                  Conversão PDF → texto, extração de tabelas

  **LLM (Geração)**    Mistral via Ollama          Geração de resumos, chat RAG, extração estruturada

  **Embeddings**       nomic-embed-text (Ollama)   Conversão texto → vetor 768d para busca semântica

  **Banco de dados**   Supabase (PostgreSQL)       Armazenamento de editais, analises, perfis de fornecedores

  **Busca vetorial**   ChromaDB (local)            Similarity search via cosine distance (SQLite + HNSW)

  **Frontend**         Vue.js (SPA)                Interface de chat, upload, visualização de análises
  -------------------- --------------------------- ----------------------------------------------------------

**4. SCHEMA DO BANCO DE DADOS (SUPABASE)**

**4.1 Tabela: editais**

*Editais brutos recebidos do Módulo 1*

CREATE TABLE editais (

id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

numero TEXT NOT NULL, \-- Número do edital

orgao TEXT, \-- Órgão licitante

modalidade TEXT, \-- Pregão, Concorrência, etc.

objeto TEXT, \-- Descrição do objeto

pdf_url TEXT, \-- URL do PDF no Supabase Storage

raw_text TEXT, \-- Texto extraído via pdfplumber

status TEXT DEFAULT \'pending\', \-- pending, processing, done, error

created_at TIMESTAMPTZ DEFAULT now(),

module1_metadata JSONB \-- Metadados do Módulo 1

);

**4.2 Tabela: edital_analysis**

*Resultados das regras de análise (R1-R4 + R6)*

CREATE TABLE edital_analysis (

id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

edital_id UUID REFERENCES editais(id) ON DELETE CASCADE,

legal_summary TEXT, \-- R1: Resumo jurídico

required_documents JSONB, \-- R2: Lista de documentos

price_range JSONB, \-- R3: Faixa de preços

important_dates JSONB, \-- R4: Datas importantes

go_no_go JSONB, \-- R6: Recomendação

processed_at TIMESTAMPTZ DEFAULT now()

);

**4.3 Embeddings e Chunks (ChromaDB Local)**

*Chunks embedados para RAG (R5) sao armazenados no ChromaDB localmente, nao no Supabase.*

ChromaDB utiliza SQLite + indice HNSW para busca vetorial rapida. Os chunks sao indexados por edital_id e podem ser re-gerados a qualquer momento re-executando R5.

Busca de similaridade via ChromaDB Python API:

    results = chromadb_collection.query(
        query_embeddings=[query_vector],
        n_results=5,
        where={"edital_id": edital_id}
    )

**5. API ENDPOINTS (FASTAPI)**

  ------------ --------------------------- -------------------------------------------------------------------------------------------
  **Método**   **Rota**                    **Descrição**

  **POST**     /api/upload                 Upload de PDF. Extrai texto via pdfplumber. Salva em editais.

  **POST**     /api/analyze/{edital_id}    Executa R1-R5 sequencialmente. Salva resultados em edital_analysis (Supabase) + ChromaDB (chunks).

  **GET**      /api/analysis/{edital_id}   Retorna análise completa: resumo jurídico, documentos, preços, datas.

  **POST**     /api/chat                   RAG Q&A. Body: {edital_id, question}. Embeds question, busca top 5 chunks, gera resposta.

  **POST**     /api/gonogo/{edital_id}     Cruza análise com perfil do fornecedor (Módulo 2). Retorna recomendação.

  **GET**      /api/editais                Lista todos os editais com status de processamento.

  **DELETE**   /api/editais/{edital_id}    Remove edital e todas as análises/chunks associados (CASCADE).
  ------------ --------------------------- -------------------------------------------------------------------------------------------

**6. PROMPTS DE ANÁLISE (R1-R4)**

Cada regra usa um prompt estruturado enviado ao Mistral via Ollama. O LLM recebe o texto completo do edital e retorna JSON estruturado.

**R1 --- Resumo Jurídico**

SYSTEM: Você é um analista jurídico especializado em licitações.

USER: Analise o edital abaixo e extraia:

\- Exigências legais e de conformidade

\- Certificações obrigatórias

\- Penalidades por descumprimento

\- Regime de execução (empreitada, preço unitário, etc.)

\- Cláusulas críticas

Responda APENAS em JSON. Edital: {raw_text}

**R2 --- Documentos Necessários**

SYSTEM: Você é um especialista em habilitação de licitações.

USER: Liste TODOS os documentos exigidos para habilitação:

\- Habilitação jurídica

\- Qualificação técnica

\- Qualificação econômico-financeira

\- Regularidade fiscal e trabalhista

\- Declarações complementares

Responda APENAS em JSON array. Edital: {raw_text}

**R3 --- Faixa de Preços**

SYSTEM: Você é um analista de preços de licitações.

USER: Extraia do edital:

\- Valor estimado total

\- Preço máximo por lote/item

\- Preços unitários de referência

\- Critério de julgamento (menor preço, técnica e preço)

\- Margem de preferência (se houver)

Responda APENAS em JSON. Edital: {raw_text}

**R4 --- Datas Importantes**

SYSTEM: Você é um gestor de prazos de licitações.

USER: Extraia TODAS as datas relevantes:

\- Prazo de entrega de propostas

\- Data e hora de abertura

\- Período de esclarecimentos

\- Prazo de impugnação

\- Prazo de recursos

\- Visita técnica (se obrigatória)

\- Prazo de execução/entrega

Responda APENAS em JSON. Edital: {raw_text}

**7. INTEGRAÇÃO OLLAMA/MISTRAL → SUPABASE**

**7.1 Fluxo de Integração**

\# 1. Inicializar clientes

from supabase import create_client

import requests \# Ollama API

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

OLLAMA_URL = \'http://localhost:11434\'

\# 2. Gerar embedding via Ollama

def get_embedding(text: str) -\> list\[float\]:

resp = requests.post(f\'{OLLAMA_URL}/api/embeddings\', json={

\'model\': \'nomic-embed-text\',

\'prompt\': text

})

return resp.json()\[\'embedding\'\]

\# 3. Gerar análise via Mistral

def analyze_rule(rule_prompt: str, edital_text: str) -\> dict:

resp = requests.post(f\'{OLLAMA_URL}/api/generate\', json={

\'model\': \'mistral\',

\'prompt\': rule_prompt.format(raw_text=edital_text),

\'format\': \'json\',

\'stream\': False

})

return json.loads(resp.json()\[\'response\'\])

\# 4. Salvar no Supabase

def save_analysis(edital_id: str, analysis: dict):

supabase.table(\'edital_analysis\').insert({

\'edital_id\': edital_id,

\'legal_summary\': analysis\[\'legal_summary\'\],

\'required_documents\': analysis\[\'required_documents\'\],

\'price_range\': analysis\[\'price_range\'\],

\'important_dates\': analysis\[\'important_dates\'\],

}).execute()

\# 5. Salvar chunks com embeddings no ChromaDB

def save_chunks(edital_id: str, chunks: list\[str\]):

for i, chunk in enumerate(chunks):

embedding = get_embedding(chunk)

chromadb_collection.add(

documents=\[chunk\],

embeddings=\[embedding\],

ids=\[f\'{edital_id}_{i}\'\],

metadatas=\[{\'edital_id\': edital_id, \'chunk_index\': i}\]

)

\# 6. RAG similarity search via ChromaDB

def search_chunks(question: str, edital_id: str):

q_embedding = get_embedding(question)

results = chromadb_collection.query(

query_embeddings=\[q_embedding\],

n_results=5,

where={\'edital_id\': edital_id}

)

return results

**8. HARDWARE E DEPLOY**

  -------------------------- ----------------------------------------------------------------
  **Componente**             **Especificação**

  **Servidor LLM**           i5-12400, RTX 3060 12GB, 48GB DDR4, Ubuntu 24.04 (Zora Server)

  **Modelo de geração**      Mistral via Ollama (localhost:11434)

  **Modelo de embeddings**   nomic-embed-text via Ollama

  **Banco de dados**         Supabase Cloud (PostgreSQL) ou self-hosted

  **Backend**                FastAPI no mesmo servidor, porta 8400

  **Frontend**               Vue.js (SPA), build estático servido pelo FastAPI ou Nginx
  -------------------------- ----------------------------------------------------------------

*Mistral roda localmente no servidor. Resultados são POST para Supabase via Python client. Não há dependência de APIs externas de LLM.*

**9. INTEGRAÇÃO INTER-MÓDULOS**

Com Supabase como data layer compartilhado, a integração é via SQL:

  ------------------ ---------------------------------------- --------------------------------------------
  **Módulo**         **Escreve**                              **Lê**

  **M1 (Busca)**     editais (PDF URL, metadados)             ---

  **M2 (Perfil)**    suppliers (perfil, documentos, região)   ---

  **M3 (?)**         TBD                                      TBD

  **M4 (Análise)**   edital_analysis (Supabase), chunks (ChromaDB local)           editais (M1), suppliers (M2) para Go/No-Go
  ------------------ ---------------------------------------- --------------------------------------------

*Nenhum módulo precisa chamar API de outro módulo. Todos leem e escrevem no mesmo Postgres. A integração é por dados, não por API.*

**10. PRÓXIMOS PASSOS**

8.  Criar projeto no Supabase e configurar tabelas (schema acima)

9.  Instalar Mistral via Ollama no servidor

10. Implementar regras R1-R4 como funções Python com prompts estruturados

11. Implementar chunking + embedding + armazenamento ChromaDB

12. Implementar endpoint /api/chat (RAG)

13. Implementar Go/No-Go cruzando com Módulo 2

14. Testar com edital real (pregão eletrônico municipal)

15. Apresentar para Scrum of Scrums + Prof. Kurt

**4.5 Tabela: supplier_catalogue**

*Catálogo de produtos/serviços do fornecedor (preenchido pelo Módulo 2)*

CREATE TABLE supplier_catalogue (

id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,

item_description TEXT NOT NULL, \-- Descrição do item

catmat_code TEXT, \-- Código CATMAT (opcional)

unit TEXT, \-- UN, CX, KG, M, etc.

unit_price FLOAT, \-- Preço unitário

category TEXT, \-- Categoria (elétrica, etc.)

created_at TIMESTAMPTZ DEFAULT now()

);

O Módulo 2 é responsável por popular esta tabela. O Módulo 4 lê e indexa os itens no ChromaDB para matching por similaridade de embeddings.

**4.6 Trigger: Processamento Automático**

*Trigger PostgreSQL que dispara automaticamente quando o Módulo 1 insere um novo edital.*

CREATE EXTENSION IF NOT EXISTS http;

CREATE OR REPLACE FUNCTION notify_module4()

RETURNS TRIGGER AS \$\$

BEGIN

PERFORM http_post(

\'http://SERVER:8400/api/analyze/\' \|\| NEW.id::text,

\'\',

\'application/json\'

);

RETURN NEW;

END;

\$\$ LANGUAGE plpgsql;

CREATE TRIGGER on_edital_inserted

AFTER INSERT ON editais

FOR EACH ROW

EXECUTE FUNCTION notify_module4();

Módulo 1 insere → trigger dispara → FastAPI /api/analyze é chamado automaticamente → R1-R5 executam sem intervenção humana.

**7.2 Matching de Itens --- Catálogo vs Edital**

Dentro da regra R6 (Go/No-Go), os itens do edital são comparados com o catálogo do fornecedor usando similaridade de embeddings.

\# 7. Indexar catálogo do fornecedor no ChromaDB

def index_catalogue_item(item: dict):

embedding = get_embedding(item\[\'item_description\'\])

chromadb_catalogue.add(

documents=\[item\[\'item_description\'\]\],

embeddings=\[embedding\],

ids=\[str(item\[\'id\'\])\],

metadatas=\[{

\'supplier_id\': str(item\[\'supplier_id\'\]),

\'unit_price\': item\[\'unit_price\'\],

\'unit\': item\[\'unit\'\]

}\]

)

\# 8. Matching: item do edital vs catálogo do fornecedor

def match_items(edital_items: list, supplier_id: str):

results = \[\]

for item in edital_items:

item_embedding = get_embedding(item\[\'description\'\])

matches = chromadb_catalogue.query(

query_embeddings=\[item_embedding\],

n_results=3,

where={\'supplier_id\': supplier_id}

)

best_score = matches\[\'distances\'\]\[0\]\[0\] if matches\[\'ids\'\]\[0\] else 0

similarity = 1 - best_score \# cosine distance to similarity

if similarity \> 0.85:

status = \'MATCH\'

elif similarity \> 0.60:

status = \'REVISÃO\'

else:

status = \'SEM MATCH\'

results.append({

\'edital_item\': item\[\'description\'\],

\'best_match\': matches\[\'documents\'\]\[0\]\[0\] if matches\[\'ids\'\]\[0\] else None,

\'similarity\': round(similarity, 3),

\'status\': status

})

return results

Score \> 0.85 = match automático  \| 0.60--0.85 = revisão humana  \| \< 0.60 = sem match 

*Módulo 4 --- Arquitetura v2.1 --- Henrique Hayes Hesse --- UNISC 2026*
