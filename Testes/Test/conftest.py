"""
Fixtures compartilhadas — Módulo 4: Análise Inteligente de Editais
Estratégia de mocks conforme Plano de Testes (Seção 6):
isolar OllamaClient, ChromaDBClient e SupabaseClient.
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_ollama():
    """Mock do OllamaClient — evita dependência do serviço local."""
    client = MagicMock()
    client.generate.return_value = {
        "response": "O prazo máximo de entrega é de 30 dias corridos.",
        "done": True,
    }
    client.embed.return_value = {"embedding": [0.1] * 768}
    return client


@pytest.fixture
def mock_ollama_offline():
    """Mock do OllamaClient indisponível — CT-008."""
    client = MagicMock()
    client.generate.side_effect = ConnectionError("Ollama service unavailable")
    client.embed.side_effect = ConnectionError("Ollama service unavailable")
    return client


@pytest.fixture
def mock_chromadb():
    """Mock do ChromaDBClient — coleção de teste em memória."""
    collection = MagicMock()
    collection.query.return_value = {
        "documents": [["Prazo de entrega: 30 dias corridos a partir da assinatura."]],
        "metadatas": [[{"page": 12, "edital_id": "edital_pregao_01"}]],
        "distances": [[0.18]],
    }
    collection.count.return_value = 247
    return collection


@pytest.fixture
def pdf_valido(tmp_path):
    """PDF mínimo válido para testes de upload (CT-001)."""
    pdf = tmp_path / "edital_teste.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")
    return pdf


@pytest.fixture
def pdf_corrompido(tmp_path):
    """PDF com cabeçalho adulterado — CT-005."""
    pdf = tmp_path / "edital_corrompido.pdf"
    pdf.write_bytes(b"NOT_A_PDF_HEADER\x00\x01\x02corrupted bytes")
    return pdf
