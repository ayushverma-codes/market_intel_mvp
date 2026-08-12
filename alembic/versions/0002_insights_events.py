"""add insights and agent events"""
from alembic import op
import sqlalchemy as sa

revision = "0002_insights_events"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trend_id", sa.Integer(), sa.ForeignKey("trends.id", ondelete="CASCADE"), nullable=False),
        sa.Column("india_relevance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("business_impact", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("recommendation", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(32), nullable=False, server_default="processing"),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_insights_status", "insights", ["status"])
    op.create_index("ix_insights_confidence", "insights", ["confidence"])
    op.create_table(
        "agent_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("insight_id", sa.Integer(), sa.ForeignKey("insights.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent", sa.String(100), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_index("ix_agent_events_insight_id", "agent_events", ["insight_id"])
    op.create_index("ix_agent_events_agent", "agent_events", ["agent"])
    op.create_index("ix_agent_events_status", "agent_events", ["status"])


def downgrade() -> None:
    op.drop_table("agent_events")
    op.drop_table("insights")
