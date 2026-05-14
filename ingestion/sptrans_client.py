"""Cliente HTTP da API Olho Vivo da SPTrans."""
import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import config

logger = logging.getLogger(__name__)

BASE_URL = "http://api.olhovivo.sptrans.com.br/v2.1"


class SPTransClient:
    """Cliente da API Olho Vivo. Mantém cookie de sessão entre chamadas."""

    def __init__(self, token: str | None = None):
        self.token = token or config.sptrans_token
        self.client = httpx.Client(base_url=BASE_URL, timeout=30.0)
        self._authenticated = False

    def authenticate(self) -> bool:
        response = self.client.post(
            "/Login/Autenticar",
            params={"token": self.token},
        )
        response.raise_for_status()
        success = response.json() is True
        self._authenticated = success
        if not success:
            raise RuntimeError("Falha na autenticação com SPTrans")
        logger.info("Autenticado com sucesso na API Olho Vivo")
        return success

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _get(self, path: str, **params) -> Any:
        if not self._authenticated:
            self.authenticate()
        response = self.client.get(path, params=params)
        if response.status_code == 401:
            self.authenticate()
            response = self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def get_all_posicoes(self) -> dict:
        return self._get("/Posicao")

    def get_posicoes_por_linha(self, codigo_linha: int) -> dict:
        return self._get("/Posicao/Linha", codigoLinha=codigo_linha)

    def buscar_linhas(self, termos: str) -> list:
        return self._get("/Linha/Buscar", termosBusca=termos)

    def get_previsao(self, codigo_parada: int, codigo_linha: int) -> dict:
        return self._get("/Previsao", codigoParada=codigo_parada, codigoLinha=codigo_linha)

    def get_corredores(self) -> list:
        return self._get("/Corredor")

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
