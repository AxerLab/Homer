# BACKEND CORE MODULE

AI presentation generation engine: Pydantic-AI agents, dual export engines, RAG integration.

## STRUCTURE

```
core/
├── agent/          # Pydantic-AI agents + prompts
├── engines/
│   ├── converter/  # PPTX→PDF via Go microservice
│   ├── pptx/       # JSON→PPTX via python-pptx
│   └── tex/        # JSON→LaTeX→PDF via Beamer
├── generator/      # Main generation orchestration (349 lines)
├── iterator/       # Slide-level editing/regeneration
├── llm/            # Groq/Portkey model config
├── memory/         # Conversation history (global + iteration)
├── models/         # Pydantic slide/presentation models
├── rag/            # HTTP client to rag_service
├── storage/        # Azure blob service
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
agent.run() with enhanced prompt
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
| Modify generation prompts | `agent/prompts.py` |
| Add new slide layout | `models/layouts/slide_layout.py` + update both engines |
| Change LLM model | `llm/__init__.py` (model, correction_model) |
| Add slide content type | `models/content/` + update engines |
| Customize PPTX output | `engines/pptx/generator.py` (348 lines) |
| Customize LaTeX output | `engines/tex/generator.py` (336 lines) |
| RAG HTTP client | `rag/client.py` |
| Add image search | `tools/tavily_image_search.py` |
| Azure storage | `storage/azure_blob.py` (294 lines) |

## KEY ABSTRACTIONS

### Agents (`agent/agent.py`)
```python
agent           # Main: generates SlidePresentation from prompt
correction_agent # Retry: fixes schema validation errors
interator_agent  # Edit: regenerates individual slides
```

### Models (`models/`)
- `SlidePresentation` — Root, validates flow rules (max 20 slides, image requirement)
- `Slide` — Individual slide with layout + content + validation
- `SlideLayout` — Enum: title, title_and_content, two_content, comparison, picture_with_caption, title_only, section_header, content_with_caption, blank
- `SlideContent` — Container: text, text2, comparison
- `TextContent` — para (paragraph) or bullet list
- `Comparison` — left/right side-by-side content
- `LAYOUT_CONTENT_LIMITS` — Per-layout limits for bullets/paragraphs

### Engines
- **PPTX**: `json_handler.py` parses → `generator.py` renders via python-pptx
- **LaTeX**: `generator.py` → Beamer template → pdflatex (via tex-service)

## MODEL VALIDATION RULES

**Presentation level** (`validate_presentation_flow`):
1. First slide: `title` or `title_and_content`
2. No consecutive `title_only` slides
3. At least one image slide
4. Max 20 slides

**Slide level** (`validate_layout`):
- `TITLE`/`TITLE_ONLY`: Non-empty title required
- `COMPARISON`: Must have comparison content, no text/text2
- `TITLE_AND_CONTENT`: Must have text with para or bullets
- `TWO_CONTENT`: Both text columns OR image with position
- `PICTURE_WITH_CAPTION`: Image + text caption (para only)

**Content limits** (vary by layout):
- Bullets: 4-5 max, 50-80 chars each
- Paragraphs: 120-200 chars max

## CONVENTIONS

- **Async for LLM/RAG**: `await agent.run()`, `async def`
- **Sync for engines**: PPTX/LaTeX generation is synchronous
- **Relative imports**: `from ..config import`, `from ...core.models import`
- **Validators**: `@field_validator`, `@model_validator(mode="after")`

## ANTI-PATTERNS

- **NO direct Groq/OpenAI calls** — Use agent abstraction
- **NO skipping validation** — Pydantic enforces slide rules
- **NO hardcoded themes** — Use `template_mapping.py`
- **AVOID `type: ignore`** — Some exist, need cleanup
