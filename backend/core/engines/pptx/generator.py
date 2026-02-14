from pptx import Presentation
from pptx.shapes.base import BaseShape
from pptx.text.text import TextFrame
from pptx.shapes.placeholder import PicturePlaceholder
from pptx.enum.text import MSO_AUTO_SIZE
from ...models.content.textcontent.textcontent import TextContent
from ...models.content.textcontent.comparison import Comparison, BulletList
from ....config.logs import logger
from typing import Literal, Dict, Any
import requests
from io import BytesIO
from urllib.parse import urlparse
from pathlib import Path


class TextFitConfig:
    """Layout-specific text fitting configuration to prevent overflow."""

    LAYOUT_CONFIG: Dict[str, Dict[str, Any]] = {
        "title_and_content": {"max_bullets": 5, "truncate_at": 85, "max_font": 18},
        "picture_with_caption": {"max_bullets": 0, "truncate_at": 125, "max_font": 14},
        "two_content": {"max_bullets": 4, "truncate_at": 65, "max_font": 16},
        "comparison": {"max_bullets": 4, "truncate_at": 55, "max_font": 14},
        "content_with_caption": {"max_bullets": 4, "truncate_at": 65, "max_font": 16},
        "section_header": {"max_bullets": 0, "truncate_at": 150, "max_font": 24},
        "title": {"max_bullets": 0, "truncate_at": 200, "max_font": 44},
    }

    @classmethod
    def get_config(cls, layout_name: str) -> Dict[str, Any]:
        return cls.LAYOUT_CONFIG.get(
            layout_name, {"max_bullets": 5, "truncate_at": 85, "max_font": 18}
        )


