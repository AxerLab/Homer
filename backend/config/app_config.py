from dotenv import load_dotenv
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
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
OPENAI_RESEARCH_MODEL_NAME = "gpt-5.6-luna"
OPENAI_SLIDE_MODEL_NAME = "gpt-5.6-luna"

# Import OpenAI provider
try:
    from pydantic_ai.providers.openai import OpenAIProvider
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.profiles.openai import OpenAIModelProfile
    _OPENAI_IMPORT_OK = True
except Exception:
    OpenAIProvider = None
    OpenAIChatModel = None
    OpenAIModelProfile = None
    _OPENAI_IMPORT_OK = False

if OPENAI_API_KEY and _OPENAI_IMPORT_OK:
    # Create OpenAI provider
    openai_provider = OpenAIProvider(api_key=OPENAI_API_KEY)
    
    # Configure profile with native output support for gpt-5.6-luna
    openai_profile = OpenAIModelProfile(
        supports_tools=True,
        supports_json_object_output=True,
        openai_supports_strict_tool_definition=True, 
        supports_thinking=False,# gpt-5.6-luna supports strict mode
    )
    
    # Create model with native structured output enabled
    model_provider = OpenAIChatModel(
        model_name=OPENAI_SLIDE_MODEL_NAME,
        provider=openai_provider,
        profile=openai_profile,
    )
else:
    # model_provider will be None when OpenAI isn't configured/installed; callers
    # should handle a None provider or fall back to local models.
    openai_provider = None
    model_provider = None
