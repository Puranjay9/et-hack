"""Supervisor — entry node that builds initial state from campaign data."""

from app.agents.state import AgentState


def supervisor_node(state: AgentState) -> dict:
    """Entry node: validates and enriches initial state before passing to strategy agent."""
    brand_context = state.get("brand_context", {})

    # Ensure all required fields exist with defaults
    enriched_context = {
        "name": brand_context.get("name", "Campaign"),
        "type": brand_context.get("type", "general"),
        "target_audience": brand_context.get("target_audience", "college students"),
        "budget": brand_context.get("budget", 0),
        "partnership_type": brand_context.get("partnership_type", "sponsorship"),
        "offerings": brand_context.get("offerings", {}),
        "target_sponsor_profile": brand_context.get("target_sponsor_profile", {}),
    }

    return {
        "brand_context": enriched_context,
        "sponsors_found": [],
        "retrieved_memories": [],
        "final_emails": [],
        "retry_count": 0,
        "eval_score": 0.0,
        "eval_feedback": "",
    }
