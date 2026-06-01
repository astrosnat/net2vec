import importlib

from net2vec.persistence.models import DocumentSectionRecord


def test_document_section_model_uses_local_vector_dimension() -> None:
    assert DocumentSectionRecord.__table__.c.embedding.type.dim == 768


def test_initial_migration_uses_local_vector_dimension(monkeypatch) -> None:
    recorder = MigrationRecorder()
    migration = importlib.import_module(
        "net2vec.persistence.migrations.versions.0001_enable_pgvector",
    )
    monkeypatch.setattr(migration, "op", recorder)

    migration.upgrade()

    assert recorder.embedding_dimension("document_sections") == 768


class MigrationRecorder:
    def __init__(self) -> None:
        self.tables = {}

    def execute(self, statement: str) -> None:
        pass

    def create_table(self, name: str, *columns) -> None:
        self.tables[name] = columns

    def embedding_dimension(self, table: str) -> int:
        column = next(column for column in self.tables[table] if column.name == "embedding")
        return column.type.dim
