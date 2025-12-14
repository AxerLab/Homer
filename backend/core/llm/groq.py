from pydantic_ai.models.groq import GroqModel

from ...config.app_config import MODEL, CORRECTION_MODEL, model_provider

model = GroqModel(model_name=MODEL, provider=model_provider)
correction_model = GroqModel(model_name=CORRECTION_MODEL, provider=model_provider)