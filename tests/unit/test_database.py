from types import SimpleNamespace

import pytest
from sqlalchemy.exc import OperationalError

from net2vec.persistence import database


def test_postgresql_engine_uses_five_second_connection_timeout(monkeypatch) -> None:  # noqa: ANN001
    observed = {}

    def create_engine(url, **kwargs):  # noqa: ANN001, ANN202
        observed.update(url=url, **kwargs)
        return SimpleNamespace()

    monkeypatch.setattr(database, "create_engine", create_engine)

    database.create_database_engine("postgresql+psycopg://localhost/net2vec")

    assert observed["connect_args"] == {"connect_timeout": 5}


def test_non_postgresql_engine_does_not_receive_driver_specific_timeout(monkeypatch) -> None:  # noqa: ANN001
    observed = {}

    def create_engine(url, **kwargs):  # noqa: ANN001, ANN202
        observed.update(url=url, **kwargs)
        return SimpleNamespace()

    monkeypatch.setattr(database, "create_engine", create_engine)

    database.create_database_engine("sqlite+pysqlite:///:memory:")

    assert observed["connect_args"] == {}


def test_database_preflight_wraps_connection_failure() -> None:
    session = SimpleNamespace(execute=_connection_failure)

    with pytest.raises(database.DatabaseConnectionError, match="5-second timeout per address"):
        database.verify_database_connection(session)


def _connection_failure(statement) -> None:  # noqa: ANN001
    raise OperationalError("SELECT 1", {}, RuntimeError("unavailable"))
