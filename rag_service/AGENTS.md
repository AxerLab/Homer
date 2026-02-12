# RAG SERVICE

Standalone FastAPI microservice for document ingestion and retrieval using hybrid sparse + dense search.

## STRUCTURE

```
rag_service/
├── main.py         # FastAPI app and endpoints
├── core/
│   ├── service.py  # RAGService: extraction, chunking, indexing, retrieval
│   ├── config.py   # RAGConfig (chunking, retrieval, Groq synthesis)
│   ├── schemas.py  # Pydantic request/response models
│   └── sse.py      # Server-sent events for upload/index progress
├── .env.example    # Service environment variables
├── pyproject.toml  # Lightweight dependencies
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
Text Extraction (PDF, DOCX, PPTX, XLSX, TXT/MD, images metadata)
    ↓
Chunking
    ↓
Per-document indexing:
  - BM25 index (sparse retrieval)
  - FastEmbed vectors (dense retrieval)
    ↓
RRF fusion at query-time
    ↓
Optional Groq synthesis
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

### Retrieval Strategy

- BM25 ranking and FastEmbed cosine ranking run in parallel per document
- Reciprocal Rank Fusion merges both rankings
- Top chunks are returned directly or summarized with Groq

## CONFIG HIGHLIGHTS

- `RAG_FASTEMBED_MODEL`
- `RAG_CHUNK_SIZE_CHARS`, `RAG_CHUNK_OVERLAP_CHARS`, `RAG_MIN_CHUNK_CHARS`
- `RAG_PER_RETRIEVER_K`, `RAG_FINAL_CONTEXT_K`, `RAG_RRF_K`
- `RAG_GROQ_API_KEY`, `RAG_GROQ_MODEL`, `RAG_GROQ_MAX_TOKENS`
- `RAG_QUERY_TIMEOUT_SECONDS`, `RAG_LLM_TIMEOUT_SECONDS`, `RAG_SYNTHESIS_MAX_CHARS`

## NOTES

- Port `8002`; called by backend via `backend/core/rag/client.py`
- Designed for fast ingestion and low-latency retrieval without GraphRAG
- Supports PDF-first retrieval quality with additional file-format support
