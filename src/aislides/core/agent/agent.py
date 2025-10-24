from typing import List
from src.aislides.core.llm import model
from src.aislides.core.models.presentation.presentation import SlidePresentation
from pydantic_ai import Agent, NativeOutput
import .prompts
from src.aislides.core.models.slide.slide import Slide

agent = Agent(
    model=model, output_type=NativeOutput(SlidePresentation), system_prompt=generator_system_prompt, retries=3
)

# agent for iterative slide editing
interator_agent = Agent(
    model=model, output_type=NativeOutput(List[Slide]), system_prompt=iterator_system_prompt, retries=3
)

tex_agent = Agent(
    model=model, output_type=NativeOutput(str), system_prompt=tex_generator_system_prompt, retries=3
)