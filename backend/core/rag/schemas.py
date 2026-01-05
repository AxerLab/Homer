"""Pydantic schemas for RAG API endpoints"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class RAGDocumentCreate(BaseModel):
    """Response after document upload"""

    id: str = Field(..., description="Document UUID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Processing status")


class RAGDocumentResponse(BaseModel):
    """Full document details"""

    id: str
    filename: str
    file_type: str
    file_size: int
    status: Literal["pending", "processing", "completed", "failed"]
    error_message: Optional[str] = None
    created_at: str
    processed_at: Optional[str] = None


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


class RAGQueryResponse(BaseModel):
    """Query response"""

    answer: str = Field(..., description="Generated answer")
    question: str = Field(..., description="Original question")
    mode: str = Field(..., description="Query mode used")


class RAGContextRequest(BaseModel):
    """Request context for presentation"""

    topic: str = Field(..., min_length=1, description="Presentation topic")
    mode: Literal["hybrid", "local", "global", "naive"] = Field(default="hybrid")


class RAGContextResponse(BaseModel):
    """Context for presentation generation"""

    context: str = Field(..., description="Relevant context from documents")
    topic: str = Field(..., description="Original topic")


class RAGDocumentStatusResponse(BaseModel):
    """Response for document processing status check"""

    id: str = Field(..., description="Document UUID")
    filename: str = Field(..., description="Original filename")
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ..., description="Current processing status"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[str] = Field(None, description="When processing started")
    completed_at: Optional[str] = Field(None, description="When processing completed")
