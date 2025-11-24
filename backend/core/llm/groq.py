from pydantic_ai.models.groq import GroqModel

from ...config.app_config import MODEL, model_provider

model = GroqModel(model_name=MODEL, provider=model_provider)