from dotenv import load_dotenv
from pydantic_ai.providers.groq import GroqProvider
import os

load_dotenv()  # Load environment variables from .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not GROQ_API_KEY and not OPENROUTER_API_KEY:
    raise ValueError("GROQ_API_KEY and OPENROUTER_API_KEY environment variables are not set.")

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

MODEL = "openrouter/google/gemini-2.0-flash-lite-001"

model_provider = GroqProvider(api_key=GROQ_API_KEY, base_url="https://api.groq.com/")