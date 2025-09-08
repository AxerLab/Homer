from typing import Optional

from pydantic import BaseModel, Field, field_validator
from src.aislides.core.models.content.slide_content import SlideContent
from src.aislides.core.models.layouts.slide_layout import SlideLayout

class Slide(BaseModel):
    """Individual slide model with enhanced validation and type safety."""

    title: str = Field(
        ..., description="The title of the slide", min_length=1, max_length=200
    )
    content: SlideContent = Field(..., description="The content of the slide")
    layout: SlideLayout = Field(..., description="The layout type for the slide")
    image: Optional[str] = Field(
        None, description="Optional image description or URL", max_length=500
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate slide title."""
        if not v or not v.strip():
            raise ValueError("Slide title cannot be empty")
        return v.strip()

    @field_validator("image")
    @classmethod
    def validate_image(cls, v: Optional[str]) -> Optional[str]:
        """Validate image description."""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Image description must be a string")
            if len(v.strip()) == 0:
                return None  # Convert empty string to None
            return v.strip()
        return v


