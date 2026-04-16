import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Text, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class FollowupStatus(str, enum.Enum):
    pending = "pending"
    done = "done"


class Followup(Base):
    __tablename__ = "followups"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    interaction_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False
    )
    hcp_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(FollowupStatus, name="followup_status_enum"), nullable=False, default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
