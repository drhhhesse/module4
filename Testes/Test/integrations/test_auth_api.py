"""
Testes de integração — Autenticação (US-006)
Técnica: Caixa-Cinza (FastAPI TestClient)
"""
import pytest


@pytest.mark.integration
class TestAuth:
    """Endpoints de autenticação e proteção de rotas."""

    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-011")
    def test_login_valido_retorna_jwt(self):
        """CT-011: credenciais corretas → 200, JWT em cookie httpOnly."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-012")
    def test_login_senha_errada_retorna_401(self):
        """CT-012: senha incorreta → 401, mensagem genérica, tentativa logada."""
        ...

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-013")
    def test_bloqueio_apos_5_tentativas(self):
        """CT-013: 5ª tentativa falha → conta bloqueada 15 min, HTTP 429."""
        ...

    @pytest.mark.negative
    @pytest.mark.skip(reason="Implementação na Aula 14 — CT-014")
    def test_rota_protegida_sem_token_retorna_401(self):
        """CT-014: GET /api/editais sem Authorization → 401, sem dados."""
        ...
