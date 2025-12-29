# Logos - AI RAG Engine

Python-based AI reasoning and retrieval engine for document processing and chat. Handles document parsing, chunking, embedding generation, vector search, and retrieval-augmented generation (RAG) for question answering over user documents.

## Tech Stack

- **FastAPI** - Async REST API framework
- **Celery + Redis** - Distributed task queue for document processing
- **LangChain** - RAG framework and LLM orchestration
- **Google Gemini** - LLM and embedding models
- **PostgreSQL + pgvector** - Vector database for semantic search
- **SQLAlchemy** - Async ORM with Alembic migrations
- **Docker Compose** - Container orchestration

## Features

- **Document Parsing** - Extract text from PDF and TXT files
- **Intelligent Chunking** - Recursive text splitting with overlap
- **Embeddings** - Generate vectors using Google's Gemini embedding model
- **Vector Search** - Semantic similarity search with pgvector
- **Document Summarization** - AI-generated summaries of uploaded documents
- **Document Classification** - Automatic categorization (Legal, Technical, etc.)
- **RAG Chat** - Chat with documents using retrieved context
- **SSE Streaming** - Real-time streaming responses for chat

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Server                          │
├─────────────────────────────────────────────────────────────────┤
│  /documents/upload  →  Queue Job  →  Celery Worker              │
│  /documents/{id}    →  Database Query                           │
│  /chat              →  Vector Search  →  LLM  →  SSE Stream     │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │  Redis   │   │ Postgres │   │ Google Gemini│
        │  Queue   │   │ pgvector │   │     API      │
        └──────────┘   └──────────┘   └──────────────┘
```

## Project Structure

```
app/
├── main.py                 # FastAPI app entry point
├── config.py               # Settings and environment variables
├── api/
│   ├── deps.py             # Dependency injection
│   └── routes/
│       ├── documents.py    # Document CRUD endpoints
│       └── chat.py         # Chat endpoint with SSE
├── core/
│   ├── parsing.py          # PDF/TXT text extraction
│   ├── chunking.py         # Text splitting
│   ├── embeddings.py       # Vector generation
│   ├── retrieval.py        # Similarity search
│   ├── prompts.py          # Prompt templates
│   └── llm.py              # LLM client
├── models/
│   ├── database.py         # SQLAlchemy models
│   └── schemas.py          # Pydantic schemas
├── workers/
│   ├── celery_app.py       # Celery configuration
│   └── tasks.py            # Document processing tasks
└── services/
    ├── document_service.py # Document business logic
    └── chat_service.py     # Chat/RAG logic

alembic/                    # Database migrations
uploads/                    # Uploaded files storage
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload document, returns job ID |
| GET | `/documents/{id}` | Get document details |
| GET | `/documents/{id}/status` | Get processing status |
| GET | `/documents` | List all documents |
| DELETE | `/documents/{id}` | Delete document and chunks |
| POST | `/chat` | Chat with document (SSE stream) |
| GET | `/health` | Health check |

## Document Processing Pipeline

```
Upload → Parse → Chunk → Embed → Store → Summarize → Classify
```

1. **Upload** - File received, document record created, job queued
2. **Parse** - Extract text from PDF/TXT
3. **Chunk** - Split into ~1000 char chunks with 200 char overlap
4. **Embed** - Generate 3072-dim vectors via Gemini
5. **Store** - Save chunks and vectors to pgvector
6. **Summarize** - Generate AI summary of document
7. **Classify** - Categorize document type

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Google AI API key

### Installation

```bash
# Clone and enter directory
cd logos

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```env
# Application
APP_NAME=logos
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://logos:logos@localhost:5434/logos
DATABASE_URL_SYNC=postgresql+psycopg2://logos:logos@localhost:5434/logos

# Redis
REDIS_URL=redis://localhost:6379/0

# Google AI
GOOGLE_API_KEY=your-google-api-key-here

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=models/gemini-embedding-001
LLM_MODEL=gemini-2.0-flash
```

### Running with Docker (Recommended)

```bash
# Start all services
make all

# Or manually
docker compose up -d

# Run migrations
docker compose exec api alembic upgrade head

# View logs
docker compose logs -f
```

### Running Locally (Development)

```bash
# Terminal 1: Start infrastructure
docker compose up -d postgres redis

# Terminal 2: Start API
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Start Celery worker
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

## Makefile Commands

```bash
make all        # Build and start all services
make up         # Start services
make down       # Stop services
make logs       # View logs
make migrate    # Run database migrations
make clean      # Stop and remove volumes
make status     # Check container status
```

## Database Schema

```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    content_type VARCHAR(50),
    status document_status,  -- PENDING, PROCESSING, COMPLETED, FAILED
    summary TEXT,
    classification VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Document chunks with vectors
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    content TEXT,
    chunk_index INTEGER,
    embedding vector(3072),  -- Gemini embedding dimension
    chunk_metadata JSONB
);
```

## Chat Flow

1. User sends message with document ID
2. Query is embedded using Gemini
3. Top-k similar chunks retrieved from pgvector
4. Context + query assembled into prompt
5. Gemini generates response
6. Response streamed back via SSE

## SSE Response Format

```
event: token
data: {"content": "partial response..."}

event: token
data: {"content": "more content..."}

event: done
data: {"chunk_ids": ["uuid1", "uuid2"]}
```

## Related Projects

- **[Atlas](../atlas)** - NestJS backend API gateway
- **[Lumen](../lumen)** - Next.js frontend application

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | Async PostgreSQL connection string |
| `DATABASE_URL_SYNC` | - | Sync PostgreSQL connection (Celery) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `GOOGLE_API_KEY` | - | Google AI Studio API key |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `EMBEDDING_MODEL` | `models/gemini-embedding-001` | Embedding model |
| `LLM_MODEL` | `gemini-2.0-flash` | Chat model |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload size |
