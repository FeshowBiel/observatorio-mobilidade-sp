"""Job: coleta cadastro de linhas 1x/dia e salva em raw.olho_vivo_linhas."""
import json
import logging

from sqlalchemy import text

from ..db import connection
from ..sptrans_client import SPTransClient

logger = logging.getLogger(__name__)

INSERT_SQL = text("""
    INSERT INTO raw.olho_vivo_linhas
        (codigo_linha, circular, letreiro, sentido, tipo,
         denominacao_terminal_principal, denominacao_terminal_secundario, raw_payload)
    VALUES
        (:codigo_linha, :circular, :letreiro, :sentido, :tipo,
         :denominacao_terminal_principal, :denominacao_terminal_secundario, :raw_payload)
    ON CONFLICT DO NOTHING
""")


def run() -> int:
    """Coleta cadastro de todas as linhas e retorna número de registros inseridos."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    with SPTransClient() as client:
        linhas = client.buscar_linhas("")

    if not linhas:
        logger.warning("Nenhuma linha retornada da API")
        return 0

    rows = [
        {
            "codigo_linha": l.get("cl"),
            "circular": l.get("lt0") == l.get("lt1"),
            "letreiro": l.get("lt0", ""),
            "sentido": l.get("sl"),
            "tipo": l.get("tp"),
            "denominacao_terminal_principal": l.get("tp", ""),
            "denominacao_terminal_secundario": l.get("ts", ""),
            "raw_payload": json.dumps(l),
        }
        for l in linhas
        if l.get("cl")
    ]

    with connection() as conn:
        conn.execute(INSERT_SQL, rows)

    logger.info("Inseridas/ignoradas %d linhas", len(rows))
    return len(rows)


if __name__ == "__main__":
    run()
