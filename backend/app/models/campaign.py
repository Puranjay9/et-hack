"""Campaign ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class CampaignStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.draft, nullable=False)
    type = Column(String(100))
    goal = Column(Text)
    target_audience = Column(Text)
    budget = Column(Numeric(12, 2))
    partnership_type = Column(String(100))
    target_sponsor_profile = Column(JSONB, default=dict)
    offerings = Column(JSONB, default=dict)
    strategy_output = Column(JSONB, default=dict)
    task_id = Column(String, nullable=True)  # Celery task ID for tracking
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="campaigns")
    company = relationship("Company", back_populates="campaigns")
    outreach_messages = relationship("Outreach", back_populates="campaign", lazy="selectin", cascade="all, delete-orphan")
