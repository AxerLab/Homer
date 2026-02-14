from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile

from ...config.app_config import (
    OLLAMA_RESEARCH_MODEL_NAME,
    OLLAMA_SLIDE_MODEL_NAME,
    ollama_provider
)

# Profile for research model - needs tool calling
research_profile = OpenAIModelProfile(
    supports_tools=True,
    supports_json_object_output=True,
    openai_supports_strict_tool_definition=False,  # Ollama doesn't support strict
    ignore_streamed_leading_whitespace=True,  # Qwen3 emits <think></think> tags
)

# Profile for slide model - needs JSON mode for PromptedOutput
slide_profile = OpenAIModelProfile(
    supports_tools=True,
    supports_json_object_output=True, 
    openai_supports_strict_tool_definition=False,
)

research_model = OpenAIChatModel(
    model_name=OLLAMA_RESEARCH_MODEL_NAME,
    provider=ollama_provider,
    profile=research_profile
)

slide_model = OpenAIChatModel(
    model_name=OLLAMA_SLIDE_MODEL_NAME,
    provider=ollama_provider,
    profile=slide_profile
)