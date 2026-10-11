"""Database session setup."""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_CONNECT_TIMEOUT_SECONDS = 5


class DatabaseConnectionError(RuntimeError):
    """Raised when the configured database cannot be reached."""


def create_database_engine(
    database_url: str,
    connect_timeout: int = DEFAULT_CONNECT_TIMEOUT_SECONDS,
) -> Engine:
    connect_args = _connect_args(database_url, connect_timeout)
    return create_engine(database_url, connect_args=connect_args)


def create_session_factory(database_url: str) -> Callable[[], Session]:
    engine = create_database_engine(database_url)
    return sessionmaker(bind=engine, expire_on_commit=False)


def verify_database_connection(session: Session) -> None:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise DatabaseConnectionError(
            "database connection failed (5-second timeout per address); "
            "verify DATABASE_URL and database status",
        ) from exc


def _connect_args(database_url: str, connect_timeout: int) -> dict[str, int]:
    if make_url(database_url).get_backend_name() == "postgresql":
        return {"connect_timeout": connect_timeout}
    return {}
