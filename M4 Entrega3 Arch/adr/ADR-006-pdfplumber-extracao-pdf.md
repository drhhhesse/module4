# ADR-006: pdfplumber para Extração de Texto de PDFs

**Status:** Aceito  
**Data:** 12/05/2026  
**Autor:** Henrique Hayes Hesse

## Contexto

Editais são entregues como documentos PDF, frequentemente com 30-100+ páginas. O Módulo 4 precisa extrair texto bruto de forma confiável tanto para análise LLM (R1-R4) quanto para chunking/embedding (R5). Opções consideradas:

1. PyPDF2 / PyPDF — leve, Python puro, mas tratamento ruim de layouts complexos
2. pdfplumber — construído sobre pdfminer, boa extração de tabelas, preserva estrutura de layout
3. Apache Tika — baseado em Java, dependência pesada, requer modo servidor
4. OCR (Tesseract) — para PDFs digitalizados, lento, propenso a erros em documentos digitais

A maioria dos editais de portais governamentais brasileiros são PDFs digitais (não digitalizados), com texto embutido, tabelas e seções estruturadas.

## Decisão

Utilizar pdfplumber como biblioteca principal de extração de texto de PDFs.

## Consequências

**Positivas:**
- Lida com layouts complexos comuns em documentos governamentais brasileiros
- Extração de tabelas preserva estrutura de linhas/colunas — crítico para tabelas de preços em editais
- Python puro — sem dependência Java, sem processo servidor
- Extração página por página permite processamento direcionado (ex: pular páginas de capa)
- Manutenção ativa e boa documentação

**Negativas:**
- Não consegue lidar com PDFs digitalizados (sem OCR) — necessitaria fallback Tesseract para documentos antigos
- Mais lento que PyPDF para PDFs simples com apenas texto
- Uso de memória escala com número de páginas — PDFs muito grandes podem precisar paginação

**Mitigações:**
- Adicionar fallback OCR Tesseract para PDFs digitalizados em sprint futuro
- Processar PDFs página por página para controlar uso de memória
- Validar qualidade da extração comparando contagem de caracteres com faixas esperadas
