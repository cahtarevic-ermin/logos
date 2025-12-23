import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.database import Document, DocumentStatus
from app.models.schemas import ChatRequest
from app.core.retrieval import search_similar_chunks
from app.core.prompts import build_chat_prompt, SYSTEM_PROMPT_CHAT
from app.core.llm import generate_response_stream

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat_with_document(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with a document using RAG.
    Returns a streaming response (SSE).
    """
    # Verify document exists and is processed
    stmt = select(Document).where(Document.id == request.document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready. Status: {document.status.value}",
        )

    # Retrieve relevant chunks
    chunks = await search_similar_chunks(
        db=db,
        document_id=request.document_id,
        query=request.message,
        top_k=5,
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content found in document",
        )

    # Build prompt with context
    context_texts = [chunk.content for chunk in chunks]
    conversation_history = [msg.model_dump() for msg in request.conversation_history]
    prompt = build_chat_prompt(request.message, context_texts, conversation_history)

    # Stream response
    async def generate():
        chunk_ids = [str(chunk.id) for chunk in chunks]

        async for token in generate_response_stream(prompt, SYSTEM_PROMPT_CHAT):
            yield f"event: token\ndata: {json.dumps({'content': token})}\n\n"

        # Send completion event with source chunk IDs
        yield f"event: done\ndata: {json.dumps({'chunk_ids': chunk_ids})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
