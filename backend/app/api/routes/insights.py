"""Insights routes — learning system data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(prefix="/insights", tags=["insights"])


# Insight model will be added in Phase 10
# For now, stub endpoints that return empty data

@router.get("")
async def list_insights(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return []


@router.get("/{insight_id}/report")
async def get_insight_report(
    insight_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    raise HTTPException(status_code=404, detail="Insight not found")


@router.post("/collect-data", status_code=202)
async def collect_insight_data(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Will trigger Celery task in Phase 10
    return {"status": "queued"}
