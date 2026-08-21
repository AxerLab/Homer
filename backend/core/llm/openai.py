# Make OpenAI model creation optional so imports don't crash when openai isn't installed.
try:
    from pydantic_ai.models.openai import OpenAIModel
    _OPENAI_MODEL_OK = True
except Exception:
    OpenAIModel = None
    _OPENAI_MODEL_OK = False

from ...config.app_config import GROQ_API_KEY, OPENAI_RESEARCH_MODEL_NAME, OPENAI_SLIDE_MODEL_NAME

if _OPENAI_MODEL_OK and GROQ_API_KEY:
    research_model = OpenAIModel(model_name=OPENAI_RESEARCH_MODEL_NAME, api_key=GROQ_API_KEY)
    slide_model = OpenAIModel(model_name=OPENAI_SLIDE_MODEL_NAME, api_key=GROQ_API_KEY)
else:
    research_model = None
    slide_model = None
