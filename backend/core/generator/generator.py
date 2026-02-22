from ..agent.agent import research_agent, slide_agent
from ...config.logs import logger
from ..memory.global_memory import global_memory
from ..models.presentation.presentation import SlidePresentation
from ..rag.client import rag_client
from .auto_fix import fix_presentation_dict
from pydantic_ai import Agent, ModelHTTPError, FunctionToolCallEvent, FunctionToolResultEvent
from pydantic_ai.messages import ModelResponse, ToolCallPart, TextPart
import json
from typing import Any, Optional
import toons  # type: ignore[import-untyped]


MAX_RETRY_PROMPT_CHARS = 6000
MAX_PREVIOUS_ATTEMPT_CHARS = 5000


def _is_token_limit_error(exception: Exception) -> bool:
    if isinstance(exception, ModelHTTPError):
        if exception.status_code == 413:
            return True
        if isinstance(exception.body, dict):
            error_info = exception.body.get("error", {})
            if isinstance(error_info, dict):
                error_code = error_info.get("code", "")
                error_msg = error_info.get("message", "")
                if error_code == "rate_limit_exceeded" or "tokens" in error_code:
                    return True
                if "too large" in error_msg.lower() or "token" in error_msg.lower():
                    return True
    error_str = str(exception).lower()
    return "token" in error_str and ("limit" in error_str or "too large" in error_str)


def _build_retry_prompt_for_attempt(
    failed_attempt_json: str,
    error_msg: str,
    original_prompt: str,
    attempt: int,
) -> str:
    try:
        parsed = (
            json.loads(failed_attempt_json)
            if isinstance(failed_attempt_json, str)
            else failed_attempt_json
        )
        toon_attempt = toons.dumps(parsed)  # type: ignore
    except (json.JSONDecodeError, TypeError, Exception):
        toon_attempt = failed_attempt_json

    if attempt == 0:
        return (
            f"Original prompt: {original_prompt}\n\n"
            f"Validation error: {error_msg[:300]}\n\n"
            f"Fix this presentation (TOON format) to pass validation:\n{toon_attempt}\n\n"
            "Keep the content but fix the validation errors. Return valid JSON."
        )
    elif attempt == 1:
        truncated_attempt = toon_attempt[:MAX_PREVIOUS_ATTEMPT_CHARS]
        if len(toon_attempt) > MAX_PREVIOUS_ATTEMPT_CHARS:
            truncated_attempt += "\n..."
        return (
            f"Fix this presentation (TOON format):\n{truncated_attempt}\n\n"
            "The above failed validation. Fix the errors and return valid JSON."
        )
    else:
        truncated_attempt = toon_attempt[:3000]
        if len(toon_attempt) > 3000:
            truncated_attempt += "\n..."
        return f"Fix this:\n{truncated_attempt}\n\nReturn valid presentation JSON."


def extract_unvalidated_output(messages: list) -> dict:
    result = {"text_responses": [], "final_result_args": None, "all_tool_calls": []}

    for msg in messages:
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, TextPart):
                    result["text_responses"].append(part.content)
                elif isinstance(part, ToolCallPart):
                    tool_info = {"tool_name": part.tool_name, "args": part.args}
                    result["all_tool_calls"].append(tool_info)
                    if part.tool_name == "final_result":
                        result["final_result_args"] = part.args

    return result


async def generate_presentation_async(
    original_prompt: str, user_prompt: str
) -> SlidePresentation:
    return await _generate_presentation_impl(
        original_prompt, user_prompt
    )


async def _generate_presentation_impl(
    original_prompt: str, user_prompt: str
) -> SlidePresentation:
    prompt_key = user_prompt

    logger.debug(f"Generating presentation for prompt: {original_prompt}")

    agent_slide_result = None
    agent_run_ctx = None
    prompt = original_prompt
    failed_attempt_json = ""
    error_msg = ""
    generation_attempts = 3

    # research step: gather information via tool calls (real-time logging)
    try:
        logger.debug("[Stage 1] research_agent gathering info")
        async with research_agent.iter(
            prompt,
            message_history=global_memory.get_history(user_prompt=prompt_key),
        ) as agent_run:
            async for node in agent_run:
                if Agent.is_call_tools_node(node):
                    async with node.stream(agent_run.ctx) as handle_stream:
                        async for event in handle_stream:
                            if isinstance(event, FunctionToolCallEvent):
                                logger.debug(
                                    f"[Research] Tool call: {event.part.tool_name}({json.dumps(event.part.args, default=str)[:500]})"
                                )
                            elif isinstance(event, FunctionToolResultEvent):
                                logger.debug(
                                    f"[Research] Tool result: {event.part.tool_name} -> {str(event.result.content)[:300]}"
                                )
        agent_run_ctx = agent_run
    except Exception as e:
        logger.error(f"Unexpected error generating presentation: {e}")
        raise

    # generation step: create presentation based on research and original prompt
    retry_prompt = f"Slide deck prompt: {prompt}\ncontext: {agent_run_ctx.result.output}\n\nNow create the presentation based on the prompt and this context."

    for attempt in range(generation_attempts):
        try:
            logger.debug(
                f"[Stage 2] slide_agent attempt {attempt + 1} of {generation_attempts}"
            )

            agent_slide_result = await slide_agent.run(
                retry_prompt,
                message_history=None,
            )
            break
        except Exception as e:
            logger.error(f"Error during slide_agent attempt {attempt + 1}: {e}")
            error_msg = str(e)

            exc: Any = e
            if hasattr(exc, "_messages"):
                raw = extract_unvalidated_output(exc._messages)
                if raw["final_result_args"]:
                    failed_attempt_json = json.dumps(raw["final_result_args"], default=str)

                    try:
                        fixed = fix_presentation_dict(raw["final_result_args"])
                        agent_slide_result_data = SlidePresentation(**fixed)
                        logger.info(f"Auto-fix recovered presentation on attempt {attempt + 1}")
                        return agent_slide_result_data
                    except Exception as fix_err:
                        logger.debug(f"Auto-fix failed, continuing retry loop: {fix_err}")

            if _is_token_limit_error(e):
                logger.warning(
                    "Token limit exceeded, reducing prompt size for next attempt"
                )

            retry_prompt = _build_retry_prompt_for_attempt(
                failed_attempt_json,
                error_msg,
                original_prompt,
                attempt,
            )
            logger.debug(
                f"Strategy for attempt {attempt + 2}: prompt length={len(retry_prompt)}"
            )

            continue

    if agent_slide_result is None:
        raise RuntimeError("Failed to generate presentation after retries.")

    global_memory.record_generation(
        user_prompt=prompt_key,
        messages=agent_slide_result.new_messages(),
    )

    return agent_slide_result.output

async def generate_presentation_with_rag(
    original_prompt: str,
    user_prompt: str,
    use_rag: bool = True,
    doc_ids: Optional[list[str]] = None,
) -> SlidePresentation:
    rag_context = ""

    if use_rag or bool(doc_ids):
        try:
            rag_context = await rag_client.get_context_for_topic(
                original_prompt,
                doc_ids=doc_ids,
            )
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
