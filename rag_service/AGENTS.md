# RAG SERVICE

Standalone FastAPI microservice for document ingestion and retrieval using RAGAnything.

## STRUCTURE

```
rag_service/
├── main.py         # FastAPI app, all endpoints (251 lines)
├── core/
│   ├── service.py  # RAGService singleton (306 lines)
│   ├── config.py   # RAGConfig (dirs, limits, embeddings)
│   ├── schemas.py  # Pydantic request/response models
│   ├── sse.py      # Server-sent events for progress streaming
│   └── llm_adapter.py  # LLM configuration for RAGAnything
├── pyproject.toml  # Separate dependencies (raganything, llama-index)
└── Dockerfile
```

## DATA FLOW

```
Document Upload (/upload)
    ↓
Save to rag_uploads/
    ↓
BackgroundTask: process_document()
    ↓
RAGAnything.insert() → rag_storage/ (knowledge graph)
    ↓
SSE progress updates → Frontend
```

## ENDPOINTS

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload document, returns doc_id, starts async processing |
| `/query` | POST | Query knowledge base, returns answer |
| `/context` | POST | Get context for topic (used by main backend) |
| `/documents` | GET | List all documents with status |
| `/document/{id}/status` | GET | Get processing status |
| `/document/{id}/progress` | GET | SSE stream for real-time progress |
| `/document/{id}` | DELETE | Remove document from library |
| `/status` | GET | Service configuration info |
| `/health` | GET | Health check |

## KEY ABSTRACTIONS

### RAGService (`core/service.py`)
```python
rag_service.initialize()       # Lazy init RAGAnything
rag_service.process_document() # Ingest with progress updates
rag_service.query()            # Answer questions
rag_service.get_context_for_topic()  # Context retrieval for backend
```

### Progress Stages (`core/sse.py`)
```python
PENDING → PARSING → INDEXING → COMPLETED (or FAILED)
```

### Config (`core/config.py`)
- `upload_dir`: `./rag_uploads`
- `storage_dir`: `./rag_storage`
- `parsed_dir`: `./rag_parsed`
- `allowed_extensions`: .pdf, .docx, .doc, .txt, .pptx
- `max_file_size`: 50MB
- `embedding_model`: HuggingFace sentence-transformers

## CONVENTIONS

- **Async everywhere**: All endpoints are `async def`
- **BackgroundTasks**: Document processing runs async
- **SSE for progress**: Real-time updates via Server-Sent Events
- **Separate deps**: Own pyproject.toml (raganything, llama-index)

## NOTES

- **Port 8002**: Different from main backend (8000)
- **Called by main backend**: Via `backend/core/rag/client.py`
- **Lazy initialization**: RAGAnything initialized on first use
- **Document deletion**: Removes from library, knowledge graph persists until restart
- **Volumes in Docker**: rag_storage, rag_parsed, rag_uploads mounted
