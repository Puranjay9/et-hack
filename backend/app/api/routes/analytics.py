"""Analytics routes — campaign metrics, sponsor stats, event tracking."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.campaign import Campaign
from app.models.outreach import Outreach, OutreachStatus
from app.models.company import Company
from app.schemas.analytics import (
    CampaignAnalytics,
    GlobalAnalytics,
    SponsorAnalytics,
    EventStats,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/campaigns", response_model=List[CampaignAnalytics])
async def campaign_analytics(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    campaigns = await db.execute(
        select(Campaign).where(Campaign.user_id == user_id).order_by(Campaign.created_at.desc())
    )

    results = []
    for campaign in campaigns.scalars().all():
        metrics = await db.execute(
            select(
                func.count(Outreach.id).label("total"),
                func.count(Outreach.id).filter(Outreach.status == OutreachStatus.sent).label("sent"),
                func.count(Outreach.id).filter(Outreach.status == OutreachStatus.opened).label("opened"),
                func.count(Outreach.id).filter(Outreach.status == OutreachStatus.replied).label("replied"),
                func.count(Outreach.id).filter(Outreach.status == OutreachStatus.failed).label("failed"),
                func.avg(Outreach.eval_score).label("avg_score"),
            ).where(Outreach.campaign_id == campaign.id)
        )
        row = metrics.one()
        sent = row.sent or 0
        results.append(CampaignAnalytics(
            campaign_id=campaign.id,
            campaign_goal=campaign.goal,
            total_outreach=row.total or 0,
            sent=sent,
            opened=row.opened or 0,
            replied=row.replied or 0,
            failed=row.failed or 0,
            open_rate=(row.opened / sent * 100) if sent > 0 else 0,
            reply_rate=(row.replied / sent * 100) if sent > 0 else 0,
            avg_eval_score=float(row.avg_score) if row.avg_score else 0.0,
        ))

    return results


@router.get("/sponsors", response_model=SponsorAnalytics)
async def sponsor_analytics(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    total = await db.execute(select(func.count(Company.id)))
    total_count = total.scalar() or 0

    industry_q = await db.execute(
        select(Company.industry, func.count(Company.id))
        .group_by(Company.industry)
        .order_by(func.count(Company.id).desc())
    )
    by_industry = {row[0] or "Unknown": row[1] for row in industry_q.all()}

    return SponsorAnalytics(
        total_sponsors=total_count,
        by_industry=by_industry,
    )


@router.get("/events/stats", response_model=EventStats)
async def event_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    opens = await db.execute(
        select(func.count(Outreach.id)).where(Outreach.opened_at.isnot(None))
    )
    return EventStats(
        total_opens=opens.scalar() or 0,
    )


# ---- Tracking Endpoints (no auth required) ----

tracking_router = APIRouter(prefix="/track", tags=["tracking"])


@tracking_router.get("/open/{outreach_id}")
async def track_open(outreach_id: UUID, db: AsyncSession = Depends(get_db)):
    """Open tracking pixel — returns a 1x1 transparent GIF."""
    result = await db.execute(select(Outreach).where(Outreach.id == outreach_id))
    outreach = result.scalar_one_or_none()

    if outreach and outreach.status in (OutreachStatus.sent, OutreachStatus.scheduled):
        outreach.status = OutreachStatus.opened
        outreach.opened_at = datetime.now(timezone.utc)
        await db.flush()

    # 1x1 transparent GIF
    pixel = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    return Response(content=pixel, media_type="image/gif")


@tracking_router.get("/click/{outreach_id}")
async def track_click(
    outreach_id: UUID,
    url: str,
    db: AsyncSession = Depends(get_db),
):
    """Click tracking — logs event and redirects to original URL."""
    result = await db.execute(select(Outreach).where(Outreach.id == outreach_id))
    outreach = result.scalar_one_or_none()

    if outreach and outreach.status in (OutreachStatus.sent, OutreachStatus.opened):
        outreach.status = OutreachStatus.opened
        if not outreach.opened_at:
            outreach.opened_at = datetime.now(timezone.utc)
        await db.flush()

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url)
