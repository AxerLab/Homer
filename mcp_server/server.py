"""PPT-AI MCP Server — Model Context Protocol bridge to the presentation backend.

Proxies all backend API endpoints to LLMs via MCP tools, resources, and prompts.
Runs as a standalone microservice on port 8003 with Streamable HTTP transport.

Usage:
    uv run python server.py
    # or: uv run python server.py  (reads MCP_PORT, BACKEND_URL from env)
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import colorlog
import httpx
from mcp.server.fastmcp import Context, FastMCP

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_handler = colorlog.StreamHandler()
_handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)
logger = logging.getLogger("pptai-mcp")
logger.setLevel(logging.INFO)
logger.addHandler(_handler)

# ---------------------------------------------------------------------------
# Lifespan — shared httpx.AsyncClient
# ---------------------------------------------------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@dataclass
class AppContext:
    """Shared application state available to every tool via lifespan context."""

    http_client: httpx.AsyncClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize a long-lived httpx client on startup, close on shutdown."""
    client = httpx.AsyncClient(
        base_url=BACKEND_URL,
        timeout=httpx.Timeout(180.0, connect=10.0),
    )
    logger.info("HTTP client connected to %s", BACKEND_URL)
    try:
        yield AppContext(http_client=client)
    finally:
        await client.aclose()
        logger.info("HTTP client closed")


# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "PPT-AI",
    instructions=(
        "You are connected to PPT-AI, an AI-powered presentation generator.\n"
        "PPT-AI can generate professional PPTX and PDF presentations from a topic, "
        "optionally enriched with uploaded documents via RAG (Retrieval-Augmented Generation).\n\n"
        "Key workflow: upload documents -> query/get context -> generate presentation -> download.\n\n"
        "Available file types: pptx, pdf.\n"
        "Available themes: default, dark, light.\n"
        "Slide layouts: title, title_and_content, section_header, two_content, comparison, "
        "title_only, blank, content_with_caption, picture_with_caption.\n\n"
        "Validation rules:\n"
        "  - Maximum 20 slides per presentation\n"
        "  - First slide must be a title or title_and_content layout\n"
        "  - At least one slide must contain an image\n"
        "  - No consecutive title_only slides\n\n"
        "RAG search modes: hybrid (default, recommended), local, global, naive.\n\n"
        "Note: Presentation generation is a long-running operation (30-60 seconds). "
        "generate_presentation returns a job_id immediately. "
        "Poll check_generation_status with that job_id every 10-15 seconds until "
        "status is 'completed' or 'failed'. Then use get_presentation to review.\n\n"
        "To let the user download a file, use get_download_url to construct a link and present it."
    ),
    lifespan=app_lifespan,
    host="0.0.0.0",
    port=int(os.getenv("MCP_PORT", "8003")),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _client(ctx: Context) -> httpx.AsyncClient:
    """Shortcut to extract the shared httpx client from lifespan context."""
    return ctx.request_context.lifespan_context.http_client


def _http_error(exc: httpx.HTTPStatusError, hint: str | None = None) -> dict[str, Any]:
    """Build a structured error dict from an HTTP status error."""
    try:
        detail = exc.response.json()
    except Exception:
        detail = exc.response.text
    return {
        "error": f"Backend returned HTTP {exc.response.status_code}",
        "status_code": exc.response.status_code,
        "detail": detail,
        "recovery_hint": hint or "CHECK_INPUT: Verify the parameters and try again.",
    }


def _conn_error() -> dict[str, Any]:
    """Build a structured error dict for connection failures."""
    return {
        "error": "Backend unavailable",
        "recovery_hint": (
            "RETRY_LATER: The backend service is not responding. "
            "Ensure it is running on the configured URL."
        ),
    }


# ---------------------------------------------------------------------------
# Background job tracking for long-running operations
# ---------------------------------------------------------------------------
_jobs: dict[str, dict[str, Any]] = {}


