# Make Groq model creation optional so imports don't crash when groq isn't installed.
try:
    from pydantic_ai.models.groq import GroqModel
    _GROQ_MODEL_OK = True
except Exception:
    GroqModel = None
    _GROQ_MODEL_OK = False

from ...config.app_config import GROQ_RESEARCH_MODEL_NAME, GROQ_SLIDE_MODEL_NAME, model_provider

if _GROQ_MODEL_OK and model_provider:
    research_model = GroqModel(model_name=GROQ_RESEARCH_MODEL_NAME, provider=model_provider)
    slide_model = GroqModel(model_name=GROQ_SLIDE_MODEL_NAME, provider=model_provider)
else:
    research_model = None
    slide_model = None
