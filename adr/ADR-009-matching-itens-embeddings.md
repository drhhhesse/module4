# ADR-009: Matching de Itens Edital vs Catálogo do Fornecedor via Embeddings

**Status:** Aceito  
**Data:** 13/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

A regra R6 (Go/No-Go) precisa verificar se o fornecedor oferece os itens solicitados no edital. O problema é que editais e catálogos de fornecedores usam descrições diferentes para o mesmo item:

- Edital: "Lâmpada LED"
- Fornecedor: "LED E26"
- Outro fornecedor: "Luminária LED tipo bulbo"

Comparação textual exata falha. É necessário comparação semântica.

## Opções Consideradas

1. **Dicionário de sinônimos** - manutenção manual, não escala
2. **Similaridade por embeddings** - semântica, automática, já disponível no pipeline

## Decisão

Utilizar similaridade por embeddings (cosine similarity) para matching de itens. O pipeline de embeddings (nomic-embed-text + ChromaDB) já existe para o RAG - reutilizar para matching de catálogo.

## Implementação

### Contrato de Interface com Módulo 2

O Módulo 2 deve popular a tabela `supplier_catalogue` no Supabase:

```sql
CREATE TABLE supplier_catalogue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    item_description TEXT NOT NULL,
    catmat_code TEXT,
    unit TEXT,
    unit_price FLOAT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Fluxo de Matching (dentro de R6)

1. R3 extrai lista de itens do edital com descrições e preços
2. Módulo 4 embeda cada item do edital via nomic-embed-text
3. Busca no ChromaDB (coleção `supplier_catalogue`) os itens mais similares do fornecedor
4. Classificação por score de similaridade:
   - **> 0.85** - match automático 
   - **0.60 – 0.85** - match provável, requer revisão humana 
   - **< 0.60** - sem match 

### Indexação do Catálogo

Quando o Módulo 2 insere/atualiza itens em `supplier_catalogue`, o Módulo 4 embeda e indexa no ChromaDB (coleção separada dos chunks de editais):

```python
def index_catalogue_item(item):
    embedding = get_embedding(item["item_description"])
    chromadb_catalogue.add(
        documents=[item["item_description"]],
        embeddings=[embedding],
        ids=[str(item["id"])],
        metadatas=[{
            "supplier_id": str(item["supplier_id"]),
            "unit_price": item["unit_price"],
            "unit": item["unit"]
        }]
    )
```

## Consequências

**Positivas:**
- Matching semântico - funciona mesmo com descrições diferentes para o mesmo item
- Reutiliza infraestrutura existente (Ollama + ChromaDB) - zero custo adicional
- Escala automaticamente - quanto mais itens no catálogo, mais preciso
- Sem manutenção manual de dicionários ou tabelas de sinônimos
- Score de similaridade é transparente e auditável

**Negativas:**
- Dependente da qualidade das descrições do fornecedor (descrições vagas = match ruim)
- Pode gerar falsos positivos em categorias similares (ex: "LED T8 18W" vs "LED T5 14W")
- Requer re-indexação quando o catálogo do fornecedor muda

**Mitigações:**
- Faixa de revisão humana (0.60-0.85) para casos ambíguos
- Incluir unidade e preço unitário como filtros secundários pós-matching
- Trigger no Supabase para re-indexar automaticamente quando `supplier_catalogue` é atualizado
