import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import DocumentChunk
from app.core.embeddings import generate_query_embedding


async def search_similar_chunks(
    db: AsyncSession,
    document_id: uuid.UUID,
    query: str,
    top_k: int = 5,
) -> list[DocumentChunk]:
    """
    Search for similar chunks in a document using vector similarity.
    """
    # Generate embedding for the query
    query_embedding = generate_query_embedding(query)

    # Use cosine distance for similarity search
    # pgvector uses <=> for cosine distance (lower is more similar)
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .where(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def search_similar_chunks_multi_doc(
    db: AsyncSession,
    document_ids: list[uuid.UUID],
    query: str,
    top_k: int = 5,
) -> list[DocumentChunk]:
    """
    Search for similar chunks across multiple documents.
    """
    query_embedding = generate_query_embedding(query)

    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id.in_(document_ids))
        .where(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())
