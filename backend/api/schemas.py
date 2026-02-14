from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime


class PresentationCreate(BaseModel):
    main_topic: str = Field(..., min_length=1, description="Main topic/prompt for presentation")
    file_type: Literal['pptx', 'pdf'] = Field(..., description="Type of file to generate")
    theme: Optional[str] = Field(None, description="Theme name for presentation (e.g., 'default', 'psychedelic_vibrant')")
    use_rag: bool = Field(default=False, description="Whether to use RAG context from uploaded documents")
    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of uploaded document IDs to use as RAG context",
    )

class PresentationCreateResponse(BaseModel):
    id: str = Field(..., description="UUID of the presentation")

class PresentationListItem(BaseModel):
    id: str = Field(..., description="UUID of the presentation")
    main_topic: str = Field(..., description="Main topic of the presentation")
    file_type: str = Field(default="pdf", description="Type of file (pptx or pdf)")
    created_at: Optional[datetime] = Field(None, description="When the presentation was created")

class PresentationListResponse(BaseModel):
    presentations: List[PresentationListItem] = Field(default=[], description="List of presentations")
    skip: int = Field(default=0)
    limit: int = Field(default=100)
    total: int = Field(default=0)

class SlideResponse(BaseModel):
    title: str = Field(default="", description="Slide title")
    content: str = Field(default="", description="Slide content text (flattened)")
    layout: str = Field(..., description="Slide layout type")

class PresentationGetResponse(BaseModel):
    id: str = Field(..., description="UUID of the presentation")
    main_topic: str = Field(..., description="Main topic of the presentation")
    file_type: str = Field(default="pdf", description="Type of file (pptx or pdf)")
    slides: List[SlideResponse] = Field(default=[], description="List of slides in the presentation")
    created_at: Optional[datetime] = Field(None, description="When the presentation was created")

class SlideUpdate(BaseModel):
    slide_number: int = Field(..., ge=1, description="Slide number (1-based)")
    slide_content: str = Field(..., min_length=1, description="New content for the slide")

class SlideUpdateResponse(BaseModel):
    id: str = Field(..., description="UUID of the presentation")
