from pydantic_ai.models import Model
from .groq import model as groq_model

# single export for all models defined in this package
model: Model = groq_model

__all__ = ["model"]