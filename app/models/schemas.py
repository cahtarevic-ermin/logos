import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from app.models.database import DocumentStatus

# Request schemas
class DocumentCreate(BaseModel):
    filename: str


class ChatRequest(BaseModel):
    document_id: uuid.UUID
    message: str
    conversation_history: list["ChatMessage"] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


# Response schemas
class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    status: DocumentStatus
    summary: str | None = None
    classification: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    message: str


class ProcessingStatusResponse(BaseModel):
    id: uuid.UUID
    status: DocumentStatus
    summary: str | None = None
    classification: str | None = None
    error_message: str | None = None
