from typing import List
from src.aislides.core.llm import model
from src.aislides.core.models.presentation.presentation import SlidePresentation
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from .prompts import (
    generator_system_prompt,
    iterator_system_prompt,
)
from src.aislides.core.models.slide.slide import Slide

agent = Agent(
    model=model,
    tools=[duckduckgo_search_tool(max_results=3)], 
    output_type=SlidePresentation, 
    system_prompt=generator_system_prompt, 
    retries=3
)

# agent for iterative slide editing
interator_agent = Agent(
    model=model, 
    tools=[duckduckgo_search_tool(max_results=3)],
    output_type=List[Slide], 
    system_prompt=iterator_system_prompt, 
    retries=3
)
