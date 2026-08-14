from typing import List
from ..llm import cloud_research_model, cloud_slide_model
from ..models.presentation.presentation import SlidePresentation
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from .prompts import (
    generator_system_prompt,
    research_system_prompt,
    iterator_system_prompt,
)
from ..models.slide.slide import Slide

# ModelSettings to prevent token limit errors
model_settings = ModelSettings(max_tokens=8192)

research_agent = Agent(
    model=cloud_research_model,
    tools=[duckduckgo_search_tool(max_results=2)],  # Reduced from 3 to 2
    system_prompt=research_system_prompt,
    retries=3,
    model_settings=model_settings,
)

slide_agent = Agent(
    model=cloud_slide_model, 
    output_type=SlidePresentation,
    system_prompt=generator_system_prompt,
    retries=3,
    model_settings=model_settings,
)

iterator_agent = Agent(
    model=cloud_slide_model, 
    tools=[duckduckgo_search_tool(max_results=2)],  # Reduced from 3 to 2
    output_type=List[Slide],
    system_prompt=iterator_system_prompt, 
    retries=3,
    model_settings=model_settings,
)
