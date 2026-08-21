from dotenv import load_dotenv
from pydantic_ai.providers.ollama import OllamaProvider
import os

load_dotenv()

# ollama config (local deployments)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_RESEARCH_MODEL_NAME = "llama-3.3-70b-versatile"
OLLAMA_SLIDE_MODEL_NAME = "openai/gpt-oss-120b"
ollama_provider = OllamaProvider(base_url=OLLAMA_BASE_URL)

# openai config (cloud API) - using gpt-5.6-luna with native output support
# API key is stored under GROQ_API_KEY for backward compatibility
OPENAI_API_KEY = os.getenv("GROQ_API_KEY")  # Using GROQ_API_KEY name for backward compatibility
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_RESEARCH_MODEL_NAME = "gpt-5.6-luna"
OPENAI_SLIDE_MODEL_NAME = "gpt-5.6-luna"

# Import OpenAIModel provider
try:
    from pydantic_ai.models.openai import OpenAIModel
    _OPENAI_IMPORT_OK = True
except Exception:
    OpenAIModel = None
    _OPENAI_IMPORT_OK = False

if OPENAI_API_KEY and _OPENAI_IMPORT_OK:
    # OpenAIModel with native output support enabled
    model_provider = OpenAIModel(
        model_name=OPENAI_SLIDE_MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
else:
    # model_provider will be None when OpenAI isn't configured/installed; callers
    # should handle a None provider or fall back to local models.
    model_provider = None
