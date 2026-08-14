from dotenv import load_dotenv
from pydantic_ai.providers.ollama import OllamaProvider
import os

load_dotenv()

# ollama config (local deployments)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_RESEARCH_MODEL_NAME = "qwen3.6-27b"
OLLAMA_SLIDE_MODEL_NAME = "qwen3.6-27b"
ollama_provider = OllamaProvider(base_url=OLLAMA_BASE_URL)

# groq config (cloud API) - optional
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_RESEARCH_MODEL_NAME = "qwen3.6-27b"
GROQ_SLIDE_MODEL_NAME = "qwen3.6-27b"

# Import GroqProvider only if available at runtime. This allows local-only
# deployments that don't install the `groq` dependency to continue running.
try:
    from pydantic_ai.providers.groq import GroqProvider
    _GROQ_IMPORT_OK = True
except Exception:
    GroqProvider = None
    _GROQ_IMPORT_OK = False

if GROQ_API_KEY and _GROQ_IMPORT_OK:
    model_provider = GroqProvider(api_key=GROQ_API_KEY, base_url="https://api.groq.com/")
else:
    # model_provider will be None when Groq isn't configured/installed; callers
    # should handle a None provider or fall back to local models.
    model_provider = None
