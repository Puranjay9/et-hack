"""AgentState TypedDict — shared typed state across all LangGraph nodes."""

from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    campaign_id: str
    brand_context: Dict[str, Any]       # name, positioning, audience, KPIs, offerings
    strategy_output: Dict[str, Any]     # categories, tiers, ROI projections
    sponsors_found: List[Dict[str, Any]]
    retrieved_memories: List[Dict[str, Any]]
    current_sponsor: Dict[str, Any]
    email_draft: Dict[str, Any]         # {subject, body, cta}
    eval_score: float
    eval_feedback: str
    retry_count: int                    # max 3
    final_emails: List[Dict[str, Any]]
