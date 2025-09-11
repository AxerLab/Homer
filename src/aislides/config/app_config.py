from dotenv import load_dotenv
from pydantic_ai.providers.groq import GroqProvider
import os

load_dotenv()  # Load environment variables from .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

MODEL = "llama-3.3-70b-versatile"

model_provider = GroqProvider(api_key=GROQ_API_KEY, base_url="https://api.groq.com/")