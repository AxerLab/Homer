from typing import Optional
from src.aislides.core.models.presentation.presentation import SlidePresentation
from .generator import PPTXGenerator

def structure_to_ppt(pres: SlidePresentation, save_path: Optional[str] = None):
    generator = PPTXGenerator()
    for slide in pres.slides:
        if slide.layout == "title":
            if slide.content.text is None:
                raise ValueError("Title slide text must be provided for title layout")
            if slide.content.text.para is None:
                raise ValueError("Title slide text must be provided for title layout")
            generator.add_title_slide(slide.title, slide.content.text.para)

        elif slide.layout == "title_and_content":
            if slide.content.text is None:
                raise ValueError("Content must be provided for title_and_content layout")
            generator.add_content_slide(slide.title, slide.content.text)

        elif slide.layout == "section_header":
            if slide.content.text is None:
                raise ValueError("Section header text must be provided for section_header layout")
            if slide.content.text.para is None:
                raise ValueError("Section header text must be provided for section_header layout")
            generator.section_header_slide(slide.title, slide.content.text.para)

        elif slide.layout == "two_content":
            if slide.content.text2 is None:
                raise ValueError("Second content must be provided for two_content layout")
            if slide.content.text is None:
                raise ValueError("First content must be provided for two_content layout")
            generator.two_content_slide(
                slide.title, slide.content.text, slide.content.text2
            )

        elif slide.layout == "comparison":
            if slide.content.comparison is None:
                raise ValueError("Comparison content must be provided for comparison layout")
            generator.comparison_slide(
                slide.title, slide.content.comparison
            )

        elif slide.layout == "title_only":
            generator.title_only_slide(slide.title)

        elif slide.layout == "blank":
            generator.blank_slide()

        elif slide.layout == "content_with_caption":
            if slide.content.text2 is None:
                raise ValueError("Caption content must be provided for content_with_caption layout")
            if slide.content.text2.para is None:
                raise ValueError("Main content text must be provided for content_with_caption layout")
            if slide.content.text is None:
                raise ValueError("Main content text must be provided for content_with_caption layout")
            generator.content_with_caption_slide(
                slide.title, slide.content.text, slide.content.text2.para
            )

        # elif slide.layout == "picture_with_caption":
        #     if slide.image is None:
        #         raise ValueError("Image must be provided for picture_with_caption layout")
        #     if slide.content.text2 is None:
        #         raise ValueError("Caption content must be provided for picture_with_caption layout")
        #     generator.picture_with_caption_slide(
        #         slide.title, slide.image, slide.content.text2
        #     )
        else:
            raise ValueError(f"Unsupported slide layout: {slide.layout}")
        
    if save_path:
        generator.save(save_path)
    return generator.prs

