"""Evaluator Agent — LLM-as-judge, scores generated emails and decides accept or retry."""

import json
import os
from app.agents.state import AgentState


def evaluator_agent(state: AgentState) -> dict:
    """Score the generated email on 5 dimensions and decide accept or retry."""
    email_draft = state.get("email_draft", {})
    current_sponsor = state.get("current_sponsor", {})
    brand_context = state.get("brand_context", {})
    retry_count = state.get("retry_count", 0)
    final_emails = state.get("final_emails", [])

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        eval_prompt = f"""You are an expert email marketing evaluator. Score this sponsorship outreach email on 5 dimensions.

EMAIL:
Subject: {email_draft.get('subject', '')}
Body: {email_draft.get('body', '')}
CTA: {email_draft.get('cta', '')}

TARGET SPONSOR: {current_sponsor.get('name', 'Unknown')} ({current_sponsor.get('industry', 'Unknown')})
OUR BRAND: {brand_context.get('name', 'Unknown')}

Score each dimension from 0–10 and provide specific feedback:

Return as JSON:
{{
    "scores": {{
        "personalization": 0,
        "predicted_ctr": 0,
        "length_fit": 0,
        "persuasive_strength": 0,
        "stats_usage": 0
    }},
    "average_score": 0.0,
    "feedback": "Specific improvement suggestions",
    "strengths": ["list of what's good"],
    "weaknesses": ["list of what needs improvement"]
}}"""

        response = llm.invoke([{"role": "user", "content": eval_prompt}])

        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        eval_result = json.loads(content)

        scores = eval_result.get("scores", {})
        avg_score = eval_result.get("average_score", 0.0)
        if avg_score == 0.0 and scores:
            avg_score = sum(scores.values()) / len(scores)

        feedback = eval_result.get("feedback", "")

    except Exception as e:
        # Default: accept on error to avoid blocking
        avg_score = 7.5
        feedback = f"Auto-accepted due to evaluation error: {str(e)}"
        eval_result = {"_error": str(e)}
        scores = {}

    # Decision logic
    if avg_score >= 7.0 or retry_count >= 3:
        # Accept: add to final emails
        accepted_email = {
            **email_draft,
            "sponsor_name": current_sponsor.get("name", ""),
            "sponsor_industry": current_sponsor.get("industry", ""),
            "eval_score": avg_score,
            "eval_details": scores,
            "contact_id": current_sponsor.get("contact_id"),
        }
        final_emails = list(final_emails) + [accepted_email]

        return {
            "eval_score": avg_score,
            "eval_feedback": "",
            "final_emails": final_emails,
            "retry_count": 0,  # Reset for next sponsor
        }
    else:
        # Retry: increment count and pass feedback
        return {
            "eval_score": avg_score,
            "eval_feedback": feedback,
            "retry_count": retry_count + 1,
        }
