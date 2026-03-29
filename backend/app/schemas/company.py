"""Pydantic schemas for Company."""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ContactInCompany(BaseModel):
    id: UUID
    name: str
    email: str
    role: Optional[str] = None
    linkedin: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Request schemas ----

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None


# ---- Response schemas ----

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyDetailResponse(CompanyResponse):
    contacts: List[ContactInCompany] = []
