from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

class SlideContent(BaseModel):
    """Content structure for individual slides with validation."""

    para: Optional[str] = Field(
        None, description="Paragraph content for the slide", max_length=1000
    )
    bullet: Optional[List[str]] = Field(
        None, description="List of bullet points", max_length=10
    )

    @model_validator(mode="after")
    def validate_content_not_empty(self) -> "SlideContent":
        """Ensure at least one content field is provided."""
        if not self.para and not self.bullet:
            raise ValueError("At least one of 'para' or 'bullet' must be provided")
        return self

    @field_validator("bullet")
    @classmethod
    def validate_bullet_points(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate bullet points structure and content."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Bullet points must be a list")
            if len(v) == 0:
                raise ValueError("Bullet points list cannot be empty")
            if len(v) > 10:
                raise ValueError("Too many bullet points (max 10)")
            for item in v:
                if not isinstance(item, str) or len(item.strip()) == 0:
                    raise ValueError("Each bullet point must be a non-empty string")
        return v

    @field_validator("para")
    @classmethod
    def validate_paragraph(cls, v: Optional[str]) -> Optional[str]:
        """Validate paragraph content."""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Paragraph must be a string")
            if len(v.strip()) == 0:
                raise ValueError("Paragraph cannot be empty")
            if len(v) > 1000:
                raise ValueError("Paragraph too long (max 1000 characters)")
        return v