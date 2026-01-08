from dotenv import load_dotenv
from pydantic_ai.providers.groq import GroqProvider
import os

load_dotenv()  # Load environment variables from .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

MODEL = "moonshotai/kimi-k2-instruct-0905"
CORRECTION_MODEL = "openai/gpt-oss-120b"

model_provider = GroqProvider(api_key=GROQ_API_KEY, base_url="https://api.groq.com/")

# Portkey Configuration (for RAG LLM with load balancing)
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY", "")
PORTKEY_CONFIG_ID = os.getenv("PORTKEY_CONFIG_ID", "")