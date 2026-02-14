from pydantic_ai.models.groq import GroqModel

from ...config.app_config import GROQ_RESEARCH_MODEL_NAME, GROQ_SLIDE_MODEL_NAME, model_provider

research_model = GroqModel(model_name=GROQ_RESEARCH_MODEL_NAME, provider=model_provider)
slide_model = GroqModel(model_name=GROQ_SLIDE_MODEL_NAME, provider=model_provider)