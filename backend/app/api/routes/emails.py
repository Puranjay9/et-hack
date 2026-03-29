"""Email routes — send, preview, test, and tracking."""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.outreach import Outreach, OutreachStatus
from app.models.campaign import Campaign
from app.schemas.outreach import (
    OutreachResponse,
    OutreachUpdate,
    SendEmailRequest,
    TestEmailRequest,
)

router = APIRouter(tags=["emails"])


@router.get("/campaigns/{campaign_id}/emails", response_model=List[OutreachResponse])
async def list_campaign_emails(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = await db.execute(
        select(Outreach)
        .where(Outreach.campaign_id == campaign_id)
        .order_by(Outreach.created_at.desc())
    )
    return result.scalars().all()


@router.post("/campaigns/{campaign_id}/emails/send", status_code=status.HTTP_202_ACCEPTED)
async def send_campaign_emails(
    campaign_id: UUID,
    payload: SendEmailRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    from app.tasks.email_tasks import send_outreach_email

    # Get outreach messages to send
    query = select(Outreach).where(
        Outreach.campaign_id == campaign_id,
        Outreach.status == OutreachStatus.scheduled,
    )
    if payload.outreach_ids:
        query = query.where(Outreach.id.in_(payload.outreach_ids))

    result = await db.execute(query)
    outreach_messages = result.scalars().all()

    task_ids = []
    for outreach in outreach_messages:
        task = send_outreach_email.delay(str(outreach.id))
        task_ids.append(task.id)

    return {"queued": len(task_ids), "task_ids": task_ids}


@router.get("/emails/{email_id}", response_model=OutreachResponse)
async def get_email(
    email_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Outreach).where(Outreach.id == email_id))
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Email not found")
    return outreach


@router.put("/emails/{email_id}", response_model=OutreachResponse)
async def update_email(
    email_id: UUID,
    payload: OutreachUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Outreach).where(Outreach.id == email_id))
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Email not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(outreach, key, value)

    await db.flush()
    await db.refresh(outreach)
    return outreach


@router.post("/emails/{email_id}/test", status_code=status.HTTP_202_ACCEPTED)
async def send_test_email(
    email_id: UUID,
    payload: TestEmailRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Outreach).where(Outreach.id == email_id))
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Email not found")

    from app.tasks.email_tasks import send_test_email as send_test_task

    task = send_test_task.delay(str(email_id), payload.to_email)
    return {"task_id": task.id, "status": "queued"}
