# ADR-004: Pipeline de Regras em Cascata para Análise de Editais

**Status:** Aceito  
**Data:** 12/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

O Módulo 4 precisa extrair múltiplos tipos de informação estruturada de editais em PDF: requisitos legais, documentos necessários, faixa de preços, datas importantes, embeddings para RAG e recomendação Go/No-Go. As opções de implementação são:

1. Um único prompt monolítico de LLM que extrai tudo de uma vez
2. Endpoints independentes chamados em qualquer ordem
3. Um pipeline em cascata onde cada regra é executada sequencialmente

Um prompt monolítico seria pouco confiável — LLMs perdem precisão quando solicitados a extrair 6 tipos diferentes de dados simultaneamente de um documento de 50+ páginas. Endpoints independentes deixariam a orquestração para o frontend.

## Decisão

Implementar um pipeline de regras em cascata (R1 → R2 → R3 → R4 → R5 → R6) onde cada regra é um passo de extração independente com seu próprio prompt, executado sequencialmente, com resultados armazenados no Supabase após cada etapa.

## Consequências

**Positivas:**
- Cada regra tem um prompt focado e específico — maior precisão na extração
- Se uma regra falhar, os resultados anteriores já estão salvos — análise parcial ainda é útil
- Regras podem ser re-executadas independentemente (ex: re-executar R3 após correção de preço)
- Pipeline é extensível — adicionar R7 (ex: critérios de sustentabilidade) requer apenas uma nova função e prompt
- A saída de cada regra é testável e auditável independentemente
- Arquitetura espelha padrões comprovados em sistemas de produção (validação em cascata por gates)

**Negativas:**
- Execução sequencial é mais lenta que paralela (mitigado rodando R1-R4 concorrentemente no futuro)
- Múltiplas chamadas de LLM por edital consomem mais tempo de GPU que uma única chamada
- Cada regra recebe o texto completo do edital — carregamento de contexto redundante

**Notas de Design:**
- R1-R4 são regras de extração via LLM (baseadas em prompt, retornam JSON)
- R5 é embedding + indexação (sem geração LLM, apenas modelo de embedding)
- R6 é lógica de negócio (sem LLM, cruza análise com perfil do fornecedor)
- Regras ordenadas por custo: R1-R4 (LLM) antes de R5 (embedding) antes de R6 (lógica)
