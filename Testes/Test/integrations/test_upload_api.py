"""
Testes de integração — Upload e Indexação (US-001)
Responsável: Henrique Hayes Hesse / Heloíza Dettenborn
Técnica: Caixa-Cinza (FastAPI TestClient + ChromaDB de teste)
"""
import pytest


@pytest.mark.integration
class TestUploadAPI:
    """POST /api/upload — pipeline de ingestão completo."""

    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-001")
    def test_upload_pdf_valido_indexa_completo(self, pdf_valido, mock_chromadb):
        """CT-001: PDF válido → 200, chunks indexados, edital listado."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-002")
    def test_upload_docx_retorna_422(self):
        """CT-002: extensão .docx → HTTP 422, nenhum registro criado."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-005")
    def test_upload_corrompido_retorna_500_estruturado(self, pdf_corrompido):
        """CT-005: PDF corrompido → HTTP 500 com body estruturado, sistema funcional."""
        ...
