from pptx import Presentation
from pptx.shapes.base import BaseShape
from pptx.text.text import TextFrame
from pptx.shapes.placeholder import PicturePlaceholder
from ...models.content.textcontent.textcontent import TextContent
from ...models.content.textcontent.comparison import Comparison, BulletList
from ....config.logs import logger
import requests
from io import BytesIO
from urllib.parse import urlparse


class PPTXGenerator:
    def __init__(self):
        self.prs = Presentation()
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

    def _set_placeholder_text(
        self, placeholder: BaseShape | None, text: str | TextContent | BulletList | None # type: ignore
    ) -> None:
        """Safely set text on a placeholder."""
        if placeholder is not None and placeholder.has_text_frame:
            text_frame: TextFrame = placeholder.text_frame # type: ignore
            if isinstance(text, str):
                text_frame.text = text
            elif isinstance(text, TextContent):
                if text.para:
                    p = text_frame.add_paragraph()
                    p.text = text.para
                if text.bullet:
                    for point in text.bullet:
                        p = text_frame.add_paragraph()
                        p.text = point
                        p.level = 1
            elif isinstance(text, BulletList):
                for point in text:
                    p = text_frame.add_paragraph()
                    p.text = point
                    p.level = 1
            else:
                logger.warning(f"Cannot set text: placeholder={placeholder}, text={text}")

    def _set_placeholder_picture(
        self, placeholder: BaseShape | None, image_path: str | list[str] | None
    ) -> None:
        """
        Safely insert a picture into a picture placeholder.
        
        Args:
            placeholder: The placeholder shape to insert the picture into
            image_path: Path to the image file, URL to insert, or list of URLs to try with fallback
            
        Note:
            The placeholder reference becomes invalid after calling insert_picture(),
            so this method should be called last when working with a placeholder.
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
                if isinstance(placeholder, PicturePlaceholder):
                    # Check if image_path is a URL
                    parsed = urlparse(url)
                    if parsed.scheme in ('http', 'https'):
                        # Download the image from URL
                        logger.debug(f"Downloading image from URL: {parsed.scheme}://{parsed.netloc}...")
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        image_file = BytesIO(response.content)
                        logger.debug(f"Downloaded {len(response.content)} bytes, inserting into placeholder")
                        placeholder.insert_picture(image_file)
                        logger.debug("✓ Successfully inserted image into placeholder")
                        return  # Success! Exit the function
                    else:
                        # Local file path
                        logger.debug(f"Inserting local image file: {url}")
                        placeholder.insert_picture(url)
                        logger.debug("✓ Successfully inserted local image into placeholder")
                        return  # Success! Exit the function
                else:
                    logger.error(f"Placeholder is not a PicturePlaceholder, type: {type(placeholder)}")
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

        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(subtitle_placeholder, subtitle)

    def add_content_slide(self, title: str, content: TextContent):
        """
        For title_and_content layout
        Add a content slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["title_and_content"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        content_placeholder = slide.placeholders[1]
        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(content_placeholder, content)

    def section_header_slide(self, title: str, subtitle: str):
        """
        Add a section header slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["section_header"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        subtitle_placeholder = slide.placeholders[1]
        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(subtitle_placeholder, subtitle)

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
        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(content1_placeholder, content1)
        self._set_placeholder_text(content2_placeholder, content2)

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
        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(left_title_placeholder, comparison.left_title)
        self._set_placeholder_text(left_content_placeholder, comparison.left_content)
        self._set_placeholder_text(right_title_placeholder, comparison.right_title)
        self._set_placeholder_text(right_content_placeholder, comparison.right_content)

    def title_only_slide(self, title: str):
        """
        Add a title only slide to the presentation.
        """
        slide_layout = self.prs.slide_layouts[self.layouts_indices["title_only"]]
        slide = self.prs.slides.add_slide(slide_layout)
        title_placeholder = slide.shapes.title
        self._set_placeholder_text(title_placeholder, title)

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
        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(content_placeholder, content)
        self._set_placeholder_text(caption_placeholder, caption)

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
        self._set_placeholder_text(title_placeholder, title)
        self._set_placeholder_text(caption_placeholder, caption)
        # Add image last since insert_picture invalidates the placeholder reference
        self._set_placeholder_picture(image_placeholder, image_path)

    def save(self, file_path: str):
        self.prs.save(file_path)
