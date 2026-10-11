"""Run net2vec database migrations."""

from __future__ import annotations

import argparse
import importlib
from types import ModuleType

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine

from net2vec.config.settings import Settings

MIGRATION_MODULES = (
    "net2vec.persistence.migrations.versions.0001_enable_pgvector",
    "net2vec.persistence.migrations.versions.0002_add_corpus_provenance",
)


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
    for migration in _migration_modules(command):
        _run_migration(command, operations, migration)


def _run_migration(command: str, operations: Operations, migration: ModuleType) -> None:
    original_op = migration.op
    migration.op = operations
    try:
        getattr(migration, command)()
    finally:
        migration.op = original_op


def _migration_modules(command: str) -> tuple[ModuleType, ...]:
    names = MIGRATION_MODULES if command == "upgrade" else tuple(reversed(MIGRATION_MODULES))
    return tuple(importlib.import_module(name) for name in names)


if __name__ == "__main__":
    main()
