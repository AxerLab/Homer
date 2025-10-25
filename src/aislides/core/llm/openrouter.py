from src.aislides.config.app_config import (
    OPENROUTER_API_BASE,
    OPENROUTER_API_KEY,
    MODEL,
)
import instructor

client = instructor.from_provider(
    MODEL,
    base_url=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)


def call_structured_model(messages, response_model):
    response = client.chat.completions.create(
        messages=messages,
        response_model=response_model,
        extra_body={"provider": {"require_parameters": True}},
        max_retries=3,
    )
    return response
