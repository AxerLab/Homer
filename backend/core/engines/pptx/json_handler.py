from typing import Optional, Union
from io import BytesIO
from ...models.presentation.presentation import SlidePresentation
from .generator import PPTXGenerator
from ...tools.tavily_image_search import tavily_image_search
from ....config.logs import logger
from ....templates.template_mapping import get_template_path


async def structure_to_ppt(
    pres: SlidePresentation,
    save_path: Optional[str] = None,
    theme: Optional[str] = None,
    return_bytes: bool = False,
) -> Union[BytesIO, None]:
    """Convert presentation structure to PPTX file.

    Args:
        pres: SlidePresentation object containing slide data
        save_path: Path where to save the PPTX file
        theme: Theme name to use for styling (e.g., 'default', 'psychedelic_vibrant')
    """
    # Get template path from theme name
    template_path = get_template_path(theme) if theme else None
    generator = PPTXGenerator(template_path=template_path)
    for slide in pres.slides:
        if slide.layout == "title":
            if slide.content is None or slide.content.text is None:
                raise ValueError("Title slide text must be provided for title layout")
            if slide.content.text.para is None:
                raise ValueError("Title slide text must be provided for title layout")
            if slide.title is None:
                raise ValueError("Title must be provided for title layout")
            generator.add_title_slide(slide.title, slide.content.text.para)

        elif slide.layout == "title_and_content":
            if slide.content is None or slide.content.text is None:
                raise ValueError(
                    "Content must be provided for title_and_content layout"
                )
            if slide.title is None:
                raise ValueError("Title must be provided for title_and_content layout")
            generator.add_content_slide(slide.title, slide.content.text)

        elif slide.layout == "section_header":
            if slide.content is None or slide.content.text is None:
                raise ValueError(
                    "Section header text must be provided for section_header layout"
                )
            if slide.content.text.para is None:
                raise ValueError(
                    "Section header text must be provided for section_header layout"
                )
            if slide.title is None:
                raise ValueError("Title must be provided for section_header layout")
            generator.section_header_slide(slide.title, slide.content.text.para)

        elif slide.layout == "two_content":
            if slide.content is None:
                raise ValueError("Content must be provided for two_content layout")
            if slide.title is None:
                raise ValueError("Title must be provided for two_content layout")
            
            if slide.image:
                if not slide.image_position:
                    raise ValueError(
                        "image_position must be specified for two_content with image"
                    )
                
                logger.debug(f"Fetching images for two_content query: '{slide.image}'")
                try:
                    image_urls_response = await tavily_image_search(
                        query=slide.image,
                        count=3,
                        search_depth="basic",
                        return_first_url=False,
                    )
                    
                    image_urls = []
                    if "**Image URLs:**" in image_urls_response:
                        lines = image_urls_response.split("\n")
                        for line in lines:
                            if line.strip() and line[0].isdigit() and ". http" in line:
                                url = line.split(". ", 1)[1].strip()
                                image_urls.append(url)
                    
                    if not image_urls:
                        raise ValueError(
                            f"No valid image URLs found for query '{slide.image}'"
                        )
                    
                    logger.debug(
                        f"Found {len(image_urls)} image URLs for two_content slide"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Failed to fetch images for query '{slide.image}': {str(e)}"
                    )
                    raise ValueError(
                        f"Failed to fetch images for query '{slide.image}': {str(e)}"
                    )
                
                text_content = (
                    slide.content.text2 if slide.image_position == "left" 
                    else slide.content.text
                )
                if text_content is None:
                    raise ValueError(
                        f"Text content required on opposite side of image "
                        f"(image_position={slide.image_position})"
                    )
                
                generator.two_content_with_image_slide(
                    slide.title, image_urls, text_content, slide.image_position
                )
            else:
                if slide.content.text2 is None:
                    raise ValueError(
                        "Second content must be provided for two_content layout"
                    )
                if slide.content.text is None:
                    raise ValueError(
                        "First content must be provided for two_content layout"
                    )
                generator.two_content_slide(
                    slide.title, slide.content.text, slide.content.text2
                )

        elif slide.layout == "comparison":
            if slide.content is None or slide.content.comparison is None:
                raise ValueError(
                    "Comparison content must be provided for comparison layout"
                )
            if slide.title is None:
                raise ValueError("Title must be provided for comparison layout")
            generator.comparison_slide(slide.title, slide.content.comparison)

        elif slide.layout == "title_only":
            if slide.title is None:
                raise ValueError("Title must be provided for title_only layout")
            generator.title_only_slide(slide.title)

        elif slide.layout == "blank":
            generator.blank_slide()

        elif slide.layout == "content_with_caption":
            if slide.content is None:
                raise ValueError(
                    "Content must be provided for content_with_caption layout"
                )
            if slide.content.text2 is None:
                raise ValueError(
                    "Caption content must be provided for content_with_caption layout"
                )
            if slide.content.text2.para is None:
                raise ValueError(
                    "Main content text must be provided for content_with_caption layout"
                )
            if slide.content.text is None:
                raise ValueError(
                    "Main content text must be provided for content_with_caption layout"
                )
            if slide.title is None:
                raise ValueError(
                    "Title must be provided for content_with_caption layout"
                )
            generator.content_with_caption_slide(
                slide.title, slide.content.text, slide.content.text2.para
            )

        elif slide.layout == "picture_with_caption":
            if slide.image is None:
                raise ValueError(
                    "Image search query must be provided for picture_with_caption layout"
                )
            if slide.content is None or slide.content.text is None:
                raise ValueError(
                    "Caption content must be provided for picture_with_caption layout"
                )
            if slide.title is None:
                raise ValueError(
                    "Title must be provided for picture_with_caption layout"
                )
            if slide.content.text.para is None:
                raise ValueError(
                    "Caption text must be provided for picture_with_caption layout"
                )

            # Perform image search using Tavily and get multiple image URLs as fallback
            logger.debug(f"Fetching images for query: '{slide.image}'")
            try:
                image_urls_response = await tavily_image_search(
                    query=slide.image,
                    count=3,
                    search_depth="basic",
                    return_first_url=False,
                )

                # Parse the response to extract image URLs
                image_urls = []
                if "**Image URLs:**" in image_urls_response:
                    lines = image_urls_response.split("\n")
                    for line in lines:
                        if line.strip() and line[0].isdigit() and ". http" in line:
                            # Extract URL from lines like "1. https://..."
                            url = line.split(". ", 1)[1].strip()
                            image_urls.append(url)

                if not image_urls:
                    raise ValueError(
                        f"No valid image URLs found for query '{slide.image}'"
                    )

                logger.debug(
                    f"Found {len(image_urls)} image URLs, attempting to use them in order"
                )

            except Exception as e:
                logger.error(
                    f"Failed to fetch images for query '{slide.image}': {str(e)}"
                )
                raise ValueError(
                    f"Failed to fetch images for query '{slide.image}': {str(e)}"
                )

            logger.debug(f"Adding picture_with_caption slide with title: {slide.title}")
            generator.picture_with_caption_slide(
                slide.title, image_urls, slide.content.text.para
            )
        else:
            raise ValueError(f"Unsupported slide layout: {slide.layout}")

    if return_bytes:
        return generator.save_to_bytes()

    if save_path:
        generator.save(save_path)
        logger.debug(f"PPTX saved to {save_path}")
    return None
