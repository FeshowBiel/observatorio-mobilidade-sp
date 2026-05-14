"""Job: coleta posições atuais de todos os ônibus e salva em raw.olho_vivo_posicoes."""
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import text

from ..db import connection
from ..sptrans_client import SPTransClient

logger = logging.getLogger(__name__)

INSERT_SQL = text("""
    INSERT INTO raw.olho_vivo_posicoes
        (hora_referencia, codigo_linha, prefixo_veiculo,
         latitude, longitude, acessivel, raw_payload)
    VALUES
        (:hora_referencia, :codigo_linha, :prefixo_veiculo,
         :latitude, :longitude, :acessivel, :raw_payload)
""")


def run() -> int:
    """Coleta posições e retorna número de registros inseridos."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    with SPTransClient() as client:
        data = client.get_all_posicoes()

    hora_ref = (
        datetime.fromisoformat(data["hr"].replace("Z", "+00:00"))
        if "T" in data.get("hr", "")
        else datetime.now(timezone.utc)
    )

    rows = []
    for linha in data.get("l", []):
        codigo_linha = linha.get("cl")
        for veiculo in linha.get("vs", []):
            rows.append({
                "hora_referencia": hora_ref,
                "codigo_linha": codigo_linha,
                "prefixo_veiculo": str(veiculo.get("p")),
                "latitude": veiculo.get("py"),
                "longitude": veiculo.get("px"),
                "acessivel": veiculo.get("a"),
                "raw_payload": json.dumps(veiculo),
            })

    if not rows:
        logger.warning("Nenhuma posição recebida da API")
        return 0

    with connection() as conn:
        conn.execute(INSERT_SQL, rows)

    logger.info("Inseridos %d registros de posições", len(rows))
    return len(rows)


if __name__ == "__main__":
    run()
