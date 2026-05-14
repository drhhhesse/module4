# Módulo 4 - Diagramas UML

> Engenharia de Software - Prof. Kurt - UNISC 2026/1  
> Entrega 3 - Documento de Arquitetura + Diagramas UML  
> Autor: Henrique Hayes Hesse

---

## 1. Diagrama de Casos de Uso

```mermaid
flowchart LR
    subgraph Atores
        AL[" Analista de Licitação"]
        M1[" Módulo 1\n(Sistema Externo)"]
        M2[" Módulo 2\n(Perfil Fornecedor)"]
    end

    subgraph Sistema["Módulo 4 - Análise Inteligente de Editais"]
        UC01["UC-01: Receber Edital\n(automático via trigger)"]
        UC02["UC-02: Extrair Resumo Jurídico (R1)"]
        UC03["UC-03: Listar Documentos Necessários (R2)"]
        UC04["UC-04: Extrair Faixa de Preços (R3)"]
        UC05["UC-05: Extrair Datas Importantes (R4)"]
        UC06["UC-06: Indexar para RAG (R5)"]
        UC07["UC-07: Consultar Edital via Chat"]
        UC08["UC-08: Gerar Recomendação Go/No-Go (R6)"]
        UC09["UC-09: Visualizar Análise Completa"]
        UC10["UC-10: Remover Edital"]
    end

    M1 -->|"INSERT edital"| UC01
    UC01 -->|"trigger automático"| UC02
    UC01 -->|"trigger automático"| UC03
    UC01 -->|"trigger automático"| UC04
    UC01 -->|"trigger automático"| UC05
    UC01 -->|"trigger automático"| UC06

    AL --> UC07
    AL --> UC08
    AL --> UC09
    AL --> UC10

    M2 -->|"perfil fornecedor"| UC08
```

---

## 2. Diagrama de Classes

```mermaid
classDiagram
    class EditalService {
        +analyze(edital_id) AnalysisResponse
        +get_analysis(edital_id) AnalysisResponse
        +delete(edital_id) void
        -run_rules(raw_text) dict
    }

    class ChatService {
        +ask(edital_id, question) ChatResponse
        -embed_question(text) list
        -search_chunks(embedding, edital_id) list
        -generate_answer(chunks, question) str
    }

    class GoNoGoService {
        +evaluate(edital_id) GoNoGoResponse
        -load_analysis(edital_id) Analysis
        -load_supplier_profile() SupplierProfile
        -check_documents(required, available) DocumentResult
        -check_price(teto, preco_medio) PriceResult
        -check_region(local, regioes) RegionResult
        -check_qualifications(exigidos, certificacoes) QualResult
    }

    class AnalysisRule {
        <<interface>>
        +name str
        +execute(raw_text) dict
    }

    class LegalSummaryRule {
        +execute(raw_text) dict
    }

    class RequiredDocsRule {
        +execute(raw_text) dict
    }

    class PriceRangeRule {
        +execute(raw_text) dict
    }

    class ImportantDatesRule {
        +execute(raw_text) dict
    }

    class EmbeddingRule {
        +execute(raw_text) void
        -chunk_text(text) list
        -embed_chunk(chunk) list
    }

    class PDFExtractor {
        +extract_text(file_path) str
        +extract_tables(file_path) list
    }

    class OllamaClient {
        +generate(model, prompt) str
        +embed(model, text) list
    }

    class SupabaseClient {
        +insert(table, data) Response
        +select(table, filters) list
        +delete(table, id) Response
    }

    class ChromaDBClient {
        +add(documents, embeddings, ids) void
        +query(embedding, n_results) QueryResult
        +delete(edital_id) void
    }

    AnalysisRule <|.. LegalSummaryRule
    AnalysisRule <|.. RequiredDocsRule
    AnalysisRule <|.. PriceRangeRule
    AnalysisRule <|.. ImportantDatesRule
    AnalysisRule <|.. EmbeddingRule

    EditalService --> PDFExtractor
    EditalService --> AnalysisRule
    EditalService --> SupabaseClient
    EditalService --> OllamaClient
    EmbeddingRule --> ChromaDBClient
    EmbeddingRule --> OllamaClient
    ChatService --> ChromaDBClient
    ChatService --> OllamaClient
    GoNoGoService --> SupabaseClient
```

---

## 3. Diagrama de Sequência - Processamento Automático (Trigger)

