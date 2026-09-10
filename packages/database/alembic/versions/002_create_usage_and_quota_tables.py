"""Create usage_records and user_quotas tables.

Revision ID: 002_create_usage_and_quota
Revises: 001_create_users
Create Date: 2026-09-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_create_usage_and_quota"
down_revision: Union[str, None] = "001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create usage_records table
    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("research_jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("request_type", sa.String(length=50), nullable=False, server_default="complete"),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_usage_records_user_id", "usage_records", ["user_id"], unique=False)
    op.create_index("ix_usage_records_job_id", "usage_records", ["job_id"], unique=False)
    op.create_index("ix_usage_records_provider", "usage_records", ["provider"], unique=False)
    op.create_index("ix_usage_records_model", "usage_records", ["model"], unique=False)
    op.create_index("ix_usage_records_created_at", "usage_records", ["created_at"], unique=False)

    # 2. Create user_quotas table
    op.create_table(
        "user_quotas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("daily_token_limit", sa.Integer(), nullable=True),
        sa.Column("daily_cost_limit", sa.Float(), nullable=True),
        sa.Column("tokens_used_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_used_today", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("max_concurrent_jobs", sa.Integer(), nullable=True),
        sa.Column("last_reset_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_quotas_user_id", "user_quotas", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_user_quotas_user_id", table_name="user_quotas")
    op.drop_table("user_quotas")

    op.drop_index("ix_usage_records_created_at", table_name="usage_records")
    op.drop_index("ix_usage_records_model", table_name="usage_records")
    op.drop_index("ix_usage_records_provider", table_name="usage_records")
    op.drop_index("ix_usage_records_job_id", table_name="usage_records")
    op.drop_index("ix_usage_records_user_id", table_name="usage_records")
    op.drop_table("usage_records")
