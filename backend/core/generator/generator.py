from ..agent.agent import agent, correction_agent
from ...config.logs import logger
from ..memory.global_memory import global_memory
from ..models.presentation.presentation import SlidePresentation
from ..rag.service import rag_service
from pydantic_ai import ModelHTTPError, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai.messages import ModelResponse, ToolCallPart, TextPart
import json


def extract_unvalidated_output(messages: list) -> dict:
    """
    Extract the raw unvalidated content from captured messages.

    Returns the content the model actually generated before validation failed,
    including text responses and tool call arguments (especially final_result).

    Args:
        messages: List of ModelMessage objects from capture_run_messages

    Returns:
        dict with 'text_responses', 'final_result_args', and 'all_tool_calls'
    """
    result = {"text_responses": [], "final_result_args": None, "all_tool_calls": []}

    for msg in messages:
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                # Extract text content
                if isinstance(part, TextPart):
                    result["text_responses"].append(part.content)

                # Extract tool call arguments
                elif isinstance(part, ToolCallPart):
                    tool_info = {"tool_name": part.tool_name, "args": part.args}
                    result["all_tool_calls"].append(tool_info)

                    # final_result contains the attempted structured output
                    if part.tool_name == "final_result":
                        result["final_result_args"] = part.args

    return result


def generate_presentation(original_prompt: str, user_prompt: str) -> SlidePresentation:
    """
    Generate a slide presentation based on the user's prompt.
    Synchronous version - use generate_presentation_async for async contexts.

    Args:
        original_prompt (str): The user's current prompt for generating the presentation.
        user_prompt (str): An identifier for the user session. Usually it is the first prompt for the slide generation task.

    Returns:
        SlidePresentation: The generated slide presentation.
    """
    import asyncio

    try:
        asyncio.get_running_loop()
        # We're in an async context, this shouldn't be called
        raise RuntimeError("Use generate_presentation_async in async contexts")
    except RuntimeError as e:
        if "no running event loop" in str(e).lower():
            # No running loop, safe to use run_sync
            pass
        else:
            raise

    return asyncio.run(
        _generate_presentation_impl(original_prompt, user_prompt, use_async=False)
    )


async def generate_presentation_async(
    original_prompt: str, user_prompt: str
) -> SlidePresentation:
    """
    Generate a slide presentation based on the user's prompt (async version).

    Args:
        original_prompt (str): The user's current prompt for generating the presentation.
        user_prompt (str): An identifier for the user session.

    Returns:
        SlidePresentation: The generated slide presentation.
    """
    return await _generate_presentation_impl(
        original_prompt, user_prompt, use_async=True
    )


async def _generate_presentation_impl(
    original_prompt: str, user_prompt: str, use_async: bool = False
) -> SlidePresentation:
    # Use original_prompt as the key if user_prompt is not provided
    prompt_key = user_prompt

    logger.debug(f"Generating presentation for prompt: {original_prompt}")

    agent_result = None
    retry_prompt = original_prompt
    is_schema_error = False

    with capture_run_messages() as messages:
        try:
            if use_async:
                agent_result = await agent.run(
                    retry_prompt,
                    message_history=global_memory.get_history(user_prompt=prompt_key),
                )
            else:
                agent_result = agent.run_sync(
                    retry_prompt,
                    message_history=global_memory.get_history(user_prompt=prompt_key),
                )
        except (ModelHTTPError, UnexpectedModelBehavior) as e:
            error_msg = str(e)

            # For ModelHTTPError, check status_code and body
            if isinstance(e, ModelHTTPError):
                logger.warning(f"ModelHTTPError encountered: {error_msg[:200]}...")
                if e.status_code == 400 and isinstance(e.body, dict):
                    error_dict = e.body.get("error", {})
                    if isinstance(error_dict, dict):
                        message = error_dict.get("message", "")
                        error_code = error_dict.get("code", "")
                        # Check for tool use failures or validation errors
                        if (
                            error_code == "tool_use_failed"
                            or (
                                "tool call validation failed" in message
                                and "final_result" in message
                            )
                            or (
                                "Failed to call a function" in message
                                and "final_result" in error_msg
                            )
                        ):
                            is_schema_error = True

            # For UnexpectedModelBehavior, check if it contains validation errors
            elif isinstance(e, UnexpectedModelBehavior):
                logger.warning(
                    f"UnexpectedModelBehavior encountered: {error_msg[:200]}... (Not an error)"
                )
                if "validation" in error_msg.lower() or "schema" in error_msg.lower():
                    is_schema_error = True

            if is_schema_error:
                raw_content = extract_unvalidated_output(messages)

                if raw_content["text_responses"]:
                    logger.debug(
                        f"Model text responses: {raw_content['text_responses']}"
                    )

                # Build retry prompt with the unvalidated content
                retry_prompt = (
                    f"Original prompt: {original_prompt}\n\n"
                    + "Your previous attempt failed validation with this error:\n"
                    + f"{error_msg}\n\n"
                )

                # Include the attempted output if available
                if raw_content["final_result_args"]:
                    retry_prompt += (
                        "You previously attempted to generate:\n"
                        + f"{json.dumps(raw_content['final_result_args'], indent=2)}\n\n"
                        + "Keep the content but fix the validation errors.\n"
                    )

                retry_prompt += "\nSolution: If the content becomes too long, increase the number of slides or shorten the content."

                logger.debug(
                    f"Retry prompt with unvalidated content: {retry_prompt[:500]}..."
                )
            else:
                raise
        except Exception as e:
            logger.error(f"Unexpected error generating presentation: {e}")
            raise

    if agent_result is not None:
        global_memory.record_generation(
            user_prompt=prompt_key,
            messages=agent_result.new_messages(),
        )

    if is_schema_error:
        attempts = 3
        for attempt in range(attempts):
            try:
                logger.debug(
                    f"Retrying with correction agent, attempt {attempt + 1} of {attempts}"
                )
                if use_async:
                    agent_result = await correction_agent.run(
                        retry_prompt,
                        message_history=global_memory.get_history(
                            user_prompt=prompt_key
                        ),
                    )
                else:
                    agent_result = correction_agent.run_sync(
                        retry_prompt,
                        message_history=global_memory.get_history(
                            user_prompt=prompt_key
                        ),
                    )
                break  # Exit loop if successful
            except Exception as e:
                logger.error(f"Error during correction attempt {attempt + 1}: {e}")
                continue

    if agent_result is None:
        raise RuntimeError("Failed to generate presentation after retries.")

    global_memory.record_generation(
        user_prompt=prompt_key,
        messages=agent_result.new_messages(),
    )

    return agent_result.output


async def generate_presentation_with_rag(
    original_prompt: str, user_prompt: str, use_rag: bool = True
) -> SlidePresentation:
    rag_context = ""

    if use_rag:
        try:
            await rag_service.initialize()
            rag_context = await rag_service.get_context_for_topic(original_prompt)
            if rag_context and rag_context.strip():
                logger.info(f"RAG context retrieved: {len(rag_context)} chars")
        except Exception as e:
            logger.warning(f"RAG context retrieval failed (continuing without): {e}")
            rag_context = ""

    if rag_context:
        enhanced_prompt = (
            f"{original_prompt}\n\n"
            f"Use the following reference material from uploaded documents:\n"
            f"---\n{rag_context}\n---\n"
            f"Incorporate relevant information from this context into the presentation."
        )
    else:
        enhanced_prompt = original_prompt

    return await generate_presentation_async(enhanced_prompt, user_prompt)
