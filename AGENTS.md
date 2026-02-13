# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-13
**Commit:** 3b8e5f8e
**Branch:** local_optim

## OVERVIEW

AI-powered presentation generator: Pydantic-AI agents (research + slide generation) with Groq/Ollama LLM, RAG document retrieval, dual export (PPTX via python-pptx, PDF via LaTeX/Beamer). Microservices: Python FastAPI backend, React/TypeScript frontend, Go conversion services, Python RAG service.

## STRUCTURE

```
ppt-ai/
├── main.py                 # FastAPI entry (NOT in backend/) - 676 lines, all routes inline
├── backend/
│   ├── api/               # Pydantic request/response schemas
│   ├── config/            # App config, logging (colorlog), storage config
│   ├── core/              # Agent, engines, RAG, models → see core/AGENTS.md
│   ├── db/                # SQLAlchemy models + CRUD (no migrations)
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
| Modify LLM prompts | `backend/core/agent/prompts.py` | Research + generator + iterator prompts |
| Change slide models | `backend/core/models/` | Pydantic v2 with validators |
| Add slide layout | `backend/core/models/layouts/slide_layout.py` | Update SlideLayout enum + both engines |
| PPTX generation | `backend/core/engines/pptx/generator.py` | python-pptx, layout-specific |
| LaTeX generation | `backend/core/engines/tex/generator.py` | Beamer template |
| Switch LLM provider | `backend/core/llm/` | `__init__.py` maps local/cloud models |
| RAG document processing | `rag_service/core/service.py` | Hybrid BM25 + FastEmbed (661 lines) |
| Frontend components | `frontend/src/components/` | Feature folders |
| API client | `frontend/src/services/api.ts` | presentationApi, ragApi (335 lines) |
| Add PPTX theme | `backend/templates/` + `template_mapping.py` | .pptx templates |
| Storage (Azure/local) | `backend/core/storage/azure_blob.py` | Dual backend support |
| CI/CD | `.github/workflows/deploy.yml` | Azure Container Apps on push to main |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `research_agent` | Agent | `backend/core/agent/agent.py` | Web research via DuckDuckGo, uses local Ollama |
| `slide_agent` | Agent | `backend/core/agent/agent.py` | Generates SlidePresentation, uses cloud Groq |
| `interator_agent` | Agent | `backend/core/agent/agent.py` | Slide-level editing (typo intentional) |
| `SlidePresentation` | Model | `backend/core/models/presentation/` | Root model, validates flow |
| `Slide` | Model | `backend/core/models/slide/slide.py` | Individual slide + layout + 200-line validator |
| `SlideLayout` | Enum | `backend/core/models/layouts/` | 9 layout types |
| `rag_service` | Singleton | `rag_service/core/service.py` | Per-document hybrid retrieval (661 lines) |
| `generate_presentation_with_rag` | Function | `backend/core/generator/` | Main generation entry (213 lines) |
| `structure_to_ppt` | Function | `backend/core/engines/pptx/` | JSON→PPTX |
| `generate_tex_and_pdf` | Function | `backend/core/engines/tex/` | JSON→LaTeX→PDF |
| `rag_client` | Client | `backend/core/rag/client.py` | HTTP client to rag_service |

## API ENDPOINTS (main.py)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/presentations/` | Generate presentation (optional RAG) |
| GET | `/api/v1/presentations/` | List all presentations |
| GET | `/api/v1/presentations/{id}` | Get presentation + slides |
| PUT | `/api/v1/presentations/{id}` | Update single slide |
| DELETE | `/api/v1/presentations/{id}` | Delete presentation + files |
| GET | `/api/v1/presentations/{id}/download` | Download PPTX/PDF |
| POST | `/api/v1/rag/upload` | Upload document (proxied) |
| POST | `/api/v1/rag/query` | Query RAG (proxied) |
| POST | `/api/v1/rag/context` | Get topic context (proxied) |
| GET | `/api/v1/rag/documents` | List documents (proxied) |
| GET | `/api/v1/rag/document/{id}/progress` | SSE progress stream |
| GET | `/health` | Health check |

## CONVENTIONS

### Python (Backend + RAG Service)
- **Package manager**: `uv` — `uv run`, `uv add`, `uv sync`
- **Python version**: 3.12+
- **Models**: Pydantic v2 with `@field_validator`, `@model_validator(mode="after")`
- **Async**: `async def` for LLM/RAG/storage calls, sync for engines
- **Imports**: Relative within `backend/` (`from ..config import`)
- **Logging**: Use shared logger from `backend.config.logs`

### TypeScript (Frontend)
- **Strict mode**: All strict flags enabled (`noUnusedLocals`, `verbatimModuleSyntax`)
- **Path alias**: `@/` → `src/` (use `@/components/...`)
- **Styling**: TailwindCSS only (no CSS-in-JS), one exception: `SimplifiedDocumentViewer.css`
- **State**: Local useState only (no Redux/Zustand/Context)
- **Components**: Feature folders (presentation/, layout/, rag/)
- **Icons**: HugeIcons primary, Lucide secondary

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
- **MUST have image slide** — At least one picture_with_caption or two_content with image
- **NO direct LLM calls** — Use agent abstraction (research_agent, slide_agent)
- **NO skipping Pydantic validation** — Let models enforce rules
- **NO hardcoded themes** — Use `template_mapping.py`

## PRESENTATION VALIDATION RULES

Enforced in `SlidePresentation.validate_presentation_flow()`:
1. First slide must be `title` or `title_and_content` layout
2. Cannot have consecutive `title_only` slides
3. Must have at least one slide with image
4. Max 20 slides

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

## DEPLOYMENT

- **CI/CD**: GitHub Actions (`.github/workflows/deploy.yml`) on push to main
- **Registry**: Azure Container Registry
- **Runtime**: Azure Container Apps (all 5 services)
- **Docker builds**: Multi-stage — uv for Python, Bun for frontend, Go for microservices
- **Frontend prod**: Bun builds → Caddy serves static assets

## NOTES

- **main.py at root**: Run `uvicorn main:app` from project root, NOT backend/
- **No tests yet**: pytest in dev deps, Playwright in frontend deps, but zero test files
- **No DB migrations**: No Alembic — tables created via `metadata.create_all()`
- **Two-stage generation**: research_agent (web search) → slide_agent (structured output)
- **LLM dual mode**: Ollama for local/research, Groq cloud for slide generation
- **RAG async processing**: Uploads via BackgroundTasks + SSE progress
- **Dual PDF paths**: PPTX→PDF via pptx-service, LaTeX→PDF via tex-service
- **Storage backends**: Azure blob or local filesystem (configurable)
- **Known violations**: Some `type: ignore` in Python engines/models, empty catches in TS
- **`interator_agent` typo**: Intentional — do not rename (used across codebase)
