# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-03
**Commit:** 25bfd3ea
**Branch:** test

## OVERVIEW

AI-powered presentation generator using Pydantic-AI agents with LLM (Groq), RAG document retrieval, and dual export engines (PPTX via python-pptx, PDF via LaTeX). Microservices architecture: Python FastAPI backend, React/TypeScript frontend, Go conversion services.

## STRUCTURE

```
ppt-ai/
├── main.py                 # FastAPI entry (NOT in backend/)
├── backend/
│   ├── api/               # Pydantic schemas for REST
│   ├── config/            # App config, logging
│   ├── core/              # Agent, engines, RAG, models (see core/AGENTS.md)
│   ├── db/                # SQLAlchemy models + CRUD
│   └── templates/         # dark.pptx, light.pptx templates
├── frontend/              # React 18 + Vite + TailwindCSS
│   └── src/
│       ├── components/    # By feature: layout/, presentation/, rag/, viewer/
│       ├── services/api.ts
│       └── types/
├── pptx_service/          # Go: PPTX→PDF via LibreOffice (:5001)
├── tex_service/           # Go: LaTeX→PDF via pdflatex (:8001)
└── docker-compose.yml     # 5 services: backend, frontend, db, tex, pptx
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `main.py` | All routes defined inline |
| Modify LLM prompts | `backend/core/agent/prompts.py` | Generator + iterator prompts |
| Change slide models | `backend/core/models/` | Pydantic models with validators |
| Add slide layout | `backend/core/models/layouts/slide_layout.py` | SlideLayout enum |
| PPTX generation | `backend/core/engines/pptx/` | generator.py, json_handler.py |
| LaTeX generation | `backend/core/engines/tex/generator.py` | Beamer template |
| RAG configuration | `backend/core/rag/config.py` | HuggingFace embeddings |
| Frontend components | `frontend/src/components/` | React components by feature |
| API client | `frontend/src/services/api.ts` | presentationApi object |
| Add new theme | `backend/templates/` + `template_mapping.py` | PPTX templates |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `agent` | Agent | `backend/core/agent/agent.py` | Main Pydantic-AI agent (llama-3.3-70b) |
| `correction_agent` | Agent | `backend/core/agent/agent.py` | Retry agent for schema errors |
| `interator_agent` | Agent | `backend/core/agent/agent.py` | Slide editing agent |
| `SlidePresentation` | Model | `backend/core/models/presentation/` | Root presentation model |
| `Slide` | Model | `backend/core/models/slide/slide.py` | Individual slide model |
| `SlideLayout` | Enum | `backend/core/models/layouts/` | 6 layout types |
| `rag_service` | Singleton | `backend/core/rag/service.py` | RAGAnything wrapper |
| `generate_presentation_with_rag` | Function | `backend/core/generator/` | Main generation entry |
| `structure_to_ppt` | Function | `backend/core/engines/pptx/` | JSON→PPTX conversion |
| `generate_tex_and_pdf` | Function | `backend/core/engines/tex/` | JSON→LaTeX→PDF |

## CONVENTIONS

### Python (Backend)
- **Package manager**: `uv` — use `uv run`, `uv add`, `uv sync`
- **Models**: Pydantic v2 with `field_validator`, `model_validator`
- **Async**: Use `async def` for LLM/RAG calls, sync for DB
- **Imports**: Relative within `backend/` (`from ..config import`)

### TypeScript (Frontend)
- **Strict mode**: All strict flags enabled in tsconfig
- **Path alias**: `@/` → `src/` (use `@/components/...`)
- **Styling**: TailwindCSS with custom palette (see below)
- **Components**: Feature folders (presentation/, layout/, rag/)

### Color Palette (Tailwind)
```
background: #0a0a0f    elevated: #13131a
primary: #6366f1       secondary: #8b5cf6
accent: #14b8a6        text: #f8fafc / #94a3b8
border: #1e293b        destructive: #ef4444
```

## ANTI-PATTERNS (THIS PROJECT)

- **NO `as any`** — TypeScript strict mode enforced
- **NO empty catch blocks** — Always log or handle errors
- **NO hardcoded API URLs** — Use env vars or `VITE_API_BASE_URL`
- **NO consecutive title_only slides** — Presentation validator rejects
- **MUST have picture_with_caption slide** — At least one per presentation

## PRESENTATION VALIDATION RULES

Enforced in `SlidePresentation.validate_presentation_flow()`:
1. First slide must be `title` or `title_and_content` layout
2. Cannot have consecutive `title_only` slides
3. Must have at least one `picture_with_caption` slide
4. Max 20 slides per presentation

## COMMANDS

```bash
# Backend (Python)
uv sync                           # Install dependencies
source .venv/bin/activate
uvicorn main:app --reload         # Start API server (:8000)

# Frontend
cd frontend && npm install
npm run dev                       # Vite dev server (:5173)
npm run build                     # Production build

# Docker (all services)
docker-compose up -d              # Start all: backend, frontend, db, tex, pptx
docker-compose logs -f backend    # Tail logs

# Tests
uv run pytest                     # Backend tests (empty currently)
cd frontend && npm run lint       # ESLint
```

## SERVICES & PORTS

| Service | Port | Purpose |
|---------|------|---------|
| backend | 8000 | FastAPI main API |
| frontend | 5173/80 | Vite dev / Caddy prod |
| db | 5432 | PostgreSQL 15 |
| tex-service | 8001 | LaTeX→PDF (Go) |
| pptx-service | 5001 | PPTX→PDF (Go + LibreOffice) |

## NOTES

- **main.py at root**: Not in `backend/` — run `uvicorn main:app` from project root
- **No tests yet**: `backend/tests/` empty, pytest in dev deps
- **RAG background processing**: Document uploads processed async via `BackgroundTasks`
- **Dual PDF paths**: PPTX→PDF uses pptx-service, LaTeX→PDF uses tex-service
- **LLM retry logic**: On schema validation errors, `correction_agent` retries with error context
- **Go services minimal**: Single-file microservices (~120 lines each), no cmd/internal structure
