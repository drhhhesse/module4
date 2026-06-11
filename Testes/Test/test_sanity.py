"""
Teste de sanidade — verifica que o framework pytest está operacional.
Pré-requisito da Aula 14 (Entrega 4).
"""


def test_framework_operacional():
    """O framework de testes está instalado e executando."""
    assert True


def test_fixtures_disponiveis(mock_ollama, mock_chromadb):
    """As fixtures de mock (Plano de Testes, Seção 6) estão acessíveis."""
    assert mock_ollama.generate()["done"] is True
    assert mock_chromadb.count() == 247
