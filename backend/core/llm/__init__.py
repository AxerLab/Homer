from pydantic_ai.models import Model
from .groq import model as groq_model, correction_model as groq_correction_model

# single export for all models defined in this package
model: Model = groq_model
correction_model: Model = groq_correction_model

__all__ = ["model", "correction_model"]