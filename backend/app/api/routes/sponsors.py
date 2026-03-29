"""Sponsor discovery routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.company import Company
from app.schemas.company import CompanyResponse, CompanyDetailResponse

router = APIRouter(prefix="/sponsors", tags=["sponsors"])


@router.get("", response_model=List[CompanyResponse])
async def list_sponsors(
    industry: str = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    query = select(Company)
    if industry:
        query = query.where(Company.industry == industry)
    query = query.order_by(Company.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{sponsor_id}", response_model=CompanyDetailResponse)
async def get_sponsor(
    sponsor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Company).where(Company.id == sponsor_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    return company
