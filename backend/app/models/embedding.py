"""Embedding ORM model — pgvector storage for RAG."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, index=True)  # 'sponsor' | 'email' | 'insight'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    vector = Column(Vector(1536), nullable=False)
    metadata_ = Column("metadata_", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
