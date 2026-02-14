# BACKEND CORE MODULE

AI presentation generation engine: Pydantic-AI agents, dual export engines, RAG integration.

## STRUCTURE

```
core/
├── agent/          # Pydantic-AI agents + prompts (research, slide, iterator)
├── engines/
│   ├── converter/  # PPTX→PDF via Go microservice
│   ├── pptx/       # JSON→PPTX via python-pptx (generator.py + json_handler.py)
│   └── tex/        # JSON→LaTeX→PDF via Beamer
├── generator/      # Main generation orchestration (213 lines)
├── iterator/       # Slide-level editing/regeneration (142 lines)
├── llm/            # Groq + Ollama model config (local/cloud)
├── memory/         # Conversation history (global + iteration, thread-safe)
├── models/         # Pydantic slide/presentation models (603 lines total)
├── rag/            # HTTP client to rag_service
├── storage/        # Azure blob / local filesystem
└── tools/          # Tavily image search
```

## DATA FLOW

```
User Prompt
    ↓
generator.generate_presentation_with_rag()
    ↓
rag_client.get_context()  ─→ rag_service (:8002)
    ↓
research_agent.run() (DuckDuckGo, Ollama)
    ↓
slide_agent.run() (Groq, NativeOutput → SlidePresentation)
    ↓
SlidePresentation (validated)
    ↓
┌─────────────────┬─────────────────┐
│ structure_to_ppt│ generate_tex_pdf│
│ (PPTX engine)   │ (LaTeX engine)  │
└────────┬────────┴────────┬────────┘
         ↓                  ↓
    .pptx file         .tex → .pdf
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Modify generation prompts | `agent/prompts.py` (research + generator + iterator) |
| Add new slide layout | `models/layouts/slide_layout.py` + update both engines |
| Change LLM model | `llm/__init__.py` (local_research_model, cloud_slide_model) |
| Add slide content type | `models/content/` + update engines |
| Customize PPTX output | `engines/pptx/generator.py` (346 lines) |
| Customize LaTeX output | `engines/tex/generator.py` (336 lines) |
| RAG HTTP client | `rag/client.py` (143 lines, async httpx) |
| Add image search | `tools/tavily_image_search.py` |
| Azure storage | `storage/azure_blob.py` (294 lines) |
| Generation orchestration | `generator/generator.py` (retry logic, RAG context) |
| Slide editing | `iterator/iterator.py` (context window, duplicate filtering) |

## KEY ABSTRACTIONS

### Agents (`agent/agent.py`)
```python
research_agent   # DuckDuckGo search, local Ollama model
slide_agent      # Generates SlidePresentation, cloud Groq, NativeOutput
interator_agent  # Slide-level editing, cloud Groq (typo intentional)
```
All use `pydantic_ai.Agent` with `retries=3`. No `correction_agent` anymore — retries via NativeOutput.

### LLM Models (`llm/`)
```python
local_research_model  = ollama_research_model   # Ollama (OpenAI-compatible)
local_slide_model     = ollama_slide_model       # Ollama for local dev
cloud_research_model  = groq_research_model      # Groq cloud
cloud_slide_model     = groq_slide_model         # Groq cloud (used in production)
```
Research models have tool-calling profile, slide models have JSON output profile.

### Models (`models/`)
- `SlidePresentation` — Root, validates flow rules (max 20 slides, image requirement)
- `Slide` — Individual slide with layout + content + 200-line validator
- `SlideLayout` — Enum: title, title_and_content, two_content, comparison, picture_with_caption, title_only, section_header, content_with_caption, blank
- `SlideContent` — Container: text, text2, comparison
- `TextContent` — para (paragraph) or bullet list
- `Comparison` — left/right side-by-side content
- `SlideIterator` — Context model for slide regeneration (slides_before/after, outline, instructions)
- `LAYOUT_CONTENT_LIMITS` — Per-layout limits for bullets/paragraphs

### Memory (`memory/`)
- `global_memory` — Thread-safe (asyncio.Lock), stores generation conversation history
- `iteration_memory` — Thread-safe, stores per-slide iteration history
- Both use hash-based keys and deepcopy for immutability

### Engines
- **PPTX**: `json_handler.py` parses → `generator.py` renders via python-pptx (with image URL fallbacks)
- **LaTeX**: `generator.py` → Beamer template → pdflatex (via tex-service HTTP POST)

## MODEL VALIDATION RULES

**Presentation level** (`validate_presentation_flow`):
1. First slide: `title` or `title_and_content`
2. No consecutive `title_only` slides
3. At least one image slide (picture_with_caption OR two_content with image)
4. Max 20 slides

**Slide level** (`validate_layout`):
- `TITLE`/`TITLE_ONLY`: Non-empty title required
- `TITLE_ONLY`: No text/text2/comparison content allowed
- `BLANK`: No title or content allowed
- `COMPARISON`: Must have comparison content, no text/text2
- `TITLE_AND_CONTENT`: Must have text with para or bullets
- `SECTION_HEADER`: Must have text with para only (no bullets)
- `TWO_CONTENT`: Both text columns OR image with image_position
- `CONTENT_WITH_CAPTION`: Both text and text2 required
- `PICTURE_WITH_CAPTION`: Image + text caption (para only, no bullets)

**Content limits** (vary by layout):
- Bullets: 4-5 max, 50-80 chars each
- Paragraphs: 120-200 chars max

## CONVENTIONS

- **Async for LLM/RAG**: `await agent.run()`, `async def`
- **Sync for engines**: PPTX/LaTeX generation is synchronous
- **Relative imports**: `from ..config import`, `from ...core.models import`
- **Validators**: `@field_validator`, `@model_validator(mode="after")`
- **Thread safety**: Memory modules use `asyncio.Lock`

## ANTI-PATTERNS

- **NO direct Groq/OpenAI calls** — Use agent abstraction
- **NO skipping validation** — Pydantic enforces slide rules
- **NO hardcoded themes** — Use `template_mapping.py`
- **AVOID `type: ignore`** — Some exist in engines/models, need cleanup
- **DO NOT rename `interator_agent`** — Typo used across codebase
