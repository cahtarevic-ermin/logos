from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="process_document")
def process_document(self, document_id: str):
    """
    Main task to process a document through the pipeline:
    1. Parse document
    2. Chunk text
    3. Generate embeddings
    4. Generate summary
    5. Classify document
    """
    # Will be implemented in Phase 2
    pass
