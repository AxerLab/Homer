from typing import Optional
from pydantic import BaseModel, Field, model_validator
from ..content.slide_content import SlideContent
from ..layouts.slide_layout import SlideLayout

class Slide(BaseModel):
    """Individual slide model with enhanced validation and type safety."""

    title: Optional[str] = Field(
        default="", description="The title of the slide", min_length=0, max_length=200
    )
    content: Optional[SlideContent] = Field(
        default=SlideContent(text=None, text2=None, comparison=None),
        description="The content of the slide"
    )
    layout: SlideLayout = Field(
        ..., description=f"The layout type for the slide. {SlideLayout.get_schema_description()}"
    )
    image: Optional[str] = Field(
        None, description="Optional image description or URL. Use only on picture_with_caption layout", max_length=500
    )

    # conflicts with blank layout
    # @field_validator("title")
    # @classmethod
    # def validate_title(cls, v: str) -> str:
    #     """Validate slide title."""
    #     if not v or not v.strip():
    #         raise ValueError("Slide title cannot be empty")
    #     return v.strip()

    # @field_validator("image")
    # @classmethod
    # def validate_image(cls, v: Optional[str]) -> Optional[str]:
    #     """Validate image description."""
    #     if v is not None:
    #         if not isinstance(v, str):
    #             raise ValueError("Image description must be a string")
    #         if len(v.strip()) == 0:
    #             return None  # Convert empty string to None
    #         return v.strip()
    #     return v

    @model_validator(mode="after")
    def validate_layout(self) -> "Slide":
        """Validate slide layout."""
        # Validate layouts that have specific title requirements
        if self.layout == SlideLayout.TITLE or self.layout == SlideLayout.TITLE_ONLY:
            if not self.title or not self.title.strip():
                raise ValueError("Title slides must have a non-empty title")

        # Validate TITLE_ONLY layout (no content allowed)
        if self.layout == SlideLayout.TITLE_ONLY:
            if self.content is None:
                return self
            if self.content.text or self.content.text2:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must not have any of "
                    "'text', 'text2' content"
                )
            if self.content.comparison:
                raise ValueError(
                    f"Slides with layout '{self.layout}' cannot have 'comparison' content"
                )
            return self

        # no more validation needed for TITLE layout
        if self.layout == SlideLayout.TITLE:
            return self

        # Validate BLANK layout (no title or content allowed)
        if self.layout == SlideLayout.BLANK:
            if self.title and self.title.strip():
                raise ValueError(
                    f"Slides with layout '{self.layout}' must not have a title"
                )
            if self.content is None:
                return self
            if self.content.text or self.content.text2:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must not have any of "
                    "'text', 'text2' content"
                )
            if self.content.comparison:
                raise ValueError(
                    f"Slides with layout '{self.layout}' cannot have 'comparison' content"
                )
            return self

        # For all other layouts, content should not be None
        if self.content is None:
            raise ValueError(f"Slides with layout '{self.layout}' must have content")

        if self.layout == SlideLayout.COMPARISON:
            if not self.content.comparison:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'comparison' content"
                )
            if self.content.text or self.content.text2:
                raise ValueError(
                    f"Slides with layout '{self.layout}' cannot have 'text', 'text2' content"
                )
        else:
            if self.content.comparison:
                raise ValueError(
                    f"Slides with layout '{self.layout}' cannot have 'comparison' content"
                )

        if self.layout == SlideLayout.TITLE_AND_CONTENT:
            if not self.content.text:
                raise ValueError(f"Slides with layout '{self.layout}' must have 'text' content")
            if not self.content.text.para and not self.content.text.bullet:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content "
                    "with paragraph or bullet points"
                )

        if self.layout == SlideLayout.SECTION_HEADER:
            if not self.content.text:
                raise ValueError(f"Slides with layout '{self.layout}' must have 'text' content")
            if self.content.text.para is None or self.content.text.bullet != []:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content "
                    "with paragraph only"
                )

        if self.layout == SlideLayout.TWO_CONTENT:
            if not self.content.text or not self.content.text2:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have both 'text' and "
                    "'text2' content"
                )

        if self.layout == SlideLayout.CONTENT_WITH_CAPTION:
            if not self.content.text or not self.content.text2:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have both 'text', "
                    "'text2' content"
                )
        
        if self.layout == SlideLayout.PICTURE_WITH_CAPTION:
            if not self.image:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have an 'image' description or URL"
                )
            if not self.content.text:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content as caption"
                )
            if not self.content.text.para and not self.content.text.bullet:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content "
                    "as caption and not bullet points"
                )
        return self