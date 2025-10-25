from groq import Groq
import instructor
from src.aislides.core.llm.openrouter import call_structured_model
from src.aislides.core.models.presentation.presentation import SlidePresentation
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.config.app_config import GROQ_API_KEY
from src.aislides.config.logs import logger

client = Groq(
    api_key=GROQ_API_KEY,
)

client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

def generate():
    messages=[
        {
            "role": "user",
            "content": "General theory of relativity in rigorous mathematical language. Use mathematical notation where appropriate.",
        }
    ]

    resp: SlidePresentation = call_structured_model(messages, SlidePresentation) # type: ignore
    logger.info(f"Response: {resp.model_dump_json(indent=2)}")

    structure_to_ppt(resp, save_path="test.pptx")

if __name__ == "__main__":

    generate()