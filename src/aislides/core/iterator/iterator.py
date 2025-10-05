from src.aislides.core.models.SliderIterator import SlideIterator
from src.aislides.core.models.presentation.presentation import SlidePresentation
from src.aislides.core.agent.agent import interator_agent
from src.aislides.config.logs import logger

from pydantic_ai import ModelHTTPError


def regenerate_slide(
    presentation: SlidePresentation,
    slide_index: int,
    edit_prompt: str,
    original_prompt: str,
    context_window: int = 1,
) -> SlidePresentation:
    """
    Regenerate a specific slide in the presentation based on user edits.

    Args:
        presentation (SlidePresentation): The original slide presentation.
        slide_index (int): The index of the slide to be modified (zero based).
        edit_prompt (str): The user-provided instructions for modifying the slide.
        original_prompt (str): The original prompt used to generate the presentation.
        context_window (int, optional): Number of slides before and after to include for context. Defaults to 1.

    Returns:
        SlidePresentation: The updated slide presentation with the modified slide.
    """
    if not (0 <= slide_index < len(presentation.slides)):
        raise IndexError("slide_index is out of range.")

    outline = []
    for idx, slide in enumerate(presentation.slides):
        outline.append(f"{idx + 1}. {slide.title}")

    slider_iterator = SlideIterator(
        slide=presentation.slides[slide_index],
        slides_before=presentation.slides[slide_index - context_window : slide_index]
        if slide_index > 0
        else None,
        slides_after=presentation.slides[
            slide_index + 1 : slide_index + 1 + context_window
        ]
        if slide_index < len(presentation.slides) - 1
        else None,
        outline="\n".join(outline),
        instructions=edit_prompt,
        prompt=original_prompt,
    )
    logger.debug(slider_iterator.model_dump_json())

    while True:
        try:
            modified_slide = interator_agent.run_sync(slider_iterator.model_dump_json())
            break
        except ModelHTTPError as e:
            logger.error(f"Error regenerating slide: {e.message}")
            slider_iterator.instructions += e.message + " \nSolution: If the content becomes too long, split it into multiple slides."

    updated_slides = presentation.slides.copy()
    updated_slides[slide_index:slide_index+1] = modified_slide.output

    return SlidePresentation(slides=updated_slides)
