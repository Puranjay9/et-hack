"""Pydantic schemas for Outreach (emails)."""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class OutreachResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    contact_id: Optional[UUID] = None
    status: str
    subject: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    eval_score: Optional[float] = None
    eval_details: Optional[Dict[str, Any]] = None
    follow_up_dates: Optional[List[str]] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OutreachUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None


class SendEmailRequest(BaseModel):
    outreach_ids: Optional[List[UUID]] = None  # None = send all scheduled for campaign


class TestEmailRequest(BaseModel):
    to_email: str
