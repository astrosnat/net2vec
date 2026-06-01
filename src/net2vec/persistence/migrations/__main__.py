"""Run net2vec database migrations."""

from __future__ import annotations

import argparse
import importlib
from types import ModuleType

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine

from net2vec.config.settings import Settings

MIGRATION_MODULE = "net2vec.persistence.migrations.versions.0001_enable_pgvector"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run net2vec database migrations")
    parser.add_argument("command", choices=("upgrade", "downgrade"))
    args = parser.parse_args()
    raise SystemExit(_run(args.command))


def _run(command: str) -> int:
    engine = create_engine(Settings.from_env().database_url)
    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        _run_command(command, Operations(context))
    return 0


def _run_command(command: str, operations: Operations) -> None:
    migration = _migration_module()
    original_op = migration.op
    migration.op = operations
    try:
        getattr(migration, command)()
    finally:
        migration.op = original_op


def _migration_module() -> ModuleType:
    return importlib.import_module(MIGRATION_MODULE)


if __name__ == "__main__":
    main()
