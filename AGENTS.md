# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-25
**Commit:** d46a81e9
**Branch:** main

## OVERVIEW

AI-powered presentation generator: Pydantic-AI agents + Groq LLM, RAG document retrieval, dual export (PPTX via python-pptx, PDF via LaTeX/Beamer). Microservices: Python FastAPI backend, React/TypeScript frontend, Go conversion services, Python RAG service.

## STRUCTURE

```
ppt-ai/
├── main.py                 # FastAPI entry (NOT in backend/) - 670 lines
├── backend/
│   ├── api/               # Pydantic request/response schemas
│   ├── config/            # App config, logging (colorlog)
│   ├── core/              # Agent, engines, RAG, models → see core/AGENTS.md
│   ├── db/                # SQLAlchemy models + CRUD
│   └── templates/         # dark.pptx, light.pptx PPTX templates
├── frontend/              # React 18 + Vite + TailwindCSS → see src/AGENTS.md
├── rag_service/           # Separate RAG microservice (:8002) → see AGENTS.md
├── pptx_service/          # Go: PPTX→PDF via LibreOffice (:5001) ~120 lines
├── tex_service/           # Go: LaTeX→PDF via pdflatex (:8001) ~140 lines
└── docker-compose.yml     # 6 services: backend, frontend, db, tex, pptx, rag
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `main.py` | All routes inline, uses FastAPI |
| Modify LLM prompts | `backend/core/agent/prompts.py` | Generator + iterator prompts |
| Change slide models | `backend/core/models/` | Pydantic v2 with validators |
| Add slide layout | `backend/core/models/layouts/slide_layout.py` | Update SlideLayout enum + engines |
| PPTX generation | `backend/core/engines/pptx/generator.py` | python-pptx, layout-specific |
| LaTeX generation | `backend/core/engines/tex/generator.py` | Beamer template |
| RAG document processing | `rag_service/core/service.py` | RAGAnything wrapper |
| Frontend components | `frontend/src/components/` | Feature folders |
| API client | `frontend/src/services/api.ts` | presentationApi, ragApi |
| Add PPTX theme | `backend/templates/` + `template_mapping.py` | .pptx templates |
| Storage (Azure/local) | `backend/core/storage/azure_blob.py` | Dual backend support |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `agent` | Agent | `backend/core/agent/agent.py` | Main generator (llama-3.3-70b) |
| `correction_agent` | Agent | `backend/core/agent/agent.py` | Retry on schema errors |
| `interator_agent` | Agent | `backend/core/agent/agent.py` | Slide-level editing |
| `SlidePresentation` | Model | `backend/core/models/presentation/` | Root model, validates flow |
| `Slide` | Model | `backend/core/models/slide/slide.py` | Individual slide + layout |
| `SlideLayout` | Enum | `backend/core/models/layouts/` | 9 layout types |
| `rag_service` | Singleton | `rag_service/core/service.py` | RAGAnything integration |
| `generate_presentation_with_rag` | Function | `backend/core/generator/` | Main generation entry |
| `structure_to_ppt` | Function | `backend/core/engines/pptx/` | JSON→PPTX |
| `generate_tex_and_pdf` | Function | `backend/core/engines/tex/` | JSON→LaTeX→PDF |
| `rag_client` | Client | `backend/core/rag/client.py` | HTTP client to rag_service |

## CONVENTIONS

### Python (Backend + RAG Service)
- **Package manager**: `uv` — `uv run`, `uv add`, `uv sync`
- **Python version**: 3.12+
- **Models**: Pydantic v2 with `@field_validator`, `@model_validator(mode="after")`
- **Async**: `async def` for LLM/RAG/storage calls, sync for DB
- **Imports**: Relative within `backend/` (`from ..config import`)
- **Logging**: Use shared logger from `backend.config.logs`

### TypeScript (Frontend)
- **Strict mode**: All strict flags enabled
- **Path alias**: `@/` → `src/` (use `@/components/...`)
- **Styling**: TailwindCSS only (no CSS-in-JS)
- **State**: Local useState only (no Redux/Zustand)
- **Components**: Feature folders (presentation/, layout/, rag/)

### Go (Microservices)
- **Structure**: Flat single-file (~120 lines each)
- **HTTP**: Standard `net/http`, no frameworks
- **External tools**: `os/exec.Command` for LibreOffice/pdflatex

### Color Palette (Tailwind)
```
background: #0a0a0f    elevated: #13131a
primary: #6366f1       secondary: #8b5cf6
accent: #14b8a6        text: #f8fafc / #94a3b8
border: #1e293b        destructive: #ef4444
```

## ANTI-PATTERNS (THIS PROJECT)

- **NO `as any`** — TypeScript strict mode
- **NO empty catch blocks** — Always log errors
- **NO hardcoded API URLs** — Use `VITE_API_BASE_URL`
- **NO consecutive title_only slides** — Validator rejects
- **MUST have picture_with_caption** — At least one per presentation
- **NO direct LLM calls** — Use agent abstraction
- **NO skipping Pydantic validation** — Let models enforce rules
- **NO hardcoded themes** — Use `template_mapping.py`

## PRESENTATION VALIDATION RULES

Enforced in `SlidePresentation.validate_presentation_flow()`:
1. First slide must be `title` or `title_and_content` layout
2. Cannot have consecutive `title_only` slides
3. Must have at least one slide with image
4. Max 20 slides per presentation

## COMMANDS

```bash
# Backend
uv sync && source .venv/bin/activate
uvicorn main:app --reload              # :8000

# Frontend
cd frontend && npm install && npm run dev   # :5173

# RAG Service
cd rag_service && uv sync
uvicorn main:app --port 8002

# Docker (all services)
docker-compose up -d
docker-compose logs -f backend

# Tests (empty currently)
uv run pytest
cd frontend && npm run lint
```

## SERVICES & PORTS

| Service | Port | Purpose |
|---------|------|---------|
| backend | 8000 | FastAPI main API |
| frontend | 5173/80 | Vite dev / Caddy prod |
| db | 5432 | PostgreSQL 15 |
| tex-service | 8001 | LaTeX→PDF (Go) |
| pptx-service | 5001 | PPTX→PDF (Go + LibreOffice) |
| rag-service | 8002 | Document ingestion + retrieval |

## NOTES

- **main.py at root**: Run `uvicorn main:app` from project root, NOT backend/
- **No tests yet**: pytest in dev deps, tests/ empty
- **RAG async processing**: Uploads via BackgroundTasks + SSE progress
- **Dual PDF paths**: PPTX→PDF via pptx-service, LaTeX→PDF via tex-service
- **LLM retry logic**: `correction_agent` retries on schema validation errors
- **Storage backends**: Azure blob or local filesystem (configurable)
- **Known violations**: Some `type: ignore` in Python, empty catches in TS (needs cleanup)
