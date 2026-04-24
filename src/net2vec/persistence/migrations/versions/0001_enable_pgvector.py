"""Enable pgvector and create ingestion tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "0001_enable_pgvector"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "source_documents",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("retrieval_status", sa.String(length=32), nullable=False),
        sa.Column("http_status", sa.Integer()),
        sa.Column("content_hash", sa.String(length=64)),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "document_sections",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("heading_path", sa.ARRAY(sa.Text()), nullable=False),
        sa.Column("heading_text", sa.Text()),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("full_chunk_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["document_id"], ["source_documents.id"]),
    )


def downgrade() -> None:
    op.drop_table("document_sections")
    op.drop_table("source_documents")
