"""Strategy Agent — generates sponsorship strategy from campaign context."""

import json
import os
from app.agents.state import AgentState


def strategy_agent(state: AgentState) -> dict:
    """Given company profile and campaign goals, output a structured sponsorship strategy."""
    brand_context = state.get("brand_context", {})

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.7,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        system_prompt = """You are an expert sponsorship strategist for college events and organizations.
Given a brand's context, generate a comprehensive sponsorship strategy.

Return your response as a JSON object with these fields:
{
    "sponsor_categories": ["list of industries to target"],
    "tiers": {
        "platinum": {"min_amount": 50000, "benefits": ["list"]},
        "gold": {"min_amount": 25000, "benefits": ["list"]},
        "silver": {"min_amount": 10000, "benefits": ["list"]}
    },
    "target_industries": ["ranked list of industries most likely to sponsor"],
    "search_queries": ["list of search queries to find sponsors"],
    "value_propositions": ["list of unique value props for sponsors"],
    "roi_projections": {"estimated_reach": 0, "estimated_engagement": 0}
}"""

        user_prompt = f"""Generate a sponsorship strategy for:
Brand/Event: {brand_context.get('name', 'Unknown')}
Type: {brand_context.get('type', 'general')}
Target Audience: {brand_context.get('target_audience', 'college students')}
Budget Goal: ${brand_context.get('budget', 0)}
Partnership Type: {brand_context.get('partnership_type', 'sponsorship')}
Offerings: {json.dumps(brand_context.get('offerings', {}))}
Target Sponsor Profile: {json.dumps(brand_context.get('target_sponsor_profile', {}))}"""

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

        # Parse JSON from response
        content = response.content
        # Try to extract JSON from the response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        strategy = json.loads(content)

    except Exception as e:
        # Fallback strategy if LLM call fails
        strategy = {
            "sponsor_categories": ["technology", "finance", "consumer goods", "education"],
            "tiers": {
                "platinum": {"min_amount": 50000, "benefits": ["Main stage naming rights", "Logo on all materials"]},
                "gold": {"min_amount": 25000, "benefits": ["Booth space", "Logo on website"]},
                "silver": {"min_amount": 10000, "benefits": ["Logo mention", "Social media shoutout"]},
            },
            "target_industries": ["technology", "finance", "food & beverage"],
            "search_queries": [
                f"{brand_context.get('type', 'college')} event sponsors",
                "companies sponsoring college events",
                "brand partnerships college students",
            ],
            "value_propositions": [
                "Direct access to Gen-Z consumers",
                "High engagement at live events",
                "Brand visibility across campus",
            ],
            "roi_projections": {"estimated_reach": 5000, "estimated_engagement": 2000},
            "_fallback": True,
            "_error": str(e),
        }

    return {"strategy_output": strategy}
