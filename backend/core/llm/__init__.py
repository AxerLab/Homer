from pydantic_ai.models import Model
from .ollama import research_model as ollama_research_model, slide_model as ollama_slide_model
from .groq import research_model as groq_research_model, slide_model as groq_slide_model

local_research_model: Model = ollama_research_model
local_slide_model: Model = ollama_slide_model
cloud_research_model: Model = groq_research_model
cloud_slide_model: Model = groq_slide_model

__all__ = ["local_research_model", "local_slide_model", "cloud_research_model", "cloud_slide_model"]