async def _run_generation(
    client: httpx.AsyncClient, job_id: str, body: dict[str, Any]
) -> None:
    try:
        r = await client.post("/api/v1/presentations/", json=body)
        r.raise_for_status()
        data = r.json()
        _jobs[job_id] = {
            "status": "completed",
            "presentation_id": data.get("id", data.get("presentation_id")),
            "message": (
                "Presentation created successfully. "
                "Use get_presentation to view slides or get_download_url to download."
            ),
            "data": data,
        }
    except httpx.HTTPStatusError as exc:
        logger.error("generate_presentation HTTP error: %s", exc)
        _jobs[job_id] = {
            "status": "failed",
            **_http_error(exc, "CHECK_INPUT: Verify topic is non-empty and file_type is 'pptx' or 'pdf'."),
        }
    except httpx.ConnectError:
        logger.error("generate_presentation connection error")
        _jobs[job_id] = {"status": "failed", **_conn_error()}
    except Exception as exc:
        logger.error("generate_presentation unexpected error: %s", exc)
        _jobs[job_id] = {
            "status": "failed",
            "error": str(exc),
            "recovery_hint": "RETRY: An unexpected error occurred.",
        }


# ---------------------------------------------------------------------------
# Tool 1 — generate_presentation
# ---------------------------------------------------------------------------
@mcp.tool()
async def generate_presentation(
    ctx: Context,
    topic: str,
    file_type: str = "pptx",
    theme: str | None = None,
    use_rag: bool = False,
    doc_ids: list[str] | None = None,
) -> dict:
    """Generate an AI-powered presentation on any topic.

    Creates a full slide deck (PPTX or PDF) using AI agents that research the
    topic and produce structured slides. Optionally uses uploaded documents via
    RAG for domain-specific content.

    This is a long-running operation. Returns a job_id immediately.
    Use check_generation_status to poll for completion.
    IMPORTANT: Wait at least 15 seconds between polls. Generation typically takes 30-60 seconds.

    Args:
        topic: The main subject of the presentation (e.g. "Machine Learning Fundamentals").
        file_type: Output format — "pptx" (PowerPoint) or "pdf" (LaTeX/Beamer). Default "pptx".
        theme: Visual theme — "default", "dark", or "light". None uses the default theme.
        use_rag: Whether to use uploaded documents for context enrichment. Default False.
        doc_ids: Specific document IDs to use for RAG. None uses all available documents.

    Returns:
        A dict with job_id and status "running". Poll check_generation_status for completion.
    """
    job_id = str(uuid.uuid4())
    logger.info("generate_presentation: job=%s topic=%r file_type=%s use_rag=%s", job_id, topic, file_type, use_rag)

    body: dict[str, Any] = {
        "main_topic": topic,
        "file_type": file_type,
        "theme": theme,
        "use_rag": use_rag,
        "doc_ids": doc_ids,
    }

    client = _client(ctx)
    _jobs[job_id] = {"status": "running", "topic": topic}
    asyncio.create_task(_run_generation(client, job_id, body))

    return {
        "job_id": job_id,
        "status": "running",
        "message": (
            "Presentation generation started. This typically takes 30-60 seconds. "
            "Use check_generation_status with this job_id to poll for completion. "
            "IMPORTANT: Wait at least 15 seconds between polls."
        ),
    }


# ---------------------------------------------------------------------------
# Tool 1b — check_generation_status
# ---------------------------------------------------------------------------
@mcp.tool()
async def check_generation_status(
    job_id: str,
) -> dict:
    """Check the status of a presentation generation job.

    After calling generate_presentation, use this tool to poll for completion.
    IMPORTANT: Wait at least 15 seconds between polls. Do NOT poll more frequently.
    Call until status is "completed" or "failed".

    Args:
        job_id: The job ID returned by generate_presentation.

    Returns:
        A dict with status ("running", "completed", or "failed").
        When completed, includes presentation_id and data.
    """
    job = _jobs.get(job_id)
    if job is None:
        return {
            "error": f"No job found with ID '{job_id}'",
            "recovery_hint": "CHECK_INPUT: Verify the job_id was returned by generate_presentation.",
        }
    return job


