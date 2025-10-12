import os
from groq import Groq
import instructor
from src.aislides.core.models.presentation.presentation import SlidePresentation
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.config.app_config import GROQ_API_KEY

client = Groq(
    api_key=GROQ_API_KEY,
)

client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)


resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "General theory of relativity in rigorous mathematical language. Use mathematical notation where appropriate.",
        }
    ],
    response_model=SlidePresentation,
    max_retries=3,
)

structure_to_ppt(resp, save_path="test.pptx")