from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Literal
import json

class PresentationCreate(BaseModel):
    """POST request - create presentation and generate file"""
    main_topic: str = Field(..., min_length=1, description="Main topic/prompt for presentation")
    file_type: Literal['pptx', 'pdf'] = Field(..., description="Type of file to generate")

class PresentationCreateResponse(BaseModel):
    """Response with UUID after creation"""
    id: str = Field(..., description="UUID of the presentation")

class PresentationGetResponse(BaseModel):
    """GET response - presentation data from database"""
    id: str = Field(..., description="UUID of the presentation")
    main_topic: str = Field(..., description="Main topic of the presentation")

class SlideUpdate(BaseModel):
    """PUT request - update specific slide"""
    slide_number: int = Field(..., ge=1, description="Slide number (1-based)")
    slide_content: str = Field(..., min_length=1, description="New content for the slide")

class SlideUpdateResponse(BaseModel):
    """Response after slide update"""
    id: str = Field(..., description="UUID of the presentation")
