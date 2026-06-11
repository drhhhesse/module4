"""
Testes de integração — Chat RAG (US-002)
Responsável: Heloíza Dettenborn (Plano de Testes, Seção 7)
Técnica: Caixa-Cinza (FastAPI ↔ ChromaDB ↔ Ollama mockado)
"""
import pytest


@pytest.mark.integration
class TestChatRAG:
    """POST /api/chat — fluxo RAG completo."""

    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-006")
    def test_pergunta_relevante_resposta_contextualizada(self, mock_ollama, mock_chromadb):
        """CT-006: pergunta sobre prazo → resposta com referência de página, ≤ 3s."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-007")
    def test_pergunta_fora_escopo_nao_inventa(self, mock_chromadb):
        """CT-007: similaridade abaixo do threshold → mensagem de ausência, sem alucinação."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-008")
    def test_ollama_offline_retorna_503(self, mock_ollama_offline):
        """CT-008: Ollama indisponível → HTTP 503, mensagem amigável, log registrado."""
        ...
