"""initial market intelligence schema"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("credibility", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("url", name="uq_sources_url"),
    )
    op.create_index("ix_sources_timestamp", "sources", ["timestamp"])
    op.create_index("ix_sources_source", "sources", ["source"])
    op.create_index("ix_sources_source_type", "sources", ["source_type"])
    op.create_index("ix_sources_url", "sources", ["url"])

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("entity", sa.String(255), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("embedding", Vector(), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", "content_hash", name="uq_signal_source_content"),
    )
    op.create_index("ix_signals_timestamp", "signals", ["timestamp"])
    op.create_index("ix_signals_topic", "signals", ["topic"])
    op.create_index("ix_signals_entity", "signals", ["entity"])

    op.create_table(
        "trends",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("trend_score", sa.Float(), nullable=False),
        sa.Column("growth_rate", sa.Float(), nullable=False),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_trends_topic", "trends", ["topic"])
    op.create_index("ix_trends_last_seen", "trends", ["last_seen"])


def downgrade() -> None:
    op.drop_table("trends")
    op.drop_table("signals")
    op.drop_table("sources")
