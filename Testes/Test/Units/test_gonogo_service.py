"""
Testes de unidade — GoNoGoService
Responsável: Alan da Silva Werner (Plano de Testes, Seção 7)
Técnica: Caixa-Branca — ADR-008 (matching sem LLM)
"""
import pytest


@pytest.mark.unit
class TestGoNoGoService:
    """Validação da lógica de recomendação Go/No-Go."""

    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-015")
    def test_perfil_compativel_retorna_go(self):
        """CT-015: empresa com CNAE, documentos e porte compatíveis → GO, score ≥ 0.75."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-016")
    def test_modulo2_offline_erro_amigavel(self):
        """CT-016: timeout do Módulo 2 → mensagem amigável, sem resultado parcial salvo."""
        ...
