"""Embedding service — OpenAI text-embedding-3-small → pgvector storage."""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import create_engine


async def embed_and_store(
    entity_type: str,
    entity_id: str,
    content: str,
    metadata: Dict[str, Any],
    db_session=None,
):
    """Generate embedding via OpenAI and store in pgvector."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=content,
    )

    vector = response.data[0].embedding

    if db_session:
        from app.models.embedding import Embedding

        embedding = Embedding(
            id=uuid.uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            content=content,
            vector=vector,
            metadata_=metadata,
        )
        db_session.add(embedding)
        await db_session.flush()
        return embedding
    return vector


def embed_and_store_sync(
    session: Session,
    entity_type: str,
    entity_id: str,
    content: str,
    metadata: Dict[str, Any],
):
    """Synchronous version for Celery tasks."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=content,
    )

    vector = response.data[0].embedding

    from app.models.embedding import Embedding

    embedding = Embedding(
        id=uuid.uuid4(),
        entity_type=entity_type,
        entity_id=entity_id,
        content=content,
        vector=vector,
    )
    # Set metadata directly on the column
    embedding.metadata_ = metadata

    session.add(embedding)
    session.commit()
    return embedding


async def similarity_search(
    query_text: str,
    entity_type: Optional[str] = None,
    limit: int = 5,
    db_session=None,
):
    """Search for similar embeddings using pgvector."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=query_text,
    )
    query_vector = response.data[0].embedding

    if db_session:
        from sqlalchemy import text

        sql = """
            SELECT id, entity_type, entity_id, content, metadata_,
                   1 - (vector <=> :query_vector::vector) as similarity
            FROM embeddings
        """
        params = {"query_vector": str(query_vector)}

        if entity_type:
            sql += " WHERE entity_type = :entity_type"
            params["entity_type"] = entity_type

        sql += " ORDER BY vector <=> :query_vector::vector LIMIT :limit"
        params["limit"] = limit

        result = await db_session.execute(text(sql), params)
        return [
            {
                "id": str(row[0]),
                "entity_type": row[1],
                "entity_id": str(row[2]),
                "content": row[3],
                "metadata": row[4],
                "similarity": float(row[5]),
            }
            for row in result
        ]

    return []
