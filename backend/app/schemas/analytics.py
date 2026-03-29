"""Pydantic schemas for Analytics and Insights."""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


# ---- Analytics ----

class CampaignAnalytics(BaseModel):
    campaign_id: UUID
    campaign_goal: Optional[str] = None
    total_outreach: int = 0
    sent: int = 0
    opened: int = 0
    replied: int = 0
    failed: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0
    avg_eval_score: float = 0.0


class GlobalAnalytics(BaseModel):
    total_campaigns: int = 0
    total_outreach: int = 0
    total_sent: int = 0
    total_opened: int = 0
    total_replied: int = 0
    overall_open_rate: float = 0.0
    overall_reply_rate: float = 0.0


class SponsorAnalytics(BaseModel):
    total_sponsors: int = 0
    by_industry: Dict[str, int] = {}
    top_responding: List[Dict[str, Any]] = []


class EventStats(BaseModel):
    total_opens: int = 0
    total_clicks: int = 0
    unique_opens: int = 0
    unique_clicks: int = 0


# ---- Insights ----

class InsightResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    summary: str
    category: str
    data: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True
