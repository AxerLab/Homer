from pptx import Presentation
from pptx.shapes.base import BaseShape
from pptx.text.text import TextFrame
from pptx.shapes.placeholder import PicturePlaceholder
from ...models.content.textcontent.textcontent import TextContent
from ...models.content.textcontent.comparison import Comparison
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
        self, placeholder: BaseShape | None, text: str | TextContent | None
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

    def _set_placeholder_picture(
        self, placeholder: BaseShape | None, image_path: str | None
    ) -> None:
        """Safely insert a picture into a picture placeholder.
        
        Args:
            placeholder: The placeholder shape to insert the picture into
            image_path: Path to the image file or URL to insert
            
        Note:
            The placeholder reference becomes invalid after calling insert_picture(),
            so this method should be called last when working with a placeholder.
            If image_path is a URL, it will be downloaded to a BytesIO object.
        """
        if placeholder is None or image_path is None:
            return
        try:
            if isinstance(placeholder, PicturePlaceholder):
                # Check if image_path is a URL
                parsed = urlparse(image_path)
                if parsed.scheme in ('http', 'https'):
                    # Download the image from URL
                    response = requests.get(image_path, timeout=10)
                    response.raise_for_status()
                    image_file = BytesIO(response.content)
                    placeholder.insert_picture(image_file)
                else:
                    # Local file path
                    placeholder.insert_picture(image_path)
        except (AttributeError, TypeError, requests.RequestException, OSError):
            # Not a picture placeholder, invalid placeholder type, 
            # network error, or file error
            pass


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

    def picture_with_caption_slide(self, title: str, image_path: str, caption: str):
        '''
        Add a picture with caption slide to the presentation.
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
