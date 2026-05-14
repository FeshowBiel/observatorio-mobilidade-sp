"""Conexão e helpers do Postgres"""
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import config


def get_engine() -> Engine:
    return create_engine(
        config.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


_engine: Engine | None = None


def engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


@contextmanager
def connection():
    with engine().begin() as conn:
        yield conn
