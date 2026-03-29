"""Email delivery Celery tasks."""

from app.tasks.celery_app import celery_app
from datetime import datetime, timezone


@celery_app.task(name="app.tasks.email_tasks.send_outreach_email", queue="email", bind=True, max_retries=2)
def send_outreach_email(self, outreach_id: str):
    """Send a single outreach email via SMTP/SendGrid."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    import os

    sync_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@postgres:5432/sponsor_platform")
    engine = create_engine(sync_url)

    try:
        with Session(engine) as session:
            from app.models.outreach import Outreach, OutreachStatus
            from app.models.contact import Contact

            outreach = session.query(Outreach).filter(Outreach.id == outreach_id).first()
            if not outreach:
                return {"error": "Outreach not found"}

            contact = session.query(Contact).filter(Contact.id == outreach.contact_id).first()
            if not contact:
                return {"error": "Contact not found"}

            # Inject tracking pixel and click wrappers
            tracking_base = os.getenv("TRACKING_BASE_URL", "http://localhost:8000")
            tracking_pixel = f'<img src="{tracking_base}/track/open/{outreach_id}" width="1" height="1" />'

            html_body = outreach.body or ""
            html_body += f"\n\n{tracking_pixel}"

            # Send via email provider (Phase 07 full implementation)
            from app.services.email_provider import email_provider
            if contact.email:
                success = email_provider.send_email(
                    to_email=contact.email,
                    subject=outreach.subject,
                    html_body=html_body,
                )

            # For now, mark as sent (simulate)
            outreach.status = OutreachStatus.sent
            outreach.sent_at = datetime.now(timezone.utc)
            session.commit()

            # Trigger embedding of the sent email
            from app.tasks.agent_tasks import embed_new_entity
            embed_new_entity.delay("email", str(outreach_id))

            return {"outreach_id": outreach_id, "status": "sent"}

    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@celery_app.task(name="app.tasks.email_tasks.send_test_email", queue="email")
def send_test_email(outreach_id: str, to_email: str):
    """Send a test/preview email to a specific address."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    import os

    sync_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@postgres:5432/sponsor_platform")
    engine = create_engine(sync_url)

    with Session(engine) as session:
        from app.models.outreach import Outreach

        outreach = session.query(Outreach).filter(Outreach.id == outreach_id).first()
        if not outreach:
            return {"error": "Outreach not found"}

        # Send test email (Phase 07 full implementation)
        from app.services.email_provider import email_provider
        email_provider.send_email(to_email=to_email, subject=f"[TEST] {outreach.subject}", html_body=outreach.body)

        return {"outreach_id": outreach_id, "to": to_email, "status": "test_sent"}


@celery_app.task(name="app.tasks.email_tasks.send_followup_batch", queue="email")
def send_followup_batch():
    """Send follow-up emails for active campaigns. Runs hourly via Celery Beat."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    import os

    sync_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@postgres:5432/sponsor_platform")
    engine = create_engine(sync_url)

    with Session(engine) as session:
        from app.models.outreach import Outreach, OutreachStatus
        from app.models.campaign import Campaign, CampaignStatus

        # Find active campaigns with sent but not replied outreach
        active_campaigns = session.query(Campaign).filter(
            Campaign.status == CampaignStatus.active
        ).all()

        followups_queued = 0
        for campaign in active_campaigns:
            # Skip contacts who already replied
            pending_outreach = session.query(Outreach).filter(
                Outreach.campaign_id == campaign.id,
                Outreach.status.in_([OutreachStatus.sent, OutreachStatus.opened]),
            ).all()

            for outreach in pending_outreach:
                # Check if follow-up is due (Phase 07 full implementation)
                pass

        return {"followups_queued": followups_queued}
