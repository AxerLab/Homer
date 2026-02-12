"""Pydantic schemas for RAG API endpoints"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class RAGDocumentCreate(BaseModel):
    """Response after document upload"""

    id: str = Field(..., description="Document UUID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Processing status")


class RAGDocumentResponse(BaseModel):
    id: str
    filename: str
    file_extension: str
    file_size_bytes: int
    status: Literal["pending", "processing", "completed", "failed"]
    progress: int = 0
    progress_message: str = ""
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class RAGDocumentList(BaseModel):
    """List of documents"""

    documents: List[RAGDocumentResponse]
    total: int


class RAGQueryRequest(BaseModel):
    """Query request"""

    question: str = Field(..., min_length=1, description="Question to ask")
    mode: Literal["hybrid", "local", "global", "naive"] = Field(
        default="hybrid", description="Query mode"
    )
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results")
    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional document IDs to scope retrieval",
    )


class RAGQueryResponse(BaseModel):
    """Query response"""

    answer: str = Field(..., description="Generated answer")
    question: str = Field(..., description="Original question")
    mode: str = Field(..., description="Query mode used")


class RAGContextRequest(BaseModel):
    """Request context for presentation"""

    topic: str = Field(..., min_length=1, description="Presentation topic")
    mode: Literal["hybrid", "local", "global", "naive"] = Field(default="hybrid")
    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional document IDs to scope retrieval",
    )


class RAGContextResponse(BaseModel):
    """Context for presentation generation"""

    context: str = Field(..., description="Relevant context from documents")
    topic: str = Field(..., description="Original topic")


class RAGDocumentStatusResponse(BaseModel):
    id: str
    filename: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: int = 0
    progress_message: str = ""
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    file_size_bytes: int = 0
    file_extension: str = ""


class RAGProgressEvent(BaseModel):
    doc_id: str
    progress: int
    stage: str
    message: str
    error: Optional[str] = None


class RAGDocumentDeleteResponse(BaseModel):
    id: str
    deleted: bool
    message: str
