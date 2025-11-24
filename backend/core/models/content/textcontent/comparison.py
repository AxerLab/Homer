from pydantic import BaseModel, Field, model_validator,field_validator, conlist
from typing import Optional

MAX_BULLET_POINTS = 5
BulletList = conlist(str, min_length=0, max_length=MAX_BULLET_POINTS)

class Comparison(BaseModel):
    """Model for comparison content with validation."""

    left_title: Optional[str] = Field(
        None, description="Title for the left side of the comparison", max_length=200
    )
    left_content: Optional[BulletList] = Field( # type: ignore
        None, description="Content for the left side of the comparison"
    )
    right_title: Optional[str] = Field(
        None, description="Title for the right side of the comparison", max_length=200
    )
    right_content: Optional[BulletList] = Field( # type: ignore
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
    def validate_text_content(cls, v: Optional[BulletList]) -> Optional[BulletList]: # type: ignore
        """Validate that text content is provided."""
        if v is None:
            raise ValueError("Bullet content must be provided for comparison")
        return v

    @model_validator(mode="after")
    def check_bullet_points_equal(self) -> "Comparison":
        """Ensure both sides have the same number of bullet points."""
        if self.left_content and self.right_content:
            left_bullets = self.left_content
            right_bullets = self.right_content
            if len(left_bullets) != len(right_bullets):
                raise ValueError("Both sides must have the same number of bullet points")
        return self