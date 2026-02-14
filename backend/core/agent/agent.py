from typing import List
from ..llm import cloud_research_model, cloud_slide_model
from ..models.presentation.presentation import SlidePresentation
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from .prompts import (
    generator_system_prompt,
    research_system_prompt,
    iterator_system_prompt,
)
from ..models.slide.slide import Slide

slide_output_type = NativeOutput(SlidePresentation)
iterator_output_type = NativeOutput(List[Slide])

research_agent = Agent(
    model=cloud_research_model,
    tools=[duckduckgo_search_tool(max_results=3)],
    system_prompt=research_system_prompt,
    retries=3
)

slide_agent = Agent(
    model=cloud_slide_model, 
    output_type=slide_output_type,
    system_prompt=generator_system_prompt,
    retries=3
)

interator_agent = Agent(
    model=cloud_slide_model, 
    tools=[duckduckgo_search_tool(max_results=3)],
    output_type=iterator_output_type,
    system_prompt=iterator_system_prompt, 
    retries=3
)

