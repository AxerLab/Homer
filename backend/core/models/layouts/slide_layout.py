from enum import Enum


class SlideLayout(str, Enum):
    """Predefined slide layouts for PowerPoint presentations."""

    # Core PowerPoint Layouts
    TITLE = "title"  # Presentation title slide with main title and subtitle
    TITLE_AND_CONTENT = (
        "title_and_content"  # Standard layout with title and content area for text or media
    )
    SECTION_HEADER = (
        "section_header"  # Section break slide with title for transitioning between topics
    )
    TWO_CONTENT = "two_content"  # Two side-by-side content areas with bullet points or text
    COMPARISON = "comparison"  # Side-by-side comparison with titles for each content area
    TITLE_ONLY = "title_only"  # Clean slide with only a centered title
    BLANK = "blank"  # Empty slide with no predefined content areas
    CONTENT_WITH_CAPTION = "content_with_caption"  # Content area with accompanying caption text
    PICTURE_WITH_CAPTION = (
        "picture_with_caption"  # Image-focused layout with descriptive caption
    )

    @classmethod
    def get_descriptions(cls) -> dict[str, str]:
        """Get descriptions for all slide layouts."""
        return {
            cls.TITLE.value: "Presentation title slide with main title and subtitle",
            cls.TITLE_AND_CONTENT.value: "Standard layout with title and content area for text or media",
            cls.SECTION_HEADER.value: "Section break slide with title for transitioning between topics. Must have title and paragraph text only.",
            cls.TWO_CONTENT.value: "Two side-by-side content areas with bullet points or text",
            cls.COMPARISON.value: "Side-by-side comparison with titles for each content area",
            cls.TITLE_ONLY.value: "Clean slide with only a centered title. Must not have any other content.",
            cls.BLANK.value: "Empty slide with no predefined content areas. Cannot have title, text, bullet or any form of content.",
            cls.CONTENT_WITH_CAPTION.value: "Content area with accompanying caption text. Must have both text and text2 content.",
            cls.PICTURE_WITH_CAPTION.value: "Image-focused layout with descriptive caption",
        }

    @classmethod
    def get_schema_description(cls) -> str:
        """Get formatted description for schema generation."""
        descriptions = cls.get_descriptions()
        formatted = []
        for layout, desc in descriptions.items():
            # layout is already the string value since SlideLayout inherits from str
            formatted.append(f"- '{layout}': {desc}")
        return "Available slide layouts:\n" + "\n".join(formatted)
