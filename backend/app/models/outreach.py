"""Outreach ORM model — stores generated emails and their delivery status."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class OutreachStatus(str, enum.Enum):
    scheduled = "scheduled"
    sent = "sent"
    opened = "opened"
    replied = "replied"
    failed = "failed"


class Outreach(Base):
    __tablename__ = "outreach"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    status = Column(SAEnum(OutreachStatus), default=OutreachStatus.scheduled, nullable=False)
    subject = Column(Text)
    body = Column(Text)
    cta = Column(Text)
    eval_score = Column(Float)
    eval_details = Column(JSONB, default=dict)  # Per-dimension scores
    follow_up_dates = Column(JSONB, default=list)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    campaign = relationship("Campaign", back_populates="outreach_messages")
    contact = relationship("Contact", back_populates="outreach_messages")
