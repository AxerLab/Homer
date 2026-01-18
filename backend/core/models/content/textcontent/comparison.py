from pydantic import BaseModel, Field, model_validator,field_validator, conlist
from typing import Optional, List

MAX_BULLET_POINTS = 4  # Reduced for side-by-side layouts
MAX_BULLET_LENGTH_COMPARISON = 50  # Shorter bullets for comparison columns
BulletList = conlist(str, min_length=0, max_length=MAX_BULLET_POINTS)

class Comparison(BaseModel):
    """Model for comparison content with validation."""

    left_title: Optional[str] = Field(
        None, description="Title for the left side of the comparison", max_length=100
    )
    left_content: Optional[BulletList] = Field(  # type: ignore
        None, description="Content for the left side of the comparison"
    )
    right_title: Optional[str] = Field(
        None, description="Title for the right side of the comparison", max_length=100
    )
    right_content: Optional[BulletList] = Field(  # type: ignore
        None, description="Content for the right side of the comparison"
    )

    @model_validator(mode="after")
    def validate_comparison_not_empty(self) -> "Comparison":
        """Ensure all of the comparison fields are provided."""
        if not (self.left_title and self.left_content and self.right_title and self.right_content):
            raise ValueError("All fields must be filled out.")
        return self

    @field_validator("left_content", "right_content")
    @classmethod
    def validate_text_content(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that text content is provided and within length limits."""
        if v is None:
            raise ValueError("Bullet content must be provided for comparison")
        for i, item in enumerate(v):
            if not isinstance(item, str) or len(item.strip()) == 0:
                raise ValueError("Each comparison bullet must be a non-empty string")
            if len(item) > MAX_BULLET_LENGTH_COMPARISON:
                raise ValueError(
                    f"Comparison bullet {i+1} exceeds {MAX_BULLET_LENGTH_COMPARISON} chars "
                    f"({len(item)} chars): '{item[:30]}...'"
                )
        return v
