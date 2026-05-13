# ADR-007: Processamento Automático via Trigger PostgreSQL

**Status:** Aceito  
**Data:** 13/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

O Módulo 1 busca editais em portais de licitação e salva os PDFs no Supabase. O Módulo 4 precisa processar cada edital automaticamente assim que ele chega — sem intervenção humana para disparar a análise.

Opções consideradas:

1. Polling (cron job) — verifica a tabela a cada N minutos buscando status "pending"
2. Supabase Realtime (WebSocket) — escuta eventos de INSERT em tempo real
3. Trigger PostgreSQL — função executada automaticamente no banco após cada INSERT

## Decisão

Utilizar um trigger PostgreSQL na tabela `editais` que dispara uma chamada HTTP para o endpoint `/api/analyze/{edital_id}` do FastAPI sempre que um novo edital é inserido pelo Módulo 1.

## Implementação

```sql
CREATE EXTENSION IF NOT EXISTS http;

CREATE OR REPLACE FUNCTION notify_module4()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM http_post(
        'http://SERVER:8400/api/analyze/' || NEW.id::text,
        '',
        'application/json'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_edital_inserted
    AFTER INSERT ON editais
    FOR EACH ROW
    EXECUTE FUNCTION notify_module4();
```

## Consequências

**Positivas:**
- Zero latência — processamento inicia imediatamente após inserção
- Sem polling — não consome recursos verificando a tabela repetidamente
- Sem dependência de WebSocket — mais simples que Supabase Realtime
- O banco de dados é a fila de mensagens — sem infraestrutura adicional (RabbitMQ, Redis, etc.)
- Módulo 1 não precisa saber que o Módulo 4 existe — desacoplamento total

**Negativas:**
- Requer extensão `http` habilitada no Supabase (disponível no tier gratuito)
- Se o servidor FastAPI estiver offline, o trigger falha silenciosamente — necessita tratamento de erro
- Chamadas HTTP dentro de triggers podem aumentar latência do INSERT para o Módulo 1

**Mitigações:**
- Adicionar campo `status` na tabela editais (pending → processing → done → error) para rastreamento
- Implementar retry: um cron job de fallback a cada 5 minutos processa editais com status "pending" que o trigger não conseguiu processar
- Log de erros no campo `error_message` da tabela para diagnóstico
