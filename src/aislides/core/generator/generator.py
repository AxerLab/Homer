from src.aislides.core.agent.agent import agent
from src.aislides.config.logs import logger
from src.aislides.core.memory.global_memory import global_memory
from src.aislides.core.models.presentation.presentation import SlidePresentation
from typing import Optional
from pydantic_ai import ModelHTTPError


def generate_presentation(
    original_prompt: str, user_prompt: str
) -> SlidePresentation:
    """
    Generate a slide presentation based on the user's prompt.

    Args:
        original_prompt (str): The user's current prompt for generating the presentation.
        user_prompt (str): An identifier for the user session. Usually it is the first prompt for the slide generation task.

    Returns:
        SlidePresentation: The generated slide presentation.
    """
    # Use original_prompt as the key if user_prompt is not provided
    prompt_key = user_prompt 

    logger.debug(f"Generating presentation for prompt: {original_prompt}")

    agent_result = None
    retry_prompt = original_prompt

    while True:
        try:
            agent_result = agent.run_sync(
                retry_prompt,
                message_history=global_memory.get_history(user_prompt=prompt_key),
            )
            break
        except ModelHTTPError as e:
            logger.error(f"Error generating presentation: {e.message}")
            retry_prompt = (
                original_prompt
                + "\n\n"
                + e.message
                + "\nSolution: If the content becomes too long, increase the number of slides or shorten the content."
            )

    # logger.debug(f"Agent result: {agent_result.all_messages_json()}")

    if agent_result is None:
        raise RuntimeError("Failed to generate presentation after retries.")

    # Record the generation in global memory
    global_memory.record_generation(
        user_prompt=prompt_key,
        messages=agent_result.new_messages(),
    )

    return agent_result.output
