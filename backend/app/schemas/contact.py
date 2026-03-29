"""Pydantic schemas for Contact."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ContactCreate(BaseModel):
    company_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    role: Optional[str] = None
    linkedin: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    linkedin: Optional[str] = None


class ContactResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    email: str
    role: Optional[str] = None
    linkedin: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
