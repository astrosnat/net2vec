"""Database session setup."""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(database_url: str) -> Callable[[], Session]:
    engine = create_engine(database_url)
    return sessionmaker(bind=engine, expire_on_commit=False)
