from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    """Return a process-wide SQLAlchemy engine (requires database_url)."""
    if not settings.database_url:
        raise RuntimeError("settings.database_url is not configured")
    return create_engine(settings.database_url, pool_pre_ping=True)
