from dotenv import load_dotenv
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.providers.ollama import OllamaProvider
import os

load_dotenv()

# ollama config (local deployments)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_RESEARCH_MODEL_NAME = "qwen3:4b"
OLLAMA_SLIDE_MODEL_NAME = "lfm2.5-thinking:latest"
ollama_provider = OllamaProvider(base_url=OLLAMA_BASE_URL)

# groq config (cloud API)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_RESEARCH_MODEL_NAME = "llama-3.3-70b-versatile"
GROQ_SLIDE_MODEL_NAME = "openai/gpt-oss-120b"
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
model_provider = GroqProvider(api_key=GROQ_API_KEY, base_url="https://api.groq.com/")