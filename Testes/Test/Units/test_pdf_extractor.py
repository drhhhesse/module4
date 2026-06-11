"""
Testes de unidade — PDFExtractor
Responsável: Henrique Hayes Hesse (Plano de Testes, Seção 7)
Técnica: Caixa-Branca (cobertura de branch)
"""
import pytest


@pytest.mark.unit
class TestPDFExtractor:
    """Validação da extração de texto e regras de aceitação de arquivos."""

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-002")
    def test_rejeita_extensao_nao_pdf(self):
        """CT-002: arquivo .docx deve ser rejeitado antes do processamento."""
        # from src.services.pdf_extractor import PDFExtractor
        # with pytest.raises(UnsupportedFormatError):
        #     PDFExtractor().validate("proposta_comercial.docx")
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-005")
    def test_pdf_corrompido_nao_gera_crash(self, pdf_corrompido):
        """CT-005: PDF com bytes inválidos deve levantar erro tratável, sem crash."""
        # from src.services.pdf_extractor import PDFExtractor, ExtractionError
        # with pytest.raises(ExtractionError):
        #     PDFExtractor().extract(pdf_corrompido)
        ...

    @pytest.mark.boundary
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-003/CT-004")
    def test_valor_limite_paginas(self):
        """CT-003/CT-004: 200 páginas aceito (limite), 201 recusado (acima)."""
        # Particionamento: [1..200] válido | [201..∞) inválido
        # Valor limite: testar exatamente 200 e 201
        ...
