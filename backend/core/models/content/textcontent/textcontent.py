from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, List
from pydantic import conlist


MAX_BULLET_POINTS = 5
MAX_PARAGRAPH_LENGTH = 1000
BulletList = conlist(str, min_length=0, max_length=MAX_BULLET_POINTS)
class TextContent(BaseModel):
    para: Optional[str] = Field(
        None, description="Paragraph content for the slide", max_length=MAX_PARAGRAPH_LENGTH
    )
    bullet: Optional[BulletList] = Field(  # type: ignore
        default=[],
        description=(
            f"List of bullet points. Max {MAX_BULLET_POINTS} items."
            "If there are more than {MAX_BULLET_POINTS} points, consider"
            "splitting into multiple slides."
        ),
    )

    @model_validator(mode="after")
    def validate_content_not_empty(self) -> "TextContent":
        """Ensure at least one content field is provided."""
        if not self.para and not self.bullet:
            raise ValueError("At least one of 'para' or 'bullet' must be provided")
        return self

    @field_validator("bullet")
    @classmethod
    def validate_bullet_points(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate bullet points structure and content."""
        if v is None:
            return []
        if v != []:
            if not isinstance(v, list):
                raise ValueError("Bullet points must be a list")
            if len(v) > MAX_BULLET_POINTS:
                raise ValueError(f"Too many bullet points (max {MAX_BULLET_POINTS})")
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
            if len(v) > MAX_PARAGRAPH_LENGTH:
                raise ValueError(f"Paragraph too long (max {MAX_PARAGRAPH_LENGTH} characters)")
        return v