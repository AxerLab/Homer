from src.aislides.core.llm import model
from src.aislides.core.models.presentation.presentation import SlidePresentation
from pydantic_ai import Agent
from .prompts import generator_system_prompt

agent = Agent(
    model=model, output_type=SlidePresentation, system_prompt=generator_system_prompt
)
