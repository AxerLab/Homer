# OpenAI model configuration (using gpt-5.6-luna with native output support)
# File kept as groq.py for backward compatibility with imports

from ...config.app_config import model_provider

# Export the configured model for cloud operations
research_model = model_provider
slide_model = model_provider
