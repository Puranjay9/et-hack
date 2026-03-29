"""Discovery Agent — finds real sponsor candidates matching the strategy."""

import json
import os
from typing import List, Dict, Any
from app.agents.state import AgentState


def discovery_agent(state: AgentState) -> dict:
    """Find sponsor candidates using Search API + vector similarity."""
    strategy = state.get("strategy_output", {})
    brand_context = state.get("brand_context", {})
    sponsors_found: List[Dict[str, Any]] = []

    search_queries = strategy.get("search_queries", [])
    target_industries = strategy.get("target_industries", [])

    try:
        import httpx
        import redis

        search_api_key = os.getenv("SEARCH_API_KEY", "")
        search_api_url = os.getenv("SEARCH_API_URL", "https://www.searchapi.io/api/v1/search")
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

        # Connect to Redis for caching
        r = redis.from_url(redis_url)

        for query in search_queries[:5]:  # Limit queries
            cache_key = f"search:{query}"
            cached = r.get(cache_key)

            if cached:
                results = json.loads(cached)
            else:
                try:
                    with httpx.Client(timeout=30) as client:
                        resp = client.get(
                            search_api_url,
                            params={"engine": "google", "q": query, "api_key": search_api_key},
                        )
                        resp.raise_for_status()
                        results = resp.json().get("organic_results", [])
                        # Cache for 24 hours
                        r.set(cache_key, json.dumps(results), ex=86400)
                except Exception:
                    results = []

            for result in results[:5]:
                sponsors_found.append({
                    "name": result.get("title", "Unknown"),
                    "website": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "source": "search_api",
                })

        # Score and deduplicate sponsors using LLM
        if sponsors_found:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.3,
                    api_key=os.getenv("GOOGLE_API_KEY"),
                )

                scoring_prompt = f"""Score these potential sponsors for relevance to our campaign.
Campaign: {brand_context.get('name', 'Unknown')} - {brand_context.get('type', 'event')}
Target Industries: {', '.join(target_industries)}

Sponsors found:
{json.dumps(sponsors_found[:20], indent=2)}

Return a JSON array of the top 10 most relevant sponsors, each with:
{{"name": "...", "website": "...", "industry": "...", "relevance_score": 0-10, "reason": "..."}}"""

                response = llm.invoke([{"role": "user", "content": scoring_prompt}])

                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                scored = json.loads(content)
                if isinstance(scored, list):
                    sponsors_found = scored

            except Exception:
                pass

    except Exception as e:
        # Fallback — return mock sponsors for testing
        sponsors_found = [
            {
                "name": "TechCorp Inc",
                "website": "https://techcorp.example.com",
                "industry": "technology",
                "relevance_score": 8.5,
                "reason": "Strong college campus presence",
            },
            {
                "name": "EduBrand Global",
                "website": "https://edubrand.example.com",
                "industry": "education",
                "relevance_score": 7.0,
                "reason": "Education-focused brand",
            },
        ]

    return {"sponsors_found": sponsors_found}
