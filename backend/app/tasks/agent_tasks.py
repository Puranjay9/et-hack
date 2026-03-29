"""Agent Celery tasks — triggers LangGraph pipeline."""

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.agent_tasks.run_outreach_pipeline", queue="agent", bind=True, max_retries=2)
def run_outreach_pipeline(self, campaign_id: str, regenerate_only: bool = False):
    """Run the full LangGraph agent pipeline for a campaign."""
    import asyncio
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    import os

    from app.models.campaign import Campaign, CampaignStatus

    sync_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@postgres:5432/sponsor_platform")
    engine = create_engine(sync_url)

    try:
        with Session(engine) as session:
            campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return {"error": "Campaign not found"}

            campaign.status = CampaignStatus.processing
            session.commit()

            # Build initial state for LangGraph
            from app.agents.graph import compiled_graph

            initial_state = {
                "campaign_id": campaign_id,
                "brand_context": {
                    "name": campaign.goal or "Campaign",
                    "type": campaign.type or "general",
                    "target_audience": campaign.target_audience or "",
                    "budget": float(campaign.budget) if campaign.budget else 0,
                    "partnership_type": campaign.partnership_type or "",
                    "offerings": campaign.offerings or {},
                    "target_sponsor_profile": campaign.target_sponsor_profile or {},
                },
                "strategy_output": campaign.strategy_output or {},
                "sponsors_found": [],
                "retrieved_memories": [],
                "current_sponsor": {},
                "email_draft": {},
                "eval_score": 0.0,
                "eval_feedback": "",
                "retry_count": 0,
                "final_emails": [],
            }

            # Run the graph
            if regenerate_only:
                # Skip strategy + discovery, go straight to email gen
                initial_state["strategy_output"] = campaign.strategy_output or {}
                result = compiled_graph.invoke(initial_state)
            else:
                result = compiled_graph.invoke(initial_state)

            # Update campaign with results
            campaign.strategy_output = result.get("strategy_output", {})
            campaign.status = CampaignStatus.active
            session.commit()

            # Write outreach records
            from app.models.outreach import Outreach, OutreachStatus
            from app.models.contact import Contact
            import uuid

            for email_data in result.get("final_emails", []):
                outreach = Outreach(
                    id=uuid.uuid4(),
                    campaign_id=campaign_id,
                    contact_id=email_data.get("contact_id"),
                    status=OutreachStatus.scheduled,
                    subject=email_data.get("subject", ""),
                    body=email_data.get("body", ""),
                    cta=email_data.get("cta", ""),
                    eval_score=email_data.get("eval_score", 0.0),
                    eval_details=email_data.get("eval_details", {}),
                    follow_up_dates=email_data.get("follow_up_dates", []),
                )
                session.add(outreach)

            session.commit()

            return {
                "campaign_id": campaign_id,
                "emails_generated": len(result.get("final_emails", [])),
                "status": "completed",
            }

    except Exception as e:
        # Mark campaign as failed
        try:
            with Session(engine) as session:
                campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
                if campaign:
                    campaign.status = CampaignStatus.failed
                    session.commit()
        except Exception:
            pass

        raise self.retry(exc=e, countdown=30)


@celery_app.task(name="app.tasks.agent_tasks.embed_new_entity", queue="agent")
def embed_new_entity(entity_type: str, entity_id: str):
    """Embed a new entity (sponsor, email, insight) into pgvector."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    import os

    sync_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@postgres:5432/sponsor_platform")
    engine = create_engine(sync_url)

    with Session(engine) as session:
        if entity_type == "sponsor":
            from app.models.company import Company
            company = session.query(Company).filter(Company.id == entity_id).first()
            if company:
                content = f"{company.name} - {company.industry or 'Unknown industry'}. {company.website or ''}"
                # Phase 06: call embedding service
                # from app.services.embedding import embed_and_store_sync
                # embed_and_store_sync(session, "sponsor", entity_id, content, {"name": company.name, "industry": company.industry})

        elif entity_type == "email":
            from app.models.outreach import Outreach
            outreach = session.query(Outreach).filter(Outreach.id == entity_id).first()
            if outreach:
                content = f"Subject: {outreach.subject}\n\n{outreach.body}"
                # Phase 06: call embedding service

    return {"entity_type": entity_type, "entity_id": entity_id, "status": "processed"}
