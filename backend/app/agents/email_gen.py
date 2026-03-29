"""Email Generation Agent — generates hyper-personalized sponsorship pitch emails."""

import json
import os
from app.agents.state import AgentState


def email_generation_agent(state: AgentState) -> dict:
    """Generate a personalized sponsorship pitch email for the current sponsor."""
    brand_context = state.get("brand_context", {})
    strategy = state.get("strategy_output", {})
    current_sponsor = state.get("current_sponsor", {})
    memories = state.get("retrieved_memories", [])
    eval_feedback = state.get("eval_feedback", "")
    retry_count = state.get("retry_count", 0)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.8,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        # Build system prompt
        system_prompt = """You are a professional sponsorship outreach specialist who writes compelling, 
personalized pitch emails for college events and organizations.

Your emails should be:
- Highly personalized to the specific sponsor
- Concise but compelling (300-500 words)
- Include specific value propositions and ROI framing
- Have a clear, actionable CTA
- Use a professional but warm tone

Return your response as a JSON object:
{
    "subject": "Compelling email subject line",
    "body": "Full email body in HTML format",
    "cta": "Primary call-to-action text",
    "follow_up_dates": ["date1", "date2"]
}"""

        # Build few-shot examples from retrieved memories
        few_shot = ""
        email_memories = [m for m in memories if m.get("type") == "past_email"]
        if email_memories:
            few_shot = "\n\nHere are examples of successful past emails for reference:\n"
            for m in email_memories[:3]:
                few_shot += f"\n---\n{m.get('content', '')}\n---\n"

        # Build user prompt
        user_prompt = f"""Generate a sponsorship pitch email for:

OUR EVENT/BRAND:
- Name: {brand_context.get('name', 'Unknown')}
- Type: {brand_context.get('type', 'event')}
- Target Audience: {brand_context.get('target_audience', 'college students')}
- Budget: ${brand_context.get('budget', 0)}
- Partnership Type: {brand_context.get('partnership_type', 'sponsorship')}
- Offerings: {json.dumps(brand_context.get('offerings', {}))}

SPONSOR TARGET:
- Company: {current_sponsor.get('name', 'Unknown Company')}
- Industry: {current_sponsor.get('industry', 'Unknown')}
- Website: {current_sponsor.get('website', '')}
- Relevance Score: {current_sponsor.get('relevance_score', 'N/A')}

STRATEGY CONTEXT:
- Tiers: {json.dumps(strategy.get('tiers', {}))}
- Value Props: {json.dumps(strategy.get('value_propositions', []))}
- ROI: {json.dumps(strategy.get('roi_projections', {}))}
{few_shot}"""

        # On retry, append evaluator feedback
        if retry_count > 0 and eval_feedback:
            user_prompt += f"\n\n⚠️ IMPROVEMENT REQUIRED (Attempt {retry_count + 1}/3):\n{eval_feedback}\n\nPlease address the feedback above and generate an improved version."

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        email_draft = json.loads(content)

    except Exception as e:
        email_draft = {
            "subject": f"Partnership Opportunity with {brand_context.get('name', 'Our Event')}",
            "body": f"""<p>Dear {current_sponsor.get('name', 'Partner')},</p>
<p>I'm reaching out to explore a sponsorship partnership for {brand_context.get('name', 'our upcoming event')}.</p>
<p>We believe there's a strong alignment between your brand and our audience of {brand_context.get('target_audience', 'college students')}.</p>
<p>I'd love to schedule a quick call to discuss how we can create mutual value.</p>
<p>Best regards</p>""",
            "cta": "Schedule a 15-minute call",
            "follow_up_dates": [],
            "_fallback": True,
            "_error": str(e),
        }

    return {"email_draft": email_draft}