class PPTXGenerator:
    def __init__(self, template_path: str | None = None):
        """Initialize PPTX generator with optional template.
        
        Args:
            template_path: Path to .pptx template file. If None, uses default blank template.
        """
        if template_path and Path(template_path).exists():
            self.prs = Presentation(template_path)
            logger.info(f"Using template: {template_path}")
        else:
            self.prs = Presentation()
            if template_path:
                logger.warning(f"Template not found: {template_path}, using default")
        self.layouts_indices = {
            "title": 0,
            "title_and_content": 1,
            "section_header": 2,
            "two_content": 3,
            "comparison": 4,
            "title_only": 5,
            "blank": 6,
            "content_with_caption": 7,
            "picture_with_caption": 8,
        }

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text with ellipsis, preserving word boundaries."""
        if len(text) <= max_length:
            return text
        truncated = text[: max_length - 3]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.7:
            truncated = truncated[:last_space]
        logger.warning(f"Truncated text from {len(text)} to {len(truncated) + 3} chars")
        return truncated.rstrip() + "..."

    def _apply_text_fit(self, text_frame: TextFrame, layout_name: str) -> None:
        """Apply auto-fit to prevent text overflow."""
        try:
            text_frame.word_wrap = True
            text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        except Exception as e:
            logger.warning(f"Failed to apply text fit for {layout_name}: {e}")

    def _set_placeholder_text(
        self,
        placeholder: BaseShape | None,
        text: str | TextContent | BulletList | None,  # type: ignore
        layout_name: str = "title_and_content",
    ) -> None:
        """Safely set text on a placeholder with overflow protection."""
        if placeholder is None or not placeholder.has_text_frame:
            return

        text_frame: TextFrame = placeholder.text_frame  # type: ignore
        config = TextFitConfig.get_config(layout_name)

        if isinstance(text, str):
            text_frame.text = self._truncate_text(text, config["truncate_at"] * 2)
        elif isinstance(text, TextContent):
            if text.para:
                p = text_frame.add_paragraph()
                p.text = self._truncate_text(text.para, config["truncate_at"] * 2)
            if text.bullet:
                max_bullets = config.get("max_bullets", 5) or 999
                bullets = text.bullet[:max_bullets]
                for point in bullets:
                    p = text_frame.add_paragraph()
                    p.text = self._truncate_text(point, config["truncate_at"])
                    p.level = 1
        elif isinstance(text, list):
            max_bullets = config.get("max_bullets", 5) or 999
            bullets = text[:max_bullets]
            for point in bullets:
                p = text_frame.add_paragraph()
                p.text = self._truncate_text(point, config["truncate_at"])
                p.level = 1
        else:
            logger.warning(f"Cannot set text: placeholder={placeholder}, text={text}")
            return

        self._apply_text_fit(text_frame, layout_name)

    def _set_placeholder_picture(
        self, placeholder: BaseShape | None, image_path: str | list[str] | None, slide=None
    ) -> None:
        """
        Safely insert a picture into a placeholder or at placeholder position.
        
        Args:
            placeholder: The placeholder shape to insert the picture into
            image_path: Path to the image file, URL to insert, or list of URLs to try with fallback
            slide: The slide object (required for non-PicturePlaceholder placeholders)
            
        Note:
            For PicturePlaceholder: uses insert_picture() method
            For other placeholders: adds picture as shape at placeholder's position and removes placeholder
            If image_path is a URL, it will be downloaded to a BytesIO object.
            If image_path is a list, URLs will be tried in order until one succeeds.
        """
        if placeholder is None or image_path is None:
            logger.warning(f"Cannot insert picture: placeholder={placeholder}, image_path={image_path}")
            return
        
        # Convert single URL to list for uniform handling
        urls_to_try = [image_path] if isinstance(image_path, str) else image_path
        
        for i, url in enumerate(urls_to_try, 1):
            logger.debug(f"Attempting to insert image from URL {i}/{len(urls_to_try)}: {url[:100]}...")
            try:
                # Download image if URL
                parsed = urlparse(url)
                if parsed.scheme in ('http', 'https'):
                    logger.debug(f"Downloading image from URL: {parsed.scheme}://{parsed.netloc}...")
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    image_file = BytesIO(response.content)
                    logger.debug(f"Downloaded {len(response.content)} bytes")
                else:
                    image_file = url  # type: ignore  # Local file path
                
                if isinstance(placeholder, PicturePlaceholder):
                    # Use native insert_picture for PicturePlaceholder
                    placeholder.insert_picture(image_file)
                    logger.debug("✓ Successfully inserted image into PicturePlaceholder")
                    return
                elif slide is not None:
                    # For regular placeholders, add picture as shape at placeholder position
                    left = placeholder.left
                    top = placeholder.top
                    width = placeholder.width
                    height = placeholder.height
                    
                    # Remove the placeholder text box
                    sp = placeholder._element
                    sp.getparent().remove(sp)
                    
                    # Add picture at the placeholder's position
                    slide.shapes.add_picture(image_file, left, top, width=width, height=height)
                    logger.debug("✓ Successfully added image as shape at placeholder position")
                    return
                else:
                    logger.error(f"Placeholder is not a PicturePlaceholder and no slide provided, type: {type(placeholder)}")
                    return
            except Exception as e:
                # Log the error and try next URL if available
                logger.warning(f"Failed to insert picture from URL {i}/{len(urls_to_try)}: {type(e).__name__}: {str(e)}")
                if i < len(urls_to_try):
                    logger.info("Trying next fallback URL...")
                else:
                    logger.error(f"All {len(urls_to_try)} image URLs failed")


    def add_title_slide(self, title: str, subtitle: str):
        """
        Add a title slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["title"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        subtitle_placeholder = slide.placeholders[1]

        self._set_placeholder_text(title_placeholder, title, "title")
        self._set_placeholder_text(subtitle_placeholder, subtitle, "title")

    def add_content_slide(self, title: str, content: TextContent):
        """
        For title_and_content layout
        Add a content slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["title_and_content"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        content_placeholder = slide.placeholders[1]
        self._set_placeholder_text(title_placeholder, title, "title_and_content")
        self._set_placeholder_text(content_placeholder, content, "title_and_content")

    def section_header_slide(self, title: str, subtitle: str):
        """
        Add a section header slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["section_header"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        subtitle_placeholder = slide.placeholders[1]
        self._set_placeholder_text(title_placeholder, title, "section_header")
        self._set_placeholder_text(subtitle_placeholder, subtitle, "section_header")

    def two_content_slide(
        self, title: str, content1: TextContent, content2: TextContent
    ):
        """
        Add a two content slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["two_content"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        content1_placeholder = slide.placeholders[1]
        content2_placeholder = slide.placeholders[2]
        self._set_placeholder_text(title_placeholder, title, "two_content")
        self._set_placeholder_text(content1_placeholder, content1, "two_content")
        self._set_placeholder_text(content2_placeholder, content2, "two_content")

    def two_content_with_image_slide(
        self,
        title: str,
        image_path: str | list[str],
        text_content: TextContent,
        image_position: Literal["left", "right"],
    ):
        """
        Add a two content slide with image on one side and text on the other.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["two_content"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        left_placeholder = slide.placeholders[1]
        right_placeholder = slide.placeholders[2]
        
        self._set_placeholder_text(title_placeholder, title, "two_content")
        
        if image_position == "left":
            self._set_placeholder_text(right_placeholder, text_content, "two_content")
            self._set_placeholder_picture(left_placeholder, image_path, slide=slide)
        else:
            self._set_placeholder_text(left_placeholder, text_content, "two_content")
            self._set_placeholder_picture(right_placeholder, image_path, slide=slide)

    def comparison_slide(
        self,
        title: str,
        comparison: Comparison,
    ):
        """
        Add a comparison slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["comparison"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        left_title_placeholder = slide.placeholders[1]
        left_content_placeholder = slide.placeholders[2]
        right_title_placeholder = slide.placeholders[3]
        right_content_placeholder = slide.placeholders[4]
        self._set_placeholder_text(title_placeholder, title, "comparison")
        self._set_placeholder_text(left_title_placeholder, comparison.left_title, "comparison")
        self._set_placeholder_text(left_content_placeholder, comparison.left_content, "comparison")
        self._set_placeholder_text(right_title_placeholder, comparison.right_title, "comparison")
        self._set_placeholder_text(right_content_placeholder, comparison.right_content, "comparison")

    def title_only_slide(self, title: str):
        """
        Add a title only slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["title_only"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        self._set_placeholder_text(title_placeholder, title, "title_only")

    def blank_slide(self):
        """
        Add a blank slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["blank"]]
        self.prs.slides.add_slide(slide_layout)

    def content_with_caption_slide(
        self, title: str, content: TextContent, caption: str
    ):
        """
        Add a content with caption slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[
            self.layouts_indices["content_with_caption"]
        ]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        content_placeholder = slide.placeholders[1]
        caption_placeholder = slide.placeholders[2]
        self._set_placeholder_text(title_placeholder, title, "content_with_caption")
        self._set_placeholder_text(content_placeholder, content, "content_with_caption")
        self._set_placeholder_text(caption_placeholder, caption, "content_with_caption")

    def picture_with_caption_slide(self, title: str, image_path: str | list[str], caption: str):
        '''
        Add a picture with caption slide to the presentation.
        
        Args:
            title: Slide title
            image_path: Single image URL/path or list of URLs to try with fallback
            caption: Caption text for the image
        '''
        slide_layout = self.prs.slide_layouts[self.layouts_indices["picture_with_caption"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        image_placeholder = slide.placeholders[1]
        caption_placeholder = slide.placeholders[2]
        self._set_placeholder_text(title_placeholder, title, "picture_with_caption")
        self._set_placeholder_text(caption_placeholder, caption, "picture_with_caption")
        # Add image last since insert_picture invalidates the placeholder reference
        self._set_placeholder_picture(image_placeholder, image_path, slide=slide)

    def save(self, file_path: str):
        self.prs.save(file_path)

    def save_to_bytes(self) -> BytesIO:
        buffer = BytesIO()
        self.prs.save(buffer)
        buffer.seek(0)
        return buffer