```mermaid
sequenceDiagram
    participant M1 as Módulo 1 (Busca)
    participant SB as Supabase (Postgres)
    participant TG as Trigger on_edital_inserted
    participant API as FastAPI (Módulo 4)
    participant PDF as PDFExtractor
    participant LLM as Ollama (Mistral)
    participant CR as ChromaDB (Local)

    M1->>SB: INSERT editais (pdf_url, metadados)
    SB->>TG: AFTER INSERT trigger dispara
    TG->>API: HTTP POST /api/analyze/{edital_id}
    API->>SB: SELECT pdf_url, raw_text FROM editais
    SB-->>API: dados do edital
    API->>PDF: extract_text(pdf_url)
    PDF-->>API: raw_text
    API->>SB: UPDATE editais SET status = 'processing'

    rect rgb(240, 255, 244)
        Note over API,LLM: R1 - Resumo Juridico
        API->>LLM: generate(prompt_legal, raw_text)
        LLM-->>API: legal_summary (JSON)
    end

    rect rgb(240, 255, 244)
        Note over API,LLM: R2 - Documentos Necessarios
        API->>LLM: generate(prompt_docs, raw_text)
        LLM-->>API: required_documents (JSON)
    end

    rect rgb(240, 255, 244)
        Note over API,LLM: R3 - Faixa de Precos
        API->>LLM: generate(prompt_prices, raw_text)
        LLM-->>API: price_range (JSON)
    end

    rect rgb(240, 255, 244)
        Note over API,LLM: R4 - Datas Importantes
        API->>LLM: generate(prompt_dates, raw_text)
        LLM-->>API: important_dates (JSON)
    end

    API->>SB: INSERT edital_analysis (R1-R4)

    rect rgb(235, 245, 251)
        Note over API,CR: R5 - Embedding + RAG Index
        API->>API: chunk_text(raw_text, 3200, 800)
        loop Para cada chunk
            API->>LLM: embed(nomic-embed-text, chunk)
            LLM-->>API: vector(768)
            API->>CR: add(chunk, embedding, edital_id)
        end
    end

    API->>SB: UPDATE editais SET status = 'done'
```

---

## 4. Diagrama de Sequência - Chat RAG

```mermaid
sequenceDiagram
    actor AL as Analista de Licitação
    participant API as FastAPI
    participant LLM as Ollama
    participant CR as ChromaDB (Local)

    AL->>API: POST /api/chat {edital_id, question}
    API->>LLM: embed(nomic-embed-text, question)
    LLM-->>API: query_vector(768)
    API->>CR: query(query_vector, n_results=5, filter=edital_id)
    CR-->>API: top 5 chunks similares
    API->>LLM: generate(mistral, context=chunks + question)
    LLM-->>API: resposta gerada
    API-->>AL: {answer, sources}
```

---

## 5. Diagrama de Sequência - Go/No-Go (R6)

```mermaid
sequenceDiagram
    actor AL as Analista de Licitação
    participant API as FastAPI
    participant SB as Supabase (Postgres)

    AL->>API: POST /api/gonogo/{edital_id}
    API->>SB: SELECT * FROM edital_analysis WHERE edital_id = X
    SB-->>API: legal_summary, required_documents, price_range, important_dates
    API->>SB: SELECT * FROM suppliers WHERE id = fornecedor_ativo
    SB-->>API: documentos_disponiveis, preco_medio, regioes, certificacoes

    Note over API: Matching sem LLM (logica pura)

    API->>API: check_documents(required vs available)
    API->>API: check_price(teto vs preco_medio)
    API->>API: check_region(local_entrega vs regioes)
    API->>API: check_qualifications(exigidos vs certificacoes)

    alt Todos os criterios OK
        API-->>AL: GO  Pode participar
    else Uma lacuna menor
        API-->>AL: GO COM RESSALVAS  Corrigir antes do prazo
    else Multiplos bloqueios
        API-->>AL: NO-GO  Nao participar
    end

    API->>SB: UPDATE edital_analysis SET go_no_go = resultado
```

---

## 6. Diagrama ER (Entidade-Relacionamento)

```mermaid
erDiagram
    EDITAIS {
        uuid id PK
        text numero
        text orgao
        text modalidade
        text objeto
        text pdf_url
        text raw_text
        text status
        text error_message
        timestamptz created_at
        jsonb module1_metadata
    }

    EDITAL_ANALYSIS {
        uuid id PK
        uuid edital_id FK
        text legal_summary
        jsonb required_documents
        jsonb price_range
        jsonb important_dates
        jsonb go_no_go
        float confidence_score
        timestamptz processed_at
    }

    EDITAL_CHUNKS {
        uuid id PK
        uuid edital_id FK
        int chunk_index
        text content
        vector embedding
        timestamptz created_at
    }

    SUPPLIERS {
        uuid id PK
        text razao_social
        text cnpj
        jsonb documentos_disponiveis
        float preco_medio
        jsonb regioes_atendidas
        jsonb certificacoes
        jsonb categorias_cnae
        int capacidade_entrega_dias
        timestamptz updated_at
    }

    EDITAIS ||--o| EDITAL_ANALYSIS : "possui analise"
    EDITAIS ||--o{ EDITAL_CHUNKS : "dividido em chunks"
    SUPPLIERS ||--o{ EDITAL_ANALYSIS : "comparado via Go/No-Go"
```

