"""Model for handling the structured input for iterative slide enhancement."""
from .slide.slide import Slide
from typing import List, Optional
from pydantic import BaseModel, Field

class SlideIterator(BaseModel):
    """Model for handling the structured input for iterative slide enhancement."""

    slide: Slide = Field(..., description="The slide to be modified")
    slides_before: Optional[List[Slide]] = Field(
        None, description="Slides present before the current slide to be edited. This is required for context and the edited output must be coherent with these slides."
    )
    slides_after: Optional[List[Slide]] = Field(
        None, description="Slides present after the current slide to be edited. This is required for context and the edited output must be coherent with these slides."
    )
    outline: str = Field(..., description="The full outline of the presentation for context")
    instructions: str = Field(..., description="Instructions (user prompt) for modifying the slide")
    prompt: str = Field(..., description="The full prompt used to generate the presentation")