# ---------------------------------------------------------------------------
# Tool 2 — list_presentations
# ---------------------------------------------------------------------------
@mcp.tool()
async def list_presentations(
    ctx: Context,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    """List all generated presentations with pagination.

    Returns a paginated list of previously generated presentations including
    their IDs, topics, and creation dates.

    Args:
        skip: Number of presentations to skip (for pagination). Default 0.
        limit: Maximum number of presentations to return (1-100). Default 20.

    Returns:
        A dict containing the list of presentations, or an error dict.
    """
    logger.info("list_presentations: skip=%d limit=%d", skip, limit)
    try:
        client = _client(ctx)
        r = await client.get("/api/v1/presentations/", params={"skip": skip, "limit": limit})
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("list_presentations HTTP error: %s", exc)
        return _http_error(exc)
    except httpx.ConnectError:
        logger.error("list_presentations connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 3 — get_presentation
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_presentation(
    presentation_id: str,
    ctx: Context,
) -> dict:
    """Retrieve a presentation and all its slides by ID.

    Fetches the full presentation structure including every slide's layout,
    title, content, and metadata.

    Args:
        presentation_id: UUID of the presentation (e.g. "a1b2c3d4-...").

    Returns:
        A dict with the presentation data and slides, or an error dict.
    """
    logger.info("get_presentation: id=%s", presentation_id)
    try:
        client = _client(ctx)
        r = await client.get(f"/api/v1/presentations/{presentation_id}")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("get_presentation HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Verify the presentation_id exists. Use list_presentations to find valid IDs.")
    except httpx.ConnectError:
        logger.error("get_presentation connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 4 — update_slide
# ---------------------------------------------------------------------------
@mcp.tool()
async def update_slide(
    presentation_id: str,
    slide_number: int,
    new_content: str,
    ctx: Context,
) -> dict:
    """Edit and regenerate a single slide in an existing presentation.

    Updates the content of a specific slide and regenerates the presentation
    file (PPTX or PDF) with the change applied.

    Args:
        presentation_id: UUID of the presentation to edit.
        slide_number: 1-based slide number to update (e.g. 1 for the first slide).
        new_content: Natural-language instruction describing the desired change
                     (e.g. "Add more detail about neural networks").

    Returns:
        A dict confirming the update, or an error dict.
    """
    logger.info("update_slide: id=%s slide=%d", presentation_id, slide_number)
    await ctx.info("Regenerating slide...")

    body = {"slide_number": slide_number, "slide_content": new_content}

    try:
        client = _client(ctx)
        r = await client.put(f"/api/v1/presentations/{presentation_id}", json=body)
        r.raise_for_status()
        return {
            "presentation_id": presentation_id,
            "message": "Slide updated and presentation regenerated.",
            "data": r.json(),
        }
    except httpx.HTTPStatusError as exc:
        logger.error("update_slide HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Verify slide_number is within range and presentation_id exists.")
    except httpx.ConnectError:
        logger.error("update_slide connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 5 — delete_presentation
# ---------------------------------------------------------------------------
@mcp.tool()
async def delete_presentation(
    presentation_id: str,
    ctx: Context,
) -> dict:
    """Permanently delete a presentation and its generated files.

    Removes the presentation record and associated PPTX/PDF files from the server.
    This action cannot be undone.

    Args:
        presentation_id: UUID of the presentation to delete.

    Returns:
        A dict confirming deletion, or an error dict.
    """
    logger.info("delete_presentation: id=%s", presentation_id)
    try:
        client = _client(ctx)
        r = await client.delete(f"/api/v1/presentations/{presentation_id}")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("delete_presentation HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Verify the presentation_id exists.")
    except httpx.ConnectError:
        logger.error("delete_presentation connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 6 — get_download_url
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_download_url(
    ctx: Context,
    presentation_id: str,
    format: str = "pptx",
) -> dict:
    """Construct a download URL for a generated presentation file.

    Builds the direct download link for a presentation in the requested format.
    Does not call the backend — returns a URL the user can open in their browser.

    Args:
        presentation_id: UUID of the presentation to download.
        format: File format — "pptx" or "pdf". Default "pptx".

    Returns:
        A dict containing the download_url, format, and instructions.
    """
    logger.info("get_download_url: id=%s format=%s", presentation_id, format)
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    return {
        "download_url": (
            f"{backend_url}/api/v1/presentations/{presentation_id}"
            f"/download?format={format}&redirect=false"
        ),
        "format": format,
        "presentation_id": presentation_id,
        "instructions": "Provide this URL to the user to download their presentation file.",
    }


# ---------------------------------------------------------------------------
# Tool 7 — upload_document
# ---------------------------------------------------------------------------
@mcp.tool()
async def upload_document(
    filename: str,
    file_content_base64: str,
    ctx: Context,
) -> dict:
    """Upload a document to the RAG knowledge base for retrieval-augmented generation.

    Accepts a base64-encoded file and uploads it to the RAG service for indexing.
    Supported formats include PDF, DOCX, TXT, and MD. The document will be
    chunked and embedded for later retrieval during presentation generation.

    Args:
        filename: Name of the file including extension (e.g. "report.pdf").
        file_content_base64: The file content encoded as a base64 string.

    Returns:
        A dict with the document ID and processing status, or an error dict.
    """
    logger.info("upload_document: filename=%s", filename)
    try:
        decoded_bytes = base64.b64decode(file_content_base64)
    except Exception as exc:
        logger.error("upload_document base64 decode error: %s", exc)
        return {
            "error": f"Invalid base64 content: {exc}",
            "recovery_hint": "CHECK_INPUT: Ensure file_content_base64 is valid base64-encoded data.",
        }

    try:
        client = _client(ctx)
        r = await client.post(
            "/api/v1/rag/upload",
            files={"file": (filename, decoded_bytes)},
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("upload_document HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Verify the file format is supported (PDF, DOCX, TXT, MD).")
    except httpx.ConnectError:
        logger.error("upload_document connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 8 — query_knowledge_base
# ---------------------------------------------------------------------------
@mcp.tool()
async def query_knowledge_base(
    ctx: Context,
    question: str,
    mode: str = "hybrid",
    top_k: int = 10,
    doc_ids: list[str] | None = None,
) -> dict:
    """Search the uploaded document knowledge base with a natural-language question.

    Performs semantic + keyword search across indexed documents and returns the
    most relevant text chunks as context.

    Args:
        question: Natural-language query (e.g. "What are the key findings on climate change?").
        mode: Search strategy — "hybrid" (recommended), "local", "global", or "naive". Default "hybrid".
        top_k: Number of result chunks to return (1-50). Default 10.
        doc_ids: Optional list of document IDs to restrict the search to.

    Returns:
        A dict with matching text chunks and relevance scores, or an error dict.
    """
    logger.info("query_knowledge_base: question=%r mode=%s top_k=%d", question, mode, top_k)
    body: dict[str, Any] = {"question": question, "mode": mode, "top_k": top_k}
    if doc_ids is not None:
        body["doc_ids"] = doc_ids

    try:
        client = _client(ctx)
        r = await client.post("/api/v1/rag/query", json=body)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("query_knowledge_base HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Ensure documents have been uploaded and processed before querying.")
    except httpx.ConnectError:
        logger.error("query_knowledge_base connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 9 — get_topic_context
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_topic_context(
    ctx: Context,
    topic: str,
    mode: str = "hybrid",
    doc_ids: list[str] | None = None,
) -> dict:
    """Retrieve contextual information about a topic from uploaded documents.

    Gathers relevant context from the knowledge base to inform presentation
    generation. This is typically called before generate_presentation with use_rag=True.

    Args:
        topic: The topic to retrieve context for (e.g. "Renewable Energy Trends").
        mode: Search strategy — "hybrid" (recommended), "local", "global", or "naive". Default "hybrid".
        doc_ids: Optional list of document IDs to restrict the search to.

    Returns:
        A dict with aggregated context from matching documents, or an error dict.
    """
    logger.info("get_topic_context: topic=%r mode=%s", topic, mode)
    body: dict[str, Any] = {"topic": topic, "mode": mode}
    if doc_ids is not None:
        body["doc_ids"] = doc_ids

    try:
        client = _client(ctx)
        r = await client.post("/api/v1/rag/context", json=body)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("get_topic_context HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Ensure documents have been uploaded and processed first.")
    except httpx.ConnectError:
        logger.error("get_topic_context connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 10 — list_documents
# ---------------------------------------------------------------------------
@mcp.tool()
async def list_documents(ctx: Context) -> dict:
    """List all documents uploaded to the RAG knowledge base.

    Returns metadata for every indexed document including IDs, filenames,
    and processing status. Use document IDs from this list when calling
    query_knowledge_base or generate_presentation with specific documents.

    Returns:
        A dict with the list of documents, or an error dict.
    """
    logger.info("list_documents")
    try:
        client = _client(ctx)
        r = await client.get("/api/v1/rag/documents")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("list_documents HTTP error: %s", exc)
        return _http_error(exc)
    except httpx.ConnectError:
        logger.error("list_documents connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 11 — get_document_status
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_document_status(
    doc_id: str,
    ctx: Context,
) -> dict:
    """Check the processing status of an uploaded document.

    After uploading a document, use this to verify whether indexing is complete,
    in progress, or has failed.

    Args:
        doc_id: UUID of the document to check.

    Returns:
        A dict with the document's processing status, or an error dict.
    """
    logger.info("get_document_status: doc_id=%s", doc_id)
    try:
        client = _client(ctx)
        r = await client.get(f"/api/v1/rag/document/{doc_id}/status")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("get_document_status HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Verify the doc_id exists. Use list_documents to find valid IDs.")
    except httpx.ConnectError:
        logger.error("get_document_status connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 12 — delete_document
# ---------------------------------------------------------------------------
@mcp.tool()
async def delete_document(
    doc_id: str,
    ctx: Context,
) -> dict:
    """Remove a document from the RAG knowledge base.

    Permanently deletes a document and its indexed chunks. Future queries and
    generations will no longer use this document's content.

    Args:
        doc_id: UUID of the document to delete.

    Returns:
        A dict confirming deletion, or an error dict.
    """
    logger.info("delete_document: doc_id=%s", doc_id)
    try:
        client = _client(ctx)
        r = await client.delete(f"/api/v1/rag/document/{doc_id}")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as exc:
        logger.error("delete_document HTTP error: %s", exc)
        return _http_error(exc, "CHECK_INPUT: Verify the doc_id exists.")
    except httpx.ConnectError:
        logger.error("delete_document connection error")
        return _conn_error()


# ---------------------------------------------------------------------------
# Tool 13 — check_health
# ---------------------------------------------------------------------------
@mcp.tool()
async def check_health(ctx: Context) -> dict:
    """Check the health of all PPT-AI backend services.

    Queries the backend API, RAG service, and storage service in parallel and
    reports individual and overall health status.

    Returns:
        A dict with backend, rag_service, storage status and an overall verdict
        ("healthy", "degraded", or "unhealthy").
    """
    logger.info("check_health")
    client = _client(ctx)

    async def _check(path: str) -> dict[str, Any]:
        try:
            r = await client.get(path, timeout=10.0)
            r.raise_for_status()
            return {"status": "healthy", "data": r.json()}
        except httpx.HTTPStatusError as exc:
            return {"status": "unhealthy", "error": f"HTTP {exc.response.status_code}"}
        except httpx.ConnectError:
            return {"status": "unhealthy", "error": "Connection refused"}
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}

    backend_check, rag_check, storage_check = await asyncio.gather(
        _check("/health"),
        _check("/api/v1/rag/status"),
        _check("/api/v1/storage/health"),
    )

    statuses = [backend_check["status"], rag_check["status"], storage_check["status"]]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif all(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    else:
        overall = "degraded"

    return {
        "backend": backend_check,
        "rag_service": rag_check,
        "storage": storage_check,
        "overall": overall,
    }


# ---------------------------------------------------------------------------
# Resource 1 — presentation://{presentation_id}
# ---------------------------------------------------------------------------
@mcp.resource("presentation://{presentation_id}")
async def presentation_resource(presentation_id: str) -> str:
    """Retrieve a formatted text representation of a presentation and all its slides."""
    async with httpx.AsyncClient(
        base_url=BACKEND_URL,
        timeout=httpx.Timeout(30.0, connect=10.0),
    ) as client:
        r = await client.get(f"/api/v1/presentations/{presentation_id}")
        r.raise_for_status()
        data = r.json()

    lines = [
        f"Presentation: {data.get('main_topic', 'Untitled')}",
        f"ID: {data.get('id', presentation_id)}",
        f"File type: {data.get('file_type', 'unknown')}",
        f"Theme: {data.get('theme', 'default')}",
        f"Created: {data.get('created_at', 'unknown')}",
        "",
        f"--- Slides ({len(data.get('slides', []))}) ---",
    ]

    for i, slide in enumerate(data.get("slides", []), start=1):
        lines.append(f"\n[Slide {i}] Layout: {slide.get('layout', 'unknown')}")
        if slide.get("title"):
            lines.append(f"  Title: {slide['title']}")
        if slide.get("content"):
            content = slide["content"]
            if isinstance(content, list):
                for item in content:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"  Content: {content}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Resource 2 — document://{doc_id}/status
# ---------------------------------------------------------------------------
@mcp.resource("document://{doc_id}/status")
async def document_status_resource(doc_id: str) -> str:
    """Retrieve a formatted text representation of a document's processing status."""
    async with httpx.AsyncClient(
        base_url=BACKEND_URL,
        timeout=httpx.Timeout(30.0, connect=10.0),
    ) as client:
        r = await client.get(f"/api/v1/rag/document/{doc_id}/status")
        r.raise_for_status()
        data = r.json()

    lines = [
        f"Document Status",
        f"ID: {data.get('id', doc_id)}",
        f"Filename: {data.get('filename', 'unknown')}",
        f"Status: {data.get('status', 'unknown')}",
        f"Chunks: {data.get('chunk_count', 'N/A')}",
        f"Uploaded: {data.get('created_at', 'unknown')}",
    ]

    if data.get("error"):
        lines.append(f"Error: {data['error']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Prompt 1 — create_presentation
# ---------------------------------------------------------------------------
@mcp.prompt()
def create_presentation(
    topic: str,
    file_type: str = "pptx",
    use_documents: str = "false",
) -> str:
    """Guide the LLM through the presentation creation workflow.

    Produces a step-by-step plan for generating a presentation, optionally
    incorporating uploaded documents for richer content.
    """
    steps = []

    if use_documents.lower() in ("true", "1", "yes"):
        steps.extend([
            "1. First, list all available documents using the list_documents tool.",
            "2. Use get_topic_context to retrieve relevant context from the documents "
            f'   about "{topic}".',
            f'3. Generate the presentation using generate_presentation with topic="{topic}", '
            f'   file_type="{file_type}", and use_rag=True. Pass the relevant doc_ids.',
        ])
        next_step = 4
    else:
        steps.append(
            f'1. Generate the presentation using generate_presentation with topic="{topic}" '
            f'   and file_type="{file_type}".'
        )
        next_step = 2

    steps.extend([
        f"{next_step}. Once generation completes, use get_presentation to review all slides.",
        f"{next_step + 1}. If any slides need changes, use update_slide to refine them.",
        f"{next_step + 2}. Finally, use get_download_url with format=\"{file_type}\" to get "
        "the download link and present it to the user.",
    ])

    return (
        f"Create a {file_type.upper()} presentation about: {topic}\n\n"
        "Follow these steps:\n"
        + "\n".join(steps)
        + "\n\nRemember: Generation takes 30-60 seconds. Inform the user about the wait."
    )


# ---------------------------------------------------------------------------
# Prompt 2 — research_and_present
# ---------------------------------------------------------------------------
@mcp.prompt()
def research_and_present(topic: str) -> str:
    """Guide the LLM through the full RAG-enriched presentation workflow.

    Produces a multi-step plan that checks available documents, queries the
    knowledge base, generates a presentation with RAG, and provides a download link.
    """
    return (
        f"Research and create a presentation about: {topic}\n\n"
        "Follow this workflow:\n"
        "1. Check what documents are available using list_documents.\n"
        f'2. Query the knowledge base about "{topic}" using query_knowledge_base '
        "   with mode=\"hybrid\" to understand what information is available.\n"
        f'3. Get aggregated context using get_topic_context for "{topic}".\n'
        f'4. Generate the presentation using generate_presentation with topic="{topic}", '
        "   use_rag=True, and the relevant doc_ids from step 1.\n"
        "5. Review the generated slides using get_presentation.\n"
        "6. Refine any slides that need improvement using update_slide.\n"
        '7. Get the download URL using get_download_url with the desired format ("pptx" or "pdf") '
        "   and present it to the user.\n\n"
        "Note: If no documents are available, inform the user and offer to generate "
        "a presentation without RAG instead."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "8003"))
    logger.info("Starting PPT-AI MCP server on 0.0.0.0:%d", port)
    mcp.run(transport="streamable-http")
