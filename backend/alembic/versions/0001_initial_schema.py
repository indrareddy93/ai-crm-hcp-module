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

    op.execute("CREATE TYPE interaction_type_enum AS ENUM ('in_person', 'virtual', 'phone', 'email')")
    op.execute("CREATE TYPE sentiment_enum AS ENUM ('positive', 'neutral', 'negative')")
    op.execute("CREATE TYPE source_enum AS ENUM ('form', 'chat')")
    op.execute("CREATE TYPE followup_status_enum AS ENUM ('pending', 'done')")

    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("hcp_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_type", sa.Enum("in_person", "virtual", "phone", "email", name="interaction_type_enum", create_type=False), nullable=False, server_default="in_person"),
        sa.Column("interaction_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("products_discussed", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("raw_notes", sa.Text, nullable=True),
        sa.Column("sentiment", sa.Enum("positive", "neutral", "negative", name="sentiment_enum", create_type=False), nullable=True, server_default="neutral"),
        sa.Column("key_entities", postgresql.JSONB, nullable=True),
        sa.Column("outcome", sa.Text, nullable=True),
        sa.Column("source", sa.Enum("form", "chat", name="source_enum", create_type=False), nullable=False, server_default="form"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "followups",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hcp_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("pending", "done", name="followup_status_enum", create_type=False), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("followups")
    op.drop_table("interactions")
    op.drop_table("hcps")
    op.execute("DROP TYPE IF EXISTS followup_status_enum")
    op.execute("DROP TYPE IF EXISTS source_enum")
    op.execute("DROP TYPE IF EXISTS sentiment_enum")
    op.execute("DROP TYPE IF EXISTS interaction_type_enum")
