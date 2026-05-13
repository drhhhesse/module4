# ADR-001: Abordagem Híbrida — ChromaDB (RAG local) + Supabase (camada de dados compartilhada)

**Status:** Aceito  
**Data:** 12/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

O Módulo 4 utilizava originalmente o ChromaDB como banco de vetores local para RAG (Retrieval-Augmented Generation). O ChromaDB roda como SQLite + índice HNSW localmente, sem suporte a SQL e sem acesso compartilhado entre módulos.

O LicitaSoluções possui 4+ módulos que precisam compartilhar dados — o Módulo 1 grava editais, o Módulo 2 grava perfis de fornecedores, o Módulo 4 lê ambos para análise e recomendação Go/No-Go. O ChromaDB não pode servir como camada de dados compartilhada.

Porém, o ChromaDB funciona bem para sua finalidade original: busca vetorial rápida e local para o chat RAG.

## Decisão

Utilizar uma abordagem híbrida:
- **ChromaDB** permanece local para embeddings e busca de similaridade do RAG (rápido, sem latência de rede, já funcional)
- **Supabase (PostgreSQL)** serve como camada de dados compartilhada para dados estruturados: editais, resultados de análise (R1-R4), recomendações Go/No-Go e perfis de fornecedores

As regras de análise (R1-R4) rodam via Mistral localmente e fazem POST dos resultados estruturados no Supabase. Os embeddings (R5) são armazenados no ChromaDB localmente. Os outros módulos leem apenas do Supabase — nunca acessam o ChromaDB.

## Consequências

**Positivas:**
- Cada ferramenta faz o que faz melhor — ChromaDB para vetores, Postgres para dados estruturados
- Todos os módulos compartilham um único banco Postgres — integração por dados, não por API
- Extensão pgvector não necessária — simplifica a configuração do Supabase
- ChromaDB já funciona do sprint anterior — sem migração do pipeline de embeddings
- Consultas RAG permanecem rápidas (local, sem ida e volta pela rede)

**Negativas:**
- Dois bancos de dados para gerenciar em vez de um
- Dados de embedding não são acessíveis por outros módulos (isolados no ChromaDB)
- Se os dados do ChromaDB forem perdidos, é necessário re-embedding (mitigado re-executando R5)

**Neutras:**
- O tier gratuito do Supabase (500MB) é mais que suficiente para dados de análise estruturados
- ChromaDB não possui limites de tamanho no armazenamento local
