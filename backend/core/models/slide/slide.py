from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, model_validator, field_validator
from ..content.slide_content import SlideContent
from ..layouts.slide_layout import SlideLayout


LAYOUT_CONTENT_LIMITS: Dict[SlideLayout, Dict[str, Any]] = {
    SlideLayout.TITLE_AND_CONTENT: {
        "max_bullet_length": 80,
        "max_bullets": 5,
        "max_para_length": 200,
    },
    SlideLayout.PICTURE_WITH_CAPTION: {
        "max_bullet_length": None,
        "max_bullets": 0,
        "max_para_length": 120,
    },
    SlideLayout.TWO_CONTENT: {
        "max_bullet_length": 60,
        "max_bullets": 4,
        "max_para_length": 150,
    },
    SlideLayout.COMPARISON: {
        "max_bullet_length": 50,
        "max_bullets": 4,
        "max_para_length": None,
    },
    SlideLayout.CONTENT_WITH_CAPTION: {
        "max_bullet_length": 60,
        "max_bullets": 4,
        "max_para_length": 150,
    },
}


class Slide(BaseModel):
    """Individual slide model with enhanced validation and type safety."""

    title: Optional[str] = Field(
        default="", description="The title of the slide", min_length=0, max_length=200
    )
    content: Optional[SlideContent] = Field(
        default=SlideContent(text=None, text2=None, comparison=None),
        description="The content of the slide",
    )
    layout: SlideLayout = Field(
        ...,
        description=f"The layout type for the slide. {SlideLayout.get_schema_description()}",
    )
    image: Optional[str] = Field(
        None,
        description="Optional image search query. Enter the search query here in detail to improve search results. Use with picture_with_caption layout OR two_content layout (with image_position).",
        max_length=500,
    )
    image_position: Optional[Literal["left", "right"]] = Field(
        None,
        description="For two_content layout only: specifies which column the image appears in. 'left' replaces text content, 'right' replaces text2 content. Required when using image with two_content layout.",
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
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content"
                )
            if not self.content.text.para and not self.content.text.bullet:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content "
                    "with paragraph or bullet points"
                )

        if self.layout == SlideLayout.SECTION_HEADER:
            if not self.content.text:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content"
                )
            if self.content.text.para is None or self.content.text.bullet != []:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content "
                    "with paragraph only"
                )

        if self.layout == SlideLayout.TWO_CONTENT:
            if self.image:
                # Image mode: one side has image, other side has text
                if not self.image_position:
                    raise ValueError(
                        f"Slides with layout '{self.layout}' and image must specify "
                        "'image_position' ('left' or 'right')"
                    )
                if self.image_position == "left":
                    # Image on left, text2 required on right
                    if not self.content.text2:
                        raise ValueError(
                            f"Slides with layout '{self.layout}' and image on left "
                            "must have 'text2' content for right side"
                        )
                elif self.image_position == "right":
                    # Image on right, text required on left
                    if not self.content.text:
                        raise ValueError(
                            f"Slides with layout '{self.layout}' and image on right "
                            "must have 'text' content for left side"
                        )
            else:
                # Text-only mode (original behavior)
                if not self.content.text or not self.content.text2:
                    raise ValueError(
                        f"Slides with layout '{self.layout}' must have both 'text' and "
                        "'text2' content, or use image with image_position"
                    )
                # Ensure image_position is not set without image
                if self.image_position:
                    raise ValueError(
                        f"Slides with layout '{self.layout}' cannot have 'image_position' "
                        "without an 'image' search query"
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
                    f"Slides with layout '{self.layout}' must have an 'image' search query"
                )
            if not self.content.text:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content as caption"
                )
            if not self.content.text.para and self.content.text.bullet:
                raise ValueError(
                    f"Slides with layout '{self.layout}' must have 'text' content "
                    "as caption and not bullet points"
                )
            if not self.title:
                raise ValueError(
                    f"Slides with layout '{self.layout}' should have a title for better context"
                )

        self._validate_layout_content_limits()

        return self

    def _validate_layout_content_limits(self) -> None:
        """Validate content against layout-specific length limits."""
        limits = LAYOUT_CONTENT_LIMITS.get(self.layout)
        if not limits or not self.content:
            return

        for text_content in [self.content.text, self.content.text2]:
            if text_content is None:
                continue

            max_bullets = limits.get("max_bullets", 5)
            max_bullet_len = limits.get("max_bullet_length")
            max_para_len = limits.get("max_para_length")

            if text_content.bullet:
                if max_bullets == 0:
                    raise ValueError(
                        f"Bullets not allowed for {self.layout.value} layout"
                    )
                if len(text_content.bullet) > max_bullets:
                    raise ValueError(
                        f"Too many bullets for {self.layout.value}: "
                        f"{len(text_content.bullet)} (max {max_bullets})"
                    )
                if max_bullet_len:
                    for i, bullet in enumerate(text_content.bullet):
                        if len(bullet) > max_bullet_len:
                            raise ValueError(
                                f"Bullet {i+1} too long for {self.layout.value}: "
                                f"{len(bullet)} chars (max {max_bullet_len})"
                            )

            if text_content.para and max_para_len:
                if len(text_content.para) > max_para_len:
                    raise ValueError(
                        f"Paragraph too long for {self.layout.value}: "
                        f"{len(text_content.para)} chars (max {max_para_len})"
                    )

    @field_validator("image")
    @classmethod
    def validate_image_link(cls, v: str) -> Optional[str]:
        """Validate image search query."""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Image search query must be a string")
            if len(v.strip()) == 0:
                return None  # Convert empty string to None
            return v.strip()
        return v
