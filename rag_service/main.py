"""RAG Microservice - FastAPI application for document ingestion and retrieval"""

import uuid
import logging
from pathlib import Path

import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from core.service import rag_service, DocumentStatus
from core.config import rag_config
from core.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGContextRequest,
    RAGContextResponse,
    RAGDocumentCreate,
    RAGDocumentStatusResponse,
    RAGDocumentResponse,
    RAGDocumentList,
    RAGDocumentDeleteResponse,
    RAGStatusResponse,
)
from core.sse import sse_manager, sse_event_generator, ProgressStage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Service API",
    version="1.0.0",
    description="Document ingestion and retrieval service using RAGAnything",
)

# Add CORS for backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Backend service will call this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rag-service"}


@app.post("/upload", response_model=RAGDocumentCreate)
async def upload_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    """Upload a document for processing"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in rag_config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {rag_config.allowed_extensions}",
        )

    doc_id = str(uuid.uuid4())
    file_path = rag_config.upload_dir / f"{doc_id}{file_ext}"

    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            file_size = len(content)
            if file_size > rag_config.max_file_size:
                raise HTTPException(status_code=400, detail="File too large (max 50MB)")
            await f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    rag_service.register_document_with_metadata(
        doc_id=doc_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=file_size,
    )

    async def process_doc():
        try:
            await sse_manager.send_progress(
                doc_id, 5, ProgressStage.PENDING, "Initializing RAG service"
            )
            await rag_service.initialize()

            await sse_manager.send_progress(
                doc_id, 10, ProgressStage.PARSING, "Starting document processing"
            )
            await rag_service.process_document(
                str(file_path), doc_id=doc_id, filename=file.filename
            )
            await sse_manager.send_progress(
                doc_id, 100, ProgressStage.COMPLETED, "Processing complete"
            )
            logger.info(f"Document processed: {doc_id}")
        except Exception as e:
            logger.error(f"Background processing failed for {doc_id}: {e}")
            await sse_manager.send_progress(
                doc_id, 0, ProgressStage.FAILED, "Processing failed", error=str(e)
            )

    background_tasks.add_task(process_doc)

    return RAGDocumentCreate(id=doc_id, filename=file.filename, status="processing")


@app.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """Query the RAG knowledge base"""
    try:
        await rag_service.initialize()
        answer = await rag_service.query(
            question=request.question, mode=request.mode, top_k=request.top_k
        )
        return RAGQueryResponse(
            answer=answer, question=request.question, mode=request.mode
        )
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/context", response_model=RAGContextResponse)
async def get_rag_context(request: RAGContextRequest):
    """Get context for a topic from the RAG knowledge base"""
    try:
        await rag_service.initialize()
        context = await rag_service.get_context_for_topic(
            topic=request.topic, mode=request.mode
        )
        return RAGContextResponse(context=context, topic=request.topic)
    except Exception as e:
        logger.error(f"RAG context retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Context retrieval failed: {str(e)}"
        )


@app.get("/status", response_model=RAGStatusResponse)
async def rag_status():
    """Get RAG service status and configuration"""
    info = rag_service.get_config_info()
    return RAGStatusResponse(**info)


@app.get("/document/{doc_id}/status", response_model=RAGDocumentStatusResponse)
async def get_document_status(doc_id: str):
    """Get the processing status of a document"""
    doc_info = rag_service.get_document_status(doc_id)
    if doc_info is None:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    return RAGDocumentStatusResponse(
        id=doc_info.doc_id,
        filename=doc_info.filename,
        status=doc_info.status.value,
        progress=doc_info.progress,
        progress_message=doc_info.progress_message,
        error=doc_info.error,
        started_at=doc_info.started_at.isoformat() if doc_info.started_at else None,
        completed_at=doc_info.completed_at.isoformat()
        if doc_info.completed_at
        else None,
        file_size_bytes=doc_info.file_size_bytes,
        file_extension=doc_info.file_extension,
    )


@app.get("/document/{doc_id}/progress")
async def stream_document_progress(doc_id: str):
    """Stream document processing progress via SSE"""
    doc_info = rag_service.get_document_status(doc_id)
    if doc_info is None:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    return StreamingResponse(
        sse_event_generator(doc_id, sse_manager),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/documents", response_model=RAGDocumentList)
async def list_documents():
    """List all documents in the RAG service"""
    documents = rag_service.list_documents()
    return RAGDocumentList(
        documents=[
            RAGDocumentResponse(
                id=doc.doc_id,
                filename=doc.filename,
                file_extension=doc.file_extension,
                file_size_bytes=doc.file_size_bytes,
                status=doc.status.value,
                progress=doc.progress,
                progress_message=doc.progress_message,
                error=doc.error,
                started_at=doc.started_at.isoformat() if doc.started_at else None,
                completed_at=doc.completed_at.isoformat() if doc.completed_at else None,
            )
            for doc in documents
        ],
        total=len(documents),
    )


@app.delete("/document/{doc_id}", response_model=RAGDocumentDeleteResponse)
async def delete_document(doc_id: str):
    """Delete a document from the RAG service"""
    doc_info = rag_service.get_document_status(doc_id)
    if doc_info is None:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    if doc_info.status == DocumentStatus.PROCESSING:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete document while processing. Wait for completion.",
        )

    deleted = rag_service.delete_document(doc_id)
    return RAGDocumentDeleteResponse(
        id=doc_id,
        deleted=deleted,
        message="Document removed from library. Note: Content may remain in knowledge graph until server restart.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
