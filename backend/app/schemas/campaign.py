"""Pydantic schemas for Campaign."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class CampaignCreate(BaseModel):
    company_id: Optional[UUID] = None
    type: Optional[str] = None
    goal: Optional[str] = None
    target_audience: Optional[str] = None
    budget: Optional[float] = None
    partnership_type: Optional[str] = None
    target_sponsor_profile: Optional[Dict[str, Any]] = None
    offerings: Optional[Dict[str, Any]] = None


class CampaignUpdate(BaseModel):
    company_id: Optional[UUID] = None
    status: Optional[str] = None
    type: Optional[str] = None
    goal: Optional[str] = None
    target_audience: Optional[str] = None
    budget: Optional[float] = None
    partnership_type: Optional[str] = None
    target_sponsor_profile: Optional[Dict[str, Any]] = None
    offerings: Optional[Dict[str, Any]] = None


class CampaignResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_id: Optional[UUID] = None
    status: str
    type: Optional[str] = None
    goal: Optional[str] = None
    target_audience: Optional[str] = None
    budget: Optional[float] = None
    partnership_type: Optional[str] = None
    target_sponsor_profile: Optional[Dict[str, Any]] = None
    offerings: Optional[Dict[str, Any]] = None
    strategy_output: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    outreach_count: int = 0
    sent_count: int = 0
    opened_count: int = 0
    replied_count: int = 0
