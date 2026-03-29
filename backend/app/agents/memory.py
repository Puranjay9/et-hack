"""Memory Retrieval Node — RAG from pgvector for past campaign context."""

import os
import json
from typing import List, Dict, Any
from app.agents.state import AgentState


def memory_retrieval(state: AgentState) -> dict:
    """Pull relevant past email patterns and sponsor data via pgvector similarity search."""
    brand_context = state.get("brand_context", {})
    current_sponsor = state.get("current_sponsor", {})
    retrieved_memories: List[Dict[str, Any]] = []

    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import Session

        sync_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@postgres:5432/sponsor_platform")
        engine = create_engine(sync_url)

        # Generate query embedding
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        query_text = f"{brand_context.get('name', '')} {brand_context.get('type', '')} {brand_context.get('target_audience', '')}"
        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text,
        )
        query_vector = query_embedding.data[0].embedding

        with Session(engine) as session:
            # 1. Past successful emails for similar event type
            email_results = session.execute(
                text("""
                    SELECT content, metadata_, 1 - (vector <=> :query_vector::vector) as similarity
                    FROM embeddings
                    WHERE entity_type = 'email'
                    ORDER BY vector <=> :query_vector::vector
                    LIMIT 5
                """),
                {"query_vector": str(query_vector)},
            )
            for row in email_results:
                retrieved_memories.append({
                    "type": "past_email",
                    "content": row[0],
                    "metadata": row[1] or {},
                    "similarity": float(row[2]) if row[2] else 0,
                })

            # 2. High-performing sponsor engagement patterns
            insight_results = session.execute(
                text("""
                    SELECT content, metadata_, 1 - (vector <=> :query_vector::vector) as similarity
                    FROM embeddings
                    WHERE entity_type = 'insight'
                    ORDER BY vector <=> :query_vector::vector
                    LIMIT 5
                """),
                {"query_vector": str(query_vector)},
            )
            for row in insight_results:
                retrieved_memories.append({
                    "type": "insight",
                    "content": row[0],
                    "metadata": row[1] or {},
                    "similarity": float(row[2]) if row[2] else 0,
                })

            # 3. Similar past sponsor profiles
            if current_sponsor:
                sponsor_text = f"{current_sponsor.get('name', '')} {current_sponsor.get('industry', '')}"
                sponsor_embedding = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=sponsor_text,
                )
                sponsor_vector = sponsor_embedding.data[0].embedding

                sponsor_results = session.execute(
                    text("""
                        SELECT content, metadata_, 1 - (vector <=> :query_vector::vector) as similarity
                        FROM embeddings
                        WHERE entity_type = 'sponsor'
                        ORDER BY vector <=> :query_vector::vector
                        LIMIT 5
                    """),
                    {"query_vector": str(sponsor_vector)},
                )
                for row in sponsor_results:
                    retrieved_memories.append({
                        "type": "similar_sponsor",
                        "content": row[0],
                        "metadata": row[1] or {},
                        "similarity": float(row[2]) if row[2] else 0,
                    })

    except Exception as e:
        # Fallback: proceed with zero-shot (no memory context)
        retrieved_memories = []

    # Fallback check: if fewer than 2 results, proceed with zero-shot
    if len(retrieved_memories) < 2:
        retrieved_memories = []

    return {"retrieved_memories": retrieved_memories}