---

## 7. Diagrama de Atividades - Pipeline Completo

```mermaid
flowchart TD
    A["Modulo 1 insere edital no Supabase"] --> B["Trigger PostgreSQL dispara"]
    B --> C["FastAPI /api/analyze chamado automaticamente"]
    C --> D["pdfplumber: extrair texto do PDF"]
    D --> E["UPDATE status = processing"]
    E --> F["R1: Resumo Juridico via Mistral"]
    F --> G["R2: Documentos Necessarios via Mistral"]
    G --> H["R3: Faixa de Precos via Mistral"]
    H --> I["R4: Datas Importantes via Mistral"]
    I --> J["Salvar R1-R4 no Supabase"]
    J --> K["R5: Chunking 3200 chars, 800 overlap"]
    K --> L["Gerar embeddings via nomic-embed-text"]
    L --> M["Armazenar chunks no ChromaDB"]
    M --> N["UPDATE status = done"]
    N --> O{"Analista interage"}
    O -->|"Chat RAG"| P["Embedding da pergunta"]
    P --> Q["ChromaDB: busca top 5 chunks"]
    Q --> R["Mistral: gera resposta com contexto"]
    R --> S["Retorna resposta"]
    S --> O
    O -->|"Go/No-Go"| T["Carregar R1-R4 do Supabase"]
    T --> U["Carregar perfil fornecedor do Modulo 2"]
    U --> V["Comparar: documentos, preco, regiao, qualificacoes"]
    V --> W{"Resultado"}
    W -->|"Tudo OK"| X["GO "]
    W -->|"1 lacuna"| Y["GO COM RESSALVAS "]
    W -->|"Multiplos bloqueios"| Z["NO-GO "]

    style F fill:#F0FFF4,stroke:#30D158
    style G fill:#F0FFF4,stroke:#30D158
    style H fill:#F0FFF4,stroke:#30D158
    style I fill:#F0FFF4,stroke:#30D158
    style L fill:#EBF5FB,stroke:#5AC8FA
    style M fill:#EBF5FB,stroke:#5AC8FA
    style Q fill:#EBF5FB,stroke:#5AC8FA
    style R fill:#F0FFF4,stroke:#30D158
    style X fill:#F0FFF4,stroke:#30D158
    style Y fill:#FFF8E1,stroke:#FF9F0A
    style Z fill:#FFF0F0,stroke:#FF453A
```

---

## 8. Diagrama de Componentes

```mermaid
flowchart LR
    subgraph Frontend["Frontend (Vue.js (SPA))"]
        UI["Interface Web (Vue.js)\nChat / Analises / Go-No-Go"]
    end

    subgraph Backend["Backend (FastAPI porta 8400)"]
        API["REST API"]
        ES["EditalService"]
        CS["ChatService"]
        GS["GoNoGoService"]
        RULES["Regras R1-R5"]
    end

    subgraph LLM["LLM Local (Ollama porta 11434)"]
        MISTRAL["Mistral\nGeracao R1-R4"]
        NOMIC["nomic-embed-text\nEmbeddings R5"]
    end

    subgraph Dados["Camada de Dados"]
        SB["Supabase PostgreSQL\neditais + edital_analysis\n+ suppliers"]
        CHR["ChromaDB Local\nedital_chunks\nembeddings"]
        TG["Trigger\non_edital_inserted"]
    end

    subgraph Externo["Sistemas Externos"]
        M1["Modulo 1\nBusca de Editais"]
        M2["Modulo 2\nPerfil Fornecedor"]
    end

    UI <-->|"HTTP/JSON"| API
    API --> ES
    API --> CS
    API --> GS
    ES --> RULES
    RULES -->|"Prompts R1-R4"| MISTRAL
    RULES -->|"Embeddings R5"| NOMIC
    ES -->|"Analises R1-R4"| SB
    RULES -->|"Chunks + Embeddings"| CHR
    CS -->|"Busca similar"| CHR
    CS -->|"Gera resposta"| MISTRAL
    GS -->|"Le analises + perfil"| SB
    M1 -->|"INSERT editais"| SB
    M2 -->|"INSERT suppliers"| SB
    TG -->|"HTTP POST auto"| API
    SB --> TG
```

---

*Módulo 4 - Diagramas UML v2.0 - UNISC 2026/1 - Henrique Hayes Hesse*

