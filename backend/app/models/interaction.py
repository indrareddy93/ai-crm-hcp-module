import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
import enum
from app.db.base import Base


class InteractionType(str, enum.Enum):
    in_person = "in_person"
    virtual = "virtual"
    phone = "phone"
    email = "email"


class Sentiment(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Source(str, enum.Enum):
    form = "form"
    chat = "chat"


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    hcp_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False
    )
    interaction_type: Mapped[str] = mapped_column(
        Enum(InteractionType, name="interaction_type_enum"), nullable=False, default="in_person"
    )
    interaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    products_discussed: Mapped[list] = mapped_column(ARRAY(String), nullable=True, default=list)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    raw_notes: Mapped[str] = mapped_column(Text, nullable=True)
    sentiment: Mapped[str] = mapped_column(
        Enum(Sentiment, name="sentiment_enum"), nullable=True, default="neutral"
    )
    key_entities: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    outcome: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(
        Enum(Source, name="source_enum"), nullable=False, default="form"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
