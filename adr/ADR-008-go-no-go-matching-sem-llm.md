# ADR-008: Lógica de Matching Go/No-Go (R6) - Sem LLM

**Status:** Aceito  
**Data:** 13/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

A regra R6 (Go/No-Go) precisa cruzar os requisitos extraídos do edital (R1-R4) com o perfil do fornecedor (Módulo 2) para gerar uma recomendação de participação. Opções:

1. Usar o LLM (Mistral) para comparar requisitos vs capacidades
2. Usar lógica de negócio pura (Python) com comparações estruturadas

## Decisão

Implementar R6 como lógica de negócio pura em Python, sem chamadas ao LLM. A comparação é feita entre dados estruturados (JSON) já extraídos pelas regras R1-R4 e o perfil do fornecedor armazenado no Supabase pelo Módulo 2.

## Justificativa

R6 não é uma tarefa de linguagem natural - é uma comparação estruturada entre dois conjuntos de dados:
- Documentos exigidos vs documentos disponíveis (operação de conjuntos)
- Preço teto vs preço médio do fornecedor (comparação numérica)
- Região de entrega vs regiões atendidas (lookup em lista)
- Qualificações técnicas exigidas vs certificações do fornecedor (interseção de conjuntos)

Usar LLM para isso seria mais lento, mais caro em GPU, e menos confiável que lógica determinística.

## Critérios de Matching

| Critério | Edital (R1-R4) | Fornecedor (Módulo 2) | Comparação |
|----------|----------------|----------------------|------------|
| Documentos | required_documents (R2) | documentos_disponiveis | Diferença de conjuntos |
| Preço | price_range.teto (R3) | preco_medio | Numérica (<=) |
| Região | local_entrega (R4) | regioes_atendidas | Pertencimento à lista |
| Qualificações | requisitos_tecnicos (R1) | certificacoes | Interseção de conjuntos |
| Prazo | prazo_execucao (R4) | capacidade_entrega | Numérica (<=) |

## Resultados Possíveis

- **GO**  - todos os critérios atendidos, fornecedor pode participar
- **GO COM RESSALVAS**  - uma lacuna menor, corrigível antes do prazo
- **NO-GO**  - múltiplos bloqueios, não vale a pena participar

## Consequências

**Positivas:**
- Determinístico - mesmo input sempre produz mesmo output (auditável)
- Rápido - milissegundos, sem espera de inferência LLM
- Transparente - cada critério mostra o que passou e o que faltou
- Testável - unit tests simples para cada comparação
- Não consome GPU - libera recursos para R1-R5

**Negativas:**
- Não captura nuances textuais que um LLM detectaria (ex: requisito ambíguo)
- Depende da qualidade da extração R1-R4 (lixo entra, lixo sai)

**Mitigações:**
- Adicionar campo "observações" onde o Analista pode ajustar manualmente
- Flag "confiança" baseado na completude dos dados extraídos