---

## 9. Diagrama de Implantação

```mermaid
flowchart TD
    subgraph Cliente["Navegador do Analista"]
        FE["Frontend\nVue.js (SPA)\nServido pelo FastAPI"]
    end

    subgraph Servidor["Servidor Local - Zora Server\ni5-12400 | RTX 3060 12GB | 48GB DDR4\nUbuntu 24.04"]
        subgraph Docker["Docker Container"]
            FAST["FastAPI\nPorta 8400\nPython 3.11+"]
        end
        subgraph Ollama["Ollama Runtime"]
            MISTRAL["Mistral 7B\nPorta 11434\nGPU: RTX 3060"]
            NOMIC["nomic-embed-text\nPorta 11434\nCPU fallback"]
        end
        subgraph Local["Armazenamento Local"]
            CHROMA["ChromaDB\nSQLite + HNSW\nedital_chunks\nsupplier_catalogue"]
            PDF["PDFs\n/data/editais/"]
        end
    end

    subgraph Nuvem["Supabase Cloud"]
        PG["PostgreSQL\neditais\nedital_analysis\nsuppliers\nsupplier_catalogue"]
        TG["Trigger\non_edital_inserted"]
        AUTH["Supabase Auth\nRow Level Security"]
        REST["PostgREST\nAPI auto-gerada"]
    end

    subgraph Externos["Sistemas Externos"]
        M1["Modulo 1\nBusca de Editais\nINSERT via Supabase client"]
        M2["Modulo 2\nPerfil Fornecedor\nINSERT via Supabase client"]
        GOV["Portais Gov\nComprasNet\nPNCP\nBNC"]
    end

    FE <-->|"HTTP/JSON\nporta 8400"| FAST
    FAST <-->|"HTTP/JSON\nlocalhost:11434"| MISTRAL
    FAST <-->|"HTTP/JSON\nlocalhost:11434"| NOMIC
    FAST <-->|"Python API\nlocal filesystem"| CHROMA
    FAST <-->|"HTTPS\nsupabase-py client"| REST
    TG -->|"HTTP POST\n/api/analyze"| FAST
    PG --> TG
    M1 -->|"HTTPS\nsupabase-py"| PG
    M2 -->|"HTTPS\nsupabase-py"| PG
    GOV -->|"REST API\nHTTPS"| M1
```

---

## 10. Diagrama de Componentes com Interfaces

```mermaid
flowchart LR
    subgraph Frontend["«UI» Frontend"]
        UI["Interface Web\nVue.js (SPA)"]
    end

    subgraph Backend["«Application Server» FastAPI"]
        API["«REST» API Controller\n/api/upload\n/api/analyze\n/api/chat\n/api/gonogo"]
        ES["«Service» EditalService\nOrquestra R1-R5"]
        CS["«Service» ChatService\nRAG Q&A"]
        GS["«Service» GoNoGoService\nMatching sem LLM"]
        RULES["«Strategy» AnalysisRules\nR1: LegalSummary\nR2: RequiredDocs\nR3: PriceRange\nR4: ImportantDates\nR5: Embedding"]
        PDFX["«Adapter» PDFExtractor\npdfplumber"]
    end

    subgraph LLM["«AI Runtime» Ollama"]
        MISTRAL["«Model» Mistral\nGeracao R1-R4"]
        NOMIC["«Model» nomic-embed-text\nEmbeddings R5"]
    end

    subgraph Dados["«Persistence»"]
        SB["«Cloud DB» Supabase\nPostgreSQL\neditais\nedital_analysis\nsuppliers"]
        CHR["«Local DB» ChromaDB\nedital_chunks\nsupplier_catalogue"]
        TG["«Trigger» on_edital_inserted\nHTTP POST automatico"]
    end

    subgraph Externo["«External Systems»"]
        M1["«System» Modulo 1\nBusca Editais"]
        M2["«System» Modulo 2\nPerfil Fornecedor"]
    end

    UI <-->|"«HTTP/JSON»"| API
    API --> ES
    API --> CS
    API --> GS
    ES --> RULES
    ES --> PDFX
    RULES -->|"«HTTP» localhost:11434"| MISTRAL
    RULES -->|"«HTTP» localhost:11434"| NOMIC
    ES -->|"«HTTPS» supabase-py"| SB
    RULES -->|"«Python API» local"| CHR
    CS -->|"«Python API»"| CHR
    CS -->|"«HTTP»"| MISTRAL
    GS -->|"«HTTPS»"| SB
    M1 -->|"«HTTPS» INSERT"| SB
    M2 -->|"«HTTPS» INSERT"| SB
    SB --> TG
    TG -->|"«HTTP POST»"| API
```
