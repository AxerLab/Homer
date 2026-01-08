from pydantic_ai.models import Model
from .groq import model as groq_model, correction_model as groq_correction_model
from .portkey import portkey_complete, portkey_vision_complete

model: Model = groq_model
correction_model: Model = groq_correction_model

__all__ = ["model", "correction_model", "portkey_complete", "portkey_vision_complete"]