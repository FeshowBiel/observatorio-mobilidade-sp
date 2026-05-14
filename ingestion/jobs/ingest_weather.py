"""Job: coleta clima horário do Open-Meteo e salva em raw.weather_horario."""
import json
import logging
from datetime import datetime

from sqlalchemy import text

from ..db import connection
from ..weather_client import WeatherClient

logger = logging.getLogger(__name__)

INSERT_SQL = text("""
    INSERT INTO raw.weather_horario
        (hora_referencia, latitude, longitude,
         temperatura_c, precipitacao_mm, velocidade_vento_kmh, raw_payload)
    VALUES
        (:hora_referencia, :latitude, :longitude,
         :temperatura_c, :precipitacao_mm, :velocidade_vento_kmh, :raw_payload)
    ON CONFLICT (hora_referencia) DO UPDATE SET
        temperatura_c = EXCLUDED.temperatura_c,
        precipitacao_mm = EXCLUDED.precipitacao_mm,
        velocidade_vento_kmh = EXCLUDED.velocidade_vento_kmh,
        raw_payload = EXCLUDED.raw_payload,
        coletado_em = NOW()
""")


def run() -> int:
    """Coleta previsão horária e retorna número de registros upsertados."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    with WeatherClient() as client:
        data = client.get_forecast()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    precips = hourly.get("precipitation", [])
    winds = hourly.get("wind_speed_10m", [])

    lat = data.get("latitude")
    lon = data.get("longitude")

    rows = []
    for i, t in enumerate(times):
        row_data = {
            "time": t,
            "temperature_2m": temps[i] if i < len(temps) else None,
            "precipitation": precips[i] if i < len(precips) else None,
            "wind_speed_10m": winds[i] if i < len(winds) else None,
        }
        rows.append({
            "hora_referencia": datetime.fromisoformat(t),
            "latitude": lat,
            "longitude": lon,
            "temperatura_c": row_data["temperature_2m"],
            "precipitacao_mm": row_data["precipitation"],
            "velocidade_vento_kmh": row_data["wind_speed_10m"],
            "raw_payload": json.dumps(row_data),
        })

    if not rows:
        logger.warning("Nenhum dado de clima recebido")
        return 0

    with connection() as conn:
        conn.execute(INSERT_SQL, rows)

    logger.info("Upsertados %d registros de clima", len(rows))
    return len(rows)


if __name__ == "__main__":
    run()
