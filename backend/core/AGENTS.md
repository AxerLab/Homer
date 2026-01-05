# BACKEND CORE MODULE

AI presentation generation engine: Pydantic-AI agents, dual export engines, RAG integration.

## STRUCTURE

```
core/
├── agent/          # Pydantic-AI agent definitions + prompts
├── engines/
│   ├── converter/  # PPTX→PDF via Go microservice
│   ├── pptx/       # JSON→PPTX via python-pptx
│   └── tex/        # JSON→LaTeX→PDF via Beamer
├── generator/      # Main generation orchestration
├── iterator/       # Slide-level editing/regeneration
├── llm/            # Groq model configuration
├── memory/         # Conversation history (global + iteration)
├── models/         # Pydantic slide/presentation models
├── rag/            # RAGAnything document retrieval
└── tools/          # Tavily image search
```

## DATA FLOW

```
User Prompt
    ↓
generator.generate_presentation_with_rag()
    ↓
rag_service.get_context_for_topic()  ─→ RAGAnything
    ↓
agent.run() with enhanced prompt
    ↓
SlidePresentation (validated Pydantic model)
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
| Add new slide layout | `models/layouts/slide_layout.py` + update engines |
| Change LLM model | `llm/__init__.py` (model, correction_model) |
| Add slide content type | `models/content/` + update both engines |
| Customize PPTX output | `engines/pptx/generator.py` |
| Customize LaTeX output | `engines/tex/generator.py` |
| Modify RAG behavior | `rag/service.py`, `rag/config.py` |
| Add image search | `tools/tavily_image_search.py` |

## KEY ABSTRACTIONS

### Agents (`agent/agent.py`)
```python
agent           # Main: generates SlidePresentation from prompt
correction_agent # Retry: fixes schema validation errors
interator_agent  # Edit: regenerates individual slides
```

### Models (`models/`)
- `SlidePresentation` — Root model, validates flow rules
- `Slide` — Individual slide with layout + content
- `SlideLayout` — Enum: title, title_and_content, two_content, comparison, picture_with_caption, title_only
- `SlideContent` — Contains TextContent, Comparison, image URL

### Engines
- **PPTX**: `json_handler.py` → `generator.py` → python-pptx
- **LaTeX**: `generator.py` → Beamer template → pdflatex (via tex-service)

## CONVENTIONS

- **Async for LLM/RAG**: All LLM calls use `await agent.run()` or `async def`
- **Sync for engines**: PPTX/LaTeX generation is synchronous
- **Relative imports**: `from ..config import`, `from ...core.models import`
- **Pydantic validators**: Use `@field_validator`, `@model_validator(mode="after")`

## ANTI-PATTERNS

- **NO direct OpenAI/Groq calls** — Always use agent abstraction
- **NO skipping validation** — Let Pydantic enforce slide rules
- **NO hardcoded themes** — Use `template_mapping.py`
