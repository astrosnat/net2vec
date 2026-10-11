"""Add curated corpus provenance and active-only source uniqueness."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_add_corpus_provenance"
down_revision = "0001_enable_pgvector"
branch_labels = None
depends_on = None

INDEX_NAME = "uq_active_source_url"
TABLE_NAME = "source_documents"
PROVENANCE_COLUMNS = (
    ("corpus_id", 128),
    ("manifest_source_id", 128),
    ("source_classification", 32),
)


def upgrade() -> None:
    op.execute(f"ALTER TABLE {TABLE_NAME} DROP CONSTRAINT IF EXISTS {INDEX_NAME}")
    for name, length in PROVENANCE_COLUMNS:
        op.add_column(TABLE_NAME, sa.Column(name, sa.String(length=length), nullable=True))
    op.add_column(TABLE_NAME, sa.Column("resolved_url", sa.Text(), nullable=True))
    op.create_index(
        INDEX_NAME,
        TABLE_NAME,
        ["source_url"],
        unique=True,
        postgresql_where=sa.text("active"),
    )


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name=TABLE_NAME)
    op.drop_column(TABLE_NAME, "resolved_url")
    for name, _length in reversed(PROVENANCE_COLUMNS):
        op.drop_column(TABLE_NAME, name)
