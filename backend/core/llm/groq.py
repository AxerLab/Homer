# OpenAI model configuration (using gpt-5.6-luna with native output support)
# File kept as groq.py for backward compatibility with imports

try:
    from pydantic_ai.models.openai import OpenAIModel
    _OPENAI_MODEL_OK = True
except Exception:
    OpenAIModel = None
    _OPENAI_MODEL_OK = False

from ...config.app_config import OPENAI_RESEARCH_MODEL_NAME, OPENAI_SLIDE_MODEL_NAME, model_provider

if _OPENAI_MODEL_OK and model_provider:
    # Use the OpenAI model provider directly (already configured in app_config.py)
    research_model = model_provider
    slide_model = model_provider
else:
    research_model = None
    slide_model = None
