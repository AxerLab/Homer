from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .textcontent.textcontent import TextContent
from .textcontent.comparison import Comparison

class SlideContent(BaseModel):
    """Content structure for individual slides with validation."""

    text: Optional[TextContent] = Field(None, description="Text content for the slide")
    text2: Optional[TextContent] = Field(
        None, description="Secondary text content for layouts requiring two text areas"
    )
    comparison: Optional[Comparison] = Field(
        None, description="Comparison content for comparison slides. Use for Comparison layout only"
    )

    # conflicts with layouts like title_only, blank
    # @model_validator(mode="after")
    # def validate_content_not_empty(self) -> "SlideContent":
    #     """Ensure at least one content field is provided."""
    #     if not self.text and not self.text2 and not self.comparison:
    #         raise ValueError("At least one of 'text', 'text2' or 'comparison' must be provided")
    #     return self
