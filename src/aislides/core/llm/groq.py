from pydantic_ai.models.groq import GroqModel

from src.aislides.config.app_config import MODEL, model_provider

model = GroqModel(model_name=MODEL, provider=model_provider)