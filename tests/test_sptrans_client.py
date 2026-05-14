"""Testes unitários do SPTransClient."""
import pytest
from unittest.mock import MagicMock, patch


def test_client_authenticate_success():
    with patch("ingestion.sptrans_client.httpx.Client") as MockClient:
        mock_response = MagicMock()
        mock_response.json.return_value = True
        mock_response.raise_for_status = MagicMock()
        MockClient.return_value.post.return_value = mock_response

        from ingestion.sptrans_client import SPTransClient

        client = SPTransClient(token="fake-token")
        result = client.authenticate()

        assert result is True
        assert client._authenticated is True


def test_client_authenticate_failure():
    with patch("ingestion.sptrans_client.httpx.Client") as MockClient:
        mock_response = MagicMock()
        mock_response.json.return_value = False
        mock_response.raise_for_status = MagicMock()
        MockClient.return_value.post.return_value = mock_response

        from ingestion.sptrans_client import SPTransClient

        client = SPTransClient(token="invalid-token")
        with pytest.raises(RuntimeError, match="Falha na autenticação"):
            client.authenticate()
