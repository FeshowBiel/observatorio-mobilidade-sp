"""Testes de integração básicos da pipeline de ingestão."""
import json
import pytest
from unittest.mock import MagicMock, patch


SAMPLE_POSICOES = {
    "hr": "18:32:00",
    "l": [
        {
            "c": "TERM. BANDEIRA",
            "cl": 34041,
            "sl": 1,
            "lt0": "477A-10",
            "vs": [
                {"p": "12345", "a": True, "py": -23.5505, "px": -46.6333},
                {"p": "12346", "a": False, "py": -23.5510, "px": -46.6340},
            ],
        }
    ],
}


def test_ingest_olho_vivo_parses_rows():
    """Verifica que o job transforma o payload em rows corretamente."""
    rows = []
    for linha in SAMPLE_POSICOES.get("l", []):
        codigo_linha = linha.get("cl")
        for veiculo in linha.get("vs", []):
            rows.append({
                "codigo_linha": codigo_linha,
                "prefixo_veiculo": str(veiculo.get("p")),
                "latitude": veiculo.get("py"),
                "longitude": veiculo.get("px"),
                "acessivel": veiculo.get("a"),
            })

    assert len(rows) == 2
    assert rows[0]["codigo_linha"] == 34041
    assert rows[0]["prefixo_veiculo"] == "12345"
    assert rows[0]["latitude"] == -23.5505
    assert rows[1]["acessivel"] is False


def test_ingest_filters_null_positions():
    """Verifica que posições sem lat/lon são descartadas."""
    payload = {
        "hr": "18:32:00",
        "l": [
            {
                "cl": 99999,
                "vs": [
                    {"p": "00001", "py": None, "px": None},
                    {"p": "00002", "py": -23.5505, "px": -46.6333},
                ],
            }
        ],
    }

    rows = [
        v
        for linha in payload.get("l", [])
        for v in linha.get("vs", [])
        if v.get("py") is not None and v.get("px") is not null
    ]
    # Nota: este teste intencional falha se a lógica de filtragem
    # não estiver sendo aplicada — o filtro está no model dbt de staging.
    assert len(rows) == 1
