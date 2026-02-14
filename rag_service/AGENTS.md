# RAG SERVICE

Standalone FastAPI microservice for document ingestion and retrieval using hybrid sparse + dense search. Major rewrite in 3b8e5f8e — removed `llm_adapter.py`, moved LLM calls to direct Groq HTTP.

## STRUCTURE

```
rag_service/
├── main.py         # FastAPI app and endpoints (287 lines)
├── core/
│   ├── service.py  # RAGService: extraction, chunking, indexing, retrieval (661 lines)
│   ├── config.py   # RAGConfig dataclass — all settings via env vars (111 lines)
│   ├── schemas.py  # Pydantic request/response models (112 lines)
│   └── sse.py      # Server-sent events + ProgressStage enum
├── .env.example    # Service environment variables
├── pyproject.toml  # Lightweight deps (FastEmbed, rank-bm25, PyMuPDF, python-docx)
└── Dockerfile      # Multi-stage uv build, Python 3.12
```

## DATA FLOW

```
Document Upload (/upload)
    ↓
Save to rag_uploads/
    ↓
BackgroundTask: process_document()
    ↓
Text Extraction (PDF, DOCX, PPTX, XLSX, TXT/MD, images metadata)
    ↓
Chunking (configurable size/overlap/min via env)
    ↓
Per-document indexing:
  - BM25 index (sparse retrieval)
  - FastEmbed vectors (dense retrieval, BAAI/bge-small-en-v1.5 default)
    ↓
RRF fusion at query-time
    ↓
Optional Groq synthesis (direct HTTP, no llm_adapter)
    ↓
SSE progress updates → Frontend
```

## ENDPOINTS

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload document, returns doc_id, starts async processing |
| `/query` | POST | Retrieve and answer question from indexed chunks |
| `/context` | POST | Retrieve topic-focused context for presentation generation |
| `/documents` | GET | List all documents with status |
| `/document/{id}/status` | GET | Get processing status |
| `/document/{id}/progress` | GET | SSE stream for real-time progress |
| `/document/{id}` | DELETE | Remove document and its index |
| `/status` | GET | Service configuration and readiness |
| `/health` | GET | Health check |

`/query` and `/context` support optional `doc_ids` for document-scoped retrieval.

## KEY ABSTRACTIONS

### RAGService (`core/service.py`)
```python
rag_service.initialize()             # Lazy init FastEmbed model
rag_service.process_document()       # Extract + chunk + index one document
rag_service.query()                  # Hybrid retrieval + optional synthesis
rag_service.get_context_for_topic()  # Topic-focused retrieval for backend
```

### RAGConfig (`core/config.py`)
Dataclass with `__post_init__` creating storage dirs. ALL settings via env vars:
- Parser: `RAG_PARSER` (default: `hybrid_fast`)
- Embedding: `RAG_FASTEMBED_MODEL`, `RAG_EMBEDDING_DIM`, `RAG_EMBEDDING_MODEL`
- Chunking: `RAG_CHUNK_SIZE_CHARS` (1200), `RAG_CHUNK_OVERLAP_CHARS` (200), `RAG_MIN_CHUNK_CHARS` (120)
- Retrieval: `RAG_PER_RETRIEVER_K` (15), `RAG_FINAL_CONTEXT_K` (5), `RAG_RRF_K` (60)
- LLM: `RAG_GROQ_API_KEY`, `RAG_GROQ_MODEL`, `RAG_GROQ_MAX_TOKENS`, `RAG_GROQ_CHAT_COMPLETIONS_URL`
- Timeouts: `RAG_QUERY_TIMEOUT_SECONDS` (45), `RAG_LLM_TIMEOUT_SECONDS` (45)
- Files: Max 50MB, allowed: .pdf, .docx, .pptx, .xlsx, .txt, .md, .png, .jpg

### Progress Tracking (`core/sse.py`)
`ProgressStage` enum: PENDING → PARSING → EMBEDDING → INDEXING → COMPLETED/FAILED

## NOTES

- Port `8002`; called by backend via `backend/core/rag/client.py`
- Removed `llm_adapter.py` — LLM synthesis now via direct Groq HTTP calls in service.py
- Separate `pyproject.toml` — NOT shared with main backend
- Storage dirs auto-created: `rag_uploads/`, `rag_parsed/`, `rag_storage/`
- Designed for fast ingestion and low-latency retrieval without GraphRAG
