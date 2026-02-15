from ..models.SliderIterator import SlideIterator
from ..models.presentation.presentation import SlidePresentation
from ..models.slide.slide import Slide
from ..agent.agent import iterator_agent
from ...config.logs import logger
from ..memory.iteration_memory import iteration_memory
from typing import List, Set

from pydantic_ai import ModelHTTPError


def _get_context_titles(slides_before: List[Slide] | None, slides_after: List[Slide] | None) -> Set[str]:
    """Extract titles from context slides for filtering."""
    titles = set()
    if slides_before:
        for slide in slides_before:
            if slide.title:
                titles.add(slide.title.strip().lower())
    if slides_after:
        for slide in slides_after:
            if slide.title:
                titles.add(slide.title.strip().lower())
    return titles


def _filter_context_duplicates(
    generated_slides: List[Slide],
    context_titles: Set[str],
) -> List[Slide]:
    """Filter out slides that match context slide titles (LLM incorrectly regenerated context)."""
    if not context_titles:
        return generated_slides

    filtered = []

    for slide in generated_slides:
        slide_title_lower = (slide.title or "").strip().lower()

        if slide_title_lower in context_titles:
            logger.warning(
                f"Dropping slide '{slide.title}' - matches context slide title"
            )
            continue

        filtered.append(slide)

    if not filtered:
        logger.error("All generated slides were filtered out - returning original")
        return generated_slides

    if len(filtered) < len(generated_slides):
        logger.info(
            f"Filtered {len(generated_slides) - len(filtered)} context duplicate(s)"
        )

    return filtered


async def regenerate_slide(
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

    agent_result = None
    while True:
        try:
            agent_result = await iterator_agent.run(
                slider_iterator.model_dump_json(),
                message_history=iteration_memory.get_history(
                    original_prompt=original_prompt, slide_index=slide_index
                ),
            )
            break
        except ModelHTTPError as e:
            logger.error(f"Error regenerating slide: {e.message}")
            slider_iterator.instructions += (
                e.message
                + " \nSolution: If the content becomes too long, split it into multiple slides."
            )

    logger.debug(f"Agent result: {agent_result.all_messages_json()}")

    if agent_result is None:
        raise RuntimeError("Failed to generate updated slide after retries.")

    iteration_memory.record_iteration(
        original_prompt=original_prompt,
        slide_index=slide_index,
        edit_prompt=edit_prompt,
        messages=agent_result.new_messages(),
    )

    # Filter out any slides that match context titles (LLM sometimes regenerates context slides)
    context_titles = _get_context_titles(slider_iterator.slides_before, slider_iterator.slides_after)
    filtered_output = _filter_context_duplicates(agent_result.output, context_titles)

    updated_slides = presentation.slides.copy()
    updated_slides[slide_index : slide_index + 1] = filtered_output
    # Use model_construct to bypass strict validation when updating slides
    return SlidePresentation.model_construct(slides=updated_slides)
