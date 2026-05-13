# ADR-002: Mistral Local (Ollama) em vez de APIs de LLM na Nuvem

**Status:** Aceito  
**Data:** 12/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

O Módulo 4 requer um LLM para duas tarefas: extração estruturada de editais em PDF (regras R1-R4) e geração de respostas no chat RAG. Opções consideradas:

1. API OpenAI (GPT-4o) — nuvem, pagamento por token, maior qualidade
2. API Anthropic (Claude) — nuvem, pagamento por token, alta qualidade
3. Mistral via Ollama — local, gratuito, roda no hardware existente (RTX 3060 12GB)

Editais contêm dados sensíveis de licitações (preços, requisitos de fornecedores, detalhes de contratos governamentais). Enviar esses dados para APIs na nuvem levanta questões de privacidade e conformidade para uma plataforma de licitações públicas brasileiras.

## Decisão

Rodar Mistral localmente via Ollama no servidor do projeto (i5-12400, RTX 3060 12GB, 48GB DDR4). Sem dependências de LLM na nuvem. Sem chaves de API. Sem custos por token.

## Consequências

**Positivas:**
- Custo zero por consulta — processamento ilimitado
- Dados nunca saem do servidor — privacidade e conformidade garantidas
- Sem dependência de internet para inferência LLM — funciona offline
- Controle total sobre versão e comportamento do modelo
- API compatível com OpenAI (localhost:11434) — fácil trocar modelos futuramente

**Negativas:**
- Qualidade inferior ao GPT-4o ou Claude para raciocínio jurídico complexo
- Limitado a modelos que cabem em 12GB de VRAM (Mistral 7B, Qwen 14B em Q4)
- O servidor precisa estar ligado para o pipeline funcionar
- Sem atualizações automáticas do modelo

**Mitigações:**
- Prompts JSON estruturados com campos explícitos reduzem alucinações
- R1-R4 são tarefas de extração, não geração criativa — modelos menores performam bem
- Modelo pode ser atualizado para Mistral Large ou Qwen 32B se o hardware for expandido
