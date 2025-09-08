import json
from typing import List

from pydantic import BaseModel, Field, field_validator
from src.aislides.core.models.slide.slide import Slide
from src.aislides.core.models.layouts.slide_layout import SlideLayout

class SlidePresentation(BaseModel):
    """Complete presentation model with enhanced validation and flow checking."""

    slides: List[Slide] = Field(..., description="Array of slides in the presentation")

    @field_validator("slides")
    @classmethod
    def validate_slides(cls, v: List[Slide]) -> List[Slide]:
        """Validate slides list structure."""
        if not v:
            raise ValueError("Presentation must have at least one slide")
        if len(v) > 20:
            raise ValueError("Too many slides (max 20)")
        return v

    def validate_presentation_flow(self) -> bool:
        """
        Validate the logical flow of the presentation.

        Returns:
            True if the presentation has good flow, False otherwise.
        """
        if not self.slides:
            return False

        # Check for title slide at the beginning
        first_slide = self.slides[0]
        if first_slide.layout not in [
            SlideLayout.TITLE_ONLY,
            SlideLayout.TITLE_AND_CONTENT,
        ]:
            return False

        # Check for conclusion slide at the end
        last_slide = self.slides[-1]
        if last_slide.layout != SlideLayout.CONCLUSION:
            return False

        # Check for reasonable slide transitions
        for i in range(1, len(self.slides)):
            prev_layout = self.slides[i - 1].layout
            curr_layout = self.slides[i].layout

            # Avoid consecutive title_only slides
            if (
                prev_layout == SlideLayout.TITLE_ONLY
                and curr_layout == SlideLayout.TITLE_ONLY
            ):
                return False

        return True

    def to_json(self, **kwargs) -> str:
        """
        Convert the presentation to a JSON string.

        Args:
            **kwargs: Additional arguments to pass to json.dumps

        Returns:
            JSON string representation of the presentation
        """
        return self.model_dump_json(**kwargs)

    def to_dict(self) -> dict:
        """
        Convert the presentation to a dictionary.

        Returns:
            Dictionary representation of the presentation
        """
        return self.model_dump()

    @classmethod
    def from_json(cls, json_str: str) -> "SlidePresentation":
        """
        Create a SlidePresentation from a JSON string.

        Args:
            json_str: JSON string representation of the presentation

        Returns:
            SlidePresentation object
        """
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict) -> "SlidePresentation":
        """
        Create a SlidePresentation from a dictionary.

        Args:
            data: Dictionary representation of the presentation

        Returns:
            SlidePresentation object
        """
        return cls(**data)