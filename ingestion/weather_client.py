"""Cliente da API Open-Meteo (clima). Não requer autenticação."""
import logging
from datetime import datetime, date

import httpx

from .config import config

logger = logging.getLogger(__name__)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

HOURLY_VARS = "temperature_2m,precipitation,wind_speed_10m,weathercode"


class WeatherClient:
    def __init__(self):
        self.lat = config.weather_lat
        self.lon = config.weather_lon
        self.client = httpx.Client(timeout=30.0)

    def get_forecast(self) -> dict:
        """Retorna previsão horária das próximas horas."""
        response = self.client.get(
            FORECAST_URL,
            params={
                "latitude": self.lat,
                "longitude": self.lon,
                "hourly": HOURLY_VARS,
                "timezone": "America/Sao_Paulo",
                "forecast_days": 2,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_historical(self, start_date: date, end_date: date) -> dict:
        """Retorna dados históricos horários para o período informado."""
        response = self.client.get(
            ARCHIVE_URL,
            params={
                "latitude": self.lat,
                "longitude": self.lon,
                "hourly": HOURLY_VARS,
                "timezone": "America/Sao_Paulo",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
