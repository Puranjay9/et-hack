"""Campaign CRUD routes + outreach generation trigger."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.campaign import Campaign, CampaignStatus
from app.models.outreach import Outreach, OutreachStatus
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignDetailResponse,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    query = select(Campaign).where(Campaign.user_id == user_id)
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    query = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaign = Campaign(user_id=user_id, **payload.model_dump(exclude_unset=True))
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Count outreach metrics
    outreach_query = select(
        func.count(Outreach.id).label("total"),
        func.count(Outreach.id).filter(Outreach.status == OutreachStatus.sent).label("sent"),
        func.count(Outreach.id).filter(Outreach.status == OutreachStatus.opened).label("opened"),
        func.count(Outreach.id).filter(Outreach.status == OutreachStatus.replied).label("replied"),
    ).where(Outreach.campaign_id == campaign_id)
    metrics = await db.execute(outreach_query)
    row = metrics.one()

    return CampaignDetailResponse(
        **{c.key: getattr(campaign, c.key) for c in Campaign.__table__.columns},
        outreach_count=row.total,
        sent_count=row.sent,
        opened_count=row.opened,
        replied_count=row.replied,
    )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)

    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Soft delete — set status to completed
    campaign.status = CampaignStatus.completed
    await db.flush()


@router.post("/{campaign_id}/generate-outreach", status_code=status.HTTP_202_ACCEPTED)
async def generate_outreach(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Trigger Celery agent pipeline
    from app.tasks.agent_tasks import run_outreach_pipeline

    task = run_outreach_pipeline.delay(str(campaign_id))

    campaign.status = CampaignStatus.processing
    campaign.task_id = task.id
    await db.flush()

    return {"task_id": task.id, "status": "processing"}


@router.post("/{campaign_id}/email/regenerate", status_code=status.HTTP_202_ACCEPTED)
async def regenerate_emails(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    from app.tasks.agent_tasks import run_outreach_pipeline

    task = run_outreach_pipeline.delay(str(campaign_id), regenerate_only=True)

    campaign.status = CampaignStatus.processing
    campaign.task_id = task.id
    await db.flush()

    return {"task_id": task.id, "status": "processing"}
