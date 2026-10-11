import importlib

from sqlalchemy import Boolean

from net2vec.persistence.models import SourceDocumentRecord


def test_source_document_model_has_nullable_corpus_provenance() -> None:
    table = SourceDocumentRecord.__table__

    for name in ("corpus_id", "manifest_source_id", "source_classification", "resolved_url"):
        assert table.c[name].nullable is True


def test_source_document_model_uses_active_only_unique_index() -> None:
    indexes = {item.name: item for item in SourceDocumentRecord.__table__.indexes}
    index = indexes["uq_active_source_url"]

    assert index.unique is True
    assert [expression.name for expression in index.expressions] == ["source_url"]
    assert str(index.dialect_options["postgresql"]["where"]) == "active"


def test_provenance_migration_adds_columns_and_active_only_index(monkeypatch) -> None:
    recorder = MigrationRecorder()
    migration = importlib.import_module(
        "net2vec.persistence.migrations.versions.0002_add_corpus_provenance",
    )
    monkeypatch.setattr(migration, "op", recorder)

    migration.upgrade()

    assert recorder.added_columns == [
        ("source_documents", "corpus_id"),
        ("source_documents", "manifest_source_id"),
        ("source_documents", "source_classification"),
        ("source_documents", "resolved_url"),
    ]
    assert recorder.index == (
        "uq_active_source_url",
        "source_documents",
        ["source_url"],
        True,
        "active",
    )


def test_provenance_migration_columns_are_nullable_text(monkeypatch) -> None:
    recorder = MigrationRecorder()
    migration = importlib.import_module(
        "net2vec.persistence.migrations.versions.0002_add_corpus_provenance",
    )
    monkeypatch.setattr(migration, "op", recorder)

    migration.upgrade()

    assert all(column.nullable is True for column in recorder.columns)
    assert not any(isinstance(column.type, Boolean) for column in recorder.columns)


class MigrationRecorder:
    def __init__(self) -> None:
        self.added_columns = []
        self.columns = []
        self.index = None

    def execute(self, statement: str) -> None:
        assert "DROP CONSTRAINT IF EXISTS" in statement

    def add_column(self, table: str, column) -> None:  # noqa: ANN001
        self.added_columns.append((table, column.name))
        self.columns.append(column)

    def create_index(self, name, table, columns, unique, postgresql_where) -> None:  # noqa: ANN001
        self.index = (name, table, columns, unique, str(postgresql_where))
