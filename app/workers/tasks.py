import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import get_settings
from app.models.database import Document, DocumentChunk, DocumentStatus
from app.core.parsing import parse_document
from app.core.chunking import chunk_text
from app.core.embeddings import generate_embeddings
from app.core.llm import generate_response
from app.core.prompts import (
    build_summary_prompt,
    build_classification_prompt,
    SYSTEM_PROMPT_SUMMARY,
    SYSTEM_PROMPT_CLASSIFICATION,
)

settings = get_settings()

# Sync engine for Celery (Celery doesn't play well with async)
sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2")
sync_engine = create_engine(sync_database_url)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(bind=True, name="process_document")
def process_document(self, document_id: str, file_path: str):
    """
    Main task to process a document through the pipeline:
    1. Parse document
    2. Chunk text
    3. Generate embeddings
    4. Generate summary
    5. Classify document
    """
    doc_uuid = uuid.UUID(document_id)

    with SyncSession() as db:
        try:
            # Get document
            document = db.query(Document).filter(Document.id == doc_uuid).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")

            # Update status to processing
            document.status = DocumentStatus.PROCESSING
            db.commit()

            # Step 1: Parse document
            self.update_state(state="PROGRESS", meta={"step": "parsing"})
            text = parse_document(file_path)

            if not text.strip():
                raise ValueError("Document is empty or could not be parsed")

            # Step 2: Chunk text
            self.update_state(state="PROGRESS", meta={"step": "chunking"})
            chunks = chunk_text(text)

            # Step 3: Generate embeddings
            self.update_state(state="PROGRESS", meta={"step": "embedding"})
            chunk_texts = [c["content"] for c in chunks]
            embeddings = generate_embeddings(chunk_texts)

            # Store chunks with embeddings
            for chunk_data, embedding in zip(chunks, embeddings):
                chunk = DocumentChunk(
                    document_id=doc_uuid,
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    embedding=embedding,
                    chunk_metadata={"char_count": chunk_data["char_count"]},
                )
                db.add(chunk)

            db.commit()

            # Step 4: Generate summary
            self.update_state(state="PROGRESS", meta={"step": "summarizing"})
            # Use first ~10000 chars for summary to stay within context limits
            summary_text = text[:10000]
            summary_prompt = build_summary_prompt(summary_text)
            summary = generate_response(summary_prompt, SYSTEM_PROMPT_SUMMARY)
            document.summary = summary

            # Step 5: Classify document
            self.update_state(state="PROGRESS", meta={"step": "classifying"})
            classification_prompt = build_classification_prompt(text, summary)
            classification = generate_response(
                classification_prompt, SYSTEM_PROMPT_CLASSIFICATION
            )
            document.classification = classification.strip()

            # Mark as completed
            document.status = DocumentStatus.COMPLETED
            db.commit()

            return {
                "document_id": document_id,
                "status": "completed",
                "chunks_created": len(chunks),
                "summary_length": len(summary),
                "classification": document.classification,
            }

        except Exception as e:
            # Mark as failed
            document = db.query(Document).filter(Document.id == doc_uuid).first()
            if document:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                db.commit()
            raise
