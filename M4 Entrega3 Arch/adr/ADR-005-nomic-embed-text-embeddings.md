# ADR-005: nomic-embed-text para Geração de Embeddings

**Status:** Aceito  
**Data:** 12/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

O pipeline RAG requer um modelo de embedding para converter chunks de texto e consultas de usuários em vetores para busca de similaridade. Opções consideradas:

1. OpenAI text-embedding-3-small — nuvem, $0,02/1M tokens, 1536 dimensões
2. Cohere embed-v3 — nuvem, pagamento por token, 1024 dimensões
3. nomic-embed-text — local via Ollama, gratuito, 768 dimensões

Embeddings devem ser gerados para cada chunk de cada edital (centenas de chunks por documento) e para cada consulta de usuário em tempo real. APIs na nuvem gerariam custos contínuos e adicionariam latência.

## Decisão

Utilizar nomic-embed-text rodando localmente via Ollama para toda geração de embeddings.

## Consequências

**Positivas:**
- Custo zero — sem cobranças por token, embeddings ilimitados
- Baixa latência — inferência local, sem ida e volta pela rede
- Privacidade — texto do edital nunca sai do servidor
- 768 dimensões é suficiente para tarefas de recuperação de documentos
- Roda na CPU se a GPU estiver ocupada com geração Mistral — compartilhamento flexível de recursos
- Consistente com ADR-002 (local-first, sem dependências de nuvem)

**Negativas:**
- Qualidade de recuperação inferior ao OpenAI text-embedding-3-large para consultas com nuances
- 768 dimensões vs 1536 significa resolução semântica ligeiramente menor
- Atualizações do modelo requerem `ollama pull` manual

**Mitigações:**
- Chunks sobrepostos (800 chars de sobreposição em chunks de 3200 chars) compensam menor precisão do embedding
- Recuperação top-5 com reranking pelo LLM de geração melhora a qualidade das respostas
- Pode ser trocado para mxbai-embed-large (1024d) ou multilingual-e5-large com uma única mudança de configuração + re-embedding
