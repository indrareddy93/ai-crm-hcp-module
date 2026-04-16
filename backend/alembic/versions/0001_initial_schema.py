"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # hcps — no enum types needed
    op.create_table(
        "hcps",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("specialty", sa.String(150), nullable=True),
        sa.Column("hospital", sa.String(200), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # interactions — use sa.Text for enum columns; add CHECK constraints for validation
    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "hcp_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("hcps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "interaction_type",
            sa.Text,
            nullable=False,
            server_default="in_person",
        ),
        sa.Column(
            "interaction_date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("products_discussed", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("raw_notes", sa.Text, nullable=True),
        sa.Column("sentiment", sa.Text, nullable=True, server_default="neutral"),
        sa.Column("key_entities", postgresql.JSONB, nullable=True),
        sa.Column("outcome", sa.Text, nullable=True),
        sa.Column("source", sa.Text, nullable=False, server_default="form"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_check_constraint(
        "ck_interaction_type",
        "interactions",
        "interaction_type IN ('in_person', 'virtual', 'phone', 'email')",
    )
    op.create_check_constraint(
        "ck_sentiment",
        "interactions",
        "sentiment IN ('positive', 'neutral', 'negative')",
    )
    op.create_check_constraint(
        "ck_source",
        "interactions",
        "source IN ('form', 'chat')",
    )

    # followups
    op.create_table(
        "followups",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "interaction_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("interactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "hcp_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("hcps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_check_constraint(
        "ck_followup_status",
        "followups",
        "status IN ('pending', 'done')",
    )


def downgrade() -> None:
    op.drop_table("followups")
    op.drop_table("interactions")
    op.drop_table("hcps")
