"""Carrega configurações do .env"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    sptrans_token: str = os.getenv("SPTRANS_TOKEN", "")
    database_url: str = os.getenv("DATABASE_URL", "")
    weather_lat: float = float(os.getenv("WEATHER_LAT", "-23.5505"))
    weather_lon: float = float(os.getenv("WEATHER_LON", "-46.6333"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> None:
        if not self.sptrans_token:
            raise ValueError("SPTRANS_TOKEN não definido no .env")
        if not self.database_url:
            raise ValueError("DATABASE_URL não definido no .env")


config = Config()
